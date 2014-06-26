import activefolders.db as db
import activefolders.conf as conf
import activefolders.requests as requests
import activefolders.controllers.folders as folders
import activefolders.controllers.transfers as transfers
import activefolders.utils as utils


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


def check(folder_destination):
    transport_module = utils.get_transport(folder_destination.destination)
    transport = transport_module.Transport(folder_destination)

    if folder_destination.results_folder is None:
        results_folder = folders.add()
        results_folder.results = True
        results_folder.save()
        folder_destination.results_folder = results_folder
        folder_destination.save()

    transport.get_results(folder_destination)
    #folder_destination.results_retrieved = True
    folder_destination.save()
    results_folder = folder_destination.results_folder
    home_dtn = folder_destination.folder.home_dtn
    transfers.add(results_folder, home_dtn)
    transfers.check(results_folder.uuid)


def check_all(uuid=None):
    if uuid is None:
        folder_dsts = db.FolderDestination.select().where(
                db.FolderDestination.results_retrieved == False)
    else:
        folder = folders.get(uuid)
        folder_dsts = db.FolderDestination.select().where(
                db.FolderDestination.results_retrieved == False,
                db.FolderDestination.folder == folder)

    for folder_dst in folder_dsts:
        dst_dtn = conf.destinations[folder_dst.destination]['dtn']
        if dst_dtn == conf.settings['dtnd']['name']:
            check(folder_dst)
        else:
            request = requests.CheckResultsRequest(conf.dtns[dst_dtn], folder_dst.folder)
            request.execute()
