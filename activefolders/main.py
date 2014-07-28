from activefolders.api import app
from activefolders.utils import LOG
from activefolders.monitor import Monitor
import activefolders.conf as conf


def start():
    host = conf.settings['dtnd']['host']
    port = conf.settings['dtnd']['listen_port']

    LOG.info("DTN daemon is starting on {}:{}".format(host, conf))
    Monitor().start()
    app.run(host=host, port=port, debug=True)
