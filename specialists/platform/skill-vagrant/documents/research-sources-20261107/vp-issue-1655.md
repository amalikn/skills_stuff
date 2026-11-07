<!-- capture: verbatim third-party text, not authored here -->
**Canonical URL**: https://github.com/chef/bento/issues/1655
**Retrieved**: 2026-11-07 15:55 AEDT
**HTTP status**: 200 via GitHub API (`gh issue view --json`)

---

# #1655 cloud init not working

State: OPEN; opened 2025-12-05T14:50:45Z; closed -

## Body

# Version

v5.0.0 (2025-10-27)

## Environment

VirtualBox: 7.2.4 r170995
Host OS: Arch Linux

## Scenario

Start a Vagrant VM with the official bento/ubuntu-24.04 box and create an additional user (user1) via cloud-init.

## Steps to Reproduce

Vagrantfile
```
Vagrant.configure("2") do |config|
  config.vm.box = "bento/ubuntu-24.04"

  config.vm.provider "virtualbox" do |v|
    v.name = "node1"
    v.memory = 1024
    v.cpus = 2
  end

  config.vm.cloud_init :user_data do |cloud_init|
    cloud_init.content_type = "text/cloud-config"
    cloud_init.path = "cloud.cfg"
  end

end

```

cloud.cfg
```
#cloud-config

users:
  - name: user1
    sudo: "ALL=(ALL) NOPASSWD:ALL"
    plain_text_passwd: 123456
    lock_passwd: false

```

1. Create the Vagrantfile and cloud.cfg as shown above.
2. run `vagrant up`
3. After the VM is up, run `vagrant ssh`
4. Run cat /etc/passwd | grep user1 or id user1, check if user1 is exists.

## Expected Result

cloud-init processes the provided cloud.cfg file during first boot and creates the user user1.

## Actual Result

No user user1 is created.

## Comment by Stromweld at 2025-12-05T15:47:00Z

Did this work previously?

## Comment by ty2 at 2025-12-05T21:24:30Z

I'm not sure if this worked in previous versions. This was my initial attempt to use it.

## Comment by konstruktoid at 2025-12-08T00:30:23Z

`cloud-init` is disabled by default (`cat /etc/cloud/cloud-init.disabled`), so you need to enable it and then reboot.

```Vagrantfile
Vagrant.configure("2") do |config|
  config.vm.cloud_init :user_data do |cloud_init|
    cloud_init.content_type =  "text/cloud-config"
    cloud_init.inline = <<-EOF
      #cloud-config
      users:
        - name: issue1655
          shell: /bin/bash
    EOF
  end

  hosts = [
    { name: "noble", box: "bento/ubuntu-24.04" },
  ]

  hosts.each do |host|
    config.vm.define host[:name] do |node|
      node.vm.box = host[:box]
      node.ssh.insert_key = true
      node.ssh.key_type = "ed25519"
      node.vm.hostname = host[:name]
      node.vm.boot_timeout = 600
      node.vm.provision "shell",
        inline: <<-SHELL
        cloud-init clean --machine-id
      SHELL
    end
  end
end
```

## Comment by balajisam1 at 2026-04-04T16:48:09Z

After reboot, cloud-init is not starting.

[root@Test-Rocky dhcpcd]# systemctl status cloud-init
× cloud-init.service - Cloud-init: Network Stage
     Loaded: loaded (/usr/lib/systemd/system/cloud-init.service; enabled; preset: enabled)
     Active: failed (Result: exit-code) since Tue 2026-03-31 17:16:08 IST; 7s ago
Invocation: 7ba686862a7948f48a83265fe1699976
    Process: 2246 ExecStart=/usr/bin/cloud-init init (code=exited, status=1/FAILURE)
   Main PID: 2246 (code=exited, status=1/FAILURE)
   Mem peak: 29.1M
        CPU: 317ms

