import configparser

settings = configparser.ConfigParser()
settings.read('/etc/activefolders/activefolders.conf')

destinations = configparser.ConfigParser()
destinations.read('/etc/activefolders/destinations.conf')
