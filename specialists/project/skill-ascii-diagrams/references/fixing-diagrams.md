---
Title: Ascii Diagrams reference: Fixing diagrams
Category: reference
Status: current
Authority: >-
  skill-ascii-diagrams canonical reference; claims carry evidence labels and cite sources.yaml
Scope: Repair an existing diagram
Last reviewed: 2026-11-17
Summary: >-
  How `just ascii-fix` repairs a hand-drawn diagram: what it fixes, what it never touches, its guards (words unchanged, no edge finding added, generated files
  refused) and the opt-in style change `--even-widths`.
---

# Fixing diagrams

## Scope

Repair an existing diagram in a Markdown ```text block or a plain-text file. Drawing a new one: [drawing-diagrams.md](drawing-diagrams.md). What the checks
report: [checking-diagrams.md](checking-diagrams.md). Not covered here: see the non-goals in [SKILL.md](../SKILL.md#role-and-non-goals).

## Contents of this reference

- [Decision rules](#decision-rules)
- [Worked example](#worked-example)
- [Further reading](#further-reading)

## Decision rules

- **Run it as a plan first.** `just ascii-fix <file>` prints a unified diff of each block it would change and the findings left; read it, then `--apply`.
  Re-run until it reports nothing, then redraw what it lists as "not fixed" with the renderer. `VERIFIED_PRIMARY` (C-AD01).
- **Fix faults, never restyle.** A box's rows and borders end in one column: the border's width, grown only where text runs past it, keeping the padding
  space a row had. An arrow between chained boxes moves only when it points past them; one drawn inside their width stays. Equal widths along a chain are a
  style choice: `--even-widths`, only when asked. `USER_STATED` (operator 2026-11-17), `VERIFIED_PRIMARY` (a first version restyled deliberate layouts).
- **Borders may carry connectors.** An arrow into a box (`+--v--+`) and a tee out of it (`+--+--+`) are kept where they are when the border is redrawn. A grid
  is only a border whose inner `+` continues inside the box as a wall; grids are reported, not rewritten. `VERIFIED_PRIMARY`.
- **Text after a ragged edge moves with the edge.** A row one column short shifts everything after it on that row (an exit, a box beside it); closing the row
  puts them back in line. A connector glued to the edge (`|--->`) stays glued. `VERIFIED_PRIMARY`.
- **Connectors snap.** A single-arrow connector whose rows stray a column or two from its first row is moved back into that column. `VERIFIED_PRIMARY`.
- **Two guards.** The diagram's words stay in the same order, and the fix leaves no more edge or arrow findings than the drawing had; if either fails the
  block is left as it was and the reason is printed. `VERIFIED_PRIMARY` (C-AD02; both guards mutation-tested).
- **Never a generated file.** A file with a `GENERATED` banner is not written: fix the diagram in its source (the YAML or template it renders from) and
  regenerate. `USER_STATED` (2026-11-17, after a rendered document was hand-edited and its own check caught it).
- **Fix the cause, not the case.** When a diagram stays ragged after a run, find why the fixer skipped it (a border shape it does not read, a grid, a generated
  file) and change the fixer, with a test, so every document gains. `USER_STATED` (operator: "why is the right side alignment not fixed").

## Worked example

```text
before                                   after `just ascii-fix --apply`
+--------------------+                   +---------------------+
| Release trial boots   |                | Release trial boots |
| short |                 --> rejected   | short               | --> rejected
+-----------------+                      +---------------------+
```

The top border sets the width; the first row's text needs one more column, so the box grows by one; the second row's edge closes and its exit follows it;
the bottom border is redrawn to the same width.

## Further reading

- [checking-diagrams.md](checking-diagrams.md) for the findings the fixer leaves; [reading-diagrams.md](reading-diagrams.md) for how boxes are recognised.
- Upstream ideas: lewish/asciiflow `client/snap.ts` (MIT), verbatim in `documents/ascii-sources-20261117/`.
