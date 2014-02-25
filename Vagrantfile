# -*- mode: ruby -*-
# vi: set ft=ruby :

$init = <<SCRIPT
  if [ ! -f ~/runonce ]
  then
    locale-gen en_CA.UTF-8
    wget http://toolkit.globus.org/ftppub/gt5/5.2/5.2.5/installers/repo/globus-repository-5.2-stable-raring_0.0.3_all.deb
    dpkg -i *.deb
    aptitude update
    aptitude install -yq globus-gridftp libglobus-xio-udt-driver0

    cp /vagrant/chef/cookbooks/active-folders/templates/default/activefolders.conf.erb /etc/gridftp.conf
    service globus-gridftp-server restart

    python3 -m unittest discover -s "/vagrant"

    touch ~/runonce
  fi
SCRIPT

Vagrant.configure("2") do |config|
  boxes = { :srv1 => "192.168.0.100"}
  boxes.each do |srv, ip|
    config.vm.define srv do |config|
      config.vm.box = "raring64"
      config.vm.box_url = "http://cloud-images.ubuntu.com/vagrant/raring/current/raring-server-cloudimg-amd64-vagrant-disk1.box"
      config.vm.hostname = srv
      config.vm.provider :virtualbox do |vb|
        vb.customize ["modifyvm", :id, "--natdnshostresolver1", "on"]
        vb.customize ["modifyvm", :id, "--memory", 1024]
        vb.customize ["modifyvm", :id, "--cpuexecutioncap", "50"]
      end
      config.ssh.forward_agent = true
      config.vm.network :private_network, ip: ip, virtualbox__intnet: true

      config.vm.provision :shell, :inline => $init
      #config.vm.provision "chef_solo" do |chef|
      #  chef.cookbooks_path = "chef/cookbooks"
      #  chef.add_recipe "active-folders::server"
      #  chef.json = {}
      #end
    end
  end
end
