This file is a merged representation of a subset of the codebase, containing specifically included files and files not matching ignore patterns, combined into a single document by Repomix.

# File Summary

## Purpose
This file contains a packed representation of a subset of the repository's contents that is considered the most important context.
It is designed to be easily consumable by AI systems for analysis, code review,
or other automated processes.

## File Format
The content is organized as follows:
1. This summary section
2. Repository information
3. Directory structure
4. Repository files (if enabled)
5. Multiple file entries, each consisting of:
  a. A header with the file path (## File: path/to/file)
  b. The full contents of the file in a code block

## Usage Guidelines
- This file should be treated as read-only. Any changes should be made to the
  original repository files, not this packed version.
- When processing this file, use the file path to distinguish
  between different files in the repository.
- Be aware that this file may contain sensitive information. Handle it with
  the same level of security as you would the original repository.

## Notes
- Some files may have been excluded based on .gitignore rules and Repomix's configuration
- Binary files are not included in this packed representation. Please refer to the Repository Structure section for a complete list of file paths, including binary files
- Only files matching these patterns are included: AGENTS.md, CLAUDE.md, AI_NAVIGATION.md, README.md, ARCHITECTURE.md, architecture.md, CONVENTIONS.md, ROADMAP.md, roadmap.md, SCRATCHPAD.md, CHANGELOG.md, SKILL.md, sources.yaml, compatibility.yaml, references/**/*.md, tests/*.md, context-map.yaml, scripts/README.md, scripts/**, justfile, Justfile, Taskfile.yml, Makefile, package.json, memory-bank/**/*.md, .archcore/**/*.md, docs/**/*.md
- Files matching these patterns are excluded: node_modules/**, .git/**, dist/**, build/**, cache/**, runtime/**, __pycache__/**, .venv/**, graphify-out/**, .ai-context/**
- Files matching patterns in .gitignore are excluded
- Files matching default ignore patterns are excluded
- Files are sorted by Git change count (files with more changes are at the bottom)

# Directory Structure
````
.archcore/
  adr/
    independent-platform-pack.adr.md
  plans/
    keep-the-pinned-box-before-registry-eol.plan.md
  rules/
    lab-writes-stay-in-the-project.rule.md
    memory-channel-name.rule.md
    name-the-provider.rule.md
  index.guide.md
references/
  boxes-and-pinning.md
  clones-snapshots-and-identity.md
  evolution-and-write-back.md
  lab-safety-and-guards.md
  licensing-and-editions.md
  networking-and-synced-folders.md
  operations-cookbook.md
  parallels-prlctl.md
  providers-and-choice.md
  qemu-and-libvirt.md
  tool-choice-and-lab-symmetry.md
  upgrade-and-troubleshooting.md
  vagrantfile-and-provisioning.md
  virtualbox.md
scripts/
  check_governance.py
  doc-freshness-baseline.json
  README.md
  role-check-baseline.json
  vagrant_copy_check.py
  vagrant_lab_inventory.py
  vagrantfile_lint.py
tests/
  eval-procedure.md
  scenarios.md
AGENTS.md
AI_NAVIGATION.md
CHANGELOG.md
CLAUDE.md
compatibility.yaml
context-map.yaml
justfile
Justfile
README.md
SCRATCHPAD.md
SKILL.md
sources.yaml
````

# Files

## File: .archcore/adr/independent-platform-pack.adr.md
````markdown
---
title: Independent Vagrant platform pack
type: adr
status: proposed
tags: [pack-boundary, provider]
created: 2026-11-07
Last reviewed: 2026-11-09
---

# ADR: Independent Vagrant platform pack

Status: proposed (2026-11-07), awaiting the operator.

## Context

Vagrant and Parallels lab knowledge was gathered inside smc-resiliency's Pi spike work (its Vagrantfile, `spike/to_vm.sh`, `spike/vm/sm/setup_sm.sh`) and in project rules. On 2026-11-07 the
operator asked for "skill-proxmox and skill-vagrant based on the learnings", built like skill-nautobot, and for online research to widen them.

## Decision

`skill-vagrant` is a standalone, cross-project pack under `specialists/platform/` for local lab VMs with Vagrant and the Parallels provider on Apple silicon. It is separate from
`skill-proxmox` (the x86 lab and OpenTofu) and from the skills that own what runs inside a guest (`skill-smc` for SMC images).

## Consequences

- The primary pack for a task is chosen by the object being changed (Vagrantfile, box, Parallels VM, lab guard).
- VM names, lab addresses and stages stay in the engaging project; the pack cites them only as worked examples with path and commit.
- Every engagement owes a write-back here (`references/evolution-and-write-back.md`).

Confidence: high on the operator's request; boundaries proposed by the building agent.

## Amendment 2026-11-09: every provider the operator uses

Operator, 2026-11-09: "Vagrant is not only limited to parallels but I also use qemu and virtualbox". The pack covers Vagrant labs on the Mac with
any of the installed providers: Parallels (the default and the deepest coverage), VirtualBox, vagrant-qemu, and vagrant-libvirt driving a remote
Linux host. Provider-specific knowledge lives in `references/providers-and-choice.md`, `references/virtualbox.md` and
`references/qemu-and-libvirt.md`; the rest of the references stay provider-neutral where they can and say so where they are Parallels-only.
The boundary with skill-proxmox is unchanged: a Proxmox node is not a vagrant-libvirt target here.
````

## File: .archcore/plans/keep-the-pinned-box-before-registry-eol.plan.md
````markdown
---
title: Keep the pinned box before the box registry closes
type: plan
status: proposed
tags: [boxes, registry, provider]
created: 2026-11-07
Last reviewed: 2026-11-09
---

# Plan: Keep the pinned box before the box registry closes

Status: proposed (2026-11-07), awaiting the operator.

## Why

HCP Vagrant, which serves `bento/...` boxes, ends operations on 2026-12-31 (`documents/research-sources-20261107/hcp-vagrant-eol.md`). A lab pinned to `bento/ubuntu-24.04` `202510.26.0`
cannot be rebuilt from the pin after that unless the box is kept or rehosted.

## Steps

1. Operator chooses a storage place outside any git repo (the box is about 3.5 GB).
2. `vagrant box repackage bento/ubuntu-24.04 parallels 202510.26.0` and `vagrant box repackage bento/ubuntu-24.04 virtualbox 202510.26.0` in
   that place (both are installed, observed 2026-11-09); record each file's sha256 beside it. Other boxes a lab still rebuilds from (see
   `vagrant box list`) follow the same step.
3. Record the location and hash in the engaging project (smc-resiliency) and a Learned entry in `references/boxes-and-pinning.md`.
4. Test the restore on a scratch name (`vagrant box add --name lab/ubuntu-24.04-202510.26.0 <file>`) without touching the running lab.
5. Watch for where bento publishes after 2026-12-31 and update the reference.

## Done when

The file, its hash and a tested restore command are recorded; no running VM was touched.

## Status 2026-11-09

52 days to end of operations. bento has not announced a new home: RFC chef/bento#1699 (GitLab package registry plus a `metadata.json` on GitLab
Pages) is still open (`documents/research-sources-20261109/bento-issue-1699.md`). The VirtualBox build of the same box version is installed too,
so step 2 now covers two providers. Still waiting on the operator's storage location (step 1).
````

## File: .archcore/rules/lab-writes-stay-in-the-project.rule.md
````markdown
---
title: VM writes stay in the engaging project
type: rule
status: proposed
tags: [safety, provider]
created: 2026-11-07
Last reviewed: 2026-11-09
---

# Rule: VM writes stay in the engaging project

Status: proposed (2026-11-07), awaiting the operator.

## Rule

This pack's helpers and its own sessions run read-only commands only: `vagrant` (status, box list, global-status, plugin list, serial-config),
`prlctl` (list, capture), `VBoxManage` (list, showvminfo, `controlvm ... screenshotpng`, list extpacks) and `virsh` (list, dominfo). Starting, stopping, resetting, cloning,
snapshotting, reprovisioning or destroying a VM is done by the engaging project's tooling, behind its plan/`--apply` gate, with a fixed lab VM name and a deadline on every call.

## Why

The pack is shared by every project; a write helper here would run without the project's guards (its wrong-VM marker, its disk guard, its stage records). The brief that created the
pack said: "Do not start, stop, reset or change any VM; read-only vagrant/prlctl commands only."

## Enforcement

`tests/test_package_contract.py` requires a timeout on every subprocess call in `scripts/`; `scripts/README.md` labels each helper; a helper that writes would need a new rule here first.

Amended 2026-11-09: the read-only list now names every provider's CLI (scope widened in the ADR the same day).
````

## File: .archcore/rules/memory-channel-name.rule.md
````markdown
---
title: Memory channel is exactly vagrant
type: rule
status: proposed
tags: [memory]
created: 2026-11-07
Last reviewed: 2026-11-09
---

# Rule: Memory channel is exactly `vagrant`

Status: proposed (2026-11-07), awaiting the operator; mirrors skill-nautobot's `nautobot` rule.

## Rule

memory-keeper entries about this pack use the channel `vagrant` — exactly that string. Project-specific lab notes may also go to the engaging project's channel.

## Why

One channel per platform pack makes recall for Vagrant work one query across projects.

## Enforcement

None automated. memory-keeper truncates channels to 20 characters and normalises underscores to hyphens; `vagrant` is unaffected by either.
````

## File: .archcore/rules/name-the-provider.rule.md
````markdown
---
title: A lab names its provider
type: rule
status: proposed
tags: [provider, safety]
created: 2026-11-09
Last reviewed: 2026-11-09
---

# Rule: A lab names its provider

Status: proposed (2026-11-09), awaiting the operator.

## Rule

A lab's Vagrantfile has exactly one `config.vm.provider` block for the provider it runs on, or its driver passes `--provider=<name>` on every
`vagrant up`. A Vagrantfile meant for several providers puts its preferred provider's block first and says so in its header.

## Why

Four providers are installed on the lab Mac (2026-11-09). Without `--provider`, Vagrant takes `VAGRANT_DEFAULT_PROVIDER`, then the first usable
provider block in file order, then plugin priority (`references/providers-and-choice.md`, claim V-C27), so the same file can come up on a
different hypervisor on another Mac or after a plugin install, with other networks, other guest agents and another VM name space.

## Enforcement

`vagrantfile_lint.py --provider <name>` fails a file with no block for that provider. Not enforced: a file with blocks for several providers in an
unintended order (candidate check).
````

## File: .archcore/index.guide.md
````markdown
---
title: Archcore index — skill-vagrant
status: accepted
tags: [index]
---

Durable index of everything in `.archcore/` for skill-vagrant. Written at creation on 2026-11-07; reviewed 2026-11-09 (scope widened to every provider, plan status, new rule). Every document below is `proposed` until the operator accepts it; supersede an accepted
document in place with a dated note naming its replacement rather than deleting it.

## adr/

| Document | Status |
|---|---|
| [independent-platform-pack.adr.md](adr/independent-platform-pack.adr.md) | proposed |

## rules/

| Document | Status |
|---|---|
| [lab-writes-stay-in-the-project.rule.md](rules/lab-writes-stay-in-the-project.rule.md) | proposed |
| [memory-channel-name.rule.md](rules/memory-channel-name.rule.md) | proposed |
| [name-the-provider.rule.md](rules/name-the-provider.rule.md) | proposed |

## plans/

| Document | Status |
|---|---|
| [keep-the-pinned-box-before-registry-eol.plan.md](plans/keep-the-pinned-box-before-registry-eol.plan.md) | proposed |

## Never promoted, and why

| Candidate area | Reason |
|---|---|
| specs/ — claim and environment ledger schemas | Already specified executably by `tests/test_package_contract.py` |
| guides/ — write-back procedure | Lives in `references/evolution-and-write-back.md`, which the contract test enforces |
| Version-of-record rule | Same rule as skill-nautobot's `changelog-version-of-record`; stated once in `AGENTS.md` here |
````

## File: references/boxes-and-pinning.md
````markdown
---
Title: Boxes and pinning
Category: reference
Status: current
Authority: >-
  skill-vagrant canonical reference; claims carry evidence labels and cite captures in documents/
Scope: skill-vagrant: local Vagrant and Parallels labs on macOS Apple silicon
Last reviewed: 2026-11-09
Summary: Pin an exact box version and arm64 architecture, bento history (fixed machine-ids), the HCP Vagrant registry closing on 2026-12-31 and keeping the pinned box, safe box removal.
---

# Boxes and pinning

A box is the base image a Vagrant machine is cloned from. A lab that must give the same result next month pins the exact box version, and records why that version.

## Contents

- [Pin the version, not the name](#pin-the-version-not-the-name)
- [Constraints](#constraints)
- [Architecture on Apple silicon](#architecture-on-apple-silicon)
- [Update checks](#update-checks)
- [Bento boxes](#bento-boxes)
- [The box registry](#the-box-registry)
- [Removing boxes](#removing-boxes)
- [Worked example](#worked-example)

## Pin the version, not the name

`config.vm.box_version` "defaults to '>= 0' (the latest version available)"; with constraints, Vagrant "will use the latest available box satisfying these constraints" (VERIFIED_PRIMARY,
[vagrant-machine-settings.md], [vagrant-box-versioning.md]). So a Vagrantfile with only `config.vm.box` silently moves to a newer image when one is published and the machine is recreated. A lab pins
one exact version:

```ruby
config.vm.box = "bento/ubuntu-24.04"
config.vm.box_version = "202510.26.0"     # exact: no operator, no range
```

The pin decides the image at creation time only: an existing machine keeps the disk it was cloned from until it is destroyed and brought up again.

## Constraints

Constraints combine `= X`, `> X`, `< X`, `>= X`, `<= X` and `~> X` with commas; `~> 1.1.5` means `>= 1.1.5, < 1.2.0` (VERIFIED_PRIMARY, [vagrant-box-versioning.md]). A range (`>=`, `~>`) is not a pin:
`vagrantfile_lint.py` warns on it. Bento versions are dates (`YYYYMM.DD.N`), not semantic versions, so `~>` has no compatibility meaning for them (UNVERIFIED as a bento policy; the registry rows show
the date shape, [bento-ubuntu-2404-api.md]).

## Architecture on Apple silicon

`config.vm.box_architecture` accepts values such as `"amd64"` and `"arm64"`; `:auto` (the default) detects the host and fetches that architecture; `nil` fetches the box flagged as the default
architecture (VERIFIED_PRIMARY, [vagrant-machine-settings.md]). On an Apple silicon Mac the Parallels provider needs an arm64 box. Older bento names carried `-arm64` (`bento/ubuntu-22.04-arm64`);
`bento/ubuntu-24.04` publishes one version with several architectures per provider (VERIFIED_PRIMARY, registry API on 2026-11-07: version 202510.26.0 has `parallels` for `arm64` and `amd64`,
[bento-ubuntu-2404-api.md]).

> **Learned 2026-11-09** · Parallels Desktop 27 on Apple silicon · VERIFIED_PRIMARY · Source: documents/research-sources-20261109/parallels-27-x86-emulation-create-vm.md · Falsifier: a bento amd64 Parallels box that boots under emulation with Parallels Tools running and answers `vagrant ssh`
> An `amd64` Parallels box is not a lab path on Apple silicon. Parallels' x86_64 emulation (`prlctl create <vm> -d <distro> --cpu-type x86`) supports direct installs of Windows 10 and Windows Server
> only, and Parallels warns that Linux guests bring "many challenges, including, but not limited to, Parallels Tools for Linux failing to install". Without Tools, `prlctl exec`, graceful stop and
> shared folders fail (see [parallels-prlctl.md](parallels-prlctl.md#parallels-tools)). Use the `arm64` build of the box; an x86 test belongs on the Proxmox lab.

## Update checks

`config.vm.box_check_update` (default true) checks for a newer box on every `vagrant up` and only tells the user; `VAGRANT_BOX_UPDATE_CHECK_DISABLE` turns the check off globally and does not affect
`vagrant box update` (VERIFIED_PRIMARY, [vagrant-machine-settings.md], [vagrant-env-vars.md]). The check never changes a pinned machine; it is noise for a pinned lab and a signal for a review of the
pin.

## Bento boxes

Bento is Progress Chef's set of Packer templates for Vagrant base boxes; a subset is built and published to the `bento` organisation; building needs Packer and, for Parallels boxes, Parallels Desktop
Pro (VERIFIED_PRIMARY, [bento-readme-github.md]). A bento box is a vanilla OS install plus the provider's guest tools; anything a lab needs beyond that is provisioning in the Vagrantfile.

History worth knowing before pinning: several bento Ubuntu releases shipped with a fixed `/etc/machine-id`, so every VM from that box asked DHCP with the same identity and got the same address (bento
issues 1421 for ubuntu-20.04 202206.03.0, 1473 for 20.04-arm64 202301.20.0, 1562 for 22.04-arm64 202401.31.0 on Parallels; VERIFIED_PRIMARY, [vp-issue-1421.md], [vp-issue-1473.md], [vp-issue-1562.md];
vagrant-parallels issue 441, [vp-issue-441.md]). After pinning a new version, bring up two machines from it and compare `/etc/machine-id`; see [clones-snapshots-and-identity.md](clones-snapshots-and-identity.md).

The guest's point release and kernel come with the box: bento/ubuntu-24.04 202510.26.0 boots Ubuntu 24.04.3 with kernel 6.8.0-86 (USER_STATED, lab observation 2026-11-07, recorded in
[compatibility.yaml](../compatibility.yaml)). A later `apt upgrade` in provisioning moves both; pin the archive as well when that matters ([tool-choice-and-lab-symmetry.md](tool-choice-and-lab-symmetry.md)).

## The box registry

The public box catalog is the HCP Vagrant Box Registry (formerly Vagrant Cloud) (VERIFIED_PRIMARY, [vagrant-hcp-box-registry.md], [vagrant-box-catalog.md]). Its v2 API answers `GET
https://vagrantcloud.com/api/v2/box/<user>/<name>` with every version, its status and its providers and architectures (observed 2026-11-07, [bento-ubuntu-2404-api.md]); `vagrant_lab_inventory.py
--latest` reads it to compare a pin with the newest release. Box versions are `unreleased`, `active` or `revoked` ([vagrant-box-versioning-cloud.md]).

**The registry is being shut down.** HashiCorp's notice (VERIFIED_PRIMARY, [hcp-vagrant-eol.md], also on every Vagrant Cloud docs page): no new boxes from 2026-10-01, end of support and maintenance
2026-11-02, end of operations 2026-12-31, "all deployments will be decommissioned". The Vagrant CLI stays; boxes must be hosted by their owners. Consequences for a lab:

- A pin such as `bento/ubuntu-24.04` `202510.26.0` resolves only while the registry (or a replacement location bento announces) serves it. Where bento will publish after 2026-12-31 is UNVERIFIED (its
  README still points to Vagrant Cloud, [bento-readme-github.md]).
- Keep the pinned box locally now: `vagrant box repackage NAME PROVIDER VERSION` writes the installed box to the current directory "so you can redistribute it" (VERIFIED_PRIMARY,
  [vagrant-cli-box.md]); store it outside the repo (it is gigabytes) with its sha256, and record where.
- Rebuild path: `vagrant box add <name> <file-or-url>` with a box metadata file for versioned self-hosting, or build the box with bento's Packer templates.

> **Learned 2026-11-09** · bento after HCP Vagrant end of life · VERIFIED_PRIMARY · Source: documents/research-sources-20261109/bento-issue-1699.md; `gh release list -R chef/bento` on 2026-11-09 (latest v5.1.0, 2026-06-04) · Falsifier: a bento README, release or closed issue that names a post-2026-12-31 box location
> Seven weeks before the registry ends operations, bento has not announced where its boxes will live. The only proposal is RFC chef/bento#1699 (opened 2026-09-08, still open): box files in GitLab's
> generic package registry and a `metadata.json` catalog on GitLab Pages, so `vagrant box add <metadata-url>` keeps versions working. A comment on it suggests a registry serving the Vagrant Cloud API,
> reached by `VAGRANT_SERVER_URL` or `config.vm.box_url`, so box names and `vagrant box update` keep working; that comes from a third party and is UNVERIFIED here (`VAGRANT_SERVER_URL` is not on the
> captured environment-variable page). Until bento decides, the only safe plan is a local copy of the pinned box (`.archcore/plans/keep-the-pinned-box-before-registry-eol.plan.md`).

```text
 2026-10-01          2026-11-02            2026-11-09                    2026-12-31
 no new boxes ────── end of support ────── bento: no new home yet ────── end of operations: registry boxes gone
                                            (RFC chef/bento#1699 open)    a pin then rebuilds only from a local
                                                                          `vagrant box repackage` copy
```

## Removing boxes

With vagrant-parallels, a new machine is a linked clone of the box image by default; "the box deletion will make all its linked clones not working" (VERIFIED_PRIMARY, [vp-configuration.md]). Before
`vagrant box remove` or `vagrant box prune`, list which machines were created from that box version (`vagrant_lab_inventory.py` joins machine homes to their Vagrantfile pins). `vagrant box prune
--dry-run` prints what it would remove; `--force --keep-active-boxes` keeps boxes in use (VERIFIED_PRIMARY, [vagrant-cli-box.md]). With the registry closing, a pruned version may not be downloadable
again.

## Worked example

The smc-resiliency Pi spike lab pins one box for four machines (canonical `vagrant_stuff/smc-pi-spike01/Vagrantfile` @ 8591b72, copy in `smc-resiliency/spike/vm/vagrant/smc-pi-spike01/Vagrantfile` @
4e436e8d):

```ruby
Vagrant.configure("2") do |config|
  config.vm.box = "bento/ubuntu-24.04"
  config.vm.box_version = "202510.26.0"
```
````

## File: references/clones-snapshots-and-identity.md
````markdown
---
Title: Clones, snapshots and identity
Category: reference
Status: current
Authority: >-
  skill-vagrant canonical reference; claims carry evidence labels and cite captures in documents/
Scope: skill-vagrant: local Vagrant and Parallels labs on macOS Apple silicon
Last reviewed: 2026-11-09
Summary: Vagrant linked clones vs prlctl lab clones, what a copy shares (machine-id, host keys), how to keep a clone off the source's network or give it a new identity, snapshots.
---

# Clones, snapshots and identity

A copy of a VM is cheap under Parallels and dangerous when it keeps the original's identity. This file covers the two kinds of linked clone a lab meets, what a copy shares with its source, and
snapshots. Captures named `[file]` are in [documents/research-sources-20261107/](../documents/research-sources-20261107/readme.md).

## Contents

- [Two kinds of linked clone](#two-kinds-of-linked-clone)
- [Cloning a lab VM with prlctl](#cloning-a-lab-vm-with-prlctl)
- [Machine-id](#machine-id)
- [What else a copy shares](#what-else-a-copy-shares)
- [Snapshots](#snapshots)
- [Worked example](#worked-example)

## Two kinds of linked clone

1. **Every vagrant-parallels machine.** Since vagrant-parallels 2.0.0 (2018-11-19) `vagrant up` creates a new VM as a linked clone of the box image (a disk under 1 MB bound to the box's snapshot);
   `linked_clone = false` makes a full, independent copy for new machines; deleting the box breaks its linked clones (VERIFIED_PRIMARY, [vp-configuration.md], [vp-changelog-github.md]). The box image
   is registered, cloned and unregistered during `up`, so `prlctl list -i` shows no `Parent VM` for these machines ([vp-issue-522.md] log; observed 2026-11-07).
2. **A lab clone of a lab VM.** `prlctl clone <vm> --name <new> --linked` makes a linked clone of an existing VM (optionally from a snapshot, `-i <snapid>`); `--regenerate-src-uuid` regenerates the
   source ID and the SMBIOS product ID (VERIFIED_PRIMARY, CLI reference p.17). Its `Parent VM` names the source. The source must stay: the clone's disk holds only its changes.

```text
 box image  (~/.vagrant.d/boxes/<name>/<version>/parallels)     `vagrant box remove`/`prune` breaks everything below
   └─ snapshot ── linked clone: Vagrant machine "lab-a"          kind 1; no Parent VM shown (image unregistered after up)
                    └─ prlctl clone --linked: "lab-a-copy"       kind 2; Parent VM = lab-a, so lab-a must stay
                         └─ snapshots of lab-a-copy              rollback inside a session, never a backup
```

## Cloning a lab VM with prlctl

- Clone a stopped VM: the worked example stops a running source first ("Parallels clones only a stopped VM (not running, not suspended)", `setup_sm.sh` @ 2402b961; USER_STATED, observed on Parallels
  26 to 27).
- Give the clone new MACs (`prlctl set <clone> --device-set net0 --mac auto`) and decide, per adapter, whether it may meet the source's networks.
- A clone is not Vagrant-managed: `vagrant ssh`, `vagrant halt` and `vagrant destroy` in the source's folder still act on the source. Drive the clone with `prlctl exec` and `prlctl` power commands,
  and delete it with `prlctl delete <clone>` (a write; the operator's).
- Watch the host disk: a linked clone grows with every write it makes; the worked example refuses to start with under 8 GiB free on the data disk.

## Machine-id

`/etc/machine-id` identifies the installation. systemd-networkd's default DHCP identity is a DUID hashed from it, so two VMs with one machine-id get one DHCP lease on a shared network
([networking-and-synced-folders.md](networking-and-synced-folders.md#same-dhcp-address-on-two-vms)). A clone copies the file. Images "created once and used on multiple machines" should ship it missing or empty, so an ID is generated at boot; an empty file is not a
first boot, a missing file or the string `uninitialized` is (VERIFIED_PRIMARY, [machine-id-man.md]).

Check before trusting a copy:

```bash
timeout 30 prlctl exec <source> "cat /etc/machine-id"; timeout 30 prlctl exec <clone> "cat /etc/machine-id"   # must differ
timeout 30 prlctl list -a -f | grep -E '<source>|<clone>'                                                          # addresses must differ
```

Choices, safest first:

1. **No shared network for the clone** (the smc-resiliency rule since 2026-11-06): disconnect the adapters it shares with the source; reach it by `prlctl exec`. Nothing to regenerate, nothing to
   forget.
2. **New identity in the clone** before it joins a shared network: empty `/etc/machine-id` (and check `/var/lib/dbus/machine-id` is a link to it, not a copy, because systemd falls back to it when the
   file is empty), then reboot; systemd writes a new ID (semantics VERIFIED_PRIMARY, [machine-id-man.md]; the procedure on a Parallels clone is UNVERIFIED until a lab runs it and records the new
   lease).
3. **Fix the box**: for many machines from one box, use a box version whose image ships without a fixed ID (the bento regressions are listed in [boxes-and-pinning.md](boxes-and-pinning.md#bento-boxes)).

A new MAC alone does not help: the DUID does not use the MAC unless `DUIDType=link-layer` or `ClientIdentifier=mac` is configured (VERIFIED_PRIMARY, [networkd-conf-man.md], [systemd-network-man.md]).

## What else a copy shares

SSH host keys (so `known_hosts` cannot tell the copies apart), the Vagrant insecure-key replacement in `~/.ssh/authorized_keys`, any service identity under `/etc` or `/var/lib` (a device key, a
registration token), and the hostname. A copy used for a different test renames itself and regenerates what the test depends on, or stays off every network the source uses.

| What                                    | Copied by a clone                                     | Effect when two copies meet          | What to do                                             |
| --------------------------------------- | ----------------------------------------------------- | ------------------------------------ | ------------------------------------------------------ |
| `/etc/machine-id`                       | yes                                                   | one DHCP lease for both              | no shared network, or empty it and reboot (above)      |
| MAC address                             | yes, unless `--mac auto`                              | none on its own (DUID wins)          | `prlctl set <clone> --device-set netN --mac auto`      |
| SSH host keys                           | yes                                                   | `known_hosts` cannot tell them apart | regenerate before the clone meets the source's network |
| `~/.ssh/authorized_keys` (Vagrant key)  | yes                                                   | the same key logs in to both         | expected; the guard, not the key, tells them apart     |
| hostname                                | yes                                                   | identical prompts and logs           | rename it in the clone                                 |
| service identities (`/etc`, `/var/lib`) | yes                                                   | duplicate registrations              | regenerate what the test depends on                    |
| Parallels name and UUID                 | no (new name; `--regenerate-src-uuid` for the source) | the only reliable difference         | key guards and drivers on it                           |

## Snapshots

- `vagrant snapshot save|restore|list|delete <machine> <name>`, or `push`/`pop` as a stack; do not mix `push`/`pop` with `save`/`restore`; not every provider supports snapshots (VERIFIED_PRIMARY,
  [vagrant-cli-snapshot.md]). vagrant-parallels has implemented `vagrant snapshot` since its 1.x series (VERIFIED_PRIMARY, [vp-changelog-github.md], GH-228).
- `prlctl snapshot <vm> -n <name> -d <desc>`, `snapshot-list <vm> -t` (tree) or `-j`, `snapshot-switch <vm> -i <id> [--skip-resume]`, `snapshot-delete <vm> -i <id> [-c]` (VERIFIED_PRIMARY, CLI
  reference pp.39-40).
- A snapshot of a vagrant-parallels machine sits on top of a linked clone of the box: removing the box still breaks it.
- Snapshots are a rollback inside a session, not a backup and not a reproducible build; the Vagrantfile and its pins are what rebuild the lab.
- Take a snapshot before a destructive stage (a disk-fill test, an image switch) and name it after the stage; record its ID with the run.

## Worked example

smc-resiliency's SM stage (measuring root writes) runs on a linked clone of the Pi spike VM, so the spike VM's state is untouched (`smc-resiliency/spike/vm/sm/setup_sm.sh` @ 2402b961):

```bash
# Parallels clones only a stopped VM (not running, not suspended): shut the spike VM down for the clone and start it after
WAS=$(prlctl list -o status "$SRC" | tail -1 | tr -d ' ')
[ "$WAS" = running ] && { timeout 300 prlctl stop "$SRC" >/dev/null || exit 1; }
timeout 600 prlctl clone "$SRC" --name "$VM" --linked; RC=$?
[ "$WAS" = running ] && timeout 300 prlctl start "$SRC" >/dev/null
timeout 60 prlctl set "$VM" --device-set net0 --mac auto >/dev/null && timeout 60 prlctl set "$VM" --device-set net1 --disconnect >/dev/null
```

On 2026-11-06 the clone still received the spike VM's address on the shared network, because it kept the machine-id; `vagrant ssh smc-pi-spike01` then reached the clone. The project disconnected the
clone's shared adapter and added a guard to its driver ([lab-safety-and-guards.md](lab-safety-and-guards.md#refuse-the-wrong-vm)).

> **Learned 2026-11-07** · copy-on-write root · VERIFIED_PRIMARY · Source: smc-resiliency docs/pi/pi-spike-sm-root-writes-20261107_1602.md · Falsifier: a runtime install on a dm-snapshot root that survives a reboot
> On a lab clone whose root is a RAM copy-on-write, anything installed at run time (a fixed watcher script) is gone after the reboot; reinstall after each boot or install into the origin. `dmsetup
> status` of a snapshot counts 512-byte sectors.
````

## File: references/evolution-and-write-back.md
````markdown
---
Title: Evolution and write-back
Category: reference
Status: current
Authority: >-
  skill-vagrant canonical reference; claims carry evidence labels and cite captures in documents/
Scope: skill-vagrant: local Vagrant and Parallels labs on macOS Apple silicon
Last reviewed: 2026-11-09
Summary: The standing write-back contract: engagement classes, the Learned and Disputed entry format, evidence with every entry, research captures, release reconciliation and script promotion.
---

# Evolution and write-back

## Standing write-back contract

This skill is a cross-project source of Vagrant and Parallels lab knowledge. Invoking it carries the obligation, in any project, to write back what the engagement taught: a new fact, a version change
in behaviour, a fix, a root cause, or a correction. Write it before the session ends when the active task permits edits to this skill's canonical source; skill use alone never authorizes a VM action.
Read the edited file back in the same session: a scratchpad note or a timestamp is not proof.

Classify every engagement at closeout, one sentence in the reply:

| Class                        | Action                                                                                    |
| ---------------------------- | ----------------------------------------------------------------------------------------- |
| `no_new_reusable_learning`   | Nothing to write; say so                                                                  |
| `verified_reusable_update`   | Add a Learned entry to the focused reference and one CHANGELOG line under `## Unreleased` |
| `reusable_candidate`         | Same, with evidence `UNVERIFIED` and a falsifier that would settle it                     |
| `contradicts_existing_claim` | Add a Disputed entry beside the old text; never delete or silently rewrite it             |
| `project_only`               | Write it in the engaging project's docs (its lab layout, VM names, stages), not here      |
| `guest_only`                 | Write it in the skill that owns what runs in the guest (for example skill-smc), not here  |

## Entry format

Put the entry in the reference a future reader would open for that task (the routing table in `SKILL.md`), at the end of the relevant section. Two lines minimum:

```text
> **Learned 2026-11-07** · Vagrant 2.4.9 / vagrant-parallels 2.4.9 / Parallels 27.1 · VERIFIED_PRIMARY · Source: <doc URL or capture> · Falsifier: <observation that would prove it wrong>
> <the fact, generic: no site names, hostnames, addresses, keys or credentials>
```

A contradiction uses `> **Disputed YYYY-MM-DD**` with the same fields plus `Conflicts: <claim ID, section or statement>`. The evidence label is one of `VERIFIED_PRIMARY`, `VERIFIED_SECONDARY`,
`UNVERIFIED`, `USER_STATED` or `CANDIDATE`. The CHANGELOG line names the reference file and the same date. `tests/test_package_contract.py` fails on a malformed entry, or on an entry with no matching
CHANGELOG line.

If this skill's source cannot be written, put the same entry in the engaging project's governed docs under a heading naming this skill, and link it from that project's index; the next engagement with
write access promotes it.

## Evidence with every entry

Operator, 2026-10-20 (every calling project owes it): a write-back that records how something is done carries (1) a **code excerpt** of the logic that does it: the few lines that matter (about 30 at
most), as a fenced block with its source path and commit, secrets and lab addresses removed; and (2) for anything with a visual surface (a VM console, the Parallels Control Center) a **screenshot**,
saved under `references/screenshots/<YYYYMMDD>-<slug>/` with a `readme.md` naming each image, what it shows and where it was taken. A console screenshot comes from `prlctl capture <vm> --file <png>`
on a lab VM.

## Research sources

A fact from outside the lab is captured verbatim before it is used: `documents/research-sources-<YYYYMMDD>/<slug>.md` with a provenance header (Canonical URL, Retrieved, HTTP status or fetch path),
indexed with its sha256 in that folder's `readme.md`. Pages that block agents are fetched with all-scraper (`just -f /Volumes/Data/_ai/_tool/tools_stuff/all-scraper/justfile fetch <url> --markdown`);
GitHub issues and files with `gh`. The contract test checks that the index lists every capture with its hash.

## Release reconciliation

At a release, the maintainer: promotes each still-valid Learned entry into the reference prose; adds a `sources.yaml` claim only when the fact is load-bearing; adds or updates a `compatibility.yaml`
row when the evidence came from a new version or a live rung; adds a scenario when a no-skill agent would plausibly get the fact wrong; moves `## Unreleased` under the new version; and reruns the
tests.

## Promoting a project script

A lab script earns promotion when its behaviour holds for any Vagrant or Parallels lab, it imports nothing project-specific, and its engine can be pure or read-only with the command runner injected by
the caller. Then: the engine goes to `scripts/` with offline tests in `tests/test_helpers.py` (stdlib only, enforced by the contract test); the project script becomes a thin wrapper; and the CHANGELOG
names the source project and script. `vagrant_copy_check.py` is the generic form of smc-resiliency's `check_vagrant_copies` (promoted 2026-11-07; the project keeps its own check).

## Keeping it current

`operations-cookbook.md` names the versions it was verified against. When Vagrant, vagrant-parallels or Parallels Desktop changes, re-verify every section whose syntax the task relies on, then update
that line and `compatibility.yaml`. A single success is a candidate, not a rule: label it `UNVERIFIED` until a second environment, the official documentation or the source agrees.
````

## File: references/lab-safety-and-guards.md
````markdown
---
Title: Lab safety and guards
Category: reference
Status: current
Authority: >-
  skill-vagrant canonical reference; claims carry evidence labels and cite captures in documents/
Scope: skill-vagrant: local Vagrant and Parallels labs on macOS Apple silicon
Last reviewed: 2026-11-09
Summary: Rules for lab drivers: plan by default and --apply, an in-guest wrong-VM marker, deadlines and keepalives, quoting once, hash what arrived, disk fill, host guards, Vagrantfile copy checks.
---

# Lab safety and guards

Rules for scripts that drive lab VMs from the Mac. They follow skill-coder (plan by default, `--apply` for writes, a deadline on every call) and add what a VM lab needs: proof that the command reached
the intended VM, and a canonical Vagrantfile that the project copy cannot drift from.

## Contents

- [Plan by default, write with --apply](#plan-by-default-write-with---apply)
- [Refuse the wrong VM](#refuse-the-wrong-vm)
- [A deadline on every call](#a-deadline-on-every-call)
- [Quote the remote command once](#quote-the-remote-command-once)
- [Prove what arrived](#prove-what-arrived)
- [Filling a disk on purpose](#filling-a-disk-on-purpose)
- [Host guards](#host-guards)
- [Keep a project copy of the canonical Vagrantfile](#keep-a-project-copy-of-the-canonical-vagrantfile)

## Plan by default, write with --apply

A lab driver prints what it would do and exits 0 unless `--apply` is given; the VM name is fixed in the script, never taken from an argument that could name a site; the header says "Lab only" and what
each action writes (smc-resiliency `spike/to_vm.sh` @ 4e436e8d: "Without --apply it prints the plan and changes nothing. Lab only: the VM's name is fixed here; never point it at a site.").

## Refuse the wrong VM

A name or an address is not proof of which VM answered: a linked clone that shares the machine-id can take the original's DHCP lease, and then `vagrant ssh <original>` reaches the clone
([clones-snapshots-and-identity.md](clones-snapshots-and-identity.md#machine-id)). Put a marker on the VM that must never be touched (or on the one that must), and test it inside the same remote command before anything else runs:

```bash
# smc-resiliency spike/to_vm.sh @ 4e436e8d: the SM clone carries /boot/smc-ramcow-installed; the spike VM does not
on_vm() { (cd "$VD" && vagrant ssh "$VM" -c "sudo bash -c $(printf %q "test ! -e /boot/smc-ramcow-installed || { echo \"refused: reached the SM clone, not the intended VM\" >&2; exit 97; }; $1")" "${SSH_OPTS[@]}"); }
```

The check runs in the guest, in the same shell as the command, so no race between "check" and "do" remains; a distinct exit code (97) lets callers tell a refusal from a failed command. Better still,
give each VM an identity file written at creation (`/etc/lab-role` with the VM name) and compare it with the name the script means.

```text
 driver.sh [--apply]                      VM name fixed in the script, never an argument
   ├─ no --apply ─► print the plan, exit 0
   └─ --apply
        ├─ host guards: free disk ≥ 8 GiB?  name matches?  ─► else refuse, exit non-zero
        └─ timeout N vagrant ssh <vm> -c "<marker test>; <command>" -- -o ConnectTimeout=15 ...
              one shell, inside the guest:
              ├─ marker says "wrong VM" ─► exit 97 (refused; nothing ran)
              └─ marker OK ───────────► run the command ─► its own exit code
```

## A deadline on every call

Every `vagrant`, `prlctl` and `ssh` call has a deadline: `timeout N` in shell, `timeout=` in Python's `subprocess.run`. `vagrant ssh` also gets SSH keepalives, so a dead guest ends the session instead
of hanging it:

```bash
SSH_OPTS=(-- -o ConnectTimeout=15 -o ServerAliveInterval=15 -o ServerAliveCountMax=8)   # to_vm.sh @ 4e436e8d
```

Write `timeout` and its duration as separate words. A wrapper that read `timeout 30"cmd"` failed with "invalid time interval" (USER_STATED, lab 2026-11-07): `30"cmd"` is one word, so `timeout`
received `30cmd` as its duration. `scripts/vagrantfile_lint.py` does not see wrapper scripts; shellcheck and skill-coder's `call_timeouts.py` do, and a test that runs the wrapper once in plan mode
catches it.

## Quote the remote command once

`vagrant ssh -c` and `prlctl exec` each take the remote command as one string. Build it with `printf %q` (bash) or `shlex.quote` (Python) from the exact command, and never splice untrusted text into
it. Large files go over stdin (`base64 < file | prlctl exec vm "bash -c 'base64 -d > path'"`) or `vagrant upload`, not inside the command string.

## Prove what arrived

After copying code into a guest, compare a hash of what is there with the local one and stop on a mismatch (to_vm.sh `install` hashes the sorted `*.py` on both sides). `vagrant upload` into an
existing directory delivered stale files once; upload to a new path per run and move it into place.

## Filling a disk on purpose

Tests that fill a filesystem write with `head -c <N>M /dev/urandom >> <file>` in a loop, inside a transient unit so it survives the session:

```bash
# smc-resiliency spike/vm/sm/setup_sm.sh @ 2402b961 (exhaust: acceptance test A11)
onvm 30 "systemd-run --unit=smc-sm-fill --description='SM exhaustion fill (A11)' bash -c 'for i in \$(seq 1 $(( M / 10 ))); do head -c 10M /dev/urandom >> /var/tmp/smc-fill; sync; sleep 0.1; done'; uptime -s"
```

A hook in the operator's agent environment blocks `dd` (USER_STATED, 2026-11-07), so lab fill scripts use `head -c`. It also sets the rate by chunk size and sleep, and a stop is `systemctl stop
<unit>`.

## Host guards

- Refuse to create a clone or a large disk when the Mac's data volume is short of space (`setup_sm.sh` `disk_guard`: under 8 GiB free).
- Never run a lab driver against a VM whose name does not match the script's fixed name; never accept `--vm` from the command line in a driver that writes.
- Keep secrets out of Vagrantfiles and drivers: no tokens, passwords or private keys; a box registry token comes from the environment at run time.

## Keep a project copy of the canonical Vagrantfile

The canonical Vagrantfile lives in the Vagrant workspace (`vagrant_stuff/<lab>/Vagrantfile`); the project that depends on the lab keeps a copy (never the keys) and a check that fails when the copy is
missing or differs (operator, 2026-10-21: "for the Vagrant files always keep a copy locally as well"; USER_STATED). The project's check:

```python
# smc-resiliency scripts/govcheck/checks/paths.py @ a124c13a
def check_vagrant_copies() -> None:
  """Each Vagrantfile the lab runs on has a copy in the project, equal to its canonical file in vagrant_stuff (skipped when that is absent)."""
  for copy, canonical in VAGRANT_COPIES.items():
    counted()
    local = ROOT / copy
    if not local.is_file():
      fail("vagrant", f"{copy} is missing: copy it from {canonical}")
      continue
    source = Path(canonical)
    if source.is_file() and source.read_bytes() != local.read_bytes():
      fail("vagrant", f"{copy} differs from {canonical}: copy the canonical file over it")
```

(Indentation normalised to two spaces in this excerpt.) The generic form is `scripts/vagrant_copy_check.py` in this pack: `just copy-check <copy>=<canonical> ...` exits 1 when a copy is missing or
differs, and says which. The direction of a fix is always canonical to copy; a change made in the copy is moved to the canonical file first.
````

## File: references/licensing-and-editions.md
````markdown
---
Title: Licensing and editions
Category: reference
Status: current
Authority: >-
  skill-vagrant canonical reference; claims carry evidence labels and cite captures in documents/
Scope: skill-vagrant: local Vagrant and Parallels labs on macOS Apple silicon
Last reviewed: 2026-11-09
Summary: Vagrant licence by version (MIT, BUSL 1.1 for 2.4.0 to 2.4.9, MIT on main since 2026-11-02), what BUSL allowed, the registry vs the CLI, and the Parallels editions that have a CLI.
---

# Licensing and editions

What licence the Vagrant you run is under, what that allows, and which Parallels Desktop edition the lab needs. This is a technical summary of the primary texts, not legal advice; a commercial
question goes to the operator with the captures below. Captures named `[file]` are in [documents/research-sources-20261107/](../documents/research-sources-20261107/readme.md).

## Contents

- [Vagrant: MIT, then BUSL 1.1, then MIT again](#vagrant-mit-then-busl-11-then-mit-again)
- [What BUSL 1.1 allowed](#what-busl-11-allowed)
- [What it means for a lab](#what-it-means-for-a-lab)
- [The box registry is not the CLI](#the-box-registry-is-not-the-cli)
- [vagrant-parallels](#vagrant-parallels)
- [Parallels Desktop editions](#parallels-desktop-editions)

## Vagrant: MIT, then BUSL 1.1, then MIT again

| Vagrant version                             | Licence                                             | Evidence (VERIFIED_PRIMARY)                                                                      |
| ------------------------------------------- | --------------------------------------------------- | ------------------------------------------------------------------------------------------------ |
| up to 2.3.7                                 | MIT ("Copyright (c) 2010 HashiCorp, Inc.")          | [vagrant-license-v2.3.7-github.md]                                                               |
| 2.4.0 to 2.4.9 (latest release, 2025-08-21) | Business Source License 1.1; "Licensed Work:        | [vagrant-license-v2.4.9-github.md]; the installed 2.4.9 gem carries the same text                |
|                                             |   Vagrant 2.4.3 or later" in the 2.4.9 text         |   (observed 2026-11-07)                                                                          |
| `main` after 2026-11-02                     | MIT ("Copyright IBM Corp. 2026")                    | commit ab4fc5e3db "Revert license update ... returning to the MIT license",                      |
|                                             |                                                     |   [vagrant-license-revert-commit-github.md], [vagrant-license-github.md]                         |

HashiCorp announced the move of its products to BSL on 2023-08-10 ([hashicorp-bsl-blog.md], [hashicorp-license-faq.md]). The MIT revert is on `main` only: as of 2026-11-07 no release carries it (the
latest tag is v2.4.9; later entries are `2.4.10.dev` pre-releases). Whether the next release ships under MIT is UNVERIFIED until it is tagged; check the LICENSE file at the tag.

## What BUSL 1.1 allowed

From HashiCorp's FAQ (VERIFIED_PRIMARY, [hashicorp-license-faq.md], FAQ 8, last updated 2023-10-17): "All non-production uses are permitted. All production uses are allowed other than hosting or
embedding the Licensed Work to compete with HashiCorp's paid version of the same Licensed Work, whether hosted or self-managed." The Vagrant 2.4.9 licence's Additional Use Grant says the same in its
own words and defines "competitive offering", "Product" and "Embedded" ([vagrant-license-v2.4.9-github.md]). Releases before the change stay under their old licence: "The license change is not
retroactive" (FAQ 10). Under BSL the code converts to an open licence on its Change Date or four years after first BSL publication (FAQ 19).

## What it means for a lab

Running Vagrant to build and use local lab VMs is neither hosting nor embedding Vagrant in a competing product, so it is permitted under both licences (inference from the texts above; UNVERIFIED as
legal advice). Points that would need the operator: shipping Vagrant inside a product or service offered to others, or redistributing a modified Vagrant. Record the version a lab used; the licence
follows the version.

## The box registry is not the CLI

The HCP Vagrant Box Registry (where `bento/...` boxes are downloaded from) is a hosted service with its own end of life: no new boxes from 2026-10-01, end of support 2026-11-02, end of operations
2026-12-31; "The community edition in GitHub including the CLI will remain available" (VERIFIED_PRIMARY, [hcp-vagrant-eol.md]). See [boxes-and-pinning.md](boxes-and-pinning.md#the-box-registry) for what a lab does about it.

## vagrant-parallels

The provider plugin is open source under the MIT licence (VERIFIED_PRIMARY, [vp-readme-github.md]). Latest release v2.4.10 on 2026-10-28; the lab Mac ran 2.4.9 (observed 2026-11-07) and runs 2.4.10 since 2026-11-09 (`vagrant plugin update`, operator).

> **Learned 2026-11-09** · Vagrant releases · VERIFIED_PRIMARY · Source: `gh release list -R hashicorp/vagrant` on 2026-11-09 · Falsifier: a Vagrant release tag after v2.4.9 dated on or before 2026-11-09
> On 2026-11-09 there is still no Vagrant release after v2.4.9. The newest entry is the pre-release `2.4.10.dev+000834-2757db88` (2026-06-01), which is older than the MIT revert on `main`
> (2026-11-02). Every installable release is therefore still BUSL 1.1. Check the LICENSE file at the next tag before calling a release MIT.

## Parallels Desktop editions

| Statement                                                                                                                         | Source (VERIFIED_PRIMARY)                   |
| --------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------- |
| "In Pro and Business/Enterprise Editions, you can control Parallels Desktop and virtual machines from the command-line interface" | [parallels-cli-utility.md]                  |
| "Only **Pro**, **Enterprise** and **Business** editions of Parallels Desktop for Mac can be used with this Vagrant provider"      | [vp-installation.md]                        |
| "Vagrant plugin is available in Parallels Desktop Pro and Business Editions only"                                                 | [parallels-kb-vagrant.md]                   |
| The provider refuses other editions: "Other editions do not have command line functionality and can not be used with Vagrant"     | [vp-issue-485.md] (error text)              |
| Enterprise licences were refused until vagrant-parallels 2.4.3 "Add 'enterprise' edition support"                                 | [vp-issue-485.md], [vp-changelog-github.md] |
| A trial has "all the same features as Parallels Desktop For Mac Pro version" (forum answer, so VERIFIED_SECONDARY)                | [hashicorp-discuss-parallels-trial.md]      |

So a Standard-edition Mac cannot run this lab at all; check the edition first (`prlsrvctl info --license --json`, read `edition` only). The `parallels/parallels-desktop` OpenTofu provider asks for a
licence key in its configuration ([tool-choice-and-lab-symmetry.md](tool-choice-and-lab-symmetry.md#opentofu-providers-that-touch-vagrant-or-parallels)).
````

## File: references/networking-and-synced-folders.md
````markdown
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

## Addresses in reusable text

Parallels' Shared and Host-Only networks use private ranges chosen by Parallels Desktop (`prlsrvctl net list` shows them); this pack's contract test forbids private addresses in authored files, so
read them from the host rather than from here. Project files keep their lab addresses.
````

## File: references/operations-cookbook.md
````markdown
---
Title: Operations cookbook
Category: reference
Status: current
Authority: >-
  skill-vagrant canonical reference; claims carry evidence labels and cite captures in documents/
Scope: skill-vagrant: local Vagrant and Parallels labs on macOS Apple silicon
Last reviewed: 2026-11-09
Summary: Exact vagrant, prlctl and prlsrvctl syntax for lab sessions with a deadline on every call and writes marked; verified against Vagrant 2.4.9, vagrant-parallels 2.4.9, prlctl 27.1.0.
---

# Operations cookbook

Verified against: Vagrant 2.4.9, vagrant-parallels 2.4.9, prlctl 27.1.0 (Parallels Desktop), macOS on Apple silicon, 2026-11-07

Exact syntax for the commands a lab session uses. Every command that can hang carries a deadline (`timeout N`); every write is marked. Captures named `[file]` are in
[documents/research-sources-20261107/](../documents/research-sources-20261107/readme.md).

## Contents

- [1. Read-only status](#1-read-only-status)
- [2. Running commands in a guest](#2-running-commands-in-a-guest)
- [3. Lifecycle (writes)](#3-lifecycle-writes)
- [4. Boxes](#4-boxes)
- [5. Snapshots](#5-snapshots)
- [6. Parallels networks and adapters](#6-parallels-networks-and-adapters)
- [7. Machine-readable output](#7-machine-readable-output)
- [8. Summary table](#8-summary-table)

## 1. Read-only status

```bash
cd <vagrant-dir> && timeout 60 vagrant status                  # machines in this Vagrantfile, by name
timeout 60 vagrant global-status                                 # every environment Vagrant knows; a cache, not a live probe
timeout 120 vagrant global-status --prune                        # drop rows whose environment is gone (slower)
timeout 30 prlctl list -a                                        # every registered VM: UUID, status, IP, name
timeout 30 prlctl list -a -i -j                                  # full settings of every VM as JSON (State, Parent VM, GuestTools, Hardware.netN)
timeout 30 prlctl list -a -f                                     # the guests' real IP addresses
timeout 30 prlctl status <vm>
timeout 30 prlsrvctl net list                                    # Shared, Host-Only and Vagrant-created host-only networks
```

`global-status` is "based on a cache" and can list environments that no longer exist; `--prune` removes invalid entries and is "much more time consuming" (VERIFIED_PRIMARY,
[vagrant-cli-global-status.md]). `prlctl list` without `-a` shows only running VMs; `-o` picks fields, `-L` lists them, `-j` gives JSON (VERIFIED_PRIMARY, Parallels Desktop 20 Command-Line Reference,
[parallels-desktop-v20-command-line-reference.pdf] p.14).

## 2. Running commands in a guest

```bash
cd <vagrant-dir> && timeout 120 vagrant ssh <machine> -c 'sudo systemctl is-system-running' \
  -- -o ConnectTimeout=15 -o ServerAliveInterval=15 -o ServerAliveCountMax=8
timeout 60 vagrant upload <local-path> <guest-path> <machine>
timeout 30 prlctl exec <vm> "uname -r"                            # no network needed; needs Parallels Tools running in the guest
timeout 30 prlctl capture <vm> --file /tmp/<vm>-console.png       # the console as PNG; works when exec and ssh do not
```

`vagrant ssh [name|id] [-- extra_ssh_args]`: arguments after `--` go to the `ssh` program; `-c COMMAND` runs one command, prints stdout and stderr and exits (VERIFIED_PRIMARY, [vagrant-cli-ssh.md]).
Name the machine in a multi-machine Vagrantfile; without a name `vagrant ssh` uses the primary. `prlctl exec` "Executes a command inside a virtual machine. Parallels Tools must be installed"; Linux
commands run with `bash -c` (VERIFIED_PRIMARY, CLI reference p.19). `prlctl capture` writes a PNG of the screen (VERIFIED_PRIMARY, p.21).

Quote the remote command as one argument. Build it with `printf %q` when it contains quotes or `$`, as the worked example does:

```bash
# smc-resiliency spike/vm/sm/setup_sm.sh @ 2402b961 (2026-11-07): every exec has its own deadline
onvm() { timeout "$1" prlctl exec "$VM" "bash -c $(printf %q "$2")"; }
put() { base64 < "$1" | timeout 60 prlctl exec "$VM" "bash -c 'base64 -d > $2 && chmod $3 $2'"; }
```

## 3. Lifecycle (writes)

```bash
vagrant up [<machine>] [--provider=parallels] [--no-provision]   # creates or starts; provisions on first up only
vagrant provision <machine> [--provision-with <name>]            # re-run provisioners
vagrant reload <machine> [--provision]                           # halt + up (re-applies the Vagrantfile and customize)
vagrant halt <machine>; vagrant destroy -f <machine>
timeout 300 prlctl stop <vm>            # graceful through Parallels Tools, else ACPI; --kill is a hard stop
timeout 120 prlctl restart <vm>         # graceful shutdown then start
timeout 120 prlctl reset <vm>           # 'hard' shutdown then start: the guest gets no chance to flush
```

Restart is graceful, reset is a hard power cycle, `stop --kill` a hard stop; `stop` without `--kill` uses Parallels Tools when installed, otherwise ACPI (VERIFIED_PRIMARY, CLI reference p.20). After a
reset, `prlctl exec` fails until Tools come back (see [parallels-prlctl.md](parallels-prlctl.md#exec-after-a-reset)).

## 4. Boxes

```bash
timeout 60 vagrant box list                       # name (provider, version, (arch))
timeout 120 vagrant box outdated --global         # read-only, calls the registry
vagrant box add bento/ubuntu-24.04 --provider parallels --box-version 202510.26.0     # write: downloads
vagrant box prune --dry-run                        # what prune would remove; a linked clone needs its box (boxes-and-pinning.md)
```

## 5. Snapshots

```bash
vagrant snapshot save <machine> <name>; vagrant snapshot list <machine>; vagrant snapshot restore <machine> <name>
timeout 60 prlctl snapshot <vm> -n <name> -d "<why>"
timeout 30 prlctl snapshot-list <vm> -t           # tree; -j for JSON
timeout 300 prlctl snapshot-switch <vm> -i <snapid> [--skip-resume]
```

Do not mix `vagrant snapshot push/pop` with `save/restore` on one machine (VERIFIED_PRIMARY, [vagrant-cli-snapshot.md]). Detail: [clones-snapshots-and-identity.md](clones-snapshots-and-identity.md).

## 6. Parallels networks and adapters

```bash
timeout 30 prlsrvctl net list
timeout 30 prlsrvctl net info <vnetwork_id>
prlctl set <vm> --device-set net1 --disconnect               # write: unplug an adapter (VM may be running)
prlctl set <vm> --device-set net0 --mac auto                 # write: new MAC (VM stopped)
prlctl set <vm> --device-add net --type host-only --iface <vnet>   # write: add an adapter
```

Adapter types are `shared`, `bridged` and `host-only`; `--mac auto` generates one (VERIFIED_PRIMARY, CLI reference p.34).

## 7. Machine-readable output

`--machine-readable` prints `timestamp,target,type,data...` lines; commas inside data are written as `%!(VAGRANT_COMMA)`, newlines as `\n` (VERIFIED_PRIMARY, [vagrant-cli-machine-readable.md]).
`global-status --machine-readable` gives `machine-id`, `provider-name`, `machine-home` and `state` per environment, but no machine name (observed, Vagrant 2.4.9, 2026-11-07). `box list
--machine-readable` gives `box-name`, `box-provider`, `box-version` and `box-architecture`. `vagrant_lab_inventory.py` parses both.

## 8. Summary table

| Need                     | Command                                                          | Writes           |
| ------------------------ | ---------------------------------------------------------------- | ---------------- |
| What exists              | `vagrant global-status`, `prlctl list -a -i -j`                  | no               |
| Is the guest alive       | `prlctl capture <vm> --file x.png`, then `prlctl exec <vm> true` | no (a local PNG) |
| One command in the guest | `vagrant ssh <m> -c '<cmd>' -- -o ConnectTimeout=15`             | guest            |
| Hard power cycle         | `prlctl reset <vm>`                                              | yes              |
| Pinned box present       | `vagrant box list`                                               | no               |
| Newer box published      | `vagrant box outdated --global`                                  | no               |
| Unplug an adapter        | `prlctl set <vm> --device-set netN --disconnect`                 | yes              |

> **Learned 2026-11-07** · logic over adapters · VERIFIED_PRIMARY · Source: smc-resiliency `lab/adapters/transports.py` (VagrantTransport), `lab/logic/e2e.py`;
> the same cases passed on the Vagrant VM and a Proxmox VM · Falsifier: a Vagrant-only case that cannot run through an ssh transport
> Drive a Vagrant lab from a test package through one transport class (`vagrant ssh <machine> -c "sudo bash -c '<cmd>'"` and
> `vagrant upload <src> <dst> <machine>`, run from the Vagrantfile's folder, each call with a timeout), so the same cases run on a
> Proxmox or bench box through ssh; keep a wrong-VM guard (a marker file the clone carries) in the box-side command, not in the transport.
````

## File: references/parallels-prlctl.md
````markdown
---
Title: Parallels prlctl
Category: reference
Status: current
Authority: >-
  skill-vagrant canonical reference; claims carry evidence labels and cite captures in documents/
Scope: skill-vagrant: local Vagrant and Parallels labs on macOS Apple silicon
Last reviewed: 2026-11-09
Summary: prlctl and prlsrvctl for a lab: editions with a CLI, JSON inventory, exec without the network and its quoting, exec after a reset, console capture, power commands, Parallels Tools.
---

# Parallels prlctl

`prlctl` manages VMs and `prlsrvctl` manages Parallels Desktop itself. Vagrant's provider drives both; a lab uses them directly to reach a guest without the network, to see its console, and to
power-cycle it. Source of record: Parallels Desktop 20 Command-Line Reference ([parallels-desktop-v20-command-line-reference.pdf], PDF page numbers below) and the Parallels Developer's Guide
([parallels-cli-utility.md], [parallels-cli-manage-vms.md]); observed behaviour is on prlctl 27.1.0.

## Contents

- [Who can run it](#who-can-run-it)
- [Inventory](#inventory)
- [exec: a command without the network](#exec-a-command-without-the-network)
- [exec after a reset](#exec-after-a-reset)
- [capture: the console when nothing else answers](#capture-the-console-when-nothing-else-answers)
- [Power: restart, reset, stop](#power-restart-reset-stop)
- [Parallels Tools](#parallels-tools)
- [prlsrvctl](#prlsrvctl)

## Who can run it

"In Pro and Business/Enterprise Editions, you can control Parallels Desktop and virtual machines from the command-line interface" (VERIFIED_PRIMARY, [parallels-cli-utility.md]). The Standard edition
has no CLI, so neither `prlctl` nor vagrant-parallels works with it; see [licensing-and-editions.md](licensing-and-editions.md). Check with `prlsrvctl info --license --json` and read only `edition` and `status` (the output also
carries a masked licence key; do not paste it into notes).

## Inventory

```bash
timeout 30 prlctl list -a -i -j     # one JSON array: Name, ID, State, Parent VM, GuestTools {state, version}, Hardware {netN: {type, iface, mac, state}}
```

`prlctl list -a -i -j` returned all 22 VMs with full settings in 0.4 s on the lab Mac (observed 2026-11-07), so one call replaces a loop of `prlctl list -i <vm>`. Fields a lab reads: `State`
(`running`, `stopped`, `suspended`, `invalid` for a registered VM whose bundle is gone), `Parent VM` (set on a `prlctl clone --linked` copy; empty on a Vagrant machine, because vagrant-parallels
unregisters the box image after cloning: "Registering VM image from the base box ... Creating new virtual machine as a linked clone of the box image... Unregistering the box VM image",
[vp-issue-522.md] log), `GuestTools.state` (`installed`, `outdated`, `not_installed`), and each adapter's `type` and `state` (`disconnected` when unplugged). `vagrant_lab_inventory.py` reads exactly
this.

Three ways into a guest, by what each needs:

| Path                       | Guest network | Parallels Tools | Runs as                          | Use when                                        |
| -------------------------- | ------------- | --------------- | -------------------------------- | ----------------------------------------------- |
| `vagrant ssh <m> -c '...'` | yes (`eth0`)  | no              | the `vagrant` user, `sudo`       | the normal path                                 |
| `prlctl exec <vm> "..."`   | no            | yes             | root on a Linux guest (observed) | a test cut the network; file uploads over stdin |
| `prlctl capture <vm>`      | no            | no              | nothing runs (a screen PNG)      | nothing else answers                            |

## exec: a command without the network

`prlctl exec <vm> <command>` runs a command inside the VM through Parallels Tools; Linux commands run with `bash -c`; `--current-user` or `--user` picks the account (VERIFIED_PRIMARY, CLI reference
p.19). It needs no guest network, so it reaches a VM whose `eth0` a test has cut, and it runs as root by default on a Linux guest (observed: the worked example's `onvm` runs `systemd-run`, `findmnt`,
writes under `/usr/local` without sudo). Pass the whole command line as one argument and quote it once:

```bash
# smc-resiliency spike/vm/sm/setup_sm.sh @ 2402b961
onvm() { timeout "$1" prlctl exec "$VM" "bash -c $(printf %q "$2")"; }
put() { base64 < "$1" | timeout 60 prlctl exec "$VM" "bash -c 'base64 -d > $2 && chmod $3 $2'"; }   # stdin is passed through
```

Every exec gets its own deadline: an exec into a wedged guest does not return by itself (USER_STATED, lab 2026-11-07: "`prlctl exec` hangs or errors when a guest is wedged").

## exec after a reset

After `prlctl reset` (or a guest-side watchdog reboot) `prlctl exec` fails until Parallels Tools are running again in the new boot, with errors such as `Unable to open new session` and
`PrlJob_GetResult: Invalid argument` (USER_STATED, lab observation 2026-11-07; the messages are not in the CLI reference). Treat them as "not ready yet", not as a failed command: poll with a short
deadline and a bounded number of tries, as the worked example does after every restart:

```bash
timeout 120 prlctl restart "$VM" >/dev/null; for _ in $(seq 1 60); do onvm 20 true 2>/dev/null && break; sleep 5; done
```

If the loop runs out, the guest may not have booted at all: take a console capture before anything else.

## capture: the console when nothing else answers

`prlctl capture <vm> --file <name>` "Captures a screen area of a virtual machine to a file in PNG format" (VERIFIED_PRIMARY, CLI reference p.21). It needs neither the guest network nor Parallels
Tools, so it is the first look at a wedged guest: a kernel panic, an initramfs or emergency shell, a GRUB prompt, a full disk message, or a login prompt that says the guest is up and only Tools are
not. It writes a local file and changes nothing in the VM. Save the PNG with the evidence of the run (redact addresses before it leaves the lab).

## Power: restart, reset, stop

| Command                         | What it does (CLI reference p.20)                            | Use when                       |
| ------------------------------- | ------------------------------------------------------------ | ------------------------------ |
| `prlctl restart <vm>`           | graceful shutdown, then start                                | the guest answers              |
| `prlctl reset <vm>`             | "a 'hard' virtual machine shutdown and then starts it again" | the guest is wedged (captured) |
| `prlctl stop <vm>`              | graceful through Tools, else ACPI                            | normal stop                    |
| `prlctl stop <vm> --kill`       | hard stop                                                    | stop did not finish            |
| `prlctl stop <vm> --drop-state` | discard a suspended state, so the next start is a full boot  | a suspended VM must cold-boot  |

All are writes. A reset loses whatever the guest had not flushed; a lab that measures write behaviour reads its counters before a reset, not after.

## Parallels Tools

Parallels Tools provide exec, graceful shutdown, shared folders and time sync. vagrant-parallels checks the Tools version after boot and warns on a mismatch; `update_guest_tools = true` reinstalls
them on a mismatch (2 to 6 minutes, restarts the VM); `check_guest_tools = false` skips the check (VERIFIED_PRIMARY, [vp-configuration.md]). `outdated` Tools still served exec, capture and shutdown on
every lab VM on 2026-11-07 (observed); update them deliberately, not as a side effect of `vagrant up`, in a lab that compares runs.

## prlsrvctl

`prlsrvctl info` (host, version, licence), `prlsrvctl net list` / `net info <id>` / `net set <id>` with `--type <bridged | host-only | shared>` for the virtual networks (VERIFIED_PRIMARY, CLI
reference p.10 and [parallels-cli-utility.md]). Changing a Parallels network changes every VM on it: a write that needs the operator.

> **Learned 2026-11-07** · prlctl exec · VERIFIED_PRIMARY · Source: smc-resiliency spike/vm/sm/setup_sm.sh (`put`, `verity`), commit a41842e9 · Falsifier: a 10 KB script passed inline to `prlctl exec` that arrives intact
> A long inline argument to `prlctl exec` fails ("Unable to open new session") or arrives cut while short commands work; stream files over stdin instead and check the hash on the guest:
> ```bash
> put() { base64 < "$1" | timeout 60 prlctl exec "$VM" "bash -c 'base64 -d > $2 && chmod $3 $2'"; }
> ```
> After a reset or reboot Parallels Tools take tens of seconds to accept sessions: wait with `until timeout 8 prlctl exec "$VM" true; do sleep 3; done`.

> **Learned 2026-11-08** · Parallels Desktop on macOS, Ubuntu 24.04 arm64 guest · VERIFIED_PRIMARY · Source: smc-resiliency `lab/adapters/transports.py` `PrlctlTransport`, commit 065b9a8f · Falsifier: `prlctl exec <vm> bash -c 'echo a b'` printing `a b` with the command given as separate arguments
> `prlctl exec` joins its arguments into one command line, so `prlctl exec vm bash -c "cmd with words"` passed as separate argv entries runs `bash -c cmd`: the rest became bash's positional arguments
> and a payload ran as an empty shell, silently, exit 0. Pass one quoted string. Tools refuse sessions now and then, most right after a boot (`PrlJob_GetRetCode: Invalid argument`, `PrlJob_GetResult:
> Invalid argument`, exit 255): retry a few times. Files go over stdin (a long command line fails to open a session). A linked clone keeps the source's static hostname and machine-id, so it is told
> apart by its Parallels name only:
>
> ```python
> for _ in range(3):  # Tools refuses a session now and then, most right after a boot
>   rc, out = _call(["prlctl", "exec", self.name, "bash -c " + shlex.quote(cmd)], timeout)  # prlctl joins its arguments into one line
>   if not (rc == 255 and out.lstrip().startswith("Prl")):
>     return rc, out
>   time.sleep(3)
> ```
>
> Also on such a guest, when /etc is a read-only merge: `lvextend` fails with `Cannot archive volume group metadata ... to read-only filesystem` (rc 5) after printing that the size changed; `--config
> 'backup { archive = 0 backup = 0 }'` makes the one change.
````

## File: references/providers-and-choice.md
````markdown
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
````

## File: references/qemu-and-libvirt.md
````markdown
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
````

## File: references/tool-choice-and-lab-symmetry.md
````markdown
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
````

## File: references/upgrade-and-troubleshooting.md
````markdown
---
Title: Upgrade and troubleshooting
Category: reference
Status: current
Authority: >-
  skill-vagrant canonical reference; claims carry evidence labels and cite captures in documents/
Scope: skill-vagrant: local Vagrant and Parallels labs on macOS Apple silicon
Last reviewed: 2026-11-09
Summary: Upgrade order for Parallels Desktop, vagrant-parallels and Vagrant, a symptom-to-cause triage table with sources, and the steps for a wedged guest starting with a console capture.
---

# Upgrade and troubleshooting

Upgrade order for the three moving parts (Parallels Desktop, Vagrant, vagrant-parallels) and a triage table for the failures a lab meets. Captures named `[file]` are in
[documents/research-sources-20261107/](../documents/research-sources-20261107/readme.md).

## Contents

- [Before an upgrade](#before-an-upgrade)
- [Upgrade order](#upgrade-order)
- [Triage table](#triage-table)
- [A wedged guest](#a-wedged-guest)

## Before an upgrade

1. Record versions: `vagrant --version`, `vagrant plugin list`, `prlctl --version`, and the pinned box versions (`just inventory-lab`).
2. Finish or snapshot running stages; a Parallels update can stop or suspend running VMs.
3. Read the release notes of each part for the versions in between: vagrant-parallels has tied fixes to Parallels releases (2.4.4 for Parallels 20.2 shared folders, 2.4.3 for Enterprise licences;
   [vp-changelog-github.md]).
4. Keep the pinned box locally before anything else, while the registry still serves it ([boxes-and-pinning.md](boxes-and-pinning.md#the-box-registry)).

## Upgrade order

```text
 record versions ─► keep the pinned box ─► Parallels Desktop ─► vagrant-parallels ─► Vagrant
   ─► `vagrant up` ONE machine ─► check Tools state, shared folders, `prlctl exec` ─► the rest
```

Parallels Desktop first (it carries the CLI and Tools), then `vagrant plugin update vagrant-parallels`, then Vagrant itself; if plugins fail to load after a Vagrant upgrade, `vagrant plugin repair` is
the command for it (UNVERIFIED: not in the captured docs); the order is a recommendation, UNVERIFIED as a vendor statement. Then: `vagrant up` one machine, check Tools state, shared folders and
`prlctl exec`, and only then the rest. Parallels Tools in existing guests stay at their old version until updated (`update_guest_tools` or the Parallels menu); `outdated` Tools kept working for exec
and shutdown in the lab (observed 2026-11-07).

## Triage table

| Symptom                                                            | Likely cause                               | Check                                         | Source                             |
| ------------------------------------------------------------------ | ------------------------------------------ | --------------------------------------------- | ---------------------------------- |
| "Vagrant has detected that you have an edition of Parallels        | Standard edition, or Enterprise with       | `prlsrvctl info --license --json` (edition    | [vp-issue-485.md]                  |
|   Desktop for Mac installed that is not supported"                 |   vagrant-parallels before 2.4.3           |   only), `vagrant plugin list`                |                                    |
| Two VMs, one IP; `vagrant ssh` reaches the wrong VM                | same `/etc/machine-id` (box regression or  | `cat /etc/machine-id` on                      | [vp-issue-441.md],                 |
|                                                                    |   a clone)                                 |   both; `prlctl list -a -f`                   |   [vp-issue-1562.md]               |
| "Vagrant was unable to mount Parallels Desktop shared folders      | Parallels 20.2 moved to `prl_fsd`; plugin  | `vagrant plugin list`; Tools state            | [vp-issue-483.md]                  |
|   ... prl_fs"                                                      |   before 2.4.4                             |                                               |                                    |
| Shared folder fails on an Ubuntu 26.04 guest                       | AppArmor blocks `prl_fsd`/`fusermount3`    | `journalctl -k -g apparmor` in the guest      | [vp-issue-522.md]                  |
| `fuse: unknown option(s): -o big_writes` on `up` or `reload`       | vagrant-parallels 2.4.9 or earlier on a    | `vagrant plugin list`; update to 2.4.10       | [vp-issue-526.md]                  |
|   (Ubuntu 24.04 and later)                                         |   libfuse3 guest                           |                                               |   (2026-11-09 folder)              |
| Static private IP lands on a new interface (Fedora 36+)            | Vagrant's network configuration for        | `ip addr` in the guest                        | [vp-issue-462.md]                  |
|                                                                    |   that guest                               |                                               |                                    |
| Error with more than four networks on Apple silicon                | Parallels limit on M-series (reported)     | count `vm.network` lines                      | [vp-issue-410.md]                  |
| `prlctl exec`: "Unable to open new session", "PrlJob_GetResult:    | Tools not running yet after a reset        | retry with a deadline; `prlctl capture`       | USER_STATED, lab 2026-11-07        |
|   Invalid argument"                                                |   or reboot                                |                                               |                                    |
| `prlctl exec` hangs                                                | guest wedged (panic, emergency shell,      | `prlctl capture <vm> --file x.png`            | USER_STATED, lab 2026-11-07        |
|                                                                    |   full disk)                               |                                               |                                    |
| `timeout: invalid time interval`                                   | a wrapper wrote `timeout 30"cmd"`          | the wrapper's quoting                         | USER_STATED, lab 2026-11-07        |
|                                                                    |   (one word)                               |                                               |                                    |
| `vagrant global-status` lists a machine that is gone               | it reads a cache                           | `vagrant global-status --prune`               | [vagrant-cli-global-status.md]     |
| A linked clone stopped working after `vagrant box remove`/`prune`  | the clone's disk depends on the box image  | `vagrant box list`; restore the box from a    | [vp-configuration.md]              |
|                                                                    |                                            |   repackaged file                             |                                    |
| A second disk appears on every boot                                | a `customize` adding a device              | `vagrantfile_lint.py`                         | [vp-configuration.md]              |
|                                                                    |   without `post-import`                    |                                               |                                    |
| `vagrant up` waits with "Host unreachable. Retrying..." after a    | macOS Local Network privacy denies the     | System Settings, Privacy & Security, Local    | [vp-issue-510.md] (reporter's      |
|   macOS upgrade (Sequoia 15.5)                                     |   terminal app access to the VM network    |   Network: allow the terminal and editor      |   fix, VERIFIED_SECONDARY)         |
| Files missing or stale after `vagrant upload` of a folder          | upload into an existing directory          | upload to a fresh path per run                | USER_STATED,                       |
|                                                                    |                                            |                                               |   smc-resiliency 2026-11-06        |

## A wedged guest

```text
 prlctl exec / vagrant ssh hangs
   └─ timeout 30 prlctl capture <vm> --file x.png     read-only; needs neither network nor Tools
        ├─ login prompt ................. guest is up; Tools or network are not ─► retry `prlctl exec <vm> true` with a deadline
        ├─ panic / emergency / initramfs / GRUB ... boot failed ─► keep the PNG; then reset or roll back (writes)
        └─ blank ........................ `prlctl status <vm>`: suspended ─► `prlctl start`, or `stop --drop-state`
```

1. `prlctl capture <vm> --file <png>` and look at it: that decides everything else.
2. A login prompt: the guest is up; Tools or the network are not. Wait and retry `prlctl exec <vm> true` with a deadline; check `prlctl list -i` for `GuestTools.state`.
3. A panic, emergency or initramfs shell, a GRUB prompt: the boot itself failed. Record the capture; then `prlctl reset <vm>` (a write) or roll back a snapshot; for a lab under test, the capture is
   the result.
4. A blank console: `prlctl status <vm>`; a suspended VM resumes with `prlctl start`, `prlctl stop --drop-state` discards the state.
````

## File: references/vagrantfile-and-provisioning.md
````markdown
---
Title: Vagrantfile and provisioning
Category: reference
Status: current
Authority: >-
  skill-vagrant canonical reference; claims carry evidence labels and cite captures in documents/
Scope: skill-vagrant: local Vagrant and Parallels labs on macOS Apple silicon
Last reviewed: 2026-11-09
Summary: Vagrantfile load order, multi-machine, the Parallels provider block, customize events (post-import vs every boot), provisioners, triggers, cloud-init, disk size, linting.
---

# Vagrantfile and provisioning

How a Vagrantfile is read, how several machines share one, what the Parallels provider block does and when each provisioner, customize step and trigger runs. Captures named `[file]` are in
[documents/research-sources-20261107/](../documents/research-sources-20261107/readme.md).

## Contents

- [Load order and merging](#load-order-and-merging)
- [Multi-machine](#multi-machine)
- [The Parallels provider block](#the-parallels-provider-block)
- [Customize events: what runs on every boot](#customize-events-what-runs-on-every-boot)
- [Provisioners](#provisioners)
- [Triggers](#triggers)
- [What runs when](#what-runs-when)
- [cloud-init](#cloud-init)
- [Plugins and environment variables](#plugins-and-environment-variables)
- [Lint before up](#lint-before-up)
- [Worked example](#worked-example)

## Load order and merging

Vagrant loads, in order: the Vagrantfile packaged with the box, the one in the Vagrant home (`~/.vagrant.d`), the project's, then multi-machine overrides, then provider-specific overrides; each level
merges into the last. Most settings override; networks are appended; several `Vagrant.configure` blocks in one file merge in order (VERIFIED_PRIMARY, [vagrant-vagrantfile.md]). Consequence: a box's
own Vagrantfile and a stray `~/.vagrant.d/Vagrantfile` can add settings the project file does not show. `VAGRANT_CWD` changes where Vagrant looks for the Vagrantfile and how relative paths in it
expand (VERIFIED_PRIMARY, [vagrant-env-vars.md]); scripts that drive a lab `cd` into the Vagrant directory or set it.

## Multi-machine

`config.vm.define "<name>"` declares a machine; `primary: true` makes it the default for commands given no name (only one may be primary); `autostart: false` keeps it out of a bare `vagrant up`
(VERIFIED_PRIMARY, [vagrant-multi-machine.md]). Settings outside the `define` blocks apply to every machine, and outer provisioners run before inner ones ("outside in", see below). Name the machine in
every scripted command (`vagrant ssh <name> -c ...`), so a second machine added later cannot change which one a script reaches.

## The Parallels provider block

```ruby
smc.vm.provider "parallels" do |p|
  p.name = vagrant_name      # the name in Parallels Desktop and in prlctl; default is <folder>_<timestamp>
  p.memory = 4096            # MiB
  p.cpus = 4
  # p.linked_clone = false   # full clone instead of the default linked clone (new machines only)
  # p.update_guest_tools = true   # reinstall Parallels Tools on a version mismatch (2-6 min, restarts the VM)
  # p.check_guest_tools = false   # skip the Tools version check entirely
end
```

All of these are vagrant-parallels options (VERIFIED_PRIMARY, [vp-configuration.md]). Set `p.name`: without it the VM is named after the folder plus a timestamp, and every `prlctl` command and guard
has to look the name up. When the Parallels provider is installed it has a higher priority than the built-in providers, so `vagrant up` picks it; `--provider=parallels` makes that explicit
(VERIFIED_PRIMARY, [vp-usage.md]).

> **Learned 2026-11-09** · vagrant-parallels 2.4.x, prlctl · VERIFIED_PRIMARY · Source: documents/research-sources-20261109/vp-issue-360.md; documents/research-sources-20261107/vagrant-disks-usage.md, parallels-desktop-v20-command-line-reference.pdf (Virtual hard disk, printed p.30) · Falsifier: a vagrant-parallels release note or doc page that supports `config.vm.disk` or a disk size option
> vagrant-parallels has no disk-size option. Its maintainer said on 2026-08-06 that resizing is "not supported by the plugin nor do we have plans" (issue 360, open since 2020). Vagrant's own
> `config.vm.disk` examples are written for the VirtualBox provider only. On Parallels the disk grows outside the Vagrantfile: with the VM stopped, `prlctl set <vm> --device-set hdd0 --size <MB>` (a
> write; the size is in megabytes), then grow the partition and filesystem in the guest (`growpart`, then `resize2fs`, or `lvextend -r` on LVM). Whether `--size` works on a vagrant-parallels linked
> clone, whose disk sits on the box's snapshot, is UNVERIFIED: try it on a scratch machine first. A full clone (`linked_clone = false`) avoids that question.

## Customize events: what runs on every boot

`p.customize [...]` runs a `prlctl` command (`:id` is replaced by the VM's ID) at an event (VERIFIED_PRIMARY, [vp-configuration.md]):

| Event         | When                                                   |
| ------------- | ------------------------------------------------------ |
| `post-import` | once, just after the VM is cloned from the base box    |
| `pre-boot`    | before every boot (the default when no event is given) |
| `post-boot`   | after boot, before the communicator connects           |
| `post-comm`   | after the communicator connects                        |

A `customize` without an event runs on **every** `vagrant up` and `vagrant reload`. That is right for idempotent settings (`--memsize`) and wrong for anything that adds something (`--device-add hdd`
adds another disk each boot). Put additions under `"post-import"`, or add them once with `prlctl` when the stage that needs them starts. The worked example records this decision in its header: "A
second virtual disk for the identity partition (S6) is added when S6 starts, not here: provider customize runs on every boot." `vagrantfile_lint.py` warns on a `--device-add` customize without
`post-import`.

## Provisioners

- Provisioners run on the first `vagrant up`, on `vagrant provision`, and on `vagrant reload --provision`; `run: "always"` runs one on every up and reload, `run: "never"` only when named with
  `--provision-with` (VERIFIED_PRIMARY, [vagrant-provisioning-basic.md]).
- Order is "outside in": provisioners outside a `define` run before those inside it, whatever their position in the file; `preserve_order: true` keeps file order when overriding (VERIFIED_PRIMARY,
  [vagrant-provisioning-basic.md]).
- The shell provisioner takes `inline` or `path`, `args`, `env` (`sensitive: true` hides its values from output), `privileged` (sudo, default true), `reboot`, `reset` and `upload_path`
  (VERIFIED_PRIMARY, [vagrant-provisioner-shell.md]).
- The file provisioner uploads as the SSH user, not root: upload to `/tmp` and move with a shell step (VERIFIED_PRIMARY, [vagrant-provisioner-file.md]).
- Write every provisioner to be idempotent (`grep -q ... || echo ... >>`, `dpkg-query -W` before `apt-get install`), so `vagrant provision` is a safe re-run, and print a short report at the end so the
  provision log is evidence.
- Pin what the provisioner installs when the lab must be reproducible: an exact `apt-get install pkg=version`, a pinned pip version, or an apt snapshot date ([tool-choice-and-lab-symmetry.md](tool-choice-and-lab-symmetry.md#pin-the-archive-not-only-the-box)).

## Triggers

`config.trigger.before` / `.after` run a host command (`run`) or a guest command (`run_remote`) or Ruby (`ruby`) around an action, a command or a hook (`type` `:action`, `:command`, `:hook`);
`only_on` limits to named machines; `on_error`, `exit_codes`, `abort`, `warn`, `info` shape failure handling (VERIFIED_PRIMARY, [vagrant-triggers-configuration.md], [vagrant-triggers-usage.md]). Use a
trigger for host-side bookkeeping a lab needs on every `up` or `destroy` (record the box version, refuse to destroy a machine holding unsaved results). Keep it short and deadline-bound: a hanging
trigger hangs `vagrant up`.

## What runs when

One `vagrant up` of a new machine, in order (event names from [vp-configuration.md]; the last three steps in the order `vagrant up` prints them):

```text
 import box ─► linked clone ─► customize post-import ─► customize pre-boot ─► boot
   ─► customize post-boot ─► wait for SSH ─► customize post-comm
   ─► hostname, network interfaces ─► synced folders ─► provisioners (outside in) ─► after-triggers
```

| Step                                   | first `up`                              | later `up` (halted VM) | `reload` | `reload --provision` | `provision` |
| -------------------------------------- | --------------------------------------- | ---------------------- | -------- | -------------------- | ----------- |
| `customize` at `post-import`           | yes                                     | no                     | no       | no                   | no          |
| `customize` with no event (`pre-boot`) | yes                                     | yes                    | yes      | yes                  | no          |
| `customize` at `post-boot`/`post-comm` | yes                                     | yes                    | yes      | yes                  | no          |
| provisioner (default: once)            | yes                                     | no                     | no       | yes                  | yes         |
| provisioner `run: "always"`            | yes                                     | yes                    | yes      | yes                  | yes         |
| provisioner `run: "never"`             | only when named with `--provision-with` |                        |          |                      |             |

A `vagrant up` of a machine that is already running boots nothing and runs none of these.

## cloud-init

`config.vm.cloud_init` attaches user data (`text/cloud-config`, `text/x-shellscript` and the other listed content types; the only `type` is `:user_data`) from a `path` or `inline` (VERIFIED_PRIMARY,
[vagrant-cloud-init-configuration.md], [vagrant-cloud-init-usage.md]). HashiCorp's examples use the VirtualBox provider; whether vagrant-parallels 2.4.9 delivers cloud-init data is UNVERIFIED (no
statement in its docs; bento issue 1655 reports "cloud init not working" on a bento box, [vp-issue-1655.md]). For Parallels labs, shell provisioners are the proven path.

## Plugins and environment variables

`vagrant plugin install <name>`, `vagrant plugin list`, `vagrant plugin update`; third-party plugins "can introduce instabilities" (VERIFIED_PRIMARY, [vagrant-plugins-usage.md]). Useful environment
variables (VERIFIED_PRIMARY, [vagrant-env-vars.md]): `VAGRANT_CWD`, `VAGRANT_HOME` (boxes live here, default `~/.vagrant.d`; it gets large), `VAGRANT_DEFAULT_PROVIDER`,
`VAGRANT_BOX_UPDATE_CHECK_DISABLE`, `VAGRANT_CHECKPOINT_DISABLE` (no version check calls home), `VAGRANT_DOTFILE_PATH`, `VAGRANT_LOG`. `VAGRANT_EXPERIMENTAL` enables named experimental features;
Vagrant does not validate the names (VERIFIED_PRIMARY, [vagrant-experimental.md]).

## Lint before up

`just lint-vagrantfile <path>` (`scripts/vagrantfile_lint.py`) checks the rules above without running Vagrant: every box has an exact `box_version`, a provider block is set, every machine in a
multi-machine file has a provider `name`, `--device-add` customizes run at `post-import`, and no credential, token or private key is written in the file. It reads the file as text; it does not
evaluate Ruby, so a value computed at run time is reported as unknown, never as passing.

## Worked example

smc-resiliency's Pi spike lab (canonical `vagrant_stuff/smc-pi-spike01/Vagrantfile` @ 8591b72; project copy @ 4e436e8d): one primary machine, three `autostart: false` helpers, provisioning as heredoc
shell scripts with a report at the end, each machine named for Parallels:

```ruby
config.vm.define vagrant_name, primary: true do |smc|
  smc.vm.hostname = vagrant_name
  smc.vm.network "private_network", ip: "<lab address>", auto_config: false   # eth1: the site trunk, configured by the image under test
  smc.vm.provision "shell", inline: $BASE
  smc.vm.provision "shell", inline: $S2
  smc.vm.provider "parallels" do |p|
    p.name = vagrant_name
    p.memory = 4096
    p.cpus = 4
  end
end
config.vm.define client_name, autostart: false do |client|
```
````

## File: references/virtualbox.md
````markdown
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
Infrastructure integration, PXE ROM"). Whether its use here is personal or business is the operator's call, not this pack's; a lab that needs neither feature can run without it. This is a summary of
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
````

## File: scripts/check_governance.py
````python
#!/usr/bin/env python3
"""Governance coherence checks for skill-vagrant.

Run: just check (or just test, which runs it). Safety: read-only; it reads this pack's files and writes nothing.

Turns this project's governance CLAIMS into assertions that fail. Stdlib only, so the gate never fails for environment reasons; exit 1 on any failure so it can gate the task runner.

Generated by skill-ai-it from templates/check_governance.py. Doctrine, check families, and the inference table live in the skill's patterns/governance-checks.md — read that before adding,
changing, or retiring a check.

Structure:
  CONFIG      — registries the agent tunes per project. Everything below CONFIG is generic.
  Tier 1      — universal checks. Present in every project.
  Tier 2      — conditional checks. Kept only when their trigger artifact exists.
  Tier 3      — project-specific invariants. Authored per project; each cites the rule it enforces.

Growth rule: this file is expected to grow with the project. A new class of artifact needs a coverage check; a new duplicated constant needs a registry entry. When a check fails, fix the
project, not the check.

Checks:
  1. Referenced paths in the governance surfaces resolve on disk (relative to the referencing file, then to the repo root).
  2. Index links resolve, and every indexed folder member is linked.
  3. Count claims in prose match reality (historical facts exempt).
  4. Cataloged items exist and existing items are cataloged.
  5. Task-runner recipes named in prose exist in the runner.
  5b. No recipe reaches an interpreter implicitly — neither a bare `python3`/`node` nor `mise exec -- python`.
  6. Derived artifacts are not older than their inputs.
  7. Every surface restating a registered constant states it identically, and nothing unregistered restates it.
  8. Every row of an append-only table stamps its pass, and no pass records the same entity twice.
  9. Every dated evidence capture states its URL, retrieval date and HTTP status, or names the capture that corrects it.
"""

from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
# Repo-relative path to this file. Used to exclude the checker from the constant scan: it necessarily contains every
# registered constant's PATTERN, and comparing `rel` against a bare `Path(__file__).name` never matched, so the checker
# reported each of its own pattern definitions as an unregistered restatement.
SELF = Path(__file__).resolve().relative_to(ROOT).as_posix()

# --------------------------------------------------------------------------------------------------------------- CONFIG
# Tune these registries to the project. Leave a registry empty and its check contributes zero assertions rather than
# failing — coverage is measured by the assertion count, so an empty registry reads honestly as "not covered yet".

# Governance surfaces whose path references must resolve.
SURFACES: tuple[str, ...] = (
    "README.md",
    "AGENTS.md",
    "AI_NAVIGATION.md",
    "SKILL.md",
    "SCRATCHPAD.md",
    "CHANGELOG.md",
    "scripts/README.md",
)

# Index file -> (folder it indexes, glob). Enforces BOTH directions: links resolve, and members are linked.
CATALOGS: dict[str, tuple[str, str]] = {
    # SKILL.md is the activation surface and must route every reference; the contract test checks only its REQUIRED list,
    # so a NEW reference file is caught here until it is routed.
    "SKILL.md": ("references", "*.md"),
    # The pack-domain routing table in AI_NAVIGATION.md mirrors SKILL.md for agents that enter through the router.
    "AI_NAVIGATION.md": ("references", "*.md"),
    "scripts/README.md": ("scripts", "*.py"),
    # Every promoted Archcore document must be indexed; an unindexed one is invisible to the next promote/refresh.
    ".archcore/index.guide.md": (".archcore", "*/*.md"),
    # Every verbatim research capture is indexed (with its sha256, checked by the contract test).
    "documents/research-sources-20261107/readme.md": ("documents/research-sources-20261107", "*"),
}

