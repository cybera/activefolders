from uuid import UUID
from activefolders.config import config
import os
import shutil
import activefolders.db as db

def folders():
    folders = { "folders": [] }
    for folder in db.Folder.select().dicts():
        folders['folders'].append(folder)
    return folders

def folder(uuid):
    folder = db.Folder.select().where(db.uuid ** uuid).dicts().get()
    return folder

def add_folder(uuid):
    if valid_uuid(uuid):
        db.Folder.create(uuid=uuid)
        os.mkdir(config['dtnd']['storage_path'] + '/' + uuid)
    else:
        raise ValueError

def delete_folder(uuid):
    db.Folder.get(db.uuid ** uuid).delete_instance()
    shutil.rmtree(config['dtnd']['storage_path'] + '/' + uuid)

def valid_uuid(uuid):
    try:
        UUID(uuid)
        return True
    except ValueError:
        return False
