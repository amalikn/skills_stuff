---
Title: Scratchpad
Category: working-state
Status: current
Summary: Current working state, newest first per section; superseded entries rotate to docs/history (search with --find).
Kind: state
Budget: 200 lines, 25 KB
Archive: docs/history/ (`--find`, `--show`)
Last rotated: 20261010_1801
---

# SCRATCHPAD — skill-smc

Agent working memory for the skill-smc specialist pack. Use for: draft plans, terminal output, intermediate analysis, refactor outlines. Cleared between sessions unless content is explicitly marked
KEEP.

---

<!-- KEEP: populated 2026-06-26 from session history (UserPromptSubmit hook context) --> <!-- KEEP: updated 2026-06-26 (ansible-wifi session) — references/10-13 content updated from ansible-wifi
RUNBOOK audit; AGENTS.md project-coherence checklist added; manifest bumped to v0.1.3 --> <!-- KEEP: updated 2026-07-28 (ansible-wifi session, project-coherence) — captive-portal PHP SAPI corrected:
10_captive-portal.md claimed PHP-FPM processes .php and that an Ansible SetHandler fix landed 2026-06-26; BOTH false (production runs mod_php as www-data, zero php*-fpm packages on 3 sampled rcp
hosts, no SetHandler anywhere in the repo, enabled modules are only rewrite+ssl). §11.4 retitled historical/ff-smc01-only; new §11.8 APPPATH/cache failure mode; 06_failure-modes.md +
08_ansible-authoring.md (tag hazard) + 13_known-issues.md (no portal HTTP monitoring; third single-host-generalized-to-fleet correction) all gained entries; 5 routing rows across
SKILL/AGENTS/AI_NAVIGATION/RUNBOOK de-PHP-FPM'd; 3 new manifest stable_facts; manifest bumped to v0.1.5 --> <!-- KEEP: updated 2026-07-03 (ansible-wifi session, project-coherence) — DNS architecture
corrections: 02_service-map.md's "unbound=RCT/bind=non-RCT" framing was wrong (real gate is smc_ltp group, not flavor); Stubby listen port fixed (60053, not 5353); new systemd-resolved host-DNS row +
Stubby upstream chain added; 06_failure-modes.md gained garimba-smc01 DNS delay entry; 13_known-issues.md gained fleet-wide architecture risks section; rule-002 + ansible-wifi AGENTS.md gained a DNS
domain routing row (previously missing); manifest bumped to v0.1.4 --> <!-- KEEP: updated 2026-07-31 — full local-knowledge-ansible/ansible-wifi extraction pass (v0.1.6); ssh-manager MCP framing
removed, replaced with direct-tsh-ssh + confirmed flavor->Teleport-domain mapping; cross-repo feed-back rule broadened on both skill-smc and ansible-wifi sides after root-causing why the extraction
pass found unpromoted knowledge (v0.1.7) --> <!-- KEEP: updated 2026-08-03 — NBN Accelerate cluster gap-fill (v0.1.8): 01_overview.md/08_ansible-authoring.md/10_captive-portal.md/13_known-issues.md
now document the cw/nbn_accelerate/nbn_wh cluster by structural comparison against apn/rcp/rct/wh, explicitly flagged as code-inspection-only, not live-validated --> <!-- KEEP: updated 2026-08-03 —
smc_ltp properly explored (v0.1.9): fixed a real undercount (4 sites — guda-guda/pandanus-park/old-looma/new-looma — not just guda-guda) and a mislabel ("cnMaestro mDNS" was wrong; it's CNMaestro
Cambium backhaul provisioning + a DNS-resolver-stack switch to bind9/RPZ, two unrelated purposes). New dedicated section in 08_ansible-authoring.md; SKILL.md/05_troubleshooting.md quick-refs fixed -->
<!-- KEEP: updated 2026-08-03 — "low touch" onboarding method + site deployment history added (v0.1.10): guda-guda pilot 2025-04-15, then umoona/warburton/beagle-bay/pandanus-park/old-looma/new-looma
in 2026; all 4 smc_ltp sites are also low-touch sites — flagged as an unresolved correlation, not concluded. "low_touch" has no live Ansible code path (one orphaned host_var, never read) --> <!--
KEEP: updated 2026-08-03 — smc_ltp/low-touch correlation RESOLVED (v0.1.11): operator confirmed the link is real (every low-touch site should be an smc_ltp member) and directed + verified adding the 3
missing sites (warburton/beagle-bay/umoona) to inventories/rcp/prod. smc_ltp is now 7 members, not 4. Uncommitted production Ansible inventory change — not yet run against any live SMC --> <!-- KEEP:
updated 2026-09-08 — skill-ai-it refresh (v0.1.34, CHANGELOG 20260908_1955): navigation-control upgrade applied; AGENTS.md's generic navigation block upgraded to current template; AI_NAVIGATION.md's
project-specific routing table declared project-managed (`skill-ai-it:manual`) rather than overwritten, with its two missing sections (generated-context policy, compaction recovery) hand-added;
`scripts/check_governance.py` adopted for the first time, tuned to rule-reference-update-discipline.md and rule-manifest-version-discipline.md after 35 initial false positives (remote-appliance
scripts, sibling-repo paths, unrelated-software version numbers) were traced and resolved; validator now a clean PASS (26/26, 0 warnings) -->

