---
Title: Ascii Diagrams reference: Reading diagrams
Category: reference
Status: current
Authority: >-
  skill-ascii-diagrams canonical reference; claims carry evidence labels and cite sources.yaml
Scope: How diagrams are read (boxes, borders, grids, connectors)
Last reviewed: 2026-11-17
Summary: >-
  How the tools recognise a box in a character grid today (top border, corner columns, bottom border; tees and arrows on borders; grids; branch lines;
  nested boxes) and the stage-3 plan for reading any hand-drawn diagram into a graph.
---

# Reading diagrams

## Scope

How a diagram is read before it is fixed or checked. Not covered here: see the non-goals in [SKILL.md](../SKILL.md#role-and-non-goals).

## Contents of this reference

- [Decision rules](#decision-rules)
- [Worked example](#worked-example)
- [Further reading](#further-reading)

## Decision rules

- **A box starts at a top border**: a run `+-...-+` (it may hold `+`, `v`, `^`) with no `|` or `+` above its left corner. Its rows start with `|` in the left corner column; each row's right edge is
  the `|` nearest the border's right corner. It ends at the next row with a border run starting in the left corner column. `VERIFIED_PRIMARY`.
- **Tee or wall.** An inner `+` on a border is a connector's tee when the `|` continues outside the box, and a grid wall when it continues inside; only a wall makes it a grid. `VERIFIED_PRIMARY`.
- **Nested boxes** are read from the inside out; the outer box's rows keep the inner boxes as text. `VERIFIED_PRIMARY`.
- **Branch lines** (a `v` below a corner, or legs that hold nothing) have no bottom and are not boxes. `VERIFIED_PRIMARY`.
- **Stage 3 (planned)**: read any diagram into the stage-2 graph: cells into fragments and connected components, four touching fragments into a rectangle (svgbob `endorse_rect`, Apache-2.0), nested
  and shared edges by ditaa's open/closed boundary idea (LGPL: idea only), connectors traced with a claimed-cell mask (aafigure), joints by a 4-direction mask ANDed with what neighbours reach
  (MonoSketch, Apache-2.0); Unicode box drawing normalised to ASCII first. `UNVERIFIED` until built.

## Worked example

```text
   |
+--v-------+     top border with an arrow in: a box (the arrow is kept)
| ok       |
+--+-------+     bottom border with a tee out: still this box's bottom
   |
```

## Further reading

- [extensions.md](extensions.md) for the stage-3 sources and licences; `documents/ascii-sources-20261117/` for the verbatim upstream files.
