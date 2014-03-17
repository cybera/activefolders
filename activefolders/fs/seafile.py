from watchdog.events import FileSystemEventHandler
import datetime
import peewee
import activefolders.conf as conf
import activefolders.utils as utils
import activefolders.controllers.folders as folders


class SeafileHandler(FileSystemEventHandler):
    def on_created(self, event):
        """ Handles folder creation """
        if len(event.src_path.split('/')) != 2:
            # Not a new library
            return
        uuid = self.get_library_id(event)
        if uuid is not None:
            folders.add(uuid)

    def on_modified(self, event):
        """ Handles changes to folder contents """
        folder = self.get_folder(event)
        if folder is not None:
            folder.dirty = True
            folder.last_change = datetime.datetime.now()
            folder.save()
            pass

    def on_deleted(self, event):
        """ Handles folder deletion """
        if len(event.src_path.split('/')) != 2:
            # Not a deleted library
            return
        folder = self.get_folder(event)
        if folder is not None:
            folders.remove(folder['uuid'])

    def get_relative_path(self, event):
        """ Returns path relative to storage path """
        rel_path = event.src_path.replace(conf.settings['dtnd']['storage_path'], "")
        rel_path = rel_path.strip('/')
        return rel_path

    def get_library_id(self, event):
        rel_path = self.get_relative_path(event)
        tokens = rel_path.split('/')
        try:
            dir_name = tokens[1]
            library_id = dir_name.split('_')[0]
            uuid = utils.coerce_uuid(library_id)
        except ValueError:
            # Not a valid library path or UUID
            return None
        return uuid

    def get_folder(self, event):
        try:
            uuid = self.get_library_id(event)
        except ValueError:
            return None
        try:
            folder = folders.get(uuid)
        except peewee.DoesNotExist:
            # Folder somehow wasn't added on creation
            folder = folders.add(uuid)
        return folder
