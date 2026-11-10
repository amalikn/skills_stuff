**Title:** Pad MCP — Connect Claude Desktop, Cursor, Windsurf, Claude Code, Codex to your local workspace

**Source:** [https://www.getpad.dev/mcp/local](https://www.getpad.dev/mcp/local)

---

# Page Structure Map
```text
Pad MCP — Connect Claude Desktop, Cursor, Windsurf, Claude Code, Codex to your local workspace
├── 1\. Quick start (under 2 minutes)
├── 2\. What's exposed over MCP
│   ├── Tools — 9 resource-action tools
│   ├── Resources — read workspace state without a tool call
│   ├── Prompts — drop-in workflows from the /pad skill
│   └── Stability contract — two version constants
├── 3\. Install in detail
├── 4\. Where pad writes the config
├── 5\. Manual configuration (advanced)
├── 6\. Setting the active workspace
├── 7\. Error envelopes
├── 8\. Server instructions
├── 9\. Troubleshooting
│   ├── Client says "could not find server 'pad'"
│   ├── Where do MCP server logs go?
│   ├── Will my other MCP servers still work?
│   └── "Permission denied" reading the config file
└── 10\. The cloud variant: Pad Cloud as a remote MCP server
```

---

## 1\. Quick start (under 2 minutes)

If `pad` is already installed and you've got a workspace:

```
pad mcp install claude-desktop   # or: cursor, windsurf, claude-code, codex, --all
# Restart the client, ask it to use the "pad" MCP server.
```

That's the whole thing. The install command:

- Resolves the right config file for your OS (paths in §4).
- Adds a `pad` entry pointing the client at `pad mcp serve` — a JSON `mcpServers.pad` object for most clients, or a TOML `[mcp_servers.pad]` table for Codex.
- Preserves any other MCP servers you've already configured (we never clobber the file).
- Sets the file to mode `0600` so other servers' API keys stay private.

After restarting the client, ask it: *"Set the workspace to `my-project` and show me my dashboard."* The client calls `pad_set_workspace` + reads `pad://workspace/my-project/dashboard`.

## 2\. What's exposed over MCP

Heads up — hand-curated surface (clean break at v0.2)

Pad's earlier MCP surface auto-derived ~85 flat verb tools (`item_create`, `item_block`, `item_star`, …) from the CLI help tree. As of `tool_surface_version: "0.2"` that's gone, replaced with a hand-curated catalog of resource-action tools (nine today, at `tool_surface_version: "0.9"`). There is no compatibility shim — anything pinning against the v0.1 tool names won't dispatch. Pin against `tool_surface_version` from `pad://_meta/version` going forward.

### Tools — 9 resource-action tools

Instead of one tool per leaf CLI command, the MCP catalog is organized as *resource × action*: a small set of top-level tools, each accepting an `action` enum that selects the operation. This keeps the surface small enough to fit in an agent's tool list without crowding out everything else.

| Tool | Actions | Notes |
| --- | --- | --- |
| `pad_item` | `create`, `update`, `delete`, `restore`, `get`, `list`, `move`, `link`, `unlink`, `deps`, `backlinks`, `star`, `unstar`, `starred`, `comment`, `list-comments`, `bulk-update`, `note`, `decide`, `export`, `import` | The main resource. `link` / `unlink` take a `link_type` enum (`blocks`, `blocked-by`, `supersedes`, `implements`, `split-from`). `bulk-update` takes `refs: array<string>` instead of a scalar `ref`. |
| `pad_workspace` | `list`, `members`, `invite`, `storage`, `audit-log`, `create`, `claim`, `deleted`, `restore` | Workspace operations. `deleted` / `restore` cover 30-day soft-delete recovery. |
| `pad_collection` | `list`, `create`, `update`, `delete` | Collection types. |
| `pad_project` | `dashboard`, `next`, `standup`, `changelog`, `report` | Computed views. |
| `pad_role` | `list`, `create`, `update`, `delete` | Agent roles. |
| `pad_search` | `query` | Cross-workspace full-text search. |
| `pad_playbook` | `list`, `get`, `run` | Invokable procedures. `run` binds args and returns the body; side-effect-free. |
| `pad_library` | `list`, `get`, `activate` | Shared convention + playbook library. `activate` copies an entry into the workspace. |
| `pad_meta` | `server-info`, `version`, `tool-surface`, `bootstrap` | Server introspection. `tool-surface` returns the full catalog as JSON — useful for generating docs against a live server. |
| `pad_set_workspace` | (no `action` — `workspace` arg required) | Pin the session-default workspace; see §6. |

Every tool except `pad_meta` and `pad_set_workspace` accepts an optional `workspace` parameter. Resolution order is described in §6.

Interactive / destructive / streaming commands are intentionally not on the surface — `auth setup/login`, `db backup/restore`, `init`, `workspace export/import`, `item edit` (opens `$EDITOR`), `project watch` (streaming) all stay CLI-only.

### Resources — read workspace state without a tool call

Resources let agents *read* workspace state by URL without picking a tool. Four workspace-scoped templates plus two server-wide static resources are advertised:

| URI | Returns | MIME |
| --- | --- | --- |
| `pad://workspaces` | Top-level workspace list (slug, name, updated\_at, default) | `application/json` |
| `pad://workspace/{ws}/items/{ref}` | Single item — heading, parent link, fields, body | `text/markdown` |
| `pad://workspace/{ws}/items` | List of every item in the workspace | `application/json` |
| `pad://workspace/{ws}/dashboard` | Computed project overview (active items, plans, attention, blockers) | `application/json` |
| `pad://workspace/{ws}/collections` | Collection list + JSON Schemas | `application/json` |
| `pad://_meta/version` | Server-wide tool-surface stability metadata — see Stability contract | `application/json` |

`pad://workspaces` is the entry point an agent should hit when it has no workspace context yet — it lists every workspace the caller can see, marks the default, and gives the agent enough information to either pick one and call `pad_set_workspace`, or ask the user.

### Prompts — drop-in workflows from the /pad skill

Four multi-step workflows are exposed as MCP prompts so an agent can `prompts/get` one and have the workflow text injected as a system message. Identical content to what ships in the `/pad` skill — same workflow, different transport.

- `pad_plan` — load context, propose an outline, decompose into tasks with `--parent` links.
- `pad_ideate` — search related items, discuss, capture as `idea` / `doc` with confirmation.
- `pad_retro` — pull a completed plan + its tasks, generate what-shipped/what-was-deferred/lessons, save as a retro doc.
- `pad_onboard` — workspace state check, look for an Onboarding playbook, codebase scan, suggest conventions.

### Stability contract — two version constants

The MCP surface is a public contract, but it has two independent moving parts that version separately. Tool names, argument shapes, and resource URIs are stable within a major `tool_surface_version`; the underlying CLI help tree is versioned by `cmdhelp_version`. Bumps to either are reserved for incompatible changes.

- **`tool_surface_version`** (currently `"0.9"`) — the MCP tool catalog contract. This is what external agents should pin against. Advertised in the initialize handshake at `result.capabilities.experimental.padToolSurface`.
- **`cmdhelp_version`** (currently `"0.1"`) — the CLI help-tree contract used at dispatch time. Advertised at `result.capabilities.experimental.padCmdhelp`. Most consumers don't need to care about this one; it tracks the shape of `pad help --format json`.

Both surface together in one document at `pad://_meta/version`:

```
{
  "pad_version": "0.1.5",
  "cmdhelp_version": "0.1",
  "tool_surface_version": "0.9",
  "tool_surface_stable": true,
  "mcp_protocol_version": "2025-11-25"
}
```

`mcp_protocol_version` is the *maximum* MCP wire revision the server can negotiate (sourced from the underlying mcp-go library so it tracks upstream). `tool_surface_version` is what changes when tool renames, argument shape changes, or resource URI changes break consumers — pin against it.

## 3\. Install in detail

```
pad mcp status                    # Show install state across per-user clients
pad mcp install claude-desktop    # Install for one client
pad mcp install cursor
pad mcp install windsurf
pad mcp install codex             # ~/.codex/config.toml (TOML)
pad mcp install claude-code       # project-local ./.mcp.json (current directory)
pad mcp install --all             # Install for every per-user client (skips claude-code)
pad mcp uninstall cursor          # Remove the entry (other servers preserved)
```

**Claude Code is project-scoped.** It reads a `.mcp.json` from the directory it's launched in, so `pad mcp install claude-code` writes into your *current* directory — run it from the project root you want pad available in. Because there's no single global target, `--all` and `pad mcp status` (which cover the per-user clients) intentionally skip it; install it explicitly per project.

`pad mcp install` with no arguments prints the same status table as `pad mcp status` — useful as a quick "did it take?" check.

Installs are idempotent. Re-running `pad mcp install claude-desktop` after the binary moves on disk just refreshes the `command` path in the config — the rest of the file is untouched.

## 4\. Where pad writes the config

| Client | macOS / Linux | Windows |
| --- | --- | --- |
| Claude Desktop | `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS)   `~/.config/Claude/claude_desktop_config.json` (Linux) | `%APPDATA%\Claude\claude_desktop_config.json` |
| Cursor | `~/.cursor/mcp.json` | `~/.cursor/mcp.json` |
| Windsurf | `~/.codeium/windsurf/mcp_config.json` | `%APPDATA%\Codeium\windsurf\mcp_config.json` |
| Claude Code | `./.mcp.json` (project-local, in the current directory) | `.\.mcp.json` |
| Codex | `~/.codex/config.toml` (TOML `[mcp_servers.pad]`) | `%USERPROFILE%\.codex\config.toml` |

All clients except Codex use JSON with an `mcpServers.pad` entry; Codex uses a TOML `[mcp_servers.pad]` table. In every case pad merges into the existing file — other MCP servers and unrelated config keys are preserved — and tightens the file to mode `0600`.

## 5\. Manual configuration (advanced)

If you want to wire pad into a client we don't yet support, use this entry shape (any MCP-compatible client accepts it):

```
{
  "mcpServers": {
    "pad": {
      "command": "/usr/local/bin/pad",
      "args": ["mcp", "serve"]
    }
  }
}
```

The client spawns `pad mcp serve`; the server speaks JSON-RPC over stdio and shuts down on `EOF` / `SIGINT` / `SIGTERM`.

## 6\. Setting the active workspace

Every workspace-scoped tool call needs a workspace context. (`pad_meta` and `pad_set_workspace` are the two exceptions — they're server-wide.) Resolution order:

1. **Explicit per-call:** the client passes `workspace` in the tool's arguments. Always wins.
2. **Session default:** the agent calls `pad_set_workspace` once and subsequent calls inherit it for the lifetime of that MCP session.
3. **CWD `.pad.toml`:** if the server's working directory contains a workspace marker, that workspace is used. (For local installs spawned by a desktop client, the CWD is whatever the client launched from — usually your home directory, so this rarely fires unless you've set up a workspace there.)

If *none* of those resolves, the call doesn't fail silently — it returns a structured `no_workspace` error envelope (see §7) with an `available_workspaces` array. Agents are expected to read that, pick a workspace, call `pad_set_workspace`, and retry. The `pad://workspaces` resource gives the same list ahead of time if the agent wants to choose proactively.

Resource URIs always include the workspace explicitly (`pad://workspace/{ws}/...`) so reads never depend on session state.

## 7\. Error envelopes

Every 4xx / 5xx response comes back as a structured JSON envelope with a closed eight-code taxonomy, not as an opaque string. Agents can branch on `error.code` and self-recover for the common ones (`no_workspace`, `unknown_workspace`) without involving the human.

| Code | When | Extra fields |
| --- | --- | --- |
| `no_workspace` | No workspace context resolves | `available_workspaces` |
| `unknown_workspace` | Slug doesn't exist or isn't visible to the caller | `available_workspaces` |
| `auth_required` | Credentials missing or expired | `hint` |
| `permission_denied` | Auth ok, role insufficient | `required_role`, `current_role` |
| `item_not_found` | Bad item ref or slug | `hint` |
| `validation_failed` | Bad input | `field`, `expected`, `got` |
| `conflict` | Concurrent state collision | `hint` |
| `server_error` | Catch-all for unexpected failures | `hint` (with raw detail) |

Wire shape:

```
{
  "error": {
    "code": "no_workspace",
    "message": "No workspace context. Pass `workspace` explicitly, ...",
    "hint": "Available workspaces: docapp, pad-web",
    "available_workspaces": [
      { "slug": "docapp", "default": true },
      { "slug": "pad-web", "default": false }
    ]
  }
}
```

Agents that branch on `error.code` stay robust across error message rewording. The eight codes are the contract; the prose is not.

## 8\. Server instructions

The `initialize` response carries a top-level `instructions` string telling agents *when* to reach for pad — what kinds of user asks should trigger a tool call (issue refs like `TASK-5`, "what's on my plate", planning / standup / changelog), and a quick orientation to the v0.9 tool catalog and resources.

Most clients surface this string to the model verbatim, so it's part of the contract. The authoritative text lives at `internal/mcp/instructions.md` — that file is what the server actually sends. The page sections above are extended guidance that complements it (the live instructions are deliberately short to fit in the model's system context).

