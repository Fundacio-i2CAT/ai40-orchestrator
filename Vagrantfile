# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure(2) do |config|
    config.vm.box = 'ubuntu/trusty64'
    config.vm.synced_folder ".", "/home/vagrant/orchestrator"

    config.vm.provider :virtualbox do |vb|
        vb.customize ['modifyvm', :id, '--memory', '2048'] # is not required, but recommended
        vb.customize ['modifyvm', :id, '--cpus', '2'] # is not required, but recommended
        vb.customize ['modifyvm', :id, '--natdnshostresolver1', 'on']
        vb.customize ['modifyvm', :id, '--natdnsproxy1', 'on']
    end
    config.vm.network :forwarded_port, guest: 8082, host: 8082 # orchestrator port

    $script = <<-SCRIPT
    sudo apt-get update
    sudo apt-get install -y git
    sudo apt-get install -y libjpeg-dev
    sudo apt-get install -y python-pip python-dev
    sudo apt-get install -y libffi-dev libssl-dev libxml2-dev libxslt1-dev libjpeg8-dev zlib1g-dev
    cd orchestrator
    sudo pip install pytz
    sudo pip install -r requirements.txt
    sudo pip install scp
  SCRIPT

    config.vm.provision 'shell', inline: $script, privileged: false
end
