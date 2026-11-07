<!-- capture: verbatim third-party text, not authored here -->
**Canonical URL**: https://github.com/Parallels/vagrant-parallels/issues/410
**Retrieved**: 2026-11-07 15:52 AEDT
**HTTP status**: 200 via GitHub API (`gh issue view --json`)

---

# #410 Error when adding more than 4 networks

State: OPEN; opened 2021-12-07T16:22:24Z; closed -

## Body

I have a Vagrant config that works with VirtualBox. It creates 7 networks like so:

```
        vbox.vm.network "private_network", type: "dhcp"
        vbox.vm.network "private_network", type: "dhcp"
        vbox.vm.network "private_network", type: "dhcp"
        vbox.vm.network "private_network", type: "dhcp"
        vbox.vm.network "private_network", type: "dhcp"
        vbox.vm.network "private_network", type: "dhcp"
        vbox.vm.network "private_network", type: "dhcp"
```

This _appears_ to work with parallels as well:

```
$ prlctl list -i | grep -i 'net[0-9]'
  net0 (+) type=shared mac=001C4284A43B card=virtio
Boot order: hdd0 cdrom0 usb net1 net2 net3 net4 net5 net6 net7
  net0 (+) type=shared mac=001C42454134 card=virtio
  net1 (+) type=host iface='Host-Only' mac=001C42F73080 card=virtio
  net2 (+) type=host iface='Host-Only' mac=001C4214C219 card=virtio
  net3 (+) type=host iface='Host-Only' mac=001C4255D054 card=virtio
  net4 (+) type=host iface='Host-Only' mac=001C42B5BC0A card=virtio
  net5 (+) type=host iface='Host-Only' mac=001C42CE04AF card=virtio
  net6 (+) type=host iface='Host-Only' mac=001C427E80F9 card=virtio
  net7 (+) type=host iface='Host-Only' mac=001C42F6C00E card=virtio
```

I can also see the 7 networks in the Parallels desktop UI:
![tugboat_tugboat_1638893383870_85842  Configuration 2021-12-07 11-19-48](https://user-images.githubusercontent.com/66118/145066418-6d22c156-9d8d-4130-9be2-9585831ee7d4.png)

However, `ip a` only shows 4 devices which causes the `vagrant up` command to fail:

```
$ vagrant ssh -c 'sudo ip a'
1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN group default qlen 1000
    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
    inet 127.0.0.1/8 scope host lo
       valid_lft forever preferred_lft forever
    inet6 ::1/128 scope host
       valid_lft forever preferred_lft forever
2: eth0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc pfifo_fast state UP group default qlen 1000
    link/ether 00:1c:42:45:41:34 brd ff:ff:ff:ff:ff:ff
    inet 10.211.55.13/24 brd 10.211.55.255 scope global dynamic eth0
       valid_lft 1721sec preferred_lft 1721sec
    inet6 fdb2:2c26:f4e4:0:21c:42ff:fe45:4134/64 scope global dynamic mngtmpaddr
       valid_lft 2591704sec preferred_lft 604504sec
    inet6 fe80::21c:42ff:fe45:4134/64 scope link
       valid_lft forever preferred_lft forever
3: eth1: <BROADCAST,MULTICAST> mtu 1500 qdisc noop state DOWN group default qlen 1000
    link/ether 00:1c:42:f7:30:80 brd ff:ff:ff:ff:ff:ff
4: eth2: <BROADCAST,MULTICAST> mtu 1500 qdisc noop state DOWN group default qlen 1000
    link/ether 00:1c:42:14:c2:19 brd ff:ff:ff:ff:ff:ff
5: eth3: <BROADCAST,MULTICAST> mtu 1500 qdisc noop state DOWN group default qlen 1000
    link/ether 00:1c:42:55:d0:54 brd ff:ff:ff:ff:ff:ff
```

Relevant debug output from `vagrant --debug up --provider parallels`:
```
 INFO ssh: Execute: /sbin/ip -o -0 addr | grep -v LOOPBACK | awk '{print $2}' | sed 's/://' (sudo=true)
...
DEBUG network_interfaces: Unsorted list: ["eth0", "eth1", "eth2", "eth3", "eth1", "eth2", "eth0", "eth3"]
DEBUG network_interfaces: Sorted list: ["eth0", "eth1", "eth2", "eth3"]
DEBUG network_interfaces: Ethernet preferred sorted list: ["eth0", "eth1", "eth2", "eth3"]
...
 INFO ssh: Execute: /sbin/ifup 'eth1'
/sbin/ifup 'eth2'
/sbin/ifup 'eth3'
/sbin/ifup ''
/sbin/ifup ''
/sbin/ifup ''
/sbin/ifup '' (sudo=true)
...
The following SSH command responded with a non-zero exit status.
Vagrant assumes that this means the command failed!

/sbin/ifup 'eth1'
/sbin/ifup 'eth2'
/sbin/ifup 'eth3'
/sbin/ifup ''
/sbin/ifup ''
/sbin/ifup ''
/sbin/ifup ''
```

## Comment by legal90 at 2022-02-09T20:30:47Z

Hi @q0rban 

If that issue is still actual for you, could you please share more details ?
1) Could you please share the Vagrantfile (or at least a box name) which could be used to reproduce that issue ?
2) Which versions of Vagrant, vagrant-parallels and Parallels Desktop did you use?


