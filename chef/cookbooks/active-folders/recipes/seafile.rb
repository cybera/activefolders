# -----------------------------------------------------------------------
# Cookbook Name:: active-folders
# Recipe:: seafile
# Description::
#
# Copyright 2014, Cybera, inc.
# All rights reserved
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
# -----------------------------------------------------------------------
require 'digest/sha1'

include_recipe "active-folders::default"

%w(python2.7 python-setuptools python-simplejson python-imaging sqlite3).each do |name|
    package name
end

remote_file "/tmp/seafile.tar.gz" do
    source "https://bitbucket.org/haiwen/seafile/downloads/seafile-server_#{node['seafile']['version']}_x86-64.tar.gz"
    not_if { ::File.exists?("/tmp/seafile.tar.gz")}
end

TOPDIR = "/opt/seafile"

directory TOPDIR

execute "unpack seafile archive" do
    command "tar -xzf /tmp/seafile.tar.gz -C #{TOPDIR}/"
end

INSTALLPATH = "#{TOPDIR}/seafile-server-latest"

link INSTALLPATH do
    to "#{TOPDIR}/seafile-server-#{node['seafile']['version']}"
end

# Seafile config

env = {"LD_LIBRARY_PATH" => "#{INSTALLPATH}/seafile/lib/:#{INSTALLPATH}/seafile/lib64:#{ENV["LD_LIBRARY_PATH"]}"}

execute "ccnet-init" do
    command "#{INSTALLPATH}/seafile/bin/ccnet-init -c #{TOPDIR}/ccnet --name NAME --port 8000 --host 0.0.0.0"
    environment env
    not_if { ::File.exists?("#{TOPDIR}/ccnet/ccnet.conf")}
    umask 022
end

execute "seafile-server-init" do
    command "#{INSTALLPATH}/seafile/bin/seaf-server-init --seafile-dir /srv/seafile-data --port 12001 --httpserver-port 8082"
    environment env
    not_if { ::File.exists?("/srv/seafile-data/seafile.conf")}
end


file "#{TOPDIR}/ccnet/seafile.ini" do
    content "/srv/seafile-data"
end

directory "#{TOPDIR}/conf"

template "#{TOPDIR}/conf/seafdav.conf" do
    source "seafdav.conf.erb"
end


# Seahub config
execute "seahub_settings" do
    command "python #{INSTALLPATH}/seahub/tools/secret_key_generator.py #{TOPDIR}/seahub_settings.py"
    not_if { ::File.exists?("#{TOPDIR}/seahub_settings.py")}
end

ADMIN_EMAIL = "devops@cybera.ca"
ADMIN_PWD = "cyb3ra"
ADMIN_PWD_HASH = Digest::SHA1.hexdigest(ADMIN_PWD)

directory "#{TOPDIR}/PeerMgr/"

QUERY = <<-SQL
CREATE TABLE IF NOT EXISTS EmailUser (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, email TEXT, passwd TEXT, is_staff bool NOT NULL, is_active bool NOT NULL, ctime INTEGER);
INSERT INTO EmailUser(email, passwd, is_staff, is_active, ctime) VALUES (\"#{ADMIN_EMAIL}\", \"#{ADMIN_PWD_HASH}\", 1, 1, 0);
SQL

execute "create usermgr db" do
    command "/usr/bin/sqlite3 #{TOPDIR}/PeerMgr/usermgr.db '#{QUERY}'"
    not_if { ::File.exists?("#{TOPDIR}/PeerMgr/usermgr.db")}
end

env = {"PYTHONPATH" => "#{INSTALLPATH}/seafile/lib/python2.6/site-packages:#{INSTALLPATH}/seafile/lib64/python2.6/site-packages:#{INSTALLPATH}/seafile/lib/python2.7/site-packages:#{INSTALLPATH}/seafile/lib64/python2.7/site-packages:#{INSTALLPATH}/seahub/thirdpart:#{ENV["PYTHONPATH"]}",
       "CCNET_CONF_DIR" => "#{TOPDIR}/ccnet",
       "SEAFILE_CONF_DIR" => "/srv/seafile-data" }

execute "create django db" do
    cwd "#{INSTALLPATH}/seahub"
    environment env
    command "/usr/bin/python2 manage.py syncdb"
end

directory "#{TOPDIR}/seahub-data"

execute "move avatars folder" do
    command "mv #{INSTALLPATH}/seahub/media/avatars #{TOPDIR}/seahub-data/avatars"
    not_if { ::File.exists?("#{TOPDIR}/seahub-data/avatars")}
end

link "#{INSTALLPATH}/seahub/media" do
    to "#{TOPDIR}/seahub-data/avatars"
    not_if { ::File.exists?("#{TOPDIR}/seahub-data/avatars")}
end

directory "/srv/seafile-data/library-template"

execute "copy user docs" do
    command "cp -f #{INSTALLPATH}/seafile/docs/*.doc /srv/seafile-data/library-template/"
end

# service "seafile" do
#     supports :status => true, :restart => true, :reload => true
#     action [ :enable, :start ]
# end

# service "seahub" do
#     supports :status => true, :restart => true, :reload => true
#     action [ :enable, :start ]
# end
