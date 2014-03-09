from activefolders.utils import Daemon
import logging
import activefolders.api as api
import activefolders.db as db

LOG = logging.getLogger(__name__)


class DtnDaemon(Daemon):
    """
    DTN background process
    """
    def run(self):
        LOG.info("DTN daemon is starting")
        db.init()
        api.start()


def dtnd():
    LOG.info("DTN daemon is starting")
    db.init()
    api.start()
