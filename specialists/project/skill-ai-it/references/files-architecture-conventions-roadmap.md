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

**What it is for (operator, 2026-10-14).** ROADMAP holds where the project stands and what comes next: a dated current phase and the open milestones,
grouped by area. It is not a log (that is CHANGELOG), not session state (that is SCRATCHPAD) and not a decision record (decisions go to the project's
register or `.archcore/adr/`). An agent reads it whole, so it has a budget like the other records.

| Rule        | ROADMAP.md                                                                                                                   |
| ----------- | ---------------------------------------------------------------------------------------------------------------------------- |
| Header      | Front matter with `Kind: roadmap`, `Budget: 200 lines, 25 KB` and `Archive: docs/history/ (roadmap-*.md, \`just rotate\`)`   |
| Budget      | 200 lines and 25 KB; `doc_freshness.py` holds it there (ROADMAP.md is in its default budget list)                             |
| Current phase | One dated paragraph (`**YYYY-MM-DD.**`), rewritten, not appended, when the phase changes                                    |
| Items       | `- [ ]` open, `- [x]` done; each names its owner when it waits on someone and links the document that holds its detail        |
| Done items  | Moved verbatim to `docs/history/roadmap-<stamp>.md` by `scripts/roadmap_trim.py` (run by `just rotate`) once older than 7 days; `` `PIN` `` keeps one |
| Closeout    | Update the phase and the items the work changed, at the same time as CHANGELOG and SCRATCHPAD                                 |

`adopt_governed_files.py` adds the header keys and the trim line in `rotate` to any project that has a ROADMAP.md; slurp runs it at every close.

```markdown
---
Title: Roadmap
Category: roadmap
Status: current
Summary: Current phase and open milestones; done items move to docs/history (just rotate).
Kind: roadmap
Budget: 200 lines, 25 KB
Archive: docs/history/ (roadmap-*.md, `just rotate`)
---

# Roadmap — <Project Name>

## Current phase

**<YYYY-MM-DD>.** <Where the project stands, in two or three sentences.>

## <Area>

- [ ] <Milestone> (<owner, when it waits on someone>; [detail](docs/...))

## Completed

Done items move to `docs/history/roadmap-*.md` (`just rotate`; find one with `just history <term>`).
```
