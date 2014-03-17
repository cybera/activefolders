import importlib
import configparser
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


def start(folder):
    destinations = get_destinations(folder)
    for dst in destinations:
        # TODO: Check whether this is home or transit dtn
        transport_name = dst['transport']
        transport = get_transport(transport_name)
        db.Transfer.create(folder=folder, destination=dst)
        handle = transport.start_transfer(folder.path(), dst['url'])
        transfers[id(handle)] = handle


def check():
    """ Check all tranfers for failure and restart if needed """
