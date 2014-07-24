import activefolders.db as db
import activefolders.controllers.folders as folders


def get(uuid, destination):
    """ Returns results for specific destination for folder specified by uuid """
    folder = folders.get(uuid)
    folder_dst = db.FolderDestination.get(
        db.FolderDestination.folder == folder,
        db.FolderDestination.destination == destination)

    return folder_dst.results_folder


def get_all(uuid):
    """ Returns all available results folders """
    folder = folders.get(uuid)
    folder_dsts = db.FolderDestination.select().where(
        db.FolderDestination.folder == folder)
    results = {}

    for folder_dst in folder_dsts:
        dst = folder_dst.destination
        results[dst] = folder_dst.results_folder.uuid if folder_dst.results_folder else None

    return results
