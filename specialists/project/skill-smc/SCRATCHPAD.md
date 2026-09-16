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

---

## Current state

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

- [ ] Install v0.1.15 to `~/.claude/skills/skill-smc/` — run steps in `exports/claude_code/project/skill-smc/install.md` (now also copies `scripts/` and documents tsh-ssh-only access)
- [x] ~~Investigate root cause of the `clamav-freshclam` CDN-block~~ — resolved 2026-08-03: **ClamAV 0.103.x reached end-of-life for database updates on 2025-09-14; the CDN now hard-blocks any 0.103.x
  client.** This fleet runs 0.103.11/.12 uniformly. Verified via `WebSearch` against `blog.clamav.net` and the Cisco-Talos/clamav GitHub issue tracker — not a cw-cluster network/firewall issue, a
  documented upstream EOL enforcement. Fix (not yet done): upgrade to 1.0 or 1.4 LTS fleet-wide.
- [x] ~~Check whether the CDN-block is genuinely cw-cluster-specific~~ — resolved 2026-08-03: **not cluster-specific at all** — it's a ClamAV-upstream version-EOL enforcement (0.103.x blocked CDN-wide
  since 2025-09-14) that would affect any fleet anywhere still on that version, confirmed via external sources, not an artifact of this cluster's network path
- [x] ~~Extend the NBN Accelerate live-validation spot-check to more `nbn_accelerate` sites~~ — done 2026-08-03, full fleet sweep (26/26 reachable `nbn_accelerate` + both `nbn_wh` hosts). Still not
  done: `cw` flavor (no site-level hosts exist to check) and `aurukun-smc03` (unreachable via `tsh ls` at capture time)
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
- [x] ~~Grafana CW exploration — blocked, not started~~ — resolved 2026-08-03: session restart picked up the fixed token, `mcp-grafana-nbn` confirmed live. Explored both `mcp-grafana-apn` (20
  dashboards) and `mcp-grafana-nbn` (9 dashboards); documented the 11 APN-only dashboards (RISE health/watchdog framework, fleet reporting/offline tables, backlog monitoring) and pulled exact `rise_*`
  Prometheus metric names into `02_service-map.md`/`03_communication-flows.md`. See memory-keeper key `skill-smc.discovery.grafana-dashboard-inventory-rise-metrics-20260803`.
- [ ] Root-cause the new confirmed 31h new-looma-smc01 outage (2026-08-01 23:40 → 2026-08-03 06:40 UTC) — Prometheus history confirms whole-host unreachability but no `tsh ssh` was done this session
  to check WAN/power/backhaul logs; worth checking next time that site is accessed live. Not confirmed related to the still-open `my_node_network_device_info` zero-series gap on
  new-looma/old-looma/horn-island.
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

- 2026-08-03 (earlier session) — Operator offered the CW/NBN-Accelerate Grafana instance (`mcp-grafana-nbn`) for exploration. Spent the session getting the MCP connection working rather than exploring
  content: found 3 grafana MCP instances in `~/.claude.json` (unsuffixed = unrelated APN main-org grafana; `-apn` = port 53000; `-nbn` = port 63000, the actual CW instance). Root-caused two
  independent breakages (blank service-account token on `-nbn`, no tunnel on `-apn`), got operator to supply a token and start both tunnels, edited the token into `~/.claude.json` — but `-nbn` still
  401'd at the time. Confirmed via direct `curl` with the `Authorization` header (200 OK) that the token and tunnel were both fine; the blocker was the already-running MCP process caching its old
  blank-token env, needing a restart to pick up the fix. Resolved in the follow-up session above.

- 2026-08-03 — Operator asked what could be causing the fleet-wide ClamAV `freshclam` failure documented in the previous entry. Used `WebSearch` against `blog.clamav.net` and the Cisco-Talos/clamav
  GitHub issues (external, citable sources) rather than speculating from this pack's own data alone. **Confirmed root cause**: ClamAV's 0.103 branch reached end-of-life for database updates on
  2025-09-14; the ClamAV CDN now hard-blocks `freshclam` from any 0.103.x client with HTTP 403. This fleet runs 0.103.11/.12 uniformly. This also explains the 10-month staggered failure-date spread
  from the fleet sweep — each host only flips to `failed` the first time its `freshclam` timer runs after the cutoff, not simultaneously. Converts what had been "root cause not investigated, 3 open
  hypotheses" into a confirmed, externally-verified fact with a concrete fix (upgrade to 1.0/1.4 LTS — not yet done, no automated pipeline exists to do it). Manifest bumped to v0.1.16.

- 2026-08-03 — Operator asked for a thorough analysis of "all the NBN Accelerate sites," including hardware details and the state of installed apps/scripts/services, and asked that reusable scripts be
  captured under `scripts/` with a justfile. Built `scripts/collect-fleet-health.sh` + `scripts/fleet-health.justfile` (new, flavor-agnostic, same read-only safety contract as
  `collect-smc-evidence.sh`) and ran a full sweep of all 26 reachable `nbn_accelerate` hosts plus both `nbn_wh` hosts (28 total) — not a spot-check. First-ever live chassis-model inventory for this
  cluster: 11× AAEON BOXER-6641 + 15× AAEON BOXER-6404 (`nbn_accelerate`, x86), both `nbn_wh` hosts genuine Raspberry Pi (Cortex-A72) — operator confirmed `nbn_wh` is the `wh`-flavor equivalent on
  this cluster. Major finding: `clamav-freshclam` confirmed failed on **26/26** `nbn_accelerate` hosts (escalated from the earlier 2-host finding), with failure dates spanning 10 continuous months —
  an active, ongoing degradation, not a settled past incident. Mid-write-up, operator confirmed `nbn_wh`'s missing overlayroot is a planned-but-not-yet-executed rollout, not a bug — corrected the
  finding's framing accordingly before it shipped as an "unexplained gap." Also found and fixed real bugs in the tooling itself via dogfooding: a mid-run script-file edit that corrupted the first
  capture batch, a `just`-working-directory path assumption that broke all three quick-check recipes, and the same exit-code-of-last-command false-negative bug from the earlier smc_ltp work. Raw
  evidence relocated to `local-knowledge-ansible/ansible-wifi/issues/nbn-accelerate/fleet-hardware-audit-20260803/` per the pack's evidence-retention policy. Manifest bumped to v0.1.15.

