---
Title: Upgrade and troubleshooting
Category: reference
Status: current
Authority: canonical
Scope: skill-proxmox references/upgrade-and-troubleshooting.md
Last reviewed: 2026-11-19
Summary: Package repositories, minor updates, the 8-to-9 upgrade, what changed in 9.0 to 9.2 (including arm64), known issues, and triage.
---

# Upgrade and troubleshooting

Package repositories, minor updates, the 8-to-9 major upgrade, what changed in 9.0, 9.1 and 9.2, known issues, and triage. Sources: [Package
Repositories](../documents/research-sources-20261107/pve-wiki-package-repositories.md), [System Software Updates](../documents/research-sources-20261107/pve-wiki-system-software-updates.md),
[Upgrade from 8 to 9](../documents/research-sources-20261107/pve-wiki-upgrade-from-8-to-9.md),
[Roadmap](../documents/research-sources-20261107/pve-wiki-roadmap.html), [sysadmin chapter](../documents/research-sources-20261107/pve-admin-chapter-sysadmin.html), Proxmox bugzilla searches
([OVMF](../documents/research-sources-20261107/pve-bugzilla-ovmf.csv), [SDN DHCP](../documents/research-sources-20261107/pve-bugzilla-sdn-dhcp.csv),
[cloud-init](../documents/research-sources-20261107/pve-bugzilla-cloudinit.csv)).

## Contents

