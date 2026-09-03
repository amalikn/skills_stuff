# skill-smc: Claude Code Installation Instructions

## Prerequisites

- Claude Code CLI installed and configured
- `~/.claude/skills/` directory exists (created by Claude Code on first run)

## Install Steps

### 1. Create skill directory

```bash
mkdir -p ~/.claude/skills/skill-smc/references
```

### 2. Copy SKILL.md

```bash
cp /Volumes/Data/_ai/_skills/skills_stuff/specialists/project/skill-smc/SKILL.md \
   ~/.claude/skills/skill-smc/SKILL.md
```

### 3. Copy RUNBOOK.md reference

```bash
cp /Volumes/Data/_ai/_skills/skills_stuff/specialists/project/skill-smc/RUNBOOK.md \
   ~/.claude/skills/skill-smc/references/RUNBOOK.md
```

### 4. Verify

```bash
ls -la ~/.claude/skills/skill-smc/
# Expected:
#   SKILL.md
#   references/
#     RUNBOOK.md
```

## Update (re-install from canonical source)

Re-run steps 2 and 3 to pick up changes from the canonical source.

## MCP Configuration (Phase 2 — execution layer)

After installing the skill, configure the execution layer MCPs for live troubleshooting.

### ssh-manager (live SSH)

1. Create `/Volumes/Data/_ai/_mcp/mcp-data/ssh-manager/ssh-config.toml` with SMC hosts
2. Add `SSH_CONFIG_PATH` to the `ssh-manager` entry in `~/.claude/settings.json`:
   ```json
   "ssh-manager": {
     "command": "node",
     "args": ["<path-to-ssh-mcp-server>"],
     "env": {
       "SSH_CONFIG_PATH": "/Volumes/Data/_ai/_mcp/mcp-data/ssh-manager/ssh-config.toml"
     }
   }
   ```

### mcp-grafana (Prometheus metrics — read-only)

**Read-only:** Never write, modify, or create anything in Grafana via MCP.
Use the flavor-specific instance, not `mcp-grafana` (central NOC, unrelated to SMC boxes).

1. Build binary: `cd /Volumes/Data/_ai/_mcp/mcp_stuff/mcp-grafana && go build -o dist/mcp-grafana ./cmd/mcp-grafana`
2. Copy to: `/Volumes/Data/_ai/_mcp/mcp-working-cache/mcp-grafana/mcp-grafana`
3. Add flavor-specific entries to `mcpServers` in `~/.claude/settings.json`:
   ```json
   "mcp-grafana-nbn": {
     "command": "/Volumes/Data/_ai/_mcp/mcp-working-cache/mcp-grafana/mcp-grafana",
     "env": {
       "GRAFANA_URL": "http://127.0.0.1:63000",
       "GRAFANA_SERVICE_ACCOUNT_TOKEN": ""
     }
   },
   "mcp-grafana-apn": {
     "command": "/Volumes/Data/_ai/_mcp/mcp-working-cache/mcp-grafana/mcp-grafana",
     "env": {
       "GRAFANA_URL": "http://127.0.0.1:53000",
       "GRAFANA_SERVICE_ACCOUNT_TOKEN": "<token>"
     }
   }
   ```
   Requires active Teleport SSH tunnel port-forwarding 63000 (nbn) or 53000 (apn) before use.

## Verification

After install and MCP configuration, restart Claude Code and confirm:
- `ssh_list_servers` returns `malik-rct01`
- `ssh_execute` on `malik-rct01` with `echo OK && hostname` returns `OK\nmalik-rct01`
- `query_prometheus` with `node_memory_MemAvailable_bytes` returns current metrics

## Current Install State

- Installed: 2026-04-15 (Phase 1)
- MCP wired: 2026-04-17 (Phase 2)
- Canonical version: 0.1.0
