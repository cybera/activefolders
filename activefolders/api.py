from contextlib import contextmanager
import os
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
    except KeyError:
        bottle.abort(404, "Destination not found")
    except peewee.IntegrityError:
        bottle.abort(403, "Folder already exists")
    except peewee.DoesNotExist:
        bottle.abort(404, "Folder not found")


@app.post('/create_folder')
def create_folder():
    """ Creates new folder on the DTN """
    folder = folders.add()
    bottle.response.status = 201
    return folder.uuid


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
    upload = bottle.request.files.get('upload')
    name, ext = os.path.splitext(upload.filename)
    save_path = "/tmp/"
    upload.save(save_path)  # appends upload.filename automatically
    return 'OK'


@app.post('/folders/<uuid>/fileops/create_dir')
def create_dir(uuid):
    # TODO: Exception handling
    path = bottle.request.query.path
    folders.create_dir(uuid, path)


@app.post('/folders/<uuid>/fileops/delete')
def delete(uuid):
    # TODO: Exception handling
    path = bottle.request.query.path
    folders.delete(uuid, path)
    return "File/folder deleted"


@app.post('/folders/<uuid>/fileops/copy')
def copy(uuid):
    # TODO: Exception handling
    src_path = bottle.request.query.src_path
    dst_path = bottle.request.query.dst_path
    folders.copy(uuid, src_path, dst_path)
    return "File/folder copied"


@app.post('/folders/<uuid>/fileops/move')
def move(uuid):
    # TODO: Exception handling
    src_path = bottle.request.query.src_path
    dst_path = bottle.request.query.dst_path
    folders.move(uuid, src_path, dst_path)
    return "File/folder moved"


@app.get('/destinations')
def get_destinations():
    return conf.destinations


@app.get('/destinations/<name>')
def get_destination(name):
    with handle_errors():
        dst = conf.destinations[name]
    return dst

@app.get('/folders/<uuid>/destinations')
def get_folder_destinations(uuid):
    with handle_errors():
        destinations = folders.get_destinations(uuid)
    return destinations


@app.post('/folders/<uuid>/destinations')
def add_folder_destination(uuid):
    dst_name = bottle.request.query.dst
    with handle_errors():
        folders.add_destination(uuid, dst_name)
    return "Destination added"


@app.delete('/folders/<uuid>/destinations')
def remove_folder_destination(uuid):
    dst_name = bottle.request.query.dst
    with handle_errors():
        folders.remove_destination(uuid, dst_name)
    return "Destination removed"


def start():
    app.run(host=conf.settings['dtnd']['host'], port=conf.settings['dtnd']['listen_port'], debug=True)
