import configparser


settings = configparser.ConfigParser()
settings.read('/etc/activefolders/activefolders.conf')

dtns = configparser.ConfigParser()
dtns.read('/etc/activefolders/dtns.conf')

destinations = configparser.ConfigParser()
destinations.read('/etc/activefolders/destinations.conf')
