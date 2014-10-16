from io import StringIO
import os
import re
import subprocess
import threading
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
        key_path = self.get_path()
        key.write_private_key_file(key_path)

    def __exit__(self, type, value, traceback):
        key_path = self.get_path()
        subprocess.check_call(["shred", "-u", key_path])

    def get_path(self):
        thread_id = threading.current_thread().ident
        key_path = "/tmp/{}.key".format(thread_id)
        return key_path


class RsyncMixin:
    def _get_remote_host(self):
        if hasattr(self, '_transfer'):
            dtn_conf = conf.dtns[self._transfer.dtn]
            remote_host = dtn_conf['url']
        elif hasattr(self, '_folder_destination'):
            dst_conf = conf.destinations[self._folder_destination.destination]
            host = dst_conf['url']
            user = self._folder_destination.credentials['user']
            remote_host = "{}@{}".format(user, host)
        else:
            remote_host = ""
        return remote_host

    def _get_remote_path(self):
        if hasattr(self, '_folder_destination'):
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
        rsync_cmd.append("-auz")
        rsync_cmd.append("--stats")
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
        rsync_cmd.append(self._get_remote_host() + ":~/")
        with Key(self._folder_destination):
            subprocess.check_call(rsync_cmd)


class ResultsTransport(RsyncMixin, base.ResultsTransport):
    def _get_results(self):
        rsync_cmd = self._get_rsync_cmd()
        rsync_cmd.append("--relative")
        source = "{}:".format(self._get_remote_host())
        result_files = self._folder_destination.result_files
        for result_file in result_files:
            full_path = os.path.join(self._get_remote_path(), "./", result_file)
            source = "{} {}".format(source, full_path)
        rsync_cmd.append(source)
        rsync_cmd.append(self._folder_destination.results_folder.path())

        with Key(self._folder_destination):
            try:
                output = subprocess.check_output(rsync_cmd)
            except subprocess.CalledProcessError as e:
                # Rsync will return error code 23 if all files are not present, but will still transfer those that are
                if e.returncode != 23:
                    raise e
                output = e.output
 
        return self._files_transferred(output) > 0

    def _get_auto_results(self):
        rsync_cmd = self._get_rsync_cmd()
        rsync_cmd.append("--compare-dest={}/".format(self._folder_destination.folder.path()))
        rsync_cmd.append("{}:{}/".format(self._get_remote_host(), self._get_remote_path()))
        rsync_cmd.append(self._folder_destination.results_folder.path())

        with Key(self._folder_destination):
            output = subprocess.check_output(rsync_cmd)

        return self._files_transferred(output) > 0

    def _files_transferred(self, output):
        output = output.decode('utf-8')
        output = output.split('\n')
        r = re.compile(r"Number of files transferred: (\d+)")
        files_transferred = [ m.group(1) for l in output for m in [ r.search(l) ] if m is not None ]
        files_transferred = int(files_transferred[0])
        return files_transferred
