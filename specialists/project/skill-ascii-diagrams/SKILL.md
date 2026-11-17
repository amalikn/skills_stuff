---
name: skill-ascii-diagrams
description: >-
  ASCII diagrams in documents: draw from a spec, repair hand-drawn ones, check edges and arrows
---

# Ascii Diagrams

## Contents

- [Full description](#full-description)
- [Role and non-goals](#role-and-non-goals)
- [Read, write, and evidence boundaries](#read-write-and-evidence-boundaries)
- [Orient first](#orient-first)
- [Route the task](#route-the-task)
- [Verify version-sensitive facts](#verify-version-sensitive-facts)
- [Search before building](#search-before-building)
- [The pack's tools](#the-packs-tools)
- [Standing rules](#standing-rules)
- [Related skills](#related-skills)
- [Standing write-back contract](#standing-write-back-contract)
- [Evidence](#evidence)

---

## Full description

The listing shows a short description; this is the full scope.

An agent writing or reviewing documents can draw an ASCII diagram that stays aligned, and can take a diagram someone drew by hand (or an agent typed) and repair it without restyling it: ragged right
edges closed, borders redrawn to their box, connectors snapped into line, arrows that miss their box reported. Next it lays out a graph of boxes and links with orthogonal routing (stage 2) and reads a
hand-drawn diagram back into that graph (stage 3). ASCII is the immediate diagram of a document; draw.io is drawn only when explicitly asked (operator, 2026-11-16).

## Role and non-goals

Not this skill's job, and who owns it (this pack links to the owner and does not copy its facts):

| Not this skill's job | Owner |
| --- | --- |
| draw.io drawings, flow maps, exports | skill-drawio (only when explicitly asked) |
| The facts a diagram shows (network, platform, product) | the domain skill |
| Code practice for the scripts | skill-coder |
| Mermaid, PlantUML, Unicode-drawn output | not owned; Unicode is read later (stage 3), never drawn |

## Read, write, and evidence boundaries

- Reads: Markdown and plain-text files named on the command line.
- Writes: only the ```text blocks of a named file, only with `--apply`, never a file with a GENERATED banner.
- Never: network calls, other files, project facts in the pack.

## Orient first

1. Read the engaging project's own rules (`AGENTS.md`, its navigation file) before this skill; the project's rules outrank it. Keep project facts in the project.
2. The scripts are stdlib Python 3.11 or later: run them through this pack's recipes (`just bootstrap` once) or with the project's interpreter by path.
   Run `just ascii-fix <file>` (read-only) to see a document's diagrams and findings before changing anything.
3. Find the project's closing check (`just check`, CI) and its task catalogue; run catalogued tasks only.
4. Check the owning skill before stating a fact this pack does not own ([non-goals](#role-and-non-goals)).

## Route the task

Load only the reference the task needs.

| Task | Read first |
| --- | --- |
| Draw a new diagram for a document | [references/drawing-diagrams.md](references/drawing-diagrams.md) |
| Repair an existing diagram | [references/fixing-diagrams.md](references/fixing-diagrams.md) |
| Check diagrams and read the findings | [references/checking-diagrams.md](references/checking-diagrams.md) |
| How diagrams are read (boxes, borders, grids, connectors) | [references/reading-diagrams.md](references/reading-diagrams.md) |
| Lay out a graph of boxes and links (stage 2) | [references/graph-layout.md](references/graph-layout.md) |
| What was researched and set aside | [references/extensions.md](references/extensions.md) |

Reusable learning capture and engagement closeout: [references/evolution-and-write-back.md](references/evolution-and-write-back.md).

## Verify version-sensitive facts

Before asserting a current command, setting, API or release behaviour, read the version-matched official documentation and record its source and date in [sources.yaml](sources.yaml).
Use [compatibility.yaml](compatibility.yaml) only for its stated environment; an observed install is not behavioural proof. Record unknowns as unknown.

## Search before building

```text
desired outcome
  -> an existing capability of the tool or format in use
  -> an installed skill or script that already does it
  -> a maintained, compatible open-source component
  -> a new script or template, only when the acceptance test still cannot be met
```

At each step down, say why the step above cannot meet the acceptance test.

## The pack's tools

Catalogue with inputs, outputs and safety: [scripts/README.md](scripts/README.md).

| Script | What it does | Status |
| --- | --- | --- |
| `scripts/ascii_flow_render.py` | draw from a JSON spec (`just ascii-flow-render`) | built |
| `scripts/ascii_fix.py` | repair existing diagrams; diff, `--apply` writes (`just ascii-fix`) | built |
| `scripts/ascii/checks.py` | checks and connector snapping (imported) | built |

## Standing rules

| Rule | Reason | Decided by |
| --- | --- | --- |
| ASCII first; draw.io only when explicitly asked | ASCII is the immediate documentation | operator, 2026-11-16 |
| Fix faults, never restyle a correct drawing | deliberate layouts were changed by the first fixer | operator, 2026-11-17 (agreed on review) |
| Never write a generated file; fix its source | a rendered document was hand-edited | operator, 2026-11-17 |
| Words never change; no fix may add an edge finding | a fix must be safe without a reviewer | operator, 2026-11-17 |
| Plain ASCII output; Unicode read later, never drawn | 27 of 2156 real diagrams use Unicode | operator, 2026-11-17 |

## Related skills

- **skill-drawio**: draw.io drawings and flow maps, only when explicitly asked; its routing rules feed stage 2 here.
- **skill-coder**: how this pack's scripts are written and tested; code-practice lessons go there.

## Standing write-back contract

Invoking this skill, or doing its kind of work in any project without invoking it, obliges you to write back what the engagement taught before the session ends: a dated Learned entry in the
focused reference plus one CHANGELOG line under `## Unreleased`, read back after writing. Classify every engagement in one sentence (no new learning, verified update, candidate,
contradiction, project-only). Skill use never authorises a write to a live system, and this source is edited only when the task permits it; otherwise leave the entry in the engaging project
under `## skill-ascii-diagrams write-back candidates`. Format, classes and release reconciliation: [references/evolution-and-write-back.md](references/evolution-and-write-back.md).

**Evidence with every entry (operator, 2026-10-20; every calling project owes it).** A write-back that records how something is done carries a code or configuration excerpt of the few lines
that matter (source path and commit, secrets and customer identifiers removed) and, for a visual surface, a redacted screenshot under `references/screenshots/<YYYYMMDD>-<slug>/` with a
`readme.md` naming each image.

## Evidence

Load-bearing claims are in [sources.yaml](sources.yaml) (each with a falsifier); tested environments in [compatibility.yaml](compatibility.yaml); behaviour scenarios in `tests/scenarios.md`.
