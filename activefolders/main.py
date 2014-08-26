from activefolders.api import app
from activefolders.utils import LOG
from activefolders.monitor import TransportMonitor, RequestMonitor
import activefolders.conf as conf
import activefolders.utils as utils


def start():
    host = conf.settings['dtnd']['host']
    port = conf.settings['dtnd']['listen_port']

    LOG.info("DTN daemon is starting on {}:{}".format(host, conf))
    utils.remove_invalid()
    TransportMonitor().start()
    RequestMonitor().start()
    app.run(host=host, port=port, debug=True)
