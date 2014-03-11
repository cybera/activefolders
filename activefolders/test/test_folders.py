from uuid import uuid4
import peewee
import unittest as test
import activefolders.db as db
import activefolders.controllers.folders as folders
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
        all_folders = folders.get_all()
        self.assertEqual(len(all_folders['folders']), 0)
        self.uuids = testutils.populate_database(5)
        all_folders = folders.get_all()
        self.assertEqual(len(all_folders['folders']), len(self.uuids))
        for folder in all_folders['folders']:
            self.assertTrue(folder['uuid'] in self.uuids)

    def test_folder(self):
        uuid = uuid4().hex
        self.assertRaises(peewee.DoesNotExist, folders.get, uuid)
        self.uuids = testutils.populate_database(1)
        try:
            folder = folders.get(self.uuids[0])
        except:
            self.fail("folder() raised an exception unexpectedly")
        self.assertEqual(folder['uuid'], self.uuids[0])

    def test_add_folder(self):
        uuid = uuid4().hex
        try:
            folders.add(uuid)
        except:
            self.fail("add_folder() raised an exception unexpectedly")
        self.assertRaises(peewee.IntegrityError, folders.add, uuid)
        folders.remove(uuid)
        self.assertRaises(ValueError, folders.add, "a")

    def test_delete_folder(self):
        uuid = utils.coerce_uuid(uuid4().hex)
        self.assertRaises(peewee.DoesNotExist, folders.remove, uuid)
        folders.add(uuid)
        try:
            folders.remove(uuid)
        except:
            self.fail("delete_folder() raised an exception unexpectedly")
        uuids = db.Folder.select(db.Folder.uuid)
        self.assertTrue(uuid not in uuids)