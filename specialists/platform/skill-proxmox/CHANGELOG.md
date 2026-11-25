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

- 2026-11-25 references/storage.md (b): a ZFS-root install creates no swap; swap on a zvol discouraged by the admin guide; partition or zram (home NAS).

- 2026-11-25 lxc-containers.md (i): static IP on running CTs via bpg is in place; access-control.md (j): second project on one node: pool-scoped token, budgets as a daily check, ZFS quota (home NAS).

- 2026-11-25 references/storage.md: Learned 2026-11-25: clearing old-NAS md-RAID disks by serial; `zfs create` reads a passphrase from non-terminal stdin; prove the vault copy by unload and reload (home NAS).

- 2026-11-25 references/lxc-containers.md: Disputed (h) against (e): bpg 0.123.1 cannot set nesting on an existing CT with a privsep token (403); Debian 13 systemd 257 needs it; set it in the root host script (home NAS).

- 2026-11-25 (home NAS write-back): upgrade-and-troubleshooting.md (n) 9.2 installer enables Ceph enterprise too, handle ceph-squid-enterprise; lxc-containers.md (f) template index lists arm64, filter by dpkg architecture; access-control.md (g) ACME needs Sys.Modify on `/`, token_audit high accepted; monitoring-and-metrics.md (m) ntfy webhook plus system-mail matcher via proxmox-mail-forward.

- 2026-11-25 references/opentofu-bpg-provider.md: Learned 2026-11-25, bpg 0.123.1 initialization dns list form, vendor_data_file_id beside user_account, pool_membership deprecated, offline `tofu test` with mock_provider (continuum-app).

- 2026-11-25 references/backup-and-restore.md: proxmox_backup_job with prune_backups map (home NAS).

- 2026-11-25 references/lxc-containers.md (e): containers as code with root-only bind mounts and devices by host script plus ignore_changes (home NAS).

- 2026-11-25 references/qemu-vms.md: virtiofs as code (directory mapping with Mapping.Modify, VM block with Mapping.Use, on_boot false behind encrypted datasets), home NAS project.
- 2026-11-24 write-back from the home NAS project: references/access-control.md (a) root token is not root@pam, ACME rights; references/opentofu-bpg-provider.md (b) state encryption, proxmox_version, no CA option; references/storage.md (c) mirror-pair growth vs RAIDZ expansion; references/lxc-containers.md (d) iGPU render node into LXC with dev0 gid, SR-IOV on Alder Lake-N not ready. references/architecture-and-cluster.md (e) single-node service minimisation.

- 2026-11-11: front-matter description shortened to cut startup tokens; the full original text is kept verbatim in the new `## Full description` section of SKILL.md.
- 2026-11-09 read-only lab probes for the doc-only sections (operator: "Read-only probes now") blocked: the lab node was unreachable from this network (port 22 timed out, no lab route); probe set recorded in SCRATCHPAD open items; no Learned entry until they run.
- 2026-11-09 skill-ai-it promote (operator: "promote and accept all"): candidates surfaced from AGENTS.md, SKILL.md and the references and accepted: `.archcore/adr/bpg-provider-not-telmate.adr.md`, `.archcore/rules/live-node-writes.rule.md`, `.archcore/rules/project-boundary.rule.md`; contract-enforced and upstream rules left unpromoted (index table).
- 2026-11-09 `.archcore/rules/dated-latest-claims.rule.md` accepted (operator, promoted from the candidates file); `ARCHCORE_PROMOTION_CANDIDATES.md` removed (queue empty) and dropped from the Repomix include.
- 2026-11-09 AGENTS.md trimmed (operator: "Trim AGENTS.md · 3k tokens per request"): 148 to 70 lines, 12.6 to 5.7 KB; scope, search order, version and memory
  rules linked to SKILL.md and `.archcore/` instead of restated; the generic governance-checks block replaced by one paragraph and a link to the skill-ai-it
  pattern; front matter repaired (the adoption pass had cut Summary mid-sentence). AGENTS.md was hidden by skills_stuff's `.git/info/exclude` until the <!-- path:example -->
  operator's Git-tracking rule (2026-11-09); first committed in skills_stuff 95bf5f2.
