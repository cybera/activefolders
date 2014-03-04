from uuid import uuid4
import activefolders.config as config
import activefolders.db as db
import activefolders.utils as utils


def set_test_config():
    config.config['dtnd']['storage_path'] = "/tmp"
    config.config['dtnd']['db_path'] = ":memory:"
    config.config['dtnd']['host'] = "localhost"
    config.config['dtnd']['listen_port'] = "8080"


def clear_database():
    db.Folder.delete().execute()


def populate_database(num_folders):
    """ Populate database while bypassing folder creation """
    uuids = []
    for i in range(0, num_folders):
        uuid = utils.coerce_uuid(uuid4().hex)
        db.Folder.create(uuid=uuid)
        uuids.append(uuid)
    return uuids
