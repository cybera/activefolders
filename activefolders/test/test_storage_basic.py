from uuid import uuid4
import os
import io
import bottle
import unittest as test
import activefolders.db as db
import activefolders.storage.basic as storage
import activefolders.test.utils as testutils


class StorageBasicTest(test.TestCase):
    folder = None

    @classmethod
    def setUpClass(cls):
        testutils.set_test_config()
        db.init()

    def setUp(self):
        uuid = str(uuid4())
        self.folder = db.Folder.create(uuid=uuid)

    def test_basic_storage(self):
        storage.create_folder(self.folder)
        self.assertTrue(os.path.isdir(self.folder.path()))

        bytes_io = io.BytesIO(b"This is a test string.\x00\x01")
        file_upload = bottle.FileUpload(bytes_io, "upload", "test.txt")
        file_path = self.folder.path() + "/test.txt"
        file_upload.save(self.folder.path())
        self.assertTrue(os.path.exists(file_path))

        storage.create_dir(self.folder, "directory")
        dir_path = self.folder.path() + "/directory"
        self.assertTrue(os.path.isdir(dir_path))

        copy_path = self.folder.path() + "/directory/test.txt"
        storage.copy(self.folder, file_path, copy_path)
        self.assertTrue(os.path.exists(file_path))
        self.assertTrue(os.path.exists(copy_path))

        move_path = self.folder.path() + "/moved_test.txt"
        storage.move(self.folder, file_path, move_path)
        self.assertFalse(os.path.exists(file_path))
        self.assertTrue(os.path.exists(move_path))

        storage.delete(self.folder, move_path)
        self.assertFalse(os.path.exists(move_path))
        storage.delete(self.folder, dir_path)
        self.assertFalse(os.path.exists(dir_path))

        storage.delete_folder(self.folder)
        self.assertFalse(os.path.exists(self.folder.path()))

    def test_basic_storage_errors(self):
        # TODO
        pass
