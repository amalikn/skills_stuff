<!-- capture: verbatim third-party text, not authored here -->
**Canonical URL**: https://github.com/Parallels/vagrant-parallels/issues/441
**Retrieved**: 2026-11-07 15:52 AEDT
**HTTP status**: 200 via GitHub API (`gh issue view --json`)

---

# #441 Multi-Machine - DHCP Address Conflicts with Shared Networking On Default Interface

State: CLOSED; opened 2023-04-04T02:46:21Z; closed 2023-04-12T21:42:32Z

## Body

## Description/Issue

I am seeing an issue with the Vagrant Parallels Provider where a multi-machine Vagrantfile will assign the same IP address on the Shared Network to multiple VMs. Regardless if I disable parallel provisioning or individually create the VM as defined one at a time, the VMs report the same public/bridged IP address:

```
❯ prlctl list --full
UUID                                    STATUS       IP_ADDR         NAME
{26df1fde-d2a6-4063-933c-108d6dd9d730}  running      10.211.55.4     vagrant-k8s-control
{2175f695-0645-4be2-8146-19ee0362d76a}  running      10.211.55.4     vagrant-k8s-worker-1
{eec852ff-f8bd-497b-bac4-4b44012e0a04}  running      10.211.55.4     vagrant-k8s-worker-2
```

However, when using and creating VM, both with Windows 11 and Ubuntu, Parallels appears to be able to correctly assign non-conflicting IPs which suggest an possible issue with the Parallels plugin instead.

```
UUID                                    STATUS       IP_ADDR         NAME
{828445b6-2a00-44b5-a017-9e3c93a54e92}  running      10.211.55.5     Ubuntu 22.04 ARM64
{02fa6948-66f0-4f7b-96fa-562025dee57b}  running      10.211.55.3     Windows 11
{26df1fde-d2a6-4063-933c-108d6dd9d730}  running      10.211.55.4     vagrant-k8s-control
{2175f695-0645-4be2-8146-19ee0362d76a}  running      10.211.55.4     vagrant-k8s-worker-1
{eec852ff-f8bd-497b-bac4-4b44012e0a04}  running      10.211.55.4     vagrant-k8s-worker-2
```

See also the following forum post where a similar issue is reported:
https://forum.parallels.com/threads/parallels-18-vagrant-multi-machine-issues.360012/

## Expected Behavior
When creating machines with a mult-machine Vagrantfile, the VMs are brought up and assigned non-conflicting IP addresses

## Actual Behavior
Machines managed by Vagrant use the same IP address

## System Info
macOS Ventura 13.3 (M2 Pro)
Parallels Desktop 18.2.0
Vagrant Parallels Plugin 2.3.1
Vagrant 2.3.4


## Comment by legal90 at 2023-04-04T07:27:20Z

Thank you for reporting this issue, @xinkecf35 ! 
It seems that it is specific to M-series Mac hosts, as I can't reproduce it on my Intel-based Macbook - IPs are allocated just fine, without any collision. Just for the record - I used this Vagrantfile:
```
# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
  config.vm.define "web" do |web|
    web.vm.box = "bento/ubuntu-20.04"
  end
  config.vm.define "db" do |db|
    db.vm.box = "bento/ubuntu-20.04"
  end
end
```
P.s. On M-series host we would need to use `bento/ubuntu-20.04-arm64` boxes instead.
____________
I guess, we would need some insides from Parallels Inc. here.  
@bineesh-n , do you know if it's the known issue on M-series Macs?

## Comment by bineesh-n at 2023-04-04T08:27:40Z

Hi @legal90 I'll check and update soon.

## Comment by xinkecf35 at 2023-04-04T13:12:33Z

If it helps, I did try the minimal Vagrantfile as well and was able to reproduce the issue without the cruft my Vagrantfile has

```
❯ prlctl list --full
UUID                                    STATUS       IP_ADDR         NAME
{37d1ce1a-789a-4fa7-830a-99803086db9c}  running      10.211.55.4     reproduce-issue_db_1680613755534_19687
{241a2b93-1fc4-4ad3-8493-31dd5ed1da84}  running      10.211.55.4     reproduce-issue_web_1680613752360_2621
```

```
Vagrant.configure("2") do |config|
  config.vm.define "web" do |web|
    web.vm.box = "bento/ubuntu-20.04-arm64"
  end
  config.vm.define "db" do |db|
    db.vm.box = "bento/ubuntu-20.04-arm64"
  end
end
```

## Comment by sai-kumar-peddireddy at 2023-04-05T12:55:42Z

hi @xinkecf35 

Please send a [Technical report](https://kb.parallels.com/9058) to Parallels team

## Comment by xinkecf35 at 2023-04-05T16:39:01Z

@sai-kumar-peddireddy Okay, I have sent a technical report via the KB article as described with ID 422226374

Let me know if I should also important a support request since I see from the KB they are exclusive items.

## Comment by NickSmet at 2023-04-12T10:58:31Z

Hi,

The issue seems to be associated with he following:

1. Ubuntu VMs get ip based on the machine-id
2. There is an issue with the last version of bento/ubuntu 20.04 for ARM64 whereby creating new VM from the box does no change the the id.

See https://github.com/chef/bento/issues/1473

Doesn't seem like the fix has been released yet (last release for ARM64 is 3 months ago https://app.vagrantup.com/bento/boxes/ubuntu-20.04-arm64 ).

Hence, the workaround is to add the following line to your Vagrant file:

config.vm.box_version = "202112.19.0"

To make it use the previous version of the box where the issue wasn't present.


## Comment by xinkecf35 at 2023-04-12T21:42:32Z

Ah okay, thank you all for looking into this. I can the VM is now behaving as expected:

```
❯ prlctl list --full
UUID                                    STATUS       IP_ADDR         NAME
{ae172139-2a43-413f-b018-9c2d358159dd}  running      10.211.55.9     reproduce-issue_db_1681335593357_14405
{82256d3e-8e14-4059-bc53-0d928ed63fa1}  running      10.211.55.10    reproduce-issue_web_1681335598228_25324
```

I'll close out my issue now since the issue doesn't lie with the plugin or even Parallels
