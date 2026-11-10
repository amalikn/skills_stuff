**Title:** Pad MCP — Connect your AI agent

**Source:** [https://www.getpad.dev/mcp](https://www.getpad.dev/mcp)

---

# Page Structure Map
```text
Pad MCP — Connect your AI agent
├── Zero install
└── Run on your machine
```

---

Remote · Pad Cloud

## Zero install

Paste `https://mcp.getpad.dev` into Claude Desktop, Cursor, Windsurf, or ChatGPT. Sign in with your Pad account. Your agent reads and writes the workspaces you grant it — no local binary, no config files, no scripts.

- → OAuth 2.1 with PKCE, audience-restricted tokens
- → Per-workspace consent at sign-in
- → Revoke from `/console/connected-apps`
- → Best fit when your agent is hosted (Claude.ai web, ChatGPT, etc.)
Connect over Remote MCP →

Local · self-hosted

## Run on your machine

Run `pad mcp serve` as a subprocess of Claude Desktop, Cursor, or Windsurf. Pad's data lives in a SQLite file on your laptop. One install command per client; no account, no cloud round-trip.

- → No account, no network egress for tool calls
- → One-command install per client
- → Same v0.9 tool catalog as Remote
- → Best fit for desktop clients on a single machine
Set up Local MCP →

Not sure which? The homepage path-selector walks through Pad's three usage modes — zero install, CLI + cloud, self-host — and lands you on the right page.
