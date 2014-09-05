from io import StringIO
import os
import subprocess
import paramiko
import activefolders.conf as conf
import activefolders.transports.base as base

CREDENTIALS = [ 'user', 'private_key' ]


class Key():
    def __init__(self, folder_destination):
        self._folder_destination = folder_destination

    def __enter__(self):
        key_string = self._folder_destination.credentials['private_key']
        key = paramiko.RSAKey.from_private_key(StringIO(key_string))
        key_path = self.get_path
        key.write_private_key_file(key_path)

    def __exit__(self, type, value, traceback):
        key_path = self.get_path()
        subprocess.check_call(["shred", "-u", key_path])

    def get_path(self):
        uuid = self._folder_destination.folder.uuid
        destination = self._folder_destination.destination
        key_path = "/tmp/{}-{}".format(uuid, destination)
        return key_path

class RsyncMixin:
    def _get_remote_host(self):
        if hasattr(self, '_transfer'):
            dtn_conf = conf.dtns[self._transfer.dtn]
            remote_host = "{}@{}".format("USER", dtn_conf['url'])
        elif hasattr(self, '_folder_destination'):
            dst_conf = conf.destinations[self._folder_destination.destination]
            host = dst_conf['url']
            user = self._folder_destination.credentials['user']
            remote_host = "{}@{}".format(user, host)
        else:
            remote_host = ""
        return remote_host

    def _get_remote_path(self):
        if hasattr(self, '_transfer'):
            # TODO: Implement
            pass
        elif hasattr(self, '_folder_destination'):
            dst_conf = conf.destinations[self._folder_destination.destination]
            home_dir = dst_conf['home_dir']
            user = self._folder_destination.credentials['user']
            remote_path = os.path.join(home_dir, user, self._folder_destination.folder.uuid)
        else:
            remote_path = ""
        return remote_path

    def _get_rsync_cmd(self):
        rsync_cmd = []
        rsync_cmd.append("rsync")
        rsync_cmd.append("-auvz")
        if hasattr(self, '_folder_destination'):
            rsync_cmd.append("-e")
            rsync_cmd.append("ssh -i {}".format(Key(self._folder_destination).get_path()))
        return rsync_cmd


class DtnTransport(RsyncMixin, base.DtnTransport):
    def _start_transfer(self):
        rsync_cmd = self._get_rsync_cmd()
        rsync_cmd.append(self._transfer.folder.path())
        rsync_cmd.append(self._get_remote_host())
        subprocess.check_call(rsync_cmd)


class DestinationTransport(RsyncMixin, base.DestinationTransport):
    def _start_export(self):
        rsync_cmd = self._get_rsync_cmd()
        rsync_cmd.append(self._folder_destination.folder.path())
        rsync_cmd.append("{}:{}".format(self._get_remote_host(), self._get_remote_path()))
        with Key(self._folder_destination):
            subprocess.check_call(rsync_cmd)


class ResultsTransport(RsyncMixin, base.ResultsTransport):
    def _get_results(self):
        rsync_cmd = self._get_rsync_cmd()
        source = self._get_remote_host() + ":'"
        result_files = self._folder_destination.result_files
        for result_file in result_files:
            full_path = os.path.join(self._get_remote_path(), result_file)
            source = "{} {}".format(source, full_path)
        source = source + "'"
        rsync_cmd.append(source)
        rsync_cmd.append(self._folder_destination.folder.path())

    def _get_auto_results(self):
        rsync_cmd = self._get_rsync_cmd()
        rsync_cmd.append("--compare-dest={}".format(self._folder_destination.folder.path()))
        rsync_cmd.append("{}:{}".format(self._get_remote_host(), self._get_remote_path()))
        rsync_cmd.append(self._folder_destination.folder.path())
        with Key(self._folder_destination):
            subprocess.check_call(rsync_cmd)
