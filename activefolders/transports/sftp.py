from io import StringIO
from activefolders.transports.base import ExportTransport
import logging
import paramiko
import os
import stat
import activefolders.conf as conf

LOG = logging.getLogger(__name__)


class Transport(ExportTransport):
    CREDENTIALS = [ 'user', 'private_key' ]

    def __init__(self, folder_destination):
        super(Transport, self).__init__(folder_destination)
        self._ssh = self._open_ssh()
        self._sftp = self._ssh.open_sftp()
        dst = folder_destination.destination
        home_dir = conf.destinations[dst]['home_dir']
        self._remote_folder_path = os.path.join(home_dir,
                folder_destination.credentials['user'],
                folder_destination.folder.uuid)

    def _open_ssh(self):
        destination = self._folder_destination.destination
        url = conf.destinations[destination]['url']
        creds = self._folder_destination.credentials
        user = creds['user']
        key_string = creds['private_key']
        private_key = paramiko.RSAKey.from_private_key(StringIO(key_string))
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(url, username=user, pkey=private_key)
        return ssh

    def start_export(self):
        folder = self._folder_destination.folder
        folder_path = folder.path()

        try:
            self._sftp.mkdir(self._remote_folder_path)
        except OSError:
            pass

        for root, dirs, files in os.walk(folder_path):
            relative_root = root[len(folder_path):].lstrip('/')
            remote_root = os.path.join(self._remote_folder_path, relative_root)
            for d in dirs:
                remote_path = os.path.join(remote_root, d)
                self._sftp.mkdir(remote_path)
            for f in files:
                remote_path = os.path.join(remote_root, f)
                local_path = os.path.join(root, f)
                self._sftp.put(local_path, remote_path)

    def export_success(self):
        return True

    def results_available(self):
        result_files = self._folder_destination.result_files

        for result_file in result_files:
            try:
                remote_path = os.path.join(self._remote_folder_path, result_file)
                self._sftp.stat(remote_path)
            except IOError:
                return False

        return True

    def get_results(self):
        result_files = self._folder_destination.result_files

        if result_files is None:
            self._auto_results()
        else:
            self._results()

    def _relative_path(self, remote_file):
        remote_path = self._remote_path(remote_file)
        return remote_path[len(self._remote_folder_path):].lstrip('/')

    def _remote_path(self, remote_file):
        return os.path.join(self._sftp.getcwd(), remote_file)

    def _local_path(self, remote_file, folder):
        relative_path = self._relative_path(remote_file)
        return os.path.join(folder.path(), relative_path)

    def _get(self, remote_file):
        results_folder = self._folder_destination.results_folder
        remote_path = self._remote_path(remote_file)
        local_path = self._local_path(remote_file, results_folder)
        local_dir = "/".join(local_path.split("/")[:-1])
        os.makedirs(local_dir, exist_ok=True)

        self._sftp.get(remote_path, local_path)

    def _recursive_get(self, remote_dir):
        cwd = self._sftp.getcwd()
        self._sftp.chdir(remote_dir)
        files = self._sftp.listdir_attr()

        for f in files:
            if stat.S_ISDIR(f.st_mode):
                self._recursive_get(f.filename)
            else:
                self._get(f.filename)

        self._sftp.chdir(cwd)

    def _results(self):
        result_files = self._folder_destination.result_files
        self._sftp.chdir(self._remote_folder_path)

        for result_file in result_files:
            self._get(result_file)

    def _auto_results(self):
        folder = self._folder_destination.folder
        dirs = [ self._remote_folder_path ]
        files = []

        for d in dirs:
            self._sftp.chdir(d)
            files = self._sftp.listdir_attr()
            for f in files:
                local_path = self._local_path(f.filename, folder)
                if os.path.exists(local_path):
                    if stat.S_ISDIR(f.st_mode):
                        dirs.append(local_path)
                else:
                    if stat.S_ISDIR(f.st_mode):
                        self._recursive_get(f.filename)
                    else:
                        self._get(f.filename)
