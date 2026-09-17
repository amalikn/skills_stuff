# SCRATCHPAD

Agent working memory for skill-cambium. Use for: draft plans, terminal output, intermediate analysis. Cleared between sessions unless content is explicitly marked KEEP.

---

<!-- KEEP: populated 2026-09-17 at pack bootstrap; no prior memory-keeper/project-context/claude-mem history for this new pack -->

> **Superseded 2026-09-17, later the same day (staleness audit).** The "Current state"/"Open items"/"Next actions" below were written at first-adapter time (XV2 only) and went stale within the same
> session as three more adapters landed. What still stands: the bootstrap narrative, the resolved-item history, and every item not specifically annotated below. What changed: all four Cambium families
> now have real, live-verified adapter code — see `references/06_device-api-cli-reference.md` and `CHANGELOG.md`'s `20260917_2050`/`20260917_2057` entries for the R195P and cnWave adapters, and the
> full live-test trail. Superseded bullets are marked `[x]` with a dated note rather than rewritten, per this file's own KEEP convention.

## Contents

- [Current state](#current-state)
- [Open items](#open-items)
- [Key anchors](#key-anchors)
- [Recent decisions](#recent-decisions)
- [Session history (summaries — full detail in memory-keeper)](#session-history-summaries--full-detail-in-memory-keeper)
- [Next actions](#next-actions)
- [Memory pointers (navigation only — content is above)](#memory-pointers-navigation-only--content-is-above)

---

## Current state

**Phase:** All four Cambium device families (Enterprise Wi-Fi XV2/E-series, ePMP AP/SM, cnWave 60GHz, cnPilot R195P) now have real, live-verified adapter code and `VERIFIED-OBSERVED` data — see
`references/06_device-api-cli-reference.md`. Pack scaffolded 2026-09-17 from `cambium-swap`'s device-credentialing/device-inventory session; same day, later sessions added: `scripts/cambium-portal.sh`
(moved from `cambium-swap`, support-portal login + version-matched release fetch), the confirmed live Hope Vale access chain (SSH CLI + authenticated REST API, written into
`references/02_device-access-and-vault.md`), `scripts/cambium_xv2_adapter.py` (first real adapter code), then `scripts/cambium_epmp_adapter.py`, `scripts/cambium_cnwave_adapter.py`, and
`scripts/cambium_r195p_adapter.py` — all run live against real hardware and verified correct. `references/05_known-issues.md`'s blanket staleness disclaimer and site-coverage row were updated in the
same pass as this note (2026-09-17, staleness audit).

---

## Open items

- [x] Authenticated device session — resolved 2026-09-17: real SSH CLI login (`show version`) and real REST API session (`login`/`get_facts`/`get_interfaces`/`logout`) both confirmed against Hope Vale
  Tower 1 (Enterprise Wi-Fi XV2-2T0). Credential (`<secret:keepassxc:cambium-devices/enterprise-wifi>`) confirmed correct against real hardware.
- [ ] `hardware_revision` still UNKNOWN for all 17 models except what's now observed for XV2-2T0 (model/serial/firmware confirmed via `get_facts()` — hardware_revision itself not yet in scope of the
  adapter's returned fields).
- [x] `scripts/cambium_xv2_adapter.py`'s remaining getters — resolved 2026-09-17: `get_radios`/`get_wlans`/`get_clients`/`get_config`/`get_events` all implemented and run live against Hope Vale Tower
  1, matching every row in [cambium-vendor-adapter-data-points.md](/Volumes/Data/_ai/_project/project_stuff/apn/cambium-swap/docs/migration/controller-option3/cambium-vendor-adapter-data-points.md).
- [ ] **Rotate SNMP community strings, 2026-09-17 — operator decision still pending as far as this file records.** See `references/05_known-issues.md` Security Incidents: this device's real
  `snmp_read_community`/`snmp_write_community` briefly printed to a transcript during exploration. Both strings should be treated as compromised. **Note (2026-09-17 staleness audit):** the operator
  has since added four real SNMP community credentials to the vault (`apn-snmp-ro`/`rw`, `nbn-snmp-ro`/`rw` — CHANGELOG `20260917_2057`) and these are now live-verified fleet-wide; whether that
  constitutes the rotation this item asks for, versus a separate standard-credential addition, was not confirmed by this audit — operator should close or restate this item explicitly rather than leave
  it ambiguous.
- [x] Only this one family (Enterprise Wi-Fi XV2) has an adapter or live-observed data — **superseded 2026-09-17, same day, staleness audit.** All four families now have adapters and live-observed
  data: ePMP AP/SM (`scripts/cambium_epmp_adapter.py`), cnWave 60GHz (`scripts/cambium_cnwave_adapter.py`), cnPilot R195P (`scripts/cambium_r195p_adapter.py`) — see CHANGELOG `20260917_1946` through
  `20260917_2057` and `references/06_device-api-cli-reference.md`.
- [x] Only 2 sites' asset registers seen (Hope Vale, Burringurrah) — **narrowed 2026-09-17, staleness audit.** `references/site-addressing.yaml` now covers all 10 rcp-flavour sites. What still stands:
  the naming-convention *prose* in `references/03_asset-register-conventions.md` was written from only 2 sites and has not been individually re-verified against the other 8 — treat as
  likely-generalizes, not confirmed-generalizes.
- [ ] `scripts/check_governance.py` created at bootstrap with Tier 1 (universal) checks only — extend as the pack grows real scripts/tasks.

---

## Key anchors

| Item             | Detail                                                                                    |
| ---------------- | ----------------------------------------------------------------------------------------- |
| Live device data | `/Volumes/Data/_ai/_project/project_stuff/apn/cambium-swap/inventory/`                    |
| KeePassXC vault  | `~/Library/CloudStorage/OneDrive-Personal/A/APN_keepassDB.kdbx`, `cambium-devices/` group |
| Related pack     | `/Volumes/Data/_ai/_skills/skills_stuff/specialists/project/skill-smc`                    |

---

## Recent decisions

- 2026-09-17 — Operator rejected building a formal CLI/API grammar + capability-model skill (`device-interface-modeler`) ahead of any real adapter code, despite a real multi-vendor plan. Resolved via
  `skill-walk-before-run` (RED, then RESOLVED by the `scripts/cambium_xv2_adapter.py` test — `PASS`, schema not needed). Standing rule going forward: build the next vendor's adapter the same way (own
  specialist skill pack, plain code against the real device) — revisit formal schema only once a second real vendor adapter exists to design against.
- 2026-09-17 — All Cambium development work (scripts, adapter code) goes into this pack, not into `cambium-swap` — explicit operator instruction, reinforcing the Standing Write-Back Contract.
- 2026-09-17 — Created as a separate pack from `skill-smc` rather than folding into it. Rationale: different domain (hardware/credentials/asset-registers vs box/Ansible), already had real
  cross-project-reusable volume, mirrors the precedent that created `skill-smc` in the first place.
- 2026-09-17 — Vault-related reference file is `references/02_device-access-and-vault.md`, not a name containing "credentials" — the workspace's OPA write-gate hard-blocks any file **path** containing
  `credential`/`secret`/`password`, regardless of content.

---

## Session history (summaries — full detail in memory-keeper)

### 2026-09-17 (~21:21-22:15) — first whole-pack staleness audit, coherence sweep, first-ever commit

- Ran skill-staleness-audit in full detail mode: gate PASSED, checks 133→145. Found and fixed 13 defects, the two most material being a KEEP-block in this file that still claimed only the XV2 family
  had an adapter (superseded above — all four landed the same day) and a self-contradiction inside `AI_NAVIGATION.md` itself (line 89 said `.archcore/` was empty while lines 35/63 of the same file
  said 6 documents accepted). Also fixed a stale `RUNBOOK.md` header banner, a blanket "everything USER_STATED" staleness-risk note in `references/05_known-issues.md` that no longer matched the
  VERIFIED-OBSERVED state of all four families, a frozen `manifest.json` version/timestamp, a superseded R195P `stable_fact`, and two "5 reference files" miscounts (file `06` already existed). Added
  `check_manifest_freshness` and populated the previously-empty `COUNT_CLAIMS` registry in `scripts/check_governance.py`, both negative-tested.
- Coherence sweep then propagated those fixes further: checks 145→150. `AI_NAVIGATION.md` and `context-map.yaml` were both missing routing rows/entries for reference files 05 and 06;
  `.archcore/README.md` and its manifest-version-discipline rule still claimed no automated check existed for manifest freshness, immediately after the audit added one. Verified `skill-smc` only ever
  references this pack by topic, never by version or file count, so nothing there needed reconciling.
- **Committed this pack to git for the first time.** It had accumulated a full day of real work (four live-verified adapters, `site-addressing.yaml` expanded to all 10 sites, SNMP vault entries,
  `.archcore/` rules and ADRs) with zero version-control history until now. `skills_stuff` repo (this pack is a subpath, remote `amalikn/skills_stuff`), commit `1d25892`, 39 files, pushed to `main`.

### 2026-09-17 ~11:35a-12:15p — live device access, first adapter code, formal-schema question resolved

- Moved the former cambium-support-login.sh here from `cambium-swap` as `scripts/cambium-portal.sh`, added a `fetch-release` subcommand; used it to fetch the exact firmware-version-matched CLI
  Reference Guide (Release 6.6.0.3, matching the live-confirmed device firmware) after finding the previously-archived guide was a newer, mismatched Release 7.2.
- Documented the confirmed live Hope Vale access chain in `references/02_device-access-and-vault.md`: `tsh` tunnel form (`--proxy` required), REST API auth (`POST /api/login`, cookie+XSRF-header
  session), SSH-vs-web-UI comparison.
- Operator pushed on a proposal to build a formal CLI/API grammar skill before writing any adapter, given multi-vendor plans. Ran `skill-walk-before-run` (RED), then wrote and ran
  `scripts/cambium_xv2_adapter.py` (`get_facts`/`get_interfaces`, stdlib-only) live against Hope Vale Tower 1 — resolved RED to PASS: no formal schema needed. Found and fixed one real bug along the
  way (`port_stats.link` unreliable; `port_status` array is authoritative for link state).

### 2026-09-17 — pack bootstrap

- Scaffolded via `skill-ai-it` (bootstrap mode): governance files, `.archcore/` init, 5 reference files, cross-links to `skill-smc` in both directions.
- Content ported: the asset-register naming-convention learning originally written into skill-smc's numbered reference file on the same topic moved here as its canonical home; that file trimmed to a
  stub pointing here.

---

## Next actions

- [x] Extend `scripts/cambium_xv2_adapter.py` with `get_radios`/`get_wlans`/`get_clients`/`get_config` — **done 2026-09-17**, see Open items above.
- [x] Other 4 Cambium families (cnPilot R195P, ePMP AP, ePMP SM, cnWave 60GHz) have no adapter or live-observed data yet — **superseded 2026-09-17, staleness audit.** All four now do; ePMP shares the
  XV2/E-series adapter, cnWave and R195P each have their own. See `references/06_device-api-cli-reference.md`.
- [x] `references/05_known-issues.md` still says no `VERIFIED-OBSERVED` data exists — stale for Enterprise Wi-Fi XV2 now, fix next time that file is touched. — **fixed 2026-09-17, staleness audit**
  (the file's "Pack Staleness Risks" blanket disclaimer and its site-coverage row were both updated).
- Done: register this pack in `/Volumes/Data/_ai/_skills/skills_stuff/README.md`'s Specialist Packs table and symlink `~/.claude/skills/skill-cambium` → canonical path (completed at bootstrap).
- **New, from the 2026-09-17 staleness audit:** `hardware_revision` (all 17 models) and the SNMP-rotation decision remain genuinely open — see Open items above. Also open: this entire pack directory
  is untracked in the parent `skills_stuff` git repo (`git status --porcelain` shows it as a single `??` — never `git add`ed) — everything built this session (four adapters, expanded
  `references/site-addressing.yaml`, SNMP vault entries, `.archcore/` rules) has no version-control history and would be lost with the working tree. Not fixed by this audit per its git-write
  constraint; flagged for the operator to commit.
- **`skill-project-coherence` run 2026-09-17 ~21:45, propagating the staleness audit above.** Found and fixed two companion-file gaps the audit itself didn't reach: `AI_NAVIGATION.md` still said "5
  files" in a managed-block comment and was missing a routing-table row for `references/06_device-api-cli-reference.md`; `context-map.yaml`'s `routing`/`update_rules` sections had no entries for files
  05/06 at all. Also found `.archcore/README.md` and its manifest-version-discipline rule still claimed "no automated check yet" after the audit added `check_manifest_freshness` — corrected. See
  CHANGELOG `20260917_2145`. The untracked-directory item above is still open — this pass did not touch git state, per its own constraint.

---

## Memory pointers (navigation only — content is above)

- memory-keeper: no results (new pack, not yet queried under a dedicated channel)
- project-context: no results
- claude-mem: not queried — this pack has no prior session history