## Contents

- [Current state](#current-state)
- [Open items](#open-items)
- [Key anchors](#key-anchors)
- [Recent decisions](#recent-decisions)
- [Session history (summaries)](#session-history-summaries)
- [Next actions](#next-actions)
- [Memory pointers (navigation only)](#memory-pointers-navigation-only)

## Current state

**2026-10-07 16:43 `KEEP` — v0.1.100 (renumbered 0.2.0 at 16:45 under the new 0–9 patch rule), layout parity with skill-cambium / skill-mikrotik.** Root `justfile` (`just bootstrap` once, then `just check`, `just nav_validate`,
`just fleet …`, `just routing …`), `.mise.toml`, `requirements.txt` (PyYAML for the nav validator only), lint config, `.gitignore`, `.archcore/index.guide.md`. `SKILL.md` is a short router
(144 lines); detail lives in references. The profile file, the dedicated-agent prompt and the `exports/` adapter are retired; install is the symlink `~/.claude/skills/skill-smc`.
`AGENTS.md` is local-only (`.git/info/exclude`), so its rule edits never appear in git. Checks: governance 320/320, nav 0/0, archcore 0 issues.

**2026-10-02 16:41 KEEP, scoped topology-design update:** the local RCP plan covers Kapitan/CUE/Jsonnet and three inventory integration paths; the corrected design summary is in
`references/08_ansible-authoring.md`. Metadata version: 0.1.80. Evidence branch: `unc-virtual-smc-malik-rcp01`, clean production tree at start. No implementation or live changes. Open decisions:
authoritative `generic-big01` DHCP baseline, integration path and runnable tool comparison. Prior KEEP entries below remain historical; this entry does not resolve unrelated open items.

**2026-09-24 (12:25) `KEEP` — v0.1.54: TP-Link site switches and the SMC neighbour table.** New `references/16_tplink-site-switches.md` and `scripts/tplink-switch.sh` +
`tplink_cli_driver.py` (kalumburu switches reached; read-only default, fping discovery on `bridge_500` only, redacted `--backup`). `13_known-issues.md` records `gc_thresh` 1/512/1024 on the SMCs
and mornington's 2,230 `table_fulls`, with a 16384/4096/1024 proposal (not applied). Commits `d5566c2`, `8db6d56` not pushed. Two pre-existing governance failures remain (SKILL.md
`smc_collect.py` path, `08_ansible-authoring.md:526` split path).

**Phase:** Stable — v0.1.34. skill-ai-it refresh completed 2026-09-08 (CHANGELOG 20260908_1955): `scripts/check_governance.py` adopted for the first time and now gates on this pack's own stated
reference-routing and version-discipline rules; `AI_NAVIGATION.md` declared project-managed to protect its 13-file routing table from generic overwrite; `AGENTS.md` navigation block upgraded.
`validate_navigation_control_layer.py` reports a clean PASS. Prior: Backdoor SSH Access documented 2026-09-08 (CHANGELOG 20260908_1330): new section in `03_communication-flows.md`, plus a terminology
fix (Teleport-cluster split is by project, not flavor) propagated to `01_overview.md`, `SKILL.md`, and `PROFILE.md`. Prior: pack-structure self-audit completed 2026-09-08 (CHANGELOG 20260908_1200):
removed RUNBOOK.md's duplicate/stale version stamp, fixed install.md's frozen "Canonical version: 0.1.6" note, widened `rule-reference-update-discipline.md` from 4 to 6 required surfaces (added
AI_NAVIGATION.md + context-map.yaml), removed the vestigial empty `evidence/` dir, and promoted all `.archcore/` docs from `proposed` to `accepted`. `.graylog-token` was checked and is already
correctly gitignored — not a defect. Prior operational-content phase summary (ClamAV EOL root cause, Grafana CW/NBN exploration, new-looma-smc01 outage) unchanged, see CHANGELOG for full history.

skill-smc is the canonical specialist pack for SMC (Site Management Controller) box operations and ansible-wifi authoring. As of v0.1.3 the pack has 13 numbered focused reference files under
`references/`. RUNBOOK.md is a navigation index only — all operational content lives in `references/0N_*.md`. Content for `references/10_captive-portal.md`, `references/11_vagrant-lab.md`,
`references/12_content-filtering.md` was updated from the ansible-wifi 2026-06-26 session (captive portal architecture, Vagrant lab nuances, Eclipse identity, CAKE queuing). AGENTS.md now includes an
explicit project-coherence checklist with tier-ordered update instructions and cross-repo trigger rule from ansible-wifi. As of v0.1.6, `scripts/` covers two categories (WAN-routing diagnostics +
ansible-lint pre-push/CI gate) and every markdown file under `local-knowledge-ansible/ansible-wifi/` has been swept for gaps against this pack (see CHANGELOG 20260731_1245). As of v0.1.7, the
feed-back loop that broke last time (narrow "incident/debug fix" wording) is fixed: `AGENTS.md`'s cross-repo trigger rule and the matching rules on the ansible-wifi side (`AGENTS.md`, `rule-002`,
`task-patterns.md`, `validation.md`) now cover the whole tree, both `skill-slurp-chat` and `project-coherence` as trigger points, and a broader knowledge-type list (design docs, ADRs, OPA, scripts) —
intended to make another full-directory sweep unnecessary. As of v0.1.8, the pack documents the **NBN Accelerate cluster** (`cw`/`nbn_accelerate`/`nbn_wh`, `teleport.communitywifi.net.au`) by
structural comparison against the APN cluster (`apn`/`rcp`/`rct`/`wh`, `teleport.apn.au`) — closing the gap where ~95% of prior content was APN-cluster-derived and NBN Accelerate had only the
flavor→domain mapping. New content spans `01_overview.md` (full comparison table + selector mechanism), `08_ansible-authoring.md` (confirmed flavor-exclusive gates), `10_captive-portal.md`
(protocol/redirect diffs), and `13_known-issues.md` (coverage gap + naming-collision + OPA gaps) — all explicitly flagged as code-inspection-only, not live-validated against a cw-cluster host. As of
v0.1.9, `smc_ltp` — previously documented only as a DNS-gating side effect of the 2026-07-03 RCA — is properly explored: it is a static `rcp`-only group (`inventories/rcp/prod`, initially found as 4
sites, not `topology_vars`-generated) with two unrelated purposes (CNMaestro Cambium backhaul provisioning via a separate `smc_ltp.yml` playbook, and a DNS-resolver-stack switch to bind9/RPZ),
documented in a new `08_ansible-authoring.md` section with cross-references from `01_overview.md`, `02_service-map.md`, `13_known-issues.md`, `SKILL.md`, and `05_troubleshooting.md`. As of v0.1.10, a
related finding was documented alongside it: a named **"low touch" onboarding method** (`guda-guda` pilot 2025-04-15; `umoona`/`warburton`/`beagle-bay`/`pandanus-park`/`old-looma`/`new-looma` in 2026)
— initially only 4 of 7 low-touch sites showed up in `smc_ltp`, flagged as an unresolved (not concluded) correlation. **As of v0.1.11, that correlation is resolved**: operator confirmed every
low-touch site is meant to be an `smc_ltp` member, and directed + verified (via `ansible-inventory --list` and `ansible-playbook --syntax-check`) adding the 3 missing sites
(`warburton`/`beagle-bay`/`umoona`) to `inventories/rcp/prod`. `smc_ltp` is now documented as 7 members throughout this pack. This is a real, uncommitted production Ansible inventory change — not yet
run against any live SMC. Separately, "low touch" itself still has no live Ansible code path of its own (the one `low_touch`-named var in the repo, on an uninvolved host, is set but never read) — the
resolved link is specifically "low-touch sites should be `smc_ltp` members," not "low touch is implemented via `smc_ltp` group logic." **The mechanism question is now also resolved (v0.1.12): it's a
manual step someone has to remember**, with no tooling or enforcement — the confirmed root cause of the 3-site gap, and a standing risk for future low-touch sites rather than a one-off.

---

## Open items

- [ ] **2026-10-08 `KEEP`, proposed, not decided:** extend the 0–9 patch scheme (operator rule 2026-10-07, skill-smc only so far) to skill-cambium (0.6.45) and
  skill-mikrotik (0.1.24), each with `check_version_format`. Asked 2026-10-07, no answer yet.
- [x] **2026-10-07 `KEEP`:** commit `fbc0aff` is labelled "skill-smc 0.1.98" but committed manifest 0.1.99. Closed 2026-10-08: pushed, so it stays as a known
  mislabel; CHANGELOG 20261007_1625 records the real content.
- [x] **2026-10-07 `KEEP`:** ~~skill-ai-it's upgrader appends its CHANGELOG entry at the end~~ — fixed upstream in `cc0fa32` (2026-10-07 21:26): it now places the entry by
  the file's order. Closed 2026-10-08.
- [ ] **2026-09-24 `KEEP`:** ~~push `d5566c2` + `8db6d56`~~ (on origin, checked 2026-10-08); fleet read-only `table_fulls` survey (offered); find the `gc_thresh1` = 1 setter; live-test the enable-password, already-privileged,
  `--shell` and `--write` paths of `tplink-switch.sh` when a suitable switch appears; fix the two pre-existing governance failures.

- [ ] Live-validate the `smc_ltp` documentation (CNMaestro provisioning behavior, bind9/RPZ DNS switch) against one of the 7 real member hosts (`guda-guda`, `pandanus-park`, `old-looma`, `new-looma`,
  `warburton`, `beagle-bay`, `umoona`) via `tsh ssh` — everything added 2026-08-03 is from Ansible source inspection only; these are `rcp` (APN cluster) sites, not reachable from the
  `teleport.communitywifi.net.au` session used for the fleet sweep
- [ ] Ask the operator (or check further afield — commit history, old design docs) whether "LTP" has a known expansion; currently documented as an open question, not guessed
- [ ] Resolve the naming-collision question flagged 2026-08-03 in `04_dependency-tree.md`: is the generic "cnmaestro-provisioning"/`redis` Level-4 dependency row (RCT-oriented, `05_troubleshooting.md`
  Tier 4) the same mechanism as `smc_ltp`'s `roles/smc_cnmaestro_provisioning` (no Redis observed), or two genuinely separate provisioning paths?
- [ ] Confirm the `inventories/rcp/prod` `smc_ltp` group change (adding `warburton`/`beagle-bay`/`umoona`) gets committed to the `ansible-wifi` repo and run against those 3 sites — as of this update
  it's a verified-but-uncommitted file-level change
- [ ] Consider whether a lightweight enforcement check (e.g. a periodic `ansible-inventory` diff, or a checklist item) is worth proposing for future low-touch onboardings, given the mechanism is now
  confirmed manual/unenforced — not this pack's call to implement, but worth flagging if asked
- [ ] Re-check `mount | grep overlay` on `bungardi-smc01`/`darlngunaya-smc01` after the operator's planned `nbn_wh` overlay rollout lands, to confirm it took
- [ ] Resolve the `nbn_wh` zram/swap discrepancy flagged 2026-08-03 in `07_hardware-overlay.md` (`Swap: 0B`, no `zram0` device on either `nbn_wh` host) against the platform table's universal "RPi →
  zram" claim — may mean the claim itself needs re-checking against a live `rct`/`wh` host, never actually confirmed there either
- [ ] `koonibba-smc01` flagged at 95% disk usage with the fleet's oldest kernel (`5.15.0-79-generic`) — worth a maintenance pass, not investigated further this sweep
- [ ] Resolve the OPA `flavors.json`/`environments.json` coverage question flagged in `13_known-issues.md` (no `cw`/`apn`/`rct`/`wh` entries — intentional scoping or gap?) — needs whoever owns the OPA
  policy layer
- [ ] Validate `references/13_known-issues.md` entries against current ansible-wifi state when next working on that repo
- [x] ~~Regenerate `.ai-context/governance-pack.md` after today's content + governance changes~~ — done, regenerated 3× today as content landed in stages
- [ ] The bonding design (08_ansible-authoring.md, RCP/NBN-Accelerate doubled circuits) and the `smc_host_dns_mode: resolved_stub` DNS mitigation (06_failure-modes.md) are both unimplemented design
  recommendations, not confirmed fixes — re-check their status next time this pack is touched and update the wording if either has since been canaried/adopted/rejected.
- [ ] The apt-lock-race vs. apt-daily-upgrade-timer-mask duplicate-fix question flagged in `13_known-issues.md` (Skill Staleness Risks) needs resolving against actual ansible-wifi commits before
  either fix's documentation can be fully trusted.
- [ ] Grafana dashboards not yet explored in detail: "Data Backlog" (0 panels — appears unused/placeholder, confirm before assuming dead), the two Prometheus RW Receiver+Sender Backlog dashboards
  (federation pipeline health — not yet cross-referenced against the `autossh-prometheus-federation` service row in `02_service-map.md`), "Servers Network"/"Servers System Information" (backend infra,
  likely out of skill-smc scope but not confirmed), "RISE Dashboard" (`rise-stage0_5` — earlier-stage rollout view, not compared against the newer RISE SMC Table/Health Detail dashboards for
  redundancy)

---

## Key anchors

| Item                          | Detail                                                                                                                                                               |
| ----------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Canonical source              | `/Volumes/Data/_ai/_skills/skills_stuff/specialists/project/skill-smc/`                                                                                              |
| Installed skill (Claude Code) | `~/.claude/skills/skill-smc/`                                                                                                                                        |
| ansible-wifi repo             | `/Volumes/Data/_ansible/ansible-wifi`                                                                                                                                |
| ansible-malik repo            | `/Volumes/Data/_ansible/ansible-malik`                                                                                                                               |
| dns_query scripts             | `/Volumes/Data/_ai/_scripts/scripts_stuff/python/dns_query`                                                                                                          |
| local-knowledge               | `/Volumes/Data/_ansible/local-knowledge-ansible/ansible-wifi`                                                                                                        |
| skill-smc venv                | `/Volumes/Data/_ai/_skills/skills-working-cache/skill-smc/venv`                                                                                                      |
| ansible-wifi venv             | `/Volumes/Data/_ai/_skills/skills-working-cache/ansible-wifi/venv`                                                                                                   |
| Validated against             | malik-rct01 (RCT flavor, ARM64, Ubuntu 22.04, overlayroot enabled)                                                                                                   |
| Grafana MCP config            | `~/.claude.json` `mcpServers` block: `mcp-grafana` (APN main-org, unrelated), `mcp-grafana-apn` (port 53000), `mcp-grafana-nbn` (port 63000 — the                    |
|                               |   CW/NBN-Accelerate instance)                                                                                                                                        |

---

## Recent decisions

- 2026-10-07 `KEEP` — **Version scheme (operator rule):** patch runs 0 to 9; after `x.y.9` comes `x.(y+1).0`. Pack renumbered 0.1.100 -> 0.2.0. Rule in
  `.archcore/rules/manifest-version-discipline.rule.md`, enforced by `check_version_format`.
- 2026-08-03 — Operator reported "new-looma-smc01 is back online." Verified rather than just acknowledged: queried live Prometheus via `mcp-grafana-apn` (`up{instance=~"new-looma.*"}`, 7-day range).
  Confirmed a 31h whole-host outage (both `prometheus` self-scrape and `node_exporter` dark simultaneously) from 2026-08-01 23:40 UTC to 2026-08-03 06:40 UTC, now recovered — matching the operator's
  report with hard evidence and exact timestamps rather than taking it at face value. Also found a second, earlier 18h gap in the same window that turned out to already be explained by the documented
  2026-07-30 topology cross-wiring fix — good cross-validation that the existing docs are accurate. The new 31h gap's root cause is NOT established (no tsh ssh this session) — logged as
  confirmed-timeline-only. Added to `13_known-issues.md`'s existing new-looma section; manifest bumped to v0.1.18.

- 2026-08-03 — Follow-up session: operator confirmed the NBN Grafana token fix had landed and a session restart happened, unblocking the connection left stuck at the end of the previous session.
  Confirmed `mcp-grafana-nbn` live via `search_dashboards` (9 dashboards, all `smc`-tagged). Rather than stop at "connection works," compared it against `mcp-grafana-apn` (20 dashboards) to find
  what's genuinely new: 11 APN-only dashboards, most notably a RISE health/watchdog framework (RISE SMC Health Detail, RISE SMC Table) absent from NBN because RISE only deploys to `rct`/`wh` flavors —
  confirmed via the `flavor=~"rct|wh"` gate in a panel query, not inferred from dashboard absence alone. Pulled exact Prometheus metric names for the 4 `rise_*` textfile collectors that previously had
  `—` placeholders in `02_service-map.md`, plus the offline-vs-pending fleet-rollup distinction (30d-seen-but-not-5m vs. series-never-existed). Documented in `02_service-map.md` (new RISE
  Health/Watchdog Framework subsection) and `03_communication-flows.md` (new Dashboard inventory subsection). Manifest bumped to v0.1.17.







---

## Session history (summaries)

- **2026-10-07 (16:37) — Layout parity with the newer project packs (v0.1.99 -> v0.1.100).** Root `justfile`, `.mise.toml`, lint config, `.gitignore`, Archcore index added;
  `SKILL.md` slimmed to the cambium/mikrotik shape with SKILL-only facts moved into references 03/05/08; profile, system prompt and exports adapter retired.
- **2026-10-07 (16:25) — skill-ai-it refresh (v0.1.98 -> v0.1.99).** `AGENTS.md` and `scripts/README.md` managed blocks upgraded to `2026-09-23-template-sourced-blocks-v1`;
  `AI_NAVIGATION.md` stays project-managed. Template item 12/14 defect fixed in skill-ai-it and re-applied; `.archcore/` files renamed to `<slug>.<type>.md`, `archcore status` clean.
- **2026-09-24 (10:44–12:25) — TP-Link switches + neighbour table** (from unified-network-controller). Switch access worked out and scripted; neighbour-table overflow found on mornington;
  gc_thresh1 attribution corrected in v0.1.54. Detail: memory-keeper channel `unc`, keys `unc.tplink-*`, `unc.neighbour-table.20260924`. `KEEP`

## Next actions

- On a new machine: `ln -s` the pack to `~/.claude/skills/skill-smc`, then `just bootstrap`; run `just check` and `just nav_validate` before calling any change done.
- New reference file: update the four index surfaces (`RUNBOOK.md`, `SKILL.md`, `AI_NAVIGATION.md`, `context-map.yaml`); the checker fails until all four name it.
- Explore the remaining unreviewed Grafana dashboards flagged 2026-08-03 (Data Backlog, RW-backlog pair, Servers Network/System Information, RISE Dashboard `rise-stage0_5`) next time Grafana access is
  used — see Open Items
- Cross-reference the RW-backlog dashboards against `autossh-prometheus-federation` in `02_service-map.md` once reviewed — may reveal federation-pipeline health signals not currently documented
- Propose/plan a fleet-wide ClamAV upgrade to 1.0 or 1.4 LTS next time remediation authorization is available — root cause confirmed 2026-08-03, no automated pipeline exists to do this without a
  deliberate rollout
- Fix mechanism found 2026-08-03 (memory-only so far, not yet in `references/13_known-issues.md`): `roles/smc_clamav/tasks/ubuntu.yml` installs with `state: present` (never upgrades an
  already-installed package) + this fleet's already-documented masking of `unattended-upgrades`/`apt-daily` compound to explain why ClamAV never self-healed. Canary-first remediation plan proposed to
  operator, not yet executed (offered a read-only `apt-cache policy clamav` check on a live host, awaiting go-ahead). If operator wants this folded into the pack's docs, run `project-coherence` — it
  currently only lives in memory-keeper key `skill-smc.discovery.clamav-fix-mechanism-20260803`
- Re-check `nbn_wh` overlayroot status after the operator's planned rollout lands
- `cw` flavor still has no site-level hosts to check (central-infra only); `aurukun-smc03` still unreachable — note if either changes
- Resolve the smc_ltp/generic-cnmaestro-provisioning naming-collision question flagged in `04_dependency-tree.md`
- Re-check the two unimplemented design recommendations (bonding, DNS resolved_stub) and the apt-lock-race duplicate-fix question next time this pack or ansible-wifi is touched
- On next ansible-wifi (or local-knowledge-ansible/ansible-wifi subfolder) session: invoke skill-smc first; both `skill-slurp-chat` and `project-coherence` must now check for unpromoted knowledge
  before closing out (broadened rule, 2026-07-31)
- Next time one of the 7 `smc_ltp` sites (`guda-guda`, `pandanus-park`, `old-looma`, `new-looma`, `warburton`, `beagle-bay`, `umoona`) is accessed via `tsh ssh`, live-validate the
  CNMaestro-provisioning and bind9/RPZ-DNS-switch documentation in `08_ansible-authoring.md` "smc_ltp Sub-Group"
- Confirm the `inventories/rcp/prod` `smc_ltp` group change gets committed in `ansible-wifi` and actually run against `warburton`/`beagle-bay`/`umoona` — currently a verified-but-uncommitted
  file-level change

---

## Memory pointers (navigation only)

- 2026-10-08 14:27: memory-keeper `skill-smc.progress.slurp-delta-20261008`; project-context `0bf38158` note; checkpoint `slurp-20261008-skill-smc-version-delta`
  (memory-keeper `84ffcf40`, project-context `f07a8367`). `KEEP`

- 2026-10-07 16:43: memory-keeper `skill-smc` keys `skill-smc.progress.skill-ai-it-refresh-v0199-20261007`, `skill-smc.finding.skill-ai-it-template-item12-20261007`,
  `skill-smc.progress.archcore-rename-20261007`, `skill-smc.error.concurrent-commit-fbc0aff-20261007`, `skill-smc.progress.layout-parity-v01100-20261007`,
  `skill-smc.finding.content-moved-on-slim-20261007`, `skill-smc.error.venv-missing-pyyaml-20261007`, `skill-smc.progress.cambium-spec-fix-20261007`,
  `skill-smc.decision.layout-parity-and-commit-scope-20261007`, `skill-smc.decision.version-scheme-patch-0-9-20261007`; project-context `0bf38158` note + decision; checkpoint `slurp-20261007-skill-smc-layout-parity`
  (memory-keeper `8ab3b9e2`, project-context `709e1015`). `KEEP`

- 2026-09-24 12:25: memory-keeper `unc` keys `unc.tplink-switch-access.20260924`, `unc.tplink-tooling.20260924`, `unc.neighbour-table.20260924`, `unc.errors.20260924-tplink`; project-context
  `0bf38158` note; checkpoint `slurp-20260924-tplink-switches-neigh-table` (`98c3a99e`). `KEEP`

- memory-keeper channel: `skill-smc` / earlier keys: `skill-smc.structure.progressive-disclosure-20260626`, `skill-smc.audit.fixes-20260626`, `skill-smc.governance.bootstrap-20260626`,
  `skill-smc.governance.archcore-promote-20260626`, `skill-smc.docs.readme-architecture-20260626`, `skill-smc.coherence-sweep-20260626`
- memory-keeper checkpoint: `slurp-20260803-skill-smc-new-looma-outage` (ID: af68fc31) — 402 context items; earlier today: `slurp-20260803-skill-smc-grafana-rise-dashboard-inventory` (ID: ce01b46c) —
  401 context items; earlier today: `slurp-20260803-grafana-cw-blocked` (ID: cdb3b0ab) — 400 context items; earlier today: `slurp-20260803-skill-smc-clamav-fix-mechanism` (ID: d784984d) — 399 context
  items; earlier today: `slurp-20260803-skill-smc-clamav-root-cause` (ID: 609d0e06), `slurp-20260803-skill-smc-nbn-accelerate-fleet-sweep` (ID: eea021c1),
  `slurp-20260803-skill-smc-nbn-accelerate-live-validation` (ID: f293e11b), `slurp-20260803-skill-smc-coherence-sweep-close` (ID: fcb5bd7d), `slurp-20260803-skill-smc-ltp-manual-mechanism` (ID:
  a0b0525f), `slurp-20260803-skill-smc-ltp-seven-sites` (ID: 0e74230f), `slurp-20260803-skill-smc-low-touch-onboarding` (ID: 7c2ca18e), `slurp-20260803-skill-smc-smc-ltp-correction` (ID: d6fbd843),
  `slurp-20260803-skill-smc-nbn-accelerate-gapfill` (ID: 4052409c); earlier: `slurp-20260731-skill-smc-extraction-and-governance` (ID: 4fc94978), `slurp-20260626-skill-smc-governance` (ID: 7a4df5b2),
  `slurp-20260626-skill-smc-coherence` (ID: 85dae74b)
