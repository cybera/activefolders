import importlib
import peewee
import requests
import activefolders.conf as conf
import activefolders.db as db
import activefolders.controllers.folders as folders

handles = {}


def get_transport(name):
    transport_module = "activefolders.transports.{}".format(name)
    transport = importlib.import_module(transport_module)
    return transport


def add_folder_to_dtn(folder, dtn_conf):
    url = dtn_conf['url'] + "/add_folder"
    dsts = folders.get_destinations(folder.uuid)
    folder_info = { 'folder': {} }
    folder_info['folder']['uuid'] = folder.uuid
    folder_info['folder']['home_dtn'] = conf.settings['dtnd']['name']
    folder_info['folder']['destinations'] = list(dsts.keys())
    resp = requests.post(url, data=folder_info)


def start(transfer):
    if transfer.is_dtn:
        dst_conf = conf.dtns[transfer.destination]
        transport = get_transport('gridftp_simple')
    else:
        dst_conf = conf.destinations[transfer.destination]
        transport_name = dst_conf['transport']
        transport = get_transport(transport_name)
    handle = transport.start_transfer(transfer.folder, dst_conf)
    handles[transfer.id] = handle


def update(transfer):
    dst_conf = conf.destinations[transfer.id]
    if transfer.is_dtn:
        dtn_conf = conf.dtns[dst_conf['dtn']]

    if not transfer.active:
        try:
            db.Transfer.get(db.Transfer.folder==transfer.folder, db.Transfer.destination==transfer.destination, db.Transfer.active==True)
            return
        except peewee.DoesNotExist:
            transfer.active = True
            transfer.save()

    if transfer.status == db.Transfer.PENDING and transfer.is_dtn:
        add_folder_to_dtn(transfer.folder, dtn_conf)
        transfer.status = db.Transfer.FOLDER_CREATED
        transfer.save()
    if transfer.status == db.Transfer.PENDING or transfer.status == db.Transfer.FOLDER_CREATED:
        start(transfer)
        transfer.status = db.Transfer.IN_PROGRESS
        transfer.save()
    if transfer.status == db.Transfer.IN_PROGRESS:
        handle = handles.get(transfer.id)
        transport = get_transport(dst_conf['transport'])
        if handle is None:
            start(transfer)
        else:
            if transport.transfer_success(handle):
                # TODO: Acknowledge transfer
                if transfer.is_dtn:
                    url = dtn_conf['url']
                else:
                    url = dst_conf['url']
                requests.get(url + '/folders/{}/start_transfers'.format(transfer.folder.uuid))
                transfer.status = db.Transfer.ACKNOWLEDGED
                transfer.save()
    if transfer.status == db.Transfer.ACKNOWLEDGED:
        transfer.delete_instance()


def add(folder, destination):
    try:
        if destination['dtn'] == conf.settings['dtnd']['name']:
            transfer = db.Transfer.create(folder=folder, destination=destination, active=False, is_dtn=False)
        else:
            transfer = db.Transfer.create(folder=folder, destination=destination['dtn'], active=False, is_dtn=True)
    except peewee.IntegrityError:
        # Transfer already pending
        return None
    return transfer


def add_all(folder):
    destinations = folders.get_destinations(folder)
    dtns = []
    for dst in destinations:
        # If sending to multiple destinations that belong to one DTN only add one transfer to that DTN
        if dst['dtn'] in dtns:
            continue
        if dst['dtn'] != conf.settings['dtnd']['name']:
            dtns.append(dst['dtn'])
        add(folder, dst)


def check():
    transfers = db.Transfer.select()
    for transfer in transfers:
        update(transfer)
