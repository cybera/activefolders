import logging
import importlib
import peewee
import activefolders.db as db
import activefolders.conf as conf
import activefolders.controllers.folders as folders
import activefolders.utils as utils

LOG = logging.getLogger(__name__)

handles = {}


def update(export):
    folder = export.folder_destination.folder
    destination = export.folder_destination.destination
    dst_conf = conf.destinations[destination]

    LOG.debug("Updating export {} for folder {} to {}, active: {}".format(
        export.id, folder.uuid, dst_conf['url'], export.active))

    if not export.active:
        try:
            db.Export.get(db.Export.folder_destination==export.folder_destination, db.Export.active==True)
            LOG.debug("Export {} is still pending".format(export.id))
            return
        except peewee.DoesNotExist:
            export.active = True
            export.save()
            LOG.debug("Export {} is now active".format(export.id))

    transport = utils.get_transport(destination)
    handle = handles.get(export.id)
    if handle is None:
        LOG.debug("No handle found for export {}, starting new export".format(export.id))
        handle = transport.start_export(export)
        handles[export.id] = transport.start_export(export)

    export_success = transport.success(handle)
    if export_success:
        LOG.debug("Export {} complete".format(export.id))
        del handles[export.id]
        export.delete_instance()
    elif export_success == False:
        LOG.error("Export {} failed".format(export.id))
        del handles[export.id]
    else:
        LOG.debug("Export {} in progress".format(export.id))


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


def check():
    exports = db.Export.select()
    for export in exports:
        update(export)
