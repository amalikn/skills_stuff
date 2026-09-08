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
