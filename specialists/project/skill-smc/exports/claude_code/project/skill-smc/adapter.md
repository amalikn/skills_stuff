# skill-smc: Claude Code Adapter

## What This Exports

Maps the canonical specialist package to the Claude Code installed skill format.

## Source → Install Mapping

| Canonical source | Installed location | Notes |
|---|---|---|
| `SKILL.md` | `~/.claude/skills/skill-smc/SKILL.md` | Primary skill file; loaded as context |
| `RUNBOOK.md` | `~/.claude/skills/skill-smc/references/RUNBOOK.md` | Referenced via `references/` subdir |
| `PROFILE.md` | Not installed | Content summarised in SKILL.md and RUNBOOK.md Section 9 |
| `SYSTEM_PROMPT.md` | Not installed by default | Use when deploying as a dedicated agent |

## Skill Activation

Claude Code activates the skill via `~/.claude/skills/skill-smc/SKILL.md`.

**SKILL.md frontmatter trigger:**
```yaml
description: Use when working on ansible-wifi repo, developing or troubleshooting SMC (Site Management Controller) boxes, or investigating live SMC appliance issues.
```

The skill is auto-loaded when context matches: ansible-wifi repo, SMC troubleshooting, live appliance investigation.

## MCP Integration (Phase 2 — execution layer)

This skill pairs with two MCPs configured in `~/.claude/settings.json`:

| MCP | Role | Config |
|---|---|---|
| `ssh-manager` | SSH execution against live SMC boxes via Teleport | `SSH_CONFIG_PATH=/Volumes/Data/_ai/_mcp/mcp-data/ssh-manager/ssh-config.toml` |
| `mcp-grafana-nbn` | Prometheus metrics — nbn_accelerate, nbn_wh (read-only) | `GRAFANA_URL=http://127.0.0.1:63000` (tunnel required) |
| `mcp-grafana-apn` | Prometheus metrics — rcp, rct, wh (read-only) | `GRAFANA_URL=http://127.0.0.1:53000` (tunnel required) |

Note: `mcp-grafana` (`monitoring.apn.net.au:3000`) is central NOC Grafana — not for SMC box work.

Without these MCPs, the skill produces manual checklists. With them, Claude runs the commands directly.

## Canonical Source

`/Volumes/Data/_ai/_skills/skills_stuff/specialists/project/skill-smc/`
