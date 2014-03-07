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


include_recipe "active-folders::default"

remote_file "/tmp/seafile.tar.gz" do
    owner node['dtnd']['user']
    source "https://bitbucket.org/haiwen/seafile/downloads/seafile-server_#{node['seafile']['version']}_x86-64.tar.gz"
end

execute "unpack seafile" do
    user node['dtnd']['user']
    cwd "/vagrant/"
    command "tar -xzf /tmp/seafile.tar.gz"
end

%w(python2.7 python-setuptools python-simplejson python-imaging sqlite3).each do |name|
    package name
end
