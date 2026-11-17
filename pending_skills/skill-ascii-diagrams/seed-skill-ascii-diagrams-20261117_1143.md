---
Title: Skill seed: skill-ascii-diagrams
Category: skill-seed
Status: draft
Authority: >-
  Design brief for a new skill pack, written by the operator with an agent; the pack is built from it with `new-skill scaffold` and the agent fills the references, scripts and evidence it lists
Scope: What the skill is for, what it is not, what it learned from real work, and every file the pack will hold
Last reviewed: 20261117_1143
Summary: >-
  Seed for skill-ascii-diagrams: purpose, boundaries, source material, lessons, routing, scripts, rules, evidence, acceptance scenarios and build order, in the form `new-skill` reads.
---

# Skill seed: skill-ascii-diagrams

<!-- seed: this file is the one input `new-skill` reads. Replace every `TODO(seed)` with content or delete the row; `new-skill check-seed` fails while one remains.
Write for the agent that will build the pack and has no other context: name files, give evidence, say what is decided and what is not. Keep prose
under 200 columns. Model packs to read before filling this in: skill-nautobot (version-sensitive platform), skill-vagrant (lab tool, guards),
skill-coder (practice with language overrides), skill-network-architect and skill-systems-architect (method packs with shared modules and an
operator layer). -->

## Contents

