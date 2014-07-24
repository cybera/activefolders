import peewee
import activefolders.db as db
import activefolders.conf as conf
import activefolders.controllers.folders as folders


def add(folder_destination):
    destination = folder_destination.destination
    dst_conf = conf.destinations[destination]
    if dst_conf['dtn'] != conf.settings['dtnd']['name']:
        return

    try:
        export = db.Export.create(folder_destination=folder_destination, active=False)
    except peewee.IntegrityError:
        # Export already pending
        return
    return export


def add_all(uuid):
    folder = folders.get(uuid)
    folder_destinations = db.FolderDestination.select().where(
            db.FolderDestination.folder == folder)
    for folder_dst in folder_destinations:
        add(folder_dst)
