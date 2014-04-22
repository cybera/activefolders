from contextlib import contextmanager
import os
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


@app.post('/add_folder')
def add_folder():
    """ Adds existing folder from another DTN """
    folder_data = bottle.request.json
    folder = folders.add(folder_data['uuid'])
    folder.home_dtn = folder_data['home_dtn']
    folder.save()
    if 'destinations' in folder_data:
        for dst in folder_data['destinations']:
            folders.add_destination(folder_data['uuid'], dst)
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


@app.post('/folders/<uuid>/files')
def upload_file(uuid):
    upload = bottle.request.files.get('upload')
    name, ext = os.path.splitext(upload.filename)
    try:
        folders.save_file(uuid, upload)
    except IOError:
        bottle.abort(403, "File already exists")
    return 'OK'


@app.put('/folders/<uuid>/files/<filepath:path>')
def put_file(uuid, filepath):
    if 'Content-Range' in bottle.request.headers:
        range_str = bottle.request.headers['Content-Range']
        offset = int(range_str.split(' ')[1].split('-')[0])
    else:
        offset = 0
    folders.put_file(uuid, path=filepath, data=bottle.request.body, offset=offset)


@app.get('/folders/<uuid>/files/<filepath:path>')
def get_file(uuid, filepath):
    return folders.get_file(uuid, filepath, bottle.static_file)


@app.post('/folders/<uuid>/fileops/create_dir')
def create_dir(uuid):
    # TODO: Exception handling
    path = bottle.request.query.path
    if not path:
        bottle.abort(400)
    folders.create_dir(uuid, path)


@app.post('/folders/<uuid>/fileops/delete')
def delete(uuid):
    # TODO: Exception handling
    path = bottle.request.query.path
    if not path:
        bottle.abort(400)
    folders.delete(uuid, path)
    return "File/folder deleted"


@app.post('/folders/<uuid>/fileops/copy')
def copy(uuid):
    # TODO: Exception handling
    src_path = bottle.request.query.src_path
    dst_path = bottle.request.query.dst_path
    if not src_path or not dst_path:
        bottle.abort(400)
    folders.copy(uuid, src_path, dst_path)
    return "File/folder copied"


@app.post('/folders/<uuid>/fileops/move')
def move(uuid):
    # TODO: Exception handling
    src_path = bottle.request.query.src_path
    dst_path = bottle.request.query.dst_path
    if not src_path or not dst_path:
        bottle.abort(400)
    folders.move(uuid, src_path, dst_path)
    return "File/folder moved"


@app.get('/destinations')
def get_destinations():
    return conf.destinations._sections


@app.get('/destinations/<name>')
def get_destination(name):
    with handle_errors():
        dst = dict(conf.destinations[name].items())
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


@app.post('/folders/<uuid>/start_transfers')
def start_transfers(uuid):
    with handle_errors():
        folder = folders.get(uuid)
    transfers.add_all(folder)
    transfers.check()


def start():
    app.run(host=conf.settings['dtnd']['host'], port=conf.settings['dtnd']['listen_port'], debug=True)
