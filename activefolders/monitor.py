from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import activefolders.conf as conf

observer = None


class FolderHandler(FileSystemEventHandler):
    def on_modified(self, event):
        print(event)


def start():
    global observer
    if observer is None:
        path = conf.settings['dtnd']['storage_path']
        event_handler = FolderHandler()
        observer = Observer()
        observer.schedule(event_handler, path, recursive=True)
 
    observer.start()


def stop():
    observer.stop()
    observer.join()