- 2026-08-03 — Operator made `tsh login` available for the NBN Accelerate cluster and invited exploratory commands — the first-ever live access this pack has had to that cluster. Ran read-only
  diagnostics against `warakurna-smc01` and `indulkana-smc01` (both `nbn_accelerate`). Every code-inspection-only claim from earlier today's gap-fill checked out confirmed on 2/2 hosts (Teleport
  domain, HTTPS-only portal with on-box TLS termination, mobile-app backend present, ClamAV+Lynis installed, Asterisk absent, non-`smc_ltp` DNS stack). New finding, previously unknown:
  `clamav-freshclam` chronically failing on both hosts (CDN-blocked, exit 17) since 2026-06-21/07-23 — ClamAV's virus database is stale on both, degraded detection despite the daemon staying active.
  Not investigated further and no remediation attempted — read-only exploratory session, root cause left open. Written up in `13_known-issues.md` (new "Known Operational Bugs (NBN Accelerate cluster)"
  section), `08_ansible-authoring.md` (ClamAV/Lynis gate row), `01_overview.md` (evidence-basis note). `nbn_wh`/`cw` flavors remain unvalidated. Manifest bumped to v0.1.14.

- 2026-08-03 — Operator confirmed the final open question from the `smc_ltp`/"low touch" thread: the group-membership mechanism is **a manual step someone has to remember** — no low-touch onboarding
  tooling automatically assigns `smc_ltp` membership, and nothing enforces or checks that it happened. This is the confirmed root cause of the 3-site gap fixed in the immediately-preceding decision (a
  manual, unenforced step is exactly what silently drops during a busy onboarding), and stands as an ongoing risk for any future low-touch site, not a one-off closed by that fix. Added an explicit
  operational note to `08_ansible-authoring.md` recommending `smc_ltp:children` membership be verified explicitly (not assumed) whenever a new low-touch site goes live. Manifest bumped to v0.1.12.
- 2026-08-03 — Operator confirmed and resolved the `smc_ltp`/"low touch" correlation flagged earlier today: every low-touch-onboarded site is meant to be an `smc_ltp` member, and the 3 that weren't
  (`umoona`, `warburton`, `beagle-bay`) were a plain inventory gap, not a coincidental overlap. Operator made and verified the fix directly in `ansible-wifi`: added
  `warburton_smc_ltp`/`beagle-bay_smc_ltp`/`umoona_smc_ltp` host groups plus each site's `:children` block to `inventories/rcp/prod`, matching the existing 4-site pattern. Verified via
  `ansible-inventory --list` (all 7 now under `smc_ltp:children`) and `ansible-playbook --syntax-check smc_ltp.yml` (clean) — a real, uncommitted production Ansible inventory change, not yet run
  against any live SMC. `smc_ltp` membership updated to 7 sites throughout this pack (`08_ansible-authoring.md`, `01_overview.md`, `02_service-map.md`, `13_known-issues.md`, `SKILL.md`,
  `05_troubleshooting.md`, `manifest.json`). Manifest bumped to v0.1.11.

- 2026-08-03 — Operator relayed a newly-confirmed "low touch" onboarding method and site deployment history (from parallel work on the ansible-wifi side): `guda-guda` was the pilot (2025-04-15, a full
  year before the next site), followed by `umoona` (2026-04-12), `warburton`, `beagle-bay`, `pandanus-park`, `old-looma`, `new-looma` in 2026. Cross-checked against
  `local-knowledge-ansible/ansible-wifi/issues/apn/routing-issue/{CHANGELOG,SCRATCHPAD}.md` and the root governance `SCRATCHPAD.md`, all consistent. Notable finding surfaced while writing this up: all
  4 `smc_ltp` sites (from the correction earlier today) are also in the low-touch cohort — flagged as an unresolved, not-concluded correlation rather than asserted as causal, since the mechanism (if
  any) is unconfirmed. Separately grepped the whole `ansible-wifi` repo for `low_touch` and found only one hit, an orphaned host_var (`smc_bases_low_touch_provisioning: true` on `pierre-rcp01`, not a
  cohort member) that no role or playbook reads — "low touch" currently has no Ansible-code representation, it's a process/operational distinction only. Manifest bumped to v0.1.10.
- 2026-08-03 — Operator flagged that `smc_ltp` "has not been explored and documented properly" — correct: prior coverage was only a side effect of the 2026-07-03 DNS RCA, never independently
  re-verified. Direct read of `smc_ltp.yml`, `inventories/rcp/group_vars/smc_ltp.yml`, `inventories/rcp/prod`, `roles/smc_cnmaestro_provisioning/`, `roles/smc_dns_mgmt/tasks/main.yml` found two things
  wrong: (1) membership undercounted as "only guda-guda" — the actual grep-source (`inventories/rcp/prod`) is INI-format, not `.yml`, and was missed by the original grep; real membership is 4 sites
  (`guda-guda`, `pandanus-park`, `old-looma`, `new-looma`). (2) purpose mislabeled "cnMaestro mDNS" — actually two unrelated purposes, neither mDNS: CNMaestro-managed Cambium ePMP/cnPilot
  wireless-backhaul provisioning (separate `smc_ltp.yml` playbook) and a DNS-resolver-stack switch from unbound+stubby to bind9+RPZ (`smc_bases.yml`'s `dns_mgmt` play, zone file literally named
  `db.cambium-rpz`). This session's findings were independently cross-checked against a parallel same-day pass done from the ansible-wifi side, which reached the same conclusions. New dedicated
  section added to `08_ansible-authoring.md`; `01_overview.md`/`02_service-map.md`/`13_known-issues.md`/`SKILL.md`/`05_troubleshooting.md` corrected. LTP's literal expansion is not documented anywhere
  in the codebase — left as an open question rather than guessed. Manifest bumped to v0.1.9.
