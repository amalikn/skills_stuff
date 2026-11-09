---
Title: QEMU and libvirt
Category: reference
Status: current
Authority: >-
  skill-vagrant canonical reference; claims carry evidence labels and cite captures in documents/
Scope: skill-vagrant: the vagrant-qemu provider on macOS Apple silicon and the vagrant-libvirt provider against a Linux libvirt host
Last reviewed: 2026-11-09
Summary: >-
  vagrant-qemu on an Apple silicon Mac (defaults, boxes, networking modes and their root needs, synced folders, disks, serial console, the macOS 27
  port-check fix in 0.6.4) and vagrant-libvirt driven from the Mac against a remote Linux KVM host over qemu+ssh.
---

# QEMU and libvirt

Two providers run QEMU. **vagrant-qemu** starts `qemu-system-*` directly on the Mac, no daemon and no hypervisor licence. **vagrant-libvirt** asks a libvirt daemon to run QEMU/KVM, which in practice
means a Linux host. Observed on this Mac 2026-11-09: QEMU 11.1.3 (Homebrew), vagrant-qemu 0.7.0 (latest, 2026-10-15; updated from 0.6.3 that day), vagrant-libvirt 0.12.2 (latest, 2023-06-24). Captures named `[file]` are in
[documents/research-sources-20261109/](../documents/research-sources-20261109/readme.md).

## Contents

