---
Title: Roadmap — skill-ascii-diagrams
Category: roadmap
Status: current
Authority: canonical
Scope: Planned and open work for the ASCII diagram pack
Last reviewed: 2026-11-17
Summary: >-
  The staged plan (operator, 2026-11-17: "snap, then graph"): stage 1 done; stage 2 graph renderer; stage 3 parser; the lessons from MonoSketch and a public
  diagram catalogue; whether a projects' own edge checker retires into this pack.
---

# Roadmap

## Current phase

**2026-11-17.** Stage 1 (repair existing diagrams) is done and the pack is split from skill-drawio; arrow lists line up; next, stage 2.

## Open

- [ ] **Stage 2: graph renderer** ([graph-layout.md](references/graph-layout.md)): a spec of boxes and links laid out with skill-drawio's rules (layered rows, barycentre order, channels with one track per arrow, port spreading,
  crossing-cutting swaps; reused by import) and A* routing on the character grid after mermaid-ascii `getPath` and `mergePath` (MIT), with a crossing penalty; logic in `scripts/ascii/`.
- [ ] **Stage 3: read a hand-drawn diagram into the stage-2 spec** ([reading-diagrams.md](references/reading-diagrams.md)): svgbob's fragments, contacts and `endorse_rect` (Apache-2.0), ditaa's boundary idea (LGPL: idea only),
  aafigure's claimed-cell mask; Unicode normalised to ASCII first (operator, 2026-11-17).
- [ ] **MonoSketch lessons** (Apache-2.0: reimplement with a NOTICE line): side-and-ratio attachment for stage 2, joint masks for stages 1 and 3.
- [ ] **A public diagram catalogue as a test corpus** (asciidiagrams.github.io, no licence: test input only, never copied into the pack).
- [ ] **A projects' own edge checker retiring into this pack** (proposed 2026-11-16): `edge_issues()` in `scripts/ascii_fix.py` carries its rule plus the branch-line and border-connector fixes; the
  move is that project's decision.

## Done

- [x] **Arrow lists line up** (2026-11-17): `align_arrows()` in `scripts/ascii/checks.py`, run by `ascii-fix`.
- [x] **Stage 1: repair existing diagrams** (2026-11-17): `ascii_fix.py` with `ascii/checks.py`; split from skill-drawio the same day.
