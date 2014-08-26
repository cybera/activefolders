from uuid import UUID
import logging
import logging.config
import importlib
import activefolders.conf as conf
import activefolders.db as db

LOGGING = {
    'version': 1,
    'formatters': {
        'verbose': {
            'format': '%(levelname)-8s %(name)-15s %(message)s'
        },
        'terse': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'syslog': {
            'address': '/dev/log',
            'class': 'logging.handlers.SysLogHandler',
            'facility': 'local6',
            'formatter': 'verbose'
        }
    },
    'root': {
        'level': 'DEBUG',
        },
    'loggers': {
        'dtnd': {
            'handlers': ['syslog'],
            'level': 'DEBUG',
            },
        'peewee': {
            'handlers': ['syslog'],
            'level': 'DEBUG',
            }
    }
}

logging.config.dictConfig(LOGGING)

LOG = logging.getLogger('dtnd')


def get_transport_module(destination):
    dst_conf = conf.destinations[destination]
    transport_name = dst_conf['transport']
    module_name = "activefolders.transports.{}".format(transport_name)
    transport_module = importlib.import_module(module_name)
    return transport_module


def coerce_uuid(uuid):
    return str(UUID(uuid))


def remove_invalid():
    """ Only call before starting TransportMonitor """
    # Remove folder destinations not in conf.destinations
    folder_destinations = db.FolderDestination.select()
    for folder_destination in folder_destinations:
        if folder_destination.destination not in conf.destinations:
            # Recursive will also delete any invalidated exports
            folder_destination.delete_instance(recursive=True)

    # Remove transfers if dtn not in conf.dtns
    transfers = db.Transfer.select()
    for transfer in transfers:
        if transfer.dtn not in conf.dtns:
            transfer.delete_instance()
