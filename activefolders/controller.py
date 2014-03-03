from uuid import UUID
from importlib import import_module
import os
import shutil
import activefolders.db as db
import activefolders.config as config

# Getting the correct transport adaptor
transport_module = "activefolders.transports.{}".format(
    config.config['dtnd']['transport'])
transport = import_module(transport_module)

transfers = {}


def folders():
    folders = {"folders": []}
    for folder in db.Folder.select().dicts():
        folders['folders'].append(folder)
    return folders


def folder(uuid):
    folder = db.Folder.select().where(db.Folder.uuid ** uuid).dicts().get()
    return folder


def add_folder(uuid):
    if valid_uuid(uuid):
        db.Folder.create(uuid=uuid)
        os.mkdir(config.config['dtnd']['storage_path'] + '/' + uuid)
    else:
        raise ValueError


def delete_folder(uuid):
    db.Folder.get(db.Folder.uuid ** uuid).delete_instance()
    shutil.rmtree(config.config['dtnd']['storage_path'] + '/' + uuid)


def start_transfer(uuid, dst):
    # Check if we know about this folder
    db.Folder.get(db.Folder.uuid ** uuid)

    # Form urls
    src = config.config['dtnd']['storage_path'] + '/' + uuid + '/'
    #if dst[-1] is not '/':
    #    dst += '/'
    dst += '/' + uuid + '/'

    # Init transfer and store its handle for future use
    handle = transport.start_transfer(src, dst)
    transfers[id(handle)] = handle
    return id(handle)


def valid_uuid(uuid):
    try:
        UUID(uuid)
        return True
    except ValueError:
        return False
