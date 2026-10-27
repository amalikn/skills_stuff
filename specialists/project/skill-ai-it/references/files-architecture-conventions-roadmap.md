---
Title: skill-ai-it reference: Conditional files: ARCHITECTURE, CONVENTIONS, ROADMAP, SETUP
Category: reference
Status: current
Authority: local-supplement
Scope: On-need reference moved verbatim from SKILL.md
Last reviewed: 2026-10-14
Summary: >-
  Conditional files: ARCHITECTURE, CONVENTIONS, ROADMAP and (2026-10-14) SETUP; first moved verbatim from SKILL.md so SKILL.md stays an
  orchestration file within budget. Roles: governed-file-roles.md.
---

# skill-ai-it reference: Conditional files: ARCHITECTURE, CONVENTIONS, ROADMAP, SETUP

Moved verbatim from `SKILL.md` on 2026-10-10 to keep that file within its budget for files loaded whole. What each file is for, and what keeps it
there: [governed-file-roles.md](governed-file-roles.md). These are on-need files: an agent reads them when the task touches design, style or
setup, so they may be longer than the files loaded whole, but each opens with a front-matter Summary so it can be judged unopened (`just docs`).

#### ARCHITECTURE.md — create when: code, infrastructure, or design decisions are present, or user requests architecture documentation

Preferred source: derive from project inventory and content reads. No external template — write from analysis.

```markdown
---
Title: Architecture — <Project Name>
Category: architecture
Status: current
Authority: canonical
Scope: How <Project Name> works: components, data flow, boundaries
Last reviewed: <YYYY-MM-DD>
Summary: <One or two sentences: the shape of the system and its source of truth.>
Depends on: <comma-separated paths this describes, e.g. src/, config/; a commit to one flags this file for review (`just stale`)>
---

# Architecture — <Project Name>

## Overview

<One paragraph on what this project is and how its parts connect.>

## Components

| Component | Role |
|---|---|
| <name> | <purpose> |

## Data flow and source of truth

<Where data enters, where it is authoritative, what is derived from it. A diagram in a code block is fine.>

## Boundaries

<What this project owns and what it does not; the interfaces at the edge.>

## Key decisions

- <Decision or constraint that shapes the architecture>, because <reason>. (Link the ADR in `.archcore/adr/` when one exists.)
```

Keeps out: setup steps (SETUP.md), rules for agents (AGENTS.md), dated history (CHANGELOG.md). A superseded design moves to `docs/archive/`,
linked in one line, rather than staying as a section.

#### CONVENTIONS.md — create when: code files present, naming patterns exist, or style/linting rules are discoverable

Preferred source: derive from existing code and naming conventions. No external template.

```markdown
---
Title: Conventions — <Project Name>
Category: conventions
Status: current
Authority: canonical
Scope: Naming, style and anti-patterns in <Project Name>
Last reviewed: <YYYY-MM-DD>
Summary: <One sentence: the conventions that are not obvious from the code.>
---

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
| Done items  | Moved verbatim to `docs/history/roadmap-<stamp>.md` by `scripts/records/roadmap_trim.py` (run by `just rotate`) once older than 7 days; `` `PIN` `` keeps one |
| Closeout    | Update the phase and the items the work changed, at the same time as CHANGELOG and SCRATCHPAD                                 |

`adopt_governed_files.py` adds the header keys and the trim line in `rotate` to any project that has a ROADMAP.md; slurp runs it at every close.

```markdown
---
Title: Roadmap
Category: roadmap
Status: current
Authority: canonical
Scope: Current phase and open milestones of <Project Name>
Last reviewed: <YYYY-MM-DD>
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

#### SETUP.md — create when: setup needs more than a short README quick start plus `just bootstrap` (several prerequisites, pinned versions, environment variables, services to start)

Preferred source: the justfile's `bootstrap` recipe, `.mise.toml`, `requirements.txt` / `package.json`, `.env.example`. Never copy a secret value:
name the variable and where its value comes from. When setup fits in a few lines, put them under README's **Quick start** and do not create this
file. README links it from **Quick start**. Recipe renames reach it (`managed-blocks.md`).

```markdown
---
Title: Setup — <Project Name>
Category: setup
Status: current
Authority: canonical
Scope: Installing and running <Project Name>
Last reviewed: <YYYY-MM-DD>
Summary: <One sentence: what a working setup needs.>
Depends on: justfile, .mise.toml
---

# Setup — <Project Name>

## Prerequisites

| Tool | Version | Pinned in |
|---|---|---|
| <tool> | <version> | <.mise.toml / requirements.txt> |

## Bootstrap

`just bootstrap`, then `just check`.

## Environment

| Variable | Purpose | Source of the value |
|---|---|---|
| <NAME> | <what it configures> | <vault entry, .env.example; never the value> |

## First run

<The command that proves it works, and what success looks like.>

## Troubleshooting

- <Symptom> — <fix>
```