## Comment by legal90 at 2022-02-09T20:31:42Z

I tried to reproduce it on Parallels Desktop for Mac `17.1.1` , Vagrant `2.2.19` and vagrant-parallels `2.2.4` and it works just fine in both cases:
### Case n.1 
All networks are type DHCP. In reality all these virtual NICs will be bridged through the same bridge interface on your Mac (bridge101), which is mapped to the default "Host Only" network:
```ruby
Vagrant.configure("2") do |config|
  config.vm.box = "bento/ubuntu-20.04"
  config.vm.network "private_network", type: "dhcp"
  config.vm.network "private_network", type: "dhcp"
  config.vm.network "private_network", type: "dhcp"
  config.vm.network "private_network", type: "dhcp"
  config.vm.network "private_network", type: "dhcp"
  config.vm.network "private_network", type: "dhcp"
  config.vm.network "private_network", type: "dhcp"
  config.vm.network "private_network", type: "dhcp"
end

```
Output:
```
$ vagrant ssh
Welcome to Ubuntu 20.04.2 LTS (GNU/Linux 5.4.0-77-generic x86_64)

 * Documentation:  https://help.ubuntu.com
 * Management:     https://landscape.canonical.com
 * Support:        https://ubuntu.com/advantage

  System information as of Wed 09 Feb 2022 12:28:06 PM PST

  System load:           0.75
  Usage of /:            2.4% of 61.31GB
  Memory usage:          21%
  Swap usage:            0%
  Processes:             133
  Users logged in:       0
  IPv4 address for eth0: 10.211.55.37
  IPv6 address for eth0: fdb2:2c26:f4e4:0:21c:42ff:fe22:8053
  IPv4 address for eth1: 10.37.129.23
  IPv6 address for eth1: fdb2:2c26:f4e4:1:21c:42ff:fe9d:7f1b
  IPv4 address for eth2: 10.37.129.22
  IPv6 address for eth2: fdb2:2c26:f4e4:1:21c:42ff:fe7c:8b40
  IPv4 address for eth3: 10.37.129.21
  IPv6 address for eth3: fdb2:2c26:f4e4:1:21c:42ff:fe81:9ae8
  IPv4 address for eth4: 10.37.129.20
  IPv6 address for eth4: fdb2:2c26:f4e4:1:21c:42ff:fe64:e404
  IPv4 address for eth5: 10.37.129.19
  IPv6 address for eth5: fdb2:2c26:f4e4:1:21c:42ff:fe92:d98b
  IPv4 address for eth6: 10.37.129.18
  IPv6 address for eth6: fdb2:2c26:f4e4:1:21c:42ff:febd:65f3
  IPv4 address for eth7: 10.37.129.17
  IPv6 address for eth7: fdb2:2c26:f4e4:1:21c:42ff:fe1f:30f5
  IPv4 address for eth8: 10.37.129.16
  IPv6 address for eth8: fdb2:2c26:f4e4:1:21c:42ff:fe2e:73ef


This system is built by the Bento project by Chef Software
More information can be found at https://github.com/chef/bento
```

