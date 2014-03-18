import importlib
import configparser
import peewee
import activefolders.conf as conf
import activefolders.db as db

transfers = {}


def get_transport(name):
    transport_module = "activefolders.transports.{}".format(name)
    transport = importlib.import_module(transport_module)
    return transport


def get_destinations(folder):
    """ Gets destinations names from folder conf and returns full details """
    folder_dsts = configparser.ConfigParser()
    folder_dsts.read(folder.path() + '/folder.conf')
    destinations = []
    for dst_name in folder_dsts:
        dst = conf.destinations.get(dst_name)
        if dst is not None:
            destinations.append(dst)
    return destinations


def start(transfer):
    # TODO: Don't fail if there's an existing transfer
    transport_name = conf.destinations[transfer.destination]['transport']
    transport = get_transport(transport_name)
    handle = transport.start_transfer(transfer.folder.path(), transfer.destination['url'])
    transfers[id(handle)] = handle
    transfer.pending = False
    transfer.save()


def add(folder, destination):
    # TODO: Check whether this is home or transit dtn
    try:
        db.Transfer.create(folder=folder, destination=destination, pending=True)
    except peewee.IntegrityError:
        # Transfer already pending
        return


def add_all(folder):
    destinations = get_destinations(folder)
    for dst in destinations:
        add(folder, dst)


def check():
    """ Check all tranfers for failure and initiate pending ones """
    active_transfers = db.Transfer.select().where(db.Transfer.pending=False)
    pending_transfers = db.Transfer.select().where(db.Transfer.pending=True)
    for transfer in active_transfers:
        # TODO: Check status
        pass
    for transfer in pending_transfers:
        try:
            active_transfer = db.Transfer.get(db.Transfer.folder=transfer.folder, db.Transfer.destination=transfer.dst, pending=False)
        except peewee.DoesNotExist:
            start(transfer)
