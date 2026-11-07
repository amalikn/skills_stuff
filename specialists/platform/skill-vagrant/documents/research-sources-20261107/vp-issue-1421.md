<!-- capture: verbatim third-party text, not authored here -->
**Canonical URL**: https://github.com/chef/bento/issues/1421
**Retrieved**: 2026-11-07 15:55 AEDT
**HTTP status**: 200 via GitHub API (`gh issue view --json`)

---

# #1421 VMs from `ubuntu-20.04` v202206.03.0 inherit a single `machine-id`, which breaks DHCP

State: CLOSED; opened 2022-07-20T18:10:55Z; closed 2023-02-10T04:33:01Z

## Body

# Version:

`bento/ubuntu-20.04` v202206.03.0

# Environment:

Reproduced with:

| OS | Vagrant | Provider |
| --- | --- | --- |
| Debian 11 | 2.2.14 | libvirt |
| macOS 12.3 | 2.2.19 | VirtualBox |

# Scenario:

`vagrant up` for multiple VMs, either in parallel or serially, from the same box image, should receive distinct DHCP leases.

# Steps to Reproduce:

```sh-session
$ vagrant init  # config.vm.box = "bento/ubuntu-20.04"
$ vagrant up
$ vagrant ssh -c "cat /etc/machine-id"
$ vagrant destroy
$ vagrant ssh -c "cat /etc/machine-id"
```

# Expected Result:

Using `bento/ubuntu-20.04` v202112.19.0, the VMs have different `/etc/machine-id`s, so they receive different DHCP leases.

```sh-session
cfm@ozymandias securedrop-6497 % vagrant box add --provider virtualbox bento/ubuntu-20.04 --box-version 202112.19.0
[...]
cfm@ozymandias securedrop-6497 % vagrant up
[...]
cfm@ozymandias securedrop-6497 % vagrant ssh -c "cat /etc/machine-id"
588777d009ab480bae0cf2b9e6dc3a0b
Connection to 127.0.0.1 closed.
cfm@ozymandias securedrop-6497 % vagrant destroy
[...]
cfm@ozymandias securedrop-6497 % vagrant ssh -c "cat /etc/machine-id"
bf790e22f06d405983e19866eff76b2c
Connection to 127.0.0.1 closed.
cfm@ozymandias securedrop-6497 % vagrant destroy   
[...]
```

# Actual Result:

Using `bento/ubuntu-20.04` v202206.03.0, the VMs have the same `/etc/machine-id`, so they receive the same DHCP lease, which causes an IP collision if the VMs are running simultaneously.

```sh-session
cfm@ozymandias securedrop-6497 % vagrant box update
==> default: Checking for updates to 'bento/ubuntu-20.04'
    default: Latest installed version: 202112.19.0
    default: Version constraints: 
    default: Provider: virtualbox
==> default: Updating 'bento/ubuntu-20.04' with provider 'virtualbox' from version
==> default: '202112.19.0' to '202206.03.0'...
==> default: Loading metadata for box 'https://vagrantcloud.com/bento/ubuntu-20.04'
==> default: Adding box 'bento/ubuntu-20.04' (v202206.03.0) for provider: virtualbox
    default: Downloading: https://vagrantcloud.com/bento/boxes/ubuntu-20.04/versions/202206.03.0/providers/virtualbox.box
==> default: Successfully added box 'bento/ubuntu-20.04' (v202206.03.0) for 'virtualbox'!
cfm@ozymandias securedrop-6497 % vagrant up
[...]
cfm@ozymandias securedrop-6497 % vagrant ssh -c "cat /etc/machine-id"
10ac0529b1ef4e1c85f504f698893be7
Connection to 127.0.0.1 closed.
cfm@ozymandias securedrop-6497 % vagrant destroy
[...]
cfm@ozymandias securedrop-6497 % vagrant up
[...]
cfm@ozymandias securedrop-6497 % vagrant ssh -c "cat /etc/machine-id"
10ac0529b1ef4e1c85f504f698893be7
Connection to 127.0.0.1 closed.
```

May be a regression of #1062.

## Comment by tas50 at 2022-12-12T01:09:00Z

I think this may be partially due to the conversion to libvirt format. We currently truncate the  machine-id file as part of the cleanup.sh script that runs on Ubuntu. This *should* be empty on your libvirt images. Can you check that to confirm if it's empty?

## Comment by cfm at 2022-12-23T23:28:28Z

