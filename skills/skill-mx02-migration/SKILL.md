---
name: skill-mx02-migration
description: Project specialist for mx02 migration runbooks, risks, and rollback-oriented execution.
metadata:
  short-description: mx02 migration specialist
---

# Project Specialist: mx02_migration

## Use When
Use this skill when working on this specialist subject and you need stable runbook-driven execution with explicit rollback.

## Rules
- Prioritize read-only diagnostics before risky actions.
- Keep rollback steps explicit and executable.
- Prefer stable facts over volatile observations.

## Stable Facts
- # MX02 Migration Bundle
- Date: 2026-03-06
- Owner: infra-ops
- Scope: Cold/parallel migration from legacy mx02 (RHEL 5.7) to new KVM VM with Storinator-backed mail data.
- ## Structure
- - `strategy/`
- - `runbooks/`
- - `architecture/`
- - `operations/`
- - `evidence/`
- - `inputs/`
- ## Files

## References
- references/PROFILE.md
- references/RUNBOOK.md
- references/KNOWN_ISSUES.md
- references/CHANGELOG.md
- references/CHECKLISTS/healthcheck.md
- references/CHECKLISTS/change.md
- references/CHECKLISTS/rollback.md
- references/CONTEXT/assumptions.md
- references/CONTEXT/dependencies.md
- references/CONTEXT/boundaries.md

## Source
- specialist_type: project
- slug: skill-mx02-migration
- version: 0.1.0

## Action: Generate Domain Status Snapshot on hoth
- Prefer the helper script over one-shot long commands.
- Script path: `/Volumes/Data/_ai/_project/project_stuff/mx02_migration/deploy/mx02-rsync/bin/mx02-status-snapshot.sh`
- Example:
  - `ssh root@hoth '/Volumes/Data/_ai/_project/project_stuff/mx02_migration/deploy/mx02-rsync/bin/mx02-status-snapshot.sh -d activ8.net.au'`
- Expected output:
  - `NEW=/Backups-Pool/Backups-Volume/mx02_backup/status/<domain>/status_<timestamp>.txt`
  - summary fields and storage usage line.