- 2026-08-03 — Operator asked to fill the NBN Accelerate (`teleport.communitywifi.net.au`) documentation gap: ~95% of the pack was APN-cluster-derived (`apn`/`rcp`/`rct`/`wh`), with NBN Accelerate
  (`cw`/`nbn_accelerate`/`nbn_wh`) only covered by the flavor→domain mapping from 2026-07-31. Ran three parallel research passes (inventory group_vars diff across all 7 flavors; repo-wide grep for
  flavor-conditional branching in roles/templates/playbooks; doc/ADR/OPA search in local-knowledge-ansible/ansible-wifi) rather than assuming the two clusters are identical. Findings: real structural
  differences (no graylog/opensearch or kernel-update pipeline on the cw side; mobile-app backend + kiosk mode on `nbn_accelerate` only; HTTPS-only portal + different blocked-URL domain), a small
  number of genuine flavor-exclusive role gates (ClamAV/Lynis on `nbn_accelerate` only, VoIP/Asterisk on `rcp` only), and that most hardware-class branching (`hotspot_flavor` small-box/big-box) is
  identical across both clusters — it's a hardware split, not a cluster split. Also surfaced a "community wifi" naming collision (used generically for `rcp` sites in `issues/apn/routing-issue/`) and
  an OPA policy coverage gap (`flavors.json`/`environments.json` have no `cw`/`apn`/`rct`/`wh` entries). All new content explicitly flagged as code-inspection-only — no live cw-cluster host was
  accessed this session. Manifest bumped to v0.1.8.
- 2026-07-31 — Removed an incorrect ssh-manager MCP framing from `install.md`/`adapter.md` after two rounds of operator correction, and added the confirmed flavor→Teleport-domain mapping (never
  previously documented). Access is exclusively a direct `tsh ssh root@<hostname>` shell command — no MCP, no `ssh-config.toml`. Domain mapping: `rcp`/`rct`/`wh`/`apn` → `teleport.apn.au`;
  `nbn_accelerate`/`nbn_wh`/`cw` → `teleport.communitywifi.net.au` (all 7 flavors). Added to `01_overview.md` "Remote Access", `install.md`, closed the brief `13_known-issues.md` coverage gap once
  confirmed.
