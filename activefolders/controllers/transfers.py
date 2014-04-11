import importlib
import peewee
import activefolders.conf as conf
import activefolders.db as db

handles = {}


def get_transport(name):
    transport_module = "activefolders.transports.{}".format(name)
    transport = importlib.import_module(transport_module)
    return transport


def get_destinations(folder):
    """ Gets destination names from folder conf and returns full details """
    folder_dsts = db.FolderDestination.select().where(db.FolderDestination.folder==folder)
    destinations = []
    for dst in folder_dsts:
        destinations.append(dst.destination)
    return destinations


def start(transfer):
    # TODO: Fail if there's an existing transfer
    # TODO: If sending to a dtn, register folder through api
    dst_conf = conf.destinations[transfer.destination]
    transport_name = dst_conf['transport']
    transport = get_transport(transport_name)
    handle = transport.start_transfer(transfer.folder, dst_conf)
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
        transfer = db.Transfer.get(db.Transfer.id==transfer_id, db.Transfer.pending==False)
        dst = conf.destinations[transfer.destination]
        transport = get_transport(dst['transport'])
        if transport.transfer_success(handle):
            transfer.delete_instance()

    pending_transfers = db.Transfer.select().where(db.Transfer.pending==True)
    for transfer in pending_transfers:
        try:
            db.Transfer.get(db.Transfer.folder==transfer.folder, db.Transfer.destination==transfer.destination, db.Transfer.pending==False)
        except peewee.DoesNotExist:
            start(transfer)
