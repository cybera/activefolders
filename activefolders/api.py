from contextlib import contextmanager
import bottle
import peewee
import activefolders.controllers.folders as folders
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


@app.post('/create_folder')
def create_folder():
    """ Creates new folder on the DTN """
    folders.add()
    bottle.response.status = 201
    return "Folder added"


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


@app.delete('/folders/<uuid>')
def delete_folder(uuid):
    """ Deletes a folder from the DTN """
    with handle_errors():
        folders.remove(uuid)
    return "Folder deleted"


@app.get('/folders/<uuid>/delta')
def delta(uuid):
    pass


@app.put('/folders/<uuid>/upload')
def upload_file(uuid):
    pass


@app.post('/folders/<uuid>/fileops/create_dir')
def create_dir(uuid):
    path = bottle.request.query.path
    folders.create_dir(uuid, path)
    bottle.response.status = 201
    return "Directory created"


@app.post('/folders/<uuid>/fileops/delete')
def delete(uuid):
    path = bottle.request.query.path
    folders.delete(uuid, path)
    return "File/folder deleted"


@app.post('/folders/<uuid>/fileops/copy')
def copy(uuid):
    cur_path = bottle.request.query.cur_path
    new_path = bottle.request.query.new_path
    folders.copy(uuid, cur_path, new_path)
    return "File/folder copied"


@app.post('/folders/<uuid>/fileops/move')
def move(uuid):
    cur_path = bottle.request.query.cur_path
    new_path = bottle.request.query.new_path
    folders.move(uuid, cur_path, new_path)
    return "File/folder moved"


@app.get('/destinations')
def get_destinations():
    return conf.destinations


@app.get('/destinations/<name>')
def get_destination(name):
    try:
        dst = conf.destinations[name]
    except KeyError:
        bottle.abort(404, "Destination not found")
    return dst

@app.get('/folders/<uuid>/destinations')
def get_folder_destinations(uuid):
    with handle_errors():
        destinations = folders.get_destinations(uuid)
    return destinations


@app.post('/folders/<uuid>/destinations')
def add_folder_destination(uuid):
    dst_name = bottle.request.query.dst
    folders.add_destination(uuid, dst_name)
    return "Destination added"


@app.delete('/folders/<uuid>/destinations')
def remove_folder_destination(uuid):
    dst_name = bottle.request.query.dst
    folders.remove_destination(uuid, dst_name)
    return "Destination removed"


def start():
    app.run(host=conf.settings['dtnd']['host'], port=conf.settings['dtnd']['listen_port'], debug=True)
