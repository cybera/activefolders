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
        self.uuids = []

    def populate_database(self):
        for i in range(1, 5):
            uuid = uuid4()
            db.Folder.create(uuid=uuid)
            self.uuids.appent(uuid)

    def test_folders(self):
        folders = controller.folders()
        self.assertEqual(len(folders), 0)
        self.populate_database()
        folders = controller.folders()
        self.assertEqual(len(folders), len(self.uuids))
        for folder in folders:
            self.assertTrue(folder.uuid in self.uuids)

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
        self.assertRaises(peewee.IntegrityError, controller.add_folder, uuid)
        self.assertRaises(ValueError, controller.add_folder, 0)

    def test_delete_folder(self):
        uuid = uuid4()
        self.assertRaises(peewee.IntegrityError, controller.delete_folder, uuid)
        self.populate_database()
        try:
            controller.delete_folder(self.uuids[0])
        except:
            self.fail("delete_folder() raised an exception unexpectedly")
        new_uuids = db.Folder.select(db.Folder.uuid)
        assertTrue(self.uuids[0] not in new_uuids)

    def test_start_transfer(self):
        uuid = uuid4()
        self.assertRaises(peewee.IntegrityError, controller.start_transfer, uuid, "/tmp")

    def test_valid_uuid(self):
        uuid = uuid4()
        self.assertTrue(controller.valid_uuid(uuid))
        self.assertFalse(controller.valid_uuid(0))
