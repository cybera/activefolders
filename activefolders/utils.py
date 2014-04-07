from uuid import UUID
import logging

LOG = logging.getLogger(__name__)


def coerce_uuid(uuid):
    return str(UUID(uuid))
