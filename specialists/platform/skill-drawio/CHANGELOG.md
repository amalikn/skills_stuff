---
Title: skill-drawio changelog
Category: log
Status: current
Authority: local-supplement
Scope: Release and governance history of the skill-drawio pack
Last reviewed: 2026-10-19
Kind: log
Budget: 200 lines, 25 KB
Archive: docs/history/ (`--find`, `--show`)
Summary: Release history and governance changes of skill-drawio; the release heading holds the version of record.
Last rotated: 20261026_1533
---

# Changelog

## Unreleased

- 20261027 Flow page arrow labels take their lane's colour as background instead of white (`route_costs.lane_colour`; operator:
  "remove white background from arrow text"); a long decision may widen to `look.decision_max_width` (560) to stay a diamond (operator:
  "disproportionately elongated vertically"). Placement unchanged; crossings unchanged on all three maps
- 20261027 Flow pages: a decision is sized to its text (starts at the step width, widens to `look.decision_aspect` 0.6, up to
  `decision_width`), not a fixed 380 px; an arrow label keeps 8 px from every box and is placed on the arrow's straight run, not on half of it
  (operator, smc_change Apply: "box 2 unnecessarily elongated", "text of arrow 2 too close to box 1"). Crossings unchanged on all three maps
- 20261027 E2E pages: a final polish swaps two crossing links' neighbouring vertical tracks and horizontal tracks together
  (`crossing_search.tracks_together`; operator: "2.3 and 2.7 overlap could have been avoided"); run after the searches, as a move
  inside them it steered the joint search to 82 crossings against 56. smc_change E2E 56 -> 50; smc-resiliency, UNC unchanged; time unchanged
- 20261027 Two arrows no longer merge at one decision corner (a shared corner costs as a crossed box; `unshare` pass redraws such a pair in the
  other order, `drawing.look.unshare`); branch labels are two lines, number then case (`label_size`, operator: "make this a standard"); the
  uncross pair repair also tries other exit sides, then paths ranked by fewest crossings, lets a third arrow step aside, and never keeps a
  result with more runs alongside another arrow. Measured: smc_change 11 pages, Apply 1 -> 1, PHP steps merge gone; smc-resiliency 533 -> 533
  (fw-x86 kept at 0 after the label change first made it 1); unified-network-controller 4569 -> 4555; render 1.1 s and 18.9 s, unchanged
- 20261027 Decision branches no longer cross each other: a branchy decision's reserved corners are free for its own branches, and a crossing
  between sibling branches costs COST_SIBLING_CROSS; Overview row gaps of up to 7 runs try every track order; Learned 2026-10-27 (two entries) in references/layout-and-routing.md
  (smc_change flows 88 -> 85 crossings, Overview 2 -> 0)
- 20261027 A one-flow family is labelled by its prefix alone; Learned 2026-10-27 in references/visual-style.md; test `test_one_flow_family_has_no_number`
- 20261027 Contract test reads changelog lines the budget rotation moved to docs/ (data-first-diagrams.md 2026-10-21 entries were logged, then rotated)
- 20261026 `e2e_page: false`, flow `tab`; near-lane gaps; arrows turn in gaps (`route_costs`, `branch_order`)
- 20261026 E2E in-column links always go right (last column too); far links may run along a free target row (`row_move`); Learned 2026-10-26 in references/layout-and-routing.md
- 20261026 Release 0.2.0 cut to keep this file within 200 lines and 25 KB (operator, 2026-10-26); 0.1.0 rotated to docs/history

## Reference moved out

Sections moved verbatim from this file (read on need; a citation by section name resolves there):
- [docs/changelog-reference-1-20261026_2147.md](docs/changelog-reference-1-20261026_2147.md): 0.2.0 — 2026-10-26.

## 20261026_2147 — Flow maps: quote yes/no decision labels

- `references/data-first-diagrams.md`: Learned 2026-10-26 - bare yes/no in a step's `when` parse as booleans and fail the schema; quote them (local-knowledge-ansible `76b0f86`).
