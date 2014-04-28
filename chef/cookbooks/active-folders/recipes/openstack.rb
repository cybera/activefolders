ohai "reload openstack" do
  action :nothing
  plugin "openstack"
end

directory "/etc/chef/ohai/hints" do
  action :create
  recursive true
end

file "/etc/chef/ohai/hints/openstack.json" do
  action :create
  notifies :reload, "ohai[reload openstack]", :immediately
end