- [Repositories](#repositories)
- [Minor updates](#minor-updates)
- [Major upgrade 8 to 9](#major-upgrade-8-to-9)
- [What changed in 9.x](#what-changed-in-9x)
- [Known issues worth checking](#known-issues-worth-checking)
- [Triage](#triage)

## Repositories

- **pve-enterprise** (default, needs a subscription key), **pve-no-subscription** ("can be used for testing and non-production use. It's not recommended to use this on production servers"),
  **pve-test** (renamed from `pvetest` in 9.0). The base Debian repositories are always needed as well. `VERIFIED_PRIMARY` (Package Repositories; Roadmap 9.0).
- Trixie uses the deb822 format (`/etc/apt/sources.list.d/*.sources`); apt complains about the legacy one-line `.list` format, and `apt modernize-sources` migrates most entries. Disable a repository
  with `Enabled: no` in its stanza. `VERIFIED_PRIMARY`.
- Without a subscription, disable `pve-enterprise.sources` with `Enabled: no` (this "will prevent error messages if your host does not
  have a subscription key") and enable no-subscription; for Ceph the same pairing exists (`ceph-squid` enterprise and
  no-subscription). `VERIFIED_PRIMARY` (Package Repositories).
- Read the configuration with `pvesh get /nodes/<node>/apt/repositories`: each file's format and each entry's `Enabled`.

## Minor updates

```text
  GET  /nodes/<node>/apt/update   read the cached list (daily pveupdate refreshes it)     read
  POST /nodes/<node>/apt/update   refresh the list = apt update                           write
     |
     +-- minor (9.1 -> 9.2): read known issues -> one node: apt full-upgrade -> check guests
     |                       -> reboot for a new kernel -> the other nodes      (never apt upgrade)
     |
     +-- major (8 -> 9):     latest 8.4 -> pve8to9 --full, fix FAILs -> repos bookworm -> trixie
                             -> apt dist-upgrade -> pve8to9 again -> reboot     (Ceph on Squid first)
```

- "To install updates use the web-based GUI or `apt update` then `apt full-upgrade`". **Never `apt upgrade`**: Proxmox VE is a rolling release on Debian and `apt upgrade` "may result in a partially
  upgraded or broken package state", because only `full-upgrade` may remove packages to satisfy dependencies. `VERIFIED_PRIMARY` (System Software Updates).
- PVE checks for updates daily (`pve-daily-update.timer` runs `pveupdate`) and notifies root@pam; the cached list is readable with `GET /nodes/<node>/apt/update` without refreshing it.
  `VERIFIED_PRIMARY` (sysadmin chapter) for the daily check; the timer and unit observed on 9.1.5.
- A point release such as 9.1 to 9.2 arrives as ordinary updates on the same repository: `proxmox-ve`, `pve-manager`, `qemu-server`, `pve-qemu-kvm`, `pve-edk2-firmware*` and a new kernel series. Plan
  it like an upgrade: read the release's known issues first, upgrade one node, check guests, then the rest. A new QEMU or OVMF takes effect for a VM only after it is stopped and started (or migrated);
  a new kernel needs a host reboot, which stops or migrates every guest. `VERIFIED_SECONDARY` (general QEMU/KVM behaviour; not in a captured page).

## Major upgrade 8 to 9

1. All nodes on the latest 8.4 (`pve-manager` at least 8.4.1). `VERIFIED_PRIMARY`.
2. Run `pve8to9` (and `pve8to9 --full`) before, during and after; fix every FAIL and review every WARN. `VERIFIED_PRIMARY`.
3. Hyper-converged Ceph must already run Ceph 19.2 Squid. `VERIFIED_PRIMARY`.
4. Move every Debian and Proxmox repository entry from bookworm to trixie, then `apt update` and `apt dist-upgrade` (the guide's form; same as `full-upgrade`), then re-run `pve8to9` and reboot.
   `VERIFIED_PRIMARY`.
5. Test on a spare node first (an 8.4 install upgraded with a copy of the production configuration). `VERIFIED_PRIMARY`.

## What changed in 9.x

| Release | Date       | Base             | Highlights and breaking changes                                                                                                                            |
| ------- | ---------- | ---------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 9.0     | 2025-08-05 | Debian 13,       | HA groups become node/resource affinity rules; SDN fabrics (OpenFabric, OSPF); LVM snapshots as volume chains (preview). Breaking: `VM.Monitor` removed    |
|         |            |   kernel 6.14,   |   (use `Sys.Audit` and the `VM.GuestAgent.*` privileges); new `VM.Replicate`; creating a privileged container needs `Sys.Modify`; virtio vNIC MTU now      |
|         |            |   QEMU 10.0      |   inherits the bridge MTU; `maxfiles` removed; GlusterFS dropped; cgroup v1 gone; repository `pvetest` renamed `pve-test`; NIC names may change (pin them  |
|         |            |                  |   with `pve-network-interface-pinning` first)                                                                                                              |
| 9.1     | 2025-11-19 | Debian 13.2,     | LXC from OCI images; TPM state in qcow2; nested-virtualisation vCPU flag; SDN status (guests per bridge and VNet). Known: some Dell PowerEdge fail on 6.17 |
|         |            |   kernel 6.17,   |   (pin 6.14); DRBD not on 6.17; AMD Zen 5 RDSEED on 6.17.9+ needs microcode or a different CPU type                                                        |
|         |            |   QEMU 10.1      |                                                                                                                                                            |
| 9.2     | 2026-05-21 | Debian 13.5,     | CRS dynamic load balancing; `disarm-ha` / `arm-ha`; SDN WireGuard and BGP fabrics, route maps; custom CPU models in the GUI; Ceph Tentacle option. Known:  |
|         |            |   kernel 7.0,    |   upgrade can stall if HA is disarmed mid-migration; Windows + host CPU + VBS freezes on Intel (fixed by machine version 11.0+pve2); installer kernel      |
|         |            |   QEMU 11.0      |   and `megaraid_sas`                                                                                                                                       |
| 9.2     | 2026-08-05 | arm64 build,     | First non-x86 release: NVIDIA Grace and Vera official, other UEFI+ACPI ARMv9-A best effort; no SeaBIOS, AMD SEV or GVT-g; live migration only within one       |
| (arm64) |            |   Debian 13.6    |   architecture; later releases cover both architectures ([architecture-and-cluster.md](architecture-and-cluster.md#arm64-hosts))                                  |

`VERIFIED_PRIMARY` (Roadmap release notes, captured 2026-11-07).

QEMU 11.0 is what 9.2 shipped with (Roadmap, "Proxmox VE 9.2 ... QEMU 11.0"); `pve-qemu-kvm` 11.1.x arrived later as an ordinary update, so Learned 2026-11-07 (k)'s "10.1 to 11.1"
is the pending package in November, not a conflict. `VERIFIED_PRIMARY` (https://pve.proxmox.com/wiki/Roadmap and
http://download.proxmox.com/debian/pve/dists/trixie/pve-no-subscription/binary-amd64/Packages.gz listing `pve-qemu-kvm` 11.0.0-1 to 11.1.3-2 and `pve-manager` 9.2.26, retrieved 2026-11-19).

## Known issues worth checking

Open Proxmox bugzilla entries found on 2026-11-07 (status as captured; check the live tracker before relying on one):

- OVMF/EFI: 7341 "EFI disk is lost in the .conf file during cloning or migrating" (more info needed); 3227 cannot move a running VM's EFI disk when its size does not match the target's granularity;
  4774 enrolling custom Secure Boot keys in the efidisk (undecided); 6519 migrating away from legacy (2m) EFI images.
- SDN DHCP and IPAM: 7022 SDN firewall dropping DHCP despite rules for UDP 67/68; 6021 IPAM keeps the old VMID after cloning a container; 6332 the DHCP offer carries no guest hostname; 6014 no custom
  DHCP options per zone, VNet or subnet.
- cloud-init: 4782 an `@` in the password breaks it; 5195 a storage lock failure while removing the cloud-init volume leaves the VM config broken; 3338 and 4251 hostname/FQDN not passed in some cases.

`VERIFIED_PRIMARY` that these reports exist with these titles and statuses on the capture date; whether each affects 9.1.5 is `UNVERIFIED`.

## Triage

- **Start with facts**: `pveversion -v`, `journalctl -b -u pveproxy -u pvedaemon -u pve-cluster -u corosync`, the task log of the failing action (`GET /nodes/<node>/tasks`, it names user and token),
  `qm config` or `pct config`.
- **`/etc/pve` read-only** or "cluster not ready - no quorum": a quorum problem, not a file permission one (`pvecm status`).
- **Permission check failed**: read the required privilege with `pvesh usage <path> --verbose`, then `pveum user permissions` for the user **and** for the token; a separated token without the user's
  grant has nothing. Some operations are root-only.
- **A guest gets no address**: on a VNet with IPAM, check the `ethers` binding and the lease file; on `vmbr0`, the LAN's DHCP may refuse unknown MACs ([networking-and-sdn.md](networking-and-sdn.md)).
- **SSH to a recreated lab VM fails**: a reused address leaves a stale `known_hosts` entry; an agent holding many keys gives "Too many authentication failures" (pass `-o IdentitiesOnly=yes -i <key>`).
- **`apt update` errors on enterprise.proxmox.com**: no subscription key; disable that stanza (`Enabled: no`). The exact HTTP status
  is `UNVERIFIED` here.

> **Learned 2026-11-07 (k)** · Proxmox VE 9.1.5 · VERIFIED_PRIMARY · Source: lab node read-only (`pvesh get /nodes/localhost/apt/update`, `/apt/versions`, `/apt/repositories`, `systemctl show
> pve-daily-update.service`) and the coordinating session's read of `apt list --upgradable` (2026-11-07) · Falsifier: the same node listing a different pending pve-manager after the next daily
> refresh with no new packages published
> A 9.1.5 node on pve-no-subscription had about 290 pending updates (289 by `apt list --upgradable`, 294 by the API): `pve-manager` 9.1.5 to 9.2.26, `pve-qemu-kvm` 10.1 to 11.1,
> `pve-edk2-firmware-ovmf` 4.2025.05 to 4.2026.08 and kernel 6.17.9 to 6.17.13; the enterprise stanza was present but disabled, and the no-subscription entry was in the legacy `.list` format. A node
> left on a point release for months carries the next release in its queue: read that release's known issues before `apt full-upgrade`.

> **Learned 2026-11-07** · upgrade · VERIFIED_PRIMARY · Source: smc-resiliency SCRATCHPAD 20261107_1617, lab node log `/root/upgrade-20261107.log` · Falsifier: a 9.1 to 9.2 `apt full-upgrade` that keeps the 6.17 kernel as default
> A 9.1.5 to 9.2.26 upgrade (289 packages) ran unattended with `DEBIAN_FRONTEND=noninteractive apt-get -y -o Dpkg::Options::=--force-confdef -o Dpkg::Options::=--force-confold full-upgrade` under `nohup`, exit 0, then a reboot brought the node up on kernel 7.0.14 (the 9.2 default kernel moved from 6.17 to 7.0), no failed units, SDN vnets and their dnsmasq back by themselves. Stop or shut down guests first. Before it, tidy the repositories: keep `pve-enterprise.sources` with `Enabled: false`, move `*.disabled` duplicates and an empty `ceph-no-subscription.list` to a backup folder, and write the no-subscription repo as deb822 `proxmox.sources`.

> **Learned 2026-11-25 (n)** · Proxmox VE 9.2.2 (fresh install, no subscription), bpg/proxmox 0.123.1 · VERIFIED_PRIMARY (node API
> `/nodes/<node>/apt/repositories` and apply output) · Source: home NAS project `tofu/host/main.tf` (commit 4606775) · Falsifier: a 9.2 install whose
> `ceph.sources` is not enabled, or a handle other than `ceph-squid-enterprise`
> The 9.2 installer enables two enterprise files: `pve-enterprise.sources` and `ceph.sources` (`ceph-squid` / `enterprise`), so a node without a
> subscription fails `apt update` on Ceph even when no Ceph is used. Turn both off as code with the standard-repository handles the API lists
> (`enterprise`, `ceph-squid-enterprise`; 9.2 also lists the `ceph-tentacle-*` handles) and enable `no-subscription`; a re-plan is then clean.
> ```hcl
> resource "proxmox_apt_standard_repository" "ceph_enterprise" { handle = "ceph-squid-enterprise"  node = var.node_name }
> resource "proxmox_apt_repository" "ceph_enterprise" {
>   enabled   = false
>   file_path = proxmox_apt_standard_repository.ceph_enterprise.file_path
>   index     = proxmox_apt_standard_repository.ceph_enterprise.index
>   node      = proxmox_apt_standard_repository.ceph_enterprise.node
> }
> ```
