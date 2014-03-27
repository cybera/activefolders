import os
import shutil
import datetime
import threading
import activefolders.db as db
import activefolders.conf as conf
import activefolders.controllers.transfers as transfers
import activefolders.utils as utils


def get_all():
    folders = db.Folder.select()
    return folders


def get_all_dicts():
    folders = {"folders": []}
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
def add(uuid):
    uuid = utils.coerce_uuid(uuid)
    folder = db.Folder.create(uuid=uuid)
    os.mkdir(conf.settings['dtnd']['storage_path'] + '/' + uuid)
    return folder


@db.database.commit_on_success
def remove(uuid):
    # TODO: Remove outstanding transfers
    uuid = utils.coerce_uuid(uuid)
    db.Folder.get(db.Folder.uuid == uuid).delete_instance()
    shutil.rmtree(conf.settings['dtnd']['storage_path'] + '/' + uuid)


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
