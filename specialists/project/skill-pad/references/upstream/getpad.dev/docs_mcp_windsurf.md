**Title:** MCP — Windsurf

**Source:** [https://www.getpad.dev/docs/mcp/windsurf](https://www.getpad.dev/docs/mcp/windsurf)

---

# Page Structure Map
```text
MCP — Windsurf
├── Prerequisites
├── Steps
│   ├── 1\. Open MCP settings
│   ├── 2\. Pick remote server
│   ├── 3\. Paste the URL
│   ├── 4\. Sign in to Pad
│   ├── 5\. Consent
│   └── 6\. Verify
├── Notes
└── What’s next
```

---

Connect Windsurf (Codeium’s IDE) to your Pad Cloud workspaces.

## Prerequisites

- A current Windsurf release with MCP support
- A Pad Cloud account (or be ready to create one during the OAuth flow)

## Steps

### 1\. Open MCP settings

In Windsurf, open the command palette and run **“Cascade: MCP Servers”**. Or navigate to **Settings → Cascade → MCP servers** and click **Add server**.

### 2\. Pick remote server

Windsurf supports both local-subprocess and remote MCP servers. Choose **remote** (HTTP).

### 3\. Paste the URL

```
https://mcp.getpad.dev
```

Name the server `Pad`.

### 4\. Sign in to Pad

The OAuth window opens. Sign in, or click **“Don’t have an account? Sign up”** to create one without losing your in-flight OAuth flow.

### 5\. Consent

Pick the workspaces this Windsurf instance can access and the permission tier (read-only / read-write / admin). Click **Allow access**.

### 6\. Verify

In a Cascade chat, ask:

> *“Set the Pad workspace to `my-project` and run the project dashboard tool.”*

You should get back the workspace’s active items, recent activity, and suggested next task.

## Notes

Windsurf shares MCP infrastructure with Cursor and the broader Codeium product line. If you’ve already configured Pad in Cursor on the same machine, the underlying tokens are independent — connecting from Windsurf creates its own token, audit-logged separately, revocable separately from `/console/connected-apps`.

## What’s next

- Tool catalog
- Troubleshooting

← Remote MCP overview · Troubleshooting →
