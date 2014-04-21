import logging
import activefolders.api as api
import activefolders.db as db
import activefolders.controllers.folders as folders
import activefolders.controllers.transfers as transfers

LOG = logging.getLogger(__name__)


def default_start():
    LOG.info("DTN daemon is starting")
    db.init()
    #folders.check()
    transfers.check()
    api.start()
