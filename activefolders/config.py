import configparser
import os

activefolders = configparser.ConfigParser()
activefolders.read(['/etc/activefolders.conf', os.path.expanduser('~/.activefolders.conf')])

destinations = configparser.ConfigParser()
destinations.read(['/etc/activefolders/destinations.conf'])