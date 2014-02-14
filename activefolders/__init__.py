from activefolders.main import DtnDaemon
import logging

logging.basicConfig(
    filename='active-folders.log',
    level=logging.DEBUG,
    format="%(asctime)-15s - %(levelname)s::%(name)s - %(message)s")
LOG = logging.getLogger(__name__)

default_dtn = DtnDaemon(pidfile='/tmp/dtn-daemon.pid')
