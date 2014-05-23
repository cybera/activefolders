from io import StringIO
import logging
import paramiko
import os
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
    ssh.connect(url, username=user, pkey=private_key)
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
            sftp.mkdir(remote_path)
        for f in files:
            remote_path = os.path.join(remote_root, f)
            local_path = os.path.join(root, f)
            sftp.put(local_path, remote_path)


def results_available(folder_destination):
    folder = folder_destination.folder
    home_dir = _home_dir(folder_destination.credentials['user'])
    remote_folder_path = os.path.join(home_dir, folder.uuid)
    result_files = folder_destination.result_files
    ssh = _open_ssh(folder_destination)
    sftp = ssh.open_sftp()

    for result_file in result_files:
        try:
            remote_path = os.path.join(remote_folder_path, result_file)
            sftp.stat(remote_path)
        except Exception:
            return False

    return True


def get_results(folder_destination):
    folder = folder_destination.folder
    results_folder = folder_destination.results_folder
    results_folder_path = results_folder.path()
    result_files = folder_destination.result_files
    home_dir = _home_dir(folder_destination.credentials['user'])
    ssh = _open_ssh(folder_destination)
    sftp = ssh.open_sftp()

    for result_file in result_files:
        remote_path = os.path.join(home_dir, folder.uuid, result_file)
        local_path = os.path.join(results_folder_path, result_file)
        sftp.get(remote_path, local_path)


def success(_):
    return True
