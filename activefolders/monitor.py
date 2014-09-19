from threading import Thread
from time import sleep
from activefolders.utils import logging
import peewee
import activefolders.conf as conf
import activefolders.db as db
import activefolders.controllers.folders as folders
import activefolders.controllers.transfers as transfers
import activefolders.controllers.exports as exports
import activefolders.transports.gridftp_simple as gridftp
import activefolders.utils as utils
import activefolders.requests as requests

LOG = logging.getLogger(__name__)


class TransportMonitor(Thread):
    SLEEP_TIME = conf.settings.getint('dtnd', 'update_interval') / 3
    RESULTS_RETRIES = conf.settings.getint('dtnd', 'results_retries')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._transfers = {}
        self._exports = {}
        self._results = {}

    def run(self):
        while True:
            self._update_transfers()
            sleep(self.SLEEP_TIME)
            self._update_exports()
            sleep(self.SLEEP_TIME)
            self._update_results()
            sleep(self.SLEEP_TIME)

    def _update_transfers(self):
        inactive_transfers = db.Transfer.select().where(db.Transfer.active==False)
        for transfer in inactive_transfers:
            try:
                db.Transfer.get(db.Transfer.folder==transfer.folder,
                    db.Transfer.dtn==transfer.dtn,
                    db.Transfer.active==True)
            except peewee.DoesNotExist:
                transfer.active = True
                transfer.save()

        active_transfers = db.Transfer.select().where(db.Transfer.active==True)
        for transfer in active_transfers:
            transport = self._transfers.get(transfer.id)
            if transport is None:
                transport = gridftp.DtnTransport(transfer)
                self._transfers[transfer.id] = transport
                transport.start()

        for transfer_id, transport in list(self._transfers.items()):
            transfer = db.Transfer.get(db.Transfer.id==transfer_id)
            if transport.is_alive():
                continue
            elif not transport.success:
                LOG.error("Transfer {} failed with error: {}".format(transfer_id, transport.exception))
            del self._transfers[transfer_id]
            transfer.delete_instance()

    def _update_exports(self):
        inactive_exports = db.Export.select().where(db.Export.active==False)
        for export in inactive_exports:
            try:
                db.Export.get(db.Export.folder_destination==export.folder_destination,
                    db.Transfer.active==True)
            except peewee.DoesNotExist:
                export.active = True
                export.save()

        active_exports = db.Export.select().where(db.Export.active==True)
        for export in active_exports:
            transport = self._exports.get(export.id)
            if transport is None:
                transport_module = utils.get_transport_module(export.folder_destination.destination)
                transport = transport_module.DestinationTransport(export)
                self._exports[export.id] = transport
                transport.start()

        for export_id, transport in list(self._exports.items()):
            export = db.Export.get(db.Export.id==export_id)
            if transport.is_alive():
                continue
            elif not transport.success:
                LOG.error("Export {} failed with error: {}".format(export_id, transport.exception))
            del self._exports[export_id]
            export.delete_instance()

    def _update_results(self):
        this_dtn = conf.settings['dtnd']['name']
        reachable_destinations = [ dst for dst, dst_conf in conf.destinations.items() if dst != 'DEFAULT' and dst_conf['dtn'] == this_dtn ] # TODO: Avoid default section
        folder_destinations = db.FolderDestination.select().where(
            db.FolderDestination.check_for_results==True,
            db.FolderDestination.results_retrieved==False,
            db.FolderDestination.destination<<reachable_destinations)

        for folder_destination in folder_destinations:
            # Don't check for results if an export exists
            num_exports = db.Export.select().where(db.Export.folder_destination==folder_destination).count()
            if num_exports > 0:
                continue

            if folder_destination.results_folder is None:
                self._create_results_folder(folder_destination)

            uuid = folder_destination.folder.uuid
            if self._results.get(uuid) is None:
                self._results[uuid] = {}

            destination = folder_destination.destination
            transport = self._results[uuid].get(destination)
            if transport is None:
                transport_module = utils.get_transport_module(destination)
                transport = transport_module.ResultsTransport(folder_destination)
                self._results[uuid][destination] = transport
                transport.start()
                continue
            elif transport.is_alive():
                continue
            elif not transport.success:
                LOG.error("Results retrieval for folder {} from {} failed with error: {}".format(uuid, destination, transport.exception))
            else:
                self._update_results_status(transport, folder_destination)
            del self._results[uuid][destination]

    def _create_results_folder(self, folder_destination):
        results_folder = folders.add()
        results_folder.results = True
        results_folder.save()
        folder_destination.results_folder = results_folder
        folder_destination.save()

    def _update_results_status(self, transport, folder_destination):
        if transport.new_results:
            if folder_destination.initial_results:
                folder_destination.tries_without_changes = 0
            else:
                folder_destination.initial_results = True
            folder_destination.save()
            self._transfer_results(folder_destination)
        elif folder_destination.initial_results:
            folder_destination.tries_without_changes += 1
            folder_destination.save()
            if folder_destination.tries_without_changes >= self.RESULTS_RETRIES:
                folder_destination.results_retrieved = True
                folder_destination.save()

    def _transfer_results(self, folder_destination):
        results_folder = folder_destination.results_folder

        if folder_destination.results_destination is None:
            home_dtn = folder_destination.folder.home_dtn
            transfers.add(results_folder, home_dtn)
        else:
            try:
                db.FolderDestination.get(
                    db.FolderDestination.folder==results_folder)
            except peewee.DoesNotExist:
                db.FolderDestination.create(folder=results_folder,
                    destination=folder_destination.results_destination,
                    credentials=folder_destination.credentials)

            transfers.add_all(results_folder.uuid)
            exports.add_all(results_folder.uuid)


class RequestMonitor(Thread):
    SLEEP_TIME = conf.settings.getint('dtnd', 'requests_update_interval')

    def run(self):
        while True:
            self._update_requests()
            sleep(self.SLEEP_TIME)

    def _update_requests(self):
        all_requests = db.Request.select()

        for r in all_requests:
            if r.dtn not in conf.dtns:
                r.delete_instance()

            request = requests.Request(r.dtn, r.command, r.method, r.headers, r.params, r.data, r.expected_responses)
            resp = request.execute()
            if request.success:
                r.delete_instance()
            else:
                if resp is None:
                    LOG.error("Request failed with no reponse")
                else:
                    LOG.error("Request failed with response: {}".format(resp.text))
                r.failures += 1
                r.save()