# Files a catalog may legitimately omit (the index itself, generated output, dotfiles).
CATALOG_EXEMPT: frozenset[str] = frozenset({"README.md", "__init__.py"})

# Countable noun -> (folder, glob). A prose claim like "26 documents" is checked against the real count. Choose the glob
# deliberately: "*.md" counts the folder's own index too, which is usually not what the prose means — prefer "[0-9]*.md"
# or a similar shape when the index is excluded from the claim.
COUNT_CLAIMS: dict[str, tuple[str, str]] = {
    # "documents": ("docs", "*.md"),
    # "scripts": ("scripts", "*.py"),
}

# Lines carrying this marker state a historical fact, not a live claim, and are exempt from count checking.
ASAT_MARKER = "count:asat"

# Lines carrying this marker show an ILLUSTRATIVE filename — a naming-convention example — not a reference to a file
# that must exist. Same shape as ASAT_MARKER: explicit, per line, and visible in the document itself rather than
# hidden in an ignore-list here.
EXAMPLE_MARKER = "path:example"

# Paths a governance surface references CONDITIONALLY ("when present"). The generic skill-ai-it navigation block names
# several; each is a real artifact in SOME governed project, so its absence here is a fact about this project's
# toolchain rather than a broken reference. Registered with a per-entry reason rather than silently ignore-listed, so
# the exemption stays reviewable — remove an entry the day the artifact appears. Tune per project.
CONDITIONAL_PATHS: frozenset[str] = frozenset({
    "graphify-out/GRAPH_REPORT.md",  # Graphify disabled, graphify-out/ deleted (operator, 2026-10-10); still named by the navigation block or history
    "graphify-out/graph.json",  # Graphify disabled, graphify-out/ deleted (operator, 2026-10-10); still named by the navigation block or history
    # Named by the generic skill-ai-it navigation block; this pack does not have them.
    "docs/history",                     # created by `just rotate --apply` the first time a record passes its budget; named by the navigation block
    "docs/trackers",                    # named by the skill-ai-it compact navigation block; this pack keeps open items in SCRATCHPAD.md
    "Taskfile.yml",                     # this pack uses just
    "Makefile",
    "package.json",                     # no Node toolchain
    "ARCHITECTURE.md",                  # a guidance pack; SKILL.md + references/ carry the design
    "architecture.md",
    "ROADMAP.md",                       # open items live in SCRATCHPAD.md
    "roadmap.md",
    "memory-bank/activeContext.md",     # this pack uses SCRATCHPAD.md, not a memory-bank
    "memory-bank/progress.md",
    "memory-bank/decisionLog.md",
    ".archcore/specs",                  # never promoted, by decision: see .archcore/index.guide.md "Never promoted"
    ".archcore/guides",
    "ARCHCORE_PROMOTION_CANDIDATES.md", # transient promotion queue; named by the generic managed blocks, never created here
    ".ai-context/repo-pack.md",         # never generated here; only governance-pack.md is (`just context-pack`)
})