@tas50, that matches my understanding.  But per <https://github.com/chef/bento/issues/1421#issue-1311634441> I can reproduce a non-empty (and identical) `/etc/machine-id` beginning with `bento/ubuntu-20.04` v202206.03.0 under both the VirtualBox provider (before/without conversion to libvirt format) and the libvirt provider (after conversion).  By contrast, the prior version 202112.19.0 behaves as expected under both providers.

## Comment by Stromweld at 2023-01-20T18:41:44Z

Can you test and verify this is still an issue with the latest hcl2 packer code in bento main branch?

## Comment by cfm at 2023-01-31T01:47:53Z

@Stromweld, here's the same test case against v202212.11.0, showing reuse of a different `machine-id`:

```sh-session
cfm@ozymandias ~ % vagrant box add --provider virtualbox bento/ubuntu-20.04
[...]
==> box: Successfully added box 'bento/ubuntu-20.04' (v202212.11.0) for 'virtualbox'!
cfm@ozymandias ~ % vagrant up
[...]
cfm@ozymandias ~ % vagrant ssh -c "cat /etc/machine-id"
4117adcefa904fa48e0ba81bf75e4678
Connection to 127.0.0.1 closed.
cfm@ozymandias ~ % vagrant destroy
[...]
cfm@ozymandias ~ % vagrant up                          
[...]
cfm@ozymandias ~ % vagrant ssh -c "cat /etc/machine-id"
4117adcefa904fa48e0ba81bf75e4678
Connection to 127.0.0.1 closed.
cfm@ozymandias ~ % vagrant destroy
[...]
```

## Comment by sford at 2023-02-07T16:36:17Z

I am seeing the same bug with `bento/ubuntu-22.04`. I assume the 20.04 and 22.04 boxes are sharing setup and are impacted by same issue with `machine-id` being the same.

Here is the reproduce steps from ticket using `bento/ubuntu-22.04` and `parallels` provider:
```
% vagrant up
Bringing machine 'default' up with 'parallels' provider...
...
==> default: Checking if box 'bento/ubuntu-22.04' version '202212.13.0' is up to date...
...
% vagrant ssh -c "cat /etc/machine-id"
ad945f1feeab504f9a6f5ea1494b44b7
% vagrant destroy
% vagrant up
Bringing machine 'default' up with 'parallels' provider...
...
==> default: Checking if box 'bento/ubuntu-22.04' version '202212.13.0' is up to date...
...
% vagrant ssh -c "cat /etc/machine-id"
ad945f1feeab504f9a6f5ea1494b44b7
```

We are also using `libvirt` provider. When bringing up multiple boxes at once, the impact that `machine-id` re-use has on DHCP is easily seen by how all the boxes receive the same IP address:
```
Bringing machine 'vm1' up with 'libvirt' provider...
Bringing machine 'vm2' up with 'libvirt' provider...
Bringing machine 'vm3' up with 'libvirt' provider...
Bringing machine 'vm4' up with 'libvirt' provider...
Bringing machine 'vm5' up with 'libvirt' provider...
==> vm5: Checking if box 'bento/ubuntu-22.04' version '202212.11.0' is up to date...
==> vm2: Checking if box 'bento/ubuntu-22.04' version '202212.11.0' is up to date...
==> vm3: Checking if box 'bento/ubuntu-22.04' version '202212.11.0' is up to date...
==> vm4: Checking if box 'bento/ubuntu-22.04' version '202212.11.0' is up to date...
==> vm1: Checking if box 'bento/ubuntu-22.04' version '202212.11.0' is up to date...
    vm2: SSH address: 192.168.121.113:22
    vm1: SSH address: 192.168.121.113:22
    vm3: SSH address: 192.168.121.113:22
    vm4: SSH address: 192.168.121.113:22
    vm5: SSH address: 192.168.121.113:22
```
In this example output, VM creation quickly fails due to these IP address issues.

Expected behavior is that vagrant boxes using `bento/ubuntu-22.04` (other others) don't have the same `machine-id`.

## Comment by sford at 2023-02-08T16:04:52Z

I looked into this a bit more, specifically @tas50 's comment around /etc/machine-id truncation:

> We currently truncate the machine-id file as part of the cleanup.sh script that runs on Ubuntu. This should be empty on your libvirt images. Can you check that to confirm if it's empty?

I checked `bento/ubuntu-22.04` image for `libvirt` using `virt-rescue` and discovered this:

