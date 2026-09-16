---
title: Manifest Version Discipline
type: rule
status: accepted
provenance: promoted from AGENTS.md on 20260626
---

# Rule: Manifest Version Discipline

Update `manifest.json` whenever any pack content changes:

- `version` — bump patch (e.g. `0.1.2` → `0.1.3`) for content changes; minor for structural changes
- `updated_at` — set to the current date in ISO 8601 format (`YYYY-MM-DDT00:00:00Z`)

Also update `stable_facts` if a live validation session confirms or contradicts a prior fact, and `known_constraints` if a new constraint is discovered.

Append a corresponding entry to `CHANGELOG.md`.

**No other file may hardcode a duplicate version number** — not `RUNBOOK.md`, not `SKILL.md`, not any `references/*.md` file. `manifest.json` is the sole version-of-record. A second hardcoded copy
inevitably drifts because no other rule updates it on a bump; this happened once already (`RUNBOOK.md`'s header carried a stale `0.1.28` against manifest's `0.1.29`, fixed 2026-09-08) and `SKILL.md`'s
own `## Source` footer carried the same risk until fixed the same day. If a file needs to display the pack's version to a reader, point to `manifest.json` (canonical source) or say "see manifest.json"
— never restate the number.

**Rationale:** `manifest.json` is the machine-readable specialist metadata consumed by install tooling and skill validators. A stale `updated_at` misleads automated freshness checks.
