from uuid import UUID
from activefolders.config import config
import os
import shutil
import activefolders.db as db
from importlib import import_module

# Getting the correct transport adaptor
transport_module = "activefolders.transports.{}".format(
    config['dtnd']['transport'])
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
        os.mkdir(config['dtnd']['storage_path'] + '/' + uuid)
        db.Folder.create(uuid=uuid)
    else:
        raise ValueError


def delete_folder(uuid):
    db.Folder.get(db.Folder.uuid ** uuid).delete_instance()
    shutil.rmtree(config['dtnd']['storage_path'] + '/' + uuid)


def start_transfer(uuid, dst):
    # Check if we know about this folder
    db.Folder.get(db.Folder.uuid ** uuid)

    # Form urls
    src = config['dtnd']['storage_path'] + '/' + uuid + '/'
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
