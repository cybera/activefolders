from activefolders.api import app
import activefolders.conf as conf
from activefolders.utils import LOG


def start():
    host = conf.settings['dtnd']['host']
    port = conf.settings['dtnd']['listen_port']

    LOG.info("DTN daemon is starting on {}:{}".format(host, conf))
    app.run(host=host, port=port, debug=True)
