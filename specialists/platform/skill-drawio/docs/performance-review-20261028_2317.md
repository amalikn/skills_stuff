---
Title: skill-drawio engine performance and design review
Category: reference
Status: current
Authority: local-supplement
Scope: Read-only review of scripts/drawio and scripts/flowmap against three consumers (smc_change, unified-network-controller, smc-resiliency)
Last reviewed: 2026-10-29
Summary: >-
  Measured profile, hotspots with in-memory proven gains (output byte-identical), duplication across page types and a ranked shortlist.
  Applied 2026-10-29: B, F, C, H, D (byte-identical, UNC 18.3 -> 10.1 s); E applied then reverted (0.3 s, module size); A and G not
  applied (operator: "time efficiency is not problem here"). See CHANGELOG 20261029.
---

# skill-drawio engine performance and design review (2026-10-28)

Read-only; each gain below was measured by patching functions in memory and comparing every output byte for byte (`cmp`) with the unpatched render. Machine: Apple M2 Max, Python 3.14.5 (working-cache
venv). `just test` passes (5.8 s).

## Runtime (render_flowmap --write to a scratch output)

| Consumer                   | Wall        | Where                                                                                      |
| -------------------------- | ----------- | ------------------------------------------------------------------------------------------ |
| unified-network-controller | 17.5-18.2 s | End-to-end page 86%; `improve` incl. a second full search started by `plan_loops` (12.1 s) |
| smc-resiliency             | 0.95-1.02 s | `improve` 1.1 s (profiled); the map's YAML parsed 3 times                                  |
| smc_change                 | 0.51-0.57 s | flow pages, `improve`, YAML x3                                                             |

UNC hotspots (own time): `route.count_crossings` 11.2 M calls 7.7 s; `e2e._crossings` 6.8 s; `e2e_grid._port_y` 4.27 M calls 3.4 s; `e2e_grid._verticals` 1.7 s. `--audit` renders every page again
(18.75 s); `count_crossings --compare` 5.9 s, 2.9 s of it XML parsing.

## Hotspots (measured on UNC unless stated)

| #   | Where                             | Problem                                                          | Gain                        | Safe change                                               |
| --- | --------------------------------- | ---------------------------------------------------------------- | --------------------------- | --------------------------------------------------------- |
| A   | `loops.plan_loops`                | full two-way search rerun when a gap widens; structure and       | 17.5 -> 10.1 s, identical   | snapshot structure + result before `_size`; restore       |
|     |   -> `_size(); _improve()`        |   result identical on all 5 reruns                               |                             |   exactly when unchanged (a polish round changed output)  |
| B   | `crossing_search` `_apply` on     | computes `_crossings(cids)` and discards it per trial            | 17.5 -> 14.7 s, identical   | `count=False` path or plain undo helper                   |
|     |   undo (:96, :248)                |                                                                  |                             |                                                           |
| C   | `e2e._runs_ok`                    | rebuilds every link's spans per call                             | ~2.6 s, identical           | span cache updated in `_refresh`, cleared in `_size`      |
| D   | `e2e._crossings` in `_try`        | "before" count recomputed with nothing moved                     | memo 1.6 s; pair matrix     | per-pair crossing matrix updated in `_refresh`            |
|     |                                   |                                                                  |   est. ~40% of `_crossings` |                                                           |
| E   | `e2e_grid._port_y`                | linear pool scan 4.3 M times                                     | est. 15-20% of the E2E page | `{(cid, end): index}` per pool, updated by every          |
|     |                                   |                                                                  |                             |   pool mutation                                           |
| F   | `count_crossings.py`              | 42-page file parsed 86 times; `read.pages` calls `cells()` twice | est. 5.9 s -> <0.5 s        | parse once per file                                       |
|     |   measure/page_runs               |                                                                  |                             |                                                           |
| G   | `model.read_map`                  | read 3 times per run                                             | 0.09-0.17 s, identical      | read once; `yaml.CSafeLoader`                             |
| H   | `render_flowmap.audit()`          | renders all pages again                                          | ~18 s per write+audit       | audit the pages `render()` built; `--write --audit`       |
| I   | `routing.cost`                    | rebuilds all segments per candidate                              | small                       | build once per `route_forward` edge                       |
|     |   / `route_costs._crosses`        |                                                                  |                             |                                                           |

A+B+C+D+G together: UNC 17.5 -> 5.95 s, smc-resiliency 0.95 -> 0.57 s, smc_change 0.51 -> 0.32 s, all byte-identical.

## Duplication

Crossings counted five ways: `route.count_crossings` (oriented runs), `audit.crossing` (segments; routing, route_costs, uncross, placement.routed_crossings, flow_quality), `placement._orth_cross`
(channel paths), `count_crossings.cuts` (exact `==`, audit allows 0.5 px), order estimates (`placement.row_crossings`, `grid_crossings`). "Alongside" thresholds differ: audit 3 px, route_costs 8,
count_crossings 8. Four local searches each repeat swap-recount-keep: placement (row_search, column_search, _climb), crossing_search._search, uncross.

Proposal (after A-F, not with them): `drawio/crossings.py` with one primitive on oriented runs, a `CrossingIndex` (incremental pair matrix) and a generic `search(candidates, apply, undo, touched)`:
real routing, strict drop to keep, start state wins ties. Overview (`best_cells`), E2E (`improve`) and flow pages (`uncross`) supply only candidates and routing. Preserve: strict-drop and
plain-wins-tie rules, visit order and fixed seeds, `tracks_together` as polish after the search (crossing_search.py:282, the 82 vs 56 lesson), uncross undo discipline, look keys `e2e_row_search`,
`overview_row_search`, `overview_group_search`, `e2e_loops`, `uncross`, `unshare`.

## Proof of no regression (per change)

`cmp` of all three consumers' renders against a baseline; `count_crossings.py AFTER --compare BEFORE` (exit 3 = a page got worse); `render_flowmap --audit`; `flow_quality.py`; `just test`; `just
example-check`; each consumer's drift check. G: compare loaded map dicts. Threshold unification: keep or migrate deliberately with before/after numbers in the CHANGELOG.

## Ranked shortlist

1. B skip the discarded undo count. 2. F parse once in count_crossings. 3. C span cache. 4. A reuse search result on unchanged structure
(add a look key to switch off). 5. H `--write --audit`. 6. E port index map. 7. D pair matrix, G one read_map + CSafeLoader.
8. Shared engine search loop last. Also: state a runtime budget for render_flowmap (e.g. UNC under 10 s) and record timings in the CHANGELOG.
