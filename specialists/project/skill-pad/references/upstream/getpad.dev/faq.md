**Title:** FAQ

**Source:** [https://www.getpad.dev/faq](https://www.getpad.dev/faq)

---

# Page Structure Map
```text
FAQ
├── Where does my data go?
├── Does it work offline?
├── Does Pad collect telemetry or analytics?
├── How do I update?
├── Can I migrate from Linear / Notion / Jira?
├── Is Pad Cloud the same product as self-hosted Pad?
├── What's the license?
├── How do AI agents work with Pad?
└── Does Pad work in a multi-user team?
```

---

## Where does my data go?

On your machine. Self-hosted Pad stores everything in a single SQLite database at `~/.pad/pad.db`. No cloud, no sync, no telemetry, no analytics. The CLI and web UI both read from the same file.

On Pad Cloud ([app.getpad.dev](https://app.getpad.dev/)), your data lives on our managed PostgreSQL with encrypted backups. See [Privacy](https://www.getpad.dev/privacy) for details.

## Does it work offline?

Self-hosted Pad: yes, fully. The whole binary plus its embedded web UI run locally with no network dependency.

Pad Cloud: no — by definition it's a hosted service.

## Does Pad collect telemetry or analytics?

Self-hosted Pad: no. We don't phone home, don't track usage, don't send crash reports anywhere. The binary you run is the binary you can audit.

Pad Cloud (the app at `app.getpad.dev`): standard server access logs only — IP and user-agent for rate limiting and abuse detection. No third-party analytics, no advertising trackers.

Marketing site (`getpad.dev`): uses Cloudflare Web Analytics — cookieless, no fingerprinting, aggregate page-view and Core Web Vitals metrics only. See [Privacy](https://www.getpad.dev/privacy).

## How do I update?

If you installed via Homebrew:

```bash
brew upgrade PerpetualSoftware/tap/pad
```

If you downloaded a binary, grab the latest from [GitHub Releases](https://github.com/PerpetualSoftware/pad/releases).

If you built from source:

```bash
cd /path/to/pad-clone
git pull
make install
```

Database migrations run automatically on first start of the new binary — no manual migration step.

## Can I migrate from Linear / Notion / Jira?

Pad has `pad workspace import` which accepts a JSON export. Currently there are no first-party importers from other tools, but the JSON schema is documented in the [REST API reference](https://www.getpad.dev/docs/api) and the CLI has a working `workspace export` for the reverse direction.

The pragmatic path most users take: export from your existing tool to CSV, write a small script that POSTs each item to `/api/v1/workspaces/{ws}/collections/{coll}/items`, run it once, done.

## Is Pad Cloud the same product as self-hosted Pad?

Same engine, different operational model. Pad Cloud runs the same Go binary, the same SvelteKit UI, the same conventions and playbooks. The hosted version adds: managed Postgres, encrypted backups, OAuth sign-in, team billing, no operator burden.

You can self-host Pad for solo use indefinitely (LAN, Tailscale, home VPN — see [Self-Hosting](https://www.getpad.dev/docs/self-hosting)). For team setups, [Pad Cloud](https://app.getpad.dev/) is the supported path.

## What's the license?

Apache 2.0. See [LICENSE](https://github.com/PerpetualSoftware/pad/blob/main/LICENSE) on GitHub. You can use, modify, and distribute Pad freely; commercial use is allowed.

## How do AI agents work with Pad?

Pad ships with a `/pad` skill that any major AI coding agent (Claude Code, Cursor, Windsurf, Codex, OpenCode, GitHub Copilot, Amazon Q, JetBrains Junie) can install via `pad agent install`. The agent then manages your project through natural language — `/pad what should I work on next?`, `/pad I finished the auth refactor, mark it done`, etc.

See [Agent Integration](https://www.getpad.dev/docs/agent-integration) for the full setup.

## Does Pad work in a multi-user team?

On Pad Cloud, yes — that's its primary use case. On self-hosted, the binary supports multi-user via user accounts + workspace invitations + roles (owner / editor / viewer), but operating it for a team is your responsibility — backups, TLS, account recovery, capacity. Most teams find [Pad Cloud](https://app.getpad.dev/) simpler.
