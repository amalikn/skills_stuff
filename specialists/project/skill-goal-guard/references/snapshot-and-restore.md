---
Title: GoalGuard Snapshot and Restore
Category: reference
Status: current
Authority: consolidated from the v1.7 handoff §37.3-37.5 and kickoff (portable recovery proof); research pack 04 rollout and M5 hardening
Scope: Portable per-project task snapshots, manifests, offline read-only use and dry-run/clean-instance restore
Last reviewed: 2026-10-27
Summary: >-
  One project snapshot plus a parent manifest, checksummed and atomically replacing only a complete export; offline read-only use with its age shown;
  restore proven by dry run and into a clean test instance; project portability is not full Vikunja disaster recovery.
---
# Snapshot and restore

## Snapshot

- A project snapshot is the single stored copy of that project's exported task entities: portable IDs, provider IDs, title, description, status, priority, dates, relations, milestones, status
  timestamps, mapping provenance (handoff §37.3.1).
- Internal targets, baseline links and forecasts come from GoalGuard's own records as **referenced** supplementary data, never presented as Vikunja fields.
- Cross-project edges live in a portfolio relationship index, not as copies of other projects' tasks (§37.3.2).
- Manifests: project → partition (`apn` / `me`) → root, each with time (UTC), format version, source instance and version, completeness, record counts, checksums and child references. Readers guard
  against cycles, duplicate IDs, broken references, missing files (§37.3.3).
- Write atomically; validate checksums; never replace the last-known-good snapshot with a partial export (S04).
- Never export tokens, credentials, private session state or unneeded personal data; keep `apn` and `me` apart (S07).
- Large or sensitive payloads go to the data peer; the `.gg/` manifest points to them (§37.3.6).

## Offline use

With Vikunja unavailable, show the latest verified snapshot read-only with its age and any partial-data warning; no completion, reprioritisation or scope authorisation from it (§37.4, S05).

## Restore

1. Dry run: validate schema, hashes, IDs, references and the full dependency graph without writing (default no-write).
2. Restore into a **clean test instance** first: map portable IDs to new provider IDs, rebuild relations, verify counts, dates, priorities, dependencies and milestone links. Re-import is idempotent.
3. Restoring into a live instance needs conflict detection, reconciliation and a backup; never last-write-wins.
4. Keep the intermediate format provider-neutral so another FOSS PM tool could be targeted.

An export is not proof of restore; nothing is "delivered" without a verified restore test (§37.4).

## Not captured (state it in the pilot report)

Attachments, user accounts and permissions, comments (unless exported), instance configuration. Full Vikunja disaster recovery is a separate instance-level backup of database and files (pack 04).

## Pilot ceiling

One project snapshot, one parent manifest, one dry-run and one clean-instance restore for one authorised `apn` project (§37.5, kickoff v1.7 addendum).
