from contextlib import contextmanager
import bottle
import peewee
import activefolders.controller as controller
import activefolders.config as config

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
def folders():
    """ Returns a list of all folders present on the DTN """
    folders = controller.folders()
    return folders


@app.get('/folders/<uuid>')
def folder(uuid):
    """ Returns metadata for a folder """
    with handle_errors():
        folder = controller.folder(uuid)
    return folder


@app.post('/folders/<uuid>')
def add_folder(uuid):
    """ Adds a new folder to the DTN """
    with handle_errors():
        controller.add_folder(uuid)
    bottle.response.status = 201
    return "Folder added"


@app.delete('/folders/<uuid>')
def delete_folder(uuid):
    """ Deletes a folder from the DTN """
    with handle_errors():
        controller.delete_folder(uuid)
    return "Folder deleted"


@app.post('/transfer/<uuid>')
def transfer(uuid):
    """ Transfers a folder to another DTN """
    dst = bottle.request.params.get('dst')
    with handle_errors():
        controller.start_transfer(uuid, dst)
    return "Transfer initiated"


def start():
    app.run(host=config.config['dtnd']['host'], port=config.config['dtnd']['listen_port'], debug=True)
