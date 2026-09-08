---
title: Manifest Version Discipline
type: rule
status: proposed
provenance: promoted from AGENTS.md on 20260626
---

# Rule: Manifest Version Discipline

Update `manifest.json` whenever any pack content changes:

- `version` — bump patch (e.g. `0.1.2` → `0.1.3`) for content changes; minor for structural changes
- `updated_at` — set to the current date in ISO 8601 format (`YYYY-MM-DDT00:00:00Z`)

Also update `stable_facts` if a live validation session confirms or contradicts a prior fact, and `known_constraints` if a new constraint is discovered.

Append a corresponding entry to `CHANGELOG.md`.

**Rationale:** `manifest.json` is the machine-readable specialist metadata consumed by install tooling and skill validators. A stale `updated_at` misleads automated freshness checks.