- 2026-07-31 — Broadened the cross-repo feed-back rule (operator-requested, follow-up to the extraction pass) so this pack never needs another full-directory sweep. Root cause of the extraction pass's
  gaps: the existing rule (`AGENTS.md`, ansible-wifi's `rule-002`/`task-patterns.md`/`validation.md`) was worded narrowly around "SMC incident/debug fixes," so design docs, ADRs, OPA changes, and
  scripts never triggered it, and only `project-coherence` (not `skill-slurp-chat`) was named as a trigger. Broadened both sides symmetrically: scope now covers the whole
  `local-knowledge-ansible/ansible-wifi` tree including current/future subfolders (via the `@`-import convention those subfolders already use), the knowledge-type list now explicitly includes
  unimplemented design recommendations/ADRs/OPA/scripts/ROADMAP items, and both `skill-slurp-chat` and `project-coherence` are named as mandatory trigger points with a closeout self-check. Manifest
  bumped to v0.1.7.
- 2026-07-31 — Full extraction pass over `local-knowledge-ansible/ansible-wifi/` (operator-requested, exhaustive). Two subagent audits (`.archcore/` ADRs+rules+specs; `apn/routing-issue/docs/` 20
  files) plus a background `.remember/` completeness sweep found: amata-smc01's disk-failure incident was entirely uncaptured (added to 06/07/13); a bonding-vs-bridging design recommendation for
  RCP/NBN-Accelerate dual-switch WAN circuits (dated the same day, 2026-07-31) was brand new; the OPA policy layer (env-gate/flavor-gate precedence, policy packages) had zero coverage despite one
  passing mention of "the OPA gate" in 08_ansible-authoring.md; `smc_qos`'s "planned, not started" framing in 03_communication-flows.md was stale (the role exists, is just misgated to rct-only); a
  third topology_vars authoring-bug class (role mistagging, rocket-bore-smc01) and a distinct multi-incident site cluster (bungardi-smc01) surfaced only in raw `.remember` daily logs, never promoted
  to an ADR/issue-report. `snapshots/` (59 dirs) and `history/` confirmed via diff to be point-in-time copies of the same governance file, not distinct content — not deep-read. Manifest bumped to
  v0.1.6.
- 2026-07-03 — DNS documentation in `02_service-map.md` had been silently wrong since v0.1.0: the "unbound = RCT flavor, bind = non-RCT flavors" framing was a generalization from the single initial
  RCT-only validation that was never checked against other flavors. Corrected to the real gate (`smc_ltp` inventory-group membership, orthogonal to flavor) via a repo-wide grep during the
  garimba-smc01 RCA. Lesson generalized into `13_known-issues.md`: treat single-host-validated claims in this pack as unverified for other flavors until independently checked.
- 2026-07-03 — Added an explicit "DNS resolution architecture" row to the domain-routing tables in ansible-wifi's `rule-002` and `AGENTS.md` — this domain had no routing entry despite being a
  documented troubleshooting area, which is likely why the garimba-smc01 DNS incident wasn't fed back into this pack until a later `project-coherence` run caught the gap.
- 2026-06-26 — Split monolithic RUNBOOK.md into 13 numbered focused reference files. RUNBOOK.md is now a navigation index only.
- 2026-06-26 — SYSTEM_PROMPT.md line 32 fixed: stale "Reference RUNBOOK.md for full service map…" replaced with specific numbered reference list.
- 2026-06-26 — Dead `references/PROFILE.md` pointer removed from SKILL.md (PROFILE.md is not installed per adapter.md).
- 2026-06-26 — Bootstrap governance scaffold added: AGENTS.md, CLAUDE.md, AI_NAVIGATION.md, context-map.yaml, SCRATCHPAD.md.
- 2026-06-26 — Coherence sweep: repomix.config.json fixed (added .archcore/ content); adapter.md expanded to 16 rows; spec expanded to 17 rows; ARCHITECTURE.md stale token count corrected.

---

## Session history (summaries)

### 2026-08-03 — new-looma-smc01 second whole-host outage confirmed via live Prometheus (v0.1.17 → v0.1.18)
- Operator reported "new-looma-smc01 is back online" — a bare status ping. Rather than just acknowledge it, queried live Prometheus (`mcp-grafana-apn`, still connected from the previous exploration)
  to verify and get exact timestamps.
- Confirmed: `up{job="prometheus"}` and `up{job="node_exporter"}` for `new-looma-smc01` both went dark simultaneously 2026-08-01 23:40 UTC → 2026-08-03 06:40 UTC (31h), then both resumed together —
  whole-host/network outage signature, not a single service crash.
- Found and ruled out a red herring: a second, earlier 18h gap in the same 7-day window (2026-07-29 11:10 → 2026-07-30 05:10 UTC) exactly matches the already-documented topology cross-wiring fix —
  good cross-validation, not a new finding.
- Root cause of the new 31h gap NOT established — no `tsh ssh` this session, Prometheus history only. Logged as confirmed-timeline, open root cause.
- Written to `13_known-issues.md` (new paragraph in the existing new-looma section). Manifest bumped v0.1.17 → v0.1.18; CHANGELOG.md entry added.
- Evidence basis: live `mcp-grafana-apn` `query_prometheus` reads this session; timestamps converted via direct `date -u -r <epoch>`, not estimated.

### 2026-08-03 — Grafana CW exploration unblocked: dashboard inventory + RISE metric names (v0.1.16 → v0.1.17)
- Follow-up to the blocked exploration attempt below: operator confirmed the token fix landed and a restart happened. Confirmed `mcp-grafana-nbn` live (9 dashboards).
- Compared against `mcp-grafana-apn` (20 dashboards) rather than stopping at "it connects now" — found 11 APN-only dashboards, most notably a RISE health/watchdog framework with no NBN counterpart.
- Confirmed (not assumed) that RISE deploys only to `rct`/`wh` via the `flavor=~"rct|wh"` gate in a live panel query. Pulled exact `rise_*` Prometheus metric names for 4 previously-placeholder (`—`)
  textfile collectors in `02_service-map.md`, plus the offline-vs-pending fleet-rollup distinction.
- Wrote a new "RISE Health/Watchdog Framework" subsection into `02_service-map.md` and a new "Dashboard inventory" subsection into `03_communication-flows.md` (11-row table with UIDs/purpose).
- Manifest bumped v0.1.16 → v0.1.17; CHANGELOG.md entry added.
- Evidence basis: live `mcp-grafana-apn`/`mcp-grafana-nbn` reads this session (`search_dashboards`, `get_dashboard_summary`, `get_dashboard_panel_queries`) — not inferred from prior documentation.
- Not yet explored: Data Backlog (0 panels), the two RW-backlog dashboards, Servers Network/System Information (likely out of scope), RISE Dashboard (`rise-stage0_5`, older rollout view) — flagged in
  Open Items.

### 2026-08-03 — ClamAV freshclam root cause confirmed via WebSearch (v0.1.15 → v0.1.16)
- Operator asked what could be causing the fleet-wide ClamAV failure documented in the previous entry, rather than settling for the 3 open hypotheses already written up.
- Verified via `WebSearch` against `blog.clamav.net` and Cisco-Talos/clamav GitHub issues before answering, per the "never guess, verify" convention.
- Confirmed: ClamAV 0.103.x reached end-of-life for database updates on 2025-09-14; the CDN hard-blocks any 0.103.x client since then. This fleet runs 0.103.11/.12 uniformly. Explains the 10-month
  staggered failure-date spread from the fleet sweep exactly (each host trips the block on its own timer's first post-cutoff run, not simultaneously).
- Not cw-cluster-specific — documented upstream behavior affecting any fleet on this ClamAV branch. Fix: upgrade to 1.0/1.4 LTS (not yet done, no automated version pipeline exists for this cluster).
- Updated `13_known-issues.md` (bug row rewritten from "not investigated" to "confirmed"), `08_ansible-authoring.md`, `01_overview.md`; `manifest.json` gained a 3rd diagnostics entry.
- Manifest bumped v0.1.15 → v0.1.16; CHANGELOG.md entry added.
- Evidence basis: external sources (ClamAV's own EOL announcement, community-reported GitHub issues matching the exact error signature), cross-checked against this session's own captured data for
  consistency.

### 2026-08-03 — Full NBN Accelerate fleet sweep: 28 hosts, hardware inventory, fleet-wide ClamAV finding (v0.1.14 → v0.1.15)
- Operator asked for a thorough analysis of all NBN Accelerate sites (hardware + installed apps/scripts/services state), and to capture reusable scripts under `scripts/` with a justfile.
- Built `scripts/collect-fleet-health.sh` (new, flavor-agnostic, read-only, 4 bundled captures/host to stay tractable at fleet scale over satellite) and `scripts/fleet-health.justfile`. Ran against
  all 26 reachable `nbn_accelerate` hosts + both `nbn_wh` hosts (28 total, `aurukun-smc03` unreachable).
- First-ever live hardware inventory for this cluster: 11× BOXER-6641 + 15× BOXER-6404 (`nbn_accelerate`), 2× genuine Raspberry Pi/Cortex-A72 (`nbn_wh` — operator-confirmed `wh`-flavor equivalent).
- Major finding: `clamav-freshclam` confirmed failed on **26/26** `nbn_accelerate` hosts (up from the earlier 2), failure dates spanning 10 continuous months — an active, ongoing degradation.
- Mid-session, operator confirmed `nbn_wh`'s missing overlayroot is a planned rollout, not a bug — corrected that finding's framing before it shipped incorrectly.
- Also found and fixed real tooling bugs via dogfooding: a mid-run script-file edit that corrupted the first capture batch (11/28 hosts real, 17/28 crashed to zero-byte files, required a second batch
  run); a `just`-working-directory path assumption that silently broke all 3 quick-check recipes; a nested-directory `mv` bug when merging the two capture batches; the same exit-code-of-last-command
  false-negative from the earlier smc_ltp session, recurring in the justfile recipes.
- Other findings: kernel-version drift (5.15.0-79 to -133) corroborating the earlier no-automated-kernel-pipeline structural finding; `koonibba-smc01` at 95% disk usage with the oldest kernel;
  `isc-dhcp-server6` failed 28/28 (confirmed benign, IPv6 disabled by policy); `fwupd-refresh` failed on 3/28 (minor); `nbn_wh` zram/swap absence contradicting the platform table's universal RPi-zram
  claim (unresolved).
- Written to `07_hardware-overlay.md` (new hardware-inventory section), `13_known-issues.md` (bugs section rewritten for full fleet), `01_overview.md`, `08_ansible-authoring.md`,
  `04_dependency-tree.md` (separately, smc_ltp/ClamAV/Lynis entries + a flagged naming-collision question).
- Raw evidence relocated to `local-knowledge-ansible/ansible-wifi/issues/nbn-accelerate/fleet-hardware-audit-20260803/` per the pack's evidence-retention policy (skill-smc holds analysis/tooling, not
  case evidence).
- Manifest bumped v0.1.14 → v0.1.15; CHANGELOG.md entry added.
- Evidence basis: direct `tsh ssh root@<host>` read-only commands, this session, 28/28 hosts confirmed by file-size verification post-merge.

### 2026-08-03 — First live NBN Accelerate validation: cluster comparison confirmed, ClamAV CDN-block found (v0.1.13 → v0.1.14)
- Operator made `tsh login` for the NBN Accelerate cluster (`teleport.communitywifi.net.au`) available and invited exploratory commands — first-ever live access this pack has had to that cluster,
  after a full day of code-inspection-only NBN Accelerate content.
- Ran read-only diagnostics against `warakurna-smc01` and `indulkana-smc01` (both `nbn_accelerate`): Teleport domain, HTTPS-only portal (permanent redirect, on-box TLS termination), mobile-app
  backend, ClamAV+Lynis presence, Asterisk absence, non-`smc_ltp` DNS stack — every claim confirmed, 2/2 hosts.
- New finding: `clamav-freshclam.service` failing on both hosts (identical signature — exit 17, `Forbidden; Blocked by CDN`, permanent give-up) since 2026-06-21 (`indulkana`) / 2026-07-23
  (`warakurna`) — ClamAV's virus database is stale/frozen on both, a real degradation of the documented cw-only security hardening. Not investigated further; no remediation attempted (read-only
  session).
- Written to `13_known-issues.md` (new "Known Operational Bugs (NBN Accelerate cluster)" section + coverage-gap row update), `08_ansible-authoring.md` (ClamAV/Lynis gate row), `01_overview.md`
  (evidence-basis paragraph), `manifest.json` (new `diagnostics` entry — first use of that field).
- Manifest bumped v0.1.13 → v0.1.14; CHANGELOG.md entry added.
- Evidence basis: direct `tsh ssh root@<host>` read-only commands, this session. `nbn_wh`/`cw` flavors and every other `nbn_accelerate` site beyond these 2 remain unvalidated.

### 2026-08-03 — project-coherence sweep: routing/architecture staleness fixed (v0.1.12 → v0.1.13)
- Ran `project-coherence` across today's cumulative content changes (NBN Accelerate gap-fill → smc_ltp exploration → 7-site correction → manual-mechanism confirmation). Content files (Tier 1) were
  already coherent from the piecemeal edits; this pass caught Tier 2/routing-layer drift.
- Fixed: `context-map.yaml`'s `ansible_authoring`/`smcbox_basics` routing descriptions (hadn't been extended to mention `smc_ltp`/onboarding or NBN Accelerate); `ARCHITECTURE.md`'s governance-pack
  size figure (stale "~125k chars" since 2026-06-26, now ~470k); `RUNBOOK.md`/`AI_NAVIGATION.md`'s `08_ansible-authoring.md` rows (extended to match the pattern already applied to `01_overview.md`).
