**Title:** REST API

**Source:** [https://www.getpad.dev/docs/api](https://www.getpad.dev/docs/api)

---

# Page Structure Map
```text
REST API
├── Authentication
│   ├── Bootstrap First Admin
│   ├── Session State
│   ├── Login
│   ├── Register
│   ├── Logout
│   ├── Current User
│   ├── Forgot Password
│   ├── Reset Password
│   └── API Tokens
├── Workspaces
│   ├── List Workspaces
│   ├── Get Workspace
│   ├── Workspace Members
│   ├── Accept an Invitation
│   └── Agent Roles
├── Collections
│   ├── List Collections
│   └── Create Collection
├── Items
│   ├── List Items
│   ├── Create Item
│   ├── Get Item
│   ├── Update Item
│   ├── Delete Item
│   ├── Item Children
│   ├── Item Progress
│   └── Item Links
├── Search
│   └── Full-Text Search
├── Real-Time Events
│   └── SSE Stream
├── Dashboard
│   └── Get Dashboard
├── Activity
│   └── List Activity
├── Webhooks
│   ├── List Webhooks
│   ├── Create Webhook
│   │   └── Delivery and retries
│   ├── Delete Webhook
│   └── Test Webhook
└── Admin
    ├── Platform Settings
    ├── Test Email
    ├── User Administration
    ├── Invitations Administration
    ├── Plan Limits
    └── Stats
```

---

Pad exposes a REST API at `http://localhost:7777/api/v1/`. All responses are JSON.

## Authentication

Fresh Pad instances must be initialized with `pad auth setup` on the server host before normal login and registration flows are available. The bootstrap path is only intended for host-local setup.

### Bootstrap First Admin

```
POST /api/v1/auth/bootstrap
Content-Type: application/json

{
  "email": "admin@example.com",
  "name": "Admin User",
  "password": "your-password"
}
```

Creates the first admin account for a fresh instance. This endpoint is only available from localhost on the machine or container running the Pad server.

### Session State

```
GET /api/v1/auth/session
```

Returns explicit setup/auth state for the current client, including whether the instance still requires setup.

### Login

```
POST /api/v1/auth/login
```

Normal email/password login for initialized Pad instances.

### Register

```
POST /api/v1/auth/register
```

Creates a user account after setup. Registration is intended for admin-created accounts or invitation flows; it is not used to bootstrap the first admin user.

### Logout

```
POST /api/v1/auth/logout
```

Destroys the current session.

### Current User

```
GET /api/v1/auth/me
```

Returns the authenticated user’s profile (`id`, `email`, `name`, `username`, `created_at`, etc.).

```
PATCH /api/v1/auth/me
Content-Type: application/json

{ "name": "New Name", "password": "NewPassword123!" }
```

Updates the authenticated user’s name and/or password. Accepts only `name` and `password` — admin-only fields use `/admin/users/{id}` instead.

### Forgot Password

```
POST /api/v1/auth/forgot-password
Content-Type: application/json

{ "email": "user@example.com" }
```

Triggers a password-reset email when Maileroo is configured. Always returns 200 regardless of whether the email exists (avoid account enumeration).

### Reset Password

```
POST /api/v1/auth/reset-password
Content-Type: application/json

{ "token": "<reset-token>", "password": "NewPassword123!" }
```

Resets the password using a token from the forgot-password email. Tokens are single-use and short-lived.

### API Tokens

User-scoped tokens for CLI tools, AI agents, and CI. Bearer-style — pass as `Authorization: Bearer <token>`.

```
GET /api/v1/auth/tokens                 # List the caller's tokens
POST /api/v1/auth/tokens                # Create a new token
DELETE /api/v1/auth/tokens/{tokenID}    # Revoke a token
```

**Create body:**

```
{
  "name": "ci-bot",
  "scopes": "[\"read\"]",
  "expires_in": 90
}
```

`expires_in` is the lifetime in days; omit it for the server default. The response body includes the raw token **once** — store it immediately; subsequent reads return only the prefix.

**Access levels.** A key is either **Read and write** or **Read only**. Choose one in the web console (**Settings → API Tokens → Access**), with `pad token create --scopes read`, or with `scopes` on create:

| Level | `scopes` | Allows |
| --- | --- | --- |
| Read and write | omit it (the default), or `"[\"*\"]"` | everything your role in the workspace allows |
| Read only | `"[\"read\"]"` | `GET`, `HEAD` and `OPTIONS`, plus running a playbook (`POST /api/v1/workspaces/{ws}/playbooks/{ref}/run`) |

A read-only key’s other writes are refused: `403` over REST, and `permission_denied` over remote MCP. A key never exceeds your role in a workspace; its level is only a ceiling on that role.

`scopes` is a **string** holding a JSON array of `*`, `read`, `write`, `pad:read`, `pad:write` or `pad:admin`. `write` and `pad:write` mean the same as `*`, `pad:read` the same as `read`, and `pad:admin` grants nothing beyond `write` for an API key. The server refuses these with `400 validation_error`, and the message lists the allowed values:

- a bare array (`"scopes": ["read"]`), JSON `null`, or any other non-string;
- `""` or `"[]"` (omit `scopes` for full access instead);
- a string that is not a JSON array of strings;
- any value outside the list above.

The token list in the console shows each key’s access. Keys made before access levels existed read as *older key, unrestricted*.

## Workspaces

### List Workspaces

```
GET /api/v1/workspaces
```

### Get Workspace

```
GET /api/v1/workspaces/{workspace}
```

### Workspace Members

```
GET /api/v1/workspaces/{workspace}/members
```

Returns workspace members and pending invitations. Each member entry includes `user_id`, `email`, `name`, `role` (`owner` / `editor` / `viewer`), and timestamps.

```
POST /api/v1/workspaces/{workspace}/members/invite
Content-Type: application/json

{ "email": "alice@example.com", "role": "editor" }
```

Invites a user. If the user already has an account, they’re added directly. Otherwise an invitation join code is generated and (when email is configured) emailed to them.

```
PATCH /api/v1/workspaces/{workspace}/members/{userID}
DELETE /api/v1/workspaces/{workspace}/members/{userID}
DELETE /api/v1/workspaces/{workspace}/members/invitations/{invID}
```

Update a member’s role, remove a member, or cancel a pending invitation.

### Accept an Invitation

```
POST /api/v1/invitations/{code}/accept
```

Public-ish endpoint — does not require workspace membership; the invitation `code` is the proof. Authenticated callers are added to the target workspace with the role embedded in the invitation.

### Agent Roles

```
GET /api/v1/workspaces/{workspace}/agent-roles
POST /api/v1/workspaces/{workspace}/agent-roles
GET /api/v1/workspaces/{workspace}/agent-roles/{roleID}
PATCH /api/v1/workspaces/{workspace}/agent-roles/{roleID}
DELETE /api/v1/workspaces/{workspace}/agent-roles/{roleID}
```

CRUD for the role definitions used to organize work by capability profile (Planner / Implementer / Reviewer / etc.). Items can be assigned to a `(user, agent_role_id)` pair.

**Create body:**

```
{
  "name": "Designer",
  "slug": "designer",
  "description": "UX research, IA, visual design",
  "icon": "🎨"
}
```

## Collections

### List Collections

```
GET /api/v1/workspaces/{workspace}/collections
```

**Response:**

```
[
  {
    "id": "uuid",
    "name": "Tasks",
    "slug": "tasks",
    "icon": "✓",
    "description": "Track work items, bugs, and to-dos",
    "schema": { "fields": [...] },
    "item_count": 12
  }
]
```

### Create Collection

```
POST /api/v1/workspaces/{workspace}/collections
Content-Type: application/json

{
  "name": "Bugs",
  "icon": "🐛",
  "schema": {
    "fields": [
      { "key": "severity", "type": "select", "options": ["low", "medium", "high"] }
    ]
  }
}
```

## Items

### List Items

```
GET /api/v1/workspaces/{workspace}/collections/{collection}/items
```

**Query parameters:**

- `status` — filter by status
- `priority` — filter by priority
- `all` — include done/archived items (`true`/`false`)

### Create Item

```
POST /api/v1/workspaces/{workspace}/collections/{collection}/items
Content-Type: application/json

{
  "title": "Fix OAuth redirect",
  "fields": {
    "status": "open",
    "priority": "high"
  },
  "content": "## Description\n\nThe OAuth redirect is broken..."
}
```

### Get Item

```
GET /api/v1/workspaces/{workspace}/items/{slug}
```

### Update Item

```
PATCH /api/v1/workspaces/{workspace}/items/{slug}
Content-Type: application/json

{
  "fields": {
    "status": "done"
  }
}
```

### Delete Item

```
DELETE /api/v1/workspaces/{workspace}/items/{slug}
```

### Item Children

```
GET /api/v1/workspaces/{workspace}/items/{slug}/children
```

Returns child items linked to this parent (via the `--parent` flag at create time). Used for plan → tasks tree views and progress aggregation.

### Item Progress

```
GET /api/v1/workspaces/{workspace}/items/{slug}/progress
```

Returns `{ total, done, in_progress, percent }` summarising child completion status. Powers the dashboard’s Active Plans progress bars.

### Item Links

```
GET /api/v1/workspaces/{workspace}/items/{slug}/links
POST /api/v1/workspaces/{workspace}/items/{slug}/links
DELETE /api/v1/workspaces/{workspace}/links/{linkID}
```

Item-to-item relationships beyond parent/child: dependencies (`blocks`, `blocked_by`) and lineage (`split_from`, `supersedes`, `implements`). Each link has a `type`, a `source_id`, and a `target_id`.

**Create body:**

```
{ "target_slug": "TASK-12", "type": "blocks" }
```

## Search

### Full-Text Search

```
GET /api/v1/search?q=OAuth&workspace={workspace}
```

Returns items matching the query across all collections, ranked by relevance.

## Real-Time Events

### SSE Stream

```
GET /api/v1/events?workspace={workspace}
```

Server-Sent Events stream for real-time updates. Events are emitted when items are created, updated, or deleted.

**Event format:**

```
{
  "type": "item.updated",
  "workspace": "my-project",
  "collection": "tasks",
  "item_slug": "fix-oauth-redirect",
  "timestamp": "2026-03-26T12:00:00Z"
}
```

## Dashboard

### Get Dashboard

```
GET /api/v1/workspaces/{workspace}/dashboard
```

Returns computed project overview including:

- **summary** — Total items + per-collection status breakdown
- **active\_items** — Items currently in progress with refs, priority, status
- **active\_plans** — Plans with progress percentages and task counts
- **attention** — Overdue, stalled, blocked, and orphaned items
- **suggested\_next** — Recommended next tasks from active plans
- **recent\_activity** — Last 10 workspace events

## Activity

### List Activity

```
GET /api/v1/workspaces/{workspace}/activity?limit=30&offset=0&action=created&source=cli
```

Returns workspace activity entries. Supports filtering by action type and source.

**Query parameters:**

- `limit` — Max entries to return (default: 30)
- `offset` — Pagination offset
- `action` — Filter by action: `created`, `updated`, `archived`, `restored`
- `source` — Filter by source: `web`, `cli`

## Webhooks

### List Webhooks

```
GET /api/v1/workspaces/{workspace}/webhooks
```

Each webhook includes `failure_count` (consecutive failed deliveries) and `dropped_count` (events dropped while still owed to it; see [Delivery and retries](#delivery-and-retries)).

### Create Webhook

```
POST /api/v1/workspaces/{workspace}/webhooks
```
```
{
  "url": "https://example.com/webhook",
  "events": "[\"item.created\", \"item.updated\"]",
  "secret": "optional-hmac-secret"
}
```

Events: `item.created`, `item.updated`, `item.deleted`, `item.moved`, `comment.created`, or `*` for all.

When a secret is provided, each delivery includes an `X-Pad-Signature` header with an HMAC-SHA256 signature of the payload.

Webhooks are automatically deactivated after 10 consecutive delivery failures.

#### Delivery and retries

Each event is delivered to each matching webhook at least once. Every delivery carries the event’s `id`, so a receiver can drop a duplicate.

- A `2xx` response means the webhook accepted the event. It is not sent that event again.
- A `5xx` response, a timeout or a network error is retried. So are `408 Request Timeout`, `425 Too Early` and `429 Too Many Requests`.
- Any other response (for example `400` or `404`) is final for that event: the webhook is not sent it again.
- A retry goes only to webhooks still owed the event, never to one that already accepted or refused it.

Events are kept for retrying for 7 days (the default; a self-hosted server can change it with `PAD_OUTBOX_MAX_AGE`). An event still owed to a webhook when that window ends, or when the webhook is deactivated, is dropped. `GET /webhooks` reports these as `dropped_count`, and `pad webhook list` shows them in the `DROPPED` column.

### Delete Webhook

```
DELETE /api/v1/workspaces/{workspace}/webhooks/{id}
```

### Test Webhook

```
POST /api/v1/workspaces/{workspace}/webhooks/{id}/test
```

Sends a test payload to verify the webhook is receiving events correctly.

## Admin

Endpoints below require an admin account. They control platform-level settings, user lifecycle, and operational tooling.

### Platform Settings

```
GET /api/v1/admin/settings
PATCH /api/v1/admin/settings
```

Fetch or update server-wide settings stored in the `platform_settings` table. Used for plan limits, feature flags, and email templates that need to be tunable without a redeploy.

### Test Email

```
POST /api/v1/admin/test-email
Content-Type: application/json

{ "to": "ops@example.com" }
```

Sends a one-off test email through the configured Maileroo provider. Useful for verifying SMTP/API configuration after rotating keys.

### User Administration

```
GET    /api/v1/admin/users                              # List users
GET    /api/v1/admin/users/{userID}                     # User detail
PATCH  /api/v1/admin/users/{userID}                     # Update profile / role / status
POST   /api/v1/admin/users/{userID}/reset-password      # Generate password-reset link
GET    /api/v1/admin/users/{userID}/workspaces          # User's workspace memberships
POST   /api/v1/admin/users/{userID}/disable             # Suspend the account
POST   /api/v1/admin/users/{userID}/enable              # Re-enable a suspended account
```

### Invitations Administration

```
GET    /api/v1/admin/invitations                        # All pending invitations
POST   /api/v1/admin/invitations/{invID}/resend         # Re-send the invitation email
DELETE /api/v1/admin/invitations/{invID}                # Cancel an invitation
```

### Plan Limits

```
GET   /api/v1/admin/limits
PATCH /api/v1/admin/limits
```

Read or update the plan-limit table (`workspaces`, `items_per_workspace`, `members_per_workspace`, `api_tokens`, `storage_bytes`, `webhooks`, `automated_backups` — per plan tier). DB-stored, idempotent on restart, so admin tweaks survive deploys.

### Stats

```
GET /api/v1/admin/stats
```

Returns aggregate counts (active users, total items, signups in the last 30 days, plan distribution).
