---
name: skill-vagrant
description: >-
  Vagrant labs on macOS Apple silicon: Parallels, VirtualBox, QEMU, libvirt providers; bento boxes, Vagrantfiles, networks, synced folders, provisioners, snapshots, linked clones, prlctl/VBoxManage; not Proxmox.
---

# Vagrant

## Contents

- [Full description](#full-description)
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

## Full description

The listing shows a short description; this is the full scope (moved here 2026-11-11 to cut startup tokens).

Build, pin, run and troubleshoot local Vagrant labs on macOS Apple silicon: Parallels (default), VirtualBox 7.1/7.2, QEMU and libvirt/KVM providers and selection order; bento arm64 boxes and pinning;
multi-machine and multi-provider Vagrantfiles, customize, per-provider networks (host-only, internal, vmnet), synced folders, provisioners, triggers, cloud-init; `vagrant ssh -c`, prlctl/VBoxManage
exec, serial console; linked clones (machine-id), snapshots, wrong-VM guards; Vagrant vs OpenTofu, licensing. Not Proxmox/OpenTofu (skill-proxmox) or what runs inside the guest.

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

Before asserting a flag, a Vagrantfile key, a provider option or a licence term, read the version-matched source and record it in [sources.yaml](sources.yaml); the verbatim captures are in the dated folders listed in [documents/readme.md](documents/readme.md) (2026-11-07: Vagrant, Parallels, bento, licences; 2026-11-09: VirtualBox, QEMU, libvirt, provider selection). Use [compatibility.yaml](compatibility.yaml) only for its stated environment and evidence rung; an observed install is not behavioural proof. Record unknowns as unknown
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
