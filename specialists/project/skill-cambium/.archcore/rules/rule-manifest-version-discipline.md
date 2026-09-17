---
title: Manifest Version Discipline
type: rule
status: accepted
provenance: promoted from AGENTS.md (Working rules) on 20260917; accepted by operator 20260917
---

# Rule: Manifest Version Discipline

Update `manifest.json` whenever any content file in this pack changes:

- `version` — bump patch for content changes; minor for structural changes (new reference file, new top-level section)
- `updated_at` — set to the current date in ISO 8601 format (`YYYY-MM-DDT00:00:00Z`)

Also update `stable_facts` when a live validation session confirms or contradicts a prior fact, and `known_constraints` when a new constraint is discovered (e.g. the `hardware_revision: UNKNOWN` entry
currently in `known_constraints` should be replaced with a confirmed value once a real cnMaestro export happens against actual hardware).

Append a corresponding entry to `CHANGELOG.md` in the same pass.

**No other file may hardcode a duplicate version number** — not `RUNBOOK.md`, not `SKILL.md`, not any `references/*.md` file. `manifest.json` is the sole version-of-record. If a file needs to display
the pack's version to a reader, point to `manifest.json` (canonical source) rather than restating the number.

**Rationale:** `manifest.json` is the machine-readable specialist metadata consumed by install tooling and skill validators. A stale `updated_at` or a second hardcoded version number misleads
automated freshness checks and eventually drifts, because no other rule updates a restated copy on a bump — this is the same failure mode `skill-smc` already hit once (`RUNBOOK.md`'s header carrying a
stale version against `manifest.json`'s current one), and this pack hit its own version too: `manifest.json`'s `updated_at` sat on an early-morning bootstrap timestamp for ~19 hours on 2026-09-17
while dozens of real content changes (four device adapters, `references/site-addressing.yaml` expansion, SNMP vault additions) landed in `CHANGELOG.md`, caught only by manual staleness audit.

**Automated enforcement (added 2026-09-17):** `scripts/check_governance.py`'s `check_manifest_freshness` (Tier 3) fails the gate if `manifest.json`'s `updated_at` is older, to the minute, than
`CHANGELOG.md`'s latest `## YYYYMMDD_HHMM` heading. This covers only the freshness half of this rule. Still unenforced, per `CHANGELOG.md`'s `20260917_2130` Residual notes: whether the version was
actually bumped for every content change, and whether any other file has hardcoded a duplicate version number.
