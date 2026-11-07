# Changelog

## Unreleased

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
