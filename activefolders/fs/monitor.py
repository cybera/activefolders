from watchdog.observers.polling import PollingObserver
from activefolders.fs.seafile import SeafilePollingHandler
import activefolders.conf as conf

observer = None


def start():
    global observer
    if observer is None:
        path = conf.settings['dtnd']['storage_path']
        event_handler = SeafilePollingHandler()
        observer = PollingObserver()
        observer.schedule(event_handler, path, recursive=True)
    observer.start()


def stop():
    observer.stop()
    observer.join()
