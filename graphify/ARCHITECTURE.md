Title: Graphify ARCHITECTURE
Category: ai-governance
Status: current
Labels: graphify, skills_stuff, ai-files, governance
Last reviewed: 2026-04-28

# Architecture — Graphify Workspace

## Overview

This workspace is a local governance and source boundary around the upstream Graphify codebase clone. It separates operator-facing governance artifacts from upstream package source while preserving direct proximity for maintenance workflows.

## Component map

| Component | Path | Role |
|---|---|---|
| Workspace governance | `./` | Local governance files, plans, and operating notes |
| Upstream source clone | `./graphify-github/` | Canonical Graphify package source (`graphifyy`, CLI `graphify`) |
| Parent governance layer | `../AGENTS.md`, `../README.md` | Repo-level policy and routing context |
| Local install runtime | `/Users/malik.ahmad/.local/share/uv/tools/graphifyy/` | Active macOS uv-tool installation |

## Data / request flow

1. Operator or agent performs Graphify work in this workspace.
2. Source-level changes, when needed, happen in `graphify-github/`.
3. Local governance and project state are recorded at workspace root (`README.md`, `AGENTS.md`, `SCRATCHPAD.md`, roadmap artifacts).
4. Runtime execution uses local macOS installation (`/Users/malik.ahmad/.local/bin/graphify`) unless explicit alternate environment is requested.

## Key design decisions

- Keep upstream clone and local governance separated by directory boundary.
- Store operational install facts in governance docs to avoid redundant reinstall workflows.
- Inherit parent `skills_stuff` governance via `@../AGENTS.md`.

## Invariants — do not change without understanding

- `graphify-github/` remains the upstream code boundary.
- Local governance files at folder root remain the operator-facing source for this workspace.
- macOS local install paths must be validated before changing install guidance.
