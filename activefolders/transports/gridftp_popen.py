from subprocess import Popen, DEVNULL, STDOUT
import os.path
import logging

LOG = logging.getLogger(__name__)
PATH = "/usr/"
binary = PATH+"bin/globus-url-copy"
default_behaviour = [binary,  # binary to run
                     "-cd",  # create destination dirs if needed
                     "-r",  # recursive
                     "-fast",  # reuse data channels
                     "-g2",  # use v2 control protocol when possible
                     "-vb",  # display bytes and rate to stdout
                     "-rst",  # restart on fail (5 retries by default)
                     "-sync"]  # try to transfer only new or updated files

if not os.path.isfile(binary):
    LOG.critical("No {} is found".format(binary))
    raise IOError("No {} is found".format(binary))


def start_transfer(src,
                   dst,
                   parallel_streams=4,
                   concurrent_files=4,
                   offset=0,
                   length=None):
    opts = ["-p", str(parallel_streams), "-cc", str(concurrent_files), "-off", str(offset)]
    if length:
        opts.append("-len {}".format(length))  # length for partial transfers
    transfer = default_behaviour + opts
    transfer.append(src)
    transfer.append(dst)
    LOG.debug("Initiating transfer '{}'".format(transfer.join(" ")))
    return Popen(transfer, stdin=DEVNULL, stdout=DEVNULL, stderr=STDOUT )


def stop_transfer(proc):
    return proc.kill()


def transfer_is_success(proc):
    retcode = proc.poll()
    if retcode == 0:
        return True
    else:
        return False
