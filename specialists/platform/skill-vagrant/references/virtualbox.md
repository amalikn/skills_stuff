---
Title: VirtualBox
Category: reference
Status: current
Authority: >-
  skill-vagrant canonical reference; claims carry evidence labels and cite captures in documents/
Scope: skill-vagrant: Vagrant's built-in VirtualBox provider on macOS Apple silicon (VirtualBox 7.1 and 7.2)
Last reviewed: 2026-11-09
Summary: >-
  VirtualBox under Vagrant on an Apple silicon Mac: which versions run arm64 guests, Vagrant's support by version, provider options, macOS
  host-only networks and their allowed range, internal networks, VBoxManage equivalents of prlctl, and the Extension Pack licence.
---

# VirtualBox

VirtualBox is Vagrant's built-in, documented default provider ([vagrant-providers-default.md]). On this Mac it runs beside Parallels: VirtualBox 7.2.22 (upgraded from 7.2.10 that day) with the Oracle Extension Pack 7.2.10, arm64
bento boxes for it, and one lab (observed 2026-11-09). Captures named `[file]` are in [documents/research-sources-20261109/](../documents/research-sources-20261109/readme.md) unless another folder is named.

## Contents

- [Apple silicon support](#apple-silicon-support)
- [Vagrant support by version](#vagrant-support-by-version)
- [Provider block](#provider-block)
- [Networking on a macOS host](#networking-on-a-macos-host)
- [VBoxManage for a lab](#vboxmanage-for-a-lab)
- [Licence: base package and Extension Pack](#licence-base-package-and-extension-pack)
- [Worked example](#worked-example)

## Apple silicon support

| Version             | What it changed on an Arm Mac                                                            | Source                                       |
| ------------------- | ---------------------------------------------------------------------------------------- | -------------------------------------------- |
| 7.1.0 (2024-09-09)  | "macOS/Arm host: Arm virtualization for Linux and BSD VMs"                               | [virtualbox-changelog-7.1.md]                |
| 7.1.x               | macOS/Arm UI loses its BETA label; Arm Guest Additions upgrade from the Devices menu     | [virtualbox-changelog-7.1.md]                |
| 7.1.6               | the floor bento states for its arm64 VirtualBox boxes ("Virtualbox 7.1.6+ required")     | [bento-readme-github.md] (2026-11-07 folder) |
| 7.2.0               | the saved state of Arm VMs from 7.1 is incompatible: shut such VMs down before upgrading | [virtualbox-changelog-7.2.md]                |
| 7.2.22 (2026-10-20) | latest release; this Mac runs it since 2026-11-09                               | [virtualbox-changelog-7.2.md]                |

All VERIFIED_PRIMARY. The guest must be arm64: VirtualBox on an Arm host virtualizes Arm guests, so an amd64 box is not a lab path here (as with Parallels, [boxes-and-pinning.md](boxes-and-pinning.md#architecture-on-apple-silicon)). Before a 7.1 to 7.2
upgrade, `vagrant halt` every machine that is `saved` (`vagrant suspend` leaves one in that state) and delete snapshots that carry a saved state, or they will not restore.

## Vagrant support by version

Vagrant checks the installed VirtualBox version and refuses one it does not know. Support was added in (VERIFIED_PRIMARY, [vagrant-changelog-main-github.md]): VirtualBox 7.0 in Vagrant 2.3.2
(GH-12947), 7.1 in **2.4.2** (2024-11-01, GH-13513), 7.2 in **2.4.9** (2025-08-21, GH-13709). So VirtualBox 7.2 needs Vagrant 2.4.9, the latest release; upgrading VirtualBox to a new minor line before
Vagrant supports it stops every VirtualBox lab. On macOS, Vagrant 2.3.3 added VirtualBox 7 "hostonlynets" for `private_network` (GH-12983, [vagrant-pr-12983.md]).

## Provider block

```ruby
config.vm.provider "virtualbox" do |vb|
  vb.name = "lab-a"                 # the VirtualBox VM name; default <folder>_<timestamp>
  vb.memory = 4096                  # MiB
  vb.cpus = 4
  vb.gui = false                    # headless
  # vb.linked_clone = true          # differencing disk on a master VM imported once; default is a full import
  # vb.check_guest_additions = false
  # vb.default_nic_type = "virtio"
  vb.customize ["modifyvm", :id, "--nicpromisc2", "allow-all"]   # runs in the order written
end
```

Options and their defaults: [vagrant-vbox-configuration.md] (VERIFIED_PRIMARY). `customize` runs `VBoxManage` with `:id` replaced, in the order given, before boot. As with Parallels, a `customize`
that adds something (`storageattach` of a new disk) is wrong on every boot; a primary disk is grown with `config.vm.disk :disk, size: "<N>GB", primary: true`, which Vagrant's disk docs show for
VirtualBox and which cannot shrink a disk ([vagrant-disks-usage.md], 2026-11-07 folder).

## Networking on a macOS host

```text
 Mac host (VirtualBox 7.x)
 ├─ NAT (adapter 1, default) ─────────── per-VM NAT; Vagrant's SSH path via a forwarded port
 ├─ host-only NETWORK (not adapter) ──── host gets the lowest address of the range; VMs and host share it
 │     only inside the allowed range, unless /etc/vbox/networks.conf adds one
 ├─ internal network "name" ──────────── VM to VM only, no host, no DHCP unless configured
 └─ bridged to en0 ───────────────────── the real LAN
```

- "Hosts running recent macOS versions do not support host-only adapters. These adapters are replaced by host-only networks, which define a network mask and an IP address range, where the host network
  interface receives the lowest address in the range" (VERIFIED_PRIMARY, [virtualbox-manual-networking.md]). Vagrant 2.3.3 and later create these for `private_network` on macOS
  ([vagrant-pr-12983.md]).
- On Linux, macOS and Solaris, VirtualBox allows host-only addresses only in its default range (a /21; the exact range is in [virtualbox-manual-networking.md]) and IPv6 link-local only; other ranges
  are enabled in `/etc/vbox/networks.conf`. The host-only interface limit on Linux and macOS is 128 (VERIFIED_PRIMARY, same capture). A `private_network` address outside the range fails at `vagrant
  up`, and Vagrant validates the range itself since 2.2.19 (GH-12564, [vagrant-changelog-main-github.md]). Editing `networks.conf` is a host change for the operator, not a lab script.
- `virtualbox__intnet: "<name>"` on a `private_network` makes it an internal network; the double underscore marks a VirtualBox-only option that other providers ignore ([vagrant-vbox-networking.md]).
  Two machines with the same name share the wire, with no host on it: the VirtualBox equivalent of the Parallels host-only wire used for a site trunk.
- `name: "<host-only network>"` picks which host-only network an interface uses ([vagrant-vbox-networking.md]).

## VBoxManage for a lab

From the 7.2.10 help, captured before the same-day upgrade to 7.2.22 ([virtualbox-7.2.10-vboxmanage-help.txt], VERIFIED_PRIMARY). Every call gets a `timeout`.

| Need                    | Command                                                                                            | Writes           |
| ----------------------- | -------------------------------------------------------------------------------------------------- | ---------------- |
| What exists             | `VBoxManage list vms`; `VBoxManage list runningvms`                                                | no               |
| One VM as key=value     | `VBoxManage showvminfo <vm> --machinereadable`                                                     | no               |
| Console picture         | `VBoxManage controlvm <vm> screenshotpng <file.png>`                                               | no (a local PNG) |
| Command without network | `VBoxManage guestcontrol <vm> run --username <u> --passwordfile <f> --exe /bin/bash -- -c '<cmd>'` | guest            |
| Graceful stop           | `VBoxManage controlvm <vm> acpipowerbutton`                                                        | yes              |
| Cold reset              | `VBoxManage controlvm <vm> reset` ("the state of the VM is not saved")                             | yes              |
| Power off               | `VBoxManage controlvm <vm> poweroff` ("data might be lost")                                        | yes              |
| Snapshot                | `VBoxManage snapshot <vm> take <name>`; `list`; `restore <name>`                                   | yes              |
| Extension Pack in use   | `VBoxManage list extpacks`                                                                         | no               |

`guestcontrol` needs the Guest Additions running and a guest account and password, unlike `prlctl exec`, which runs as root through Parallels Tools; prefer `vagrant ssh` and keep the password in a
file outside the repo, never on the command line. `screenshotpng` plays the role of `prlctl capture` for a wedged guest.

## Licence: base package and Extension Pack

| Part                             | Licence                                                                                                                           | Source (VERIFIED_PRIMARY)     |
| -------------------------------- | --------------------------------------------------------------------------------------------------------------------------------- | ----------------------------- |
| VirtualBox base package          | GPLv3; "perpetual and cannot be taken back unless you violate the license"                                                        | [virtualbox-licensing-faq.md] |
| Oracle VirtualBox Extension Pack | PUEL: free for personal and educational use; "expressly exclude any use of the product for commercial purposes or to operate or   | [virtualbox-licensing-faq.md] |
|                                  |   run a business"; an Enterprise licence is sold for that; no trial                                                               |                               |

Vagrant does not need the Extension Pack; the base package runs the provider. This Mac has Extension Pack 7.2.22 installed (observed 2026-11-09, `VBoxManage list extpacks`: "Oracle Cloud
Infrastructure integration, PXE ROM"). Whether its use here is personal or business is the operator's call: recorded as personal use (operator, 2026-11-09; USER_STATED). A lab that needs neither feature can run
without it. This is a summary of
Oracle's FAQ, not legal advice.

## Worked example

`vagrant_stuff/family-friendly-vsmc01/Vagrantfile` (untracked working copy, read 2026-11-09; addresses redacted): a bento/ubuntu-22.04 SMC machine with two internal networks for its LAN segments and
promiscuous NICs, and a desktop client VM on the same internal network.

```ruby
c.vm.network "private_network", ip: "<lab-a>", auto_config: false, virtualbox__intnet: "smc01_lan"   # eth4: segment for the client VM
c.vm.provider "virtualbox" do |vb|
  vb.name = vagrant_name
  vb.memory = 2048
  vb.cpus = 1
  vb.customize ["modifyvm", :id, "--nic1", "nat"]
  vb.customize ["modifyvm", :id, "--natnet1", "<private /24>"]       # moves the NAT range off a clash
  vb.customize ["modifyvm", :id, "--nicpromisc4", "allow-all"]
  vb.customize ["modifyvm", :id, "--nicpromisc5", "allow-all"]
end
```

The box is pinned only for the client (`cloudicio/ubuntu-desktop` 24.04.1); the SMC machine's `bento/ubuntu-22.04` has no `box_version`, which `vagrantfile_lint.py --provider virtualbox` reports. The
file is not in git yet, which breaks the project-copy rule ([lab-safety-and-guards.md](lab-safety-and-guards.md#keep-a-project-copy-of-the-canonical-vagrantfile)).

> **Learned 2026-11-09** · VirtualBox 7.2.22, Vagrant 2.4.9 · VERIFIED_PRIMARY (lab observation) · Source: `VBoxManage list vms` (empty), `vagrant global-status`, `.vagrant/machines/*/virtualbox/id`, `mdfind` for the `.vbox` files, 2026-11-09 · Falsifier: a `VBoxManage list vms` that lists the ids Vagrant holds
> Vagrant's cache can name VirtualBox machines whose VMs no longer exist: `global-status` showed two `poweroff` machines, their id files held UUIDs,
> but VirtualBox had no registered VM and no `.vbox` file anywhere. `just inventory-lab` reports such a machine as `(virtualbox)->not registered`.
> The next `vagrant up` in that folder creates new VMs; it does not recover the old disks.
