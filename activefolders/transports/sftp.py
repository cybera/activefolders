from io import StringIO
import logging
import paramiko
import os
import stat
import activefolders.conf as conf

LOG = logging.getLogger(__name__)

CREDENTIALS = [ 'user', 'private_key' ]


def _open_ssh(folder_destination):
    destination = folder_destination.destination
    url = conf.destinations[destination]['url']
    creds = folder_destination.credentials
    user = creds['user']
    key_string = creds['private_key']
    private_key = paramiko.RSAKey.from_private_key(StringIO(key_string))
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(url, username=user, pkey=private_key, allow_agent=False, look_for_keys=False)
    return ssh


def _home_dir(user):
    home_dir = os.path.join("/home", user)
    return home_dir


def start_export(export):
    folder = export.folder_destination.folder
    folder_path = folder.path()
    home_dir = _home_dir(export.folder_destination.credentials['user'])
    storage_path = conf.settings['dtnd']['storage_path']
    ssh = _open_ssh(export.folder_destination)
    sftp = ssh.open_sftp()

    try:
        remote_path = os.path.join(home_dir, folder.uuid)
        sftp.mkdir(remote_path)
    except OSError:
        pass

    for root, dirs, files in os.walk(folder_path):
        relative_root = root[len(storage_path):].lstrip('/')
        remote_root = os.path.join(home_dir, relative_root)
        for d in dirs:
            remote_path = os.path.join(remote_root, d)
            try:
                sftp.mkdir(remote_path)
            except OSError:
                pass
        for f in files:
            remote_path = os.path.join(remote_root, f)
            local_path = os.path.join(root, f)
            sftp.put(local_path, remote_path)


def get_results(folder_destination):
    folder = folder_destination.folder
    results_folder = folder_destination.results_folder
    results_folder_path = results_folder.path()
    result_files = folder_destination.result_files
    home_dir = _home_dir(folder_destination.credentials['user'])
    ssh = _open_ssh(folder_destination)
    sftp = ssh.open_sftp()
    remote_folder_path = os.path.join(home_dir, folder.uuid)

    if folder_destination.result_files is None:
        _auto_results(sftp, remote_folder_path, folder.path(), results_folder_path)
    else:
        _results(sftp, result_files, remote_folder_path, results_folder_path)


def success(_):
    return True


def _relative_path(sftp, remote_file, remote_folder_path):
    remote_path = _remote_path(sftp, remote_file)
    return remote_path[len(remote_folder_path):].lstrip('/')


def _remote_path(sftp, remote_file):
    return os.path.join(sftp.getcwd(), remote_file)


def _local_path(sftp, remote_file, remote_folder_path, local_folder_path):
    relative_path = _relative_path(sftp, remote_file, remote_folder_path)
    return os.path.join(local_folder_path, relative_path)


def _get(sftp, remote_file, remote_folder_path, local_folder_path):
    remote_path = _remote_path(sftp, remote_file)
    local_path = _local_path(sftp, remote_file, remote_folder_path, local_folder_path)
    local_dir = "/".join(local_path.split("/")[:-1])

    os.makedirs(local_dir, exist_ok=True)
    sftp.get(remote_path, local_path)


def _recursive_get(sftp, remote_dir, remote_folder_path, local_folder_path):
    cwd = sftp.getcwd()
    sftp.chdir(remote_dir)
    files = sftp.listdir_attr()

    for f in files:
        if stat.S_ISDIR(f.st_mode):
            _recursive_get(sftp, f.filename, remote_folder_path, local_folder_path)
        else:
            _get(sftp, f.filename, remote_folder_path, local_folder_path)

    sftp.chdir(cwd)


def _results(sftp, result_files, remote_folder_path, results_folder_path):
    for result_file in result_files:
        remote_path = os.path.join(remote_folder_path, result_file)
        local_path = os.path.join(results_folder_path, result_file)
        local_dir = "/".join(local_path.split("/")[:-1])
        os.makedirs(local_dir, exist_ok=True)
        sftp.get(remote_path, local_path)


def _auto_results(sftp, remote_folder_path, local_folder_path, results_folder_path):
    dirs = [ remote_folder_path ]
    files = []
    for d in dirs:
        sftp.chdir(d)
        files = sftp.listdir_attr()
        for f in files:
            local_path = _local_path(sftp, f.filename, remote_folder_path, local_folder_path)
            if os.path.exists(local_path):
                if stat.S_ISDIR(f.st_mode):
                    remote_path = _remote_path(sftp, f.filename)
                    dirs.append(remote_path)
            else:
                if stat.S_ISDIR(f.st_mode):
                    _recursive_get(sftp, f.filename, remote_folder_path, results_folder_path)
                else:
                    _get(sftp, f.filename, remote_folder_path, results_folder_path)

