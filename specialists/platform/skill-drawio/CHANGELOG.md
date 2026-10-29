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

- 20261029 Learned 2026-10-29 in references/layout-and-routing.md: wireless topology views per site or sector, radial for PtMP, stored positions, node caps.

- 20261029 Slurp close. `scripts/consumer_check.py` (`just consumer-check`) and `consumers.yaml`: render every consumer (unified-network-controller,
  smc-resiliency, smc_change, skill-goal-guard, the example) to a scratch folder, timed, compare with a baseline (exit 3 when one differs),
  `--engine DIR` for an older checkout, `--look K=V` to measure a key before a project adopts it; never a consumer's own drawing. Promoted
  from the session's scratch harness; proved against a worktree of 245ead0: every consumer byte-identical except UNC, whose map now turns the
  searches on (unified-network-controller ec08930: 4555 -> 4277 crossings). skill-goal-guard was not in the hand-made proofs; it is identical.
  Schema descriptions of the three search keys now state the guards (b108050). Learned 2026-10-29 in references/layout-and-routing.md with
  screenshots; ROADMAP: Overview in-group arrows (21 of 24 thin crossings in UNC's OpenWISP group). Incident: a staging script opened two
  skill-coder files for writing before reading them and emptied them, with another session's uncommitted P-36 inside; rebuilt from HEAD plus
  that session's exact text (from its transcript), verified by line counts, and only this session's P-37/P-38 committed (29b39aa).

- 20261029 Speed review applied, one item per commit, each proved by `cmp` of the three consumers' renders (unified-network-controller,
  smc-resiliency, smc_change) against a baseline, plus `just test`: B no crossing count on a search undo; F `count_crossings --compare`
  parses each file once (4.1 -> 0.33 s); C E2E vertical-run spans kept in `_refresh` (stale-cache assert never fired); H one page build
  for render and audit, `render_flowmap --write --audit` in one pass (the audit now reads the drawn flow pages, family labels included;
  `--look` still refused when writing); D E2E crossings memoised per pair of distinct polylines. E (port index cache) was applied and
  reverted: 0.3 s, and it pushed `e2e_grid.py` past the 400-line rule. UNC render 18.3 -> 10.1 s (211 MB peak), smc-resiliency 1.05 ->
  0.84 s; all byte-identical. Not applied: A (reusing the search after a gap widens is identical today but not guaranteed: `_runs_ok`
  spacing changes with the stretch) and G (0.1 s); operator 2026-10-29: "time efficiency is not problem here". `e2e._swapper` moved to
  `crossing_search.swapper` and `render_flowmap.write` split from `main` (size rules). Also fixed: `flow_quality.py` without `--schema`
  failed on every map (its default was "", now the renderer's schema).
- 20261029 Layout quality analysis, first slice. `scripts/layout_quality.py` (`just layout-quality`): per page arrows, crossings, shared
  runs, bends, length, arrows through boxes (a label belongs to its arrow by id, else by centre when no arrow joins it) and overlapping
  labelled boxes; `--compare` exits 3 when a page got worse. Baseline: no arrow through a box and no overlap on any page of the three
  consumers; crossings are the problem, nearly all on End-to-end pages (UNC full E2E 3613, smc-resiliency 475) and UNC's Overview (245).
  With the opt-in searches on, UNC got worse on two pages (Onboarding 427 -> 506, Operator pages 44 -> 48: the E2E column search scores a
  grid estimate) and the Overview merged two thick-arrow pairs (shared runs 1 -> 3). Fixed: `flowmap.e2e.routed_e2e` routes and searches
  both column orders in full and keeps the searched one only when its real crossings are fewer; `placement.best_cells` keeps a candidate
  only with no more shared runs than the map's placement. UNC with the three look keys: 4555 -> 4277 crossings, Overview 245 -> 135,
  no page worse (compare exit 0). Existing drawings byte-identical; tests in `tests/test_layout_quality.py` and `tests/test_placement_search.py`.

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
