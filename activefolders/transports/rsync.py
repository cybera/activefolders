from subprocess import Popen, DEVNULL, STDOUT
import logging

LOG = logging.getLogger(__name__)

CREDENTIALS = [ 'user', 'private_key' ]


def start_transfer(folder, dst_conf):
    
