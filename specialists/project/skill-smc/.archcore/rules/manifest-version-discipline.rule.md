---
title: Manifest Version Discipline
type: rule
status: accepted
provenance: promoted from AGENTS.md on 20260626
---

# Rule: Manifest Version Discipline

Update `manifest.json` whenever any pack content changes:

- `version` — `major.minor.patch`, where **patch runs 0 to 9 only** (operator, 2026-10-07). Each change bumps patch; after `x.y.9` the next version is `x.(y+1).0`,
  never `x.y.10`. A structural change may also move straight to the next minor. The pack was renumbered from `0.1.100` to `0.2.0` on 2026-10-07 under this rule;
  versions before that (up to `0.1.100`) stay as recorded in `CHANGELOG.md`.
- `updated_at` — the time of the change as `YYYYMMDD_hhmm`, read from `date`, never estimated. (Until 2026-10-07 this rule said ISO 8601; the pack has used
  `YYYYMMDD_hhmm` in practice, so the rule now says what the pack does.)

Also update `stable_facts` if a live validation session confirms or contradicts a prior fact, and `known_constraints` if a new constraint is discovered.

Append a corresponding entry to `CHANGELOG.md`.

**No other file may hardcode a duplicate version number** — not `RUNBOOK.md`, not `SKILL.md`, not any `references/*.md` file. `manifest.json` is the sole version-of-record. A second hardcoded copy
inevitably drifts because no other rule updates it on a bump; this happened once already (`RUNBOOK.md`'s header carried a stale `0.1.28` against manifest's `0.1.29`, fixed 2026-09-08) and `SKILL.md`'s
own `## Source` footer carried the same risk until fixed the same day. If a file needs to display the pack's version to a reader, point to `manifest.json` (canonical source) or say "see manifest.json"
— never restate the number.

**Enforced by** `scripts/check_governance.py`: `check_version_single_source` (no duplicate stamps) and `check_version_format` (patch is a single digit, and the newest
`CHANGELOG.md` heading's `-> vX.Y.Z` matches `manifest.json`).

**Rationale:** `manifest.json` is the machine-readable specialist metadata consumed by install tooling and skill validators. A stale `updated_at` misleads automated freshness checks.
