import activefolders.api as api
import activefolders.db as db
import activefolders.controllers.transfers as transfers
from activefolders.utils import LOG


def default_start():
    LOG.info("DTN daemon is starting")
    db.init()
    transfers.check()
    api.start()
