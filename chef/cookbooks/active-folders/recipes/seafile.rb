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
    source "https://bitbucket.org/haiwen/seafile/downloads/seafile-server_#{node[:seafile][:version]}_x86-64.tar.gz"
    not_if { ::File.exists?("/tmp/seafile.tar.gz")}
end

directory node[:seafile][:installpath]

execute "unpack seafile archive" do
    command "tar -xzf /tmp/seafile.tar.gz -C #{node[:seafile][:installpath]}/"
end

SERVERDIR = "#{node[:seafile][:installpath]}/seafile-server-latest"

link SERVERDIR do
    to "#{node[:seafile][:installpath]}/seafile-server-#{node[:seafile][:version]}"
end

# Seafile config

env = {"LD_LIBRARY_PATH" => "#{SERVERDIR}/seafile/lib/:#{SERVERDIR}/seafile/lib64:#{ENV["LD_LIBRARY_PATH"]}"}

execute "ccnet-init" do
    command "#{SERVERDIR}/seafile/bin/ccnet-init -c #{node[:seafile][:ccnet][:configdir]} --name '#{node[:seafile][:ccnet][:name]}' --port #{node[:seafile][:ccnet][:port]} --host #{node[:seafile][:ccnet][:host]}"
    environment env
    not_if { ::File.exists?("#{node[:seafile][:ccnet][:configdir]}/ccnet.conf")}
end

execute "seafile-server-init" do
    command "#{SERVERDIR}/seafile/bin/seaf-server-init --seafile-dir #{node[:seafile][:datadir]} --port #{node[:seafile][:port]} --httpserver-port #{node[:seafile][:httpport]}"
    environment env
    not_if { ::File.exists?("#{node[:seafile][:datadir]}/seafile.conf")}
end


file "#{node[:seafile][:ccnet][:configdir]}/seafile.ini" do
    content node[:seafile][:datadir]
end

directory node[:seafile][:configdir]

template "#{node[:seafile][:configdir]}/seafdav.conf" do
    source "seafdav.conf.erb"
end


# Seahub config
execute "seahub_settings" do
    command "python #{SERVERDIR}/seahub/tools/secret_key_generator.py #{node[:seafile][:installpath]}/seahub_settings.py"
    not_if { ::File.exists?("#{node[:seafile][:installpath]}/seahub_settings.py")}
end

directory "#{node[:seafile][:ccnet][:configdir]}/PeerMgr"

QUERY = <<-SQL
CREATE TABLE IF NOT EXISTS EmailUser (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, email TEXT, passwd TEXT, is_staff bool NOT NULL, is_active bool NOT NULL, ctime INTEGER);
INSERT INTO EmailUser(email, passwd, is_staff, is_active, ctime) VALUES (\"#{ node[:seafile][:seahub][:login] }\", \"#{ Digest::SHA1.hexdigest(node[:seafile][:seahub][:password]) }\", 1, 1, 0);
SQL

execute "create usermgr db" do
    command "/usr/bin/sqlite3 #{node[:seafile][:ccnet][:configdir]}/PeerMgr/usermgr.db '#{QUERY}'"
    not_if { ::File.exists?("#{node[:seafile][:ccnet][:configdir]}/PeerMgr/usermgr.db") }
end

env = {"PYTHONPATH" => "#{SERVERDIR}/seafile/lib/python2.6/site-packages:#{SERVERDIR}/seafile/lib64/python2.6/site-packages:#{SERVERDIR}/seafile/lib/python2.7/site-packages:#{SERVERDIR}/seafile/lib64/python2.7/site-packages:#{SERVERDIR}/seahub/thirdpart:#{ENV["PYTHONPATH"]}",
       "CCNET_CONF_DIR" => "#{node[:seafile][:ccnet][:configdir]}",
       "SEAFILE_CONF_DIR" => "#{node[:seafile][:datadir]}" }

execute "create django db" do
    cwd "#{SERVERDIR}/seahub"
    environment env
    command "/usr/bin/python2 manage.py syncdb"
end

directory node[:seafile][:seahub][:datadir]

execute "move avatars folder" do
    command "mv #{SERVERDIR}/seahub/media/avatars #{node[:seafile][:seahub][:datadir]}/avatars"
    not_if { ::File.exists?("#{node[:seafile][:seahub][:datadir]}/avatars") }
end

link "#{SERVERDIR}/seahub/media/avatars" do
    to "#{node[:seafile][:seahub][:datadir]}/avatars"
    not_if { ::File.exists?("#{node[:seafile][:seahub][:datadir]}/avatars") }
end

directory "#{node[:seafile][:datadir]}/library-template"

execute "copy user docs" do
    command "cp -f #{SERVERDIR}/seafile/docs/*.doc #{node[:seafile][:datadir]}/library-template/"
end

template "/etc/init.d/seafile" do
    source "seafile-init.erb"
    mode 0755
end

template "/etc/init.d/seahub" do
    source "seahub-init.erb"
    mode 0755
end

service "seafile" do
    supports :restart => true
    action [ :enable, :start ]
end

service "seahub" do
    supports :restart => true
    action [ :enable, :start ]
end
