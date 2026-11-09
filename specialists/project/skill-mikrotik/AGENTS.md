@../../../AGENTS.md

Title: skill-mikrotik Agent Policy
Category: agent-governance-guide
Status: current
Authority: local-supplement
Scope: skill-mikrotik specialist pack — canonical source for MikroTik site switch and AP knowledge in the SMC fleet
Last reviewed: 20261007
Summary: Agent guidance for maintaining and using skill-mikrotik: structure, reference routing, write-back and self-evolution loop, boundaries with skill-smc and skill-cambium.

# AGENTS.md

## Contents

- [Working rules](#working-rules)
- [Self-evolution loop](#self-evolution-loop)
- [Cross-project write-back trigger](#cross-project-write-back-trigger)
- [Project-coherence checklist](#project-coherence-checklist)
- [Governance coherence checks](#governance-coherence-checks)
- [Code changes](#code-changes)

---

## Working rules

- `SKILL.md` is the activation surface: triggers, the Standing Write-Back Contract, the decision tree and pointers to `references/`.
- `RUNBOOK.md` is the navigation index only. Content goes in the numbered `references/` files.
- `manifest.json` carries `version` and `updated_at`; bump both whenever a content file changes, and add a `CHANGELOG.md` entry.
- Read-only by default. Any RouterOS change needs the operator's explicit go-ahead, one device first, then a small canary, then the fleet.
- Never write a password or other secret value into any file. Reference: `<secret:keepassxc:Network/mikrotik switch & metal ap>`. Keep the substrings `credential`, `secret` and `password` out of file
  **paths** (the workspace OPA write-gate blocks them).
- `450gmk3_v1.1.py` in the pack root is the team's provisioning script, kept as a **read-only reference**: never edit, reformat or rename it. A change
  goes into our own version under `scripts/`, which follows this pack's rules (operator, 2026-10-08). It holds the admin password in clear text and is
  committed as is to the private repo (operator, 2026-10-08; commit `471c970`); never quote that value into another file (`references/06_provisioning.md`).
- Raw captures belong in the investigation folder under `local-knowledge-ansible/ansible-wifi/issues/`, not in this pack.
- Time-bound docs use `<slug>-YYYYMMDD_hhmm.md`; check the clock with `date` before writing a stamp.
- Every function in `scripts/` is documented in the style of ansible-wifi's `roles/smc_rise_watchdog/templates/rise_watchdog.py.j2`: a docstring with a summary line, then the reasoning and
  failure behaviour where they are not obvious; a comment block above every shell function; section banners in longer files. Code embedded as a string
  (the SMC agent in `scripts/snmp_via_smc.py`) counts. `just check` (`check_function_docs`) fails on an undocumented one (operator, 2026-10-07).
- Triage before opening: `just docs <folder>` gives one header line per file; run `just stale` before editing. Old CHANGELOG and SCRATCHPAD
  entries live in `docs/history/`; do not read them by default: `just history <term>` or `just history-show <stamp>` when a live entry cites one.

## Self-evolution loop

This pack is meant to grow from use, not from scheduled rewrites. Every session that touches a MikroTik:

1. **Before acting**, read `references/05_known-issues.md`: an open item may already describe the question, or the answer may close one.
2. **While working**, keep raw evidence in the investigation folder and note each new fact with its evidence label and date.
3. **Before reporting**, write each confirmed fact to its reference file (routing in `RUNBOOK.md`), promote any reusable script into `scripts/`, close or update `references/05_known-issues.md` items, add new
   ones for what is still unknown, bump `manifest.json`, add a `CHANGELOG.md` entry, update `SCRATCHPAD.md` current state, run `just check`, and read the changed files back.
4. **If a fact contradicts the pack**, correct the pack in place and say what changed in the CHANGELOG. Do not leave the old claim beside the new one.
5. **If the fact spans packs**, write it to skill-smc or skill-cambium as well in the same session.

## Cross-project write-back trigger

Invoking this skill from any project (ansible-wifi, local-knowledge-ansible, unified-network-controller, or a new one) carries the write-back obligation above. Both `skill-slurp-chat` and
`project-coherence` runs must check for unpromoted MikroTik knowledge before closing.

## Project-coherence checklist

1. Reference files (content) — `references/01..05`.
2. Navigation — `RUNBOOK.md` routing table, `SKILL.md` References list, `scripts/README.md` catalogue, `justfile` recipes.
3. Metadata — `manifest.json`, `CHANGELOG.md`, `SCRATCHPAD.md`.
4. Neighbours — skill-smc and skill-cambium Related Skills rows, ansible-wifi `AGENTS.md` invoke rule.

## Governance coherence checks

Run `just check` (`scripts/check_governance.py`, stdlib only) before claiming any durable change is complete. When it fails, fix the pack, not the check.

## Code changes

Invoke `skill-coder` before adding or changing any script in this pack (operator, 2026-10-20; the skills_stuff root rule): its rules apply
(purpose header, docstrings, `--apply` for writes, timeouts, tests, measured runtime) and the session owes it a write-back.
