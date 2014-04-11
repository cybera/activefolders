from subprocess import Popen, DEVNULL, STDOUT
import os.path
import logging

LOG = logging.getLogger(__name__)
PATH = "/usr"
BINARY = PATH+"/bin/globus-url-copy"
default_behaviour = [BINARY,  # binary to run
                     "-cd",  # create destination dirs if needed
                     "-r",  # recursive
                     "-fast",  # reuse data channels
                     "-g2",  # use v2 control protocol when possible
                     "-vb",  # display bytes and rate to stdout
                     "-rst",  # restart on fail (5 retries by default)
                     "-sync"]  # transfer only new or updated files

if not os.path.isfile(BINARY):
    LOG.critical("{} is not found".format(BINARY))
    raise IOError("{} is not found".format(BINARY))


def start_transfer(folder,
                   dst_conf,
                   parallel_streams=4,
                   concurrent_files=4,
                   offset=None,
                   length=None):
    opts = ["-p", str(parallel_streams),  # per file
            "-cc", str(concurrent_files)]

    # Partial transfer
    if offset:
        opts += ["-off", str(offset)]
    if length:
        assert offset
        opts += ["-len", str(length)]

    transfer = default_behaviour + opts
    transfer.append(folder.path() + '/')
    transfer.append(dst_conf['url'] + '/' + folder.uuid + '/')
    proc = Popen(transfer, stdin=DEVNULL, stdout=DEVNULL, stderr=STDOUT)
    LOG.debug("Initiated transfer {}:'{}'".format(id(proc), " ".join(transfer)))
    return proc


def stop_transfer(proc):
    LOG.debug("Killing transfer process {}".format(id(proc)))
    return proc.kill()


def transfer_success(proc):
    LOG.debug("Checking transfer process {}".format(id(proc)))
    retcode = proc.poll()
    if retcode is None:
        return None
    elif retcode == 0:
        return True
    else:
        return False