```
><rescue> cat /var/lib/dbus/machine-id
b4047197195f4f359571cd0658157294
><rescue> cat /etc/machine-id
><rescue>
```
It appears that `/etc/machine-id` is indeed truncated, but I found `/var/lib/dbus/machine-id` with a machine-id set.

When I bring this VM up in vagrant, it is using the machine-id from `/var/lib/dbus/machine-id`:

```
$ vagrant up vm1
Bringing machine 'vm1' up with 'libvirt' provider...
==> vm1: Checking if box 'bento/ubuntu-22.04' version '202212.11.0' is up to date...
...
$ vagrant ssh vm1 -c 'cat /etc/machine-id'
b4047197195f4f359571cd0658157294
$ vagrant ssh vm1 -c 'cat /var/lib/dbus/machine-id'
b4047197195f4f359571cd0658157294
```

While I am testing with `libvirt`, I don't think that is a factor since we are seeing machine-id issues in other providers.

But... it appears that the root cause is that machine-id isn't being cleared from `/var/lib/dbus/machine-id`, which causes machines to end up with the same `machine-id`.

As a test... I modified my `bento/ubuntu-22.04` image and truncated `/var/lib/dbus/machine-id`. After I did that, `machine-id` was generated per-vagrant VM:

```
$ vagrant up vm1
Bringing machine 'vm1' up with 'libvirt' provider...
==> vm1: Checking if box 'bento/ubuntu-22.04' version '202212.11.0' is up to date...
    vm1: SSH address: 192.168.121.228:22
$ vagrant ssh vm1 -c 'cat /etc/machine-id'
5d6b62ac52dd4eb689269f1012a4e9a9

....

$ vagrant up vm1
Bringing machine 'vm1' up with 'libvirt' provider...
==> vm1: Checking if box 'bento/ubuntu-22.04' version '202212.11.0' is up to date...
    vm1: SSH address: 192.168.121.143:22
$ vagrant ssh vm1 -c 'cat /etc/machine-id'
692ae02bd4aa4d31bed930245be89eed
```





## Comment by cfm at 2023-02-08T17:58:16Z

Nice find, @sford!  The extra truncation operation should be easy to tack on here:

https://github.com/chef/bento/blob/1df5023908847526bbfeb9d4cf16af1e310904eb/packer_templates/scripts/ubuntu/cleanup_ubuntu.sh#L91-L92

I can open a pull request with that change today or tomorrow unless you beat me to it.  :-)

## Comment by cfm at 2023-02-10T02:11:14Z

Further isolated the culprit as demonstrated here.  Fix proposed in #1471.

```sh-session
cfm@ozymandias ~ % vagrant box add bento/ubuntu-20.04 --box-version 202112.19.0
[...]
==> box: Successfully added box 'bento/ubuntu-20.04' (v202112.19.0) for 'virtualbox'!
cfm@ozymandias ~ % vagrant up                                                  
[...]
cfm@ozymandias ~ % vagrant ssh -c "ls -al /etc/machine-id /var/lib/dbus/machine-id"
-r--r--r-- 1 root root 33 Feb 10 01:34 /etc/machine-id
lrwxrwxrwx 1 root root 15 Dec 19  2021 /var/lib/dbus/machine-id -> /etc/machine-id
Connection to 127.0.0.1 closed.
cfm@ozymandias ~ % vagrant destroy
    default: Are you sure you want to destroy the 'default' VM? [y/N] y
==> default: Forcing shutdown of VM...
==> default: Destroying VM and associated drives...
cfm@ozymandias ~ % vagrant box update                                              
[...]
==> default: Successfully added box 'bento/ubuntu-20.04' (v202212.11.0) for 'virtualbox'!
cfm@ozymandias ~ % vagrant up                                                      
Bringing machine 'default' up with 'virtualbox' provider...
[...]
cfm@ozymandias ~ % vagrant ssh -c "ls -al /etc/machine-id /var/lib/dbus/machine-id"
-r--r--r-- 1 root root 33 Feb 10 01:38 /etc/machine-id
-rw-r--r-- 1 root root 33 Dec 11 06:23 /var/lib/dbus/machine-id
```

## Comment by kom177 at 2024-02-05T18:28:06Z

The same problem still persists in recent box bento/ubuntu-22.04-arm64 202401.31.0 for arm64 in Parallels (19.1.1) provider - any new machine gets the same IP from DHCP. Generating new MAC address for public network interface solves problem.