- Stale-reference grep validated clean — all "old phrase" hits are correctly-framed historical narrative, no live incorrect claims.
- `.remember/today-2026-08-03.md` reviewed and found out of scope — self-managed by the global `remember` skill, not authored by skill-smc's own governance.
- Manifest bumped v0.1.12 → v0.1.13; CHANGELOG.md entry added; governance pack regenerated (final pass).
- Evidence basis: this session's own systematic file-by-file scan per the `skill-project-coherence` checklist.

### 2026-08-03 — smc_ltp/"low touch" mechanism confirmed: manual, unenforced step (v0.1.11 → v0.1.12)
- Final piece of the same-day `smc_ltp`/"low touch" thread: operator confirmed the mechanism is a manual step someone has to remember — no tooling automatically assigns `smc_ltp` membership for a new
  low-touch site, and nothing checks or enforces it.
- This directly explains the root cause of the 3-site gap fixed in the previous entry, and reframes it as an ongoing risk (any future low-touch site could be missed the same way), not a closed
  one-off.
- Added an explicit operational note to `08_ansible-authoring.md` ("smc_ltp Sub-Group") recommending membership be verified explicitly for future low-touch sites; updated the `13_known-issues.md`
  row's status and framing; `manifest.json` stable_fact updated, confidence raised to 0.92.
- Manifest bumped v0.1.11 → v0.1.12; CHANGELOG.md entry added.
- Evidence basis: operator-confirmed directly, relayed to this session; not independently verifiable from Ansible source (confirms an absence of automation, not a code finding).

### 2026-08-03 — smc_ltp/"low touch" correlation resolved: 3 sites added, 7 members confirmed (v0.1.10 → v0.1.11)
- Direct follow-up to the "low touch" onboarding entry below, same day: operator confirmed the previously-flagged correlation is real, not coincidental — every low-touch site is meant to be an
  `smc_ltp` member.
- Operator made and verified the fix directly in `ansible-wifi`: added `warburton_smc_ltp`/`beagle-bay_smc_ltp`/`umoona_smc_ltp` host groups + `:children` blocks to `inventories/rcp/prod`, matching
  the existing 4-site pattern. Verified via `ansible-inventory --list` (all 7 under `smc_ltp:children`) and `ansible-playbook --syntax-check smc_ltp.yml` (clean) — uncommitted, not yet run against any
  live SMC.
- Updated `smc_ltp` membership from 4 to 7 sites everywhere it's mentioned in this pack: `08_ansible-authoring.md`, `01_overview.md`, `02_service-map.md`, `13_known-issues.md`, `SKILL.md`,
  `05_troubleshooting.md`, `manifest.json`. The "flagged, not concluded" framing replaced with "resolved" throughout.
