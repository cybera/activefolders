from uuid import uuid4
import peewee
import unittest as test
import activefolders.db as db
import activefolders.controller as controller
import activefolders.test.utils as testutils
import activefolders.utils as utils


class ControllerTest(test.TestCase):
    uuids = None

    @classmethod
    def setUpClass(cls):
        testutils.set_test_config()
        db.init()

    def tearDown(self):
        testutils.clear_database()
        self.uuids = None

    def test_folders(self):
        folders = controller.folders()
        self.assertEqual(len(folders['folders']), 0)
        self.uuids = testutils.populate_database(5)
        folders = controller.folders()
        self.assertEqual(len(folders['folders']), len(self.uuids))
        for folder in folders['folders']:
            self.assertTrue(folder['uuid'] in self.uuids)

    def test_folder(self):
        uuid = uuid4().hex
        self.assertRaises(peewee.DoesNotExist, controller.folder, uuid)
        self.uuids = testutils.populate_database(1)
        try:
            folder = controller.folder(self.uuids[0])
        except:
            self.fail("folder() raised an exception unexpectedly")
        self.assertEqual(folder['uuid'], self.uuids[0])

    def test_add_folder(self):
        uuid = uuid4().hex
        try:
            controller.add_folder(uuid)
        except:
            self.fail("add_folder() raised an exception unexpectedly")
        self.assertRaises(peewee.IntegrityError, controller.add_folder, uuid)
        controller.delete_folder(uuid)
        self.assertRaises(ValueError, controller.add_folder, "a")

    def test_delete_folder(self):
        uuid = utils.coerce_uuid(uuid4().hex)
        self.assertRaises(peewee.DoesNotExist, controller.delete_folder, uuid)
        controller.add_folder(uuid)
        try:
            controller.delete_folder(uuid)
        except:
            self.fail("delete_folder() raised an exception unexpectedly")
        uuids = db.Folder.select(db.Folder.uuid)
        self.assertTrue(uuid not in uuids)

    def test_start_transfer(self):
        uuid = uuid4().hex
        self.assertRaises(peewee.DoesNotExist, controller.start_transfer, uuid, "/tmp")
