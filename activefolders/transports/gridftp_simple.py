from subprocess import Popen, DEVNULL, STDOUT
from activefolders.transports.base import TransferTransport
import os.path
import logging
import activefolders.conf as conf

LOG = logging.getLogger(__name__)
PATH = "/usr"
BINARY = PATH+"/bin/globus-url-copy"
default_behaviour = [BINARY,  # binary to run
                     "-cd",  # create destination dirs if needed
                     "-r",  # recursive
                     "-fast",  # reuse data channels
                     "-g2",  # use v2 control protocol when possible
                     "-vb",  # display bytes and rate to stdout
                     "-rst"]  # restart on fail (5 retries by default)
                     #"-sync"]  # transfer only new or updated files

if not os.path.isfile(BINARY):
    LOG.critical("{} is not found".format(BINARY))
    raise IOError("{} is not found".format(BINARY))


class Transport(TransferTransport):
    def __init__(self, transfer):
        super(Transport, self).__init__(transfer)
        self._proc = None

    def start_transfer(self,
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

        folder = self._transfer.folder
        dtn = self._transfer.dtn
        dtn_conf = conf.dtns[dtn]

        gridtftp_cmd = default_behaviour + opts
        gridtftp_cmd.append(folder.path() + '/')
        gridtftp_cmd.append(dtn_conf['url'] + '/' + folder.uuid + '/')
        self._proc = Popen(gridtftp_cmd, stdin=DEVNULL, stdout=DEVNULL, stderr=STDOUT)
        LOG.debug("Initiated transfer {}:'{}'".format(id(self._proc), " ".join(gridtftp_cmd)))

    def stop_transfer(self):
        LOG.debug("Killing transfer process {}".format(id(self._proc)))
        self._proc.kill()

    def transfer_success(self):
        LOG.debug("Checking transfer process {}".format(id(self._proc)))
        retcode = self._proc.poll()
        if retcode is None:
            return None
        elif retcode == 0:
            return True
        else:
            return False
