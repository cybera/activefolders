from io import StringIO
import logging
import paramiko
import os
import activefolders.conf as conf

LOG = logging.getLogger(__name__)

CREDENTIALS = [ 'user', 'private_key' ]


def _get_credentials(export):
    destination = export.folder_destination.destination
    creds = export.folder_destination.credentials
    user = creds['user']
    key_string = creds['private_key']
    private_key = paramiko.RSAKey.from_private_key(StringIO(key_string))
    return user, private_key


def start_export(export):
    folder = export.folder_destination.folder
    destination = export.folder_destination.destination
    url = conf.destinations[destination]['url']
    folder_path = folder.path()
    user, private_key = _get_credentials(export)
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(url, username=user, pkey=private_key)
    sftp = ssh.open_sftp()
 
    try:
        os.mkdir(folder_path)
    except OSError:
        pass
    for root, dirs, files in os.walk(folder_path):
        for d in dirs:
            dir_path = os.path.join(root, d)
            sftp.mkdir(dir_path)
        for f in files:
            file_path = os.path.join(root, f)
            sftp.put(file_path, file_path)


def success(_):
    return True
