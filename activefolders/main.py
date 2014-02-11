from activefolders.utils import Daemon
import logging
import time

LOG = logging.getLogger(__name__)


class EmptyDaemon(Daemon):
    """
    Empty background process
    """
    def run(self):
        LOG.info("Empty daemon is up")
        while True:
            time.sleep(1)
