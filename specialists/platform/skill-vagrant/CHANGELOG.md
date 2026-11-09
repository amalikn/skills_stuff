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

- 2026-11-09 (b) operator: "Fix all" — scratch-lab VM tests (two throwaway VMs, destroyed), box copies, inventory, evaluation, Archcore accepted.
- 2026-11-09 references/clones-snapshots-and-identity.md: clone keeps machine-id and lease; emptying machine-id gives a new one (lab run).
- 2026-11-09 references/vagrantfile-and-provisioning.md: `config.vm.cloud_init` is ignored under vagrant-parallels 2.4.10 (lab run).
- 2026-11-09 references/networking-and-synced-folders.md (b): 2.4.10 mounts /vagrant via fuse.prl_fsd on 24.04 (lab run).
- 2026-11-09 references/boxes-and-pinning.md (b): both box copies made with sha256, restore tested.
- 2026-11-09 references/virtualbox.md: Extension Pack recorded as personal use; Vagrant cache can name VirtualBox VMs that no longer exist.
- 2026-11-09 scripts/vagrant_lab_inventory.py: VirtualBox VMs and provider-aware machine ids; a missing hypervisor CLI is unavailable, not exit 1 (3 new tests).
- 2026-11-09 tests/eval-procedure.md: evaluation record for V-S16 and V-S18 (with and without the skill).
- 2026-11-09 .archcore/: all five documents accepted (operator); plan steps 1 to 4 done.
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
