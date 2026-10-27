---
Title: Archive safety
Category: reference
Status: current
Authority: local-supplement; operator decision 2026-10-27 (plan only in v1); design doc section 8 Phase F, INV-001, INV-010, INV-012
Scope: When a source may be archived, what kc archive-plan checks and rehearses, and what a future archive run must add before it may move anything
Last reviewed: 2026-10-27
Summary: >-
  v1 never moves, copies into the project or deletes a source. archive-plan lists sources fully absorbed by promoted pages, reports anything still
  linking to them, and rehearses copy and restore with hash checks in a temporary folder.
---

# Archive safety

## Contents

- [What v1 does](#what-v1-does)
- [Candidate rules](#candidate-rules)
- [Restore rehearsal](#restore-rehearsal)
- [Before a real archive run (deferred)](#before-a-real-archive-run-deferred)

## What v1 does

`kc archive-plan --project P` builds a plan; `--apply` saves it as `.kc/archive-plans/<batch>.json`. The batch ID is a hash of the candidates' bytes, so the same set gives the same batch. Each entry
names the source, its SHA-256 and size, and its target `archive/originals/<batch>/<original path>`. Nothing in the project changes except that file.

## Candidate rules

A live source is a candidate only when all hold:

1. At least one claim cites it.
2. Every claim citing it is either on a promoted page or is history (`HISTORICAL`, `SUPERSEDED`, `DUPLICATE`, `REJECTED`).
3. No claim citing it is `REVIEW_REQUIRED` (so no open P0/P1 conflict touches it).
4. Every section of it is accounted for (no `pending`).
5. Its bytes still match the inventory hash.

Each blocked source is listed with its reasons. `referrers` lists Markdown files outside the batch that link to a candidate; those links must be redirected before any move, so a plan with referrers is
`ready: false`.

## Restore rehearsal

The plan copies every candidate into a temporary folder under the archive layout, verifies each hash, copies it back to a second temporary folder at its original path and verifies again. The temporary
folder is deleted. A failed check makes the plan not ready (exit 6 is reserved for a future apply).

## Before a real archive run (deferred)

The design's Phase F stays deferred until the pilot passes and the operator asks. A future `archive --apply` must at least: take an independent backup outside any cache folder; re-verify the plan's
hashes and refuse on change (exit 5); require a separate approval bound to the plan file's digest; move with `git mv` after resolving both paths; leave a redirect or updated links; commit sources,
ledger and pages together; verify the post-commit state; and keep the backup (Git is not a backup). An interruption must leave a known state and a deterministic restore (INV-010, INV-012).
