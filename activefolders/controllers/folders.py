from uuid import uuid4
import datetime
import threading
import importlib
import activefolders.db as db
import activefolders.conf as conf
import activefolders.controllers.transfers as transfers
import activefolders.utils as utils

STORAGE_MODULE = "activefolders.storage.{}".format(conf.settings['dtnd']['storage'])
storage = importlib.import_module(STORAGE_MODULE)


def get_all():
    folders = db.Folder.select()
    return folders


def get_all_dicts():
    folders = { "folders": [] }
    for folder in db.Folder.select().dicts():
        folder['last_changed'] = str(folder['last_changed'])
        folders['folders'].append(folder)
    return folders


def get(uuid):
    uuid = utils.coerce_uuid(uuid)
    folder = db.Folder.get(db.Folder.uuid == uuid)
    return folder


def get_dict(uuid):
    uuid = utils.coerce_uuid(uuid)
    folder = db.Folder.select().where(db.Folder.uuid == uuid).dicts().get()
    folder['last_changed'] = str(folder['last_changed'])
    return folder


@db.database.commit_on_success
def add(uuid=None):
    if uuid is None:
        uuid = str(uuid4())
    uuid = utils.coerce_uuid(uuid)
    folder = db.Folder.create(uuid=uuid)
    storage.create_folder(folder)
    return folder


@db.database.commit_on_success
def remove(uuid):
    # TODO: Remove outstanding transfers
    folder = get(uuid)
    folder.delete_instance()
    storage.delete_folder(folder.path())


def save_file(uuid, upload):
    folder = get(uuid)
    storage.save_file(folder, upload)


def store(uuid, path, data, offset):
    folder = get(uuid)
    path = path.split('/')
    filename = path.pop()
    path = '/'.join(path)
    storage.create_dir(folder, path)
    storage.store(folder, path, filename, data, offset)


def create_dir(uuid, path):
    folder = get(uuid)
    storage.create_dir(folder, path)


def delete(uuid, path):
    folder = get(uuid)
    storage.delete(folder, path)


def copy(uuid, src_path, dst_path):
    folder = get(uuid)
    storage.copy(folder, src_path, dst_path)


def move(uuid, src_path, dst_path):
    folder = get(uuid)
    storage.move(folder, src_path, dst_path)


def get_destinations(uuid):
    folder = get(uuid)
    dst_dict = { "destinations": [] }
    destinations = db.FolderDestination.select().where(db.FolderDestination.folder == folder)
    for dst in destinations:
        dst_dict['destinations'].append(dst.destination)
    return dst_dict


def add_destination(uuid, dst_name):
    folder = get(uuid)
    if dst_name in conf.destinations:
        db.FolderDestination.create(folder=folder, destination=dst_name)
    else:
        raise KeyError


def remove_destination(uuid, dst_name):
    folder = get(uuid)
    if dst_name in conf.destinations:
        db.FolderDestination.delete().where(db.FolderDestination.folder == folder, db.FolderDestination.destination == dst_name)
    else:
        raise KeyError


def check():
    """ Initiate transfers on any dirty folders """
    folders = db.Folder.select()
    for folder in folders:
        time_delta = datetime.datetime.now() - folder.last_changed
        if folder.dirty and time_delta.total_seconds() > 60:
            transfers.add_all(folder)
            folder.dirty = False
            folder.save()
    threading.Timer(20, check).start()
