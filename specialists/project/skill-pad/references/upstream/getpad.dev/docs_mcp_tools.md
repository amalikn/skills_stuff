**Title:** MCP — Tool catalog (v0.9)

**Source:** [https://www.getpad.dev/docs/mcp/tools](https://www.getpad.dev/docs/mcp/tools)

---

# Page Structure Map
```text
MCP — Tool catalog (v0.9)
├── Tool catalog (v0.9)
├── Capability scopes
├── Tools
│   ├── pad\set\workspace
│   ├── pad\item
│   ├── pad\workspace
│   ├── pad\collection
│   ├── pad\project
│   ├── pad\role
│   ├── pad\search
│   ├── pad\playbook
│   ├── pad\library
│   └── pad\meta
├── Resources
├── Prompts
└── Going deeper
```

---

## Tool catalog (v0.9)

Pad’s remote MCP server at `https://mcp.getpad.dev` advertises a hand-curated catalog of resource × action tools. Each resource-action tool takes an `action` enum that selects the operation, plus action-specific parameters (`pad_set_workspace` is the exception — it takes a `workspace` slug, no `action`). This shape keeps the surface compact (10 tools in the agent’s tool list, not 80+) without losing access to any individual capability.

The contract is versioned. Two independent version tiers are advertised:

- **`padToolSurface`** — the MCP tool catalog shape (this page documents v0.9).
- **`padCmdhelp`** — the underlying CLI help-tree shape (currently `"0.1"`). Bumps independently from the tool surface.

The handshake’s `result.capabilities.experimental` block carries both:

```
{
  "result": {
    "capabilities": {
      "experimental": {
        "padToolSurface": { "version": "0.9", "tool_surface_stable": true },
        "padCmdhelp":     { "version": "0.1", "tool_surface_stable": true }
      }
    }
  }
}
```

The same values are also reachable two other ways:

- Read the `pad://_meta/version` resource:
	```
	{ "tool_surface_version": "0.9", "cmdhelp_version": "0.1" }
	```
- Call the `pad_meta` tool with `action: version` — same payload as the resource.

Pin against `tool_surface_version: "0.9"` if you’re building a downstream consumer. Breaking changes bump the version and are announced on the [blog](https://www.getpad.dev/blog) before they ship.

## Capability scopes

Every tool action is gated by one of three scopes:

| Scope | Example actions |
| --- | --- |
| `pad:read` | `pad_item.list`, `pad_item.get`, `pad_search.query`, `pad_project.dashboard` |
| `pad:write` | `pad_item.create`, `pad_item.update`, `pad_item.comment`, `pad_item.bulk-update` |
| `pad:admin` | `pad_workspace.invite`, `pad_collection.create`, `pad_role.create` |

A token’s scope is set at consent time and is bounded by your role in each workspace at call time. See [the Remote MCP overview’s authentication section](https://www.getpad.dev/mcp/remote#authentication-overview) for the full model.

## Tools

### pad\_set\_workspace

Sets the active workspace for the rest of the conversation. After calling this, every subsequent tool call defaults to that workspace unless you explicitly pass a different one via the `workspace` parameter.

| Parameter | Type | Description |
| --- | --- | --- |
| `workspace` | string | Workspace slug (e.g. `my-project`) |

Returns: the workspace’s `{ slug, name, role }` for confirmation, plus an embedded `bootstrap` blob (the same payload as `pad_meta.bootstrap` / `pad://workspace/{ws}/bootstrap`) so you pin the workspace and load its context in one round-trip.

### pad\_item

Items are the universal unit: tasks, ideas, plans, docs, and any custom collections you’ve defined. References use issue IDs (`TASK-5`, `BUG-12`, `PLAN-3`).

| Action | Scope | Notes |
| --- | --- | --- |
| `list` | read | List items, filter by collection / status / priority / parent / role / assignee. **Summary shape** (see note below) |
| `get` | read | Show full item including content, comments, links |
| `create` | write | Create an item; specify collection, title, optional fields |
| `update` | write | Partial update; pass `comment` to capture *why* (also how role assignment happens — set `role` to a role slug) |
| `delete` | write | Archive (soft delete) |
| `restore` | write | Un-archive a soft-deleted item |
| `move` | write | Move between collections |
| `link` | write | Create a relationship — see `link_type` enum below |
| `unlink` | write | Remove a relationship of a given `link_type` |
| `deps` | read | Show dependency graph for an item |
| `backlinks` | read | Inbound `[[…]]` references (“Mentioned in”), paged via `limit` / `offset` |
| `star` / `unstar` | write | Personal-pin (per user, per item) |
| `starred` | read | List your starred items |
| `comment` | write | Add a comment, optionally a reply via `reply_to` |
| `list-comments` | read | Read the comment thread |
| `bulk-update` | write | Apply the same patch to multiple items (`refs: array<string>`) |
| `note` | write | Append an implementation\_notes entry |
| `decide` | write | Append a decision\_log entry |
| `export` | read | Return the portable artifact text (YAML frontmatter + Markdown) for a playbook or convention |
| `import` | write | Create an item from artifact text (the `artifact` param); returns `{ref, slug, warnings}` |

As of tool-surface **v0.9**, `pad_item.list` returns a **summary shape** by default: each item omits its rich `content` body and the result set is capped (default 50, hard max 300 on the MCP surface). This keeps large listings from flooding the agent’s context. To read an item’s full content, fetch it directly with `pad_item.get`; the local CLI (`pad item list`) exposes a `--full` flag to restore the complete shape (with its own higher 200 / 1000 caps).

`link_type` enum (for `link` / `unlink`): `blocks`, `blocked-by`, `supersedes`, `implements`, `split-from`. Full-text search over items is exposed separately as [`pad_search.query`](#pad_search) — not as a `pad_item` action.

### pad\_workspace

| Action | Scope | Notes |
| --- | --- | --- |
| `list` | read | List workspaces this token can access |
| `members` | read | List members of a workspace |
| `invite` | admin | Invite a user by email |
| `storage` | read | Workspace storage usage (items, attachments, etc.) |
| `audit-log` | read | Workspace audit-log entries (filter by `audit_action`) |
| `create` | admin | Create a new workspace (optional `template`); auto-joins this connection |
| `claim` | admin | Add an existing workspace to this connection via its 6-digit claim `code` |
| `deleted` | read | List the caller’s soft-deleted workspaces still inside the 30-day restore window |
| `restore` | admin | Un-delete a workspace by `slug` while it’s still restorable (owner-only) |

### pad\_collection

Collections are typed item containers (Tasks, Ideas, Plans, Docs by default; custom collections supported).

| Action | Scope | Notes |
| --- | --- | --- |
| `list` | read | List collections in the workspace with their schemas + counts |
| `create` | admin | Define a new collection (typed fields via the field DSL or full `schema`) |
| `update` | admin | Rename, re-icon, or reshape a collection’s schema |
| `delete` | admin | Remove a user-created collection |

### pad\_project

Higher-level intelligence tools that aggregate across collections.

| Action | Scope | Notes |
| --- | --- | --- |
| `dashboard` | read | Active items, plans, attention items, suggestions |
| `next` | read | Recommended next task (role-aware if role is set) |
| `standup` | read | Recently completed / in-progress / blockers (configurable lookback) |
| `changelog` | read | Release notes from completed items (range-filterable) |
| `report` | read | Roll-up report over a `window` (day / week / 2wk / month) |

### pad\_role

Pad’s agent-role system (Planner, Implementer, Reviewer, etc.) lets users organize work by *what kind of thinking it requires*.

| Action | Scope | Notes |
| --- | --- | --- |
| `list` | read | List workspace roles |
| `create` | admin | Define a new role (slug, name, optional icon + description) |
| `update` | admin | Rewrite a role’s name, slug, description, or icon |
| `delete` | admin | Remove a role |

Role *assignment* is not a `pad_role` action — assign items to a (user, role) pair via `pad_item.action: update` with the `role` and `assign` parameters.

### pad\_search

| Action | Scope | Notes |
| --- | --- | --- |
| `query` | read | Full-text search across items in the workspace |

Returns: `{ items, total }`. Cross-collection by design.

### pad\_playbook

Playbooks are workspace-owned, user-invokable procedures. The MCP tool mirrors `pad playbook` (list / show / run) so a remote agent can browse and execute playbooks the same way a local CLI user does.

| Action | Scope | Notes |
| --- | --- | --- |
| `list` | read | Workspace playbook metadata (slug, invocation\_slug, trigger, status, has\_arguments, summary). Same shape as the bootstrap response |
| `get` | read | Full body + fields for one playbook; accepts `invocation_slug`, item slug, or issue ref |
| `run` | read | Parse args against the playbook’s declared spec and return the body + bound args + any unbound required args. **Side-effect-free** — the server never executes a playbook; the agent reads the body and runs the steps |

For `action: run`, pass either:

- `args` (object) — pre-parsed argument map keyed by name, OR
- `raw_args` (array of strings) — CLI-style tokens (positional values, bareword flags, `key=value` pairs); the server applies the same strict parser as `pad playbook run`.

The two forms are mutually compatible — explicit `args` take precedence over `raw_args` on key conflicts.

See [Playbooks →](https://www.getpad.dev/docs/playbooks) for the author guide.

### pad\_library

The global convention + playbook library — the catalog of pre-built entries a workspace activates into its own collections.

| Action | Scope | Notes |
| --- | --- | --- |
| `list` | read | Browse library entries; filter by `type` (convention / playbook) or `category` |
| `get` | read | Full body of one library entry by `title` |
| `activate` | write | Copy a library entry into the workspace’s conventions / playbooks collection |

### pad\_meta

| Action | Scope | Notes |
| --- | --- | --- |
| `server-info` | read | Server name + runtime version (lightweight, no params) |
| `version` | read | Full version metadata: pad version, `cmdhelp_version`, `tool_surface_version`, MCP protocol version (same JSON as `pad://_meta/version`) |
| `tool-surface` | read | Catalog dump: every tool, action, and input schema |
| `bootstrap` | read | One-shot workspace overview: workspace + user + collections + always-on conventions + roles + playbook metadata + dashboard + recent activity. Equivalent to `pad://workspace/{ws}/bootstrap` and to `pad_set_workspace`’s embedded response |

## Resources

The MCP `resources/list` surface exposes:

- `pad://workspaces` — list of workspaces this token can access (top-level, server-wide)
- `pad://workspace/{ws}/items/{ref}` — a single item
- `pad://workspace/{ws}/items` — all items in a workspace
- `pad://workspace/{ws}/dashboard` — the dashboard payload (same as `pad_project.dashboard`)
- `pad://workspace/{ws}/collections` — collection list
- `pad://workspace/{ws}/bootstrap` — one-shot workspace overview (same as `pad_meta.bootstrap` and `pad_set_workspace`’s embedded response)
- `pad://_meta/version` — server-wide version + contract metadata

Resources are read-only and cheaper for an agent to inspect than calling a tool.

## Prompts

Pad ships four MCP prompts (multi-step workflows the agent can run on demand):

- `pad_plan` — guided plan creation
- `pad_ideate` — brainstorming workflow that captures ideas at checkpoints
- `pad_retro` — retrospective for a completed plan
- `pad_onboard` — codebase analysis + workspace setup

These are the same workflows the local `/pad` skill exposes. The remote MCP server hands them to any client that supports `prompts/get`.

## Going deeper

- The Go source of the catalog is at [`internal/mcp/catalog_*.go`](https://github.com/PerpetualSoftware/pad/tree/main/internal/mcp). Each `pad_<resource>` is its own file.
- For local-machine MCP (no account, runs against a SQLite file on your laptop), see [MCP — Local](https://www.getpad.dev/mcp/local). It exposes the same v0.9 catalog over stdio.

[← Remote MCP overview](https://www.getpad.dev/mcp/remote) · [Troubleshooting →](https://www.getpad.dev/docs/mcp/troubleshooting)