## 9\. Troubleshooting

### Client says "could not find server 'pad'"

- Run `pad mcp status` — confirm the client's row shows `[x]` with the right binary path.
- If the path looks wrong (e.g. you moved `pad` after installing), re-run `pad mcp install <client>` to refresh.
- Restart the client app after install — most clients only re-read MCP config on launch.

### Where do MCP server logs go?

`stderr`. `stdout` is reserved for JSON-RPC; writing to it from the server would corrupt the protocol stream. Run with `--debug` for verbose output:

```
pad mcp serve --debug 2> /tmp/pad-mcp.log
```

Most clients capture the spawned server's stderr to their own log file — check the client's docs for where (Claude Desktop: `~/Library/Logs/Claude/` on macOS).

### Will my other MCP servers still work?

Yes. `pad mcp install` only modifies pad's own entry (`mcpServers.pad`, or `[mcp_servers.pad]` for Codex); every other entry in the file is preserved verbatim. `pad mcp uninstall` removes only that entry.

### "Permission denied" reading the config file

Pad sets the config file to mode `0600`. If the client app you're using runs as a different user (e.g. inside a container), you may need to adjust ownership manually.

## 10\. The cloud variant: Pad Cloud as a remote MCP server

This page covers the **local** MCP server — pad runs on your machine, the client spawns it as a subprocess. The complement is Pad Cloud's **remote** MCP server: same v0.9 catalog, served over Streamable HTTP at `https://mcp.getpad.dev`, authenticated with OAuth so any cloud-based agent (web apps, mobile, hosted Claude) can connect without a local install. See the Remote MCP page for per-agent setup, the auth model, and the full tool catalog.
