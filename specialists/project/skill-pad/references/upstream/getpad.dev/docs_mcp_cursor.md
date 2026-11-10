**Title:** MCP — Cursor

**Source:** [https://www.getpad.dev/docs/mcp/cursor](https://www.getpad.dev/docs/mcp/cursor)

---

# Page Structure Map
```text
MCP — Cursor
├── Prerequisites
├── Steps
│   ├── 1\. Open MCP settings
│   ├── 2\. Choose “Remote (Streamable HTTP)”
│   ├── 3\. Paste the Pad MCP URL
│   ├── 4\. Sign in to Pad
│   ├── 5\. Pick workspaces and permission tier
│   └── 6\. Verify
├── Pairing with the local /pad skill
└── What’s next
```

---

Connect Cursor to your Pad Cloud workspaces so the in-editor agent can read and update tasks, ideas, plans, and docs as you code.

## Prerequisites

- Cursor with MCP support (any current release)
- A Pad Cloud account (or be willing to create one during the OAuth flow)

## Steps

### 1\. Open MCP settings

In Cursor, open the command palette (⌘⇧P / Ctrl-Shift-P) and run **“MCP: Add Server”**. Or navigate to **Settings → Features → MCP servers** and click **Add server**.

### 2\. Choose “Remote (Streamable HTTP)”

Cursor supports both stdio (local subprocess) and remote (HTTP) MCP servers. Pick **Remote**.

### 3\. Paste the Pad MCP URL

```
https://mcp.getpad.dev
```

Give the connection a name — `Pad` is what we recommend so log lines and Cursor’s UI both read clearly.

### 4\. Sign in to Pad

Cursor opens an OAuth window. Sign in to your Pad account, or create one — the registration page on `app.getpad.dev` preserves your in-flight OAuth flow so you can sign up and continue the connection without restarting.

### 5\. Pick workspaces and permission tier

The consent screen lists your Pad workspaces. Tick the ones Cursor can access; pick a tier (read-only / read-write / admin). Click **Allow access**.

Tier is capped by your role in each workspace — see the Remote MCP overview for the full model.

### 6\. Verify

In a Cursor chat, ask:

> *“Set the Pad workspace to `my-project` and show me what’s on my plate.”*

The agent should call `pad_set_workspace` followed by `pad_project.action: next` and report the recommended next task.

## Pairing with the local /pad skill

Cursor reads project-local skills out of `.agents/skills/`. If you also `pad agent install cursor` from your project, the agent gets both the conversational `/pad` skill (works against any local config) AND the remote MCP connector (works against your Pad Cloud workspaces). They cooperate: the skill knows the conventions and patterns, the MCP server provides the typed tool surface.

## What’s next

- Tool catalog — every tool the agent can call
- Troubleshooting — common setup errors

← Remote MCP overview · Troubleshooting →
