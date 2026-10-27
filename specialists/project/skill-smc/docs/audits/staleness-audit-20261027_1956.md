---
Title: Staleness audit 2026-10-27
Category: audit-report
Status: current
Authority: evidence
Scope: skill-smc specialist pack, whole project (first staleness audit)
Last reviewed: 2026-10-27
Summary: >-
  First staleness audit of skill-smc. Main finding: the pack documents fixes that live on rise-multi and side branches but not on rise, so a run
  from rise reverts them. Two checker gaps fixed with new negative-tested checks; one rule conflict left for the operator.
---

# Staleness audit — `skill-smc` — `2026-10-27`

**Scope:** whole project (no earlier staleness audit in this pack)
**Standard:** would a careful reader be misled — not "does the suite pass"
**Validation:** 442 checks before → 465 after · `just check` green (governance and doc freshness)

## Contents

- [What could mislead a reader](#what-could-mislead-a-reader)
- [Why these survived](#why-these-survived)
- [Coverage](#coverage)
- [Claims](#claims)
- [New checks, and proof they can fail](#new-checks-and-proof-they-can-fail)
- [Errors made during this audit](#errors-made-during-this-audit)
- [Residual risk](#residual-risk)
- [What a reader should do next](#what-a-reader-should-do-next)
- [Audit evidence](#audit-evidence)
- [Gate result](#gate-result)

## What could mislead a reader

> **The pack says "deployed" about fixes that are not on `rise`.** The 2026-07-15 apt fixes (`0c51cb1` timer mask, `4889af8` `apt_info.py`
> without `cache.update()`) and url_capture v2 (`c19a61fa`, 2026-06-09) are on `rise-multi` and side branches, not on `rise` (67a44aa3).
> **This was realised in the documents, not yet on the boxes** — `git show rise:roles/smc_node_exporter/files/apt_info.py` still calls
> `cache.update()`, `git grep apt-daily rise -- roles` finds no mask task, and `rise` has only the v1 url_capture role. The exposure is
> **latent**: it bites when `smc_system`, `smc_node_exporter` or `smc_url_capture` runs from `rise` against the rcp boxes.

Root cause: `rise` and `rise-multi` diverged at `e1077c17` (2025-12-09); local `rise-multi` has 36 commits `rise` lacks, 25 of them unpushed. The
`smc_ltp` inventory fix `17583da3` is the same pattern (pushed on side branches, not merged). Notes now sit in place in `references/08`, `09` and
`13` (Branch reach), and the tracker. Merging is the operator's pending branch-merge work (operator, 2026-10-27).

## Why these survived

> The suite checks that the pack's documents agree with each other and that paths resolve; nothing compared a claim of "deployed" with the
> branch a run is made from. A check written now (`just ansible_change_reach <commit>`) answers it per commit; it is a probe, not a gate.

## Coverage

```text
Total files in scope:            215
  Examined:                      165
  Exempt (reason stated):        50
  Out of scope (stated):         0
                                 ---
                                 215   ✓ reconciles
```

Binary and tabular files: two firmware `.bin` files under `firmware-files/raspberry-pi/` are covered by their `firmware-manifest.yaml`
(provenance and hashes); the vendor-source PDFs by their folder `readme.md`. No `.xlsx` or `.parquet` in the pack. Systems of record: none —
the pack writes prose to no live system.

## Claims

```text
Checkable claims:                2616
  VERIFIED against source:       1928
  MARKED-HISTORICAL:             145
  RESIDUAL (see register):       543
                                 ----
                                 2616   ✓ reconciles
```

## New checks, and proof they can fail

Each was negative-tested in both directions. **A check that never fires breaks nothing and passes forever.**

| Check | Defect it exists for | Negative-tested |
|---|---|---|
| `check_recipe_interpreter` | Four recipes ran bare `python3` against the `{{py}}` rule | ✓ red on the real pack (4 recipes), green after the fix |
| basename resolution skips `.staleness-audit*` | Every audit turned `just check` red | ✓ red on a duplicate `13_known-issues.md` in `docs/`, green on removal |

## Errors made during this audit

1. Tracker item 4 first listed three branches for `17583da3` from `head -3` output and missed the pushed remotes; corrected.
2. Earlier in the session the manifest `updated_at` was set to a date without reading the rule that says `YYYYMMDD_hhmm`; now an open conflict.
3. Re-running `artifact_signals.py --out` overwrote the filled Phase 4 worksheet; restored from the session transcript.

## Residual risk

Register: the residual list below and `SCRATCHPAD.md` Open items. Summarised: the deploy branch is assumed to be `rise` (UNVERIFIED; `origin/HEAD`
is `master`, last commit 2026-07-24), and 25 `rise-multi` commits exist on one machine only.

- 194 path claims do not resolve: most point into other repos (unified-network-controller `wc-local/`, investigation `docs/`) or are on-box names.
- 297 claims need manual reading and were not read one by one.
- `updated_at` format conflict between the version rule and practice (operator decision).
- A branch in ansible-wifi is named after the 40-hex commit `fb419e6c…`; git warns it is ambiguous (ansible-wifi owner).
- Tracker items 1, 6, 7, 8 and 13 need live hosts or Grafana.

## What a reader should do next

1. Merge, or cherry-pick, `0c51cb1`, `4889af8`, `c19a61fa` and `17583da3` into `rise` (or confirm the deploy branch) before running those roles from `rise`.
2. Push or merge the 25 local-only `rise-multi` commits.
3. Decide the `updated_at` format.

This audit verified every checkable claim, marked it historical, or listed it as residual. It does not show that a box is in any given state:
no box was read.

<!-- BEGIN staleness-audit:evidence sha256=7bf6e60f92d918695ed477c272443ac81cd1ccbb2d56fd678655ab65b9e57d78 -->
## Audit evidence

Generated by `audit_report.py` from `.staleness-audit/` before the gate deleted it. Do not edit by hand; re-run the
script instead.

### Receipts

| Phase | Key | Value |
|---|---|---|
| 0 | `snapshot_path` | .staleness-audit-snapshot-20261027_084751 |
| 0 | `files_snapshotted` | 13 |
| 1 | `files_total` | 215 |
| 1 | `files_examined` | 165 |
| 1 | `files_exempt` | 50 |
| 1 | `files_out_of_scope` | 0 |
| 1 | `defects_found` | 9 |
| 1 | `systems_of_record` | 0 |
| 1 | note | systems_of_record 0: skill-smc writes prose to no live system; it reads Grafana/Teleport/ansible-wifi only |
| 2 | `defects_fixed` | 6 |
| 3 | `banners_added` | 3 |
| 4 | `artifacts_total` | 44 |
| 4 | `artifacts_reasoned` | 44 |
| 4 | `findings` | 2 |
| 5 | `checks_negative_tested` | 2 |
| 5 | `checks_added` | 2 |
| 6 | `residual_items` | 7 |
| 7 | `claims_total` | 2616 |
| 7 | `claims_verified` | 1928 |
| 7 | `claims_historical` | 145 |
| 7 | `claims_residual` | 543 |
| 7 | `claims_residual_manual` | 297 |
| 7 | `claims_residual_broken` | 194 |
| 7 | `claims_residual_conditional` | 33 |
| 7 | `claims_residual_on_box` | 19 |
| 7 | `inverse_orphan_dirs` | 0 |
| 7 | `inverse_unindexed_dirs` | 0 |
| 7 | `inverse_displaced_refs` | 0 |
| 7 | `inverse_empty_indexes` | 0 |
| 7 | `inverse_unlisted_entries` | 0 |
| 8 | `changelog_updated` | 1 |

### Negative tests

- **ambiguous-basename** red — accepted; exit 1; `/Volumes/Data/_ai/_skills/skills-working-cache/skill-smc/.venv/bin/python scripts/check_governance.py`; expect `which is ambiguous`; output sha256 `0c92bf513f55ac27`; 2026-10-27T08:49:53+00:00

  ```text
    ✗ path: scripts/README.md references `13_known-issues.md`, which is ambiguous — 2 files carry that name; qualify it with its folder
  …
  FAIL — 1 issue(s) across 457 checks
  
    ✗ path: scripts/README.md references `13_known-issues.md`, which is ambiguous — 2 files carry that name; qualify it with its folder
  ```

- **ambiguous-basename** green — accepted; exit 0; `/Volumes/Data/_ai/_skills/skills-working-cache/skill-smc/.venv/bin/python scripts/check_governance.py`; expect `which is ambiguous`; output sha256 `6fdc71380391e946`; 2026-10-27T08:49:53+00:00

  ```text
  …
  OK — 456 governance checks passed
  ```

- **recipe-interpreter** red — accepted; exit 1; `/Volumes/Data/_ai/_skills/skills-working-cache/skill-smc/.venv/bin/python scripts/check_governance.py`; expect `runs a bare Python interpreter`; output sha256 `3f073e3cb1ccad3c`; 2026-10-27T08:51:53+00:00

  ```text
    ✗ recipe-interpreter: justfile:101 runs a bare Python interpreter; use {{py}} and depend on _require-venv
    ✗ recipe-interpreter: justfile:106 runs a bare Python interpreter; use {{py}} and depend on _require-venv
    ✗ recipe-interpreter: justfile:122 runs a bare Python interpreter; use {{py}} and depend on _require-venv
    ✗ recipe-interpreter: justfile:161 runs a bare Python interpreter; use {{py}} and depend on _require-venv
  …
  
    ✗ recipe-interpreter: justfile:101 runs a bare Python interpreter; use {{py}} and depend on _require-venv
    ✗ recipe-interpreter: justfile:106 runs a bare Python interpreter; use {{py}} and depend on _require-venv
    ✗ recipe-interpreter: justfile:122 runs a bare Python interpreter; use {{py}} and depend on _require-venv
    ✗ recipe-interpreter: justfile:161 runs a bare Python interpreter; use {{py}} and depend on _require-venv
  ```

- **recipe-interpreter** green — accepted; exit 0; `/Volumes/Data/_ai/_skills/skills-working-cache/skill-smc/.venv/bin/python scripts/check_governance.py`; expect `runs a bare Python interpreter`; output sha256 `5d5e5faa708ea8cf`; 2026-10-27T08:52:09+00:00

  ```text
  …
  OK — 460 governance checks passed
  ```


### `defect-register.md`

### Defect register — skill-smc, 2026-10-27

| # | Materiality | File:line | Defect | Evidence | Status |
|---|---|---|---|---|---|
| 1 | M | references/08_ansible-authoring.md (timer-mask "Applies to"); references/13_known-issues.md (apt_info row) | July apt fixes `0c51cb1` and `4889af8` described as deployed fleet-wide; neither is on `rise`, whose `apt_info.py` still calls `cache.update()` and has no mask task — a `rise` run reverts them | `just ansible_change_reach 0c51cb19 4889af8`; `git grep apt-daily rise -- roles`; `git show rise:roles/smc_node_exporter/files/apt_info.py` | fixed: in-place notes in 08 and 13 |
| 2 | M | references/09_url-capture-pcap.md §10 | url_capture v2 documented as current; `rise` carries only the v1 role (no `v2_setup.yml`) | `git ls-tree -r rise roles/smc_url_capture`; v2 commit `c19a61fa` on rise-multi/side branches | fixed: banner in §10 |
| 3 | M | references/13_known-issues.md | No caveat that `rise` and `rise-multi` diverged (merge-base `e1077c17`, 2025-12-09; 36 vs 20 commits; 203 role files); 25 rise-multi commits unpushed | `git rev-list --count`, `git diff --stat rise origin/rise-multi -- roles` | documented; unpushed commits are residual |
| 4 | M | docs/trackers/open-items-20261010_1821.md item 4 | Said the smc_ltp change was uncommitted; it is committed and pushed on side branches, not on `rise` | `git branch -a --contains 17583da3`; `ansible-inventory --graph smc_ltp` on rise (4 hosts) | fixed (and own first list corrected) |
| 5 | H | scripts/check_governance.py:267 | Basename resolution counted the gitignored audit snapshot, so every staleness audit turned `just check` red | `just check` during this audit | fixed; negtest red/green |
| 6 | H | justfile:100,105,121,160 | Four recipes ran bare `python3` against the skills_stuff `{{py}}` rule; nothing checked it | grep of recipe lines | fixed; new check `check_recipe_interpreter`, negtest red/green |
| 7 | G | AGENTS.md:68 | Tier 3 said bump the version only when a reference changes; `check_version_format` requires `(vA -> vB)` on every newest CHANGELOG entry | `just check` failure on a docs-only entry this session | fixed |
| 8 | G | .archcore/rules/manifest-version-discipline.rule.md:15 vs manifest.json | Rule says `updated_at` is `YYYYMMDD_hhmm` and claims that is practice; every commit since at least 2026-10-22 writes `YYYY-MM-DD`; no check enforces either | `git log -p -- manifest.json` | open: operator decision |
| 9 | G | ansible-wifi refs | A branch named after the 40-hex `fb419e6c…` exists; git warns it is ambiguous; `analyse-routing-drift.py` pins that commit | git warning on `for-each-ref`/`ls-tree` | residual: ansible-wifi owner |


### `phase4-worksheet.md`

### Phase 4 — per-artifact reasoning worksheet

**One line per artifact. Skipping an artifact is fine; skipping the QUESTION is not.**

Ask all three prompts of each:

1. Does it print or compute anything whose **meaning** changed, though its wording did not?
2. Does it assume **continuity, completeness, or availability** that is no longer true?
3. Does it **enumerate a live inventory** (an API list, a database, an inventory file) whose population
   changed since the last audit? Then its reach changed with no line of code changing. `REACH?` rows also
   write, install or connect: name what the population is today and whether every member is meant.

`GENERATOR` rows get a third: **would running it now revert something?** Run it and diff —
a clean diff proves the output is current and proves nothing about the generator's assumptions.

Flags are a PRIORITISATION HINT, not an answer. An unflagged artifact still needs a verdict,
and "clear" needs a reason — an unfalsifiable verdict is not a verdict.

Artifacts: **44**

| Artifact | What it is | Flags | Verdict (fill in) |
|---|---|---|---|
| `scripts/analyse-routing-drift.py` | analyse-routing-drift.py — correlate live SMC routing state against committed topology. | — || CHANGED-CONTEXT: compares boxes with pinned DEPLOYED_COMMIT fb419e6c (2026-07-29 rcp) and rise-multi af2edf56, not rise; still correct for the rcp boxes deployed then (--commit overrides). Meaning unchanged; a branch named after that hash now exists in ansible-wifi (git warns ambiguous) — commit resolves first, so output unaffected. Residual noted. |
| `scripts/analyse-topology-interface-match.py` | analyse-topology-interface-match.py — cross-check topology_vars against a site's real hardware. | continuity? || clear: reads the topology_vars of the checkout it is pointed at; no branch assumption in output; working tree is rise now, so results describe rise. |
| `scripts/ansible-lint-delta-gate.sh` | /usr/bin/env bash | back-solve? || clear: copy of ansible-wifi/scripts/ansible_lint_delta_gate.sh; compares lint against a baseline file, no population or branch assumption. |
| `scripts/ansible_change_reach.py` | Report whether ansible-wifi commits have reached the deploy branch, whether each would cherry-p | back-solve? enumerates-live? || new this session; base branch passed by recipe (rise) — the deploy-branch assumption is UNVERIFIED (origin/HEAD is master) and stated in the catalogue; tests prove reach/conflict logic. |
| `scripts/ata_settings_read.py` | Read the settings of the rct site ATA (Dallas Delta DDC_VoIP-m) through each site's SMC, and co | back-solve? || clear: reads only the named nodes; no back-solve; output meaning unchanged. |
| `scripts/audit-pin-activation.sh` | /usr/bin/env bash | continuity? || clear: reads one box's pin activation logs; continuity assumption is per-box journal retention, unchanged. |
| `scripts/backdoor-watch.sh` | /usr/bin/env bash | back-solve? enumerates-live? REACH? || REACH reasoned: reads ansible-wifi/inventories in the working tree (rise now) only to map a host to its cluster; a host absent from rise's inventory (e.g. one only on a side branch) would fail lookup — fails loudly, not silently. Read-only. |
| `scripts/backdoor_exec.sh` | /usr/bin/env bash | back-solve? || clear: one named target, checks hostname first; no population. |
| `scripts/check_governance.py` | Governance coherence checks for skill-smc. | back-solve? || CHANGED this audit: snapshot dirs excluded from basename resolution (negtest red/green recorded). Other checks unaffected. |
| `scripts/collect-fleet-health.sh` | /usr/bin/env bash | back-solve? continuity? || clear: host list comes from the caller; continuity = boxes reachable at run time, reported per host. |
| `scripts/collect-smc-evidence-full.sh` | /usr/bin/env bash | — || clear: on-box rise-* unit names are the RISE service names (not the git branch); still present on boxes. |
| `scripts/collect-smc-evidence.sh` | /usr/bin/env bash | back-solve? continuity? || clear: single-box evidence; no branch assumption. |
| `scripts/correlate-pin-activation.sh` | /usr/bin/env bash | continuity? || clear: joins two logs from one box; continuity per log retention. |
| `scripts/dns_capture_top.sh` | /usr/bin/env bash | — || clear: one node, one window; no population. |
| `scripts/fleet-reboot-timeline.py` | Per-site reboot and outage timeline from Prometheus, classifying each event. Read-only. | — || clear: reads Graylog for given hosts; meaning unchanged. |
| `scripts/fleet-resource-profile.py` | One CSV row per site: memory, load, PSI, temperature, throttling, overlay usage and RISE watchd | — || clear: rise_* are Prometheus metric names from the RISE watchdog, unrelated to the rise branch; metrics still emitted per 07/02 references. |
| `scripts/graylog-health.sh` | /usr/bin/env bash | back-solve? || clear: Graylog API health; no back-solved figure. |
| `scripts/install_packages.sh` | /usr/bin/env bash | back-solve? enumerates-live? REACH? || REACH reasoned: enumerates `tsh ls` on the given proxy — population is every node the proxy lists today, which grew with onboarding since it was written; it is gated (prints plan, needs explicit run) per its header; operator names the proxy. No change needed; noted as reach-sensitive. |
| `scripts/lint-baseline-refresh.sh` | /usr/bin/env bash | — || clear: copy of the ansible-wifi script; writes only the baseline file it is pointed at. |
| `scripts/local_knowledge_index.sh` | /usr/bin/env bash | back-solve? || clear: lists the local-knowledge folder and repo symlinks; reads the checkout given by --repo. |
| `scripts/overlay-usage-breakdown.sh` | /usr/bin/env bash | — || clear: one box's overlay usage. |
| `scripts/php_package_probe.sh` | /usr/bin/env bash | — || clear: named nodes only. |
| `scripts/pi_identity_probe.sh` | /usr/bin/env bash | back-solve? continuity? || clear: named nodes only; rise-* are on-box unit names. |
| `scripts/predark-snapshot.py` | What a box looked like in the hours before it went dark: memory, swap, overlay, load, PSI, temp | — || clear: rise_* metric names; read-only Prometheus. |
| `scripts/site_device_probe.sh` | /usr/bin/env bash | back-solve? || clear: named node and IPs. |
| `scripts/smc_change_compare_records.py` | Compare two sets of smc_change run records, ignoring what changes run to run, to prove a refact | — || clear: local record files. |
| `scripts/smc_change_runs_table.py` | Tabulate smc_change run records: result, phase times, whether the SMC rebooted, what held the l | — || clear: local record files; records layout runs/<flavor>/records handled (2026-10-27). |
| `scripts/smc_graylog.py` | Read-only Graylog search for SMC logs through the apn-graylog Teleport app (references/03_commu | — || clear: query helper; no population. |
| `scripts/smc_inventory_add.py` | Add one new SMC (one site, one box) to an ansible-wifi inventory: the three groups and the thre | back-solve? GENERATOR enumerates-live? REACH? || REACH reasoned: writes (gated by --apply) into the inventory of whatever branch the ansible-wifi working tree has checked out — today rise. An add made on rise will not appear on rise-multi or side branches and vice versa; this is the same divergence as the branch-reach finding. No code change; the caveat is in 13_known-issues (Branch reach). |
| `scripts/smc_link_health.sh` | /usr/bin/env bash | back-solve? || clear: one host over Teleport; tests offline. |
| `scripts/smc_prom.py` | Read-only Prometheus access for SMC fleet analysis, through the local Grafana datasource proxy. | — || clear: query helper. |
| `scripts/survey_snmp_tooling.sh` | /usr/bin/env bash | enumerates-live? REACH? || REACH reasoned: `tsh ls` population per proxy (grown since written); read-only per box, so the larger reach only lengthens the run. |
| `scripts/teleport-tunnel.sh` | /usr/bin/env bash | back-solve? || clear: one tunnel to a named host. |
| `scripts/teleport_sessions.py` | List who had Teleport sessions on given SMC hosts over a date range, from the cluster's session | back-solve? || clear: named hosts and days. |
| `scripts/test_ansible_change_reach.py` | Offline test for ansible_change_reach.py. Run: python3 -m unittest test_ansible_change_reach -v | GENERATOR || clear: builds its own temp repo; 5 tests pass. |
| `scripts/test_smc_change_runs_table.py` | Offline test for smc_change_runs_table.py. Run: python3 -m unittest test_smc_change_runs_table  | GENERATOR || clear: temp files only. |
| `scripts/test_smc_link_health.py` | Offline checks for smc_link_health.sh: it parses, prints its help, and refuses bad arguments be | — || clear: offline. |
| `scripts/test_with_deadline.sh` | /usr/bin/env bash | — || clear: offline. |
| `scripts/tplink-switch.sh` | /usr/bin/env bash | back-solve? continuity? GENERATOR || clear: one switch through one SMC; templates nothing from ansible-wifi state. |
| `scripts/tplink_cli_driver.py` | Drive a TP-Link JetStream/Omada switch CLI over SSH from an SMC box (runs ON the SMC). | — || clear: runs on the SMC against one switch. |
| `scripts/tstik-capture.sh` | /usr/bin/env bash | enumerates-live? REACH? || REACH reasoned: `tsh ls` lookup to find the node; `rise-logcaps` is an on-box path name. One node per run. |
| `scripts/undervoltage-profile.py` | Raspberry Pi undervoltage events per day or per hour-of-day, from Graylog kern.log. Read-only. | — || clear: Graylog kern.log for named hosts. |
| `scripts/vlan-traffic-timeline.py` | Where did an SMC's outage happen on the wire? Per-interface traffic around an outage. Read-only | — || clear: one SMC's interface counters. |
| `scripts/x86_resiliency_probe.sh` | /usr/bin/env bash | back-solve? continuity? || clear: named nodes, read-only. |


### `residual-risk.md`

### Residual-risk register — skill-smc, 2026-10-27

- **Deploy branch UNVERIFIED.** `origin/HEAD` is `master` (last commit 2026-07-24); `rise` is 67 ahead and active, so treated as live. `ansible_change_reach` defaults to `rise` via the recipe.
- **25 `rise-multi` commits exist only on this machine** (local 36 ahead of rise, origin 11). Loss risk until pushed or merged; operator's branch-merge work.
- **`updated_at` format** (defect 8) undecided.
- **121 path claims resolve nowhere** in this pack, any ansible-wifi branch or local-knowledge: mostly other repos (unified-network-controller `wc-local/`, investigation `docs/`) and on-box names. Not verified; 18 resolve on `rise` (bare names), 12 only on side branches (url_capture v2, yakanarra topology, a vagrant host_vars).
- **297 NEEDS-MANUAL claims** from claim_scan not individually verified this run.
- **Tracker items needing live hosts or Grafana** (items 1, 6, 7, 8, 13) not checked.
- **Own errors this run:** (a) tracker item 4 first listed three branches from `head -3` output, missing the pushed remotes — corrected; (b) earlier this session I set `updated_at` back to a date without reading the rule that says `YYYYMMDD_hhmm` — now defect 8; (c) re-running `artifact_signals.py --out` overwrote the filled Phase 4 worksheet — restored from the transcript.

<!-- END staleness-audit:evidence -->

<!-- BEGIN staleness-audit:gate -->
## Gate result

```text
GATE PASSED 2026-10-27 19:57
coverage      : 167 examined + 52 exempt = 219
structured    : 12 files parsed (duplicate keys checked)
old-value hits: 0 for ['verified-but-uncommitted']
inverse sweep : 0 item(s)
suite         : exit 0 (just check)
Does NOT establish that any claim about the external world is still true; for those the audit verified provenance label and as-at date only.
```
<!-- END staleness-audit:gate -->
