import os
import shutil
import datetime
import activefolders.db as db
import activefolders.conf as conf
import activefolders.controllers.transfers as transfers
import activefolders.utils as utils


def get_all():
    # folders = {"folders": []}
    # for folder in db.Folder.select().dicts():
    #     folders['folders'].append(folder)
    # return folders
    folders = db.Folder.select()
    return folders


def get(uuid):
    uuid = utils.coerce_uuid(uuid)
    # folder = db.Folder.select().where(db.Folder.uuid == uuid).dicts().get()
    folder = db.Folder.get(db.Folder.uuid == uuid)
    return folder


@db.database.commit_on_success
def add(uuid):
    uuid = utils.coerce_uuid(uuid)
    folder = db.Folder.create(uuid=uuid)
    os.mkdir(conf.settings['dtnd']['storage_path'] + '/' + uuid)
    return folder


@db.database.commit_on_success
def remove(uuid):
    uuid = utils.coerce_uuid(uuid)
    db.Folder.get(db.Folder.uuid == uuid).delete_instance()
    shutil.rmtree(conf.settings['dtnd']['storage_path'] + '/' + uuid)


def check():
    """ Initiate transfers on any dirty folders """
    folders = db.Folder.select()
    for folder in folders:
        time_delta = datetime.datetime.now() - folder.last_change
        if folder.dirty and time_delta.total_seconds() > 60:
            transfers.start(folder)
