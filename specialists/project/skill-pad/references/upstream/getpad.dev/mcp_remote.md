**Title:** MCP — Connect your AI agent to Pad

**Source:** [https://www.getpad.dev/mcp/remote](https://www.getpad.dev/mcp/remote)

---

# Page Structure Map
```text
MCP — Connect your AI agent to Pad
├── MCP
├── What you get
├── Pick your agent
├── Reference
├── What’s exposed
├── Authentication overview
├── What if I don’t have a Pad account yet?
└── Privacy and data handling
```

---

## MCP

Pad Cloud runs as a remote Model Context Protocol server at `https://mcp.getpad.dev`. Drop the URL into any MCP-capable agent (Claude Desktop, Cursor, ChatGPT, Windsurf), sign in with the same Pad account you use for the web UI, and your agent can read and write your tasks, ideas, plans, and docs through natural conversation.

This is the **remote** path — zero local install. If you’d rather run an MCP server on your own machine against a local SQLite database, see MCP — Local instead.

## What you get

- A single copyable URL: `https://mcp.getpad.dev`
- OAuth 2.1 authentication with PKCE — your agent never holds your password
- Per-workspace consent: choose which Pad workspaces this connection can read or write at sign-in time
- Per-call permission enforcement: your role in each workspace (Owner, Editor, Viewer) is checked on every tool call
- Revocable from the web UI: open `/console/connected-apps`, click revoke, the next call from that agent fails with 401

## Pick your agent

Step-by-step setup for each MCP-capable client:

- **Claude Desktop** — the most commonly tested path; works on macOS, Windows, and Linux
- **Cursor** — IDE-integrated MCP support
- **ChatGPT** — via OpenAI’s custom connector / remote MCP server feature; availability depends on your plan and workspace admin policy
- **Windsurf** — IDE-integrated MCP support

## Reference

- **Tool catalog** — every tool the remote MCP surface exposes, with parameters, return shapes, and required scopes (v0.9 contract)
- **Troubleshooting** — common errors and their fixes

## What’s exposed

Pad’s MCP server advertises a hand-curated **v0.9** tool surface: nine resource × action tools (`pad_item`, `pad_workspace`, `pad_collection`, `pad_project`, `pad_role`, `pad_search`, `pad_playbook`, `pad_library`, `pad_meta`) plus `pad_set_workspace` for the session default — **ten tools total**. Plus four MCP prompts (`pad_plan`, `pad_ideate`, `pad_retro`, `pad_onboard`), and read-only resources for items, dashboards, and the server-wide `_meta/version`.

Each resource-action tool takes an `action` enum that selects the operation (`pad_item.action: list`, `pad_item.action: create`, etc.); `pad_set_workspace` is the exception — it takes a `workspace` slug, no `action`. This keeps the surface compact enough to leave room for your agent’s other connectors.

The contract is versioned: the handshake advertises `capabilities.experimental.padToolSurface.version` (currently `"0.9"`), and the same value is reachable as `tool_surface_version` from the `pad://_meta/version` resource and the `pad_meta` tool. If we make breaking changes, that version bumps and your client gets a clear signal to re-pin. See Tool catalog for the full enumeration and exact wire shapes.

## Authentication overview

When your agent connects to `https://mcp.getpad.dev` for the first time, it doesn’t have a token. The server returns a `401 Unauthorized` with a `WWW-Authenticate` header pointing at our OAuth metadata. Your agent follows that to:

1. Discover Pad’s authorization server (`https://app.getpad.dev`)
2. Register itself dynamically (RFC 7591) — no manual app creation
3. Open a browser tab to Pad’s `/oauth/authorize` page
4. Walk you through sign-in (or sign-up if you don’t have a Pad account yet)
5. Show you a consent screen: pick which workspaces this connection can access and at what permission tier (read-only / read-write / admin)
6. Issue a token bound to that workspace allow-list and tier
7. Retry the original request with `Authorization: Bearer <token>`

After this, your agent calls Pad over the lifetime of the token. Tokens are audience-restricted to the MCP transport URL `https://mcp.getpad.dev/mcp` (RFC 8707) — they can’t be replayed against any other server. The `/mcp` path is the internal transport mount; you still only ever paste `https://mcp.getpad.dev` into your client (our nginx transparently rewrites the root to `/mcp` so the canonical URL stays clean).

## What if I don’t have a Pad account yet?

You’ll create one as part of step 4 above. The sign-in page on `app.getpad.dev` carries a “Don’t have an account? Sign up” link that preserves your in-flight OAuth flow — finish registration, return to the consent screen, grant access, and you’re connected. New accounts get a default workspace seeded with the startup template so the consent screen has something to grant against immediately.

## Privacy and data handling

- Your tokens are opaque random strings, not JWTs. Revoking a token from `/console/connected-apps` invalidates it on Pad’s side immediately.
- Membership changes (you’re removed from a workspace, your role drops from Editor to Viewer) take effect on the *next* tool call — there’s no waiting for a token to expire.
- Every tool call is audit-logged with `(user_id, workspace_id, tool, action, status)`. You can review your own audit log at `/console/audit-log`.

For the underlying `pad` CLI’s REST API, see REST API. For the local-machine variant — pad runs on your laptop, no account needed — see MCP — Local.
