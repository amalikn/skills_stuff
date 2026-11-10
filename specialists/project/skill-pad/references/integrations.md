---
Title: skill-pad reference: MCP, other clients, Pad Cloud and the official plugin
Category: reference
Status: current
Authority: canonical
Scope: How Pad reaches agents other than through this skill (local and remote MCP, client setup), and why the operator uses skill-pad instead of Pad's plugin
Last reviewed: 2026-11-10
Summary: >-
  Pad's MCP surface (local stdio and remote mcp.getpad.dev), the client install commands and their state on this Mac, self-hosting pointers, and a
  comparison of Pad's official Claude Code plugin with skill-pad, which replaced it (operator, 2026-11-10).
---

# Integrations

Sources: getpad.dev `mcp/local`, `mcp/remote`, `docs/mcp/*`, `docs/self-hosting`, `docs/claude-code`; repo `docs/mcp.md`, `plugin/`; mirrored in [upstream/](upstream/readme.md). VERIFIED_PRIMARY 2026-11-10.

## Contents

- [MCP](#mcp)
- [Pad Cloud and self-hosting](#pad-cloud-and-self-hosting)
- [Official plugin compared with skill-pad](#official-plugin-compared-with-skill-pad)

## MCP

Use MCP for a client with no shell (Claude Desktop, ChatGPT) or when the CLI is not wanted; agents with a shell use the CLI through this skill.

- **Local:** `pad mcp install claude-desktop|cursor|windsurf|claude-code|codex|--all`, restart the client. It adds a `pad` entry running `pad mcp serve` (stdio), keeps other servers and sets the
  config file to 0600. `pad mcp status` shows the state: on 2026-11-10 none of Claude Desktop, Cursor, Windsurf or Codex had it. For Claude Code, the operator's MCP entries live in `~/.claude.json`,
  not `settings.json`.
- **Remote:** `https://mcp.getpad.dev` (Pad Cloud) with OAuth sign-in; tokens are audience-restricted to `https://mcp.getpad.dev/mcp`. A self-hosted server serves Streamable HTTP at `/mcp`.
- **Surface:** 9 resource-action tools (`pad_item`, `pad_workspace`, `pad_collection`, `pad_project`, `pad_role`, `pad_search`, `pad_playbook`, `pad_library`, `pad_meta`) plus `pad_set_workspace`;
  resources such as `pad://workspaces` and `pad://workspace/<slug>/dashboard`; prompts `pad_plan`, `pad_ideate`, `pad_retro`, `pad_onboard`. A call with no workspace returns a `no_workspace` envelope
  listing `available_workspaces`: pick, call `pad_set_workspace`, retry.
- Per-client steps: [upstream/getpad.dev/](upstream/getpad.dev/) `docs_mcp_claude-desktop.md`, `_cursor`, `_windsurf`, `_chatgpt`, `docs_mcp_troubleshooting.md`.

## Pad Cloud and self-hosting

This Mac runs Pad locally (`mode = "local"`, SQLite, data in tools_stuff/pad). Pad Cloud is `app.getpad.dev`; self-hosting (Docker, Postgres, Unraid) is in `upstream/getpad.dev/docs_self-hosting*.md` and
`upstream/v0.19.2/docs_deployment.md`. Moving data: `pad workspace export` (tar.gz) and `import`, `pad db migrate-to-pg`, `pad db release-cloud`; all operator decisions.

Container image (VERIFIED_PRIMARY, GHCR package page and README v0.19.2, 2026-11-10): `ghcr.io/perpetualsoftware/pad`, multi-arch and cosign-signed;
`latest` follows each stable release (0.19.2 on 2026-11-10), so pin a bare version tag (`:0.19.2`). `docker run -p 127.0.0.1:7777:7777 -v pad-data:/data
ghcr.io/perpetualsoftware/pad`; first run prints a one-time setup URL to the log (`docker logs <c> 2>&1 | grep -A6 'Pad first-run setup'`), or
`docker exec -it <c> pad auth setup`; `PUID`/`PGID` set file ownership (defaults 99/100). Not used here: this Mac runs the Homebrew binary.

## Official plugin compared with skill-pad

Pad ships a Claude Code plugin (`/plugin marketplace add PerpetualSoftware/pad`, `/plugin install pad@pad`). The operator does not install it (operator, 2026-11-10). What it holds and where each part
lives here:

| Plugin part                                         | skill-pad equivalent                                                            |
| --------------------------------------------------- | ------------------------------------------------------------------------------- |
| `skills/pad` (conversational skill)                 | `SKILL.md` and `references/` (extracted, rewritten, plus operator rules)        |
| `skills/status`, `capture`, `onboard`               | modes in [modes.md](modes.md)                                                   |
| `skills/connect`, `disconnect` + `monitors.json`    | modes + `scripts/pad_monitor.sh` under the Monitor tool (re-armed every 30 min) |
| `scripts/pad-monitor.sh`                            | `scripts/pad_monitor.sh` (adapted, Apache-2.0, tested offline)                  |
| `hooks/activity-hooks.json` (busy/idle)             | the same two hooks in `~/.claude/settings.json`                                 |
| `/pad-pane` side panel (a mod, `hooks/register.js`) | none: use `pad server open` (web UI); a Claude Code mod could follow            |

Why: one source the operator controls, the operator's conventions and setup in the same place, the same file for Codex, and no lag: the plugin's marketplace entry was pinned to v0.18.1 while the CLI
was v0.19.2 (`.claude-plugin/marketplace.json`, 2026-11-10).
