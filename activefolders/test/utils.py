from uuid import uuid4
import activefolders.config as config
import activefolders.db as db

def set_test_config():
    config.config['dtnd']['storage_path'] = "/tmp"
    config.config['dtnd']['db_path'] = ":memory:"
    config.config['dtnd']['host'] = "localhost"
    config.config['dtnd']['listen_port'] = "8080"

def populate_database():
    uuids = []
    for i in range(1, 5):
        uuid = uuid4().hex
        db.Folder.create(uuid=uuid)
        uuids.append(uuid)
    return uuids
