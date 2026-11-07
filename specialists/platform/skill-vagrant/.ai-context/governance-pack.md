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
  tool-choice-and-lab-symmetry.md
  upgrade-and-troubleshooting.md
  vagrantfile-and-provisioning.md
scripts/
  check_governance.py
  README.md
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
tags: [pack-boundary, vagrant]
created: 2026-11-07
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
````

## File: .archcore/plans/keep-the-pinned-box-before-registry-eol.plan.md
````markdown
---
title: Keep the pinned box before the box registry closes
type: plan
status: proposed
tags: [boxes, registry]
created: 2026-11-07
---

# Plan: Keep the pinned box before the box registry closes

Status: proposed (2026-11-07), awaiting the operator.

## Why

HCP Vagrant, which serves `bento/...` boxes, ends operations on 2026-12-31 (`documents/research-sources-20261107/hcp-vagrant-eol.md`). A lab pinned to `bento/ubuntu-24.04` `202510.26.0`
cannot be rebuilt from the pin after that unless the box is kept or rehosted.

## Steps

1. Operator chooses a storage place outside any git repo (the box is about 3.5 GB).
2. `vagrant box repackage bento/ubuntu-24.04 parallels 202510.26.0` in that place; record the file's sha256 beside it.
3. Record the location and hash in the engaging project (smc-resiliency) and a Learned entry in `references/boxes-and-pinning.md`.
4. Test the restore on a scratch name (`vagrant box add --name lab/ubuntu-24.04-202510.26.0 <file>`) without touching the running lab.
5. Watch for where bento publishes after 2026-12-31 and update the reference.

## Done when

The file, its hash and a tested restore command are recorded; no running VM was touched.
````

## File: .archcore/rules/lab-writes-stay-in-the-project.rule.md
````markdown
---
title: VM writes stay in the engaging project
type: rule
status: proposed
tags: [safety]
created: 2026-11-07
---

# Rule: VM writes stay in the engaging project

Status: proposed (2026-11-07), awaiting the operator.

## Rule

This pack's helpers and its own sessions run read-only `vagrant` and `prlctl` commands only (status, list, box list, global-status, capture). Starting, stopping, resetting, cloning,
snapshotting, reprovisioning or destroying a VM is done by the engaging project's tooling, behind its plan/`--apply` gate, with a fixed lab VM name and a deadline on every call.

## Why

The pack is shared by every project; a write helper here would run without the project's guards (its wrong-VM marker, its disk guard, its stage records). The brief that created the
pack said: "Do not start, stop, reset or change any VM; read-only vagrant/prlctl commands only."

## Enforcement

`tests/test_package_contract.py` requires a timeout on every subprocess call in `scripts/`; `scripts/README.md` labels each helper; a helper that writes would need a new rule here first.
````

## File: .archcore/rules/memory-channel-name.rule.md
````markdown
---
title: Memory channel is exactly vagrant
type: rule
status: proposed
tags: [memory]
created: 2026-11-07
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

## File: .archcore/index.guide.md
````markdown
---
title: Archcore index — skill-vagrant
status: accepted
tags: [index]
---

Durable index of everything in `.archcore/` for skill-vagrant. Written at creation on 2026-11-07. Every document below is `proposed` until the operator accepts it; supersede an accepted
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

The public box catalog is the HCP Vagrant Box Registry (formerly Vagrant Cloud) (VERIFIED_PRIMARY, [vagrant-hcp-box-registry.md], [vagrant-box-catalog.md]).
Its v2 API answers `GET https://vagrantcloud.com/api/v2/box/<user>/<name>` with every version, its status and its providers and architectures (observed
2026-11-07, [bento-ubuntu-2404-api.md]); `vagrant_lab_inventory.py --latest` reads it to compare a pin with the newest release. Box versions are
`unreleased`, `active` or `revoked` ([vagrant-box-versioning-cloud.md]).

**The registry is being shut down.** HashiCorp's notice (VERIFIED_PRIMARY, [hcp-vagrant-eol.md], also on every Vagrant Cloud docs page): no new boxes
from 2026-10-01, end of support and maintenance 2026-11-02, end of operations 2026-12-31, "all deployments will be decommissioned". The Vagrant CLI
stays; boxes must be hosted by their owners. Consequences for a lab:

