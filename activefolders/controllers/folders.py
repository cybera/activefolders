from uuid import uuid4
import importlib
import os
import json
import activefolders.db as db
import activefolders.conf as conf
import activefolders.utils as utils

STORAGE_MODULE = "activefolders.storage.{}".format(
        conf.settings['dtnd']['storage'])
storage = importlib.import_module(STORAGE_MODULE)


def get_all():
    folders = db.Folder.select()
    return folders


def get_all_dicts():
    folders = { "folders": [] }
    for folder in db.Folder.select().dicts():
        folders['folders'].append(folder)
    return folders


def get(uuid):
    folder = db.Folder.get(db.Folder.uuid == uuid)
    return folder


def get_dict(uuid):
    folder = db.Folder.select().where(db.Folder.uuid == uuid).dicts().get()
    return folder


def exists(uuid):
    return db.Folder.select().where(db.Folder.uuid == uuid).count() == 1


@db.database.commit_on_success
def add(uuid=None, home_dtn=conf.settings['dtnd']['name']):
    if uuid is None:
        uuid = str(uuid4())
    folder = db.Folder.create(uuid=uuid, home_dtn=home_dtn)
    storage.create_folder(folder)
    return folder


@db.database.commit_on_success
def remove(uuid):
    # TODO: Remove outstanding transfers
    folder = get(uuid)
    storage.delete_folder(folder)
    folder.delete_instance()


def list_files(uuid):
    folder = get(uuid)
    files = { 'files': [] }

    for root, _, files in os.walk(folder.path()):
        for f in files:
            path = os.path.join(root, f)
            relative_path = path[len(folder.path()):].lstrip('/')
            files['files'].append(relative_path)

    return files


def save_file(uuid, upload):
    folder = get(uuid)
    storage.save_file(folder, upload)


def put_file(uuid, path, data, offset):
    folder = get(uuid)
    path = path.split('/')
    filename = path.pop()
    path = '/'.join(path)
    storage.create_dir(folder, path)
    storage.put_file(folder, path, filename, data, offset)


def get_file(uuid, path, callback):
    folder = get(uuid)
    return storage.get_file(folder, path, callback)


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
    destinations = {}
    folder_destinations = db.FolderDestination.select().where(
            db.FolderDestination.folder == folder)
    for folder_dst in folder_destinations:
        dst_conf = dict(conf.destinations[folder_dst.destination])
        destinations[folder_dst.destination] = dst_conf
        destinations[folder_dst.destination]['credentials'] = folder_dst.credentials
        destinations[folder_dst.destination]['result_files'] = folder_dst.result_files
    return destinations


def add_destination(uuid, destination, body):
    folder = get(uuid)
    credentials = body['credentials']
    # TODO: Verify results correctness
    result_files = body.get('result_files')
    check_for_results = body.get('check_for_results', False)
    transport = utils.get_transport_module(destination)
    if set(transport.CREDENTIALS) != set(credentials):
        # TODO: Raise an error
        return
    folder_destination = db.FolderDestination.create(folder=folder,
            destination=destination, credentials=credentials,
            result_files=result_files, check_for_results=check_for_results)
    return folder_destination


def remove_destination(uuid, destination):
    folder = get(uuid)
    if destination in conf.destinations:
        db.FolderDestination.delete().where(
                db.FolderDestination.folder == folder,
                db.FolderDestination.destination == destination).execute()
    else:
        raise KeyError
