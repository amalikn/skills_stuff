Title: ADR 0002 — Canonical source, symlinked delivery
Category: architecture-decision
Status: accepted
Promoted: 20260902_0245 by skill-ai-it promote
Accepted: 20260902_0300 by operator
Source: ARCHITECTURE.md
Summary: This repository is the only authoring surface; global installs are symlinks back to it and never copies.

# ADR 0002 — Canonical source, symlinked delivery

## Decision

Skill and persona content is authored here and delivered by symlink. Runtime installs (`~/.claude/skills`, `~/.codex/skills`, `~/.agents/skills`) are never an
authoring surface.

## Rationale

A copy drifts silently across three agents. A symlink cannot.

## Consequences

- The installer never overwrites a pre-existing entry and never copies source content.
- "Fix it in the install and copy back" is not an available move.