- A pin such as `bento/ubuntu-24.04` `202510.26.0` resolves only while the registry (or a replacement location bento announces) serves it. Where bento
  will publish after 2026-12-31 is UNVERIFIED (its README still points to Vagrant Cloud, [bento-readme-github.md]).
- Keep the pinned box locally now: `vagrant box repackage NAME PROVIDER VERSION` writes the installed box to the current directory "so you can
  redistribute it" (VERIFIED_PRIMARY, [vagrant-cli-box.md]); store it outside the repo (it is gigabytes) with its sha256, and record where.
- Rebuild path: `vagrant box add <name> <file-or-url>` with a box metadata file for versioned self-hosting, or build the box with bento's Packer
  templates.

## Removing boxes

With vagrant-parallels, a new machine is a linked clone of the box image by default; "the box deletion will make all its linked clones not working"
(VERIFIED_PRIMARY, [vp-configuration.md]). Before `vagrant box remove` or `vagrant box prune`, list which machines were created from that box version
(`vagrant_lab_inventory.py` joins machine homes to their Vagrantfile pins). `vagrant box prune --dry-run` prints what it would remove; `--force
--keep-active-boxes` keeps boxes in use (VERIFIED_PRIMARY, [vagrant-cli-box.md]). With the registry closing, a pruned version may not be downloadable
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
````

## File: references/evolution-and-write-back.md
````markdown
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

The provider plugin is open source under the MIT licence (VERIFIED_PRIMARY, [vp-readme-github.md]). Latest release v2.4.10 on 2026-10-28; the lab Mac runs 2.4.9 (observed 2026-11-07).

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
````

## File: references/operations-cookbook.md
````markdown
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
````

## File: references/parallels-prlctl.md
````markdown
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
````

## File: references/tool-choice-and-lab-symmetry.md
````markdown
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
````

## File: references/upgrade-and-troubleshooting.md
````markdown
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

Parallels Desktop first (it carries the CLI and Tools), then `vagrant plugin update vagrant-parallels`, then Vagrant itself; if plugins fail to load after a Vagrant upgrade, `vagrant plugin repair` is
the command for it (UNVERIFIED: not in the captured docs); the order is a recommendation, UNVERIFIED as a vendor statement. Then: `vagrant up` one machine, check Tools state, shared folders and
`prlctl exec`, and only then the rest. Parallels Tools in existing guests stay at their old version until updated (`update_guest_tools` or the Parallels menu); `outdated` Tools kept working for exec
and shutdown in the lab (observed 2026-11-07).

## Triage table

