---
Title: Tool choice and lab symmetry
Category: reference
Status: current
Authority: >-
  skill-vagrant canonical reference; claims carry evidence labels and cite captures in documents/
Scope: skill-vagrant: local Vagrant and Parallels labs on macOS Apple silicon
Last reviewed: 2026-11-09
Summary: Vagrant for local VMs and OpenTofu for Proxmox, the two OpenTofu providers that touch Vagrant or Parallels, and matching an arm64 lab to an x86 lab by package set and apt snapshot.
---

# Tool choice and lab symmetry

When to describe a lab VM with Vagrant and when with OpenTofu, and how an arm64 Vagrant lab and an x86 Proxmox lab are kept comparable. Captures named `[file]` are in
[documents/research-sources-20261107/](../documents/research-sources-20261107/readme.md).

## Contents

- [Vagrant for local VMs, OpenTofu for Proxmox](#vagrant-for-local-vms-opentofu-for-proxmox)
- [OpenTofu providers that touch Vagrant or Parallels](#opentofu-providers-that-touch-vagrant-or-parallels)
- [Lab symmetry with an x86 Proxmox lab](#lab-symmetry-with-an-x86-proxmox-lab)
- [Pin the archive, not only the box](#pin-the-archive-not-only-the-box)

## Vagrant for local VMs, OpenTofu for Proxmox

Operator guidance (USER_STATED, 2026-11-07): keep Vagrant for local VMs on the Mac and OpenTofu for Proxmox. The reasons hold on the evidence below:

- Vagrant describes a disposable, single-user lab on one host: boxes, provisioning, `vagrant ssh`, snapshots, all in one file the project copies.
- OpenTofu describes long-lived infrastructure with state, plans and drift detection; Proxmox has a maintained provider for it (`bpg/proxmox`; see skill-proxmox).
- Neither OpenTofu provider below replaces the Vagrantfile for this lab shape; each would add state and a second description of the same VM.

## OpenTofu providers that touch Vagrant or Parallels

The operator's statement (2026-11-07) was "no supported OpenTofu provider for Vagrant/Parallels; community bmatcuk/vagrant only wraps the CLI". The registry shows two providers (VERIFIED_PRIMARY,
OpenTofu registry search on 2026-11-07, [opentofu-search-vagrant.md], [opentofu-search-parallels.md]):

| Provider                      | Owner, licence, version       | What it manages                                                                                                                      |
| ----------------------------- | ----------------------------- | ------------------------------------------------------------------------------------------------------------------------------------ |
| `bmatcuk/vagrant`             | community, MIT, v4.1.0        | a `vagrant_vm` resource that points at a directory holding a Vagrantfile and brings it up; outputs machine names, SSH config, ports  |
|                               |                               |   ([tf-vagrant-provider-readme.md], [opentofu-registry-vagrant.md])                                                                  |
| `parallels/parallels-desktop` | Parallels, MIT,               | Parallels Desktop VMs "in a remote environment"; needs a licence key in the provider block (the page says "business edition          |
|                               |   v0.7.6 (2026-10-19)         |   license"; its schema says "Pro or Business license") ([opentofu-parallels-desktop.md], [tf-parallels-desktop-readme.md])           |

> **Disputed 2026-11-07** · OpenTofu registry, parallels/parallels-desktop v0.7.6 · VERIFIED_PRIMARY · Source: documents/research-sources-20261107/opentofu-parallels-desktop.md · Falsifier: the provider withdrawn from the registry, or Parallels stating it is not supported · Conflicts: operator statement 2026-11-07 "no supported OpenTofu provider for Vagrant/Parallels"
> A vendor-maintained OpenTofu provider for Parallels Desktop exists (0.x, MIT, maintained by Parallels and the community). For Vagrant itself only the community `bmatcuk/vagrant` exists, which drives
> a Vagrantfile. The recommendation stands (Vagrant for this lab) because the Parallels provider is pre-1.0, needs the licence key in configuration, and adds state for a disposable lab; how it reaches
> the Mac (its service and registration guides) is UNVERIFIED here.

## Lab symmetry with an x86 Proxmox lab

A project that tests one design on an arm64 Pi-like VM (Vagrant, Parallels, bento box) and on an x86 VM (Proxmox, cloud image) cannot make the base images identical: different architecture, different
image builder, different first-boot path (a bento box has a `vagrant` user and Parallels Tools; a cloud image has cloud-init). Matching the base images is the wrong target. Make the **package set**
the same instead:

1. Pin both base images (box version here; image file and its checksum on Proxmox).
2. Pin both labs' apt to one Ubuntu snapshot date, so every package installed or upgraded in provisioning comes from the same archive state.
3. Record the resulting kernel and key package versions per lab, and compare them as data (a `dpkg-query -W` list), not by eye.
4. Differences that remain (architecture, kernel flavour, guest tools) are listed as known differences in the project, with why they do not matter for the test or which test covers them.

## Pin the archive, not only the box

The Ubuntu snapshot service serves the archive as it was at a UTC time; the ID is `YYYYMMDDTHHMMSSZ`; snapshots exist for any time after 2023-03-01; on Ubuntu 24.04 `apt` detects snapshot support
itself, and `apt-get update --snapshot <id>` or a `Snapshot: <id>` line in a deb822 `.sources` stanza pins it (VERIFIED_PRIMARY, [ubuntu-snapshot-docs.md], [ubuntu-snapshot-service.md]). Canonical
intends to keep "at least 2 years" of snapshots (VERIFIED_PRIMARY, [ubuntu-snapshot-service.md]): a lab pinned longer than that needs its own mirror.

```bash
# provisioning, both labs, same ID (illustrative)
SNAP=20261101T000000Z
apt-get update --snapshot "$SNAP" && apt-get install -y --snapshot "$SNAP" <packages>
```

Whether the snapshot service covers `ports.ubuntu.com` (where arm64 packages come from) is UNVERIFIED: the captured documentation shows only `archive.ubuntu.com` and `security.ubuntu.com` examples.
Test it on the arm64 lab (`apt-get update --snapshot <id>` and read which URLs answer) before relying on it, and record the result here.

> **Learned 2026-11-07** · lab symmetry · VERIFIED_PRIMARY · Source: smc-resiliency spike/vm/lab/apt_snapshot_pin.sh, run on the arm64 Vagrant VM and the x86 Proxmox VM · Falsifier: `apt-get update` against `https://snapshot.ubuntu.com/ubuntu/<id>` failing for arm64 noble
> snapshot.ubuntu.com serves arm64 noble under the same `/ubuntu/<id>` path as amd64 (no ubuntu-ports path needed): pinning both lab VMs to `20261105T000000Z` and running `full-upgrade` gave both kernel 6.8.0-147 and the same package versions. This resolves the UNVERIFIED ports.ubuntu.com claim. On a box whose /etc is a merged confext (read-only overlay), unmerge first and merge after.
