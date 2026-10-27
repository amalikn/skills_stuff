---
Title: GoalGuard Vikunja Integration Design
Category: integration-design
Status: proposed, not decided
Authority: research proposal; projection-only model task-ownership sections superseded by the v1.7 handoff (Vikunja owns live tasks; operator, 2026-10-27)
Scope: Vikunja entity mapping, API v2/MCP access, sync stages, deployment and security
Last reviewed: 2026-10-27
Summary: Staged Vikunja integration (export-only, webhook observe, mediated bidirectional) with field mapping and rollout/rollback steps.
---

# Vikunja integration design — research-backed and staged

## Contents

- [Product and version fit](#product-and-version-fit)
- [Two-plane architecture](#two-plane-architecture)
- [Entity mapping](#entity-mapping)
- [Kanban configuration](#kanban-configuration)
- [API connection and permissions](#api-connection-and-permissions)
- [Solo pilot deployment](#solo-pilot-deployment)
- [Rollout and rollback](#rollout-and-rollback)
- [Security and privacy](#security-and-privacy)

---

## Product and version fit

Vikunja is AGPLv3 and self-hostable. Current official docs provide Kanban, List, Table and Gantt views, parent/subtask/blocking relations, cross-project saved filters and official MCP (≥2.7). The
newest API v2 started at 2.4 and is the integration target. Verify the *deployed* instance's `/api/v2/openapi.json` rather than writing from undocumented guesses. Sources: https://vikunja.io/ ,
https://vikunja.io/help/mcp/ , https://vikunja.io/docs/api-v2/ , https://vikunja.io/help/task-relations/ , https://vikunja.io/help/projects/ .

## Two-plane architecture

```
         Human-approved GoalGuard contracts
                       |
             GoalGuard PM / critic
                       |
           Trusted policy + state service
       SQLite journal, tasks, evidence, outbox
           /           |            \
      CLI hooks    Scheduler       Projection adapter
     Codex/Claude  risk review      REST v2 + signed webhook inbox
                                     |
                                 Vikunja UI
                         Kanban, Gantt, saved filters
```

**Crucial:** Vikunja is a *projection* during pilot; don't give agents both direct Vikunja write tools and the canonical GoalGuard writer unless permissions and conflict resolution are explicitly
designed. The official Vikunja MCP can initially be **read-only**. All protected operations go through GoalGuard's policy-mediated path. A UI change can create an *untrusted proposal*, not
automatically rewrite the approved MVP.

## Entity mapping

| GoalGuard field | Vikunja representation | Policy |
|---|---|---|
| Project | Project | One per UNC / SMC / Ad-hoc, optionally subprojects |
| Task | Task | Stable GoalGuard ID in integration mapping (not title alone) |
| Subtask | Parent/subtask relation | Validate direction on round-trip |
| Blocking dependency | Blocking / blocked-by relation | Can cross project; verify mapping |
| Milestone | Labelled milestone task / project convention | Not claim native immutable milestone entity; authoritative criteria remain GoalGuard |
| Due date | Task `due_date` | Only derived from approved deadline, version-controlled |
| Start/end | Task start/end fields | For Gantt where applicable |
| Priority | Task priority mapping | Define scale and avoid accidental inversion |
| Workflow state | Kanban bucket / label | Label alone is insufficient for agent runtime |
| Scope verdict | Comment/label/summary | Decision source is GoalGuard journal |
| Acceptance criteria/evidence | Description/comment + external reference | Avoid leaking sensitive logs/secrets |
| Agent and subagent | GoalGuard separate telemetry | Vikunja assignee is human responsibility, not process activity |

## Kanban configuration

Minimum buckets: `Inbox`, `Ready`, `Doing`, `Blocked`, `Review`, `Done`; **Parked** as a separate label or bucket depending on view capabilities. Keep a single cross-project saved filter for `My
Focus`, and saved filters `Overdue`, `Due Next 7 Days`, `Ready`, `Blocked`, `Approval`, `Parked`. The operator's `Doing` should contain at most one primary attention item; agent-only parallel tasks
can be tagged `agent-running` based on trustworthy telemetry, not assumption.

### Project and portfolio views

- UNC: agreed replacement MVP, milestones, readiness, dependencies, blocked decisions.
- SMC: agreed recovery MVP, verification gates, safety tests, due dates.
- Ad-hoc: quick capture, urgency, deadline and return-to-project trigger.
- Portfolio: current recommended focus, project next item, earliest committed milestone, blockers, conflicts, parked ideas, exception queue.

Vikunja provides views and saved filters, but **a custom portfolio 'single next focus' explanation may require an exported report / task description or a small integration page**. Do not claim it
exists natively.

## API connection and permissions

Vikunja MCP endpoint: `https://<host>/api/v2/mcp`, available 2.7+. Use scoped API token from Settings -> MCP. Official Codex pattern:

```bash
export VIKUNJA_MCP_TOKEN='...from secure store...'
codex mcp add vikunja --url 'https://vikunja.example/api/v2/mcp' --bearer-token-env-var VIKUNJA_MCP_TOKEN
```

Official Claude pattern:

```bash
claude mcp add --transport http --header 'Authorization: Bearer TOKEN' vikunja 'https://vikunja.example/api/v2/mcp'
```

Do **not** paste a persistent token directly into a shared shell history in production. Use a local secret mechanism and least-privilege account. Prefer `read-only` for observations, plus a dedicated
writer identity for the projection adapter. Note native MCP write access is not a substitute for GoalGuard approval checks.

### API v2 specifics

V2: `/api/v2`, GET/POST create, PATCH partial update, conditional requests, `items` pagination envelopes, live OpenAPI at `/api/v2/openapi.json`. Confirm actual conditional headers and supported task
fields in the running instance's schema and HTTP responses. Treat `409` / `412` conflicts according to observed API contract and re-fetch/reconcile rather than guessing. Avoid mixing v1-style HTTP
verbs with v2. Source: https://vikunja.io/docs/api-v2/.

### Sync protocol (incremental)

**Stage A — export-only:** write an idempotent projection from GoalGuard to Vikunja. Maintain mapping `(goalguard_id, vikunja_id, synced_revision, content_hash, synced_at)`. Start with read-only
verification/dry-run before upserts.

**Stage B — observe UI edits:** subscribe to signed Vikunja webhooks. Validate raw-body `X-Vikunja-Signature` HMAC-SHA256, use replay deduplication, store raw event (with retention policy), and
convert to *proposals* for GoalGuard. Schedule full/incremental poll reconciliation because official Vikunja docs say failed deliveries are **not retried**.

**Stage C — mediated bidirectional:** for approved mutable fields (e.g., notes or task status), apply optimistic revision checks and policy validation. For protected fields (MVP, goal, scope,
committed deadline, approval), require explicit human decision. Conflict -> quarantine and review, not last-write-wins.

**Outbox:** persist projection intent first, then send remote write, then record success. Retry with exponential backoff and rate limits. Idempotent stable IDs prevent duplication after retries.

## Solo pilot deployment

For local trial: use OrbStack with official Vikunja Docker image and bundled SQLite and persisted host volumes; official docs provide `docker run -p 3456:3456 -v ...:/app/vikunja/files -v ...:/db
vikunja/vikunja` and require public URL/CORS alignment. For robust concurrent server usage and longer-lived multi-client service, prefer PostgreSQL using the documented Compose example. Pin tested
image version/digest and back up both DB and attachments. Don't expose to public internet during pilot. Sources: https://vikunja.io/docs/installing/ and https://vikunja.io/docs/full-docker-example/.

Operational checks: `GET /api/v2/openapi.json`, UI login, token read perms, task create/update in disposable fixture, relation round-trip, due date timezone, signed webhook to reachable endpoint,
reconciliation after purposely failed webhook. An internal webhook receiver on localhost may need explicit Vikunja outgoing private-address policy adjustments; never weaken SSRF protections casually
(https://vikunja.io/docs/webhooks/).

## Rollout and rollback

1. Snapshot baseline GoalGuard state; deploy disposable Vikunja with test data.
2. Confirm version, feature access, OpenAPI and token scopes.
3. Export sample 3 projects and task edges, verify visually and via API.
4. Simulate duplicate sync, deleted task, conflicting update and lost webhook.
5. Enable pilot read-only on real data, review for one week.
6. After written gate approval, enable mediated task-state edits only (not protected contract fields).
7. Rollback by disabling write tokens and adapter, preserving journal; restore projection DB or rebuild it from GoalGuard source; never silently delete real user edits.

## Security and privacy

Minimize potentially sensitive community/device data. No passwords, customer identifiers or credentials in task descriptions. Local default bind and authenticated HTTPS for remote access. Separate
token privileges and expiry. Check webhook HMAC and protect against replay; make dedupe persistent. Reject direct API edits of approved goal without human review; never use UI task status as final
proof of physical infrastructure validation.
