# -----------------------------------------------------------------------
# Cookbook Name:: active-folders
# Recipe:: server
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

execute "locale" do
    command "locale-gen en_CA.UTF-8"
end

remote_file "/tmp/globus.deb" do
    source "http://toolkit.globus.org/ftppub/gt5/5.2/5.2.5/installers/repo/globus-repository-5.2-stable-raring_0.0.3_all.deb"
end

execute "unpack globus" do
    command "dpkg -i --force-all /tmp/globus.deb"
end

execute "refresh-apt" do
    command "apt-get update"
    #action :nothing
end

package "globus-gridftp"
package "libglobus-xio-udt-driver0"

template "/etc/gridftp.conf" do
    source "gridftp.conf.erb"
    owner "root"
    group "root"
    mode "0644"
end

package "python3"
package "python3-pip"

template "/etc/activefolders.conf" do
    source "activefolders.conf.erb"
    owner "root"
    group "root"
    mode "0644"
end

execute "install daemon" do
    command "pip3 install -e #{node['active-folders']['repository']}"
    action :run
end


# installation directory is specified via --install-dir, --prefix, or the distutils default setting
#     /usr/local/lib/python3.3/dist-packages/
# A different installation directory is preferably one that is listed in the PYTHONPATH environment variable.
execute "start" do
    user node['active-folders']['user']
    group node['active-folders']['group']
    command "#{node['active-folders']['repository']}/runner restart"
end

service "globus-gridftp-server" do
    supports :status => true, :restart => true, :reload => true
    action [ :enable, :reload ]
end