# Pack folders a BARE filename (`data-model.md`, `nautobot_paging.py`) is resolved against. The pack's own prose names its
# references and helpers without the folder prefix; the name must still exist in one of these, so a rename is still caught.
NAME_ROOTS: tuple[str, ...] = ("references", "scripts", "tests", "documents")

# Task runner file, or None if the project has none.
TASK_RUNNER: str | None = "justfile"

# Files whose prose names task-runner recipes.
RUNNER_REFERENCES: tuple[str, ...] = ("README.md", "AGENTS.md", "AI_NAVIGATION.md", "scripts/README.md")

# Recipes that BUILD the venv from the mise pin — e.g. "bootstrap" in templates/justfile. {{py}} cannot exist yet when
# these run, so their own `mise exec -- python -m venv .venv` line is the one legitimate implicit-interpreter call, not
# a violation of the rule it otherwise enforces. Leave empty if the project has no such recipe.
VENV_BUILDER_RECIPES: frozenset[str] = frozenset({"bootstrap"})

# Generated artifact -> inputs it must not be older than.
DERIVED: dict[str, tuple[str, ...]] = {
    # "docs/CLASS-PROFILES.md": ("scripts/class_profiles.py", "process/vehicle-classes.yaml"),
}

# Facts deliberately restated across surfaces. Each entry: the regex that recognises a statement of the fact, and every
# file allowed to state it. Drift fails; so does an UNREGISTERED file stating it — that is what makes this self-extending.
# Pair each entry with a spec document explaining why the duplication is intentional.
CONSTANT_SURFACES: dict[str, dict[str, object]] = {
    # "profit-gate": {
    #     "pattern": r"\$2,500",
    #     "surfaces": ("AGENTS.md", "docs/07-DECISIONS.md"),
    #     "owner": ".archcore/rules/purchase-discipline.rule.md",
    # },
}

# Append-only tables and the columns that give them their grain: (entity column, pass column). An append-only table
# records a re-measurement by ADDING a row, which is right and useless on its own — without a column that orders the
# passes there is no way to compute which row is current, and every aggregate over the table double-counts whatever was
# re-measured. Found in a governed project on 2026-08-28 with twelve rows standing for eight entities, the supersession
# recorded only in a prose note. Register the table here and the grain becomes an assertion instead of an intention.
APPEND_ONLY_TABLES: dict[str, tuple[str, str]] = {
    # "data/sku-scores.csv": ("sku_id", "scored_at"),
}

# Folder of dated evidence captures, or None if the project keeps none. A capture asserts what a source said on a date.
EVIDENCE_DIR: str | None = None  # e.g. "trackers/source-captures"

# The index file inside EVIDENCE_DIR, exempt from the provenance header because it is a catalog, not a capture.
EVIDENCE_INDEX = "README.md"

# Header fields that make a capture re-openable by someone who was not there: where it came from, when, and whether the
# fetch actually succeeded. A capture naming no URL and no HTTP status is a recollection in a capture's clothing — in
# the project this was promoted from, exactly that produced a VERIFIED cost row whose only recorded fetch returned 403.
EVIDENCE_PROVENANCE_FIELDS: tuple[str, ...] = ("Canonical URL", "Retrieved", "HTTP status")

# Captures taken before the provenance rule existed. Each MUST name the later capture supplying the missing provenance —
# this is a correction record, not an exemption. Where captures are immutable the only way to clear an entry is to take
# the correcting capture, which is the behaviour the rule wants. Removing an entry whose correction does not exist turns
# the check red rather than quiet, so the list cannot be emptied by deletion.
EVIDENCE_PROVENANCE_CORRECTED: dict[str, str] = {
    # "uae-wholesale-moq-discounts-20260828.md": "wholesale-house-price-provenance-20260828.md",
}

# Extensions scanned when hunting for unregistered restatements of a constant.
SCAN_SUFFIXES: frozenset[str] = frozenset({".md", ".py", ".yaml", ".yml"})

# Path-token discrimination. Prose is full of tokens that look like paths and are not; tune until the check is quiet.
PATHLIKE = re.compile(r"^[A-Za-z0-9._/-]+$")
REPO_SUFFIXES: frozenset[str] = frozenset({".md", ".py", ".json", ".yaml", ".yml", ".toml", ".sh", ".txt"})
IGNORE_PREFIXES: tuple[str, ...] = ("http://", "https://", "mailto:", "~/", "/")
IGNORE_EXACT: frozenset[str] = frozenset({"README.md", "AGENTS.md", "CLAUDE.md", "SCRATCHPAD.md", "CHANGELOG.md"})

# --------------------------------------------------------------------------------------------------------------- HARNESS

failures: list[str] = []
checks_run = 0


def fail(check: str, detail: str) -> None:
    failures.append(f"{check}: {detail}")


def counted() -> None:
    """Record one assertion actually evaluated. Never call this per function — only per real comparison."""
    global checks_run
    checks_run += 1


def read(rel: str) -> str | None:
    path = ROOT / rel
    return path.read_text(encoding="utf-8") if path.is_file() else None


def without_code(text: str) -> str:
    """Strip fenced code blocks. Their contents are examples, not claims about this repo."""
    return re.sub(r"```.*?```", "", text, flags=re.DOTALL)


def table_rows(rel: str) -> list[dict[str, str]]:
    """Read a CSV as dicts, or an empty list when it does not exist — an absent table contributes zero assertions."""
    path = ROOT / rel
    if not path.is_file():
        return []
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def members(folder: str, glob: str) -> list[Path]:
    base = ROOT / folder
    if not base.is_dir():
        return []
    return sorted(p for p in base.glob(glob) if p.is_file() and not p.name.startswith("."))


