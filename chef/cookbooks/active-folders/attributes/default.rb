default[:dtnd][:repository] = "/home/ubuntu/active-folders"
default[:dtnd][:user] = "ubuntu"
default[:dtnd][:group] = "ubuntu"

default[:seafile][:version] = "2.1.5"
default[:seafile][:installpath] = "/opt/seafile"
default[:seafile][:datadir] = "/srv/seafile"
default[:seafile][:port] = 12001
default[:seafile][:httpport] = 8082
default[:seafile][:configdir] = node[:seafile][:installpath] + "/conf"

default[:seafile][:ccnet][:host] = "0.0.0.0"
default[:seafile][:ccnet][:port] = 10001
default[:seafile][:ccnet][:name] = "active-folders"
default[:seafile][:ccnet][:configdir] = node[:seafile][:installpath] + "/ccnet"


default[:seafile][:seahub][:login] = "devops@cybera.ca"
default[:seafile][:seahub][:password] = "cyb3ra"
default[:seafile][:seahub][:port] = 8000
default[:seafile][:seahub][:host] = "0.0.0.0"
default[:seafile][:seahub][:datadir] = "/srv/seahub"
default[:seafile][:seahub][:peermgrdir] = node[:seafile][:ccnet][:configdir] + "/PeerMgr"

default[:seafile][:seahub][:config][:open_signup] = true
default[:seafile][:seahub][:config][:site_name] = "example.com"
default[:seafile][:seahub][:config][:site_base] = "http://www." + node[:seafile][:seahub][:config][:site_name] +"/"
