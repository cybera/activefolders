import configparser
import os

config = configparser.ConfigParser()
config.read(['/etc/activefolders.conf', os.path.expanduser('~/.activefolders.conf')])