- 2026-11-09 incidents: a scratch-folder recursive delete was refused by the OPA hook (rerun in a fresh dated folder); `git push` and one read-only listing
  were refused by the auto-mode classifier (the operator pushed by hand); the first blind memory-recall test read the session-start copy of MEMORY.md, not
  the file on disk, and was discarded.
- 2026-11-09 archcore review (operator: "see if it is all up to date and if it needs more optimization"): the six `.archcore/` documents corrected (version rule enforcement wording, plan steps for the 2026-11-09 doc-only sections and the 9.2 cookbook re-run, memory rule names both backends, pack ADR names the skill-vagrant boundary, checker ADR names the new test) and accepted (operator, 2026-11-09); index updated; `ARCHCORE_PROMOTION_CANDIDATES.md` written (one candidate: dated-latest-claims) and added to the Repomix include; doc-freshness baseline 8 to 2. New governance check `check_version_restated` with `Governance.test_a_restated_version_fails_the_gate` (it caught a missed sentence-final version before release).
- 2026-11-09 gap review with online research (operator: "confirm the skill is defined properly ... do online research and fill in"): new sections for hyperconverged Ceph (references/storage.md), node removal and arm64 hosts (references/architecture-and-cluster.md), migration, resource mappings and virtiofs (references/qemu-vms.md), notifications (references/monitoring-and-metrics.md), two-factor authentication (references/access-control.md), PBS 4.x and S3 datastores (references/backup-and-restore.md), PDM 1.0/1.1 (references/capability-extension.md), the 9.2 arm64 release row (references/upgrade-and-troubleshooting.md); ASCII diagrams and tables in nine references (operator: "add ASCII diagrams and tables"); claims P-C22 to P-C27, scenarios P-S17 to P-S20, environment pve-docs-9-current-20261109; seven captures in documents/research-sources-20261109/; bpg/proxmox re-checked, still 0.120.0.
- 2026-11-09 skill-ai-it refresh: govern (navigation block upgraded, AI_NAVIGATION 322 to 159 lines, adoption recipes and record keys), front matter with summaries on 16 references and 2 test documents (doc-freshness baseline 26 to 8), docs/history and docs/trackers registered as conditional paths in the checker, code-map.toml with each module's status, context pack regenerated.
- 2026-11-08 write-back from smc-resiliency X1: references/qemu-vms.md (iTCO_wdt on q35 without i6300esb; explicit modprobe past the deny-list; a crash reset in 91.1 s)
- 2026-11-07 (c) write-back from smc-resiliency X2: references/qemu-vms.md (OVMF entry deletion, watchdog driver), references/opentofu-bpg-provider.md (watchdog block, boot_order)

- 2026-11-07 (b) write-back from smc-resiliency's lab package: per-VMID ACL on 9.2, IPAM bind on start, isolated bridge; Vagrant transport

- 2026-11-07 write-back from smc-resiliency: references/upgrade-and-troubleshooting.md, references/networking-and-sdn.md (Learned 2026-11-07).

- 20261107 Pack created (operator, 2026-11-07: "create and setup skill-proxmox like skill-nautobot ... with the same detail and logic"); not committed.

## 0.1.0 — 2026-11-07

First release, built to skill-nautobot's structure: `SKILL.md`, sixteen focused references, claim and environment ledgers, sixteen scenarios, an offline package contract, three stdlib-only helpers
with tests, the skill-ai-it governance layer (`AGENTS.md`, `AI_NAVIGATION.md`, `context-map.yaml`, `justfile`, governance checker) and six proposed `.archcore/` documents. Sources: 51 verbatim
captures in `documents/research-sources-20261107/` (Proxmox VE 9.x admin guide chapters, man pages and wiki, 9.0 to 9.2 release notes, bugzilla lists, bpg/proxmox docs, changelog and issues, OpenTofu
docs, edk2 sources, one installed-source excerpt). Lab facts read only, on one Proxmox VE 9.1.5 node.

