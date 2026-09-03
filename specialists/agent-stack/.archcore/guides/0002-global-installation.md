Title: Guide 0002 — Global installation
Category: operating-guide
Status: accepted
Promoted: 20260902_0245 by skill-ai-it promote
Accepted: 20260902_0300 by operator
Source: README.md
Summary: Symlink-only installation, preview first, and removal that only unlinks what still points here.

# Guide 0002 — Global installation

## Workflow

- `just global-status` — report the current symlink-only installation state.
- `just global-dry-run` — preview without changing any client directory.
- `just global-install install` — install every non-conflicting entry through verified symlinks.
- `just global-uninstall uninstall` — remove only links that still point exactly to Agent Stack sources.

## Rules

- Installation never overwrites a pre-existing entry and never copies content.
- `skill-creator` stays excluded by default.