- [Parameters](#parameters)
- [Purpose and users](#purpose-and-users)
- [Trigger phrases](#trigger-phrases)
- [Non-goals and neighbours](#non-goals-and-neighbours)
- [Source material](#source-material)
- [What was learned](#what-was-learned)
- [Vocabulary](#vocabulary)
- [Outputs and artifacts](#outputs-and-artifacts)
- [Task routing](#task-routing)
- [Scripts plan](#scripts-plan)
- [Templates and assets](#templates-and-assets)
- [Standing rules](#standing-rules)
- [Safety boundaries](#safety-boundaries)
- [Evidence plan](#evidence-plan)
- [Acceptance scenarios](#acceptance-scenarios)
- [Write-back](#write-back)
- [Install and registry](#install-and-registry)
- [Deferred and extensions](#deferred-and-extensions)
- [Open questions](#open-questions)
- [Build order and done](#build-order-and-done)

---

## Parameters

One `key: value` per line; the scaffold reads only this block. `family` is the folder under the skills root: `specialists/project` (method or practice, any project), `specialists/platform` (one
product or tool), `skills` (single-file behavioural contract) or `personal`.

```text seed-parameters
name: skill-ascii-diagrams
family: specialists/project
short_description: ASCII diagrams in documents: draw from a spec, repair hand-drawn ones, check edges and arrows
aliases:
scripts: yes
operator_context: no
memory_channel: skill-ascii-diagrams
related: skill-drawio, skill-coder
forbidden_terms: APN, apn, smc-resiliency, unified-network-controller, UNC, enterprise-strategy
```

`short_description` is one line, at most 250 characters, in the form "what it covers: topic, topic, topic". It is the only text every session loads, so it must tell an agent when to pick this skill
and when not to. The full scope goes in `Purpose and users` and lands in SKILL.md's `## Full description`. `aliases` are slash shortcuts (for example `/skill-xyz`) and are registered in the global
instructions by the operator, not by this build. `related` lists the neighbouring skills, comma separated. `forbidden_terms` lists project, customer and people names (comma separated) that must never appear in the finished pack: a shared skill holds only what is true in every project, so the
scaffold refuses if one lands in a generated file. This seed stays in `pending_skills/` and is never copied into the pack, so it may name them while recording what was learned.

## Contents

- [Purpose and users](#purpose-and-users)
- [Trigger phrases](#trigger-phrases)
- [Non-goals and neighbours](#non-goals-and-neighbours)
- [Source material](#source-material)
- [What was learned](#what-was-learned)
- [Vocabulary](#vocabulary)
- [Outputs and artifacts](#outputs-and-artifacts)
- [Task routing](#task-routing)
- [Scripts plan](#scripts-plan)
- [Templates and assets](#templates-and-assets)
- [Standing rules](#standing-rules)
- [Safety boundaries](#safety-boundaries)
- [Evidence plan](#evidence-plan)
- [Acceptance scenarios](#acceptance-scenarios)
- [Write-back](#write-back)
- [Install and registry](#install-and-registry)
- [Deferred and extensions](#deferred-and-extensions)
- [Open questions](#open-questions)

---

## Purpose and users

An agent writing or reviewing documents can draw an ASCII diagram that stays aligned, and can take a diagram someone drew by hand (or an agent typed) and repair it without restyling it: ragged right
edges closed, borders redrawn to their box, connectors snapped into line, arrows that miss their box reported. Next it lays out a graph of boxes and links with orthogonal routing (stage 2) and reads a
hand-drawn diagram back into that graph (stage 3). ASCII is the immediate diagram of a document; draw.io is drawn only when explicitly asked (operator, 2026-11-16).

- Any project's agent writing Markdown documents (runbooks, designs, reports).
- The operator, asking to add, improve or fix the diagrams in a document.
- skill-drawio, which points here for ASCII.

## Trigger phrases

- "add/update and improve ascii diagrams where needed"
- "fix this diagram", "the right side alignment is not fixed", "the edges are ragged"
- "draw it as ASCII", "ASCII diagram", "text diagram", "box diagram in the doc"
- dictation: "ASP diagrams", "ask a diagram"

## Non-goals and neighbours

| Not this skill's job                                   | Owner                                                   |
| ------------------------------------------------------ | ------------------------------------------------------- |
| draw.io drawings, flow maps, exports                   | skill-drawio (only when explicitly asked)               |
| The facts a diagram shows (network, platform, product) | the domain skill                                        |
| Code practice for the scripts                          | skill-coder                                             |
| Mermaid, PlantUML, Unicode-drawn output                | not owned; Unicode is read later (stage 3), never drawn |

## Source material

| Source                                                | Where                                                              | Label                     | Capture                                     |
| ----------------------------------------------------- | ------------------------------------------------------------------ | ------------------------- | ------------------------------------------- |
| Operator rulings 2026-11-16 and 2026-11-17 (ASCII     | this session and skill-drawio CHANGELOG                            | USER_STATED               | not needed                                  |
|   first; fix existing diagrams; staged plan; own      |                                                                    |                           |                                             |
|   skill; ASCII now, Unicode read later; no alias)     |                                                                    |                           |                                             |
| The ASCII code and its tests                          | skill-drawio scripts/ascii_flow_render.py, scripts/ascii_fix.py,   | VERIFIED_PRIMARY          | moved into the pack                         |
|                                                       |   scripts/ascii/checks.py, tests/test_ascii_*.py (commits 49231b4  |                           |                                             |
|                                                       |   to 76c875f)                                                      |                           |                                             |
| Research into existing tools                          | research/research-20261117_1050.md                                 | VERIFIED_PRIMARY, some    | upstream files verbatim                     |
|                                                       |                                                                    |   UNVERIFIED marked       |   in documents/ascii-sources-20261117/      |
| Real documents swept (106 files, 243 diagrams,        | two project document trees                                         | VERIFIED_PRIMARY          | not needed                                  |
|   0.09 s)                                             |                                                                    |                           |                                             |

## What was learned

| Lesson                                                                                    | Evidence                                                           | Becomes                             |
| ----------------------------------------------------------------------------------------- | ------------------------------------------------------------------ | ----------------------------------- |
| A fixer must repair faults only and never restyle: equal chain widths and re-centred      | first sweep widened boxes chained over blank lines and moved       | rule; `--even-widths` opt-in;       |
|   arrows changed deliberate layouts                                                       |   arrows aligned on purpose                                        |   reference fixing-diagrams         |
| Two guards make every fix safe: the words in the same order, and no more edge findings    | tests mutation-proven; sweep showed the fixer never reports more   | rule; reference fixing-diagrams     |
|   than before                                                                             |   than the checker                                                 |                                     |
| A border may carry an arrow in (`+--v--+`) and a tee out (`+--+--+`); a grid is only an   | a design document's main box was never recognised, so its ragged   | reference reading-diagrams          |
|   inner `+` that continues inside as a wall                                               |   edge stayed (operator: "why is the right side alignment          |                                     |
|                                                                                           |   not fixed")                                                      |                                     |
| Text after a ragged row's edge moves with the edge (a box beside a short row is           | anchoring the tail to its old column pushed a neighbour box out    | reference fixing-diagrams           |
|   short too)                                                                              |   of line                                                          |                                     |
| A connector glued to an edge (` | --->`) stays glued | an inserted space broke arrows | test; reference fixing-diagrams |
| Edges that end having held nothing are a fan-out branch, not a broken box                 | the projects' checker reported two false positives                 | reference checking-diagrams         |
| Never write a generated file: fix its source and regenerate                               | `--apply` rewrote a rendered interface document; the check         | rule; guard in the fixer            |
|                                                                                           |   caught it                                                        |                                     |
| A ```text block of command output is not a diagram: tab and wide-character checks only    | an efibootmgr capture was flagged                                  | reference checking-diagrams         |
|   where a box is drawn                                                                    |                                                                    |                                     |
| Mutation tests in Python: a same-length mutation reuses a stale `.pyc`; run with `-B` and | a restored module kept failing                                     | test practice (skill-coder has      |
|   `touch` after restoring                                                                 |                                                                    |   the entry)                        |
| Hand-drawn arrows drift by a column; a renderer that pads every box keeps edges clean     | 18 diagrams drawn edge-clean (2026-11-16)                          | reference drawing-diagrams          |
| No existing tool parses a hand-drawn ASCII diagram into a graph and re-routes it; the     | research-20261117_1050.md                                          | reference extensions; stages 2      |
|   parts exist under permissive licences                                                   |                                                                    |   and 3                             |
| Real diagrams are plain ASCII (27 of 2156 Unicode) and about 80 columns wide              | asciidiagrams corpus                                               | rule: ASCII, 80 columns by default  |
|                                                                                           |                                                                    |   for new drawings                  |

## Vocabulary

- **Box**: a `+---+` border with `|` sides. **Grid**: boxes sharing edges. **Branch line**: a border-like run that fans arrows out and never closes.
- **Connector**: a run of single-arrow rows (`|`, `v`, `^`). **Exit**: text after a box's edge, `--> label`. **Tee**: a `+` on a border where a connector meets it.
- **Ragged edge**: a row whose right `|` is not in the border's column. **Restyle**: a change to a correct drawing (never done unasked).

## Outputs and artifacts

| Output           | Format and name                                            | Saved in     | Reader                      |
| ---------------- | ---------------------------------------------------------- | ------------ | --------------------------- |
| A drawn diagram  | ASCII on stdout, pasted into a ```text block               | the document | anyone reading the document |
| A fix plan       | unified diff on stdout                                     | not saved    | the agent and operator      |
| A fixed document | the same file, only its ```text blocks changed (`--apply`) | the project  | the project                 |

## Task routing

| Task                                                      | Reference file       | Contents                                                                                       |
| --------------------------------------------------------- | -------------------- | ---------------------------------------------------------------------------------------------- |
| Draw a new diagram for a document                         | drawing-diagrams.md  | the JSON spec (chain, grid, box, text, columns), widths, arrows, 80 columns                    |
| Repair an existing diagram                                | fixing-diagrams.md   | what is fixed, what is never touched, the guards, generated files, `--even-widths`             |
| Check diagrams and read the findings                      | checking-diagrams.md | edge rule, branch lines, arrows missing boxes, wide characters and tabs, command-output blocks |
| How diagrams are read (boxes, borders, grids, connectors) | reading-diagrams.md  | box recognition, tees and arrows on borders, grids, branch lines; stage 3 plan                 |
| Lay out a graph of boxes and links (stage 2)              | graph-layout.md      | plan: rows, barycentre order, channels and tracks, A* routing, crossing penalty                |
| What was researched and set aside                         | extensions.md        | upstream tools, licences, how to enable                                                        |

## Scripts plan

| Script                     | Does                                             | Origin                                          | Safety      | Test                          |
| -------------------------- | ------------------------------------------------ | ----------------------------------------------- | ----------- | ----------------------------- |
| scripts/ascii_flow_render.py | draw from a JSON spec                            | reuse (skill-drawio scripts/ascii_flow_render.py) | read-only   | tests/test_ascii_flow_render.py |
| scripts/ascii_fix.py       | repair existing diagrams; diff, `--apply` writes | reuse (skill-drawio scripts/ascii_fix.py)       | write-gated | tests/test_ascii_fix.py       |
| scripts/ascii/checks.py    | checks and connector snapping                    | reuse (skill-drawio scripts/ascii/checks.py)    | read-only   | tests/test_ascii_fix.py       |

## Templates and assets

- none (specs are written per diagram; examples live in the references).

## Standing rules

| Rule                                                | Reason                                             | Decided by                              |
| --------------------------------------------------- | -------------------------------------------------- | --------------------------------------- |
| ASCII first; draw.io only when explicitly asked     | ASCII is the immediate documentation               | operator, 2026-11-16                    |
| Fix faults, never restyle a correct drawing         | deliberate layouts were changed by the first fixer | operator, 2026-11-17 (agreed on review) |
| Never write a generated file; fix its source        | a rendered document was hand-edited                | operator, 2026-11-17                    |
| Words never change; no fix may add an edge finding  | a fix must be safe without a reviewer              | operator, 2026-11-17                    |
| Plain ASCII output; Unicode read later, never drawn | 27 of 2156 real diagrams use Unicode               | operator, 2026-11-17                    |

## Safety boundaries

- Reads: Markdown and plain-text files named on the command line.
- Writes: only the ```text blocks of a named file, only with `--apply`, never a file with a GENERATED banner.
- Never: network calls, other files, project facts in the pack.

## Evidence plan

| Claim                                                  | Evidence and source                                                                   | Falsifier                                           |
| ------------------------------------------------------ | ------------------------------------------------------------------------------------- | --------------------------------------------------- |
| The fixer changes only faulty diagrams                 | sweep of 106 documents, 243 diagrams: changes only where the edge checker             | a diagram the checker passes that the fixer changes |
|                                                        |   had findings                                                                        |                                                     |
| Words are never changed                                | guard plus mutation-proven test                                                       | a fixed block whose word sequence differs           |
| No existing tool parses and re-routes ASCII diagrams   | research-20261117_1050.md                                                             | a maintained tool that does both                    |
| Real diagrams are mostly plain ASCII within 80 columns | asciidiagrams agg.json counts                                                         | a corpus where Unicode is common                    |

## Acceptance scenarios

| Prompt                                                         | Expected behaviour                                                                                            |
| -------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------- |
| "fix the diagrams in docs/design.md"                           | run `ascii-fix` (diff), read it, `--apply`, re-run until clean, report what is left for a redraw              |
| "draw the boot flow as an ASCII diagram"                       | write a JSON spec, render with `ascii-flow-render`, paste into a ```text block, check edges                   |
| "why is the right edge of this box still ragged?"              | find why the fixer skipped it (border with tees, grid, generated file) and fix the cause, not the one diagram |
| "make a draw.io drawing of the flows"                          | not this skill: skill-drawio                                                                                  |
| "fix the diagram in the interface document" (a generated file) | stop: find its source, fix there and regenerate, or ask                                                       |
| "make all the boxes the same width"                            | style change: use `--even-widths` only because it was asked                                                   |

## Write-back

- Learned entries go to: the reference of the task (fixing-diagrams, checking-diagrams, reading-diagrams, drawing-diagrams); a code practice lesson to skill-coder.
- Stays in the project: which documents were fixed and their content.

## Install and registry

- Install targets: `~/.claude/skills`, `~/.codex/skills`, `~/.hermes/skills/domain` (symlinks to the canonical folder).
- Registry rows: `skills_stuff/.agents/skill-surfaces.md`, `skills_stuff/skills.md`; the calling project's `skills.md` where it lists skills.

## Deferred and extensions

| Item                                                                                         | Why not now           | Evidence                        | How to enable                               |
| -------------------------------------------------------------------------------------------- | --------------------- | ------------------------------- | ------------------------------------------- |
| Graph renderer (stage 2): A* after mermaid-ascii, skill-drawio's channels and crossing swaps | staged plan           | research-20261117_1050.md       | build in scripts/ascii/ per graph-layout.md |
|                                                                                              |                       |   pass 1                        |                                             |
| Parser (stage 3): svgbob fragments and rectangles, ditaa's boundary idea, aafigure's mask    | staged plan           | research pass 1                 | build after stage 2                         |
| MonoSketch side-and-ratio attachment and joint masks                                         | stage 2 and 3         | research pass 2                 | reimplement with a NOTICE line (Apache-2.0) |
| Unicode box drawing                                                                          | read later only       | operator 2026-11-17             | normalise to ASCII before reading           |
| Retire the projects' edge checker into this pack                                             | owned by              | skill-drawio ROADMAP            | ask that project's owner through its hub    |
|                                                                                              |   another project     |                                 |                                             |

## Open questions

| Question                                                   | Blocking | Owner                |
| ---------------------------------------------------------- | -------- | -------------------- |
| Does the projects' own edge checker retire into this pack? | later    | operator             |
| Stage 2 spec shape (boxes, links, labels, groups)          | later    | agent, then operator |

## Build order and done

<!-- The order the agent builds in and what done means. Keep the default unless the skill needs otherwise. -->

1. `new-skill check-seed` passes (no `TODO(seed)` left, every table filled or its row deleted).
2. `new-skill scaffold` plan read; then `--apply` writes the skeleton and copies this seed into the pack's `docs/`.
3. Run `skill-ai-it bootstrap` on the new folder (governance files, task runner, checker), then `just bootstrap` and `just check`.
4. Fill each reference from `What was learned` and `Source material`; every claim gets its `sources.yaml` row.
5. Write each script in `Scripts plan` with skill-coder: tests first, catalogue row, recipe, `code-map.toml` entry.
6. Turn `Acceptance scenarios` into `tests/scenarios.md`, run them, and record the result in `tests/eval-procedure.md`.
7. `skill_pack_check.py <pack> --strict` reports no error and no `planned` row; `just check` passes.
8. Install by symlink, add the registry rows, add the CHANGELOG `## Unreleased` line, and commit in `skills_stuff` (the operator decides when to push).
