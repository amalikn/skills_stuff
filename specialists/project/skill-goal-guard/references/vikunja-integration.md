---
Title: GoalGuard Vikunja Integration
Category: reference
Status: current
Authority: >-
  consolidated from the v1.7 handoff §17.2, §25, §27, §37 and research pack 00 and 04; Vikunja product facts are as the research pack reports them
  (vikunja.io docs read 2026-10-27), checked against the local 2.7.1 instance where marked (deployed 2026-10-27)
Scope: Local deployment, version and API inventory, entity mapping, read path, write path, webhooks, MCP and the platform exit gate
Last reviewed: 2026-10-27
Summary: >-
  Vikunja is the live task authority and runs locally (2.7.1, deployed 2026-10-27); first read its version and /api/v2/openapi.json, then read tasks and relations for one
  project, map IDs, and only later write through an attributable, policy-checked path. Webhooks are not retried, so poll to reconcile.
---
# Vikunja integration

## Position

Vikunja owns live tasks (operator, 2026-10-27; PORT-001). GoalGuard reads it to rank and gate, and writes to it only through an authenticated, attributable action after a decision (handoff §17.4). No
second task database; no uncontrolled bidirectional sync with Markdown or Excel (handoff §23.1).

## Deployment (operator, 2026-10-27: local)

**Deployed 2026-10-27:** `vikunja/vikunja:2.7.1` (index digest pinned) on OrbStack, SQLite, `http://localhost:3456` bound to 127.0.0.1, registration off, timezone Australia/Sydney; source `/Volumes/Data/_ai/_tool/tools_stuff/vikunja` (`just up`, `just status`, `just dump`), data `/Volumes/Data/_ai/_tool/tools-data/vikunja`. Live `openapi.json` (OpenAPI 3.1.0, 137 paths) and `/api/v1/info` saved under `documents/vikunja-2.7.1-20261027/`; the schema lists `/tasks/{task}/relations` and `/mcp/info`. Backups: `just dump` (zip with config, database and files; it includes the JWT secret).

Original guidance (research pack): The research pack suggests the official image with bundled SQLite and persisted volumes for a single-user pilot, PostgreSQL for heavier concurrency; pin the image version or digest;
back up the database **and** attachments; do not expose it to the internet (pack 04). Before any mapping, record from the running instance: version, `GET /api/v2/openapi.json`, token permission
presets, due-date timezone behaviour (handoff §17.2, pack 04 operational checks).

## Facts to verify on the instance (UNVERIFIED here)

| Claim (research pack 00/04)                                                                | Why it matters                                                              |
| ------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------- |
| API v2 at `/api/v2` from 2.4: PATCH, conditional requests, `items` envelopes, live OpenAPI | Choose v2, honour 409/412 conflicts                                         |
| Official MCP at `/api/v2/mcp` from 2.7 with scoped tokens                                  | Agents may get a **read-only** MCP token; MCP writes are not GoalGuard approval |
| Relations: parent/subtask, blocking/blocked-by, precedes/follows, duplicate                | Dependency eligibility; direction must round-trip (GG-305)                  |
| Saved filters can span projects; projects nest                                             | Portfolio views                                                             |
| Webhooks signed (HMAC-SHA256, `X-Vikunja-Signature`), sent once, no retry                  | Poll reconciliation is mandatory (GG-303)                                   |
| AGPLv3, self-hostable                                                                      | Licence of the platform, not of GoalGuard                                   |

## Mapping