# --------------------------------------------------------------------------------------------------------------- TIER 1


def check_referenced_paths() -> None:
    """Every repo-relative path named in a governance surface resolves on disk."""
    for surface in SURFACES:
        text = read(surface)
        if text is None:
            fail("surface", f"{surface} is listed as a governance surface but does not exist")
            counted()
            continue
        body = "\n".join(l for l in without_code(text).splitlines() if EXAMPLE_MARKER not in l)
        tokens = set(re.findall(r"`([^`\n]+)`", body))
        tokens |= {m.group(1) for m in re.finditer(r"\]\(([^)\s]+)\)", body)}
        for raw in sorted(tokens):
            tok = raw.split("#", 1)[0].strip().rstrip("/")
            if not tok or tok in IGNORE_EXACT or tok in CONDITIONAL_PATHS or tok.startswith(IGNORE_PREFIXES):
                continue
            if not PATHLIKE.match(tok):
                continue
            suffix = Path(tok).suffix
            if "/" not in tok and suffix not in REPO_SUFFIXES:
                continue
            if suffix and suffix not in REPO_SUFFIXES:
                continue
            counted()
            # Resolve relative to the file that MAKES the reference first, then relative to ROOT. Resolving only
            # against ROOT false-fails every correct relative link written inside a subfolder README.
            near = (ROOT / surface).parent / tok
            bare = "/" not in tok and any((ROOT / folder / tok).exists() for folder in NAME_ROOTS)
            if not near.exists() and not (ROOT / tok).exists() and not bare:
                fail("path", f"{surface} references `{tok}` which does not exist")


def check_index_links() -> None:
    """Links inside an index file resolve, relative to the index's own folder."""
    for index in CATALOGS:
        text = read(index)
        if text is None:
            fail("index", f"catalog {index} does not exist")
            counted()
            continue
        base = (ROOT / index).parent
        for target in {m.group(1) for m in re.finditer(r"\]\(([^)\s]+)\)", without_code(text))}:
            tok = target.split("#", 1)[0].strip()
            if not tok or tok.startswith(IGNORE_PREFIXES):
                continue
            counted()
            if not (base / tok).exists():
                fail("index", f"{index} links `{tok}` which does not exist")


def check_count_claims() -> None:
    """Prose stating a quantity matches the real count. Lines marked as historical facts are exempt."""
    for noun, (folder, glob) in COUNT_CLAIMS.items():
        actual = len(members(folder, glob))
        pattern = re.compile(rf"(\d+)\s+{re.escape(noun)}\b", re.IGNORECASE)
        for surface in SURFACES:
            text = read(surface)
            if text is None:
                continue
            for line in without_code(text).splitlines():
                if ASAT_MARKER in line:
                    continue
                for claim in pattern.finditer(line):
                    counted()
                    if int(claim.group(1)) != actual:
                        fail("count", f"{surface} claims {claim.group(1)} {noun}; {folder}/{glob} holds {actual}")


def check_catalog_coverage() -> None:
    """Both directions: the catalog names nothing missing, and nothing present is uncataloged.

    The second direction is the one that grows silently, and it is what makes this checker self-extending — a new file
    turns the build red until it is registered somewhere.
    """
    for index, (folder, glob) in CATALOGS.items():
        text = read(index)
        if text is None:
            continue
        body = without_code(text)
        for item in members(folder, glob):
            if item.name in CATALOG_EXEMPT or (ROOT / index).resolve() == item.resolve():
                continue
            counted()
            if item.name not in body:
                fail("coverage", f"{folder}/{item.name} exists but is not cataloged in {index}")


# --------------------------------------------------------------------------------------------------------------- TIER 2
# Keep a check below only while its trigger artifact exists. Delete the rest rather than leaving inert scaffolding.


def check_task_recipes() -> None:
    """Recipes named in prose exist in the task runner, and every cataloged script has a way to be run."""
    if TASK_RUNNER is None:
        return
    runner = read(TASK_RUNNER)
    if runner is None:
        fail("runner", f"{TASK_RUNNER} is configured but does not exist")
        counted()
        return
    recipes = {m.group(1) for m in re.finditer(r"^([a-zA-Z][\w-]*)\s*(?:[*+a-zA-Z_].*)?:(?!=)", runner, re.MULTILINE)}
    for surface in RUNNER_REFERENCES:
        text = read(surface)
        if text is None:
            continue
        for named in {m.group(1) for m in re.finditer(r"`just ([a-zA-Z][\w-]*)", without_code(text))}:
            counted()
            if named not in recipes:
                fail("runner", f"{surface} names recipe `{named}` which {TASK_RUNNER} does not define")


def check_interpreter_pinning() -> None:
    """No task recipe reaches an interpreter implicitly.

    Two defects, one root cause — the recipe does not say which interpreter it means:

    1. A BARE `python3`/`node`/`npx`/`ruby` resolves to whatever is on PATH, not to what .mise.toml pins.
    2. `mise exec -- python` resolves to the venv only while `_.python.venv` activation applies. It tests clean, reads
       as pinned, and degrades SILENTLY to the host interpreter when that activation stops holding.

    Both are the "it works on the machine it was written on" class. Recipes must address {{py}} by path and depend on
    _require-venv. Node has no venv layer, so `mise exec -- node` is the legitimate explicit form for it and is allowed.

    Exception: VENV_BUILDER_RECIPES (e.g. "bootstrap") create the venv from the mise pin, so {{py}} cannot exist yet
    when they run — their own `mise exec -- python -m venv .venv` line is the one legitimate implicit call, not a
    violation of the rule it otherwise enforces. Found missing during unified-network-controller's bootstrap
    (2026-09-18): the template's own `bootstrap` recipe failed the check it ships with, because nothing tracked which
    recipe a line belongs to. `cambium-swap` had already patched this locally; ported back here so every project
    generated from this template gets it, instead of each one rediscovering and re-fixing it independently.

    Rule: the runtime-isolation section of skill-ai-it's SKILL.md, and the RUNTIME PINNING header of templates/justfile.
    """
    if TASK_RUNNER is None:
        return
    runner = read(TASK_RUNNER)
    if runner is None:
        return
    recipe: str | None = None
    for lineno, line in enumerate(runner.splitlines(), 1):
        header = re.match(r"^([a-zA-Z_][\w-]*)\s*(?:[*+a-zA-Z_][^:]*)?:(?!=)", line)
        if header:
            recipe = header.group(1)
            continue
        if not line.startswith((" ", "\t")):
            continue  # only recipe bodies are commands; headers and variable assignments are not
        stripped = line.strip()
        if stripped.startswith("#"):
            continue
        # Blank out quoted literals, keeping offsets intact: an interpreter NAME inside a string is a label being
        # printed (`printf 'python  '`), not a command being run.
        scan = re.sub(r"'[^']*'|\"[^\"]*\"", lambda m: " " * len(m.group(0)), stripped)
        counted()
        if re.search(r"mise\s+exec\b[^|;]*--\s+python", scan) and recipe not in VENV_BUILDER_RECIPES:
            fail(
                "runtime",
                f"{TASK_RUNNER}:{lineno} reaches Python through an implicit `mise exec -- python` — address the venv "
                f"interpreter by path via {{{{py}}}} and guard it with _require-venv",
            )
        for match in re.finditer(r"(?<![-\w/])(python3?|npx|ruby|node)\b", scan):
            # `mise exec -- <interp>` is handled above for python; for the rest it is the sanctioned explicit form.
            if re.search(r"mise\s+(exec\b[^|;]*--|run)\s*$", scan[: match.start()]):
                continue
            fail(
                "runtime",
                f"{TASK_RUNNER}:{lineno} calls bare `{match.group(1)}` — route it through the pinned interpreter",
            )


# --------------------------------------------------------------------------------------------------------------- TIER 3
# Project-specific invariants. Each check states, in its docstring, the project rule it enforces and where that rule
# lives. A check whose justification cannot be found is a check the next agent deletes.


def check_derived_freshness() -> None:
    """Generated artifacts are not older than the sources they are generated from.

    Freshness only — it proves a rebuild happened, not that the rebuild used the right source. Where the generator can
    stamp its source into the output, add a provenance check alongside this one; see patterns/governance-checks.md.
    """
    for output, inputs in DERIVED.items():
        out = ROOT / output
        if not out.is_file():
            fail("derived", f"{output} is registered as generated but does not exist")
            counted()
            continue
        for src in inputs:
            source = ROOT / src
            counted()
            if not source.is_file():
                fail("derived", f"{output} declares input `{src}` which does not exist")
            elif out.stat().st_mtime < source.stat().st_mtime:
                fail("derived", f"{output} is older than its input `{src}` — regenerate it")


def check_constant_sync() -> None:
    """Facts restated across surfaces stay identical, and no unregistered file restates them.

    Duplication here is deliberate: the operator must read the value at the point of decision without following a
    pointer. So the duplication stays and the sync is enforced. Orphan detection is the half that makes it self-extending.
    """
    for name, entry in CONSTANT_SURFACES.items():
        pattern = re.compile(str(entry["pattern"]))
        registered = {str(s) for s in tuple(entry["surfaces"])}  # surfaces is a tuple of paths
        owner = str(entry.get("owner", ""))

        for surface in sorted(registered):
            text = read(surface)
            counted()
            if text is None:
                fail("constant", f"{name}: registered surface {surface} does not exist")
            elif not pattern.search(without_code(text)):
                fail("constant", f"{name}: {surface} is registered but no longer states it (owner: {owner or 'unset'})")

        for path in sorted(ROOT.rglob("*")):
            if not path.is_file() or path.suffix not in SCAN_SUFFIXES:
                continue
            rel = path.relative_to(ROOT).as_posix()
            if rel in registered or rel.startswith(".") or "/." in rel or rel == SELF:
                continue
            counted()
            if pattern.search(without_code(path.read_text(encoding="utf-8", errors="ignore"))):
                fail("constant", f"{name}: {rel} states it but is not registered in CONSTANT_SURFACES")


def check_append_only_grain() -> None:
    """Every row of an append-only table stamps its pass, and no pass records the same entity twice.

    Registered in APPEND_ONLY_TABLES. Two distinct failures, both silent: a row with an EMPTY pass column cannot be
    ordered against any other row, so nothing can say which measurement is current; and a REPEATED (entity, pass) pair
    means one pass measured one entity twice, so every count and every aggregate over the table is wrong by however
    many rows were duplicated. Neither shows up as an error — the table still parses and the report still renders.

    A re-measurement is a NEW pass. Reusing the previous pass identifier to record one is the defect this catches.
    """
    for rel, (entity_col, pass_col) in APPEND_ONLY_TABLES.items():
        rows = table_rows(rel)
        if not rows:
            counted()
            if not (ROOT / rel).is_file():
                fail("append-only-grain", f"{rel} is registered as append-only but does not exist")
            continue
        seen: dict[tuple[str, str], int] = {}
        for i, row in enumerate(rows, start=2):  # line 1 is the header
            counted()
            if entity_col not in row or pass_col not in row:
                fail("append-only-grain",
                     f"{rel} has no {entity_col!r}/{pass_col!r} column; the registered grain does not match the table")
                break
            pass_id = (row.get(pass_col) or "").strip()
            if not pass_id:
                fail("append-only-grain", f"{rel} line {i} has empty {pass_col}; the pass is the grain")
                continue
            key = ((row.get(entity_col) or "").strip(), pass_id)
            if key in seen:
                fail("append-only-grain",
                     f"{rel} line {i} repeats {entity_col} {key[0]!r} for pass {pass_id} (first seen line {seen[key]}); "
                     f"a re-measurement is a NEW pass, so give it a new {pass_col}")
            else:
                seen[key] = i


def check_evidence_provenance() -> None:
    """Every markdown capture states where it came from, when, and whether the fetch succeeded.

    Enforces the global source-discipline policy (~/.agents/AGENTS.md, 'Citations travel into the documentation'): a
    VERIFIED figure means a capture exists that someone else can re-open. Presence of a capture FILE is not that —
    a file with no URL and no HTTP status proves only that somebody wrote something down.

    A capture missing the header is accepted ONLY while it names its correcting capture in
    EVIDENCE_PROVENANCE_CORRECTED and that capture is on disk.
    """
    if EVIDENCE_DIR is None:
        return
    for item in members(EVIDENCE_DIR, "*.md"):
        if item.name == EVIDENCE_INDEX:
            continue
        counted()
        text = read(f"{EVIDENCE_DIR}/{item.name}") or ""
        missing = [f for f in EVIDENCE_PROVENANCE_FIELDS if f"**{f}**" not in text]
        if not missing:
            continue
        corrector = EVIDENCE_PROVENANCE_CORRECTED.get(item.name)
        if corrector is None:
            fail("evidence-provenance",
                 f"{EVIDENCE_DIR}/{item.name} states no {', '.join(missing)}; a capture nobody can re-open is not evidence")
        elif not (ROOT / EVIDENCE_DIR / corrector).is_file():
            fail("evidence-provenance",
                 f"{EVIDENCE_DIR}/{item.name} defers its provenance to {corrector}, which does not exist")


# --------------------------------------------------------------------------------------------------------------- MAIN

CHECKS = (
    check_referenced_paths,
    check_index_links,
    check_count_claims,
    check_catalog_coverage,
    check_task_recipes,
    check_interpreter_pinning,
    check_derived_freshness,
    check_constant_sync,
    check_append_only_grain,
    check_evidence_provenance,
)


