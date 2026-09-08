# skill-smc: Claude Code Adapter

## What This Exports

Maps the canonical specialist package to the Claude Code installed skill format.

## Source → Install Mapping

| Canonical source | Installed location | Notes |
|---|---|---|
| `SKILL.md` | `~/.claude/skills/skill-smc/SKILL.md` | Primary skill file; loaded as context |
| `RUNBOOK.md` | `~/.claude/skills/skill-smc/RUNBOOK.md` | Navigation index and reference routing |
| `references/*.md` | `~/.claude/skills/skill-smc/references/*.md` | Focused progressive-disclosure references |
| `scripts/*` | `~/.claude/skills/skill-smc/scripts/*` | Reusable diagnostic + ansible-lint gate scripts, `chmod +x` on install (see `scripts/README.md`) |
| `PROFILE.md` | Not installed | Content summarised in SKILL.md and references/01_overview.md |
| `SYSTEM_PROMPT.md` | Not installed by default | Use when deploying as a dedicated agent |
| `manifest.json` | Not installed | Consumed by skill tooling; not needed at agent runtime |
| `README.md` | Not installed | Pack orientation; canonical source only |
| `ARCHITECTURE.md` | Not installed | Pack structure doc; canonical source only |
| `AGENTS.md` | Not installed | Pack maintenance policy; not for end-users |
| `CLAUDE.md` | Not installed | Claude Code governance wrapper; pack maintenance only |
| `AI_NAVIGATION.md` | Not installed | Context router; pack maintenance only |
| `context-map.yaml` | Not installed | Machine-readable routing; pack maintenance only |
| `SCRATCHPAD.md` | Not installed | Agent working memory; pack maintenance only |
| `repomix.config.json` | Not installed | Context bundle config; pack maintenance only |
| `.archcore/` | Not installed | Durable rules, ADR, spec; canonical source only |

## Skill Activation

Claude Code activates the skill via `~/.claude/skills/skill-smc/SKILL.md`.

**SKILL.md frontmatter trigger:**
```yaml
description: Use when working on ansible-wifi repo, developing or troubleshooting SMC (Site Management Controller) boxes, or investigating live SMC appliance issues.
```

The skill is auto-loaded when context matches: ansible-wifi repo, SMC troubleshooting, live appliance investigation.

## MCP Integration (Phase 2 — execution layer)

Live SSH access uses **no MCP at all** — every SMC is reached by running `tsh ssh root@<hostname>`
directly (Bash/shell tool), with `tsh login` arranged manually by the operator against whichever
Teleport cluster matches the flavor/site (`teleport.apn.au`, `teleport.communitywifi.net.au`, and
possibly others not yet fully mapped — see `references/13_known-issues.md`). There is no
`ssh-manager` MCP, no `ssh-config.toml`, nothing to configure for SSH access.

This skill pairs with one MCP configured in `~/.claude/settings.json` for the metrics side of the execution layer:

| MCP | Role | Config |
|---|---|---|
| `mcp-grafana-nbn` | Prometheus metrics — nbn_accelerate, nbn_wh (read-only) | `GRAFANA_URL=http://127.0.0.1:63000` (tunnel required) |
| `mcp-grafana-apn` | Prometheus metrics — rcp, rct, wh (read-only) | `GRAFANA_URL=http://127.0.0.1:53000` (tunnel required) |

Note: `mcp-grafana` (`monitoring.apn.net.au:3000`) is central NOC Grafana — not for SMC box work.

Without `mcp-grafana`, Prometheus queries fall back to manual checklists; SSH access is always direct `tsh ssh`, MCP or not.

## Canonical Source

`/Volumes/Data/_ai/_skills/skills_stuff/specialists/project/skill-smc/`
