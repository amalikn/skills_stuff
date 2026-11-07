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

## Addresses in reusable text

Parallels' Shared and Host-Only networks use private ranges chosen by Parallels Desktop (`prlsrvctl net list` shows them); this pack's contract test forbids private addresses in authored files, so
read them from the host rather than from here. Project files keep their lab addresses.
