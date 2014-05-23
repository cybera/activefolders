import peewee
import requests
import logging
import json
import activefolders.conf as conf
import activefolders.db as db
import activefolders.controllers.folders as folders
import activefolders.transports.gridftp_simple as transport

LOG = logging.getLogger(__name__)

handles = {}


def add_folder_to_dtn(folder, dtn_conf):
    url = dtn_conf['api'] + "/add_folder"
    headers = { 'Content-type': 'application/json' }
    destinations = folders.get_destinations(folder.uuid)
    folder_data = {
        'uuid': folder.uuid,
        'home_dtn': conf.settings['dtnd']['name'],
        'destinations': destinations
    }

    if folder.results:
        folder_dst = db.FolderDestination.get(db.FolderDestination.results_folder == folder)
        folder_data['results_for'] = {}
        folder_data['results_for']['folder'] = folder_dst.folder.uuid
        folder_data['results_for']['destination'] = folder_dst.destination

    LOG.info("Adding folder {} to {}".format(folder.uuid, url))
    resp = requests.post(url, data=json.dumps(folder_data), headers=headers)
    if resp.status_code == 200 or resp.status_code == 201:
        return 0
    else:
        LOG.error("Adding folder {} to {} failed with error: {}".format(folder.uuid, url, resp.text))
        return 1


def update(transfer):
    folder = transfer.folder
    dtn_conf = conf.dtns[transfer.dtn]
    LOG.debug("Checking transfer {} for folder {} to {}, current status {}".format(transfer.id, folder.uuid, transfer.dtn, transfer.status))

    if not transfer.active:
        try:
            db.Transfer.get(db.Transfer.folder==folder, db.Transfer.dtn==transfer.dtn, db.Transfer.active==True)
            LOG.debug("Transfer {} is still pending".format(transfer.id))
            return
        except peewee.DoesNotExist:
            transfer.active = True
            transfer.save()
            LOG.debug("Transfer {} is now active".format(transfer.id))

    if transfer.status == db.Transfer.CREATE_FOLDER:
        if add_folder_to_dtn(folder, dtn_conf) == 0:
            transfer.status = db.Transfer.IN_PROGRESS
            transfer.save()
    if transfer.status == db.Transfer.IN_PROGRESS:
        handle = handles.get(transfer.id)
        if handle is None:
            handle = transport.start_transfer(transfer)
            handles[transfer.id] = handle
        transfer_success = transport.transfer_success(handle)
        if transfer_success:
            LOG.debug("Transfer {} complete".format(transfer.id))
            transfer.status = db.Transfer.GET_ACKNOWLEDGMENT
            transfer.save()
            del handles[transfer.id]
        elif transfer_success == False:
            LOG.error("Transfer {} failed".format(transfer.id))
            del handles[transfer.id]
    if transfer.status == db.Transfer.GET_ACKNOWLEDGMENT:
        # TODO: Acknowledge transfer instead of using start_transfers
        LOG.debug("Transfer {} was to DTN, getting acknowledgement".format(transfer.id))
        api_url = dtn_conf['api']
        resp = requests.post(api_url + '/folders/{}/start_transfers'.format(folder.uuid))
        if resp.status_code == 200:
            transfer.delete_instance()


def add(folder, dtn):
    if dtn == conf.settings['dtnd']['name']:
        return
    try:
        transfer = db.Transfer.create(folder=folder, dtn=dtn, active=False)
    except peewee.IntegrityError:
        # Transfer already pending
        return
    return transfer


def add_all(uuid):
    folder = folders.get(uuid)
    if folder.home_dtn != conf.settings['dtnd']['name']:
        return
    dtns = set()
    folder_destinations = db.FolderDestination.select().where(
            db.FolderDestination.folder == folder)
    for folder_dst in folder_destinations:
        destination = folder_dst.destination
        dtn = conf.destinations[destination]['dtn']
        dtns.add(dtn)
    for dtn in dtns:
        add(folder, dtn)


def check():
    transfers = db.Transfer.select()
    for transfer in transfers:
        update(transfer)
