from contextlib import contextmanager
from uuid import UUID
import os
import bottle
import peewee
import json
import activefolders.controllers.folders as folders
import activefolders.controllers.transfers as transfers
import activefolders.controllers.exports as exports
import activefolders.controllers.results as results
import activefolders.conf as conf
import activefolders.db as db


class App(bottle.Bottle):
    def __init__(self, *args, **kwargs):
        db.init()
        super(App, self).__init__(*args, **kwargs)


app = App(autojson=False)


class JsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, db.JsonSerializer):
            return obj.to_json()
        return super(JsonEncoder, self).default(obj)


app.install(bottle.JSONPlugin(json_dumps=lambda s: json.dumps(s, cls=JsonEncoder)))


def uuid_filter(_):
    # TODO: Decide if we really need it in str
    regexp = r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'

    def to_python(match):
        return str(UUID(match))

    def to_url(string):
        return str(UUID(string))

    return regexp, to_python, to_url


app.router.add_filter('uuid', uuid_filter)


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
    uuid = folder_data['uuid']

    if folders.exists(uuid):
        bottle.response.status = 200
        folder = folders.get(uuid)
    else:
        bottle.response.status = 201
        folder = folders.add(uuid, folder_data['home_dtn'])

    results_for = folder_data.get('results_for')
    if results_for is not None:
        # TODO: Check results_folder doesn't already exist
        folder.results = True
        folder.save()
        parent = folders.get(results_for['folder'])
        folder_dst = db.FolderDestination.get(
            db.FolderDestination.folder == parent,
            db.FolderDestination.destination == results_for['destination'])
        folder_dst.results_folder = folder
        folder_dst.save()

    if 'destinations' in folder_data:
        # TODO: Figure out why destinations doesn't exist if it's empty
        old_destinations = folders.get_destinations(uuid)
        new_destinations = folder_data['destinations']
        for dst, dst_conf in new_destinations.items():
            if dst not in old_destinations:
                folders.add_destination(uuid, dst, dst_conf)
        for dst in old_destinations:
            if dst not in new_destinations:
                folders.remove_destination(uuid, dst)

    return "Folder added/updated"


@app.get('/folders')
def get_folders():
    """ Returns a list of all folders present on the DTN """
    return folders.get_all_dicts()


@app.get('/folders/<uuid:uuid>')
def get_folder(uuid):
    """ Returns metadata for a folder """
    with handle_errors():
        return folders.get_dict(uuid)


@app.delete('/folders/<uuid:uuid>')
def delete_folder(uuid):
    """ Deletes a folder from the DTN """
    with handle_errors():
        folders.remove(uuid)
    return "Folder deleted"


@app.get('/folders/<uuid:uuid>/delta')
def delta(uuid):
    pass


@app.post('/folders/<uuid:uuid>/files')
def upload_file(uuid):
    upload = bottle.request.files.get('upload')
    name, ext = os.path.splitext(upload.filename)
    try:
        folders.save_file(uuid, upload)
    except IOError:
        bottle.abort(403, "File already exists")
    return 'OK'


@app.put('/folders/<uuid:uuid>/files/<filepath:path>')
def put_file(uuid, filepath):
    if 'Content-Range' in bottle.request.headers:
        range_str = bottle.request.headers['Content-Range']
        offset = int(range_str.split(' ')[1].split('-')[0])
    else:
        offset = 0
    folders.put_file(uuid, path=filepath,
                     data=bottle.request.body, offset=offset)


@app.get('/folders/<uuid:uuid>/files/<filepath:path>')
def get_file(uuid, filepath):
    return folders.get_file(uuid, filepath, bottle.static_file)


@app.post('/folders/<uuid:uuid>/fileops/create_dir')
def create_dir(uuid):
    # TODO: Exception handling
    path = bottle.request.query.path
    if not path:
        bottle.abort(400)
    folders.create_dir(uuid, path)


@app.post('/folders/<uuid:uuid>/fileops/delete')
def delete(uuid):
    # TODO: Exception handling
    path = bottle.request.query.path
    if not path:
        bottle.abort(400)
    folders.delete(uuid, path)
    return "File/folder deleted"


@app.post('/folders/<uuid:uuid>/fileops/copy')
def copy(uuid):
    # TODO: Exception handling
    src_path = bottle.request.query.src_path
    dst_path = bottle.request.query.dst_path
    if not src_path or not dst_path:
        bottle.abort(400)
    folders.copy(uuid, src_path, dst_path)
    return "File/folder copied"


@app.post('/folders/<uuid:uuid>/fileops/move')
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


@app.get('/folders/<uuid:uuid>/destinations')
def get_folder_destinations(uuid):
    with handle_errors():
        destinations = folders.get_destinations(uuid)
    return destinations


@app.post('/folders/<uuid:uuid>/destinations')
def add_folder_destination(uuid):
    destination = bottle.request.query.dst
    body = bottle.request.json
    with handle_errors():
        folders.add_destination(uuid, destination, body)
    return "Destination added"


@app.delete('/folders/<uuid:uuid>/destinations')
def remove_folder_destination(uuid):
    destination = bottle.request.query.dst
    with handle_errors():
        folders.remove_destination(uuid, destination)
    return "Destination removed"


@app.get('/folders/<uuid:uuid>/results')
def get_available_results(uuid):
    with handle_errors():
        available_results = results.get_all(uuid)
    return available_results


@app.get('/folders/<uuid:uuid>/check_results')
def check_results(uuid):
    results.check_all(uuid)


@app.post('/folders/<uuid:uuid>/start_transfers')
def start_transfers(uuid):
    transfers.add_all(uuid)
    exports.add_all(uuid)
    transfers.check(uuid)
    exports.check()
