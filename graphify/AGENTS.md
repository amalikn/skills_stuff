@../AGENTS.md

Title: Graphify Workspace Agent Policy
Category: agent-governance-guide
Status: current
Authority: local-supplement
Scope: Repo-local behavior for `/Volumes/Data/_ai/_skills/skills_stuff/graphify`
Last reviewed: 2026-04-28
Summary: Local rules for maintaining the Graphify workspace, upstream clone boundaries, and install/runtime notes.

# AGENTS.md

## Working rules

- Treat [graphify-github/](graphify-github/) as the upstream source clone boundary; do not mix local governance files into upstream package internals unless explicitly requested.
- Keep operator-facing notes and planning artifacts at the `graphify/` root.
- When changing local Graphify guidance, keep [README.md](README.md), [SCRATCHPAD.md](SCRATCHPAD.md), and parent indexes in sync.
- Keep time-bound markdown naming as `<slug>-YYYYMMDD_hhmm.md` for new dated artifacts.
- Prefer documenting local install/runtime facts explicitly when they affect operator workflows.
- Graphify local install in this environment is on macOS via uv tool (`/Users/malik.ahmad/.local/bin/graphify`); verify this path before proposing reinstall steps.

## Canonical governance linkage

- Parent area guidance: [../AGENTS.md](../AGENTS.md)
- Cross-repo governance root: [/Volumes/Data/_ai/governance/README.md](/Volumes/Data/_ai/governance/README.md)
