from io import StringIO
import logging
import paramiko
import os
import stat
import activefolders.conf as conf
import activefolders.transports.base as base

LOG = logging.getLogger(__name__)

CREDENTIALS = [ 'user', 'private_key' ]


class SftpMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._ssh = self._open_ssh()
        self._sftp = self._ssh.open_sftp()
        destination = self._folder_destination.destination
        home_dir = conf.destinations[destination]['home_dir']
        self._remote_folder_path = os.path.join(home_dir,
                self._folder_destination.credentials['user'],
                self._folder_destination.folder.uuid)

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


class DestinationTransport(SftpMixin, base.DestinationTransport):
    def _start_export(self):
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


class ResultsTransport(SftpMixin, base.ResultsTransport):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._retrieved_files = 0

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

        remote_file_size = self._sftp.stat(remote_path).st_size
        try:
            local_file_size = os.stat(local_path).st_size
        except OSError:
            local_file_size = -1

        if remote_file_size != local_file_size:
            self._sftp.get(remote_path, local_path)
            self._retrieved_files += 1

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

    def _get_results(self):
        result_files = self._folder_destination.result_files
        self._sftp.chdir(self._remote_folder_path)

        for result_file in result_files:
            self._get(result_file)

        return self._retrieved_files > 0

    def _get_auto_results(self):
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

        return self._retrieved_files > 0
