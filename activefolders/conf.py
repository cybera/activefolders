import configparser
import os

settings = configparser.ConfigParser()
settings.read(['/etc/activefolders.conf', os.path.expanduser('~/.activefolders.conf')])

destinations = configparser.ConfigParser()
destinations.read(['/etc/activefolders/destinations.conf'])