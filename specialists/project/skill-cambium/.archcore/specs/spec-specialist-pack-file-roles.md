---
title: Specialist Pack File Roles
type: spec
status: accepted
provenance: promoted from AGENTS.md (Working rules) on 20260917; reclassified from a rule candidate to a spec on promotion, mirroring skill-smc's identical spec; accepted by operator 20260917
---

# Spec: Specialist Pack File Roles

Defines the role and content-source status of every governance file in the skill-cambium specialist pack.

## File role table

| File                     | Role                                               | Notes                                                                             |
| ------------------------ | -------------------------------------------------- | --------------------------------------------------------------------------------- |
| `SKILL.md`               | Agent-facing activation surface                    | Defines triggers, the Standing Write-Back Contract, and pointers to `references/` |
| `RUNBOOK.md`             | Navigation index only                              | Maps task types to numbered reference files; not a content source                 |
| `references/01_` – `05_` | Numbered content source files                      | Load only the one needed for the task                                             |
| `manifest.json`          | Machine-readable specialist metadata               | Sole version-of-record — see `rule-manifest-version-discipline.md`                |
| `AGENTS.md`              | Agent policy for pack maintenance                  | Governs contributors, not end-users                                               |
| `CLAUDE.md`              | Claude Code governance wrapper                     | Pack maintenance only                                                             |
| `AI_NAVIGATION.md`       | Human-readable context router                      | Pack maintenance only                                                             |
| `context-map.yaml`       | Machine-readable routing map                       | Pack maintenance only                                                             |
| `CHANGELOG.md`           | Pack version history                               | History and corroboration only — never a promotion source                         |
| `README.md`              | Pack orientation and folder index                  | Human entry point                                                                 |
| `SCRATCHPAD.md`          | Agent working memory for pack maintenance sessions | Durable only where marked `KEEP`                                                  |
| `.archcore/`             | Durable rules, ADR, spec for this pack             | Canonical source once accepted                                                    |

## Authority

`manifest.json` is the highest-authority metadata source. `SKILL.md` is the highest-authority agent-facing surface. `references/*.md` are content truth for their domain. No other file overrides these.

## Notes

This pack is smaller than its sibling `skill-smc` (5 reference files versus skill-smc's 13, no `exports/` client-adapter layer yet, no dedicated-agent `PROFILE.md`/`SYSTEM_PROMPT.md`), so this spec
omits rows for files that do not exist here. Add a row when a corresponding file is introduced.
