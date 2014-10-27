from Crypto import Random
import os
import base64
import activefolders.conf as conf


def key_exists():
    return os.path.exists(conf.settings['dtnd']['key_path'])


def create_key():
    key = Random.new().read(32)
    key = base64.b64encode(key)
    f = open(conf.settings['dtnd']['key_path'], 'wb')
    os.chmod(conf.settings['dtnd']['key_path'], 0o600)
    f.write(key)
    f.close()


def get_key():
    f = open(conf.settings['dtnd']['key_path'], 'rb')
    key = f.read()
    f.close()
    return base64.b64decode(key)