Mar 31 17:16:08 Test-Rocky cloud-init[2249]:   File "/usr/lib/python3.12/site-packages/cloudinit/sources/DataSourceCloudStack.py", line 133, in _get_domainname
Mar 31 17:16:08 Test-Rocky cloud-init[2249]:     latest_lease = self.distro.dhcp_client.get_newest_lease(
Mar 31 17:16:08 Test-Rocky cloud-init[2249]:                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Mar 31 17:16:08 Test-Rocky systemd[1]: cloud-init.service: Main process exited, code=exited, status=1/FAILURE
Mar 31 17:16:08 Test-Rocky cloud-init[2249]:   File "/usr/lib/python3.12/site-packages/cloudinit/net/dhcp.py", line 879, in get_newest_lease
Mar 31 17:16:08 Test-Rocky cloud-init[2249]:     raise NoDHCPLeaseError from error
Mar 31 17:16:08 Test-Rocky cloud-init[2249]: cloudinit.net.dhcp.NoDHCPLeaseError
Mar 31 17:16:08 Test-Rocky cloud-init[2249]: ------------------------------------------------------------
Mar 31 17:16:08 Test-Rocky systemd[1]: cloud-init.service: Failed with result 'exit-code'.
Mar 31 17:16:08 Test-Rocky systemd[1]: Failed to start cloud-init.service - Cloud-init: Network Stage.

## Comment by konstruktoid at 2026-04-05T17:12:44Z

what version are you running @balajisam1?
https://github.com/canonical/cloud-init/issues/5961 might be related

## Comment by balajisam1 at 2026-04-06T03:33:10Z

@konstruktoid Thanks for the response.

We are using below version.

cloud-init-24.4-6.el10_1.1.rocky.0.1.noarch
cloud-utils-growpart-0.33-11.el10.noarch


## Comment by konstruktoid at 2026-04-06T20:09:43Z

can you verify in another way that the DHCP is actually working as intended, thinking about the `NoDHCPLeaseError`? 

## Comment by balajisam1 at 2026-04-07T04:43:13Z

Hi @konstruktoid Yes DHCP is working.

[root@Test-Rocky ~]# systemctl status dhcpcd.service
● dhcpcd.service - A minimalistic network configuration daemon with DHCPv4, rdisc and DHCPv6 support
     Loaded: loaded (/usr/lib/systemd/system/dhcpcd.service; enabled; preset: disabled)
     Active: active (running) since Tue 2026-04-07 10:11:13 IST; 36s ago
 Invocation: df9daf17127240a08a5230231e1ba8fa
   Main PID: 959 (dhcpcd)
      Tasks: 5 (limit: 48778)
     Memory: 2.6M (peak: 5.1M)
        CPU: 57ms
     CGroup: /system.slice/dhcpcd.service
             ├─ 959 "dhcpcd: [manager] [ip4] [ip6]"
             ├─ 969 "dhcpcd: [privileged proxy]"
             ├─ 970 "dhcpcd: [network proxy]"
             ├─ 971 "dhcpcd: [control proxy]"
             └─1003 "dhcpcd: [BPF ARP] ens3 10.0.0.98"

Apr 07 10:11:13 Test-Rocky dhcpcd[969]: ens3: IAID 02:46:00:22
Apr 07 10:11:13 Test-Rocky dhcpcd[969]: ens3: adding address fe80::c8a:fe04:3e66:486b
Apr 07 10:11:13 Test-Rocky dhcpcd[969]: ens3: rebinding lease of 10.0.0.98
Apr 07 10:11:14 Test-Rocky dhcpcd[969]: ens3: soliciting an IPv6 router
Apr 07 10:11:15 Test-Rocky dhcpcd[969]: ens3: probing address 10.0.0.98/24
Apr 07 10:11:16 Test-Rocky dhcpcd[969]: control command: dhcpcd --dumplease --ipv4only ens3
Apr 07 10:11:20 Test-Rocky dhcpcd[969]: ens3: leased 10.0.0.98 for infinity
Apr 07 10:11:20 Test-Rocky dhcpcd[969]: ens3: adding route to 10.0.0.0/24
Apr 07 10:11:20 Test-Rocky dhcpcd[969]: ens3: adding default route via 10.0.0.1
Apr 07 10:11:27 Test-Rocky dhcpcd[969]: ens3: no IPv6 Routers available


## Comment by konstruktoid at 2026-04-07T13:16:31Z

How do you add `cloud-init`? 
The following returns "cloud-init is not found. Please ensure that cloud-init is installed and available on path for guest 'rocky'."

```
Vagrant.configure("2") do |config|
  config.vm.cloud_init :user_data do |cloud_init|
    cloud_init.content_type =  "text/cloud-config"
    cloud_init.inline = <<-EOF
      #cloud-config
      users:
        - name: issue1655
          shell: /bin/bash
    EOF
  end

  hosts = [
    { name: "rocky", box: "bento/rockylinux-10" },
  ]

  hosts.each do |host|
    config.vm.define host[:name] do |node|
      node.vm.box = host[:box]
      node.ssh.insert_key = true
      node.ssh.key_type = "ed25519"
      node.vm.hostname = host[:name]
      node.vm.boot_timeout = 600
    end
  end
end
```
