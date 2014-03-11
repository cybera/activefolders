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
    destinations = configparser.ConfigParser(folder.path())
    return destinations


def start(folder):
    destinations = get_destinations(folder)

    for dst_name, dst_config in destinations:
        transport_name = conf.destinations[dst_name]['transport']
        transport = get_transport(transport_name)
        db.Transfer.create(folder=folder, destination=dst_name)
        handle = transport.start_transfer(folder.path(), dst_config['url'])
        transfers[id(handle)] = handle


def check():
    """ Check status of all transfers and restart if needed """
