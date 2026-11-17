---
Title: ASCII diagram tool sources (verbatim)
Category: reference
Status: current
Authority: external-source-capture
Scope: Verbatim upstream source files for parsing, routing and linting ASCII box diagrams
Last reviewed: 2026-11-17
Summary: >-
  Verbatim copies of permissively licensed upstream files studied for ascii_fix.py and the ASCII renderer. Saved with a .txt suffix so they never execute or get linted. Fetched 2026-11-17 via the GitHub API from the default branch.
---

# ASCII diagram tool sources

All files fetched 2026-11-17 from the default branch. Keep the licence and copyright notice with any code ported from them.

| File | Upstream URL | Licence | Why |
|---|---|---|---|
| svgbob-endorse.rs.txt | https://github.com/ivanceras/svgbob/blob/master/crates/svgbob/src/buffer/cell_buffer/endorse.rs | Apache-2.0 | Promote 4 touching line fragments to a rectangle |
| svgbob-contacts.rs.txt | https://github.com/ivanceras/svgbob/blob/master/crates/svgbob/src/buffer/cell_buffer/contacts.rs | Apache-2.0 | Group touching fragments into connected components |
| mermaid-ascii-arrow.go.txt | https://github.com/AlexanderGrooff/mermaid-ascii/blob/master/pkg/graph/arrow.go | MIT | A* orthogonal path search on the node grid |
| mermaid-ascii-mapping_edge.go.txt | https://github.com/AlexanderGrooff/mermaid-ascii/blob/master/pkg/graph/mapping_edge.go | MIT | Preferred vs alternative port choice, mergePath, label placement |
| asciiflow-snap.ts.txt | https://github.com/lewish/asciiflow/blob/main/client/snap.ts | MIT | Normalise each junction glyph to the neighbours it really connects to |
| box-diagram-validate.py.txt | https://github.com/ilia-pluzhnikov/box-diagram/blob/master/skills/box-diagram/validate.py | MIT | Stdlib Python lint: widths, wide chars, vertical connector continuity |
| aafigure-aafigure.py.txt | https://github.com/aafigure/aafigure/blob/master/aafigure/aafigure.py | BSD-style, clause count not checked (LICENSE.txt) | Python character-grid recogniser with a classification mask |
