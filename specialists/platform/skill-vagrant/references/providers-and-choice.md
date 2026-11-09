---
Title: Providers and choice
Category: reference
Status: current
Authority: >-
  skill-vagrant canonical reference; claims carry evidence labels and cite captures in documents/
Scope: skill-vagrant: Vagrant providers on macOS Apple silicon (Parallels, VirtualBox, QEMU, libvirt) and how a lab picks one
Last reviewed: 2026-11-09
Summary: >-
  Which Vagrant provider fits a lab on an Apple silicon Mac, what each needs and lacks, how Vagrant picks a provider, how one Vagrantfile serves
  several, and the exec, console and power commands of each side by side.
---

# Providers and choice

Vagrant drives a hypervisor through a provider. This Mac has four installed (observed 2026-11-09, `vagrant plugin list` and the tools' version commands; [compatibility.yaml](../compatibility.yaml) `lab-mac-2026-11-09`).
Captures named `[file]` are in [documents/research-sources-20261109/](../documents/research-sources-20261109/readme.md) unless another folder is named.

## Contents

- [The four providers](#the-four-providers)
- [Pick a provider](#pick-a-provider)
- [How Vagrant chooses](#how-vagrant-chooses)
- [One Vagrantfile, several providers](#one-vagrantfile-several-providers)
- [The same task on each provider](#the-same-task-on-each-provider)
- [What changes per provider](#what-changes-per-provider)

## The four providers

| Provider (plugin)               | Observed here         | Hypervisor and host                                     | Licence                                    | Detail              |
| ------------------------------- | --------------------- | ------------------------------------------------------- | ------------------------------------------ | ------------------- |
| `parallels` (vagrant-parallels) | 2.4.10 (latest)        | Parallels Desktop 27 on this Mac                        | plugin MIT; Parallels Pro/Business licence | [parallels-prlctl.md](parallels-prlctl.md) |
| `virtualbox` (built in)         | VirtualBox 7.2.22     | VirtualBox on this Mac; arm64 guests only               | GPLv3 base; Extension Pack PUEL            | [virtualbox.md](virtualbox.md) |
| `qemu` (vagrant-qemu)           | 0.7.0 (latest)        | QEMU 11.1.3 from Homebrew, hvf acceleration on this Mac | plugin MIT; QEMU GPLv2                     | [qemu-and-libvirt.md](qemu-and-libvirt.md) |
| `libvirt` (vagrant-libvirt)     | 0.12.2 (latest, 2023) | libvirtd + QEMU/KVM on a **Linux** host, reached by URI | plugin MIT                                 | [qemu-and-libvirt.md](qemu-and-libvirt.md) |

Licences: vagrant-parallels MIT ([vp-readme-github.md], 2026-11-07 folder); VirtualBox [virtualbox-licensing-faq.md]; vagrant-qemu and vagrant-libvirt MIT per their repositories (UNVERIFIED here: the
LICENSE files were not captured); QEMU GPLv2 (UNVERIFIED here).

```text
                    ┌────────────── Vagrant 2.4.9 (one CLI, one Vagrantfile) ──────────────┐
                    │                   │                     │                          │
             vagrant-parallels     built-in virtualbox    vagrant-qemu              vagrant-libvirt
                    │                   │                     │                          │ qemu+ssh://
             prlctl / prlsrvctl      VBoxManage          qemu-system-aarch64         virsh / libvirtd
                    │                   │                 (hvf, no daemon)               │
             Parallels Desktop       VirtualBox 7.2           │                     Linux host: KVM
             ── on this Mac ─────────────────────────────────┘                     ── elsewhere ──
```

## Pick a provider

```text
 Need an x86_64 guest that runs at normal speed?
   └─ yes ─► not on this Mac: Proxmox (skill-proxmox) or vagrant-libvirt on a Linux KVM host
   └─ no (arm64 guest)
        ├─ need prlctl exec / console capture / linked clones, and a Parallels licence exists ─► parallels (default here)
        ├─ need a free GUI hypervisor, internal networks, or a box only built for VirtualBox ─► virtualbox
        ├─ need no hypervisor licence or daemon, a raw qcow2/libvirt box, or serial-console work ─► qemu
        └─ the VM must run on a Linux server, not the Mac ─► libvirt (remote URI)
```

x86_64 guests under emulation exist on all three local hypervisors but are slow and limited: Parallels supports only Windows installs and warns that Linux guests may lack Tools
([parallels-27-x86-emulation-create-vm.md]); vagrant-qemu runs a non-host architecture with TCG and `cpu = "max"` ([vq-readme-github.md], example 7 and "Compatible with"); VirtualBox on an Arm host
virtualizes Arm guests ([virtualbox-changelog-7.1.md], 7.1.0 "macOS/Arm host: Arm virtualization for Linux and BSD VMs").

## How Vagrant chooses

Vagrant picks the provider in this order (VERIFIED_PRIMARY, [vagrant-providers-basic_usage.md]):

1. `vagrant up --provider=<name>`; afterwards Vagrant remembers the provider of a created machine, so `halt`, `destroy` and the rest need no flag.
2. `VAGRANT_DEFAULT_PROVIDER` ([vagrant-providers-default.md]; without it the documented default is VirtualBox).
3. The `config.vm.provider` blocks in the Vagrantfile, in order: the first one that is usable on this host.
4. Installed provider plugins by their own priority (a better-known system outranks a worse one).

With four providers installed, rules 3 and 4 make a bare `vagrant up` depend on the file and the installed plugins. A lab names its provider: either `--provider` in its driver, or a single
`config.vm.provider` block, or an empty `config.vm.provider "<first choice>"` line at the top to fix the order ([vagrant-providers-basic_usage.md]). `vagrant global-status` shows each machine's
provider; one Vagrant directory cannot hold the same machine under two providers at once.

## One Vagrantfile, several providers

A box is published per provider and architecture: the same name and version can carry `parallels` and `virtualbox` builds (`bento/ubuntu-24.04` 202510.26.0 is installed here for both, arm64; observed
2026-11-09 `vagrant box list`). Provider blocks hold only provider settings, and a provider override can change the box:

```ruby
Vagrant.configure("2") do |config|
  config.vm.box = "bento/ubuntu-24.04"
  config.vm.box_version = "202510.26.0"
  config.vm.provider "parallels" do |p|        # first block: preferred when usable
    p.name = "lab-a"; p.memory = 4096; p.cpus = 4
  end
  config.vm.provider "virtualbox" do |vb, override|
    vb.name = "lab-a"; vb.memory = 4096; vb.cpus = 4
  end
  config.vm.provider "qemu" do |qe, override|
    override.vm.box = "<a libvirt-format arm64 box>"   # vagrant-qemu imports libvirt boxes
    qe.memory = "4G"; qe.smp = "4"
  end
end
```

`vagrantfile_lint.py --provider <name>` checks the block for the provider the lab runs. Network declarations that only one provider understands (`virtualbox__intnet`, `libvirt__*`, a Parallels
`customize` with `prlctl` arguments) go inside that provider's block or are guarded, or the other providers ignore them or fail.

## The same task on each provider

| Task                      | Parallels                              | VirtualBox                                              | QEMU (vagrant-qemu)                                     | libvirt (remote)                         |
| ------------------------- | -------------------------------------- | ------------------------------------------------------- | ------------------------------------------------------- | ---------------------------------------- |
| List VMs | `prlctl list -a -i -j` | `VBoxManage list vms`; `showvminfo <vm> --machinereadable` | `vagrant status`; | `virsh -c <uri> list --all` |
|   (read-only) |  |  |   `.vagrant/machines/<m>/qemu/id` |  |
| Command | `prlctl exec <vm> "<cmd>"` (Tools) | `VBoxManage guestcontrol <vm> run --username <u> --exe <path>` | serial console: | `virsh -c <uri> console <domain>` |
|   without |  |   (Guest Additions) |   `vagrant serial-config <m>`, |  |
|   network |  |  |   then `nc -U <socket>` (0.7.0) |  |
| Console | `prlctl capture <vm> --file x.png` | `VBoxManage controlvm <vm> screenshotpng x.png` | none; read the serial console | `virsh -c <uri> screenshot <domain> x.ppm` |
|   picture |  |  |  |  |
| Graceful stop | `prlctl stop <vm>` | `VBoxManage controlvm <vm> acpipowerbutton` | `vagrant halt <m>` | `virsh -c <uri> shutdown <domain>` |
| Hard reset | `prlctl reset <vm>` | `VBoxManage controlvm <vm> reset` | `vagrant halt -f` then `up` | `virsh -c <uri> reset <domain>` |
| Snapshot | `vagrant snapshot` | `vagrant snapshot` or `VBoxManage snapshot <vm> take` | not listed as a | `vagrant snapshot`; `snapshot_pool_name` |
|  |   or `prlctl snapshot` |  |   feature ([vq-readme-github.md]) |   sets |
|  |  |  |  |   where ([vl-configuration-github.md]) |

Sources: Parallels rows [parallels-prlctl.md](parallels-prlctl.md); VirtualBox rows from the 7.2.10 help (captured before the 7.2.22 upgrade the same day) ([virtualbox-7.2.10-vboxmanage-help.txt]); QEMU rows [vq-readme-github.md] ("Basic operation: up, ssh, halt,
destroy, package"; Debug section); libvirt rows are standard `virsh` subcommands, UNVERIFIED here (no virsh manual captured). Every one of them gets a `timeout` like the Parallels commands
([lab-safety-and-guards.md](lab-safety-and-guards.md#a-deadline-on-every-call)).

## What changes per provider

| Concern               | Parallels                             | VirtualBox                                             | QEMU (vagrant-qemu)                        | libvirt                        |
| --------------------- | ------------------------------------- | ------------------------------------------------------ | ------------------------------------------ | ------------------------------ |
| Default first adapter | Shared (NAT + DHCP)                   | NAT                                                    | user-mode NAT, SSH forwarded to            | the management network on      |
|                       |                                       |                                                        |   `ssh_port` (50022)                       |   the host                     |
| `private_network`     | host-only `vagrant-vnetN`             | host-only *network* on macOS, allowed range only       | only with `advanced_network = true`        | libvirt network on the         |
|                       |                                       |                                                        |   (vmnet, socket)                          |   Linux host                   |
| Synced folder default | Parallels Shared Folders (Tools)      | `vboxsf` (Guest Additions)                             | SMB, rsync; VirtioFS experimental on       | NFS or rsync (UNVERIFIED here) |
|                       |                                       |                                                        |   macOS (0.7.0)                            |                                |
| Linked clones         | default since vagrant-parallels 2.0.0 | `vb.linked_clone = true` (off: a full import by        | qcow2 overlay on the box                   | backing image on the           |
|                       |                                       |   default, [vagrant-vbox-configuration.md])            |   image (UNVERIFIED)                       |   host (UNVERIFIED)            |
| Guest agent needed    | Parallels Tools                       | Guest Additions                                        | none (cloud-init for                       | none                           |
|                       |                                       |                                                        |   `advanced_network` addresses)            |                                |
| Disk size             | `prlctl set --device-set hdd0 --size` | `config.vm.disk ... primary: true`                     | `config.vm.disk ... primary: true`         | domain option                  |
|                       |                                       |   ([vagrant-disks-usage.md], 2026-11-07 folder)        |   grows (0.7.0)                            |   `machine_virtual_size`       |
|                       |                                       |                                                        |                                            |   in GB ([vl-configuration-github.md]) |

Most of this pack's other references were written for Parallels; their rules (pin the box, name the machine, deadline every call, refuse the wrong VM, keep the Vagrantfile copy) hold on every
provider. The machine-id rule holds too: a cloned disk carries its `/etc/machine-id` whatever the hypervisor ([clones-snapshots-and-identity.md](clones-snapshots-and-identity.md#machine-id)).
