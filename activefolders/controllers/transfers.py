import importlib
import configparser
import peewee
import threading
import activefolders.conf as conf
import activefolders.db as db

handles = {}


def get_transport(name):
    transport_module = "activefolders.transports.{}".format(name)
    transport = importlib.import_module(transport_module)
    return transport


def get_destinations(folder):
    """ Gets destination names from folder conf and returns full details """
    folder_dsts = configparser.ConfigParser()
    folder_dsts.read(folder.path() + '/folder.conf')
    destinations = []
    for dst_name, dst_conf in folder_dsts:
        dst = conf.destinations.get(dst_name)
        if dst is not None:
            destinations.append(dst)
    return destinations


def start(transfer):
    # TODO: Don't fail if there's an existing transfer
    transport_name = conf.destinations[transfer.destination]['transport']
    transport = get_transport(transport_name)
    handle = transport.start_transfer(transfer.folder.path(), transfer.destination['url'])
    handles[transfer.id] = handle
    transfer.pending = False
    transfer.save()


def add(folder, destination):
    # TODO: Check whether this is home or transit dtn
    try:
        transfer = db.Transfer.create(folder=folder, destination=destination, pending=True)
    except peewee.IntegrityError:
        # Transfer already pending
        return
    return transfer


def add_all(folder):
    destinations = get_destinations(folder)
    for dst in destinations:
        add(folder, dst)


def check():
    """ Check all current and pending transfers """
    for transfer_id, handle in handles:
        transfer = db.Transfer.get(db.Transfer.id==transfer_id)
        dst = conf.destinations[transfer.destination]
        transport = get_transport(dst['transport'])
        if transport.transfer_success(handle):
            transfer.delete_instance()

    pending_transfers = db.Transfer.select().where(db.Transfer.pending==True)
    for transfer in pending_transfers:
        try:
            db.Transfer.get(db.Transfer.folder==transfer.folder, db.Transfer.destination==transfer.dst, db.Transfer.pending==False)
        except peewee.DoesNotExist:
            start(transfer)
    threading.Timer(20, check).start()
