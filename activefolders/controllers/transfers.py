import peewee
import logging
import activefolders.conf as conf
import activefolders.db as db
import activefolders.controllers.folders as folders
import activefolders.transports.gridftp_simple as transport
import activefolders.requests as requests

LOG = logging.getLogger(__name__)

handles = {}


def add(folder, dtn):
    if dtn == conf.settings['dtnd']['name']:
        return
    try:
        transfer = db.Transfer.create(folder=folder, dtn=dtn, active=False)
    except peewee.IntegrityError:
        # Transfer already pending
        return
    return transfer


def add_all(uuid):
    folder = folders.get(uuid)
    if folder.home_dtn != conf.settings['dtnd']['name']:
        return
    dtns = set()
    folder_destinations = db.FolderDestination.select().where(
            db.FolderDestination.folder == folder)
    for folder_dst in folder_destinations:
        destination = folder_dst.destination
        dtn = conf.destinations[destination]['dtn']
        dtns.add(dtn)
    for dtn in dtns:
        add(folder, dtn)


def check(uuid=None):
    if uuid is None:
        transfers = db.Transfer.select()
    else:
        folder = folders.get(uuid)
        transfers = db.Transfer.select().where(db.Transfer.folder == folder)

    for transfer in transfers:
        update(transfer)
