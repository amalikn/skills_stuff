---
Title: Ascii Diagrams reference: Graph layout
Category: reference
Status: draft
Authority: >-
  skill-ascii-diagrams canonical reference; claims carry evidence labels and cite sources.yaml
Scope: Lay out a graph of boxes and links (stage 2, planned)
Last reviewed: 2026-11-17
Summary: >-
  The stage-2 plan: a spec of boxes and links laid out in layered rows with barycentre ordering, arrows in channels with one track each, ports spread on box
  sides, A* routing on the character grid with a crossing penalty, and crossing-cutting swaps. Not built yet.
---

# Graph layout

## Scope

Stage 2 (operator 2026-11-17, staged plan): turn a spec of boxes and links into a routed ASCII diagram, so a diagram need not be laid out by hand. Not built yet; this file is the design. Not covered
here: see the non-goals in [SKILL.md](../SKILL.md#role-and-non-goals).

## Contents of this reference

- [Decision rules](#decision-rules)
- [Worked example](#worked-example)
- [Further reading](#further-reading)

## Decision rules

- **Layout from skill-drawio's proven rules**: depth rows (a box above what it needs), placeholder slots for arrows that skip a row, barycentre sweeps to order each row, arrows only in channels
  between rows and columns with one track each, ports spread along a box side and ordered by the other end, interval tracks so short runs share a track, then swap neighbouring tracks or ports while
  crossings fall. Reuse skill-drawio's pure functions by import, never copy them. `VERIFIED_PRIMARY` for the rules in draw.io (skill-drawio references/layout-and-routing.md); `UNVERIFIED` on a
  character grid until built.
- **Route on the grid with A\*** (mermaid-ascii `getPath`, MIT): a priority queue over cells, boxes as obstacles, the preferred port tried first and the other kept when shorter, collinear steps
  merged; add a cost for crossing an existing route. `UNVERIFIED` until built.
- **Attach a link to a box side by ratio** (MonoSketch, Apache-2.0: reimplement with a NOTICE line): a moved or resized box re-derives the end. `UNVERIFIED`.
- **Output is plain ASCII within about 80 columns**, drawn edge-clean, so `ascii-fix` finds nothing to change.

## Worked example

Planned spec shape (open question): `{"boxes": [{"id": "a", "lines": ["..."]}], "links": [{"from": "a", "to": "b", "label": "..."}]}`.

## Further reading

- skill-drawio `references/layout-and-routing.md` (rows, channels, tracks, ports, crossing search).
- mermaid-ascii `pkg/graph/arrow.go`, `mapping_edge.go` (MIT), verbatim in `documents/ascii-sources-20261117/`.
