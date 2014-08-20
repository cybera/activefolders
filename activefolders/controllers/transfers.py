import peewee
import activefolders.conf as conf
import activefolders.db as db
import activefolders.controllers.folders as folders


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

    dtns = folders.get_dtns(folder)
    for dtn in dtns:
        add(folder, dtn)
