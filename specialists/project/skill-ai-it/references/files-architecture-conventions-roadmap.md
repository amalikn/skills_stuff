---
Title: skill-ai-it reference: Conditional files: ARCHITECTURE, CONVENTIONS, ROADMAP
Category: reference
Status: current
Authority: local-supplement
Scope: On-need reference moved verbatim from SKILL.md
Last reviewed: 2026-10-10
Summary: >-
  Conditional files: ARCHITECTURE, CONVENTIONS, ROADMAP; moved verbatim from SKILL.md so SKILL.md stays an orchestration file within budget.
---

# skill-ai-it reference: Conditional files: ARCHITECTURE, CONVENTIONS, ROADMAP

Moved verbatim from `SKILL.md` on 2026-10-10 to keep that file within its budget for files loaded whole.

#### ARCHITECTURE.md — create when: code, infrastructure, or design decisions are present, or user requests architecture documentation

Preferred source: derive from project inventory and content reads. No external template — write from analysis.

```markdown
# Architecture — <Project Name>

## Overview

<One paragraph on what this project is and how its parts connect.>

## Components

| Component | Role |
|---|---|
| <name> | <purpose> |

## Key decisions

- <Decision or constraint that shapes the architecture.>
```

#### CONVENTIONS.md — create when: code files present, naming patterns exist, or style/linting rules are discoverable

Preferred source: derive from existing code and naming conventions. No external template.

```markdown
# Conventions — <Project Name>

## Naming

| Thing | Pattern | Example |
|---|---|---|
| Time-bound docs | `<slug>-YYYYMMDD_hhmm.md` | `design-notes-20260422_1400.md` |
| <language> files | <pattern from existing code> | <example> |

## Code style

<Derived from existing code. List only rules that are non-obvious or project-specific.
Do not restate language defaults.>

## Anti-patterns

- <Pattern to avoid and why>
```

#### ROADMAP.md — create when: active development, TODOs present, migration/phase structure, or incomplete features detected

Preferred source: derive from TODOs, scratchpad, and memory systems. No external template.

```markdown
# Roadmap — <Project Name>

## Current phase

**Phase <N>:** <Description.>

## Next milestones

- [ ] <Milestone>

## Completed

- [x] <Completed milestone>
```
