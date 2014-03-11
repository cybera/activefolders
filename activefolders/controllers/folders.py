import os
import shutil
import activefolders.db as db
import activefolders.conf as conf
import activefolders.utils as utils


def get_all():
    folders = {"folders": []}
    for folder in db.Folder.select().dicts():
        folders['folders'].append(folder)
    return folders


def get(uuid):
    uuid = utils.coerce_uuid(uuid)
    folder = db.Folder.select().where(db.Folder.uuid == uuid).dicts().get()
    return folder


def add(uuid):
    uuid = utils.coerce_uuid(uuid)
    db.Folder.create(uuid=uuid)
    os.mkdir(conf.settings['dtnd']['storage_path'] + '/' + uuid)


def remove(uuid):
    uuid = utils.coerce_uuid(uuid)
    db.Folder.get(db.Folder.uuid == uuid).delete_instance()
    shutil.rmtree(conf.settings['dtnd']['storage_path'] + '/' + uuid)