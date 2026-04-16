# RUNBOOK

## Diagnostics (read-only first)
1. - `runbooks/05_CUTOVER_CHECKLIST.md`
1. ## Status
1. - Health checks and progress checks run from `hoth` against `/Backups-Pool/Backups-Volume/mx02_backup`.
1. - Mailbox parity checks pass after final sync.
1. - Cutover checklist: `runbooks/05_CUTOVER_CHECKLIST.md`
1. ## Status Note
1. - Added cutover checklist controls for auth parity and existing-password login validation in `runbooks/05_CUTOVER_CHECKLIST.md`.
1. - Mailbox export progress and health checks are being monitored from `hoth` against `/Backups-Pool/Backups-Volume/mx02_backup`.
1. # Capture row counts for later parity checks
1. ## Post-import parity and password continuity checks
1. echo "hash quality checks:"
1. # Cutover Checklist

## Rollback
1. - Execute controlled cutover with rollback readiness.
1. - [ ] Validate backup/restore test
1. ## Rollback
1. - [ ] Revert MX/NAT/relay if severe issue
1. - [ ] Maintain rollback window 3-7 days minimum
1. - Keep rollback mapping document updated with exact MX/NAT/relay reversal steps.

## Generate `status_*` Files (hoth)
When asked to generate new domain status files under `/Backups-Pool/Backups-Volume/mx02_backup/status/<domain>/`, run:

```bash
/Volumes/Data/_ai/_project/project_stuff/mx02_migration/deploy/mx02-rsync/bin/mx02-status-snapshot.sh -d <domain>
```

This writes:
- `status_<timestamp>.txt`
- `status_latest.txt` (refreshed)
