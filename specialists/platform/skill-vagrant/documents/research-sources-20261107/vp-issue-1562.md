<!-- capture: verbatim third-party text, not authored here -->
**Canonical URL**: https://github.com/chef/bento/issues/1562
**Retrieved**: 2026-11-07 15:55 AEDT
**HTTP status**: 200 via GitHub API (`gh issue view --json`)

---

# #1562 Bug has potentially returned - Duplicate MAC / IP for ubuntu boxes

State: CLOSED; opened 2024-04-05T22:57:49Z; closed 2024-07-22T18:31:23Z

## Body

This was addressed previously in #1473 for 20.04 and 22.04.

# Version

bento/ubuntu-22.04-arm64 v202401.31.0

## Environment

MacOS 14.4.1
Mac Studio M2 Ultra
Vagrant 2.4.1
Parallels 19.3.0

## Scenario

Creating 2 virtual machines from the same base image and version result in a duplicate "mac address" (yes ubuntu still uses the 'machine id' when requesting IP addresses) which results in the same IP being assigned on the shared network.

## Steps to Reproduce
```
Vagrant.configure("2") do |config|
  config.vm.
  config.vm.box = "bento/ubuntu-22.04-arm64"
  config.vm.box_version = "202401.31.0"
  config.vm.box_architecture = :auto

  config.vm.provider "parallels" do |v|
    v.memory = 2048
    v.cpus = 1
    v.linked_clone = false
    v.update_guest_tools = true
  end

  config.ssh.forward_agent = true

  config.vm.define "machine-one", primary: true do |web|
    web.vm.hostname = "machine-one"
  end
end
```
MACHINE TWO
```
Vagrant.configure("2") do |config|
  config.vm.
  config.vm.box = "bento/ubuntu-22.04-arm64"
  config.vm.box_version = "202401.31.0"
  config.vm.box_architecture = :auto

  config.vm.provider "parallels" do |v|
    v.memory = 2048
    v.cpus = 1
    v.linked_clone = false
    v.update_guest_tools = true
  end

  config.ssh.forward_agent = true

  config.vm.define "machine-two", primary: true do |web|
    web.vm.hostname = "machine-two"
  end
end
```


## Expected Result

Each machine should get unique ip addresses from the shared network DHCP. Potentially Parallels should report different MAC addresses.

## Actual Result

Machines get the same IP address from the shared network DHCP.

```
vagrant up
Bringing machine 'machine-one' up with 'parallels' provider...
==> machine-one: Checking if box 'bento/ubuntu-22.04-arm64' version '202401.31.0' is up to date...
==> machine-one: Preparing network interfaces based on configuration...
    machine-one: Adapter 0: shared
    machine-one: Adapter 1: hostonly
==> machine-one: Clearing any previously set network interfaces...
==> machine-one: Running 'pre-boot' VM customizations...
==> machine-one: Booting VM...
==> machine-one: Waiting for machine to boot. This may take a few minutes...
    machine-one: SSH address: 10.211.55.11:22
....
```

```
vagrant up
Bringing machine 'machine-two' up with 'parallels' provider...
==> machine-two: Checking if box 'bento/ubuntu-22.04-arm64' version '202401.31.0' is up to date...
==> machine-two: Preparing network interfaces based on configuration...
    machine-two: Adapter 0: shared
    machine-two: Adapter 1: hostonly
==> machine-two: Clearing any previously set network interfaces...
==> machine-two: Running 'pre-boot' VM customizations...
==> machine-two: Booting VM...
==> machine-two: Waiting for machine to boot. This may take a few minutes...
    machine-two: SSH address: 10.211.55.11:22
....
```

## Comment by Stromweld at 2024-04-09T15:20:36Z

can you test this new build https://github.com/chef/bento/actions/runs/8601528699/artifacts/1395233285 or any of the ubuntu images from this pipeline. https://github.com/chef/bento/actions/runs/8601528699#artifacts

## Comment by ps-mattstuart at 2024-04-13T16:56:13Z

I will attempt in short order here

## Comment by Stromweld at 2024-07-22T18:31:23Z

i believe this is fixed with #1572 feel free to reopen this issue if you find that not to be the case.
