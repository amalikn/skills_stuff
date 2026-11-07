<!-- capture: verbatim third-party text, not authored here -->
**Canonical URL**: https://github.com/Parallels/vagrant-parallels/issues/462
**Retrieved**: 2026-11-07 15:52 AEDT
**HTTP status**: 200 via GitHub API (`gh issue view --json`)

---

# #462 Setting a private IP address does not work 

State: OPEN; opened 2023-11-23T00:16:32Z; closed -

## Body

Configuring static IP addresses for the `private_network` using the configuration given at https://parallels.github.io/vagrant-parallels/docs/networking/private_network.html does not work.

Vagrant version: 

```
$ vagrant version
Installed Version: 2.4.0
Latest Version: 2.4.0
 
You're running an up-to-date version of Vagrant!
```

Vagrant parallels plugin version:

```
$ vagrant plugin list  
vagrant-parallels (2.4.1, global)
  - Version Constraint: > 0
```

Parallels Desktop version:

```
$ prlctl --version
prlctl version 19.1.1 (54734)
```

Vagrantfile:

```
# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
  config.vm.box = "dcagatay/fedora-39-aarch64"
  config.vm.network :private_network, ip: "10.37.130.6"
end
```

Running `vagrant up`:

```
$ vagrant up
Bringing machine 'default' up with 'parallels' provider...
==> default: Registering VM image from the base box 'dcagatay/fedora-39-aarch64'...
==> default: Creating new virtual machine as a full clone of the box image...
==> default: Setting the default configuration for VM...
==> default: Running 'post-import' VM customizations...
==> default: Checking if box 'dcagatay/fedora-39-aarch64' version '0.0.7' is up to date...
==> default: Setting the name of the VM: vault-2_default_1700698403147_67535
==> default: Preparing network interfaces based on configuration...
    default: Adapter 0: shared
    default: Adapter 1: hostonly
==> default: Clearing any previously set network interfaces...
==> default: Running 'pre-boot' VM customizations...
==> default: Booting VM...
==> default: Waiting for machine to boot. This may take a few minutes...
    default: SSH address: 10.211.55.85:22
    default: SSH username: vagrant
    default: SSH auth method: private key
    default: Warning: Authentication failure. Retrying...
    default: 
    default: Vagrant insecure key detected. Vagrant will automatically replace
    default: this with a newly generated keypair for better security.
    default: 
    default: Inserting generated public key within guest...
    default: Removing insecure key from the guest if it's present...
    default: Key inserted! Disconnecting and reconnecting using new SSH key...
==> default: Machine booted and ready!
==> default: Checking for Parallels Tools installed on the VM...
==> default: Parallels Tools installed on this VM are outdated! In most cases
==> default: this is fine but in rare cases it can cause things such as shared
==> default: folders to not work properly. If you see shared folder errors,
==> default: please update Parallels Tools within the virtual machine and
==> default: reload your VM.
==> default: Configuring and enabling network interfaces...
==> default: Running provisioner: shell...
    default: Running: inline script
    default: CHANGED: partition=3 start=3328000 old: size=63780864 end=67108863 new: size=99071967 end=102399966
    default: Resize device id 1 (/dev/sda3) from 30.41GiB to max
```

But the IP address is wrong:
```
$ vagrant ssh -- ip addr show
1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN group default qlen 1000
    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
    inet 127.0.0.1/8 scope host lo
       valid_lft forever preferred_lft forever
2: eth0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc fq_codel state UP group default qlen 1000
    link/ether 00:1c:42:07:b4:52 brd ff:ff:ff:ff:ff:ff
    altname enp0s5
    inet 10.211.55.85/24 brd 10.211.55.255 scope global dynamic noprefixroute eth0
       valid_lft 1774sec preferred_lft 1774sec
3: eth1: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc fq_codel state UP group default qlen 1000
    link/ether 00:1c:42:f0:5e:3d brd ff:ff:ff:ff:ff:ff
    altname enp0s6
    inet 10.37.132.10/24 brd 10.37.132.255 scope global dynamic noprefixroute eth1
       valid_lft 1774sec preferred_lft 1774sec
    inet6 fdb2:2c26:f4e4:2:23e6:bfcd:3929:7d66/64 scope global dynamic noprefixroute 
       valid_lft 2591977sec preferred_lft 604777sec
    inet6 fe80::fe26:1f1e:bca9:29a1/64 scope link noprefixroute 
       valid_lft forever preferred_lft forever
```

The IP address `10.37.132.10` differs from `10.37.130.6`. I think the private network is still using DHCP.

## Comment by christophersjchow at 2024-02-06T08:19:11Z

Running into the same issue, it sets the private IP address on a new interface `eth1` leaving `eth0`.

## Comment by xinkecf35 at 2024-11-17T06:16:26Z

For any passers-by:

As of Vagrant 2.4.3, this is still an issue but it's specific to Fedora 36 and newer boxes. Upstream issue hashicorp/vagrant#12762 covers the issue in detail, but TL;DR Fedora no longer supports how Vagrant tries to configure static interface via ifcfg-rh files, instead it should be using NetworkManager keyfiles. Appropriate workaround pending a fix in the upstream would be to manually configure the additional interface it creates with the desired address with `nmcli`.

You probably don't want to fiddle with the `eth0` interface since that's attached to the shared network and is what Vagrant/Parallels is using to provide SSH access and general WAN access.