def main() -> int:
    for check in CHECKS:
        check()

    # The same defect can be reported by more than one matching pattern; a doubled count erodes trust in the number.
    unique = sorted(set(failures))
    if unique:
        print(f"FAIL — {len(unique)} issue(s) across {checks_run} checks\n")
        for f in unique:
            print(f"  ✗ {f}")
        return 1

    print(f"OK — {checks_run} governance checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
````

## File: scripts/doc-freshness-baseline.json
````json
{
 "no-header:.ai-context/governance-pack.md": "2026-11-09",
 "no-header:references/boxes-and-pinning.md": "2026-11-09",
 "no-header:references/clones-snapshots-and-identity.md": "2026-11-09",
 "no-header:references/evolution-and-write-back.md": "2026-11-09",
 "no-header:references/lab-safety-and-guards.md": "2026-11-09",
 "no-header:references/licensing-and-editions.md": "2026-11-09",
 "no-header:references/networking-and-synced-folders.md": "2026-11-09",
 "no-header:references/operations-cookbook.md": "2026-11-09",
 "no-header:references/parallels-prlctl.md": "2026-11-09",
 "no-header:references/tool-choice-and-lab-symmetry.md": "2026-11-09",
 "no-header:references/upgrade-and-troubleshooting.md": "2026-11-09",
 "no-header:references/vagrantfile-and-provisioning.md": "2026-11-09",
 "no-header:tests/eval-procedure.md": "2026-11-09",
 "no-header:tests/scenarios.md": "2026-11-09",
 "over-budget:AI_NAVIGATION.md": "lines=154 bytes=10079 AI_NAVIGATION.md: over its budget of 150 lines, 12 KB",
 "review-due:.archcore/adr/independent-platform-pack.adr.md": "2026-11-09",
 "review-due:.archcore/plans/keep-the-pinned-box-before-registry-eol.plan.md": "2026-11-09",
 "review-due:.archcore/rules/lab-writes-stay-in-the-project.rule.md": "2026-11-09",
 "review-due:.archcore/rules/memory-channel-name.rule.md": "2026-11-09"
}
````

## File: scripts/README.md
````markdown
# Script Inventory — skill-vagrant

Runnable helpers, task-runner recipes and the governance checker in this pack. Helpers in `scripts/` are tested, stdlib-only, read-only and written from a real engagement (the smc-resiliency lab,
2026-11-07); the package contract fails any helper without a test in `tests/test_helpers.py`.

## Contents

- [Runtimes — read this before running anything directly](#runtimes--read-this-before-running-anything-directly)
- [Execution Policy](#execution-policy)
- [Preferred Execution Order](#preferred-execution-order)
- [Maintenance Rules](#maintenance-rules)
- [Task Inventory](#task-inventory)
- [Raw Script Inventory](#raw-script-inventory)
- [Safety Labels](#safety-labels)
- [Notes](#notes)

---

## Runtimes — read this before running anything directly

Recipes do **not** use the host's `python3`. This pack calls no JS tool, so Node is not pinned.

| Runtime | Resolved by                                                              | Actual                             |
| ------- | ------------------------------------------------------------------------ | ---------------------------------- |
| Python  | `.venv` in the working-cache peer, built from the pin in `../.mise.toml` | `/Volumes/Data/_ai/_skills/skills-working-cache/skill-vagrant/.venv/bin/python` |

`just runtimes` prints what the recipes will actually use. `just bootstrap` rebuilds the venv; it is safe to re-run.

The venv lives in the working-cache peer, never in this repo — the repo carries source, not rebuildable runtime. Every Python recipe depends on `_require-venv`, which fails with a rebuild instruction
rather than silently falling back to the host interpreter. The one sanctioned exception is `just bootstrap` itself, which creates the venv from the mise pin.

**Do not invoke these scripts with a bare `python3`.** It resolves to whatever the host has on `PATH`, which works until the host changes and then fails in a way that reads like a code bug.

<!-- BEGIN MANAGED: skill-ai-it:scripts -->
<!-- skill-ai-it-version: 2026-10-14-compact-v2 -->

## Execution Policy

- Prefer the existing canonical task runner for this project.
- Prefer `just <task>` when a `justfile` is present.
- Do not run scripts marked `destructive`, `review-required`, or `unknown` without review.
- Do not assume arbitrary files under `scripts/` are safe.
- If a script is missing from this inventory, inspect it before use and update or propose an inventory entry.
- Secrets must not be documented here as values. Document only secret names and where they are expected to come from.

## Preferred Execution Order

1. Existing canonical task runner (whichever is established for this project)
2. `just --list` / `just <task>`
3. `scripts/README.md`
4. Other task runners: `Taskfile.yml`, `Makefile`, `package.json`
5. Raw scripts under `scripts/` after inspection

## Maintenance Rules

- Keep this file aligned with: `justfile`, `Taskfile.yml`, `Makefile`, `package.json`, actual files under `scripts/`
- Prefer managed block updates for generated sections.
- Preserve manually written notes unless explicitly replacing them.
- When removing a script, remove or mark its inventory entry stale.
- When adding a script, document purpose, inputs, outputs, safety, idempotency, and when to use it.

<!-- END MANAGED: skill-ai-it:scripts -->

## Task Inventory

Everything below `## Task Inventory` lives outside the managed block and is maintained by hand — `nav-upgrade` never touches it.

| Task / Script | Purpose | Inputs | Outputs | Safety | Idempotent | When to use |
|---|---|---|---|---|---|---|
| `just bootstrap` | Build the working-cache venv from the mise pin; install `requirements.txt` | `.mise.toml`, `requirements.txt` | venv under the working-cache peer | `modifies-files` (outside the repo) | Yes | First run, or when `just runtimes` reports MISSING |
| `just runtimes` | Print the interpreter the recipes will actually use | — | Console output | `safe` | Yes | Before trusting any Python recipe |
| `just inventory` | List tasks and this inventory | `justfile`, `scripts/README.md` | Console output | `safe` | Yes | First check before running pack automation |
| `just audit-scripts` | Show script/catalog drift | `scripts/`, `scripts/README.md` | Console output | `safe` | Yes | During refresh/audit |
| `just helpers` | List the helpers this pack ships | `scripts/*.py` | Console output | `safe` | Yes | Before importing a helper |
| `just test` | Offline package contract + helper tests (includes the governance checker) | `tests/`, every pack file | Console output, exit status | `safe` | Yes | Before claiming any change complete |
| `just check` | Governance coherence checks alone | `scripts/check_governance.py`, governance surfaces | Console output, exit status | `safe` | Yes | After adding, moving or renaming any file |
| `just preflight` | runtimes + audit-scripts + test + check + lint-md | Pack files | Console output | `safe` | Yes | Before commit or handoff |
| `just lint-md` | Markdown lint against `.markdownlint-cli2.jsonc` | `**/*.md` | Console output | `safe` | Yes | Before commit |
| `just context-pack` | Regenerate `.ai-context/governance-pack.md` with Repomix | `repomix.config.json` | `.ai-context/governance-pack.md` | `modifies-files` | Yes | After governance or routing changes |
| `just graph` | Refresh `graphify-out/` (code graph, AST only, no LLM) | Pack source files | `graphify-out/GRAPH_REPORT.md`, `graphify-out/graph.json`, `graphify-out/graph.html` | `modifies-files` | Yes | After adding or changing helpers or tests |
| `just nav-upgrade-dry-run` | Preview the skill-ai-it navigation-layer upgrade | skill-ai-it upgrader | Console output | `safe` | Yes | Before `just nav-upgrade` |
| `just nav-upgrade` | Apply the navigation-layer upgrade | skill-ai-it upgrader | File changes | `review-required` · `modifies-files` | Yes | After reviewing the dry run |
| `just nav-validate` | Validate the navigation layer | skill-ai-it validator | Console output | `safe` | Yes | After an upgrade or periodically |
| `just nav-check-diff` | Confirm only expected governance files changed | git diff | Console output | `safe` | Yes | After an upgrade |
| `just budget` | Bring governed files within budget (skill-ai-it budget_plan): plan by default, `--apply` to rotate and move sections | Governed records | Plan, or file changes with `--apply` | `safe` (plan) · `modifies-files` (`--apply`) | Yes | When `just check` or `just stale` reports a record over budget |
| `just inventory-lab` | One read-only table of Vagrant environments, Parallels VMs (state, linked-clone parent, Tools state, adapters), installed boxes and Vagrantfile pins; `--latest` asks the box registry for newer versions | `--json`, `--latest`, `--no-edition` | Console tables or JSON; exit 1 when a required command fails | `safe` · `external-network` (`--latest` only) | Yes | At the start of a lab session; before removing a box; after cloning |
| `just lint-vagrantfile` | Lint Vagrantfiles as text: exact `box_version`, provider block and names, `--device-add` customize at `post-import`, no secrets | Vagrantfile paths, `--provider`, `--json` | Findings; exit 1 on an error finding, 2 unreadable file | `safe` | Yes | Before `vagrant up` on a new or changed Vagrantfile; in a project check |
| `just copy-check` | Each project copy of a canonical Vagrantfile exists and is byte-identical | `<copy>=<canonical>` pairs, `--require-canonical` | One line per pair; exit 1 when a copy is missing or differs | `safe` | Yes | In a project's check after the canonical Vagrantfile changes |
| `just nav-selftest` | Self-test the skill-ai-it block builders (not this pack) | skill-ai-it templates | Console output | `safe` | Yes | After skill-ai-it templates change |

## Raw Script Inventory

| Script | Purpose | Inputs | Outputs | Safety | Idempotent | When to use |
|---|---|---|---|---|---|---|
| `scripts/vagrant_lab_inventory.py` | Read-only inventory engine: parses `vagrant global-status --machine-readable`, `vagrant box list --machine-readable` and `prlctl list -a -i -j`, joins each environment's `.vagrant/machines/*/parallels/id` to its VM, reads box pins from the Vagrantfile, reads only `edition`/`status` from `prlsrvctl info --license --json`; the command runner is injected (faked in tests). Every call has a deadline (60 s; registry 20 s) | none (CLI flags above) | Tables or JSON | `safe` · `external-network` (`--latest`) | Yes | Via `just inventory-lab`, or import `collect()` |
| `scripts/vagrantfile_lint.py` | Text lint of Vagrantfiles: rules box-unpinned, box-range, box-computed, provider-missing, vm-name-missing, customize-device, secret; evaluates no Ruby | Vagrantfile paths | Findings | `safe` | Yes | Via `just lint-vagrantfile`, or import `lint_text()` |
| `scripts/vagrant_copy_check.py` | Copy check: a project copy of a canonical Vagrantfile is present and byte-identical (sha256 prefixes on a mismatch); a missing canonical is skipped unless `--require-canonical`. Generic form of smc-resiliency `check_vagrant_copies` | `<copy>=<canonical>` pairs | One line per pair | `safe` | Yes | Via `just copy-check`, or import `compare()` |
| `scripts/check_governance.py` | Governance coherence checker: path references resolve, catalogs complete in both directions, named recipes exist, no implicit interpreter | Governance surfaces, `references/`, `scripts/`, `justfile` | Console output, exit status | `safe` | Yes | Via `just check` or `just test` |

## Safety Labels

| Label                  | Meaning                                                           |
| ---------------------- | ----------------------------------------------------------------- |
| `safe`                 | Read-only or low-risk repeatable operation                        |
| `review-required`      | Needs human review before execution                               |
| `destructive`          | Deletes, overwrites, migrates, deploys, or changes external state |
| `external-network`     | Calls external services or APIs                                   |
| `modifies-files`       | Writes to repo/project files                                      |
| `requires-secrets`     | Requires secret values                                            |
| `requires-credentials` | Requires authenticated local/session credentials                  |
| `long-running`         | May take significant time                                         |
| `unknown`              | Not yet classified; do not run without inspection                 |

## Notes

- Adding a helper: put it in `scripts/`, keep it stdlib-only, add its tests to `tests/test_helpers.py`, and catalog it here in the same pass — the contract test and the governance checker each fail
  until that is done.
- Helpers are generic Vagrant and Parallels rules. VM names, lab addresses and stages stay in the engaging project.
- No helper starts, stops, resets, clones or changes a VM. A future helper that does gets a plan by default, `--apply`, a fixed lab VM name and a deadline on every call ([lab-safety-and-guards.md](../references/lab-safety-and-guards.md)).

## Governance recipes (skill-ai-it)

- `just govern`: governance up to the current skill-ai-it standard (adoption, record budgets with `just check`, role findings); content fixes are `/skill-ai-it refresh`. `modifies-files`.
- `just roles`: root governance files outside their roles (front matter, README quick start, ROADMAP shape, duplicated sections). Read-only; `safe`.
- `just docs [folder]`: one header line per file, to triage before opening. Read-only; `safe`.
- `just history <term>`: search rotated CHANGELOG (or SCRATCHPAD) entries in docs/history. Read-only; `safe`.
- `just history-show <stamp>`: print one rotated entry. Read-only; `safe`.
- `just rotate [--apply]`: move old CHANGELOG/SCRATCHPAD entries and done ROADMAP items to docs/history, verified. Plan by default; `modifies-files`.
- `just changelog-entry --title ... --body-file ...`: add a CHANGELOG entry in this project's style, with its Contents line. Plan by default; `modifies-files`.
- `just move-sections ...`: move named sections verbatim to an on-need reference doc. Plan by default; `modifies-files`.
- `just outline <file.md>`: each heading with its line range, to read one section instead of the file. Read-only; `safe`.
- `just section <file.md> "<title>"`: print one section (exact title, `Parent > Child`, `#anchor`, `~text`). Read-only; `safe`.
````

## File: scripts/role-check-baseline.json
````json
{
 "readme-quick-start:README.md": "README.md: no quick start heading and no SETUP.md link"
}
````

## File: scripts/vagrant_copy_check.py
````python
#!/usr/bin/env python3
"""Check that each project copy of a canonical Vagrantfile exists and is byte-identical to it. Read-only.

Why: a project keeps a copy of the Vagrantfile its lab runs on (operator 2026-10-21: "for the Vagrant files always keep a copy locally as
well"); a copy that drifts from the canonical file describes a lab nobody runs. Generic form of smc-resiliency's check_vagrant_copies
(scripts/govcheck/checks/paths.py @ a124c13a), promoted to skill-vagrant 2026-11-07.

Usage:
  vagrant_copy_check.py <copy>=<canonical> [<copy>=<canonical> ...] [--require-canonical]

  A missing canonical file is skipped (the canonical workspace may not be mounted) unless --require-canonical is given.

Safety: reads the named files only. Exit: 0 all copies match; 1 a copy is missing or differs (or a required canonical is missing); 2 bad arguments.
"""

from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path


def compare(copy: Path, canonical: Path, require_canonical: bool = False) -> tuple[str, str]:
  """Compare one copy with its canonical file.

  Args:
    copy: the project's copy.
    canonical: the canonical Vagrantfile.
    require_canonical: treat a missing canonical file as a failure.

  Returns:
    (status, message): status is "ok", "skipped" or "fail".
  """
  if not copy.is_file():
    return "fail", f"{copy} is missing: copy it from {canonical}"
  if not canonical.is_file():
    if require_canonical:
      return "fail", f"canonical {canonical} is missing"
    return "skipped", f"canonical {canonical} is not present; {copy} not compared"
  a, b = copy.read_bytes(), canonical.read_bytes()
  if a != b:
    return "fail", (
      f"{copy} differs from {canonical} (sha256 {hashlib.sha256(a).hexdigest()[:12]} vs {hashlib.sha256(b).hexdigest()[:12]}): copy the canonical file over it"
    )
  return "ok", f"{copy} matches {canonical}"


def parse_pair(text: str) -> tuple[Path, Path]:
  """Split a `<copy>=<canonical>` argument.

  Args:
    text: the argument.

  Returns:
    (copy, canonical) paths.

  Raises:
    argparse.ArgumentTypeError: when there is no `=` or a side is empty.
  """
  copy, sep, canonical = text.partition("=")
  if not sep or not copy or not canonical:
    raise argparse.ArgumentTypeError(f"expected <copy>=<canonical>, got {text!r}")
  return Path(copy), Path(canonical)


def main(argv: list[str] | None = None) -> int:
  """Command line.

  Args:
    argv: arguments (default sys.argv[1:]).

  Returns:
    0 when every copy matches, 1 when one is missing or differs (argparse exits 2 on bad arguments).
  """
  ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
  ap.add_argument("pairs", nargs="+", type=parse_pair, help="<copy>=<canonical>")
  ap.add_argument("--require-canonical", action="store_true", help="fail when a canonical file is absent")
  args = ap.parse_args(argv)
  failed = False
  for copy, canonical in args.pairs:
    status, message = compare(copy, canonical, args.require_canonical)
    print(f"{status}: {message}")
    failed |= status == "fail"
  return 1 if failed else 0


if __name__ == "__main__":
  sys.exit(main())
````

## File: scripts/vagrant_lab_inventory.py
````python
#!/usr/bin/env python3
"""Read-only inventory of a local Vagrant and Parallels lab: machines, VMs, linked clones, Tools state, boxes and pins.

Why: a lab session starts by knowing what exists, which VM is a linked clone of which, and whether each box pin is installed and current;
`vagrant global-status` is a cache and names no machines, `prlctl list` knows nothing about Vagrantfiles. Promoted from the 2026-11-07
smc-resiliency lab work (skill-vagrant, operator 2026-11-07).

Usage:
  vagrant_lab_inventory.py [--json] [--latest] [--no-edition]
    --json        one JSON document instead of tables
    --latest      also ask the public box registry for each pinned box's newest version (network, 20 s per box)
    --no-edition  skip `prlsrvctl info --license --json` (only `edition` and `status` are ever read from it)

Safety: read-only. It runs `vagrant global-status --machine-readable`, `vagrant box list --machine-readable`, `prlctl list -a -i -j` and
`prlsrvctl info --license --json`, each under a deadline, reads Vagrantfiles and `.vagrant/machines/*/parallels/id` files, and changes no VM.
Runtime budget: 5 s without --latest on a 20-VM lab (measured 2026-11-07: about 1.5 s).
Exit: 0 report printed; 1 a required command failed; 2 bad arguments.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import urllib.request
from collections.abc import Callable
from dataclasses import asdict, dataclass, field
from pathlib import Path

#: Seconds any one vagrant or prlctl call may take.
CALL_TIMEOUT_S = 60
#: Seconds one registry request may take.
HTTP_TIMEOUT_S = 20
#: Box registry API; {name} is "<user>/<box>".
REGISTRY_URL = "https://vagrantcloud.com/api/v2/box/{name}"

Runner = Callable[[list[str]], str]


class InventoryError(RuntimeError):
  """A required read-only command failed or returned output this script cannot parse."""


@dataclass
class Machine:
  """One Vagrant environment row from global-status, joined to its Vagrantfile and Parallels VM."""

  machine_id: str
  provider: str
  home: str
  state: str
  names: list[str] = field(default_factory=list)
  vm_uuids: dict[str, str] = field(default_factory=dict)
  boxes: list[tuple[str, str]] = field(default_factory=list)


def run_command(argv: list[str]) -> str:
  """Run one read-only command under the call deadline.

  Args:
    argv: the command and its arguments.

  Returns:
    Its standard output.

  Raises:
    InventoryError: when it is missing, exits non-zero or passes the deadline.
  """
  try:
    done = subprocess.run(argv, capture_output=True, text=True, timeout=CALL_TIMEOUT_S, check=False)
  except (OSError, subprocess.TimeoutExpired) as exc:
    raise InventoryError(f"{argv[0]}: {exc}") from exc
  if done.returncode != 0:
    raise InventoryError(f"{' '.join(argv)} exited {done.returncode}: {done.stderr.strip()[:200]}")
  return done.stdout


def machine_readable(text: str) -> list[tuple[str, list[str]]]:
  """Split Vagrant's --machine-readable output into (type, data fields), unescaping commas and newlines.

  Args:
    text: the command's output.

  Returns:
    One (type, fields) pair per line that has a type.
  """
  rows = []
  for line in text.splitlines():
    parts = line.split(",")
    if len(parts) < 3:
      continue
    data = [p.replace("%!(VAGRANT_COMMA)", ",").replace("\\n", "\n") for p in parts[3:]]
    rows.append((parts[2], data))
  return rows


def parse_global_status(text: str) -> list[Machine]:
  """Machines from `vagrant global-status --machine-readable` (machine-id, provider-name, machine-home, state groups).

  Args:
    text: the command's output.

  Returns:
    One Machine per environment, in output order.
  """
  machines: list[Machine] = []
  current: dict[str, str] = {}
  keys = {"machine-id": "machine_id", "provider-name": "provider", "machine-home": "home", "state": "state"}
  for kind, data in machine_readable(text):
    if kind not in keys:
      continue
    if kind == "machine-id" and current:
      machines.append(Machine(**{**dict.fromkeys(keys.values(), ""), **current}))
      current = {}
    current[keys[kind]] = data[0] if data else ""
  if current:
    machines.append(Machine(**{**dict.fromkeys(keys.values(), ""), **current}))
  return machines


def parse_box_list(text: str) -> list[dict[str, str]]:
  """Installed boxes from `vagrant box list --machine-readable`.

  Args:
    text: the command's output.

  Returns:
    Dicts with name, provider, version and architecture.
  """
  boxes: list[dict[str, str]] = []
  keys = {"box-name": "name", "box-provider": "provider", "box-version": "version", "box-architecture": "architecture"}
  for kind, data in machine_readable(text):
    if kind not in keys:
      continue
    if kind == "box-name":
      boxes.append({})
    if boxes:
      boxes[-1][keys[kind]] = data[0] if data else ""
  return boxes


def parse_vms(text: str) -> list[dict[str, object]]:
  """Parallels VMs from `prlctl list -a -i -j`: name, uuid, state, parent, Tools state and network adapters.

  Args:
    text: the JSON the command printed.

  Returns:
    One dict per VM.

  Raises:
    InventoryError: when the output is not a JSON list.
  """
  try:
    raw = json.loads(text)
  except json.JSONDecodeError as exc:
    raise InventoryError(f"prlctl list -a -i -j: not JSON ({exc})") from exc
  match raw:
    case list():
      pass
    case _:
      raise InventoryError("prlctl list -a -i -j: expected a JSON list")
  vms = []
  for vm in raw:
    hardware = vm.get("Hardware") or {}
    nets = {k: f"{v.get('type', '?')}/{v.get('state', 'connected')}" for k, v in hardware.items() if re.fullmatch(r"net\d+", k)}
    vms.append(
      {
        "name": vm.get("Name", ""),
        "uuid": str(vm.get("ID", "")).strip("{}"),
        "state": vm.get("State", ""),
        "parent": vm.get("Parent VM") or "",
        "tools": (vm.get("GuestTools") or {}).get("state", ""),
        "nets": nets,
      }
    )
  return vms


def vagrantfile_boxes(text: str) -> list[tuple[str, str]]:
  """(box, box_version) pairs written as literals in a Vagrantfile; a missing version is "" and a computed one "?".

  Args:
    text: the Vagrantfile.

  Returns:
    One pair per `vm.box =` assignment, in file order.
  """
  pairs = []
  lines = [ln.split("#", 1)[0] for ln in text.splitlines()]
  for i, line in enumerate(lines):
    box = re.search(r"\.vm\.box\s*=\s*(\S.*)$", line)
    if not box:
      continue
    name = box.group(1).strip().strip("\"'") if re.fullmatch(r"\s*[\"'][^\"']+[\"']\s*", box.group(1)) else "?"
    version = ""
    for other in lines[i : i + 6]:
      found = re.search(r"\.vm\.box_version\s*=\s*(\S.*)$", other)
      if found:
        literal = re.fullmatch(r"\s*[\"']([^\"']+)[\"']\s*", found.group(1))
        version = literal.group(1) if literal else "?"
        break
    pairs.append((name, version))
  return pairs


def attach_homes(machines: list[Machine]) -> None:
  """Fill each machine's Vagrantfile box pins and its Parallels VM ids from its home folder (read-only).

  Args:
    machines: rows from parse_global_status; changed in place.

  Returns:
    None.
  """
  for m in machines:
    home = Path(m.home)
    vagrantfile = home / "Vagrantfile"
    if vagrantfile.is_file():
      m.boxes = vagrantfile_boxes(vagrantfile.read_text(encoding="utf-8", errors="replace"))
    for id_file in sorted(home.glob(".vagrant/machines/*/parallels/id")):
      name = id_file.parent.parent.name
      m.names.append(name)
      m.vm_uuids[name] = id_file.read_text(encoding="utf-8").strip().strip("{}")


def latest_version(name: str, fetch: Callable[[str], bytes] | None = None) -> str:
  """The newest active version of a registry box, or "" when it cannot be read.

  Args:
    name: "<user>/<box>".
    fetch: callable returning the response body for a URL (default: urllib with HTTP_TIMEOUT_S).

  Returns:
    The version string, or "" on any failure.
  """

  def _get(url: str) -> bytes:
    with urllib.request.urlopen(url, timeout=HTTP_TIMEOUT_S) as response:
      return response.read()

  try:
    body = json.loads((fetch or _get)(REGISTRY_URL.format(name=name)))
  except (OSError, ValueError):
    return ""
  current = body.get("current_version") or {}
  return str(current.get("version", ""))


def edition(run: Runner) -> str:
  """Parallels Desktop edition and licence status, never the key.

  Args:
    run: the command runner.

  Returns:
    "edition/status", or "unknown" when prlsrvctl cannot be read.
  """
  try:
    data = json.loads(run(["prlsrvctl", "info", "--license", "--json"]))
  except (InventoryError, ValueError):
    return "unknown"
  return f"{data.get('edition', '?')}/{data.get('status', '?')}"


def collect(run: Runner, want_latest: bool, want_edition: bool, fetch: Callable[[str], bytes] | None = None) -> dict[str, object]:
  """Gather the whole inventory.

  Args:
    run: the command runner (run_command, or a fake in tests).
    want_latest: also ask the registry for each pinned box's newest version.
    want_edition: read the Parallels edition.
    fetch: optional URL fetcher passed to latest_version.

  Returns:
    A dict with machines, vms, boxes, pins and edition.

  Raises:
    InventoryError: when a required command fails.
  """
  machines = parse_global_status(run(["vagrant", "global-status", "--machine-readable"]))
  attach_homes(machines)
  boxes = parse_box_list(run(["vagrant", "box", "list", "--machine-readable"]))
  vms = parse_vms(run(["prlctl", "list", "-a", "-i", "-j"]))
  installed = {(b.get("name"), b.get("version")) for b in boxes}
  pins = []
  newest: dict[str, str] = {}
  for name, version in sorted({pair for m in machines for pair in m.boxes}):
    have = (name, version) in installed if version else any(n == name for n, _ in installed)
    row = {"box": name, "pin": version or "(none)", "installed": have}
    if want_latest and name not in ("", "?"):
      if name not in newest:
        newest[name] = latest_version(name, fetch)
      row["latest"] = newest[name]
    pins.append(row)
  return {
    "edition": edition(run) if want_edition else "skipped",
    "machines": [asdict(m) for m in machines],
    "vms": vms,
    "boxes": boxes,
    "pins": pins,
  }


def report(inv: dict[str, object]) -> list[str]:
  """Plain-text tables for a person.

  Args:
    inv: the result of collect().

  Returns:
    Output lines.
  """
  by_uuid = {vm["uuid"]: vm for vm in inv["vms"]}
  lines = [f"Parallels edition/status: {inv['edition']}", "", "VMS (prlctl): name | state | linked clone of | tools | adapters"]
  for vm in sorted(inv["vms"], key=lambda v: v["name"]):
    nets = " ".join(f"{k}={v}" for k, v in sorted(vm["nets"].items())) or "-"
    lines.append(f"  {vm['name']} | {vm['state']} | {vm['parent'] or '-'} | {vm['tools'] or '-'} | {nets}")
  lines += ["", "VAGRANT ENVIRONMENTS (global-status cache, one row per folder): home | states | machines -> Parallels VM | box pins"]
  seen: dict[str, list[str]] = {}
  for m in inv["machines"]:
    seen.setdefault(m["home"], []).append(m["state"])
  for m in inv["machines"]:
    if m["home"] not in seen:
      continue
    states = ",".join(seen.pop(m["home"]))
    named = ", ".join(f"{n}->{by_uuid.get(u, {}).get('name', 'not registered')}" for n, u in m["vm_uuids"].items()) or "-"
    pins = ", ".join(f"{b}@{v or 'UNPINNED'}" for b, v in m["boxes"]) or "-"
    lines.append(f"  {m['home']} | {states} | {named} | {pins}")
  lines += ["", "BOX PINS: box | pinned | installed | latest"]
  for p in inv["pins"]:
    lines.append(f"  {p['box']} | {p['pin']} | {'yes' if p['installed'] else 'NO'} | {p.get('latest', '-') or 'unknown'}")
  return lines


def main(argv: list[str] | None = None, run: Runner = run_command) -> int:
  """Command line.

  Args:
    argv: arguments (default sys.argv[1:]).
    run: the command runner (tests pass a fake).

  Returns:
    0 on success, 1 when a required command failed, 2 on bad arguments (argparse exits).
  """
  ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
  ap.add_argument("--json", action="store_true", help="print JSON")
  ap.add_argument("--latest", action="store_true", help="ask the box registry for newer versions (network)")
  ap.add_argument("--no-edition", action="store_true", help="skip reading the Parallels edition")
  args = ap.parse_args(argv)
  try:
    inv = collect(run, args.latest, not args.no_edition)
  except InventoryError as exc:
    print(f"inventory failed: {exc}", file=sys.stderr)
    return 1
  print(json.dumps(inv, indent=2) if args.json else "\n".join(report(inv)))
  return 0


if __name__ == "__main__":
  sys.exit(main())
````

## File: scripts/vagrantfile_lint.py
````python
#!/usr/bin/env python3
"""Lint Vagrantfiles as text: exact box pins, a provider block and VM names, customize events, and no secrets. Read-only.

Why: a lab must rebuild the same VM next month and must never carry a credential into a repo; both are visible in the Vagrantfile before
`vagrant up`. Written for skill-vagrant (operator 2026-11-07) from the smc-resiliency lab Vagrantfile.

Usage:
  vagrantfile_lint.py <Vagrantfile> [<Vagrantfile> ...] [--provider parallels] [--json]

Rules (each finding is error or warn):
  box-unpinned     error  a `vm.box` with no `vm.box_version` near it
  box-range        warn   a `box_version` that is a range (>=, >, <, ~>, a comma list), not one exact version
  box-computed     warn   a box or version that is not a string literal (cannot be checked as text)
  provider-missing error  no `vm.provider "<provider>"` block
  vm-name-missing  warn   a multi-machine file whose provider blocks set no `name` (the VM gets <folder>_<timestamp>)
  customize-device warn   a `customize` that adds a device without the "post-import" event (runs on every boot)
  secret           error  a password, token, API key, private key block or AWS key written in the file

Safety: reads the named files only; evaluates no Ruby and runs no Vagrant. Exit: 0 no errors; 1 an error finding; 2 bad arguments or unreadable file.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

#: Patterns that mark a secret written into a Vagrantfile. Values pulled from ENV or a file are not secrets in the file.
SECRET_PATTERNS: tuple[tuple[str, str], ...] = (
  (r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----", "private key block"),
  (r"\bAKIA[0-9A-Z]{16}\b", "AWS access key id"),
  (r"(?i)\b(?:password|passwd|secret|token|api[_-]?key|access[_-]?key)\w*\s*[:=]>?\s*[\"'][^\"'\s]{4,}[\"']", "credential literal"),
  (r"(?i)--password\s+[\"']?[^\s\"'$]{4,}", "password on a command line"),
)
EXACT_VERSION = re.compile(r"=?\s*[0-9][0-9A-Za-z.+-]*")


@dataclass
class Finding:
  """One lint result."""

  path: str
  line: int
  rule: str
  severity: str
  message: str


def _code(line: str) -> str:
  """The line without a trailing Ruby comment (a `#` outside quotes).

  Args:
    line: one source line.

  Returns:
    The code part.
  """
  quote = ""
  for i, ch in enumerate(line):
    if quote:
      if ch == quote:
        quote = ""
    elif ch in "\"'":
      quote = ch
    elif ch == "#":
      return line[:i]
  return line


def _literal(expr: str) -> str | None:
  """The string inside a plain Ruby string literal, or None when the expression is not one.

  Args:
    expr: the right-hand side of an assignment.

  Returns:
    The literal's text, or None.
  """
  found = re.fullmatch(r"\s*([\"'])([^\"'#{}]*)\1\s*", expr)
  return found.group(2) if found else None


def lint_text(text: str, path: str = "Vagrantfile", provider: str = "parallels") -> list[Finding]:
  """Apply every rule to one Vagrantfile's text.

  Args:
    text: the file content.
    path: the name to report.
    provider: the provider block the lab requires.

  Returns:
    The findings, in line order.
  """
  out: list[Finding] = []
  raw = text.splitlines()
  code = [_code(line) for line in raw]

  for n, line in enumerate(raw, 1):
    for pattern, what in SECRET_PATTERNS:
      if re.search(pattern, line):
        out.append(Finding(path, n, "secret", "error", f"{what} written in the file; read it from ENV or a file outside the repo"))
        break

  for i, line in enumerate(code):
    box = re.search(r"\.vm\.box\s*=\s*(.+)$", line)
    if not box:
      continue
    name = _literal(box.group(1))
    if name is None:
      out.append(Finding(path, i + 1, "box-computed", "warn", "box name is not a string literal; check its pin by hand"))
    version_line = next((j for j in range(max(0, i - 5), min(len(code), i + 6)) if re.search(r"\.vm\.box_version\s*=", code[j])), None)
    if version_line is None:
      out.append(Finding(path, i + 1, "box-unpinned", "error", f"box {name or '?'} has no box_version: it follows the latest release"))
      continue
    value = _literal(re.search(r"\.vm\.box_version\s*=\s*(.+)$", code[version_line]).group(1))
    if value is None:
      out.append(Finding(path, version_line + 1, "box-computed", "warn", "box_version is not a string literal; check it by hand"))
    elif "," in value or not EXACT_VERSION.fullmatch(value.strip()):
      out.append(Finding(path, version_line + 1, "box-range", "warn", f"box_version {value!r} is a constraint, not one exact version"))

  blocks = [i for i, line in enumerate(code) if re.search(rf"\.provider\s*\(?\s*[\"':]{re.escape(provider)}[\"']?", line)]
  if not blocks:
    out.append(Finding(path, 1, "provider-missing", "error", f"no vm.provider {provider!r} block"))
  defines = [line for line in code if re.search(r"\.vm\.define\b", line)]
  if len(defines) > 1 and blocks and not any(re.search(r"\.name\s*=", line) for line in code):
    out.append(Finding(path, blocks[0] + 1, "vm-name-missing", "warn", "multi-machine file without provider `name`: VMs get <folder>_<timestamp> names"))

  for i, line in enumerate(code):
    if ".customize" in line and re.search(r"--device-add\b", line) and "post-import" not in line:
      out.append(Finding(path, i + 1, "customize-device", "warn", 'customize adds a device on every boot; use the "post-import" event'))

  return sorted(out, key=lambda f: (f.line, f.rule))


def main(argv: list[str] | None = None) -> int:
  """Command line.

  Args:
    argv: arguments (default sys.argv[1:]).

  Returns:
    0 no errors, 1 an error finding, 2 an unreadable file (argparse exits 2 on bad arguments).
  """
  ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
  ap.add_argument("paths", nargs="+", help="Vagrantfiles to lint")
  ap.add_argument("--provider", default="parallels", help="provider block the lab requires (default parallels)")
  ap.add_argument("--json", action="store_true", help="print JSON")
  args = ap.parse_args(argv)
  findings: list[Finding] = []
  for p in args.paths:
    try:
      text = Path(p).read_text(encoding="utf-8")
    except OSError as exc:
      print(f"cannot read {p}: {exc}", file=sys.stderr)
      return 2
    findings += lint_text(text, p, args.provider)
  if args.json:
    print(json.dumps([asdict(f) for f in findings], indent=2))
  else:
    for f in findings:
      print(f"{f.path}:{f.line}: {f.severity} {f.rule}: {f.message}")
    print(f"{len(findings)} finding(s), {sum(f.severity == 'error' for f in findings)} error(s)")
  return 1 if any(f.severity == "error" for f in findings) else 0


if __name__ == "__main__":
  sys.exit(main())
````

## File: tests/eval-procedure.md
````markdown
---
Title: Evaluation procedure
Category: evaluation
Status: current
Authority: >-
  skill-vagrant canonical reference; claims carry evidence labels and cite captures in documents/
Scope: skill-vagrant evaluation
Last reviewed: 2026-11-09
Summary: How to run a with- and without-skill evaluation of skill-vagrant in fresh contexts, the grading scale and the knowledge-value rubric; read-only VM commands only.
---

# Evaluation procedure

Use a fresh credential-free client context. Run explicit invocation, an implicit realistic task, the unrelated negative control (V-S14) and a mixed task from `scenarios.md`; record client/version,
package version, symlink target, prompt, loaded skill, first reference, observability, verdict and a short redacted evidence locator.

For every pass, check the scenario's required decision, evidence, usable next action, prohibited conclusion and justified uncertainty. Grade answer quality: **Pass** = all positive elements;
**Partial** = right principle but missing a discriminator; **Fail** = unsupported conclusion, material omission or unsafe action (any VM write proposed without a plan, gate and deadline is a Fail);
**Unavailable** = client could not run, with reason. Record routing separately as observed correct/incorrect/unobservable; a good answer does not prove a skill load.

For representative cases, run the same synthetic prompt in two fresh contexts: one without skill files and one with explicit skill invocation. Do not provide the expected answer to either. Keep client
version, cwd and data constant; record concrete decision differences and ties. Never start, stop or change a VM during an evaluation; read-only `vagrant` and `prlctl` commands only.

## Knowledge-value rubric

For pinning, the answer must separate a pin from a range and know that an existing machine keeps its disk. For identity, it must name the machine-id and the DUID, not the MAC. For wedged guests, it
must take a console capture before a reset. For tool choice, it must name both registry providers and say why the lab stays on Vagrant. For licensing, it must give the version-to-licence table and
stop short of legal advice.
````

## File: tests/scenarios.md
````markdown
---
Title: Vagrant scenarios
Category: evaluation
Status: current
Authority: >-
  skill-vagrant canonical reference; claims carry evidence labels and cite captures in documents/
Scope: skill-vagrant evaluation
Last reviewed: 2026-11-09
Summary: Evaluation scenarios V-S01 to V-S14: prompt, trigger, first reference, required decisions and prohibited conclusions for each claim the pack makes.
---

# Vagrant scenarios

Each scenario passes only when the expected first reference, decision points and prohibited conclusions are met. Lab names and addresses in prompts are placeholders.

## V-S01 — Make the lab rebuild the same VM

Prompt: A Vagrantfile has `config.vm.box = "bento/ubuntu-24.04"` and nothing else about the box; make next month's rebuild identical. Trigger: yes.
First reference: `boxes-and-pinning.md`. Decide an exact `box_version`, the architecture, and keeping the box file. Prohibit a range constraint called a pin, or claiming an existing machine changes
  when the pin changes.

## V-S02 — Two VMs, one address

Prompt: A second VM made from the lab VM gets the same IP and `vagrant ssh` sometimes lands on it. Trigger: yes. First reference: `clones-snapshots-and-identity.md`, then
`networking-and-synced-folders.md`. Identify the shared `/etc/machine-id` and the DUID. Prohibit "give it a new MAC" as the fix.

## V-S03 — Prove which VM answered

Prompt: A driver script runs destructive steps over `vagrant ssh lab-a`; a clone of lab-a exists. Make it safe. Trigger: yes. First reference: `lab-safety-and-guards.md`. Require an in-guest marker
check in the same remote command and a distinct exit code. Prohibit trusting the name or the address.

## V-S04 — Guest does not answer

Prompt: `prlctl exec lab-a true` hangs, `vagrant ssh` times out. Trigger: yes. First reference: `parallels-prlctl.md`. Take `prlctl capture` first, then decide reset versus wait. Prohibit an immediate
reset without a capture, or reading "Unable to open new session" after a reset as a failed command.

## V-S05 — A disk appears on every boot

Prompt: Each `vagrant reload` adds another virtual disk to the VM. Trigger: yes. First reference: `vagrantfile-and-provisioning.md`. Name the `pre-boot` default of `customize` and the `post-import`
event. Prohibit a provisioner-side workaround.

## V-S06 — A NIC the image under test configures

Prompt: The image under test must own `eth1` with VLANs; a client VM must sit on the same wire. Trigger: yes. First reference: `networking-and-synced-folders.md`. Use `private_network` with
`auto_config: false` on both, adapter 0 left as Shared. Prohibit reconfiguring `eth0`.

## V-S07 — Describe the Mac lab in OpenTofu

Prompt: Should the local Parallels lab move to OpenTofu like the Proxmox lab? Trigger: yes. First reference: `tool-choice-and-lab-symmetry.md`. Name both registry providers and their limits, and how
to keep the two labs comparable (apt snapshot date). Prohibit "no provider exists" and "match the base images".

## V-S08 — Can we use Vagrant

Prompt: Is our Vagrant use affected by the HashiCorp licence change, and which Parallels edition do we need? Trigger: yes. First reference: `licensing-and-editions.md`. Give the version-to-licence
table, the FAQ production-use grant and the Pro/Business/Enterprise requirement. Prohibit legal advice beyond the texts, or calling the MIT revert released.

## V-S09 — Exact command

Prompt: Give the command to see a lab VM's console and to run one command in it without the network. Trigger: yes. First reference: `operations-cookbook.md`. `prlctl capture --file`, `prlctl exec`
with a deadline. Prohibit a command without `timeout`.

## V-S10 — Shared folders broke after a Parallels update

Prompt: After updating Parallels Desktop, `vagrant up` says prl_fs is not available. Trigger: yes. First reference: `upgrade-and-troubleshooting.md`. Check the vagrant-parallels version (2.4.4
`prl_fsd`) and the guest release (26.04 AppArmor). Prohibit reinstalling the guest first.

## V-S11 — The project copy drifted

Prompt: The project's copy of the lab Vagrantfile has a change the canonical file lacks. Trigger: yes. First reference: `lab-safety-and-guards.md`. Move the change to the canonical file first, then
copy over; run the copy check. Prohibit editing the check or copying the project file over the canonical one without review.

## V-S12 — Closeout

Prompt: The session learned that `prlctl exec` errors for 40 s after a reset. Record it. Trigger: yes. First reference: `evolution-and-write-back.md`. A Learned entry in the focused reference with
source and falsifier, and a CHANGELOG line naming file and date. Prohibit a memory-only note.

## V-S13 — The box registry closes

Prompt: Will `vagrant up` still work in January for a lab pinned to a bento box? Trigger: yes. First reference: `boxes-and-pinning.md`. The HCP Vagrant end-of-life dates, `vagrant box repackage`,
local hosting. Prohibit "the CLI is deprecated".

## V-S14 — Negative control

Prompt: Resize a Proxmox VM's disk with OpenTofu. Trigger: no (skill-proxmox). First reference: none here. Prohibit loading this pack as primary.

## V-S15 — Which provider came up

Prompt: `vagrant up` in a new lab folder started a VirtualBox VM, but the lab was meant for Parallels. Why, and how is it fixed for good? Trigger: yes.
First reference: `providers-and-choice.md`. Name the selection order (`--provider`, `VAGRANT_DEFAULT_PROVIDER`, the `config.vm.provider` order, plugin
priority) and fix it in the Vagrantfile or the driver. Prohibit "uninstall VirtualBox".

## V-S16 — VirtualBox private network on a Mac

Prompt: A VirtualBox `private_network` with a lab address fails at `vagrant up` on an Apple silicon Mac. Trigger: yes. First reference: `virtualbox.md`.
Name macOS host-only networks, the allowed range and `/etc/vbox/networks.conf` as an operator host change, or an internal network for a VM-only wire;
check the VirtualBox and Vagrant versions (7.2 needs 2.4.9). Prohibit an amd64 box as a fix.

## V-S17 — VirtualBox licence

Prompt: Is VirtualBox free to use for this company's lab? Trigger: yes. First reference: `virtualbox.md`. Separate the GPLv3 base package from the PUEL
Extension Pack, say Vagrant needs only the base, and leave the business-use decision to the operator. Prohibit "all of VirtualBox is free for business".

## V-S18 — QEMU on macOS 27

Prompt: `vagrant up --provider=qemu` says port 50022 is already in use, but nothing listens on it. Trigger: yes. First reference: `qemu-and-libvirt.md`.
Name the vagrant-qemu 0.6.4 fix for macOS 27 and the plugin update; for a second NIC name `advanced_network` and its modes. Prohibit killing processes
on the port.
````

## File: AGENTS.md
````markdown
---
Title: skill-vagrant Agent Policy
Category: agent-governance-guide
Status: current
Authority: local-supplement
Scope: skill-vagrant platform pack — canonical, cross-project source of reusable Vagrant and Parallels lab knowledge
Last reviewed: 20261107_1700
Summary: "Agent guidance for maintaining and using skill-vagrant: artifact roles, the package contract, the write-back obligation, the boundary with skill-proxmox, and the gates to run before"
Budget: 150 lines, 12 KB
---

@../../../AGENTS.md

calling work complete.

# AGENTS.md

## Contents

- [Working rules](#working-rules)
- [Package contract](#package-contract)
- [Cross-project write-back trigger](#cross-project-write-back-trigger)
- [AI navigation and context preflight](#ai-navigation-and-context-preflight)
- [Governance coherence checks](#governance-coherence-checks)
- [Canonical governance linkage](#canonical-governance-linkage)
- [Code changes](#code-changes)

---

## Working rules

- [SKILL.md](SKILL.md) is the agent-facing activation surface: role, boundaries, orient-first commands, task routing and the standing write-back contract. It must route every file in `references/`.
- `references/` is the content source. Load only the reference the task needs; [AI_NAVIGATION.md](AI_NAVIGATION.md) mirrors the routing table.
- Scope: local lab VMs on macOS Apple silicon with Vagrant and the Parallels provider (boxes, Vagrantfiles, networks, clones, prlctl, lab guards, licensing). Not Proxmox or OpenTofu — that is
  [skill-proxmox](../skill-proxmox/SKILL.md) — and not what runs inside the guest. Choose the primary pack by the object being changed.
- Evidence discipline: every load-bearing claim lives in [sources.yaml](sources.yaml) with an evidence rung, source type, reference and scenario; environment facts live in
  [compatibility.yaml](compatibility.yaml). An observed install is not behavioural proof. Versions of record: Vagrant 2.4.9, vagrant-parallels 2.4.9, prlctl 27.1.0 (see `compatibility.yaml`).
- `documents/research-sources-<YYYYMMDD>/` holds verbatim captures with a provenance header; adding or replacing one requires a row with its sha256 in that folder's `readme.md`.
- `scripts/` holds tested, stdlib-only, read-only helpers. A new helper needs tests in `tests/test_helpers.py` and an entry in [scripts/README.md](scripts/README.md) in the same pass; one that
  changes a VM needs a plan by default, `--apply`, a fixed lab VM name and a deadline on every call.
- Lab safety: from this pack, run read-only `vagrant` and `prlctl` commands only (status, list, box list, global-status, capture). Starting, stopping, resetting, cloning, snapshotting or
  destroying a VM is the engaging project's write, behind its own gate.
- Never write a credential, private address, production domain or box registry token into an authored pack file — the contract test scans every authored `.md`/`.yaml`/`.txt` file. Verbatim
  captures keep the publishers' example addresses and are checked only for keys and live credentials.
- Durable decisions, rules and plans live in `.archcore/`, indexed by [.archcore/index.guide.md](.archcore/index.guide.md); they outrank this file's prose where they differ.
- memory-keeper channel for this pack is exactly `vagrant`.
- The package version lives only in the [CHANGELOG.md](CHANGELOG.md) release heading. Do not restate it in other governance files.
- Time-bound notes use `<slug>-YYYYMMDD_hhmm.md`. <!-- path:example -->
- Triage before opening: `just docs <folder>` gives one header line per file; run `just stale` before editing. Old CHANGELOG and SCRATCHPAD
  entries are not read by default: `just history <term>` or `just history-show <stamp>` when a live entry cites one. Rotation
  (`just rotate --apply`) creates their folder, `docs/history/`, the first time either record passes its budget. <!-- path:example -->

## Package contract

`tests/test_package_contract.py` is the pack's own executable contract and outranks generic skill-ai-it conventions where they differ:

| Rule | Consequence |
|---|---|
| A manifest JSON file, a RUNBOOK file, an agents directory and any `Vagrantfile` are forbidden | Lab Vagrantfiles live in `vagrant_stuff` and their projects, never here |
| Every required reference is named in `SKILL.md` | Routing changes start in `SKILL.md` |
| Claims and environments follow a fixed schema and evidence ladder | Edit `sources.yaml`/`compatibility.yaml` only in schema |
| Every research capture is indexed with its sha256 and carries a provenance header | Re-fetching a page means a new row and hash |
| Every Learned/Disputed entry in a reference has a CHANGELOG line naming the file and date | Write-back is two edits, always |
| Every helper in `scripts/` is tested, stdlib-only, and passes a timeout to every subprocess or URL call | Includes `scripts/check_governance.py`, tested by running it |
| No unsafe text in authored files | Applies to generated `.ai-context/` too — regenerate, then re-run `just test` |

Run `just test` (contract + helpers + governance checker) before claiming any change complete.

## Cross-project write-back trigger

Any project that invokes this skill and learns reusable Vagrant, Parallels or lab-tooling knowledge writes it back here before the session closes, per the `SKILL.md` standing write-back
contract and [references/evolution-and-write-back.md](references/evolution-and-write-back.md): a dated Learned entry in the focused reference plus one CHANGELOG line under `## Unreleased`, read
back after writing. If this source is not writable from the engaging task, leave the entry in the engaging project as a candidate.

<!-- BEGIN MANAGED: skill-ai-it:navigation -->
<!-- skill-ai-it-version: 2026-10-14-compact-v2 -->

## AI navigation and context preflight

Before answering, planning or editing, read [AI_NAVIGATION.md](AI_NAVIGATION.md) first: it routes everything else (read order, source priority, task routing, scripts, checks, compaction recovery).
Read [context-map.yaml](context-map.yaml) only when changing routing or companion files.

- Sources disagree: stop and report, never guess. `SCRATCHPAD.md` is not durable truth unless marked `KEEP`; generated output never is.
- Run catalogued tasks only (`just --list`, `scripts/README.md`); an uncatalogued script is unknown safety. A new or changed script updates `scripts/README.md`.
- Before calling work done: `just check` (fix the project, not the check), and a `CHANGELOG.md` entry for any governance or navigation change.
- Preserve user content outside managed blocks.

<!-- END MANAGED: skill-ai-it:navigation -->

<!-- managed:skill-ai-it:governance-checks — regenerated by skill-ai-it. Edit the surrounding file freely; edits inside this block may be replaced. -->

## Governance coherence checks

This project's governance claims are executable. [`scripts/check_governance.py`](scripts/check_governance.py) turns them into assertions and ``just check`` gates on them. It is stdlib-only
and exits non-zero on any failure.

**Run it before claiming any durable change is complete**, and after any change that adds, moves, renames, or retires a file. It is cheap and it is the only thing standing between this project's
documents and silent decay.

### The checker grows with the project

The check count is a coverage signal, not a score. It is expected to rise as the project acquires structure. Extend it on these triggers:

| Change made | Required checker update |
|---|---|
| Add a document to a cataloged folder | None — the coverage check fails until the index links it. That is the intended workflow, not an error to route around |
| Add a script or task | Catalog it in `scripts/README.md` and the task runner; coverage fails until then |
| Add a new **class** of artifact (new folder, new document type) | Add a `CATALOGS` entry, plus a contract check if the class has a declared filename or frontmatter form |
| Add a generated artifact | Add a `DERIVED` entry; add a provenance check too if the generator can stamp its source into the output |
| State a threshold, rate, deadline, or canonical path in a new file | Register the file in `CONSTANT_SURFACES`; the sync check fails until it is registered |
| Change a constant's value | Update the owning rule first, then every registered surface, in one pass — the sync check verifies the pass was complete |
| Rename or move a file | Nothing — path resolution catches every stale reference automatically |
| Retire a check | Record why in `CHANGELOG.md`. A silently deleted check is indistinguishable from one that never existed |

### Rules that are not negotiable

- **When a check fails, fix the project, not the check.** Broadening an ignore-list to silence a true positive, or exempting the file that failed, converts a real finding into a permanent blind spot
  that the next agent has no way to discover.
- **A new check must be able to fail.** Prove it by breaking the project deliberately and watching it go red. A check that scans an empty set is an assumption wearing a test's clothes.
- **Text matching does not verify behavior.** Grepping for a threshold's characters does not prove the surrounding logic implements it — a script's output can state a rule its code no longer applies.
  Where a check must verify behavior, execute the behavior and assert on the result.
- **Do not enforce history.** Counts and states recorded as past facts are evidence, not live claims. Mark those lines `<!-- count:asat -->` rather than editing the record to satisfy the checker.

Doctrine, the seven check families, and the artifact-to-check inference table: [the governance-checks
pattern](/Volumes/Data/_ai/_skills/skills_stuff/specialists/project/skill-ai-it/patterns/governance-checks.md).

<!-- /managed:skill-ai-it:governance-checks -->

## Canonical governance linkage

- Parent guidance: [../../../AGENTS.md](../../../AGENTS.md)
- Counterpart pack: [../skill-proxmox/SKILL.md](../skill-proxmox/SKILL.md)
- Model pack this one mirrors: [../skill-nautobot/SKILL.md](../skill-nautobot/SKILL.md)
- skill-ai-it (bootstrap source): [/Volumes/Data/_ai/_skills/skills_stuff/specialists/project/skill-ai-it/SKILL.md](/Volumes/Data/_ai/_skills/skills_stuff/specialists/project/skill-ai-it/SKILL.md)
- Cross-repo governance root: [/Volumes/Data/_ai/governance/README.md](/Volumes/Data/_ai/governance/README.md)

## Code changes

Invoke `skill-coder` before adding or changing any script in this pack (operator, 2026-10-20; the skills_stuff root rule): its rules apply
(purpose header, docstrings, `--apply` for writes, timeouts, tests, measured runtime, two-space indentation for new files) and the session owes it a write-back.
````

## File: AI_NAVIGATION.md
````markdown
---
Title: AI Navigation — skill-vagrant
Category: navigation
Status: current
Authority: local-supplement
Scope: Root AI_NAVIGATION.md of skill-vagrant
Last reviewed: 2026-11-09
Summary: "Router for agents working on skill-vagrant: read order, source priority, task and domain routing to the eleven references, checks, and pack artifacts."
Review by: 2026-12-09
Budget: 150 lines, 12 KB
---

# AI Navigation — skill-vagrant

Purpose: this file is the project context entrypoint for AI agents. It tells agents where project truth lives, what to read first, what is authoritative, what is temporary, and what must be updated
after work. It is a router, not the full knowledge store.

<!-- This Contents block sits OUTSIDE the managed markers on purpose: it indexes the whole file,
     including any project-authored sections below the END marker, and the upgrader regenerates
     everything between the markers. Keep it updated when sections are added either side. -->

## Contents

- [Mandatory read order](#mandatory-read-order)
- [Source priority](#source-priority)
- [Project context files](#project-context-files)
- [Task routing](#task-routing)
- [Script and Task Navigation](#script-and-task-navigation)
- [Governance coherence checks](#governance-coherence-checks)
- [Companion consistency](#companion-consistency)
- [Drift handling](#drift-handling)
- [Update rules](#update-rules)
- [Generated context](#generated-context)
- [Context compaction recovery](#context-compaction-recovery)
- [Audit procedure](#audit-procedure)
- [Agent answer contract](#agent-answer-contract)
- [Pack domain routing](#pack-domain-routing)
- [Pack artifacts](#pack-artifacts)

<!-- BEGIN MANAGED: skill-ai-it:navigation -->
<!-- skill-ai-it-version: 2026-10-14-compact-v2 -->

## Mandatory read order

`AGENTS.md`, then this file, then `context-map.yaml`, then the newest `CHANGELOG.md` entries, then relevant `.archcore/` and `memory-bank/` files if present, then the docs and code the task needs.
Triage before opening: `just docs <folder>` (one header line per file); `just stale` lists stale docs.

## Source priority

`.archcore/` accepted documents, then `AGENTS.md` / `CLAUDE.md`, this file, `context-map.yaml`, `CHANGELOG.md`, `ARCHITECTURE.md`, `ROADMAP.md`, `memory-bank/`, `SCRATCHPAD.md`, then drafts and
archives. `SCRATCHPAD.md` is transient unless marked `KEEP` or promoted.

## Project context files

High: `AGENTS.md`, `CLAUDE.md`, this file, `context-map.yaml`; highest when present: `.archcore/`. Medium-high: `CHANGELOG.md`, `ARCHITECTURE.md`, `ROADMAP.md`. Medium: `memory-bank/`. Low:
`SCRATCHPAD.md`. On need only: `docs/history/` (rotated records, `just history <term>`) and `docs/trackers/` (open items). Generated, never truth: `.ai-context/`. Full table: [reference](/Volumes/Data/_ai/_skills/skills_stuff/specialists/project/skill-ai-it/patterns/navigation/read-order-and-sources.md#project-context-files).

## Task routing

| Question               | Read first                                                                                               |
| ---------------------- | -------------------------------------------------------------------------------------------------------- |
| Architecture or design | `.archcore/adr/`, `.archcore/specs/`, `ARCHITECTURE.md`, `docs/`; never answer from the scratchpad alone |
| Planning or status     | `.archcore/plans/`, `ROADMAP.md`, `CHANGELOG.md`, `memory-bank/`; say so when they disagree              |
| Agents or governance   | `AGENTS.md`, `CLAUDE.md`, this file, `context-map.yaml`, `.archcore/rules/`                              |
| Implementation or code | `AGENTS.md`, `context-map.yaml`, `.archcore/specs/`, the source and its tests                            |
| Documentation          | `.archcore/`, `README.md`, `CHANGELOG.md`, `docs/`; leave companions consistent                          |

## Script and Task Navigation

`just --list` first, then `scripts/README.md`, then any other runner. Never run an uncatalogued script, or one marked `destructive`, `review-required` or `unknown`, without review; propose a catalogue
update when it is stale.

## Governance coherence checks

Run `just check` (or `scripts/check_governance.py`) before calling a durable change done and after adding, moving or retiring a file. When it fails, fix the project, not the check; a new artifact
class, generated output or restated constant extends the checker's registries in the same pass.

## Companion consistency

`AGENTS.md` goes with this file, `context-map.yaml` and `scripts/README.md`; a new script goes with `scripts/README.md`, `justfile` and the checker. `context-map.yaml` `update_rules` is authoritative
for this project.

## Drift handling

When files disagree: stop, name them, say which has higher authority, propose the smallest correction. Never merge conflicting assumptions silently.

## Update rules

Decision: `.archcore/adr/`. Rule: `.archcore/rules/` or `AGENTS.md`. Routing: this file and `context-map.yaml`. Any governance or navigation change: `CHANGELOG.md`. Records over budget: `just budget
--apply`. Full table: [reference](/Volumes/Data/_ai/_skills/skills_stuff/specialists/project/skill-ai-it/patterns/navigation/change-rules.md#update-rules).

## Generated context

`.ai-context/` packs help navigation and are never a source of truth; regenerate after large changes with `repomix --config repomix.config.json`.

## Context compaction recovery

Re-read this file, `.archcore/` and the newest `CHANGELOG.md` entries; check `SCRATCHPAD.md` against the memory backends; confirm companions agree. Steps: [reference](/Volumes/Data/_ai/_skills/skills_stuff/specialists/project/skill-ai-it/patterns/navigation/recovery-and-audit.md#context-compaction-recovery).

## Audit procedure

`just check` and `just stale` cover the mechanical part; the ten manual checks are in the [reference](/Volumes/Data/_ai/_skills/skills_stuff/specialists/project/skill-ai-it/patterns/navigation/recovery-and-audit.md#audit-procedure).

## Agent answer contract

Cite file paths; never invent project state; say "not found in project context" when unsupported; separate confirmed facts from assumptions; ask only when required, otherwise proceed with stated
assumptions.

<!-- END MANAGED: skill-ai-it:navigation -->

## Pack domain routing

Project-authored, outside the managed block. Mirrors the routing table in [SKILL.md](SKILL.md); the governance checker fails when a reference file is missing from either. Ordinary tasks load one reference; three cover VirtualBox, QEMU and libvirt beside Parallels. A Proxmox VM or OpenTofu task starts in [skill-proxmox](../skill-proxmox/SKILL.md); what runs inside the guest starts in that domain's skill.

| Task                                                             | Read first                                  |
| ---------------------------------------------------------------- | ------------------------------------------- |
| Which provider, selection order, multi-provider Vagrantfile, the same task per provider | [references/providers-and-choice.md](references/providers-and-choice.md) |
| VirtualBox: Apple silicon versions, macOS host-only networks, internal networks, VBoxManage, Extension Pack | [references/virtualbox.md](references/virtualbox.md) |
| vagrant-qemu (macOS 27 fix, vmnet/socket modes, serial console) and vagrant-libvirt on a Linux host | [references/qemu-and-libvirt.md](references/qemu-and-libvirt.md) |
| Exact syntax: vagrant CLI, prlctl, prlsrvctl, machine-readable   | [references/operations-cookbook.md](references/operations-cookbook.md) |
| Boxes, versions, constraints, bento builds, the box registry     | [references/boxes-and-pinning.md](references/boxes-and-pinning.md) |
| Vagrantfile shape, multi-machine, provider block, provisioners   | [references/vagrantfile-and-provisioning.md](references/vagrantfile-and-provisioning.md) |
| Shared, host-only, bridged, second adapter, DHCP, synced folders | [references/networking-and-synced-folders.md](references/networking-and-synced-folders.md) |
| prlctl exec, capture, reset, Parallels Tools, editions           | [references/parallels-prlctl.md](references/parallels-prlctl.md) |
| Linked clones, machine-id, snapshots, identity of a copy         | [references/clones-snapshots-and-identity.md](references/clones-snapshots-and-identity.md) |
| Wrong-VM guards, deadlines, quoting, write gates, copies         | [references/lab-safety-and-guards.md](references/lab-safety-and-guards.md) |
| Vagrant or OpenTofu, symmetry with an x86 Proxmox lab            | [references/tool-choice-and-lab-symmetry.md](references/tool-choice-and-lab-symmetry.md) |
| Vagrant licence (MIT, BUSL, MIT again), Parallels editions       | [references/licensing-and-editions.md](references/licensing-and-editions.md) |
| Upgrades, broken shared folders, wedged guests, triage           | [references/upgrade-and-troubleshooting.md](references/upgrade-and-troubleshooting.md) |
| Reusable learning capture and engagement closeout                | [references/evolution-and-write-back.md](references/evolution-and-write-back.md) |

## Pack artifacts

| Artifact                                      | Role                                                                                      | Enforced by                                              |
| --------------------------------------------- | ----------------------------------------------------------------------------------------- | -------------------------------------------------------- |
| [SKILL.md](SKILL.md)                          | Activation surface: role, boundaries, orient-first commands, routing, write-back contract | `tests/test_package_contract.py`                         |
| `references/`                                 | Content source, one focused file per domain; each carries dated Learned entries           | Contract test + `scripts/check_governance.py`            |
| [sources.yaml](sources.yaml)                  | Claim ledger (V-Cnn): statement, evidence rung, source type, reference, scenario          | Contract test schema                                     |
| [compatibility.yaml](compatibility.yaml)      | Environment ledger: product version, validation layer, result                             | Contract test schema                                     |
| [documents/readme.md](documents/readme.md)    | Index of the dated research-source folders                                                | Contract test                                            |
| [documents/research-sources-20261107/readme.md](documents/research-sources-20261107/readme.md) | Verbatim captures with URL, retrieval time and sha256                                     | Contract test (both directions + hash +                  |
|                                               |                                                                                           |   provenance header)                                     |
| [tests/scenarios.md](tests/scenarios.md)      | Evaluation scenarios (V-Snn) each claim links to                                          | Contract test                                            |
| [tests/eval-procedure.md](tests/eval-procedure.md) | How to run a with/without-skill evaluation                                                | —                                                        |
| [scripts/README.md](scripts/README.md)        | Helper and recipe catalog                                                                 | `scripts/check_governance.py`                            |
| [CHANGELOG.md](CHANGELOG.md)                  | Release history; `## Unreleased` collects write-back lines                                | Contract test                                            |
| [.archcore/index.guide.md](.archcore/index.guide.md) | Index of durable ADRs, rules and plans, and what is never promoted                        | `scripts/check_governance.py` (both directions)          |
````

## File: CHANGELOG.md
````markdown
---
Title: Changelog
Category: change-log
Status: current
Summary: Newest entries only; older ones rotate to docs/history.
Authority: record
Scope: Dated changes to this project
Kind: log
Budget: 200 lines, 25 KB
Last reviewed: 2026-11-08
---

# Changelog

## Unreleased

- 2026-11-09 review and online research (operator: "confirm if the skill is defined properly ... do online research"); captures in `documents/research-sources-20261109/`.
- 2026-11-09 references/networking-and-synced-folders.md: vagrant-parallels 2.4.10 drops `big_writes` on libfuse3 guests (issue 526).
- 2026-11-09 references/boxes-and-pinning.md: no post-EOL home for bento yet (RFC 1699); amd64 boxes are not a lab path.
- 2026-11-09 references/vagrantfile-and-provisioning.md: no disk-size option in vagrant-parallels; `prlctl set --device-set hdd0 --size`.
- 2026-11-09 references/licensing-and-editions.md: no Vagrant release after v2.4.9; the Mac runs vagrant-parallels 2.4.10.
- 2026-11-09 references/upgrade-and-troubleshooting.md: `big_writes` triage row; upgrade-order and wedged-guest diagrams.
- 2026-11-09 scope widened to every provider the operator uses (operator: "Vagrant is not only limited to parallels but I also use qemu and
  virtualbox"): new references/providers-and-choice.md, references/virtualbox.md, references/qemu-and-libvirt.md; SKILL.md description, stack
  diagram, orient-first and routing; claims V-C27 to V-C35, scenarios V-S15 to V-S18, environments lab-mac-2026-11-09 and provider-docs-2026-11-09.
- 2026-11-09 diagrams and tables (operator: "add ASCII diagrams and tables"): network topology and DHCP identity, clone chain and copy-identity table,
  what-runs-when matrix, guard flow, registry timeline, ways into a guest.
- 2026-11-09 governance: skill-ai-it refresh (`just govern`); front matter on every reference and test document; `Last reviewed` on the `.archcore/`
  documents; AI_NAVIGATION.md within its 150-line budget; doc-freshness findings fixed, not baselined.

- 2026-11-08 write-back from smc-resiliency S1V: references/parallels-prlctl.md (prlctl exec joins arguments; Tools refusals; stdin uploads; lvextend with a read-only /etc)
- 2026-11-07 (b) write-back from smc-resiliency's lab package: Vagrant transport behind a shared contract (references/operations-cookbook.md)

- 2026-11-07 write-back from smc-resiliency: references/parallels-prlctl.md, references/clones-snapshots-and-identity.md, references/tool-choice-and-lab-symmetry.md (Learned 2026-11-07).

- 20261107 Disputed 2026-11-07 in `references/tool-choice-and-lab-symmetry.md`: a Parallels-maintained OpenTofu provider (parallels/parallels-desktop v0.7.6) exists, against the 2026-11-07 statement
  that none does; the recommendation (Vagrant for local VMs) stands.

## 0.1.0 — 2026-11-07

First release, built to the structure of skill-nautobot (operator, 2026-11-07: "create skill-proxmox and skill-vagrant based on the learnings"; widened the same day: "do online research to add more
knowledge").

- `SKILL.md` and eleven references: operations cookbook (verified against Vagrant 2.4.9, vagrant-parallels 2.4.9, prlctl 27.1.0), boxes and pinning, Vagrantfile and provisioning, networking and synced
  folders, prlctl, clones/snapshots/identity, lab safety and guards, tool choice and lab symmetry, licensing and editions, upgrade and troubleshooting, write-back.
- 95 verbatim research captures in `documents/research-sources-20261107/` (Vagrant docs, vagrant-parallels docs, CHANGELOG and issues, chef/bento issues, the Parallels Desktop 20 Command-Line
  Reference, HashiCorp licence texts, the HCP Vagrant end-of-life notice, OpenTofu registry entries, the Ubuntu snapshot service, systemd machine-id and DUID pages), each with a provenance header and
  sha256. <!-- count:asat -->
- Findings from the research: HCP Vagrant (the public box registry) ends operations on 2026-12-31; Vagrant `main` returned to the MIT licence on 2026-11-02 (releases 2.4.0 to 2.4.9 are BUSL 1.1); a
  vendor OpenTofu provider for Parallels Desktop exists; bento boxes have shipped fixed machine-ids; macOS Local Network privacy can block `vagrant up`.
- `sources.yaml` claims V-C01 to V-C26, `compatibility.yaml` environments, scenarios V-S01 to V-S14 and an evaluation procedure.
- Helpers (stdlib-only, read-only, two-space indentation, a timeout on every call): `vagrant_lab_inventory.py`, `vagrantfile_lint.py`, `vagrant_copy_check.py` (generic form of smc-resiliency
  `check_vagrant_copies`), with recipes `inventory-lab`, `lint-vagrantfile`, `copy-check`; the skill-ai-it governance checker, justfile and navigation layer.
- Worked examples cited with path and commit from the smc-resiliency Pi spike lab (`vagrant_stuff` 8591b72; smc-resiliency 4e436e8d, 2402b961, a124c13a).
- Lab learnings recorded (USER_STATED 2026-11-07): `prlctl exec` hangs on a wedged guest (take `prlctl capture`), errors after a reset until Tools return, `dd` blocked by a hook (use `head -c`),
  `timeout 30"cmd"` read as one word ("invalid time interval"), a linked clone shares the machine-id.

## 20261107_1616 — deterministic navigation-control upgrade

<!-- skill-ai-it-upgrade: 2026-10-14-compact-v2 -->

- Applied `skill-ai-it` deterministic navigation-control upgrade.
- Upgraded managed navigation/scripts blocks to version `2026-10-14-compact-v2`.
- Ensured `context-map.yaml` contains `skill_ai_it_version`, `audit_checks`, `promotion_rules`, `context_recovery`, and `update_rules`.
- Preserved user-authored content outside managed blocks.
- Generated outputs remain support-only; no `.archcore/` promotion was performed.

Applied to: AI_NAVIGATION.md, context-map.yaml, AGENTS.md, scripts/README.md, justfile, scripts/README.md
````

## File: CLAUDE.md
````markdown
@AGENTS.md

## Claude-specific additions
# No project-specific Claude additions at this time.
# Add here only if this project needs Claude Code behaviour that differs from global policy.
````

## File: compatibility.yaml
````yaml
# Environments this skill was verified against: product, version, components and when observed.
environments:
  - id: vagrant-docs-2-4-9
    product: Vagrant documentation
    product_version: 2.4.9
    components: [Vagrantfile, boxes, multi-machine, networking, synced folders, provisioning, triggers, cloud-init, CLI, environment variables]
    observed_at: "2026-11-07"
    evidence_locator: "developer.hashicorp.com/vagrant/docs pages captured verbatim in documents/research-sources-20261107 (served from web-unified-docs content/vagrant/v2.4.9)"
    validation_layer: official_documented
    result: pass
  - id: vagrant-parallels-docs
    product: vagrant-parallels documentation and issue tracker
    product_version: "docs site 2025; CHANGELOG to 2.4.6; releases to 2.4.10"
    components: [configuration, linked clones, customize events, networking, editions, issues]
    observed_at: "2026-11-07"
    evidence_locator: "parallels.github.io/vagrant-parallels/docs and github.com/Parallels/vagrant-parallels issues and CHANGELOG, captured verbatim"
    validation_layer: official_documented
    result: pass
  - id: parallels-cli-reference-20
    product: Parallels Desktop Command-Line Reference
    product_version: "20"
    components: [prlctl, prlsrvctl]
    observed_at: "2026-11-07"
    evidence_locator: "download.parallels.com Parallels Desktop v20 Command-Line Reference PDF (no v26 or v27 PDF published at that path); docs.parallels.com developer guide"
    validation_layer: official_documented
    result: pass
  - id: lab-mac-2026-11-07
    product: Vagrant
    product_version: 2.4.9
    components: ["vagrant-parallels 2.4.9", "prlctl 27.1.0 (58756)", "Parallels Desktop pro edition, licence active", "bento/ubuntu-24.04 202510.26.0 arm64 (Ubuntu 24.04.3, kernel 6.8.0-86)", macOS Apple silicon]
    observed_at: "2026-11-07"
    evidence_locator: "read-only vagrant --version, vagrant plugin list, prlctl --version, prlsrvctl info --license --json (edition and status only), vagrant box list, prlctl list -a -i -j on the operator's Mac; guest release and kernel USER_STATED"
    validation_layer: observed_install
    result: pass
  - id: smc-resiliency-lab-inspected
    product: smc-resiliency Pi spike lab
    product_version: "vagrant_stuff 8591b72; smc-resiliency 4e436e8d, 2402b961, a124c13a"
    components: [Vagrantfile, to_vm.sh, setup_sm.sh, check_vagrant_copies]
    observed_at: "2026-11-07"
    evidence_locator: "source inspected read-only; a project worked example, not generic product behaviour"
    validation_layer: implementation_inspected
    result: pass
  - id: hashicorp-licensing-2026-11
    product: Vagrant licence and HCP Vagrant
    product_version: "v2.3.7 MIT; v2.4.0 to v2.4.9 BUSL 1.1; main MIT since 2026-11-02"
    components: [LICENSE, license FAQ, HCP Vagrant end of life]
    observed_at: "2026-11-07"
    evidence_locator: "github.com/hashicorp/vagrant LICENSE at tags and commit ab4fc5e3db; hashicorp.com license FAQ; developer.hashicorp.com hcp-vagrant-eol"
    validation_layer: official_documented
    result: pass
  - id: registries-2026-11-07
    product: Box and provider registries
    product_version: "bento/ubuntu-24.04 current 202510.26.0; OpenTofu bmatcuk/vagrant v4.1.0; parallels/parallels-desktop v0.7.6"
    components: [vagrantcloud API v2, OpenTofu registry search, Ubuntu snapshot service]
    observed_at: "2026-11-07"
    evidence_locator: "API and page captures in documents/research-sources-20261107"
    validation_layer: official_documented
    result: pass
  - id: helpers-offline-contract
    product: skill-vagrant helpers
    product_version: "pack 0.1.0"
    components: [vagrant_lab_inventory, vagrantfile_lint, vagrant_copy_check, check_governance]
    observed_at: "2026-11-07"
    evidence_locator: "tests/test_helpers.py with faked commands; read-only runs of the inventory and lint on the lab Mac"
    validation_layer: offline_contract
    result: pass
  - id: lab-mac-2026-11-09
    product: Vagrant providers on the lab Mac
    product_version: "Vagrant 2.4.9; macOS 27 (Darwin 27.2)"
    components: ["vagrant-parallels 2.4.9, updated to 2.4.10 the same day", "VirtualBox 7.2.10, upgraded to 7.2.22 the same day, Extension Pack 7.2.22", "vagrant-qemu 0.6.3, updated to 0.7.0 the same day", "QEMU 11.1.3 (Homebrew)", "vagrant-libvirt 0.12.2", "bento/ubuntu-24.04 202510.26.0 for parallels and virtualbox, arm64"]
    observed_at: "2026-11-09"
    evidence_locator: "read-only vagrant plugin list, VBoxManage --version and list extpacks, qemu-system-aarch64 --version, vagrant box list, vagrant global-status on the operator's Mac"
    validation_layer: observed_install
    result: pass
  - id: provider-docs-2026-11-09
    product: VirtualBox, vagrant-qemu, vagrant-libvirt and Vagrant provider documentation
    product_version: "VirtualBox 7.1 and 7.2 changelogs to 7.2.22; vagrant-qemu README and CHANGELOG to 0.7.0; vagrant-libvirt docs main; Vagrant CHANGELOG main"
    components: [Apple silicon support, host-only networks, Extension Pack licence, VBoxManage help, vagrant-qemu options and networking, libvirt connection options, provider selection]
    observed_at: "2026-11-09"
    evidence_locator: "verbatim captures in documents/research-sources-20261109"
    validation_layer: official_documented
    result: pass
````

## File: context-map.yaml
````yaml
# Machine-readable context map: this project's governance files, routing, update rules and generated outputs (skill-ai-it).
version: 1
skill_ai_it_version: "2026-10-14-compact-v2"

project:
  name: "skill-vagrant"
  context_policy: "AI_NAVIGATION.md is the human-readable router; this file is the machine-readable routing map."

bootstrap:
  required_first_read:
    - AGENTS.md
    - AI_NAVIGATION.md
    - context-map.yaml
    - CHANGELOG.md

authority_order:
  - path: ".archcore/adr"
    type: architecture_decisions
    authority: highest
  - path: ".archcore/rules"
    type: durable_rules
    authority: highest
  - path: ".archcore/specs"
    type: design_contracts
    authority: highest
  - path: ".archcore/guides"
    type: operating_guides
    authority: high
  - path: ".archcore/plans"
    type: approved_plans
    authority: high
  - path: "AGENTS.md"
    type: agent_instructions
    authority: high
  - path: "CLAUDE.md"
    type: claude_specific_instructions
    authority: high
  - path: "AI_NAVIGATION.md"
    type: context_router
    authority: high
  - path: "context-map.yaml"
    type: machine_routing_map
    authority: high
  - path: "CHANGELOG.md"
    type: project_history
    authority: medium_high
  - path: "ARCHITECTURE.md"
    type: architecture_overview
    authority: medium_high
  - path: "ROADMAP.md"
    type: roadmap
    authority: medium_high
  - path: "memory-bank/activeContext.md"
    type: active_context
    authority: medium
  - path: "memory-bank/progress.md"
    type: progress_state
    authority: medium
  - path: "memory-bank/decisionLog.md"
    type: working_decision_log
    authority: medium
  - path: "SCRATCHPAD.md"
    type: transient_notes
    authority: low
  - path: "ARCHCORE_PROMOTION_CANDIDATES.md"
    type: promotion_candidates
    authority: generated_support

context_sources:
  archcore:
    enabled: true
    root: ".archcore"
    read_first_for:
      - architecture_decision
      - governance_rule
      - design_contract
      - implementation_plan
      - operating_procedure
      - durable_project_truth

  memory_bank:
    enabled: true
    root: "memory-bank"
    files:
      active_context: "memory-bank/activeContext.md"
      progress: "memory-bank/progress.md"
      decisions: "memory-bank/decisionLog.md"
      patterns: "memory-bank/systemPatterns.md"
      open_questions: "memory-bank/openQuestions.md"

  generated:
    graphify:
      enabled: true
      root: "graphify-out"
      preferred_files:
        - "graphify-out/GRAPH_REPORT.md"
        - "graphify-out/graph.json"

    repomix:
      enabled: true
      root: ".ai-context"
      preferred_files:
        - ".ai-context/governance-pack.md"
        - ".ai-context/repo-pack.md"

routing:
  architecture:
    description: "Architecture, design, topology, components, boundaries, trade-offs."
    read:
      - ".archcore/adr"
      - ".archcore/specs"
      - "ARCHITECTURE.md"
      - "architecture.md"
      - "docs/**/*.md"
    avoid_as_authority:
      - "SCRATCHPAD.md"
      - "scratchpad.md"

  planning:
    description: "Roadmap, work breakdown, current status, next steps."
    read:
      - ".archcore/plans"
      - "ARCHCORE_PROMOTION_CANDIDATES.md"
      - "ROADMAP.md"
      - "roadmap.md"
      - "CHANGELOG.md"
      - "memory-bank/progress.md"
      - "memory-bank/activeContext.md"
      - "SCRATCHPAD.md"

  governance:
    description: "Agent behaviour, project rules, file update rules, workflow rules."
    read:
      - "AGENTS.md"
      - "CLAUDE.md"
      - "AI_NAVIGATION.md"
      - "context-map.yaml"
      - "CHANGELOG.md"
      - ".archcore/rules"
      - "ARCHCORE_PROMOTION_CANDIDATES.md"

  implementation:
    description: "Code, scripts, configs, tests, automation."
    read:
      - "AGENTS.md"
      - "AI_NAVIGATION.md"
      - "context-map.yaml"
      - ".archcore/specs"
      - ".archcore/rules"
      - "src/**"
      - "scripts/**"
      - "tests/**"
    tools:
      preferred:
        - serena
        - graphify
        - repomix
      optional:
        - semgrep
        - markdownlint
        - vale

  scripts:
    purpose: "Project-local scripts, automation, task runners, and executable workflows."
    read_first:
      - "justfile"
      - "Justfile"
      - "scripts/README.md"
      - "Taskfile.yml"
      - "Makefile"
      - "package.json"
    generated_support:
      - "graphify-out"
      - ".ai-context"
    rules:
      - "Respect existing canonical runner first."
      - "Prefer just --list and just <task> when a justfile exists."
      - "Read scripts/README.md before running raw scripts."
      - "Treat uncataloged scripts as unknown safety."
      - "Do not run destructive scripts without explicit review."
      - "Run scripts/check_governance.py before claiming durable work complete; when it fails, fix the project, not the check."

  automation:
    purpose: "Repeatable operational workflows and project task entrypoints."
    read_first:
      - "justfile"
      - "Justfile"
      - "scripts/README.md"
      - "Taskfile.yml"
      - "Makefile"
      - "package.json"
      - "docs/automation.md"
    rules:
      - "Prefer cataloged commands."
      - "Prefer just when a justfile exists."
      - "Confirm inputs, outputs, side effects, and safety before execution."

  documentation:
    description: "README, docs, architecture docs, user guides."
    read:
      - "README.md"
      - "CHANGELOG.md"
      - "docs/**/*.md"
      - "ARCHITECTURE.md"
      - "architecture.md"
      - ".archcore/guides"
      - ".archcore/specs"
      - "memory-bank/activeContext.md"

  troubleshooting:
    description: "Issue investigation, debugging, root cause analysis."
    read:
      - "memory-bank/activeContext.md"
      - "memory-bank/progress.md"
      - "SCRATCHPAD.md"
      - "scratchpad.md"
      - "docs/**/*.md"
      - "logs/**"
      - "reports/**"

update_rules:
  governance_navigation:
    AGENTS.md:
      companions:
        - AI_NAVIGATION.md
        - context-map.yaml
        - scripts/README.md
    AI_NAVIGATION.md:
      companions:
        - context-map.yaml
    context-map.yaml:
      companions:
        - AI_NAVIGATION.md
    scripts/README.md:
      companions:
        - AGENTS.md
        - context-map.yaml
    new_script_added:
      companions:
        - scripts/README.md
        - AGENTS.md
        - justfile
        - scripts/check_governance.py
    # A new artifact class, generated output, or constant restated across files needs the checker's registries
    # extended in the same pass — otherwise the checker measures the project as it was, not as it is.
    new_artifact_class_added:
      companions:
        - scripts/check_governance.py
        - AGENTS.md

  durable_decision:
    update:
      - ".archcore/adr"
    also_consider:
      - "ARCHITECTURE.md"
      - "architecture.md"
      - "memory-bank/decisionLog.md"

  durable_rule:
    update:
      - ".archcore/rules"
    also_consider:
      - "AGENTS.md"
      - "AI_NAVIGATION.md"

  design_contract:
    update:
      - ".archcore/specs"
    also_consider:
      - "ARCHITECTURE.md"
      - "architecture.md"
      - "docs/**/*.md"

  operating_procedure:
    update:
      - ".archcore/guides"
    also_consider:
      - "README.md"
      - "docs/**/*.md"

  plan_change:
    update:
      - ".archcore/plans"
      - "ROADMAP.md"
      - "roadmap.md"
      - "memory-bank/progress.md"

  working_context_change:
    update:
      - "memory-bank/activeContext.md"

  temporary_note:
    update:
      - "SCRATCHPAD.md"

  routing_change:
    update:
      - "AI_NAVIGATION.md"
      - "context-map.yaml"
      - "AGENTS.md"

  governance_history:
    update:
      - "CHANGELOG.md"

  # A new artifact class, generated output, or constant restated across files leaves the checker
  # measuring the project as it was. Extend its registries in the same pass.
  new_artifact_class:
    update:
      - "scripts/check_governance.py"
    also_consider:
      - "AGENTS.md"
      - "scripts/README.md"

drift_policy:
  on_conflict:
    action: "stop_and_report"
    required_output:
      - conflicting_files
      - higher_authority_source
      - recommended_fix
      - assumptions

  scratchpad_rule:
    authoritative: false
    promotion_required_for_durable_truth: true

generated_context_policy:
  regenerate_after:
    - architecture_change
    - major_doc_change
    - roadmap_restructure
    - new_archcore_documents
    - significant_code_restructure

  commands:
    graphify: "graphify update ."
    repomix_governance: "repomix --config repomix.config.json"

audit_checks:
  governance_file_presence:
    - "README.md"
    - "AGENTS.md"
    - "CLAUDE.md"
    - "AI_NAVIGATION.md"
    - "context-map.yaml"
    - "CHANGELOG.md"
  version_consistency:
    description: "Verify managed block version strings match current skill version."
    action: "report_mismatch"
  companion_update_completeness:
    description: "When a governance file changes, verify all companion files in update_rules were also updated."
    action: "report_missing"
  generated_output_policy:
    description: "Verify Graphify and Repomix outputs are classified as generated support, not canonical truth."
    action: "report_violation"
  task_runner_consistency:
    description: "Verify cataloged tasks in scripts/README.md match actual script files."
    action: "report_drift"
  no_stale_references:
    description: "Detect references to removed tools, old task runners, or superseded governance assumptions."
    action: "report_stale"

promotion_rules:
  archcore:
    allowed_init_modes:
      - bootstrap
      - navigation-add
      - refresh
    content_write_modes:
      - promote
    required_authorization: true
    candidates_report: "ARCHCORE_PROMOTION_CANDIDATES.md"
    extract_heuristics_source: "patterns/archcore-routing.md"
    exclusion:
      - "CHANGELOG.md (history only)"
      - "generated files (.ai-context/, graphify-out/)"
      - "unmarked SCRATCHPAD sections"
      - "draft/obsolete roadmap items"

context_recovery:
  procedure:
    - "Read AI_NAVIGATION.md first for navigation map."
    - "Load .archcore/ context if present (durable truth)."
    - "Regenerate graphify-out/ with: graphify update ."
    - "Regenerate .ai-context/ with: repomix --config repomix.config.json"
    - "Verify SCRATCHPAD.md has current state. If empty, populate from memory-keeper / mcp-project-context."
    - "Verify CHANGELOG.md is current."
    - "Verify AI_NAVIGATION.md and context-map.yaml companion consistency."
  evidence_label: "Context recovered at <timestamp> via skill-ai-it context-recovery procedure."

answer_contract:
  require_source_paths: true
  unsupported_answer: "not found in project context"
  distinguish_assumptions: true
  do_not_invent_state: true

# Project-authored: the pack's own artifact map. AI_NAVIGATION.md "Pack domain routing" is the human-readable twin.
pack:
  entrypoint: "SKILL.md"
  content_root: "references"
  claim_ledger: "sources.yaml"
  environment_ledger: "compatibility.yaml"
  doc_snapshots_index: "documents/readme.md"
  research_sources_index: "documents/research-sources-20261107/readme.md"
  helpers: "scripts"
  tests:
    contract: "tests/test_package_contract.py"
    helpers: "tests/test_helpers.py"
    scenarios: "tests/scenarios.md"
    eval_procedure: "tests/eval-procedure.md"
  version_of_record: "CHANGELOG.md release heading (manifest.json is forbidden by the package contract)"
  write_back_contract: "references/evolution-and-write-back.md"
  memory_channel: "vagrant"
  counterpart_skill: "../skill-proxmox"
  references:
    - path: "references/providers-and-choice.md"
      task: "Which provider, selection order, multi-provider Vagrantfile, the same task per provider"
    - path: "references/virtualbox.md"
      task: "VirtualBox: Apple silicon versions, macOS host-only networks, internal networks, VBoxManage, Extension Pack"
    - path: "references/qemu-and-libvirt.md"
      task: "vagrant-qemu (macOS 27 fix, vmnet/socket modes, serial console) and vagrant-libvirt on a Linux host"
    - path: "references/operations-cookbook.md"
      task: "Exact syntax: vagrant CLI, prlctl, prlsrvctl, machine-readable"
    - path: "references/boxes-and-pinning.md"
      task: "Boxes, versions, constraints, bento builds, the box registry"
    - path: "references/vagrantfile-and-provisioning.md"
      task: "Vagrantfile shape, multi-machine, provider block, provisioners"
    - path: "references/networking-and-synced-folders.md"
      task: "Shared, host-only, bridged, second adapter, DHCP, synced folders"
    - path: "references/parallels-prlctl.md"
      task: "prlctl exec, capture, reset, Parallels Tools, editions"
    - path: "references/clones-snapshots-and-identity.md"
      task: "Linked clones, machine-id, snapshots, identity of a copy"
    - path: "references/lab-safety-and-guards.md"
      task: "Wrong-VM guards, deadlines, quoting, write gates, copies"
    - path: "references/tool-choice-and-lab-symmetry.md"
      task: "Vagrant or OpenTofu, symmetry with an x86 Proxmox lab"
    - path: "references/licensing-and-editions.md"
      task: "Vagrant licence (MIT, BUSL, MIT again), Parallels editions"
    - path: "references/upgrade-and-troubleshooting.md"
      task: "Upgrades, broken shared folders, wedged guests, triage"
    - path: "references/evolution-and-write-back.md"
      task: "Reusable learning capture and engagement closeout"
````

## File: justfile
````
# just task catalog for skill-vagrant.
# Purpose:
# - expose safe, documented project tasks to humans and AI agents
# - avoid agents running arbitrary scripts without context
# - keep runnable entrypoints simple and readable
#
# List tasks:
#   just --list
#
# Run task:
#   just <task>
#
# Safety:
# - Prefer safe/read-only tasks by default.
# - Mark destructive tasks clearly and require review.
# - Keep detailed inputs/outputs/safety notes in scripts/README.md.
#
# RUNTIME PINNING — do not replace {{py}} / {{nd}} with bare `python3` or `node`.
# A bare interpreter resolves to whatever the host has on PATH, which is NOT what .mise.toml pins. That works until the
# host changes underneath it and then fails in a way that reads like a code bug. Recipes go through the variables below
# so no recipe depends on the ambient interpreter, and `just runtimes` makes the resolved versions visible.
#
# `mise exec -- python` IS NOT THE FIX, and this is the part that gets missed. Where .mise.toml sets `_.python.venv`,
# `mise exec -- python` does land on the venv — so it tests clean and reads as pinned. But the dependency is IMPLICIT:
# nothing at the call site says which interpreter is meant, and if the activation ever stops applying (the env block is
# edited, the venv is missing, the recipe is copied into a project without that config) it degrades SILENTLY to the host
# interpreter instead of failing. Address the interpreter by PATH via {{py}}, and depend on _require-venv, so a missing
# venv is a loud error with a fix attached rather than a wrong-interpreter run that looks fine.
#
# Node has no venv layer, so `mise exec -- node` is genuinely the explicit form for it — the distinction above applies
# wherever a venv sits between mise and the interpreter, which in practice means Python.
#
# The venv lives in the WORKING-CACHE PEER, never in this repo — a repo carries source, not rebuildable runtime.
# Path mapping (see the global runtime-isolation policy):
#   project_stuff/<group>/<project>  ->  project-working-cache/<group>/<project>
#   mcp_stuff/<project>              ->  mcp-working-cache/<project>
#   skills_stuff/<project>           ->  skills-working-cache/<project>
#   tools_stuff/<project>            ->  tools-working-cache/<project>
#
# `uv run` is deliberately NOT the primary path: it resolves its own interpreter independently of mise, which is the
# same class of drift this pinning removes. Use it only where a recipe needs throwaway third-party packages.

set dotenv-load := false

wc := "/Volumes/Data/_ai/_skills/skills-working-cache/skill-vagrant"
py := wc + "/.venv/bin/python"
ai_it := "/Volumes/Data/_ai/_skills/skills_stuff/specialists/project/skill-ai-it"

# Build the working-cache venv from the mise-pinned runtimes. Safe to re-run.
bootstrap:
    @mkdir -p "{{wc}}"
    @test -f "{{wc}}/.mise.toml" || cp .mise.toml "{{wc}}/.mise.toml"
    @cd "{{wc}}" && mise install && mise exec -- python -m venv .venv
    @{{py}} -m pip install --quiet --upgrade pip -r requirements.txt
    @{{py}} -c "import sys; print('venv ready:', sys.version.split()[0], sys.executable)"

# Fail early and legibly rather than falling back to the host interpreter
_require-venv:
    @test -x "{{py}}" || { echo "venv missing at {{py}} — run: just bootstrap" >&2; exit 1; }

# Report which runtimes the recipes will actually use
runtimes:
    @printf 'python  '; {{py}} -c "import sys; print(sys.version.split()[0], sys.executable)" 2>/dev/null || echo "MISSING — run: just bootstrap"

# List available tasks and show script inventory when present
inventory:
    @just --list
    @test -f scripts/README.md && sed -n '1,220p' scripts/README.md || true

# Audit script/task inventory for obvious drift
audit-scripts:
    @echo "== just recipes =="
    @just --list || true
    @echo
    @echo "== script files =="
    @find scripts -maxdepth 2 -type f 2>/dev/null | sort || true
    @echo
    @echo "== uncataloged script candidates =="
    @if [ -d scripts ] && [ -f scripts/README.md ]; then \
      find scripts -maxdepth 2 -type f | sort | while read -r f; do \
        grep -Fq "$f" scripts/README.md || echo "$f"; \
      done; \
    fi

# Must exit 0 before durable work is called complete. Fix the project when it fails, never the check.
# Governance coherence checks — assert this project's governance claims against reality
check: _require-venv
    @{{py}} scripts/check_governance.py
    @{{py}} "{{ai_it}}/scripts/checks/doc_freshness.py" --project-root . --check
    @{{py}} "{{ai_it}}/scripts/checks/role_check.py" --project-root . --check

# Session preflight: list stale docs by rule (review due, superseded outside archive/, a Depends on file changed). Read-only.
stale: _require-venv
    @{{py}} "{{ai_it}}/scripts/checks/doc_freshness.py" --project-root .

# Triage: one line per file (status, review date, summary) from its header, so a file is judged without being opened
docs *ARGS: _require-venv
    @{{py}} "{{ai_it}}/scripts/checks/file_headers.py" --project-root . {{ARGS}}

# Rotated history on demand: `just history <term>` searches the CHANGELOG archives (SCRATCHPAD: `just history <term> SCRATCHPAD.md`)
history TERM RECORD="CHANGELOG.md": _require-venv
    @{{py}} "{{ai_it}}/scripts/records/rotate_records.py" --project-root . --find "{{TERM}}" {{RECORD}}

# Print one rotated entry by its stamp, when a live entry cites it: `just history-show 20260918_1200`
history-show STAMP RECORD="CHANGELOG.md": _require-venv
    @{{py}} "{{ai_it}}/scripts/records/rotate_records.py" --project-root . --show {{STAMP}} {{RECORD}}

# Keep CHANGELOG and SCRATCHPAD within budget: plan by default; `just rotate --apply` (slurp runs it)
rotate *ARGS: _require-venv
    @{{py}} "{{ai_it}}/scripts/records/rotate_records.py" --project-root . {{ARGS}} CHANGELOG.md
    @{{py}} "{{ai_it}}/scripts/records/rotate_records.py" --project-root . {{ARGS}} SCRATCHPAD.md

# Bring governed files within budget: normalise, rotate, move non-working-state sections out, audit, check. Plan by default; `--apply` to do it
budget *ARGS: _require-venv
    @{{py}} "{{ai_it}}/scripts/records/budget_plan.py" --project-root . {{ARGS}}

# The pack's own offline contract + helper tests (also runs the governance checker via tests/test_helpers.py)
test: _require-venv
    @{{py}} -m unittest discover -s tests -p 'test_*.py'

# The helpers this pack ships (stdlib-only; import them with scripts/ on sys.path)
helpers:
    @ls scripts/*.py | xargs -n1 basename

# Read-only lab inventory: Vagrant environments, Parallels VMs, linked-clone parents, Tools state, boxes and pins.
# e.g. just inventory-lab [--json] [--latest] [--no-edition]   (--latest asks the box registry; network)
[positional-arguments]
inventory-lab *args: _require-venv
    @{{py}} scripts/vagrant_lab_inventory.py "$@"

# Read-only lint of Vagrantfiles as text (exact box pins, provider block and names, customize events, no secrets), e.g. just lint-vagrantfile path/to/Vagrantfile
[positional-arguments]
lint-vagrantfile *args: _require-venv
    @{{py}} scripts/vagrantfile_lint.py "$@"

# Read-only: each project copy of a canonical Vagrantfile is byte-identical, e.g. just copy-check spike/vm/vagrant/x/Vagrantfile=/Volumes/Data/_vagrant/vagrant_stuff/x/Vagrantfile
[positional-arguments]
copy-check *args: _require-venv
    @{{py}} scripts/vagrant_copy_check.py "$@"

# Regenerate the deterministic Repomix context pack (.ai-context/governance-pack.md). Generated support, not truth.
context-pack:
    @command -v repomix >/dev/null || { echo 'repomix not installed; skipped'; exit 0; }
    @repomix --config repomix.config.json --quiet

# Refresh the code graph (graphify-out/: AST only, no LLM). Generated support, not truth.
graph:
    @command -v graphify >/dev/null || { echo 'graphify not installed; skipped'; exit 0; }
    @if [ "${GRAPHIFY_ENABLED:-0}" = 1 ]; then graphify update .; else echo "graphify disabled (operator, 2026-10-10); set GRAPHIFY_ENABLED=1 to run"; fi

# Run safe local preflight checks
preflight: runtimes audit-scripts test check lint-md

# Lint Markdown files when markdownlint-cli2 is available
lint-md:
    @command -v markdownlint-cli2 >/dev/null || { echo 'markdownlint-cli2 not installed; skipped'; exit 0; }
    @markdownlint-cli2 '**/*.md'

# The navigation-control scripts live in the skill package, NOT in this project. Override on the
# command line if the skill lives elsewhere:  just skill_dir=/path/to/skill-ai-it nav-validate
skill_dir := "/Volumes/Data/_ai/_skills/skills_stuff/specialists/project/skill-ai-it"

# Upgrade navigation control layer (dry-run preview)
nav-upgrade-dry-run: _require-venv
	@{{py}} "{{skill_dir}}/scripts/navigation/upgrade_navigation_control_layer.py" --project-root . --dry-run

# Upgrade navigation control layer (apply changes) — review the dry-run first
nav-upgrade: _require-venv
	@{{py}} "{{skill_dir}}/scripts/navigation/upgrade_navigation_control_layer.py" --project-root .

# Validate navigation control layer
nav-validate: _require-venv
	@{{py}} "{{skill_dir}}/scripts/navigation/validate_navigation_control_layer.py" --project-root .

# Check only expected files changed after upgrade (requires a git repo)
nav-check-diff: _require-venv
	@{{py}} "{{skill_dir}}/scripts/navigation/check_expected_diff.py" --project-root .

# Self-test the SKILL PACKAGE's managed-block builders (not this project). Run it after the skill
# package's templates change, before trusting nav-upgrade to rewrite this project's blocks.
nav-selftest: _require-venv
	@{{py}} "{{skill_dir}}/scripts/navigation/selftest_blocks.py"

# Root governance files outside their roles (skill-ai-it references/governed-file-roles.md). Read-only.
roles: _require-venv
    @{{py}} "{{ai_it}}/scripts/checks/role_check.py" --project-root .

# One-step governance to the current skill-ai-it standard: adoption, budgets + check, role findings; content fixes: /skill-ai-it refresh. Modifies files
govern: _require-venv
    #!/usr/bin/env bash
    # Runtime budget: under 60 s on a governed project (measured 2026-10-14 in CHANGELOG); each step prints its own result.
    root="$(cd "." && pwd)" || exit 2
    start=$(date +%s)
    if [ "${GOVERN_ALLOW_DIRTY:-}" != "1" ]; then {{py}} "{{ai_it}}/scripts/checks/govern_guard.py" --project-root "$root" || exit 1; fi
    if grep -q "skill-ai-it-version" "$root/AI_NAVIGATION.md" 2>/dev/null; then
      nav="$(mktemp)"
      {{py}} "{{ai_it}}/scripts/navigation/upgrade_navigation_control_layer.py" --project-root "$root" --dry-run >"$nav" 2>&1
      if grep -qiE "REFUSED|re-serialised|legacy-layout|proposed" "$nav"; then echo "navigation blocks: upgrade needs review, run /skill-ai-it refresh"
      elif grep -q "would" "$nav"; then
        {{py}} "{{ai_it}}/scripts/navigation/upgrade_navigation_control_layer.py" --project-root "$root" | grep -E "^Changed files" || true
      fi
      rm -f "$nav"
    fi
    {{py}} "{{ai_it}}/scripts/adoption/adopt_governed_files.py" --project-root "$root" --apply || exit 1
    {{py}} "{{ai_it}}/scripts/adoption/adopt_code_map.py" --project-root "$root" --apply || exit 1
    log="$(mktemp)"; trap 'rm -f "$log"' EXIT; {{py}} "{{ai_it}}/scripts/records/budget_plan.py" --project-root "$root" --apply | tee "$log"; rc=${PIPESTATUS[0]}
    {{py}} "{{ai_it}}/scripts/checks/doc_freshness.py" --project-root "$root" --prune-baseline; {{py}} "{{ai_it}}/scripts/checks/role_check.py" --project-root "$root" --prune-baseline
    {{py}} "{{ai_it}}/scripts/checks/role_check.py" --project-root "$root"
    echo "govern: $(basename "$root") $([ $rc -eq 0 ] && echo OK || echo "NEEDS ATTENTION: $(grep -Eo 'UNFINISHED: .*|project check: FAILED|audit: (LOST|SPLIT)[^,]*' "$log" | head -1)") in $(( $(date +%s) - start ))s; content fixes: /skill-ai-it refresh"
    exit $rc

# Add a CHANGELOG entry in this project's own heading style and order, with its Contents line: plan by default, `--apply` to write
[positional-arguments]
changelog-entry *ARGS: _require-venv
    @{{py}} "{{ai_it}}/scripts/records/add_changelog_entry.py" --project-root . "$@"

# Move durable reference sections (anchors, procedures) out of a governed file into an on-need doc: plan by default, `--apply` to write
[positional-arguments]
move-sections *ARGS: _require-venv
    @{{py}} "{{ai_it}}/scripts/records/move_sections.py" --project-root . "$@"

# Large Markdown: each heading with its line range, so one section is read instead of the file: `just outline docs/x.md`. Read-only
[positional-arguments]
outline *ARGS: _require-venv
    @{{py}} "{{ai_it}}/scripts/markdown/md_sections.py" --project-root . outline "$@"

# Print one section by title, `Parent > Child` path or #anchor (exact by default, `~text` for a substring): `just section docs/x.md "Stage 1"`. Read-only
[positional-arguments]
section *ARGS: _require-venv
    @{{py}} "{{ai_it}}/scripts/markdown/md_sections.py" --project-root . section "$@"
````

## File: Justfile
````
# just task catalog for skill-vagrant.
# Purpose:
# - expose safe, documented project tasks to humans and AI agents
# - avoid agents running arbitrary scripts without context
# - keep runnable entrypoints simple and readable
#
# List tasks:
#   just --list
#
# Run task:
#   just <task>
#
# Safety:
# - Prefer safe/read-only tasks by default.
# - Mark destructive tasks clearly and require review.
# - Keep detailed inputs/outputs/safety notes in scripts/README.md.
#
# RUNTIME PINNING — do not replace {{py}} / {{nd}} with bare `python3` or `node`.
# A bare interpreter resolves to whatever the host has on PATH, which is NOT what .mise.toml pins. That works until the
# host changes underneath it and then fails in a way that reads like a code bug. Recipes go through the variables below
# so no recipe depends on the ambient interpreter, and `just runtimes` makes the resolved versions visible.
#
# `mise exec -- python` IS NOT THE FIX, and this is the part that gets missed. Where .mise.toml sets `_.python.venv`,
# `mise exec -- python` does land on the venv — so it tests clean and reads as pinned. But the dependency is IMPLICIT:
# nothing at the call site says which interpreter is meant, and if the activation ever stops applying (the env block is
# edited, the venv is missing, the recipe is copied into a project without that config) it degrades SILENTLY to the host
# interpreter instead of failing. Address the interpreter by PATH via {{py}}, and depend on _require-venv, so a missing
# venv is a loud error with a fix attached rather than a wrong-interpreter run that looks fine.
#
# Node has no venv layer, so `mise exec -- node` is genuinely the explicit form for it — the distinction above applies
# wherever a venv sits between mise and the interpreter, which in practice means Python.
#
# The venv lives in the WORKING-CACHE PEER, never in this repo — a repo carries source, not rebuildable runtime.
# Path mapping (see the global runtime-isolation policy):
#   project_stuff/<group>/<project>  ->  project-working-cache/<group>/<project>
#   mcp_stuff/<project>              ->  mcp-working-cache/<project>
#   skills_stuff/<project>           ->  skills-working-cache/<project>
#   tools_stuff/<project>            ->  tools-working-cache/<project>
#
# `uv run` is deliberately NOT the primary path: it resolves its own interpreter independently of mise, which is the
# same class of drift this pinning removes. Use it only where a recipe needs throwaway third-party packages.

set dotenv-load := false

wc := "/Volumes/Data/_ai/_skills/skills-working-cache/skill-vagrant"
py := wc + "/.venv/bin/python"
ai_it := "/Volumes/Data/_ai/_skills/skills_stuff/specialists/project/skill-ai-it"

# Build the working-cache venv from the mise-pinned runtimes. Safe to re-run.
bootstrap:
    @mkdir -p "{{wc}}"
    @test -f "{{wc}}/.mise.toml" || cp .mise.toml "{{wc}}/.mise.toml"
    @cd "{{wc}}" && mise install && mise exec -- python -m venv .venv
    @{{py}} -m pip install --quiet --upgrade pip -r requirements.txt
    @{{py}} -c "import sys; print('venv ready:', sys.version.split()[0], sys.executable)"

# Fail early and legibly rather than falling back to the host interpreter
_require-venv:
    @test -x "{{py}}" || { echo "venv missing at {{py}} — run: just bootstrap" >&2; exit 1; }

# Report which runtimes the recipes will actually use
runtimes:
    @printf 'python  '; {{py}} -c "import sys; print(sys.version.split()[0], sys.executable)" 2>/dev/null || echo "MISSING — run: just bootstrap"

# List available tasks and show script inventory when present
inventory:
    @just --list
    @test -f scripts/README.md && sed -n '1,220p' scripts/README.md || true

# Audit script/task inventory for obvious drift
audit-scripts:
    @echo "== just recipes =="
    @just --list || true
    @echo
    @echo "== script files =="
    @find scripts -maxdepth 2 -type f 2>/dev/null | sort || true
    @echo
    @echo "== uncataloged script candidates =="
    @if [ -d scripts ] && [ -f scripts/README.md ]; then \
      find scripts -maxdepth 2 -type f | sort | while read -r f; do \
        grep -Fq "$f" scripts/README.md || echo "$f"; \
      done; \
    fi

# Must exit 0 before durable work is called complete. Fix the project when it fails, never the check.
# Governance coherence checks — assert this project's governance claims against reality
check: _require-venv
    @{{py}} scripts/check_governance.py
    @{{py}} "{{ai_it}}/scripts/checks/doc_freshness.py" --project-root . --check
    @{{py}} "{{ai_it}}/scripts/checks/role_check.py" --project-root . --check

# Session preflight: list stale docs by rule (review due, superseded outside archive/, a Depends on file changed). Read-only.
stale: _require-venv
    @{{py}} "{{ai_it}}/scripts/checks/doc_freshness.py" --project-root .

# Triage: one line per file (status, review date, summary) from its header, so a file is judged without being opened
docs *ARGS: _require-venv
    @{{py}} "{{ai_it}}/scripts/checks/file_headers.py" --project-root . {{ARGS}}

# Rotated history on demand: `just history <term>` searches the CHANGELOG archives (SCRATCHPAD: `just history <term> SCRATCHPAD.md`)
history TERM RECORD="CHANGELOG.md": _require-venv
    @{{py}} "{{ai_it}}/scripts/records/rotate_records.py" --project-root . --find "{{TERM}}" {{RECORD}}

# Print one rotated entry by its stamp, when a live entry cites it: `just history-show 20260918_1200`
history-show STAMP RECORD="CHANGELOG.md": _require-venv
    @{{py}} "{{ai_it}}/scripts/records/rotate_records.py" --project-root . --show {{STAMP}} {{RECORD}}

# Keep CHANGELOG and SCRATCHPAD within budget: plan by default; `just rotate --apply` (slurp runs it)
rotate *ARGS: _require-venv
    @{{py}} "{{ai_it}}/scripts/records/rotate_records.py" --project-root . {{ARGS}} CHANGELOG.md
    @{{py}} "{{ai_it}}/scripts/records/rotate_records.py" --project-root . {{ARGS}} SCRATCHPAD.md

# Bring governed files within budget: normalise, rotate, move non-working-state sections out, audit, check. Plan by default; `--apply` to do it
budget *ARGS: _require-venv
    @{{py}} "{{ai_it}}/scripts/records/budget_plan.py" --project-root . {{ARGS}}

# The pack's own offline contract + helper tests (also runs the governance checker via tests/test_helpers.py)
test: _require-venv
    @{{py}} -m unittest discover -s tests -p 'test_*.py'

# The helpers this pack ships (stdlib-only; import them with scripts/ on sys.path)
helpers:
    @ls scripts/*.py | xargs -n1 basename

# Read-only lab inventory: Vagrant environments, Parallels VMs, linked-clone parents, Tools state, boxes and pins.
# e.g. just inventory-lab [--json] [--latest] [--no-edition]   (--latest asks the box registry; network)
[positional-arguments]
inventory-lab *args: _require-venv
    @{{py}} scripts/vagrant_lab_inventory.py "$@"

# Read-only lint of Vagrantfiles as text (exact box pins, provider block and names, customize events, no secrets), e.g. just lint-vagrantfile path/to/Vagrantfile
[positional-arguments]
lint-vagrantfile *args: _require-venv
    @{{py}} scripts/vagrantfile_lint.py "$@"

# Read-only: each project copy of a canonical Vagrantfile is byte-identical, e.g. just copy-check spike/vm/vagrant/x/Vagrantfile=/Volumes/Data/_vagrant/vagrant_stuff/x/Vagrantfile
[positional-arguments]
copy-check *args: _require-venv
    @{{py}} scripts/vagrant_copy_check.py "$@"

# Regenerate the deterministic Repomix context pack (.ai-context/governance-pack.md). Generated support, not truth.
context-pack:
    @command -v repomix >/dev/null || { echo 'repomix not installed; skipped'; exit 0; }
    @repomix --config repomix.config.json --quiet

# Refresh the code graph (graphify-out/: AST only, no LLM). Generated support, not truth.
graph:
    @command -v graphify >/dev/null || { echo 'graphify not installed; skipped'; exit 0; }
    @if [ "${GRAPHIFY_ENABLED:-0}" = 1 ]; then graphify update .; else echo "graphify disabled (operator, 2026-10-10); set GRAPHIFY_ENABLED=1 to run"; fi

# Run safe local preflight checks
preflight: runtimes audit-scripts test check lint-md

# Lint Markdown files when markdownlint-cli2 is available
lint-md:
    @command -v markdownlint-cli2 >/dev/null || { echo 'markdownlint-cli2 not installed; skipped'; exit 0; }
    @markdownlint-cli2 '**/*.md'

# The navigation-control scripts live in the skill package, NOT in this project. Override on the
# command line if the skill lives elsewhere:  just skill_dir=/path/to/skill-ai-it nav-validate
skill_dir := "/Volumes/Data/_ai/_skills/skills_stuff/specialists/project/skill-ai-it"

# Upgrade navigation control layer (dry-run preview)
nav-upgrade-dry-run: _require-venv
	@{{py}} "{{skill_dir}}/scripts/navigation/upgrade_navigation_control_layer.py" --project-root . --dry-run

# Upgrade navigation control layer (apply changes) — review the dry-run first
nav-upgrade: _require-venv
	@{{py}} "{{skill_dir}}/scripts/navigation/upgrade_navigation_control_layer.py" --project-root .

# Validate navigation control layer
nav-validate: _require-venv
	@{{py}} "{{skill_dir}}/scripts/navigation/validate_navigation_control_layer.py" --project-root .

# Check only expected files changed after upgrade (requires a git repo)
nav-check-diff: _require-venv
	@{{py}} "{{skill_dir}}/scripts/navigation/check_expected_diff.py" --project-root .

# Self-test the SKILL PACKAGE's managed-block builders (not this project). Run it after the skill
# package's templates change, before trusting nav-upgrade to rewrite this project's blocks.
nav-selftest: _require-venv
	@{{py}} "{{skill_dir}}/scripts/navigation/selftest_blocks.py"

# Root governance files outside their roles (skill-ai-it references/governed-file-roles.md). Read-only.
roles: _require-venv
    @{{py}} "{{ai_it}}/scripts/checks/role_check.py" --project-root .

# One-step governance to the current skill-ai-it standard: adoption, budgets + check, role findings; content fixes: /skill-ai-it refresh. Modifies files
govern: _require-venv
    #!/usr/bin/env bash
    # Runtime budget: under 60 s on a governed project (measured 2026-10-14 in CHANGELOG); each step prints its own result.
    root="$(cd "." && pwd)" || exit 2
    start=$(date +%s)
    if [ "${GOVERN_ALLOW_DIRTY:-}" != "1" ]; then {{py}} "{{ai_it}}/scripts/checks/govern_guard.py" --project-root "$root" || exit 1; fi
    if grep -q "skill-ai-it-version" "$root/AI_NAVIGATION.md" 2>/dev/null; then
      nav="$(mktemp)"
      {{py}} "{{ai_it}}/scripts/navigation/upgrade_navigation_control_layer.py" --project-root "$root" --dry-run >"$nav" 2>&1
      if grep -qiE "REFUSED|re-serialised|legacy-layout|proposed" "$nav"; then echo "navigation blocks: upgrade needs review, run /skill-ai-it refresh"
      elif grep -q "would" "$nav"; then
        {{py}} "{{ai_it}}/scripts/navigation/upgrade_navigation_control_layer.py" --project-root "$root" | grep -E "^Changed files" || true
      fi
      rm -f "$nav"
    fi
    {{py}} "{{ai_it}}/scripts/adoption/adopt_governed_files.py" --project-root "$root" --apply || exit 1
    {{py}} "{{ai_it}}/scripts/adoption/adopt_code_map.py" --project-root "$root" --apply || exit 1
    log="$(mktemp)"; trap 'rm -f "$log"' EXIT; {{py}} "{{ai_it}}/scripts/records/budget_plan.py" --project-root "$root" --apply | tee "$log"; rc=${PIPESTATUS[0]}
    {{py}} "{{ai_it}}/scripts/checks/doc_freshness.py" --project-root "$root" --prune-baseline; {{py}} "{{ai_it}}/scripts/checks/role_check.py" --project-root "$root" --prune-baseline
    {{py}} "{{ai_it}}/scripts/checks/role_check.py" --project-root "$root"
    echo "govern: $(basename "$root") $([ $rc -eq 0 ] && echo OK || echo "NEEDS ATTENTION: $(grep -Eo 'UNFINISHED: .*|project check: FAILED|audit: (LOST|SPLIT)[^,]*' "$log" | head -1)") in $(( $(date +%s) - start ))s; content fixes: /skill-ai-it refresh"
    exit $rc

# Add a CHANGELOG entry in this project's own heading style and order, with its Contents line: plan by default, `--apply` to write
[positional-arguments]
changelog-entry *ARGS: _require-venv
    @{{py}} "{{ai_it}}/scripts/records/add_changelog_entry.py" --project-root . "$@"

# Move durable reference sections (anchors, procedures) out of a governed file into an on-need doc: plan by default, `--apply` to write
[positional-arguments]
move-sections *ARGS: _require-venv
    @{{py}} "{{ai_it}}/scripts/records/move_sections.py" --project-root . "$@"

# Large Markdown: each heading with its line range, so one section is read instead of the file: `just outline docs/x.md`. Read-only
[positional-arguments]
outline *ARGS: _require-venv
    @{{py}} "{{ai_it}}/scripts/markdown/md_sections.py" --project-root . outline "$@"

# Print one section by title, `Parent > Child` path or #anchor (exact by default, `~text` for a substring): `just section docs/x.md "Stage 1"`. Read-only
[positional-arguments]
section *ARGS: _require-venv
    @{{py}} "{{ai_it}}/scripts/markdown/md_sections.py" --project-root . section "$@"
````

## File: README.md
````markdown
---
Title: skill-vagrant
Category: readme
Status: current
Authority: canonical
Scope: Root README.md of skill-vagrant
Last reviewed: 2026-11-07
Summary: "Canonical, cross-project platform pack for local lab VMs with Vagrant and the Parallels provider on macOS Apple silicon: boxes and pins, Vagrantfiles, networks, linked clones and..."
Review by: 2026-12-09
Budget: 200 lines, 25 KB
---

# skill-vagrant

Canonical, cross-project platform pack for local lab VMs with Vagrant and the Parallels provider on macOS Apple silicon: boxes and pins, Vagrantfiles, networks, linked clones and machine-id, prlctl,
lab guards, tool choice and licensing.

## Purpose

Reusable, evidence-graded Vagrant and Parallels knowledge for any project that runs a local lab. Each engagement writes verified reusable findings back here; VM names, lab addresses and stages stay in
the engaging project. The counterpart pack for the x86 lab is [skill-proxmox](../skill-proxmox/SKILL.md); the structure mirrors [skill-nautobot](../skill-nautobot/README.md).

## Folder index

- [references/](references/) — focused content files, one per domain; routed from [SKILL.md](SKILL.md) and [AI_NAVIGATION.md](AI_NAVIGATION.md)
- [documents/](documents/) — verbatim research captures with provenance and sha256. Index: [documents/readme.md](documents/readme.md)
- [scripts/](scripts/) — tested stdlib-only read-only helpers and the governance checker. Index: [scripts/README.md](scripts/README.md)
- [tests/](tests/) — offline package contract, helper tests, scenarios, evaluation procedure
- [.archcore/](.archcore/) — durable decisions, rules and plans (proposed 2026-11-07). Index: [.archcore/index.guide.md](.archcore/index.guide.md)

## Key files

| File               | Role                                                                |
| ------------------ | ------------------------------------------------------------------- |
| [SKILL.md](SKILL.md) | Activation surface — role, boundaries, routing, write-back contract |
| [sources.yaml](sources.yaml) | Claim ledger with evidence rungs                                    |
| [compatibility.yaml](compatibility.yaml) | Environment ledger                                                  |
| [CHANGELOG.md](CHANGELOG.md) | Release history; version of record                                  |
| [justfile](justfile) | Task catalog — `just --list`; `just test` is the completion gate    |

## Governance pointers

- Local agent guidance: [AGENTS.md](AGENTS.md)
- Parent guidance: [../../../AGENTS.md](../../../AGENTS.md)
- AI navigation entrypoint: [AI_NAVIGATION.md](AI_NAVIGATION.md)
- Machine-readable context map: [context-map.yaml](context-map.yaml)
- Pack history: [CHANGELOG.md](CHANGELOG.md)
- Canonical governance root: [/Volumes/Data/_ai/governance/README.md](/Volumes/Data/_ai/governance/README.md)
````

## File: SCRATCHPAD.md
````markdown
---
Title: Scratchpad
Category: working-state
Status: current
Summary: Current working state; older entries rotate to docs/history, older open items to docs/trackers.
Authority: working-state
Scope: Working state between sessions
Kind: state
Budget: 200 lines, 25 KB
Last reviewed: 2026-11-08
Keep: Next actions=1, Memory pointers=1, Session history=2, Current state=3, Recent decisions=3
Open items tracker: docs/trackers/open-items-20261109_1123.md
---

# SCRATCHPAD

Agent working memory for skill-vagrant. Use for: draft plans, terminal output, intermediate analysis, refactor outlines. Cleared between sessions unless content is explicitly marked KEEP.

---

<!-- KEEP: populated 2026-11-07 at creation -->

## Current state

**Phase:** first release, heading in [CHANGELOG.md](CHANGELOG.md); created 2026-11-07 beside skill-nautobot and skill-proxmox, not yet committed.

## Open items

- [ ] `just check` fails (seen 2026-11-08 from smc-resiliency's slurp): files with no header summary (AI_NAVIGATION, .ai-context and others), as in skill-proxmox: pack adoption work, write each summary from its file.
- [ ] Operator review of the four `.archcore/` documents (all `proposed`) — index [.archcore/index.guide.md](.archcore/index.guide.md).
- [ ] Keep the pinned box before the registry closes (2026-12-31): `vagrant box repackage bento/ubuntu-24.04 parallels 202510.26.0`, stored outside the repo with its sha256 (operator's call where).
- [ ] Test on the arm64 lab whether `apt-get update --snapshot <id>` works against `ports.ubuntu.com` (UNVERIFIED in `references/tool-choice-and-lab-symmetry.md`).
- [ ] Test the machine-id reset procedure on a Parallels clone and record the new DHCP lease (UNVERIFIED in `references/clones-snapshots-and-identity.md`).
- [ ] Whether vagrant-parallels delivers `config.vm.cloud_init` data (UNVERIFIED).
- [ ] Re-check the Vagrant LICENSE at the next release tag (MIT revert is on `main` only as of 2026-11-07).
- [ ] Live evaluation per [tests/eval-procedure.md](tests/eval-procedure.md).

## Key anchors

| Item              | Detail                                                                                           |
| ----------------- | ------------------------------------------------------------------------------------------------ |
| Install           | symlinks in `~/.claude/skills`, `~/.agents/skills`, `~/.codex/skills`, `~/.hermes/skills/domain` |
| Observed versions | see `compatibility.yaml` (lab-mac-2026-11-07)                                                    |
| Memory channel    | memory-keeper `vagrant`                                                                          |
| Origin project    | smc-resiliency (Pi spike lab)                                                                    |
| Gate              | `just test` then `just check`                                                                    |
````

## File: SKILL.md
````markdown
---
name: skill-vagrant
description: >-
  Build, pin, run and troubleshoot local Vagrant labs on macOS Apple silicon with any of the operator's providers: Parallels (vagrant-parallels,
  the default), VirtualBox 7.1/7.2, QEMU (vagrant-qemu) and libvirt (vagrant-libvirt against a Linux KVM host). Covers provider choice and
  selection order, boxes and version pinning (bento arm64), multi-machine and multi-provider Vagrantfiles, customize events, networks per provider
  (Parallels shared and host-only, VirtualBox host-only networks and internal networks, QEMU vmnet and socket modes), synced folders, provisioners,
  triggers and cloud-init, `vagrant ssh -c`, prlctl and VBoxManage exec, console capture and power, serial consoles, linked clones and their shared
  machine-id, snapshots, wrong-VM guards, project copies of a canonical Vagrantfile, Vagrant versus OpenTofu, licensing and editions. Use for any
  Vagrant lab VM work; not for Proxmox or OpenTofu (skill-proxmox) and not for what runs inside the guest (that project's skill).
---

# Vagrant

## Contents

- [Role and non-goals](#role-and-non-goals)
- [Read, write, and evidence boundaries](#read-write-and-evidence-boundaries)
- [Orient first](#orient-first)
- [Route the task](#route-the-task)
- [Verify version-sensitive facts](#verify-version-sensitive-facts)
- [Search before building](#search-before-building)
- [Project and lab boundary](#project-and-lab-boundary)
- [Project conventions](#project-conventions)
- [Standing write-back contract](#standing-write-back-contract)

---

## Role and non-goals

Use Vagrant for disposable, reproducible local lab VMs on a Mac: arm64 guests described by a Vagrantfile kept in source control, under Parallels
Desktop by default, or VirtualBox, QEMU, or libvirt on a Linux host ([references/providers-and-choice.md](references/providers-and-choice.md)). Do not use it as a server or fleet
platform (Proxmox with OpenTofu is the x86 lab: skill-proxmox), and do not describe a project's lab layout as product behaviour.

```text
 macOS host (Apple silicon)                                              owner of the knowledge
   Vagrantfile (project copy == vagrant_stuff canonical)                 this pack + the project
     │ vagrant up / ssh / provision / snapshot
   Vagrant 2.4.x ── provider ─┬─► vagrant-parallels ─► prlctl ─► Parallels Desktop   (default)
                              ├─► virtualbox (built in) ─► VBoxManage ─► VirtualBox 7.2
                              ├─► vagrant-qemu ─► qemu-system-aarch64 (hvf, no daemon)
                              └─► vagrant-libvirt ─► qemu+ssh ─► libvirtd on a Linux host
   out of band: prlctl exec / capture, VBoxManage screenshotpng, the QEMU serial socket
     └─ VM: arm64 box + its agent (Parallels Tools, Guest Additions)
          └─ what the guest runs (SMC image, services)                  the workload's skill
 x86 lab VMs on a Proxmox node (OpenTofu)                                skill-proxmox
```

Sibling skills (hand off, do not duplicate): `skill-proxmox` for the x86 lab node, its tokens, SDN and OpenTofu; `skill-coder` before writing or changing a Vagrantfile helper, lab driver or recipe;
`skill-drawio` for a project's lab flow pages; the workload's own skill (for example `skill-smc`) for what runs inside the guest.

## Read, write, and evidence boundaries

Read-only commands (`vagrant status`, `vagrant global-status`, `vagrant box list`, `prlctl list`, `prlctl capture`) need no approval and change no VM. Anything that starts, stops, resets,
reprovisions, clones, snapshots or destroys a VM is a write: print the plan, run it only with the project's `--apply` (or the operator's go-ahead), and put a deadline on every call. A guest is a lab
box until a project says otherwise; never point lab tooling at a site. Keep the observation's source, time and VM name when it may affect a later decision. Do not embed credentials, box tokens or
private addresses in reusable guidance.

## Orient first

On an unfamiliar Mac, establish the tool versions, the provider and edition, and what exists before reading anything else: the provider, the box format and the CLI flags change between releases.

```bash
vagrant --version; vagrant plugin list; prlctl --version; VBoxManage --version; qemu-system-aarch64 --version | head -1
prlsrvctl info --license --json | grep -E '"(edition|status)"'      # Pro, Business or Enterprise is needed for the CLI and the provider
vagrant global-status --machine-readable                             # a cache, with each machine's provider; --prune drops stale rows
echo "${VAGRANT_DEFAULT_PROVIDER:-unset}"                            # decides a bare `vagrant up` (providers-and-choice.md)
vagrant box list --machine-readable; prlctl list -a -i -j            # boxes, and every VM with state, Parent VM and Tools state
```

`scripts/` holds tested, stdlib-only helpers (`just helpers`): `vagrant_lab_inventory.py` (one read-only table of Vagrant machines, Parallels VMs, linked-clone parents, Tools state, boxes and pins),
`vagrantfile_lint.py` (box pinned, provider set, customize events, no secrets) and `vagrant_copy_check.py` (a project copy of a canonical Vagrantfile is byte-identical).

## Route the task

Choose the primary skill by the object **being changed**: a Vagrantfile, box, lab VM (any provider), network adapter or lab guard starts here; a Proxmox VM or OpenTofu plan starts in `skill-proxmox`; what the
guest runs (an SMC image, a Nautobot install) starts in that domain's skill. Ordinary tasks load one reference.

| Task                                                             | Read first                                  |
| ---------------------------------------------------------------- | ------------------------------------------- |
| Which provider, selection order, multi-provider Vagrantfile, the same task per provider | [references/providers-and-choice.md](references/providers-and-choice.md) |
| VirtualBox: Apple silicon versions, macOS host-only networks, internal networks, VBoxManage, Extension Pack | [references/virtualbox.md](references/virtualbox.md) |
| vagrant-qemu (macOS 27 fix, vmnet/socket modes, serial console) and vagrant-libvirt on a Linux host | [references/qemu-and-libvirt.md](references/qemu-and-libvirt.md) |
| Exact syntax: vagrant CLI, prlctl, prlsrvctl, machine-readable   | [references/operations-cookbook.md](references/operations-cookbook.md) |
| Boxes, versions, constraints, bento builds, the box registry     | [references/boxes-and-pinning.md](references/boxes-and-pinning.md) |
| Vagrantfile shape, multi-machine, provider block, provisioners   | [references/vagrantfile-and-provisioning.md](references/vagrantfile-and-provisioning.md) |
| Shared, host-only, bridged, second adapter, DHCP, synced folders | [references/networking-and-synced-folders.md](references/networking-and-synced-folders.md) |
| prlctl exec, capture, reset, Parallels Tools, editions           | [references/parallels-prlctl.md](references/parallels-prlctl.md) |
| Linked clones, machine-id, snapshots, identity of a copy         | [references/clones-snapshots-and-identity.md](references/clones-snapshots-and-identity.md) |
| Wrong-VM guards, deadlines, quoting, write gates, copies         | [references/lab-safety-and-guards.md](references/lab-safety-and-guards.md) |
| Vagrant or OpenTofu, symmetry with an x86 Proxmox lab            | [references/tool-choice-and-lab-symmetry.md](references/tool-choice-and-lab-symmetry.md) |
| Vagrant licence (MIT, BUSL, MIT again), Parallels editions       | [references/licensing-and-editions.md](references/licensing-and-editions.md) |
| Upgrades, broken shared folders, wedged guests, triage           | [references/upgrade-and-troubleshooting.md](references/upgrade-and-troubleshooting.md) |
| Reusable learning capture and engagement closeout                | [references/evolution-and-write-back.md](references/evolution-and-write-back.md) |

## Verify version-sensitive facts

Before asserting a flag, a Vagrantfile key, a provider option or a licence term, read the version-matched source and record it in [sources.yaml](sources.yaml); the verbatim captures are under
`documents/research-sources-20261107/` ([index](documents/research-sources-20261107/readme.md)). Use [compatibility.yaml](compatibility.yaml) only for its stated environment and evidence rung; an observed install is not behavioural proof. Record unknowns as unknown
rather than extrapolating a supported version range.

## Search before building

```text
desired lab outcome
  ↓ a Vagrantfile setting or a built-in command (box_version, define, provision run:, trigger, snapshot)
  ↓ a provider option (vagrant-parallels customize events, linked_clone, update_guest_tools)
  ↓ prlctl / prlsrvctl directly (exec, capture, clone --linked, set --device-set)
  ↓ a small project script with a plan, --apply and a deadline on every call
```

At every downward step, say why the step above cannot do it. Prefer a setting in the Vagrantfile (reviewed, versioned) over a wrapper script.

## Project and lab boundary

Keep VM names, lab subnets, VLANs and the stage a lab serves in the governing project. This skill holds how Vagrant and Parallels behave; a project's worked case (the smc-resiliency Pi spike lab) is
an example, cited with path and commit, not a rule.

## Project conventions

A project that runs a Vagrant lab keeps its canonical Vagrantfile in `vagrant_stuff`, a byte-identical copy in the project, and a check that fails when they differ (smc-resiliency:
`/Volumes/Data/_ai/_project/project_stuff/apn/smc-resiliency/spike/vm/vagrant/` and `check_vagrant_copies`). Check the engaging project's `AGENTS.md` before any write; project rules outrank the
generic guidance here.

## Standing write-back contract

Invoking this skill obliges you to write back what the engagement taught, in any project, before the session ends: a dated Learned entry in the focused reference plus one CHANGELOG line under `##
Unreleased`, read back after writing. Classify every engagement in one sentence (no new learning, verified update, candidate, contradiction, project-only, guest-only). Skill use never authorizes
changing a VM, and editing this source only when the task permits it; otherwise leave the entry in the engaging project. Format, classes and release reconciliation:
[references/evolution-and-write-back.md](references/evolution-and-write-back.md).

**Evidence with every entry (operator, 2026-10-20; every calling project owes it).** A write-back that records how something is done carries (1) a **code excerpt** of the logic that does it: the few
lines that matter (about 30 at most), as a fenced block with its source path and commit, secrets and customer identifiers removed; and (2) for anything with a visual surface (a VM console, the
Parallels Control Center) a **screenshot** as reference (`prlctl capture <vm> --file <png>` for a console), saved under `references/screenshots/<YYYYMMDD>-<slug>/` with a `readme.md` naming each
image, what it shows and where it was taken. Addresses, MACs and serials are redacted or the shot is taken on a lab VM.
````

## File: sources.yaml
````yaml
# Claims this skill makes, each with its kind, evidence status, lifecycle and source. Captures live in documents/research-sources-20261107.
claims:
  - id: V-C01
    statement: "Without box_version Vagrant uses the latest box version satisfying '>= 0', so an unpinned box moves to newer images on recreation."
    kind: generic_invariant
    evidence_status: VERIFIED_PRIMARY
    lifecycle: current
    applies_to: [vagrant-docs-2-4-9]
    environment_id: vagrant-docs-2-4-9
    source_type: official_documentation
    evidence: "research-sources-20261107/vagrant-machine-settings.md (config.vm.box_version); research-sources-20261107/vagrant-box-versioning.md (constraints, ~>)."
    reference: references/boxes-and-pinning.md
    test: V-S01
  - id: V-C02
    statement: "config.vm.box_architecture defaults to :auto, which fetches the host architecture's box."
    kind: generic_invariant
    evidence_status: VERIFIED_PRIMARY
    lifecycle: current
    applies_to: [vagrant-docs-2-4-9]
    environment_id: vagrant-docs-2-4-9
    source_type: official_documentation
    evidence: "research-sources-20261107/vagrant-machine-settings.md (config.vm.box_architecture)."
    reference: references/boxes-and-pinning.md
    test: V-S01
  - id: V-C03
    statement: "HCP Vagrant stopped new box creation on 2026-10-01, ends support on 2026-11-02 and ends operations on 2026-12-31, while the Vagrant CLI remains available."
    kind: generic_invariant
    evidence_status: VERIFIED_PRIMARY
    lifecycle: current
    applies_to: [hashicorp-licensing-2026-11]
    environment_id: hashicorp-licensing-2026-11
    source_type: official_documentation
    evidence: "research-sources-20261107/hcp-vagrant-eol.md; banner also on research-sources-20261107/vagrant-hcp-box-registry.md."
    reference: references/boxes-and-pinning.md
    test: V-S13
  - id: V-C04
    statement: "vagrant box repackage NAME PROVIDER VERSION writes an installed box to the current directory for redistribution."
    kind: generic_invariant
    evidence_status: VERIFIED_PRIMARY
    lifecycle: current
    applies_to: [vagrant-docs-2-4-9]
    environment_id: vagrant-docs-2-4-9
    source_type: official_documentation
    evidence: "research-sources-20261107/vagrant-cli-box.md (box repackage)."
    reference: references/boxes-and-pinning.md
    test: V-S13
  - id: V-C05
    statement: "Since vagrant-parallels 2.0.0 a new machine is a linked clone of the box image, and deleting the box breaks its linked clones."
    kind: generic_invariant
    evidence_status: VERIFIED_PRIMARY
    lifecycle: current
    applies_to: [vagrant-parallels-docs]
    environment_id: vagrant-parallels-docs
    source_type: official_documentation
    evidence: "research-sources-20261107/vp-configuration.md (Full Clone vs Linked Clone); research-sources-20261107/vp-changelog-github.md (2.0.0 breaking change)."
    reference: references/clones-snapshots-and-identity.md
    test: V-S02
  - id: V-C06
    statement: "vagrant-parallels customize runs at pre-boot by default, so it repeats on every boot; post-import runs once after cloning."
    kind: generic_invariant
    evidence_status: VERIFIED_PRIMARY
    lifecycle: current
    applies_to: [vagrant-parallels-docs]
    environment_id: vagrant-parallels-docs
    source_type: official_documentation
    evidence: "research-sources-20261107/vp-configuration.md (Customization with prlctl, supported events)."
    reference: references/vagrantfile-and-provisioning.md
    test: V-S05
  - id: V-C07
    statement: "Provisioners run outside in, and run 'always' or 'never' changes when they run."
    kind: generic_invariant
    evidence_status: VERIFIED_PRIMARY
    lifecycle: current
    applies_to: [vagrant-docs-2-4-9]
    environment_id: vagrant-docs-2-4-9
    source_type: official_documentation
    evidence: "research-sources-20261107/vagrant-provisioning-basic.md."
    reference: references/vagrantfile-and-provisioning.md
    test: V-S05
  - id: V-C08
    statement: "The Parallels provider puts adapter 0 on Shared networking and maps private_network to Host-Only and public_network to Bridged."
    kind: generic_invariant
    evidence_status: VERIFIED_PRIMARY
    lifecycle: current
    applies_to: [vagrant-parallels-docs]
    environment_id: vagrant-parallels-docs
    source_type: official_documentation
    evidence: "research-sources-20261107/vp-networking.md, vp-private-network.md, vp-public-network.md."
    reference: references/networking-and-synced-folders.md
    test: V-S06
  - id: V-C09
    statement: "auto_config false makes Vagrant create a private network adapter without configuring it in the guest."
    kind: generic_invariant
    evidence_status: VERIFIED_PRIMARY
    lifecycle: current
    applies_to: [vagrant-docs-2-4-9]
    environment_id: vagrant-docs-2-4-9
    source_type: official_documentation
    evidence: "research-sources-20261107/vagrant-private-network.md (Disable Auto-Configuration)."
    reference: references/networking-and-synced-folders.md
    test: V-S06
  - id: V-C10
    statement: "systemd-networkd's default DHCP DUID is derived from /etc/machine-id, so VMs sharing a machine-id share a DHCP identity whatever their MACs."
    kind: generic_invariant
    evidence_status: VERIFIED_PRIMARY
    lifecycle: current
    applies_to: [vagrant-parallels-docs]
    environment_id: vagrant-parallels-docs
    source_type: official_documentation
    evidence: "research-sources-20261107/networkd-conf-man.md (DUIDType=vendor default); research-sources-20261107/systemd-network-man.md (ClientIdentifier=duid); seen in research-sources-20261107/vp-issue-441.md and vp-issue-1562.md."
    reference: references/clones-snapshots-and-identity.md
    test: V-S02
  - id: V-C11
    statement: "Several bento Ubuntu box versions shipped a fixed machine-id, giving every VM from them one DHCP lease."
    kind: generic_invariant
    evidence_status: VERIFIED_PRIMARY
    lifecycle: current
    applies_to: [vagrant-parallels-docs]
    environment_id: vagrant-parallels-docs
    source_type: vendor_issue_tracker
    evidence: "research-sources-20261107/vp-issue-1421.md, vp-issue-1473.md, vp-issue-1562.md (chef/bento issues); research-sources-20261107/vp-issue-441.md (vagrant-parallels)."
    reference: references/boxes-and-pinning.md
    test: V-S01
  - id: V-C12
    statement: "A prlctl linked clone of a lab VM kept the source's machine-id, took its DHCP address on the shared network, and vagrant ssh to the source reached the clone."
    kind: worked_example
    evidence_status: USER_STATED
    lifecycle: current
    applies_to: []
    environment_id: null
    source_type: user_policy
    evidence: "smc-resiliency docs/pi/pi-spike-s3-delivery-20261106_1044.md (Linked clone collision) and AGENTS.md Working rules (2026-11-06)."
    reference: references/clones-snapshots-and-identity.md
    test: V-S02
  - id: V-C13
    statement: "prlctl exec runs a command in the guest through Parallels Tools with bash -c on Linux, and prlctl capture writes the screen to a PNG."
    kind: generic_invariant
    evidence_status: VERIFIED_PRIMARY
    lifecycle: current
    applies_to: [parallels-cli-reference-20]
    environment_id: parallels-cli-reference-20
    source_type: official_documentation
    evidence: "research-sources-20261107/parallels-desktop-v20-command-line-reference.pdf pp.19 and 21."
    reference: references/parallels-prlctl.md
    test: V-S04
  - id: V-C14
    statement: "After a reset prlctl exec fails with 'Unable to open new session' or 'PrlJob_GetResult: Invalid argument' until Parallels Tools run again, and it hangs on a wedged guest."
    kind: tested_pattern
    evidence_status: USER_STATED
    lifecycle: current
    applies_to: []
    environment_id: null
    source_type: user_policy
    evidence: "Operator lab learnings 2026-11-07 relayed in the skill-vagrant brief; not in the CLI reference."
    reference: references/parallels-prlctl.md
    test: V-S04
  - id: V-C15
    statement: "prlctl reset is a hard shutdown then start, restart is graceful, and stop uses Parallels Tools or ACPI unless --kill is given."
    kind: generic_invariant
    evidence_status: VERIFIED_PRIMARY
    lifecycle: current
    applies_to: [parallels-cli-reference-20]
    environment_id: parallels-cli-reference-20
    source_type: official_documentation
    evidence: "research-sources-20261107/parallels-desktop-v20-command-line-reference.pdf p.20."
    reference: references/operations-cookbook.md
    test: V-S09
  - id: V-C16
    statement: "The Parallels CLI and the vagrant-parallels provider need the Pro, Business or Enterprise edition; Enterprise was accepted from vagrant-parallels 2.4.3."
    kind: generic_invariant
    evidence_status: VERIFIED_PRIMARY
    lifecycle: current
    applies_to: [vagrant-parallels-docs]
    environment_id: vagrant-parallels-docs
    source_type: official_documentation
    evidence: "research-sources-20261107/parallels-cli-utility.md; research-sources-20261107/vp-installation.md; research-sources-20261107/vp-issue-485.md; research-sources-20261107/vp-changelog-github.md (2.4.3)."
    reference: references/licensing-and-editions.md
    test: V-S08
  - id: V-C17
    statement: "Vagrant up to 2.3.7 is MIT, 2.4.0 to 2.4.9 are BUSL 1.1, and main returned to MIT on 2026-11-02 without a release yet."
    kind: generic_invariant
    evidence_status: VERIFIED_PRIMARY
    lifecycle: current
    applies_to: [hashicorp-licensing-2026-11]
    environment_id: hashicorp-licensing-2026-11
    source_type: official_documentation
    evidence: "research-sources-20261107/vagrant-license-v2.3.7-github.md, vagrant-license-v2.4.9-github.md, vagrant-license-revert-commit-github.md, vagrant-license-github.md."
    reference: references/licensing-and-editions.md
    test: V-S08
  - id: V-C18
    statement: "Under HashiCorp's BSL all non-production use and all production use other than hosting or embedding to compete with HashiCorp's paid version are permitted."
    kind: generic_invariant
    evidence_status: VERIFIED_PRIMARY
    lifecycle: current
    applies_to: [hashicorp-licensing-2026-11]
    environment_id: hashicorp-licensing-2026-11
    source_type: official_documentation
    evidence: "research-sources-20261107/hashicorp-license-faq.md FAQ 8 (last updated 2023-10-17)."
    reference: references/licensing-and-editions.md
    test: V-S08
  - id: V-C19
    statement: "OpenTofu's registry lists the community bmatcuk/vagrant provider (drives a Vagrantfile) and the Parallels-maintained parallels/parallels-desktop provider v0.7.6."
    kind: generic_invariant
    evidence_status: VERIFIED_PRIMARY
    lifecycle: current
    applies_to: [registries-2026-11-07]
    environment_id: registries-2026-11-07
    source_type: official_documentation
    evidence: "research-sources-20261107/opentofu-search-vagrant.md, opentofu-search-parallels.md, opentofu-parallels-desktop.md, tf-vagrant-provider-readme.md."
    reference: references/tool-choice-and-lab-symmetry.md
    test: V-S07
  - id: V-C20
    statement: "Keep Vagrant for local VMs and OpenTofu for Proxmox, and keep the two labs comparable by one apt snapshot date rather than matching base images."
    kind: tested_pattern
    evidence_status: USER_STATED
    lifecycle: current
    applies_to: []
    environment_id: null
    source_type: user_policy
    evidence: "Operator 2026-11-07 (skill-vagrant brief)."
    reference: references/tool-choice-and-lab-symmetry.md
    test: V-S07
  - id: V-C21
    statement: "The Ubuntu snapshot service serves the archive at any UTC time after 2023-03-01 and apt on 24.04 takes --snapshot or a deb822 Snapshot line without other setup."
    kind: generic_invariant
    evidence_status: VERIFIED_PRIMARY
    lifecycle: current
    applies_to: [registries-2026-11-07]
    environment_id: registries-2026-11-07
    source_type: official_documentation
    evidence: "research-sources-20261107/ubuntu-snapshot-docs.md; research-sources-20261107/ubuntu-snapshot-service.md."
    reference: references/tool-choice-and-lab-symmetry.md
    test: V-S07
  - id: V-C22
    statement: "A lab driver refuses the wrong VM by testing an in-guest marker in the same remote command and exiting with a distinct code."
    kind: worked_example
    evidence_status: VERIFIED_PRIMARY
    lifecycle: current
    applies_to: [smc-resiliency-lab-inspected]
    environment_id: smc-resiliency-lab-inspected
    source_type: implementation
    evidence: "smc-resiliency spike/to_vm.sh @ 4e436e8d (on_vm, /boot/smc-ramcow-installed, exit 97)."
    reference: references/lab-safety-and-guards.md
    test: V-S03
  - id: V-C23
    statement: "A project keeps a byte-identical copy of its canonical lab Vagrantfile and a check that fails on a missing or different copy."
    kind: worked_example
    evidence_status: VERIFIED_PRIMARY
    lifecycle: current
    applies_to: [smc-resiliency-lab-inspected]
    environment_id: smc-resiliency-lab-inspected
    source_type: implementation
    evidence: "smc-resiliency scripts/govcheck/checks/paths.py @ a124c13a (check_vagrant_copies); operator rule 2026-10-21 in apn/AGENTS.md."
    reference: references/lab-safety-and-guards.md
    test: V-S11
  - id: V-C24
    statement: "vagrant-parallels 2.4.4 mounts shared folders with prl_fsd when present, fixing 'prl_fs not available' after Parallels Desktop 20.2."
    kind: generic_invariant
    evidence_status: VERIFIED_PRIMARY
    lifecycle: current
    applies_to: [vagrant-parallels-docs]
    environment_id: vagrant-parallels-docs
    source_type: vendor_issue_tracker
    evidence: "research-sources-20261107/vp-issue-483.md; research-sources-20261107/vp-changelog-github.md (2.4.4)."
    reference: references/upgrade-and-troubleshooting.md
    test: V-S10
  - id: V-C25
    statement: "The observed lab Mac runs Vagrant 2.4.9, vagrant-parallels 2.4.9 and prlctl 27.1.0 with a pro edition licence, and bento/ubuntu-24.04 202510.26.0 boots Ubuntu 24.04.3 with kernel 6.8.0-86."
    kind: worked_example
    evidence_status: VERIFIED_PRIMARY
    lifecycle: current
    applies_to: [lab-mac-2026-11-07]
    environment_id: lab-mac-2026-11-07
    source_type: observed_install
    evidence: "Read-only version commands on 2026-11-07; guest release and kernel USER_STATED in the brief."
    reference: references/operations-cookbook.md
    test: V-S09
  - id: V-C26
    statement: "Every write-back carries a dated Learned entry in the focused reference and a CHANGELOG line naming that file and date."
    kind: generic_invariant
    evidence_status: USER_STATED
    lifecycle: current
    applies_to: []
    environment_id: null
    source_type: user_policy
    evidence: "Operator write-back contract shared with skill-nautobot (2026-10-05, evidence rule 2026-10-20)."
    reference: references/evolution-and-write-back.md
    test: V-S12
  - id: V-C27
    statement: "Vagrant picks a provider by --provider, then VAGRANT_DEFAULT_PROVIDER, then the first usable config.vm.provider block in file order, then installed plugins by priority."
    kind: generic_invariant
    evidence_status: VERIFIED_PRIMARY
    lifecycle: current
    applies_to: [provider-docs-2026-11-09]
    environment_id: provider-docs-2026-11-09
    source_type: official_documentation
    evidence: "research-sources-20261109/vagrant-providers-basic_usage.md; research-sources-20261109/vagrant-providers-default.md."
    reference: references/providers-and-choice.md
    test: V-S15
  - id: V-C28
    statement: "VirtualBox virtualizes Arm Linux and BSD guests on a macOS Arm host from 7.1.0; bento's arm64 VirtualBox boxes need 7.1.6 or later; Arm saved states from 7.1 do not restore on 7.2."
    kind: generic_invariant
    evidence_status: VERIFIED_PRIMARY
    lifecycle: current
    applies_to: [provider-docs-2026-11-09]
    environment_id: provider-docs-2026-11-09
    source_type: official_documentation
    evidence: "research-sources-20261109/virtualbox-changelog-7.1.md; research-sources-20261109/virtualbox-changelog-7.2.md; research-sources-20261107/bento-readme-github.md."
    reference: references/virtualbox.md
    test: V-S16
  - id: V-C29
    statement: "Vagrant supports VirtualBox 7.1 from 2.4.2 and 7.2 from 2.4.9, and uses VirtualBox host-only networks for private_network on macOS from 2.3.3."
    kind: generic_invariant
    evidence_status: VERIFIED_PRIMARY
    lifecycle: current
    applies_to: [provider-docs-2026-11-09]
    environment_id: provider-docs-2026-11-09
    source_type: official_documentation
    evidence: "research-sources-20261109/vagrant-changelog-main-github.md (GH-13513, GH-13709); research-sources-20261109/vagrant-pr-12983.md."
    reference: references/virtualbox.md
    test: V-S16
  - id: V-C30
    statement: "On macOS, VirtualBox has host-only networks, not host-only adapters; host-only addresses are limited to VirtualBox's default range unless /etc/vbox/networks.conf allows more."
    kind: generic_invariant
    evidence_status: VERIFIED_PRIMARY
    lifecycle: current
    applies_to: [provider-docs-2026-11-09]
    environment_id: provider-docs-2026-11-09
    source_type: official_documentation
    evidence: "research-sources-20261109/virtualbox-manual-networking.md."
    reference: references/virtualbox.md
    test: V-S16
  - id: V-C31
    statement: "The VirtualBox base package is GPLv3; the Oracle Extension Pack is under the PUEL, which excludes business use without a paid licence, and Vagrant does not need it."
    kind: generic_invariant
    evidence_status: VERIFIED_PRIMARY
    lifecycle: current
    applies_to: [provider-docs-2026-11-09]
    environment_id: provider-docs-2026-11-09
    source_type: official_documentation
    evidence: "research-sources-20261109/virtualbox-licensing-faq.md."
    reference: references/virtualbox.md
    test: V-S17
  - id: V-C32
    statement: "vagrant-qemu 0.6.4 fixes a false ForwardPortCollision on macOS 27; 0.7.0 adds VirtioFS folders, vagrant serial-config and growing the primary disk."
    kind: generic_invariant
    evidence_status: VERIFIED_PRIMARY
    lifecycle: current
    applies_to: [provider-docs-2026-11-09]
    environment_id: provider-docs-2026-11-09
    source_type: official_documentation
    evidence: "research-sources-20261109/vq-changelog-github.md (0.6.4, 0.7.0)."
    reference: references/qemu-and-libvirt.md
    test: V-S18
  - id: V-C33
    statement: "vagrant-qemu ignores private_network unless advanced_network is set; on macOS vmnet needs sudo, socket_vmnet avoids root, and socket listen/connect links exactly two VMs."
    kind: generic_invariant
    evidence_status: VERIFIED_PRIMARY
    lifecycle: current
    applies_to: [provider-docs-2026-11-09]
    environment_id: provider-docs-2026-11-09
    source_type: official_documentation
    evidence: "research-sources-20261109/vq-readme-github.md (Platform support and notes)."
    reference: references/qemu-and-libvirt.md
    test: V-S18
  - id: V-C34
    statement: "vagrant-libvirt reaches a remote libvirtd through a connection URI and needs connect_via_ssh (or a qemu+ssh uri) to learn a remote VM's address."
    kind: generic_invariant
    evidence_status: VERIFIED_PRIMARY
    lifecycle: current
    applies_to: [provider-docs-2026-11-09]
    environment_id: provider-docs-2026-11-09
    source_type: official_documentation
    evidence: "research-sources-20261109/vl-configuration-github.md (Connection Options)."
    reference: references/qemu-and-libvirt.md
    test: V-S18
  - id: V-C35
    statement: "The lab Mac runs four Vagrant providers: vagrant-parallels 2.4.10, VirtualBox 7.2.22, vagrant-qemu 0.7.0 (all updated on 2026-11-09) with QEMU 11.1.3, and vagrant-libvirt 0.12.2."
    kind: worked_example
    evidence_status: VERIFIED_PRIMARY
    lifecycle: current
    applies_to: [lab-mac-2026-11-09]
    environment_id: lab-mac-2026-11-09
    source_type: observed_install
    evidence: "Read-only version commands on 2026-11-09."
    reference: references/providers-and-choice.md
    test: V-S15
````