- Underlying mechanism (does low-touch tooling itself assign `smc_ltp` membership, or is it manual) remains unestablished — only the intended end-state membership is now confirmed.
- Manifest bumped v0.1.10 → v0.1.11; CHANGELOG.md entry added.
- Evidence basis: operator-directed and operator-verified change relayed to this session; not independently re-verified, not yet run against any live SMC or committed to `ansible-wifi`.

### 2026-08-03 — "Low touch" onboarding method and site deployment history added (v0.1.9 → v0.1.10)
- Operator relayed operator-confirmed install dates for a cohort of `rcp` sites, naming a "low touch" onboarding method: `guda-guda` pilot (2025-04-15), then
  `umoona`/`warburton`/`beagle-bay`/`pandanus-park`/`old-looma`/`new-looma` across 2026.
- Cross-checked against `local-knowledge-ansible/ansible-wifi/issues/apn/routing-issue/{CHANGELOG,SCRATCHPAD}.md` and root governance `SCRATCHPAD.md` — consistent, and those docs had already
  independently noted the same finding from the ansible-wifi side same day.
- Surfaced (this session) that all 4 `smc_ltp` sites are also low-touch sites — flagged as unresolved correlation, not concluded. Also grepped `ansible-wifi` for `low_touch`: exactly one hit, an
  orphaned host_var on an uninvolved host, never read by any role/playbook.
- New "'Low Touch' Onboarding Method and Site Deployment History" section added to `08_ansible-authoring.md`; `13_known-issues.md` gained an open-question row; the pre-existing "cnmaestro-provisioning
  internals" coverage-gap row updated to reflect the smc_ltp findings from the prior session.
- Manifest bumped v0.1.9 → v0.1.10; CHANGELOG.md entry added.
- Evidence basis: operator-provided dates, cross-referenced against `local-knowledge-ansible/ansible-wifi` docs and this session's own repo-wide grep; not live-validated against any site.

### 2026-08-03 — smc_ltp properly explored and documented (v0.1.8 → v0.1.9)
- Operator flagged smc_ltp as under-explored — a fair call: prior coverage was purely a side effect of the 2026-07-03 DNS RCA, never independently re-verified since.
- Direct read of `smc_ltp.yml`, `inventories/rcp/group_vars/smc_ltp.yml`, `inventories/rcp/prod`, `roles/smc_cnmaestro_provisioning/`, `roles/smc_dns_mgmt/tasks/main.yml` found and fixed two errors:
  membership undercount (was "only guda-guda", actually 4 sites — the INI-format `prod` file was missed by the original `.yml`-scoped grep) and a purpose mislabel ("cnMaestro mDNS" — actually two
  unrelated purposes: CNMaestro Cambium ePMP/cnPilot wireless-backhaul provisioning via a separate `smc_ltp.yml` playbook, and a DNS-resolver-stack switch to bind9/RPZ via `smc_bases.yml`'s `dns_mgmt`
  play).
- Findings cross-checked against an independent same-day pass on the ansible-wifi side — same conclusions reached.
- New "smc_ltp Sub-Group" section added to `08_ansible-authoring.md`; `01_overview.md`, `02_service-map.md`, `13_known-issues.md`, `SKILL.md`, `05_troubleshooting.md` corrected/cross-referenced. LTP's
  literal acronym expansion documented as an open question, not guessed.
- Manifest bumped v0.1.8 → v0.1.9; CHANGELOG.md entry added.
- Evidence basis: this session's direct file reads of ansible-wifi source; not live-validated against any of the 4 member hosts.

### 2026-08-03 — NBN Accelerate cluster gap-fill (v0.1.7 → v0.1.8)
- Operator-requested: document how the NBN Accelerate cluster (`cw`/`nbn_accelerate`/`nbn_wh`, `teleport.communitywifi.net.au`) differs from the APN cluster (`apn`/`rcp`/`rct`/`wh`,
  `teleport.apn.au`), since ~95% of prior content was APN-derived.
- Three parallel Explore-agent research passes: (1) inventory `group_vars`/`prod` diff across all 7 flavors — found cw-cluster is structurally thinner (no graylog/opensearch, no kernel-update Jenkins
  pipeline) with its own extras (mobile-app backend, kiosk mode, HTTPS-only portal, distinct blocked-URL redirect); (2) repo-wide grep for flavor-conditional branching in roles/templates — found the
  selector is `hotspot_flavor` (hardware class, spans both clusters identically) or `inventory_dir.split('/')|last` (exact flavor, drives a small number of genuine flavor-exclusive gates: ClamAV/Lynis
  on `nbn_accelerate` only, VoIP/Asterisk on `rcp` only), and nothing branches on the literal strings cw/community/communitywifi; (3) doc/ADR/OPA search in local-knowledge-ansible/ansible-wifi — found
  a "community wifi" naming collision (generic term for `rcp` sites in `issues/apn/routing-issue/`) and an OPA policy coverage gap (`flavors.json`/`environments.json` missing `cw`/`apn`/`rct`/`wh`).
- Wrote findings into `01_overview.md` (new comparison section + selector mechanism), `08_ansible-authoring.md` (new flavor-gate reference table), `10_captive-portal.md` (new §11.9 protocol diffs),
  `13_known-issues.md` (coverage-gap row + 2 new staleness-risk entries) — all explicitly labeled code-inspection-only, not live-validated.
- Routing tables (`RUNBOOK.md`, `SKILL.md`, `AI_NAVIGATION.md`) updated for the `01_overview.md` row; manifest bumped v0.1.7 → v0.1.8; CHANGELOG.md entry added.
- Evidence basis: this session's direct file reads + three Explore-agent research passes (no prior memory-keeper/project-context entry existed for this topic).

### 2026-07-31 — Full extraction pass + ssh-access/Teleport-domain corrections + feed-back governance broadening
- Exhaustive sweep of `local-knowledge-ansible/ansible-wifi/**` (operator-requested): ~15 new knowledge items across 8 reference files, 2 lint-gate scripts promoted/genericized, full coherence pass.
  v0.1.5 → v0.1.6.
- Operator corrected an invented ssh-manager MCP framing (twice) — access is direct `tsh ssh`, no MCP — and provided the confirmed flavor→Teleport-domain mapping, both fixed across
  `install.md`/`adapter.md`/`01_overview.md`/`13_known-issues.md`.