### Case n.2 
All networks (except first 2) are set to static IPs from separate /24 subnets, so there will be an individual bridge interface created for each of them:
```ruby
Vagrant.configure("2") do |config|
  config.vm.box = "bento/ubuntu-20.04"
  config.vm.network "private_network", ip: "10.20.30.10"
  config.vm.network "private_network", ip: "10.20.30.11"
  config.vm.network "private_network", ip: "10.20.40.10"
  config.vm.network "private_network", ip: "10.20.50.10"
  config.vm.network "private_network", ip: "10.20.60.10"
  config.vm.network "private_network", ip: "10.20.70.10"
  config.vm.network "private_network", ip: "10.20.80.10"
  config.vm.network "private_network", ip: "10.20.90.10"
end
```
Output:
```
$ vagrant ssh
Welcome to Ubuntu 20.04.2 LTS (GNU/Linux 5.4.0-77-generic x86_64)

 * Documentation:  https://help.ubuntu.com
 * Management:     https://landscape.canonical.com
 * Support:        https://ubuntu.com/advantage

  System information as of Wed 09 Feb 2022 12:14:51 PM PST

  System load:           0.55
  Usage of /:            2.4% of 61.31GB
  Memory usage:          20%
  Swap usage:            0%
  Processes:             131
  Users logged in:       0
  IPv4 address for eth0: 10.211.55.36
  IPv6 address for eth0: fdb2:2c26:f4e4:0:21c:42ff:fef4:44de
  IPv4 address for eth1: 10.20.30.10
  IPv6 address for eth1: fdb2:2c26:f4e4:2:21c:42ff:fe3a:b849
  IPv4 address for eth2: 10.20.30.11
  IPv6 address for eth2: fdb2:2c26:f4e4:2:21c:42ff:fef4:e89e
  IPv4 address for eth3: 10.20.40.10
  IPv6 address for eth3: fdb2:2c26:f4e4:3:21c:42ff:fe9c:e5f5
  IPv4 address for eth4: 10.20.50.10
  IPv6 address for eth4: fdb2:2c26:f4e4:4:21c:42ff:fefa:347
  IPv4 address for eth5: 10.20.60.10
  IPv6 address for eth5: fdb2:2c26:f4e4:5:21c:42ff:fefa:d695
  IPv4 address for eth6: 10.20.70.10
  IPv6 address for eth6: fdb2:2c26:f4e4:6:21c:42ff:fe25:cf6b
  IPv4 address for eth7: 10.20.80.10
  IPv6 address for eth7: fdb2:2c26:f4e4:7:21c:42ff:fec9:1f4b
  IPv4 address for eth8: 10.20.90.10
  IPv6 address for eth8: fdb2:2c26:f4e4:8:21c:42ff:fe5c:97c7


This system is built by the Bento project by Chef Software
More information can be found at https://github.com/chef/bento
```
^ In both cases NICs are configured successfully

## Comment by q0rban at 2022-02-10T18:14:41Z

Thanks so much for taking a look at this, @legal90 !

One thing I failed to mention is that I am on an M1 Mac
Parallels Desktop Pro for Mac: Version 17.1.1 (51537)
Vagrant 2.2.19
Vagrantfile:

```
Vagrant.configure("2") do |config|
  config.vm.box = "avi0xff/debian10-arm64"
  config.vm.network "private_network", type: "dhcp"
  config.vm.network "private_network", type: "dhcp"
  config.vm.network "private_network", type: "dhcp"
  config.vm.network "private_network", type: "dhcp"
  config.vm.network "private_network", type: "dhcp"
  config.vm.network "private_network", type: "dhcp"
  config.vm.network "private_network", type: "dhcp"
  config.vm.network "private_network", type: "dhcp"
end
```

