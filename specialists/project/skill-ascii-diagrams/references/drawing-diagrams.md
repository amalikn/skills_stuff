---
Title: Ascii Diagrams reference: Drawing diagrams
Category: reference
Status: current
Authority: >-
  skill-ascii-diagrams canonical reference; claims carry evidence labels and cite sources.yaml
Scope: Draw a new diagram for a document
Last reviewed: 2026-11-19
Summary: >-
  Drawing a new ASCII diagram from a JSON spec with `just ascii-flow-render`: parts (chain, grid, box, text, columns), widths, arrows under the box centre,
  exits, plain ASCII within about 80 columns.
---

# Drawing diagrams

## Scope

Draw a new ASCII diagram for a document. Repairing an existing one: [fixing-diagrams.md](fixing-diagrams.md). A graph laid out automatically: [graph-layout.md](graph-layout.md) (planned).
Not covered here: see the non-goals in [SKILL.md](../SKILL.md#role-and-non-goals).

## Contents of this reference

- [Decision rules](#decision-rules)
- [Worked example](#worked-example)
- [Further reading](#further-reading)

## Decision rules

- **ASCII first.** A document's diagram is ASCII; draw.io only when explicitly asked (skill-drawio). `USER_STATED` (operator 2026-11-16).
- **Draw from a spec, never by hand.** Hand-typed diagrams drift by a column; the renderer pads every box to its width and puts each arrow at the box centre (`indent + 1 + width // 2`), so the edge
  check stays clean. `VERIFIED_PRIMARY` (18 diagrams drawn clean, 2026-11-16).
- **Spec parts.** A JSON list, stacked top to bottom: `chain` (boxes joined by arrows, each with an optional side `exit` and an arrow `label`), `grid` (rows of cells with shared edges), `box`, `text`
  (verbatim lines) and `columns` (parts side by side). `VERIFIED_PRIMARY`.
- **Exits read sideways, labels on arrows.** Put a failure path as a box's `exit` (`--> fails: ...`) and a short note on the arrow below as `label`; keep exit text on one line, or it spills across the
  next box's arrow. `VERIFIED_PRIMARY`.
- **Plain ASCII within about 80 columns.** Real diagrams in code are plain ASCII (27 of 2156 used Unicode) with a median width of 75 and a 90th percentile of
  80. `VERIFIED_SECONDARY` (C-AD04); Unicode is read later, never drawn (operator 2026-11-17).
- **Paste into a ```text block** with the lead-in sentence that says what it shows; then run `just ascii-fix <file>` and expect no change.

## Worked example

```json
[{"chain": {"width": 40, "indent": 2, "steps": [
  {"lines": ["Release trial boots"]},
  {"lines": ["Health probes"], "exit": "fails: trial rejected"},
  {"lines": ["Slot committed"]}
]}}]
```

`just ascii-flow-render spec.json` prints three 40-column boxes joined by centred arrows, the exit on the second box's first text line.

## Further reading

- `scripts/ascii_flow_render.py` (module docstring: the spec), `tests/test_ascii_flow_render.py`.
- The asciidiagrams.github.io catalogue (2156 diagrams from code comments; no licence: a test corpus only).