- Root-caused why the extraction pass found gaps at all: the cross-repo feed-back rule (this pack's `AGENTS.md` + ansible-wifi's `AGENTS.md`/`rule-002`/`task-patterns.md`/`validation.md`) was worded
  narrowly around "incident/debug fixes" and only named `project-coherence`, not `skill-slurp-chat`, as a trigger. Broadened all of it symmetrically to whole-tree scope, a wider knowledge-type list,
  both trigger points, and a closeout self-check. v0.1.6 → v0.1.7.
- Evidence basis: this session; memory-keeper keys `skill-smc.extraction.local-knowledge-sweep-20260731`, `skill-smc.correction.ssh-access-and-teleport-domains-20260731`,
  `skill-smc.governance.feedback-rule-broadening-20260731`

### 2026-07-03 (ansible-wifi session, project-coherence run) — DNS architecture corrections + garimba-smc01 failure mode
- Triggered by `project-coherence` on ansible-wifi after the garimba-smc01 DNS RCA (revisions 2-3) surfaced factual errors and a coverage gap in this pack's DNS documentation.
- `references/02_service-map.md`: fixed the DNS-resolver-by-flavor mental model (real gate is `smc_ltp` group, not flavor), fixed Stubby's documented listen port (60053, not 5353), added the
  previously-undocumented `systemd-resolved` host-DNS row and Stubby's single-upstream/no-failover autossh-local-forward chain.
- `references/06_failure-modes.md`: added the garimba-smc01 domain-specific DNS resolution delay failure signature.
- `references/13_known-issues.md`: added a coverage-gap entry for the host-DNS architecture and a new "Fleet-Wide Architecture Risks" section (Stubby no-failover, no monitoring on the autossh local
  forward).
- `.archcore/rules/rule-002-*.md` and `AGENTS.md` (both ansible-wifi): added an explicit DNS domain routing row — this domain had no routing entry, which is likely why the incident wasn't fed back
  into this pack sooner.
- Version bumped 0.1.3 → 0.1.4; CHANGELOG.md updated.
- Evidence basis: ansible-wifi 2026-07-03 session MK keys `ansible-wifi.smc.garimba-smc01.dns-rca-revision2-corrections.20260703`,
  `ansible-wifi.smc.garimba-smc01.dns-rca-revision3-corrections.20260703`, `ansible-wifi.smc.garimba-smc01.dns-repo-facts.20260703`

### 2026-06-26 (ansible-wifi session) — references/10-13 content updates + AGENTS.md project-coherence checklist
- `references/10_captive-portal.md`, `references/11_vagrant-lab.md`, `references/12_content-filtering.md` received content updates from ansible-wifi RUNBOOK audit: captive portal two-tier arch,
  Eclipse config.txt sync, PHP-FPM SetHandler, a2enconf alternative, PHP short_open_tag, vsmc networkd race chain, Eclipse identity model, MAC randomization table, CAKE fair queuing on bridge_501.
- Added `## Project-coherence checklist` to `AGENTS.md` — explicit Tier 1-4 update instructions for when project-coherence runs on skill-smc, plus cross-repo trigger rule for ansible-wifi sessions.
- Version bumped to v0.1.3; CHANGELOG.md updated.
- Evidence basis: ansible-wifi 2026-06-26 session MK keys `ansible-wifi.runbook.sections-11-12-13.20260626`, `ansible-wifi.runbook.gap-fill-audit.20260626`

### 2026-06-26 — Progressive-disclosure restructure
- Split 1724-line RUNBOOK.md into 13 numbered reference files (01_ through 13_).
- Moved KNOWN_ISSUES.md to references/13_known-issues.md.
- RUNBOOK.md replaced with 48-line navigation index.
- All cross-references updated; version bumped to 0.1.2.
- Evidence basis: session hook history (UserPromptSubmit context)

### 2026-06-26 — Pack audit and fixes
- Identified dead PROFILE.md reference in SKILL.md; removed.
- Fixed stale SYSTEM_PROMPT.md reference to monolithic RUNBOOK.md content.
- Confirmed adapter.md, install.md, manifest.json consistent with new structure.
- Evidence basis: direct file reads this session

### 2026-06-26 — Bootstrap governance scaffold + archcore promote + docs
- Added AGENTS.md, CLAUDE.md, AI_NAVIGATION.md, context-map.yaml, repomix.config.json, SCRATCHPAD.md.
- Initialized .archcore/, promoted 5 candidates (3 rules, 1 ADR, 1 spec).
- Added README.md, ARCHITECTURE.md.

### 2026-06-26 — Coherence sweep
- Fixed repomix.config.json: .archcore/ content now included; README.md, ARCHITECTURE.md, SCRATCHPAD.md added.
- Expanded adapter.md (5 → 16 rows) and spec file-roles (12 → 17 rows) to cover all governance files.
- Corrected ARCHITECTURE.md stale repomix count. Governance bundle: 145,706 chars.

---

## Next actions

- Root-cause the new-looma-smc01 31h outage (2026-08-01→2026-08-03) next time `tsh ssh` access to that site is available — check WAN/backhaul/power logs; confirm or rule out any link to the still-open
  `my_node_network_device_info` gap
- Explore the remaining unreviewed Grafana dashboards flagged 2026-08-03 (Data Backlog, RW-backlog pair, Servers Network/System Information, RISE Dashboard `rise-stage0_5`) next time Grafana access is
  used — see Open Items
- Cross-reference the RW-backlog dashboards against `autossh-prometheus-federation` in `02_service-map.md` once reviewed — may reveal federation-pipeline health signals not currently documented
- Install v0.1.17 to `~/.claude/skills/skill-smc/` per `install.md` (not yet done — same open item since v0.1.2)
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

- memory-keeper channel: `skill-smc` / keys added 2026-09-08 (skill-ai-it refresh slurp): `skill-smc.decision.skill-ai-it-refresh-mode-correction-20260908`,
  `skill-smc.decision.ai-navigation-declared-manual-20260908`, `skill-smc.note.check-governance-adopted-and-tuning-20260908`, `skill-smc.progress.v0134-refresh-20260908`,
  `skill-smc.note.mk-pc-backend-divergence-20260908`. Checkpoint: `slurp-20260908-skill-ai-it-refresh` (both backends).