```
$ vagrant --debug up --provider parallels
...
The following SSH command responded with a non-zero exit status.
Vagrant assumes that this means the command failed!

/sbin/ifup 'eth1'
/sbin/ifup 'eth2'
/sbin/ifup 'eth3'
/sbin/ifup ''
/sbin/ifup ''
/sbin/ifup ''
/sbin/ifup ''
/sbin/ifup ''

Stdout from the command:



Stderr from the command:

ifup: /etc/network/interfaces:39: unknown or no address type and no inherits keyword specified
ifup: couldn't read interfaces file "/etc/network/interfaces"
ifup: /etc/network/interfaces:39: unknown or no address type and no inherits keyword specified
ifup: couldn't read interfaces file "/etc/network/interfaces"
ifup: /etc/network/interfaces:39: unknown or no address type and no inherits keyword specified
ifup: couldn't read interfaces file "/etc/network/interfaces"
ifup: /etc/network/interfaces:39: unknown or no address type and no inherits keyword specified
ifup: couldn't read interfaces file "/etc/network/interfaces"
ifup: /etc/network/interfaces:39: unknown or no address type and no inherits keyword specified
ifup: couldn't read interfaces file "/etc/network/interfaces"
ifup: /etc/network/interfaces:39: unknown or no address type and no inherits keyword specified
ifup: couldn't read interfaces file "/etc/network/interfaces"
ifup: /etc/network/interfaces:39: unknown or no address type and no inherits keyword specified
ifup: couldn't read interfaces file "/etc/network/interfaces"
ifup: /etc/network/interfaces:39: unknown or no address type and no inherits keyword specified
ifup: couldn't read interfaces file "/etc/network/interfaces"
```

I will try a different box to see if it's something with the box causing the issue.


## Comment by q0rban at 2022-02-10T18:35:19Z

