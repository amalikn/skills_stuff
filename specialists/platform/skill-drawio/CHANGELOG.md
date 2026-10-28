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

- 20261027 Fold long flow pages (ROADMAP item built): `drawing.look.fold` (`off` default, `serpentine`, `z`) and `fold_after` (7), per flow
  `layout: {fold, fold_after}` (schema). New `scripts/flowmap/fold.py` (rows; each row routed by the ordinary router on a scratch page left to right, then
  copied, mirrored for a right-to-left row) and `scripts/flowmap/fold_turns.py` (arrows between rows through gutters). Operator review the same day: a
  short last row stretches the rows above, a one-lane flow keeps one swim lane for every row, a mid-row branch drops at once instead of a U turn.
  No-behaviour moves: `step_edges` to `flow_geometry.py`, `routing.draw_label` out of `route_forward`, `pages.flow_header`, `BACK_STYLE`/`BACK_MARK`;
  `draw_lanes` gains `lanes` and `least`. Fold off: all five consumers' drawings byte-identical (drift check). Tests in `tests/test_fold.py`
  (both styles audit clean, negative test); documented in references/visual-style.md.
- 20261027 Fold lane margins (operator review of the folded Decision order page): a folded lane ends a column gap plus `GAP` past the right
  gutter (was one `GAP`, matching an unfolded lane's room past its last box); a one-lane fold keeps `2 * GAP` above the first row and below the last.
  `scripts/flowmap/fold.py` `folded_page` only; fold off unchanged; 182 tests pass.
- 20261027 Incident, fixed before commit: the markdown PostToolUse hook flattened the 17 quoted Python excerpts in `references/visual-style.md`
  (Learned entries) into prose while the fold paragraph was edited. Rebuilt from HEAD plus the fold paragraph; the hook's tool fixed in scripts_stuff
  (`markdown_rewrap`, quoted fences kept verbatim) and the file reflowed with it: all 17 blocks and every word unchanged.
- 20261027 `drawing.look.last_row_align` (`left` default, `centre`): centres a part-filled last Overview grid row under the row above unless a group in it is pinned
  (`flowmap.overview_layout.centre_last_row`, schema, tests in `tests/test_group_layout.py`; documented in references/visual-style.md). Default unchanged, so every
  existing drawing renders byte-identical; skill-goal-guard opts in.
- 20261027 Parts are the standard for every flow map (operator, skill-goal-guard session): SKILL.md "Using the flow-map engine", README, AGENTS, SETUP; the example
  `examples/shop` is now `examples/shop/parts/master.yaml` plus eight parts, `flows.yaml` assembled (`just example` assembles then renders; drawing byte-identical). `split_flowmap.py`
  splits flows by `drawing.families` when a map has no section comments (tests in `tests/test_split_flowmap.py`).
  Learned 2026-10-27 in `references/data-first-diagrams.md` (parts are the standard).
- 20261027 `count_crossings.py --compare BEFORE`: every page of two versions, crossings and shared runs, exit 3 when a page got worse
  (`just count-crossings AFTER --compare BEFORE`); Learned 2026-10-27 (five entries) in references/layout-and-routing.md with screenshots
  `references/screenshots/20261027-labels-routing/`
- 20261027 Flow pages: a two-line arrow label on a vertical run sits across the line, number left of it and case right of it, two cells
  with no background (`route_costs.SPLIT_GAP`, cell `<arrow>-lbl-case`; operator). Flat runs and one-line labels unchanged; crossings unchanged
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

## 20261028_2318 — Engine performance review (read-only)

docs/performance-review-20261028_2317.md: profile of three consumers, hotspots A-I with in-memory proven byte-identical gains (UNC render 17.5 -> 5.95 s with A+B+C+D+G), crossing-count and search duplication, ranked shortlist. Nothing applied; operator approves each item (ROADMAP).

## 20261028_2306 — Placement searches: E2E columns, overview rows and group grid

- `scripts/flowmap/placement.py` (new): placement searches after barycentre, opt-in look keys `e2e_row_search`, `overview_row_search`,
  `overview_group_search` (schema, profile defaults false). Overview group placement: candidates from a hill climb and 24 seeded restarts,
  each routed for real, the fewest thick-arrow crossings kept (never worse than the map own placement; pinned groups stay). UNC overview
  245 -> 130 crossings; smc_change E2E 93 -> 43, PHP E2E 31 -> 13. Tests: `tests/test_placement_search.py`. Research of Graphviz dot,
  ELK layered, libavoid, ILP crossing minimisation in ROADMAP (not adopted).

## 20261026_2147 — Flow maps: quote yes/no decision labels

- `references/data-first-diagrams.md`: Learned 2026-10-26 - bare yes/no in a step's `when` parse as booleans and fail the schema; quote them (local-knowledge-ansible `76b0f86`).
