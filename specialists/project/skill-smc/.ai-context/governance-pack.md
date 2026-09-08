This file is a merged representation of a subset of the codebase, containing specifically included files, combined into a single document by Repomix.

# File Summary

## Purpose
This file contains a packed representation of a subset of the repository's contents that is considered the most important context.
It is designed to be easily consumable by AI systems for analysis, code review,
or other automated processes.

## File Format
The content is organized as follows:
1. This summary section
2. Repository information
3. Directory structure
4. Repository files (if enabled)
5. Multiple file entries, each consisting of:
  a. A header with the file path (## File: path/to/file)
  b. The full contents of the file in a code block

## Usage Guidelines
- This file should be treated as read-only. Any changes should be made to the
  original repository files, not this packed version.
- When processing this file, use the file path to distinguish
  between different files in the repository.
- Be aware that this file may contain sensitive information. Handle it with
  the same level of security as you would the original repository.

## Notes
- Some files may have been excluded based on .gitignore rules and Repomix's configuration
- Binary files are not included in this packed representation. Please refer to the Repository Structure section for a complete list of file paths, including binary files
- Only files matching these patterns are included: AGENTS.md, CLAUDE.md, AI_NAVIGATION.md, README.md, ARCHITECTURE.md, SKILL.md, RUNBOOK.md, PROFILE.md, SYSTEM_PROMPT.md, manifest.json, CHANGELOG.md, context-map.yaml, SCRATCHPAD.md, exports/**/*.md, references/**/*.md, scripts/README.md, .archcore/**/*.md, .archcore/**/*.json
- Files matching patterns in .gitignore are excluded
- Files matching default ignore patterns are excluded
- Files are sorted by Git change count (files with more changes are at the bottom)

# Directory Structure
````
.archcore/
  adr/
    adr-progressive-disclosure-structure.md
  rules/
    rule-manifest-version-discipline.md
    rule-progressive-disclosure-loading.md
    rule-reference-update-discipline.md
  specs/
    spec-specialist-pack-file-roles.md
  settings.json
exports/
  claude_code/
    project/
      skill-smc/
        adapter.md
        install.md
references/
  01_overview.md
  02_service-map.md
  03_communication-flows.md
  04_dependency-tree.md
  05_troubleshooting.md
  06_failure-modes.md
  07_hardware-overlay.md
  08_ansible-authoring.md
  09_url-capture-pcap.md
  10_captive-portal.md
  11_vagrant-lab.md
  12_content-filtering.md
  13_known-issues.md
scripts/
  README.md
AGENTS.md
AI_NAVIGATION.md
ARCHITECTURE.md
CHANGELOG.md
CLAUDE.md
context-map.yaml
manifest.json
PROFILE.md
README.md
RUNBOOK.md
SCRATCHPAD.md
SKILL.md
SYSTEM_PROMPT.md
````

# Files

## File: .archcore/adr/adr-progressive-disclosure-structure.md
````markdown
---
title: Progressive Disclosure Reference Structure
type: adr
status: proposed
date: 20260626
provenance: promoted from CHANGELOG.md v0.1.2 on 20260626
---

# ADR: Progressive Disclosure Reference Structure

## Status

Proposed (implemented as of v0.1.2)

## Context

The original skill-smc pack had a monolithic `RUNBOOK.md` containing 1724 lines across 13 major sections: overview, service map, communication flows, dependency tree, troubleshooting, failure modes, hardware/overlayroot, Ansible authoring, URL capture, captive portal, Vagrant lab, content filtering, and known issues.

Loading this file in full consumed significant context before any task-specific work could begin. A focused troubleshooting question required reading the entire service architecture section to get to the troubleshooting section.

## Decision

Split RUNBOOK.md into 13 numbered focused reference files under `references/`:

- `01_overview.md` through `13_known-issues.md`
- RUNBOOK.md replaced with a 48-line navigation index providing a task-to-reference routing table
- Files numbered to establish a progressive learning path from foundational to specialized topics

## Consequences

**Positive:**
- Agents load only the specific reference needed (e.g. `05_troubleshooting.md` for a live incident)
- Total token cost for focused tasks drops from ~1700 lines to the relevant section only
- Navigation index (RUNBOOK.md) is short enough to read as a routing step without cost

**Negative:**
- More files to maintain (13 references vs 1 monolithic file)
- Cross-reference discipline required: adding a reference file requires updating 4 surfaces
- Install step now copies a directory (`references/*.md`) rather than a single file

## Enforcement

See rules:
- `.archcore/rules/rule-progressive-disclosure-loading.md`
- `.archcore/rules/rule-reference-update-discipline.md`
````

## File: .archcore/rules/rule-manifest-version-discipline.md
````markdown
---
title: Manifest Version Discipline
type: rule
status: proposed
provenance: promoted from AGENTS.md on 20260626
---

# Rule: Manifest Version Discipline

Update `manifest.json` whenever any pack content changes:

- `version` — bump patch (e.g. `0.1.2` → `0.1.3`) for content changes; minor for structural changes
- `updated_at` — set to the current date in ISO 8601 format (`YYYY-MM-DDT00:00:00Z`)

Also update `stable_facts` if a live validation session confirms or contradicts a prior fact, and `known_constraints` if a new constraint is discovered.

Append a corresponding entry to `CHANGELOG.md`.

**Rationale:** `manifest.json` is the machine-readable specialist metadata consumed by install tooling and skill validators. A stale `updated_at` misleads automated freshness checks.
````

## File: .archcore/rules/rule-progressive-disclosure-loading.md
````markdown
---
title: Progressive Disclosure Loading
type: rule
status: proposed
provenance: promoted from AGENTS.md + AI_NAVIGATION.md on 20260626
---

# Rule: Progressive Disclosure Loading

RUNBOOK.md is a navigation index only. Do not use it as a content source.

When loading reference material for a task, load only the specific numbered reference file needed:
- Identify the task type
- Consult RUNBOOK.md routing table (or AI_NAVIGATION.md reference routing) to find the correct file
- Load only that file — do not load all 13 references up front

Loading multiple references is only justified when the task genuinely spans multiple domains (e.g. live incident involving both `05_troubleshooting.md` and `07_hardware-overlay.md`).

**Rationale:** The 13 reference files total ~1700+ lines. Loading all up front consumes context that could be used for the actual task and degrades response quality on focused questions.
````

## File: .archcore/rules/rule-reference-update-discipline.md
````markdown
---
title: Reference Update Discipline
type: rule
status: proposed
provenance: promoted from AGENTS.md on 20260626
---

# Rule: Reference Update Discipline

After editing any `references/` file, verify consistency with the index layer in the same pass:

- Check `SKILL.md` References section — description must match file content
- Check `RUNBOOK.md` routing table — task-to-file mapping must still be accurate

After **adding** a new reference file, update all four surfaces in the same commit/session:

1. `RUNBOOK.md` routing table — add row for new file
2. `SKILL.md` References section — add bullet for new file
3. `exports/claude_code/project/skill-smc/adapter.md` — add row to source→install mapping
4. `exports/claude_code/project/skill-smc/install.md` — add file to copy step

**Rationale:** The routing index (RUNBOOK.md), skill entrypoint (SKILL.md), and client adapter docs are interdependent. Updating one without the others causes navigation failures and install drift.
````

## File: .archcore/specs/spec-specialist-pack-file-roles.md
````markdown
---
title: Specialist Pack File Roles
type: spec
status: proposed
provenance: promoted from AI_NAVIGATION.md + exports/claude_code/project/skill-smc/adapter.md on 20260626
---

# Spec: Specialist Pack File Roles

Defines the role and install treatment of every file in the skill-smc specialist pack.

## File role table

| File | Role | Installed to clients? | Notes |
|---|---|---|---|
| `SKILL.md` | Agent-facing activation surface | Yes — `~/.claude/skills/skill-smc/SKILL.md` | Primary skill file loaded by Claude Code |
| `RUNBOOK.md` | Navigation index only | Yes — `~/.claude/skills/skill-smc/RUNBOOK.md` | 48-line routing table; not a content source |
| `references/01_` – `13_` | Numbered content source files | Yes — `~/.claude/skills/skill-smc/references/` | Load on demand per task |
| `manifest.json` | Machine-readable specialist metadata | No | Consumed by skill tooling; not needed at runtime |
| `PROFILE.md` | Background context; canonical source | No | Content summarised in SKILL.md and references/01_overview.md |
| `SYSTEM_PROMPT.md` | Dedicated agent mode prompt | No (default) | Use only when deploying skill-smc as a dedicated agent |
| `exports/claude_code/` | Client adapter and install docs | No | Governance only; describes what gets installed and how |
| `AGENTS.md` | Agent policy for pack maintenance | No | Governs contributors, not end-users |
| `CLAUDE.md` | Claude Code governance wrapper | No | Pack maintenance only |
| `AI_NAVIGATION.md` | Human-readable context router | No | Pack maintenance only |
| `context-map.yaml` | Machine-readable routing map | No | Pack maintenance only |
| `CHANGELOG.md` | Pack version history | No | Pack maintenance only |
| `README.md` | Pack orientation and folder index | No | Human entry point; canonical source only |
| `ARCHITECTURE.md` | Pack structure, component table, information flow | No | Canonical source only |
| `SCRATCHPAD.md` | Agent working memory for pack maintenance sessions | No | Pack maintenance only |
| `repomix.config.json` | Context bundle configuration for repomix | No | Pack maintenance only |
| `.archcore/` | Durable rules, ADR, spec for this pack | No | Canonical source only; not installed |

## Authority

`manifest.json` is the highest-authority metadata source. `SKILL.md` is the highest-authority agent-facing surface. References are content truth for their domain. No other file overrides these.

## Install surface

The Claude Code install surface is exactly:
```
~/.claude/skills/skill-smc/
├── SKILL.md
├── RUNBOOK.md
└── references/
    ├── 01_overview.md
    ├── ...
    └── 13_known-issues.md
```

All other pack files stay in the canonical source (`skills_stuff/specialists/project/skill-smc/`) and are not copied to the install surface.
````

## File: .archcore/settings.json
````json
{
  "sync": "none"
}
````

## File: exports/claude_code/project/skill-smc/adapter.md
````markdown
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
````

## File: exports/claude_code/project/skill-smc/install.md
````markdown
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
````

## File: references/01_overview.md
````markdown
# SMC Overview

## 1. What an SMC Box Is

An SMC (Site Management Controller) box is a managed Linux appliance deployed as a WiFi hotspot and network gateway. It serves WiFi clients, manages local DHCP/DNS, routes traffic, collects metrics, and optionally provides VoIP services.

### Hardware

| Platform | CPU | RAM (typical) | Storage | Notes |
|---|---|---|---|---|
| x86 PC | x86_64 | 4–16 GB (rcp/nbn_accelerate flavor) | SSD (Samsung monitored via SBDM/SMART) | Standard production |
| Raspberry Pi | ARM64 (aarch64) | 4-8 GB (rct/wh/nbn_wh flavor) | SD card / USB SSD | RCT flavor; zram swap |

**OS:** Ubuntu 20.04+ (22.04 confirmed in production)

**Time zone:** All SMC boxes use Melbourne local time regardless of flavor, location, or
operational state. Interpret local timestamps and day-boundary behavior as
Australia/Melbourne time: AEST (UTC+10) or AEDT (UTC+11) depending on daylight saving.
The `smc_ntpd` role sets this timezone for all SMC flavors; services that depend on
day boundaries should wait for NTP sync before acting on local time.

### Remote Access

All remote access routes through **Teleport** via a persistent `autossh` reverse SSH tunnel:
- SSH port on Teleport server: `50000 + site_eclipse_siteid`
  - Example: `malik-rct01` → siteid `11001` → Teleport port `61001`
- `ansible_host = {{inventory_hostname}}.teleport.<flavor>.au` — **the Teleport cluster domain is
  not a single value fleet-wide; it splits by flavor into two clusters** (operator-confirmed
  2026-07-31):

  | Flavors | Teleport domain |
  |---|---|
  | `rcp`, `rct`, `wh`, `apn` | `teleport.apn.au` |
  | `nbn_accelerate`, `nbn_wh`, `cw` | `teleport.communitywifi.net.au` |

  All 7 inventory flavors are covered by this split. The operator runs `tsh login` manually against
  whichever cluster matches the flavor/site being worked on before any `tsh ssh` session — do not
  hardcode a single domain in tooling or scripts; use this table to pick the right one instead.
- Direct SSH to port 22 is not reachable externally
- **SSH only** — Teleport DB/Kubernetes/app access features not in use
- **Access is exclusively `tsh ssh root@<hostname>` (Teleport CLI) — there is no SSH-wrapping MCP
  in use and no plain-`ssh` path to an SMC.** A `ssh root@<hostname>.teleport.<domain>` form only
  works if `tsh config` has already generated a `ProxyCommand`-wired `~/.ssh/config` entry for that
  specific cluster and `tsh login` is active; `tsh ssh` directly is the authoritative form.

### APN Cluster vs NBN Accelerate Cluster — Structural Comparison (2026-08-03)

The 7 inventory flavors split into two independently-managed Ansible clusters, not just two Teleport
domains (see "Remote Access" above). Roughly 95% of this pack's operational detail (troubleshooting,
known issues, live-validated fixes) was extracted from `rcp`/`rct`/`wh` work on the **APN cluster**.
This section documents the **NBN Accelerate cluster** (`cw` / `nbn_accelerate` / `nbn_wh`) by direct
comparison, so the two are not conflated. Both clusters follow the same **1 central-infra inventory +
N site-fleet inventories** topology, but NBN Accelerate is materially thinner and has real functional
differences beyond the SSH endpoint — do not assume "communitywifi.net.au = apn.au with a different
domain" without checking this table.

| | APN cluster (`teleport.apn.au`) | NBN Accelerate cluster (`teleport.communitywifi.net.au`) |
|---|---|---|
| Central-infra inventory | `inventories/apn/` — jenkins, prometheus_aws, teleport_aws, **graylog_servers, opensearch_servers** | `inventories/cw/` — jenkins, prometheus_aws, teleport_aws; **no graylog/opensearch host groups** |
| Site-fleet inventories | `rcp` (x86, ~10 sites, VoIP), `rct` (RPi, ~300+ sites — largest fleet in repo), `wh` (x86, ~15 sites) | `nbn_accelerate` (x86, ~20 sites), `nbn_wh` (x86, 2 real sites + 1 generic template) |
| Kernel-update pipeline | Full automated Jenkins kernel-update pipeline (`jenkins_update_kernel` batch/quarantine config) in `apn/group_vars/jenkins.yml`; per-flavor `smc_update_kernel` toggle | **Absent** — `cw/group_vars/jenkins.yml` has no kernel-update keys or toggle at all |
| Mobile app backend | Not present | `smc_bases_mobile_app` / `smc_bases_wifi_community_app_backend_git` — dedicated mobile-app backend deploy, `nbn_accelerate` only |
| Kiosk mode | Not present | `smc_dss_kiosk` toggle, `nbn_accelerate/group_vars/smc_bases.yml` |
| Teleport alert routing | Centralized in `prometheus.yml` only (noc/dev MS Teams webhooks) | Same, **plus** a separate `group_vars/teleport_monitoring.yml` (dedicated MS Teams webhook) on `nbn_accelerate`/`nbn_wh` — no apn-side equivalent file |
| Captive portal protocol | `smc_bases_portal_protocol: http` (rcp/rct/wh) | `smc_bases_portal_protocol: https` — cw-side portals are HTTPS-only |
| Blocked-URL redirect | `activ8me.net.au/blocked/wifi/` | `blocked.communitywifi.net.au` |
| VoIP (Asterisk) | `rcp` only (`inventory_dir == 'rcp'` gate) | Not present on any cw-cluster flavor |
| ClamAV + Lynis hardening | Not applied to `rcp` | Applied to `nbn_accelerate` only (`inventory_dir == 'nbn_accelerate'` gate) — genuine cw-only security-hardening difference, not hardware-driven. **Live-confirmed 2026-08-03: installed on 26/26 hosts, but `clamav-freshclam` failing on 26/26 — root cause confirmed: fleet-wide `clamav 0.103.x` is past its 2025-09-14 database-update end-of-life, CDN now hard-blocks it (HTTP 403)**, fix is a version upgrade to 1.0/1.4 LTS, not a retry. See `13_known-issues.md`. |
| `smc_ltp` sub-group | `rcp`-only static group (`inventories/rcp/prod`), 7 sites (all "low touch"-onboarded) — dual purpose: (1) CNMaestro-managed Cambium ePMP/cnPilot wireless backhaul provisioning, (2) switches DNS resolver from unbound+stubby to bind9+RPZ. See `08_ansible-authoring.md` "smc_ltp Sub-Group" | Not present — no cw-cluster equivalent |
| Hardware form-factor split | `hotspot_flavor` groups `{rct, wh, nbn_wh}` as "big box" (overlay+GPS+telemetry) and `{rcp, nbn_accelerate}` as "small box" — **this split is identical across both clusters**, not cluster-specific | (same row — the split spans both clusters) |

**Genuinely identical across both clusters:** the `all.yml`/`teleport.yml`/`prometheus.yml`/
`smc_bases.yml` variable *vocabulary* (only values differ per site), the hardware form-factor
branching (`hotspot_flavor` "small box" vs "big box" applies the same way on both sides), and the
hub-and-spoke inventory topology itself (a central-infra inventory with no `topology_vars/`, feeding
N site-fleet inventories that do have `topology_vars/`).

**Selector mechanism:** nothing in the codebase branches on the literal strings `cw`/`community`/
`communitywifi` — role-level conditionals key off `hotspot_flavor` (hardware class: small-box vs
big-box) or `inventory_dir.split('/')|last` (exact flavor name, e.g. `rcp`, `nbn_accelerate`), never
off cluster identity directly. `cw` and `apn` as group names are only used for the central-infra
plays (jenkins/teleport/graylog/prometheus controllers) — no device-level role branches on them.
When authoring a new cw-cluster-specific conditional, follow the same `inventory_dir.split('/')|last
== '<flavor>'` pattern already used for the ClamAV/Lynis and Asterisk gates — see
`08_ansible-authoring.md` "Flavor/Cluster Conditional Branching".

**Confidence / evidence basis:** structural findings from direct read of
`inventories/{apn,cw,nbn_accelerate,nbn_wh,rcp,rct,wh}/group_vars/*.yml` and `inventories/*/prod`
(2026-08-03 sweep); behavioral/conditional findings from repo-wide grep across `roles/*/tasks/
main.yml`, `roles/*/templates/*.j2`, and `smc_bases.yml` (same sweep). **Live-validated at full
fleet scale, 2026-08-03**: `tsh ssh` to all 26 reachable `nbn_accelerate` hosts plus both `nbn_wh`
hosts (28 total — not a spot-check) confirmed the Teleport domain, HTTPS-only portal, mobile-app
backend, ClamAV+Lynis presence/absence split, Asterisk absence, non-`smc_ltp` DNS stack, and a full
hardware inventory (chassis models, CPU/RAM/storage, kernel/OS versions) — see `13_known-issues.md`
"Known Operational Bugs (NBN Accelerate cluster — full fleet sweep, 2026-08-03)" and
`07_hardware-overlay.md` "NBN Accelerate / NBN WH Hardware Inventory". New findings from this sweep:
ClamAV virus definitions chronically stale fleet-wide (26/26, CDN-blocked, 10-month failure-date
spread — an ongoing degradation, not a stabilized past incident), `nbn_wh` overlayroot not yet active
(operator-confirmed as a planned-but-not-yet-executed rollout, not a bug), kernel-version drift
corroborating the no-automated-kernel-pipeline finding above, and one host (`koonibba-smc01`) at 95%
disk usage with the fleet's oldest kernel. `cw` flavor itself remains unvalidated (central-infra only,
no site-level hosts to check) and `aurukun-smc03` was unreachable at capture time. Every
troubleshooting/known-issue entry elsewhere in this pack besides the NBN Accelerate bugs section is
still an APN-cluster (`rcp`) site unless stated otherwise.

### Agentic Teleport Execution Pattern (Operational)

When using agent frameworks for SMC troubleshooting:
- Run Teleport commands (`tsh ssh`) from coordinator/main agent by default.
- Treat sub-agents as local analyzers of captured artifacts unless their own escalation/network approvals are explicitly in place.
- Persist raw outputs first (project artifact folder), then delegate parsing/summarization.
- This prevents false "stuck" states caused by sandbox DNS/approval mismatches in worker contexts.

### MCP + Skill Workflow (SMC Analysis Sessions)

For SMC disk-wear and node-audit work, use this minimum workflow:
- `skill-smc` for SMC topology/service context and disposition logic.
- `generator-and-derived-artifact-tracing` when updating generated artifacts (workbooks/scripts/docs) to keep source-of-truth aligned.
- `skill-slurp-chat` before handoff/closeout so decisions, commands, and artifacts are persisted.

MCP persistence discipline (mandatory):
- Read first, write second:
  - `memory-keeper`: `context_get(... sort=created_desc)` to find last savepoint.
  - `mcp-project-context`: `get_project_context(... section=notes, sort=created_desc)` to find latest note.
- Save only deltas/gaps (avoid duplicate notes), then checkpoint both backends.
- Channel convention for this repo: `ansible-wifi`.

Python environment for spreadsheet + workbook tasks:
- Python 3.14.4 project venv location (governed):
  - `/Volumes/Data/_ai/_project/project-working-cache/apn/smc-file-writing-analysis/.venv`
- Symlink retained for convenience at:
  - `/Volumes/Data/_ai/_project/project_stuff/apn/smc-file-writing-analysis/.venv`
- Required packages: `openpyxl`, `numpy`, `pandas`, `xlsxwriter`.

### Network Link — Satellite (Critical)

**All SMC boxes connect over satellite links:**
- Minimum RTT: ~600ms
- Average RTT: ~800ms

Operational implications:
- SSH session startup is slow — multiple Teleport handshake RTTs over satellite
- Ansible runs take significantly longer than LAN-connected hosts
- Batch commands into single SSH round-trips wherever possible (chain with `;` or `&&`)
- autossh keepalive tuning is critical — link drops are common on satellite
- Fluent Bit / Graylog log shipping subject to 800ms RTT per batch
- Prometheus remote_write and federation scrapes must tolerate high latency
- Any continuous disk writer (pcap, journal, large logs) has compounding impact since data cannot be quickly offloaded over the link

### Inventory Flavors

| Flavor | Platform | Description |
|---|---|---|
| apn | x86 | APN network hotspots |
| cw | x86 | NBN Accelerate cluster — central infra hub |
| rcp | x86 | RCP network |
| rct | ARM64 (RPi) | Raspberry Pi-based |
| wh | x86 | WH network |
| nbn_accelerate | x86 | NBN Accelerate broadband |
| nbn_wh | x86 | NBN WH |

---
````

## File: references/02_service-map.md
````markdown
# SMC Service Map

## Contents
- Core networking
- Netplan internet interface behavior
- Remote access and tunneling
- WiFi AP management
- Monitoring and metrics
- System/platform services
- Logging
- VoIP and HA services
- RCT web applications
- IoT and other services

## 2. Service Architecture Map

### Core Networking

| Service | Role | Unit | Config | Notes |
|---|---|---|---|---|
| networking | Interfaces, bridges, VLANs | systemd-networkd or ifupdown | `/etc/network/interfaces` or networkd | Configured from topology_vars |
| smc_network | Ansible role for network setup | — | topology_vars derived | Handles x86/ARM differences |
| isc-dhcp-server | DHCP server | `isc-dhcp-server` | `/etc/dhcp/dhcpd.conf` | Subnets per bridge/VLAN; generated by smc_dhcpd role |
| unbound | DHCP/LAN client DNS resolver (all flavors, non-`smc_ltp` hosts) | `unbound` | `/etc/unbound/unbound.conf` | Forwards to Stubby at `127.0.0.1@60053`; gate is `smc_ltp` group membership, **not flavor** — corrected 2026-07-03 (see below) |
| stubby | DNS-over-TLS forwarder (non-`smc_ltp` hosts) | `stubby` | `/etc/stubby/stubby.yml` | Listens on `127.0.0.1@60053` (not 5353 — that port is unbound's own listener, `smc_ltp` hosts only). Single upstream, no failover: `127.0.0.1@60853`, reached via an autossh **local port forward** (`-L 60853:127.0.0.1:853`, not a reverse tunnel) to `teleport.apn.au:853` — not a public DoT resolver |
| bind/named (`smc_dns_mgmt` role) | DNS resolver + RPZ content filter, replaces unbound entirely | `named` | `/etc/bind/` | Gated `hosts: smc_ltp` — a static group defined in `inventories/rcp/prod` (INI inventory, not topology_vars-generated), **7** `rcp` sites: `guda-guda`, `pandanus-park`, `old-looma`, `new-looma`, `warburton`, `beagle-bay`, `umoona` (all "low touch"-onboarded sites — see `08_ansible-authoring.md` "'Low Touch' Onboarding Method"). **Corrected 2026-08-03, twice same day**: first found as "only `rcp`/guda-guda" (stale `.yml`-scoped grep missing the INI-format `prod` file), then re-read directly as 4 sites, then operator confirmed the group should track every low-touch site and directed adding the 3 that were missing (`warburton`/`beagle-bay`/`umoona`) — a real inventory gap, now fixed. See `08_ansible-authoring.md` "smc_ltp Sub-Group" for the full picture including its CNMaestro-provisioning role, which this row alone does not cover. RPZ zone file is literally named `db.cambium-rpz` — ties directly to the Cambium ePMP/cnPilot backhaul gear these hosts provision |
| systemd-resolved | **Host's own** DNS resolution — a separate system from the three rows above | `systemd-resolved` | `/etc/systemd/resolved.conf` | `DNSStubListener=no` unconditional (present since the repo's first commit) — host glibc queries `external_dns_servers` (e.g. `8.8.8.8`/`8.8.4.4`) directly, bypassing both the stub *and* unbound/stubby. See `06_failure-modes.md` for a confirmed failure mode tied to this design |
| iptables | Firewall / NAT | (loaded at boot) | `/etc/iptables/rules.v4` | `MANAGEMENT` chain for access control |

**Corrected 2026-07-03** (garimba-smc01 DNS RCA): the original "unbound = RCT flavor / bind = non-RCT flavors" framing above was a generalization from the initial single-host (`malik-rct01`, RCT) validation that turned out to be wrong once checked against the full repo. The real architecture split is: **unbound+stubby serves every flavor's DHCP/LAN clients** except hosts in the `smc_ltp` inventory group (which get bind9/RPZ instead via `smc_dns_mgmt`); this is orthogonal to flavor and currently coincides with 7 `rcp` sites (`guda-guda`, `pandanus-park`, `old-looma`, `new-looma`, `warburton`, `beagle-bay`, `umoona` — corrected 2026-08-03, see the row above). Separately, **the SMC's own DNS queries never go through unbound/stubby/bind at all** — they go through `systemd-resolved`/glibc directly to the same upstream servers, because the client-facing PREROUTING DNS redirect (`roles/smc_iptables/templates/iptables.smp.j2`) is scoped to the LAN-facing bridge interface, not the host's own OUTPUT traffic. Conflating "host DNS" and "client DNS" is a common source of confusion when debugging DNS delays reported from the box itself vs. from a connected client.

**Live-verified network layout (RCT):**
- `eth1.500` → `bridge_500` (management VLAN, 10.255.0.0/24, DHCP .100-.110)
- `eth1.501` → `bridge_501` (client VLAN, 10.0.0.0/23, DHCP .10-.254)

**eth1 has no IP by design** — it is the VLAN trunk interface. IPs live only on VLANs (vlan521, vlan522) and bridges above it. This is correct even if `ip addr show eth1` shows no inet address.

### Netplan Internet Interface Behavior (Critical)

The `smc_network` role generates `/etc/netplan/00-ansible.yaml` from `roles/smc_network/templates/netplan.yml.j2`. For interfaces with `role: internet` in topology_vars, the template **only** emits:
```yaml
<interface>:
  activation-mode: manual
```
No addresses. No routes. This is intentional — internet interfaces are brought up/down by the WAN management daemon, not by systemd-networkd.

**Default route source in production:** DHCP on the physical WAN interface triggers `dhclient-enter-hooks` which puts the default route into a **per-interface routing table** (not the main table). The `add_default_gateway` override in `roles/smc_application/templates/dhclient-enter-hooks.j2` does:
```bash
ip route replace default via ${router} ... table ${interface}   # per-interface table
ip rule add from ${new_ip_address} table ${interface}           # source-based routing rule
```
No default route ever appears in the main routing table from dhclient. The Kohana gateway status app (`kohana status:gateway`) is called after each DHCP bind to update WAN state. This design enables multi-WAN load balancing on production boxes.

**Default route in Vagrant lab:** eth1 (internet-role) never gets a DHCP lease in Parallels + bridged mode due to **Parallels MAC translation**: Parallels rewrites the source MAC on bridged packets before forwarding to the physical switch. The DHCP OFFER comes back addressed to the translated MAC (`ba:53:35:65:1b:d0`) rather than eth1's real MAC — dhclient rejects the offer silently. dhclient loops DISCOVER forever with no lease.

Six-layer chain that prevents eth1 from getting an IP/route in Vagrant:
1. **Parallels MAC translation** — DHCP OFFER Client-Ethernet-Address mismatch → offer rejected
2. **`dhclient.eth1.conf` reject clause** — rejects `192.168.100.0/24` (NBN modem DHCP scope); not triggered in Vagrant but would further block if MAC issue were fixed
3. **`00-interface-activation.sh` bounce** — every networkd state change does `ip link set eth1 down; ip link set eth1 up`, wiping any manually-assigned IP
4. **`dhclient-enter-hooks` policy routing** — even with a lease, default route goes into `table eth1`, not main table; no fallback default route exists
5. **netplan `activation-mode: manual`** — systemd-networkd does not auto-configure eth1 at all
6. **eth0 default route suppression** — `vagrant-netplan.yml.j2` sets `use-routes: false` on eth0; Vagrantfile deletes eth0 default route on every boot — leaves box with no default route

**Vagrant lab fix (simplest):** Remove the `ip route del` provision from the Vagrantfile. eth0 (Parallels NAT) provides internet access. Teleport connects. Ansible can deploy over eth0. The route suppression was intended to force traffic out eth1 but is broken in Parallels bridged mode by design — MAC translation is not fixable from the guest side.

### Remote Access / Tunneling

| Service | Role | Unit | Config | Notes |
|---|---|---|---|---|
| teleport | Teleport node agent | `teleport` | `/etc/teleport.yaml` | Registers box as a Teleport node |
| autossh-teleport-openssh | Persistent reverse SSH tunnel | `autossh-teleport-openssh` | systemd drop-in | Port = 50000 + site_eclipse_siteid |
| autossh-prometheus-federation | Prometheus federation tunnel | `autossh-prometheus-federation` | systemd drop-in | Tunnels metrics to central Prometheus |
| ssh | SSHD | `ssh` | `/etc/ssh/sshd_config` | Local port 22 |

### WiFi AP Management

| Service | Role | Unit | Config | Notes |
|---|---|---|---|---|
| hostapd | WiFi AP daemon | `hostapd` | `/etc/hostapd/` | One instance per radio |
| cnmaestro-provisioning | WiFi AP provisioning | `cnmaestro-provisioning` | `/usr/local/etc/cnmaestro-provisioning/` | Talks to CNMaestro cloud API; uses Redis |
| redis | Key-value store for provisioning | `redis-server` | `/etc/redis/redis.conf` | Required by cnmaestro-provisioning |

### Monitoring / Metrics

| Service | Role | Unit | Config | Notes |
|---|---|---|---|---|
| node_exporter | Prometheus system metrics | `node_exporter` | systemd / textfile collector dir | Exposes `/metrics`; textfile at `/var/lib/node_exporter/textfile_collector/` |
| prometheus | Local Prometheus (scrapes node_exporter, speedtest) | `prometheus` | `/etc/prometheus/` | `remote_write` configured; scraped by central via federation tunnel |
| speedtest-exporter | Ookla speed test metrics | `speedtest-exporter` | systemd | Interval: 1h; writes to textfile collector |
| iperf-* | Network perf test servers | `iperf-55200` … `iperf-55209` | systemd (10 instances) | TCP ports 55200–55209 |

**Textfile collectors (staleness limits):**

| Script | Output file | Max staleness |
|---|---|---|
| `sbdm.py` | `sbdm.prom` | 5400s (90min) |
| `smartmon.py` | `smartmon.prom` | 5400s (90min) |
| `interfacecheckv2.sh` | `my_node_interfacecheck_success.prom` | 450s (7.5min) |
| `apt_info.py` | `apt_info.prom` | 450s (7.5min) |
| `rise_healthcheck.py` | (RISE systemd service, `rise-healthcheck.timer`) | — |
| `rise_overlay_metrics.sh` | overlay metrics | — |
| `rise_zram_metrics.sh` | zram metrics (`rct`/`wh` only) | — |
| `rise_watchdog.py` | watchdog metrics | — |

**RISE Health/Watchdog Framework (metric names confirmed via `mcp-grafana-apn` dashboard queries, 2026-08-03).** RISE is deployed **only** to `rct`/`wh` flavors — confirmed both by the `flavor=~"rct|wh"` gate in the "RISE SMC Table" → Pending sites query, and by the total absence of any RISE dashboard on `mcp-grafana-nbn` (nbn_accelerate/nbn_wh run no RISE metrics at all). Do not expect these series on `rcp` or NBN Accelerate hosts.

| Metric | Source script | Meaning |
|---|---|---|
| `rise_healthcheck_health_score_overall` | `rise_healthcheck.py` | Composite 0–100 health score |
| `rise_healthcheck_health_score_cpu` / `_memory` / `_disk` / `_zram` | `rise_healthcheck.py` | Per-domain subscores feeding the overall score |
| `rise_healthcheck_health_penalty_total`, `rise_healthcheck_health_penalty{penalty=...}` | `rise_healthcheck.py` | Aggregate and per-reason penalty deductions |
| `rise_healthcheck_thermal_throttling`, `rise_healthcheck_temperature_celsius_cpu` | `rise_healthcheck.py` | Thermal state and CPU temp |
| `rise_healthcheck_cpu_cores`, `rise_healthcheck_resource_usage_pct_cpu`/`_memory`, `rise_healthcheck_load_average_1m`, `rise_healthcheck_iowait_pct` | `rise_healthcheck.py` | Raw vitals backing the subscores |
| `rise_overlay_used_pct`, `rise_overlay_inodes_free_pct`, `rise_overlay_active` | `rise_overlay_metrics.sh` | Overlayroot tmpfs usage/inode headroom; `_active` is the collector's own up/down flag |
| `rise_zram_active`, `rise_zram_failed_reads_total`, `rise_zram_failed_writes_total`, `rise_zram_invalid_io_total` | `rise_zram_metrics.sh` | zram device health (`rct`/`wh` only, per existing zram-is-RCT-flavor note above) |
| `rise_watchdog_up`, `rise_watchdog_active`, `rise_watchdog_boot_firmware_used_pct`, `rise_watchdog_unit_active{unit=...}` | `rise_watchdog.py` | Collector liveness (`_up`/`_active`), boot-partition usage, and per-systemd-unit active state (e.g. `unit="rise-healthcheck.timer"`) |

Fleet-wide rollup lives on the "RISE SMC Table" Grafana dashboard (`mcp-grafana-apn`, uid `e3c73c2a-351f-4734-b6f9-3eed971ceaa9`): a host counts as **offline** when `rise_watchdog_up` was seen in the last 30 days but not in the last 5 minutes, and as **pending** (RISE not yet deployed) when `node_exporter` is up on an `rct`/`wh` host but no `rise_watchdog_up` series exists for it at all — i.e. pending vs. offline is distinguished by whether the watchdog series has ever existed, not just whether it's currently reporting.

### System / Platform

| Service | Role | Unit | Config | Notes |
|---|---|---|---|---|
| chrony | NTP time sync | `chrony` | `/etc/chrony.conf` | |
| overlayroot | tmpfs overlay filesystem | (kernel) | `/etc/overlayroot.conf` | Critical — see Section 8 |
| zram | Compressed swap (RCT only) | (kernel) | `/etc/default/zramswap` | `/dev/zram0` ~1.2 GB on 1.9 GB RAM box |
| postfix | Mail relay (outbound) | `postfix` | `/etc/postfix/` | |
| rsyslog | Log shipping | `rsyslog` | `/etc/rsyslog.conf` | Ships to Graylog (when server configured) |
| clamav-daemon | Antivirus | `clamav-daemon` | `/etc/clamav/` | |

### Logging

| Service | Role | Unit | Config | Notes |
|---|---|---|---|---|
| graylog-sidecar | Log shipper agent | `graylog-sidecar` | `/etc/graylog/sidecar/sidecar.yml` | `server_url` must be set; empty in bare Vagrant env — expected |

### VoIP (non-RCT flavors)

| Service | Role | Unit | Config | Notes |
|---|---|---|---|---|
| asterisk | VoIP/PBX (built from source) | `asterisk` | `/etc/asterisk/` | Extensions at `extensions.conf` (generated by smc_asterisk role) |

### HA / Failover (non-RCT flavors)

| Service | Role | Unit | Config | Notes |
|---|---|---|---|---|
| keepalived | VRRP HA (built from source) | `keepalived` | `/etc/keepalived/` | VIP assignment; conntrack monitoring |

### Web Applications (RCT-specific)

| App | Stack | Path | Notes |
|---|---|---|---|
| Kohana wifi app | PHP / Kohana | `/var/www/html/wifi` | Served by Apache |
| Tstik | PHP / Laravel/Artisan | `/var/www/html/rct-tstik` | RCT-specific management interface |
| apache2 | Web server | `apache2` | `/etc/apache2/` | Serves both apps |

### IoT / Other

| Service | Role | Unit | Config | Notes |
|---|---|---|---|---|
| mosquitto | MQTT broker | `mosquitto` | `/etc/mosquitto/` | IoT device telemetry |

---
````

## File: references/03_communication-flows.md
````markdown
# SMC Communication Flows

## 3. Communication Flows

### All Inbound Access

```
External / Management
    │
    ▼
Teleport proxy (teleport.<flavor>.au)
    │
    ▼  [via autossh reverse SSH tunnel]
SMC box — port 22 (SSH)
    │
    ├── Human operators (tsh ssh / ansible)
    ├── Jenkins CI (Ansible playbook runs)
    └── Prometheus central (scrape via federation tunnel)
```

### Outbound from SMC Box

```
autossh-teleport-openssh → teleport.<flavor>.au   (persistent, always on)
autossh-prometheus-federation → central Prometheus (metrics federation)
prometheus (local) → remote_write endpoint
speedtest-exporter → Ookla speed test servers      (every 1h)
cnmaestro-provisioning → CNMaestro cloud API       (WiFi AP provisioning)
rsyslog → Graylog UDP syslog                       (log shipping, when configured)
graylog-sidecar + fluent-bit → gl.aws.apn.au:443   (structured HTTPS GELF; X-GELF-Token header)
postfix → mail relay
NBN Accelerate API                                  (broadband management, nbn_accelerate flavor)
```

### Fluent Bit / Graylog Sidecar Config Architecture

Graylog Sidecar manages Fluent Bit config dynamically. `/etc/fluent-bit/fluent-bit.conf` is a placeholder only. Live config is stored under a hash-named subdirectory:

```
/var/lib/graylog-sidecar/generated/<collector-hash>/apn-gelf-http.conf
```

Inspect live tailed paths:
```bash
ls /var/lib/graylog-sidecar/generated/          # shows hash dir name
find /var/lib/graylog-sidecar/generated/ -type f -exec grep -h "^\[INPUT\]" -A5 {} \;
```

**Output endpoint is port 443 HTTPS, not UDP 9000.** Do not use `nc -zw3 gl.aws.apn.au 9000` to check connectivity — it will always fail. Correct check:
```bash
nc -zw3 gl.aws.apn.au 443 && echo GL_OK || echo GL_FAIL
```

**Fluent Bit reads NO journald directly.** All inputs are `tail`-based file readers. As of 2026-06-30 (verified on tjuntjuntjara-smc01), the 9 inputs are:

| Tag | Path |
|---|---|
| syslog | `/var/log/syslog` |
| misclog | `/var/log/auth.log`, `kern.log`, `mail.log`, `daemon.log`, `dpkg.log` |
| apache | `/var/log/apache2/*.log` |
| squid | `/var/log/squid/*.log`, `/var/log/squidguard/*.log` |
| apt | `/var/log/apt/*.log` |
| interfacecheck | `/var/log/interfacecheck.log` |
| sidecar | `/run/graylog-sidecar/sidecar.log` |
| fluent-bit | `/var/log/fluent-bit/fluent-bit.log` |
| unattended-upgrades | `/var/log/unattended-upgrades/*.log` |

**journald → rsyslog path:** `ForwardToSyslog` is commented out (system default = no on Ubuntu 22.04). rsyslog reads journald via `imjournal` module, writing `/var/log/syslog` and facility files —
which Fluent Bit then tails. Setting `Storage=volatile` on journald does not break this pipeline since `imjournal` reads from `/run/log/journal/` (the volatile RAM location).

**Future improvement:** Adding `[INPUT] Name systemd` to the sidecar collector config and removing `syslog` + `misclog` tail inputs would give structured journald fields in Graylog and decouple Fluent
Bit from rsyslog files, enabling rsyslog write reduction independently.

**The live config is downloaded from the CENTRAL Graylog server, not from the box or the ansible role (critical — found 2026-07-23).** `sidecar.yml` sets `server_url: https://gl.aws.apn.au/api/` and
the sidecar polls every 10s, downloading its assigned Collector Configuration and regenerating the hash-dir file. So:
- **A local edit to `/var/lib/graylog-sidecar/generated/<hash>/*.conf` is reverted within 10s** — never fix the pipeline by editing the box.
- The ansible role file `roles/smc_graylog/files/apn-fluentbit-config-file` is a **reference copy only** — it is **NOT auto-deployed to Graylog**. It must be **manually applied** to the Graylog
  server-side Configuration. This is a real drift trap (see smcgroup gap below).
- All 50 SMC sidecars (every flavor) share **one** config: `68a08bfc1a864a6164886a2c` (`apn-gelf-http-configuration`). A test copy exists: `68a3b61c…` (`apn-gelf-http-test-configuration`).

**smcgroup shipping gap (canary log-loss, found + RESOLVED 2026-07-23):** the `smc_rsyslog` log-group split (canary on tjuntjuntjara only) `stop`s (MOVES) wifi/dhcp/system programs out of
`/var/log/syslog` into `/var/log/smc-groups/*.log`, but the `smcgroup` `[INPUT]` tailing those files existed **only in the ansible reference file, not in the live Graylog config** — so from
~2026-07-20 the diverted programs (`dhcpd`/`dhclient`/`nl80211`/`netifd`/exact-`systemd`/`hostapd`/`cnmaestro-provisioning`/`WIFI-4-CLIENT-*`…) **stopped reaching Graylog entirely** (`dhcpd`=0 in the
shipped syslog, all in the unshipped `dhcp.log`). `WIFI-6-CLIENT-*` is NOT diverted, so general wifi data still appeared — masking the gap. **RESOLVED 2026-07-23:** the `smcgroup` `[INPUT]` +
`rewrite_tag` `[FILTER]` (→ `smcgroup.wifi/.dhcp/.system`) were added to Graylog config `68a08bfc…` (UI paste). Verified: Graylog now receives `_tag:smcgroup*` (dhcpd back as `smcgroup.dhcp`).
**Fleet-safe:** the shared-config input is a no-op on non-split nodes (glob matches nothing → 0 records, no error — confirmed live on mornington). Naturally RCP-only because the files only exist where
the RCP-flavor split runs. **Standing note: `apn-fluentbit-config-file` changes must be MANUALLY re-applied to config `68a08bfc…` — there is no sync automation.**

**Consolidating /var/log writers onto the smc-groups tmpfs + rotation rules (2026-07-23, deployed fleet-wide 15/16 that evening — new-looma pending).** Beyond the rsyslog-split families, the other
residual SSD log-writers (squid `access.log`/`cache.log`, `interfacecheck.log`, and — added the same evening — mosquitto `mosquitto.log`) were moved onto the same tmpfs by **symlinking their paths**
into `/var/log/smc-groups/` (squid/mosquitto: `stop → rm dir → symlink → start`, to dodge the FD-shadow trap — mosquitto holds its log file open continuously same as squid, confirmed via `lsof`;
interfacecheck: plain file symlink). squid and interfacecheck kept their **existing** Fluent Bit inputs/tags (`squid`/`interfacecheck`); **mosquitto had NO existing input at all — it was not shipping
to Graylog before this** (confirmed live), so a new own-tag `mosquitto` input was added at the same time, closing a long-pending disposition rather than being a relocation of something already
shipping. All three keep their own tag rather than riding `smcgroup.*` for two reasons: their native log formats would misparse under `smcgroup`'s `syslog-rfc3164` parser, and `smcgroup`'s input globs
`/var/log/smc-groups/*.log` non-recursively so it would never match a subdirectory anyway. The tmpfs was bumped 64M→128M→**256M** (dir 0755 so `proxy`/`mosquitto` can traverse into their own subdirs)
— the 256M bump was a deliberate flood-headroom decision for heavy-squid/AP-flood-prone nodes (horn-island, mornington): a tmpfs `size=` is a ceiling not a preallocation, so raising it costs ~0 RAM at
steady state. Durable rotation rules for any tmpfs-backed log dir:
- **Fluent Bit `tail` is read-only — it NEVER deletes/truncates.** On a tmpfs, logrotate + the size cap are the *only* reclaim. So every relocated log needs a size-bounded logrotate.
- **No `delaycompress` on tmpfs** — it keeps an uncompressed ~20M `.1` per busy file (~doubles footprint); rsyslog/squid/mosquitto reopen via postrotate so nothing writes `.1` after rotation. Use
  `size 20M` + `rotate 4` + `compress`. squid and mosquitto each keep their own logrotate (glob `*.log` doesn't reach a subdirectory) — role-managed, `maxsize 20M` added to each.
- **A daily-only logrotate.timer means `size` triggers are checked once/day, not continuously** — found via mosquitto's own stock package fragment (`size 100k daily`), which never actually bounded it
  in practice: `logrotate.timer` is `OnCalendar=daily` fleet-wide (confirmed live, plus the `cron.daily` fallback), so a file can grow well past its "size" trigger between daily checks (mosquitto
  reached 4.5M on the heaviest node vs a 100k target). The same latent limitation likely applies to `smc-log-groups.logrotate`'s own `size 20M` trigger during a real burst — not yet independently
  verified, worth a follow-up check.
- **`Rotate_Wait` is a seconds-scale drain window, NOT an outage buffer** — set it small (30s). A long value pins the *unlinked-but-open* rotated inode's RAM on the tmpfs for that whole duration (an
  unlinked file still occupies space until the FD closes). Outage resilience is the fbpos 256M buffer instead: once FB reads a line it lives there independent of the source file.
- **Only tmpfs *log* dirs need logrotate.** `/tmp`, Prometheus-TSDB, textfile-collector, and fluent-bit-pos are self-bounding (retention / overwrite / SQLite autocheckpoint) — running logrotate
  against the TSDB or the pos SQLite DBs would corrupt them.

Implemented in `smc_rsyslog` (ansible-wifi commit `594653b` + a same-day mosquitto follow-up): tmpfs resize + squid/interfacecheck/mosquitto relocation + `smc-log-groups.logrotate` (size-based) +
role-managed `squid.logrotate`/`mosquitto.logrotate`; `Rotate_Wait 30` on all 4 tmpfs-tailed inputs (reference config + applied to Graylog `68a08bfc` for both the smcgroup and mosquitto inputs).
**Deployed fleet-wide** — squid/ interfacecheck on 15/16 (new-looma pending), mosquitto on 14/15 (also n/a on tjuntjuntjara — confirmed no `mosquitto.service` there). Both deploys hit and recovered
from transient tooling incidents unrelated to the SMC side: an ansible interrupted-handler trap (config deployed but rsyslog never restarted, so the split looked present but was inactive — caught by a
post-deploy fatrace audit, not by `changed=0`) and a Homebrew `ansible` auto-upgrade mid-run (Cellar dir removed while a process still had imports open — just retry).

**Shared-config flavor gating — FreeMarker `<#if>`, NOT Go-template (2026-07-23 incident).** The central config `68a08bfc` is pulled by **~300 sidecars of every flavor** (rcp/rct/wh), so any
flavor-specific tail INPUT must be gated or it errors continuously on flavors that lack the path — a real-disk `fluent-bit.log` error loop, the exact write class this project targets. This bit us both
directions: the mosquitto INPUT (rcp-only) errored on all rct/wh; the `rise_logs`/`rise_status` INPUTs (rct/wh-only) error on all rcp (making `fluent-bit` the #1 real-disk writer on 11/15 rcp nodes).
Gating mechanism, version-confirmed on the deployed **Graylog server 6.3.1 / Sidecar 1.5.1 / Fluent Bit 4.0.7**:
- **Graylog Sidecar templating is FreeMarker**, per the server's own in-app docs — `<#if sidecar.tags.<tag>??> … </#if>`, existence-tested with `??` on `sidecar.tags.<tag>`. **NOT** Go-template `{{ if
  in "x" .tags }}` (wrong engine — renders as literal text, then Fluent Bit rejects it: "indentation level is too low"; sidecars keep their last-good config so it's not an outage, but the config can't
  update until fixed).
- Flavor tags come from the sidecar's `sidecar.yml` `tags:` list. rcp nodes are tagged `rcp` via `smc_graylog.yml`'s `graylog_sidecar_extra_tags: ["{{ inventory_dir.split('/')|last }}"]`; rct/wh
  already carry a `rise` tag. Gate rcp-only inputs on `<#if sidecar.tags.rcp??>`, RISE inputs on `<#if sidecar.tags.rise??>`.
- **`record_modifier` multi-word values MUST be quoted.** Fluent Bit's `Record` is `FLB_CONFIG_MAP_SLIST_2` (exactly KEY + one VALUE token); `Record log RISE status update` (4 tokens) is **silently
  dropped** — the field is never added, config still validates + starts. Use `Record log "RISE status update"`. This is why `rise.status` (which uses `parser json`, dropping the default `log` field)
  needs a quoted `log` record_modifier to satisfy the GELF encoder's `gelf_short_message_key log` (else "missing short_message key").
- **Guardrails (project tooling):** `just graylog-config-lint` (read-only lint of the live config for all three of the above failure modes) and `just sidecar-health` (fleet probe: sidecar state,
  config-validation, recent fb errors, unrendered-literal count, tag/gating). Run both after ANY `68a08bfc` edit.
- **General rule reinforced:** never guess syntax for a shared/production system — verify against the docs or source for the *exact deployed version* (all three errors above "validated" but silently
  didn't work).

**Graylog REST API access (read-only inspection):** reach it via the `apn-graylog` **Teleport app** (`tsh apps login apn-graylog`, mTLS) — the endpoint 302-redirects to Teleport login otherwise. Auth
is a **Graylog API token** as basic auth `<token>:token` (the on-box `admin:admin` and the GELF `X-GELF-Token` and the SSM `/apn-graylog/access-token` all do NOT work for the API — the working token
is stored per-project, e.g. `smc-file-writing-analysis/.graylog-token`, gitignored). Convenience recipes: `just graylog-configs`, `just graylog-check-smcgroup`, `just graylog-config <id>`, `just
graylog-api <path>`. `apn-graylog01` is the server host (`tsh ssh`), API on `localhost:9000`.

**Teleport / tsh scope:** SSH access + the `apn-graylog` **app** (Graylog API via `tsh apps login`). DB/Kubernetes access not in use.

### WAN Uplink Addressing and Default-Route Programming

Established 2026-07-29 from ansible-wifi source during the APN routing-issue investigation (`local-knowledge-ansible/ansible-wifi/issues/apn/routing-issue/`). All source-verified unless marked
otherwise. **Not yet confirmed on a live box.**

> **The `internet` / `starlink` role labels mean the opposite of what they say (operator-confirmed 2026-07-29).** Originally `internet` = Skymuster Plus primaries (the nbn satellite product; note the
> spelling — **Skymuster**, not "Skymaster") and `starlink` = Starlink backup, which is what the `internetNN` / `starlinkNN` interface keys encode. Starlink was later promoted to primary and simply
> inherited the existing `internet` label; the `starlink` label stayed on what is now the **single SMP backup link per site — `vlan621`**, with `vlan631` as its switch02 counterpart. Nothing was
> renamed, and no `provider`/`description` field exists anywhere in `topology_vars` to record it. Read every `role:` value, interface key and template comment mentioning "starlink" with this inversion
> in mind. A label retrofit is planned but **has not happened** — do not assume it has.

**Second confirmed instance, and a concrete retrofit proposal — 2026-07-31 (operator discussion with Sandro, `local-knowledge-ansible/ansible-wifi/issues/internet-link-handling/`).** Pia Wadjari is a
second live case of the same inversion, deploying with the roles reversed from Horn Island: active links are Starlink (label `internet`), backup links are SkyMuster Plus (label `starlink`). Agreed
with Sandro: the deployment proceeds as scheduled — this is a labeling/monitoring-clarity issue, not a functional one, confirmed against the live mechanism (see "The decisive behaviour is the
enter-hook override" below — `dhclient-enter-hooks.j2`'s per-interface-table vs. main-table-metric split operates on `role:`, not on provider identity, so it works correctly regardless of which
provider sits in which role).

**Proposed fix (design only, not agreed with the wider team, not implemented):** relabel by role rather than provider — e.g. `active-internet` / `standby-internet` — and add explicit per-link
metadata (`provider:`, `link_type:` e.g. satellite/fibre/fixed-wireless, plus any other operationally useful attributes) as separate `topology_vars` fields, rather than encoding provider identity
into the label itself. Must stay backward-compatible with already-deployed sites' current monitoring (no forced redeploy as a precondition); new deployments would follow the revised convention once
agreed. Estimated 2-3 weeks design+testing+implementation once the team agrees. A separate, not-yet-actioned process-improvement ask came out of the same discussion: better version control,
diffable change communication, and formal stakeholder sign-off for deployment-specific decisions like this one — organizational, not technical, tracked in the source workspace only. Full detail:
`local-knowledge-ansible/ansible-wifi/issues/internet-link-handling/internet-link-labeling-and-metadata-convention-20260731_1241.md` (analysis, code-verified) and
`internet-link-labeling-and-metadata-prompt-20260731_1244.md` (verbatim source).

**Site VLAN scheme** (rcp, repo-verified): `internetNN` keys alternate across two switch uplinks — `52x` VLANs on `switch01`, `53x` on `switch02` — and `starlink01`/`02` are `vlan621` (switch01) and
`vlan631` (switch02). Two pairing conventions exist: same-index (521↔531) at old-looma, new-looma, beagle-bay, warburton, horn-island; offset-by-one (521↔532, 523↔534, …) at umoona, pandanus-park,
mornington. Useful when judging whether an unexpected VLAN is a new uplink or a typo.

- **Every rcp site is wired with both VLAN blocks, but switch02 (`53x`) is cold standby by design at every site except Horn Island.** *(live-verified 2026-07-29, Grafana `rate()` on
  `node_network_receive_bytes_total`, all seven sites)* Horn Island is the transition site — built at the point the fleet moved from two switches to one, with too many Starlink services to fit on a
  single switch, so it's the only site actually using both. Every site built after it (all six others) shows exactly **0 bps** on every `53x` VLAN, live, right now — netplan/the hook still define
  those VLANs (so they count toward a "missing N" hook-coverage gap), but nothing is physically plugged into switch02 there. **Do not size customer impact directly from a hook-coverage gap without
  splitting switch01 from switch02 first** — on the four sites checked during the 2026-07-29 routing investigation, roughly half of each site's "missing" count was switch02, cold and harmless;
  only the switch01 half was costing anything. A second refinement on the switch01 half itself: `ip -br link` showing an interface `UP` does not mean it's **leased** — `ip -br addr` (a real CGNAT
  address present) is what distinguishes a genuine orphaned uplink (costing bandwidth right now) from an empty, never-provisioned slot (present in netplan, no dish behind it yet, costing nothing).
  **Caveat:** this assumes switch02 stays unplugged — if it's ever wired up at a site whose `dhclient-enter-hooks` case list is stale, the hook's ignorance of those VLANs reproduces the exact same
  stray-route/missing-route symptom the moment they go live.
- **`LAN1`/`LAN2` (Testra-managed, residential-plan Starlink, 50 Mbps unlimited) are a separate uplink pair, outside the `Swp1/9`–`1/18` VLAN scheme entirely and not yet correlated to any
  `topology_vars` interface key.** *(operator-reported provisioning table, 2026-07-29)* Present at six of seven sites (two lines each); Horn Island has only `LAN1`. Distinct from the direct-Starlink
  enterprise-plan VLANs (`521`–`52N`/`531`–`53N`, 2 TB cap) this section otherwise describes — if a site-specific WAN count doesn't add up against `topology_vars`, check whether `LAN1`/`LAN2` are
  the unaccounted-for difference before assuming a topology drift.

WAN interfaces are *not* managed by systemd-networkd. `netplan.yml.j2` renders every interface with `role: internet` or `role: starlink` as `activation-mode: manual` with **no `dhcp4` key**;
`00-interface-activation.sh.j2` brings them up, and a per-interface `dhclient@<iface>.service` does DHCP using `ubuntu-dhclient-script.j2` (an APN fork of the CentOS dhclient script).

**The decisive behaviour is the enter-hook override.** `ubuntu-dhclient-script.j2`'s `add_default_gateway()` is replaced at runtime by `/etc/dhcp/dhclient-enter-hooks`, generated from
`roles/smc_application/templates/dhclient-enter-hooks.j2`. That hook's `case` list is built at template-render time from **`role == 'internet'` only** — `starlink` is deliberately excluded — and it
has two branches:

| | Matched (`role: internet`) | Fallback (`*)`) |
|---|---|---|
| Default route lands in | per-interface table named after the interface | **main table** |
| Source policy routing | `ip rule from <lease-ip> table <iface>` | none |
| Metric | from DHCP (normally none) | **100** |
| Registers with portal app | yes — `cd /var/www/html/wifi && kohana status:gateway` | no |
| Visible in `ip route show` | no | **yes** |

Consequences worth knowing before diagnosing any WAN routing question:

- **`ip route show` is not the whole picture.** Healthy `role: internet` uplinks do not appear in the main table at all. Check `ip rule show` and `ip route show table <iface>`.
- **A stray `default via <gw> dev <iface> metric 100` in the main table means that interface is missing from the generated case list** — it is being given backup-link treatment. The fallback itself is
  not a bug (metric 100 loses to the metric-0 ECMP pool, which is correct for the SMP backup on `vlan621`), but a *primary* WAN VLAN landing there is silent misconfiguration: no per-interface table,
  no source rule, no registration with the portal app, and — because the primaries are Starlink — **an installed, leased, healthy dish carrying no traffic at all** while the pool is up. It also
  degrades failover, since the `*)` branch is meant to hold exactly one link. Nothing logs this and no monitoring distinguishes "in the pool" from "parked at metric 100".
- **The one-line triage: does the hook's case list cover every uplink VLAN in netplan?** *(live-verified 2026-07-29 across seven `rcp` sites — 7/7 accurate, no exceptions.)* A site is healthy
  **exactly** when it does, excluding `vlan621`/`vlan631` which are *meant* to be absent. Compare the `case` arm in `/etc/dhcp/dhclient-enter-hooks` against `vlanNNN:` keys in `/etc/netplan/*.yaml`.
  Any VLAN in netplan and not in the hook is a confirmed orphan. This is faster and more reliable than reading routes, because it names the *cause* rather than one of its symptoms.
- **The `*)` branch is first-come, so the number of stray routes tells you nothing about how many interfaces are affected.** It runs `ip -4 route add default …`, which only succeeds when the main
  table has no default. The first orphan to obtain a lease installs the `metric 100` route; every later orphan installs **nothing at all** and is invisible in `ip route show`. One site observed with
  three orphaned uplinks showed a single stray route. **Never size the impact from the route table** — count the gap between the hook list and netplan instead.
- **Confirmation that the fallback is the backup path, not a bug:** a healthy site was observed carrying `default via … dev vlan621 metric 100` — the SMP backup, exactly where the `*)` branch is
  supposed to put it. Absence of that route on other healthy sites means their backup is not leasing, which is its own failover finding.
- **The three network-touching roles can disagree, and which one is stale is diagnostic.** `smc_network` writes netplan, `smc_iptables` writes the NAT masquerade set, `smc_application` writes the
  hook. On every affected site observed, the first two agreed with each other on a newer topology and only `smc_application` lagged — which narrows remediation to one role. Cross-check with `iptables
  -t nat -S | grep POSTROUTING` (masquerade covers every uplink `smc_iptables` believes in).
- **`iptables -S` shows only the `filter` table.** `smc_iptables` templates declare `*filter`, `*mangle` and `*nat`. Use `iptables-save`. For the record, `mangle` on these boxes holds only
  `connmark`-based session accounting on `bridge_501` (`COUNT*`, `MARK_SESSION`, `ECLIPSE_*` chains) for portal quota — **there is no `fwmark` policy routing**, so neither `nat` nor `mangle`
  participates in uplink selection. That is decided entirely by the hook, the per-interface tables and the `ip rule` set.
- **The `smc_application` override is `/etc/dhcp/dhclient-enter-hooks` — extensionless. `dhclient-enter-hooks.d/` is a decoy.** That directory holds only stock Debian fragments (`debug`, `resolved`)
  and never contains `add_default_gateway()`. Both this and the `iptables -S` trap above fail **silently** — exit code 0, plausible-looking output, wrong content — so a capture script or a manual
  `cat` that only checked the `.d/` directory would read as "the hook is empty/minimal" when the real override was never inspected.
- **`dhclient@<iface>.service` is only ever instantiated by `networkd-dispatcher` when the underlying netplan device actually exists.** A stale `/etc/dhcp/dhclient.<name>.conf` file left over from a
  VLAN that's since been removed from `topology_vars` (see `smc_network`'s idempotency gap below) has no running unit behind it and is currently inert — `systemctl list-units 'dhclient@*' --all`
  only ever shows real, live interfaces, never orphaned conf-file names. Useful when auditing whether a conf file on disk implies an active interface: it doesn't, check `dhclient@<name>.service`
  state directly rather than inferring from file presence.
- **The deployed commit is a per-host fact, not a fleet-wide one.** Two of seven sites were found running a hook rendered from a *different branch* than the one believed deployed. Where a site's
  topology differs between two candidate commits, the hook's case list identifies which one it came from — a cheap, reliable way to pin per-host deploy state. Where the commits define a site
  identically the hook cannot discriminate, and that must be stated rather than assumed away.
- **A topology file can shrink.** One site's `internetNN` definitions went from 16 to 6 on a branch, and the shrunken render reached `smc_application` while netplan still held all 16. The failure
  looks identical to a site outgrowing its topology file; only the direction differs. **Stale `ip rule` entries are the forensic marker** — a rule with no matching hook entry is residue from an
  earlier render, since rules persist until deleted or reboot. An interface holding *both* a stale rule and a `metric 100` default is two renders coexisting, not a contradiction.
- **The `100` is accidental.** `metric` is empty at that point, so the code runs `expr + 100`; GNU `expr` treats a leading `+` as a quoting operator, yielding `100`. If DHCP ever returns more than one
  router, `metric` is already the string `metric 1`, `expr metric 1 + 100` errors, and the route is added with **no metric at all** — colliding with the ECMP entry instead of losing to it.
- **Nothing in ansible-wifi builds the ECMP multipath default.** `grep -rn nexthop roles/` returns zero hits. The matched branch calls `kohana status:gateway` on every lease, so the multipath route is
  built by the Kohana wifi app — *inferred, not verified* (that repo is not checked out locally). Practical effect: ECMP membership reflects the portal app's view of link health, which is why an
  unhealthy link quietly leaves the pool.
- **`interfacecheckv2.sh` does not delete routes.** It pings `8.8.8.8` (`-c 4 -W 3`) per interface and on failure runs `systemctl restart dhclient@<iface>.service`, writing
  `my_node_interfacecheck_success{device="…"} 0`. Route disappearance is second-order. That series is a usable per-interface failure-onset history without box access (`mcp-grafana-apn` for
  rcp/rct/wh).
- **`192.168.100.0/24` is the modem's own DHCP scope**, not an SMC address range. Both `roles/smc_network/files/dhclient.conf` and `dhclient-starlink.conf` carry `reject 192.168.100.0/24;` with the
  comments "nbn modem dhcp scope" / "starlink modem dhcp scope". On a primary uplink this is the **Starlink dish management address** (Starlink's standard `192.168.100.1`). Seeing ARP from it on a WAN
  VLAN means the dish's LAN side shares that broadcast domain — the dish is not in a clean bypass state, a real finding worth chasing — but **live-verified 2026-07-29 not to be the cause of "lease
  held, can't ping" by itself.** On two sites where this ARP traffic was captured, `ip neigh` showed the *same* MAC correctly resolving as the gateway on every WAN interface, healthy and broken alike
  — it is the segment's real gateway, periodically also ARPing from its own management IP for its own upstream next-hops. See the missing-route bullet below for what actually broke those interfaces.
  Corroborating signal for the bypass concern independently of that: a `100.64.x.x/10` lease with gateway `100.64.0.1` is Starlink's own CGNAT, so on those links the "carrier gateway" the SMC ARPs for
  is the dish itself — and a public-IP lease (not `100.64.0.0/10`) turning up in an `ip rule`/lease file anywhere is a stronger, independent signal the dish handed out a router-mode address at some
  point.
- **"Lease held, can't ping 8.8.8.8" can be a missing route, not an ARP failure — check which before assuming the dish.** *(live-verified 2026-07-29, two `rcp` sites)* An interface orphaned from the
  hook's `case` list (see the first-come bullet above) can end up with **zero default route in any table** if it lost the race for the `*)` branch's single shared `metric 100` route — that branch
  runs `ip route add`, not `replace`, so only the first orphan to renew gets a route; every later orphan gets none. With no route out that device at all, `ping -I <iface> <off-link-target>` fails
  **locally** (`Destination Host Unreachable` from the SMC's own address, or silent 100% loss with nothing ever sent) — before ARP is even attempted. The tell that distinguishes this from a real L2/
  dish problem: `ping -I <iface> <on-link-gateway>` (e.g. `100.64.0.1`, inside the leased `/10`) still succeeds, because on-link destinations resolve via ARP directly and never need a routing-table
  entry. Diagnose with `ip route show table all | grep <iface>` (real orphans show only the on-link `scope link` route, no `default via ... dev <iface>` anywhere) and `ip rule show` (no `from
  <lease-ip> lookup <iface>` entry). This is the same root mechanism as the stray-route bullet above, just the *losing* side of the same race rather than the winning side — fixing the hook's `case`
  list fixes both. Full evidence: `local-knowledge-ansible/ansible-wifi/issues/apn/routing-issue/docs/problem2-live-root-cause-20260729_2112.md`.
- **WAN VLAN MACs are deterministic**, seeded on hostname + interface name: `'72:77:77' | random_mac(seed='{}{}'.format(inventory_hostname, iface_name))`. Renaming a site or a VLAN changes its MAC,
  which can strand a carrier-side or upstream-device binding.
- **`INPUT -i <starlink-iface> -j DROP` is intentional, but its comment is stale.** `iptables.smp.j2` says "Starlink has a public ip, we want to hide it as much as possible" — written when the label
  meant Starlink. Under today's inversion the rule protects the **SMP backup**; the actual Starlink primaries, under the `internet` label, get no equivalent DROP. Currently harmless because they sit
  on CGNAT, but true by accident rather than design. The rule sits after the `ESTABLISHED,RELATED` accept, so outbound-initiated traffic is unaffected, and it is `DROP` not `REJECT` so the host does
  not answer a scanner. Note the template's INPUT chain already ends in `-j REJECT --reject-with icmp-host-prohibited`, so against the template the DROP governs *how* traffic is refused rather than
  *whether* — but a box whose live ruleset shows `-P INPUT ACCEPT` and no trailing REJECT has the DROP as its only protection there. Never recommend deleting it; add a narrower ACCEPT above it if
  inbound access is genuinely required.
- **DHCP negotiation bypasses the `iptables` filter-table `INPUT` chain entirely — this is why the starlink DROP rule above never blocks DHCP, and generalizes to any interface-scoped
  `INPUT ... -j DROP`/`REJECT` rule on this fleet.** ISC `dhclient` (the fleet's DHCP client) opens a raw `AF_PACKET` socket for its own port-68 traffic, tapping frames at the link layer
  before/parallel to netfilter's `NF_INET_LOCAL_IN` hook where the filter table's `INPUT` chain lives — true for the initial `DISCOVER`/`OFFER`/`ACK` exchange (before the interface has an IP at
  all, so `ESTABLISHED,RELATED` can't be the explanation either) and for later unicast-retry/broadcast-rebind renewals alike. Confirmed live on Warburton: DHCP lease renewal on `vlan621` succeeds
  cleanly despite 1.68M packets dropped on that same interface by the very DROP rule in question, and the template's own `dss` role block has an explicit dhcp-broadcast ACCEPT carve-out before its
  DROP while the starlink block has none — yet starlink DHCP demonstrably works, confirming it isn't relying on any filter-table rule at all.
- **Deterministic WAN MACs are a forensic tool, not just a config detail.** Because the seed is `inventory_hostname + iface_name`, the expected MAC for any host/interface pair can be recomputed
  offline and compared against what the box actually has:
  ```python
  from random import Random; import re
  def mac(prefix, seed):
      v = Random(seed).randint(68719476736, 1099511627775)
      return prefix + re.sub(r"(..)", r":\1", f"{v:x}"[:2*(6-len(prefix.split(":")))])
  mac("72:77:77", "old-looma-smc01" + "vlan525")   # -> 72:77:77:d1:90:4a
  ```
A match proves Ansible rendered that stanza (the interface was not hand-created) **and** that the interface carried `role: internet`/`nbn-modem` at render time, since no other role emits a
`macaddress:` line. A mismatch means the interface came from somewhere else. This was the evidence that identified an rcp site whose production netplan had been rendered from inventory present in no
ref of the repository — see `local-knowledge-ansible/ansible-wifi/issues/apn/routing-issue/`.
- **Generated artifacts can disagree with each other.** `smc_network` renders netplan and `00-interface-activation.sh`; `smc_application` renders `/etc/dhcp/dhclient-enter-hooks`. A tag- or
  role-limited run can update one and not the other, leaving an interface that netplan treats as a primary and the hook has never heard of — which is exactly what produces a stray `metric 100` route.
  Compare `stat` mtimes of `/etc/netplan/*.yaml` and `/etc/dhcp/dhclient-enter-hooks` when diagnosing. Same failure class as `rule-005`.
- **VRF and multi-WAN policy routing (`multiwan-setup.sh.j2`, `smc-link-allocator.py`, fwmark/nft hashing, per-link tc shaping) exist only on `rise-multi`** (commit `d0635e5e`) and are **not
  deployed**. If WAN routes appear in the main table, VRF is not in play on that box. **More precise 2026-07-31 (git archaeology, `local-knowledge-ansible/ansible-wifi/issues/internet-link-handling/`,
  confirmed on the branch now shared by `rise-multi`/`internet-label-rename` after a same-day reset):** the *deploying* Ansible task block for `multiwan-setup.sh.j2`/`.service.j2`
  (`roles/smc_network/tasks/ubuntu.yml`, ~lines 377-405) is fully commented out — added by commit `5eb127bf` (2025-10-16, the per-WAN-VRF fix for same-subnet/same-MAC Starlink CPE ARP flapping),
  then disabled as **apparent incidental collateral** of an unrelated commit, `c19a61fa` (2026-06-09, a URL-capture-v2 refactor) — no deliberate rationale recorded. This reads as accidentally
  orphaned complexity, not a considered decision to abandon the mechanism. **Important nuance not previously captured here:** the fwmark script being dead does not mean VRF is fully "not in play" —
  `roles/smc_network/templates/netplan.yml.j2`'s per-WAN VRF *allocation* (the `{% if interface.role in ['internet','starlink'] %}` VRF-membership block, ~lines 46/127) is **still live and rendered
  into every deploy today**. Only the fwmark `ip rule`s that would route traffic into those VRF tables are missing. A box could plausibly carry allocated-but-unused `vrf-<tableid>` devices as a
  result — **not yet checked on any live SMC**, flagged as an open item, not confirmed either way.
- **`smc_application`'s dhclient-restart handler had no connectivity safety net — `smc_network`'s does. Fixed 2026-07-29, not yet live-tested under a real failure.** Both roles can trigger
  `systemctl restart dhclient@*.service` (every WAN interface, all at once). `smc_network` (`roles/smc_network/handlers/main.yml`, listen `Protected dhclient services restart`) schedules an
  independent `at systemctl restart teleport` job 2 minutes out *before* the restart, runs the restart `async`/`poll: 0`, then `wait_for_connection` (up to 1h) and cancels the `at` job only if the
  connection comes back — protecting against the exact case where the current SSH/Teleport session dies mid-restart. `smc_application`'s equivalent (`roles/smc_application/handlers/main.yml`,
  listen `Restart Internet interfaces`, fired by the `dhclient-enter-hooks` template task) was a bare synchronous `systemctl restart dhclient@*.service` with none of that — confirmed the only
  listener repo-wide. **The same protected pattern has now been ported into `smc_application`'s handler**, on branch `fix/routing-issue` (uncommitted as of 2026-07-29), `at`/`atd` confirmed
  installed and active on all four affected sites. It has been syntax-checked and validated with `ansible-playbook --check --diff` dry-runs, but **not yet exercised against a real connection-loss
  scenario** — treat it as fixed-on-paper-and-in-dry-run, not fully proven, until that happens. Full detail:
  `local-knowledge-ansible/ansible-wifi/issues/apn/routing-issue/docs/dhclient-restart-safety-gap-20260729_2006.md`.

### Manual TBF/`ifb` Ingress Shaping — live, fleet-wide, NOT Ansible-managed

Established 2026-07-29, live-verified (read-only capture, all seven `rcp` sites). **This is a separate mechanism from the `rise-multi`/VRF "per-link tc shaping" mentioned above** — that one is
part of the undeployed multi-WAN allocator; this one is deployed today, on the currently-live branch, and has nothing to do with VRF.

**Mechanism, confirmed identical everywhere it runs:** a manually-installed script (`/usr/local/sbin/internet-ingress-shaping.sh`) plus a hand-installed `systemd` oneshot unit
(`internet-shaping.service`, `WantedBy=multi-user.target`, runs once at boot). Since `tc` only natively shapes egress, ingress shaping uses the standard redirect pattern: for each shaped `vlanN`,
an `ingress` qdisc redirects all traffic to a paired `ifbN` device (`tc filter ... action mirred egress redirect dev ifbN`), then a `tbf` (token bucket filter) qdisc on that `ifb`'s egress caps
the rate. Only direct-Starlink VLANs (`role: internet`) are shaped — Testra-managed `LAN1`/`LAN2` (already at a 50 Mbps plan cap) and the nbn SMP backup are deliberately excluded, per the
operator's own design intent.

**Not templated, not idempotent, not rendered by any `smc_*` role — confirmed by grep and by absence from every relevant role's tasks.** A future `smc_bases.yml` run will not recreate this if it's
ever lost (e.g. a reinstall), and nothing currently guards against configuration drifting between sites other than each site's script having been hand-edited once at install time.

**The script is hand-parametrized per site, not identical fleet-wide — do not assume a pasted example applies verbatim to another site.** Confirmed live: VLAN loop range varies (2 to 10 VLANs per
site), and Horn Island's rate itself differs — `70mbit` for 10 VLANs, `80mbit` for the other 4, versus `150mbit` uniformly at the other six sites that have the script at all. A site whose live
rate doesn't match a "should be 150mbit" assumption is not necessarily a fault; check that site's own script text first.

**`tc -s qdisc show`'s byte counters are cumulative since the shaping unit last ran (i.e. since last boot), not an instantaneous rate.** For a live rate, query Prometheus instead:
`rate(node_network_receive_bytes_total{device=~"vlan5[0-9]+"}[5m]) * 8` via `mcp-grafana-apn` — this is also how the switch01-vs-switch02 cold-standby fact above was established.

**Known gap, not a fault:** New Looma (installed 2026-07-25, the most recently onboarded rcp site) has no shaping script, unit, or `ifb` interfaces at all — `ip -br link show type ifb` returns
empty. Consistent with shaping being rolled out per-site by hand rather than fleet-wide in one pass; New Looma simply hasn't received it yet. Also confirmed: shaping scripts only ever cover the
`52x` (switch01) block on sites that have them — the `53x` (switch02) cold-standby block above is unshaped everywhere, which is expected since it carries no traffic to shape.

**Corrected 2026-07-30 — not "planned, not started".** A `smc_qos` role already exists in the repo, but it is gated `when: inventory_dir.split('/')|last == 'rct'` — it silently no-ops on every
`rcp`/`nbn_accelerate` deploy. `--tags qos` ran clean during all three 2026-07-30 canary deploys and never fired. Manual TBF/`ifb` shaping (above) remains the only active mechanism on rcp, and it
has NOT been extended to VLANs that were only newly fixed by the routing-drift remediation: 2 VLANs missing shaping at Pandanus Park, 10 at Umoona, 8 at Old Looma (as of 2026-07-30). Two open
design questions if `smc_qos` is regated for rcp/nbn_accelerate: (1) the rate-variable shape needs to support Horn Island's per-VLAN split, not just a single per-host rate — six of seven sites use
one rate, Horn Island needs two; (2) role placement/name relative to `smc_network`/`smc_application` in `smc_bases.yml`'s run order is unconfirmed. Source: `local-knowledge-ansible/ansible-wifi/
issues/apn/routing-issue/docs/ingress-shaping-not-managed-or-extended-20260730_1245.md`.

### WAN-Path Diagnostic Techniques (from the 2026-07-30 dark-VLAN investigation)

Two generalizable techniques, not site-specific, established while chasing a Starlink-backup VLAN that showed as provisioned but was dark at L2:

- **A NIC-level RX counter of exactly `0` (`ip -s link show <iface>`) rules out firewall/L3-L4 causes instantly** — nothing has ever arrived on that interface for iptables/routing to act on, so
  time is better spent on the physical/L2 path (cable, switch port, switch-trunk VLAN membership, carrier CPE) than on iptables rules.
- **The sibling-VLAN isolation test**: if a different VLAN sharing the same physical parent NIC/port as the dark VLAN is carrying real traffic, that exonerates the cable/port/NIC — the fault is
  isolated to the dark VLAN's own switch-trunk membership or the carrier-side CPE, not anything the SMC itself controls.

This pair found Pandanus Park/Umoona/Beagle Bay's `vlan621` backup circuit provisioned in topology but dark at L2 (fixed switch-side, outside ansible-wifi's scope) and separately confirmed Horn
Island's `starlink01`/`starlink02` topology block is applied even at sites with no backup circuit ever ordered — see `13_known-issues.md`. Source: `local-knowledge-ansible/ansible-wifi/
issues/apn/routing-issue/docs/starlink-backup-no-lease-l2-investigation-20260730_1400.md`.

### Local (LAN) Traffic

```
WiFi clients ─→ hostapd (radio)
               ─→ bridge_501 (client VLAN)
               ─→ isc-dhcp-server (DHCP for clients)
               ─→ unbound/named (DNS for clients)
               ─→ NAT/routing (iptables MASQUERADE)
               ─→ upstream WAN

MQTT devices → mosquitto (IoT telemetry)
```

### Alert Flows

```
Prometheus alertmanager
    ├── → prometheus_noc_msteams_webhook → Teams (NOC)
    └── → prometheus_dev_msteams_webhook → Teams (dev)

Jenkins
    └── → jenkins_teams_webhook → Teams
```

### Grafana / Prometheus MCP Access

**Read-only:** mcp-grafana is used for reads only — metric queries, alert state, dashboard inspection. Never write, modify, or create anything in Grafana via MCP.

Grafana instances are not directly accessible — they're reached via local SSH tunnel port-forwards. Use the flavor-specific instance, not `mcp-grafana` (central NOC Grafana, unrelated to SMC boxes).

| MCP instance | Grafana URL | Covers flavors |
|---|---|---|
| `mcp-grafana-nbn` | `http://127.0.0.1:63000` | nbn_accelerate, nbn_wh |
| `mcp-grafana-apn` | `http://127.0.0.1:53000` | rcp, rct, wh |

Note: `mcp-grafana` (`monitoring.apn.net.au:3000`) is central NOC Grafana — do NOT use for SMC box troubleshooting. It covers network/ISP dashboards, not SMC host metrics.

**Prerequisite:** The SSH tunnel port-forward must be active before the MCP will respond. Verify with:
```bash
lsof -nP -iTCP:63000 -sTCP:LISTEN   # nbn cluster
lsof -nP -iTCP:53000 -sTCP:LISTEN   # apn cluster
```

**Dashboard inventory (confirmed live 2026-08-03).** The two instances are not mirrors — `mcp-grafana-apn` has 20 dashboards vs 9 on `mcp-grafana-nbn`. Both share a common "smc"-tagged core (Alerts, Heatmaps, Disk Wear and Tear, Internet Speed Analysis, SMC Disk Life Time, SMC Home, SMC Network, SMC System, Speedtest Exporter). `mcp-grafana-apn` additionally carries dashboards with no NBN counterpart:

| Dashboard | UID | Purpose |
|---|---|---|
| RISE SMC Health Detail | `rise-smc-detailed-health` | Per-host RISE health subscores, penalties, thermal/temp, overlay/inode/zram — see "RISE Health/Watchdog Framework" in `02_service-map.md` |
| RISE SMC Table | `e3c73c2a-351f-4734-b6f9-3eed971ceaa9` | Fleet-wide RISE rollup: Fleet Summary (WATCHDOG#/ZRAM#/OVERLAY#/HEALTH CHECK#/DOWN SMC# counts), Offline SMCs (30d), Pending sites (RISE not yet deployed) |
| RISE Dashboard | `rise-stage0_5` | Earlier-stage RISE rollout view |
| Sites not reporting | `fa620053-7cdf-4737-8be1-c60cd3b31b8d` | Per-cluster (RCP/RCT/WH) reporting-site counts + list of non-reporting sites |
| Site Reporting Graph | `e0774e71-5f36-4f20-80c1-d84d7cfd9dde` | Time-series view of the above |
| SMC Table | `b796b0ef-7d6d-4a44-953c-3591960f84f7` | Per-host flavor-filtered detail table (non-RISE) |
| RPi SD Card Status | `f560056d-6545-4d01-ac4b-bfb086c32686` | SD card wear/status table, RPi flavors only |
| Data Backlog / (1)Prometheus RW Receiver + Sender Backlog | `d4921bf0-…`, `prom-rw-backlog`, `1prom-rw-backlog` | Federation `remote_write` pipeline backlog — `Data Backlog` has 0 panels (unused/placeholder), the two RW Backlog dashboards are the live ones |
| Servers Network / Servers System Information | `ddd96f19-…`, `c1b900ba-…` | Backend infra servers, not SMC boxes — out of skill-smc scope |

RISE dashboards exist **only** on `mcp-grafana-apn` because RISE is deployed to `rct`/`wh` flavors only (confirmed via the `flavor=~"rct|wh"` gate in the "Pending sites" panel query) — `rcp` (x86 non-RISE) and the NBN Accelerate cluster (`nbn_accelerate`/`nbn_wh`) run no RISE metrics at all, which is why they're absent from `mcp-grafana-nbn`.

---
````

## File: references/04_dependency-tree.md
````markdown
# SMC Dependency Tree

## 4. Dependency Tree

Services in order of criticality (what breaks everything downstream when down):

```
Level 0 — Foundation
  overlayroot         → must be healthy before any file write has effect
  network             → everything depends on connectivity

Level 1 — Remote Management
  teleport            → all remote access (SSH, Ansible, CI) is lost without this
  autossh-teleport-openssh → Teleport tunnel; without it teleport node is unreachable

Level 2 — Local Services
  isc-dhcp-server     → WiFi clients cannot get IPs
  unbound / named     → clients cannot resolve DNS
  hostapd             → WiFi clients cannot associate

Level 3 — Monitoring
  autossh-prometheus-federation → metrics federation to central Prometheus lost
  node_exporter       → all system metrics stop
  prometheus (local)  → local metrics storage, speedtest scraping

Level 4 — Optional / Flavor-Specific
  asterisk            → VoIP (rcp only, apn-cluster-exclusive — never on cw-cluster flavors)
  keepalived          → HA VIP failover (non-RCT only)
  cnmaestro-provisioning → WiFi AP cloud provisioning
  redis               → required by cnmaestro-provisioning
  apache2             → web app access (RCT: Kohana + Tstik)
  clamav-daemon / clamav-freshclam → antivirus hardening (nbn_accelerate only, apn-cluster-exclusive-absent)
  lynis               → security-audit CLI, on-demand only, no daemon (nbn_accelerate only)
  smc_ltp (7 rcp sites — see 08_ansible-authoring.md) → bind9/named replaces unbound+stubby;
                         CNMaestro Cambium ePMP/cnPilot backhaul provisioning via a SEPARATE
                         smc_cnmaestro_provisioning role/playbook (smc_ltp.yml) — distinct
                         mechanism from the "cnmaestro-provisioning" service two rows above; do
                         not conflate the two without checking which one a given host actually runs
```

**smc_ltp vs the generic `cnmaestro-provisioning` service — a naming collision risk, not yet fully resolved.** The Level 4 `cnmaestro-provisioning`/`redis` row above (WiFi AP cloud provisioning,
`systemctl status cnmaestro-provisioning`, `redis-cli ping` — see `05_troubleshooting.md` Tier 4) predates the 2026-08-03 `smc_ltp` exploration and appears to describe a different mechanism:
the `smc_ltp`-only path found 2026-08-03 uses `roles/smc_cnmaestro_provisioning` (a Python script + static YAML config, no Redis dependency observed) invoked by the standalone `smc_ltp.yml`
playbook, not a `cnmaestro-provisioning` systemd service. Both provision Cambium/CNMaestro-managed wireless gear, so the naming overlap could be: (a) two genuinely separate provisioning paths
for different hardware roles, (b) the same underlying mechanism described two different ways by different sessions, or (c) the Level 4 row above being written from a different flavor's
architecture (RCT) than `smc_ltp` (`rcp`-only). Not resolved — check which flavor/host a given "cnmaestro-provisioning" troubleshooting reference actually applies to before assuming it's the
same thing as `smc_ltp`'s CNMaestro provisioning. See `08_ansible-authoring.md` "smc_ltp Sub-Group" for the `smc_ltp` mechanism in full.

---
````

## File: references/05_troubleshooting.md
````markdown
# SMC Troubleshooting

## Contents
- Tier 1: box unreachable
- Tier 2: service down
- Tier 3: DHCP and DNS failures
- Tier 4: WiFi AP issues
- Tier 5: VoIP / Asterisk
- Tier 6: HA / failover
- Tier 7: monitoring gaps
- Tier 8: overlayroot persistence
- Tier 9: SMP iptables ipset failure
- Tier 10: smc_application loop input failure
- Tier 11: --check does not gate command+async restart handlers

## 5. Troubleshooting Workflows

### Tier 1: Box Unreachable

```
1. autossh tunnel up?
   systemctl status autossh-teleport-openssh
   journalctl -u autossh-teleport-openssh --since "1h ago"

2. Network route stable?
   Prometheus: NodeNetworkDefaultRouteInstability (4+ route changes / 60min)
   ip route show

3. Teleport node healthy?
   systemctl status teleport
   journalctl -u teleport --since "30m ago"

   From the operator side, distinguish "this one connection attempt failed" from
   "the box has fully deregistered" before assuming a transient blip:
     tsh ssh root@<host>          # a single failed attempt can be a local DNS/network hiccup
     tsh ls | grep <host>         # confirms whether the node is still in the cluster roster at all
   A node present in `tsh ls` (shows "<- Tunnel") that fails one ssh attempt is likely transient —
   retry. A node ABSENT from the full `tsh ls` roster (not just this one connection failing) means
   its Teleport agent has dropped off the cluster entirely — confirmed live 2026-07-29 on a site
   whose primary WAN interfaces were simultaneously failing DHCP (no DHCPOFFERS at all), consistent
   with the Teleport tunnel riding the same failing uplink. That's a stronger, different signal than
   a single ssh timeout and points at the box's WAN/management path generally, not just one service.

4. Overlayroot healthy?
   mount | grep overlay
   (lower dir must be mounted; tmpfs upper dir must have headroom)
```

### Tier 2: Service Down (systemd failed)

```
1. What failed?
   journalctl -u <service> --since "1h ago"

2. Other units also failed?
   systemctl list-units --state=failed

3. Disk full?
   df -h
   Prometheus alerts: HostOutOfDiskSpace, HostOutOfInodes, HostDiskWillFillIn24Hours

4. Config error from last Ansible run?
   Check playbook run output in Jenkins / check generated config:
   - DHCP: dhcpd -t -cf /etc/dhcp/dhcpd.conf
   - Unbound (RCT): unbound-checkconf
   - named (others): named-checkconf
```

### Tier 3: DHCP Not Serving Clients

```
1. Test DHCP config:
   dhcpd -t -cf /etc/dhcp/dhcpd.conf

2. Check for errors:
   grep -i error /var/log/syslog | tail -20
   journalctl -u isc-dhcp-server --since "30m ago"

3. Verify leases:
   cat /var/lib/dhcp/dhcpd.leases | head -50

4. Check bridge exists and is up:
   ip link show bridge_501
   brctl show bridge_501
```

### Tier 3b: DNS Not Serving Clients (non-`smc_ltp` hosts — Unbound + Stubby)

**Corrected 2026-07-03, membership count corrected twice 2026-08-03**: this is gated by `smc_ltp` inventory-group membership, not flavor — applies to every flavor's hosts except those in `smc_ltp` (a static `rcp`-only group, 7 sites — `guda-guda`, `pandanus-park`, `old-looma`, `new-looma`, `warburton`, `beagle-bay`, `umoona`, all "low touch"-onboarded — see `08_ansible-authoring.md` "smc_ltp Sub-Group" for the full picture, including its unrelated CNMaestro backhaul-provisioning role). This tier only covers DHCP/LAN client DNS; the SMC's own DNS resolution is a separate `systemd-resolved`/glibc path — see `02_service-map.md` and `06_failure-modes.md` if the box itself (not a client) is slow to resolve names.

```
1. Check Unbound:
   systemctl status unbound
   unbound-checkconf
   unbound-control status
   journalctl -u unbound --since "30m ago"

2. Check Stubby (DNS-over-TLS upstream):
   systemctl status stubby
   journalctl -u stubby --since "30m ago"
   # Stubby listens on 127.0.0.1:60053; Unbound forwards here.
   # Stubby's own upstream is 127.0.0.1:60853 (single, no failover) via an
   # autossh local port forward to teleport.apn.au:853 — if journalctl shows
   # repeated connection failures, check `systemctl status autossh-teleport.service`.

3. Test resolution:
   dig @127.0.0.1 google.com
   dig @127.0.0.1:60053 google.com   # direct Stubby test
```

### Tier 3c: DNS Not Serving Clients (`smc_ltp` hosts only — BIND/named)

Applies to the 7 static `smc_ltp` member sites only: `guda-guda`, `pandanus-park`, `old-looma`, `new-looma`, `warburton`, `beagle-bay`, `umoona` (`rcp`-exclusive, all "low touch"-onboarded — `warburton`/`beagle-bay`/`umoona` added 2026-08-03 after the operator confirmed every low-touch site should be a member). These hosts also run CNMaestro-managed Cambium ePMP/cnPilot backhaul provisioning via a separate `smc_ltp.yml` playbook — if DNS is fine but backhaul radios aren't provisioning, check `roles/smc_cnmaestro_provisioning` and CNMaestro cloud connectivity instead, not this tier. See `08_ansible-authoring.md` "smc_ltp Sub-Group" for the full mechanism.

```
1. Check named:
   systemctl status named
   named-checkconf
   rndc status
   journalctl -u named --since "30m ago"

2. Verify zones loaded:
   rndc reload
   ls /etc/bind/

3. Test resolution:
   dig @127.0.0.1 <local-domain>
```

### Tier 4: WiFi AP Issues

```
1. hostapd:
   systemctl status hostapd
   journalctl -u hostapd --since "1h ago"
   # Config: /etc/hostapd/

2. CNMaestro provisioning:
   systemctl status cnmaestro-provisioning
   journalctl -u cnmaestro-provisioning --since "1h ago"
   cat /var/log/cnmaestro-provisioning/*.log 2>/dev/null || ls /var/log/
   redis-cli ping     # must respond PONG
   redis-cli info server
```

### Tier 5: VoIP / Asterisk Issues (non-RCT only)

```
1. Asterisk CLI:
   asterisk -rvvv

2. Verify dialplan:
   asterisk -rx "dialplan show"
   cat /etc/asterisk/extensions.conf

3. Trunk / SIP registration:
   asterisk -rx "sip show registry"
   asterisk -rx "sip show peers"
```

### Tier 6: HA / Failover Issues (non-RCT only)

```
1. VIP assignment:
   ip addr show
   # VIP should be on active node only

2. VRRP state:
   journalctl -u keepalived --since "1h ago"
   systemctl status keepalived

3. Conntrack limit:
   cat /proc/sys/net/netfilter/nf_conntrack_count
   cat /proc/sys/net/netfilter/nf_conntrack_max
   # Alert fires at > 80%
```

### Tier 7: Monitoring Gaps

```
1. Textfile collectors stale?
   ls -la /var/lib/node_exporter/textfile_collector/
   # Check mtime vs max staleness (see Section 2 table)

   # Manually run stale collector:
   sudo python3 /opt/rise/sbdm.py
   sudo bash /opt/rise/interfacecheckv2.sh

2. Prometheus not federating?
   systemctl status autossh-prometheus-federation
   journalctl -u autossh-prometheus-federation --since "1h ago"

3. node_exporter not scraping?
   curl -s http://localhost:9100/metrics | head -20
   systemctl status node_exporter

4. A specific metric missing from Grafana/Prometheus, but node_exporter IS up?
   Don't stop at `up{instance="..."} == 1` — that only proves the scrape target is
   reachable, not that every expected metric is populated. Query the specific metric
   directly against the instance and compare to a known-healthy site:
     curl -s http://localhost:9100/metrics | grep <metric_name>
   Confirmed gap (2026-07-29, see 13_known-issues.md): `my_node_network_device_info`
   returns zero series on some rcp sites while base kernel network metrics and `up`
   are both fine on the same hosts — a per-metric gap, not a per-scrape-target one.
```

### Tier 8: Overlayroot — Ansible Changes Not Persisting

```
Problem: Ansible ran successfully but changes disappeared after reboot.

Cause: Writes went to tmpfs upper dir (/media/root-rw/overlay), not to
the real filesystem (/media/root-ro).

Verify:
   mount | grep overlay
   # Lower dir must be remounted rw for changes to persist

Ansible fix:
   The smc_bases.yml playbook handles overlayroot remount before making
   changes. If running a role directly, ensure smc_bases.yml ran first or
   that the lower dir is already mounted rw.

Manual check:
   mount | grep root-ro
   # If "ro" → changes will not persist
   # If "rw" → changes will persist
```

### Tier 9: `smc_iptables` SMP apply fails with `Set restricted doesn't exist`

**Status: RESOLVED 2026-06-09** — removed ipset match rule from template on `family-friendly` branch.

```
Symptom:
  TASK [smc_iptables : Generate and copy iptables configuration for smp]
  iptables-restore ... Set restricted doesn't exist

Root cause:
  fqdn2ip/ipset teardown removed runtime `restricted` set, but SMP iptables
  template still referenced `-m set --match-set restricted dst`.

Current policy:
  No site should rely on ipset classification for this path anymore.
  SMP metered-time flow must be deterministic and non-ipset.
  Service is unlimited — metered/unmetered distinction is no longer active.
  The METERED_TIME chain and ECLIPSE_METERED_TIME chain remain in the template
  for connmark-based traffic classification but do not enforce data quotas.

Source of truth:
  roles/smc_iptables/templates/iptables.smp.j2
  roles/smc_iptables/defaults/main.yml
  roles/smc_fqdn2ip/tasks/main.yml

Fix applied (2026-06-09):
  Removed line from iptables.smp.j2 METERED_TIME chain:
    -A METERED_TIME -m set ! --match-set restricted dst -j RETURN
  Retained non-ipset returns:
    -A METERED_TIME -m connmark --mark 0 -j RETURN
    -A METERED_TIME -j RETURN

Fix pattern (for reference):
  1. Remove ipset match lines from SMP template.
  2. Keep non-ipset returns (as above).
  3. Remove stale ipset feature flags/conditionals and stale comments.
  4. Validate with:
       ansible-playbook -i inventories/rct/stage smc_bases.yml -l <host> -t smc_iptables -vv
```

### Tier 10: `smc_application` fails with `Invalid data passed to 'loop'`

```
Symptom:
  TASK [smc_application : Collect archive size for each pkg (bytes)]
  Invalid data passed to 'loop' ... got this instead: php8.1-cli

Root cause:
  roles/_helpers/custom_apt_install.yml normalized package input with
  `install_package_name is sequence`, which evaluates true for strings.
  That made `pkgs` scalar instead of list for single package names.

Source of truth:
  roles/_helpers/custom_apt_install.yml (package normalization + loop users)

Fix:
  Normalize as:
    install_package_name if iterable and not string else [install_package_name]

Why:
  Loops must always receive a list; string package names like `php8.1-cli`
  must become `[php8.1-cli]`.

Validation:
  ansible-playbook --syntax-check smc_bases.yml
  ansible-playbook -i inventories/rct/stage smc_bases.yml -l <host> -t smc_application --syntax-check
```

**Superseded 2026-07-29 (old-looma/umoona topology recovery):** the `is sequence` normalization above
was the first-attempt fix, but it hit a second incompatibility under `--check` mode (`Package
unavailable`). The fix actually applied was a **wholesale replacement**, not an in-place patch:
`roles/_helpers/custom_apt_install.yml` and `custom_apt_update_cache.yml` were replaced with their
`rise-multi` branch versions — a simpler `apt-cache policy` check with no size-collection step. If
this symptom recurs, check which version of these two helper files is deployed before re-deriving
the `is sequence` fix from scratch.

### Tier 11: `--check` does not gate `command` + `async` restart handlers

```
Symptom:
  An `ansible-playbook --check --diff` run against a live SMC, intended as a
  read-only preview, actually restarts a live service. journalctl on the
  target shows a real `ansible-ansible.legacy.command Invoked with cmd=...`
  log line for a command the run was only supposed to be previewing.

Root cause:
  `command`/`shell` modules wrapped in `async:`/`poll: 0` do not reliably
  respect --check mode in this Ansible version -- this is a general Ansible
  property, not a task-authoring mistake. No `check_mode:` directive is
  needed to trigger it; the escape happens by default. Confirmed live on
  pandanus-park-smc01, 2026-07-30: `smc_application`'s "Ubuntu Restart
  Internet interfaces" handler (`command: systemctl restart
  dhclient@*.service`, `async: 60, poll: 0`) executed for real during
  --check --diff, while the `template` task that notified it correctly
  stayed in check mode and did not write the file -- a disruptive restart
  against a configuration that was never actually updated.

Source of truth:
  roles/smc_application/handlers/main.yml ("Ubuntu Restart Internet
  interfaces" handler)
  roles/smc_network/handlers/main.yml (contrast: "Protected
  systemd-resolved restart" / "Protected systemd-networkd reload" use the
  `service:` module, state: restarted/reloaded, which DOES correctly
  respect check mode -- these were never at risk)

Why the difference:
  `service:` does not support glob unit names (`dhclient@*.service`), so
  the dhclient-restart handlers use `command:` instead -- which is the
  exact combination that bypasses check mode when wrapped in async.

Fix / mitigation:
  Do not treat `--check --diff` as a safety gate for any handler built on
  `command:`/`shell:` + `async:`. The rendered-file diff shown by
  --check --diff remains accurate as a preview of *what config would
  change* -- it is only the *handler's* behavior during that same run that
  cannot be trusted to stay inert. Review the task diff statically instead
  of relying on a live --check run when the notified handler uses this
  shape. Before running --check against any host with a pending change to
  dhclient-enter-hooks or equivalent, expect the restart to actually fire,
  and treat it the same as a real deploy for change-control purposes.

Validation:
  journalctl --since <window> | grep 'ansible-ansible.legacy.command' on
  the target after any --check run touching this handler shape, to confirm
  whether it actually executed.

Full incident writeup: local-knowledge-ansible/ansible-wifi/issues/apn/routing-issue/docs/pandanus-park-checkmode-async-restart-incident-20260730_1140.md
```

---
````

## File: references/06_failure-modes.md
````markdown
# SMC Failure Modes

## 6. Failure Mode Reference

### Key Prometheus Alerts

| Alert | Trigger | First check |
|---|---|---|
| `HostOutOfDiskSpace` | < 10% free | `/var/log`, overlayroot upper dir fills (tmpfs) |
| `HostOutOfInodes` | < 10% inodes | Small file accumulation in `/tmp`, logs |
| `HostDiskWillFillIn24Hours` | `predict_linear` > 24h | Find write rate source |
| `HostSystemdServiceCrashed` | unit state = failed | `journalctl -u <unit>` |
| `HostClockSkew` | offset > ±0.05s | `chronyc tracking` |
| `HostClockNotSynchronising` | stratum = 0 | `chronyc sources -v`; upstream NTP reachable? |
| `HostConntrackLimit` | > 80% conntrack | `ss -s`; check for connection leak; see Tier 6 |
| `NodeNetworkDefaultRouteInstability` | 4+ route changes / 60min | VRRP flap, overlay issue, uplink unstable |
| `NodeStarlinkInterfacecheckPacketLoss` | 100% loss / 60min | Starlink interface down (specific flavor) |
| `sbdm_device_health_status == 0` | RPi Swissbit microSD card degraded (RPi/rct/wh/nbn_wh only — corrected 2026-07-13, was mislabeled "Samsung SSD"; `sbdm-cli` only detects genuine Swissbit hardware, never fires on x86 SSD/CFast) | microSD card replacement needed |
| `smartmon_device_smart_healthy == 0` | SMART failure — x86 rcp/nbn_accelerate only (Innodisk CFast or Transcend SSD; `smartctl` finds no ATA-SMART device on RPi microSD, this alert never fires there) | Drive health critical |

### Overlayroot Upper Dir Full

```
Symptom: HostOutOfDiskSpace fires on a box with 60GB storage
Cause: /dev/overlay (tmpfs at /media/root-rw) fills RAM-backed space
Check: df -h | grep overlay
       # "size=40%" → 40% of RAM = ~780MB on 1.9GB RPi
Fix:   Identify what is filling /media/root-rw/overlay
       find /media/root-rw/overlay -type f -size +10M 2>/dev/null
```

### Root Filesystem Unexpectedly Read-Only (x86 `rcp` / `nbn_accelerate`)

| Field | Value |
|---|---|
| Error text | Write failures (`Read-only file system`) on `/`; package/install tasks and file edits fail |
| Typical context | `rcp` or `nbn_accelerate` where overlayroot is not expected |
| Cause class | Kernel protective remount after ext4 journal/storage I/O errors (not overlayroot behavior) |
| Immediate checks | `findmnt -no SOURCE,OPTIONS /`; `mount \| egrep ' on / \|overlay\|root-ro'`; `dmesg -T \| egrep -i 'EXT4-fs error\|I/O error\|Remounting filesystem read-only\|nvme\|sda' \| tail -n 120` |
| Source-of-truth files | `/etc/fstab`; `inventories/nbn_accelerate/group_vars/smc_bases.yml`; `references/07_hardware-overlay.md` migration table |
| Fix pattern | 1) `mount -o remount,rw /` 2) reboot once 3) if RO returns, run offline `fsck.ext4 -f -y <root-device>` from rescue/initramfs 4) run SMART check and replace disk if media errors persist |
| Validation commands | `findmnt -no OPTIONS /` shows `rw`; `touch /root/.rw_test && rm /root/.rw_test`; `journalctl -k -b \| egrep -i 'EXT4-fs error\|I/O error\|read-only'` shows no new remount errors |

### Domain-Specific Host DNS Resolution Delay (non-`smc_ltp` hosts)

| Field | Value |
|---|---|
| Error text | `ping <fqdn>` / `getaddrinfo(AF_UNSPEC)` from the SMC itself stalls ~15s before resolving; direct IP and single-record `dig` are fast; delay is domain-specific (reproduces on domains with an A record + AAAA NODATA, not on domains with no AAAA-eligible answer path) |
| Typical context | Any non-`smc_ltp` host performing a combined A+AAAA lookup (`getaddrinfo(AF_UNSPEC)`) — this is glibc's default behavior for most name resolution, not something the caller opts into |
| Cause class | Architecture exposure, not a code bug: `DNSStubListener=no` (unconditional, `roles/smc_network/templates/resolved.conf.j2`) means host glibc talks directly to `external_dns_servers` over raw UDP — bypassing systemd-resolved's stub *and* unbound/stubby entirely (see `02_service-map.md`). On some WAN paths, one leg (typically AAAA) of the near-simultaneous A/AAAA query pair fails to return; isolated queries and TCP both succeed, ruling out general DNS reachability |
| First confirmed on | garimba-smc01 (rct), 2026-07-03; not reproduced on yuelamu-10mile-smc01 (same fleet, different WAN path) |
| Immediate checks | `time ping <fqdn>` from the box; compare `dig +tcp` (expected to succeed) against default `getaddrinfo` (may stall); packet capture on the WAN interface during the stall to see which query type's response is missing |
| Mitigation (not yet fleet-validated) | Point host resolution at systemd-resolved's stub (`127.0.0.53`) instead of the raw uplink file — this changes resolver *implementation* and appears to route around the WAN-path condition, but does **not** prove the underlying condition is fixed. Do not roll out fleet-wide without live validation — see `13_known-issues.md` |
| Source-of-truth files | `roles/smc_network/templates/resolved.conf.j2`, `roles/smc_network/tasks/ubuntu.yml:196-214`, `roles/smc_dns/templates/unbound.conf.j2`, `roles/smc_dns/files/stubby.yml` |
| Full RCA | `local-knowledge-ansible/ansible-wifi/issues/garimba-smc01/garimba-smc01-dns-resolution-rca-20260703_1158.md` (revision 3, with two rounds of validation-prompt corrections) + companion docs under `issues/garimba-smc01/docs/reports/` |

### Captive Portal Dead at Bootstrap — `Directory APPPATH/cache must be writable`

| Field | Value |
|---|---|
| Error text | Response body is exactly `Directory APPPATH/cache must be writable` (40 bytes), served with **HTTP 200**, and `/var/log/apache2/error.log` stays **empty** — Kohana catches and prints the exception rather than raising it |
| Typical context | Any Ubuntu SMC after `application/cache` or `application/logs` ends up `0755 root:root`. Apache runs mod_php as `www-data` (see `10_captive-portal.md` §11.1), so the dirs are unwritable and `Kohana::init()` throws before routing |
| Cause class | Ansible tag gap, not drift: a `--tags wifi_dev_repo` run wipes and re-clones `/var/www/html/wifi` (git recreates both dirs at umask 022) while the untagged block that chmods them 0777 is skipped. A full untagged run is correct, which masks the defect |
| Source-of-truth files | `/var/www/kohana-base/system/classes/kohana/core.php:281` (cache check), `.../kohana/log/file.php:31` (logs check — **fix both dirs or the failure just moves one step later**), `roles/smc_application/tasks/main.yml` |
| First confirmed on | 10 of 16 in-scope `rcp` sites, 2026-07-21 → 2026-07-28 (7-day outage). `rct` and `wh` swept and unaffected |
| Immediate checks | `stat -c '%a %U:%G' /var/www/html/wifi/application/{cache,logs}` (expect `777 root:root`); then curl the **real ServerName**, never `localhost` with a `Host:` header — localhost is served by `000-default` and returns a healthy-looking 10671-byte `index.html` on a completely dead portal |
| Resolution | `ansible ... -m file -a "path=/var/www/html/wifi/application/cache state=directory recurse=yes owner=root group=root mode=0777"`, repeated for `logs`. Permanent fix: the perms block **and** the `stat` task registering `wifi_stat` must both carry `tags: wifi_dev_repo` |
| Detection gap | No alert can fire on this today. The Kohana usage/status crons run as **root**, for whom a 0755 root-owned dir is writable, so they keep succeeding and Eclipse keeps receiving data. A status-code-only HTTP probe would also miss it — the failure returns 200 |
| Full RCA | `local-knowledge-ansible/ansible-wifi/issues/rcp-fleet/rcp-captive-portal-cache-perms-outage-20260728_1240.md` |

### Disk Path Failure Forcing Root Read-Only (x86 `nbn_accelerate`, active disk path)

| Field | Value |
|---|---|
| Error text | `/dev/sdb2 on / type ext4 (ro,relatime)`; `mount -o remount,rw /` fails with `cannot remount /dev/sdb2 read-write, is write-protected` (rc=32); most binaries (`efibootmgr`, `lsblk`, `blkid`, `findmnt`, `dmesg`) fail with `Input/output error`, not a PATH issue |
| Typical context | amata-smc01 (nbn_accelerate, x86, BOXER-6641 class) |
| Cause class | Physical storage-path failure on the active root disk (`sdb`) — SSD fault and/or SATA link/cable/backplane/power instability. **Not** overlayroot behavior, not a PATH issue, not an Ansible playbook logic error |
| Error signature (from device log, ~2026-04-25 10:37:08) | `ata4.00: failed command: WRITE FPDMA QUEUED`, repeated `COMRESET failed`, `ata4.00: disabled`, `blk_update_request: I/O error, dev sdb`, `EXT4-fs ... I/O error while writing superblock`, `EXT4-fs (sdb2): Remounting filesystem read-only`, `hostbyte=DID_BAD_TARGET` |
| What was evaluated | `smc_disk_failover` role: uses `efibootmgr -n` (BootNext, one-time) after a prolonged internet-failure count — **not a guaranteed safe immediate failover under active I/O corruption**, and EFI tooling itself was unreliable on this host because of the ongoing I/O errors |
| Operational decision guidance | 1) Reboot is a reasonable first attempt, outage risk acknowledged. 2) If a short RW window appears post-reboot: `efibootmgr -v` → set one-time boot to the alternate Ubuntu entry (`efibootmgr -n <id>`) → reboot quickly. 3) If tooling fails or host stays RO: BIOS/UEFI console boot to the alternate SSD manually. 4) After a successful alternate boot: set permanent `BootOrder` with the alternate first (`efibootmgr -o ...`), verify Teleport/autossh, then replace/repair the failed disk path before reintroducing it to the boot order |
| Status | **Open as of 2026-04-30 — not yet recovered.** ROADMAP backlog for this host still lists: recover via reboot/failover, re-establish the PIN/session enforcement chain (`ECLIPSE_*` mark population + `netfilter-persistent`) once writable, validate month-rollover PIN behavior post-recovery, and capture final incident closeout. Baseline content filtering was confirmed still active during the degradation window — do not assume a fully down box means filtering is also down |
| Full incident capture | `local-knowledge-ansible/ansible-wifi/issues/amata-smc01/2026-04-30-amata-smc01-storage-incident.md` + `amata-error.log` |

### Ansible Failure: `iptables-restore` references missing `restricted` set

| Field | Value |
|---|---|
| Error text | `iptables-restore ... Set restricted doesn't exist` |
| Typical task | `smc_iptables : Generate and copy iptables configuration for smp` |
| Cause class | Template/runtime drift after fqdn2ip/ipset decommissioning |
| Immediate check | `rg -n "match-set|restricted|ipset" roles/smc_iptables roles/smc_fqdn2ip` |
| Resolution | Remove active ipset dependency from SMP template and stale toggle logic |

### Ansible Failure: loop receives scalar package name

| Field | Value |
|---|---|
| Error text | `Invalid data passed to 'loop' ... got this instead: php8.1-cli` |
| Typical task | `smc_application : Collect archive size for each pkg (bytes)` |
| Cause class | Jinja type-check bug in helper normalization |
| Immediate check | `roles/_helpers/custom_apt_install.yml` package normalization logic |
| Resolution | First-attempt fix (`is sequence` normalization, see `05_troubleshooting.md` Tier 10) hit a second incompatibility under `--check` mode (`Package unavailable`). **Actual applied fix (old-looma/umoona, 2026-07-29): wholesale-replaced** `roles/_helpers/custom_apt_install.yml` and `custom_apt_update_cache.yml` with their `rise-multi` versions (simpler `apt-cache policy` check, no size-collection step) rather than patching in place |

---
````

## File: references/07_hardware-overlay.md
````markdown
# SMC Hardware and Overlayroot

## Contents
- Hardware differences: x86 vs Raspberry Pi
- NBN Accelerate / NBN WH hardware inventory (first live fleet sweep)
- Overlay filesystem structure and runtime behavior
- Overlayroot status checks
- Ansible and overlayroot persistence
- Disable sequence
- Read-only migration status
- Verifying 12-fix parity on-box (probe gotchas + healthy-node write profile)
- rcp disk write profile
- Legacy url_capture disk-write behavior

## 7. Hardware Differences: x86 vs Raspberry Pi

**Corrected 2026-08-03 — the DNS and VoIP rows below were wrong, conflating platform (x86 vs ARM) with flavor-specific gates that are actually orthogonal to platform.** This table predates
both the 2026-07-03 DNS correction (which fixed the same "unbound=RCT/bind=non-RCT" mistake in `02_service-map.md` but was never applied here) and the 2026-08-03 NBN Accelerate gap-fill —
it went unnoticed because no coherence sweep had re-checked this specific file against those corrections until today.

| Aspect | x86 PC (`rcp`, `nbn_accelerate`) | Raspberry Pi (`rct`, `wh`, `nbn_wh`) |
|---|---|---|
| CPU arch | x86_64 | ARM64 (aarch64) |
| RAM | 4–16 GB typical | 1.9 GB |
| Storage | SSD or CFast (Innodisk CFast 3ME3 / Transcend TS128GSSD420K confirmed brands, monitored via `smartmon.py`/`smartctl`) | **Always SD card** (Swissbit industrial microSD, monitored via `sbdm.py`/`sbdm-cli`) — USB storage may be physically present but is reserved for future use, not the root/primary storage device |
| Swap | Traditional swap partition | zram (`/dev/zram0`, ~1.2 GB, compressed) |
| DNS | **Not platform-determined — corrected 2026-08-03.** Every flavor (both x86 and RPi) runs Unbound + Stubby (DNS-over-TLS) by default; the *only* hosts that get BIND/named instead are members of the `smc_ltp` inventory group — a static, `rcp`-only, 7-site allowlist, unrelated to CPU architecture. See `02_service-map.md` and `08_ansible-authoring.md` "smc_ltp Sub-Group". | Same — Unbound + Stubby, unless `smc_ltp` (never applies to RPi flavors; `smc_ltp` is `rcp`-only) |
| VoIP | **Not platform-determined either — corrected 2026-08-03.** Asterisk is gated to `rcp` specifically (`inventory_dir.split('/')|last == 'rcp'`), not "x86" generally — confirmed live 2026-08-03 that `nbn_accelerate` (also x86) does **not** have Asterisk (`systemctl is-active asterisk` → inactive/not found on `warakurna-smc01`/`indulkana-smc01`). See `08_ansible-authoring.md` "Flavor/Cluster Conditional Branching". | Not deployed |
| Antivirus/security | **`nbn_accelerate` only** (ClamAV + Lynis) — confirmed live 2026-08-03 on `warakurna-smc01`/`indulkana-smc01`, both installed. `rcp` does not get this despite being the same x86 platform. | Not deployed on any RPi flavor |
| HA | keepalived (VRRP, built from source) | Not deployed |
| Web apps | Depends on flavor | Kohana + Laravel Tstik |
| QoS | tc via role (gated `rct`-only per `08_ansible-authoring.md` — silently no-ops on `rcp`/`nbn_accelerate` despite this row's platform framing; see `13_known-issues.md`) | networkd-dispatcher |
| Kernel modules | Standard x86 | RPi-specific |
| Ansible | Same roles | OS-specific tasks in smc_network |

**Both platforms** run the identical service stack (monitoring, DHCP, WiFi AP, Teleport tunnel, Prometheus) with flavor-specific differences handled by `when: ansible_architecture == 'aarch64'`
conditions in Ansible roles for genuinely platform-driven behavior — but as the DNS/VoIP/antivirus/QoS rows above show, **not every difference in this table is actually platform-driven**; several
are flavor-exclusive gates (`inventory_dir.split('/')|last == '<flavor>'`) or inventory-group gates (`smc_ltp`) that happen to correlate with platform for some rows and not others. Don't assume a
row applies to "all x86" or "all RPi" without checking whether it's gated by `ansible_architecture`, `hotspot_flavor`, or an exact flavor/group name — see `08_ansible-authoring.md` "Flavor/Cluster
Conditional Branching" for the full selector-mechanism reference.

### Storage health monitoring — two different tools, clarified 2026-07-13

The table above says x86 storage is "monitored by SBDM/SMART" — this undersells how split the two
mechanisms actually are. Confirmed live 2026-07-13:

| Tool | Binary | Works on | Fails on |
|---|---|---|---|
| `smartmon.py` (wraps `smartctl`) | n/a (uses system `smartctl`) | x86 rcp: Innodisk CFast, Transcend SSD (both report via ATA SMART) | RPi/mmcblk SD cards — `smartctl --scan-open` finds zero devices; SD/eMMC doesn't expose classic ATA SMART attributes the way SATA/USB-SAT drives do |
| `sbdm.py` (wraps `sbdm-cli`, "Swissbit Device Manager") | `roles/smc_node_exporter/files/{x86-64,aarch64}/sbdm-cli` — deployed to **both** architectures | RPi/rct/wh: genuine Swissbit-branded industrial microSD cards (model "SD card SB AFNI0", series S-58) | x86 rcp: Innodisk/Transcend hardware isn't Swissbit-branded — `sbdm-cli` returns "No supported disks found" (exit 3), and `sbdm.py` currently exits 0 with **zero stdout output**, producing a 0-byte `sbdm.prom`. This is the root cause of the standing "sbdm.prom = 0 bytes" bug tracked as a known issue on tjuntjuntjara/burringurrah/warburton — expected behavior for non-Swissbit hardware, not a bug in those specific nodes. |

So: x86 rcp nodes are monitored by `smartmon.py`/`smartctl` only (SBDM silently no-ops there). RPi
rct/wh nodes are monitored by `sbdm.py`/`sbdm-cli` only (SMART silently no-ops there, confirmed
`smartmon.prom` has metric headers but zero data lines on every RPi node checked). Never assume
both tools produce meaningful data on both platforms.

### Transcend SSD wear metric — firmware limitation, fixed fleet-wide (found 2026-06-02, root-caused 2026-07-13, Part 1 shipped + confirmed live 2026-07-17)

Transcend TS128GSSD420K (BOXER-6641 nodes: mornington, bidyadanga, horn-island, warburton) used to
report `smartmon_attr_value` = **100 for every single SMART attribute**, not just
`remaining_lifetime_perc` — confirmed via full `smartmon.prom` comparison against a working Innodisk
CFast node. This was a firmware limitation (Transcend doesn't implement SMART VALUE normalization at
all on this model), not something `smartmon.py` got wrong — the script mirrors whatever the drive
reports, faithfully, for both hardware classes identically.

`RAW_VALUE` (`smartmon_attr_raw_value`) being correct on both vendors was the original workaround
(ADR-002, RULE-005, both dated 2026-06-02), superseded 2026-07-13 by a collector-level fix — see
`docs/smartmon-active-disk-value-fix-plan-20260713_1310.md` Part 1 — that makes `smartmon_attr_value`
itself directly correct. **Status as of 2026-07-17: Part 1 is deployed fleet-wide and confirmed live
via direct Prometheus query**, not just the 2/12-node state recorded 2026-07-13 ~17:33 — all 4
BOXER-6641 nodes now return distinct, plausible per-disk values on the active Transcend disk
(mornington sdb=90%, bidyadanga sdb=91%, horn-island sda=100%, warburton sda=100%; idle standby
disks correctly still read ~100%, near-zero writes). `smartmon_attr_raw_value` now returns **zero
series fleet-wide** — the raw-value workaround is fully retired, not just deprecated. The fix also
covers `temperature_celsius`, which had the identical VALUE=100 bug and the identical fix
precondition. **Do not point new dashboards/alerts at `smartmon_attr_raw_value`** — it has no data
to query. See `docs/disk-write-rates-20260716.md` for the live-query evidence and ADR-002 for the
supersession record. The earlier interim relabel fix mentioned in older revisions of this note was
reverted before Part 1 implementation began — it is dead, do not deploy it anywhere.

### RPi/Swissbit microSD wear metrics — genuinely low fleet-wide usage, not a bug (investigated 2026-07-13)

`sbdm_device_attribute{name="remaining_erase_life_time"}` reads exactly `100.0` fleet-wide (298/298
reporting sites, zero exceptions) — investigated as a possible bug matching the Transcend pattern
above, concluded **genuine**: even the single busiest RPi node found fleet-wide (`rollah-smc01`,
282,613 total erases, 1,972 power cycles — both far above every other node sampled) has an average
erase count of only 312 against a 60,000-cycle rated budget (~0.5% used). Confirmed directly against
Swissbit's own human-readable `sbdm-cli` output, not just CSV parsing — not a parsing bug.
`remaining_spare_blocks` (a different, discrete metric tracking physically failed/retired NAND
blocks) *does* show real variance (5/298 sites below 100%, down to 93% on `rollah-smc01`) — proves
the pipeline can and does report differentiated data, it's specifically the erase-life percentage
that's precision-starved (a coarse whole-number field) at this fleet's current usage level, not
broken.

A plan to add real, currently-useful usage metrics
(`docs/smartmon-active-disk-value-fix-plan-20260713_1310.md` Part 2 — **not yet approved**) would
extend `sbdm.py` to also publish `average_erase_count`, `total_erase_count`, `power_on_cycles`, and
a computed `estimated_remaining_lifetime_perc` (full float precision instead of Swissbit's coarse
integer) — none of which `sbdm.py` currently publishes despite the raw `sbdm-cli` CSV output already
containing them.

**Also found**: 4 RPi nodes (`malupirti-smc01`, `orrtipa-thurra-bonya-smc01`, `rocket-bore-smc01`,
`yuelamu-smc01`) genuinely lack overlayroot — root mounted directly from `/dev/mmcblk0p2 ext4`, a
real writable device, not the `overlayroot` pseudo-source seen on the rest of the RPi fleet.
Operator-confirmed 2026-07-13: these are recently-replaced SMCs, expected to lack overlayroot at
this stage, not itself an urgent finding — but a real, live example of exactly the write-exposure
this project exists to catch, worth revisiting once these units complete their overlayroot rollout.

### Mismatched Transcend SSD pairs on BOXER-6641 — now a recurring pattern (3 nodes confirmed 2026-07-17→2026-07-21)

Three rcp nodes discovered live in Teleport outside the original 12-node ansible-wifi inventory
(beagle-bay-smc01, pandanus-park-smc01 2026-07-17; old-looma-smc01 2026-07-21) all run BOXER-6641
chassis with a **mismatched Transcend SSD pair** — `TS128GSSD472K` and `TS128GSSD460KI-VS1` on the
same node, one active one standby, roles swapped between nodes (beagle-bay: active=472K,
standby=460KI-VS1; old-looma: active=460KI-VS1, standby=472K) — unlike the 4 fleet-standard
BOXER-6641 nodes (mornington, bidyadanga, horn-island, warburton), which run a matched
`TS128GSSD420K` pair. Worth treating as an expected trait of nodes provisioned outside the main
ansible-wifi rollout, not a per-node anomaly to re-investigate each time. `Wear_Leveling_Count`
raw=0 on both old-looma disks (near-new) at first audit.

### Same 3 nodes: `smartmon.py`'s `remaining_lifetime_perc` didn't publish — fixed 2026-07-21 (attribute-169 name-resolution gap, not a hardware limitation)

Found 2026-07-17, root-caused and fixed 2026-07-21: beagle-bay's/old-looma's Transcend pair
(`TS128GSSD472K`/`TS128GSSD460KI-VS1`) and pandanus-park's Transcend CFast (`TS64GCFX600`) — the
same 3 non-standard models from the section above — all report SMART attribute id **169** as
smartctl's generic `Unknown_Attribute` placeholder rather than a resolved name, because these
specific models aren't in smartctl's drivedb. This is a *different* limitation from the original
Transcend `VALUE`-column bug (Part 1, 2026-07-13 — that one affected `TS128GSSD420K` and was about
the VALUE column being uniformly wrong, not about name resolution) — don't conflate the two when
triaging a "wear metric missing" report on this fleet; check which failure mode it actually is
before assuming it's already covered by Part 1.

Fixed at the collector (`roles/smc_node_exporter/files/smartmon.py`, `collect_ata_metrics`): before
the whitelist-skip check, rewrite the id-169 `Unknown_Attribute` placeholder to
`remaining_lifetime_perc`, scoped narrowly (both the id **and** the placeholder name must match) so
any drive smartctl already resolves correctly (e.g. Innodisk CFast 3ME3, unaffected) is untouched.
Deployed live via `smc_prometheus.yml --tags node_exporter` to all 3 affected nodes, confirmed
end-to-end in central Prometheus (beagle-bay 100%/100%, pandanus-park 99% — matching the
previously manually-recovered figures exactly). `smartmon.py` remains **uncommitted** in
ansible-wifi. See `docs/log-audit-results.md` `20260721_1830` in smc-file-writing-analysis for the
full live-verification narrative.

**Correction (live `tsh ssh` root-cause 2026-07-23, `disk-write-rates-20260723.md` Live Audit Addendum):**
the "all 3 affected nodes" claim above held for **beagle-bay and pandanus-park only**. The two looma nodes
are both unpublished but for **entirely different reasons — don't treat them as one gap:**

- **old-looma-smc01** (same `TS128GSSD472K`/`TS128GSSD460KI-V` Transcend pair): its `/usr/local/lib/smartmon.py`
  is still the **pre-fix version** — no id-169 rewrite present (grep for `169`/`Unknown_Attribute` returns
  nothing). The 07-21 fix was **never actually applied here** (the confirmation only ever cited
  beagle-bay/pandanus-park values, never old-looma's). `smartctl -A /dev/sda` attr 169 = `Unknown_Attribute`
  RAW=100 → real wear **100%**, data present, just unnamed. **Secondary bug:** old-looma publishes
  `smartmon_active_disk_remaining_lifetime_perc 0.0` — a **false 0%** (the gauge defaults to 0.0 when the
  per-attribute value can't be resolved, instead of going absent — could trip a wear alert). **Fix:** redeploy
  the already-fixed `smartmon.py` via `smc_prometheus.yml --tags node_exporter`; no new code needed.
- **new-looma-smc01** (BOXER-6404, **standard Innodisk CFast 3ME3**): **no monitoring stack at all** —
  `node_exporter` inactive, no textfile_collector dir, `smartmon.py` absent, no Graylog sidecar, no tmpfs
  mounts, overlayroot disabled, plain LVM root. Ungoverned node. Its Innodisk disk resolves attr 169 natively
  (`Remaining_Lifetime_Perc VALUE=099` → **99%**), so it needs **no collector code fix** — just the standard
  ansible-wifi onboarding + full 12-fix stack. Its 446 MB/day is an idle-baseline, not a fixed-state figure.

### `fatrace` not installed on ungoverned nodes — audit-methodology gotcha (found 2026-07-21, old-looma-smc01) — standing fix: install it, don't just substitute

Every prior live audit in this project used `fatrace`'s 60s true-write count as the primary
write-rate evidence (see `AGENTS.md` "Live Audit Procedure"). `fatrace` is installed as part of the
ansible-wifi rollout, not present on the base OS image — a node discovered live but never touched
by any ansible-wifi playbook (old-looma-smc01, first case found) will not have it. Don't assume
fatrace availability when auditing a node without confirmed ansible-wifi history — check
`which fatrace` first before spending time on a filter/capture command that silently returns
nothing.

**Standing policy as of 2026-07-21: install it, don't just work around it.** `apt-get install -y
fatrace` on any rcp node found missing it, then re-run the standard 60s true-write capture — do not
settle for the `iostat -xd <interval> <count> <device...>` per-device substitute as a final answer,
it gives directional evidence only (no per-process attribution). On old-looma-smc01 the install was
a clean one-package `apt-get` (`fatrace_0.16.3-1`, pulled in `powertop` as a dependency, no service
restarts triggered) — confirmed low-risk on a plain rw-ext4 rcp node. The real fatrace capture after
install surfaced a write surface the iostat-only pass had missed entirely: `python3` writing 24
times/60s to `/var/local/cnmaestro-provisioning/` (130M, 116 files) — a path this project's own
`AGENTS.md` inventory had listed at the wrong location (`/var/log/cnmaestro-provisioning/`, which
doesn't exist on this node), now corrected. Same lesson as the `iostat`-only limitation above: a
substitute methodology doesn't just lose precision, it can miss entire write surfaces that only
show up in a true per-process syscall trace.

### Verifying 12-fix parity on-box — two probe gotchas + what "healthy" looks like (2026-07-22)

When re-auditing whether the fleet's write-reduction fixes are actually applied on a node (as
opposed to trusting a deployment recap), check each fix's **durable on-box artifact** — the mount,
symlink, masked unit, journald drop-in, or published metric — not the ansible run result. Two
naive probes give false negatives; use the corrected form:

- **Fluent Bit is NOT a standalone systemd unit on this fleet.** `systemctl is-active fluent-bit`
  returns inactive even when it is running correctly. Fluent Bit is spawned as a **child process of
  `graylog-sidecar`** (`/opt/fluent-bit/bin/fluent-bit -c
  /var/lib/graylog-sidecar/generated/<id>/apn-gelf-http.conf`). Verify with `pgrep -a fluent-bit`
  (or confirm it appears under the sidecar cgroup in `systemctl status graylog-sidecar`), never with
  `systemctl is-active`.
- **`apt_info.py` lives at `/usr/local/lib/apt_info.py`** (confirmed on beagle-bay/pandanus-park/
  old-looma), not `/var/lib/node_exporter/` or `/usr/local/bin/`. A locator that guesses the wrong
  directory will make a "no live `cache.update()`" check pass vacuously. Locate with
  `find / -name apt_info.py` first, then `grep -nE '^[^#]*cache\.update\(\)'` on the real path — the
  only legitimate occurrence is the explanatory comment, so any *uncommented* hit is a regression.

Other durable signatures (all `findmnt -rno FSTYPE <path> | grep tmpfs` or `systemctl is-enabled
… | grep masked`): journald `Storage=volatile` drop-in under `/etc/systemd/journald.conf.d/`;
`url-capture.service` active + `/run/url_capture` tmpfs (**unit name is `url-capture`, hyphen, not
`url_capture`**); `status.json` a symlink; `apt-daily`/`apt-daily-upgrade`/`apt-news`/`esm-cache`/
`unattended-upgrades` all `masked`; `/tmp`, `/var/lib/node_exporter/textfile_collector`,
`/var/lib/prometheus` all tmpfs; `remaining_lifetime_perc` present in
`textfile_collector/smartmon.prom`.

**What a healthy post-fix rcp node looks like in a 5-min fatrace capture (2026-07-22, all 3 new
nodes):** none of the 12 fixes' target surfaces appear anywhere in the top writers — no apt/gpgv
churn, no url_capture `.pcap`, no prometheus WAL/TSDB, no `status.json`, no textfile `.prom` hitting
disk. The residual top writers are the **fleet-wide known-open backlog**, not regressions:
`/var/log/syslog` (rsyslogd, dominant — rcp has no overlayroot so it writes straight to ext4; the
rsyslog 3-group split + Fluent-Bit-systemd-input migration per ADR-006 is the next disk-reduction
target, not one of the 12 fixes), `squid/access.log` and `mosquitto.log` (drafted-not-deployed
STOP/STREAM dispositions), `interfacecheck.log` (parser-bug writer, fix committed `ae838c2`, deploy
deferred), and `asterisk/astdb.sqlite3-journal` (SQLite WAL churn, low, LOCAL-KEEP-class). Totals
landed 1070–1627 true-writes/300s, in-family with the governed fleet's 538–1624 range — so a node
sitting in that band with syslog/squid/mosquitto on top is behaving normally, not carrying an
undeployed fix. Full evidence: `docs/log-audit-results.md` `20260722_2020`/`20260722_2028`.

---

### NBN Accelerate / NBN WH Hardware Inventory (first live fleet sweep, 2026-08-03)

No live hardware inventory existed for this cluster before this sweep — everything below is from
direct `tsh ssh` capture against all 26 reachable `nbn_accelerate` hosts plus both `nbn_wh` hosts
(28 total, `aurukun-smc03` unreachable at capture time), via `scripts/collect-fleet-health.sh`.
**`nbn_wh` is the operator-confirmed `wh`-flavor equivalent on this cluster** — compare it against
the `rct`/`wh` row in the platform table above, not against `nbn_accelerate`'s x86 baseline.

| Chassis | Count | CPU | RAM | Storage | Flavor | Kernel |
|---|---|---|---|---|---|---|
| AAEON BOXER-6641 | 11 | Intel Core i5-8500T @ 2.10GHz | 15Gi | Transcend TS128GSSD420K SSD | `nbn_accelerate` | `5.15.0-119-generic` (fleet-uniform) |
| AAEON BOXER-6404 | 15 | Intel Celeron J1900 @ 1.99GHz | 7.7Gi | Innodisk CFast 3ME3 | `nbn_accelerate` | `5.15.0-117-generic` (2 outliers — see below) |
| Raspberry Pi, Cortex-A72 (`-raspi` kernel, no dmidecode) | 2 | ARM64, 4-core Cortex-A72 | 7.6Gi | Swissbit SB AFNI0 microSD (`sbdm.prom` populated, `smartmon.prom` header-only — same split as `rct`/`wh`) | `nbn_wh` | `5.15.0-1064-raspi` / `5.15.0-1078-raspi` |

Same BOXER-6641/BOXER-6404 chassis family already documented for the `rcp` fleet (`amata-smc01` was
independently confirmed BOXER-6641 during the earlier disk-fault incident) — this is not new hardware,
just the first time it's been inventoried for this specific cluster.

**Kernel/OS version drift, live-confirmed — corroborates the already-documented "no automated
kernel-update pipeline for cw-cluster" structural finding** (`01_overview.md` "APN Cluster vs NBN
Accelerate Cluster"): most BOXER-6404 hosts run `5.15.0-117-generic`, but `koonibba-smc01` is on
`5.15.0-79-generic` (significantly older) and `warakurna-smc01` is on `5.15.0-133-generic`
(significantly newer) — a wide, organic spread consistent with hosts being patched independently by
hand rather than through a fleet-wide pipeline, exactly as predicted by the earlier structural finding
(apn-cluster has a Jenkins kernel-update pipeline; cw-cluster does not). OS point-release also varies:
`22.04.1`/`22.04.3`/`22.04.4` seen across the fleet, no single dominant version.

**`nbn_wh` swap/zram discrepancy — not yet resolved.** Both `nbn_wh` hosts show `Swap: 0B` in `free -h`
and no `zram0` device in `lsblk`, contradicting the "RPi flavor → zram swap" row in the platform table
above as a universal claim. Not established whether `nbn_wh` genuinely doesn't get zram (a real
flavor-level difference from `rct`/`wh`), or whether the zram claim itself needs re-checking against a
live `rct`/`wh` host — this pack has not directly confirmed zram presence on `rct`/`wh` via `tsh ssh`
either, only asserted it. Flag any zram-dependent troubleshooting step as unconfirmed for `nbn_wh`
until checked.

**`nbn_wh` overlayroot: not yet active, and that's expected — a planned-but-not-yet-executed rollout,
confirmed by the operator 2026-08-03.** `smc_rise_deploy.yml` targets `nbn_wh` alongside `rct`/`wh`
(`inventory_dir.split('/')|last in ['rct', 'wh', 'nbn_wh']`), consistent with `nbn_wh` being the
`wh`-equivalent flavor where overlayroot is the expected long-term state — but live `mount | grep
overlay` on both `nbn_wh` hosts returns nothing today. The operator confirmed this is simply
pre-rollout current state (overlay is planned to be enabled on these 2 sites in the near future), not
a stalled or reverted deployment. Re-check after that rollout lands — see `13_known-issues.md` "Known
Operational Bugs (NBN Accelerate cluster)" for the tracking row.

**Disk usage:** `koonibba-smc01` at 95% root disk usage is the fleet's clear outlier (next highest:
`warakurna-smc01` at 65%; everyone else under 55%, most well under 35%) — combined with its outlier-old
kernel, this specific host looks overdue for a maintenance pass. Not investigated further this sweep
(no directory-level `du` breakdown taken).

Full per-host data: `local-knowledge-ansible/ansible-wifi/issues/nbn-accelerate/fleet-hardware-audit-20260803/`
(relocated from `skill-smc/evidence/` per the evidence-retention policy in `scripts/README.md`).

---

## 8. Overlay Filesystem (Critical Concept)

### Structure

```
/                          ← merged view (what you see at runtime)
├── upper dir: /media/root-rw/overlay   (tmpfs, volatile, ~40% RAM)
├── lower dir: /media/root-ro           (ext4, real filesystem, read-only at runtime)
└── workdir:   /media/root-rw/overlay-workdir/_

Real block device: /dev/sda1 or equivalent → mounted at /media/root-ro (60 GB on RPi)
tmpfs:             size=40% → ~780 MB on 1.9 GB RPi
```

### Runtime Behavior

- All file writes go to tmpfs upper dir
- On reboot: upper dir is gone, lower dir reverts to original state
- `df -h` shows the tmpfs as `/dev/overlay` at `/`; real filesystem at `/media/root-ro`

### Checking Overlayroot Status

```bash
mount | grep overlay     # confirms overlay is mounted
mount | grep root-ro     # confirm lower dir is ro vs rw
df -h                    # check tmpfs headroom
```

### Configuration

```
/etc/overlayroot.conf:
  overlayroot="tmpfs:swap=1,recurse=0"
```

### Ansible + Overlayroot

1. Ansible must remount lower dir rw before making changes that must persist
2. `smc_bases.yml` playbook handles this remount
3. If running a role directly (not via `smc_bases.yml`), verify lower dir is rw first
4. After Ansible completes, confirm change persisted: check file in `/media/root-ro/...`

### Disable Sequence (when needed)

```bash
# 1. Remount lower dir rw
mount -o remount,rw /media/root-ro

# 2. Remove overlayroot config
rm /media/root-ro/etc/overlayroot.conf

# 3. Reboot
reboot

# 4. After reboot: verify overlayroot is gone
mount | grep overlay   # should return nothing
```

**Kernel match required:** `uname -r` must match an entry in `/lib/modules/` on the lower dir. Kernel upgrades without rebooting can cause overlayroot to fail on next boot.

### Read-Only Migration Status (per flavor)

| Flavor | Platform | Root partition | Firmware/boot | Track | Status |
|---|---|---|---|---|---|
| rct / wh | RPi ARM64 | **READ-ONLY** (overlayroot active) | WRITABLE (/boot vfat) | Track B | Root done; firmware pending |
| rcp / nbn_accelerate | x86 | **WRITABLE** (bare ext4, no overlayroot) | WRITABLE (/boot + /boot/efi) | Track A | Primary migration target |

### `smc_disk_failover` role — EFI BootNext mechanism, not a guaranteed live-corruption failover

The role's failover mechanism sets a one-time EFI boot entry (`efibootmgr -n <id>`, "BootNext") to
an alternate disk after a prolonged internet-failure count is observed — it is a **connectivity**
failover trigger, not a storage-health trigger, and it is not guaranteed to run cleanly while the
active disk is under active I/O corruption (EFI tooling itself can fail with `Input/output error`
in that state — confirmed live on amata-smc01, see the storage incident in `06_failure-modes.md`
"Disk Path Failure Forcing Root Read-Only"). If a disk is failing hard enough to force the root
filesystem read-only, do not assume `smc_disk_failover` will cut over automatically — verify EFI
tooling is actually responsive (`efibootmgr -v`) before relying on it, and be ready to set the
one-time boot entry manually or fall back to a BIOS/UEFI console boot to the alternate disk.

### rcp Disk Write Profile (confirmed jigalong-smc01, 2026-04-20; re-confirmed 3 more nodes 2026-07-20)

**2026-07-20 re-confirmation:** live-checked `/etc/overlayroot.conf` (`overlayroot=""`),
`mount | grep overlay`/`root-ro`/`root-rw` (no matches), and `findmnt -T /var/log/syslog` (resolves
to the real root device, `ext4 rw`) on tjuntjuntjara-smc01, mornington-smc01, and jigalong-smc01 —
same result on all 3, no overlayroot anywhere on rcp. This re-confirmation was prompted by
`smc-file-writing-analysis/AGENTS.md`'s "Overlayroot Context" section having drifted to describe
rcp as running overlayroot with a writable lower dir (implying partial RAM buffering) — that
section has now been corrected to match this file, which had the right model all along.

rcp has NO overlayroot — all writes go directly to SSD:
- journald: **3.9GB uncapped** (fix: RuntimeMaxUse=200M on real disk)
- /url_capture/: **~22MB/day** — intentional DNS pcap (dst port 53 on bridge_501)
- /var/lib/squidguard/db/: **665MB** — blocklist databases (LOCAL-KEEP)
- /var/lib/asterisk/: **344MB** — VoIP SQLite + logs
- /var/lib/dhcp/dhcpd.leases: continuous DHCP lease writes
- Prometheus WAL: 2.9MB (real disk, remote_write active)

### url_capture DNS Monitoring Service (rcp only)

> **Superseded by Python streaming service (Section 10).** v2 must be deployed per-node via
> Ansible. Nodes not yet migrated remain on v1 with active crons — do not assume crons are
> removed until confirmed for a specific node.

**Legacy system (active on un-migrated nodes):**
- Script: `/var/local/sslurlcapture/url_capturev1.sh`
- Midnight reset cron: `59 23 * * *` — kills screen session so next start creates new daily file
- Rsync cron: `10 0,8,16 * * *` — ships pcaps to remote (`rsync_urlcapture.sh`)
- Path: `/url_capture/YYYYMM/<hostname>-<iface>-YYYYMMDD-0000.pcap`
- Rate: ~22MB/day accumulated locally; shipped up to 8h late

**Known rsync behaviour (rsync_urlcapture.sh.j2):**
- Excludes the newest file in the sync dir — protects the active tcpdump capture from partial transfer
- This means the last file of each month is delayed by one rsync cycle after a new month starts
- Fix applied 2026-05-01: `yearmonth_today` was a literal string (missing `$()`); now fixed plus
  a conditional block syncs the current month dir on the 1st when today ≠ yesterday month

---

### fatrace write-rate audits: filter bug — RO/RC/RCO counted as writes (2026-07-09)

`fatrace` event codes: `R`=read, `O`=open, `C`=close, `W`=write. Only codes containing `W`
(`W`, `WO`, `CW`, `CWO`, `RW`) are real writes. A filter of `grep -v ': R '` excludes only the
bare `R` event — it lets `RO`/`RC`/`RCO` (read-open/read-close/read-close-open — all still just
reads, no write) through as if they were writes. Every shared-library load during process exec
(`ld.so.cache`, `libc.so.6`, `locale-archive`) fired by routine cron `sh`/`stat`/`grep`/`dash`
spawns gets miscounted this way — confirmed on smc-file-writing-analysis fleet checks: on a 60s
capture, one node showed 6,029 events passing the old filter but only 59 were true writes (~100x
inflation). Correct filter: `grep -E ': (W|WO|CW|CWO|RW) '`.

**Fleet-wide `*/5`, `*/2`, `*/1` cron schedule (identical via Ansible) means any capture window
of a few minutes will always catch a full interfacecheck/apt_info/Kohana/mqtt-client cycle** —
a burst of activity at that moment is normal steady-state, not an anomaly, and does not on its
own indicate a regression.

**Phase 3 effectiveness re-confirmed with the corrected filter:** Phase 3 node (journald volatile
+ Fluent Bit pos tmpfs + sidecar redirect) showed 0 `systemd-journal` write events in a 60s true-write
capture; a non-Phase-3 node showed 32 direct writes to `/var/log/journal/.../system.journal` in the
same window, and ~3.7x more total true writes overall. Full detail:
[log-audit-results.md](../../../../../../_project/project_stuff/apn/smc-file-writing-analysis/docs/log-audit-results.md)
(2026-07-09 12:37 AEST entry). `scripts/wear_fatrace_remote.sh` in that project was corrected to
use the true-write filter.

---

### fatrace write counts measure syscalls, not physical disk I/O (2026-07-15)

Even with the true-write filter above, a `fatrace` event count is **not** a physical-disk-write
count or an SSD-wear figure — it's a write-*syscall* count. `fatrace` logs every individual
`write()` call as its own event, and processes that stream data through in small buffered chunks
(confirmed: `gpgv`, verifying apt package-list signatures) generate dozens of events for one
logical operation — one `/tmp/apt.data.*` temp file showed 29 separate `W` events plus 1 `CW` for
a single download-verify pass, in just an 80-line raw sample slice.

The kernel buffers small `write()` calls in page cache and coalesces them before an actual physical
flush (delayed writeback, ~30s default `dirty_expire_centisecs`). Short-lived temp files — created
and deleted within seconds, like apt's staging files — may never fully reach physical media before
being overwritten or removed. So a fatrace count systematically **overstates** physical wear for
syscall-heavy buffered-write files, and is closer to accurate for writers that `fsync`/`O_DIRECT`
on every write (databases, journals).

**How to apply:** treat fatrace counts as a relative/comparative signal (did this go up or down
after a fix) and a lock-contention/CPU-churn proxy — never as a literal physical-write or SSD-wear
number. Comparing counts captured with different methodologies (e.g. a 60s×5-sampled full total
vs a continuous-window top-N-sum) is also invalid — they're different metrics, not just different
samples of the same one. Full detail:
[smc-file-writing-analysis/.archcore/rules/RULE-011-fatrace-write-count-syscall-not-physical-io.md](../../../../../../_project/project_stuff/apn/smc-file-writing-analysis/.archcore/rules/RULE-011-fatrace-write-count-syscall-not-physical-io.md).

### fatrace excludes tmpfs entirely — every sweep in this project is real-disk-only (confirmed 2026-07-24)

`fatrace` on rcp SMC nodes **never reports writes to tmpfs-mounted paths** — `/tmp`, `/run`,
`/var/lib/prometheus`, `/var/lib/fluent-bit/pos`, `/var/lib/node_exporter/textfile_collector`,
`/var/log/smc-groups` (and anything symlinked onto it, e.g. `squid`/`interfacecheck`) are all
invisible to it, even though `fatrace`'s own man page/`--help` don't call this out explicitly and
expose no fstype-include/exclude flag. Confirmed live on tjuntjuntjara-smc01: a background
`fatrace --timestamp --filter=W` capture caught a real-disk write to `/root/mytestfile.txt`
(`CW /root/mytestfile.txt`) but produced zero output for the identical `echo`/`echo >>` write
pattern against `/tmp/mytestfile.txt` in the same window, with `findmnt` confirming the fstypes
(`ext4` vs `tmpfs`) as expected.

**How to apply:** every fatrace-derived top-writer list or `write_count` in this project — this
sweep's or any historical one in `docs/fatrace-sweep-history.csv` — is a **real-disk-write list
only**. This is the correct scope for the project's read-only-migration goal (only real SSD/CFast
writes matter), but it means fatrace **cannot** answer "is a tmpfs mount under write pressure" —
use `du -sh`/`df -h` on the mount, or the `node_filesystem_*` Prometheus metrics enabled fleet-wide
2026-07-23, for that question instead. Do not read a fatrace sweep's silence on
prometheus/tmp/squid/interfacecheck as those paths being idle — they aren't, fatrace simply can't
see them. Full detail:
[smc-file-writing-analysis/.archcore/rules/RULE-014-fatrace-excludes-tmpfs-real-disk-only.md](../../../../../../_project/project_stuff/apn/smc-file-writing-analysis/.archcore/rules/RULE-014-fatrace-excludes-tmpfs-real-disk-only.md).

---

---

## Orphaned persistent journal after the volatile conversion (~44 GB fleet-wide, reclaimed 2026-07-28)

Once journald is `Storage=volatile` it writes to `/run/log/journal` and **never touches `/var/log/journal` again**. Any persistent journal left behind from before the conversion is therefore
**inert dead weight on the SSD/CFast that nothing will ever reclaim on its own** — it does not shrink, rotate, or get vacuumed.

Found across the rcp fleet 2026-07-28: **~43,952 MB total.** ~4.1–4.3 GB each on kalumburu, mowanjum, guda-guda, jigalong, umoona, horn-island, bidyadanga, warburton, beagle-bay and
pandanus-park; 1.9 GB on old-looma; 153 MB on new-looma. On a 64 GB BOXER-6404 CFast that is ~6.6% of the device, permanently consumed.

**Where the gap came from.** Only four nodes were clean (1 MB) — tjuntjuntjara, burringurrah, wujal-wujal, mornington — which are **exactly the 2026-06-30 first Phase 3 cohort**. That deploy
reclaimed the pre-existing journal; every later Phase 3 rollout (07-10, 07-14, 07-21, 07-23) did not. The gap would have recurred on every future onboarding, so the cleanup is now a task in
`smc_system` rather than a manual step.

### `journalctl --vacuum-*` cannot do this job

This is the trap. journald does not manage `/var/log/journal` once volatile, so vacuum reports **`freed 0B` for that path while happily vacuuming the RAM journal instead**. Verified live on
new-looma 2026-07-28: `journalctl --vacuum-time=1s` freed 192 MB from `/run/log/journal` and 0 B from the actual target — i.e. it destroyed recent journal history in RAM and achieved nothing
against the disk residue. Removing the directory is the only thing that works.

### Safe reclaim procedure

1. Confirm journald is *genuinely* volatile at runtime — `/run/log/journal` must exist. Do **not** rely on the config file saying `Storage=volatile`; a node that has not restarted journald yet
   is still writing persistently, and deleting its journal would destroy live logs.
2. Confirm no open handles: `lsof +D /var/log/journal` should be 0.
3. Remove the directory. Removing it (rather than emptying it) also hardens against a future `Storage=auto`, which only uses persistent storage if `/var/log/journal` exists.
4. Verify after: directory absent, `systemd-journald` active, `/run/log/journal` present and capped, and a `logger` round-trip visible in `journalctl` — proving logging still works end to end.

Canary result (kalumburu, 4.1 GB): 37 G → 41 G free, 32% → 24% used, all checks green. Fleet result: all 16 nodes clean, journald active, runtime journal at its 200 M cap, disk used 12–25%.
````

## File: references/08_ansible-authoring.md
````markdown
# SMC Ansible Authoring

## Contents
- Operational learning capture
- Flavor/cluster conditional branching (selector reference)
- smc_ltp sub-group (CNMaestro backhaul provisioning + DNS architecture switch)
- "Low touch" onboarding method and site deployment history
- IPv6 disable policy
- Skill runtime paths
- Canonical source rules
- Topology change workflow
- Variable rename / refactor workflow
- Cache coherence rules
- Inventory path convention
- Cross-branch file fetch tool
- Playbook run safety
- Validation command reference

## 9. Ansible Authoring Workflows

### Operational Learning Capture (Mandatory)

For any SMC incident/debug fix in `ansible-wifi` that changes behavior, defaults, or troubleshooting assumptions:

1. Update the relevant focused reference in this specialist pack during the same work session.
2. Add a short entry under troubleshooting/failure-mode sections with:
   - exact error signature
   - root cause class
   - source-of-truth file path(s)
   - fix pattern
   - validation command(s)
3. Treat the reference update as part of done criteria for the task, not optional follow-up.

### Flavor/Cluster Conditional Branching (Selector Reference — 2026-08-03)

**No role branches on cluster identity (`cw`/`community`/`communitywifi`/`apn`) directly.** Every
flavor-conditional found repo-wide keys off one of two variables, both derived from the inventory
folder name:

- `hotspot_flavor` — hardware-class selector, groups `{rct, wh, nbn_wh}` as "big box" (overlayroot +
  GPS + telemetry) vs `{rcp, nbn_accelerate}` as "small box". This spans **both** clusters — it is a
  hardware split, not a cluster split. Used in `roles/smc_teleport/templates/teleport.yaml.j2` and
  `roles/smc_system/tasks/main.yml`.
- `inventory_dir.split('/')|last` — exact flavor name (`rcp`, `rct`, `wh`, `apn`, `cw`,
  `nbn_accelerate`, `nbn_wh`). Used for flavor-exclusive role gates.

**Confirmed flavor-exclusive gates (not hardware-driven):**

| Gate | Condition | Effect |
|---|---|---|
| `smc_bases.yml` ClamAV + Lynis | `inventory_dir.split('/')|last == 'nbn_accelerate'` | Security hardening applied only on cw-cluster's small-box flavor — no apn-cluster equivalent (`rcp` does not get this). **Live-confirmed at full fleet scale 2026-08-03** (26/26 reachable `nbn_accelerate` hosts): both packages installed on every host, all uniformly `clamav 0.103.11`/`.12`. **Root cause confirmed 2026-08-03**: ClamAV 0.103.x reached end-of-life for database updates on 2025-09-14, and its CDN now hard-blocks `freshclam` from any 0.103.x client (HTTP 403) — every host is affected, fix is a version upgrade, not a retry. See `13_known-issues.md` "Known Operational Bugs (NBN Accelerate cluster)" for full detail. |
| `smc_rise_deploy.yml` RISE/overlayroot rollout | `inventory_dir.split('/')|last in ['rct', 'wh', 'nbn_wh']` | `nbn_wh` is explicitly a RISE-rollout target alongside `rct`/`wh` — the mechanism that (eventually) enables overlayroot on RPi-class flavors. **Live-confirmed 2026-08-03**: overlayroot is NOT YET active on either `nbn_wh` host — operator confirmed this is a planned-but-not-yet-executed rollout, not a stalled deployment or code gap. `nbn_accelerate`/`rcp` are never targeted (they don't use overlayroot at all — bare ext4, per `07_hardware-overlay.md`'s "Read-Only Migration Status" table). |
| `smc_bases.yml` VoIP (Asterisk) | `inventory_dir.split('/')|last == 'rcp'` | Asterisk + firewall rules (SIP 5060, RTP 10000-20000, Cambium TFTP 69) — apn-cluster exclusive, never applied on `nbn_accelerate`/`nbn_wh` |
| `smc_qos` role | `inventory_dir.split('/')|last == 'rct'` | QoS role exists but silently no-ops on `rcp`/`nbn_accelerate`/`wh` — see `13_known-issues.md` |
| `smc_ltp` sub-group (CNMaestro backhaul + DNS switch — see below) | `'smc_ltp' in group_names`; group membership from `inventories/rcp/prod` (static INI), vars from `inventories/rcp/group_vars/smc_ltp.yml` | `rcp`-only (apn-cluster), no cw-cluster equivalent |

**`smc_autossh` cluster/Teleport-endpoint selection.** `roles/smc_autossh/tasks/main.yml` copies
pem/key files from `roles/smc_autossh/files/{{ teleport_fqdn }}/...`. `teleport_fqdn` is set in
`smc_bases.yml` from the per-inventory group_var `smc_bases_teleport_fqdn`
(`inventories/{rcp,rct,wh}/group_vars/smc_bases.yml` → `teleport.apn.au`;
`inventories/{nbn_accelerate,nbn_wh}/group_vars/smc_bases.yml` → `teleport.communitywifi.net.au`).
Individual hosts can override further (e.g. a host_var pointing at `teleport.apntest.au` or
`telestage.communitywifi.net.au` for staging). This is a **pure SSH-endpoint selection** — nothing
else in the `smc_autossh` role, or in `smc_graylog`/`teleport_core`/`jenkins_core`, branches on
cluster identity; only the *values* (graylog server URL, teleport fqdn, jenkins fqdn) differ via
group_vars, following the identical pattern on both clusters.

**When authoring a new cw-cluster-specific task**, follow the same
`inventory_dir.split('/')|last == '<flavor>'` pattern as the ClamAV/Lynis and VoIP gates above — do
not introduce a new `cw`/`community` string check, since no existing code does that and it would be
an inconsistent selector. See `01_overview.md` "APN Cluster vs NBN Accelerate Cluster — Structural
Comparison" for the full cross-cluster comparison this section supports.

---

### smc_ltp Sub-Group — CNMaestro Backhaul Provisioning + DNS Architecture Switch (documented 2026-08-03)

Previously under-explored: earlier passes only captured `smc_ltp`'s DNS-gating side effect (see
`02_service-map.md`) and mislabeled it as "cnMaestro mDNS" in the summary tables above. It is not
mDNS-related at all. Direct read of `smc_ltp.yml`, `inventories/rcp/group_vars/smc_ltp.yml`,
`inventories/rcp/prod`, `roles/smc_cnmaestro_provisioning/`, and `roles/smc_dns_mgmt/tasks/main.yml`
gives the full picture:

**Membership.** `smc_ltp` is a **static** Ansible group defined in `inventories/rcp/prod` (INI
inventory — not generated by `topology_vars.py`, so it will not show up in a `topology_vars/*.yml`
review). 7 `rcp` sites are members, each via a per-site `<site>_smc_ltp` child group: `guda-guda`,
`pandanus-park`, `old-looma`, `new-looma`, `warburton`, `beagle-bay`, `umoona`. `rcp`-exclusive — no
other flavor (`apn`, `rct`, `wh`, `cw`, `nbn_accelerate`, `nbn_wh`) defines an `smc_ltp` group or any
`smc_ltp_*` var. **Corrected 2026-08-03 (same day, twice)**: first found 4 members from direct
`inventories/rcp/prod` read; operator then confirmed the group is meant to track every "low touch"
onboarding site (see below) and directed adding the 3 that were missing (`warburton`, `beagle-bay`,
`umoona`) — a real inventory gap, not a re-read miss. Verified via `ansible-inventory -i
inventories/rcp/prod --playbook-dir . --list` (`smc_ltp:children` lists all 7) and `ansible-playbook -i
inventories/rcp/prod --syntax-check smc_ltp.yml` (clean). File-level Ansible inventory change,
uncommitted as of this edit — not yet run against any live SMC; adding a host here makes it *eligible*
for the `dns_mgmt` play and `smc_ltp.yml` on the next real run, it does not trigger anything itself.

**Purpose 1 — CNMaestro wireless backhaul/CPE provisioning.** A standalone top-level playbook,
`smc_ltp.yml` (separate entry point from `smc_bases.yml`), targets `hosts: smc_ltp` and runs the
`smc_cnmaestro_provisioning` role (`roles/smc_cnmaestro_provisioning/files/cnmaestro-provisioning.py`)
against `smc_ltp_cnmaestro_provisioning` (defined in `inventories/rcp/group_vars/smc_ltp.yml`). This
auto-provisions Cambium wireless equipment via the CNMaestro cloud API: cnPilot r195P (home CPE),
XV2-2T0/XV2-22H (indoor/outdoor enterprise AP), ePMP Force 300-16/300-25 (SM/AP backhaul radios, incl.
EP2P mode), and ePMP 3000L — auto-allocating management/provisioning IP ranges (`10.255.x.x`,
`192.168.254.x`, `10.0.x.x`), SSID prefixes (`WifiBridge_`, `WifiP2P_`), and per-model config
templates. Some LTP hosts override branding at the host level (e.g. `whprov-smc01.yml` uses
`WHProv`-prefixed SSIDs instead of the group default). `smc_bases_teleport`/iptables plays in
`smc_bases.yml` also reference `smc_ltp_cnmaestro_address|default('')` as a harmless empty default on
non-LTP hosts — this is not evidence LTP applies fleet-wide, just a shared var namespace.

**Purpose 2 — DNS resolver architecture switch.** `smc_bases.yml`'s `dns_mgmt` play
(`hosts: smc_ltp`) runs `smc_dns_mgmt`, which stops+masks `unbound` if it holds port 53, installs
`bind9`, and deploys `named.conf.local` + an RPZ zone file **literally named `db.cambium-rpz`** — the
filename itself ties this DNS switch directly to the Cambium wireless-backhaul context above, most
likely so the private management/provisioning IP ranges used by the ePMP/cnPilot mesh (which will
never resolve via public DNS) get a local zone. This *replaces* the unbound+stubby DNS-over-TLS setup
every other host gets — see `02_service-map.md` for the full DNS-resolver comparison.

**`smc_dhcpd` LTP-specific fix.** `roles/smc_dhcpd/tasks/ubuntu.yml` has an apparmor-profile-removal +
service-user block gated `when: "'smc_ltp' in group_names"` — runs `isc-dhcp-server` as root instead
of the default `dhcpd` user on LTP hosts, unrelated to the DNS or CNMaestro purposes above.

**Open question — the acronym.** "LTP" is not expanded anywhere in the codebase (no comment, no
README, no commit message found). Functional purpose is well-evidenced from code; the literal meaning
of the letters is not — do not guess/state one as fact without an operator confirmation.

---

### "Low Touch" Onboarding Method and Site Deployment History (operator-confirmed 2026-08-03)

**Not previously documented anywhere in this pack.** Operator supplied install dates for a specific
cohort of `rcp` sites, confirming these were deployed via a named **"low touch" onboarding method**:

| Site | Install date | `smc_ltp` member? |
|---|---|---|
| **guda-guda** | **2025-04-15 — pilot site**, a full year before the next low-touch site | Yes |
| Horn Island | 2025-11-23 (not low-touch — predates the method's next use, listed for timeline context only) | No |
| Umoona | 2026-04-12 | Yes (added 2026-08-03, see below) |
| Warburton | 2026-05-02 | Yes (added 2026-08-03, see below) |
| Beagle Bay | 2026-05-12 | Yes (added 2026-08-03, see below) |
| Pandanus Park | 2026-06-17 | Yes |
| Old Looma | 2026-07-16 | Yes |
| New Looma | 2026-07-25 | Yes |

**Resolved 2026-08-03 (link confirmed, not coincidental).** Initially only 4 of the 7 low-touch sites
showed up in `smc_ltp` (`guda-guda`, `pandanus-park`, `old-looma`, `new-looma`); `umoona`/`warburton`/
`beagle-bay` were flagged as a possible-but-unconfirmed correlation. Operator confirmed directly: every
low-touch site is meant to be an `smc_ltp` member, and the 3 missing ones were a plain inventory gap —
not a coincidental overlap of two unrelated rollout decisions. Fixed by adding
`warburton_smc_ltp`/`beagle-bay_smc_ltp`/`umoona_smc_ltp` child groups to `inventories/rcp/prod`'s
`smc_ltp:children` block, operator-directed. **Mechanism confirmed 2026-08-03 (same day, third
correction): it's a manual step someone has to remember** — low-touch onboarding tooling does not
itself assign `smc_ltp` group membership; a human has to add the site to `inventories/rcp/prod`
separately, with no automated check that it happened. This directly explains how 3 of 7 sites ended up
missing in the first place — a manual, un-enforced step is exactly the kind of thing that silently
drops during a busy onboarding. **Operational implication:** when a new low-touch site is onboarded,
adding it to `smc_ltp:children` is not automatic — confirm it explicitly (e.g. `ansible-inventory -i
inventories/rcp/prod --list | grep -A1 smc_ltp`) rather than assuming low-touch deployment alone
guarantees group membership.

**What "low touch" means in Ansible code terms: currently nothing.** Repo-wide grep for
`low_touch`/`low-touch` in `ansible-wifi` finds exactly one hit: `smc_bases_low_touch_provisioning:
true` in `inventories/rcp/host_vars/pierre-rcp01.yml` — and **no role or playbook anywhere reads that
variable**. It is a set-but-never-consumed host_var. **Do not conflate this with the operator's "low
touch" onboarding method above** — `pierre-rcp01` is not in the low-touch site cohort the operator
described, and the var's naming proximity is likely coincidental (or a vestige of an earlier/different,
possibly not-yet-implemented automation attempt) rather than evidence the method is Ansible-encoded.
The actual "low touch" method, whatever it consists of operationally, currently leaves no trace in
Ansible logic that this pack has found — it is an operational/process distinction, not (yet) a code
path.

**Confidence / evidence basis:** site list and dates are operator-provided, cross-referenced against
independently-observed netplan/hook render timestamps in the routing-issue investigation (which land
1-92 days after each site's operator-given install date — consistent with "installed then later
touched by unrelated remediation work", not a contradiction). The `smc_ltp`-overlap observation and the
orphaned `smc_bases_low_touch_provisioning` var are this session's own direct-grep findings. See
`13_known-issues.md` for the now-resolved history of this correlation (initially flagged as unconfirmed,
then operator-confirmed and fixed same day).

---

### Isolated jinja2 Testing Is Not Proof of Ansible's Real Templating Behavior (`regex_replace` backreferences — 2026-07-29)

**The rule:** for any `regex_replace` (or similarly escaping-heavy filter) that uses a backreference (`\1`), do not trust an isolated `jinja2.Environment().from_string()` test as proof the same
expression will behave identically inside `ansible-playbook`. Only a real `ansible-playbook --check --diff -v` against a live host counts as validation for escape-sensitive template expressions.

**How it bit us:** `roles/smc_network/tasks/ubuntu.yml` needed a filter to build the list of expected `dhclient.<name>.conf` filenames from `interfaces|dict2items`, for a find/delete-extraneous
cleanup pass (routing-issue investigation, `apn/routing-issue/docs/smc-network-idempotency-gap-20260729_1958.md`). Two attempts, both validated in isolation, both wrong in a real run:

1. `map('regex_replace', '^(.*)$', 'dhclient.\1.conf')` — single backslash. Isolated testing caught that Jinja2's string-literal lexer converts `\1` to an octal escape (`chr(1)`) before the regex
   engine ever runs — clearly broken, not the interesting failure.
2. `'dhclient.\\1.conf'` — double backslash "fix". Re-tested in isolation with the same `jinja2.Environment()` harness, using the exact same interpreter Ansible itself uses, and got the correct
   filenames. Declared fixed. **It was not.** A real `ansible-playbook --check --diff -v` against a live Pandanus Park box showed `dhclient_conf_keep` resolving to eight copies of the literal,
   un-substituted string `dhclient.\1.conf` — Ansible's actual Jinja/regex_replace evaluation differs from what an isolated `jinja2.Environment()` test shows for identical source text. Had this
   shipped, the delete task (`when: item.path|basename not in dhclient_conf_keep`) would have matched and deleted **all 16 files, including all 8 real, currently-active interfaces**
   (`enp1s0`, `enp2s0`, `vlan521/522/531/532/621/631`) — confirmed via the `--diff` output, not inferred.

**Fix:** avoid the escaping question entirely — rebuild as a task-level loop with `~` string concatenation instead of `regex_replace`:
```yaml
- name: Determine expected /etc/dhcp/dhclient.<interface>.conf filenames
  set_fact:
    dhclient_conf_keep: "{{ dhclient_conf_keep + ['dhclient.' ~ item.value.name ~ '.conf'] }}"
  when: item.value.role|default('none') in ['internet', 'starlink']
  loop: "{{ interfaces|dict2items }}"
```
`~` concatenation has no escaping layer to get wrong — there is no backslash for any templating pass to reinterpret. Re-ran the identical live `--check --diff` and confirmed `dhclient_conf_keep`
built up to exactly the real interface filenames, correctly sparing them while flagging only the genuine orphans.

**General lesson:** "I tested the Jinja2 expression in isolation and it produced the right string" is not validation for anything involving backslash escaping — Ansible's own templating layer
(env markers, `AnsibleUnsafeText`, filter plugin wrapping) can diverge from vanilla `jinja2.Environment()` behavior for the same source text. Prefer concatenation (`~`) or list-building filters
over `regex_replace` backreferences wherever a simpler construct can do the same job — and when a backreference is unavoidable, validate it live before trusting it.

**The architectural gap underneath this bug, worth stating on its own:** one templated artifact being self-cleaning does not imply a sibling artifact rendered by the same role is too — each
generated file's lifecycle has to be audited independently. `roles/smc_network/tasks/ubuntu.yml` already had a correct find/delete-extraneous pattern for netplan (`00-ansible.yaml` is a
single fully-overwritten file, plus an explicit find+delete pass for any other stray `.yaml`), so it looked idempotent. But the *separate* per-interface `dhclient.<name>.conf` files it also
renders (one `copy` task per interface, gated on `role == 'internet'`/`'starlink'`) had no equivalent cleanup anywhere in the role — proven live, files over a year stale on every affected site.
Before assuming a role is idempotent on removal because you've verified one of its outputs, check every distinct file/artifact it templates separately; `grep` for every `copy`/`template` task in
the role and ask "what deletes this when its `when:` condition stops matching" for each one individually. (Currently low-stakes here specifically: `dhclient@<iface>.service` is only ever
instantiated by `networkd-dispatcher` when the netplan device is real, so an orphaned conf file with no matching interface is inert clutter today — see `03_communication-flows.md` — but the gap
itself is the kind of thing that makes future "is this file real?" audits unreliable, independent of whether it's currently harmful.)

**Topology-cloning risk — confirmed live, not hypothetical.** When a new site's `topology_vars/<site>.yml` is authored by copying an existing site's file as a starting point, the VLAN IDs (or
other per-site values) can be left uncorrected and this survives `yamllint`/`ansible-lint`/`ansible-playbook --syntax-check` silently — none of those check that IDs are semantically correct for
the site, only that the YAML is well-formed. Pandanus Park's `topology_vars` file was confirmed byte-identical to Umoona's (except hostname) going back to before the currently-deployed commit,
with wrong `vlanid` values that went undetected for roughly five weeks after install. Live MAC forensics (the deterministic-seed technique in `03_communication-flows.md`) is what caught it, not
any validation step in the normal authoring workflow. When authoring a new site by cloning an existing one's topology file, diff every `vlanid`/interface-key value against the site's real cabling
documentation before committing — do not trust that lint passing means the values are right for the new site.

**Mandatory pre-check: verify physical interface names against the live box, not just VLAN IDs — before any topology_vars edit or any Ansible run touching a site's interfaces.** Confirmed live at
New Looma (2026-07-30): `topology_vars/new-looma.yml`'s `internet01`/`internet02` were named `eno1`/`enp3s0`, and `switch01`/`switch02` were named `enp2s0`/`enp1s0` — a complete cross-wiring, not
just wrong VLAN IDs. `eno1` doesn't exist on this box's hardware at all; it's the naming convention of a **different SMC model** (BOXER-6641, e.g. Old Looma) than the one actually deployed here
(BOXER-6404, same class as Umoona/Pandanus Park, real NICs `enp1s0`-`enp4s0`). Meanwhile the box's two real, currently-leased WAN NICs (`enp1s0`, `enp2s0`) were assigned to `switch01`/`switch02`
(the LAN trunk role) instead of `internet01`/`internet02` — silently swapping which physical port the WAN role and the LAN-trunk role point to. This survived `yamllint`/`ansible-lint`/
`--syntax-check` exactly like the vlanid-cloning bug above, for the same reason: none of those tools know what hardware model a site actually runs, only that the YAML is well-formed.

**Do this before touching any site's topology_vars, or before running any playbook against a site whose topology_vars provenance is uncertain:**
```bash
tsh ssh root@<site>-smc01 'dmidecode -s system-product-name'          # which SMC model — determines the real NIC naming scheme
tsh ssh root@<site>-smc01 "grep -E '^\s+(enp|eno|eth)[a-z0-9]*:' /etc/netplan/00-ansible.yaml"   # the box's actual physical interface names
tsh ssh root@<site>-smc01 'systemctl list-units "dhclient@*" --all'    # which of those names are actually active WAN NICs right now
```
Cross-check the model against a known-good site of the same model (this fleet has at least two: BOXER-6404 uses `enp1s0`/`enp2s0` for WAN and `enp3s0`/`enp4s0` for the LAN trunk, confirmed at
Umoona/Pandanus Park; BOXER-6641 uses `eno1`/`enp3s0` for WAN, confirmed at Old Looma) — do not assume a `topology_vars` file's existing physical interface names are correct for the box just
because the file parses and the site is currently "working" (New Looma's case shows a box can partially route traffic — 3 of 12 real interfaces were live — while this exact bug sits uncorrected).
Full writeup: `issues/apn/routing-issue/docs/backup-vlan-trunk-fixed-and-new-looma-online-20260730_1520.md` in the local-knowledge repo (§ New Looma reconstruction, once committed).

**A third distinct topology_vars authoring bug class, confirmed at rocket-bore-smc01 (2026-07-28) — role mistagging, not naming or cloning.** Both the `switch` interface and `internet02` were
tagged `role: internet` in this site's `topology_vars` — producing redundant routing tables for what should be one LAN-trunk interface and one WAN interface with distinct roles. Same underlying
netplan 0.104 `vrf:`-key-unsupported regression as the family-friendly-smc01/BOXER6404 case applied here too; yimidarra-smc01 was used to confirm a VRF-less topology works as the fallback while
the netplan-version fix is pending. This is a third failure mode alongside vlanid-cloning and physical-interface-naming above — `role:` values themselves can be wrong even when interface names
and VLAN IDs are correct, and none of `yamllint`/`ansible-lint`/`--syntax-check` catch it either. When auditing a site's topology_vars, check all three independently: VLAN IDs, physical interface
names against live hardware, and `role:` assignment per interface.

**Handler-name reuse across different `listen` topics is safe, not a collision risk.** Ansible matches handlers by their `listen` topic, not by uniqueness of `name` — `smc_network`'s handler file
reuses the same four handler names (`Schedule a Teleport service restart in 2 minutes`, `Ensure we have an operational ssh connection`, `Delete Teleport service restart job`, etc.) across four
different protected-restart `listen` blocks, and `smc_application`'s ported copy of the same pattern reuses them a fifth time in a different role entirely. If you see the same handler `name`
appear multiple times across a role's handler file or across roles, that's this codebase's established convention for the protected-restart pattern, not a bug to fix.

---

### SSH Cipher Negotiation Fix Location (smc_sshd role — 2026-06-10, corrected 2026-06-24)

**Symptom:** a remote host (SSL cert copy target) was hardened to modern-only SSH ciphers
(`chacha20-poly1305`, `aes256-gcm`, `aes128-gcm`) and the SMC's SSH client didn't propose any of
them by default, breaking `sslcertcopy.sh`'s cert-copy step; a `basename` call further down the
script also crashed once the connection itself started failing.

**First-attempt fix (2026-06-10) put the cipher flags in the wrong place** — added directly to
`roles/smc_url_capture/files/sslcertcopy.sh` and `templates/sslcertcopy.sh.j2` as explicit
`-c <cipher-list>` flags, plus a guard around the `basename` crash. This worked for that one
script but only that one script.

**Corrected fix (2026-06-24):** reverted the per-script patches and moved the cipher preference into
`smc_sshd`'s `ssh_config` template instead — prepending the modern cipher list at the client-config
level applies to every SSH client call the box makes, not just this one script. If another
role/script hits the same "modern-cipher-only remote host" failure in the future, check
`smc_sshd`'s `ssh_config` template first rather than re-patching the calling script.

### Tag Hazard: destroy/recreate blocks must carry their repair tasks (2026-07-28)

**The rule:** if a tagged block *destroys and recreates* state, every task that repairs permissions, ownership, or content on that recreated state must carry the **same tag**. Otherwise the tag-limited run is guaranteed broken while the full untagged run stays correct — so the defect is invisible in normal use and only fires when someone runs the tag.

**How it bit us:** `roles/smc_application/tasks/main.yml` has a `tags: wifi_dev_repo` block that does `file: path=/var/www/html/wifi state=absent` then re-clones the portal repo. Git recreates `application/cache` and `application/logs` at `0755 root:root` (both are tracked only via a `.gitignore` stub, so umask 022 applies). The tasks that chmod them to `0777` sat in a **separate untagged block**. Result: a `--tags wifi_dev_repo` run on 2026-07-21 left the captive portal dead on 10 of 16 `rcp` sites for 7 days. See `06_failure-modes.md` and `10_captive-portal.md` §11.8.

**Non-obvious detail — tag the `stat` too.** The perms block is gated by `when: wifi_stat.stat.exists`, and `wifi_stat` is registered by a preceding `stat` task. Tagging only the block makes a tag-limited run evaluate `when` against an **undefined variable** and fail. Both must carry the tag, or neither works.

**Safe by construction:** adding a tag never removes a task from untagged full runs (untagged runs execute everything), so this class of fix is purely additive — there is no full-run behaviour change to regression-test.

**Audit pattern** — look for a tagged block containing `state: absent` / `git:` / `unarchive:` and check what fixes up the result:
```bash
grep -n "clear old\|state: absent\|tags:" roles/<role>/tasks/main.yml
ansible-playbook -i <inv> <playbook> --tags <tag> --list-tasks   # does the repair task appear?
```

`--list-tasks` under the tag is the authoritative check — it shows exactly what a tag-limited run would execute. Surveyed `smc_application`'s other destroy/reclone blocks (`wifi_community_app_backend_git`, `telemetry_git`): both untagged, so not vulnerable. The pattern is not role-specific — worth checking elsewhere.

### apt-daily Timer Mask (smc_system role — 2026-07-15)

**Change:** Added a task to `roles/smc_system/tasks/main.yml`, in the same block as the existing
`unattended-upgrades` disable, stopping/disabling/masking `apt-daily.timer` and
`apt-daily-upgrade.timer`:
```yaml
- name: Stop and mask apt-daily timers (prevents periodic apt/dpkg lock contention)
  systemd:
    name: "{{ item }}"
    state: stopped
    enabled: no
    masked: yes
  loop:
    - apt-daily.timer
    - apt-daily-upgrade.timer
```

**Why:** the pre-existing `APT::Periodic::Update-Package-Lists`/`Unattended-Upgrade` = `"0"` task
(same block) only gates *what* `apt.systemd.daily` does once it fires — the timers still fire on
their own schedule and still take the apt/dpkg lock for an update+cleanup pass regardless. Root
cause of transient `apt-get clean failed` collisions during concurrent Ansible runs (found during
the smc-file-writing-analysis fleet rollout, 2026-07-14 — 3 collisions: jigalong ×2, bidyadanga ×1,
each failing early in the play before reaching any target task, no partial state, clean on retry).
Also a real contributor to ongoing write volume: `gpgv` (apt package-list signature verification,
triggered by this same timer) was found to be the dominant `fatrace` writer on most rcp nodes
*after* the status.json/graylog-sidecar/journald fixes were rolled out — not the `apt_info.py`
textfile collector, as the write path (`/tmp/apt.data.*`) initially suggested. Confirmed by
checking `fatrace`'s `top_proc` output, not just `top_path` — a temp file's path alone doesn't tell
you which process is writing it.

**Gotcha — `masked`, not just `stopped`/`disabled`:** a stopped-and-disabled (but unmasked) timer
can still be re-triggered by another unit's dependency chain. Mask it so it can't fire at all.

**Applies to:** All Ubuntu SMC flavors (rcp, rct, wh) via `when: os_distribution == 'Ubuntu'` — same
`smc_system` role, shared across flavors via `smc_bases.yml`. Deployed live to all 12/12 rcp nodes
(2026-07-15, ansible-wifi commit `0c51cb1`); **not yet rolled to rct/wh** — same gap exists there
too, but that's outside the smc-file-writing-analysis project's scope. Worth flagging to whoever
owns that flavor.

**Validation:**
```bash
tsh ssh root@<node> 'systemctl is-enabled apt-daily.timer apt-daily-upgrade.timer'
# Expect: masked / masked
```

---

### apt_info.py cache.update() Removal (smc_node_exporter role — 2026-07-15)

**Change:** Removed the upstream default `cache.update()` call from
`roles/smc_node_exporter/files/apt_info.py` (the node_exporter textfile-collector script, cron
`*/5 * * * *`). The script now just does `cache = apt.cache.Cache(); cache.open()`, no update.

**Why:** `cache.update()` on every 5-min cron tick is a full `apt update` — network fetch + `gpgv`
Release-signature verification against every configured repo, 288×/day. This is the actual root
cause of persistent `gpgv`/`/tmp/apt.data.*` writes, independent of and untouched by the
apt-daily-timer mask above (it's not the same trigger — it's this script's own `cache.update()`
call). That call is also what fires `20apt-esm-hook.conf`'s `APT::Update::Pre-Invoke` hook, starting
`apt-news.service`+`esm-cache.service` (see next entry) as a *side effect* — do not assume masking
those two services fixes the gpgv writes; it doesn't, this does. Confirmed safe: the script's own
comment already tolerated `cache.update()` failing (`contextlib.suppress(LockFailedException,
FetchFailedException)`, falling back to the existing index) — a "packages pending upgrade" gauge
doesn't need a live network refresh every 5 min, especially once the apt-daily timer (which used to
do a real daily refresh) is masked anyway.

**Applies to:** rcp only (deployed). Not yet checked on rct/wh — likely the same gap if they run
this same textfile-collector script.

**Validation:**
```bash
tsh ssh root@<node> 'grep -c "^import contextlib" /usr/local/lib/apt_info.py; grep -c "^\s*cache\.update()" /usr/local/lib/apt_info.py'
# Expect: 0 / 0
tsh ssh root@<node> 'python3 /usr/local/lib/apt_info.py | head -3'
# Expect: valid Prometheus output, exit 0
```

---

### `/tmp` + `textfile_collector` → Size-Capped tmpfs (smc_system + smc_node_exporter roles — 2026-07-15)

**Change:** `smc_system` mounts `/tmp` as tmpfs, size-capped at 512M (not systemd's 50%-of-RAM
default). `smc_node_exporter` mounts `/var/lib/node_exporter/textfile_collector/` as its own 16M
tmpfs.

**Why:** on rcp (no overlayroot yet), `/tmp` is real lower-disk — confirmed via `findmnt`.
Size-capped deliberately: without a cap, a runaway write trades today's contained failure mode
(disk full, `ENOSPC`) for **RAM exhaustion / OOM-killer picking an arbitrary victim process** on
these 4-8GB boxes — a materially worse outcome. `textfile_collector` content is fully regenerated
by its own collector script every cron tick, same accepted-loss-on-reboot tradeoff already used for
`/var/lib/fluent-bit/pos` (smc_graylog, see below).

**Gotcha 1 — `tmp.mount` isn't loadable out of the box.** Ubuntu/Debian ship `tmp.mount` only as a
*reference template* at `/usr/share/systemd/tmp.mount`, not in the actual unit search path
(`LoadState=not-found` confirmed live until fixed). It must be symlinked in first:
```yaml
- name: Symlink tmp.mount unit from the systemd-shipped reference template
  file:
    src: /usr/share/systemd/tmp.mount
    dest: /etc/systemd/system/tmp.mount
    state: link
```

**Gotcha 2 — first activation doesn't reliably pick up a same-run drop-in, and don't `state:
restarted` unconditionally either.** Even after `daemon_reload`, the *first* `systemctl start
tmp.mount` right after symlinking it in used the base unit's default `size=50%` instead of a
same-run drop-in override — a manual `systemctl restart tmp.mount` fixed it immediately after.
The naive fix (`state: restarted` on every run) breaks worse: restarting `tmp.mount` unmounts and
remounts `/tmp`, which is also where **Ansible's own AnsiBallZ module payload for that very task is
running from** — the remount shadows the module's own working files mid-execution, so it reports
`Module result deserialization failed: No start of json char found` on *every single run*, even
though the underlying `systemctl restart` genuinely succeeds every time (verified live: `/tmp` at
the correct cap, `unattended-upgrades` masked, no other collateral damage). **Fix:** `state:
started` (idempotent, no-op once active) plus a `notify`-triggered handler that only fires when the
drop-in content actually changes, dispatched fire-and-forget:
```yaml
# task
- name: Write tmp.mount size-cap override
  copy: {dest: /etc/systemd/system/tmp.mount.d/99-smc-size-cap.conf, content: "...", ...}
  notify: Restart tmp.mount
- name: Enable and start tmp.mount
  systemd: {name: tmp.mount, enabled: yes, state: started}
# handlers/main.yml
- name: Restart tmp.mount
  systemd: {name: tmp.mount, state: restarted}
  async: 15
  poll: 0
```
This class of bug (a task that restarts something Ansible's own execution depends on) will recur
for any future unit that touches `/tmp` — remember it's not specific to `tmp.mount`.

**Gotcha 3 — first-activation self-wipe of Ansible's own module payload (found 2026-07-23, new-looma
onboarding).** On a node's *first* onboarding, the "Enable and start tmp.mount" task fatals with
`Module result deserialization failed: No start of json char found` →
`FileNotFoundError: /tmp/ansible_systemd_payload_*.zip`. Cause: AnsiballZ self-extracts the module's
payload honoring the **remote shell's `TMPDIR`** (defaults to `/tmp`), which is *independent of*
ansible's `remote_tmp` (set to `/var/tmp/${USER}/` in this repo's `ansible.cfg` — that governs module
*args*, not the AnsiballZ extraction dir). The moment the task activates `tmp.mount`, a fresh tmpfs is
mounted over `/tmp`, wiping the payload the running module is executing from → it dies before it can
return JSON. The `Restart tmp.mount` handler still fires and the mount *does* end up active, so a blind
re-run "works" (second pass finds `/tmp` already mounted, no re-wipe) — which is why this looked like a
transient error rather than a bug. **Fix (deployed 2026-07-23, `smc_system` role):** pin `TMPDIR` off
`/tmp` for that one task so the payload survives the remount:
```yaml
- name: Enable and start tmp.mount (relocates /tmp to size-capped tmpfs)
  systemd: {name: tmp.mount, enabled: yes, state: started}
  environment:
    TMPDIR: /var/tmp
```
Note this is a *different* mechanism from `remote_tmp` — setting `remote_tmp` alone does **not** fix it,
because AnsiballZ extraction follows `TMPDIR`. Same reasoning applies to any future task that mounts over
a directory Ansible might be staging into.

**Gotcha 4 — changing the `/tmp` size cap doesn't apply live on a busy node (found 2026-07-23, 512M→256M
resize).** When you edit the `size=` in `99-smc-size-cap.conf` and redeploy, the `Restart tmp.mount`
handler fires and reports `changed`, but on a node whose `/tmp` is in use (systemd `PrivateTmp`, X11
sockets, any process with a cwd/open fd there) the **remount silently does not take** — `systemctl restart
tmp.mount` = stop+start, the stop can't unmount a busy filesystem, so systemd leaves the existing mount at
the *old* size and the "start" is a no-op. The handler still shows `changed` (systemd accepted the restart),
so the recap looks successful while `findmnt -nb -o SIZE /tmp` still reports the old value. Observed live:
only 2/15 nodes (the ones whose `/tmp` happened to be unmountable at that instant) actually resized; the
other 13 stayed at the old cap. **The drop-in config is correct, so it applies on next reboot** — but to
apply it *live* without a reboot, remount in place:
```bash
# per node (safe as long as current /tmp usage < the new cap):
mount -o remount,size=256M /tmp
findmnt -nb -o SIZE /tmp   # confirm it actually changed
```
`mount -o remount` changes the cap in place without unmounting, so it works on a busy `/tmp` where
`systemctl restart` can't. **Growing** a tmpfs (e.g. fluent-bit/pos 64m→256m via the `mount` module) has no
such issue — that's already a plain remount and applies cleanly. Only **shrinking `/tmp`** hits this, and
the remount must keep the cap above current usage. Consider adding an explicit `mount -o remount` (or a
reboot note) to the role if live-apply-on-resize is ever required rather than reboot-eventual.

**Applies to:** rcp only (`hotspot_flavor == 'rcp'` gate) — rct/wh already get `/tmp` on tmpfs for
free via overlayroot's upper dir, no change needed there.

### Making the size-capped tmpfs mounts visible to Prometheus (node_exporter, 2026-07-23)

node_exporter's filesystem collector **excludes tmpfs by default in this fleet** — the `smc_node_exporter`
unit (`roles/smc_node_exporter/files/node_exporter.service`) shipped
`--collector.filesystem.fs-types-exclude=^(tmpfs|squashfs|nsfs|vboxsf)$`, so **none** of the four
size-capped tmpfs mounts (`/tmp`, `/var/lib/prometheus`, `/var/lib/node_exporter/textfile_collector`,
`/var/lib/fluent-bit/pos`) produced `node_filesystem_*` series — a monitoring blind spot (a filling tmpfs,
especially fbpos where "full" = log loss, would trip no alert).

**Fix: drop `tmpfs|` from the fs-types-exclude regex** (→ `^(squashfs|nsfs|vboxsf)$`). Do **not** use
`--collector.filesystem.fs-types-include=tmpfs` — an `-include` acts as a whitelist and would make tmpfs the
*only* published fstype, dropping the real root-disk `/` metrics. Removing it from the exclude is the correct
"include tmpfs" mechanism.

Why this is cleanly scoped (verified live on mornington, `findmnt -t tmpfs` = 9 mounts): the **existing**
`--collector.filesystem.mount-points-exclude=^/(sys|proc|dev|run)($|/)` already drops `/dev/shm` and every
`/run/*` tmpfs, so removing the fs-type exclusion surfaces **exactly** the four `/tmp`/`/var/...` mounts and
nothing noisy (no `/dev/shm`, no `/run/*`, no PrivateTmp — those aren't separate mounts in the host
namespace). systemd note: **do not** add `#` comment lines inside the `\`-continued `ExecStart` block — systemd
does not support comments mid-continuation and it breaks unit parsing (keep the rationale in this doc instead).

Deploy: `smc_prometheus.yml --tags node_exporter` (copies the unit, restarts node_exporter — brief scrape
gap only). Verified 2026-07-23 across 15/16 nodes (new-looma offline at the time): all four mounts publish
`node_filesystem_size_bytes{fstype="tmpfs"}` in central Prometheus; fbpos %-used reads 6–9%, matching live
`findmnt`. Alert query: `100*(1 - node_filesystem_avail_bytes{mountpoint="/var/lib/fluent-bit/pos"}/node_filesystem_size_bytes{mountpoint="/var/lib/fluent-bit/pos"})`, warn ~80%.

**Validation:**
```bash
tsh ssh root@<node> 'df -h /tmp /var/lib/node_exporter/textfile_collector'
# Expect: /tmp = 256M tmpfs (was 512M until 2026-07-23), textfile_collector = 16M tmpfs
tsh ssh root@<node> 'systemctl --failed'
# Expect: only the already-known masked-timer entries (they always show "failed" by design) --
# investigate anything else live before assuming it's related to this change.
```

### Prometheus TSDB tmpfs — first-install `stop` guard (smc_prometheus role — 2026-07-23)

**Symptom (fresh-node onboarding):** `smc_prometheus.yml` fatals at "Stop prometheus before relocating
its data directory" with `Could not find the requested service prometheus`. The stop task exists so an
*already-running* prometheus releases its open handles into the old data dir before the tmpfs is mounted
over `/var/lib/prometheus` (correct ordering on an upgrade). But on a **never-installed** node the
service doesn't exist yet and the `service` module fatals — and because the install task comes *after*
the stop, a blind re-run fails at the same point every time (it never reaches the install). This is the
same "first-install ordering" class as the `tmp.mount` gotchas above.

**Fix (deployed 2026-07-23):** gather `service_facts` and guard the stop so it's skipped when the unit
isn't present yet:
```yaml
- name: Gather service facts (guard the first-install stop below)
  service_facts:
  when: [ansible_distribution == 'Ubuntu', hotspot_flavor == 'rcp']

- name: Stop prometheus before relocating its data directory
  service: {name: prometheus, state: stopped}
  when:
    - ansible_distribution == 'Ubuntu'
    - hotspot_flavor == 'rcp'
    - "'prometheus.service' in ansible_facts.services"
```
Prefer the `service_facts` guard over `failed_when: false`/`ignore_errors` — the guard *skips* cleanly
(no red error line), whereas suppression still prints an alarming trace and hides genuine failures.
General rule for onboarding playbooks: any "stop/restart X before reconfiguring it" task must tolerate
X-not-yet-installed on first run.

---

### apt-news.service + esm-cache.service Mask (smc_system role — 2026-07-15)

**Change:** Masks `apt-news.service` and `esm-cache.service` via a direct symlink, not the
`systemd` module's `masked: yes`:
```yaml
- name: Mask apt-news and esm-cache services (no functional loss, no ESM/Pro attachment)
  file:
    src: /dev/null
    dest: "/etc/systemd/system/{{ item }}"
    state: link
  loop:
    - apt-news.service
    - esm-cache.service
```

**Why:** these fire via `20apt-esm-hook.conf`'s `APT::Update::Pre-Invoke` hook on any apt cache-open
— a downstream side effect of `apt_info.py`'s `cache.update()` (see above), not an independent
cause. Belt-and-suspenders cleanup for any other trigger of that hook (manual apt commands, future
ansible apt tasks). No functional loss: `apt-news.service` only fetches a cosmetic MOTD banner;
`esm-cache.service` maintains ESM entitlement caches for a subscription that doesn't exist on this
fleet (`ua status --format json` → `attached: false` on every node checked).

**Gotcha — these units are version-gated, `systemd: masked: yes` fails hard where they don't
exist.** Only shipped by `ubuntu-advantage-tools` **≥28.x** — confirmed live: 27.9~22.04.1
(tjuntjuntjara) does not ship them at all, 28.1~22.04 (horn-island) does. `systemd: masked: yes`
queries current unit state first via `systemctl show`, and fails with `Could not find the
requested service` wherever the unit's `LoadState` is `not-found` — genuinely the case on any node
still on the older package version, not a check-mode artifact (compare to the `tmp.mount` gotcha
above, which *was* check-mode-only). **Fix:** mask via a direct `/dev/null` symlink instead (what
`systemctl mask` does under the hood) — this doesn't require the unit to exist or be loadable,
since `/etc/systemd/system/` takes priority over `/lib/systemd/system/` in systemd's unit search
order regardless, so it stays correct fleet-wide even as nodes eventually pick up the newer
package. **General lesson:** before assuming a `masked: yes` failure is the same known
check-mode-only false-positive as a previous session's finding, check live (`systemctl show -p
LoadState`, `dpkg -L <package>`) whether the unit genuinely exists on *that* node — package version
drift across a fleet provisioned/updated at different times is a real, recurring cause here.

**Applies to:** rcp, all Ubuntu flavors technically (`when: os_distribution == 'Ubuntu'`, no
flavor gate) — not yet checked on rct/wh.

**Validation:**
```bash
tsh ssh root@<node> 'systemctl show apt-news.service esm-cache.service -p LoadState --value'
# Expect: masked / masked (works regardless of ubuntu-advantage-tools version)
```

---

### nl80211 rsyslog Drop Filter — DEPLOYED 2026-07-15, REMOVED 2026-07-17 (never actually worked)

**Original change:** `/etc/rsyslog.d/00-drop-nl80211.conf` (`if $msg contains 'nl80211' then stop`),
numbered `00-` so it evaluates before the default rules that would otherwise write the message.

**Original why:** 13 Cambium APs relay wireless-driver debug chatter over UDP 514 into rsyslog —
`nl80211` is the Linux kernel wireless netlink API name, and this string only ever appears in that
AP-relayed debug output (SMCs have no local wireless hardware). horn-island-smc01 alone generated
557MB/day this way (root cause found 2026-06-04). Dropping before any output action was also meant
to stop it reaching Fluent Bit, which tails `/var/log/syslog` directly (ADR-006).

**THE BUG — found and fixed 2026-07-17: this filter never actually worked.** `$msg contains
'nl80211'` checks the rsyslog `$msg` property, but every real AP-relayed line has the form
`<AP-hostname> nl80211: <message-body>` — rsyslog's BSD-syslog parser splits `TAG: MSG` on ingest,
so `nl80211` here is the syslog **TAG**/`$programname`, never part of `$msg`. The filter was
checking the wrong field from day one.

**Verified live on horn-island with paired `logger` probes** (non-destructive local test
messages):
```bash
logger -t nl80211 'TESTPROBE'          # tag=nl80211, matches real AP format
# -> landed in /var/log/syslog, NOT dropped

logger -t testtag 'nl80211: TESTPROBE' # nl80211 inside the message body instead
# -> correctly dropped
```
This is why the original "Gotcha" note below (now struck through) was itself wrong: the write-count
fluctuation it described as "expected, filter is exercised but doesn't cover all chatter" was
actually the filter **never being exercised at all** for real traffic. Every fatrace/write-count
improvement this project ever attributed to this filter — including the 2026-07-16 "horn-island
fully resolved" post-fix verification — was in fact 100% attributable to the AP-side Event Logging
Severity fix (Debug→Warning via cnMaestro), not this filter.

~~**Gotcha — does not cover all AP chatter, only this specific string.** Verified live after
deploying: `nl80211:`-tagged lines stop appearing, but other AP debug messages (`deauth`/`mgmt`
events, "Unknown event N") still pass through unfiltered.~~ — **struck through, was based on a
false premise**: the filter was never blocking anything, so the "quiet window" observed at
deploy-verification time was the AP not emitting a qualifying burst at that moment, not the filter
working.

**Fix (2026-07-17):** removed rather than patched, since the root cause is corrected at the AP
config layer — no local rsyslog filter is needed once APs stop emitting at `Debug` verbosity, and
a broken filter that looks correct is worse than no filter. `roles/smc_rsyslog/tasks/main.yml`'s
`copy` task replaced with a `file: state=absent` task (commit `9d9b0b9`). Deployed live to all
12/12 rcp nodes (dry-run + live clean, verified via `tsh ssh`: file absent, rsyslog active,
every node). **There is now no local backstop for this issue class** — horn-island/mornington rely
entirely on AP-side Event Logging Severity being correct going forward. See
`smc-file-writing-analysis/docs/log-audit-results.md` `20260717_1330` for the full verification
narrative and `smc-file-writing-analysis/SCRATCHPAD.md` Open items for the still-open "audit all
APs at both sites in one cnMaestro pass" recommendation.

**Lesson for future rsyslog filters on this project:** when filtering on content that arrives via
relayed/forwarded syslog (UDP 514 from an external device), check whether the target string lands
in `$msg` or in `$programname`/`$syslogtag` before writing the filter — do not assume `$msg`
contains the full line. Verify with a paired `logger -t <tag> '<body>'` probe before trusting a
"quiet window" as proof the filter works.

---

### wifi/dhcp/system rsyslog Log-Group Split → tmpfs, restart-after-mount (smc_rsyslog role — 2026-07-20)

**Change:** `/etc/rsyslog.d/10-log-groups.conf` routes `dhcpd`/`dhclient` → `dhcp.log`,
AP/Cambium-relayed chatter (`nl80211`/`mgmt`/`WPA`/`hostapd*`/`ap_sta_set_authorized`/`ioctl`/
`WIFI-4-CLIENT-*`) → `wifi.log`, and `systemd`/`CRON`/`networkd-dispatcher`/`netifd`/`teleport`/
`postfix/qmgr` → `system.log`, each with `stop` so it's a move off `/var/log/syslog`, not a copy.
`/var/log/smc-groups/` is mounted as a 64M tmpfs (rcp only).

**Why:** confirmed live 2026-07-20 (3 nodes: tjuntjuntjara, mornington, jigalong) that rcp runs
**no overlayroot at all** (`overlayroot=""`) — every `/var/log/syslog` write hits the real SSD
directly, unlike rct/wh where overlayroot's tmpfs upper dir already absorbs this for free. See
`07_hardware-overlay.md` and `AGENTS.md` "Overlayroot Context".

**THE BUG — same failure class as the Prometheus `stop-before-mount` entry above, but hit live
instead of caught by reasoning first.** The Prometheus entry above already documents this exact
pattern (mounting tmpfs over a directory a running process already has open silently shadows its
file handles) — that lesson existed in this file before this rollout, and it still wasn't applied:
the `smc_rsyslog` mount task shipped with no `notify`. On the tjuntjuntjara canary, a manual
pre-deployment test had already made rsyslog open `wifi.log`/`dhcp.log`/`system.log` on the real
disk (no tmpfs mount existed yet at that point). The later Ansible run mounted tmpfs over the same
directory without restarting rsyslog. Result: `ls`/`tail` on the group files showed nothing (the
new, empty tmpfs), `dhcpd`/`dhclient` kept leaking into `/var/log/syslog`, and — the dangerous
part — `/proc/<rsyslogd-pid>/fd/` showed the open FDs as completely valid, target path intact, **no
`(deleted)` marker**, because mount-shadowing doesn't unlink the underlying file the way the
Prometheus entry's scenario did; it just makes it unreachable by path. rsyslog kept writing real
bytes to a real-disk inode that had become invisible to any normal check. A clean Ansible recap
(`ok=18 changed=5 failed=0`) gave zero indication of this — the task that mounts tmpfs reported
"changed" correctly, but "changed" only describes the mount action, not whether the log-writing
process noticed.

**Caught only because the operator explicitly asked "is it actually applied" and "are the log
files being written" after the run — not by any of my own verification.** Recap success does not
verify content; this is the same "read the file body, don't trust the confirmation" gap RULE-007
exists for, just for a running process's file handles instead of a doc edit.

**Fix:** added `notify: Restart rsyslog service` to the mount task itself (not just the conf-deploy
task) — a bare `state: mounted` mount action can report "changed" without the conf file changing at
all (e.g. first-ever mount, or an fstab option tweak), and that's exactly the case that needs the
restart most.

**Generalized rule for any future tmpfs-mount task in this codebase:** if the directory being
mounted might already have a writer process with it open — which is always true once *any* prior
version of the role has run, including a manual test during development — the mount task itself
must `notify` (or directly trigger) a restart of that writer. Don't rely on a separate
"ensure service started" task later in the role; `state: started` is a no-op if the process is
already running, exactly like the Prometheus entry already warned.

**Applies to:** rcp only (`hotspot_flavor == 'rcp'`) — rct/wh get this for free via overlayroot.

**Validation:**
```bash
tsh ssh root@<node> 'mount | grep smc-groups; ls -la /proc/$(pgrep -f rsyslogd|head -1)/fd/ | grep smc-groups'
tsh ssh root@<node> "logger -t dhcpd 'verify'; sleep 1; cat /var/log/smc-groups/dhcp.log"
# Expect: tmpfs mount present, fd targets match live paths (not just non-"(deleted)"), and the
# logger probe's output actually appears in the file -- not just that the mount/task recap is clean.
```

---

### Prometheus TSDB → tmpfs, stop-before-mount (smc_prometheus role — 2026-07-15)

**Change:** Mounts `/var/lib/prometheus` as a 128M tmpfs on rcp, with an explicit
`service: {name: prometheus, state: stopped}` task immediately *before* the mount task.

**Why:** Prometheus here runs in **agent mode** (`--storage.agent.retention.max-time 120m`),
remote_write-ing continuously to a central server — the local TSDB is architecturally a 2-hour
scrape buffer, not a durable store. Confirmed live across 5 nodes before implementing: actual disk
usage 2.0M-4.3M, well within the 128M cap.

**Gotcha — mounting tmpfs over an already-running service's data directory needs an explicit stop
first, not just a mount-then-rely-on-later-start-task.** The existing "ensure prometheus is enabled
and started" task later in the role uses `state: started`, which is a no-op on any node where the
service is already running — true for every node in a rollout like this one. Without an explicit
stop first, the live process keeps its open file handles into the now-shadowed old directory and
never actually picks up the new tmpfs-backed path, defeating the whole point of the mount, until
some unrelated future restart. Caught by reasoning through the task order *before* deploying live
(the same class of problem as the `tmp.mount` self-disruption bug above — a mount happening
underneath a still-active consumer of the old path — but this one only needed a plain `stop` first,
not the async/fire-and-forget trick, since Prometheus doesn't share Ansible's own execution
directory the way `/tmp` does).

**Applies to:** rcp only (`hotspot_flavor == 'rcp'`) — rct/wh already get this for free via
overlayroot.

**Validation:**
```bash
tsh ssh root@<node> 'df -h /var/lib/prometheus; journalctl -u prometheus --since "-2min" | grep fs_type'
# Expect: tmpfs 128M; fs_type=TMPFS_MAGIC logged on the most recent startup
```

---

### interfacecheckv2.sh NaN-on-parse-failure (smc_network role — 2026-07-15)

**Change:** When the `sed` extraction of ping loss/RTT values from the summary line comes back
empty, write `NaN` to the Prometheus metric instead of feeding the empty string into `bc`.

**Why:** An empty `sed` match feeding straight into `bc` produces an empty `bc` result, which then
gets written into the Prometheus exposition line with no value at all — invalid format, causing
node_exporter to log a parse error every collection cycle (root cause of the 2,880 log
entries/day fleet-wide finding). `NaN` is the correct could-not-determine value in
Prometheus/OpenMetrics — not `0`, which would falsely read as "0% loss"/"0s RTT" (perfect
connectivity), which is not what happened.

**Status:** fix drafted and committed (`ae838c2`) 2026-07-15, **deploy deferred to a later session**
per operator instruction — not yet on any node.

**Applies to:** `smc_network` role, deployed via `smc_bases.yml --tags network` when actioned.

---

### smartmon.py Part 1 rollout gap: collector script and relabel config are two separate tags (2026-07-15)

**Lesson:** the 2026-07-13 Part 1 implementation touches two different files in two different
roles/tags — `roles/smc_node_exporter/files/smartmon.py` (the collector, `--tags node_exporter`)
and the `write_relabel_configs` addition in `roles/smc_prometheus/templates/prometheus.yml.j2`
(`--tags prometheus`). A 2026-07-15 rollout of the collector to the remaining 10 nodes ran only
`--tags node_exporter` and was recorded as "Part 1: 12/12" — but the relabel-config half was never
deployed to those 10 nodes, meaning the new `smartmon_active_disk_remaining_lifetime_perc` metric
was being generated locally but silently dropped before reaching the central Prometheus server
(the exact same "silently dropped, not matching the keep-list" failure mode Part 1 was fixing in
the first place). Not caught until an unrelated later rollout's dry-run diff happened to show the
same file changing. **When rolling any fix that touches both `smc_node_exporter` and
`smc_prometheus` config, deploy both tags together, or explicitly track both as separate rollout
items — do not assume one tag's rollout covers the other.**

---

### Journald Volatile Storage (smc_system role — 2026-06-30)

**Change:** Added journald volatile storage task to `roles/smc_system/tasks/main.yml`.

Creates `/etc/systemd/journald.conf.d/99-smc-volatile.conf`:
```ini
[Journal]
Storage=volatile
RuntimeMaxUse=200M
```

**Why:** journald was writing 163–333MB/day to SSD (rcp fleet). `Storage=volatile` moves journal
to `/run/log/journal/` (RAM tmpfs), eliminating continuous SSD wear. `RuntimeMaxUse=200M` caps
RAM usage on log storms.

**Safety:** rsyslog reads journald via `imjournal` from `/run/log/journal/` — works with volatile.
Fluent Bit pipeline (syslog + misclog tail inputs) is unaffected. `ForwardToSyslog` not needed.

**Handler added:** `roles/smc_system/handlers/main.yml` — `Restart journald` (restarts
`systemd-journald` to apply config changes).

**Applies to:** All Ubuntu SMC flavors (rcp, rct, wh) via `when: os_distribution == 'Ubuntu'`.

**Validation:**
```bash
# After playbook run:
tsh ssh root@<node> 'journalctl --disk-usage'
# Expect: /run/log/journal/... (RAM path, not /var/log/journal/)
tsh ssh root@<node> 'cat /etc/systemd/journald.conf.d/99-smc-volatile.conf'
```

---

### smc_graylog RISE Defaults Bug — rcp Override (2026-06-30)

**Bug:** `roles/smc_graylog/defaults/main.yml` sets RISE-specific defaults for all flavors:
```yaml
graylog_sidecar_extra_tags:
  - rise
graylog_sidecar_extra_log_files:
  - "/var/log/rise"
  - "/opt/rise/status"
```

On **rct/wh** these paths exist (RISE is deployed) — no crash. On **rcp** they don't exist →
sidecar validates `list_log_files` on startup → fatal crash-loop.

**Symptom:**
```
level=error msg="stat /var/log/rise: no such file or directory"
level=fatal msg="Please provide a list of directories for list_log_files."
```

**Fix:** Added to `inventories/rcp/group_vars/smc_bases.yml`:
```yaml
graylog_sidecar_extra_tags: []
graylog_sidecar_extra_log_files: []
```

**Critical:** Any re-run of `smc_graylog` against rcp redeploys `sidecar.yml` from template,
overwriting manual fixes with RISE defaults. The group_vars override must be in place before
running the role on any rcp node.

**Validation:**
```bash
tsh ssh root@<rcp-node> 'systemctl is-active graylog-sidecar'
# expect: active
```

---

### Fluent Bit Position Directory → tmpfs (smc_graylog role — 2026-06-30)

**Change:** Added tmpfs bind-mount task to `roles/smc_graylog/tasks/main.yml`.

Mounts tmpfs (64M) over `/var/lib/fluent-bit/pos/` at role execution. Size documented as
`fluent_bit_pos_tmpfs_size: 64m` in `roles/smc_graylog/vars/main.yml`.

**Why:** The pos directory holds SQLite WAL files (25–32MB across fleet, one file per tailed
log source). These were written every 5 seconds — 1,419–2,633 write events per 5-minute window
per node. tmpfs eliminates all SSD writes from this source.

**Safety:** pos files track the read offset per tailed file. On wipe (reboot or remount):
- Fluent Bit re-reads from last known Graylog position (duplicate window)
- Graylog deduplicates by message hash — no log loss; brief duplication only

**Validation:**
```bash
tsh ssh root@<node> 'mount | grep fluent'
# expect: tmpfs on /var/lib/fluent-bit/pos type tmpfs (rw,...)
```

---

### Graylog Sidecar Log Redirect → `/run/` RAM (smc_graylog role — 2026-06-30)

**Change:** Sidecar log path moved from `/var/log/graylog-sidecar/` (SSD) to
`/run/graylog-sidecar/` (RAM tmpfs). Three file changes:

1. `roles/smc_graylog/templates/sidecar.yml.j2` — `log_path` updated to `/run/graylog-sidecar`;
   `list_log_files` entry updated to `/run/graylog-sidecar/sidecar.log` (Fluent Bit tail path)
2. `roles/smc_graylog/tasks/main.yml` — directory creation task target updated to
   `/run/graylog-sidecar`
3. `roles/smc_graylog/tasks/main.yml` — new task deploys
   `/etc/tmpfiles.d/graylog-sidecar.tmpdir.conf` to recreate the `/run/` directory at boot

**Why:** Sidecar stderr/stdout log flood caused 1,101–153,116 writes/5min (worst: mornington,
8-month-old stale sidecar process with stderr fallback). `/run/` is tmpfs — writes hit RAM only.

**Boot persistence:** `systemd-tmpfiles-setup.service` recreates `/run/graylog-sidecar/` at
boot from the tmpfiles.d conf. No sidecar state is lost — sidecar logs are ephemeral by design.

**Validation:**
```bash
tsh ssh root@<node> 'cat /etc/tmpfiles.d/graylog-sidecar.tmpdir.conf'
tsh ssh root@<node> 'systemctl is-active graylog-sidecar'
```

---

### apn-mqtt-client status.json → tmpfs symlink (smc_application role — 2026-07-13/14)

**Change:** brand-new automation block added to `roles/smc_application/tasks/main.yml` (no prior
ansible-wifi role managed this app — its cron task traces to an unmerged `origin/mqtt_update`
branch, yet was live in production fleet-wide, a "phantom-deployed" gap worth remembering when
auditing what's actually running vs what `rise-multi` shows). Stat-guarded so it's a safe no-op on
nodes without the app:
```yaml
- block:
    - name: Check if apn-mqtt-client app is installed on this node
      stat: {path: /var/www/apn-mqtt-client}
      register: apn_mqtt_client_dir
    - name: Deploy tmpfiles.d to create /run/apn-mqtt-client at boot
      copy: {src: apn-mqtt-client-tmpfiles.conf, dest: /etc/tmpfiles.d/apn-mqtt-client.conf}
      when: apn_mqtt_client_dir.stat.exists
    - name: Symlink status.json to tmpfs to eliminate SSD writes
      file: {src: /run/apn-mqtt-client/status.json, dest: /var/www/apn-mqtt-client/status.json, state: link}
      when: apn_mqtt_client_dir.stat.exists
  when: hotspot_flavor in ['rcp', 'nbn_accelerate']
```

**Why:** `status.json` was the single highest-frequency writer on every rcp node where the app is
present — up to ~2,900 write events per 5-minute fatrace window on the busiest node (mornington),
rewriting continuously, forever, unbounded. Proven fix first on burringurrah (2026-07-13, 80%
total-write reduction confirmed same-day), then rolled fleet-wide (2026-07-14) — deployed to all
12/12 rcp nodes, verified `status.json` no longer appears in any node's top-5 fatrace writers
afterward.

**Gotcha — "app absent" needs direct verification, not inference from a sample.** 3 nodes
(tjuntjuntjara, kalumburu, umoona) were initially classified "N/A — app absent" based on
`apn-mqtt-client`/`status.json` not appearing in a short fatrace capture window. Direct check
(`ls -la /var/www/apn-mqtt-client`) found the app genuinely installed on all three — one
(kalumburu) had a `status.json` actively written the day before the correction. The app is
installed fleet-wide; there are no genuine N/A nodes on rcp for this fix. **Absence from a sample
is not proof of absence** — if a fix's applicability is being scoped from fatrace output alone,
verify the target file/directory's existence directly before excluding a node.

**Validation:**
```bash
tsh ssh root@<node> 'readlink /var/www/apn-mqtt-client/status.json'
# Expect: /run/apn-mqtt-client/status.json
tsh ssh root@<node> 'ls -la /var/www/apn-mqtt-client'  # confirms app presence directly, don't infer from fatrace alone
```

---

### url_capture v2 — Legacy Directory Auto-Cleanup (smc_url_capture role — 2026-07-14)

**Change:** `roles/smc_url_capture/tasks/v2_setup.yml` gained a final check-then-remove step —
after the existing flush/clear logic empties `smc_url_capture_dir` (`/url_capture`) of its legacy v1
`.pcap` files, a new `find` (recurse: false, hidden: true) + `file: state=absent` pair removes the
now-empty top-level directory itself, guarded on `matched == 0` so it never touches a directory that
still has unflushed content for any reason.

**Why:** the existing logic only ever cleared file *contents*, leaving an empty `/url_capture`
directory behind on every node migrated to v2. Found and manually `rmdir`'d on 3 already-migrated
nodes (burringurrah, tjuntjuntjara, horn-island) during the 2026-07-14 fleet rollout before folding
the cleanup into the role so it's automatic for every node going forward.

**Gotcha:** `rm -rf` on the legacy dir was blocked by the local OPA governance gate (destructive
bash pattern hard block) when attempted via a raw `tsh ssh ... rm -rf` command outside Ansible —
use `rmdir` for manual one-off cleanup (fails safely on non-empty dirs anyway) or let the role's
guarded `file: state=absent` task handle it.

**Validation:**
```bash
tsh ssh root@<node> 'ls -la /url_capture'   # should fail with "No such file or directory" post-v2
```

---

### IPv6 Disable Policy (Fleet vs Vagrant)

When changing IPv6 behavior in `roles/smc_network/tasks/ubuntu.yml`, keep production-fleet
consistency as the default.

- Production/default path: use the existing GRUB-based behavior already in repo
  (`/etc/default/grub` with `ipv6.disable=1`, then `update-grub` + reboot).
- Do not introduce mixed GRUB formatting or append-style rewrites across only a subset of hosts
  unless a coordinated fleet-wide change is explicitly approved.
- Vagrant troubleshooting changes should be scoped as lab-only behavior (for example, gated by
  `smc_bases_vagrant_interface is defined`) and must not silently alter production host
  configuration conventions.
- If a Vagrant-only workaround is needed without fleet GRUB drift, prefer explicit Vagrant-only
  controls and document them in the same change.

#### unbound `interface-automatic` on IPv6-disabled Vagrant VMs

**Symptom:** `unbound[PID]: error: can't bind socket: Cannot assign requested address for ::1 port 53` → `fatal error: could not open ports`. Unbound fails to start even with `do-ip6: no` and `interface: 0.0.0.0` in the config.

**Root cause:** `interface-automatic: yes` combined with `interface: 0.0.0.0` causes unbound to probe for a matching IPv6 wildcard socket at startup — separate from the `do-ip6` DNS processing flag. On Vagrant VMs where `$DISABLE_IPV6` sets `net.ipv6.conf.lo.disable_ipv6=1`, the loopback has no `::1` address. The IPv6 socket probe → bind fails → fatal startup error.

**Fix in `roles/smc_dns/templates/unbound.conf.j2`:**
```jinja2
{% if smc_bases_vagrant_interface is defined %}
        interface-automatic: no
{% else %}
        interface-automatic: yes
{% endif %}
```

**Why physical SMC is unaffected:** Physical boxes have IPv6 on loopback (`::1` present). The probe succeeds silently; `do-ip6: no` then prevents IPv6 DNS queries from being served. No operational change to fleet behavior.

**Note:** Adding `control-interface: 127.0.0.1` to the `remote-control:` section (port 8953) is correct hardening but does NOT fix the port 53 error — they are independent socket bindings.

### Skill Runtime Paths

For local skill tooling consistency, use these dedicated working-cache venvs:
- ansible-wifi venv: `/Volumes/Data/_ai/_skills/skills-working-cache/ansible-wifi/venv`
- skill-smc venv: `/Volumes/Data/_ai/_skills/skills-working-cache/skill-smc/venv`
- ephemeral logs, pid files, and sockets: `/Volumes/Data/_ai/_skills/skills-runtime/<skill>/`

When executing validation commands from this reference, prefer invoking tools from the
ansible-wifi working-cache venv to avoid host-level version drift.

### Canonical Source Rules

1. `inventories/*/topology_vars/<site>.yml` — canonical topology source. Edit these.
2. `inventories/*/topology_vars/.<site>.yml` — generated cache (mtime-gated). Never edit.
3. `roles/smc_generate_smc_files/templates/` — future-site generator templates. Changes here must stay consistent with manual edits to existing sites.

### Design Recommendation (Not Yet Implemented): Bond Doubled RCP/NBN-Accelerate Internet Circuits

**Status: design recommendation, 2026-07-31 — not implemented, not canary-tested.** Scoped to RCP
and NBN-Accelerate flavor sites only, where internet circuits terminate on two independent L2
switches (`switch01`/`switch02`) downstream of the SMC. `topology_vars` today models each such
circuit as **two separate interfaces** (e.g. `internet03`=vlan521/switch01, `internet04`=vlan531/
switch02) — both permanently defined, both in the default VRF, both polled every cycle by
`interfacecheckv2.sh`, even though only one ever has a live cable at a time (manual cold-standby:
a technician physically moves the cable to switch02 if switch01 fails). For old-looma this means
18 pings/cycle where 9 would suffice.

The team considered bridging `switch01`/`switch02` under one shared VLAN tag to collapse this, and
correctly worried that if a technician ever leaves both legs live simultaneously, two independent
WAN CPEs would race for DHCP on one broadcast domain. **That risk assessment is right, but bridging
+ STP is the wrong fix for it** — STP blocks *redundant paths between bridges* via loop detection;
here there is no loop for STP to see (the CPEs aren't bridges), so STP would not prevent the
dual-live condition at all.

**Recommended mechanism: Linux bonding, `mode=active-backup`, not bridging.** Only the active slave
ever passes frames up the stack — the backup slave is excluded from the forwarding path
structurally, even if it independently shows carrier/link-up, so a technician leaving both legs
physically live causes no DHCP race and no ARP instability. One logical `bond_internetNN` interface
also replaces two for VRF attachment and health-check purposes, restoring the 1:1 interface-to-circuit
ratio `interfacecheckv2.sh` was implicitly designed around.

```yaml
bonds:
  bond_internet03:
    interfaces: [vlan521, vlan531]   # vlan521 → switch01, vlan531 → switch02
    parameters:
      mode: active-backup
      primary: vlan521
      mii-monitor-interval: 0        # required — cannot mix MII and ARP monitoring on one bond
      arp-interval: 100
      arp-ip-targets: [<circuit's known CPE gateway IP>]
      arp-validate: all
```

**Monitoring must be ARP-based, not MII-based** — `switch01`/`switch02` sit between the SMC and the
CPE, so SMC↔switch carrier stays up even if the actual WAN device behind that switch port has died;
`miimon` alone is blind to that. `arp_interval`/`arp_ip_target` (the circuit's known/fixed CPE
gateway IP) tests end-to-end reachability, matching what `interfacecheckv2.sh` already does via
ping today.

**Known implementation risk — verify before any fleet rollout.** Bonding a VLAN device as a bond
slave (VLAN created first, then enslaved) is the reverse of netplan's own documented bond-then-VLAN
pattern and has documented systemd-networkd boot-time race bugs: [systemd #7020](
https://github.com/systemd/systemd/issues/7020) and [systemd #15280](
https://github.com/systemd/systemd/issues/15280). Ubuntu 20.04/22.04 SMCs use systemd-networkd as
the netplan renderer by default, so this applies directly — comparable in kind to the netplan
0.104→0.107 VRF syntax incompatibility already found on rocket-bore-smc01/yimidarra-smc01
(elsewhere in this file). **Do not roll out fleet-wide on reasoning alone** — canary one non-critical
circuit at one site, reboot 3× minimum, confirm `cat /proc/net/bonding/bond_internetNN` survives
each reboot, and confirm active-backup failover by physically unplugging the primary leg's cable
before trusting the pattern.

**Rollout scope note:** this is a schema change. `type: bond` is not currently a recognized
interface type in `topology_vars`/`roles/smc_generate_smc_files` — only `ethernet | vlan | bridge |
loopback` are — and `interfacecheckv2.sh` role-filtering/VRF attachment need to point at the bond
interface, not its two legs, once added. Scope the change to RCP/NBN-Accelerate only; this
dual-switch pattern does not exist fleet-wide across all 7 flavors. Full analysis:
`local-knowledge-ansible/ansible-wifi/issues/internet-link-handling/internet-link-active-standby-handling-analysis-20260731_1107.md`.

### Topology Change Workflow

```
1. Identify the flavor and canonical topology file
   inventories/<flavor>/topology_vars/<site>.yml

2. Edit the canonical source only
   (never touch the hidden .*.yml cache file)

3. Assess cross-flavor impact
   - topology_vars/<site>.yml change → single flavor only
   - group_vars/** change → all 7 flavors affected
   - topology_vars.py plugin change → all 7 flavors affected

4. Find consuming roles
   grep -r "topology_interfaces" roles/
   grep -r "topology_bridges" roles/
   grep -r "topology_vrfs" roles/

   Confirmed 2026-07-29 (rcp, APN routing-issue investigation) — every role whose templates filter
   on `interface.role` (internet/starlink/user/management/provision/nbn_modem) goes stale the same
   way if topology changes and it isn't re-run. All render from the same topology-derived
   `interfaces` dict as smc_network/smc_application:
     - smc_network (tag `network`)       — netplan, dhclient confs, rt_tables, interfacecheck
     - smc_application (tag `application`) — dhclient-enter-hooks (ECMP/default-route membership)
     - smc_iptables (tag `iptables`)      — builds internets/starlinks/users/managements/
                                             provisionings/nbn_modems ACL lists from `.role`
     - smc_qos (tag `qos`)                — shapes only `role == 'internet'` interfaces
     - smc_node_exporter (tag `node_exporter`) — SEPARATE PLAYBOOK, smc_prometheus.yml, not
                                             smc_bases.yml — easy to omit from a remediation run.
                                             Also COMPUTES the ECMP-health alert threshold as
                                             count(internet interfaces)/2+1, so a stale topology
                                             miscalibrates the alert, not just interface labels.
     - smc_keepalived (tag `keepalived`)  — looks up a VRRP interface by ID from the same dict,
                                             but is NOT `.role`-filtered like the others — lower
                                             risk, flagged for completeness, not confirmed broken.
   Checked and NOT implicated: smc_dhcpd, smc_hostapd (LAN-side / bridge_500,501 only).
   A remediation run scoped to `smc_bases.yml --tags network,application` alone is incomplete —
   add `iptables,qos` to that tag list, and run `smc_prometheus.yml --tags node_exporter`
   separately. Evidence: local-knowledge-ansible/ansible-wifi/issues/apn/routing-issue/docs/
   problem2-live-root-cause-20260729_2112.md

5. Check generator template drift
   Compare roles/smc_generate_smc_files/templates/ against your change
   Future sites generated from the template must stay consistent

6. Delete stale cache (important after git checkout — mtime may be stale)
   rm inventories/<flavor>/topology_vars/.<site>.yml

7. Run validation sequence (in order)
   yamllint <changed_files>
   ansible-lint <changed_playbooks>
   ansible-inventory -i inventories/<flavor>/prod --playbook-dir . --list
   ansible-inventory -i inventories/<flavor>/prod --playbook-dir . --host <site>
   ansible-playbook --syntax-check <playbook>
```

### Variable Rename / Refactor Workflow

```
1. Enumerate all source changes required
   (topology_vars YAML, group_vars, host_vars, role defaults/vars)

2. Grep all consuming roles and templates
   grep -rn "old_variable_name" roles/
   grep -rn "old_variable_name" inventories/

3. Check generator templates for drift
   grep -rn "old_variable_name" roles/smc_generate_smc_files/

4. Identify cache files that will auto-regenerate vs. stale caches
   Delete relevant hidden .*.yml files to force fresh generation

5. Run full validation sequence after changes
```

**Guardrailed single-site interface-key rename pattern** (pia-wadjari, `internetNN`→`a-internetNN` /
`starlinkNN`→`s-internetNN`): when renaming interface *keys* specifically (not general variables),
prefer scoping the rename to one site's `topology_vars/<site>.yml` plus the generator templates
under `roles/smc_generate_smc_files/templates/` that produce future sites — not a repo-wide rename
of existing sites. This works cleanly here because `vars_plugins/topology_vars.py` is already raw-ID
agnostic (it preserves whatever interface keys a site defines) and consumer templates (e.g.
`roles/smc_iptables/templates/iptables.smp.j2`, `roles/smc_qos/templates/50-qos.sh.j2`) branch on
`interface.role`, never on the `internetNN`/`starlinkNN` key prefix itself — so leaving other sites'
existing keys unchanged does not break anything. **Before assuming this shortcut applies to some
other variable rename, confirm the same two properties hold** (the vars plugin is ID-agnostic, and
every consumer branches on a semantic field rather than the key name) — if either is false, a
single-site guardrail leaves other sites on an inconsistent scheme with no code path enforcing
consistency. Regenerate the hidden `.<site>.yml` cache via `ansible-inventory`, never hand-edit it.

### Cache Coherence Rules

After a `git checkout` or branch switch, hidden `.*.yml` cache files may appear current (mtime preserved by git) but contain stale content. Always delete cache files for affected sites before relying on topology output:

```bash
# Delete single site cache
rm inventories/<flavor>/topology_vars/.<site>.yml

# Delete all cache files for a flavor (safe — they regenerate on next run)
find inventories/<flavor>/topology_vars/ -name '.*.yml' -delete
```

### Inventory Path Convention

Each flavor's `inventories/<flavor>/` directory contains **two separate inventory files**,
`prod` and `stage` (e.g. `inventories/rcp/prod`, `inventories/rcp/stage`) — not a nested
directory structure. Always pass `-i inventories/<flavor>/prod` (or `/stage`) explicitly to
`ansible-playbook`/`ansible-inventory`. Passing the bare `-i inventories/<flavor>` directory
instead loads **both** `prod` and `stage` as inventory sources in one run — every host in both
environments becomes a valid target, and only an explicit `--limit <host>` protects you from
touching the wrong one. This was caught live 2026-07-20: a canary rollout used `-i
inventories/rcp` (bare directory) instead of `-i inventories/rcp/prod`; `--limit
tjuntjuntjara-smc01` happened to keep the actual blast radius correct since that host is
unambiguously in `prod`, but the imprecise inventory path was still a latent risk that should be
fixed before it causes a real cross-environment mistake. This convention was already documented
in the Validation Command Reference below (`ansible-inventory -i inventories/<flavor>/prod ...`)
but wasn't called out as a standalone rule — do not rely on spotting it embedded in an example.

### Cross-Branch File Fetch Tool

`scripts/fetch-commit-files.sh` (added 2026-07-21) pulls specific files out of a given commit/ref
and writes them into the current working tree, without merging or cherry-picking the whole
commit/branch. Built for exactly the situation that prompted it: a colleague's branch
(`origin/fix_rcp_wifi_commit`) had already added `group_vars`/`host_vars`/`topology_vars` for two
sites (`old-looma-smc01`, `new-looma-smc01`) that were never merged into `rise-multi` — `old-looma`
was showing up as a live Teleport/Prometheus target with zero presence in the local inventory
because of this, not because it was deliberately unmanaged.

```bash
scripts/fetch-commit-files.sh <commit-ish> <file1> [file2] ... [--force]
scripts/fetch-commit-files.sh <commit-ish> --file-list <path> [--force]
```

- Verifies the commit resolves locally first — if it's on a remote branch you haven't fetched,
  `git fetch --all` first (`git branch --all --contains <sha>` finds which remote/branch has it).
- Verifies each requested file actually exists in that commit's tree before doing anything.
- **Never silently overwrites a local file that already exists and differs** — shows the diff and
  skips it unless `--force` is passed. Safe to re-run; already-matching files report `unchanged`.
- Never runs `git add`/`git commit` — review with `git status`/`git diff` afterward, same as any
  other change in this codebase (ansible-wifi commits are held local pending explicit operator
  decision per this project's standing practice).
- Accepts a file list via `--file-list <path>` (one path per line, `#` comments and blank lines
  ignored) for bulk fetches instead of long positional argument lists.

**Gotcha found during the looma fetch — vars alone don't make a host live.** Even at the source
commit, `old-looma-smc01`/`new-looma-smc01` were **not** registered as hosts in
`inventories/rcp/prod` or `/stage` — only the `group_vars`/`host_vars`/`topology_vars` files
existed. `group_vars`/`host_vars` only apply to hosts actually declared in the inventory and
assigned to that group/hostname — fetching the vars files is necessary but not sufficient to bring
a site under active management. Check `git show <ref>:inventories/<flavor>/prod` for the actual
host entry before assuming a fetched var-file set is deployable as-is.

### Playbook Run Safety (Overlayroot)

- Changes made via playbooks that do not remount the lower dir are **volatile** — they survive
  until next reboot only. **This applies to rct/wh only**, where overlayroot is real.
- Verify with: `mount | grep root-ro` on target before running critical plays
- The `smc_bases.yml` playbook handles overlayroot remount; run it first or ensure it runs as a dependency
- **rcp has NO overlayroot at all** (confirmed live 2026-07-20 on tjuntjuntjara/mornington/jigalong
  — see `07_hardware-overlay.md`). On rcp, playbook changes are **permanent**, not volatile — they
  land on the real ext4 root (or an explicit tmpfs mount, if the role adds one) and persist across
  reboots exactly like changes to any normal Linux host. Do not assume rcp changes need a
  "did it survive reboot" check the way rct/wh changes do; assume the opposite — an rcp mistake
  stays until explicitly reverted.

### Validation Command Reference

```bash
# YAML syntax
yamllint inventories/<flavor>/topology_vars/<site>.yml

# Ansible lint
ansible-lint roles/<role_name>/

# Inventory list (warns on plugin errors)
ansible-inventory -i inventories/<flavor>/prod --playbook-dir . --list

# Per-host variable dump (verifies topology_vars plugin output)
ansible-inventory -i inventories/<flavor>/prod --playbook-dir . --host <site>

# Playbook syntax check
ansible-playbook -i inventories/<flavor>/prod --syntax-check smc_bases.yml

# Lint baseline refresh (regenerate .git/.ansible-lint-ignore from current violations)
scripts/lint-baseline-refresh.sh

# Lint delta gate (fail only on NEW violations in changed files/lines — used by pre-push hook)
scripts/ansible-lint-delta-gate.sh <changed-file1> <changed-file2> ...
```

Both lint scripts above are promoted, generalized copies at `skill-smc/scripts/lint-baseline-refresh.sh`
and `skill-smc/scripts/ansible-lint-delta-gate.sh` — see `skill-smc/scripts/README.md` for the
full mechanism (baseline-ignore file format, changed-line detection, why pre-existing violations in
untouched lines are not blocking). The pre-push hook that invokes `ansible-lint`/`yamllint` has
previously failed with `ModuleNotFoundError` in some environments — if that happens, these scripts
still need the venv at `/Volumes/Data/_ai/_skills/skills-runtime/ansible-wifi/.venv/bin` on `PATH`
(both scripts add it automatically if present).

### OPA Policy Layer (deployment governance gate)

`ansible-wifi` carries an [Open Policy Agent](https://www.openpolicyagent.org/) layer under `opa/`
that enforces fleet deployment rules independent of `ansible-lint`/`yamllint` — it checks semantic
correctness (is this deployment safe/consistent), not syntax.

```
opa/
  policies/
    smc_url_capture.rego   # url_capture version, tmpfs, and capture config rules
    inventory_vars.rego    # required host/group var completeness rules
    site_deployment.rego   # deployment gate rules (flavor match, commit pin, blast radius)
  tests/
    smc_url_capture_test.rego
  data/
    flavors.json, environments.json   # collapsed lookup data (avoids OPA CLI merge errors)
```

| Package | Deny rules | Warn rules |
|---|---|---|
| `ansible_wifi.smc_url_capture` | v1 on prod without approval, tmpfs cap range, chunk seconds range | non-bridge capture iface |
| `ansible_wifi.inventory_vars` | missing `teleport_fqdn`, bad `eclipse_siteid`, unknown `url_capture` version | orphaned host |
| `ansible_wifi.site_deployment` | cross-flavor deploy, unpinned wifi repo commit | multi-site blast radius, mixed v1/v2 fleet |

```bash
# Evaluate against a host input file
opa eval -d opa/policies/ -d opa/data/ -i input/<site>-smc01.json 'data.ansible_wifi.smc_url_capture.deny'

# Run policy unit tests
opa test opa/policies/ opa/tests/ -v

# Conftest (YAML lint integration, not yet wired into CI — ROADMAP backlog item)
conftest test inventories/rcp/host_vars/<site>-smc01.yml --policy opa/policies/
```

**ADR-001 — env gate overrides flavor gate.** The per-flavor `required_version` deny rule (e.g. rcp
must run `smc_url_capture` v2) only fires when `env_cfg.url_capture.required_version != null` in
`opa/data/environments.json`. `stage` sets this to `null` — permissive regardless of what the
flavor requires; `prod` sets a non-null value to actually enforce the gate. Precedence is
**env-gate first, then flavor-gate** — do not assume a flavor's `required_version` alone determines
whether a v1 deployment is denied; check which environment the input targets first.

**Gotcha (live-confirmed):** the local OPA governance gate also blocks destructive shell commands
(e.g. `rm -rf` on a legacy directory) as a safety net independent of the deploy-policy packages
above — if a destructive command is unexpectedly refused, check whether this gate fired before
assuming a shell/permissions problem.

---

---

## tmpfs relocations need `tmpfiles.d`, not just a `file:` task (2026-07-28)

**Pattern to follow for any future tmpfs relocation in `ansible-wifi`.** Full rationale and the incident that produced it:
`smc-file-writing-analysis/.archcore/rules/RULE-016-tmpfs-relocation-needs-tmpfiles-for-daemon-dirs.md` and `docs/log-audit-results.md` `20260728_1240`.

### The failure mode

`roles/smc_rsyslog` relocates squid/mosquitto logs onto the `/var/log/smc-groups` tmpfs, creating their subdirs with `file: state: directory`. That is a **one-time deploy action**, and tmpfs
contents are destroyed on every reboot. squid and mosquitto do not create their own log directory — they abort. Result: squid `FATAL` at boot and a user-facing outage.

**The part that makes it dangerous:** the relocation block is guarded on `stat.islnk` ("not yet relocated"), which is correct for idempotency but means the subdir-creation task **no-ops on a
node that has already been relocated** — including one that has since rebooted and lost the directory. So "just re-run the playbook" does not fix it. There is no self-healing path.

**And it is invisible until a reboot.** On 2026-07-28 only 2 of 15 nodes had failed; the other 13 carried the same defect with pre-deploy uptimes. Never conclude a tmpfs relocation is
reboot-safe from "all nodes healthy" — correlate against uptime first.

### The required shape

```yaml
- name: Ensure smc-groups tmpfs subdirs are recreated on every boot (tmpfiles.d)
  template:
    src: smc-log-groups.tmpfiles.conf.j2
    dest: /etc/tmpfiles.d/smc-log-groups.conf
    owner: root
    group: root
    mode: '0644'
  register: smc_loggroups_tmpfiles
  when: hotspot_flavor == 'rcp'

- name: Apply the tmpfiles rules now (heals a node that already lost its subdirs)
  command: systemd-tmpfiles --create /etc/tmpfiles.d/smc-log-groups.conf
  when:
    - hotspot_flavor == 'rcp'
    - smc_loggroups_tmpfiles is changed
  changed_when: true
```

Four things that matter:

1. **Keep owner/mode in sync** with the `file:` tasks that create the same dirs (`proxy:proxy 0750` for squid, `mosquitto:mosquitto 0740` for mosquitto).
2. **Gate optional daemons in the template.** mosquitto is absent on tjuntjuntjara; a `tmpfiles.d` rule naming a non-existent user makes `systemd-tmpfiles` log a hard error every boot. Use
   `{% if 'mosquitto.service' in (ansible_facts.services | default({})) %}` — which requires `service_facts` to have run earlier in the role (it already does, for the mosquitto relocation guard).
3. **Apply immediately**, so an already-broken node is healed by the run rather than waiting for its next boot.
4. **Ordering needs no special handling** — `systemd-tmpfiles-setup.service` is `After=local-fs.target` (so after the fstab tmpfs mounts) and completes within `sysinit.target`, before
   `multi-user.target` starts squid/mosquitto.

### Verifying without breaking production

Don't delete the live directory to prove recreation (the OPA destructive-command gate will block it, correctly). Use a scratch rule on the same tmpfs —
`d /var/log/smc-groups/_tmpfiles_probe 0750 proxy proxy -` → `systemd-tmpfiles --create <file>` → confirm owner/mode → remove probe. Same mechanism, zero service risk.

## Reclaiming state that a role's own tooling can't see (`smc_system` journal reclaim, 2026-07-28)

`roles/smc_system` now removes the orphaned `/var/log/journal` left behind by the `Storage=volatile` conversion. Two authoring points generalise:

- **Guard on runtime evidence, not on config intent.** The reclaim fires only when `/run/log/journal` exists — proof journald is *actually* volatile. Guarding on "we wrote `Storage=volatile` to
  the drop-in" would delete live logs on a node whose journald had not restarted yet.
- **`meta: flush_handlers` before destructive follow-up work.** The volatile config notifies `Restart journald`; without flushing, a first-time conversion would delete the journal while journald
  still held it open and was still writing persistently.

See `07_hardware-overlay.md` for the fleet numbers and why `journalctl --vacuum-*` cannot do this job.

---

## Narrowing tags: ask what the tag EXCLUDES (2026-07-28)

Full rule: `smc-file-writing-analysis/.archcore/rules/RULE-017-narrowing-tag-must-select-the-repair-tasks.md`. Incident detail: `docs/log-audit-results.md` `20260728_1500`.

### The failure

`roles/smc_application` has a block that wipes and re-clones `/var/www/html/wifi` (`file: state=absent force=yes` then `git`), and a **separate** block that chmods `application/cache` and
`application/logs` to 0777 so Apache (`www-data`) can write them. Git recreates those directories at 0755 root:root.

A `wifi_git` tag was added in July 2026 to scope a commit-bump deploy narrowly. It tagged the **destructive** block and left the **repair** block untagged. The narrow run therefore wiped and never
repaired, `Kohana::init()`'s `is_writable(APPPATH.'cache')` threw before routing, and **10 of 16 rcp captive portals were down for 7 days.**

**Rule: if a tagged block destroys or recreates state, every task that repairs that state must carry the same tag.** Ask what a new tag excludes, not just what it includes.

### Why it stayed invisible for a week

Worth knowing as a diagnostic signature, because all four properties fight detection:

- Kohana prints the error itself, so the response is **HTTP 200** with a plain-text body. A status-code health check passes. **HTTP 200 is not a health check** — assert on body content.
- It throws in `init()` before routing, so nothing reaches PHP's error handler and `apache2/error.log` stays clean.
- The `kohana status:update:*` CLI crons run **as root**, pass the writability check, and keep feeding Eclipse — upstream data keeps flowing, so nothing alerts.
- Already-authorised sessions are unaffected (enforcement is iptables/conntrack), so the site looks half-alive rather than down.

### `--tags` on this role is destructive, not a repair path

`--tags wifi_dev_repo` (renamed from `wifi_git` 2026-07-28) **wipes and re-clones the portal**. Confirmed by check-mode dry run: `clear old /var/www/html/wifi repository` reports `changed`. Do not
reach for it to fix permissions. The safe repair is ad-hoc:

```bash
ansible -i inventories/rcp/prod <hosts> -m file \
  -a "path=/var/www/html/wifi/application/{cache,logs} state=directory mode=0777 owner=root group=root"
```

Also note `roles/smc_teleport/templates/teleport.yaml.j2` runs `cat /var/www/html/wifi/application/config/site.txt` **every 60 s** as the Teleport `id` dynamic label — that label drops for every node
during the wipe window.

### Tracing an identifier in this repo

Two traps, both hit during the 2026-07-28 audit:

1. **The same word is often both a tag and a variable.** `wifi_git` was 3 tag declarations against 30 variable usages (`{{ wifi_git.repo }}`, the role-invocation vars in `smc_bases.yml` and
   `smc_rise_deploy.yml`, `smc_bases_wifi_git` in five inventory flavors, plus the `jenkins_wifi_git`/`ansible_wifi_git` family). Classify every hit before editing, and anchor the edit regex
   (`^\s*tags:\s*<name>$`) rather than doing a blind replace.
2. **A yml-only grep is not enough — include `*.j2`.** `roles/smc_teleport/templates/teleport.yaml.j2` consumes `wifi_git` as template data, and the first audit sweep (yml/yaml/sh/cfg/md) missed it
   entirely.

### Renaming a tag fails silently

Ansible emits **no unmatched-tag warning**. After the rename, `--tags wifi_git` still **exits 0 and runs 37 tasks** — all of them `always`-tagged (apt cache, lock clearing, fact gathering) and
**none**
of them `smc_application`. A stale saved command produces a run that looks successful and never touches the thing it names. Flush runbook and shell-history copies whenever a tag is renamed.

### Verification order that actually catches this

`--syntax-check` and `--list-tasks` tell you selection, never behaviour. Only `--check` reveals that a selected task is destructive:

1. `--tags X --list-tasks` and `--skip-tags X --list-tasks` — what is in, what is now out.
2. `--check` against one host — read which tasks report **changed**.
3. Confirm no regression to the broad tag (`--tags application` here) and to full runs. Tags are additive, so adding one never removes a task from an untagged full run.
````

## File: references/09_url-capture-pcap.md
````markdown
# SMC URL Capture and PCAP Workflows

## Contents
- Why url_capture was rewritten
- Replacement architecture
- Design decisions
- Remote storage layout
- Ansible role changes
- systemd service
- Node and Ansible verification
- Fetching PCAPs
- Rollout policy
- Fleet deployment lessons
- PIN/session enforcement degradation

## 10. url_capture v2 — Python Streaming Service

### Why the Rewrite

The legacy `screen` + cron architecture had three problems:
1. **SSD wear** — tcpdump wrote one large continuous `.pcap` to `/url_capture/` (SSD); rsync
   shipped data up to 8 hours late accumulating ~22MB/day on disk with no rotation.
2. **Fragile supervision** — a `*/2` cron checked whether a `screen` session existed; race
   condition possible if cron fired while tcpdump was dying. Restart latency up to 2 min.
3. **No observability** — state was visible only via `screen -ls`; no structured logs, no stats.

### What Replaced It

A single Python daemon (`url_capture_manager.py`) installed as a **systemd service** replaces
all three cron jobs.

| Removed cron | Replaced by |
|---|---|
| `*/2` screen watchdog | `systemd Restart=always` (15 s → 60 s restart delay) |
| `23:59` midnight kill | Boundary-aware chunk duration — the last chunk before midnight is shortened so the next day starts in a new file |
| `0,8,16` rsync | Continuous `drain_queue()` loop inside daemon |
| `screen` package | Removed from role package list |

During migration, `v1_teardown.yml` removes the v1 crons, stops the legacy `screen`
capture, waits for tcpdump to close the active file, then performs a full rsync flush of
`/url_capture/` to the legacy remote hostname directory. That final flush is a hard gate:
SSH or rsync failure must fail the play rather than being ignored.

`v2_setup.yml` also performs an idempotent legacy-data safety flush before starting or
restarting v2. If any old `/url_capture/YYYYMM/*.pcap` files still exist locally, it rsyncs
only missing or changed legacy PCAPs to the legacy remote hostname directory, marks changed
only when files transfer, and fails the play on SSH or rsync errors. After that flush
completes successfully, `v2_setup.yml` clears the contents of the local legacy
`/url_capture/` directory so already-flushed v1 files do not remain on the SMC disk.

### Architecture

```
tcpdump subprocess (5-min chunk)
    ↓ capture chunk → /run/url_capture/work/<host>-bridge_501-YYYYMMDD_HHMMSS.pcap
    ↓ compress (pigz → gzip fallback) → .pcap.gz
    ↓ move to /run/url_capture/ (tmpfs — RAM, no SSD write)
    ↓ upload via SCP (atomic: .part → rename) to remote
    ↓ delete from tmpfs on success
    ↓ repeat
```

**Three selectable modes** (set via `url_capture_mode` Ansible var):

| Mode | Queue | On upload failure |
|---|---|---|
| `tmpfs-buffer` (default) | `/run/url_capture/` (RAM, 256 MB cap) | Queue in RAM; evict oldest when cap hit |
| `stream-only` | None | Drop chunk; increment `dropped` counter |
| `disk-spool` | `/url_capture/spool/` (disk, 1 GB cap) | Accumulate on disk; drain when link recovers |

**Why tmpfs-buffer is default:** satellite links drop frequently but briefly. 256 MB holds
~50–250 chunks — enough to survive hours of outage without SSD writes.

**Explicit tmpfs mount:** v2 mounts `/run/url_capture` with `run-url_capture.mount`.
This makes the RAM-backed buffer visible as its own mount in `findmnt` output instead of
only inheriting the parent `/run` tmpfs mount.

**tmpfs vs zram:** tmpfs is a RAM-backed virtual filesystem. zram is compressed RAM used as
swap. URL capture uses tmpfs for low-latency staging — not zram. pcap data compresses
poorly (high entropy) so zram's compression advantage is minimal here.

### Key Design Decisions

- **tcpdump primary** (not dumpcap): already in use, operationally familiar, supports `-w -`
  for direct pipeline. dumpcap has stronger ring/rotation but adds new operational path.
- **5-minute chunks**: 288 files/day. Chosen for upload atomicity and RAM efficiency. The
  chunk that reaches midnight in Melbourne local time is shortened so pcap contents do not
  span calendar days.
- **YYYYMMDD/ subfolders on remote**: keeps per-day dir to 288 files (manageable for `ls`).
  Flat YYYYMM/ would be ~8,640 files/month per SMC. The folder date is derived from the
  timestamp embedded in the `.pcap.gz` filename, not upload wall-clock time, so a chunk that
  starts just before midnight stays under the capture-start day.
- **Filename keeps full hostname**: `amata-smc01-bridge_501-20260421_083000.pcap.gz`.
  Canonical source identifies the SMC by full hostname for unambiguous attribution.
- **SIGTERM handler**: sets a stop flag and terminates the tcpdump subprocess cleanly on
  `systemctl stop`. Without this, tcpdump stays as an orphan writing to work dir.
- **Work dir stays on tmpfs**: default work dir is `/run/url_capture/work`, not `/tmp`, so
  current chunks and queued chunks stay on the same RAM-backed filesystem. The manager also
  falls back to copy+unlink when a non-default mode crosses filesystems.
- **Mount is explicit**: `url-capture.service` requires `run-url_capture.mount`, whose
  `Where=/run/url_capture` and `Type=tmpfs` make the RAM buffer obvious during operations.
- **Orphan work recovery**: on startup the manager scans `/run/url_capture/work` for closed
  orphan `.pcap` or `.pcap.gz` files from interrupted captures, compresses/queues/uploads them
  through the normal path, and removes empty pcap headers.
- **`--healthcheck` flag**: prints stats JSON and exits 0 for cron/nagios health checks
  without stopping the service.

### Remote Storage Layout

```
/home/sslurlcapture/urlcapture_storage/
  amata-smc01/
    20260421/                               ← YYYYMMDD subfolder (288 files/day)
      amata-smc01-bridge_501-20260421_000000.pcap.gz
      amata-smc01-bridge_501-20260421_000500.pcap.gz
      ...
    20260422/
      ...
```

SSH key: `/var/local/sslurlcapture/sslurlcapture.id_rsa` (unchanged from legacy).
Remote user: `sslurlcapture` (unchanged).

### Ansible Role Changes (smc_url_capture)

**New files:**
- `roles/smc_url_capture/files/url_capture_manager.py` — Python daemon
- `roles/smc_url_capture/templates/url-capture.service.j2` — systemd unit
- `roles/smc_url_capture/templates/run-url_capture.mount.j2` — explicit tmpfs mount for
  `/run/url_capture`

**Modified files:**
- `roles/smc_url_capture/vars/urlcapture_vars.yml` — 6 new vars added:
  ```yaml
  url_capture_manager_script: /usr/local/sbin/url_capture_manager.py
  url_capture_mode: tmpfs-buffer
  url_capture_iface: bridge_501
  url_capture_chunk_seconds: 300
  url_capture_tmpfs_dir: /run/url_capture
  url_capture_tmpfs_mount_unit: run-url_capture.mount
  url_capture_tmpfs_cap_mb: 256
  ```
- `roles/smc_url_capture/tasks/main.yml` — `screen` → `python3`; crons → service

**Unchanged files (do not modify):**
- `roles/smc_url_capture/files/url_capturev1.sh` — legacy, kept for rollback reference
- `roles/smc_url_capture/templates/rsync_urlcapture.sh.j2` — legacy rsync script; still
  deployed to `/var/local/sslurlcapture/rsync_urlcapture.sh` for manual rollback use (no cron)

**Canonical Python source** (update here, then copy to role):
```
/Volumes/Data/_ai/_project/project_stuff/apn/smc-file-writing-analysis/plans/dns-query-capture-manager.py
```

### systemd Service

```ini
[Mount]
What=tmpfs
Where=/run/url_capture
Type=tmpfs
Options=mode=0755,size=256M,nosuid,nodev,noexec
```

```ini
[Unit]
Requires=run-url_capture.mount
Wants=network-online.target time-sync.target
After=network-online.target time-sync.target run-url_capture.mount

[Service]
Type=simple
Environment=TZ=Australia/Melbourne
ExecStartPre=/usr/sbin/ntp-wait -n 60 -s 5 -v
ExecStart=/usr/bin/python3 /usr/local/sbin/url_capture_manager.py \
  --mode tmpfs-buffer --iface bridge_501 --chunk-seconds 300 \
  --remote-host {{ teleport_fqdn }} ...
Restart=always
RestartSec=60
StandardOutput=journal
StandardError=journal
```

### Verification (on SMC node after deploy)

```bash
# Service status
systemctl status url-capture
journalctl -u url-capture -f

# After first chunk (~5 min) — tmpfs queue draining
ls /run/url_capture/

# Confirm explicit RAM mount
findmnt -T /run/url_capture/work -o TARGET,SOURCE,FSTYPE,OPTIONS
df -T /run/url_capture/work

# Health check (non-disruptive)
python3 /usr/local/sbin/url_capture_manager.py --healthcheck

# Confirm old crons gone
crontab -l | grep -E 'url_capturev1|tcpdump|rsync_urlcapture'   # should return nothing

# On remote — new YYYYMMDD subfolder
ls /home/sslurlcapture/urlcapture_storage/<hostname>/$(date +%Y%m%d)/
```

### Ansible verification

```bash
ansible-lint roles/smc_url_capture/
ansible-playbook smc_bases.yml -i inventories/<flavor>/prod \
  --tags smc_url_capture --check --limit <canary_host>
```

### Fetching pcaps (smc_get_pcapv7.yml)

Use `ansible-malik/smc_get_pcapv7.yml` (v7) for mixed legacy/v2 URL-capture pulls.
During migration a site may still have legacy monthly `YYYYMM/` directories, v2 daily
`YYYYMMDD/` directories, or both. v7 handles both layouts for the requested month.

**v7 fetch flow:**
1. Prompts for `YYYYMM` (e.g. `202604`)
2. Finds matching `YYYYMM` and `YYYYMMDD` dirs for that month under each host dir
3. Groups matching dirs by site into `site_capture_dir_map`
4. Tars all matched dirs per site into one monthly archive:
   `amata-smc01-bridge_501-202604-monthly.tar.gz`
5. Rsyncs archives to local `fetched/nbn_accelerate/` or `fetched/rcp/`
6. Extracts archives and flattens any `YYYYMM` / `YYYYMMDD` folders into `extracted/<flavor>/<site>/`
7. Decompresses `.pcap.gz` → `.pcap` via `pigz -df`, or `gzip -df` when pigz is unavailable
8. Deletes zero-byte and `generic-*.pcap` files
9. Runs `pcapfix` on remaining `.pcap` files and removes originals when a fixed copy is produced
10. Writes `checked_pcaps.txt` in the extracted root after all checks complete

**Local output layout:**
```
fetched/
  nbn_accelerate/
    amata-smc01-bridge_501-202604-monthly.tar.gz
extracted/
  nbn_accelerate/
    amata/                                    ← short name (regex strips -smc01)
      state                                   ← "sa"
      amata-smc01-bridge_501-20260401_000000.pcap
      amata-smc01-bridge_501-20260401_000500.pcap
      ...                                     ← daily and/or 5-minute pcaps after checks
checked_pcaps.txt                             ← relative list of final checked pcaps
```

Note: the extracted folder uses the **short site name** (`amata`) from the regex
`'^(.*?)-smc0.*'` applied to the archive filename. The pcap filenames themselves
retain the full hostname (`amata-smc01-...`) as captured at source.
Do not expect `YYYYMM` or `YYYYMMDD` subdirectories under the extracted site folder after
`--tags process_files`; the processing step intentionally flattens them.

Validation anchor: APN `202605` was validated with mixed inputs from `kalumburu-smc01`
(legacy `202605/` plus v2 `20260501/`...) and `jigalong-smc01` (legacy `202605/` only).
The process run completed with `checked_pcap_count=1696`, no retained `.pcap.gz` files,
and final pcaps directly under `extracted/rcp/kalumburu/` and `extracted/rcp/jigalong/`.

**Usage:**
```bash
# fetch all
ansible-playbook -i inventories/rcp/prod ../ansible-malik/smc_get_pcapv7.yml --tags fetch_files

# fetch specific flavor
ansible-playbook -i inventories/cw/prod ../ansible-malik/smc_get_pcapv7.yml \
  -l cw-teleport01,localhost, --tags fetch_files

# process only (after manual fetch or re-run)
ansible-playbook -i inventories/apn/prod ../ansible-malik/smc_get_pcapv7.yml \
  -l apn-teleport01,localhost, --tags process_files
```

### Rollout Policy

- Canary on 1–3 SMC nodes first
- Verify the expected remote storage appears for the site: legacy `YYYYMM/`, v2 `YYYYMMDD/`, or both during migration
- Verify `journalctl -u url-capture` shows clean chunk/upload cycles
- Staged fleet rollout after canary passes
- `rsync_urlcapture.sh` stays deployed (no cron) as manual drain option during canary

### Fleet Deployment Lessons (2026-05-18)

#### Ansible + Teleport: host key verification fails for new hosts
**Symptom:** `ansible-playbook` fails with `Host key verification failed` on a host that `tsh ssh` reaches fine.

**Cause:** The `*.teleport.apn.au` block in `~/.ssh/config` has `ProxyCommand` (tsh) but no `UserKnownHostsFile`. Ansible falls back to `~/.ssh/known_hosts`, which has no entry for new Teleport-managed hosts. tsh uses `~/.tsh/known_hosts` (Teleport CA-signed) which trusts all cluster hosts automatically.

**Fix:** Add `UserKnownHostsFile /Users/malik.ahmad/.tsh/known_hosts` to the `Host *.teleport.apn.au !teleport.apn.au` block in `~/.ssh/config`. This is a one-time fix — all future Teleport hosts work without per-host key acceptance.

#### cisofy-lynis apt source blocks `apt-get update` on satellite-linked sites
**Symptom:** `apt-get update` fails silently (empty error, rc≠0) on nbn_accelerate or other sites.

**Cause:** `/etc/apt/sources.list.d/cisofy-lynis.list` contains a `deb https://packages.cisofy.com/...` entry. Sites on satellite links cannot reach this host.

**Fix:** The `custom_apt_update_cache.yml` helper now comments out that line via `ansible.builtin.lineinfile` (with `backrefs: true`) before running apt. Check for other unreachable third-party apt sources when `apt-get update` fails with empty errors.

#### Broad nightly `pkill -9 python3` kills url-capture.service
**Symptom**: `url-capture.service` is killed at 23:59 every night; journal shows kill + restart at 00:00:02. Orphan pre-midnight chunk uploads immediately after restart. No data loss observed but lifecycle is not clean.

**Cause**: `roles/smc_application/tasks/main.yml` task `Kill Python3 processes to avoid stale processes` installs a root crontab:
```
59 23 * * * pkill -9 python3 >/dev/null 2>&1
```
This was intended for `webapp.py` (WH flavor). It kills **all** python3 processes, including `url_capture_manager.py`.

**Fix**: Replace broad `pkill -9 python3` with a narrowly targeted kill (process name or pid file). Gate it to the specific flavor that needs it (`hotspot_flavor == 'wh'`). Not yet implemented as of 2026-05-07.

#### `rsync_urlcapture.sh.j2` — two bugs fixed (2026-05-01)
Even though v1 rsync crons are removed under url_capture v2, the script stays deployed for manual rollback use. Two bugs were corrected in the template:

1. **`yearmonth_today` not evaluated**: Was a literal string `$(date +%Y%m)` missing the outer `$()` → never expanded → rsync failed to find today's directory. Fixed by wrapping in command substitution.

2. **Missing month-boundary rsync**: On the 1st of the month there was no block to rsync the previous month's data. Added: a conditional block that fires only when today ≠ yesterday's month and rsyncs the prior month's directory.

**Location**: `roles/smc_url_capture/templates/rsync_urlcapture.sh.j2`

#### Expected daily url-capture volume: ~270 files/day
5-minute chunks over ~22.5h (accounting for midnight boundary restart overhead) = ~270 `.pcap.gz` files per day in `urlcapture_storage/<hostname>/YYYYMMDD/`. Lower counts indicate service gaps. May 4, 2026 showed 249 files due to the SSH deadlock incident (~1.75h gap).

#### Healthy check commands (post-deploy verification)
```bash
# Service status
tsh ssh root@<host> "systemctl status url-capture.service --no-pager && journalctl -u url-capture.service -n 10 --no-pager"

# Remote storage file count for today
tsh ssh root@<host> "ssh -i /var/local/sslurlcapture/sslurlcapture.id_rsa -o StrictHostKeyChecking=no sslurlcapture@teleport.apn.au 'ls /home/sslurlcapture/urlcapture_storage/<host>/$(date +%Y%m%d)/ | wc -l'"
```

### PIN/Session Enforcement Degraded While Content Filtering Still Works (`nbn_accelerate` / `rcp`)

| Field | Value |
|---|---|
| Error text | Users report PIN/session behavior inconsistent while web filtering still blocks content |
| Typical context | Host in storage-degraded or read-only state; automation attempts to restart policy services but write paths fail |
| Cause class | Control-plane partial failure: per-user mark refresh failed, but baseline DNS/HTTP filter redirect path remains active |
| Immediate checks | `systemctl status netfilter-persistent`; `iptables -t mangle -S ECLIPSE_MARK`; `iptables -t mangle -S ECLIPSE_METERED_TIME`; `dig @127.0.0.1 www.pornhub.com`; `tail -n 200 /var/log/squid/access.log \| egrep 'TCP_DENIED|403|302'` |
| Detection pattern | `ECLIPSE_MARK` and `ECLIPSE_METERED_TIME` chains empty, `netfilter-persistent` failed, but Squid denies and Umbrella block IP responses still present |
| Operational impact | Baseline filtering still enforced; per-user/PIN granularity unreliable (stale sessions may continue, new/rollover PIN behavior inconsistent) |
| Fix pattern | Recover host to RW / alternate disk, restore `netfilter-persistent`, repopulate mangle mark chains via normal role/service path, then validate end-to-end PIN issuance/expiry flow |
| Validation commands | `iptables -t mangle -S ECLIPSE_MARK` shows populated rules; non-zero connmark distribution for active bridge_501 users; month rollover PIN expiry/new PIN flow verified from app to kernel marks |

---
````

## File: references/10_captive-portal.md
````markdown
# SMC Captive Portal

## Contents
- Two-tier architecture (incl. PHP SAPI — mod_php, NOT PHP-FPM)
- APN vs NBN Accelerate protocol differences
- Eclipse config.txt sync
- View template versions
- Apache + PHP-FPM wiring (⚠️ historical, ff-smc01 only — never reached production)
- PHP short_open_tag issue
- Kohana exception handler issues
- End-to-end portal verification
- `Directory APPPATH/cache must be writable` — portal dead at bootstrap

## 11. Captive Portal — Architecture, Known Gaps, and Troubleshooting

### 11.1 Two-tier architecture

The captive portal is a two-tier system:

| Tier | Component | Role |
|---|---|---|
| Remote | Eclipse server (`wifi.activ8me.net.au:443`) | Site config source of truth; pushes config.txt; can run arbitrary Commands on SMC |
| Local | Kohana PHP app at `/var/www/html/wifi` | Renders portal; reads config.txt; calls Eclipse on each page load |

Apache serves the portal and the Kohana framework handles routing, templating, and Eclipse integration.

**PHP SAPI — corrected 2026-07-28.** This file previously stated flatly that "PHP-FPM processes `.php` files". That is **not true of the production fleet**. Verified on three sampled `rcp` hosts (horn-island, kalumburu, mornington): **zero** `php*-fpm` packages installed, `libapache2-mod-php` installed, `apache2ctl -M` shows `php_module (shared)`, and no `/etc/php/8.1/fpm/` directory exists at all. Production SMCs run **mod_php, executing as `www-data` inside the Apache process** — there is no FPM pool, no socket, and no `proxy_fcgi`.

This matters for any permissions question: file/directory access is decided by `www-data`'s rights, and there is no FPM pool config (`open_basedir`, `chroot`, unit sandboxing) to blame when something is unwritable. See §11.8.

The PHP-FPM material in §11.4 below describes work done on `family-friendly-smc01` in June 2026 that was **reverted and never reached the production fleet** — read it as history, not as current architecture.

### 11.2 Eclipse config.txt sync

**Location**: `/var/www/html/wifi/application/config/config.txt` (NOT the web root — `config.txt` in `/var/www/html/wifi/` is never read)

**How it gets populated**: On every PHP page request, `WiFi_Config::sync()` calls `run_eclipse_command()` which:
1. Reads the `Command` field from the current config.txt
2. If non-empty, executes it via `system($command)` — used for software updates (e.g. `git pull`)
3. Fetches fresh site config JSON from Eclipse and writes it to config.txt

**What Eclipse syncs**: JSON blob containing `VIEW_TEMPLATE_VERSION`, `WELCOME_MSG`, `VLAN_501_ACCESS_METHOD`, `PREPAID_BLOCKS`, `TC_SPEED`, `Limited_Sites`, `Asterisk`, `Hardware_List`, `Software_List`, `Command`, etc.

**What Eclipse does NOT sync**: PHP view template files — those come from the Bitbucket git clone at provision time and are only updated if Eclipse sends a `Command` with a git pull.

**First-request bootstrap**: If config.txt is missing (fresh provision, no Eclipse contact yet), the app defaults to `VIEW_TEMPLATE_VERSION=v1` → serves the v1 template with `p.a8me.au` base URLs. After first PHP request hits the live host, Eclipse populates config.txt (v3, `wifi.a8me.au`).

**Check Eclipse reachability**:
```bash
curl -sk https://wifi.activ8me.net.au/ -o /dev/null -w "%{http_code}"
# or
telnet wifi.activ8me.net.au 443
```

**Check current config.txt**:
```bash
cat /var/www/html/wifi/application/config/config.txt | python3 -m json.tool
grep VIEW_TEMPLATE_VERSION /var/www/html/wifi/application/config/config.txt
```

### 11.3 View template versions

| Version | Base href | Notes |
|---|---|---|
| v1 | `https://p.a8me.au/` | Old/legacy; loads when config.txt missing |
| v3 | `http://wifi.a8me.au/` | Standard for RCP/NBN SMCs (NBN-59-config-management branch) |
| v4 | `http://wifi.a8me.au/` | SMP variant (release/rct_v4 branch) |

Eclipse sets `VIEW_TEMPLATE_VERSION` in config.txt. If the portal is showing `p.a8me.au` URLs, config.txt is missing or stale.

### 11.4 Apache + PHP-FPM wiring — HISTORICAL, ff-smc01 only (⚠️ corrected 2026-07-28)

> ⚠️ **Supersession note.** This section was written as if the PHP-FPM wiring was fleet-wide and permanently fixed in Ansible on 2026-06-26. **Both claims are wrong.** Verified 2026-07-28:
> - Repo-wide grep finds **no `SetHandler` in any role template** (the only hit in the tree is a vendored `community.general` test fixture). `portal-site.conf.j2` contains no PHP handler config.
> - The enabled-modules list in `roles/smc_application/tasks/ubuntu-apache-install-configure.yml` is only `rewrite` and `ssl` — **no `proxy`, no `proxy_fcgi`**.
> - Production `rcp` hosts have **no `php*-fpm` package installed** and run mod_php instead (see §11.1).
>
> This matches the long-standing SCRATCHPAD open item recording that the Ansible PHP-FPM change was reverted and needs a different approach. Treat everything below as a record of the `family-friendly-smc01` hotfix work only. **Do not use it to reason about production portal behaviour.**

**Symptom**: Portal returns raw PHP source code instead of rendered HTML.

**Cause**: Apache does not know to proxy `.php` requests to PHP-FPM unless explicitly configured.

**Required configuration** (now in `portal-site.conf.j2`):
```apache
<FilesMatch "\.php$">
    SetHandler "proxy:unix:/run/php/php8.1-fpm.sock|fcgi://localhost"
</FilesMatch>
```

**Required Apache modules** (now in `ubuntu-apache-install-configure.yml`):
```yaml
- proxy        # must be enabled before proxy_fcgi
- proxy_fcgi   # handles the unix socket proxy to PHP-FPM
```

**Check Apache is passing PHP to FPM**:
```bash
apache2ctl -M | grep -E "proxy|fcgi"   # should show proxy_module, proxy_fcgi_module
systemctl status php8.1-fpm
ls /run/php/php8.1-fpm.sock            # socket must exist
curl -s http://localhost/ | head -5    # should be HTML, not <?php
```

**Alternative approach (Ubuntu packaged config — applied as live hotfix 2026-06-23)**:
```bash
a2enmod proxy_fcgi setenvif
a2enconf php8.1-fpm     # enables /etc/apache2/conf-available/php8.1-fpm.conf (installed by php8.1-fpm package)
systemctl restart apache2
```
This enables the PHP-packaged Apache config which sets `SetHandler` globally. The Ansible template approach (above) would embed `SetHandler` directly in the VirtualHost, making it self-contained and not dependent on `a2enconf php8.1-fpm`. ~~the Ansible template approach is now canonical~~ — **neither is canonical**; the Ansible template change was reverted and production runs mod_php with no FPM at all (§11.1).

**Historical note (corrected 2026-07-28)**: the live hotfix on `family-friendly-smc01` 2026-06-23 (`a2enconf php8.1-fpm`) did happen. The follow-on claim that a permanent Ansible fix "landed 2026-06-26" is **false** — the change was reverted and is not in the repo. Note also that `ubuntu-php-install-configure.yml`'s `php_pkg_suffixes` list *does* include `fpm`, but that install path is gated behind `php_reinstall_needed`, and no production `rcp` host actually has an FPM package installed. Do not infer the running SAPI from the package list — check `apache2ctl -M` on the box.

### 11.5 PHP short_open_tag issue (Kohana v3 views)

**Symptom**: Portal renders but shows `Undefined variable $error`, `Undefined variable $captive_portal_message`, or `Undefined variable $version` inline in the HTML. Action buttons (Terms and Conditions, Start Browsing) may be absent.

**Root cause**: PHP 8.1 has `short_open_tag = Off` by default.
- `<? if (isset($var)) { ?>` → **NOT processed** as PHP; passes through as literal text
- `<?= $var; ?>` → **always processed** (echo shorthand enabled since PHP 5.4)
- Result: the `isset()` guard never runs; `<?= $var ?>` executes unconditionally; undefined variable echoes through Kohana error handler
- Orphan `<?php } ?>` closing tags halt PHP execution mid-template, cutting off all subsequent HTML output

**Affected files** (Bitbucket wifi.git, NBN-59-config-management branch):
- `application/views/v3/wifi/welcome.php`
- `application/views/v3/wifi/welcome_contents.php`
- `application/views/v3/wifi/base.php`
- `application/views/v3/wifi/prepaid/resume.php`
- `application/views/v3/wifi/prepaid/success.php`

**Hotfix on live host** (not persistent across software updates):
```bash
# Find all short tags in v3 views
grep -rn "^<? " /var/www/html/wifi/application/views/v3/

# Fix — sed (note: double-substitution hazard if <?php already exists)
sed -i 's/<?\s*/<?php /' /path/to/file.php
# Always follow with cleanup pass for double-substitution artifacts:
grep -rl "<?phpphp" /var/www/html/wifi/application/views/v3/ | xargs sed -i 's/<?phpphp/<?php/g'
```

**Permanent fix**: Replace all `<? ?>` with `<?php ?>` in Bitbucket wifi.git `NBN-59-config-management` branch. Raised to dev team 2026-06-26.

**Check short_open_tag setting**:
```bash
php -r "echo ini_get('short_open_tag');"   # 0 = off (PHP 8.1 default)
grep short_open_tag /etc/php/8.1/fpm/php.ini
```

### 11.6 Kohana exception handler issues (fixed 2026-06-24 on ff-smc01)

**Symptom 1**: Portal returns blank 500 page.
**Cause**: `email_exception()` called in exception handler but function never defined → Fatal Error → empty body.
**Fix**: Guard call with `if (function_exists('email_exception'))`.

**Symptom 2**: Exception message text appears in page body.
**Cause**: Debug line `echo $e->getMessage(); exit;` left in exception handler.
**Fix**: Remove the debug echo.

**Symptom 3**: E_NOTICE errors echoed to page via Kohana error handler.
**Cause**: `error_reporting(E_ALL | E_STRICT)` in Kohana `index.php` converts E_NOTICE to ErrorException via `set_error_handler`.
**Fix**: Change to `error_reporting(E_ALL & ~E_NOTICE)` in `index.php`, or fix the underlying undefined variables.

### 11.7 End-to-end portal verification

```bash
# From SMC itself — check portal responds with HTML
# Must use the real ServerName. Probing localhost with a Host: header hits 000-default
# and returns /var/www/html/index.html (10671 bytes) even when the portal is fully dead.
curl -s wifi.a8me.au | grep -E "btn-apn|Terms|Start Browsing|Undefined|base href"

# From client on VLAN 501 — check captive redirect
curl -s http://1.1.1.1/ -L | grep -i "wifi\|activ8me\|Terms"

# Check which PHP SAPI is actually live (expect php_module = mod_php, NOT proxy_fcgi)
apache2ctl -M | grep -E "php_module|proxy_fcgi"

# Check cache/logs are writable by www-data — a 0755 here kills the whole portal (§11.8)
stat -c '%a %U:%G' /var/www/html/wifi/application/cache /var/www/html/wifi/application/logs

# Check Apache logs for PHP errors
# NOTE: the §11.8 bootstrap failure leaves NOTHING here — an empty log does not mean healthy
tail -50 /var/log/apache2/error.log | grep -E "PHP|AH"

# Check Eclipse sync happened
stat /var/www/html/wifi/application/config/config.txt
python3 -m json.tool /var/www/html/wifi/application/config/config.txt | grep VIEW_TEMPLATE
```

---

### 11.8 `Directory APPPATH/cache must be writable` — portal dead at bootstrap (2026-07-28)

**Symptom**: every portal request returns a 40-byte plain-text body `Directory APPPATH/cache must be writable`, with **HTTP status 200**, and **nothing in `/var/log/apache2/error.log`**.

**Mechanism**: Kohana checks writability unconditionally during `Kohana::init()`, before any routing:

```
/var/www/kohana-base/system/classes/kohana/core.php:281
    if ( ! is_writable(Kohana::$cache_dir))
        throw new Kohana_Exception('Directory :dir must be writable', ...);
```

`Debug::path()` rewrites the `APPPATH` prefix to the literal token `APPPATH/`, which is why no real path appears in the message. Kohana catches and *prints* the exception, which is why the status is 200 and apache's error log stays silent — **a status-code-only health check cannot detect this**.

**The same exception exists for logs** at `system/classes/kohana/log/file.php:31`. Fix both `application/cache` and `application/logs`, or the failure just moves one step later.

**Cause**: the directories are `0755 root:root` while Apache runs mod_php as `www-data` (§11.1). They land at 0755 whenever git recreates them — the tracked content is only a `.gitignore` stub, so a fresh clone applies umask 022. `roles/smc_application` chmods them to `0777` explicitly; if that task is skipped, the portal dies.

**Check**:
```bash
stat -c '%a %U:%G' /var/www/html/wifi/application/cache /var/www/html/wifi/application/logs
# expect 777 root:root on both

V=$(ls /etc/apache2/sites-enabled/ | grep -v 000-default | head -1 | sed 's/.conf$//')
curl -s http://$V/ | head -c 40
# expect HTML, not the error string
```

⚠️ **Do not probe `http://localhost/` with a `Host:` header** — Apache serves the `000-default` vhost regardless and returns `/var/www/html/index.html` (10671 bytes), which looks healthy on a completely dead portal. This produced a wrong "no impact" conclusion during the 2026-07-28 incident. Always curl the real ServerName.

**Fix**:
```bash
ansible -i inventories/<flavor>/prod <hosts> -m file \
  -a "path=/var/www/html/wifi/application/cache state=directory recurse=yes owner=root group=root mode=0777"
# repeat for .../application/logs
```

**Incident**: 2026-07-21 → 07-28, 10 of 16 in-scope `rcp` sites fully down for 7 days. Root cause was an Ansible tag gap, not drift — see `08_ansible-authoring.md` and rule-005 in the ansible-wifi repo. Undetected because the Kohana usage/status crons run as **root**, for whom a 0755 root-owned dir is writable, so they kept succeeding and Eclipse kept receiving data throughout. Full RCA: `local-knowledge-ansible/ansible-wifi/issues/rcp-fleet/rcp-captive-portal-cache-perms-outage-20260728_1240.md`.

### 11.9 APN vs NBN Accelerate portal protocol differences (2026-08-03, code-inspection only — not live-validated)

Everything in §11.1–11.8 above was extracted from APN-cluster (`rcp`) incidents and live hosts. Two
group_vars-level differences apply on the NBN Accelerate cluster (`nbn_accelerate`/`nbn_wh`) that are
**not yet confirmed against a live cw-cluster host**:

| Var | APN cluster (`rcp`/`rct`/`wh`) | NBN Accelerate cluster (`nbn_accelerate`/`nbn_wh`) |
|---|---|---|
| `smc_bases_portal_protocol` | `http` | `https` — cw-side portals are HTTPS-only |
| `smc_bases_blocked_url_redirect` | `activ8me.net.au/blocked/wifi/` | `blocked.communitywifi.net.au` |

Implications worth checking before assuming §11.1–11.8 troubleshooting steps transfer directly to a
cw-cluster host:
- The `curl` verification commands in §11.7 (`curl -s wifi.a8me.au | grep ...`) use APN-cluster
  hostnames/base-hrefs (`p.a8me.au`/`wifi.a8me.au`, §11.3) — a cw-cluster host's equivalent hostname
  and expected base href are not documented anywhere in this pack yet.
- HTTPS termination on the cw side means an Apache vhost/TLS-cert config exists that has no APN-side
  equivalent to reference — not yet located or documented.
- The 0755-vs-0777 cache/logs permissions bug (§11.8) is Kohana-framework-level and independent of
  transport protocol, so it plausibly applies identically on cw-cluster hosts, but this is inferred,
  not confirmed live.

See `01_overview.md` "APN Cluster vs NBN Accelerate Cluster — Structural Comparison" for the source
of these two var values, and `13_known-issues.md` "NBN Accelerate cluster coverage gap" for the
broader live-validation gap this note is part of.
````

## File: references/11_vagrant-lab.md
````markdown
# SMC Vagrant Lab

## Contents
- Overview
- Network topology
- Key Vagrant nuances and known issues
- Bring-up procedure
- Useful commands

## 12. Vagrant Lab — family-friendly-vsmc01

### 12.1 Overview

Vagrantfile: `/Volumes/Data/_vagrant/vagrant_stuff/family-friendly-vsmc01/Vagrantfile`

Three VMs defined; only two are typically used:

| VM | Box | RAM/CPU | Role |
|---|---|---|---|
| `family-friendly-vsmc01` | `bento/ubuntu-22.04` | 2GB / 1 | SMC under test |
| `cf-test-client` | `cloudicio/ubuntu-desktop 24.04.1` | 8GB / 4 | Ubuntu Desktop client on VLAN 501 |
| `cf-test-client-02` | `stromweld/windows-11` | — | Windows 11 client (inactive/optional) |

### 12.2 Network topology

**vsmc01 adapter map** (bento/ubuntu-22.04 keeps `ethN` naming in VirtualBox):

| VirtualBox Adapter | Guest Interface | intnet / type | Purpose |
|---|---|---|---|
| adapter 1 (nat1) | `eth0` | NAT (172.29.10.0/24) | Vagrant management + internet access |
| adapter 2 | `eth1` | public\_network (bridged en0) | WAN1 — Mac Wi-Fi |
| adapter 3 | `eth2` | public\_network (no auto\_config) | WAN2 — Mac Wi-Fi (second) |
| adapter 4 | `eth3` | intnet `switch01_unused` (promisc) | Switch01 placeholder — promisc only |
| adapter 5 | `eth4` | intnet `smc01_lan` (promisc) | LAN segment shared with client |

**cf-test-client adapter map** (Ubuntu Desktop 24.04 uses predictable names — NOT `ethN`):

| VirtualBox Adapter | Guest Interface | intnet / type | Purpose |
|---|---|---|---|
| adapter 1 (default NAT) | `enp0s8` | NAT | Vagrant SSH; suppressed as default route |
| adapter 2 | `enp0s9` | intnet `smc01_lan` DHCP | LAN — gets IP from SMC DHCP on VLAN 501 |

> **Critical naming distinction**: The vsmc01 SMC uses `eth0–eth4` (VirtualBox bento box keeps legacy naming). The cf-test-client uses `enp0s8/enp0s9` (Ubuntu Desktop 24.04 predictable names). Scripts or provisioners that assume `eth0/eth1` on the client will silently fail.

### 12.3 Key Vagrant nuances and known issues

**1 — NAT default route suppression on cf-test-client**

Problem: VirtualBox gives `enp0s8` (NAT) a default gateway with low metric (~100), which wins over the SMC gateway on `enp0s9` (metric ~20101). Traffic bypasses the captive portal.

Fix (in Vagrantfile, `run: always`): Writes a netplan override that persists across DHCP renewals and reboots:
```
/etc/netplan/99-no-default-via-enp0s8.yaml:
  network.version: 2
  ethernets.enp0s8.dhcp4: true
  ethernets.enp0s8.dhcp4-overrides.use-routes: false
```
Then `netplan apply && ip route del default dev enp0s8 || true`.

Verify routing is correct:
```bash
# On cf-test-client — should show ONLY SMC default route
ip route show default
# Expected: default via 10.0.0.1 dev enp0s9 proto dhcp metric 20100  (only one line)
```

**2 — VirtualBox orphaned VM cleanup**

If a previous `vagrant up` failed mid-provision, the VM directory may exist on disk but not be registered in VirtualBox. `vagrant up` will fail with `VERR_ALREADY_EXISTS`.

Fix:
```bash
VBoxManage registervm ~/VirtualBox\ VMs/cf-test-client/cf-test-client.vbox
VBoxManage unregistervm "cf-test-client" --delete
```
Never `rm -rf` the VM directory — leaves orphaned disk records in VirtualBox internal media registry causing future conflicts.

**3 — VirtualBox Guest Additions compile failure on Apple Silicon**

`vboxguest` kernel module compile fails with `#error "Not on AMD64 or x86"` on ARM64 Mac. This is expected and **ignorable** — Guest Additions only affect shared folders, clipboard, and display. cf-test-client has `synced_folder disabled: true`; no shared folders are needed.

**4 — vsmc Ansible networkd race condition (eth1 bounce → SSH drop)**

**Symptom**: `smc_network` handler `Reload systemd-networkd service` fires, then Ansible reports `UNREACHABLE` (SSH timeout on Teleport port 65535). Play ends: `ok=91 changed=64 unreachable=1`.

**Root cause chain**:
1. networkd reload → networkd-dispatcher fires `configured.d/00-interface-activation.sh`
2. Script unconditionally bounces eth1: `ip link set eth1 down; ip link set eth1 up`
3. eth1 bounce → dhclient@eth1 gets `ENETDOWN` → tries to renew stale lease (172.20.10.2 = old iPhone hotspot IP, wrong network)
4. `timeout 10` in `/etc/dhcp/dhclient.eth1.conf` too short for WiFi bridge DHCP → no DHCPACK → lease expires
5. Default route via eth1 disappears
6. Teleport tunnel cannot reach `teleport.apn.au` (no internet route) → SSH banner exchange times out
7. Ansible marks UNREACHABLE before `wait_for_connection` can recover

**Fix**: `roles/smc_network/templates/00-interface-activation.sh.j2` — Vagrant guard added:
- When `smc_bases_vagrant_interface` is defined: skip eth1 bounce entirely; only bring interface up if it is currently down (no down/up cycle).
- `smc_bases_vagrant_interface: eth0` set in `host_vars/family-friendly-vsmc01.yml`.

**Physical SMC not affected**: Wired DHCP is fast; interface reaches `routable` within the timeout; loop stops naturally.

**Ansible provisioning on vsmc01**: Ansible is not run by Vagrant directly. After `vagrant up family-friendly-vsmc01`, run from the Mac:
```bash
cd /Volumes/Data/_ansible/ansible-wifi
ansible-playbook smc_bases.yml -l family-friendly-vsmc01 --diff
```
Key vars: `smc_bases_vagrant_interface` set in host_vars → activates all Vagrant guards (eth1 bounce skip, dirmngr IPv6 disable).

**5 — unbound on first Ansible run**

`interface-automatic: no` is required in `unbound.conf.j2` (fixed 2026-06-26). Without it, unbound tries to bind `::1` as a companion to `0.0.0.0` even with `do-ip6: no`, which fails fatally when IPv6 is disabled by sysctl. Second run succeeds (socket state changes). The template fix makes the first run reliable.

**6 — PHP PPA on Vagrant**

dirmngr defaults to AAAA lookup for apt.releases.phpunit.de. On IPv6-disabled Vagrant VMs, this causes `No route to host`. Fix: `disable-ipv6` in `/etc/gnupg/dirmngr.conf`, applied by `ubuntu-php-install-configure.yml` when `smc_bases_vagrant_interface` is defined.

### 12.4 Bring-up procedure

```bash
# 1. Start SMC VM
cd /Volumes/Data/_vagrant/vagrant_stuff/family-friendly-vsmc01
vagrant up family-friendly-vsmc01

# 2. Provision SMC with Ansible (from ansible-wifi repo root)
ansible-playbook smc_bases.yml -l family-friendly-vsmc01 --diff

# 3. Start client VM
vagrant up cf-test-client

# 4. Verify client routing (only one default route via SMC)
vagrant ssh cf-test-client -- ip route show default

# 5. Test portal from client
vagrant ssh cf-test-client -- curl -s wifi.a8me.au | grep -E "btn-apn|Terms|Start"

# 6. Test captive redirect from client
vagrant ssh cf-test-client -- curl -sv http://1.1.1.1/ 2>&1 | grep -E "Location|302"
```

### 12.5 Useful commands

```bash
# SSH to vsmc01 directly
vagrant ssh family-friendly-vsmc01

# SSH to cf-test-client
vagrant ssh cf-test-client

# Check cf-test-client has correct default route
vagrant ssh cf-test-client -- ip route

# Portal smoke test from SMC itself
vagrant ssh family-friendly-vsmc01 -- curl -s wifi.a8me.au | grep -E "Terms|Undefined|btn-apn"

# Check iptables VLAN 501 rules on SMC
vagrant ssh family-friendly-vsmc01 -- iptables -t mangle -S ECLIPSE_MARK
vagrant ssh family-friendly-vsmc01 -- iptables -S FORWARD | grep 501

# Check DHCP leases (what IP did the client get?)
vagrant ssh family-friendly-vsmc01 -- cat /var/lib/dhcp/dhcpd.leases | grep -A5 "binding state active"
```

---
````

## File: references/12_content-filtering.md
````markdown
# SMC Family-Friendly Content Filtering

## 13. Family-Friendly Content Filtering

### 13.1 VLAN 501 access model

Family-friendly sites use `VLAN_501_ACCESS_METHOD: Prepaid Pins` (from Eclipse config.txt). Unauthenticated clients on VLAN 501 are redirected to the captive portal by iptables rules. Authentication happens via PIN entry in the Kohana portal.

Access flow:
```
Client (VLAN 501)
  → HTTP request → iptables REDIRECT/DNAT → Apache captive portal
  → PIN entry → Kohana app → Eclipse validates PIN
  → Eclipse sends MARK command → SMC sets connmark
  → iptables ECLIPSE_MARK allows client traffic through FORWARD chain
  → Squid proxies HTTP; Unbound resolves DNS
```

### 13.2 iptables chains for VLAN 501

Key chains (inspect on SMC):
```bash
iptables -t mangle -S ECLIPSE_MARK          # authenticated user marks
iptables -t mangle -S ECLIPSE_METERED_TIME  # time-based metering marks
iptables -S FORWARD | grep -E "501|MARK"    # FORWARD chain filter rules
iptables -t nat -S PREROUTING | grep 501    # captive portal redirect rules
```

If `ECLIPSE_MARK` is empty: no users have authenticated, or the Eclipse command to populate marks has not been received.

**Differential diagnosis: VLAN 500 working while VLAN 501 doesn't is by design, not a fault.**
`bridge_500` (management VLAN) carries an **unconditional ACCEPT** in the FORWARD chain and bypasses
Eclipse enforcement entirely — it is not subject to `connmark`/`ECLIPSE_MARK` gating at all.
`bridge_501` (public/family-friendly WiFi) is the only VLAN that requires `connmark != 0` to pass
FORWARD. If a site reports "management access works fine but public WiFi doesn't authenticate,"
that is consistent with everything working correctly — it is not evidence the FORWARD chain itself
is broken. Source: `.archcore/specs/spec-002-iptables-forward-chain-behavior-by-bridge.md`.

### 13.3 Content filtering stack

| Layer | Component | Config location |
|---|---|---|
| DNS | Unbound | `/etc/unbound/unbound.conf` (managed by `smc_dns` role) |
| HTTP proxy | Squid | `/etc/squid/squid.conf` (managed by `smc_squid` role) |
| Content filter | SquidGuard | `/etc/squid/squidGuard.conf` (managed by `smc_squid` role) |
| Captive portal | Apache + Kohana | `/var/www/html/wifi` (cloned from Bitbucket wifi.git) |
| Access control | iptables | managed by `smc_iptables` role + Eclipse mark updates |

### 13.4 Eclipse identity model and MAC randomization

**Identity chain** (no human in loop, no PII):
```
T&C acceptance
  → Eclipse auto-generates PIN (invisible to user)
  → PIN bound to client MAC address
  → iptables connmark set per PIN/MAC via ECLIPSE_MARK chain
  → Subsequent packets matched by connmark → allowed through FORWARD
```

**Control granularity**: Binary only — full access or none. No **per-user** rate shaping (`tc`/`htb`) deployed. Squid present on SMP flavor but no delay pools configured. (Do not read this as "no
`tc` shaping anywhere on the fleet" — a separate, manually-installed **per-WAN-link** ingress-shaping mechanism, `tc`/`tbf`/`ifb` on the Starlink VLANs, is live fleet-wide; see
`03_communication-flows.md`, "Manual TBF/`ifb` Ingress Shaping". Different layer, different purpose — WAN-link cap vs. per-client fairness.)

**MAC randomization impacts**:

| Scenario | Effect |
|---|---|
| iOS or Android — stable per-SSID private MAC | PIN binding survives reconnects ✓ |
| User forgets + rejoins same SSID | MAC rotates → new auto-PIN → any prior PIN suspension bypassed ✗ |
| Android Enhanced Randomization | MAC rotates periodically on same SSID without user action → new PIN needed ✗ |

**No-PII constraint**: Cannot tie identity to phone, email, name, or community ID above PIN level in Eclipse. PIN suspension requires automated Eclipse threshold logic — not currently built.

### 13.5 CAKE fair queuing (per-user bandwidth fairness)

Deploy CAKE on `bridge_501` (LAN-facing bridge), **not** per WAN interface.

```bash
# Set total WAN bandwidth (example: 5 × 80Mbps = 400Mbps)
tc qdisc replace dev bridge_501 root cake bandwidth 400mbit
```

**Why bridge_501 not per-WAN**: Per-WAN CAKE creates uneven fair shares — nftables may hash 5 users to WAN1 and 10 to WAN2. `bridge_501` sees all users combined regardless of WAN assignment; fair share is consistent.

**How host fairness works**: Equal slice per device IP regardless of parallel flows. Idle users' slices go to active users. MAC-proof — shapes packets in flight, not identity claims.

**Limits**: CAKE solves speed hogging but does NOT limit total data usage. A user at fair share 24/7 still consumes heavily. Full per-user total usage limiting requires persistent identity or Eclipse automation (neither currently deployed on family-friendly flavor).

### 13.6 Verify content filtering works

```bash
# From cf-test-client — after PIN authentication
# HTTP request should go through Squid (check X-Cache or Squid headers)
curl -sv http://www.google.com/ 2>&1 | grep -E "Via|X-Squid|Cache"

# DNS resolution via SMC Unbound
dig @10.0.0.1 www.google.com +short

# Check Squid access log
vagrant ssh family-friendly-vsmc01 -- tail -20 /var/log/squid/access.log

# Unauthenticated client should be redirected (HTTP 302 to portal)
# (from client before PIN entry)
curl -sv http://1.1.1.1/ 2>&1 | grep -E "Location|302|wifi"
```
````

## File: references/13_known-issues.md
````markdown
# skill-smc Known Issues and Gaps

## Knowledge Gaps (by design — require execution layer)

| Gap | Why | Mitigation |
|---|---|---|
| Actual flattened topology output for a specific host | Requires executing `vars_plugins/topology_vars.py` against live inventory | Phase 3: ansible-wifi MCP |
| Live service status, log content, running metrics | Requires SSH access to the box | Direct `tsh ssh root@<hostname>` (no MCP — operator arranges `tsh login` manually per flavor's Teleport cluster) + `mcp-grafana` for metrics |
| Cross-flavor inventory impact at scale | Requires running `ansible-inventory --list` × 7 flavors | Phase 3: ansible-wifi MCP |

## Coverage Gaps (partial knowledge)

| Area | Status | Notes |
|---|---|---|
| x86 / apn flavor live validation | Not validated | RUNBOOK flavor differences are from code inspection only; malik-rct01 is the only live-validated box |
| cnmaestro-provisioning internals | Partial, deployment side now well-documented (2026-08-03) | Deployment mechanism (`smc_cnmaestro_provisioning` role, `smc_ltp.yml` playbook, per-model Cambium hardware profiles, IP/SSID auto-allocation) now covered in `08_ansible-authoring.md` "smc_ltp Sub-Group". Still undocumented: `cnmaestro-provisioning.py`'s actual runtime behavior against the CNMaestro cloud API (error handling, retry logic, what happens on a provisioning conflict) — not live-validated |
| NBN Accelerate API behavior | Minimal | API call pattern noted; response handling and error states undocumented |
| Redis usage details | Minimal | Used by cnmaestro-provisioning; key schema undocumented |
| Kohana / Tstik web apps | Minimal | Running on RCT; role config paths known; app internals not documented |
| RISE monitoring suite (riseclient, risengine) | Partial | Unit names known; behavioral details from code inspection only |
| Host-level (own) DNS resolution architecture, as distinct from DHCP/LAN client DNS | Newly documented 2026-07-03, single-incident-grounded | `systemd-resolved` stub is disabled by design (`DNSStubListener=no`, unconditional) — host DNS bypasses unbound/stubby/bind entirely and goes straight to `external_dns_servers`. Confirmed via the garimba-smc01 RCA; not independently re-validated at any other site yet. See `02_service-map.md` + `06_failure-modes.md` |
| Flavor → Teleport cluster domain mapping | Resolved 2026-07-31 (operator-confirmed) | `rcp`/`rct`/`wh`/`apn` → `teleport.apn.au`; `nbn_accelerate`/`nbn_wh`/`cw` → `teleport.communitywifi.net.au`. Covers all 7 inventory flavors. Operators still arrange `tsh login` manually per site — this table is for orientation, not for hardcoding into scripts/tooling. See `01_overview.md` "Remote Access" |
| **NBN Accelerate cluster coverage gap** | Largely closed — full fleet sweep done 2026-08-03 | `01_overview.md` "APN Cluster vs NBN Accelerate Cluster — Structural Comparison" and `08_ansible-authoring.md` "Flavor/Cluster Conditional Branching" were structural/code-inspection only when written. **Full-fleet live validation 2026-08-03** (`tsh ssh` to all 26 reachable `nbn_accelerate` hosts + both `nbn_wh` hosts, 28 total): Teleport domain, HTTPS-only portal, mobile-app backend, ClamAV+Lynis presence, Asterisk absence, non-`smc_ltp` DNS stack, and full hardware inventory all confirmed live — see "Known Operational Bugs (NBN Accelerate cluster — full fleet sweep, 2026-08-03)" above and `07_hardware-overlay.md` "NBN Accelerate / NBN WH Hardware Inventory". **Still not live-validated**: `cw` flavor itself (central-infra only, no site hosts to check), `aurukun-smc03` (unreachable at capture time); every troubleshooting entry in `05_troubleshooting.md`/`06_failure-modes.md`/this file's incident rows *besides* the NBN Accelerate bugs section above is still an APN-cluster (`rcp`) site. |
| **"Low touch" onboarding method ↔ `smc_ltp` link — resolved 2026-08-03** | Confirmed, operator-directed; mechanism confirmed manual | All 7 low-touch sites (`guda-guda` pilot 2025-04-15, `umoona`, `warburton`, `beagle-bay`, `pandanus-park`, `old-looma`, `new-looma`) are now `smc_ltp` group members — operator confirmed the link is real (low-touch onboarding implies `smc_ltp`) and directed adding the 3 missing sites (`umoona`/`warburton`/`beagle-bay`) to `inventories/rcp/prod`'s `smc_ltp` group, closing what had been a plain inventory gap, not a coincidental correlation. **Mechanism confirmed 2026-08-03: it's a manual step someone has to remember** — no low-touch onboarding tooling automatically assigns `smc_ltp` group membership, and nothing enforces or checks that it happened. This is the actual root cause of the 3-site gap — treat this as a standing risk for any future low-touch site, not a one-off fixed with this correction; verify `smc_ltp:children` membership explicitly whenever a new low-touch site goes live rather than assuming it's automatic. Separately, Ansible-code-wise the *string* "low touch" still means nothing: the one `low_touch` hit in the whole repo (`smc_bases_low_touch_provisioning: true` on `pierre-rcp01`, not a cohort member) is never read by any role/playbook — an orphaned var, not evidence of an implemented low-touch code path distinct from `smc_ltp` group membership itself. See `08_ansible-authoring.md` "'Low Touch' Onboarding Method and Site Deployment History". |
tunnels are ready
## Skill Staleness Risks

- Service names and config paths may drift as ansible-wifi roles are updated.
- Flavor differences (RCT vs x86) are grounded in live RCT validation only; x86 assumptions are from role code inspection.
- **2026-07-03 correction**: the DNS resolver row in `02_service-map.md` previously generalized "unbound = RCT flavor, bind = non-RCT flavors" from the single initial RCT validation — this was wrong.
The real gate is `smc_ltp` inventory-group membership (orthogonal to flavor), confirmed by repo-wide grep across all inventories during the garimba-smc01 RCA. Treat any other flavor-generalized claim
in this pack derived from a single-host validation as unverified for other flavors until independently checked.
- **2026-08-03 correction**: that same garimba-smc01 RCA grep undercounted `smc_ltp` group membership as "only `rcp`/guda-guda" — it was `.yml`-scoped and missed `inventories/rcp/prod`, the INI-format
static inventory where the group is actually defined. Direct read of `prod` initially showed 4 member sites: `guda-guda`, `pandanus-park`, `old-looma`, `new-looma`. Same failure class as the pattern
below — grep-only inventory investigation missing a non-`.yml` file. See `02_service-map.md` and `08_ansible-authoring.md` "smc_ltp Sub-Group" for the corrected, fuller picture (including the previously
undocumented CNMaestro-provisioning purpose of the group, mislabeled elsewhere in this pack as "mDNS").
- **2026-08-03, same day, superseding the count above**: operator confirmed `smc_ltp` should have **7** members, not 4 — the group is meant to track "low touch" onboarding sites, and 3
  (`umoona`, `warburton`, `beagle-bay`) were low-touch-deployed but missing from `inventories/rcp/prod`'s `smc_ltp` group, a real inventory gap rather than a grep miss this time. Operator directed
  the fix directly: `warburton_smc_ltp`/`beagle-bay_smc_ltp`/`umoona_smc_ltp` child groups added to `inventories/rcp/prod` (`smc_ltp:children` now lists all 7), verified via `ansible-inventory --list`
  and `ansible-playbook --syntax-check smc_ltp.yml`, both clean. This resolves the "low touch ↔ smc_ltp link unresolved" row above — see its updated text. **Uncommitted** as of this edit — a real,
  file-level production Ansible inventory change (not yet run against any live SMC).
- **2026-07-28 correction**: `10_captive-portal.md` previously stated flatly that "PHP-FPM processes `.php` files" and that a permanent Ansible `SetHandler` fix "landed 2026-06-26". **Both were wrong** — generalizations from `family-friendly-smc01` hotfix work in June 2026 that never reached the production fleet. Verified on three sampled `rcp` hosts: zero `php*-fpm` packages, `libapache2-mod-php` installed, `apache2ctl -M` shows `php_module`, no `/etc/php/8.1/fpm/` directory; and repo-wide grep finds no `SetHandler` in any template, with the enabled-modules list being only `rewrite` and `ssl`. **This is the third instance of the same failure pattern in this pack** (after the 2026-07-03 DNS row and the 2026-07-09 MySQL row): a single host's observed behaviour written up as fleet-wide architecture. When adding architecture claims, state the validation scope explicitly — which hosts, which flavors, verified how.
- Prometheus alert names and thresholds are taken from `roles/smc_prometheus/` at commit `0d0c91a`; these may change.
- **Unreconciled duplicate-fix risk (flagged, not resolved):** `.remember` daily logs (2026-07-24/07-26) describe an "apt-lock-race" backport (`/proc/locks` probe, an `is sequence` trap, a
`tmpfiles.d` template, the 44GB journal reclaim, and reordering lock-clearing in `custom_apt_update_cache.yml`/`custom_apt_install.yml`) fixing `rc:100 apt-daily-upgrade` collisions. This pack
already documents a *different*-sounding apt-daily-upgrade fix (masking `apt-daily.timer`/`apt-daily-upgrade.timer`, commit `0c51cb1`, see `08_ansible-authoring.md`). It is not established whether
these are the same fix described two ways or a genuine additional hardening layer — confirm against the actual commits before treating both as independently true.
- **2026-07-09 correction**: the "Kohana PHP tries MySQL (not installed on rcp)" bug row below was diagnosed from smc-file-writing-analysis's 2026-06-02 burringurrah audit, which found no
`/var/lib/mysql` and concluded the 1min/5min/daily Kohana cron jobs were failing local DB connections. ansible-wifi ADR-002 (`.archcore/adr/adr-002-eclipse-kohana-captive-portal-architecture.md`)
documents the exact same three cron cadences as Kohana's sync jobs with a **remote Eclipse server** (`wifi.activ8me.net.au:443`), not local MySQL — Kohana is the local half of a two-tier
captive-portal auth system, and the `ECLIPSE_MARK` iptables chain (gates `bridge_501` public WiFi) is only populated after a successful Eclipse sync. The "MySQL not installed" fact may still be true
but is not established as the actual failure path for these specific cron errors. Treat the root cause as unresolved until a live node's actual PHP error text and Eclipse connectivity are checked —
see `smc-file-writing-analysis` memory-keeper key `smc.audit.kohana.eclipse.correction.20260709`.
- **"Community wifi" naming collision — this is why this pack calls the `cw`/`nbn_accelerate`/`nbn_wh` customer "NBN Accelerate," not "Community WiFi" (found 2026-08-03, operator-directed rename same day).** `local-knowledge-ansible/ansible-wifi/issues/apn/routing-issue/{README,problem}.md` use the phrase "community-wifi"/"community wifi" generically, to mean **`rcp` sites within the APN network**
(i.e. an APN-cluster community's WiFi service) — a completely different sense from the `cw`/`nbn_accelerate`/`nbn_wh` customer this pack documents in `01_overview.md`. Anyone grepping the ansible-wifi
knowledge tree for "community wifi" to find NBN-Accelerate-cluster content will hit that apn/routing-issue file instead and may misattribute apn-cluster routing-issue findings to the wrong cluster.
This pack deliberately avoids the ambiguous term as the cluster's display name — use "NBN Accelerate cluster" (or the literal `teleport.communitywifi.net.au` domain / `cw`/`nbn_accelerate`/`nbn_wh`
flavor names) instead. Check which sense is meant before treating any "community wifi" hit elsewhere in the ansible-wifi tree as evidence about this cluster.
- **OPA policy layer has no dedicated `cw` entry, and `environments.json` is incomplete/possibly stale (found 2026-08-03).** `opa/data/flavors.json` defines per-flavor policy for `rcp`, `nbn_wh`,
`nbn_accelerate` only — no `cw`, `apn`, `rct`, or `wh` entries exist. `opa/data/environments.json`'s prod `inventory_groups` list is similarly partial (`rcp`, `nbn_wh`, `nbn_accelerate` only). Not
established whether this is intentional scoping (OPA gating only applies to flavors that run destructive-command-guarded playbooks) or a genuine coverage gap — confirm against OPA policy intent
before assuming `cw`/`apn`/`rct`/`wh` are ungated by design.

## Fleet-Wide Architecture Risks (identified, not yet remediated)

| Risk | Detail | Evidence basis |
|---|---|---|
| Stubby DoT upstream has no failover | Exactly one `upstream_recursive_servers` entry (`127.0.0.1@60853`, reached via an autossh local port forward to Teleport) is configured fleet-wide, identically, for every non-`smc_ltp` site — `round_robin_upstreams: 1` is set but meaningless with a single upstream | garimba-smc01 DNS RCA, 2026-07-03, `roles/smc_dns/files/stubby.yml` |
| No monitoring for the autossh local forward or Stubby upstream reachability | Repo-wide search found no Prometheus alert rule specific to `autossh-teleport.service` state or DNS-upstream health; if the Teleport connection drops, DHCP/LAN client DNS on that SMC has no fallback once Unbound's cache expires (positive TTL up to 24h, negative TTL up to 5min) — failure would be silent until users notice | garimba-smc01 DNS RCA, 2026-07-03 |
| **No HTTP-level captive-portal monitoring anywhere in the fleet** | Nothing probes whether the portal actually serves. The only portal-adjacent signals are the Kohana `status:update:usage` / `status:update:status` crons, which run as **root** and therefore keep succeeding even when the portal is dead for `www-data` — Eclipse keeps receiving data throughout an outage. This let 10 of 16 `rcp` sites sit fully down for 7 days undetected. A naive probe would not help either: the failure returns **HTTP 200** with a 40-byte error body, so any check must assert on response body content or size, not status code | rcp portal outage RCA, 2026-07-28, `issues/rcp-fleet/rcp-captive-portal-cache-perms-outage-20260728_1240.md` |
| Host-level DNS resolution bypasses any stub/cache | `DNSStubListener=no` + `Cache=no` unconditional on all non-`smc_ltp` hosts — host glibc is directly exposed to any WAN-path DNS anomaly with no resolver-level mitigation in place today | See `06_failure-modes.md` — mitigation candidate exists but is not yet fleet-validated |
| `smc_qos` role exists but is gated `when: inventory_dir.split('/')|last == 'rct'` — silently no-ops on every `rcp`/`nbn_accelerate` site | `03_communication-flows.md` previously stated Ansible-managed QoS was "planned, not started" — that's stale. The role exists and `--tags qos` runs during rcp deploys, it just never fires due to the gate. Manual TBF/ifb shaping remains the only active mechanism on rcp, and it has NOT been extended to newly-fixed VLANs at every site (2 missing at Pandanus Park, 10 at Umoona, 8 at Old Looma as of 2026-07-30) | routing-issue investigation, `ingress-shaping-not-managed-or-extended-20260730_1245.md` |
| Fixed-topology `starlink01`/`starlink02` interfaces defined even at sites with no Starlink circuit ordered | Confirmed at Horn Island: the boilerplate two-interface starlink block is applied regardless of whether a backup circuit actually exists, inflating `interfacecheckv2.sh`'s per-cycle ping count for no operational benefit. Topology generation should condition this block on actual provisioning, not apply it unconditionally per flavor | routing-issue investigation, `starlink-backup-no-lease-l2-investigation-20260730_1400.md` |

## Known Operational Bugs (rcp fleet — confirmed 2026-06-30)

| Bug | Impact | Fix location |
|---|---|---|
| `interfacecheckv2.sh` outputs empty float → node_exporter parse error | 2,880 syslog entries/day fleet-wide | **Fix drafted + committed 2026-07-15** (`ae838c2`, writes `NaN` on empty sed match instead of feeding it into `bc`) — deploy deferred to a later session, not yet on any node. `roles/smc_network/templates/interfacecheckv2.sh.j2` |
| Kohana PHP cron error (root cause revised 2026-07-09 — see below) | 1,440 syslog entries/day fleet-wide; possible silent bridge_501 public WiFi outage on Eclipse-enabled sites, not just log spam | **Investigated live 2026-07-15, no active failure found.** The 2026-07-09 theory does not hold up: `wifi.activ8me.net.au:443` TLS handshake clean, `bridge_501` up, `ECLIPSE_MARK` correctly populated, manual `kohana status:update:status` exits 0. `rpm`/`sbltm-cli` "not found" errors seen during the manual run are from an unrelated Eclipse-server-side dev script, not this project's concern. No fix applied — nothing currently reproducing. `roles/smc_application/` |
| `sbdm.prom` = 0 bytes on tjuntjuntjara + burringurrah — likely fleet-wide | No SSD health metrics shipped | `roles/smc_node_exporter/` |
| `smc_graylog` RISE defaults (`graylog_sidecar_extra_tags`, `graylog_sidecar_extra_log_files`) lack rcp override | **FIXED 2026-06-30** — was actively crash-looping sidecar on tjuntjuntjara. Fix: `inventories/rcp/group_vars/smc_bases.yml` — see ansible-authoring ref. **Deploy-lag gotcha (found 2026-07-14 on horn-island):** the group_vars fix landing doesn't retroactively fix already-deployed nodes — horn-island's on-disk sidecar config still had the old `rise` tag/paths and had been `failed` since 2026-07-03 until a normal `smc_bases.yml`+`smc_graylog.yml` redeploy regenerated it from the (already-correct) current vars. If a node's sidecar is `failed` referencing `/var/log/rise`, check whether it's simply never been redeployed since 2026-06-30 before assuming a new bug. | `inventories/rcp/group_vars/smc_bases.yml` ✓ |
| `apt_info.py` called `cache.update()` unconditionally on every 5-min cron tick — a full `apt update` (network fetch + gpgv Release-signature verification against every repo), 288×/day of apt.data.*/gpgv writes | **FIXED 2026-07-15 — deployed fleet-wide, 12/12 nodes.** Was independent of and untouched by the `apt-daily.timer`/`apt-daily-upgrade.timer` fix (commit `0c51cb1`). Root cause traced one level deeper than first assumed: `cache.update()` is what fired `20apt-esm-hook.conf`'s `APT::Update::Pre-Invoke` hook (`systemctl start --no-block apt-news.service esm-cache.service`) — the downstream `apt-news.service`/`esm-cache.service` masking (see next row) is a belt-and-suspenders cleanup, not the primary fix; masking those two alone would not have stopped the update-and-verify cycle itself. Fix: removed `cache.update()` — the script already tolerated it failing and falling back to the existing index, so this is functionally identical to that already-accepted path. Deployed via a scoped ansible ad-hoc `copy` targeting only `apt_info.py` (not the full `--tags node_exporter` role, which would have bundled in the separate, not-yet-approved smartmon.py Part 1 rollout to 10 nodes lacking it — caught via dry-run showing `changed=2-4` instead of the expected 1 on several hosts). Verified fleet-wide: `cache.update()`/`contextlib` import confirmed absent, script runs clean, `apt_info.prom` still populates. Explained why the post-timer-fix re-baseline (2026-07-15 13:23) showed no measurable write-rate improvement on 11/12 nodes. See `smc-file-writing-analysis/ROADMAP.md` Completed milestones and `docs/log-audit-results.md` 2026-07-15 entries. | `roles/smc_node_exporter/files/apt_info.py` — ansible-wifi commit `4889af8`, deployed 12/12, not pushed to origin |
| `apt-news.service` + `esm-cache.service` fire as a side effect of the `apt_info.py` issue above (row above), not independently | **FIXED 2026-07-15 — masked fleet-wide, 12/12 nodes.** Belt-and-suspenders cleanup, deployed same evening as the row above. **Version-gated gotcha found live**: only shipped by `ubuntu-advantage-tools` ≥28.x (27.9~22.04.1 on tjuntjuntjara doesn't ship them; 28.1~22.04 on horn-island does) — `systemd: masked: yes` fails hard (`Could not find the requested service`) on any node still on the older version since it queries current state first. Fixed by masking via a direct `/dev/null` symlink instead (`file: state: link`, what `systemctl mask` does under the hood) — works regardless of unit existence. Full detail: `08_ansible-authoring.md` "apt-news.service + esm-cache.service Mask". | `roles/smc_system/tasks/main.yml` — ansible-wifi commit `97854ee`, deployed 12/12, not pushed |
| `my_node_network_device_info` (per-interface device/role/topology registry metric) returns **zero series** on old-looma, new-looma, and horn-island (rcp) — confirmed 2026-07-29 | `up{instance="<host>:9100"} == 1` and base kernel network metrics (`node_network_receive_bytes_total` etc.) are present and correct on all three — only this specific metric is absent, so `node_exporter` scraping health alone does not prove this metric is populated. Breaks any Grafana panel/query keyed on `role`/`device` labels for these three sites (e.g. the `${role}`/`${ethernet}` panels on the *SMC Network* dashboard silently show nothing). **Not explained** — old-looma/new-looma are also the most severely topology-stale sites in the 2026-07-29 routing investigation, which invites a "same root cause as the dhclient-hook staleness" guess, but horn-island is healthy/unaffected by that issue, so a single shared cause doesn't hold across all three. If picked up: check whether this metric is populated by a textfile-collector script rendered per-site from `topology_vars` (like the dhclient hook) — if so it would be a fourth topology-derived render that can silently drift, alongside the hook, netplan, and the service-inventory table | `roles/smc_node_exporter/` — unconfirmed which collector/exporter path emits this metric; not yet traced to source |

## Known Operational Bugs (NBN Accelerate cluster — full fleet sweep, 2026-08-03)

**Full-fleet live `tsh ssh` sweep, not a spot-check**: all 26 reachable `nbn_accelerate` sites plus
both `nbn_wh` sites (`bungardi-smc01`, `darlngunaya-smc01`) — 28 hosts total, effectively the entire
NBN Accelerate cluster minus `aurukun-smc03` (in the static inventory but not visible in `tsh ls` at
capture time) and the `cw`/central-infra nodes. Superseded the earlier same-day 2-host spot-check
(`warakurna-smc01`/`indulkana-smc01`). Collected via the new `scripts/collect-fleet-health.sh` +
`scripts/fleet-health.justfile`. **`nbn_wh` is the `wh`-flavor equivalent on this cluster** (same RPi
hardware class as `rct`/`wh` on the APN cluster, operator-confirmed) — every `wh`-flavor expectation
(RPi ARM64, Swissbit SD storage, overlayroot) is the baseline `nbn_wh` should be compared against, not
`nbn_accelerate`'s x86 baseline.

**Every code-inspection-only claim from the earlier gap-fill confirmed, 28/28 hosts**: Teleport domain
(`teleport.communitywifi.net.au:443`), HTTPS-only portal with on-box TLS termination, mobile-app
backend + `apn-mqtt-client` + url_capture (v1 path) present on all 26 `nbn_accelerate` hosts (absent on
both `nbn_wh` hosts — flavor-gated as documented), ClamAV+Lynis installed on all 26 `nbn_accelerate`
hosts and absent on both `nbn_wh` hosts, Asterisk absent everywhere, non-`smc_ltp` DNS stack everywhere.

### Hardware inventory (new — no prior live chassis data existed for this cluster)

| Chassis | Count | CPU | RAM | Storage | Flavor |
|---|---|---|---|---|---|
| AAEON BOXER-6641 | 11 | Intel Core i5-8500T @ 2.10GHz | 15Gi | Transcend TS128GSSD420K SSD | `nbn_accelerate` |
| AAEON BOXER-6404 | 15 | Intel Celeron J1900 @ 1.99GHz | 7.7Gi | Innodisk CFast 3ME3 | `nbn_accelerate` |
| Raspberry Pi (Cortex-A72, `-raspi` kernel) | 2 | ARM64, 4-core Cortex-A72 | 7.6Gi | Swissbit SB AFNI0 microSD | `nbn_wh` |

No dmidecode data on the 2 `nbn_wh` hosts (expected — RPi boards have no DMI/SMBIOS tables, same as
`rct`/`wh`). Both `nbn_wh` hosts show `Swap: 0B` and no `zram0` device in `lsblk` — **contradicts**
`07_hardware-overlay.md`'s "RPi flavor → zram swap" row as a universal claim; either `nbn_wh` doesn't
get zram unlike `rct`/`wh`, or zram provisioning is flavor-specific in a way not yet checked against
live `rct`/`wh` hosts either. Not resolved — flagged in `07_hardware-overlay.md`.

### Bugs and anomalies found

| Bug | Impact | Fix location |
|---|---|---|
| `clamav-freshclam.service` chronically failing — **ROOT CAUSE CONFIRMED 2026-08-03: ClamAV 0.103.x is past end-of-life for database updates** | Fleet runs `clamav 0.103.11+dfsg-0ubuntu0.22.04.1` uniformly (one host, `warakurna-smc01`, on `0.103.12` — same EOL branch). **ClamAV's 0.103 branch reached end-of-life for database updates on 2025-09-14** ([ClamAV blog](https://blog.clamav.net/2025/03/advance-notice-end-of-life-for-clamav.html)); after that date the CDN actively rejects `freshclam` requests from any 0.103.x client with HTTP 403 ("Forbidden; Blocked by CDN") — exactly the signature captured on all 26 `nbn_accelerate` hosts, exit code 17, `This is fatal. Retrying later won't help. Exiting now.`. **This explains the 10-month staggered failure-date spread** (2025-10-02 → 2026-07-30): a host only flips to `failed` the first time its `freshclam` timer runs *after* the 2025-09-14 cutoff — hosts with different timer schedules or later provisioning dates would trip the block at different times, not simultaneously. The three hosts sharing 2025-10-02 exactly (`arreyonga`, `kowanyama`, `mindi-rardi`) are consistent with a shared timer schedule that first fired ~18 days post-cutoff. ClamAV 0.103.4+ added a 24h cool-down for CDN-blocked clients specifically, but freshclam still treats the block as fatal — **no version of "wait and retry" fixes this; only upgrading ClamAV does.** `clamav-daemon` stays `active` on every host (still scanning) but with a virus database frozen at whatever it had before the block, degraded fleet-wide. Not cluster-specific, not a firewall/proxy issue, not `nbn_accelerate`-specific — this would affect any fleet anywhere still running 0.103.x past 2025-09-14. | **Confirmed, not yet remediated.** Fix: upgrade `clamav`/`clamav-freshclam` fleet-wide to 1.4 LTS (current) or 1.0 LTS (older supported alternative) — no automated ClamAV-version-update pipeline exists for this cluster (consistent with the already-documented absence of an automated kernel-update pipeline, `01_overview.md`), so nothing will self-correct this without a deliberate package-upgrade rollout via `roles/smc_bases.yml`. Confirmed on all 26 reachable `nbn_accelerate` hosts (see `scripts/fleet-health.justfile`'s `freshclam-check` recipe). No comparison fleet exists on `apn`-cluster (ClamAV isn't deployed there per the flavor gate). |
| `nbn_wh` overlayroot **not yet active** — planned rollout, not a bug (operator-confirmed 2026-08-03) | `smc_rise_deploy.yml` (`ansible-wifi` root playbook) explicitly targets `inventory_dir.split('/')|last in ['rct', 'wh', 'nbn_wh']` — `nbn_wh` is coded as a RISE/overlay-rollout target alongside `rct`/`wh`. Live on both `nbn_wh` hosts: `mount | grep overlay` returns nothing — no overlayroot active yet. **Operator confirmed the plan is to enable overlay on these two `nbn_wh` sites in the near future** — this is pre-rollout current state, not an unexplained gap or a stalled/reverted deployment. `darlngunaya-smc01`'s 318-day uptime is consistent with it simply not having been reached by this specific rollout yet. | Tracked, not a bug — re-check `mount \| grep overlay` on `bungardi-smc01`/`darlngunaya-smc01` after the planned rollout lands to confirm it took; until then this row documents expected pre-rollout state. `roles/smc_rise_overlay/`, `smc_rise_deploy.yml` line ~316. See `08_ansible-authoring.md` and `07_hardware-overlay.md` "NBN Accelerate / NBN WH Hardware Inventory" for the full picture. |
| `koonibba-smc01` at **95% root disk usage**, fleet's highest by a wide margin (next is `warakurna-smc01` at 65%) | Approaching full — worth an operator disk-usage check before it becomes an outage. Same host also runs the fleet's oldest kernel (`5.15.0-79-generic` vs the fleet norm of `-117`/`-119`; `warakurna-smc01` is the opposite outlier at `-133`, newer than everyone else) — two independent signs this host hasn't been touched by a routine maintenance pass in a long time, consistent with the already-documented absence of an automated kernel-update pipeline for the cw-cluster (`01_overview.md` "APN Cluster vs NBN Accelerate Cluster"). | Not investigated further — `koonibba-smc01` disk contents not examined (would need a live `du`/`df -h` breakdown by directory, not run this sweep). |
| `fwupd-refresh.service` failed on 3/28 hosts (`bungardi-smc01`, `darlngunaya-smc01`, `warakurna-smc01`) — minor, low-priority | Firmware-metadata refresh failing, not security-critical like the ClamAV finding above, but same general class of "outbound CDN/metadata fetch quietly broken" — possibly related to the same egress-path hypothesis being considered for the freshclam finding, possibly unrelated. Not investigated. | Not investigated — `fwupd-refresh.service`, 3 hosts only, not fleet-wide. |
| `isc-dhcp-server6.service` failed on **28/28 hosts** — confirmed benign, not a bug | Every single host shows this in `systemctl --failed`. This fleet disables IPv6 at the kernel level by policy (`08_ansible-authoring.md` "IPv6 Disable Policy") — an IPv6 DHCP server service failing to bind on an IPv6-disabled host is the expected, correct outcome, not a defect. Documented here explicitly so a future `systemctl --failed` audit doesn't waste time re-investigating it. | N/A — expected behavior, no fix needed. |

### Evidence basis

Direct `tsh ssh root@<host>` read-only commands via `scripts/collect-fleet-health.sh`, this session,
28/28 targeted hosts successful (two-batch capture after a mid-run script edit corrupted the first
batch — see the script's own header note on why editing a running script file is unsafe). Raw evidence
retained at `local-knowledge-ansible/ansible-wifi/issues/nbn-accelerate/fleet-hardware-audit-20260803/`
(relocated from `skill-smc/evidence/` per this pack's evidence-retention policy — see
`scripts/README.md`). Not covered: `cw` flavor itself (central-infra only, no site-level hosts to
check), `aurukun-smc03` (not reachable via `tsh ls` at capture time).

## Known Site Issues (as of 2026-06-30)

| Site | Issue | Status |
|---|---|---|
| kalumburu-smc01 | ~~graylog-sidecar inactive; cannot reach gl.aws.apn.au:443~~ — **RESOLVED 2026-07-10.** Live pre-deploy check found `graylog-sidecar.service` did not exist at all (never installed) — the 2026-06-30 "connectivity issue" framing was not reproduced/sourced in ansible-wifi. Phase 3 deployed (`smc_bases.yml` + `smc_graylog.yml`, `--limit kalumburu-smc01`); sidecar installed fresh, active, tailing syslog/squid/apache/apt/interfacecheck with no errors after a 15s settle check. | Resolved — see `smc-file-writing-analysis/docs/log-audit-results.md` 2026-07-10 09:18–09:31 UTC entry |
| ~~horn-island-smc01~~ | ~~557MB/day syslog flood from 13 Cambium APs via UDP 514; AP11 alone = 14.6M nl80211 kernel lines~~ | **RESOLVED 2026-07-15** — rsyslog drop filter deployed fleet-wide 12/12 (commit `3032c2a`). Only covers the `nl80211:`-tagged lines specifically, not the AP's other verbose chatter — see `08_ansible-authoring.md` "nl80211 rsyslog Drop Filter" for the full gotcha. **Severity understated by fatrace, found 2026-07-16**: a time-aligned live capture found horn-island writes ~16,400 actual syslog lines/5min (`nl80211:`/`mgmt:`/`WPA:`/hostapd chatter, 89%+ of volume) but only ~2,670 fatrace write-syscalls in the same window — rsyslog batches ~6 lines per syscall at this extreme volume vs ~1.2-1.3 on quieter nodes, so the fatrace `write_count` metric understates the true message flood ~6x here. See `smc-file-writing-analysis/docs/log-audit-results.md` 20260716_1300 and that project's `.archcore/rules/RULE-011` addendum. **Confirmed not an SMC-side debug flag, found 2026-07-16**: ruled out identical rsyslog config (byte-diff against a quiet node), raw AP/device count (mornington has 2x horn-island's Cambium device count but a tiny fraction of the chatter), and any ansible-wifi/SMC-side AP config (none exists at all for any site — Cambium APs are managed entirely through cnMaestro, outside this project's Teleport/ansible-wifi access). Fleet-wide grep of full retained syslog history: 10/12 nodes have **zero** `mgmt:`/`WPA:` lines ever; only horn-island and mornington have any, with horn-island ~80-410x mornington's volume depending on tag. Root cause is AP-side (hostapd/wpa_supplicant debug verbosity, or a firmware/model difference specific to those 2 sites) — needs whoever has cnMaestro/AP-admin access to compare horn-island's and mornington's AP hardware/firmware against the other 10 sites. Not fixable from this project. **Per-AP breakdown added 2026-07-16**: horn-island's chatter is ~73% concentrated in 2 of its 13 APs (AP11 50%, AP9 23% — refines the original 2026-06-04 "AP11 alone" finding by identifying AP9 as a second major contributor); mornington's is more evenly spread (top AP only 34% of its total) but shows a distinct anomaly — exactly 5 of its 13 APs each log exactly 444 `WPA:` lines, the rest exactly 0, suggesting a shared triggering event across those 5 specifically rather than organic traffic. See `smc-file-writing-analysis/docs/log-audit-results.md` 20260716_1420. **ROOT CAUSE CONFIRMED 2026-07-16 (operator, via cnMaestro)**: horn-island's and mornington's APs had Event Logging Severity set to `Debug`; every other site's APs are set to `Warning` — exactly the hypothesis this project raised. Fix in progress — correcting both sites' severity to `Warning`, a cnMaestro AP-config change entirely outside ansible-wifi/SMC scope. Once applied, re-sweep both nodes and reassess whether the `00-drop-nl80211.conf` rsyslog filter is still needed. See `smc-file-writing-analysis/docs/log-audit-results.md` 20260716_1445. **POST-FIX VERIFICATION 2026-07-16 ~15:00**: horn-island is **fully resolved** — live syslog sample shows zero `nl80211:`/`mgmt:`/`WPA:`, fatrace top5-sum dropped 3,793-4,144→1,324, now indistinguishable from a normal fleet node. Mornington is **partially resolved** — `nl80211:` still the live #1 tag, traced by source-AP grep to exactly 2 of its 13 APs still on `Debug` (AP47 `MOR_XV2-22H_AP47_IP3_227`, AP53 `MOR_XV2-22H_AP53_IP3_233`); the other 11 (including previously-worst AP19) confirmed clean. Actionable: apply the severity fix to AP47/AP53 specifically. See `smc-file-writing-analysis/docs/log-audit-results.md` 20260716_1500. **RE-CHECKED 2026-07-16 ~16:05 — AP47/AP53 CONFIRMED FIXED, but pattern shifted to 2 different APs**: a larger 3,000-line window confirms zero `nl80211:` from AP47/AP53. But `MOR_XV2-22H_AP35_IP3_215` (207 lines — previously mornington's *lowest*-volume AP, never flagged) and `MOR_XV2-22H_AP45_IP3_225` (2 lines, trace) now show the same debug signature. Mornington remains not fully resolved — stragglers changed, didn't disappear. See `smc-file-writing-analysis/docs/log-audit-results.md` 20260716_1605. **HORN-ISLAND REGRESSED 2026-07-17 — a repeat fleet-wide sweep found `nl80211:` back at 1,071 lines in a 2,000-line window (was zero every check since 2026-07-16's post-fix verification)**, horn-island jumped from 3rd-busiest to fleet-busiest node (rsyslogd 1,287→2,134). Traced 100% to a **new** AP — `HRN_XV2_AP5_IP3_50` — not AP11/AP9, which stayed clean. Same whack-a-mole pattern as mornington's AP35/AP45 emergence — this is the **3rd recurrence across the 2 sites** (horn-island AP11/AP9 → mornington AP47/AP53 → mornington AP35/AP45 → horn-island AP5). **Horn-island can no longer be called "fully resolved."** Recommend whoever has cnMaestro access audit Event Logging Severity across ALL APs at both sites in one pass, rather than continuing to chase individual stragglers reactively. See `smc-file-writing-analysis/docs/log-audit-results.md` 20260717_1020. **THE `00-drop-nl80211.conf` RSYSLOG FILTER WAS FOUND TO HAVE NEVER WORKED, REMOVED FLEET-WIDE 2026-07-17** — `if $msg contains 'nl80211' then stop` checks `$msg`, but real AP-relayed lines carry `nl80211` as the syslog TAG/`$programname`, not inside `$msg` (rsyslog splits TAG from MSG on ingest). Verified live on horn-island with paired `logger` probes: a tag-based test message (matching real AP format) was NOT dropped, while a message with `nl80211` inside the body WAS dropped. **This filter never blocked a single real AP-relayed line since deployment** — every past write-count improvement credited to it was actually the AP-side severity fix, not this filter. Removed rather than patched (ansible-wifi commit `9d9b0b9`, `roles/smc_rsyslog/tasks/main.yml`, deployed live to all 12/12, dry-run + live clean, verified via `tsh ssh`) since the AP-side fix is the real and only needed solution — **no local safety net now exists for this issue class**, see `08_ansible-authoring.md` "nl80211 rsyslog Drop Filter" (needs updating to reflect removal). **AP5 SEVERITY FIX CONFIRMED LIVE 2026-07-17 ~13:45** — verified rather than taken on report alone: `nl80211:` dropped from 1,071/2,000 to 2/3,000 (residual = `localhost` boilerplate, not AP-relayed), fresh tag sample shows normal DHCP-dominant baseline. **Horn-island is fully clean again** — this was the 4th AP fixed via this process across the 2 sites (AP11, AP9, AP47, AP53, AP35/AP45 partial, AP5). The "audit all APs at both sites in one pass" recommendation remains open. See `smc-file-writing-analysis/docs/log-audit-results.md` 20260717_1330, 20260717_1345. |
| wujal-wujal-smc01 | syslog.2 = 222MB uncompressed (Jan file) | Cleanup needed |
| mornington-smc01 | `/var/lib/dhcp/dhcpd.leases` = 223MB | Investigate lease cleanup |
| bidyadanga-smc01, wujal-wujal-smc01 | **`dhcpd.leases.<unix-epoch>` orphaned snapshot files — CONFIRMED FLEET-WIDE PATTERN 2026-07-17.** isc-dhcp-server's atomic lease-rewrite temp file, usually self-cleaning (confirmed on horn-island — the same file pattern appeared transiently in fatrace top-5 twice, `smc-file-writing-analysis/docs/log-audit-results.md` 20260716_1500 and 20260717_1020, gone both times when checked live immediately after), but sometimes orphaned. bidyadanga: 2 files from April 2024 (68K+235K). wujal-wujal: 4 files from May 2025–March 2026 (~1.1MB total), newly found. Likely an interrupted/crashed rewrite. See `smc-file-writing-analysis/docs/log-audit-results.md` 20260717_1020 "Finding 2". | Low priority (single-digit MB) — needs operator approval per destructive-command guard before cleanup; bundle with the deferred DHCP-split item |
| guda-guda-smc01 | ~~graylog-sidecar `active` but writing to local disk, not tmpfs~~ **RESOLVED 2026-07-14** — turned out a standard `smc_graylog.yml` redeploy fixed it cleanly; the "investigate why the config never took" concern didn't materialize into a distinct root cause, it just needed the normal rollout like every other node. | Resolved — see `smc-file-writing-analysis/docs/log-audit-results.md` 20260714_0830 entry |
| bidyadanga-smc01 | ~~Graylog connectivity broken since 2026-05-18~~ **CORRECTED 2026-07-16** — that framing was stale: the May-June sidecar.log errors were the sidecar's own self-health-check, unrelated to actual log shipping, self-resolved by the 2026-07-14 Phase 3 redeploy, not reproduced live. Real current issue: fleet-wide GELF-HTTP silent drop rate (0.2%-56.5% per node) from a hard 64 KiB WAF/ALB body-size limit on `gl.aws.apn.au`, confirmed via live curl binary search — server-side, not bidyadanga-specific. See `smc-file-writing-analysis/docs/log-audit-results.md` 20260716_1230. ~~graylog-sidecar `active` but writing to local disk~~ **RESOLVED 2026-07-14** — same as guda-guda, standard `smc_graylog.yml` redeploy fixed it, no special investigation needed. dhcpd churn (8,171 leases, old snapshots not cleaned) still unaddressed. | GELF drop-rate root-caused, fix pending decision (needs Graylog admin access + WAF/ALB owner); dhcpd churn unaddressed |
| warburton-smc01 | Same `dhcpd`+`dhclient` lease-churn pattern as mornington/bidyadanga/wujal-wujal (confirmed live 2026-07-16, see below) | dhcpd churn unaddressed, same class as the 3 rows above |
| kalumburu-smc01 | **New 2026-07-16**: the only rcp node where `auth.log` (129/300s) edges out `syslog` (128/300s) in top writers — every other node has syslog clearly #1. Also the fleet's worst GELF-HTTP drop rate (56.5%, see bidyadanga row above) — two independent oddities on the same node, not yet investigated together or root-caused. | Not investigated — flagged only |
| jigalong-smc01 | `cnPilot`/`Could` top syslog tag, initially suspected to be the same raw-AP-relay-chatter signature as horn-island's nl80211 flood. **ROOT-CAUSED 2026-07-16 — confirmed NOT the same issue**: at least 5 distinct Cambium devices (serial-number hostnames — likely subscriber/CPE radios, not APs) stuck in an infinite cnMaestro registration retry loop, each rejected with `"Device Not Claimed"` (error 1011) every ~5 minutes, 5 log lines/cycle (17,500-17,900 lines/device in retained history). A provisioning gap (devices never claimed in cnMaestro), not a logging-severity setting. See `smc-file-writing-analysis/docs/log-audit-results.md` 20260716_1530. | Not fixable from ansible-wifi/SMC side — needs cnMaestro access to claim the devices |
| bungardi-smc01 | Multi-incident cluster, 2026-07-21→07-27 (master branch), each with a distinct root cause: (1) `apt-get clean` exiting rc=100 traced to a **hostapd driver hang** (33 processes stuck D-state on `genl_rcv`) — not lock contention as first suspected, and explains a prior 14-day wedge dating to Jul-10; (2) a system-wide nl80211 netlink wedge, resolved by a kernel `5.15.0-1064-raspi` reboot, after which hostapd was disabled; (3) Teleport TLS handshake failures traced to `upgrade_teleport.sh` purging node identity across a major-version upgrade combined with an ALPN routing change, plus `teleport.yaml` alphanumeric-key validation contradictions; (4) a persistent Teleport reverse-tunnel registration failure ~50s post-join that survived the cert fix; (5) eth0 flaky under load, traced to simultaneous TCP resets from both `teleport` and `autossh` to `teleport.communitywifi.net.au` — pointing at a WAN-level issue rather than a local NIC fault (`ethtool`/`dmesg` both clean), recurring after restart #31 | Partially resolved (hostapd/netlink/kernel reboot); Teleport reverse-tunnel registration and eth0/WAN flakiness remain open — needs field/WAN follow-up. Diagnostic pattern worth reusing: a driver hang can masquerade as lock contention via D-state processes — check `ps` state column before assuming a lock-file/flock issue |
| amata-smc01 (nbn_accelerate) | Root filesystem forced read-only by an active SATA/ATA disk-path fault since 2026-04-25 (`ata4.00` COMRESET failures, `DID_BAD_TARGET`) — **still open as of the last check (2026-04-30)**, not yet recovered via reboot/failover; PIN/session enforcement chain (`ECLIPSE_*` marks + `netfilter-persistent`) needs re-establishing once the box is writable again | Open — see `06_failure-modes.md` "Disk Path Failure Forcing Root Read-Only" |
| pandanus-park-smc01 (rcp) | `interfacecheckv2.sh`'s 5-minute cron restarted `enp2s0`, `vlan531`, `vlan532`, `vlan621`, `vlan631` on **every single cycle**, continuously, for 24h+ (as of 2026-07-30). `vlan531`/`vlan532` are expected to clear once the corrected dhclient hook deploys fleet-wide; `vlan621`/`vlan631` restarting is expected/benign (cold-standby links with no live cable); `enp2s0` restarting is a genuinely separate, unexplained fault not yet investigated. Worth checking as a general diagnostic pattern (chronic per-cycle restart = live evidence of the Problem-2-class topology/hook mismatch) on other sites too, not just this one | Not fully investigated — `enp2s0` restart cause open; `local-knowledge-ansible/ansible-wifi/issues/apn/routing-issue/docs/pandanus-park-interfacecheck-chronic-restart-20260730_1140.md` |
| old-looma-smc01 (rcp) | `smc_iptables`-rendered config removes INPUT ACCEPT rules for Asterisk/MQTT/Cambium-TFTP that are actually present on the live deployed ruleset — a real ACL drift, unrelated to the topology/routing investigation it was found during, not yet fixed | Open, unfixed — `local-knowledge-ansible/ansible-wifi/issues/apn/routing-issue/docs/problem2-live-root-cause-20260729_2112.md` |
| warburton-smc01 (rcp) | `iptables.smp.j2`'s starlink `INPUT ... -j DROP` rule on `vlan621` (the only site with a live SMP-backup lease at check time) shows 1.68M packets/3.3GB dropped over 2 weeks. Two 5-minute live `tcpdump` captures (Warburton + Old Looma) found zero unsolicited third-party inbound traffic — only the box's own self-generated ARP/ICMP/DHCP. Ruled out: self-generated traffic, public-internet exposure (address is RFC1918 private, not public — see the stale-comment note above). Not confirmed: leading hypothesis is shared-carrier L2 segment noise; would need an hours-long capture or a live `iptables LOG` rule (a real ruleset change, separate authorization) to pin down | Open, unresolved — `local-knowledge-ansible/ansible-wifi/issues/apn/routing-issue/docs/starlink-backup-no-lease-l2-investigation-20260730_1400.md` |
| mercedes-cove-smc01 (rct) | Captive portal returns `Attempt to read property "result" on null` — a distinct application bug surfaced during the 2026-07-28 rcp portal-outage fleet sweep, unrelated to the cache-perms issue that prompted the sweep | Open, not investigated — `rcp-captive-portal-cache-perms-outage-20260728_1240.md` §10 |
| `inventories/rcp/prod` | Declares `[horn-island_smc_bases]` twice (lines 42 and 45) — cosmetic inventory duplication, not observed to cause incorrect behavior, but should be cleaned up | Open, cosmetic — `rcp-captive-portal-cache-perms-outage-20260728_1240.md` §10 |
| tjuntjuntjara-smc01 | `netifd` top syslog tag (the only CFast node where DHCP doesn't dominate), initially suspected to be the same AP-relay-chatter class. **ROOT-CAUSED 2026-07-16 — confirmed NOT the same issue**: at least 5 distinct devices with `eth0` links rapidly cycling down/up (18,000-36,000 lines/device in retained history, e.g. `TJN_F300SM_1065_IP_2_65` down→up within 1-2 seconds repeatedly). Likely a physical-layer issue (power/cabling/interference), not confirmed. See `smc-file-writing-analysis/docs/log-audit-results.md` 20260716_1530. | Needs field/hardware investigation — not a config change |

**2026-07-16 synthesis — the fleet's 5 highest fatrace nodes generalize into two distinct causes,
not one shared bug** (full detail: `smc-file-writing-analysis/docs/log-audit-results.md`
20260716_1118): (1) **mornington, warburton, bidyadanga, wujal-wujal** are high because they're
currently the busiest public-WiFi sites — live `/var/log/syslog` tail on all 4 shows `dhcpd`+
`dhclient` as the #1/#2 tag by volume, i.e. ordinary client connect/disconnect churn, not a defect
— this ties together the previously separate per-node dhcpd/lease notes above into one fleet-wide
pattern. (2) **horn-island** is the one node with an actual unresolved defect layered on top of
that same baseline traffic — the nl80211 filter above still only blocks that one tagged string,
confirmed still 89% of its fatrace top5 sum live today. Do not conflate the two: adding a
dhcpd/DHCP-churn "fix" would not touch horn-island's issue, and vice versa.

## Out of Scope (permanent)

- Bugs that only appear on live hardware (require CI/test environment)
- CNMaestro / NBN API behaviour (external systems; no test access)
- WiFi RF performance (hardware/environment)
- Multi-engineer workflow coordination (process problem, not knowledge problem)

---

## 2026-07-28 — fleet fatrace sweep findings (all 16 rcp incl. new-looma)

Source: `smc-file-writing-analysis/docs/log-audit-results.md` `20260728_1033`; per-node trend rows in `docs/fatrace-sweep-history.csv`.

### GELF-HTTP 413 — the known 64 KiB limit also costs local SSD (new dimension)

The fleet-wide GELF drop issue in the bidyadanga row above (64 KiB WAF/ALB body-size limit on `gl.aws.apn.au`, root-caused 2026-07-16) surfaces on-box as
`[error] [output:http:http.0] gl.aws.apn.au:443, HTTP status=413` + `[ warn] ... chunk will not be retried`, continuously since **2026-07-14 07:38** on **all 16 rcp nodes**.
Counts: mornington 184,573 / bidyadanga 57,989 / horn-island 37,557 / tjuntjuntjara 35,802 / wujal-wujal 22,101 / remainder 375–4,375.

**The part not previously recorded: `/var/log/fluent-bit/fluent-bit.log` is not on tmpfs**, so this retry loop is a real-SSD writer — mornington 157M, wujal-wujal 81M,
tjuntjuntjara 54M, bidyadanga 49M, burringurrah 36M, horn-island 16M. It is what puts `fluent-bit` back into the fatrace top-5 on tjuntjuntjara (160) and horn-island (163).

**Two traps when reading this signal:**
1. `fluent-bit` reappearing in a fatrace top-5 is **not** automatically a rise-gate (`68a08bfc`) regression. Check the log body first — if it is 413/flush errors, the rise-gate
   fix is still holding and this is the 413 loop.
2. Do not disposition the writes as STOP (RULE-008). The writes are the symptom; the dropped log shipping is the defect, and it is blocked on Graylog-admin/WAF access.
   The SMC-side half that *is* actionable without external access: relocate `/var/log/fluent-bit/` onto the smc-groups tmpfs. Not yet done.

### Fluent Bit squid/mosquitto tail inputs failing — it is a SQUID OUTAGE, and "check permissions" is a misleading message

On tjuntjuntjara (98,607 occurrences) and horn-island (35,365), vs a uniform ~4,245 baseline on the 13 healthy nodes:
`[error] [input:tail:squid] read error, check permissions: /var/log/squid/*.log` (and the mosquitto equivalent).

**RESOLVED 2026-07-28 — and the severity was understated when first written.** squid was not merely failing to log on these nodes, it was **failing to start** (`/var/log/squid/cache.log: No such file
or directory` → `FATAL` → restart-backoff), which is a **user-facing outage** because squid sits in the mandatory tcp/80 intercept path and is the captive-portal redirector. Root cause:
`/var/log/smc-groups` is an fstab tmpfs, so its subdirs die on every reboot, and the ansible tasks creating them are guarded on `stat.islnk` so an ansible re-run does not heal a rebooted node either.
Only the two nodes that had rebooted since the 2026-07-23 relocation were broken — **the other 13 were latent, not fixed**. Fixed by a `tmpfiles.d` rule in `smc_rsyslog`; see **RULE-016** in
`smc-file-writing-analysis/.archcore/rules/` for the full pattern and the safe way to verify it. **It is not a permission problem — Fluent Bit runs as root.** The glob matches nothing:
`/var/log/smc-groups/squid/` and `/var/log/smc-groups/mosquitto/` hold **zero files** on
those two nodes, where the other 13 have 2 and 1. The symlinks are correct on all 16 (`/var/log/squid -> /var/log/smc-groups/squid`, dated 2026-07-23), so this is
**empty-target, not broken-link** — apparent fallout from the 2026-07-23 squid/mosquitto→tmpfs move on those two nodes. Diagnose why the services emit no files under the tmpfs
target rather than chasing ownership/modes.

### new-looma-smc01 — was in production missing the log-consolidation stack (REMEDIATED 2026-07-28)

new-looma is live and carrying traffic as of 2026-07-28 and is the **fleet's heaviest writer** (827 top-5 top_path events/300s, ~3.7× fleet median). The 2026-07-23 onboarding
delivered `smc_bases`/`smc_graylog`/`smc_prometheus`, but the same-day log-consolidation rollout (`594653b`) skipped it while it was DOWN. Verified live:

- `/etc/rsyslog.d/` holds **only stock Ubuntu configs** (`20-ufw`, `21-cloudinit`, `50-default`, `postfix`) — no `smc_rsyslog` files, no wifi/dhcp/system split.
- **No `/var/log/smc-groups`** — squid, interfacecheck and mosquitto all on real ext4. Top paths: `/var/log/syslog` 574, `/var/log/auth.log` 110, `mosquitto.log` 105.
- journald **is** correctly volatile (`99-smc-volatile.conf`, 200M in `/run/log/journal`), but **337M of stale archived journal** still sits on `/var/log/journal` from before the
  drop-in landed — reclaimable, not ongoing writes. A volatile journald drop-in does **not** clean up pre-existing `/var/log/journal` content; check for it on any node converted
  after it had been running persistent.
- `/var/lib/prometheus` tmpfs is **128M, not the 256M** the rest of the fleet was rebalanced to.
- `fatrace` was **not installed** — itself a reliable tell that a node was never reached by the ansible-wifi package pass. Per `smc-file-writing-analysis/AGENTS.md` standing
  policy, install it rather than substituting another tool, so write-rate numbers stay comparable across nodes.

**Remediated 2026-07-28** — and only two of the four items listed here were real. `smc_rsyslog` was deployed and verified (`ok=37 changed=23 failed=0`), and the orphaned journal was reclaimed
fleet-wide (see below). **The other two were never gaps:** `/var/lib/prometheus` at 128M *is* the fleet standard (the 128M→256M rebalance covered `/tmp` and `fbpos` only), and tmpfs monitoring was
already published on new-looma. Both had been asserted from a status doc's pending list without a live check. Also note `journalctl --vacuum-time` **cannot** reclaim the stale journal — see the
journal section below. new-looma is now at full 16/16 parity.

**Second confirmed outage, 2026-08-01 23:40 UTC → 2026-08-03 06:40 UTC (31h) — operator-reported "back online," confirmed via live Prometheus (`mcp-grafana-apn`).** `up{instance="new-looma-smc01:9090",job="prometheus"}` and `up{instance="new-looma-smc01:9100",job="node_exporter"}` both dropped from the scrape at the same instant and returned at the same instant — i.e. the whole host went unreachable (network/power/backhaul), not a single service crashing, since a service-level failure would leave `node_exporter` (or the self-scrape) reporting `up=1` while only the failed service's own metric goes stale. **Root cause not established this session** — no live `tsh ssh` access was used, only read-only Prometheus history via Grafana MCP; this is a confirmed timeline, not a diagnosed cause. A separate, earlier 18h gap in the same 7-day window (2026-07-29 11:10 UTC → 2026-07-30 05:10 UTC) lines up exactly with the already-documented topology cross-wiring fix and "New Looma reconstruction" in `08_ansible-authoring.md` (§ backup-vlan-trunk-fixed-and-new-looma-online-20260730_1520.md) — that gap is explained, this new one is not. Two whole-host outages in ~5 days is a recurrence pattern worth watching, not necessarily the same root cause as the cross-wiring bug (which was fixed and verified). If picked up: check whether this outage also correlates with the still-open `my_node_network_device_info` zero-series gap on new-looma (topology-derived textfile collector, unresolved, see the Known Operational Bugs table above) — both are new-looma-specific and topology/network-adjacent, but no shared mechanism has been established between them.

### guda-guda dhcpd lease churn — LOCAL-KEEP, not a new fault

guda-guda's +169% sweep-over-sweep rise is one path: `/var/lib/dhcp/dhcpd.leases.<epoch>` at 186 events — isc-dhcp-server's atomic lease-rewrite temp file (same class as the
orphaned-snapshot row in the table above). Server-side DHCP lease state must survive reboot, so it stays **LOCAL-KEEP** — distinct from the client-side `dhclient` leases
withdrawn to disk on 2026-07-24.
````

## File: scripts/README.md
````markdown
Title: skill-smc — Reusable Diagnostic and Validation Scripts
Category: script-inventory
Status: current
Authority: local-supplement
Scope: Reusable read-only diagnostic tooling for SMC WAN-routing/topology-drift investigations and fleet-wide hardware/service-health audits, plus generic ansible-lint pre-push/CI gate scripts for the ansible-wifi repo
Summary: Three categories — (1) WAN-routing diagnostics (evidence capture + drift analysis + topology/hardware cross-check + task-runner template), promoted from the 2026-07-29/30 APN routing-issue
  investigation; (2) ansible-lint baseline/delta-gate scripts, promoted 2026-07-31 from `local-knowledge-ansible/ansible-wifi/scripts/`, for a pre-push hook that blocks only NEW lint violations;
  (3) fleet hardware/security/service-health audit (evidence capture + task-runner), written 2026-08-03 for the first full NBN Accelerate cluster sweep.
  Read before running the WAN-routing tools: the "hook covers netplan" discriminator they automate, and why it works, is documented in `../references/03_communication-flows.md`.

# scripts/

Promoted **2026-07-29** (evidence capture + drift analysis) and **2026-07-30** (topology/hardware cross-check) from `local-knowledge-ansible/ansible-wifi/issues/apn/routing-issue/scripts/`, where
they were built and live-validated across all seven `rcp` sites during that investigation. Kept here so a future WAN-routing investigation — any site, any flavor — doesn't have to re-derive the
discriminator or re-write the capture set from scratch.

**These are deliberately separate copies from the investigation folder's originals, not symlinks.** Promotion is a review checkpoint, not a relocation — the copies here are genericized (no
hardcoded site lists, `OUTDIR_ROOT` override, etc.) and are meant to diverge from whatever an investigation folder's working copy does next. When an investigation script changes in a way worth
having everywhere, diff it against the promoted copy and re-apply deliberately (see e.g. the `dmidecode-model` capture below) rather than assuming the two stay in sync automatically.

**Promotion checklist — every time a script is promoted or an existing promoted script is updated:**
1. Copy/update the script itself here, genericized (no investigation-specific hardcoding).
2. Add or update its row in the safety-classification table and its own `###` section below.
3. **Update `routing-diagnostics.justfile`** with any new recipe the script needs — a script with
   no justfile recipe is easy to forget exists. Confirmed missed once (2026-07-30) before being
   caught and fixed in the same pass; treat this as a mandatory step, not an afterthought.
4. Cross-reference the relevant `../references/*.md` file if the script encodes a lesson worth
   capturing there too (it usually does).

**Safety classification, per the parent policy — every script here is catalogued. An uncatalogued script must be treated as `unknown` safety until inspected.**

| Script | Touches | Safety | Notes |
|---|---|---|---|
| [collect-smc-evidence.sh](collect-smc-evidence.sh) | Live SMC appliances over Teleport | **read-only** | Remote command set is hardcoded; the script takes host names only, never arbitrary commands. **Requires explicit hosts as arguments — no default site list** (genericized from the original, which defaulted to one investigation's specific sites) |
| [analyse-routing-drift.py](analyse-routing-drift.py) | Local `evidence/` tree, local `ansible-wifi` git objects | **read-only** | `git show` only; never checks out, never writes to the ansible repo. `--flavor` selects `inventories/<flavor>/topology_vars`; `--commit` selects the comparison ref — both default to the original investigation's `rcp`/`fb419e6c` and should be overridden per new investigation |
| [analyse-topology-interface-match.py](analyse-topology-interface-match.py) | Local `evidence/` tree, local `ansible-wifi` working tree | **read-only** | Reads `topology_vars/<site>.yml` from the working tree (not a specific commit — pre-deploy sanity check, not historical drift analysis); `--flavor` overridable |
| [routing-diagnostics.justfile](routing-diagnostics.justfile) | Wraps the three scripts above | **read-only** | A **template**, not a ready-to-run file — copy it into a new investigation folder and edit the `sites`/`deployed`/`flavor` variables at the top before use |

**Nothing here may write to an SMC.** If a future task needs a mutating command, run it by hand under change control and record it in the investigation's own analysis — do not add it to
`collect-smc-evidence.sh`. The read-only contract is what makes it safe to run these against production sites without a change window.

**Fleet hardware/security/service-health audit (promoted 2026-08-03, different category — full-fleet hardware/software inventory, not WAN-routing-specific):**

| Script | Touches | Safety | Notes |
|---|---|---|---|
| [collect-fleet-health.sh](collect-fleet-health.sh) | Live SMC appliances over Teleport | **read-only** | Same hardcoded-command, host-names-only contract as `collect-smc-evidence.sh`. Bundles ~20 read-only commands into 4 grouped captures (not one-command-per-round-trip) to stay tractable at fleet scale over satellite links — see the script's own header note |
| [fleet-health.justfile](fleet-health.justfile) | Wraps `collect-fleet-health.sh` | **read-only** | Unlike `routing-diagnostics.justfile`, ships with a real current site list (the NBN Accelerate cluster, confirmed live via `tsh ls` 2026-08-03) rather than a placeholder — edit `sites` or override on the command line for a different fleet |

**Requires explicit hosts as arguments — no default site list in the script itself** (the justfile's `sites` variable supplies the default site list for `just collect`, the script always requires args).

**Ansible-lint pre-push/CI gate (promoted 2026-07-31, different category — no SMC/host access at all):**

| Script | Touches | Safety | Notes |
|---|---|---|---|
| [lint-baseline-refresh.sh](lint-baseline-refresh.sh) | Local git repo only (`ansible-lint --generate-ignore`) | **read-only w.r.t. the repo's tracked content** | Writes only to `.git/.ansible-lint-ignore` (an untracked git-internal file, not repo content). Genericized: config path defaults to `<repo_root>/.ansible-lint`, override with `ANSIBLE_LINT_CONFIG=<path>` — the two scripts this was promoted from disagreed on a hardcoded path (`local-knowledge/` vs `local-knowledge-ansible/`); this removes that class of drift |
| [ansible-lint-delta-gate.sh](ansible-lint-delta-gate.sh) | Local git repo only (`git diff`/`git cat-file`, `ansible-lint`) | **read-only** | Never writes anything; exits non-zero only to block a push/commit. Same `ANSIBLE_LINT_CONFIG` override as above. Falls back through `@{upstream}` → `origin/master` → `origin/main` → empty-tree for the comparison base, so it works on a fresh clone with no upstream configured |

### `lint-baseline-refresh.sh`

Regenerates `.git/.ansible-lint-ignore` from every currently-lintable file (`*.yml`, `*.yaml`,
`*.j2` tracked by git), sorted and deduplicated. Run this deliberately when you want to accept the
current violation set as the new baseline (e.g. after a bulk cleanup, or when first adopting the
delta-gate on a repo with existing debt) — **not** as part of every normal lint run, since that
would silently re-baseline away violations introduced since the last refresh.

```bash
scripts/lint-baseline-refresh.sh
# override config location if not at <repo_root>/.ansible-lint:
ANSIBLE_LINT_CONFIG=/path/to/.ansible-lint scripts/lint-baseline-refresh.sh
```

### `ansible-lint-delta-gate.sh`

Meant to run from a pre-push hook (or CI) with the set of changed ansible files as arguments. Runs
`ansible-lint` against exactly those files, then classifies every violation:

- **New file** (didn't exist at the merge-base with upstream) → always blocking.
- **Existing file, violation on a line the diff actually touched** → blocking.
- **Existing file, violation on an untouched line, and it's in the baseline** → allowed (pre-existing debt, not yours).
- **Existing file, violation on an untouched line, NOT in the baseline** → blocking (a genuinely new finding on an old line — e.g. a rule version bump surfacing something new).
- **Warnings** → never blocking.

```bash
scripts/ansible-lint-delta-gate.sh roles/smc_network/tasks/ubuntu.yml roles/smc_dns/templates/unbound.conf.j2
```

Exits 0 (with `clean` or `no new violations`) when safe to proceed, non-zero with the blocking
violation list on stderr otherwise. Requires `ansible-lint` on `PATH` (or set
`ANSIBLE_LINT_VENV_BIN` to a venv's `bin/` directory, same convention both scripts share).

## What each script is for

### `collect-smc-evidence.sh`

Captures the following read-only views from each appliance into `<output-root>/evidence/<YYYYMMDD_hhmm>/<host>/`:

| Capture | Command | Why it matters |
|---|---|---|
| `ip-route` | `ip route show` | The ECMP pool and any stray `metric 100` default — the primary evidence for a Problem-1-class fault |
| `ip-route-table-all` | `ip route show table all` | The per-interface tables the dhclient hook builds for `role: internet` interfaces |
| `ip-rule` | `ip rule show` | A source rule per interface proves the hook recognised that interface |
| `ip-addr` / `ip-link` | `ip -br addr` / `ip -br link` | Which interfaces hold a CGNAT lease; the deterministic `72:77:77:*` generated MACs |
| `dmidecode-model` | `dmidecode -s system-product-name` | Which SMC chassis this is — different models use different physical NIC naming schemes (`enp1s0`-`enp4s0` vs `eno1`/`enp3s0`/...), and `topology_vars` can silently assume the wrong one. Feeds `analyse-topology-interface-match.py`'s cross-model naming hint |
| `netplan` | `cat /etc/netplan/*.yaml` | What `smc_network` actually rendered — compare against the deployed topology |
| `dhclient-enter-hooks` | `cat /etc/dhcp/dhclient-enter-hooks` | What `smc_application` rendered — **the interface list that decides ECMP membership** |
| `dhclient-enter-hooks-d` | `cat /etc/dhcp/dhclient-enter-hooks.d/*` | Stock Debian fragments only; kept to prove the override is not here (see capture trap below) |
| `dhclient-script` | `cat /etc/dhcp/dhclient-script` | Base `add_default_gateway()` and `is_router_reachable()` |
| `dhclient-units` | `systemctl list-units 'dhclient@*'` | Which interfaces are actually being leased |
| `iptables-save` | `iptables-save` | All tables in one dump — the authoritative ruleset snapshot |
| `iptables-filter` / `-nat` / `-mangle` / `-raw` | `iptables [-t <table>] -S` | Per-table views — `filter`-only misses NAT/mangle entirely (see capture trap below) |
| `interfacecheck` | `cat /usr/local/bin/interfacecheckv2.sh` | The ping check and its `dhclient@` restart behaviour |
| `internet-ingress-shaping-script` / `internet-shaping-service` / `internet-shaping-unit-status` | script/unit/status | The manual TBF/`ifb` ingress-shaping mechanism — see `../references/03_communication-flows.md`, "Manual TBF/`ifb` Ingress Shaping" |
| `tc-qdisc` / `ip-link-ifb` | `tc -s qdisc show` / `ip -br link show type ifb` | Actual configured shaping rate/burst/latency and traffic counters, and which `ifb*` redirects exist |
| `netplan-mtime` / `hook-mtime` | `stat --format='%Y %y %n' ...` | Last-modified time of netplan vs the dhclient hook — directly shows how far apart `smc_network` and `smc_application` were last actually run |

**Two capture-path traps, both hit and corrected on 2026-07-29** — see `../references/03_communication-flows.md` for the full write-up:

- **The dhclient override is `/etc/dhcp/dhclient-enter-hooks`, without an extension.** `/etc/dhcp/dhclient-enter-hooks.d/` contains only stock Debian fragments and does **not** contain
  `add_default_gateway()`. Capturing only the `.d/` directory silently yields the wrong file with no error.
- **`iptables -S` shows only the `filter` table.** `smc_iptables` templates declare `*filter`, `*mangle` and `*nat`, and the role also references `-t raw`. A filter-only capture misses NAT and
  mangle entirely.

### `analyse-routing-drift.py`

Reads a capture directory and correlates it against the topology committed at a given commit (`--commit`, `--flavor`). For each site it reports the switch01 primary count in git, the live ECMP
members, the stray `metric 100` interface, and any interface holding a lease with no matching `ip rule` (leased but unrecognised by the hook). This automates **the discriminator**: a site is
healthy exactly when the dhclient hook's `case` arm covers every uplink VLAN netplan defines (excluding the SMP-backup VLANs, which are meant to be absent). Full mechanism write-up in
`../references/03_communication-flows.md`.

`--markdown` emits a table ready to paste into an analysis document.

### `analyse-topology-interface-match.py`

Cross-checks a site's committed `topology_vars/<site>.yml` against what the box's live `netplan` actually has, in both directions: every physical interface name and VLAN-parent pairing
topology_vars declares is checked against netplan, and every real (`macaddress:`-bearing) VLAN on the box is checked for a matching topology_vars entry. Also flags a physical interface name
that isn't typical for the box's `dmidecode`-reported model, when the model is in the script's `KNOWN_MODELS` table.

**Run this before editing any site's `topology_vars`, or before deploying to a site you haven't touched recently** — none of `yamllint`/`ansible-lint`/`--syntax-check` catch a topology file that
parses fine but names the wrong physical NIC or points a VLAN at the wrong parent. Confirmed live at New Looma (2026-07-30): `topology_vars` named a WAN interface `eno1` — a NIC name that exists
on a *different* SMC chassis model, not the BOXER-6404 actually deployed there — and had the WAN/LAN-trunk physical roles completely cross-wired. `yamllint`/`ansible-lint`/`--syntax-check` all
passed anyway. See the "Mandatory pre-check" note in `../references/08_ansible-authoring.md` for the full incident.

```bash
./analyse-topology-interface-match.py <site>                    # newest capture
./analyse-topology-interface-match.py <site> <capture-dir>
./analyse-topology-interface-match.py <site> --flavor rct
```

### `collect-fleet-health.sh`

Captures a broad hardware + software-inventory snapshot from each appliance into
`<output-root>/evidence/<YYYYMMDD_hhmm>/<host>/`, grouped into 4 files instead of one-per-command
(see the script header for why):

| Capture file | Covers | Why it matters |
|---|---|---|
| `01-identity-hardware.txt` | hostname/uptime/kernel/OS, `dmidecode` manufacturer/product/serial, CPU (`lscpu`), RAM (`free -h`), disks (`lsblk`, `df -h`), `smartmon.prom`/`sbdm.prom` textfile-collector SSD health, overlayroot mount state | The chassis-model + resource baseline this pack never had for `nbn_accelerate`/`nbn_wh` before 2026-08-03 |
| `02-services-security.txt` | `systemctl --failed`, Teleport/autossh state, DNS-stack (`unbound`/`stubby`/`named`), ClamAV daemon + `freshclam` detailed status, Lynis presence, full list of running services | ClamAV/Lynis is an `nbn_accelerate`-only hardening gate (`08_ansible-authoring.md`) — the `freshclam` status specifically checks for the CDN-block finding first seen 2026-08-03 on `warakurna`/`indulkana` |
| `03-apps-scripts-cron.txt` | `apn-mqtt-client`/`cnmaestro-provisioning`/`url_capture` presence, Kohana portal git reflog, `graylog-sidecar`/`node_exporter`/`prometheus`/`fluent-bit`/`cnmaestro-provisioning` service state, `/usr/local/{bin,sbin,lib}` listing, `crontab -l`, `/etc/cron.d/`, `systemctl list-timers` | Surfaces undocumented custom scripts the way the rcp-fleet audits in `smc-file-writing-analysis` found several — don't assume the documented app list is exhaustive |
| `04-portal-packages.txt` | Apache vhost config, mobile-app-backend + Kohana portal dir presence, installed versions of `bind9`/`unbound`/`stubby`/`apache2`/`php*`/`clamav`/`lynis`/`prometheus`/`node-exporter`/`fluent-bit`/`teleport`/`isc-dhcp-server` | Confirms/refutes the code-inspection-only portal-protocol and package claims in `01_overview.md`/`10_captive-portal.md` |

```bash
./collect-fleet-health.sh warakurna indulkana bungardi        # named sites
# or, with the pre-populated NBN Accelerate site list:
just -f fleet-health.justfile collect
just -f fleet-health.justfile freshclam-check                 # quick cross-host summary
just -f fleet-health.justfile chassis-models
```

**Sites with more than one numbered host (e.g. `aurukun-smc01`/`aurukun-smc02`) must be passed
with their full `-smcNN` suffix** — a bare `aurukun` always resolves to `aurukun-smc01`.

**`just -f <path>` runs recipes with cwd = the justfile's own directory, not the invoker's cwd —
confirmed the hard way on the first real fleet run.** `fleet-health.justfile` lives in `scripts/`,
but `collect-fleet-health.sh` writes `evidence/` into its *parent* directory (skill-smc root) by
default. A recipe written as `./scripts/collect-fleet-health.sh` or a bare `evidence` path looks
correct when read, but silently resolves to a nonexistent `scripts/scripts/...` or `scripts/
evidence/` and fails (or worse, reports a misleading "no captures yet" instead of an error).
`fleet-health.justfile`'s recipes use `./collect-fleet-health.sh` (sibling file) and `../evidence`
(one level up) for this reason — if you add a recipe to a justfile that lives in `scripts/`,
match that convention, and **run every new recipe for real before trusting it**, the way this one
was dogfooded: three of its four quick-check recipes had real bugs (wrong paths, and the same
exit-code-of-last-command quirk documented in `collect-fleet-health.sh`'s header) that a syntax
check alone would never have caught.

## Usage

```bash
# One-off, no justfile:
./collect-smc-evidence.sh <site1> <site2> ...
./analyse-routing-drift.py --flavor <flavor> --commit <ref>
./collect-fleet-health.sh <site1> <site2> ...

# Or copy routing-diagnostics.justfile into your investigation folder, edit its top variables, then:
just collect
just analyse-md

# fleet-health.justfile ships with a real site list already — usable directly from skill-smc/scripts/:
just -f fleet-health.justfile collect
```

## Requirements

- `tsh` logged in to the relevant Teleport cluster (`tsh login`).
- `just` (optional — only needed if using the justfile template), `bash`, Python 3 (standard library only — no third-party imports).
- A local clone of `ansible-wifi` at `/Volumes/Data/_ansible/ansible-wifi` for the topology comparisons.

## Evidence retention

Captures are the only record of live state at a point in time and **should be kept**, not deleted to save space — they cannot be regenerated for a past date. Write them into your investigation
folder's own `evidence/` directory (via `OUTDIR_ROOT=<investigation-path> ./collect-smc-evidence.sh ...` or `./collect-fleet-health.sh ...`), not into this skill-smc directory — skill-smc holds
reusable knowledge and tooling, not case-specific evidence. See the parent repo's canonical-source-of-truth policy on keeping investigation artifacts local to their investigation folder.

**The 2026-08-03 NBN Accelerate fleet sweep was captured without `OUTDIR_ROOT` set** (script default, under `skill-smc/evidence/`) — relocate that capture to a case-specific
`local-knowledge-ansible/ansible-wifi/issues/` folder per this policy once collection finishes, rather than leaving raw per-host evidence inside the skill-smc pack long-term. The *analysis*
(conclusions, confirmed/refuted claims, new findings) belongs in `references/*.md`; the raw capture files do not.
````

## File: AGENTS.md
````markdown
@../../../AGENTS.md

Title: skill-smc Agent Policy
Category: agent-governance-guide
Status: current
Authority: local-supplement
Scope: skill-smc specialist pack — canonical source for SMC box operational knowledge and ansible-wifi authoring
Last reviewed: 20260731_1300
Summary: Agent guidance for maintaining and using the skill-smc specialist pack. Covers specialist structure, reference routing, and update discipline. Cross-repo trigger rule broadened 2026-07-31 to cover the whole local-knowledge-ansible/ansible-wifi tree (current and future subfolders) and both skill-slurp-chat and project-coherence as mandatory feed-back trigger points.

# AGENTS.md

## Working rules

- `SKILL.md` is the agent-facing activation surface — it defines triggers, inline quick-reference, and pointers to `references/`.
- `RUNBOOK.md` is the navigation index — it maps task types to specific numbered reference files. Do not use it as a content source.
- `references/01_` through `references/13_` are the content source files. Load only the one needed for the task.
- `manifest.json` is the machine-readable specialist metadata. Update `version` and `updated_at` when any content file changes.
- `PROFILE.md` is canonical context not installed to clients. Content is summarised in `SKILL.md` and `references/01_overview.md`.
- `SYSTEM_PROMPT.md` is for dedicated agent deployments only — not loaded in normal skill invocations.
- `exports/claude_code/` contains the Claude Code adapter and install docs. Update these when the installed structure changes.
- After editing any `references/` file, check `SKILL.md` References section and `RUNBOOK.md` routing table for consistency.
- After adding a new reference file, update the `RUNBOOK.md` routing table, `SKILL.md` References section, `adapter.md` source mapping, and `install.md` copy steps in the same pass.
- Follow naming convention for time-bound docs: `<slug>-YYYYMMDD_hhmm.md`.
- Keep `CHANGELOG.md` current — append entries when content or structure changes.

## Project-coherence checklist

When running `project-coherence` on the `skill-smc` specialist pack — whether triggered directly or from an ansible-wifi session — apply this tier order:

### Tier 1 — Reference files (content source — update first)

| New knowledge type | Target file |
|---|---|
| Captive portal, Kohana, Eclipse config, portal PHP (mod_php, not PHP-FPM) | `references/10_captive-portal.md` |
| Vagrant lab bring-up, VirtualBox, vsmc nuances | `references/11_vagrant-lab.md` |
| VLAN 501, content filtering, MAC randomization, CAKE | `references/12_content-filtering.md` |
| New coverage gaps, staleness risk, unvalidated assumptions | `references/13_known-issues.md` |
| URL capture, PCAP, dns_query | `references/09_url-capture-pcap.md` |
| Ansible authoring, topology, cache, blast radius | `references/08_ansible-authoring.md` |
| All other domains → per routing table in `RUNBOOK.md` | matching `references/0N_*.md` |

**Do not write new operational content to `RUNBOOK.md`** — it is a navigation index only. Write content to the matching reference file.

### Tier 2 — Routing and navigation (check for staleness after Tier 1)

- `RUNBOOK.md` routing table — new reference file or renamed file → add/update routing row
- `SKILL.md` References section — pointer to the new/updated file
- `AI_NAVIGATION.md` routing table and Project context files table — new file → add row
- `context-map.yaml` routing section — new domain → add routing entry

### Tier 3 — Metadata and history

- `manifest.json` — bump `version` (patch) + `updated_at` if any reference file content or structure changed
- `CHANGELOG.md` — append entry for what changed (references updated, routing added, version bump)
- `SCRATCHPAD.md` — update current state, tick/add open items, prepend session history summary

### Tier 4 — Generated context (do last)

Regenerate `.ai-context/governance-pack.md`:
```
repomix --config /Volumes/Data/_ai/_skills/skills_stuff/specialists/project/skill-smc/repomix.config.json
```

### Cross-repo trigger rule (when triggered from ansible-wifi or local-knowledge-ansible/ansible-wifi)

**Scope: the whole tree, not just top-level sessions.** This rule fires for work done in
`/Volumes/Data/_ansible/ansible-wifi` itself, in `/Volumes/Data/_ansible/local-knowledge-ansible/ansible-wifi`,
and in **any current or future subfolder of either** — `issues/**`, `ai-tooling/`, `opa/`, `plans/`,
`scripts/`, `history/`, and any new investigation/design workspace bootstrapped later. Every such
subfolder is expected to `@`-import `ansible-wifi-root-governance/AGENTS.md` (the established
convention — see e.g. `issues/apn/routing-issue/AGENTS.md`), which is what makes this rule reach
new folders automatically without a separate wiring step per folder.

**Trigger conditions — broader than "bug fixes".** Any of the following, from any session anywhere
in that tree, counts as producing knowledge this pack must capture:
- An incident, debug fix, or change in assumptions (the original narrow case).
- A design analysis or recommendation — **even if not yet implemented or canary-tested.** Do not
  wait for something to ship before capturing it; mark it clearly as a design recommendation with
  its implementation status, so a future session doesn't have to rediscover it from a dated
  investigation-folder doc.
- A new or updated ADR, rule, guide, or spec under `.archcore/`.
- A change to the OPA policy layer (`opa/policies/`, `opa/data/`) or its precedence/gating logic.
- A reusable script worth generalizing for future investigations (promote to `skill-smc/scripts/`
  per its own promotion checklist in `scripts/README.md`).
- A ROADMAP-tracked architectural decision or backlog item that changes what this pack currently
  documents as true.

**Trigger points — both are mandatory, not just one.** Both `skill-slurp-chat` and
`project-coherence`, run anywhere in the tree above, must check for unpromoted knowledge before
closing out — not only project-coherence. If either closes a session without this check, treat the
closeout as incomplete.

**Steps once new knowledge is identified:**
1. Write content to the matching `references/*.md` in this pack (use `RUNBOOK.md`'s routing table
   to find the file — never write content to `RUNBOOK.md` itself).
2. Verify the RUNBOOK.md routing table has a row pointing to that reference.
3. Bump `manifest.json` version + `updated_at`.
4. Append CHANGELOG.md entry.
5. Update SCRATCHPAD.md current state.
6. Regenerate `.ai-context/governance-pack.md` (Tier 4, above).

**Closeout self-check (this is what prevents needing another full directory sweep):** before
ending any `skill-slurp-chat` or `project-coherence` pass that touched this tree, explicitly ask —
did this session create or change anything under `local-knowledge-ansible/ansible-wifi/**` (a new
issue report, design doc, ADR, script, ROADMAP edit, `.remember` entry) that isn't yet reflected
here? If yes, promote it in the same pass per the steps above rather than deferring it.

<!-- BEGIN skill-ai-it:navigation -->

## AI navigation and context preflight

Before answering, planning, editing, or creating files in this project:

1. **Check `.ai-context/governance-pack.md`** — if it exists and is current (< 7 days), read it as the primary context load. If stale or missing, regenerate: `repomix --config repomix.config.json`.
2. If pack unavailable, read individually:
   - [AI_NAVIGATION.md](AI_NAVIGATION.md) — context router
   - [context-map.yaml](context-map.yaml) — machine-readable routing map
   - [SKILL.md](SKILL.md) — agent-facing skill definition
   - [RUNBOOK.md](RUNBOOK.md) — reference routing index
   - Recent entries in [CHANGELOG.md](CHANGELOG.md)
3. Then load the specific `references/*.md` file relevant to the task.
4. If sources conflict, stop and report the conflict instead of guessing.
5. Do not treat `SCRATCHPAD.md` as durable truth unless content is marked `KEEP`.

<!-- END skill-ai-it:navigation -->

## Canonical governance linkage

- Parent guidance: [../../../AGENTS.md](../../../AGENTS.md)
- Cross-repo governance root: [/Volumes/Data/_ai/governance/README.md](/Volumes/Data/_ai/governance/README.md)
````

## File: AI_NAVIGATION.md
````markdown
# AI Navigation — skill-smc

Purpose: context entrypoint for AI agents working on the skill-smc specialist pack. Tells agents where knowledge lives, what to read first, what is authoritative, and what to update after work.

This file is a router, not the knowledge store.

<!-- BEGIN skill-ai-it:navigation -->

## Mandatory read order

Before answering, planning, editing, or creating files:

1. **Check `.ai-context/governance-pack.md`** — if current (< 7 days), read as primary context load. Regenerate if stale: `repomix --config repomix.config.json`.
2. If pack unavailable, read:
   - `AGENTS.md`
   - `SKILL.md` — activation surface and quick-reference
   - `RUNBOOK.md` — navigation index for references
   - `CHANGELOG.md` — recent changes
3. Then load the specific `references/*.md` file relevant to the task.

## Source priority

When sources conflict:

1. `manifest.json` — machine-readable specialist metadata (version, scope, stable facts)
2. `SKILL.md` — agent-facing activation surface and inline quick-reference
3. `RUNBOOK.md` — navigation index
4. `references/<nn>_*.md` — numbered content source files
5. `PROFILE.md` — background context (not installed to clients)
6. `CHANGELOG.md` — history
7. `SCRATCHPAD.md` — temporary only

## Reference routing (task → file)

| Task | Read |
|---|---|
| Live incident: box unreachable, service down, alert firing | `references/05_troubleshooting.md` |
| Identify which services are present / service names / config paths | `references/02_service-map.md` |
| Understand external comms paths (Teleport, Prometheus, Graylog) | `references/03_communication-flows.md` |
| Understand dependencies between services | `references/04_dependency-tree.md` |
| Identify known failure signatures and fix patterns | `references/06_failure-modes.md` |
| Hardware differences, overlayroot, persistence risk | `references/07_hardware-overlay.md` |
| Ansible authoring: topology vars, cache, validation, blast radius, smc_ltp sub-group, "low touch" onboarding history | `references/08_ansible-authoring.md` |
| URL capture v2, PCAP layout, fetch/process, dns_query assumptions | `references/09_url-capture-pcap.md` |
| Captive portal, Kohana, Eclipse config sync, portal PHP (mod_php, not PHP-FPM) | `references/10_captive-portal.md` |
| Vagrant lab bring-up and virtualization issues | `references/11_vagrant-lab.md` |
| VLAN 501, content filtering, MAC randomization, CAKE | `references/12_content-filtering.md` |
| Coverage gaps, staleness risk, unvalidated assumptions | `references/13_known-issues.md` |
| SMC box definition, inventory flavors, Teleport access pattern, APN vs NBN Accelerate cluster differences | `references/01_overview.md` |

## Project context files

| File | Role | Authority |
|---|---|---|
| `AGENTS.md` | Agent instructions for maintaining this pack | High |
| `CLAUDE.md` | Claude Code bootstrap (thin wrapper) | High |
| `AI_NAVIGATION.md` | Human-readable context router (this file) | High |
| `context-map.yaml` | Machine-readable routing map | High |
| `SKILL.md` | Agent-facing activation surface | High |
| `RUNBOOK.md` | Navigation index — task-to-reference routing | High |
| `manifest.json` | Specialist metadata, scope, stable facts | High |
| `PROFILE.md` | Background context; not installed to clients | Medium |
| `SYSTEM_PROMPT.md` | Dedicated agent mode prompt; not loaded in normal invocations | Medium |
| `references/01_overview.md` | SMC box definition, flavors, access, APN vs NBN Accelerate differences | Content |
| `references/02_service-map.md` | 50+ services, units, config paths | Content |
| `references/03_communication-flows.md` | Inbound/outbound paths | Content |
| `references/04_dependency-tree.md` | Service dependency relationships | Content |
| `references/05_troubleshooting.md` | Live incident triage (Tiers 1–7) | Content |
| `references/06_failure-modes.md` | Failure signatures and fix patterns | Content |
| `references/07_hardware-overlay.md` | Hardware diff, overlayroot, persistence | Content |
| `references/08_ansible-authoring.md` | Ansible rules, validation, generator drift, smc_ltp, onboarding history | Content |
| `references/09_url-capture-pcap.md` | URL capture v2, PCAP, dns_query | Content |
| `references/10_captive-portal.md` | Captive portal, Kohana, portal PHP (mod_php) | Content |
| `references/11_vagrant-lab.md` | Vagrant lab setup | Content |
| `references/12_content-filtering.md` | VLAN 501 filtering stack | Content |
| `references/13_known-issues.md` | Known gaps and staleness | Content |
| `exports/claude_code/project/skill-smc/adapter.md` | Claude Code source→install mapping | Adapter |
| `exports/claude_code/project/skill-smc/install.md` | Claude Code installation steps | Adapter |
| `CHANGELOG.md` | Pack version history and governance changes | Medium-high |
| `SCRATCHPAD.md` | Temporary working notes | Low |
| `.ai-context/governance-pack.md` | Generated context bundle | Generated |

## Update rules

| Change type | Update |
|---|---|
| New operational knowledge | Add/update `references/<nn>_*.md`; update `RUNBOOK.md` routing; check `SKILL.md` |
| New reference file | Update `RUNBOOK.md` routing table + `SKILL.md` References + `adapter.md` + `install.md` |
| Structural change | Bump `manifest.json` version + `updated_at`; append `CHANGELOG.md` |
| Scope boundary change | Update `manifest.json` `scope_boundary`; review `SKILL.md` Use When |
| Stable fact confirmed/changed | Update `manifest.json` `stable_facts`; update relevant reference |
| Context routing changed | Update `AI_NAVIGATION.md` and `context-map.yaml` |
| Governance change | Append `CHANGELOG.md` |

## Drift handling

If files disagree:

1. Stop.
2. Name the conflicting files.
3. State which has higher authority per source priority above.
4. Propose the smallest correction.
5. Do not silently merge.

<!-- END skill-ai-it:navigation -->
````

## File: ARCHITECTURE.md
````markdown
# Architecture — skill-smc

## Overview

skill-smc is a multi-file specialist pack following the canonical `specialists/project/` pattern. It separates an agent-facing activation surface (SKILL.md) from a progressive-disclosure reference layer (references/01–13) via a navigation index (RUNBOOK.md). Client adapter docs in `exports/` describe what gets installed and where. Durable pack rules, the structural ADR, and a file-roles spec live in `.archcore/`.

## Components

| Component | Role |
|---|---|
| `SKILL.md` | Agent activation surface: trigger conditions, inline quick-reference tables, and pointers to numbered references |
| `RUNBOOK.md` | Navigation index: 48-line table mapping task types to specific reference files. Not a content source. |
| `references/01_overview.md` – `references/13_known-issues.md` | Numbered progressive-disclosure content files. Each covers one domain. Loaded on demand. |
| `manifest.json` | Machine-readable specialist metadata: version, scope boundary, stable facts, known constraints |
| `PROFILE.md` | Background context (hardware, flavors, access pattern). Content summarised in SKILL.md and 01_overview.md. Not installed to clients. |
| `SYSTEM_PROMPT.md` | Dedicated agent mode prompt. Not loaded in normal skill invocations. |
| `exports/claude_code/` | Claude Code adapter: source→install mapping (`adapter.md`) and install steps (`install.md`) |
| `.archcore/` | Durable pack truth: 3 rules, 1 ADR, 1 spec |
| `AGENTS.md` | Pack maintenance policy for contributors |
| `AI_NAVIGATION.md` | Human-readable context router for agents working on the pack |
| `context-map.yaml` | Machine-readable routing map |
| `.ai-context/governance-pack.md` | Generated repomix bundle (~470k chars as of 2026-08-03, 35 files) — regenerable |

## Information flow

```
Agent invoked with SMC task
  └── reads SKILL.md (activation surface, inline quick-ref)
        └── reads RUNBOOK.md (navigation index, identifies relevant reference)
              └── reads references/<nn>_*.md (focused content for the task)
```

## Installed surface (Claude Code)

```
~/.claude/skills/skill-smc/
├── SKILL.md
├── RUNBOOK.md
└── references/
    ├── 01_overview.md
    ├── 02_service-map.md
    ├── ...
    └── 13_known-issues.md
```

Everything else (PROFILE.md, SYSTEM_PROMPT.md, manifest.json, exports/, .archcore/, governance files) stays in the canonical source at `skills_stuff/specialists/project/skill-smc/` and is not installed to clients.

## Key decisions

- **Progressive disclosure (ADR v0.1.2):** monolithic RUNBOOK.md split into 13 numbered references to reduce per-task token cost. See [.archcore/adr/adr-progressive-disclosure-structure.md](.archcore/adr/adr-progressive-disclosure-structure.md).
- **RUNBOOK.md as index only:** never holds content; is always a routing table. See [.archcore/rules/rule-progressive-disclosure-loading.md](.archcore/rules/rule-progressive-disclosure-loading.md).
- **PROFILE.md not installed:** content is summarised in SKILL.md and 01_overview.md to avoid a dangling reference in the client install surface.
- **manifest.json not installed:** consumed by skill tooling at build/validate time, not needed at agent runtime.

## Related workspaces

| Repo | Relationship |
|---|---|
| `/Volumes/Data/_ansible/ansible-wifi` | Production Ansible source governed by this skill |
| `/Volumes/Data/_ansible/ansible-malik` | Operator playbooks for SMC operations |
| `/Volumes/Data/_ai/_scripts/scripts_stuff/python/dns_query` | DNS reporting consuming SMC PCAP output |
| `/Volumes/Data/_ansible/local-knowledge-ansible/ansible-wifi` | Local-only SMC plans and investigation notes |
````

## File: CHANGELOG.md
````markdown
# skill-smc Changelog

## 20260803_1825 — new-looma-smc01 second whole-host outage confirmed via live Prometheus (v0.1.17 → v0.1.18)

Operator reported "new-looma-smc01 is back online." Rather than take the status at face value, queried `mcp-grafana-apn` (already live from the previous session's Grafana work) for `up{instance=~"new-looma.*"}` over the last 7 days.

**Confirmed:** both the self-scrape (`job="prometheus"`) and `node_exporter` targets for `new-looma-smc01` went dark simultaneously from **2026-08-01 23:40 UTC to 2026-08-03 06:40 UTC (31h)**, then both resumed together — the signature of a whole-host/network outage, not a single failed service. A second, earlier 18h gap in the same window (2026-07-29 11:10 → 2026-07-30 05:10 UTC) lines up exactly with the already-documented topology cross-wiring fix (`08_ansible-authoring.md`), confirming that gap is already explained. This newer 31h gap is not — no `tsh ssh` access was used this session, so root cause is confirmed-timeline-only, not diagnosed.

### Changed

- `references/13_known-issues.md` — new paragraph appended to the existing "new-looma-smc01" section documenting the confirmed 31h outage, its whole-host signature, cross-reference to the already-explained earlier gap, and an open question about whether it relates to the still-open `my_node_network_device_info` zero-series gap (also new-looma-specific).
- `manifest.json` — new `diagnostics` entry (6th); version bumped 0.1.17 → 0.1.18.

### Evidence basis

Live `mcp-grafana-apn` `query_prometheus` reads this session (`up{instance=~"new-looma.*"}`, instant + 7-day range). Timestamps converted via direct `date -u -r <epoch>` — not estimated. No SSH/tsh access to the box itself this session.

## 20260803_1810 — Grafana CW exploration unblocked: dashboard inventory + RISE metric names (v0.1.16 → v0.1.17)

Operator supplied the missing NBN-instance service-account token and confirmed a session restart had happened, unblocking the `mcp-grafana-nbn` connection left stuck at the end of the previous session (blank-token 401, MCP process caching old env). Explored both flavor-specific Grafana instances rather than just confirming connectivity.

**Confirmed:** `mcp-grafana-apn` (20 dashboards) and `mcp-grafana-nbn` (9 dashboards) are not mirrors. The 11 APN-only dashboards include a RISE health/watchdog framework (RISE SMC Health Detail, RISE SMC Table, RISE Dashboard) that has no NBN counterpart because RISE is deployed only to `rct`/`wh` flavors — confirmed via the `flavor=~"rct|wh"` gate in the "Pending sites" panel query, not just dashboard absence. Pulled the actual Prometheus metric names behind the four `rise_*` textfile collectors that previously had `—` placeholders in `02_service-map.md` (`rise_healthcheck_health_score_*`, `rise_healthcheck_health_penalty*`, `rise_overlay_used_pct`/`_inodes_free_pct`/`_active`, `rise_zram_*`, `rise_watchdog_up`/`_active`/`_boot_firmware_used_pct`/`_unit_active`), plus the offline-vs-pending fleet-rollup logic (offline = watchdog seen in last 30d but not last 5m; pending = node_exporter up on rct/wh but watchdog series never existed).

### Changed

- `references/03_communication-flows.md` — new "Dashboard inventory" subsection under Grafana/Prometheus MCP Access: full table of the 11 APN-only dashboards with UIDs and purpose, plus the RISE-flavor-gate explanation for why they're absent from the NBN instance.
- `references/02_service-map.md` — Monitoring/Metrics textfile-collector table rows for the four `rise_*` scripts now note their systemd unit/flavor gate; new "RISE Health/Watchdog Framework" subsection with the full metric table and the offline/pending distinction.
- `manifest.json` — new `diagnostics` entry (5th) capturing the dashboard-inventory and RISE-metric findings; version bumped 0.1.16 → 0.1.17.

### Evidence basis

Live `mcp-grafana-apn`/`mcp-grafana-nbn` reads this session: `search_dashboards` (both instances), `get_dashboard_summary` and `get_dashboard_panel_queries` (RISE SMC Health Detail, RISE SMC Table, Sites not reporting, SMC Table, Data Backlog, RPi SD Card Status). RPi hardware detail cross-checked against already-confirmed `07_hardware-overlay.md` content — no new hardware facts, dashboard is a visualization of already-documented state.

## 20260803_1745 — ClamAV freshclam root cause confirmed: ClamAV 0.103.x end-of-life (v0.1.15 → v0.1.16)

Operator asked "what could be the reason for the ClamAV error" following the fleet sweep in the previous entry. Rather than restate the open hypotheses, verified via `WebSearch` against clamav.net and the Cisco-Talos/clamav GitHub issue tracker before answering.

**Confirmed root cause**: ClamAV's 0.103 branch reached end-of-life for database updates on 2025-09-14. This fleet runs `clamav 0.103.11`/`.12` uniformly, squarely in the EOL'd branch — after the cutoff, ClamAV's CDN actively rejects `freshclam` from any 0.103.x client with HTTP 403 ("Forbidden; Blocked by CDN"), exactly the signature captured on all 26 hosts. This also explains the 10-month staggered failure-date spread from the previous entry: each host only flips to `failed` the first time its `freshclam` timer runs *after* the cutoff, so hosts with different timer schedules trip it at different times rather than all at once. Not a cw-cluster-specific network/firewall issue — this is documented, expected upstream behavior for any fleet still on 0.103.x. Fix is a version upgrade (1.0 or 1.4 LTS), not a retry; no automated ClamAV-version-update pipeline exists for this cluster to do that automatically.

### Changed

- `references/13_known-issues.md` — ClamAV bug row rewritten from "root cause not investigated, 3 open hypotheses" to "root cause confirmed," with the EOL date, the CDN-block mechanism, and the staggered-date explanation; "Fix location" column updated from "not investigated" to the concrete upgrade path.
- `references/08_ansible-authoring.md`, `references/01_overview.md` — ClamAV/Lynis rows updated to reference the confirmed root cause instead of open hypotheses.
- `manifest.json` — new `diagnostics` entry (3rd) capturing the confirmed root cause with its sources; version bumped 0.1.15 → 0.1.16.

### Evidence basis

`WebSearch` against `blog.clamav.net` (the official EOL announcement) and `github.com/Cisco-Talos/clamav` issue tracker (multiple community reports of the identical error signature) — external, citable sources, not inferred from this fleet's data alone. Cross-checked against this session's own captured data (uniform 0.103.x package version, exit code 17, exact error text match) for internal consistency.

## 20260803_1730 — Full NBN Accelerate fleet sweep: 28 hosts, hardware inventory, fleet-wide ClamAV finding (v0.1.14 → v0.1.15)

Operator requested a thorough analysis of "all the NBN Accelerate sites" including hardware details and the state of installed apps/scripts/services — a full fleet sweep, not a spot-check, superseding the 2-host check in the previous entry. Built two new reusable tools (`scripts/collect-fleet-health.sh`, `scripts/fleet-health.justfile`) and ran them against all 26 reachable `nbn_accelerate` hosts plus both `nbn_wh` hosts (28 total).

**Hardware inventory (new — no prior live chassis data existed for this cluster):** 11× AAEON BOXER-6641 (i5-8500T, 15Gi RAM, Transcend SSD) + 15× AAEON BOXER-6404 (Celeron J1900, 7.7Gi RAM, Innodisk CFast) for `nbn_accelerate`; both `nbn_wh` hosts are genuine Raspberry Pi-class (Cortex-A72, Swissbit microSD) — operator confirmed `nbn_wh` is the `wh`-flavor equivalent on this cluster.

**Major finding: `clamav-freshclam` confirmed failed fleet-wide, 26/26 `nbn_accelerate` hosts** (not the 2 found in the earlier spot-check) — same CDN-blocked exit-17 signature on every host, but failure *dates* span 10 continuous months (2025-10-02 → 2026-07-30), indicating an ongoing degradation still actively catching hosts, not a single past incident.

**Resolved during write-up (operator-confirmed mid-session):** `nbn_wh` overlayroot is not yet active on either host — this is a planned-but-not-yet-executed rollout (`smc_rise_deploy.yml` already targets `nbn_wh`), not a bug or stalled deployment.

**Other findings:** kernel-version drift (5.15.0-79 to 5.15.0-133) corroborating the earlier no-automated-kernel-pipeline structural finding; `koonibba-smc01` at 95% disk usage with the fleet's oldest kernel; `isc-dhcp-server6` failed on 28/28 hosts (confirmed benign — IPv6 disabled by policy); `fwupd-refresh` failed on 3/28 hosts (minor); `nbn_wh` swap/zram absence contradicting the platform table's universal RPi-zram claim (unresolved).

### Added

- `scripts/collect-fleet-health.sh` — new reusable, flavor-agnostic hardware/security/service-health evidence-capture script (read-only, hardcoded command bundles, same safety contract as `collect-smc-evidence.sh`). Bundles ~20 commands into 4 grouped captures per host to stay tractable over satellite links at fleet scale.
- `scripts/fleet-health.justfile` — task-runner wrapping the script, ships with the current NBN Accelerate site list plus `freshclam-check`/`failed-units-check`/`chassis-models` quick-check recipes. Dogfooded after writing — found and fixed 2 real bugs (a `just`-working-directory path assumption, and the same exit-code-of-last-command quirk documented in the collection script) before trusting it.
- `scripts/README.md` — new safety-classification rows, "What each script is for" section, and a documented lesson on `just -f <path>`'s working-directory behavior.
- `references/07_hardware-overlay.md` — new "NBN Accelerate / NBN WH Hardware Inventory" section with the full chassis/CPU/RAM/storage/kernel table and all findings above.
- `references/13_known-issues.md` — "Known Operational Bugs (NBN Accelerate cluster)" section rewritten for the full 28-host sweep (was 2-host); coverage-gap row updated to "largely closed."
- `references/01_overview.md`, `references/08_ansible-authoring.md` — evidence-basis and flavor-gate rows updated to reflect full-fleet validation.
- `references/04_dependency-tree.md` — separately, added `smc_ltp`/ClamAV/Lynis Level-4 entries and flagged a naming-collision risk between `smc_ltp`'s CNMaestro provisioning and a pre-existing generic `cnmaestro-provisioning`/`redis` dependency row (unresolved — may be the same mechanism described two ways, or two genuinely separate paths).
- `manifest.json` — new `diagnostics` entry for the full sweep; version bumped 0.1.14 → 0.1.15.

### Operational note

Raw per-host evidence relocated from `skill-smc/evidence/` to `local-knowledge-ansible/ansible-wifi/issues/nbn-accelerate/fleet-hardware-audit-20260803/` per this pack's evidence-retention policy — skill-smc holds analysis and tooling, not case-specific raw captures.

### Evidence basis

Direct `tsh ssh root@<host>` read-only commands, this session, 28/28 targeted hosts. Two-batch capture: batch 1 crashed at 11/28 hosts after a same-session edit to the running script file corrupted its execution (a documented gotcha now — never edit a script file while it's still running); batch 2 recaptured the remainder with the fixed script. Not covered: `cw` flavor (central-infra only), `aurukun-smc03` (unreachable at capture time).

## 20260803_1615 — First live NBN Accelerate validation: confirms cluster comparison, finds ClamAV CDN-block (v0.1.13 → v0.1.14)

Operator made `tsh login` available for the NBN Accelerate cluster (`teleport.communitywifi.net.au`) and invited exploratory commands — the first-ever live access this pack has had to that cluster, closing (partially) the "code-inspection-only" caveat that's sat on every NBN Accelerate claim since the gap-fill earlier today. Ran read-only diagnostic commands against two `nbn_accelerate` hosts, `warakurna-smc01` and `indulkana-smc01`.

**Every prior code-inspection-only claim checked came back confirmed, 2/2 hosts:** Teleport domain (`teleport.communitywifi.net.au:443`), HTTPS-only portal (permanent HTTP→HTTPS redirect, on-box TLS termination at `/etc/ssl/communitywifi.net.au/`), `wifi-community-app-backend` present, ClamAV + Lynis both installed, Asterisk absent, DNS stack is standard unbound+stubby (not `smc_ltp`/bind9, as expected — neither host is an `smc_ltp` member).

**New finding, not previously known:** `clamav-freshclam.service` has been failing on both hosts — `warakurna-smc01` since 2026-07-23, `indulkana-smc01` since 2026-06-21 — identical signature (exit code 17, `Forbidden; Blocked by CDN`, freshclam gives up permanently rather than retrying). ClamAV's virus database is stale/frozen on both; the daemon itself stays active but with degraded detection. Root cause not investigated (read-only session, no remediation attempted).

### Added / Changed

- `references/13_known-issues.md` — new "Known Operational Bugs (NBN Accelerate cluster — first live check, 2026-08-03)" section with the confirmed-claims summary and the ClamAV/freshclam bug row; "NBN Accelerate cluster coverage gap" row updated from "not live-validated" to "first live spot-check done."
- `references/08_ansible-authoring.md` — ClamAV+Lynis gate row updated with the live-confirmed install + the freshclam finding.
- `references/01_overview.md` — evidence-basis paragraph updated: partially live-validated as of 2026-08-03; `nbn_wh`/`cw` flavors still unvalidated.
- `manifest.json` — new `diagnostics` entry (first use of this previously-empty field) capturing the live-validation results and the ClamAV finding; version bumped 0.1.13 → 0.1.14.

### Evidence basis

Direct `tsh ssh root@<host>` read-only commands against `warakurna-smc01` and `indulkana-smc01`, this session. No writes/remediation performed. `nbn_wh` and `cw` flavors, and every other NBN Accelerate site, remain unvalidated — this is a 2-host spot-check, not a fleet sweep.

## 20260803_1545 — project-coherence sweep: routing/architecture staleness fixed (v0.1.12 → v0.1.13)

`project-coherence` run covering today's cumulative changes (NBN Accelerate gap-fill through the smc_ltp manual-mechanism confirmation). Content files (Tier 1) were already coherent — this pass caught two Tier 2/routing staleness items that hadn't been touched during the piecemeal content edits:

### Changed

- `context-map.yaml` — `ansible_authoring` and `smcbox_basics` routing descriptions extended to mention `smc_ltp`/"low touch" onboarding and the APN-vs-NBN-Accelerate comparison respectively; previously only the underlying reference files had been updated, not this machine-readable routing layer.
- `ARCHITECTURE.md` — governance-pack size figure corrected from a stale "~125k chars" (last accurate 2026-06-26) to the current ~470k chars / 35 files — had drifted across multiple sessions' worth of content growth, not just today's.
- `RUNBOOK.md`, `AI_NAVIGATION.md` — `08_ansible-authoring.md` routing rows extended to mention `smc_ltp` and onboarding history, matching the pattern already applied to the `01_overview.md` row for NBN Accelerate.

### Validated

Stale-reference grep across the whole pack for old figures/phrases ("cnMaestro mDNS", "only rcp/guda-guda", "Community WiFi cluster", "~125k chars") — all remaining hits are correctly-framed historical/correction narrative in `CHANGELOG.md`/`SCRATCHPAD.md`/the "corrected 2026-08-03" notes, no live incorrect claims found. `README.md`, `SYSTEM_PROMPT.md` reviewed — generic pointers, no stale figures. `.remember/today-2026-08-03.md` reviewed — out of scope for this pack's own coherence pass (self-managed by the global `remember` skill, not a skill-smc-authored file).

Version bumped 0.1.12 → 0.1.13; governance pack regenerated.

## 20260803_1530 — smc_ltp/"low touch" mechanism confirmed: manual step, no enforcement (v0.1.11 → v0.1.12)

Final piece of the smc_ltp/"low touch" thread, same day: operator confirmed the one remaining open question — whether low-touch onboarding tooling itself assigns `smc_ltp` group membership, or it's a manual step. **It's manual.** No tooling automatically adds a new low-touch site to `smc_ltp:children`, and nothing checks or enforces that it happened. This directly explains the root cause of the 3-site gap fixed in the previous entry — a manual, unenforced step is exactly the kind of thing that silently drops during a busy onboarding.

### Changed

- `references/08_ansible-authoring.md` — "smc_ltp Sub-Group" low-touch resolution paragraph updated with the confirmed mechanism and an explicit operational implication: verify `smc_ltp:children` membership explicitly for any future low-touch site rather than assuming it's automatic.
- `references/13_known-issues.md` — the "low touch ↔ `smc_ltp` link" row's status upgraded to include "mechanism confirmed manual"; reframed as a standing risk for future low-touch sites, not a one-off closed by this correction.
- `manifest.json` — `smc_ltp`/low-touch `stable_facts` entry updated with the confirmed mechanism; confidence raised to 0.92; version bumped 0.1.11 → 0.1.12.

### Evidence basis

Operator-confirmed directly, relayed to this session. No independent verification possible from Ansible source alone (absence of automation is what's being confirmed, not a positive code finding).

## 20260803_1515 — smc_ltp/"low touch" correlation resolved: 3 sites added to the group, 7 members confirmed (v0.1.10 → v0.1.11)

Follow-up to the "low touch" onboarding entry below, same day. That entry flagged, but did not conclude, whether "low touch" onboarding and `smc_ltp` membership were mechanistically linked (4 of 7 low-touch sites were `smc_ltp` members; 3 — `umoona`/`warburton`/`beagle-bay` — were not). Operator confirmed the link is real: every low-touch site is meant to be an `smc_ltp` member, and the 3 missing ones were a plain inventory gap, not a coincidental overlap of two unrelated rollout decisions.

Operator made and verified the fix directly in `ansible-wifi`: added `warburton_smc_ltp`/`beagle-bay_smc_ltp`/`umoona_smc_ltp` host groups to `inventories/rcp/prod`, plus each site's own `:children` block, matching the existing pattern for the other 4 sites. Verified via `ansible-inventory --list` (all 7 now under `smc_ltp:children`) and `ansible-playbook --syntax-check smc_ltp.yml` (clean). **Uncommitted** — a real production Ansible inventory change, not yet run against any live SMC.

### Changed

- `references/08_ansible-authoring.md` — "smc_ltp Sub-Group" section updated: membership is now 7 sites, not 4; the site/date table's `smc_ltp member?` column updated; the low-touch section's "flagged, not concluded" framing replaced with "Resolved 2026-08-03 (link confirmed, not coincidental)" and the fix/verification steps documented. The underlying *mechanism* (does low-touch tooling itself assign `smc_ltp` membership, or is it manual) remains unestablished — only the intended end-state membership is now confirmed.
- `references/02_service-map.md`, `references/13_known-issues.md` — DNS resolver row and coverage-gap row updated to 7 sites and "resolved" status.
- `references/01_overview.md`, `SKILL.md`, `references/05_troubleshooting.md` — quick-reference/table mentions of `smc_ltp` membership updated from 4 to 7 sites.
- `manifest.json` — both `smc_ltp`-related `stable_facts` entries updated to reflect 7 members and the resolved correlation; version bumped 0.1.10 → 0.1.11.

### Evidence basis

Operator-directed and operator-verified (`ansible-inventory --list`, `ansible-playbook --syntax-check`) file-level change relayed to this session; not independently re-verified by this session, and not yet run against any live SMC or committed to the ansible-wifi repo.

## 20260803_1445 — "Low touch" onboarding method and site deployment history added (v0.1.9 → v0.1.10)

Operator supplied install dates for a cohort of `rcp` sites, confirming a named **"low touch" onboarding method**: `guda-guda` (pilot, 2025-04-15), then a year later `umoona` (2026-04-12), `warburton`, `beagle-bay`, `pandanus-park`, `old-looma`, `new-looma`. Genuinely new information not previously documented anywhere in this pack.

### Added

- `references/08_ansible-authoring.md` — new "'Low Touch' Onboarding Method and Site Deployment History" section (added to Contents list): the full site/date/`smc_ltp`-membership table; the flagged-not-concluded observation that all 4 `smc_ltp` sites are also low-touch sites (3 of 4 `smc_ltp` non-pilot members plus the pilot itself), while `umoona`/`warburton`/`beagle-bay` are low-touch without `smc_ltp`; and a direct-grep finding that "low touch" currently has no Ansible-code representation — the one `low_touch`-named var in the repo (`smc_bases_low_touch_provisioning` on `pierre-rcp01`, not a cohort member) is set but never read by any role or playbook.
- `references/13_known-issues.md` — new open-question row capturing the unresolved `smc_ltp`/low-touch correlation; updated the pre-existing "cnmaestro-provisioning internals" coverage-gap row to reflect that the deployment side is now well-documented (only the CNMaestro API's own runtime behavior remains unknown).
- `manifest.json` — new `stable_facts` entry for the low-touch cohort/dates and the orphaned-var finding; version bumped 0.1.9 → 0.1.10.

### Evidence basis

Site list and dates are operator-provided, cross-referenced against independently-observed netplan/hook render timestamps already in this pack's routing-issue-derived content (consistent, not contradictory — renders land 1-92 days after each stated install date, matching later unrelated remediation work touching those files). The `smc_ltp` overlap and the orphaned `smc_bases_low_touch_provisioning` var are this session's own repo-wide grep findings. Not live-validated against any site.

## 20260803_1400 — smc_ltp properly explored and documented; membership undercount fixed (v0.1.8 → v0.1.9)

Operator flagged that `smc_ltp` "has not been explored and documented properly" — a fair call. Prior coverage was a side effect of the 2026-07-03 DNS RCA (which only established that `smc_ltp` gates the unbound-vs-bind DNS split) and had never been independently re-verified since. Direct read of `smc_ltp.yml`, `inventories/rcp/group_vars/smc_ltp.yml`, `inventories/rcp/prod`, `roles/smc_cnmaestro_provisioning/`, and `roles/smc_dns_mgmt/tasks/main.yml` (this session, cross-checked against a parallel same-day pass done from the ansible-wifi side, which reached the same conclusions independently) found two things wrong with the prior documentation:

1. **Membership undercount.** Every prior mention said "currently only `rcp`/guda-guda". That was based on a `.yml`-scoped grep that missed `inventories/rcp/prod` — an INI-format static inventory file, not a `topology_vars`-generated one. The group actually has 4 members: `guda-guda`, `pandanus-park`, `old-looma`, `new-looma`.
2. **Purpose mislabeled.** Prior docs called it "cnMaestro mDNS" — wrong on both halves. It has two unrelated purposes, neither of which is mDNS: (1) a separate `smc_ltp.yml` playbook runs CNMaestro-managed Cambium ePMP/cnPilot wireless-backhaul provisioning (auto-allocates management IPs, SSIDs, per-model config for cnPilot/XV2/ePMP Force/ePMP 3000L hardware); (2) `smc_bases.yml`'s `dns_mgmt` play switches the DNS resolver stack from unbound+stubby to bind9+RPZ (zone file literally named `db.cambium-rpz`, tying the DNS switch to the same Cambium backhaul context).

### Added / Fixed

- `references/08_ansible-authoring.md` — new "smc_ltp Sub-Group — CNMaestro Backhaul Provisioning + DNS Architecture Switch" section: membership mechanism (static INI group, not topology_vars), both purposes in full, the `smc_dhcpd` LTP-specific apparmor/service-user fix, and an explicit "LTP acronym not expanded anywhere in the codebase — do not guess" note. Added to the Contents list.
- `references/01_overview.md`, `references/02_service-map.md`, `references/13_known-issues.md` — corrected the "only `rcp`/guda-guda" undercount to the 4-site list and cross-referenced the new 08_ansible-authoring.md section instead of restating it.
- `SKILL.md` Tier 3 DNS quick-reference and `references/05_troubleshooting.md` Tier 3b/3c — same undercount fixed; Tier 3c now notes the CNMaestro-provisioning angle so a "DNS is fine but backhaul radios aren't provisioning" report on one of these 4 sites doesn't get misdiagnosed as a DNS issue.
- `manifest.json` — new `stable_facts` entry capturing the corrected membership, dual purpose, and the open "LTP acronym" question; version bumped 0.1.8 → 0.1.9.

### Evidence basis

Direct read of the playbook/role/inventory files listed above (this session). Not live-validated against any of the 4 member hosts via `tsh ssh` — the CNMaestro-provisioning and DNS-switch mechanisms are confirmed from Ansible source, not from a live box.

## 20260803_1230 — NBN Accelerate cluster gap-fill (v0.1.7 → v0.1.8)

Operator request: ~95% of this pack's operational detail was extracted from APN-cluster (`rcp`/`rct`/`wh`, `teleport.apn.au`) work; the NBN Accelerate cluster (`cw`/`nbn_accelerate`/`nbn_wh`,
`teleport.communitywifi.net.au`) had only the flavor→domain mapping documented (from the 2026-07-31 SSH/Teleport corrections). Ran a three-pronged research sweep (inventory group_vars diff across
all 7 flavors, repo-wide grep for flavor-conditional branching in roles/templates, doc/ADR/OPA search in local-knowledge-ansible/ansible-wifi) to fill the gap with a structured comparison rather
than assuming parity between the two clusters.

### Added

- `references/01_overview.md` — new "APN Cluster vs NBN Accelerate Cluster — Structural Comparison" section: both clusters share a 1-central-infra + N-site-fleet topology, but NBN Accelerate is
  materially thinner (no graylog/opensearch, no kernel-update Jenkins pipeline) and has real functional differences beyond the SSH endpoint (mobile-app backend + kiosk mode on `nbn_accelerate`
  only, HTTPS-only portal protocol, different blocked-URL redirect domain, ClamAV+Lynis hardening on `nbn_accelerate` only, VoIP/Asterisk on `rcp` only). Documents the selector mechanism
  (`hotspot_flavor` hardware-class split spans both clusters; `inventory_dir.split('/')|last` drives flavor-exclusive gates; nothing branches on the literal strings cw/community/communitywifi).
- `references/08_ansible-authoring.md` — new "Flavor/Cluster Conditional Branching (Selector Reference)" section: table of confirmed flavor-exclusive role gates (ClamAV/Lynis, VoIP/Asterisk,
  `smc_qos`, `smc_ltp`) with their exact conditions, plus the `smc_autossh` Teleport-endpoint selection mechanism (`teleport_fqdn` per-inventory group_var, host_var overrides for staging domains).
- `references/10_captive-portal.md` — new §11.9: `smc_bases_portal_protocol` (http vs https) and `smc_bases_blocked_url_redirect` differences between clusters, flagged explicitly as
  code-inspection-only (not live-validated against a cw-cluster host), with implications for §11.1–11.8's APN-cluster-derived verification commands.
- `references/13_known-issues.md` — new "NBN Accelerate cluster coverage gap" row (Knowledge Gaps table) stating the live-validation boundary explicitly; two new Skill Staleness Risks entries: a
  "community wifi" naming-collision warning (used generically for `rcp` sites in `issues/apn/routing-issue/`, distinct from the cw-flavor customer — a false-positive risk for future greps), and an
  OPA `flavors.json`/`environments.json` coverage note (no `cw`/`apn`/`rct`/`wh` entries — not established whether intentional).
- `RUNBOOK.md`, `SKILL.md`, `AI_NAVIGATION.md` — `01_overview.md` routing rows updated to mention the new APN vs NBN Accelerate comparison content.

### Evidence basis

Structural findings: direct read of all 7 inventories' `group_vars/*.yml` and `prod` files. Behavioral findings: repo-wide grep across `roles/*/tasks/main.yml`, `roles/*/templates/*.j2`,
`smc_bases.yml`. Doc/ADR/OPA findings: search of `local-knowledge-ansible/ansible-wifi/{.archcore,issues,opa,docs,.remember}`. None of this is live-validated against a running `nbn_accelerate`/
`nbn_wh`/`cw` host — flagged as such in every new section rather than presented as fleet-confirmed fact, consistent with this pack's existing evidence-labeling convention.

## 20260731_1312 — Fed back Pia Wadjari labeling case + proposed convention; multiwan-disable git archaeology

Operator worked in `local-knowledge-ansible/ansible-wifi/issues/internet-link-handling/` on internet-link topics (dual-switch bonding, label/metadata convention, manual ingress shaping, dormant
multi-WAN VRF/fwmark), initially without checking here first — that workspace's own governance now flags this happened and corrects the resulting mechanism mis-citations. Two genuinely new pieces
of information from that session, not previously here, fed back per operator request:

### Added

- `references/03_communication-flows.md` — under the existing label-inversion note: Pia Wadjari as a second confirmed instance (Starlink active/`internet` label, SkyMuster Plus backup/`starlink`
  label — inverse of Horn Island), agreed with the operator's colleague Sandro that deployment proceeds as scheduled, and the concrete retrofit proposal (role-based `active-internet`/
  `standby-internet` labels + `provider:`/`link_type:` metadata fields) with a rough 2-3 week timeline once agreed — the existing note only said a retrofit was "planned" with no detail on what it
  would look like.
- `references/03_communication-flows.md` — under the existing multiwan/VRF note: the specific disable commit (`c19a61fa`, apparent incidental collateral of an unrelated URL-capture refactor, not a
  deliberate decision) and an important nuance the existing note didn't have — the fwmark script being dead does not mean VRF is fully out of play; `netplan.yml.j2`'s per-WAN VRF *allocation* is
  still live and rendered into every deploy today, only the fwmark `ip rule`s that would use those tables are missing. Flagged as an open, not-yet-checked question whether any live SMC carries
  orphaned `vrf-<tableid>` devices as a result.

### Not added (already covered, verified during this pass)

- Topic 1 (dual-switch bonding design) — already fully promoted into `references/08_ansible-authoring.md`, correctly citing the source workspace's own analysis doc. No gap found.
- Topic 3 (manual ingress-shaping script) — already fully documented (`references/03_communication-flows.md`, `13_known-issues.md`), established 2026-07-29. The source workspace had independently
  rediscovered this and initially mis-described it as "unknown" — corrected there after this check, not here (nothing here was stale).
- The core label-inversion mechanism and the `dhclient-enter-hooks.j2` override itself — already accurate and complete here; it was the *source workspace's* citation of `ubuntu-dhclient-script.j2`
  that was wrong, not anything in this file.

## 20260731_1215 — Two residual gaps closed from the routing-issue Problem 3 deep-dive

Operator asked, from the routing-issue investigation folder, "was all the information in this project fed back to skill-smc?" — a spot-check after the 20260731_1245 full extraction pass (below,
despite the out-of-order stamp — see the note on CHANGELOG stamps not matching wall-clock order) and the earlier 20260729_2324 pass. Both were thorough; this check found the coverage was
otherwise complete, with two specific, narrow gaps in the Problem 3 (starlink `INPUT` DROP) deep-dive.

### Added

- `references/03_communication-flows.md` — the DHCP-bypasses-netfilter-`INPUT` mechanism: ISC `dhclient` uses a raw `AF_PACKET` socket for its own port-68 traffic, tapping frames at the link
  layer before/parallel to `NF_INET_LOCAL_IN`, for both the initial lease and later renewals — this is *why* the starlink DROP rule (already documented) never blocks DHCP, and generalizes to any
  interface-scoped DROP/REJECT rule on this fleet. Live-confirmed on Warburton.
- `references/13_known-issues.md` — new Known Site Issues row: warburton-smc01's unexplained 1.68M-packet/3.3GB starlink DROP-rule counter (live tcpdump ruled out self-generated traffic and
  public-internet exposure; source remains unresolved).

## 20260731_1330 — Broadened cross-repo feed-back governance (prevent future full-sweep need)

Follow-up to the 20260731_1245 extraction pass: the operator asked that ansible-wifi and
local-knowledge-ansible/ansible-wifi (current and future subfolders) always consult skill-smc and
always feed new knowledge back via `skill-slurp-chat`/`project-coherence`, so this kind of exhaustive
sweep never has to happen again.

### Changed

- `AGENTS.md` "Cross-repo trigger rule" — broadened scope from "when triggered from ansible-wifi"
  to explicitly cover the whole `local-knowledge-ansible/ansible-wifi` tree (current and future
  subfolders, via the existing `@`-import convention those subfolders already use). Broadened the
  trigger-condition list beyond "fixes, architecture decisions, failure modes" to explicitly include
  unimplemented design recommendations, ADRs/rules/specs, OPA policy changes, reusable scripts, and
  ROADMAP decisions. Named `skill-slurp-chat` as an equally mandatory trigger point alongside
  `project-coherence` (previously only the latter was named). Added a closeout self-check.

### Corresponding changes in ansible-wifi's own governance (not this pack, but the other half of the loop)

- `ansible-wifi-root-governance/AGENTS.md` (symlinked as `/Volumes/Data/_ansible/ansible-wifi/AGENTS.md` — a single edit covers both), `.archcore/rule-002`, `.agents/task-patterns.md`, and
  `.agents/validation.md` were broadened identically, and rule-002 was renamed to drop the
  "incident/debug fixes" framing that had been the actual root cause of the extraction-pass gaps.
  See that repo's own `CHANGELOG.md` entry `20260731_1330` for detail.

## 20260731_1245 — Full local-knowledge-ansible/ansible-wifi extraction pass

Operator asked for an exhaustive sweep of every markdown file under
`local-knowledge-ansible/ansible-wifi/` and subfolders to confirm nothing was missed. Covered
directly: `ai-tooling/`, `opa/`, `plans/`, `scripts/` (top-level lint scripts), `history/`,
`graphify-out/GRAPH_REPORT.md`, `issues/garimba-smc01/`, `issues/amata-smc01/`,
`issues/rcp-fleet/`, `issues/internet-link-handling/`, and the `ansible-wifi-root-governance/`
top-level docs (ROADMAP.md, CONVENTIONS.md, `.serena/memories/`). Delegated to subagents:
`ansible-wifi-root-governance/.archcore/` (6 ADRs, 5 rules, 1 guide, 2 specs) and
`issues/apn/routing-issue/docs/` (20 files) against current pack content; a third background sweep
covered `.remember/` daily logs for anything that fell through the ADR-promotion workflow.
`snapshots/` (59 timestamped dirs) and `history/current/` confirmed to be point-in-time copies of
the ansible-wifi repo's own AGENTS.md, not distinct knowledge — spot-checked via diff, not deep-read.

### Added

- `references/06_failure-modes.md` — amata-smc01 disk-path failure (ATA/COMRESET, `DID_BAD_TARGET`,
  forced read-only root) as a new failure-mode entry, flagged still-open per ROADMAP.md.
- `references/07_hardware-overlay.md` — `smc_disk_failover` role mechanism (EFI BootNext on
  connectivity failure, not storage-health failure; not guaranteed to run cleanly under active I/O
  corruption).
- `references/13_known-issues.md` — amata-smc01 open-incident row; `smc_qos` misgated to `rct`-only
  (silently no-ops on rcp/nbn_accelerate); Horn Island's unconditional `starlink01`/`starlink02`
  topology block; Pandanus Park chronic `interfacecheckv2.sh` restart loop; Old Looma `smc_iptables`
  ACL drift (Asterisk/MQTT/Cambium-TFTP rules missing); mercedes-cove null-property portal bug;
  duplicate `[horn-island_smc_bases]` inventory declaration; bungardi-smc01 multi-incident cluster
  (hostapd driver hang masquerading as apt lock contention, nl80211 netlink wedge, Teleport
  cert/reverse-tunnel issues, WAN-level eth0 flakiness); an unreconciled-duplicate-fix flag for two
  differently-described apt-daily-upgrade fixes that may or may not be the same change.
- `references/08_ansible-authoring.md` — OPA policy layer overview (packages, `opa eval`/`opa
  test`/`conftest` usage, ADR-001's env-gate-before-flavor-gate precedence); a design recommendation
  for bonding (not bridging) doubled RCP/NBN-Accelerate internet circuits (`mode=active-backup`,
  ARP-based monitoring, systemd-networkd VLAN-as-bond-slave race-bug risk); a third topology_vars
  authoring-bug class (role mistagging, confirmed at rocket-bore-smc01, alongside the existing
  vlanid-cloning and physical-interface-naming bugs); the SSH cipher-negotiation fix's correct home
  (`smc_sshd`'s `ssh_config` template, not per-script patches); a guardrailed single-site
  interface-key rename pattern (pia-wadjari) with the two preconditions that make it safe to reuse.
- `references/12_content-filtering.md` — SPEC-002's bridge_500-unconditional-ACCEPT fact as an
  explicit differential-diagnosis note ("VLAN 500 works, 501 doesn't" = by design, not a fault).
- `references/03_communication-flows.md` — corrected the stale "`smc_qos` planned, not started"
  claim (the role exists, is just misgated) with the per-site missing-shaping data; two
  generalizable WAN-path diagnostic techniques (RX=0 rules out firewall causes; sibling-VLAN
  isolation test) from the dark-VLAN Starlink-backup investigation.
- `references/05_troubleshooting.md` / `06_failure-modes.md` — noted the `custom_apt_install.yml`
  "invalid loop data" fix was superseded by a wholesale file replacement, not the originally
  documented in-place patch.
- **`scripts/lint-baseline-refresh.sh` + `scripts/ansible-lint-delta-gate.sh`** — promoted and
  genericized from `local-knowledge-ansible/ansible-wifi/scripts/`. Config path is now
  repo-root-relative (`ANSIBLE_LINT_CONFIG` override) instead of two hardcoded paths that disagreed
  with each other (`local-knowledge/` vs `local-knowledge-ansible/`). See `scripts/README.md`
  (retitled to cover both the WAN-routing and lint-gate script categories).

### Corrected (post-pass, operator-flagged, two rounds)

- `install.md` + `adapter.md` — first correction round stated SMC access "must go through `tsh ssh`
  via the `ssh-manager` MCP." **Also wrong** — no `ssh-manager` (or any SSH-wrapping) MCP is used at
  all; access is a direct `tsh ssh root@<hostname>` shell command, no MCP involved. Rewrote both to
  remove the MCP framing entirely: a plain "Live SSH access — direct `tsh ssh`, no MCP" section, and
  `mcp-grafana` as the only MCP left in the execution layer. Fixed the stale `ssh_list_servers`/
  `ssh_execute` verification steps to a direct `tsh ssh` check.
- `references/01_overview.md` "Remote Access" + `references/13_known-issues.md` — the Teleport
  cluster domain was previously assumed single-value fleet-wide (`teleport.apn.au`). Operator
  confirmed the actual split: `rcp`/`rct`/`wh`/`apn` → `teleport.apn.au`;
  `nbn_accelerate`/`nbn_wh`/`cw` → `teleport.communitywifi.net.au` (all 7 flavors covered). Added
  this mapping table to `01_overview.md`, `install.md`, and closed the coverage-gap row in
  `13_known-issues.md` that had briefly flagged it as unresolved.

### Not promoted (reviewed, judged not durable/in-scope)

- `ai-tooling/*.md` — meta design-rationale docs for skill-smc itself (already implemented, matches
  current pack state); not operational SMC knowledge.
- `plans/20260317_1656_interface-id-rename-plan.md` — historical, fully superseded by the
  guardrailed-rename pattern now captured in `08_ansible-authoring.md`.
- `graphify-out/` — mostly vendored-Ansible-collection graph noise; the one durable pointer
  (overlayroot-persistence roadmap item) was already covered by existing Tier 8 content.
- `snapshots/`, `history/` (except the one url-capture-v2 migration doc, already captured
  pre-session) — point-in-time governance-file backups, not distinct knowledge.

## 20260729_2324 — WAN-routing coverage expansion + reusable diagnostic scripts (APN routing-issue investigation)

Full pass to make sure the APN routing-issue investigation's learnings actually made it into this pack, prompted by an operator audit question ("did you capture all the information in the docs
folder into skill-smc?"). Answer was initially no — a subagent audit against all 11 investigation docs found real gaps, all closed in this pass.

### Added

- `references/03_communication-flows.md` — new "Manual TBF/`ifb` Ingress Shaping" subsection: a live, fleet-wide, NOT-Ansible-managed shaping mechanism previously undocumented anywhere in this
  pack. Also added: the extensionless-`dhclient-enter-hooks`-vs-`.d/`-decoy capture trap; `dhclient@<iface>.service`'s instantiation-only-when-the-netplan-device-is-real behaviour; switch02
  (`53x`) being cold-standby by design at every site except Horn Island, with the leased-vs-empty-slot triage refinement; the `LAN1`/`LAN2` Testra-managed uplink pair, outside the VLAN scheme and
  unmapped to `topology_vars`; the missing-route-vs-real-ARP-failure diagnostic (the actual Problem 2 mechanism at old-looma/umoona, live-verified 2026-07-29 — supersedes the dish-bypass theory
  for those two sites specifically).
- `references/08_ansible-authoring.md` — the confirmed list of roles that consume `interface.role` and go stale on topology drift the same way `smc_application` does (`smc_iptables`, `smc_qos`,
  `smc_node_exporter` — the last in a *separate playbook*, easy to miss); the topology-cloning authoring risk (a new site's `topology_vars` copied from an existing site can carry wrong VLAN IDs
  silently past every lint/syntax check); the standalone principle that one templated artifact being self-cleaning doesn't imply a sibling artifact from the same role is too; handler-name reuse
  across different `listen` topics being safe, not a collision.
- `references/13_known-issues.md` — new Known Operational Bug row: `my_node_network_device_info` returns zero series on old-looma/new-looma/horn-island despite `node_exporter` being up.
- `references/05_troubleshooting.md` — Tier 1 gained the `tsh ls`-vs-single-`ssh` technique for distinguishing a transient connection blip from a box that's fully deregistered from Teleport; Tier
  7 gained a step for metric-specific monitoring gaps that survive `up{instance=...} == 1`.
- `references/12_content-filtering.md` — one-line cross-reference so its existing "no per-user `tc`/`htb` shaping" claim isn't misread as "no `tc` shaping anywhere on the fleet."
- **New `scripts/` directory** — `collect-smc-evidence.sh` (read-only evidence capture) and `analyse-routing-drift.py` (the "hook covers netplan" drift discriminator), promoted from the
  investigation folder and genericized for reuse (no hardcoded default site list; `--flavor`/`--commit` override the investigation-specific defaults). Plus `routing-diagnostics.justfile`, a
  template task-runner to copy into a future investigation folder. See `scripts/README.md`.

### Corrected

- `references/03_communication-flows.md` — the dish-management-address bullet previously stated the dish-not-in-clean-bypass theory as the accepted cause of "lease held, gateway unreachable."
  Live testing 2026-07-29 showed this is not the cause on the two sites where it reproduced (the same MAC legitimately answers as gateway on every WAN interface there, healthy and broken alike) —
  qualified accordingly, downgraded from "the cause" to "a real, separate observation."
- `references/03_communication-flows.md` — the `smc_application` dhclient-restart-handler-has-no-safety-net bullet was stale relative to a same-day fix; updated from present-tense gap description
  to past-tense-fixed-with-caveat (ported, dry-run validated, not yet tested under a real connection loss).

Full narrative: `local-knowledge-ansible/ansible-wifi/issues/apn/routing-issue/docs/problem2-live-root-cause-20260729_2112.md` and
`old-looma-umoona-topology-fix-20260729_2316.md`.

## 20260728_1240 — v0.1.5: captive-portal PHP SAPI correction + APPPATH/cache failure mode + Ansible tag hazard (project-coherence run)

Triggered by `project-coherence` on ansible-wifi after a 7-day captive-portal outage across 10 of 16 in-scope `rcp` sites (2026-07-21 → 07-28). Investigating it surfaced two materially wrong architecture claims in this pack, both of the same kind the 2026-07-03 run already flagged: a single host's behaviour written up as fleet-wide truth.

### Corrected

- `references/10_captive-portal.md` §11.1 — previously stated flatly that "PHP-FPM processes `.php` files". **Wrong for the production fleet.** Verified on three sampled `rcp` hosts (horn-island, kalumburu, mornington): zero `php*-fpm` packages installed, `libapache2-mod-php` present, `apache2ctl -M` shows `php_module (shared)`, and no `/etc/php/8.1/fpm/` directory exists. Production runs **mod_php as `www-data`**. Replaced with a scoped, evidence-cited statement.
- `references/10_captive-portal.md` §11.4 — claimed a permanent Ansible `SetHandler` fix "landed 2026-06-26". **False.** Repo-wide grep finds no `SetHandler` in any role template (only a vendored `community.general` test fixture), and the enabled-modules list in `ubuntu-apache-install-configure.yml` is only `rewrite` and `ssl` — no `proxy`, no `proxy_fcgi`. This matches the long-standing ansible-wifi SCRATCHPAD open item recording the change was reverted. Section retitled as historical/ff-smc01-only with a supersession note at the top; the trailing "the Ansible template approach is now canonical" line corrected.
- `references/10_captive-portal.md` §11.7 — the verification snippet told you to test PHP-FPM processing and to read `error.log`. Replaced with a SAPI check (`apache2ctl -M`), a cache/logs perms check, an explicit warning that the §11.8 failure leaves the error log empty, and a warning not to probe `localhost` with a `Host:` header (Apache serves `000-default` and returns a healthy-looking 10671-byte page on a fully dead portal — this produced a wrong "no impact" conclusion during the incident).

### Added

- `references/10_captive-portal.md` §11.8 — new failure mode: `Directory APPPATH/cache must be writable`. Covers the Kohana `core.php:281` bootstrap check, the matching `log/file.php:31` check on `APPPATH/logs` (fix both or the failure just moves one step later), why the response is **HTTP 200** with an empty apache error log, the correct probe form, and the fix command.
- `references/06_failure-modes.md` — matching failure-mode table entry with error signature, cause class, source-of-truth paths, immediate checks, resolution, and the detection gap.
- `references/08_ansible-authoring.md` — new "Tag Hazard" entry: a tagged block that destroys and recreates state must carry its repair tasks under the same tag, including any `stat` task whose registered variable gates the repair block's `when` (otherwise a tag-limited run evaluates `when` against an undefined variable and fails). Includes the `--list-tasks` audit pattern.
- `references/13_known-issues.md` — new fleet-wide risk row: no HTTP-level captive-portal monitoring exists anywhere, and the Kohana usage/status crons run as **root** so they keep succeeding through an outage; also notes a status-code-only probe cannot detect this failure. Plus a staleness-risk note recording this as the **third** instance of the single-host-generalized-to-fleet pattern in this pack (after the 2026-07-03 DNS row and the 2026-07-09 MySQL row).
- `manifest.json` — three new `stable_facts` entries (mod_php not PHP-FPM; the Kohana writability check and its HTTP-200 signature; the Ansible tag-hazard rule). Version bumped 0.1.4 → 0.1.5; `updated_at` set to 2026-07-28T12:40:00Z.

### Related (outside this pack)

- `local-knowledge-ansible/ansible-wifi/issues/rcp-fleet/rcp-captive-portal-cache-perms-outage-20260728_1240.md` — full RCA.
- `ansible-wifi/.archcore/rules/rule-005-tagged-destroy-blocks-must-carry-repair-tasks.md` — new permanent rule.
- `ansible-wifi/roles/smc_application/tasks/main.yml` — the actual fix (uncommitted at time of writing).

## 20260703_1300 — v0.1.4: DNS architecture corrections + garimba-smc01 failure mode (project-coherence run)

Triggered by `project-coherence` on ansible-wifi after the garimba-smc01 DNS RCA (revisions 2-3) surfaced factual errors in this pack's DNS documentation that predated the incident — rule-002 had never actually been applied for a DNS-domain incident before, and the domain routing table had no explicit DNS row.

### Corrected

- `references/02_service-map.md` — DNS resolver row previously claimed "unbound = RCT flavor / bind = non-RCT flavors", generalized from the single initial RCT-only validation. Corrected: the real gate is `smc_ltp` inventory-group membership (orthogonal to flavor, currently only coincides with `rcp`/guda-guda). Also fixed Stubby's documented listen port (was wrongly given as `127.0.0.1:5353` — that's actually unbound's own `smc_ltp`-only port; Stubby listens on `127.0.0.1@60053`).
- `references/13_known-issues.md` — added a staleness-risk note generalizing the lesson: single-host-validated claims in this pack should not be assumed to hold across all flavors without an independent check.

### Added

- `references/02_service-map.md` — new `systemd-resolved` row documenting the SMC's own DNS path (separate from the DHCP/LAN unbound/stubby/bind path), and Stubby's upstream chain (single upstream, no failover, reached via an autossh **local port forward** — not a reverse tunnel — to Teleport).
- `references/06_failure-modes.md` — new failure-mode entry: domain-specific host DNS resolution delay on non-`smc_ltp` hosts (`DNSStubListener=no` exposes host glibc directly to WAN-path DNS anomalies). First confirmed on garimba-smc01, 2026-07-03.
- `references/13_known-issues.md` — new "Fleet-Wide Architecture Risks" section: Stubby's single-upstream-no-failover design and the lack of monitoring for the autossh local forward / Stubby upstream reachability, both fleet-wide, both discovered incidentally during the garimba-smc01 RCA.
- `.archcore/rules/rule-002-*.md` (ansible-wifi repo) and `AGENTS.md` (ansible-wifi repo) — added an explicit DNS domain row to the domain-routing tables, since none existed despite DNS being a documented troubleshooting area.
- `manifest.json` — new `stable_facts` entry on the `smc_ltp`-vs-flavor DNS gating; version bumped 0.1.3 → 0.1.4; `updated_at` set to 2026-07-03T13:00:00Z.
- `SCRATCHPAD.md` — current state and session history updated.

## 20260626_1845 — v0.1.3: project-coherence checklist + references/10-13 content update

### Added

- `AGENTS.md` — `## Project-coherence checklist` section: explicit Tier 1-4 update instructions for when `project-coherence` runs on this pack, with domain-to-reference routing table and cross-repo trigger rule from ansible-wifi sessions.

### Updated

- `references/10_captive-portal.md` — captive portal two-tier arch, Eclipse config.txt sync mechanism, PHP-FPM SetHandler + a2enconf alternative, PHP short_open_tag (PHP 8.1), Kohana exception handler.
- `references/11_vagrant-lab.md` — vsmc networkd race condition full root cause chain (eth1 bounce → stale DHCP lease → default route drop → Teleport unreachable); Vagrant guard fix.
- `references/12_content-filtering.md` — Eclipse identity model (T&C → auto-PIN → MAC binding → connmark), MAC randomization impact table (stable/bypass/rotate), CAKE fair queuing on bridge_501 with WAN capacity rationale.
- `manifest.json` — version bumped 0.1.2 → 0.1.3; `updated_at` set to 2026-06-26T18:45:00Z.
- `SCRATCHPAD.md` — current state updated; session history entry added; open items updated for v0.1.3.

### Notes

- Content updates fed from ansible-wifi 2026-06-26 session RUNBOOK audit (MK keys: `ansible-wifi.runbook.sections-11-12-13.20260626`, `ansible-wifi.runbook.gap-fill-audit.20260626`).
- Governance-pack regeneration pending (`.ai-context/governance-pack.md` is stale after this change).

## 20260626_1820 — Coherence sweep: repomix config, adapter.md, spec, ARCHITECTURE.md

### Fixed

- `repomix.config.json` — added `README.md`, `ARCHITECTURE.md`, `SCRATCHPAD.md`, `.archcore/**/*.md`, `.archcore/**/*.json` to `include`; moved `.archcore/**` out of `ignore`
- `exports/claude_code/project/skill-smc/adapter.md` — added install-status rows for all 12 governance files added since initial adapter.md creation: `manifest.json`, `README.md`, `ARCHITECTURE.md`, `AGENTS.md`, `CLAUDE.md`, `AI_NAVIGATION.md`, `context-map.yaml`, `SCRATCHPAD.md`, `repomix.config.json`, `.archcore/`
- `.archcore/specs/spec-specialist-pack-file-roles.md` — added file-role rows for `README.md`, `ARCHITECTURE.md`, `SCRATCHPAD.md`, `repomix.config.json`, `.archcore/`
- `ARCHITECTURE.md` — corrected stale repomix token count (was "25 files / ~33k tokens"; now "~125k chars")

### Notes

- Generated by `skill-project-coherence`.
- Coherence greps: clean — no live stale references found.

## 20260626_1812 — README and ARCHITECTURE added

### Added

- `README.md` — folder index, purpose, key file table, governance pointers, install link
- `ARCHITECTURE.md` — component table, information flow, installed surface diagram, key decisions, related workspaces

## 20260626_1810 — Archcore promotion

### Added

- `.archcore/rules/rule-progressive-disclosure-loading.md` — load only the specific reference needed for the task
- `.archcore/rules/rule-reference-update-discipline.md` — cross-file consistency on reference add/edit
- `.archcore/rules/rule-manifest-version-discipline.md` — bump version + updated_at on any content change
- `.archcore/adr/adr-progressive-disclosure-structure.md` — ADR documenting the v0.1.2 monolithic→split decision
- `.archcore/specs/spec-specialist-pack-file-roles.md` — authoritative table of file roles and install surface

### Deleted

- `ARCHCORE_PROMOTION_CANDIDATES.md` — consumed by promotion (all 5 candidates written successfully)

### Notes

- Generated by `skill-ai-it` in `promote` mode.

## 20260626_1808 — Governance scaffold bootstrap

### Added

- `AGENTS.md` — agent policy for maintaining this specialist pack; @-imports `skills_stuff/AGENTS.md`
- `CLAUDE.md` — thin Claude Code wrapper over `AGENTS.md`
- `AI_NAVIGATION.md` — human-readable context router with task-to-reference routing table
- `context-map.yaml` — machine-readable routing map for all 13 references
- `SCRATCHPAD.md` — working memory, populated from session history
- `repomix.config.json` — packs all 25 pack files into `.ai-context/governance-pack.md`
- `.archcore/` — initialized via `archcore init`
- `ARCHCORE_PROMOTION_CANDIDATES.md` — 5 candidates: 3 rules, 1 ADR, 1 spec

### Notes

- Generated by `skill-ai-it` in `bootstrap` mode.
- Graphify: no code files found, no graph output (docs-only pack — expected).
- Repomix: 25 files / 32,896 tokens packed to `.ai-context/governance-pack.md`.

## 0.1.2 — 2026-06-26

- Split the monolithic `RUNBOOK.md` into focused progressive-disclosure files under `references/`.
- Replaced root `RUNBOOK.md` with a concise navigation index and task-to-reference routing table.
- Moved known issues into `references/13_known-issues.md`.
- Removed empty placeholder resource directories.
- Updated Claude Code adapter/install docs to copy the indexed runbook plus focused references.

## 0.1.1 — 2026-06-26

- Aligned canonical source references with installed client adapter references.
- Added known issues as an explicit discoverable reference for coverage gaps and staleness risk.
- Corrected skill venv guidance to use `skills-working-cache/<skill>/venv` and reserve `skills-runtime/` for ephemeral runtime state.
- Normalized OS wording to Ubuntu 20.04+ with Ubuntu 22.04 confirmed in production.
- Updated package metadata version to 0.1.1.

## Unreleased — 2026-05-08

- Corrected SMC expansion to **Site Management Controller** across skill source and exported adapter references.
- Added related workspace mapping for `ansible-wifi`, `ansible-malik`, `dns_query`, and `local-knowledge-ansible/ansible-wifi`.
- Updated runbook guidance so URL-capture/PCAP layout changes are reconciled across the related SMC workspaces.

## 0.1.0 — 2026-04-15

Initial creation.

- SKILL.md: SMC box definition, troubleshooting decision tree (Tiers 1-7), Prometheus alert reference, Ansible authoring rules, communication flows quick reference
- RUNBOOK.md: 9-section deep reference — service map (50+ services), comms flows, dependency tree, failure modes, hardware differences, overlayroot detail, full Ansible workflows
- PROFILE.md: SMC box definition, inventory flavors (apn, cw, nbn_accelerate, nbn_wh, rcp, rct, wh), Teleport access pattern, overlayroot structure
- Validated against live malik-rct01 (RCT flavor, ARM64, Raspberry Pi 4, Ubuntu 22.04)

### Key corrections from live validation (differ from generic docs)

| Assumption | Validated Reality (RCT) |
|---|---|
| DNS = BIND/named | RCT uses Unbound + Stubby (DNS-over-TLS) |
| Traditional swap | RCT uses zram (`/dev/zram0`, ~1.2 GB) |
| iptables chain = `ECLIPSE_*` | Actual chain: `MANAGEMENT` |
| asterisk present | Not deployed on RCT |
| keepalived present | Not deployed on RCT |
| 40 GB storage | Real ext4 FS = 60 GB at `/media/root-ro`; overlayroot = 984 MB tmpfs |
````

## File: CLAUDE.md
````markdown
@AGENTS.md

## Claude-specific additions
# No skill-smc-specific Claude additions at this time.
# Add here only if this specialist pack needs Claude Code behaviour that differs from global policy.
````

## File: context-map.yaml
````yaml
version: 1

project:
  name: skill-smc
  type: specialist-pack
  context_policy: "AI_NAVIGATION.md is the human-readable router; this file is the machine-readable routing map."

bootstrap:
  required_first_read:
    - AGENTS.md
    - SKILL.md
    - RUNBOOK.md
    - AI_NAVIGATION.md
    - CHANGELOG.md

authority_order:
  - path: "manifest.json"
    type: specialist_metadata
    authority: highest
  - path: "AGENTS.md"
    type: agent_instructions
    authority: high
  - path: "CLAUDE.md"
    type: claude_specific_instructions
    authority: high
  - path: "AI_NAVIGATION.md"
    type: context_router
    authority: high
  - path: "SKILL.md"
    type: agent_activation_surface
    authority: high
  - path: "RUNBOOK.md"
    type: navigation_index
    authority: high
  - path: "references"
    type: content_source
    authority: high
  - path: "PROFILE.md"
    type: background_context
    authority: medium
  - path: "exports"
    type: client_adapter
    authority: medium
  - path: "CHANGELOG.md"
    type: project_history
    authority: medium_high
  - path: "SCRATCHPAD.md"
    type: transient_notes
    authority: low

routing:
  live_incident_triage:
    description: "Box unreachable, service down, alert firing, DHCP/DNS/WiFi/VoIP/HA failure."
    read:
      - "SKILL.md"
      - "references/05_troubleshooting.md"
      - "references/06_failure-modes.md"

  service_architecture:
    description: "Service names, unit names, config paths, monitoring collectors."
    read:
      - "references/02_service-map.md"
      - "references/03_communication-flows.md"
      - "references/04_dependency-tree.md"

  hardware_and_overlay:
    description: "x86 vs Raspberry Pi differences, overlayroot, persistence risk."
    read:
      - "references/07_hardware-overlay.md"
      - "references/01_overview.md"

  ansible_authoring:
    description: "Topology vars, cache coherence, cross-flavor blast radius, validation, generator drift, flavor/cluster conditional branching, smc_ltp sub-group (CNMaestro backhaul + DNS switch), 'low touch' onboarding method and site history."
    read:
      - "references/08_ansible-authoring.md"
      - "SKILL.md"

  url_capture_pcap:
    description: "URL capture v2, PCAP layout, smc_get_pcapv* workflows, dns_query assumptions."
    read:
      - "references/09_url-capture-pcap.md"

  captive_portal:
    description: "Captive portal architecture, Eclipse config sync, PHP-FPM setup, Kohana issues."
    read:
      - "references/10_captive-portal.md"

  vagrant_lab:
    description: "Local family-friendly-vsmc01 Vagrant lab setup and known virtualization issues."
    read:
      - "references/11_vagrant-lab.md"

  content_filtering:
    description: "VLAN 501 family-friendly filtering, Eclipse PIN/MAC, MAC randomization, CAKE queuing."
    read:
      - "references/12_content-filtering.md"

  coverage_and_gaps:
    description: "Known coverage gaps, unvalidated assumptions, live-validation limits."
    read:
      - "references/13_known-issues.md"

  smcbox_basics:
    description: "SMC box definition, inventory flavors, Teleport access pattern, satellite constraints, APN vs NBN Accelerate cluster structural comparison."
    read:
      - "references/01_overview.md"
      - "PROFILE.md"

  pack_maintenance:
    description: "Adding/updating references, bumping version, updating export adapters."
    read:
      - "AGENTS.md"
      - "AI_NAVIGATION.md"
      - "context-map.yaml"
      - "CHANGELOG.md"
      - "manifest.json"
      - "exports/claude_code/project/skill-smc/adapter.md"
      - "exports/claude_code/project/skill-smc/install.md"

generated_context_policy:
  regenerate_after:
    - new_reference_file
    - structural_change
    - scope_boundary_change
  commands:
    repomix_governance: "repomix --config repomix.config.json"
    graphify: "graphify update ."

answer_contract:
  require_source_paths: true
  unsupported_answer: "not found in skill-smc reference material"
  distinguish_assumptions: true
  do_not_invent_state: true
````

## File: manifest.json
````json
{
  "specialist_type": "project",
  "subject_name": "smc",
  "slug": "skill-smc",
  "subject_id": null,
  "title": "SMC Box Operations and ansible-wifi Authoring",
  "description": "Operational knowledge base for SMC (Site Management Controller) boxes and related ansible-wifi, ansible-malik, dns_query, and local-knowledge workflows. Covers Ansible authoring, URL capture/PCAP processing, service architecture, communication flows, troubleshooting, and failure modes.",
  "tags": ["ansible", "smc", "wifi", "operations", "troubleshooting", "teleport", "networking"],
  "environment": "ansible-wifi",
  "owner": null,
  "site": null,
  "role": null,
  "scope_boundary": "In scope: ansible-wifi repo authoring, ansible-malik SMC operator playbooks, dns_query work tied to SMC URL-capture PCAP layouts, local-knowledge-ansible/ansible-wifi artifacts, SMC box service management, live troubleshooting, Teleport access, Prometheus alerting interpretation, topology variable management. Out of scope: CNMaestro dashboard UI operations, NBN Accelerate portal, Teleport server administration.",
  "parent_refs": [],
  "related_refs": [
    "/Volumes/Data/_ansible/ansible-wifi",
    "/Volumes/Data/_ansible/ansible-malik",
    "/Volumes/Data/_ai/_scripts/scripts_stuff/python/dns_query",
    "/Volumes/Data/_ansible/local-knowledge-ansible/ansible-wifi"
  ],
  "source_bias": "stable-operational",
  "created_at": "2026-04-15T00:00:00Z",
  "updated_at": "2026-08-03T18:25:00Z",
  "version": "0.1.18",
  "dependencies": [],
  "known_constraints": [
    "SMC boxes run overlayroot — changes do not persist across reboot unless lower dir is remounted rw",
    "Ansible connects via Teleport proxy, not direct SSH",
    "topology_vars.py plugin output is cached in hidden .*.yml files — mtime-based, may be stale after git checkout"
  ],
  "stable_facts": [
    {"statement": "SMC boxes are x86 PCs or ARM64 Raspberry Pis running Ubuntu 20.04+ (22.04 seen in production).", "confidence": 0.99, "tags": ["hardware"]},
    {"statement": "All remote access routes through Teleport reverse SSH tunnel. SSH port = 50000 + site_eclipse_siteid.", "confidence": 0.99, "tags": ["access", "teleport"]},
    {"statement": "overlayroot is enabled: writes go to tmpfs at /media/root-rw/overlay and are lost on reboot.", "confidence": 0.99, "tags": ["overlayroot", "persistence"]},
    {"statement": "Canonical topology source is inventories/*/topology_vars/<site>.yml. Hidden .*.yml files are generated cache.", "confidence": 0.99, "tags": ["ansible", "topology"]},
    {"statement": "DHCP/LAN client DNS (Unbound+Stubby, or bind9/RPZ) is gated by smc_ltp inventory-group membership, not flavor. The SMC's own DNS resolution is a separate systemd-resolved/glibc path with DNSStubListener=no by default, bypassing unbound/stubby/bind entirely.", "confidence": 0.95, "tags": ["dns", "networking"]},
    {"statement": "smc_ltp is a static rcp-only Ansible group defined in inventories/rcp/prod (INI, not topology_vars-generated), currently 7 sites: guda-guda, pandanus-park, old-looma, new-looma, warburton, beagle-bay, umoona -- every 'low touch'-onboarded site. It has two unrelated purposes, not one: (1) a separate smc_ltp.yml playbook runs CNMaestro-managed Cambium ePMP/cnPilot wireless-backhaul provisioning; (2) smc_bases.yml's dns_mgmt play switches the host's DNS resolver from unbound+stubby to bind9+RPZ (zone file literally named db.cambium-rpz). The literal expansion of the acronym 'LTP' is not documented anywhere in the codebase. Corrected 2026-08-03, twice same day: first from 'only guda-guda' (mislabeled 'cnMaestro mDNS') to 4 sites via direct inventory read, then to the full 7 after the operator confirmed every low-touch site should be a member and directed adding the 3 missing ones (warburton/beagle-bay/umoona) -- a real inventory gap, operator-directed fix, verified via ansible-inventory --list and ansible-playbook --syntax-check, uncommitted/not yet run against any live SMC.", "confidence": 0.92, "tags": ["dns", "networking", "cnmaestro", "smc_ltp"]},
    {"statement": "A named 'low touch' onboarding method (operator-confirmed 2026-08-03) was used to deploy guda-guda (pilot, 2025-04-15), then a year later umoona (2026-04-12), warburton, beagle-bay, pandanus-park, old-looma, and new-looma. All 7 low-touch sites are confirmed smc_ltp members (operator confirmed the link is real, not coincidental, and directed adding the 3 that were missing from the inventory). Mechanism confirmed 2026-08-03: it is a manual step someone has to remember -- no low-touch onboarding tooling automatically assigns smc_ltp group membership, and nothing enforces or checks it happened, which is the actual root cause of the 3-site gap and a standing risk for future low-touch sites. The only 'low_touch' hit anywhere in ansible-wifi (smc_bases_low_touch_provisioning: true on pierre-rcp01, not a cohort member) is never read by any role/playbook -- an orphaned var, not an implemented code path distinct from smc_ltp group membership itself.", "confidence": 0.92, "tags": ["onboarding", "deployment-history", "smc_ltp"]},
    {"statement": "The captive portal runs under mod_php as www-data, NOT PHP-FPM. Verified 2026-07-28 on three rcp hosts: no php*-fpm packages installed, libapache2-mod-php present, apache2ctl -M shows php_module, no /etc/php/*/fpm directory. No SetHandler exists in any role template and the enabled Apache modules are only rewrite and ssl. Earlier PHP-FPM documentation described reverted family-friendly-smc01 work that never reached production.", "confidence": 0.95, "tags": ["captive-portal", "php"]},
    {"statement": "Kohana::init() unconditionally requires APPPATH/cache AND APPPATH/logs to be writable by the web user, throwing 'Directory :dir must be writable' before routing. It prints rather than raises, so the response is HTTP 200 with a ~40-byte body and apache error.log stays empty — status-code-only health checks cannot detect a dead portal.", "confidence": 0.99, "tags": ["captive-portal", "kohana", "monitoring"]},
    {"statement": "An Ansible tag on a block that destroys and recreates state must also be carried by every task repairing permissions/ownership on that state, including any stat task whose registered variable gates the repair block's when condition. Otherwise the tag-limited run is guaranteed broken while the untagged full run stays correct.", "confidence": 0.99, "tags": ["ansible", "authoring"]}
  ],
  "assumptions": [],
  "diagnostics": [
    {"statement": "First live tsh ssh access to the NBN Accelerate cluster (2026-08-03): warakurna-smc01 and indulkana-smc01, both nbn_accelerate. Confirmed live: Teleport domain (teleport.communitywifi.net.au:443), HTTPS-only portal (permanent redirect, on-box TLS termination at /etc/ssl/communitywifi.net.au/), wifi-community-app-backend present, ClamAV+Lynis installed, Asterisk absent, non-smc_ltp DNS stack (unbound+stubby, named inactive) -- every prior code-inspection-only claim checked came back confirmed, 2/2 hosts. New finding: clamav-freshclam has been failing on both hosts (exit 17, CDN-blocked) since 2026-06-21/07-23 respectively -- ClamAV hardening is deployed but running a stale virus database. Not investigated further (read-only exploratory session). nbn_wh and cw flavors remain unvalidated.", "confidence": 0.95, "tags": ["nbn-accelerate", "live-validation", "clamav"]},
    {"statement": "Full NBN Accelerate cluster fleet sweep (2026-08-03), superseding the 2-host spot-check above: all 26 reachable nbn_accelerate hosts + both nbn_wh hosts (28 total, aurukun-smc03 unreachable). Hardware: 11x AAEON BOXER-6641 (i5-8500T, 15Gi RAM, Transcend TS128GSSD420K SSD) + 15x AAEON BOXER-6404 (Celeron J1900, 7.7Gi RAM, Innodisk CFast 3ME3) for nbn_accelerate; both nbn_wh hosts are Cortex-A72 RPi-class (7.6Gi RAM, Swissbit SB AFNI0 microSD, no dmidecode -- expected). nbn_wh is the operator-confirmed wh-flavor equivalent on this cluster. clamav-freshclam confirmed failed on 26/26 nbn_accelerate hosts (not just 2), failure dates spanning 10 continuous months (2025-10-02 to 2026-07-30). nbn_wh overlayroot not yet active on either host -- operator confirmed this is a planned-but-not-yet-executed rollout (smc_rise_deploy.yml already targets nbn_wh alongside rct/wh), not a bug. Kernel-version drift confirmed live (5.15.0-79 to 5.15.0-133 across the fleet), corroborating the earlier no-automated-kernel-pipeline structural finding. koonibba-smc01 flagged at 95% disk usage with the fleet's oldest kernel. isc-dhcp-server6 failed on 28/28 hosts, confirmed benign (IPv6 disabled by policy). nbn_wh zram/swap presence contradicts the platform table's universal RPi-zram claim -- unresolved. Raw evidence relocated to local-knowledge-ansible/ansible-wifi/issues/nbn-accelerate/fleet-hardware-audit-20260803/ per evidence-retention policy.", "confidence": 0.95, "tags": ["nbn-accelerate", "live-validation", "clamav", "hardware-inventory", "fleet-sweep"]},
    {"statement": "clamav-freshclam fleet-wide failure ROOT CAUSE CONFIRMED (2026-08-03, verified via WebSearch against clamav.net and Cisco-Talos/clamav GitHub issues, not just inferred): fleet runs clamav 0.103.11+dfsg-0ubuntu0.22.04.1 uniformly (one host, warakurna-smc01, on 0.103.12 -- same EOL branch). ClamAV's 0.103 branch reached end-of-life for database updates on 2025-09-14; after that date the ClamAV CDN actively rejects freshclam requests from any 0.103.x client with HTTP 403 Forbidden. This is documented, expected, upstream behavior affecting any fleet still on 0.103.x past the cutoff -- not a cw-cluster-specific network/firewall/proxy issue, and not something that self-heals (ClamAV 0.103.4+ added a 24h cool-down for CDN-blocked clients specifically, but the block itself is permanent until the client version is upgraded). This also explains the 10-month staggered failure-date spread: each host only flips to failed the first time its freshclam timer runs after the 2025-09-14 cutoff, so hosts with different timer schedules/provisioning dates trip it at different times rather than simultaneously. Fix: upgrade clamav/clamav-freshclam fleet-wide to 1.4 LTS (current) or 1.0 LTS (older supported alternative) via roles/smc_bases.yml -- no automated version-update pipeline exists for this cluster, so nothing will self-correct without a deliberate rollout.", "confidence": 0.97, "tags": ["nbn-accelerate", "clamav", "root-cause", "eol"]},
    {"statement": "Grafana MCP exploration (2026-08-03) after fixing the blank nbn-instance service-account token (required a session/MCP restart to pick up -- stdio MCP servers cache env vars at spawn time): mcp-grafana-apn has 20 dashboards vs mcp-grafana-nbn's 9. RISE health/watchdog dashboards (RISE SMC Health Detail, RISE SMC Table, RISE Dashboard) exist only on mcp-grafana-apn -- confirmed via dashboard panel queries that RISE is deployed only to rct/wh flavors (flavor=~\"rct|wh\" gate on the 'Pending sites' panel), so rcp and the whole NBN Accelerate cluster (nbn_accelerate/nbn_wh) run zero RISE metrics. Pulled exact Prometheus metric names for the previously-undocumented rise_healthcheck.py/rise_overlay_metrics.sh/rise_zram_metrics.sh/rise_watchdog.py textfile collectors (rise_healthcheck_health_score_*, rise_healthcheck_health_penalty*, rise_overlay_used_pct/_inodes_free_pct/_active, rise_zram_*, rise_watchdog_up/_active/_boot_firmware_used_pct/_unit_active) -- these previously had '--' placeholders in the service-map textfile-collector table. Also confirmed the RISE fleet-rollup logic: a host is 'offline' when rise_watchdog_up was seen in the last 30d but not the last 5m, vs. 'pending' (RISE not yet deployed) when node_exporter is up on an rct/wh host but no rise_watchdog_up series has ever existed for it.", "confidence": 0.95, "tags": ["grafana", "rise", "monitoring", "live-validation"]},
    {"statement": "new-looma-smc01 second confirmed whole-host outage (2026-08-03), independent of the 2026-07-30 topology cross-wiring fix: operator reported the site back online; live Prometheus query via mcp-grafana-apn confirmed both up{job=\"prometheus\"} and up{job=\"node_exporter\"} for new-looma-smc01 dropped simultaneously from 2026-08-01 23:40 UTC to 2026-08-03 06:40 UTC (31h gap), then both resumed together -- consistent with whole-host/network unreachability, not a single-service crash. A separate, already-explained 18h gap in the same 7-day window (2026-07-29 11:10 to 2026-07-30 05:10 UTC) lines up with the documented cross-wiring fix. Root cause of this second, newer gap NOT established (no tsh ssh used this session, Prometheus history only) -- flagged as a possible recurrence pattern at this specific site, not concluded to share a cause with the cross-wiring bug or the still-open my_node_network_device_info zero-series gap also unique to new-looma/old-looma/horn-island.", "confidence": 0.9, "tags": ["new-looma", "outage", "live-validation", "grafana"]}
  ]
}
````

## File: PROFILE.md
````markdown
# PROFILE

## Subject
- Type: project
- Name: smc
- Slug: skill-smc

## What an SMC Box Is
An SMC (Site Management Controller) box is a managed Linux appliance deployed as a WiFi hotspot and network gateway. Hardware is either an **x86 PC** or an **ARM64 Raspberry Pi** (aarch64), running **Ubuntu 20.04+ (22.04 seen in production)**. All remote management access goes through **Teleport** via a persistent autossh reverse SSH tunnel. The port used on the Teleport server is `50000 + site_eclipse_siteid`.

## Inventory Flavors
The `ansible-wifi` repo manages 7 flavors:

| Flavor | Description |
|---|---|
| apn | APN network hotspots |
| cw | NBN Accelerate cluster — central infra hub |
| rcp | RCP network |
| rct | RCT (Raspberry Pi-based) |
| wh | WH network |
| nbn_accelerate | NBN Accelerate broadband |
| nbn_wh | NBN WH |

## Related Workspaces

| Path | Role |
|---|---|
| `/Volumes/Data/_ansible/ansible-wifi` | Canonical SMC Ansible source: roles, inventory, topology, service deployment |
| `/Volumes/Data/_ansible/ansible-malik` | Operator SMC playbooks, including URL-capture PCAP fetch/process |
| `/Volumes/Data/_ai/_scripts/scripts_stuff/python/dns_query` | DNS query processing and reporting for SMC URL-capture PCAPs |
| `/Volumes/Data/_ansible/local-knowledge-ansible/ansible-wifi` | Local-only SMC plans, reports, OPA artifacts, and investigation notes |

## Overlayroot
All SMC boxes run with overlayroot enabled:
- Lower dir (real filesystem, read-only at runtime): `/media/root-ro`
- Upper dir (tmpfs, volatile): `/media/root-rw/overlay`
- Workdir: `/media/root-rw/overlay-workdir/_`
- Mount: `overlay / overlay rw,relatime,lowerdir=/media/root-ro,...`
- **Consequence**: file writes at runtime go to RAM and are lost on reboot. Ansible changes only persist if the lower dir is remounted rw before changes are made.

## Stable Facts
- Root AGENTS.md thin wrapper over .agents/ docs.
- Ansible connects to SMC boxes via `ansible_host = {{inventory_hostname}}.teleport.<flavor>.au`.
- Topology plugin generates `topology_interfaces`, `topology_bridges`, `topology_vrfs` per host.
- 7 inventory flavors; group_vars structure separates: teleport, prometheus, jenkins, aws, per-user, all.
````

## File: README.md
````markdown
# skill-smc

Canonical specialist pack for SMC (Site Management Controller) box operations and ansible-wifi authoring.

## Purpose

Provides structured operational knowledge for SMC appliances (x86 PC and ARM64 Raspberry Pi), the ansible-wifi repo, and related SMC workflows. Covers live incident triage, Ansible authoring, URL-capture PCAP processing, captive portal, content filtering, and hardware/overlayroot behavior.

## Folder index

- [references/](references/) — 13 numbered progressive-disclosure reference files (content source)
- [exports/](exports/) — client adapter and install documentation
- [.archcore/](.archcore/) — durable rules, ADR, and spec for this pack

## Governance pointers

- Local agent guidance: [AGENTS.md](AGENTS.md)
- Parent guidance: [../../../AGENTS.md](../../../AGENTS.md)
- AI navigation entrypoint: [AI_NAVIGATION.md](AI_NAVIGATION.md)
- Machine-readable context map: [context-map.yaml](context-map.yaml)
- Pack architecture: [ARCHITECTURE.md](ARCHITECTURE.md)
- Pack version history: [CHANGELOG.md](CHANGELOG.md)
- Canonical governance root: [/Volumes/Data/_ai/governance/README.md](/Volumes/Data/_ai/governance/README.md)

## Key files

| File | Role |
|---|---|
| [SKILL.md](SKILL.md) | Agent activation surface — triggers, quick-reference, reference pointers |
| [RUNBOOK.md](RUNBOOK.md) | Navigation index — maps task types to numbered reference files |
| [PROFILE.md](PROFILE.md) | SMC box background context (not installed to clients) |
| [SYSTEM_PROMPT.md](SYSTEM_PROMPT.md) | Dedicated agent mode prompt |
| [manifest.json](manifest.json) | Machine-readable metadata: version, scope, stable facts, constraints |

## Install

See [exports/claude_code/project/skill-smc/install.md](exports/claude_code/project/skill-smc/install.md).
````

## File: RUNBOOK.md
````markdown
# SMC Box Operational Runbook

**Version:** 0.1.2
**Validated against:** malik-rct01 (RCT flavor, ARM64, Ubuntu 22.04, overlayroot enabled)
**Scope:** x86 and ARM64 SMC appliances managed by `ansible-wifi`

This file is the navigation index for the `skill-smc` specialist pack. Load only the focused
reference needed for the task instead of reading every SMC detail up front.

## SMC-Related Workspaces

| Path | Relationship |
|---|---|
| `/Volumes/Data/_ansible/ansible-wifi` | Production Ansible source for SMC roles, inventories, topology, and URL-capture deployment |
| `/Volumes/Data/_ansible/ansible-malik` | Operator playbooks for SMC operations, including `smc_get_pcapv*.yml` fetch/process workflows |
| `/Volumes/Data/_ai/_scripts/scripts_stuff/python/dns_query` | DNS reporting and workbook pipeline consuming SMC URL-capture PCAP output |
| `/Volumes/Data/_ansible/local-knowledge-ansible/ansible-wifi` | Local-only SMC plans, reports, OPA artifacts, and investigation knowledge for `ansible-wifi` |

Reference hygiene: when a URL-capture or PCAP-layout change affects more than one workspace,
update the relevant focused reference plus the relevant repo governance files in the same session
where practical.

## Reference Routing

| Task | Read |
|---|---|
| Basic SMC definition, inventory flavors, remote access, satellite constraints, APN vs NBN Accelerate cluster differences | `references/01_overview.md` |
| Service names, config paths, monitoring collectors, RCT vs x86 service map | `references/02_service-map.md` |
| External communication paths and inbound/outbound flows | `references/03_communication-flows.md` |
| Dependency relationships between network, DNS, portal, monitoring, and access systems | `references/04_dependency-tree.md` |
| Live incident triage, alerts, service failures, DHCP/DNS/WiFi/VoIP/HA issues | `references/05_troubleshooting.md` |
| Known failure signatures and fix patterns | `references/06_failure-modes.md` |
| Hardware differences, overlayroot, disk write behavior, persistence risk | `references/07_hardware-overlay.md` |
| Ansible topology vars, cache coherence, validation commands, generator drift, smc_ltp sub-group, "low touch" onboarding history | `references/08_ansible-authoring.md` |
| URL capture v2, PCAP layout, fetch/process workflows, dns_query assumptions | `references/09_url-capture-pcap.md` |
| Captive portal, Eclipse config sync, Kohana issues, portal PHP (mod_php, not PHP-FPM) | `references/10_captive-portal.md` |
| Local Vagrant lab bring-up and known virtualization issues | `references/11_vagrant-lab.md` |
| Family-friendly VLAN 501 access, filtering stack, MAC randomization, CAKE | `references/12_content-filtering.md` |
| Coverage gaps, live-validation limits, stale assumptions | `references/13_known-issues.md` |
| Reusable read-only scripts: WAN-routing/topology-drift investigation tooling (evidence capture, drift analyser, topology/hardware cross-check), plus ansible-lint pre-push/CI gate scripts | `scripts/README.md` |

## Runtime Paths

- ansible-wifi venv: `/Volumes/Data/_ai/_skills/skills-working-cache/ansible-wifi/venv`
- skill-smc venv: `/Volumes/Data/_ai/_skills/skills-working-cache/skill-smc/venv`
- ephemeral logs, pid files, and sockets: `/Volumes/Data/_ai/_skills/skills-runtime/<skill>/`

Prefer the working-cache venvs when running SMC validation tooling (`ansible-lint`, `yamllint`,
`ansible-inventory`, `ansible-playbook`) to keep versions stable across sessions.
````

## File: SCRATCHPAD.md
````markdown
# SCRATCHPAD — skill-smc

Agent working memory for the skill-smc specialist pack.
Use for: draft plans, terminal output, intermediate analysis, refactor outlines.
Cleared between sessions unless content is explicitly marked KEEP.

---

<!-- KEEP: populated 2026-06-26 from session history (UserPromptSubmit hook context) -->
<!-- KEEP: updated 2026-06-26 (ansible-wifi session) — references/10-13 content updated from ansible-wifi RUNBOOK audit; AGENTS.md project-coherence checklist added; manifest bumped to v0.1.3 -->
<!-- KEEP: updated 2026-07-28 (ansible-wifi session, project-coherence) — captive-portal PHP SAPI corrected: 10_captive-portal.md claimed PHP-FPM processes .php and that an Ansible SetHandler fix landed 2026-06-26; BOTH false (production runs mod_php as www-data, zero php*-fpm packages on 3 sampled rcp hosts, no SetHandler anywhere in the repo, enabled modules are only rewrite+ssl). §11.4 retitled historical/ff-smc01-only; new §11.8 APPPATH/cache failure mode; 06_failure-modes.md + 08_ansible-authoring.md (tag hazard) + 13_known-issues.md (no portal HTTP monitoring; third single-host-generalized-to-fleet correction) all gained entries; 5 routing rows across SKILL/AGENTS/AI_NAVIGATION/RUNBOOK de-PHP-FPM'd; 3 new manifest stable_facts; manifest bumped to v0.1.5 -->
<!-- KEEP: updated 2026-07-03 (ansible-wifi session, project-coherence) — DNS architecture corrections: 02_service-map.md's "unbound=RCT/bind=non-RCT" framing was wrong (real gate is smc_ltp group, not flavor); Stubby listen port fixed (60053, not 5353); new systemd-resolved host-DNS row + Stubby upstream chain added; 06_failure-modes.md gained garimba-smc01 DNS delay entry; 13_known-issues.md gained fleet-wide architecture risks section; rule-002 + ansible-wifi AGENTS.md gained a DNS domain routing row (previously missing); manifest bumped to v0.1.4 -->
<!-- KEEP: updated 2026-07-31 — full local-knowledge-ansible/ansible-wifi extraction pass (v0.1.6); ssh-manager MCP framing removed, replaced with direct-tsh-ssh + confirmed flavor->Teleport-domain mapping; cross-repo feed-back rule broadened on both skill-smc and ansible-wifi sides after root-causing why the extraction pass found unpromoted knowledge (v0.1.7) -->
<!-- KEEP: updated 2026-08-03 — NBN Accelerate cluster gap-fill (v0.1.8): 01_overview.md/08_ansible-authoring.md/10_captive-portal.md/13_known-issues.md now document the cw/nbn_accelerate/nbn_wh cluster by structural comparison against apn/rcp/rct/wh, explicitly flagged as code-inspection-only, not live-validated -->
<!-- KEEP: updated 2026-08-03 — smc_ltp properly explored (v0.1.9): fixed a real undercount (4 sites — guda-guda/pandanus-park/old-looma/new-looma — not just guda-guda) and a mislabel ("cnMaestro mDNS" was wrong; it's CNMaestro Cambium backhaul provisioning + a DNS-resolver-stack switch to bind9/RPZ, two unrelated purposes). New dedicated section in 08_ansible-authoring.md; SKILL.md/05_troubleshooting.md quick-refs fixed -->
<!-- KEEP: updated 2026-08-03 — "low touch" onboarding method + site deployment history added (v0.1.10): guda-guda pilot 2025-04-15, then umoona/warburton/beagle-bay/pandanus-park/old-looma/new-looma in 2026; all 4 smc_ltp sites are also low-touch sites — flagged as an unresolved correlation, not concluded. "low_touch" has no live Ansible code path (one orphaned host_var, never read) -->
<!-- KEEP: updated 2026-08-03 — smc_ltp/low-touch correlation RESOLVED (v0.1.11): operator confirmed the link is real (every low-touch site should be an smc_ltp member) and directed + verified adding the 3 missing sites (warburton/beagle-bay/umoona) to inventories/rcp/prod. smc_ltp is now 7 members, not 4. Uncommitted production Ansible inventory change — not yet run against any live SMC -->

## Current state

**Phase:** Stable — v0.1.18, fully coherent. ClamAV fleet-wide failure root cause confirmed (ClamAV 0.103.x end-of-life, not a network/cluster issue). Grafana CW/NBN exploration completed: dashboard inventory + RISE metric names documented. new-looma-smc01 second whole-host outage (31h, 2026-08-01→2026-08-03) confirmed via live Prometheus, root cause open.

skill-smc is the canonical specialist pack for SMC (Site Management Controller) box operations and ansible-wifi authoring. As of v0.1.3 the pack has 13 numbered focused reference files under `references/`. RUNBOOK.md is a navigation index only — all operational content lives in `references/0N_*.md`. Content for `references/10_captive-portal.md`, `references/11_vagrant-lab.md`, `references/12_content-filtering.md` was updated from the ansible-wifi 2026-06-26 session (captive portal architecture, Vagrant lab nuances, Eclipse identity, CAKE queuing). AGENTS.md now includes an explicit project-coherence checklist with tier-ordered update instructions and cross-repo trigger rule from ansible-wifi. As of v0.1.6, `scripts/` covers two categories (WAN-routing diagnostics + ansible-lint pre-push/CI gate) and every markdown file under `local-knowledge-ansible/ansible-wifi/` has been swept for gaps against this pack (see CHANGELOG 20260731_1245). As of v0.1.7, the feed-back loop that broke last time (narrow "incident/debug fix" wording) is fixed: `AGENTS.md`'s cross-repo trigger rule and the matching rules on the ansible-wifi side (`AGENTS.md`, `rule-002`, `task-patterns.md`, `validation.md`) now cover the whole tree, both `skill-slurp-chat` and `project-coherence` as trigger points, and a broader knowledge-type list (design docs, ADRs, OPA, scripts) — intended to make another full-directory sweep unnecessary. As of v0.1.8, the pack documents the **NBN Accelerate cluster** (`cw`/`nbn_accelerate`/`nbn_wh`, `teleport.communitywifi.net.au`) by structural comparison against the APN cluster (`apn`/`rcp`/`rct`/`wh`, `teleport.apn.au`) — closing the gap where ~95% of prior content was APN-cluster-derived and NBN Accelerate had only the flavor→domain mapping. New content spans `01_overview.md` (full comparison table + selector mechanism), `08_ansible-authoring.md` (confirmed flavor-exclusive gates), `10_captive-portal.md` (protocol/redirect diffs), and `13_known-issues.md` (coverage gap + naming-collision + OPA gaps) — all explicitly flagged as code-inspection-only, not live-validated against a cw-cluster host. As of v0.1.9, `smc_ltp` — previously documented only as a DNS-gating side effect of the 2026-07-03 RCA — is properly explored: it is a static `rcp`-only group (`inventories/rcp/prod`, initially found as 4 sites, not `topology_vars`-generated) with two unrelated purposes (CNMaestro Cambium backhaul provisioning via a separate `smc_ltp.yml` playbook, and a DNS-resolver-stack switch to bind9/RPZ), documented in a new `08_ansible-authoring.md` section with cross-references from `01_overview.md`, `02_service-map.md`, `13_known-issues.md`, `SKILL.md`, and `05_troubleshooting.md`. As of v0.1.10, a related finding was documented alongside it: a named **"low touch" onboarding method** (`guda-guda` pilot 2025-04-15; `umoona`/`warburton`/`beagle-bay`/`pandanus-park`/`old-looma`/`new-looma` in 2026) — initially only 4 of 7 low-touch sites showed up in `smc_ltp`, flagged as an unresolved (not concluded) correlation. **As of v0.1.11, that correlation is resolved**: operator confirmed every low-touch site is meant to be an `smc_ltp` member, and directed + verified (via `ansible-inventory --list` and `ansible-playbook --syntax-check`) adding the 3 missing sites (`warburton`/`beagle-bay`/`umoona`) to `inventories/rcp/prod`. `smc_ltp` is now documented as 7 members throughout this pack. This is a real, uncommitted production Ansible inventory change — not yet run against any live SMC. Separately, "low touch" itself still has no live Ansible code path of its own (the one `low_touch`-named var in the repo, on an uninvolved host, is set but never read) — the resolved link is specifically "low-touch sites should be `smc_ltp` members," not "low touch is implemented via `smc_ltp` group logic." **The mechanism question is now also resolved (v0.1.12): it's a manual step someone has to remember**, with no tooling or enforcement — the confirmed root cause of the 3-site gap, and a standing risk for future low-touch sites rather than a one-off.

---

## Open items

- [ ] Install v0.1.15 to `~/.claude/skills/skill-smc/` — run steps in `exports/claude_code/project/skill-smc/install.md` (now also copies `scripts/` and documents tsh-ssh-only access)
- [x] ~~Investigate root cause of the `clamav-freshclam` CDN-block~~ — resolved 2026-08-03: **ClamAV 0.103.x reached end-of-life for database updates on 2025-09-14; the CDN now hard-blocks any 0.103.x client.** This fleet runs 0.103.11/.12 uniformly. Verified via `WebSearch` against `blog.clamav.net` and the Cisco-Talos/clamav GitHub issue tracker — not a cw-cluster network/firewall issue, a documented upstream EOL enforcement. Fix (not yet done): upgrade to 1.0 or 1.4 LTS fleet-wide.
- [x] ~~Check whether the CDN-block is genuinely cw-cluster-specific~~ — resolved 2026-08-03: **not cluster-specific at all** — it's a ClamAV-upstream version-EOL enforcement (0.103.x blocked CDN-wide since 2025-09-14) that would affect any fleet anywhere still on that version, confirmed via external sources, not an artifact of this cluster's network path
- [x] ~~Extend the NBN Accelerate live-validation spot-check to more `nbn_accelerate` sites~~ — done 2026-08-03, full fleet sweep (26/26 reachable `nbn_accelerate` + both `nbn_wh` hosts). Still not done: `cw` flavor (no site-level hosts exist to check) and `aurukun-smc03` (unreachable via `tsh ls` at capture time)
- [ ] Live-validate the `smc_ltp` documentation (CNMaestro provisioning behavior, bind9/RPZ DNS switch) against one of the 7 real member hosts (`guda-guda`, `pandanus-park`, `old-looma`, `new-looma`, `warburton`, `beagle-bay`, `umoona`) via `tsh ssh` — everything added 2026-08-03 is from Ansible source inspection only; these are `rcp` (APN cluster) sites, not reachable from the `teleport.communitywifi.net.au` session used for the fleet sweep
- [ ] Ask the operator (or check further afield — commit history, old design docs) whether "LTP" has a known expansion; currently documented as an open question, not guessed
- [ ] Resolve the naming-collision question flagged 2026-08-03 in `04_dependency-tree.md`: is the generic "cnmaestro-provisioning"/`redis` Level-4 dependency row (RCT-oriented, `05_troubleshooting.md` Tier 4) the same mechanism as `smc_ltp`'s `roles/smc_cnmaestro_provisioning` (no Redis observed), or two genuinely separate provisioning paths?
- [ ] Confirm the `inventories/rcp/prod` `smc_ltp` group change (adding `warburton`/`beagle-bay`/`umoona`) gets committed to the `ansible-wifi` repo and run against those 3 sites — as of this update it's a verified-but-uncommitted file-level change
- [ ] Consider whether a lightweight enforcement check (e.g. a periodic `ansible-inventory` diff, or a checklist item) is worth proposing for future low-touch onboardings, given the mechanism is now confirmed manual/unenforced — not this pack's call to implement, but worth flagging if asked
- [ ] Re-check `mount | grep overlay` on `bungardi-smc01`/`darlngunaya-smc01` after the operator's planned `nbn_wh` overlay rollout lands, to confirm it took
- [ ] Resolve the `nbn_wh` zram/swap discrepancy flagged 2026-08-03 in `07_hardware-overlay.md` (`Swap: 0B`, no `zram0` device on either `nbn_wh` host) against the platform table's universal "RPi → zram" claim — may mean the claim itself needs re-checking against a live `rct`/`wh` host, never actually confirmed there either
- [ ] `koonibba-smc01` flagged at 95% disk usage with the fleet's oldest kernel (`5.15.0-79-generic`) — worth a maintenance pass, not investigated further this sweep
- [ ] Resolve the OPA `flavors.json`/`environments.json` coverage question flagged in `13_known-issues.md` (no `cw`/`apn`/`rct`/`wh` entries — intentional scoping or gap?) — needs whoever owns the OPA policy layer
- [ ] Validate `references/13_known-issues.md` entries against current ansible-wifi state when next working on that repo
- [x] ~~Regenerate `.ai-context/governance-pack.md` after today's content + governance changes~~ — done, regenerated 3× today as content landed in stages
- [ ] The bonding design (08_ansible-authoring.md, RCP/NBN-Accelerate doubled circuits) and the
      `smc_host_dns_mode: resolved_stub` DNS mitigation (06_failure-modes.md) are both unimplemented
      design recommendations, not confirmed fixes — re-check their status next time this pack is
      touched and update the wording if either has since been canaried/adopted/rejected.
- [ ] The apt-lock-race vs. apt-daily-upgrade-timer-mask duplicate-fix question flagged in
      `13_known-issues.md` (Skill Staleness Risks) needs resolving against actual ansible-wifi
      commits before either fix's documentation can be fully trusted.
- [x] ~~Grafana CW exploration — blocked, not started~~ — resolved 2026-08-03: session restart picked up the fixed token, `mcp-grafana-nbn` confirmed live. Explored both `mcp-grafana-apn` (20 dashboards) and `mcp-grafana-nbn` (9 dashboards); documented the 11 APN-only dashboards (RISE health/watchdog framework, fleet reporting/offline tables, backlog monitoring) and pulled exact `rise_*` Prometheus metric names into `02_service-map.md`/`03_communication-flows.md`. See memory-keeper key `skill-smc.discovery.grafana-dashboard-inventory-rise-metrics-20260803`.
- [ ] Root-cause the new confirmed 31h new-looma-smc01 outage (2026-08-01 23:40 → 2026-08-03 06:40 UTC) — Prometheus history confirms whole-host unreachability but no `tsh ssh` was done this session to check WAN/power/backhaul logs; worth checking next time that site is accessed live. Not confirmed related to the still-open `my_node_network_device_info` zero-series gap on new-looma/old-looma/horn-island.
- [ ] Grafana dashboards not yet explored in detail: "Data Backlog" (0 panels — appears unused/placeholder, confirm before assuming dead), the two Prometheus RW Receiver+Sender Backlog dashboards (federation pipeline health — not yet cross-referenced against the `autossh-prometheus-federation` service row in `02_service-map.md`), "Servers Network"/"Servers System Information" (backend infra, likely out of skill-smc scope but not confirmed), "RISE Dashboard" (`rise-stage0_5` — earlier-stage rollout view, not compared against the newer RISE SMC Table/Health Detail dashboards for redundancy)

---

## Key anchors

| Item | Detail |
|---|---|
| Canonical source | `/Volumes/Data/_ai/_skills/skills_stuff/specialists/project/skill-smc/` |
| Installed skill (Claude Code) | `~/.claude/skills/skill-smc/` |
| ansible-wifi repo | `/Volumes/Data/_ansible/ansible-wifi` |
| ansible-malik repo | `/Volumes/Data/_ansible/ansible-malik` |
| dns_query scripts | `/Volumes/Data/_ai/_scripts/scripts_stuff/python/dns_query` |
| local-knowledge | `/Volumes/Data/_ansible/local-knowledge-ansible/ansible-wifi` |
| skill-smc venv | `/Volumes/Data/_ai/_skills/skills-working-cache/skill-smc/venv` |
| ansible-wifi venv | `/Volumes/Data/_ai/_skills/skills-working-cache/ansible-wifi/venv` |
| Validated against | malik-rct01 (RCT flavor, ARM64, Ubuntu 22.04, overlayroot enabled) |
| Grafana MCP config | `~/.claude.json` `mcpServers` block: `mcp-grafana` (APN main-org, unrelated), `mcp-grafana-apn` (port 53000), `mcp-grafana-nbn` (port 63000 — the CW/NBN-Accelerate instance) |

---

## Recent decisions

- 2026-08-03 — Operator reported "new-looma-smc01 is back online." Verified rather than just acknowledged: queried live Prometheus via `mcp-grafana-apn` (`up{instance=~"new-looma.*"}`, 7-day range). Confirmed a 31h whole-host outage (both `prometheus` self-scrape and `node_exporter` dark simultaneously) from 2026-08-01 23:40 UTC to 2026-08-03 06:40 UTC, now recovered — matching the operator's report with hard evidence and exact timestamps rather than taking it at face value. Also found a second, earlier 18h gap in the same window that turned out to already be explained by the documented 2026-07-30 topology cross-wiring fix — good cross-validation that the existing docs are accurate. The new 31h gap's root cause is NOT established (no tsh ssh this session) — logged as confirmed-timeline-only. Added to `13_known-issues.md`'s existing new-looma section; manifest bumped to v0.1.18.

- 2026-08-03 — Follow-up session: operator confirmed the NBN Grafana token fix had landed and a session restart happened, unblocking the connection left stuck at the end of the previous session. Confirmed `mcp-grafana-nbn` live via `search_dashboards` (9 dashboards, all `smc`-tagged). Rather than stop at "connection works," compared it against `mcp-grafana-apn` (20 dashboards) to find what's genuinely new: 11 APN-only dashboards, most notably a RISE health/watchdog framework (RISE SMC Health Detail, RISE SMC Table) absent from NBN because RISE only deploys to `rct`/`wh` flavors — confirmed via the `flavor=~"rct|wh"` gate in a panel query, not inferred from dashboard absence alone. Pulled exact Prometheus metric names for the 4 `rise_*` textfile collectors that previously had `—` placeholders in `02_service-map.md`, plus the offline-vs-pending fleet-rollup distinction (30d-seen-but-not-5m vs. series-never-existed). Documented in `02_service-map.md` (new RISE Health/Watchdog Framework subsection) and `03_communication-flows.md` (new Dashboard inventory subsection). Manifest bumped to v0.1.17.

- 2026-08-03 (earlier session) — Operator offered the CW/NBN-Accelerate Grafana instance (`mcp-grafana-nbn`) for exploration. Spent the session getting the MCP connection working rather than exploring content: found 3 grafana MCP instances in `~/.claude.json` (unsuffixed = unrelated APN main-org grafana; `-apn` = port 53000; `-nbn` = port 63000, the actual CW instance). Root-caused two independent breakages (blank service-account token on `-nbn`, no tunnel on `-apn`), got operator to supply a token and start both tunnels, edited the token into `~/.claude.json` — but `-nbn` still 401'd at the time. Confirmed via direct `curl` with the `Authorization` header (200 OK) that the token and tunnel were both fine; the blocker was the already-running MCP process caching its old blank-token env, needing a restart to pick up the fix. Resolved in the follow-up session above.

- 2026-08-03 — Operator asked what could be causing the fleet-wide ClamAV `freshclam` failure documented in the previous entry. Used `WebSearch` against `blog.clamav.net` and the Cisco-Talos/clamav GitHub issues (external, citable sources) rather than speculating from this pack's own data alone. **Confirmed root cause**: ClamAV's 0.103 branch reached end-of-life for database updates on 2025-09-14; the ClamAV CDN now hard-blocks `freshclam` from any 0.103.x client with HTTP 403. This fleet runs 0.103.11/.12 uniformly. This also explains the 10-month staggered failure-date spread from the fleet sweep — each host only flips to `failed` the first time its `freshclam` timer runs after the cutoff, not simultaneously. Converts what had been "root cause not investigated, 3 open hypotheses" into a confirmed, externally-verified fact with a concrete fix (upgrade to 1.0/1.4 LTS — not yet done, no automated pipeline exists to do it). Manifest bumped to v0.1.16.

- 2026-08-03 — Operator asked for a thorough analysis of "all the NBN Accelerate sites," including hardware details and the state of installed apps/scripts/services, and asked that reusable scripts be captured under `scripts/` with a justfile. Built `scripts/collect-fleet-health.sh` + `scripts/fleet-health.justfile` (new, flavor-agnostic, same read-only safety contract as `collect-smc-evidence.sh`) and ran a full sweep of all 26 reachable `nbn_accelerate` hosts plus both `nbn_wh` hosts (28 total) — not a spot-check. First-ever live chassis-model inventory for this cluster: 11× AAEON BOXER-6641 + 15× AAEON BOXER-6404 (`nbn_accelerate`, x86), both `nbn_wh` hosts genuine Raspberry Pi (Cortex-A72) — operator confirmed `nbn_wh` is the `wh`-flavor equivalent on this cluster. Major finding: `clamav-freshclam` confirmed failed on **26/26** `nbn_accelerate` hosts (escalated from the earlier 2-host finding), with failure dates spanning 10 continuous months — an active, ongoing degradation, not a settled past incident. Mid-write-up, operator confirmed `nbn_wh`'s missing overlayroot is a planned-but-not-yet-executed rollout, not a bug — corrected the finding's framing accordingly before it shipped as an "unexplained gap." Also found and fixed real bugs in the tooling itself via dogfooding: a mid-run script-file edit that corrupted the first capture batch, a `just`-working-directory path assumption that broke all three quick-check recipes, and the same exit-code-of-last-command false-negative bug from the earlier smc_ltp work. Raw evidence relocated to `local-knowledge-ansible/ansible-wifi/issues/nbn-accelerate/fleet-hardware-audit-20260803/` per the pack's evidence-retention policy. Manifest bumped to v0.1.15.

- 2026-08-03 — Operator made `tsh login` available for the NBN Accelerate cluster and invited exploratory commands — the first-ever live access this pack has had to that cluster. Ran read-only diagnostics against `warakurna-smc01` and `indulkana-smc01` (both `nbn_accelerate`). Every code-inspection-only claim from earlier today's gap-fill checked out confirmed on 2/2 hosts (Teleport domain, HTTPS-only portal with on-box TLS termination, mobile-app backend present, ClamAV+Lynis installed, Asterisk absent, non-`smc_ltp` DNS stack). New finding, previously unknown: `clamav-freshclam` chronically failing on both hosts (CDN-blocked, exit 17) since 2026-06-21/07-23 — ClamAV's virus database is stale on both, degraded detection despite the daemon staying active. Not investigated further and no remediation attempted — read-only exploratory session, root cause left open. Written up in `13_known-issues.md` (new "Known Operational Bugs (NBN Accelerate cluster)" section), `08_ansible-authoring.md` (ClamAV/Lynis gate row), `01_overview.md` (evidence-basis note). `nbn_wh`/`cw` flavors remain unvalidated. Manifest bumped to v0.1.14.

- 2026-08-03 — Operator confirmed the final open question from the `smc_ltp`/"low touch" thread: the group-membership mechanism is **a manual step someone has to remember** — no low-touch onboarding tooling automatically assigns `smc_ltp` membership, and nothing enforces or checks that it happened. This is the confirmed root cause of the 3-site gap fixed in the immediately-preceding decision (a manual, unenforced step is exactly what silently drops during a busy onboarding), and stands as an ongoing risk for any future low-touch site, not a one-off closed by that fix. Added an explicit operational note to `08_ansible-authoring.md` recommending `smc_ltp:children` membership be verified explicitly (not assumed) whenever a new low-touch site goes live. Manifest bumped to v0.1.12.
- 2026-08-03 — Operator confirmed and resolved the `smc_ltp`/"low touch" correlation flagged earlier today: every low-touch-onboarded site is meant to be an `smc_ltp` member, and the 3 that weren't (`umoona`, `warburton`, `beagle-bay`) were a plain inventory gap, not a coincidental overlap. Operator made and verified the fix directly in `ansible-wifi`: added `warburton_smc_ltp`/`beagle-bay_smc_ltp`/`umoona_smc_ltp` host groups plus each site's `:children` block to `inventories/rcp/prod`, matching the existing 4-site pattern. Verified via `ansible-inventory --list` (all 7 now under `smc_ltp:children`) and `ansible-playbook --syntax-check smc_ltp.yml` (clean) — a real, uncommitted production Ansible inventory change, not yet run against any live SMC. `smc_ltp` membership updated to 7 sites throughout this pack (`08_ansible-authoring.md`, `01_overview.md`, `02_service-map.md`, `13_known-issues.md`, `SKILL.md`, `05_troubleshooting.md`, `manifest.json`). Manifest bumped to v0.1.11.

- 2026-08-03 — Operator relayed a newly-confirmed "low touch" onboarding method and site deployment history (from parallel work on the ansible-wifi side): `guda-guda` was the pilot (2025-04-15, a full year before the next site), followed by `umoona` (2026-04-12), `warburton`, `beagle-bay`, `pandanus-park`, `old-looma`, `new-looma` in 2026. Cross-checked against `local-knowledge-ansible/ansible-wifi/issues/apn/routing-issue/{CHANGELOG,SCRATCHPAD}.md` and the root governance `SCRATCHPAD.md`, all consistent. Notable finding surfaced while writing this up: all 4 `smc_ltp` sites (from the correction earlier today) are also in the low-touch cohort — flagged as an unresolved, not-concluded correlation rather than asserted as causal, since the mechanism (if any) is unconfirmed. Separately grepped the whole `ansible-wifi` repo for `low_touch` and found only one hit, an orphaned host_var (`smc_bases_low_touch_provisioning: true` on `pierre-rcp01`, not a cohort member) that no role or playbook reads — "low touch" currently has no Ansible-code representation, it's a process/operational distinction only. Manifest bumped to v0.1.10.
- 2026-08-03 — Operator flagged that `smc_ltp` "has not been explored and documented properly" — correct: prior coverage was only a side effect of the 2026-07-03 DNS RCA, never independently re-verified. Direct read of `smc_ltp.yml`, `inventories/rcp/group_vars/smc_ltp.yml`, `inventories/rcp/prod`, `roles/smc_cnmaestro_provisioning/`, `roles/smc_dns_mgmt/tasks/main.yml` found two things wrong: (1) membership undercounted as "only guda-guda" — the actual grep-source (`inventories/rcp/prod`) is INI-format, not `.yml`, and was missed by the original grep; real membership is 4 sites (`guda-guda`, `pandanus-park`, `old-looma`, `new-looma`). (2) purpose mislabeled "cnMaestro mDNS" — actually two unrelated purposes, neither mDNS: CNMaestro-managed Cambium ePMP/cnPilot wireless-backhaul provisioning (separate `smc_ltp.yml` playbook) and a DNS-resolver-stack switch from unbound+stubby to bind9+RPZ (`smc_bases.yml`'s `dns_mgmt` play, zone file literally named `db.cambium-rpz`). This session's findings were independently cross-checked against a parallel same-day pass done from the ansible-wifi side, which reached the same conclusions. New dedicated section added to `08_ansible-authoring.md`; `01_overview.md`/`02_service-map.md`/`13_known-issues.md`/`SKILL.md`/`05_troubleshooting.md` corrected. LTP's literal expansion is not documented anywhere in the codebase — left as an open question rather than guessed. Manifest bumped to v0.1.9.
- 2026-08-03 — Operator asked to fill the NBN Accelerate (`teleport.communitywifi.net.au`) documentation gap: ~95% of the pack was APN-cluster-derived (`apn`/`rcp`/`rct`/`wh`), with NBN Accelerate (`cw`/`nbn_accelerate`/`nbn_wh`) only covered by the flavor→domain mapping from 2026-07-31. Ran three parallel research passes (inventory group_vars diff across all 7 flavors; repo-wide grep for flavor-conditional branching in roles/templates/playbooks; doc/ADR/OPA search in local-knowledge-ansible/ansible-wifi) rather than assuming the two clusters are identical. Findings: real structural differences (no graylog/opensearch or kernel-update pipeline on the cw side; mobile-app backend + kiosk mode on `nbn_accelerate` only; HTTPS-only portal + different blocked-URL domain), a small number of genuine flavor-exclusive role gates (ClamAV/Lynis on `nbn_accelerate` only, VoIP/Asterisk on `rcp` only), and that most hardware-class branching (`hotspot_flavor` small-box/big-box) is identical across both clusters — it's a hardware split, not a cluster split. Also surfaced a "community wifi" naming collision (used generically for `rcp` sites in `issues/apn/routing-issue/`) and an OPA policy coverage gap (`flavors.json`/`environments.json` have no `cw`/`apn`/`rct`/`wh` entries). All new content explicitly flagged as code-inspection-only — no live cw-cluster host was accessed this session. Manifest bumped to v0.1.8.
- 2026-07-31 — Removed an incorrect ssh-manager MCP framing from `install.md`/`adapter.md` after two rounds of operator correction, and added the confirmed flavor→Teleport-domain mapping (never previously documented). Access is exclusively a direct `tsh ssh root@<hostname>` shell command — no MCP, no `ssh-config.toml`. Domain mapping: `rcp`/`rct`/`wh`/`apn` → `teleport.apn.au`; `nbn_accelerate`/`nbn_wh`/`cw` → `teleport.communitywifi.net.au` (all 7 flavors). Added to `01_overview.md` "Remote Access", `install.md`, closed the brief `13_known-issues.md` coverage gap once confirmed.
- 2026-07-31 — Broadened the cross-repo feed-back rule (operator-requested, follow-up to the extraction pass) so this pack never needs another full-directory sweep. Root cause of the extraction pass's gaps: the existing rule (`AGENTS.md`, ansible-wifi's `rule-002`/`task-patterns.md`/`validation.md`) was worded narrowly around "SMC incident/debug fixes," so design docs, ADRs, OPA changes, and scripts never triggered it, and only `project-coherence` (not `skill-slurp-chat`) was named as a trigger. Broadened both sides symmetrically: scope now covers the whole `local-knowledge-ansible/ansible-wifi` tree including current/future subfolders (via the `@`-import convention those subfolders already use), the knowledge-type list now explicitly includes unimplemented design recommendations/ADRs/OPA/scripts/ROADMAP items, and both `skill-slurp-chat` and `project-coherence` are named as mandatory trigger points with a closeout self-check. Manifest bumped to v0.1.7.
- 2026-07-31 — Full extraction pass over `local-knowledge-ansible/ansible-wifi/` (operator-requested, exhaustive). Two subagent audits (`.archcore/` ADRs+rules+specs; `apn/routing-issue/docs/` 20 files) plus a background `.remember/` completeness sweep found: amata-smc01's disk-failure incident was entirely uncaptured (added to 06/07/13); a bonding-vs-bridging design recommendation for RCP/NBN-Accelerate dual-switch WAN circuits (dated the same day, 2026-07-31) was brand new; the OPA policy layer (env-gate/flavor-gate precedence, policy packages) had zero coverage despite one passing mention of "the OPA gate" in 08_ansible-authoring.md; `smc_qos`'s "planned, not started" framing in 03_communication-flows.md was stale (the role exists, is just misgated to rct-only); a third topology_vars authoring-bug class (role mistagging, rocket-bore-smc01) and a distinct multi-incident site cluster (bungardi-smc01) surfaced only in raw `.remember` daily logs, never promoted to an ADR/issue-report. `snapshots/` (59 dirs) and `history/` confirmed via diff to be point-in-time copies of the same governance file, not distinct content — not deep-read. Manifest bumped to v0.1.6.
- 2026-07-03 — DNS documentation in `02_service-map.md` had been silently wrong since v0.1.0: the "unbound = RCT flavor, bind = non-RCT flavors" framing was a generalization from the single initial RCT-only validation that was never checked against other flavors. Corrected to the real gate (`smc_ltp` inventory-group membership, orthogonal to flavor) via a repo-wide grep during the garimba-smc01 RCA. Lesson generalized into `13_known-issues.md`: treat single-host-validated claims in this pack as unverified for other flavors until independently checked.
- 2026-07-03 — Added an explicit "DNS resolution architecture" row to the domain-routing tables in ansible-wifi's `rule-002` and `AGENTS.md` — this domain had no routing entry despite being a documented troubleshooting area, which is likely why the garimba-smc01 DNS incident wasn't fed back into this pack until a later `project-coherence` run caught the gap.
- 2026-06-26 — Split monolithic RUNBOOK.md into 13 numbered focused reference files. RUNBOOK.md is now a navigation index only.
- 2026-06-26 — SYSTEM_PROMPT.md line 32 fixed: stale "Reference RUNBOOK.md for full service map…" replaced with specific numbered reference list.
- 2026-06-26 — Dead `references/PROFILE.md` pointer removed from SKILL.md (PROFILE.md is not installed per adapter.md).
- 2026-06-26 — Bootstrap governance scaffold added: AGENTS.md, CLAUDE.md, AI_NAVIGATION.md, context-map.yaml, SCRATCHPAD.md.
- 2026-06-26 — Coherence sweep: repomix.config.json fixed (added .archcore/ content); adapter.md expanded to 16 rows; spec expanded to 17 rows; ARCHITECTURE.md stale token count corrected.

---

## Session history (summaries)

### 2026-08-03 — new-looma-smc01 second whole-host outage confirmed via live Prometheus (v0.1.17 → v0.1.18)
- Operator reported "new-looma-smc01 is back online" — a bare status ping. Rather than just acknowledge it, queried live Prometheus (`mcp-grafana-apn`, still connected from the previous exploration) to verify and get exact timestamps.
- Confirmed: `up{job="prometheus"}` and `up{job="node_exporter"}` for `new-looma-smc01` both went dark simultaneously 2026-08-01 23:40 UTC → 2026-08-03 06:40 UTC (31h), then both resumed together — whole-host/network outage signature, not a single service crash.
- Found and ruled out a red herring: a second, earlier 18h gap in the same 7-day window (2026-07-29 11:10 → 2026-07-30 05:10 UTC) exactly matches the already-documented topology cross-wiring fix — good cross-validation, not a new finding.
- Root cause of the new 31h gap NOT established — no `tsh ssh` this session, Prometheus history only. Logged as confirmed-timeline, open root cause.
- Written to `13_known-issues.md` (new paragraph in the existing new-looma section). Manifest bumped v0.1.17 → v0.1.18; CHANGELOG.md entry added.
- Evidence basis: live `mcp-grafana-apn` `query_prometheus` reads this session; timestamps converted via direct `date -u -r <epoch>`, not estimated.

### 2026-08-03 — Grafana CW exploration unblocked: dashboard inventory + RISE metric names (v0.1.16 → v0.1.17)
- Follow-up to the blocked exploration attempt below: operator confirmed the token fix landed and a restart happened. Confirmed `mcp-grafana-nbn` live (9 dashboards).
- Compared against `mcp-grafana-apn` (20 dashboards) rather than stopping at "it connects now" — found 11 APN-only dashboards, most notably a RISE health/watchdog framework with no NBN counterpart.
- Confirmed (not assumed) that RISE deploys only to `rct`/`wh` via the `flavor=~"rct|wh"` gate in a live panel query. Pulled exact `rise_*` Prometheus metric names for 4 previously-placeholder (`—`) textfile collectors in `02_service-map.md`, plus the offline-vs-pending fleet-rollup distinction.
- Wrote a new "RISE Health/Watchdog Framework" subsection into `02_service-map.md` and a new "Dashboard inventory" subsection into `03_communication-flows.md` (11-row table with UIDs/purpose).
- Manifest bumped v0.1.16 → v0.1.17; CHANGELOG.md entry added.
- Evidence basis: live `mcp-grafana-apn`/`mcp-grafana-nbn` reads this session (`search_dashboards`, `get_dashboard_summary`, `get_dashboard_panel_queries`) — not inferred from prior documentation.
- Not yet explored: Data Backlog (0 panels), the two RW-backlog dashboards, Servers Network/System Information (likely out of scope), RISE Dashboard (`rise-stage0_5`, older rollout view) — flagged in Open Items.

### 2026-08-03 — ClamAV freshclam root cause confirmed via WebSearch (v0.1.15 → v0.1.16)
- Operator asked what could be causing the fleet-wide ClamAV failure documented in the previous entry, rather than settling for the 3 open hypotheses already written up.
- Verified via `WebSearch` against `blog.clamav.net` and Cisco-Talos/clamav GitHub issues before answering, per the "never guess, verify" convention.
- Confirmed: ClamAV 0.103.x reached end-of-life for database updates on 2025-09-14; the CDN hard-blocks any 0.103.x client since then. This fleet runs 0.103.11/.12 uniformly. Explains the 10-month staggered failure-date spread from the fleet sweep exactly (each host trips the block on its own timer's first post-cutoff run, not simultaneously).
- Not cw-cluster-specific — documented upstream behavior affecting any fleet on this ClamAV branch. Fix: upgrade to 1.0/1.4 LTS (not yet done, no automated version pipeline exists for this cluster).
- Updated `13_known-issues.md` (bug row rewritten from "not investigated" to "confirmed"), `08_ansible-authoring.md`, `01_overview.md`; `manifest.json` gained a 3rd diagnostics entry.
- Manifest bumped v0.1.15 → v0.1.16; CHANGELOG.md entry added.
- Evidence basis: external sources (ClamAV's own EOL announcement, community-reported GitHub issues matching the exact error signature), cross-checked against this session's own captured data for consistency.

### 2026-08-03 — Full NBN Accelerate fleet sweep: 28 hosts, hardware inventory, fleet-wide ClamAV finding (v0.1.14 → v0.1.15)
- Operator asked for a thorough analysis of all NBN Accelerate sites (hardware + installed apps/scripts/services state), and to capture reusable scripts under `scripts/` with a justfile.
- Built `scripts/collect-fleet-health.sh` (new, flavor-agnostic, read-only, 4 bundled captures/host to stay tractable at fleet scale over satellite) and `scripts/fleet-health.justfile`. Ran against all 26 reachable `nbn_accelerate` hosts + both `nbn_wh` hosts (28 total, `aurukun-smc03` unreachable).
- First-ever live hardware inventory for this cluster: 11× BOXER-6641 + 15× BOXER-6404 (`nbn_accelerate`), 2× genuine Raspberry Pi/Cortex-A72 (`nbn_wh` — operator-confirmed `wh`-flavor equivalent).
- Major finding: `clamav-freshclam` confirmed failed on **26/26** `nbn_accelerate` hosts (up from the earlier 2), failure dates spanning 10 continuous months — an active, ongoing degradation.
- Mid-session, operator confirmed `nbn_wh`'s missing overlayroot is a planned rollout, not a bug — corrected that finding's framing before it shipped incorrectly.
- Also found and fixed real tooling bugs via dogfooding: a mid-run script-file edit that corrupted the first capture batch (11/28 hosts real, 17/28 crashed to zero-byte files, required a second batch run); a `just`-working-directory path assumption that silently broke all 3 quick-check recipes; a nested-directory `mv` bug when merging the two capture batches; the same exit-code-of-last-command false-negative from the earlier smc_ltp session, recurring in the justfile recipes.
- Other findings: kernel-version drift (5.15.0-79 to -133) corroborating the earlier no-automated-kernel-pipeline structural finding; `koonibba-smc01` at 95% disk usage with the oldest kernel; `isc-dhcp-server6` failed 28/28 (confirmed benign, IPv6 disabled by policy); `fwupd-refresh` failed on 3/28 (minor); `nbn_wh` zram/swap absence contradicting the platform table's universal RPi-zram claim (unresolved).
- Written to `07_hardware-overlay.md` (new hardware-inventory section), `13_known-issues.md` (bugs section rewritten for full fleet), `01_overview.md`, `08_ansible-authoring.md`, `04_dependency-tree.md` (separately, smc_ltp/ClamAV/Lynis entries + a flagged naming-collision question).
- Raw evidence relocated to `local-knowledge-ansible/ansible-wifi/issues/nbn-accelerate/fleet-hardware-audit-20260803/` per the pack's evidence-retention policy (skill-smc holds analysis/tooling, not case evidence).
- Manifest bumped v0.1.14 → v0.1.15; CHANGELOG.md entry added.
- Evidence basis: direct `tsh ssh root@<host>` read-only commands, this session, 28/28 hosts confirmed by file-size verification post-merge.

### 2026-08-03 — First live NBN Accelerate validation: cluster comparison confirmed, ClamAV CDN-block found (v0.1.13 → v0.1.14)
- Operator made `tsh login` for the NBN Accelerate cluster (`teleport.communitywifi.net.au`) available and invited exploratory commands — first-ever live access this pack has had to that cluster, after a full day of code-inspection-only NBN Accelerate content.
- Ran read-only diagnostics against `warakurna-smc01` and `indulkana-smc01` (both `nbn_accelerate`): Teleport domain, HTTPS-only portal (permanent redirect, on-box TLS termination), mobile-app backend, ClamAV+Lynis presence, Asterisk absence, non-`smc_ltp` DNS stack — every claim confirmed, 2/2 hosts.
- New finding: `clamav-freshclam.service` failing on both hosts (identical signature — exit 17, `Forbidden; Blocked by CDN`, permanent give-up) since 2026-06-21 (`indulkana`) / 2026-07-23 (`warakurna`) — ClamAV's virus database is stale/frozen on both, a real degradation of the documented cw-only security hardening. Not investigated further; no remediation attempted (read-only session).
- Written to `13_known-issues.md` (new "Known Operational Bugs (NBN Accelerate cluster)" section + coverage-gap row update), `08_ansible-authoring.md` (ClamAV/Lynis gate row), `01_overview.md` (evidence-basis paragraph), `manifest.json` (new `diagnostics` entry — first use of that field).
- Manifest bumped v0.1.13 → v0.1.14; CHANGELOG.md entry added.
- Evidence basis: direct `tsh ssh root@<host>` read-only commands, this session. `nbn_wh`/`cw` flavors and every other `nbn_accelerate` site beyond these 2 remain unvalidated.

### 2026-08-03 — project-coherence sweep: routing/architecture staleness fixed (v0.1.12 → v0.1.13)
- Ran `project-coherence` across today's cumulative content changes (NBN Accelerate gap-fill → smc_ltp exploration → 7-site correction → manual-mechanism confirmation). Content files (Tier 1) were already coherent from the piecemeal edits; this pass caught Tier 2/routing-layer drift.
- Fixed: `context-map.yaml`'s `ansible_authoring`/`smcbox_basics` routing descriptions (hadn't been extended to mention `smc_ltp`/onboarding or NBN Accelerate); `ARCHITECTURE.md`'s governance-pack size figure (stale "~125k chars" since 2026-06-26, now ~470k); `RUNBOOK.md`/`AI_NAVIGATION.md`'s `08_ansible-authoring.md` rows (extended to match the pattern already applied to `01_overview.md`).
- Stale-reference grep validated clean — all "old phrase" hits are correctly-framed historical narrative, no live incorrect claims.
- `.remember/today-2026-08-03.md` reviewed and found out of scope — self-managed by the global `remember` skill, not authored by skill-smc's own governance.
- Manifest bumped v0.1.12 → v0.1.13; CHANGELOG.md entry added; governance pack regenerated (final pass).
- Evidence basis: this session's own systematic file-by-file scan per the `skill-project-coherence` checklist.

### 2026-08-03 — smc_ltp/"low touch" mechanism confirmed: manual, unenforced step (v0.1.11 → v0.1.12)
- Final piece of the same-day `smc_ltp`/"low touch" thread: operator confirmed the mechanism is a manual step someone has to remember — no tooling automatically assigns `smc_ltp` membership for a new low-touch site, and nothing checks or enforces it.
- This directly explains the root cause of the 3-site gap fixed in the previous entry, and reframes it as an ongoing risk (any future low-touch site could be missed the same way), not a closed one-off.
- Added an explicit operational note to `08_ansible-authoring.md` ("smc_ltp Sub-Group") recommending membership be verified explicitly for future low-touch sites; updated the `13_known-issues.md` row's status and framing; `manifest.json` stable_fact updated, confidence raised to 0.92.
- Manifest bumped v0.1.11 → v0.1.12; CHANGELOG.md entry added.
- Evidence basis: operator-confirmed directly, relayed to this session; not independently verifiable from Ansible source (confirms an absence of automation, not a code finding).

### 2026-08-03 — smc_ltp/"low touch" correlation resolved: 3 sites added, 7 members confirmed (v0.1.10 → v0.1.11)
- Direct follow-up to the "low touch" onboarding entry below, same day: operator confirmed the previously-flagged correlation is real, not coincidental — every low-touch site is meant to be an `smc_ltp` member.
- Operator made and verified the fix directly in `ansible-wifi`: added `warburton_smc_ltp`/`beagle-bay_smc_ltp`/`umoona_smc_ltp` host groups + `:children` blocks to `inventories/rcp/prod`, matching the existing 4-site pattern. Verified via `ansible-inventory --list` (all 7 under `smc_ltp:children`) and `ansible-playbook --syntax-check smc_ltp.yml` (clean) — uncommitted, not yet run against any live SMC.
- Updated `smc_ltp` membership from 4 to 7 sites everywhere it's mentioned in this pack: `08_ansible-authoring.md`, `01_overview.md`, `02_service-map.md`, `13_known-issues.md`, `SKILL.md`, `05_troubleshooting.md`, `manifest.json`. The "flagged, not concluded" framing replaced with "resolved" throughout.
- Underlying mechanism (does low-touch tooling itself assign `smc_ltp` membership, or is it manual) remains unestablished — only the intended end-state membership is now confirmed.
- Manifest bumped v0.1.10 → v0.1.11; CHANGELOG.md entry added.
- Evidence basis: operator-directed and operator-verified change relayed to this session; not independently re-verified, not yet run against any live SMC or committed to `ansible-wifi`.

### 2026-08-03 — "Low touch" onboarding method and site deployment history added (v0.1.9 → v0.1.10)
- Operator relayed operator-confirmed install dates for a cohort of `rcp` sites, naming a "low touch" onboarding method: `guda-guda` pilot (2025-04-15), then `umoona`/`warburton`/`beagle-bay`/`pandanus-park`/`old-looma`/`new-looma` across 2026.
- Cross-checked against `local-knowledge-ansible/ansible-wifi/issues/apn/routing-issue/{CHANGELOG,SCRATCHPAD}.md` and root governance `SCRATCHPAD.md` — consistent, and those docs had already independently noted the same finding from the ansible-wifi side same day.
- Surfaced (this session) that all 4 `smc_ltp` sites are also low-touch sites — flagged as unresolved correlation, not concluded. Also grepped `ansible-wifi` for `low_touch`: exactly one hit, an orphaned host_var on an uninvolved host, never read by any role/playbook.
- New "'Low Touch' Onboarding Method and Site Deployment History" section added to `08_ansible-authoring.md`; `13_known-issues.md` gained an open-question row; the pre-existing "cnmaestro-provisioning internals" coverage-gap row updated to reflect the smc_ltp findings from the prior session.
- Manifest bumped v0.1.9 → v0.1.10; CHANGELOG.md entry added.
- Evidence basis: operator-provided dates, cross-referenced against `local-knowledge-ansible/ansible-wifi` docs and this session's own repo-wide grep; not live-validated against any site.

### 2026-08-03 — smc_ltp properly explored and documented (v0.1.8 → v0.1.9)
- Operator flagged smc_ltp as under-explored — a fair call: prior coverage was purely a side effect of the 2026-07-03 DNS RCA, never independently re-verified since.
- Direct read of `smc_ltp.yml`, `inventories/rcp/group_vars/smc_ltp.yml`, `inventories/rcp/prod`, `roles/smc_cnmaestro_provisioning/`, `roles/smc_dns_mgmt/tasks/main.yml` found and fixed two errors: membership undercount (was "only guda-guda", actually 4 sites — the INI-format `prod` file was missed by the original `.yml`-scoped grep) and a purpose mislabel ("cnMaestro mDNS" — actually two unrelated purposes: CNMaestro Cambium ePMP/cnPilot wireless-backhaul provisioning via a separate `smc_ltp.yml` playbook, and a DNS-resolver-stack switch to bind9/RPZ via `smc_bases.yml`'s `dns_mgmt` play).
- Findings cross-checked against an independent same-day pass on the ansible-wifi side — same conclusions reached.
- New "smc_ltp Sub-Group" section added to `08_ansible-authoring.md`; `01_overview.md`, `02_service-map.md`, `13_known-issues.md`, `SKILL.md`, `05_troubleshooting.md` corrected/cross-referenced. LTP's literal acronym expansion documented as an open question, not guessed.
- Manifest bumped v0.1.8 → v0.1.9; CHANGELOG.md entry added.
- Evidence basis: this session's direct file reads of ansible-wifi source; not live-validated against any of the 4 member hosts.

### 2026-08-03 — NBN Accelerate cluster gap-fill (v0.1.7 → v0.1.8)
- Operator-requested: document how the NBN Accelerate cluster (`cw`/`nbn_accelerate`/`nbn_wh`, `teleport.communitywifi.net.au`) differs from the APN cluster (`apn`/`rcp`/`rct`/`wh`, `teleport.apn.au`), since ~95% of prior content was APN-derived.
- Three parallel Explore-agent research passes: (1) inventory `group_vars`/`prod` diff across all 7 flavors — found cw-cluster is structurally thinner (no graylog/opensearch, no kernel-update Jenkins pipeline) with its own extras (mobile-app backend, kiosk mode, HTTPS-only portal, distinct blocked-URL redirect); (2) repo-wide grep for flavor-conditional branching in roles/templates — found the selector is `hotspot_flavor` (hardware class, spans both clusters identically) or `inventory_dir.split('/')|last` (exact flavor, drives a small number of genuine flavor-exclusive gates: ClamAV/Lynis on `nbn_accelerate` only, VoIP/Asterisk on `rcp` only), and nothing branches on the literal strings cw/community/communitywifi; (3) doc/ADR/OPA search in local-knowledge-ansible/ansible-wifi — found a "community wifi" naming collision (generic term for `rcp` sites in `issues/apn/routing-issue/`) and an OPA policy coverage gap (`flavors.json`/`environments.json` missing `cw`/`apn`/`rct`/`wh`).
- Wrote findings into `01_overview.md` (new comparison section + selector mechanism), `08_ansible-authoring.md` (new flavor-gate reference table), `10_captive-portal.md` (new §11.9 protocol diffs), `13_known-issues.md` (coverage-gap row + 2 new staleness-risk entries) — all explicitly labeled code-inspection-only, not live-validated.
- Routing tables (`RUNBOOK.md`, `SKILL.md`, `AI_NAVIGATION.md`) updated for the `01_overview.md` row; manifest bumped v0.1.7 → v0.1.8; CHANGELOG.md entry added.
- Evidence basis: this session's direct file reads + three Explore-agent research passes (no prior memory-keeper/project-context entry existed for this topic).

### 2026-07-31 — Full extraction pass + ssh-access/Teleport-domain corrections + feed-back governance broadening
- Exhaustive sweep of `local-knowledge-ansible/ansible-wifi/**` (operator-requested): ~15 new knowledge items across 8 reference files, 2 lint-gate scripts promoted/genericized, full coherence pass. v0.1.5 → v0.1.6.
- Operator corrected an invented ssh-manager MCP framing (twice) — access is direct `tsh ssh`, no MCP — and provided the confirmed flavor→Teleport-domain mapping, both fixed across `install.md`/`adapter.md`/`01_overview.md`/`13_known-issues.md`.
- Root-caused why the extraction pass found gaps at all: the cross-repo feed-back rule (this pack's `AGENTS.md` + ansible-wifi's `AGENTS.md`/`rule-002`/`task-patterns.md`/`validation.md`) was worded narrowly around "incident/debug fixes" and only named `project-coherence`, not `skill-slurp-chat`, as a trigger. Broadened all of it symmetrically to whole-tree scope, a wider knowledge-type list, both trigger points, and a closeout self-check. v0.1.6 → v0.1.7.
- Evidence basis: this session; memory-keeper keys `skill-smc.extraction.local-knowledge-sweep-20260731`, `skill-smc.correction.ssh-access-and-teleport-domains-20260731`, `skill-smc.governance.feedback-rule-broadening-20260731`

### 2026-07-03 (ansible-wifi session, project-coherence run) — DNS architecture corrections + garimba-smc01 failure mode
- Triggered by `project-coherence` on ansible-wifi after the garimba-smc01 DNS RCA (revisions 2-3) surfaced factual errors and a coverage gap in this pack's DNS documentation.
- `references/02_service-map.md`: fixed the DNS-resolver-by-flavor mental model (real gate is `smc_ltp` group, not flavor), fixed Stubby's documented listen port (60053, not 5353), added the previously-undocumented `systemd-resolved` host-DNS row and Stubby's single-upstream/no-failover autossh-local-forward chain.
- `references/06_failure-modes.md`: added the garimba-smc01 domain-specific DNS resolution delay failure signature.
- `references/13_known-issues.md`: added a coverage-gap entry for the host-DNS architecture and a new "Fleet-Wide Architecture Risks" section (Stubby no-failover, no monitoring on the autossh local forward).
- `.archcore/rules/rule-002-*.md` and `AGENTS.md` (both ansible-wifi): added an explicit DNS domain routing row — this domain had no routing entry, which is likely why the incident wasn't fed back into this pack sooner.
- Version bumped 0.1.3 → 0.1.4; CHANGELOG.md updated.
- Evidence basis: ansible-wifi 2026-07-03 session MK keys `ansible-wifi.smc.garimba-smc01.dns-rca-revision2-corrections.20260703`, `ansible-wifi.smc.garimba-smc01.dns-rca-revision3-corrections.20260703`, `ansible-wifi.smc.garimba-smc01.dns-repo-facts.20260703`

### 2026-06-26 (ansible-wifi session) — references/10-13 content updates + AGENTS.md project-coherence checklist
- `references/10_captive-portal.md`, `references/11_vagrant-lab.md`, `references/12_content-filtering.md` received content updates from ansible-wifi RUNBOOK audit: captive portal two-tier arch, Eclipse config.txt sync, PHP-FPM SetHandler, a2enconf alternative, PHP short_open_tag, vsmc networkd race chain, Eclipse identity model, MAC randomization table, CAKE fair queuing on bridge_501.
- Added `## Project-coherence checklist` to `AGENTS.md` — explicit Tier 1-4 update instructions for when project-coherence runs on skill-smc, plus cross-repo trigger rule for ansible-wifi sessions.
- Version bumped to v0.1.3; CHANGELOG.md updated.
- Evidence basis: ansible-wifi 2026-06-26 session MK keys `ansible-wifi.runbook.sections-11-12-13.20260626`, `ansible-wifi.runbook.gap-fill-audit.20260626`

### 2026-06-26 — Progressive-disclosure restructure
- Split 1724-line RUNBOOK.md into 13 numbered reference files (01_ through 13_).
- Moved KNOWN_ISSUES.md to references/13_known-issues.md.
- RUNBOOK.md replaced with 48-line navigation index.
- All cross-references updated; version bumped to 0.1.2.
- Evidence basis: session hook history (UserPromptSubmit context)

### 2026-06-26 — Pack audit and fixes
- Identified dead PROFILE.md reference in SKILL.md; removed.
- Fixed stale SYSTEM_PROMPT.md reference to monolithic RUNBOOK.md content.
- Confirmed adapter.md, install.md, manifest.json consistent with new structure.
- Evidence basis: direct file reads this session

### 2026-06-26 — Bootstrap governance scaffold + archcore promote + docs
- Added AGENTS.md, CLAUDE.md, AI_NAVIGATION.md, context-map.yaml, repomix.config.json, SCRATCHPAD.md.
- Initialized .archcore/, promoted 5 candidates (3 rules, 1 ADR, 1 spec).
- Added README.md, ARCHITECTURE.md.

### 2026-06-26 — Coherence sweep
- Fixed repomix.config.json: .archcore/ content now included; README.md, ARCHITECTURE.md, SCRATCHPAD.md added.
- Expanded adapter.md (5 → 16 rows) and spec file-roles (12 → 17 rows) to cover all governance files.
- Corrected ARCHITECTURE.md stale repomix count. Governance bundle: 145,706 chars.

---

## Next actions

- Root-cause the new-looma-smc01 31h outage (2026-08-01→2026-08-03) next time `tsh ssh` access to that site is available — check WAN/backhaul/power logs; confirm or rule out any link to the still-open `my_node_network_device_info` gap
- Explore the remaining unreviewed Grafana dashboards flagged 2026-08-03 (Data Backlog, RW-backlog pair, Servers Network/System Information, RISE Dashboard `rise-stage0_5`) next time Grafana access is used — see Open Items
- Cross-reference the RW-backlog dashboards against `autossh-prometheus-federation` in `02_service-map.md` once reviewed — may reveal federation-pipeline health signals not currently documented
- Install v0.1.17 to `~/.claude/skills/skill-smc/` per `install.md` (not yet done — same open item since v0.1.2)
- Propose/plan a fleet-wide ClamAV upgrade to 1.0 or 1.4 LTS next time remediation authorization is available — root cause confirmed 2026-08-03, no automated pipeline exists to do this without a deliberate rollout
- Fix mechanism found 2026-08-03 (memory-only so far, not yet in `references/13_known-issues.md`): `roles/smc_clamav/tasks/ubuntu.yml` installs with `state: present` (never upgrades an already-installed package) + this fleet's already-documented masking of `unattended-upgrades`/`apt-daily` compound to explain why ClamAV never self-healed. Canary-first remediation plan proposed to operator, not yet executed (offered a read-only `apt-cache policy clamav` check on a live host, awaiting go-ahead). If operator wants this folded into the pack's docs, run `project-coherence` — it currently only lives in memory-keeper key `skill-smc.discovery.clamav-fix-mechanism-20260803`
- Re-check `nbn_wh` overlayroot status after the operator's planned rollout lands
- `cw` flavor still has no site-level hosts to check (central-infra only); `aurukun-smc03` still unreachable — note if either changes
- Resolve the smc_ltp/generic-cnmaestro-provisioning naming-collision question flagged in `04_dependency-tree.md`
- Re-check the two unimplemented design recommendations (bonding, DNS resolved_stub) and the apt-lock-race duplicate-fix question next time this pack or ansible-wifi is touched
- On next ansible-wifi (or local-knowledge-ansible/ansible-wifi subfolder) session: invoke skill-smc first; both `skill-slurp-chat` and `project-coherence` must now check for unpromoted knowledge before closing out (broadened rule, 2026-07-31)
- Next time one of the 7 `smc_ltp` sites (`guda-guda`, `pandanus-park`, `old-looma`, `new-looma`, `warburton`, `beagle-bay`, `umoona`) is accessed via `tsh ssh`, live-validate the CNMaestro-provisioning and bind9/RPZ-DNS-switch documentation in `08_ansible-authoring.md` "smc_ltp Sub-Group"
- Confirm the `inventories/rcp/prod` `smc_ltp` group change gets committed in `ansible-wifi` and actually run against `warburton`/`beagle-bay`/`umoona` — currently a verified-but-uncommitted file-level change

---

## Memory pointers (navigation only)

- memory-keeper channel: `skill-smc` / keys added 2026-08-03 (this pass): `skill-smc.discovery.grafana-dashboard-inventory-rise-metrics-20260803`
- memory-keeper channel: `skill-smc` / keys added 2026-08-03 (earlier pass): `skill-smc.task.grafana-cw-exploration-blocked-20260803`
- memory-keeper channel: `skill-smc` / keys added 2026-08-03 (earlier pass): `skill-smc.discovery.clamav-fix-mechanism-20260803`
- memory-keeper channel: `skill-smc` / keys added 2026-08-03 (earlier pass): `skill-smc.correction.clamav-freshclam-root-cause-20260803`
- memory-keeper channel: `skill-smc` / keys added 2026-08-03 (earlier pass): `skill-smc.extraction.nbn-accelerate-full-fleet-sweep-20260803`
- memory-keeper channel: `skill-smc` / keys added 2026-08-03 (earlier pass): `skill-smc.coherence.routing-sweep-20260803`
- memory-keeper channel: `skill-smc` / keys added 2026-08-03 (earlier pass): `skill-smc.correction.smc-ltp-manual-mechanism-20260803`
- memory-keeper channel: `skill-smc` / keys added 2026-08-03 (earlier pass): `skill-smc.correction.smc-ltp-seven-sites-20260803`
- memory-keeper channel: `skill-smc` / keys added 2026-08-03 (earlier pass): `skill-smc.discovery.low-touch-onboarding-20260803`
- memory-keeper channel: `skill-smc` / keys added 2026-08-03 (earlier pass): `skill-smc.correction.smc-ltp-exploration-20260803`
- memory-keeper channel: `skill-smc` / keys added 2026-08-03 (earlier pass): `skill-smc.extraction.nbn-accelerate-cluster-gapfill-20260803`, `skill-smc.decision.nbn-accelerate-naming-20260803`
- memory-keeper channel: `skill-smc` / keys added 2026-07-31: `skill-smc.extraction.local-knowledge-sweep-20260731`, `skill-smc.correction.ssh-access-and-teleport-domains-20260731`, `skill-smc.governance.feedback-rule-broadening-20260731`
- memory-keeper channel: `skill-smc` / earlier keys: `skill-smc.structure.progressive-disclosure-20260626`, `skill-smc.audit.fixes-20260626`, `skill-smc.governance.bootstrap-20260626`, `skill-smc.governance.archcore-promote-20260626`, `skill-smc.docs.readme-architecture-20260626`, `skill-smc.coherence-sweep-20260626`
- memory-keeper checkpoint: `slurp-20260803-skill-smc-grafana-rise-dashboard-inventory` (ID: ce01b46c) — 401 context items; earlier today: `slurp-20260803-grafana-cw-blocked` (ID: cdb3b0ab) — 400 context items; earlier today: `slurp-20260803-skill-smc-clamav-fix-mechanism` (ID: d784984d) — 399 context items; earlier today: `slurp-20260803-skill-smc-clamav-root-cause` (ID: 609d0e06), `slurp-20260803-skill-smc-nbn-accelerate-fleet-sweep` (ID: eea021c1), `slurp-20260803-skill-smc-nbn-accelerate-live-validation` (ID: f293e11b), `slurp-20260803-skill-smc-coherence-sweep-close` (ID: fcb5bd7d), `slurp-20260803-skill-smc-ltp-manual-mechanism` (ID: a0b0525f), `slurp-20260803-skill-smc-ltp-seven-sites` (ID: 0e74230f), `slurp-20260803-skill-smc-low-touch-onboarding` (ID: 7c2ca18e), `slurp-20260803-skill-smc-smc-ltp-correction` (ID: d6fbd843), `slurp-20260803-skill-smc-nbn-accelerate-gapfill` (ID: 4052409c); earlier: `slurp-20260731-skill-smc-extraction-and-governance` (ID: 4fc94978), `slurp-20260626-skill-smc-governance` (ID: 7a4df5b2), `slurp-20260626-skill-smc-coherence` (ID: 85dae74b)
- project-context project ID: `0bf38158-d30f-4b0f-8653-f6f93d22a068` / checkpoint: `44e60b56-3e94-43fc-9ab8-23ab53a420a1` (2026-08-03, grafana-rise-dashboard-inventory); earlier today: `37a5570c-f630-45ec-9f98-1290c6fadaa9` (grafana-cw-blocked); earlier today: `6c74412b-4985-447d-8e8d-3b41a30c21d2`; earlier today: `3bdde77e-2467-40ff-b901-fc62af00e8ed`, `89ad9338-2f8d-4310-bc73-98426b36c17b`, `ec1c8cdd-403a-44cd-b801-855e30857430`, `15a8bedd-5d96-4695-a317-4ad3de431974`, `bc5e696a-2db0-4a1b-ba39-6915250fbb0e`, `0df101a9-ff28-4b63-b586-6763d9c2b4ce`, `60be456a-1295-4cca-bb57-358cdc54d21b`, `24964bec-35f6-41f9-bbff-015223d7f993`, `683aadef-e04b-4e0d-8cca-429f3cf2f67a`; earlier: `8564d8a7-eba1-405e-a019-4575a12311c5` (2026-07-31), `1b4851d2`, `e07d1aff`
````

## File: SKILL.md
````markdown
---
name: skill-smc
description: Use when working on ansible-wifi, ansible-malik SMC playbooks, dns_query PCAP processing, local SMC knowledge artifacts, or live SMC appliance issues. Covers Ansible authoring, URL capture/PCAP workflows, service architecture, communication flows, and troubleshooting.
metadata:
  short-description: SMC box operational knowledge and ansible-wifi authoring
---

# SMC: Operations and ansible-wifi Authoring

## Use When
Invoke for any of:
- Working on the `ansible-wifi` Ansible repo (roles, templates, inventory, topology vars)
- Working on `/Volumes/Data/_ansible/ansible-malik` SMC operator playbooks, especially URL-capture PCAP fetch/process workflows
- Working on `/Volumes/Data/_ai/_scripts/scripts_stuff/python/dns_query` when the change depends on SMC URL-capture PCAP layout, capture cadence, or reporting assumptions
- Writing or reading SMC local knowledge under `/Volumes/Data/_ansible/local-knowledge-ansible/ansible-wifi`
- Troubleshooting a live SMC box (service down, unreachable, wrong config, alert firing)
- Understanding communication flows between SMC boxes and external systems
- Adding a new site, VLAN, service, or feature to the SMC infrastructure
- Interpreting a Prometheus alert for an SMC host
- Determining blast radius of a topology or role change

## What an SMC Box Is
An SMC box is an **x86 PC** or **ARM64 Raspberry Pi** running **Ubuntu 20.04+ (22.04 in production)**, deployed as a managed WiFi hotspot and network gateway. All remote access routes through **Teleport** via a persistent `autossh` reverse SSH tunnel. SSH port on Teleport server = `50000 + site_eclipse_siteid`. Ansible connects via `ansible_host = {{inventory_hostname}}.teleport.<flavor>.au`.

**Critical — Overlayroot:** All SMC boxes run overlayroot. Writes go to tmpfs (`/media/root-rw/overlay`) and are **lost on reboot**. Ansible changes only persist if the lower dir (`/media/root-ro`) is remounted read-write first. Always check overlayroot status before assuming a change persisted.

## Related Workspaces

Treat these paths as part of the SMC working surface:

| Path | Relationship to SMC work |
|---|---|
| `/Volumes/Data/_ansible/ansible-wifi` | Production Ansible repo: roles, inventory, topology, SMC service deployment |
| `/Volumes/Data/_ansible/ansible-malik` | Operator playbooks for SMC operations, including `smc_get_pcapv*.yml` URL-capture fetch/process |
| `/Volumes/Data/_ai/_scripts/scripts_stuff/python/dns_query` | DNS reporting pipeline consuming SMC URL-capture PCAP output |
| `/Volumes/Data/_ansible/local-knowledge-ansible/ansible-wifi` | Local-only plans, reports, OPA artifacts, and SMC investigation knowledge for `ansible-wifi` |

When behavior, layout, or troubleshooting assumptions change in one of these surfaces, update the
corresponding references in the others during the same session where practical.

**project-coherence scope**: When running `project-coherence` on `ansible-wifi`, `RUNBOOK.md`
and the focused files under `references/` are external governed artifacts and must be included in
the coherence Tier 3 pass — check that they reflect any new findings, fixes, or architecture
decisions from the session.

---

## Troubleshooting Decision Tree

### Tier 1: Box Unreachable
| Check | Command | What to look for |
|---|---|---|
| autossh tunnel | `systemctl status autossh-teleport-openssh` | Active/failed; check last restart time |
| Network route | Prometheus: `NodeNetworkDefaultRouteInstability` | 4+ route changes in 60min |
| Overlayroot | `mount \| grep overlay` | Lower dir must be mounted |
| Teleport node | `systemctl status teleport` | Failed = no new sessions possible |

### Tier 2: Service Down (systemd failed)
1. `journalctl -u <service> --since "1h ago"` — what caused the failure
2. `systemctl list-units --state=failed` — other failed units
3. Check disk: `HostOutOfDiskSpace` (< 10%) / `HostOutOfInodes`
4. Config error? Check last Ansible playbook run output

### Tier 3: DHCP / DNS Not Serving Clients
- DHCP: `dhcpd -t -cf /etc/dhcp/dhcpd.conf` (config test); `grep -i error /var/log/syslog`
- DNS, non-`smc_ltp` hosts (all flavors — Unbound + Stubby, client path only): `unbound-checkconf`; `unbound-control status`; `systemctl status stubby`; config at `/etc/unbound/`, DoT upstream config at `/etc/stubby/stubby.yml` (Stubby listens on `127.0.0.1@60053`, single upstream `127.0.0.1@60853` via autossh local forward, no failover)
- DNS, `smc_ltp` hosts only (static `rcp` group, 7 sites — `guda-guda`, `pandanus-park`, `old-looma`, `new-looma`, `warburton`, `beagle-bay`, `umoona` — all "low touch"-onboarded sites; also runs CNMaestro Cambium backhaul provisioning, see `references/08_ansible-authoring.md`): `named-checkconf`; `rndc status`; verify zones loaded in `/etc/bind/`
- DNS, host's own resolution (separate from the two rows above — see `references/02_service-map.md`): `resolvectl status`; `systemctl status systemd-resolved`; `DNSStubListener=no` by default means the box's own `getaddrinfo()` bypasses Unbound/Stubby/BIND entirely

### Tier 4: WiFi AP Issues
- hostapd: `journalctl -u hostapd --since "1h ago"`
- CNMaestro provisioning: `systemctl status cnmaestro-provisioning`; check Redis: `redis-cli ping`; daemon log at `/var/log/cnmaestro-provisioning/`

### Tier 5: VoIP / Asterisk Issues
- `asterisk -rvvv` — Asterisk CLI
- Check generated extension config: `/etc/asterisk/extensions.conf`
- `asterisk -rx "dialplan show"` — verify dialplan loaded

### Tier 6: HA / Failover Issues
- VIP assignment: `ip addr show` — VIP should be on active node
- VRRP state: `journalctl -u keepalived --since "1h ago"`
- Conntrack limit: `cat /proc/sys/net/netfilter/nf_conntrack_count` vs `nf_conntrack_max`

### Tier 7: Monitoring Gaps
- Textfile collectors must update within their staleness window:
  - `sbdm.py` → `/var/lib/node_exporter/textfile_collector/sbdm.prom` — max 5400s (90min)
  - `smartmon.py` → `smartmon.prom` — max 5400s
  - `interfacecheckv2.sh` → `my_node_interfacecheck_success.prom` — max 450s
  - `apt_info.py` → `apt_info.prom` — max 450s
- Prometheus federation: check `autossh-prometheus-federation` tunnel service

---

## Key Prometheus Alerts Reference

| Alert | Trigger | First check |
|---|---|---|
| `HostOutOfDiskSpace` | < 10% free | `/var/log`, overlayroot upper dir fills |
| `HostOutOfInodes` | < 10% inodes | small file accumulation in `/tmp`, logs |
| `HostDiskWillFillIn24Hours` | predict_linear | find write rate source |
| `HostSystemdServiceCrashed` | unit state = failed | `journalctl -u <unit>` |
| `HostClockSkew` | offset > ±0.05s | `chronyc tracking` |
| `HostConntrackLimit` | > 80% conntrack | `ss -s`; check for connection leak |
| `NodeNetworkDefaultRouteInstability` | 4+ route changes/60min | VRRP flap, overlay issue |
| `NodeStarlinkInterfacecheckPacketLoss` | 100% loss 60min | starlink interface down |
| `sbdm_device_health_status == 0` | Samsung SSD degraded | SSD replacement needed |
| `smartmon_device_smart_healthy == 0` | SMART failure | drive health critical |

---

## Ansible Authoring: Key Rules

1. **Canonical source** = `inventories/*/topology_vars/<site>.yml`. Hidden `.*.yml` files are generated cache — never edit them directly.
2. **Cross-flavor impact**: group_vars or plugin change → all 7 flavors affected. Single topology_vars file → one flavor only.
3. **Validation order**: `yamllint` → `ansible-lint` → `ansible-inventory --list` → `ansible-inventory --host <site>` → `ansible-playbook --syntax-check`.
4. **Cache coherence**: delete `inventories/*/topology_vars/.<site>.yml` to force plugin regeneration (git checkout changes mtimes, making stale cache appear current).
5. **Generator drift**: when changing a topology pattern, check `roles/smc_generate_smc_files` templates — future site generation must stay consistent with current site changes.
6. **Overlayroot impact on Ansible**: changes deployed via `smc_bases.yml` only persist if the playbook remounts the lower dir rw. Verify with `mount | grep overlay` on the target.

---

## Communication Flows (Quick Reference)

**All inbound access** → Teleport proxy → autossh reverse tunnel → port 22 (SSH)

**Outbound from SMC:**
- `autossh` → `teleport.<flavor>.au` (persistent reverse tunnel)
- Prometheus federation → central Prometheus (via dedicated federation tunnel)
- `cnmaestro-provisioning` → CNMaestro WiFi Dashboard API
- `rsyslog` → Graylog (UDP syslog)
- `speedtest_exporter` → Ookla servers
- NBN Accelerate API (broadband management)

**Alerts:** Prometheus alertmanager → Teams (NOC webhook + dev webhook)

---

## Runtime Environments
- ansible-wifi tooling venv: `/Volumes/Data/_ai/_skills/skills-working-cache/ansible-wifi/venv`
- skill-smc specialist venv: `/Volumes/Data/_ai/_skills/skills-working-cache/skill-smc/venv`
- Ephemeral logs, pid files, and sockets belong under `/Volumes/Data/_ai/_skills/skills-runtime/<skill>/`.
- Prefer the working-cache venvs when running SMC validation tooling (`ansible-lint`, `yamllint`, `ansible-inventory`, `ansible-playbook`) to keep versions stable across sessions.

## References
- `RUNBOOK.md` — navigation index and reference-routing table.
- `references/01_overview.md` — SMC definition, inventory flavors, remote access, satellite constraints, APN vs NBN Accelerate cluster differences.
- `references/02_service-map.md` — service names, units, config paths, monitoring collectors, RCT/x86 differences.
- `references/03_communication-flows.md` — inbound/outbound communication paths.
- `references/04_dependency-tree.md` — dependencies between network, DNS, portal, monitoring, and access systems.
- `references/05_troubleshooting.md` — live incident triage, alerts, DHCP/DNS/WiFi/VoIP/HA issues.
- `references/06_failure-modes.md` — known failure signatures, root causes, and fix patterns.
- `references/07_hardware-overlay.md` — hardware differences, overlayroot, persistence, disk-write risk.
- `references/08_ansible-authoring.md` — topology vars, cache coherence, validation, generator drift.
- `references/09_url-capture-pcap.md` — URL capture v2, PCAP layout, fetch/process workflows, dns_query assumptions.
- `references/10_captive-portal.md` — captive portal, Eclipse config sync, Kohana issues, portal PHP (mod_php as www-data — NOT PHP-FPM).
- `references/11_vagrant-lab.md` — local Vagrant lab bring-up and virtualization issues.
- `references/12_content-filtering.md` — family-friendly VLAN 501 filtering, MAC randomization, CAKE.
- `references/13_known-issues.md` — coverage gaps, live-validation limits, and staleness risks.
- `scripts/` — reusable read-only diagnostic tooling for WAN-routing/topology-drift investigations (evidence capture, the "hook covers netplan" drift analyser, and a topology_vars-vs-live-hardware
  cross-check), plus generic ansible-lint pre-push/CI gate scripts (baseline refresh + delta gate); see `scripts/README.md`.

## Source
- specialist_type: project
- slug: skill-smc
- version: 0.1.2
````

## File: SYSTEM_PROMPT.md
````markdown
# skill-smc System Prompt

Use this when skill-smc is loaded as agent context (e.g., a dedicated SMC troubleshooting agent).

---

You are an expert on SMC (Site Management Controller) boxes and the SMC-related working surface:
`ansible-wifi`, `ansible-malik` SMC operator playbooks, `dns_query` PCAP/reporting scripts,
and local SMC knowledge under `local-knowledge-ansible/ansible-wifi`.

An SMC box is an x86 PC or ARM64 Raspberry Pi running Ubuntu 20.04+ (22.04 confirmed in production), deployed as a managed WiFi hotspot and network gateway. All remote access routes through Teleport. All SMC boxes run overlayroot — writes go to a tmpfs overlay and are lost on reboot.

You have deep knowledge of:
- SMC box architecture: 50+ running services, systemd unit names, config paths, flavor differences (RCT vs x86)
- Troubleshooting: structured tiers covering unreachable boxes, service failures, DHCP/DNS issues, WiFi/AP, VoIP, HA failover, and monitoring gaps
- Communication flows: Teleport tunnels, Prometheus federation, CNMaestro, Graylog, NBN API, speedtest
- Prometheus alerts: known alerts with first-check guidance
- Ansible authoring: topology_vars plugin, cache coherence, cross-flavor blast radius, overlayroot persistence
- Cross-repo SMC workflows: URL-capture deployment in `ansible-wifi`, PCAP fetch/process in `ansible-malik`, DNS workbook/report processing in `dns_query`, and local-only SMC plans/reports in `local-knowledge-ansible/ansible-wifi`

When troubleshooting:
1. Follow the tiered decision tree — do not skip tiers.
2. Check overlayroot status before assuming any change persisted.
3. Distinguish RCT (ARM64, Unbound+Stubby, zram, no asterisk, no keepalived) from x86 (BIND/named, traditional swap, Asterisk, keepalived).
4. If SSH execution tools are available, run commands rather than producing manual checklists.

When authoring Ansible:
1. Treat `inventories/*/topology_vars/*.yml` as canonical source.
2. Delete `.*.yml` cache files to force plugin regeneration after checkout.
3. Always check cross-flavor impact before committing group_vars or plugin changes.

Reference RUNBOOK.md for the reference-routing table. Load focused references on demand:
- `references/02_service-map.md` — service names, config paths, flavor differences
- `references/03_communication-flows.md` — inbound/outbound paths
- `references/04_dependency-tree.md` — dependency relationships
- `references/05_troubleshooting.md` — live incident triage
- `references/06_failure-modes.md` — known failure signatures and fix patterns
````
