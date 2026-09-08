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
cp /Volumes/Data/_ai/_skills/skills_stuff/specialists/project/skill-smc/RUNBOOK.md \
   ~/.claude/skills/skill-smc/RUNBOOK.md
```

### 3. Copy references

```bash
cp /Volumes/Data/_ai/_skills/skills_stuff/specialists/project/skill-smc/references/*.md \
   ~/.claude/skills/skill-smc/references/
```

### 4. Copy scripts

```bash
mkdir -p ~/.claude/skills/skill-smc/scripts
cp /Volumes/Data/_ai/_skills/skills_stuff/specialists/project/skill-smc/scripts/* \
   ~/.claude/skills/skill-smc/scripts/
chmod +x ~/.claude/skills/skill-smc/scripts/*.sh ~/.claude/skills/skill-smc/scripts/*.py
```

### 5. Verify

```bash
ls -la ~/.claude/skills/skill-smc/
# Expected:
#   SKILL.md
#   RUNBOOK.md
#   references/
#     01_overview.md
#     ...
#     13_known-issues.md
#   scripts/
#     README.md, collect-smc-evidence.sh, analyse-routing-drift.py,
#     analyse-topology-interface-match.py, routing-diagnostics.justfile,
#     lint-baseline-refresh.sh, ansible-lint-delta-gate.sh
```

## Update (re-install from canonical source)

Re-run steps 2 through 4 to pick up changes from the canonical source.

## Execution Layer Configuration (Phase 2)

After installing the skill, configure the execution layer for live troubleshooting.

### Live SSH access — direct `tsh ssh`, no MCP

**No `ssh-manager` (or any other SSH-wrapping) MCP is used for SMC access.** Every SMC box is
reached by running `tsh ssh root@<hostname>` directly (via the Bash/shell tool), not through an MCP
tool call. There is no `ssh-config.toml`/`SSH_CONFIG_PATH` to configure and nothing to install here.

1. The operator arranges `tsh login` manually as needed, targeting whichever Teleport cluster
   matches the flavor/site currently being worked:

   | Flavors | Teleport domain |
   |---|---|
   | `rcp`, `rct`, `wh`, `apn` | `teleport.apn.au` |
   | `nbn_accelerate`, `nbn_wh`, `cw` | `teleport.communitywifi.net.au` |

   Do not assume a single hardcoded domain — see `references/01_overview.md` "Remote Access".
2. Once `tsh login` is active for the right cluster, run commands directly:
   ```bash
   tsh ssh root@<hostname> '<command>'
   ```
3. No MCP configuration step is needed for this. If a future session considers adding an
   SSH-wrapping MCP, it would need to invoke `tsh ssh` itself (a bare host/port SSH client config
   cannot authenticate against Teleport) — but as of this pack's current state, none is in use.

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
- `tsh login` succeeds against the target cluster, then `tsh ssh root@malik-rct01 'echo OK && hostname'` returns `OK\nmalik-rct01`
- `query_prometheus` with `node_memory_MemAvailable_bytes` returns current metrics (mcp-grafana)

## Current Install State

- Installed: 2026-04-15 (Phase 1)
- MCP wired: 2026-04-17 (Phase 2)
- Canonical version: 0.1.6
