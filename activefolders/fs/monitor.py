from watchdog.observers.polling import PollingObserver
from activefolders.fs.seafile import SeafilePollingHandler
import logging
import activefolders.conf as conf

LOG = logging.getLogger(__name__)
observer = None


def start():
    LOG.info("starting filesystem monitor")
    global observer
    if observer is None:
        path = conf.settings['dtnd']['storage_path']
        event_handler = SeafilePollingHandler()
        observer = PollingObserver()
        observer.schedule(event_handler, path, recursive=True)
    observer.start()


def stop():
    LOG.info("stopping filesystem monitor")
    observer.stop()
    observer.join()