| Symptom                                                            | Likely cause                                    | Check                                        | Source                         |
| ------------------------------------------------------------------ | ----------------------------------------------- | -------------------------------------------- | ------------------------------ |
| "Vagrant has detected that you have an edition of Parallels        | Standard edition, or Enterprise with            | `prlsrvctl info --license --json` (edition   | [vp-issue-485.md]              |
|   Desktop for Mac installed that is not supported"                 |   vagrant-parallels before 2.4.3                |   only), `vagrant plugin list`               |                                |
| Two VMs, one IP; `vagrant ssh` reaches the wrong VM                | same `/etc/machine-id` (box regression or       | `cat /etc/machine-id` on                     | [vp-issue-441.md],             |
|                                                                    |   a clone)                                      |   both; `prlctl list -a -f`                  |   [vp-issue-1562.md]           |
| "Vagrant was unable to mount Parallels Desktop shared folders      | Parallels 20.2 moved to `prl_fsd`; plugin       | `vagrant plugin list`; Tools state           | [vp-issue-483.md]              |
|   ... prl_fs"                                                      |   before 2.4.4                                  |                                              |                                |
| Shared folder fails on an Ubuntu 26.04 guest | AppArmor blocks `prl_fsd`/`fusermount3` | `journalctl -k -g apparmor` in the guest | [vp-issue-522.md] |
| Static private IP lands on a new interface (Fedora 36+)            | Vagrant's network configuration for that guest  | `ip addr` in the guest                       | [vp-issue-462.md]              |
| Error with more than four networks on Apple silicon                | Parallels limit on M-series (reported)          | count `vm.network` lines                     | [vp-issue-410.md]              |
| `prlctl exec`: "Unable to open new session", "PrlJob_GetResult:    | Tools not running yet after a reset or reboot   | retry with a deadline; `prlctl capture`      | USER_STATED, lab 2026-11-07    |
|   Invalid argument"                                                |                                                 |                                              |                                |
| `prlctl exec` hangs                                                | guest wedged (panic, emergency shell,           | `prlctl capture <vm> --file x.png`           | USER_STATED, lab 2026-11-07    |
|                                                                    |   full disk)                                    |                                              |                                |
| `timeout: invalid time interval`                                   | a wrapper wrote `timeout 30"cmd"` (one word)    | the wrapper's quoting                        | USER_STATED, lab 2026-11-07    |
| `vagrant global-status` lists a machine that is gone               | it reads a cache                                | `vagrant global-status --prune`              | [vagrant-cli-global-status.md] |
| A linked clone stopped working after `vagrant box remove`/`prune`  | the clone's disk depends on the box image       | `vagrant box list`; restore the box from a   | [vp-configuration.md]          |
|                                                                    |                                                 |   repackaged file                            |                                |
| A second disk appears on every boot                                | a `customize` adding a device                   | `vagrantfile_lint.py`                        | [vp-configuration.md]          |
|                                                                    |   without `post-import`                         |                                              |                                |
| `vagrant up` waits with "Host unreachable. Retrying..." after a macOS upgrade (Sequoia 15.5) | macOS Local Network privacy denies the terminal app access to the VM network | System Settings, Privacy & Security, Local Network: allow the terminal and editor | [vp-issue-510.md] (reporter's fix, VERIFIED_SECONDARY) |
| Files missing or stale after `vagrant upload` of a folder          | upload into an existing directory               | upload to a fresh path per run               | USER_STATED,                   |
|                                                                    |                                                 |                                              |   smc-resiliency 2026-11-06    |

## A wedged guest

1. `prlctl capture <vm> --file <png>` and look at it: that decides everything else.
2. A login prompt: the guest is up; Tools or the network are not. Wait and retry `prlctl exec <vm> true` with a deadline; check `prlctl list -i` for `GuestTools.state`.
3. A panic, emergency or initramfs shell, a GRUB prompt: the boot itself failed. Record the capture; then `prlctl reset <vm>` (a write) or roll back a snapshot; for a lab under test, the capture is
   the result.
4. A blank console: `prlctl status <vm>`; a suspended VM resumes with `prlctl start`, `prlctl stop --drop-state` discards the state.
````

## File: references/vagrantfile-and-provisioning.md
````markdown
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
````

## File: AGENTS.md
````markdown
@../../../AGENTS.md

Title: skill-vagrant Agent Policy
Category: agent-governance-guide
Status: current
Authority: local-supplement
Scope: skill-vagrant platform pack — canonical, cross-project source of reusable Vagrant and Parallels lab knowledge
Last reviewed: 20261107_1700
Summary: Agent guidance for maintaining and using skill-vagrant: artifact roles, the package contract, the write-back obligation, the boundary with skill-proxmox, and the gates to run before
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
# AI Navigation — skill-vagrant

Purpose: this file is the project context entrypoint for AI agents. It tells agents where project truth lives, what to read first, what is authoritative, what is temporary, and what must be updated
after work.

This file is a router, not the full knowledge store.

<!-- This Contents block sits OUTSIDE the managed markers on purpose: it indexes the whole file,
     including any project-authored sections below the END marker, and the upgrader regenerates
     everything between the markers. Keep it updated when sections are added either side. -->

## Contents

- [Mandatory read order](#mandatory-read-order)
- [Source priority](#source-priority)
- [Project context files](#project-context-files)
- [Task routing](#task-routing)
  - [Architecture/design questions](#architecturedesign-questions)
  - [Planning/status questions](#planningstatus-questions)
  - [Agent/governance questions](#agentgovernance-questions)
  - [Implementation/code questions](#implementationcode-questions)
- [Script and Task Navigation](#script-and-task-navigation)
  - [Documentation updates](#documentation-updates)
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
`SCRATCHPAD.md`. On need only: `docs/history/` (rotated records, `just history <term>`) and `docs/trackers/` (open items). Generated, never truth: `.ai-context/`. Full table:
[reference](/Volumes/Data/_ai/_skills/skills_stuff/specialists/project/skill-ai-it/patterns/navigation/read-order-and-sources.md#project-context-files).

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

Re-read this file, `.archcore/` and the newest `CHANGELOG.md` entries; check `SCRATCHPAD.md` against the memory backends; confirm companions agree. Steps:
[reference](/Volumes/Data/_ai/_skills/skills_stuff/specialists/project/skill-ai-it/patterns/navigation/recovery-and-audit.md#context-compaction-recovery).

## Audit procedure

`just check` and `just stale` cover the mechanical part; the ten manual checks are in the
[reference](/Volumes/Data/_ai/_skills/skills_stuff/specialists/project/skill-ai-it/patterns/navigation/recovery-and-audit.md#audit-procedure).

## Agent answer contract

Cite file paths; never invent project state; say "not found in project context" when unsupported; separate confirmed facts from assumptions; ask only when required, otherwise proceed with stated
assumptions.

<!-- END MANAGED: skill-ai-it:navigation -->

## Pack domain routing

Project-authored, outside the managed block. Mirrors the routing table in [SKILL.md](SKILL.md); the governance checker fails when a reference file is missing from either.
Ordinary tasks load one reference. A Proxmox VM or OpenTofu task starts in [skill-proxmox](../skill-proxmox/SKILL.md); what runs inside the guest starts in that domain's skill.

| Task | Read first |
|---|---|
| Exact syntax: vagrant CLI, prlctl, prlsrvctl, machine-readable | [references/operations-cookbook.md](references/operations-cookbook.md) |
| Boxes, versions, constraints, bento builds, the box registry | [references/boxes-and-pinning.md](references/boxes-and-pinning.md) |
| Vagrantfile shape, multi-machine, provider block, provisioners | [references/vagrantfile-and-provisioning.md](references/vagrantfile-and-provisioning.md) |
| Shared, host-only, bridged, second adapter, DHCP, synced folders | [references/networking-and-synced-folders.md](references/networking-and-synced-folders.md) |
| prlctl exec, capture, reset, Parallels Tools, editions | [references/parallels-prlctl.md](references/parallels-prlctl.md) |
| Linked clones, machine-id, snapshots, identity of a copy | [references/clones-snapshots-and-identity.md](references/clones-snapshots-and-identity.md) |
| Wrong-VM guards, deadlines, quoting, write gates, copies | [references/lab-safety-and-guards.md](references/lab-safety-and-guards.md) |
| Vagrant or OpenTofu, symmetry with an x86 Proxmox lab | [references/tool-choice-and-lab-symmetry.md](references/tool-choice-and-lab-symmetry.md) |
| Vagrant licence (MIT, BUSL, MIT again), Parallels editions | [references/licensing-and-editions.md](references/licensing-and-editions.md) |
| Upgrades, broken shared folders, wedged guests, triage | [references/upgrade-and-troubleshooting.md](references/upgrade-and-troubleshooting.md) |
| Reusable learning capture and engagement closeout | [references/evolution-and-write-back.md](references/evolution-and-write-back.md) |

## Pack artifacts

| Artifact | Role | Enforced by |
|---|---|---|
| [SKILL.md](SKILL.md) | Activation surface: role, boundaries, orient-first commands, routing, write-back contract | `tests/test_package_contract.py` |
| `references/` | Content source, one focused file per domain; each carries dated Learned entries | Contract test + `scripts/check_governance.py` |
| [sources.yaml](sources.yaml) | Claim ledger (V-Cnn): statement, evidence rung, source type, reference, scenario | Contract test schema |
| [compatibility.yaml](compatibility.yaml) | Environment ledger: product version, validation layer, result | Contract test schema |
| [documents/readme.md](documents/readme.md) | Index of the dated research-source folders | Contract test |
| [documents/research-sources-20261107/readme.md](documents/research-sources-20261107/readme.md) | Verbatim captures with URL, retrieval time and sha256 | Contract test (both directions + hash + provenance header) |
| [tests/scenarios.md](tests/scenarios.md) | Evaluation scenarios (V-Snn) each claim links to | Contract test |
| [tests/eval-procedure.md](tests/eval-procedure.md) | How to run a with/without-skill evaluation | — |
| [scripts/README.md](scripts/README.md) | Helper and recipe catalog | `scripts/check_governance.py` |
| [CHANGELOG.md](CHANGELOG.md) | Release history; `## Unreleased` collects write-back lines | Contract test |
| [.archcore/index.guide.md](.archcore/index.guide.md) | Index of durable ADRs, rules and plans, and what is never promoted | `scripts/check_governance.py` (both directions) |
````

## File: CHANGELOG.md
````markdown
# Changelog

## Unreleased

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
````

## File: README.md
````markdown
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
# SCRATCHPAD

Agent working memory for skill-vagrant. Use for: draft plans, terminal output, intermediate analysis, refactor outlines. Cleared between sessions unless content is explicitly marked KEEP.

---

<!-- KEEP: populated 2026-11-07 at creation -->

## Current state

**Phase:** first release, heading in [CHANGELOG.md](CHANGELOG.md); created 2026-11-07 beside skill-nautobot and skill-proxmox, not yet committed.

## Open items

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
  Build, pin, run and troubleshoot local Vagrant labs on macOS Apple silicon with the Parallels provider (vagrant-parallels): boxes and version pinning
  (bento arm64), multi-machine Vagrantfiles, provider customize events, private and second networks (Parallels shared, host-only, bridged), synced
  folders, provisioners, triggers and cloud-init, `vagrant ssh -c` with SSH options, linked clones and their shared machine-id, prlctl exec, capture,
  reset and snapshots, guards that refuse the wrong VM, project copies of a canonical Vagrantfile, Vagrant versus OpenTofu, licensing and editions.
  Use for Vagrant or Parallels lab VM work; not for Proxmox or OpenTofu (skill-proxmox) and not for what runs inside the guest (that project's skill).
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

Use Vagrant for disposable, reproducible local lab VMs on a Mac: arm64 Ubuntu guests under Parallels Desktop, described by a Vagrantfile kept in source control. Do not use it as a server or fleet
platform (Proxmox with OpenTofu is the x86 lab: skill-proxmox), and do not describe a project's lab layout as product behaviour.

## Read, write, and evidence boundaries

Read-only commands (`vagrant status`, `vagrant global-status`, `vagrant box list`, `prlctl list`, `prlctl capture`) need no approval and change no VM. Anything that starts, stops, resets,
reprovisions, clones, snapshots or destroys a VM is a write: print the plan, run it only with the project's `--apply` (or the operator's go-ahead), and put a deadline on every call. A guest is a lab
box until a project says otherwise; never point lab tooling at a site. Keep the observation's source, time and VM name when it may affect a later decision. Do not embed credentials, box tokens or
private addresses in reusable guidance.

## Orient first

On an unfamiliar Mac, establish the tool versions, the provider and edition, and what exists before reading anything else: the provider, the box format and the CLI flags change between releases.

```bash
vagrant --version; vagrant plugin list; prlctl --version
prlsrvctl info --license --json | grep -E '"(edition|status)"'      # Pro, Business or Enterprise is needed for the CLI and the provider
vagrant global-status --machine-readable                             # a cache: --prune to drop stale rows
vagrant box list --machine-readable; prlctl list -a -i -j            # boxes, and every VM with state, Parent VM and Tools state
```

`scripts/` holds tested, stdlib-only helpers (`just helpers`): `vagrant_lab_inventory.py` (one read-only table of Vagrant machines, Parallels VMs, linked-clone parents, Tools state, boxes and pins),
`vagrantfile_lint.py` (box pinned, provider set, customize events, no secrets) and `vagrant_copy_check.py` (a project copy of a canonical Vagrantfile is byte-identical).

## Route the task

Choose the primary skill by the object **being changed**: a Vagrantfile, box, Parallels VM, network adapter or lab guard starts here; a Proxmox VM or OpenTofu plan starts in `skill-proxmox`; what the
guest runs (an SMC image, a Nautobot install) starts in that domain's skill. Ordinary tasks load one reference.

| Task                                                             | Read first                                  |
| ---------------------------------------------------------------- | ------------------------------------------- |
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
````
