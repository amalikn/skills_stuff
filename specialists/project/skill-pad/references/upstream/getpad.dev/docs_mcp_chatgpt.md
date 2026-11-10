**Title:** MCP — ChatGPT

**Source:** [https://www.getpad.dev/docs/mcp/chatgpt](https://www.getpad.dev/docs/mcp/chatgpt)

---

# Page Structure Map
```text
MCP — ChatGPT
├── Prerequisites
├── Steps
│   ├── 1\. Open Connector / MCP settings
│   ├── 2\. Add a custom connector
│   ├── 3\. Paste the Pad MCP URL
│   ├── 4\. Sign in to Pad
│   ├── 5\. Pick workspaces and permission tier
│   └── 6\. Verify
├── Workspace-admin caveats
└── What’s next
```

---

ChatGPT supports Pad’s remote MCP server through OpenAI’s **custom connectors / remote MCP server** feature. This page covers the connection flow.

> **Availability note.** OpenAI gates MCP connector access by ChatGPT plan and (for team accounts) workspace admin policy. If the steps below don’t match what you see in your ChatGPT settings, your account likely doesn’t have the connector feature enabled. Check OpenAI’s Connectors documentation for current eligibility and your workspace admin if you’re on a ChatGPT Team / Business / Enterprise plan.

## Prerequisites

- A ChatGPT account on a plan that includes connector / remote-MCP support
- Workspace admin permission (if your ChatGPT workspace requires admin approval for new connectors)
- A Pad Cloud account (or be willing to create one during the OAuth flow)

## Steps

### 1\. Open Connector / MCP settings

In ChatGPT, navigate to **Settings → Connectors** (or the section in your build that lists installed connectors / MCP servers — exact label may vary by ChatGPT version and plan).

### 2\. Add a custom connector

Pick **Add connector** / **Add MCP server** / **Create custom connector** depending on your build. The flow asks for a server URL and a name.

### 3\. Paste the Pad MCP URL

```
https://mcp.getpad.dev
```

Name it `Pad`.

### 4\. Sign in to Pad

A browser window opens to Pad’s authorization page. Sign in to your Pad account, or click **“Don’t have an account? Sign up”** to create one without losing your in-flight OAuth flow. New accounts get a default workspace seeded with the startup template so the consent screen has something to grant against immediately.

### 5\. Pick workspaces and permission tier

The consent screen lists your Pad workspaces. Tick the ones ChatGPT can access, pick a tier (read-only / read-write / admin). Click **Allow access**.

Tier is bounded by your role in each workspace — see the Remote MCP overview’s authentication section for the full model.

### 6\. Verify

In a new ChatGPT conversation, ask:

> *“Use the Pad connector to show my project dashboard.”*

ChatGPT calls `pad_project.action: dashboard`. The first call will prompt you to confirm the connector is allowed in this conversation.

## Workspace-admin caveats

If your ChatGPT workspace runs in admin-managed mode, custom connectors usually require admin approval before they show up in user accounts. The admin-side flow:

1. Admin opens the workspace’s connector / app management.
2. Admin pastes `https://mcp.getpad.dev` and approves the connector at the workspace level.
3. Individual users then go through steps 1–6 above; the OAuth handshake binds each user to their own Pad account, so different users on the same ChatGPT workspace can connect to different Pad workspaces.

## What’s next

- Tool catalog — every tool ChatGPT can call
- Troubleshooting — common setup errors

← Remote MCP overview · Troubleshooting →
