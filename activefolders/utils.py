from uuid import UUID
import logging
import logging.config

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


def coerce_uuid(uuid):
    return str(UUID(uuid))
