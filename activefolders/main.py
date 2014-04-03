from activefolders.utils import Daemon
import logging
import activefolders.api as api
import activefolders.db as db
import activefolders.controllers.folders as folders
import activefolders.controllers.transfers as transfers

LOG = logging.getLogger(__name__)


class DtnDaemon(Daemon):
    """
    DTN background process
    """
    def run(self):
        LOG.info("DTN daemon is starting")
        db.init()
        folders.check()
        transfers.check()
        api.start()


def default_start():
    daemon = DtnDaemon(pidfile="/var/run/dtnd.pid")
    daemon.start()
