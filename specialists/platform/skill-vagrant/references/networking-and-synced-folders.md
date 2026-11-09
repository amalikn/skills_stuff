---
Title: Networking and synced folders
Category: reference
Status: current
Authority: >-
  skill-vagrant canonical reference; claims carry evidence labels and cite captures in documents/
Scope: skill-vagrant: local Vagrant and Parallels labs on macOS Apple silicon
Last reviewed: 2026-11-09
Summary: How Vagrant networks map to Parallels Shared, Host-Only and Bridged; a second adapter the lab owns; one DHCP lease for two VMs (machine-id DUID); synced folder failures by version.
---

# Networking and synced folders

How Vagrant network declarations map to Parallels networks, how a lab adds a second adapter it controls, why two VMs can receive one DHCP address, and how host folders reach the guest. Captures named
`[file]` are in [documents/research-sources-20261107/](../documents/research-sources-20261107/readme.md).

## Contents

- [Adapter 0: Parallels Shared networking](#adapter-0-parallels-shared-networking)
- [Mapping Vagrant networks to Parallels](#mapping-vagrant-networks-to-parallels)
- [A second adapter the lab controls](#a-second-adapter-the-lab-controls)
- [Same DHCP address on two VMs](#same-dhcp-address-on-two-vms)
- [Unplugging an adapter](#unplugging-an-adapter)
- [Synced folders](#synced-folders)
- [Addresses in reusable text](#addresses-in-reusable-text)

## Adapter 0: Parallels Shared networking

The Parallels provider configures the VM's first adapter as Shared networking (NAT with Parallels' DHCP server) and reaches the VM through the address it leases there; nothing in the Vagrantfile is
needed for that (VERIFIED_PRIMARY, [vp-networking.md]). In the guest it is `eth0` (bento Ubuntu). Leave it alone: it is Vagrant's SSH path. If a test cuts it anyway, `prlctl exec` still reaches the
guest through Parallels Tools (worked example header, `vagrant_stuff/smc-pi-spike01/Vagrantfile` @ 8591b72: "If a spike test cuts eth0 anyway, `prlctl exec smc-pi-spike01 <cmd>` still reaches the VM
(verified 2026-10-20)").

```text
 Mac host
 ├─ Parallels "Shared" network (NAT + Parallels DHCP)       ← Vagrant's SSH path; leave it alone
 │     eth0 ── VM lab-a                eth0 ── VM lab-b
 ├─ Host-Only "vagrant-vnetN" (one per private subnet)      ← the lab's own wire (auto_config: false)
 │     eth1 ── VM lab-a                eth1 ── VM lab-b
 ├─ Bridged to en0 (public_network)                         ← reaches the real LAN; avoid in a lab
 └─ Parallels Tools channel (no guest network at all)       ← prlctl exec, graceful stop, shared folders
```

## Mapping Vagrant networks to Parallels

| Vagrantfile                                                    | Parallels network                          | Source                                                                           |
| -------------------------------------------------------------- | ------------------------------------------ | -------------------------------------------------------------------------------- |
| (default)                                                      | Shared (adapter 0)                         | [vp-networking.md]                                                               |
| `vm.network "private_network", ip: "<addr>"` or `type: "dhcp"` | Host-Only; Vagrant creates `vagrant-vnetN` | [vp-private-network.md]; `vagrant-vnetN` observed in `prlctl list -i` 2026-11-07 |
| `vm.network "public_network"` (`bridge: "en0"`)                | Bridged to a host interface                | [vp-public-network.md]                                                           |
| `vm.network "forwarded_port", guest:, host:`                   | port forward on the Shared network         | [vagrant-forwarded-ports.md]                                                     |

All VERIFIED_PRIMARY where a capture is named. Each `private_network` with a distinct subnet becomes its own host-only network; networks append across Vagrantfile levels rather than override
([vagrant-vagrantfile.md]). A static address must not collide with anything else on that network; use reserved private space and, in reusable text, documentation ranges.

Known limits: more than four networks on one VM failed on an M1 Mac (vagrant-parallels issue 410, open, [vp-issue-410.md]; UNVERIFIED whether it holds on Parallels 26); on Fedora 36 and later a static
private address lands on a new interface rather than the intended one (issue 462, [vp-issue-462.md]).

## A second adapter the lab controls

When the lab itself must own an interface (a site trunk with VLANs, an address the image under test configures), declare it with `auto_config: false`: Vagrant creates the adapter but does not
configure it in the guest (VERIFIED_PRIMARY, [vagrant-private-network.md]; after changing `auto_config` on an existing machine, the old configuration may persist until the guest's network files are
cleaned and the VM reloaded). Two machines on the same private subnet share one host-only network, so a client VM can sit on the same "wire":

```ruby
# vagrant_stuff/smc-pi-spike01/Vagrantfile @ 8591b72 (addresses redacted)
smc.vm.network "private_network", ip: "<lab-a>", auto_config: false      # eth1: the site trunk, configured by the site config image
client.vm.network "private_network", ip: "<lab-b>", auto_config: false   # eth1: same private network as the spike's eth1
```

## Same DHCP address on two VMs

Ubuntu's systemd-networkd identifies itself to DHCP with a DUID; the default `DUIDType=vendor` hashes `/etc/machine-id` (VERIFIED_PRIMARY, [networkd-conf-man.md]; `ClientIdentifier=` defaults to
`duid`, [systemd-network-man.md]). Two VMs with the same machine-id therefore look like one client and Parallels' DHCP gives them the same address, whatever their MACs. Seen with bento boxes that
shipped a fixed machine-id (vagrant-parallels issue 441 on an M2 with Parallels 18.2, bento issues 1421, 1473 and 1562; VERIFIED_PRIMARY, [vp-issue-441.md], [vp-issue-1562.md]) and with a `prlctl
clone --linked` of a running lab VM (smc-resiliency 2026-11-06: "the SM clone of the spike VM kept its machine-id, so DHCP gave it the spike VM's address and `vagrant ssh smc-pi-spike01` reached the
clone"; USER_STATED, project record). Effects: `vagrant ssh` reaches the wrong VM, or connections flap between two VMs. Checks and fixes are in [clones-snapshots-and-identity.md](clones-snapshots-and-identity.md#machine-id).

```text
 /etc/machine-id  (identical in the source and its clone)
   └─► systemd-networkd DUID      DUIDType=vendor hashes the machine-id
         └─► DHCP client id       ClientIdentifier=duid (default), not the MAC
               └─► Parallels DHCP sees ONE client → ONE lease → both VMs get the same address
                     └─► `vagrant ssh <source>` can land on the clone
```

## Unplugging an adapter

`prlctl set <vm> --device-set net1 --disconnect` unplugs an adapter, also on a running VM; `--device-set <net> --mac auto` gives it a new MAC (VERIFIED_PRIMARY, CLI reference p.34). A clone that must
never meet the original's addresses gets no shared network at all (the smc-resiliency rule since 2026-11-06: "a linked clone gets no shared network (it shares the machine-id)"); a new MAC alone does
not change the DHCP identity.

## Synced folders

- By default the project folder is shared at `/vagrant`; `disabled: true` on a `synced_folder` turns it off; `type` selects the implementation (VERIFIED_PRIMARY, [vagrant-synced-folders.md]). Under
  Parallels the default type is Parallels Shared Folders, which need the `prl_fs` module or the `prl_fsd` FUSE daemon from Parallels Tools in the guest.
- Parallels Desktop 20.2 moved Linux shared folders to `prl_fsd`; vagrant-parallels before 2.4.4 failed with "prl_fs filesystem not found" (issue 483); 2.4.4 added "a check for prl_fsd and use that to
  mount if it exists" (VERIFIED_PRIMARY, [vp-issue-483.md], [vp-changelog-github.md]).
- Ubuntu 26.04 guests: AppArmor blocks `prl_fsd`/`fusermount3` by default (issue 522, open 2026-06; VERIFIED_PRIMARY that it is reported, [vp-issue-522.md]). Ubuntu 24.04 labs are not affected by that
  report.
- `type: "rsync"` is a one-time, one-way copy from host to guest at `up`/`reload` (`vagrant rsync`, `vagrant rsync-auto` to repeat) and needs no guest tools (VERIFIED_PRIMARY,
  [vagrant-synced-rsync.md]). A lab that tests a read-only or minimal image disables `/vagrant` and pushes files with `vagrant upload` or `prlctl exec` instead, so the image is tested without host
  mounts.
- `vagrant upload` of a directory into a folder that already exists can leave stale files; upload to a new path per run and move it into place (smc-resiliency `spike/to_vm.sh` @ 4e436e8d: "a new
  folder per run: vagrant upload of this folder delivered stale files (2026-11-06)"; USER_STATED).

> **Learned 2026-11-09** · vagrant-parallels 2.4.9 and 2.4.10, Ubuntu 24.04 and later guests · VERIFIED_PRIMARY (the report and the fix; reach UNVERIFIED) · Source: documents/research-sources-20261109/vp-issue-526.md, vp-pr-525.md, vp-pr-523.md; documents/research-sources-20261107/vp-releases-github.md (v2.4.10), vp-issue-527.md · Falsifier: `findmnt /vagrant` on the lab's bento 24.04 guest under 2.4.9 showing a `prl_fsd` FUSE mount that works
> vagrant-parallels up to 2.4.9 passes the FUSE option `big_writes` to `prl_fsd`. libfuse3 removed that option, so the issue reports that on guests that ship fusermount3 ("Ubuntu 24.04+") the mount
> fails with ``fuse: unknown option(s): `-o big_writes'`` and `vagrant up`/`reload` stop at the shared-folder step (issue 526). PR 525 passes it on libfuse2 guests only; it shipped in 2.4.10 on
> 2026-10-28 (issue 527). Whether every 24.04 guest is hit is UNVERIFIED: the worked example keeps the default `/vagrant` (its Vagrantfile has no `synced_folder` line, `vagrant_stuff` @ 8591b72) on
> bento/ubuntu-24.04 with 2.4.9 and comes up, so the mount path may depend on whether Parallels Tools use `prl_fsd` or the `prl_fs` module. If `up` stops with that message, update the plugin to 2.4.10
> (`vagrant plugin update vagrant-parallels`) or disable the folder. PR 523 (merged 2026-06-12) adds an AppArmor override for FUSE 3 mounts for the Ubuntu 26.04 case (issue 522); which release first
> carries it is UNVERIFIED, because the vendor says its GitHub release notes are "mostly not used" (issue 527).

> **Learned 2026-11-09 (b)** · vagrant-parallels 2.4.10, Ubuntu 24.04 arm64 · VERIFIED_PRIMARY (lab run) · Source: skill-vagrant scratch lab (skills-runtime/skill-vagrant/scratch-lab, bento/ubuntu-24.04 202510.26.0, Parallels 27, vagrant-parallels 2.4.10), 2026-11-09; read-only `prlctl exec smc-pi-spike01 findmnt` the same day · Falsifier: `findmnt /vagrant` on a 2.4.10 machine from this box showing no mount after a clean `vagrant up`
> With vagrant-parallels 2.4.10 the default `/vagrant` mounts as `fuse.prl_fsd` on a bento 24.04 guest (and `/media/psf/vagrant` beside it). The
> long-running spike VM, brought up under 2.4.9 on the same box, has fuse3 3.14 and `prl_fsd` installed, no `prl_fs` module, and **no** `/vagrant`
> mount: consistent with issue 526 hitting the `prl_fsd` path on 24.04. Reload such a machine after the plugin update if it needs the share.

## Addresses in reusable text

Parallels' Shared and Host-Only networks use private ranges chosen by Parallels Desktop (`prlsrvctl net list` shows them); this pack's contract test forbids private addresses in authored files, so
read them from the host rather than from here. Project files keep their lab addresses.
