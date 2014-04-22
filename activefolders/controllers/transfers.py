import importlib
import peewee
import requests
import logging
import json
import activefolders.conf as conf
import activefolders.db as db
import activefolders.controllers.folders as folders

LOG = logging.getLogger(__name__)

handles = {}


def get_transport(transfer):
    if transfer.to_dtn:
        transport_name = 'gridftp_simple'
    else:
        dst_conf = conf.destinations[transfer.destination]
        transport_name = dst_conf['transport']
    transport_module = "activefolders.transports.{}".format(transport_name)
    transport = importlib.import_module(transport_module)
    return transport


def add_folder_to_dtn(folder, dtn_conf):
    url = dtn_conf['api'] + "/add_folder"
    headers = { 'Content-type': 'application/json' }
    destinations = folders.get_destinations(folder.uuid)
    destinations = list(destinations.keys())
    folder_data = {
        'uuid': folder.uuid,
        'home_dtn': conf.settings['dtnd']['name'],
        'destinations': destinations
    }
    LOG.info("Adding folder {} to {}".format(folder.uuid, url))
    resp = requests.post(url, data=json.dumps(folder_data), headers=headers)
    if resp.status_code == 201:
        return 0
    else:
        LOG.error("Adding folder {} to {} failed with error: {}".format(folder.uuid, url, resp.text))
        return 1


def start(transfer):
    if transfer.to_dtn:
        dst_conf = conf.dtns[transfer.destination]
    else:
        dst_conf = conf.destinations[transfer.destination]
    transport = get_transport(transfer)
    LOG.info("Transferring folder {} to {}".format(transfer.folder.uuid, dst_conf['url']))
    handle = transport.start_transfer(transfer.folder, dst_conf)
    handles[transfer.id] = handle


def update(transfer):
    dst_conf = conf.destinations[transfer.destination]
    if transfer.to_dtn:
        dst_conf = conf.dtns[dst_conf['dtn']]

    LOG.debug("Checking transfer {} for folder {} to {}, current status {}".format(transfer.id, transfer.folder.uuid, dst_conf['url'], transfer.status))

    if not transfer.active:
        try:
            db.Transfer.get(db.Transfer.folder==transfer.folder, db.Transfer.destination==transfer.destination, db.Transfer.active==True)
            LOG.debug("Transfer {} is still pending".format(transfer.id))
            return
        except peewee.DoesNotExist:
            transfer.active = True
            transfer.save()
            LOG.debug("Transfer {} is now active".format(transfer.id))

    if transfer.status == db.Transfer.PENDING and transfer.to_dtn:
        if add_folder_to_dtn(transfer.folder, dst_conf) == 0:
            transfer.status = db.Transfer.FOLDER_CREATED
            transfer.save()
    if transfer.status == db.Transfer.PENDING or transfer.status == db.Transfer.FOLDER_CREATED:
        start(transfer)
        transfer.status = db.Transfer.IN_PROGRESS
        transfer.save()
    if transfer.status == db.Transfer.IN_PROGRESS:
        handle = handles.get(transfer.id)
        if handle is None:
            start(transfer)
        else:
            transport = get_transport(transfer)
            if transport.transfer_success(handle) and transfer.to_dtn:
                # TODO: Acknowledge transfer instead of using start_transfers
                LOG.debug("Transfer {} to DTN complete, getting acknowledgement".format(transfer.id))
                api_url = dst_conf['api']
                requests.get(api_url + '/folders/{}/start_transfers'.format(transfer.folder.uuid))
                transfer.status = db.Transfer.ACKNOWLEDGED
                transfer.save()
            elif transport.transfer_success(handle):
                LOG.debug("Transfer {} to destination complete, deleting".format(transfer.id))
                transfer.delete_instance()
    if transfer.status == db.Transfer.ACKNOWLEDGED:
        LOG.info("Transfer {} to DTN acknowledged, deleting".format(transfer.id))
        transfer.delete_instance()


def add(folder, destination):
    dst_conf = conf.destinations[destination]
    try:
        if dst_conf['dtn'] == conf.settings['dtnd']['name']:
            transfer = db.Transfer.create(folder=folder, destination=destination, active=False, to_dtn=False)
        else:
            transfer = db.Transfer.create(folder=folder, destination=dst_conf['dtn'], active=False, to_dtn=True)
    except peewee.IntegrityError:
        # Transfer already pending
        return None
    return transfer


def add_all(folder):
    destinations = folders.get_destinations(folder.uuid)
    dtns = []
    for dst, dst_conf in destinations.items():
        # If sending to multiple destinations that belong to one DTN only add one transfer to that DTN
        if dst_conf['dtn'] in dtns:
            continue
        if dst_conf['dtn'] != conf.settings['dtnd']['name']:
            dtns.append(dst_conf['dtn'])
        add(folder, dst)


def check():
    transfers = db.Transfer.select()
    for transfer in transfers:
        update(transfer)
