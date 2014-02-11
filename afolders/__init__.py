from afolders.main import EmptyDaemon
import logging

logging.basicConfig(
    filename='active-folders.log',
    level=logging.DEBUG,
    format="%(asctime)-15s - %(levelname)s::%(name)s - %(message)s")
LOG = logging.getLogger(__name__)

default_dtn = EmptyDaemon(pidfile='/tmp/empty-daemon.pid')