- project-context project ID `0bf38158-d30f-4b0f-8653-f6f93d22a068`: notes added 2026-09-08 mirroring the same session; **note this backend was ~5 weeks stale (last prior entry 2026-08-03) before this
  update** — see `skill-smc.note.mk-pc-backend-divergence-20260908` for the memory-keeper-only entries from 2026-09-07 that were never mirrored here.
- memory-keeper channel: `skill-smc` / keys added 2026-08-03 (this pass): `skill-smc.discovery.new-looma-outage-confirmed-20260803`
- memory-keeper channel: `skill-smc` / keys added 2026-08-03 (earlier pass): `skill-smc.discovery.grafana-dashboard-inventory-rise-metrics-20260803`
- memory-keeper channel: `skill-smc` / keys added 2026-08-03 (earlier pass): `skill-smc.task.grafana-cw-exploration-blocked-20260803`
- memory-keeper channel: `skill-smc` / keys added 2026-08-03 (earlier pass): `skill-smc.discovery.clamav-fix-mechanism-20260803`
- memory-keeper channel: `skill-smc` / keys added 2026-08-03 (earlier pass): `skill-smc.correction.clamav-freshclam-root-cause-20260803`
- memory-keeper channel: `skill-smc` / keys added 2026-08-03 (earlier pass): `skill-smc.extraction.nbn-accelerate-full-fleet-sweep-20260803`
- memory-keeper channel: `skill-smc` / keys added 2026-08-03 (earlier pass): `skill-smc.coherence.routing-sweep-20260803`
- memory-keeper channel: `skill-smc` / keys added 2026-08-03 (earlier pass): `skill-smc.correction.smc-ltp-manual-mechanism-20260803`
- memory-keeper channel: `skill-smc` / keys added 2026-08-03 (earlier pass): `skill-smc.correction.smc-ltp-seven-sites-20260803`
- memory-keeper channel: `skill-smc` / keys added 2026-08-03 (earlier pass): `skill-smc.discovery.low-touch-onboarding-20260803`
- memory-keeper channel: `skill-smc` / keys added 2026-08-03 (earlier pass): `skill-smc.correction.smc-ltp-exploration-20260803`
- memory-keeper channel: `skill-smc` / keys added 2026-08-03 (earlier pass): `skill-smc.extraction.nbn-accelerate-cluster-gapfill-20260803`, `skill-smc.decision.nbn-accelerate-naming-20260803`
- memory-keeper channel: `skill-smc` / keys added 2026-07-31: `skill-smc.extraction.local-knowledge-sweep-20260731`, `skill-smc.correction.ssh-access-and-teleport-domains-20260731`,
  `skill-smc.governance.feedback-rule-broadening-20260731`
- memory-keeper channel: `skill-smc` / earlier keys: `skill-smc.structure.progressive-disclosure-20260626`, `skill-smc.audit.fixes-20260626`, `skill-smc.governance.bootstrap-20260626`,
  `skill-smc.governance.archcore-promote-20260626`, `skill-smc.docs.readme-architecture-20260626`, `skill-smc.coherence-sweep-20260626`
- memory-keeper checkpoint: `slurp-20260803-skill-smc-new-looma-outage` (ID: af68fc31) — 402 context items; earlier today: `slurp-20260803-skill-smc-grafana-rise-dashboard-inventory` (ID: ce01b46c) —
  401 context items; earlier today: `slurp-20260803-grafana-cw-blocked` (ID: cdb3b0ab) — 400 context items; earlier today: `slurp-20260803-skill-smc-clamav-fix-mechanism` (ID: d784984d) — 399 context
  items; earlier today: `slurp-20260803-skill-smc-clamav-root-cause` (ID: 609d0e06), `slurp-20260803-skill-smc-nbn-accelerate-fleet-sweep` (ID: eea021c1),
  `slurp-20260803-skill-smc-nbn-accelerate-live-validation` (ID: f293e11b), `slurp-20260803-skill-smc-coherence-sweep-close` (ID: fcb5bd7d), `slurp-20260803-skill-smc-ltp-manual-mechanism` (ID:
  a0b0525f), `slurp-20260803-skill-smc-ltp-seven-sites` (ID: 0e74230f), `slurp-20260803-skill-smc-low-touch-onboarding` (ID: 7c2ca18e), `slurp-20260803-skill-smc-smc-ltp-correction` (ID: d6fbd843),
  `slurp-20260803-skill-smc-nbn-accelerate-gapfill` (ID: 4052409c); earlier: `slurp-20260731-skill-smc-extraction-and-governance` (ID: 4fc94978), `slurp-20260626-skill-smc-governance` (ID: 7a4df5b2),
  `slurp-20260626-skill-smc-coherence` (ID: 85dae74b)
- project-context project ID: `0bf38158-d30f-4b0f-8653-f6f93d22a068` / checkpoint: `64a823ab-dce6-4614-a7a9-6fbe917847da` (2026-08-03, new-looma-outage); earlier today:
  `44e60b56-3e94-43fc-9ab8-23ab53a420a1` (grafana-rise-dashboard-inventory); earlier today: `37a5570c-f630-45ec-9f98-1290c6fadaa9` (grafana-cw-blocked); earlier today:
  `6c74412b-4985-447d-8e8d-3b41a30c21d2`; earlier today: `3bdde77e-2467-40ff-b901-fc62af00e8ed`, `89ad9338-2f8d-4310-bc73-98426b36c17b`, `ec1c8cdd-403a-44cd-b801-855e30857430`,
  `15a8bedd-5d96-4695-a317-4ad3de431974`, `bc5e696a-2db0-4a1b-ba39-6915250fbb0e`, `0df101a9-ff28-4b63-b586-6763d9c2b4ce`, `60be456a-1295-4cca-bb57-358cdc54d21b`,
  `24964bec-35f6-41f9-bbff-015223d7f993`, `683aadef-e04b-4e0d-8cca-429f3cf2f67a`; earlier: `8564d8a7-eba1-405e-a019-4575a12311c5` (2026-07-31), `1b4851d2`, `e07d1aff`
