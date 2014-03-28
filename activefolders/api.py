from contextlib import contextmanager
import bottle
import peewee
import activefolders.controllers.folders as folders
import activefolders.controllers.transfers as transfers
import activefolders.conf as conf

app = bottle.Bottle()


@contextmanager
def handle_errors():
    try:
        yield
    except ValueError:
        bottle.abort(400, "Invalid UUID")
    except peewee.IntegrityError:
        bottle.abort(403, "Folder already exists")
    except peewee.DoesNotExist:
        bottle.abort(404, "Folder not found")


@app.get('/folders')
def get_folders():
    """ Returns a list of all folders present on the DTN """
    all_folders = folders.get_all_dicts()
    return all_folders


@app.get('/folders/<uuid>')
def get_folder(uuid):
    """ Returns metadata for a folder """
    with handle_errors():
        folder = folders.get_dict(uuid)
    return folder


@app.post('/folders/<uuid>')
def add_folder(uuid):
    """ Adds a new folder to the DTN """
    with handle_errors():
        folders.add(uuid)
    bottle.response.status = 201
    return "Folder added"


@app.delete('/folders/<uuid>')
def delete_folder(uuid):
    """ Deletes a folder from the DTN """
    with handle_errors():
        folders.remove(uuid)
    return "Folder deleted"


@app.post('/transfer/<uuid>')
def transfer_folder(uuid):
    """ Transfers a folder to another DTN """
    with handle_errors():
        folder = folders.get(uuid)
        dst = bottle.request.query.dst
        transfer = transfers.add(folder, dst)
        transfers.start(transfer)
    return "Transfer initiated"


def start():
    app.run(host=conf.settings['dtnd']['host'], port=conf.settings['dtnd']['listen_port'], debug=True)