- [vagrant-qemu: what it is](#vagrant-qemu-what-it-is)
- [Versions that matter on this Mac](#versions-that-matter-on-this-mac)
- [Provider block and defaults](#provider-block-and-defaults)
- [Networking modes](#networking-modes)
- [Synced folders, disks and boxes](#synced-folders-disks-and-boxes)
- [Serial console instead of exec](#serial-console-instead-of-exec)
- [vagrant-libvirt against a Linux host](#vagrant-libvirt-against-a-linux-host)

## vagrant-qemu: what it is

The plugin imports a libvirt-format box or a bare qcow2 image, starts QEMU without a GUI and drives it through `up`, `ssh`, `halt`, `destroy` and `package`; provisioners, forwarded ports, cloud-init
and `config.vm.disk` work; synced folders work through SMB, rsync or VirtioFS (VERIFIED_PRIMARY, [vq-readme-github.md], Features). Snapshots are not in its feature list, so `vagrant snapshot` is not a
rollback on this provider (UNVERIFIED: not tested). It was "test[ed] with Apple Silicon / M1 and CentOS / Ubuntu aarch64 image" ([vq-readme-github.md]).

```text
 vagrant up --provider=qemu
   └─ vagrant-qemu: qemu-img creates the machine disk from the box's qcow2 image
        └─ qemu-system-aarch64 -machine virt,accel=hvf -cpu host ...   (daemonised, pidfile)
             ├─ user-mode NAT: host 127.0.0.1:<ssh_port 50022> ─► guest :22   ← vagrant ssh
             ├─ serial  ─► ~/.vagrant.d/tmp/vagrant-qemu/<id>/qemu_socket_serial
             └─ optional second NIC (advanced_network): vmnet / socket_vmnet / socket
```

## Versions that matter on this Mac

| Version            | Change                                                                                                                     | Matters because                                    |
| ------------------ | -------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------- |
| 0.6.4 (2026-10-09) | Fixes `vagrant up` failing with `ForwardPortCollision` ("The forwarded port to 50022 is already in use") **on macOS 27** even | this Mac runs macOS 27 (Darwin 27.2); it had 0.6.3 until 2026-11-09 |
|                    |   when nothing listens: a non-blocking connect to a closed local port reports success on the retry there                   |                                                    |
| 0.6.4              | Quotes MACs in the generated cloud-init `network-config`; about 1.3% of generated MACs were read as base-60 integers       | an `advanced_network` VM could boot unreachable    |
| 0.7.0 (2026-10-15) | VirtioFS synced folders (`type: "qemu_virtiofs"`, experimental on macOS); `vagrant serial-config`; packaging a machine as  | serial console and folders without SMB             |
|                    |   a box                                                                                                                    |                                                    |
| 0.7.0              | `config.vm.disk :disk, primary: true, size:` grows the boot disk instead of attaching a blank one; never shrinks           | an older Vagrantfile's extra blank disk is dropped |
| 0.7.0              | `vagrant halt` bounded; on macOS 27 a `control_port` connect to localhost could pick `::1`, so halt never reached QEMU     | halts that took both timeouts                      |
| 0.7.0              | A boot that passes `config.vm.boot_timeout` (300 s) now fails instead of finishing in the background                       | slow emulated boots need `boot_timeout = 600`      |

All VERIFIED_PRIMARY from [vq-changelog-github.md]. Upgrade with `vagrant plugin update vagrant-qemu` (a host change; read the 0.7.0 behaviour changes first). The macOS 27 port-check bug was not
reproduced on this Mac (UNVERIFIED here; the falsifier is a `vagrant up --provider=qemu` with 0.6.3 that succeeds; the Mac has 0.7.0 since 2026-11-09).

## Provider block and defaults

```ruby
config.vm.provider "qemu" do |qe|
  qe.memory = "4G"            # default 4G
  qe.smp = "4"                # default 2
  # qe.arch / qe.machine / qe.cpu: auto from the host; on Apple silicon "aarch64", "virt,highmem=on,accel=hvf", "host"
  # qe.ssh_port = 50022        # default; ssh_auto_correct = true for several machines
  # qe.qemu_dir = "/opt/homebrew/share/qemu"   # firmware (edk2-aarch64-code.fd); default from HOMEBREW_PREFIX
end
```

Defaults are those of the 0.7.0 README ([vq-readme-github.md], Options). A non-host architecture switches to TCG emulation: the README's x86_64 example sets `arch = "x86_64"`, `machine = "q35"`, `cpu
= "max"` and `net_device = "virtio-net-pci"`; AlmaLinux 9 x86_64 needs `cpu = "max"` ([vq-changelog-github.md], 0.7.0). Several machines in one file need distinct `ssh_port` values or
`ssh_auto_correct`.

## Networking modes

Without `advanced_network = true` there is one user-mode NIC and a `private_network` line is ignored with a warning. With it, a second NIC (VERIFIED_PRIMARY, [vq-readme-github.md], Platform support):

| macOS `net_mode`                       | Host ↔ VM | VM ↔ VM     | Root              | Needs                                |
| -------------------------------------- | --------- | ----------- | ----------------- | ------------------------------------ |
| `:vmnet_shared` / `_host` / `_bridged` | yes       | yes         | `sudo vagrant up` | nothing (QEMU 7.0+)                  |
| `:socket_vmnet`                        | yes       | yes         | no                | the `socket_vmnet` daemon (Homebrew) |
| `:socket` (`listen=` / `connect=`)     | no        | exactly two | no                | `vagrant up --no-parallel`           |

- Running under `sudo` makes QEMU's files and any box downloaded then root-owned; add boxes as yourself first, or use `:socket_vmnet`.
- `socket` multicast (`mcast=`) does not work on macOS (`EADDRNOTAVAIL`); `listen`/`connect` is point-to-point, one pair only.
- The static address of a `private_network` reaches the guest through cloud-init: a box without cloud-init silently keeps no address.

For a lab wire between two VMs on the Mac, `:socket_vmnet` is the one mode with no root and more than two VMs.

## Synced folders, disks and boxes

- Synced folders: SMB (macOS file sharing), rsync, or VirtioFS. On macOS VirtioFS "is experimental and needs a QEMU built with vhost-user and a macOS `virtiofsd` port" from a community tap
  ([vq-changelog-github.md], 0.7.0). A lab disables `/vagrant` and uses `vagrant upload` unless it needs a share.
- Disk: from 0.7.0, `config.vm.disk :disk, primary: true, size: "100GB"` grows the virtual disk; growing the partition and filesystem in the guest is still the guest's job ([vq-readme-github.md],
  Features).
- Boxes: libvirt-format boxes (a `box.img` qcow2) import directly; a Parallels or VMware box needs the plugin wiki's conversion; libvirt box v2 is experimental ([vq-readme-github.md]). A box's
  architecture must match `qe.arch`.

## Serial console instead of exec

vagrant-qemu has no guest agent channel like `prlctl exec`. The out-of-band path is the serial console: `vagrant serial-config [<m>] [--json]` (0.7.0) prints its Unix socket or TCP port, and `nc -U
<socket>` connects; `echo 03 | xxd -r -p | nc -U <socket>` sends Ctrl-C (VERIFIED_PRIMARY, [vq-readme-github.md], Debug). The guest must run a getty on its serial console. Give `nc` a deadline
(`timeout 30`) like any other call.

## vagrant-libvirt against a Linux host

vagrant-libvirt manages "QEMU or KVM type virtual machines" through libvirtd; its install guide expects QEMU and libvirt from the Linux distribution, Vagrant from the distribution packages, and names
Vagrant 2.0 to 2.2 as tested ([vl-installation-github.md], VERIFIED_PRIMARY). From a Mac it is used remotely: the connection options build a libvirt URI, `connect_via_ssh` "is absolutely needed to
access Libvirt on remote host" or Vagrant cannot learn the VM's address, and `uri` overrides them all ([vl-configuration-github.md], Connection Options).

```ruby
# vagrant_stuff/mikrotik-qemu01/Vagrantfile (untracked working copy, read 2026-11-09; user and host redacted)
config.vm.box = "ktogias/mikrotik"
config.vm.box_version = "7.13"
config.vm.provider :libvirt do |libvirt|
  libvirt.uri = "qemu+ssh://<user>@<linux-host>/system"
  libvirt.cpus = 2
  libvirt.memory = 2048
  libvirt.nested = true
end
config.vm.network "public_network", bridge: "br0", dev: "br0"   # a bridge on the Linux host
```

- `public_network` uses macvtap on the Linux host (kernel 2.6.24 or later) ([vl-configuration-github.md]).
- The disk size is `machine_virtual_size` in GB; snapshots land in `snapshot_pool_name` when set ([vl-configuration-github.md]).
- The plugin's last release is 0.12.2 (2023-06-24) and the installed Vagrant 2.4.9 is newer than its tested range: treat a plugin load failure after a Vagrant upgrade as expected and check `vagrant
  plugin list` first (UNVERIFIED that 0.12.2 loads on 2.4.9 for every command; it is installed here).
- A libvirt VM lives on the Linux host, so the Mac-side guards (disk space, VM name) must test that host, and its writes follow [lab-safety-and-guards.md](lab-safety-and-guards.md). A Proxmox node is not a libvirt target for
  this plugin; Proxmox work is skill-proxmox.
