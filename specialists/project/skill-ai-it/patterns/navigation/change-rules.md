---
Title: Navigation reference: checks, companions, drift and update rules
Category: reference
Status: current
Authority: skill-ai-it
Scope: Full text behind these sections of every project's compact AI_NAVIGATION.md managed block: Governance coherence checks, Companion consistency, Drift handling, Update rules
Last reviewed: 2026-10-10
Summary: Moved verbatim from templates/AI_NAVIGATION.md on 2026-10-10 (Graphify steps are obsolete: Graphify was disabled workspace-wide that day).
---

# Navigation reference: checks, companions, drift and update rules

## Governance coherence checks

If `scripts/check_governance.py` exists, run it before claiming any durable change is complete, and after any change that adds, moves, renames, or retires a file. It turns this project's governance
claims into assertions and exits non-zero on failure.

When it fails, fix the project — not the check. Broadening an ignore-list or exempting the failing file converts a real finding into a permanent blind spot.

The check count is a coverage signal, not a score, and is expected to rise as the project acquires structure. Adding a new class of artifact, a generated output, or a constant restated across files
requires extending the checker's registries in the same pass.

## Companion consistency

When changing governance files, update these companion files together:

| File | Companion files |
|---|---|
| `AGENTS.md` | `AI_NAVIGATION.md`, `context-map.yaml`, `scripts/README.md` |
| `AI_NAVIGATION.md` | `context-map.yaml` |
| `context-map.yaml` | `AI_NAVIGATION.md` |
| `scripts/README.md` | `AGENTS.md`, `context-map.yaml` |
| New script added | `scripts/README.md`, `AGENTS.md`, `justfile`, `scripts/check_governance.py` |
| New artifact class, generated output, or restated constant | `scripts/check_governance.py` registries |

## Drift handling

If files disagree:

1. Stop.
2. Identify the conflicting files.
3. State which source has higher authority.
4. Propose the smallest correction.
5. Do not silently merge conflicting assumptions.

## Update rules

| Change type | Update |
|---|---|
| New durable decision | Add/propose `.archcore/adr/` |
| New agent/project rule | Add/propose `.archcore/rules/` |
| New architecture contract | Add/propose `.archcore/specs/` |
| New operating procedure | Add/propose `.archcore/guides/` |
| New implementation plan | Add/propose `.archcore/plans/` |
| Progress change | Update `memory-bank/progress.md` |
| Current working state changed | Update `memory-bank/activeContext.md` |
| Temporary note | Add to `SCRATCHPAD.md` only if not durable |
| Context routing changed | Update `AI_NAVIGATION.md` and `context-map.yaml` |
| Governance or navigation files changed | Append `CHANGELOG.md` |
