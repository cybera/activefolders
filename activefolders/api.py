import bottle
import peewee
import activefolders.controller as controller

@bottle.get('/folders')
def folders():
    """ Returns a list of all folders present on the DTN """
    folders = controller.folders()
    return folders

@bottle.get('/folders/<uuid>')
def folder(uuid):
    """ Returns metadata for a folder """
    try:
        folder = controller.folder(uuid)
    except peewee.DoesNotExist:
        bottle.abort(404)
    return folder

@bottle.post('/folders/<uuid>')
def add_folder(uuid):
    """ Adds a new folder to the DTN """
    try:
        controller.add_folder(uuid)
    except peewee.IntegrityError:
        return "Folder already exists"
    except ValueError:
        return "Invalid UUID"
    return "Folder added"

@bottle.delete('/folders/<uuid>')
def delete_folder(uuid):
    """ Deletes a folder from the DTN """
    try:
        controller.delete_folder(uuid)
    except peewee.DoesNotExist:
        bottle.abort(404)
    return "Folder deleted"

@bottle.post('/transfer/<uuid>')
def transfer(uuid):
    """ Transfers a folder to another DTN """
    dst = bottle.request.params.get('dst')
    try:
        controller.start_transfer(uuid, dst)
    except peewee.DoesNotExist:
        bottle.abort(404)
    return "Transfer initiated"

def start():
    bottle.run(host='localhost', port=8080, debug=True)
