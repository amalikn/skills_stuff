**Title:** MCP — Claude Desktop

**Source:** [https://www.getpad.dev/docs/mcp/claude-desktop](https://www.getpad.dev/docs/mcp/claude-desktop)

---

# Page Structure Map
```text
MCP — Claude Desktop
├── Prerequisites
├── Steps
│   ├── 1\. Open Connector settings
│   ├── 2\. Add a custom connector
│   ├── 3\. Paste the Pad MCP URL
│   ├── 4\. Sign in to Pad
│   ├── 5\. Pick which workspaces this connector can access
│   └── 6\. Verify the connection
└── What’s next
```

---

Connect Claude Desktop to your Pad Cloud workspaces. Three minutes if you already have a Pad account; five minutes from a cold start.

## Prerequisites

- A current build of Claude Desktop (any version with “Connectors” in Settings — macOS, Windows, or Linux)
- Either a Pad Cloud account at app.getpad.dev (you can also create one as part of the connect flow — keep reading)

## Steps

### 1\. Open Connector settings

In Claude Desktop, click your profile avatar in the top-right → **Settings** → **Connectors** in the left sidebar.

### 2\. Add a custom connector

Click **Add custom connector** (or “Add MCP server” in older builds — same thing). A modal opens asking for a URL.

### 3\. Paste the Pad MCP URL

```
https://mcp.getpad.dev
```

Click **Continue** (or **Add** depending on your build). Claude Desktop validates the URL by calling `/.well-known/oauth-protected-resource` against it; that takes a fraction of a second.

### 4\. Sign in to Pad

Claude opens a browser tab to Pad’s authorization page. If you’re already signed in to `app.getpad.dev`, you skip straight to the consent screen.

If you don’t have a Pad account yet, click **Don’t have an account? Sign up** on the sign-in page. The OAuth flow is preserved through registration — when you finish creating your account, you’ll land back on the consent screen automatically.

### 5\. Pick which workspaces this connector can access

The consent screen lists all workspaces you’re a member of. Tick the ones you want this Claude Desktop instance to access. There’s also an “Allow access to any workspace” option if you’d rather not have to grant new ones individually as you create them.

Pick a permission tier:

- **Read only** — list, show, search, dashboard
- **Read and write** *(default)* — create + update items, comments, links
- **Full access** — read, write, plus admin operations (workspace settings, members)

Your tier is bounded by your role in each workspace. If you’re a Viewer in `side-project`, you can read but not write there even at “Read and write” tier — Pad checks your role on every tool call.

Click **Allow access**.

### 6\. Verify the connection

Claude Desktop’s connector list should now show “Pad” with a green check. Open a new chat and try:

> Ask Claude: *“Use the Pad connector to show my project dashboard.”*

Claude should call `pad_project.action: dashboard`. The first call will prompt you to confirm Claude has access to the connector (a one-time dialog).

If you have multiple Pad workspaces granted, ask Claude to set the active one first:

> *“Set the Pad workspace to `my-project`, then show my dashboard.”*

This calls `pad_set_workspace` followed by `pad_project.action: dashboard`. After that, all subsequent tool calls in this conversation default to that workspace unless you set a different one.

## What’s next

- The full set of tools Claude can call is documented in the tool catalog.
- If something didn’t work, see troubleshooting.
- To revoke this connection later: visit `app.getpad.dev/console/connected-apps`, find Claude Desktop, click revoke. The next tool call returns 401 immediately.

← Remote MCP overview · Troubleshooting →
