Title: Graphify README
Category: ai-governance
Status: current
Labels: graphify, skills_stuff, ai-files, governance
Last reviewed: 2026-04-28

# Graphify

Canonical workspace for local Graphify source, governance, and operator notes under `skills_stuff`.

## Purpose

This folder hosts the local Graphify upstream clone and project-local governance for maintaining and using Graphify in the managed AI stack. It is the source-of-truth workspace for local Graphify operations in this environment, not a runtime cache.

## Context

Graphify is used to build cross-file knowledge graphs from code and documentation corpora. The local upstream clone is maintained in `graphify-github/`, while operator-facing governance and planning artifacts live at this folder root.

## Folder index

- [graphify-github/](graphify-github/)
  Upstream Graphify source clone (Python package `graphifyy`, CLI `graphify`).
  Project entry: [graphify-github/README.md](graphify-github/README.md)

## Local install notes

- Graphify is locally installed on macOS via uv tool.
- Active CLI path: `/Users/malik.ahmad/.local/bin/graphify`
- Active interpreter path: `/Users/malik.ahmad/.local/share/uv/tools/graphifyy/bin/python`

## Governance pointers

- Local agent guidance: [AGENTS.md](AGENTS.md)
- Parent area guidance: [../AGENTS.md](../AGENTS.md)
- Canonical governance root: [/Volumes/Data/_ai/governance/README.md](/Volumes/Data/_ai/governance/README.md)
