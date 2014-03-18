from activefolders.utils import Daemon
import logging
import activefolders.api as api
import activefolders.db as db
import activefolders.fs.monitor as monitor

LOG = logging.getLogger(__name__)


class DtnDaemon(Daemon):
    """
    DTN background process
    """
    def run(self):
        LOG.info("DTN daemon is starting")
        db.init()
        monitor.start()
        api.start()


def default_start():
    daemon = DtnDaemon(pidfile="/var/run/dtnd.pid")
    daemon.start()
