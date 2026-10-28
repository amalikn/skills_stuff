---
Title: Changelog
Category: change-log
Status: current
Summary: Newest entries only; older ones rotate to docs/history (search with --find, print with --show).
Kind: log
Budget: 200 lines, 25 KB
Archive: docs/history/ (`--find`, `--show`)
Last rotated: 20261028_1242
Authority: record
Scope: Dated changes to this project
Last reviewed: 2026-10-27
---

# skill-smc Changelog

## Contents

- [20261028_1242 — AVR serial collision verified on warehouse-rct01 (v0.9.2 -> v0.9.3)](#20261028_1242--avr-serial-collision-verified-on-warehouse-rct01-v092---v093)
- [20261028_1224 — rct-tstik iridium change: self-persisting command, symlinked copy sources, AVR flash (v0.9.1 -> v0.9.2)](#20261028_1224--rct-tstik-iridium-change-self-persisting-command-symlinked-copy-sources-avr-flash-v091---v092)
- [20261027_2015 — Slurp close: governed-file adoption, sibling write-backs (v0.9.0 -> v0.9.1)](#20261027_2015--slurp-close-governed-file-adoption-sibling-write-backs-v090---v091)
- [20261027_2012 — scripts/ arranged into job folders; layout and catalogue checks (v0.8.9 -> v0.9.0)](#20261027_2012--scripts-arranged-into-job-folders-layout-and-catalogue-checks-v089---v090)
- [20261027_1953 — Staleness audit: branch reach, two checker gaps, version rule (v0.8.8 -> v0.8.9)](#20261027_1953--staleness-audit-branch-reach-two-checker-gaps-version-rule-v088---v089)
- [20261027_1947 — ansible_change_reach probe; July apt fixes and smc_ltp fix not on rise (v0.8.7 -> v0.8.8)](#20261027_1947--ansible_change_reach-probe-july-apt-fixes-and-smc_ltp-fix-not-on-rise-v087---v088)
- [20261027_1937 — Open-items tracker reviewed (v0.8.6 -> v0.8.7)](#20261027_1937--open-items-tracker-reviewed-v086---v087)
- [20261027_1922 — Quoted code excerpt restored after a markdown hook bug (v0.8.5 -> v0.8.6)](#20261027_1922--quoted-code-excerpt-restored-after-a-markdown-hook-bug-v085---v086)
- [20261027_1459 — smc_change self-repair, kohana cron_job, lockstep timing; link health probe (v0.8.4 -> v0.8.5)](#20261027_1459--smc_change-self-repair-kohana-cron_job-lockstep-timing-link-health-probe-v084---v085)
- [20261027_1207 — Teleport re-join without a tunnel; first rcp PHP apply (v0.8.3 -> v0.8.4)](#20261027_1207--teleport-re-join-without-a-tunnel-first-rcp-php-apply-v083---v084)
- [20261027_1050 — smc_change: done SMCs skipped before connecting, runs per flavor, retries, TASK_TIMING, journal freeze (v0.8.2 -> v0.8.3)](#20261027_1050--smc_change-done-smcs-skipped-before-connecting-runs-per-flavor-retries-task_timing-journal-freeze-v082---v083)
- [20261026_2222 — smc_change: new order passed on two Pis; second drop at chroot dpkg (v0.8.1 -> v0.8.2)](#20261026_2222--smc_change-new-order-passed-on-two-pis-second-drop-at-chroot-dpkg-v081---v082)
- [20261026_2146 — smc_change drop-proof installs, lower dir first, runs table (v0.8.0 -> v0.8.1)](#20261026_2146--smc_change-drop-proof-installs-lower-dir-first-runs-table-v080---v081)
- [20261026_1844 — smc_change: Pi clock wait, remount retry, lower_busy, http timeout/retries, probe survives a dropped session, resume by default (v0.7.9 -> v0.8.0)](#20261026_1844--smc_change-pi-clock-wait-remount-retry-lower_busy-http-timeoutretries-probe-survives-a-dropped-session-resume-by-default-v079---v080)
- [20261026_1701 — smc_change safe recovery, completion after cleanup and phase timing (v0.7.8 -> v0.7.9)](#20261026_1701--smc_change-safe-recovery-completion-after-cleanup-and-phase-timing-v078---v079)
- [20261026_1617 — smc_change PHP verify: soak from the restart, start_now, named command checks, tstik AVR and 8080 checks; tstik-capture AVR counts (v0.7.7 -> v0.7.8)](#20261026_1617--smc_change-php-verify-soak-from-the-restart-start_now-named-command-checks-tstik-avr-and-8080-checks-tstik-capture-avr-counts-v077---v078)
- [20261026_1534 — smc_change backup.shared: name-identified backup files kept once for all SMCs (v0.7.6 -> v0.7.7)](#20261026_1534--smc_change-backupshared-name-identified-backup-files-kept-once-for-all-smcs-v076---v077)
- [20261026_1506 — smc_change flow map in parts, one E2E page per change spec (v0.7.5 -> v0.7.6)](#20261026_1506--smc_change-flow-map-in-parts-one-e2e-page-per-change-spec-v075---v076)

## 20261028_1242 — AVR serial collision verified on warehouse-rct01 (v0.9.2 -> v0.9.3)

- `references/06_failure-modes.md`: Learned entry: rct-tstik and the AVR loader collide on `/dev/ttyS0` (warehouse-rct01 test: tstik run 0/24 good
  while overlapped, 24/24 before and after); tstik re-runs stty 19200 and flushes before every send; pause tstik cron for a flash; frame format.
- `references/02_service-map.md`: deploy reference names `roles/smc_application/tasks/main.yml` instead of a person.

## 20261028_1224 — rct-tstik iridium change: self-persisting command, symlinked copy sources, AVR flash (v0.9.1 -> v0.9.2)

- `references/19_smc-change-role.md`: new section for the smc_change spec `rct-tstik-iridium-update` (canary aeroplane-1-smc01 passed 8/8 gates, 592 s): spec values naming inventory vars, a command
  action that persists itself into the lower dir (no chroot, no reboot) with a `proves` check of both HEADs, copy sources served by a directory symlink that leaves the RULE-007 fingerprint unchanged,
  copy rollback cannot remove a file that did not exist (patch in ansible-wifi `plans/`), checks false before the change go in `proves`, check mode can still act.
- `references/06_failure-modes.md`: Learned entry on the AVR firmware flash (one "Protocol Error" at block 13, passed on retry; serial contention with cron's `update:stats` suspected, UNVERIFIED), the
  vendor loader's exit 0 everywhere, endless retry and 19500 baud, and `py_avrloader_v2.py` exit codes and two-digit minor version; hand copies on an overlay SMC vanish at reboot.
- `references/01_overview.md`: Tstik open question answered: Iridium keeps `rct-tstik` on `release/iridium` (1318c7b) with AVR firmware V3.07; `smc_bases_iridium: true` also switches portal branch,
  latlon role and Teleport lat/lon labels.
- `references/02_service-map.md`: how tstik is served (`php -S` from cron, not Apache), the iridium routes, the self test, tracked `config.json`.
- Source: local-knowledge-ansible ansible-wifi change record `rct-tstik-iridium-update-20261028_1221.md`.

## 20261027_2015 — Slurp close: governed-file adoption, sibling write-backs (v0.9.0 -> v0.9.1)

- skill-ai-it `adopt_governed_files.py --apply`: recipes `roles`, `govern`, `budget`, `changelog-entry`, `move-sections`, `outline`, `section`; file roles
  in `check`; front matter on `README.md`, `AGENTS.md`, `AI_NAVIGATION.md`, `ARCHITECTURE.md`, `CHANGELOG.md`, `SCRATCHPAD.md`; `scripts/role-check-baseline.json`
  (kept at `scripts/` with the other baselines; `check_scripts_layout` allows it).
- Write-backs: skill-staleness-audit (`inverse_sweep.py` `(+ .txt)` twins, two tool hazards), skill-coder (Learned: cherry-pick simulation with
  `git merge-tree`; read branch lists whole), skill-cambium (paths to `scripts/access/teleport-tunnel.sh`).
- Incident: a `grep` printing ansible-wifi `group_vars` content was blocked by the ansible-vars-guard hook (19:39); rerun with file names only.
- Open, not decided: `updated_at` format; dropping tracker items 5 and 10 (SCRATCHPAD Open items).

## 20261027_2012 — scripts/ arranged into job folders; layout and catalogue checks (v0.8.9 -> v0.9.0)

- 43 scripts moved (`git mv`) into `scripts/ansible|access|probes|capture|fleet|metrics|routing|switch/`; tests beside their script; the two
  sub-justfiles and the governance files stay at `scripts/` (operator, 2026-10-27). Pack-root and `.graylog-token` paths now resolve two levels
  up; `fleet-health.justfile` calls `./<folder>/<script>`. 102 path references in live files updated; CHANGELOG, `docs/history/`, `docs/audits/`
  and the investigation template `routing-diagnostics.justfile` left as written.
- Callers in other repos updated, no shims (operator choice): unified-network-controller `site_onboarding/identify_candidates.py`,
  `site_cables.py`, `docs/flows/parts/flows-native-platform-flows.yaml` (+ re-assembled `flows.yaml`); skill-cambium `scripts/README.md`,
  `references/site-addressing.yaml`; ansible-wifi root-governance `AGENTS.md` and the fleet-hardware-audit README; smc-resiliency `SCRATCHPAD.md`;
  enterprise-strategy `asterisk-probe-20261022/run1.sh`. Dated reports keep the old paths.
- `check_governance.py`: the scripts catalogue walks `**/*` (subfolder files were invisible to it); new `check_scripts_layout`. Both proven red, then
  green. Layout table in `scripts/README.md`; rules in `AGENTS.md`; decisions in `ARCHITECTURE.md`; branch-reach pointer in `SKILL.md`.
- Verified: unit tests (ansible, probes), `just test-deadline`, all justfiles parse, every shell script parses, `metrics/` imports, pack root and
  token resolve, `just ansible_change_reach`, `just local_knowledge_index`. Not run: recipes that need Teleport.

## 20261027_1953 — Staleness audit: branch reach, two checker gaps, version rule (v0.8.8 -> v0.8.9)

- First staleness audit of the pack (report under `docs/audits/`). Three material findings, all one cause: `rise` and `rise-multi` diverged
  at `e1077c17` (2025-12-09), so July apt fixes and url_capture v2 are not on `rise`. In-place notes in `references/08`, `09`, `13`.
- `scripts/check_governance.py`: skips the audit's gitignored snapshot when resolving bare names (every audit turned `just check` red);
  new `check_recipe_interpreter` fails a recipe that runs bare `python3`. Four recipes (`smc_change_compare`, `smc_change_runs`,
  `smc_inventory_add`, `teleport_sessions`) now use the venv. Both checks proven red, then green.
- `AGENTS.md` Tier 3: the version is bumped with every CHANGELOG entry, as the checker already required.
- Tracker item 4: `17583da3` is pushed (`origin/internet-label-rename`, `origin/unc-virtual-smc-malik-rcp01`), not merged; the first branch list
  had been cut by `head -3`.
- Open, proposed not decided: `updated_at` format — the version rule says `YYYYMMDD_hhmm`, the manifest has used `YYYY-MM-DD` throughout.

## 20261027_1947 — ansible_change_reach probe; July apt fixes and smc_ltp fix not on rise (v0.8.7 -> v0.8.8)

- New `scripts/ansible_change_reach.py` (`just ansible_change_reach <commit>`, offline test `test_ansible_change_reach.py`, 5 tests): per commit,
  on `rise`/`origin/rise` or not, the branches holding it, and whether a cherry-pick would be clean (`git merge-tree`, no checkout); optional
  inventory group hosts. Read-only; 0.65 s for two commits plus the `smc_ltp` graph.
- Its first run found `0c51cb1` (apt timer mask) and `4889af8` (`apt_info.py` without `cache.update()`) also absent from `rise` (67a44aa3): a
  `rise` run of `smc_system`/`smc_node_exporter` would revert the 2026-07-15 fix. Notes in `references/08_ansible-authoring.md` and
  `references/13_known-issues.md`; tracker items 4 and 12 updated. Cherry-pick of `17583da3` deferred to the branch-merge work (operator, 2026-10-27).

## 20261027_1937 — Open-items tracker reviewed (v0.8.6 -> v0.8.7)

- `docs/trackers/open-items-20261010_1821.md`: reviewed all 13 items against ansible-wifi `rise` 67a44aa3; a dated note on each, none closed.
  Item 4 corrected: the `smc_ltp` inventory change is committed (`17583da3`) but only on feature branches, not `rise`. Items 5 and 10 marked
  drop candidates for the operator. Last reviewed 2026-10-27, next review 2026-11-10. `just check` doc-freshness failure cleared.

## 20261027_1922 — Quoted code excerpt restored after a markdown hook bug (v0.8.5 -> v0.8.6)

- `references/07_hardware-overlay.md`: the quoted `teleport-tags-exporter.py` excerpt had been joined into one line by the markdown hook (a `rewrap.py` bug
  with quoted fences, fixed in scripts_stuff 2026-10-27); restored from git history. The generated `.ai-context/governance-pack.md` still holds the
  flattened copy until `just context-pack` is next run.

## 20261027_1459 — smc_change self-repair, kohana cron_job, lockstep timing; link health probe (v0.8.4 -> v0.8.5)

- `references/19_smc-change-role.md`: stranded-run self-repair (`abandoned_clean`, apply only); kohana cron jobs on every flavor restarted as
  `respawn: cron_job`; rct-tstik is rct only (wh 8080 is python3); batches in lockstep; interim verify record; run-once and the tsh filter live.
- `references/03_communication-flows.md` (banana-well entry, committed 0d9859b without a version bump): afternoon Teleport errors were 30-40%
  loss at the first hop with the WAN idle.
- `scripts/smc_link_health.sh` (new, `just smc_link_health <smc>`, test `test_smc_link_health.py`): an SMC's uplink over Teleport (loss to
  first hop and proxy, Teleport error trend, clock, backlog, autossh restarts, WAN rate); smoke-run on banana-well-smc01.

## 20261027_1207 — Teleport re-join without a tunnel; first rcp PHP apply (v0.8.3 -> v0.8.4)

- `references/03_communication-flows.md` (node join section): a cleared `/var/lib/teleport` re-joins under a new host id that may never open its
  reverse tunnel (banana-well-smc01, 2026-10-27; cause unverified: clock or link); old record lingers until expiry; cluster-side read-only checks;
  on an overlay Pi the clear is RAM-only.
- `references/19_smc-change-role.md`: first rcp prod apply (jigalong-smc01, 10/10, 736 s, created `runs/rcp/`) and its verify (10/10).
- version 0.8.3 -> 0.8.4.

## 20261027_1050 — smc_change: done SMCs skipped before connecting, runs per flavor, retries, TASK_TIMING, journal freeze (v0.8.2 -> v0.8.3)

- `references/19_smc-change-role.md`: new section "Done skip, runs per flavor, retries, timing, journal freeze (2026-10-27)" with code
  excerpts (group_by split, recovery drift rule); per-flavor `runs/<flavor>/` paths throughout; captive portal render documented as part of the
  PHP verification (home and wifi/terms, bad markers, same status, unhealthy baseline refuses).
- `scripts/smc_change_runs_table.py` reads `runs/<flavor>/records` (every flavor from `runs/`, or one); `scripts/smc_change_compare_records.py`
  globs the per-flavor layout and closes its files (ruff SIM115). Unit test and smoke runs on real records pass.
- `RUNBOOK.md` unchanged in routing (reference 19 already routes smc_change); version 0.8.2 -> 0.8.3.

## 20261026_2222 — smc_change: new order passed on two Pis; second drop at chroot dpkg (v0.8.1 -> v0.8.2)

- `references/19_smc-change-role.md`: alpara and amatjatpalk 11/11 on the lower-dir-first order; alkngarrija-smc01 unreachable during the async chroot dpkg (second drop at that step, I/O-starvation hypothesis unverified); run_once patch and the operator's spec-declared design (open).

## 20261026_2146 — smc_change drop-proof installs, lower dir first, runs table (v0.8.0 -> v0.8.1)

- `references/19_smc-change-role.md`: new section "Drop-proof installs, leftover chroot, lower dir first (2026-10-26 evening)": the
  alice-well-smc01 chroot drop, `await_job.yml` (until does not retry unreachable), `own_leftover` resume, lower-dir-first apt_pin with
  `reboot_holders.py` and a planned reboot, the cron pause, check-mode lower assert, round-trip cost (5-24 s per task), the AVR probe
  collision; code excerpts from local-knowledge-ansible `76b0f86`.
- `scripts/smc_change_runs_table.py` (+ test, `just smc_change_runs <change>`): one line per run record with result, phase 6-9 seconds,
  reboot (boot_id), lower-dir holders or failure.

## 20261026_1844 — smc_change: Pi clock wait, remount retry, lower_busy, http timeout/retries, probe survives a dropped session, resume by default (v0.7.9 -> v0.8.0)

- `references/19_smc-change-role.md`: Learned 2026-10-26 (evening) entry: portal home page calls the WiFi API (2.8-10 s), Pi has no RTC (clock
  wait after a fallback reboot; timedatectl unreliable under ntpd), lower-dir remount retried 90 s and `lower_busy` recorded, Teleport session
  drops handled by `wait_for_connection`, resume on by default with drift allowed at phases 9-10; probe.yml excerpt. The earlier entry's
  `-e smc_change_resume=true` line corrected to the new default.
- `references/19_smc-change-role.md`, same day: Learned (19:30) run time on satellite SMCs (per-call cost, ControlPersist, pgrep self-match,
  dpkg-repack copies identical by md5sums so pooled builds are reused by checksum, apt cache copy for the lower dir); records feed recovery
  (pre-stage-5 failures, `already_done` tied to the spec target hash); `pkill -f` with the pattern in `environment:` killed its own session
  (base64 fix); resume after a code change refuses only phases 5-6; rollback material judged per file; the nightly `pkill -9 php` is a
  workaround (operator) with a flock proposal.
- manifest 0.7.9 -> 0.8.0.

## 20261026_1701 — smc_change safe recovery, completion after cleanup and phase timing (v0.7.8 -> v0.7.9)

## 20261026_1617 — smc_change PHP verify: soak from the restart, start_now, named command checks, tstik AVR and 8080 checks; tstik-capture AVR counts (v0.7.7 -> v0.7.8)

- `references/19_smc-change-role.md`: Learned 2026-10-26 entry: soak counted from the restart or reboot, `restart.processes[].start_now` (root's
  cron line run at once; only for programs that cope with a second start, as rct-tstik's `php -S` does), probe commands' `name`/`timeout`/note,
  the PHP spec's portal-terms, tstik 8080 and AVR read checks (`php artisan update:stats`, `Total Read Data[126,...]`, no AVR error; no AVR ever
  logged passes), RCT AVR fact (all but php-rct-smc01, operator), `pgrep -f` self-match in shells, nightly `pkill -9 php`, Run summary gates;
  with the verify.yml excerpt (local-knowledge-ansible `17a5803`, skill-smc `f13c22f`).
- `scripts/tstik-capture.sh`: capture 07 counts AVR reads, empty reads, AVR errors and `local.ERROR` per laravel.log file plus the top error kinds
  (smoke run warehouse-rct01 2026-10-26: 164,169 reads, 0 AVR errors, 308 network errors; ~90 s for the whole capture). Header: the cron
  frequency was written as every minute (arrkapa, 2026-10-07); root's crontab on warehouse-rct01, alice-well, cave-hill and adjamarragu runs
  `update:stats` every 5 minutes, so reset limits count runs. Catalogue row updated.
- manifest 0.7.7 -> 0.7.8.

## 20261026_1534 — smc_change backup.shared: name-identified backup files kept once for all SMCs (v0.7.6 -> v0.7.7)

- `references/19_smc-change-role.md`: Learned 2026-10-26 entry for spec field `backup.shared` (globs; matching backup files kept once per change on the
  controller under `runs/backups/shared/`, `shared.txt` per host, rollback copies them back; default per-SMC copies; name-only match, `paths.tgz`
  refused at spec load; dpkg-repack output differs per run so no checksum compare), with the cleanup.yml excerpt (local-knowledge-ansible `2ade781`);
  PHP spec example gains `shared: ['*.deb']`.
- manifest 0.7.6 -> 0.7.7.

## 20261026_1506 — smc_change flow map in parts, one E2E page per change spec (v0.7.5 -> v0.7.6)

- `references/19_smc-change-role.md`: the smc_change flow map is assembled from `roles/smc_change/drawio/parts/` (role parts) and each change
  folder's flow parts; each change spec gets its own `E2E: <change>` page explaining the change, its steps naming the stage (operator, 2026-10-26).
- `justfile`: `smc_change_flows` assembles `drawio/flows.yaml` from `drawio/parts/master.yaml` before rendering; `smc_change_flows_check` checks both.
- `references/19_smc-change-role.md`: one folder per change, `files/changes/<name>/` with the spec `<name>.yml`, its flow-map parts
  (`flow-components.yaml`, `flow-flows.yaml`) and `runs/` (records, `backups/`, `state/`; was `runs/<name>/`), `smc_change_runs_dir` (operator, 2026-10-26).
