# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
  boxes = { :srv1 => "192.168.0.100"}
  boxes.each do |srv, ip|
    config.vm.define srv do |config|
      config.vm.box = "raring64"
      config.vm.box_url = "http://cloud-images.ubuntu.com/vagrant/raring/current/raring-server-cloudimg-amd64-vagrant-disk1.box"
      config.vm.hostname = srv
      config.vm.provider :virtualbox do |vb|
        vb.customize ["modifyvm", :id, "--natdnshostresolver1", "on"]
        vb.customize ["modifyvm", :id, "--memory", "1024"]
        vb.customize ["modifyvm", :id, "--cpuexecutioncap", "50"]
      end
      config.ssh.forward_agent = true
      config.vm.network :private_network, ip: ip, virtualbox__intnet: "true"

      config.vm.provision "chef_solo" do |chef|
        chef.cookbooks_path = "chef/cookbooks"
        #chef.add_recipe "active-folders::dtnd"
        chef.add_recipe "active-folders::seafile"
        chef.json = {
          "dtnd" => {
            "repository" => "/vagrant",
            "user" => "vagrant",
            "group" => "vagrant"
          }
        }
      end
    end
  end
end
