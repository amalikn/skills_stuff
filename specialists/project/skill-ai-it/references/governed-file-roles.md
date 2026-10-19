---
Title: skill-ai-it reference: what each governed root file is for
Category: reference
Status: current
Authority: local-supplement
Scope: The root governance files skill-ai-it creates or audits in any project, and this package's own
Last reviewed: 2026-10-14
Summary: >-
  How agent context is loaded in tiers (small always-read files, detail on need, history on demand), one role per root file (README, AGENTS,
  CLAUDE, AI_NAVIGATION, ARCHITECTURE, CONVENTIONS, SETUP, ROADMAP, CHANGELOG, SCRATCHPAD), what enforces each, the placement test and the role check.
---

# skill-ai-it reference: what each governed root file is for

Operator, 2026-10-14: "define what each of these files mean ... what each of them would contain logically for any project", the skill must make projects adhere to it, and the files must use AI tokens
efficiently: "not too narrow so that the whole picture is not seen by the AI agent, but also we should not be bombarding it with information which is not required, and the AI agent should be able to
get more information when needed." The per-file templates stay in the `files-*.md` references; this file says what each file is for, and `scripts/role_check.py` enforces the part a script can decide.

## Contents

- [Loading model](#loading-model)
- [The files](#the-files)
- [How they relate](#how-they-relate)
- [Placement test](#placement-test)
- [Role check (audit and refresh)](#role-check-audit-and-refresh)
- [What is enforced, and how](#what-is-enforced-and-how)

## Loading model

Every root file sits in one tier. A tier decides how often an agent pays for the file, and therefore how small it must be.

| Tier                      | Files                              | When an agent reads it                       | Size rule                          | How it stays that size                          |
| ------------------------- | ---------------------------------- | -------------------------------------------- | ---------------------------------- | ----------------------------------------------- |
| 1. Always loaded          | AGENTS.md,                         | Every session, before any work               | 200 lines, 25 KB                   | Rules and pointers only; area rules move to a   |
|                           |   CLAUDE.md, AI_NAVIGATION.md      |                                              |                                    |   file read before that work                    |
| 2. Read whole at session  | SCRATCHPAD.md, CHANGELOG.md,       | Once per session, when the task needs state, | 200 lines, 25 KB                   | Rotation and trim move old entries verbatim to  |
|   start or on first touch |   ROADMAP.md, README.md, SKILL.md  |   history, plans or orientation              |                                    |   `docs/history/`                               |
|                           |                                    |                                              |                                    |   (`just rotate`, `just budget`)                |
| 3. On need                | ARCHITECTURE.md, CONVENTIONS.md,   | Only when the task touches design, style,    | No line budget; a front-matter     | `just docs <folder>` triage, `just outline` /   |
|                           |   SETUP.md, `references/`, `docs/` |   setup or that topic                        |   Summary so it is judged unopened |   `just section` to read one section            |
| 4. On demand              | `docs/history/`,                   | Only when a live file cites it or the        | None                               | `just history <term>`,                          |
|                           |   `docs/archive/`, trackers        |   agent searches                             |                                    |   `just history-show <stamp>`                   |

Three rules make the tiers work:

- **Summarise up, link down.** A tier 1 or 2 file states the conclusion and links the detail; it never copies it. Nothing is deleted to save tokens: rotation, trim and `move_sections.py` move text
  verbatim and leave a pointer, so the agent can always reach it.
- **One fact, one home.** A fact restated in two root files is paid for twice and drifts; the second file links to the first.
- **Every file can be judged unopened.** Front matter's Summary is what `just docs` shows, so an agent decides from one line whether to open it.

## The files

| File             | Tier | Reader                 | Holds                                                         | Keeps out                           | Changes by                                  |
| ---------------- | ---- | ---------------------- | ------------------------------------------------------------- | ----------------------------------- | ------------------------------------------- |
| **README.md**    | 2    | A person new to        | What it is and why, quick start (or a SETUP.md link), folder  | Agent rules, status and history,    | Edit in place when scope or layout changes  |
|                  |      |   the project          |   index, governance pointers                                  |   design detail                     |                                             |
|                  |      |                        |                                                               |   (link ARCHITECTURE.md)            |                                             |
| **AGENTS.md**    | 1    | Every AI agent (Codex, | Imperative rules: preflight, task runner, checks before done, | Design reasoning, history,          | Edit in place; short and imperative         |
|                  |      |   Claude,              |   companion rules, safety limits                              |   task lists                        |                                             |
|                  |      |   local models)        |                                                               |                                     |                                             |
| **CLAUDE.md**    | 1    | Claude Code only       | `@AGENTS.md` first, then Claude-only additions                | Anything that applies to            | Rarely                                      |
|                  |      |                        |                                                               |   every agent                       |                                             |
| **AI_NAVIGATION.md** | 1    | An agent arriving cold | Read order, source priority, task routing, what is canonical, | The rules themselves (AGENTS.md),   | Managed block via `just nav-upgrade`;       |
|                  |      |                        |   generated or transient, recovery; a rule summarised in at   |   the design (ARCHITECTURE.md)      |   preamble by hand when files move          |
|                  |      |                        |   most one line with its owner named                          |                                     |                                             |
| **ARCHITECTURE.md** | 3    | Whoever changes        | Components, data flow, source of truth, boundaries, key       | Setup steps, dated history, rules   | Edit in place when the design changes; a    |
|                  |      |   the structure        |   decisions with reasons                                      |   for agents                        |   superseded design moves                   |
|                  |      |                        |                                                               |                                     |   to `docs/archive/`                        |
| **CONVENTIONS.md** | 3    | Whoever writes code    | Naming, style, anti-patterns not obvious from the code        | Architecture, rules for agents      | Edit in place                               |
|                  |      |   or files             |                                                               |                                     |                                             |
| **SETUP.md**     | 3    | Whoever installs or    | Prerequisites, pinned versions, bootstrap, environment        | Design, history                     | Created only when setup outgrows README's   |
|                  |      |   runs it              |   variable names (never values), first run, troubleshooting   |                                     |   quick start plus `just bootstrap`         |
| **ROADMAP.md**   | 2    | Whoever decides what   | A dated current phase and open milestones by area (`- [ ]`)   | Done work (moves to history),       | Phase paragraph rewritten; done items leave |
|                  |      |   is next              |                                                               |   session state, decisions          |   by `just rotate` / `just budget`          |
| **CHANGELOG.md** | 2    | Anyone asking when and | Dated entries, newest first: what changed, why, where, in a   | Plans, speculation, current status, | Append (`just changelog-entry`); old        |
|                  |      |   why                  |   few lines                                                   |   long logs                         |   entries rotate                            |
|                  |      |   something changed    |                                                               |                                     |                                             |
| **SCRATCHPAD.md** | 2    | The next session       | Current state, open items, decisions pending promotion, next  | Durable facts (promoted out);       | Overwritten freely; rotates; durable        |
|                  |      |                        |   actions, short session log, pointers                        |   `KEEP` marks the few exceptions   |   items promoted                            |

`SKILL.md` exists only in a skill package: the orchestration contract loaded on invocation (tier 2, detail in `references/`). Templates: [files-readme-agents-claude.md](files-readme-agents-claude.md),
[files-records.md](files-records.md), [files-architecture-conventions-roadmap.md](files-architecture-conventions-roadmap.md) (also SETUP), [files-ai-navigation.md](files-ai-navigation.md).

## How they relate

```text
ROADMAP (next) ──done──▶ CHANGELOG (past, append only) ──rotate──▶ docs/history/  (on demand)
SCRATCHPAD (now, transient) ──promote──▶ ARCHITECTURE / AGENTS / ROADMAP / .archcore/
README (front door for people)        AI_NAVIGATION (front door for agents)
AGENTS (what an agent must do)        ARCHITECTURE (how it works and why)        SETUP (how to get it running)
```

## Placement test

Ask how long the sentence stays true. True this session: SCRATCHPAD. A plan: ROADMAP. A change that happened: CHANGELOG. True until the design changes: ARCHITECTURE. A standing instruction to agents:
AGENTS. How to install or run: README's quick start, or SETUP when it does not fit in a few lines. Then ask how often it must be read: if rarely, it belongs in a tier 3 file with a link from tier 1 or
2, not in the always-read file.

## Role check (audit and refresh)

`just govern` runs adoption, budgets and `just check`, then `just roles` (`scripts/role_check.py`), the mechanical part; `audit` reports its findings and the manual ones below, `refresh` fixes what can be fixed without moving the operator's content (front
matter, missing quick start, pointers) and reports the rest.

- Each file holds only what its row allows: no section repeated from another root file, no history in README or ROADMAP, no rules in ARCHITECTURE.
- README has a quick start or a SETUP.md link, a folder index whose links resolve, and no detail ARCHITECTURE.md already holds.
- ROADMAP has a dated current phase and open `- [ ]` items, and no completed-phase narrative.
- No root file states something another has since contradicted (a disabled tool still described as active, a layout missing current folders).
- Every root markdown file has `---` front matter with Title and Summary, except CLAUDE.md, whose `@AGENTS.md` line stays first.
- Tier 1 and 2 files are within budget, or held by the `doc_freshness.py` ratchet and named in the report.

## What is enforced, and how

Gate means a project's `just check` fails; ratchet means findings present when the project adopted the check are recorded in a baseline and only new ones fail, so old breaches shrink without blocking
work.

| Rule                                                                          | Mechanism                                                                                         | Strength         |
| ----------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------- | ---------------- |
| Front matter on root files (CLAUDE.md exempt)                                 | `role_check.py` rule `front-matter`; `adopt_governed_files.py` adds it at every slurp (legacy     | Gate, ratchet    |
|                                                                               |   blocks fenced, `Review by` 30 days on)                                                          |                  |
| CLAUDE.md opens with `@AGENTS.md`                                             | `role_check.py` `claude-import`; `nav-validate` warns                                             | Gate, ratchet    |
| README quick start or SETUP link; no status/history heading                   | `role_check.py` `readme-quick-start`, `readme-history`                                            | Gate, ratchet    |
| ROADMAP dated phase; no done items past 7 days or Completed narrative         | `role_check.py` `roadmap-phase`, `roadmap-done`; `roadmap_trim.py` from `just rotate` and         | Gate, ratchet    |
|                                                                               |   `just budget` (slurp)                                                                           |                  |
| No section duplicated across root files                                       | `role_check.py` `duplicate-section` (same title, bodies 80% alike); reworded copies need the      | Gate, ratchet    |
|                                                                               |   manual check                                                                                    |                  |
| Budgets: AGENTS, CLAUDE, AI_NAVIGATION, SCRATCHPAD, CHANGELOG, ROADMAP,       | `doc_freshness.py` `over-budget`; adopt adds README's key and grandfathers its size               | Gate, ratchet    |
|   SKILL, MEMORY; README via its `Budget` key                                  |                                                                                                   |                  |
| Record keys (Kind, Budget, Archive, Authority, Scope, Last reviewed)          | `adopt_governed_files.py` adds them; not a gate                                                   | Added at slurp   |
| README links resolve                                                          | the project's `check_governance.py` `SURFACES`                                                    | Gate             |
| ARCHITECTURE and SETUP reviewed when what they describe changes               | `Depends on` in their templates; `doc_freshness.py` flags a later commit                          | Gate once the    |
|                                                                               |                                                                                                   |   key is set     |
| context-map.yaml parses, no repeated key | `role_check.py` `context-map-parse` (PyYAML; reported skipped without it) | Gate, ratchet |
| Total loaded before work (CLAUDE.md, AGENTS.md and their `@` imports, AI_NAVIGATION.md) | `role_check.py` prints `always loaded: N files, X KB (~T tokens)` in `just roles` and `govern` | Report |
| AI_NAVIGATION managed block current                                           | `just nav-validate` (not part of `check`; run after an upgrade)                                   | Manual           |
| Nothing contradicted, no rules in ARCHITECTURE, no durable facts              | drift-audit section 14                                                                            | Manual           |
|   in SCRATCHPAD                                                               |                                                                                                   |                  |