I tried the [`laravel/homestead-arm`](https://app.vagrantup.com/laravel/boxes/homestead-arm) box in the same Vagrantfile and got the following error:

```
/etc/netplan/50-vagrant.yaml:14:5: Error in network definition: Invalid name ''
    ! '':
    ^

The following SSH command responded with a non-zero exit status.
Vagrant assumes that this means the command failed!

mv -f '/tmp/vagrant-network-entry-1644517501' '/etc/netplan/50-vagrant.yaml'
chown root:root '/etc/netplan/50-vagrant.yaml'
chmod 0644 '/etc/netplan/50-vagrant.yaml'
netplan apply

Stdout from the command:



Stderr from the command:

/etc/netplan/50-vagrant.yaml:14:5: Error in network definition: Invalid name ''
    ! '':
    ^
```

Same error with [`linyows/ubuntu-20.04-arm64`](https://app.vagrantup.com/linyows/boxes/ubuntu-20.04-arm64)

```
The following SSH command responded with a non-zero exit status.
Vagrant assumes that this means the command failed!

mv -f '/tmp/vagrant-network-entry-1644517998' '/etc/netplan/50-vagrant.yaml'
chown root:root '/etc/netplan/50-vagrant.yaml'
chmod 0644 '/etc/netplan/50-vagrant.yaml'
netplan apply

Stdout from the command:



Stderr from the command:

/etc/netplan/50-vagrant.yaml:12:5: Error in network definition: Invalid name ''
    ! '':
    ^
```

## Comment by legal90 at 2022-02-10T19:04:50Z

> One thing I see I failed to leave out is that I am on an M1 Mac

Oh, then this is probably some limitation or issue of Parallels Desktop on M1 Mac :(
We'll need help from Parallels folks.  cc @romankulikov @alevlasu 

## Comment by eazylaykzy at 2023-04-21T11:06:08Z

I'm having the same issue as @q0rban 

### My Vagrantfile:

```
# -*- mode: ruby -*-
# vi: set ft=ruby :

# All Vagrant configuration is done below. The "2" in Vagrant.configure
# configures the configuration version (we support older styles for
# backwards compatibility). Please don't change it unless you know what you're doing.
Vagrant.configure("2") do |config|
  # Every Vagrant development environment requires a box. You can search for
  # boxes at https://vagrantcloud.com/search.
  config.vm.box = "spox/ubuntu-arm"
  config.vm.box_version = "1.0.0"
  #config.ssh.insert_key = false

  # Provider-specific configuration so you can fine-tune various
  # backing providers for Vagrant. These expose provider-specific options.
  # Example for VMWare:
  config.vm.provider :vmware_desktop do |v|
    v.memory                            = 1024
    v.cpus                              = 1
    v.linked_clone                      = true
    v.gui                               = true
    v.vmx["ethernet0.virtualdev"]       = "vmxnet3"
    #v.vmx["ethernet0.pcislotnumber"]    = "160"
  end

  # Create a private network, which allows host-only access to the machine
  # using a specific IP.
  #########
  # Nodes: host our apps
  #########
  config.vm.define "node1" do |node|
    node.vm.network "private_network", ip: "172.17.177.21"
  end
  config.vm.define "node2" do |node|
    node.vm.network "private_network", ip: "172.17.177.22"
  end

  # Share an additional folder to the guest VM. The first argument is
  # the path on the host to the actual folder. The second argument is
  # the path on the guest to mount the folder. And the optional third
  # argument is a set of non-required options.
  #########
  # Controller: host our tools
  #########
  config.vm.define 'controller' do |machine|
    # The Ansible Local provisioner requires that all the Ansible Playbook files are available on the guest machine
    machine.vm.synced_folder ".", "/vagrant",
      owner: "vagrant", group: "vagrant", mount_options: ["dmode=755,fmode=600"]

    machine.vm.network "private_network", ip: "172.17.177.11"
    machine.vm.provision "ansible_local" do |ansible|
      # ansible setup
      ansible.install         = true
      ansible.install_mode    = "pip_args_only"
      ansible.playbook        = "playbook.yml"
      # ansible.version = "2.10.7"
      ansible.pip_install_cmd = "sudo apt-get install -y python3-pip python-is-python3 haveged && sudo ln -s -f /usr/bin/pip3 /usr/bin/pip"
      ansible.pip_args        = "ansible==2.10.7"
      # provsionning
      ansible.playbook        = "playbook.yml"
      ansible.verbose         = true
      ansible.limit           = "all" # or only "nodes" group, etc.
      ansible.inventory_path  = "inventory"
    end
  end
end
```

### vagrant up:

```
Bringing machine 'node1' up with 'vmware_desktop' provider...
Bringing machine 'node2' up with 'vmware_desktop' provider...
Bringing machine 'controller' up with 'vmware_desktop' provider...
==> node1: Cloning VMware VM: 'spox/ubuntu-arm'. This can take some time...
==> node1: Checking if box 'spox/ubuntu-arm' version '1.0.0' is up to date...
==> node1: Verifying vmnet devices are healthy...
==> node1: Preparing network adapters...
WARNING: The VMX file for this box contains a setting that is automatically overwritten by Vagrant
WARNING: when started. Vagrant will stop overwriting this setting in an upcoming release which may
WARNING: prevent proper networking setup. Below is the detected VMX setting:
WARNING: 
WARNING:   ethernet0.pcislotnumber = "160"
WARNING: 
WARNING: If networking fails to properly configure, it may require this VMX setting. It can be manually
WARNING: applied via the Vagrantfile:
WARNING: 
WARNING:   Vagrant.configure(2) do |config|
WARNING:     config.vm.provider :vmware_desktop do |vmware|
WARNING:       vmware.vmx["ethernet0.pcislotnumber"] = "160"
WARNING:     end
WARNING:   end
WARNING: 
WARNING: For more information: https://www.vagrantup.com/docs/vmware/boxes.html#vmx-allowlisting
==> node1: Starting the VMware VM...
==> node1: Waiting for the VM to receive an address...
==> node1: Forwarding ports...
    node1: -- 22 => 2222
==> node1: Waiting for machine to boot. This may take a few minutes...
    node1: SSH address: 127.0.0.1:2222
    node1: SSH username: vagrant
    node1: SSH auth method: private key
    node1: 
    node1: Vagrant insecure key detected. Vagrant will automatically replace
    node1: this with a newly generated keypair for better security.
    node1: 
    node1: Inserting generated public key within guest...
    node1: Removing insecure key from the guest if it's present...
    node1: Key inserted! Disconnecting and reconnecting using new SSH key...
==> node1: Machine booted and ready!
==> node1: Configuring network adapters within the VM...
```

### Error:
```
The following SSH command responded with a non-zero exit status.
Vagrant assumes that this means the command failed!

mv -f '/tmp/vagrant-network-entry-1682073924' '/etc/netplan/50-vagrant.yaml'
chown root:root '/etc/netplan/50-vagrant.yaml'
chmod 0644 '/etc/netplan/50-vagrant.yaml'
netplan apply

Stdout from the command:



Stderr from the command:

/etc/netplan/50-vagrant.yaml:6:5: Error in network definition: Invalid name ''
    ! '':
    ^
```

### My configuration:

> vagrant plugin list

- Vagrant 2.3.4
- vagrant-vbguest (0.31.0, global)
- vagrant-vmware-desktop (3.0.1, global)

> machine and installations
- MacBook Pro M1 Max
- VMWare Fusion Professional Version 13.0.1 (21139760)

## Comment by eazylaykzy at 2023-04-21T12:11:23Z

@q0rban I'd be happy you share how you got it resolved as it's been a while you opened this issue, thanks.

@legal90 any help will be appreciated here, thanks.

## Comment by q0rban at 2023-04-21T13:27:24Z

@eazylaykzy thank you, I ended up just not using Vagrant on Mac M1, due in part to this issue but also other issues.

## Comment by eazylaykzy at 2023-04-21T13:31:31Z

> @eazylaykzy thank you, I ended up just not using Vagrant on Mac M1, due in part to this issue but also other issues.

@q0rban that's sad, I guess I will have to get a secondary computer that will be compatible with VirtualBox. Thank you.

## Comment by eazylaykzy at 2023-04-22T07:56:06Z

For anyone hitting a roadblock like I did trying to make this work, below are the changes I made to my Vagrantfile that got me up and running:


```
# -*- mode: ruby -*-
# vi: set ft=ruby :

# All Vagrant configuration is done below. The "2" in Vagrant.configure
# configures the configuration version (we support older styles for
# backwards compatibility). Please don't change it unless you know what you're doing.
Vagrant.configure("2") do |config|
  # Every Vagrant development environment requires a box. You can search for
  # boxes at https://vagrantcloud.com/search.
  config.vm.box = "spox/ubuntu-arm"
  config.vm.box_version = "1.0.0"
  #config.ssh.insert_key = false

  # alternative box
  #config.vm.box = "rkrause/ubuntu-21.10-arm64"

  # Provider-specific configuration so you can fine-tune various
  # backing providers for Vagrant. These expose provider-specific options.
  # Example for VMWare:
  config.vm.provider :vmware_desktop do |v|
    v.memory                            = 1024
    v.cpus                              = 1
    v.linked_clone                      = true
    v.gui                               = true
    v.vmx["ethernet0.virtualdev"]       = "vmxnet3"
    v.vmx["ethernet1.virtualdev"]       = "vmxnet3"
    v.vmx["ethernet0.pcislotnumber"]    = "160"
    v.vmx["ethernet1.pcislotnumber"]    = "36"
  end

  # Create a private network, which allows host-only access to the machine
  # using a specific IP.
  #########
  # Nodes: host our apps
  #########
  config.vm.define "node1" do |node|
    node.vm.network "private_network", ip: "172.17.177.21"
  end
  config.vm.define "node2" do |node|
    node.vm.network "private_network", ip: "172.17.177.22"
  end

  # Share an additional folder to the guest VM. The first argument is
  # the path on the host to the actual folder. The second argument is
  # the path on the guest to mount the folder. And the optional third
  # argument is a set of non-required options.
  #########
  # Controller: host our tools
  #########
  config.vm.define 'controller' do |machine|
    # The Ansible Local provisioner requires that all the Ansible Playbook files are available on the guest machine
    machine.vm.synced_folder ".", "/vagrant",
      owner: "vagrant", group: "vagrant"

    machine.vm.network "private_network", ip: "172.17.177.11"
    machine.vm.provision "ansible_local" do |ansible|

      # ansible setup
      ansible.install           = true
      ansible.install_mode      = "pip_args_only"
      ansible.playbook          = "./ansible/playbook.yml"

      # ansible.version         = "2.10.7"
      ansible.pip_install_cmd   = "sudo apt-get install -y python3-pip python-is-python3 haveged && sudo ln -s -f /usr/bin/pip3 /usr/bin/pip"
      ansible.pip_args          = "ansible==2.10.7"

      # provsionning
      ansible.playbook          = "./ansible/playbook.yml"
      ansible.verbose           = true
      ansible.limit             = "all" # or only "nodes" group, etc.
      ansible.inventory_path    = "./ansible/inventory"
    end
  end
end
```

All  configurations from my [previous comments](https://github.com/Parallels/vagrant-parallels/issues/410#issuecomment-1517660457) remain the same.
