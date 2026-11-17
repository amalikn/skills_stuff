---
Title: Roadmap
Category: roadmap
Status: current
Authority: canonical
Scope: Current phase and open milestones of skill-drawio
Summary: Current phase and open milestones; done items move to docs/history (just rotate).
Kind: roadmap
Budget: 200 lines, 25 KB
Archive: docs/history/ (roadmap-*.md, `just rotate`)
Last reviewed: 2026-10-19
---

# Roadmap — skill-drawio

## Contents

- [Current phase](#current-phase)
- [Adoption in unified-network-controller](#adoption-in-unified-network-controller)
- [Engine and evidence](#engine-and-evidence)
- [Completed](#completed)
- [Engine performance review (2026-10-28) `OPEN`](#engine-performance-review-2026-10-28-open)
- [Layout quality analysis (2026-10-28, operator) `OPEN`](#layout-quality-analysis-2026-10-28-operator-open)
- [Overview in-group (thin) arrows (2026-10-29, operator: "Are arrows within a box on the overview page all ready optimized?") `OPEN`](#overview-in-group-thin-arrows-2026-10-29-operator-are-arrows-within-a-box-on-the-overview-page-all-ready-optimized-open)
- [Box placement research (2026-10-28, operator: "search them, don't incorporate at this stage") `OPEN`](#box-placement-research-2026-10-28-operator-search-them-dont-incorporate-at-this-stage-open)
- [Diagram-type sources to keep (2026-11-11, operator: "keep note of the two links") `OPEN`](#diagram-type-sources-to-keep-2026-11-11-operator-keep-note-of-the-two-links-open)

---

## Current phase

**2026-10-19.** Version 0.1.0 is built, installed (Claude, Codex, Hermes) and fully adopted by one project: unified-network-controller renders its flow map with `render_flowmap.py` from its map's
`drawing:` block and reads its as-built drawings with `drawio.read`, with no draw.io code of its own. Open work is proving the engine on a second project and closing the version and evidence gaps
below.

## Adoption in unified-network-controller

Detail and order: UNC's [retirement assessment](/Volumes/Data/_ai/_project/project_stuff/apn/unified-network-controller/docs/reports/project-reviews/skill-drawio-and-skill-coder-retirement-assessment-20261019_1841.md).

- [x] **As-built reader** — UNC `wc-local/scripts/site_onboarding/asbuilt_read.py` becomes a thin caller of `scripts/drawio/read.py` (its KMZ part stays there). Done when both site as-built sets read
  the same before and after.
- [x] **Engine tests move here** — UNC's `TextFits`, `NoteLayout`, `StepBoxLayout`, `LabelBoldTest`, `OverviewLayoutRules` and `AuditsCanFail` test this engine through UNC's wrapper; move them into
  `tests/test_helpers.py` (this pack has no text-fit, note, bold-label or failing-audit tests yet).
- [x] **UNC profile into its map** — UNC's kind colours, tiers and families move into a `drawing:` block in its `flows.yaml`; byte-identical render. Then its wrapper retires in favour of
  `scripts/render_flowmap.py` (one deliberate re-render: the banner names the new generator).

## Engine and evidence

- [x] **ASCII stage 1: repair existing diagrams** (operator 2026-11-17, staged plan "snap, then graph"): `ascii_fix.py` with `ascii/checks.py`; connector snapping
  (asciiflow's idea), wide-character and tab checks (box-diagram, MIT), arrows that miss their box, generated files never written.
- [ ] **ASCII stage 2: graph renderer** (operator 2026-11-17): a spec of boxes and links laid out with this pack's rules (layered rows, barycentre order,
  channels with one track per arrow, port spreading, crossing-cutting swaps) and A* routing on the character grid after mermaid-ascii `getPath`/`mergePath`
  (MIT; `documents/ascii-sources-20261117/`), with a crossing penalty; logic in `scripts/ascii/`.
- [ ] **ASCII stage 3: read a hand-drawn diagram into the stage-2 spec** (operator 2026-11-17): box recognition after svgbob's fragments, contacts and
  `endorse_rect` (Apache-2.0), nested boxes and shared edges after ditaa's documented boundary split (LGPL: the idea only), connectors traced with a
  claimed-cell mask (aafigure); then any diagram can be redrawn by stage 2.
- [ ] **UNC's ASCII grid renderer and edge checker join `ascii_flow_render.py` here** (proposed 2026-11-16, operator chose skill-drawio for ASCII tools): `ascii_box_render.py` and `ascii_box_check.py`
  live in unified-network-controller and smc-resiliency calls them by path; moving them is UNC's change, asked through the apn hub. Since 2026-11-17 `ascii_fix.py` carries the checker's edge rule as
  `edge_issues()`, so the checker can be retired into it once UNC agrees.
- [ ] **Archcore flow-map spec and adoption guide** — unblocked by the second project; write them (see `.archcore/index.guide.md`).
- [ ] **C-D16 on the current app** — re-check "static export draws orthogonal edges through boxes" on draw.io desktop 32.5.5 (checked only on 32.4.1; `compatibility.yaml`).
- [ ] **Python 3.11 floor** — `mise install python@3.11`, then `just test-matrix` (3.11 is not installed, so the declared floor is untested).
- [ ] **SCRATCHPAD's "Open items tracker: this file" is read as a path** (seen 2026-11-06 and at 87f5356): `just rotate --apply` moves open items into a tracked file named `this`. Point the header at
  a real tracker (or the skill-ai-it rotate tool should treat "this file" as SCRATCHPAD itself). Done when a rotation leaves no file named `this`.
- [ ] **Banner breaks on a path containing `--`** (found 2026-11-06): `render_flowmap.py --write` raises "banner part contains '--', illegal in an XML comment" when the map or output path holds `--`
  (Claude scratchpad paths do); escape or replace `--` in banner parts. Done when a map under such a path renders and the drift check still matches.
- [ ] **E2E dependency connector picks the nearest actor, not the writer** (found 2026-10-26, smc-resiliency flow 14 `box-operation`): a store the flow's steps write (`writes:` on the agent's steps)
  is joined by its dashed line to UNC, the nearest actor, rather than to the component that writes it; prefer the actor whose steps name the store in `reads`/`writes`. Screenshot: smc-resiliency
  drawing page 11 (E2E: On-box operations).
- [ ] **Redaction test decision** — vendor captures under `documents/drawio-sources-20261019/` hold example private addresses from the vendor docs; decide before adding a redaction test like
  skill-nautobot's (verbatim captures are exempt by design).

## Completed

Done items move to `docs/history/roadmap-*.md` (`just rotate`; find one with `just history <term>`).

## Engine performance review (2026-10-28) `OPEN`

Read-only review, nothing applied; the operator approves each item: `docs/performance-review-20261028_2317.md`. Measured A+B+C+D+G together: UNC render 17.5 -> 5.95 s, byte-identical. Order: B, F, C,
A, H, E, D+G, then the shared crossing/search engine.

## Layout quality analysis (2026-10-28, operator) `OPEN`

Not part of the speed review. Done 2026-10-29: the baseline tool (`just layout-quality`, CHANGELOG 20261029) and real-route guards on both placement searches (E2E column order, Overview group grid).
Baseline: crossings only (no arrow through a box, no overlap), nearly all on End-to-end pages. Next: E2E placement searched on real routes rather than only guarded (each swap routed; UNC's full E2E
page holds 3471 crossings with the search on); routing (port order, channel track nudging as libavoid, orthogonal routing as ELK); overview channel routing (most of UNC's 135 remaining Overview
crossings). UNC's schema still lacks the look keys `e2e_row_search`, `overview_row_search`, `overview_group_search` (the project's change, not this pack's).

## Overview in-group (thin) arrows (2026-10-29, operator: "Are arrows within a box on the overview page all ready optimized?") `OPEN`

No. UNC Overview after ec08930: thin arrows 24 crossings, 21 inside the OpenWISP group (screenshot `references/screenshots/20261029-unc-overview-real-route/overview-after.png`); thick arrows 111.
Today only the box order within a row (`overview_row_search`) and `route.untwist` act inside a group. Next: order each box's bottom ports by target x (and entry ports by source x), order the tracks in
each row gap by bend direction, keep an arrow that skips a row clear of the row between; each kept only when `layout_quality.py --compare` shows the page no worse (P-38 in skill-coder).

## Box placement research (2026-10-28, operator: "search them, don't incorporate at this stage") `OPEN`

Built (`scripts/flowmap/placement.py`, opt-in look keys): `e2e_row_search` (E2E column order, grid estimate): smc_change E2E 93 -> 43, PHP E2E 31 -> 13. `overview_row_search` (group rows): UNC 245 ->
243. `overview_group_search`: candidate placements (map's own, hill climb, 24 seeded restarts as Graphviz/ELK do) each routed for real, fewest thick-arrow crossings kept: UNC overview 245 -> 130
(-47%), never worse than the map's placement; pinned groups (group_cell) stay. Proxies alone misled (straight lines: 131 then 182 with more restarts; channel paths: 192/171). Next: one engine loop for
every page type (candidates, real routing, count, keep best); the E2E column search still scores a grid estimate. UNC's own schema copy lacks the new keys. Candidates for a principled next step, not
adopted:
- Graphviz dot ordering (Gansner, Koutsofios, North, Vo 1993, IEEE TSE 19(3)): weighted median plus local transpositions; crossing minimisation on layered graphs is NP-complete, so heuristics.
- Eclipse Layout Kernel (ELK) layered: cycle breaking, layering, crossing minimisation, node placement, orthogonal routing with port constraints; elkjs is its JavaScript build.
- Adaptagrams libavoid (Wybrow, Marriott, Stuckey, GD 2009): orthogonal connector routing minimising length and bends; used by Inkscape; libtopology for topology-preserving improvement.
- Exact one-sided crossing minimisation by ILP (Wilson et al., IEEE VIS 2024); OGDF ships Sugiyama crossing-minimisation heuristics.
Sources: https://uspto.report/patent/grant/4953106 , https://eclipse.dev/elk/blog/posts/2025/25-08-21-layered.html , https://www.adaptagrams.org/documentation/libavoid.html ,
https://www.doi.org/10.1007/978-3-642-11805-0_22 , https://vis.khoury.northeastern.edu/pubs/Wilson2024EvaluatingExtendingSpeedup/ ,
https://google-melange.com/archive/gsoc/2013/orgs/ogdf/projects/pawel_schmidt.html

- [ ] **2026-11-07 (label on a run near a lane edge):** smc-resiliency commission-gps, `6 Yes` sits just under its line because the run is 10 px below the lane edge and a label centred on it would
  cross the edge (route_costs.label_spot keeps labels off lane edges since d92937f). Keep runs that carry a label at least half a label's height from a lane edge (the room reserved for runs), so the
  label sits on its line.

## Diagram-type sources to keep (2026-11-11, operator: "keep note of the two links") `OPEN`

- [draw.io diagram types](https://www.drawio.com/docs/diagram-types/): the catalogue of types draw.io documents. Read 2026-11-11 by category headings only (`VERIFIED_PRIMARY` for the list; per-type articles not opened).
- [jgraph/drawio-diagrams, examples](https://github.com/jgraph/drawio-diagrams/tree/dev/examples) (branch `dev`, 75 entries listed 2026-11-11): real `.drawio` files for network, rack, sequence, UML deployment/component/timing, BPMN, Gantt and timeline. Candidate
  ground truth for shape style keys.
- Operator's fit shortlist (advice, `UNVERIFIED` against the files): network topology, rack, sequence and timing, deployment/component, swimlane and BPMN choreography, dependency graph.
- Not done: files not yet downloaded to `documents/` (verbatim, with a `readme.md` index); engine support for sequence, ER, rack and Gantt not checked.
- Gantt of the enterprise-strategy program by phase (operator, 2026-11-11): hand-built, code in `prototypes/business-views/draw_gantt.py` (prototype; the next chat decides which business views become
  skill-drawio views). Drawing: enterprise-strategy `docs/flows/drawio/program-gantt-20261111_2103.drawio`. Promotion to `scripts/` needs tests, a recipe, a catalogue row and Args/Returns docstrings
  (skill-coder).
- Open (not from this session): `just check` fails doc freshness on SETUP.md (justfile changed 2026-11-11, after Last reviewed 2026-11-07); `just test` fails because `scripts/flowmap/flow_head.py`
  (another session's uncommitted file) has no tests. Neither touched here.