- 20261107 Helpers: `scripts/pve_ssh.py` (batched read-only reader), `scripts/pve_token_audit.py` (least-privilege audit), `scripts/pve_node_report.py` (node health and inventory; `--refresh --apply`
  is its only write); recipes `node_report`, `token_audit`, `coder_checks`. The contract test indexes captures recursively and exempts them from the redaction scan except for private keys.
- 20261107 Learned 2026-11-07 (a) in `references/architecture-and-cluster.md`: standalone `/cluster/status`, `localhost` as node name, 9.2 arrives as ordinary updates.
- 20261107 Learned 2026-11-07 (b) in `references/storage.md`: adding `import` with the full content list; thin-pool fill on a single-disk lab.
- 20261107 Learned 2026-11-07 (c) and (j) in `references/networking-and-sdn.md`: SDN.Use on localnetwork for `vmbr0`; SDN simple zone DHCP with PVE IPAM binds MACs, token needs the zone ACL.
- 20261107 Learned 2026-11-07 (d) in `references/qemu-vms.md`: provider `efi_disk` to `efidisk0` mapping; cite the installed OVMF version.
- 20261107 Learned 2026-11-07 (e), (f) and (g) in `references/access-control.md`: the pool-scoped token pattern proven by the task log; `Sys.AccessNetwork` alternative for download-url; wide legacy
  tokens found by the audit.
- 20261107 Learned 2026-11-07 (h) in `references/api-and-cli.md`: apt/update GET does not refresh; repositories, resources and task-log reads.
- 20261107 Learned 2026-11-07 (i) in `references/opentofu-bpg-provider.md`: `~> 0.118` resolved to 0.120.0; one-VM apply time.
- 20261107 Learned 2026-11-07 (k) in `references/upgrade-and-troubleshooting.md`: a 9.1.5 node's pending 9.2 stack and repository state.
- 20261107 Learned 2026-11-07 (l) in `references/monitoring-and-metrics.md`: node report runtime and budget.

## 20261124_2213 — Write-back: ZFS root, ARC default and boot mirror (9.2)

- references/storage.md: Learned 2026-11-24 (a), ZFS root on Proxmox VE 9.2: installer ARC default (10% of RAM, 16 GiB cap, written to /etc/modprobe.d/zfs.conf), ZFS RAID0 over ext4 for a later mirror, and the boot-mirror steps (sgdisk -R/-G, zpool attach, proxmox-boot-tool format/init); from the admin guide 9.2.15 and a home NAS install.

## 20261119_1648 — Version of record PVE 9.2 (lab pve-manager 9.2.26); QEMU note resolved

AGENTS.md version of record moves from 9.1.5 to 9.2 (lab node on pve-manager 9.2.26 after its 2026-11-07 upgrade); compatibility.yaml gains pve-9-2-26-lab-20261107. operations-cookbook.md keeps Verified against 9.1.5 and states it was not re-verified on 9.2. upgrade-and-troubleshooting.md notes that 9.2 shipped QEMU 11.0 and pve-qemu-kvm 11.1.x is a later update, so Learned (k) and the release table agree. VERIFIED_PRIMARY: https://pve.proxmox.com/wiki/Roadmap and the pve-no-subscription Packages.gz index, retrieved 2026-11-19.

## 20261119_1631 — Periodic review; 90-day review window

- Periodic review (operator, 2026-11-19): every due doc re-read in full and dated 2026-11-19; references, Summaries and Scopes fixed, body rules aligned with their Learned entries. Review window now 90 days (`--window-days 90` in the justfile).

## 20261109_1125 — deterministic navigation-control upgrade

<!-- skill-ai-it-upgrade: 2026-10-14-compact-v2 -->

- Applied `skill-ai-it` deterministic navigation-control upgrade.
- Upgraded managed navigation/scripts blocks to version `2026-10-14-compact-v2`.
- Ensured `context-map.yaml` contains `skill_ai_it_version`, `audit_checks`, `promotion_rules`, `context_recovery`, and `update_rules`.
- Preserved user-authored content outside managed blocks.
- Generated outputs remain support-only; no `.archcore/` promotion was performed.

Applied to: AI_NAVIGATION.md, context-map.yaml, AGENTS.md, scripts/README.md, justfile, scripts/README.md
