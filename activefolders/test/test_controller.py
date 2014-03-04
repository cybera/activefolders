from uuid import uuid4
import peewee
import unittest as test
import activefolders.db as db
import activefolders.controller as controller
import activefolders.test.utils as utils

class ControllerTest(test.TestCase):
    uuids = None

    @classmethod
    def setUpClass(cls):
        utils.set_test_config()
        db.init()

    def setUp(self):
        self.uuids = None

    def test_folders(self):
        folders = controller.folders()
        self.assertEqual(len(folders), 0)
        self.uuids = utils.populate_database()
        folders = controller.folders()
        self.assertEqual(len(folders), len(self.uuids))
        for folder in folders:
            self.assertTrue(folder.uuid in self.uuids)

    def test_folder(self):
        uuid = uuid4().hex
        self.assertRaises(peewee.IntegrityError, controller.folder, uuid)
        self.uuids = utils.populate_database()
        try:
            folder = controller.folder(uuid[0])
        except:
            self.fail("folder() raised an exception unexpectedly")
        self.assertEqual(folder.uuid, uuid)

    def test_add_folder(self):
        uuid = uuid4().hex
        try:
            controller.add_folder(uuid)
        except:
            self.fail("add_folder() raised an exception unexpectedly")
        self.assertRaises(peewee.IntegrityError, controller.add_folder, uuid)
        self.assertRaises(ValueError, controller.add_folder, "a")

    def test_delete_folder(self):
        uuid = uuid4().hex
        self.assertRaises(peewee.IntegrityError, controller.delete_folder, uuid)
        self.uuids = utils.populate_database()
        try:
            controller.delete_folder(self.uuids[0])
        except:
            self.fail("delete_folder() raised an exception unexpectedly")
        new_uuids = db.Folder.select(db.Folder.uuid)
        self.assertTrue(self.uuids[0] not in new_uuids)

    def test_start_transfer(self):
        uuid = uuid4().hex
        self.assertRaises(peewee.IntegrityError, controller.start_transfer, uuid, "/tmp")

    def test_valid_uuid(self):
        uuid = uuid4().hex
        self.assertTrue(controller.valid_uuid(uuid))
        self.assertFalse(controller.valid_uuid("a"))
