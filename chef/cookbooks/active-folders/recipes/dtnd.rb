# -----------------------------------------------------------------------
# Cookbook Name:: active-folders
# Recipe:: dtnd
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
package "git"

directory "/etc/activefolders" do
    owner "root"
    group "root"
    mode "0755"
end

["activefolders", "dtns", "destinations"].each do |conf_file|
    template "/etc/activefolders/#{conf_file}.conf" do
        source "#{conf_file}.conf.erb"
        owner "root"
        group "root"
        mode "0644"
    end
end

if node[:dtnd][:bottle_dev]
  directory "/tmp/bottle"

  git "/tmp/bottle" do
  repository "git://github.com/defnull/bottle.git"
    action :sync
  end

  execute "install bottle" do
      command "pip3 install -e /tmp/bottle"
  end
end

execute "install daemon" do
    command "pip3 install -e #{node['dtnd']['repository']}"
end

template "/etc/init.d/dtnd" do
    source "dtnd-init.erb"
    mode 0755
end

service "rsyslog" do
    supports :restart => true
end

file "/etc/rsyslog.d/10-dtnd.conf" do
    content "local6.*        /var/log/dtnd.log"
    notifies :restart, "service[rsyslog]"
end

service "dtnd" do
    supports :restart => true
    action [ :enable, :start ]
end

service "globus-gridftp-server" do
    supports :status => true, :restart => true, :reload => true
    action [ :enable, :reload ]
end

