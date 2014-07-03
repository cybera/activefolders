import logging
import activefolders.db as db
import activefolders.conf as conf
import activefolders.requests as requests
import activefolders.controllers.folders as folders
import activefolders.controllers.transfers as transfers
import activefolders.utils as utils

LOG = logging.getLogger(__name__)
handles = {}


def get(uuid, destination):
    """ Returns results for specific destination for folder specified by uuid """
    folder = folders.get(uuid)
    folder_dst = db.FolderDestination.get(
        db.FolderDestination.folder == folder,
        db.FolderDestination.destination == destination)

    return folder_dst.results_folder


def get_all(uuid):
    """ Returns all available results folders """
    folder = folders.get(uuid)
    folder_dsts = db.FolderDestination.select().where(
        db.FolderDestination.folder == folder)
    results = {}

    for folder_dst in folder_dsts:
        dst = folder_dst.destination
        results[dst] = folder_dst.results_folder.uuid if folder_dst.results_folder else None

    return results


def update(folder_destination):
    if folder_destination.results_folder is None:
        results_folder = folders.add()
        results_folder.results = True
        results_folder.save()
        folder_destination.results_folder = results_folder
        folder_destination.save()

    uuid = folder_destination.folder.uuid
    destination = folder_destination.destination

    if handles.get(uuid) is None:
        handles[uuid] = {}

    handle = handles[uuid].get(destination)
    if handle is None:
        transport = utils.get_transport(folder_destination.destination)
        handle = transport.ResultsTransport(folder_destination)
        handles[uuid][destination] = handle
        handle.start()
        return
    elif handle.is_alive():
        return
    elif handle.success:
        results_folder = folder_destination.results_folder
        home_dtn = folder_destination.folder.home_dtn
        transfers.add(results_folder, home_dtn)
        transfers.check(results_folder.uuid)
        del handles[uuid][destination]
    else:
        LOG.warning("Failed to retrieve results for {} from {}".format(uuid, destination))
        del handles[uuid][destination]


def check(uuid=None):
    if uuid is None:
        folder_dsts = db.FolderDestination.select().where(
                db.FolderDestination.results_retrieved == False)
    else:
        folder = folders.get(uuid)
        folder_dsts = db.FolderDestination.select().where(
                db.FolderDestination.results_retrieved == False,
                db.FolderDestination.folder == folder)

    for folder_dst in folder_dsts:
        dst_dtn = conf.destinations[folder_dst.destination]['dtn']
        if dst_dtn == conf.settings['dtnd']['name']:
            update(folder_dst)
        else:
            request = requests.CheckResultsRequest(conf.dtns[dst_dtn], folder_dst.folder)
            request.execute()