| GoalGuard                                 | Vikunja                                                    | Rule                                                                |
| ----------------------------------------- | ---------------------------------------------------------- | ------------------------------------------------------------------- |
| Project                                   | Project (optionally nested)                                | Stable GoalGuard project ID ↔ Vikunja project ID in `mappings.yaml` |
| Task                                      | Task                                                       | Immutable mapping by ID, never by title                             |
| Dependency                                | blocking / blocked-by, precedes / follows                  | Verify direction; cross-project edges allowed                       |
| Milestone                                 | Labelled milestone task or project convention              | No native immutable milestone assumed; criteria stay in GoalGuard   |
| Committed date, internal target, forecast | **Not** overloaded onto `start_date` / `end_date` / `due_date` | Only operational due dates live in Vikunja (handoff §25)            |
| Priority                                  | Task priority via configured mapping                       | Never rewritten to justify a recommendation                         |
| Scope verdict, evidence                   | Comment or label reference                                 | Decision source stays the GoalGuard log                             |
| Agent activity                            | Not represented                                            | An assignee is not a running agent                                  |

## Stages

1. **Read** (pilot): authorised projects, incomplete tasks, priority, dates, status, relations, source timestamps; exclude blocked tasks; return one ranked queue and one recommendation (§17.2).
2. **Link** (pilot): one management milestone ↔ MVP ↔ Vikunja task(s), many-to-many allowed; idempotent upsert-or-link, never duplicate (D02, GG-301).
3. **Observe** (later): signed webhook inbox with replay protection, plus scheduled poll reconciliation; UI edits become proposals.
4. **Mediated writes** (later, after a written gate): status and notes only, optimistic revision checks; protected fields (MVP, scope, committed date, approval) need an owner decision; conflicts
   quarantine, never last-write-wins. Outbox: persist intent, send, record success; retry with backoff (pack 04).

## Degraded mode

Vikunja unavailable: read-only from the last verified snapshot; the rule is owned by [snapshot-and-restore.md](snapshot-and-restore.md).

## Security

Least-privilege tokens from a secret store (KeePassXC `kp` wrapper on this machine), never in shell history or task text; separate read and write identities; no credentials, customer identifiers or
raw logs in task descriptions; a webhook receiver on localhost may need Vikunja's private-address policy relaxed, never casually (pack 04).

## Platform exit gate

Vikunja stays unless the pilot shows GoalGuard would have to build its own milestone scheduler, custom-field platform or report UI; then compare OpenProject Community on the same fixture. A small
metadata mapping and an Excel exporter do not justify switching (handoff §27). Plane's milestones are a paid feature (pack 00).

## Learned

> **Learned 2026-10-27** · Vikunja 2.7.1 docker (OrbStack, SQLite) · VERIFIED_PRIMARY · Source: `/Volumes/Data/_ai/_tool/tools_stuff/vikunja/justfile` recipe `dump`, test dumps in
> `tools-data/vikunja/dumps` · Falsifier: two `vikunja dump` runs a second apart producing two distinct default-named zips
> `vikunja dump` writes everything under the files folder into the zip, so a dump folder inside `files/` nests every earlier dump; mount a separate dump folder. The default name rendered
> 03:46:18 UTC as `03-03-18` (hour repeated in the minutes slot) and two quick runs left one file; pass `-f` with an explicit timestamp. Each zip contains the container's `.env`, including
> `VIKUNJA_SERVICE_SECRET`: treat dumps as secrets.

```bash
# tools_stuff/vikunja/justfile, recipe dump (2026-10-27, uncommitted)
docker exec vikunja /app/vikunja/vikunja dump -p /dumps -f "vikunja-dump-$(date +%Y%m%d_%H%M%S)"
```

> **Learned 2026-10-27** · Vikunja 2.7.1 API · VERIFIED_PRIMARY · Source: `documents/vikunja-2.7.1-20261027/api-v1-info.json` · Falsifier: a 2.7.x `/api/v1/info` with a top-level
> `registration_enabled` key
> The registration flag is `auth.local.registration_enabled` in `GET /api/v1/info`, not a top-level key; with `VIKUNJA_SERVICE_ENABLEREGISTRATION=false`, `POST /api/v1/register` returns 404.
> The image has no shell (`/bin/sh` missing), so inspect its environment with `docker inspect`, not `docker exec ... sh`.

