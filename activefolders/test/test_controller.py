from uuid import uuid4
import peewee
import unittest as test
import activefolders.config as config
import activefolders.db as db
import activefolders.controller as controller

class ControllerTest(test.TestCase):
    uuids = None

    def setUp(self):
        config.config['dtnd']['storage_path'] = "/tmp"
        config.config['dtnd']['db_path'] = ":memory:"
        db.init()
        uuids = []

    def populate_database(self):
        for i in range(1, 5):
            uuid = uuid4()
            db.Folder.create(uuid=uuid)
            uuids.appent(uuid)

    def test_folders(self):
        folders = controller.folders()
        self.assertEqual(len(folders), 0)
        self.populate_database()
        folders = controller.folders()
        self.assertEqual(len(folders), len(uuids))
        for folder in folders:
            self.assertTrue(folder.uuid in uuids)

    def test_folder(self):
        uuid = uuid4()
        self.assertRaises(peewee.IntegrityError, controller.folder, uuid)
        self.populate_database()
        try:
            folder = controller.folder(uuid[0])
        except:
            self.fail("folder() raised an exception unexpectedly")

    def test_add_folder(self):
        uuid = uuid4()
        try:
            controller.add_folder(uuid)
        except:
            self.fail("add_folder() raised an exception unexpectedly")
