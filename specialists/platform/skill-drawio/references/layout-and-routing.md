---
Title: Layout and routing for generated drawings
Category: skill-reference
Status: current
Authority: The skill's renderer code (scripts/flowmap/, scripts/drawio/mxfile.py, scripts/drawio/route.py) as read on 2026-10-19; the code wins over this summary
Scope: >-
  How a generator places boxes and routes arrows so a static draw.io export is clean: layered rows, barycentre ordering, channels and tracks, port spreading,
  interval track assignment, crossing-cutting local search, label placement and text-fit sizing
Last reviewed: 2026-10-20
Summary: The layout techniques the flow-map renderer uses, each with its constant, so another generator can reuse them and pass the layout audits.
---

# Layout and routing for generated drawings

Derived from the code in the `flowmap` package and `scripts/drawio/mxfile.py` and `scripts/drawio/route.py` (promoted from UNC's flow-map renderer on 2026-10-19). Constants
are quoted as found that day. Claim IDs refer to [sources.yaml](../sources.yaml).

## Contents

- [Why the generator routes](#why-the-generator-routes)
- [Coordinates and units](#coordinates-and-units)
- [Layered rows](#layered-rows)
- [Barycentre sweeps](#barycentre-sweeps)
- [Channels and tracks](#channels-and-tracks)
- [Port spreading](#port-spreading)
- [Interval tracks](#interval-tracks)
- [Crossing-cutting local search](#crossing-cutting-local-search)
- [Untwisting close hops](#untwisting-close-hops)
- [Label placement](#label-placement)
- [Text-fit sizing](#text-fit-sizing)
- [Constants at a glance](#constants-at-a-glance)

## Why the generator routes

A static export does not route around shapes: an `orthogonalEdgeStyle` edge with no waypoints is drawn straight through any box in its way (observed with draw.io desktop 32.4.1 in UNC) [C-D16]. So the
generator plans every route itself, writes each one as explicit waypoints with pinned ends ([file-format.md](file-format.md)) with `edgeStyle=none`, so draw.io draws straight runs between the given
points, and checks the result with the layout audits ([layout-audits.md](layout-audits.md)). Every technique below serves that.

## Coordinates and units

Everything is in draw.io units (pixels at 100 percent). Runs are orthogonal: horizontal or vertical within half a unit. Points are rounded to 0.1 and repeated points are dropped by `Page.route()`, so
a zero-length run never reaches the file.

## Layered rows

Inside a group, `layout_group()` turns "what needs what" into rows [C-D23]:

1. A box's depth is 0 when it needs nothing in its group, else one more than the deepest box it needs (`overview_layout.depth`). The deepest box goes in the top row, so a box sits above what it needs and arrows
   point down.
2. Boxes with no link inside the group go in a grid below the layered rows, `OV_GRID_COLS` (3) to a row.
3. An arrow that skips rows gets a placeholder **slot** in each row it passes through, so the ordering step treats it as a chain of short hops and leaves a gap for it.

```text
row 0   [ A ]          [ B ]
          |              |
row 1   [ C ]  (slot A>E)|        <- slot keeps a gap where A's arrow passes row 1
          |      |       |
row 2   [ D ]  [ E ]    [ F ]
grid    [ G ]  [ H ]    [ I ]     <- unlinked boxes, three to a row
```

Rows are centred in the group, boxes `OV_HGAP` (34) apart, slots `OV_SLOT` (22) wide, with `OV_PAD` (26) padding.

## Barycentre sweeps

Within each row, order boxes by the average position of their neighbours in the adjacent row (the barycentre), so arrows run short and cross less [C-D23]. `layout_group()` makes six sweeps,
alternating down (order by the row above) and up (order by the row below); a box with no neighbours on that side keeps its place. The End-to-end page does the same for each tier column: a box's row is
ordered by the barycentre of the components it meets in the flows (`_neighbours`, `_place`).

## Channels and tracks

Arrows never run through a box row; they run in **channels**: the gap between two rows or two columns of boxes or groups. Within a channel each arrow gets its own **track**, a fixed x (vertical
channel) or y (horizontal channel) [C-D24].

- Overview: thick group-to-group arrows. Adjacent rows drop straight or turn once in the gap between them; only an arrow that skips a row uses a column channel (`overview_layout.far_channels`: leave through one
  row gap, run along a column gap, arrive through another row gap). Channels are at least `OV_CHANNEL` (210) wide and grow so tracks stay `OV_SP` (24) apart with `OV_MIN_HEAD` (34) clear at each side.
- Thin arrows inside a group get one track per arrow in each row gap, `OV_THIN_SP` (16) apart, and the last drop into a box is at least `OV_MIN_THIN` (22).
- `drawio.route.track()` centres the tracks on the channel's middle: track k of n sits at `centre + (k - (n - 1) / 2) * spacing`.
- End-to-end page: a link to a column on the right leaves its box's right side and enters the target's left side (mirrored for the left). One channel gives a straight line (same row) or a "z" with one
  track; two channels give a "far" route along a horizontal **corridor** next to the source row (`_plan`). Channels are at least `E2E_MIN_CH` (100) wide, corridors `E2E_MIN_CORR` (48), and tracks
  `E2E_SP` (24) apart.

> **Learned 2026-10-19** · flowmap End-to-end · VERIFIED_PRIMARY · Source: scripts/flowmap/e2e_grid.py `nch`; tests/test_layout_rules.py
> test_one_column_end_to_end_page_draws_and_passes_every_audit · Falsifier: a one-tier map whose page raises or fails an audit
> Channels sit between tier columns, so a map with one tier had none and a link inside that column raised IndexError. The grid now keeps at
> least one channel (on the right of a single column) and the page widens to hold it; maps with two or more tiers render unchanged.

> **Learned 2026-10-20** · flowmap Overview thin arrows · VERIFIED_PRIMARY · Source: scripts/drawio/route.py `gap_crossings`, `gap_order`,
> `gap_ranks`; scripts/flowmap/overview.py `_thin_routes`; tests/test_layout_rules.py ThinTrackOrder · Falsifier: a group whose thin arrows
> cross in a row gap where another track order would not, or a drawing that changes with no fewer crossings
> Thin arrows took their tracks in a row gap in chain order, so an arrow detouring around a box could take the upper track and hop its right-hand
> neighbour twice (smc-resiliency's S2 Overview, operator: "unnecessary overlaps on p1"). In one gap every crossing is fixed by the track order
> alone: run i crosses run j's way in when i is above j and j's start x is inside i's run, and j's way out when i is below and j's end x is inside.
> The tracks now start in chain order and swap neighbours only while a swap strictly lowers that count, so a drawing already at its best renders
> byte-identical (the shop example did). UNC's Overview went from 19 thin crossings to 15 on stored points (54 to 44 on full paths, `just count-crossings --prefix ov-d-`), audit clean. Screenshots:
> [before and after](screenshots/20261020-thin-track-order/readme.md).
>
> ```python
> # scripts/drawio/route.py (skill-drawio; commit named in CHANGELOG 20261020)
> def gap_crossings(seq: list, span: dict) -> int:
>     n = 0
>     for a, i in enumerate(seq):
>         lo, hi = sorted(span[i])
>         for b, j in enumerate(seq):
>             if i == j:
>                 continue
>             x0, x1 = span[j]
>             n += (a < b and lo < x0 < hi) + (a > b and lo < x1 < hi)
>     return n
>
> def gap_order(seq: list, span: dict) -> list:
>     seq, best = list(seq), gap_crossings(seq, span)
>     better = True
>     while better and best:
>         better = False
>         for k in range(len(seq) - 1):
>             trial = seq[:k] + [seq[k + 1], seq[k]] + seq[k + 2:]
>             cost = gap_crossings(trial, span)
>             if cost < best:
>                 seq, best, better = trial, cost, True
>     return seq
> ```

## Port spreading

Several arrows leaving or entering one box edge get separate **ports** along it, ordered by where each arrow's other end is, so they do not cross at the box [C-D25].

- `drawio.route.spread()` gives n arrows on an edge the fractions `(i + shift) / (n + 2)` for top and bottom edges (shift 1 on top, 2 on bottom) and `(i + 1) / (n + 1)` for sides. The top and bottom shifts
  interleave, so a stub rising from a group below never meets one dropping from a group above at the same x.
- Groups of different heights joined side to side spread their ports over the part of the edges both groups share.
- On the End-to-end page ports sit `E2E_PORT_SP` (24) apart around the row's middle; a row is as tall as its largest pool of ports, and each box covers its own ports with `E2E_BOX_PAD` (18) to spare
  (`_port_y`, `_box_span`). Arrows heading up take the upper ports (`_toward`).
- Forward and back arrows between the same pair of boxes on a flow page use separate ports (a UNC test asserts it).

## Interval tracks

When many vertical runs share a channel, they can share a track as long as their spans do not come close. `drawio.route.interval_tracks()` is the classic left-edge greedy interval colouring: sort runs by their low
end; put each on the first track whose last run ended at least `sep` before this one starts, else open a new track [C-D24]. It is deterministic (sorted input, first fit) and uses the fewest tracks for
interval graphs. `_channels()` uses it with `sep = E2E_SP`; corridors let two links share a track when a column lies between their spans.

## Crossing-cutting local search

After the first placement, `flowmap.e2e.EndToEnd._improve()` cuts crossings by local search [C-D24]:

1. Count crossings between orthogonal polylines (`drawio.route.count_crossings`, using runs pre-split by direction in `drawio.route.oriented`).
2. For each channel, try swapping each pair of neighbouring tracks; for each corridor, the same; for each port pool, each pair of neighbouring ports.
3. Keep a swap only when the crossing count of the affected links drops (`_try`), and, for corridor and port swaps, only when every moved vertical run still keeps `E2E_SP` from the others on its track
   (`_runs_ok`).
4. Repeat up to four passes, stopping early when a pass changes nothing.

It is cheap because only the links touched by a swap are re-routed and re-counted, and deterministic because the swap order is fixed (sorted keys).

## Untwisting close hops

draw.io draws a hop (`jumpStyle=arc`) where an edge crosses another; two hops closer than `2 * jumpSize + 6` merge into a double twist [C-D15]. `drawio.route.untwist()` fixes this for thin arrows inside a
group: for each horizontal run, find the vertical runs it crosses; where two neighbouring crossings are too close, slide one vertical run sideways (the later one right, else the earlier one left) by
just enough, never more than `limit` (16) from where it started. A run in a slot stays clear of the boxes beside the slot; a run leaving or entering a box slides its port along the box edge and stays
at least 12 inside the corners. It stops when nothing moves, or after 60 rounds. The arc-clash audit then confirms the result.

## Label placement

A label that belongs to an arrow (a count, a `flow.step` number) goes on that arrow's own runs, clear of everything else [C-D26]:

- Try the arrow's runs longest first, skipping runs too short for the label (overview: under 60; End-to-end: under twice the label width).
- On each run, try fractions in a fixed order: overview `0.5, 0.35, 0.65, 0.25, 0.75`; End-to-end `0.5, 0.35, 0.65, 0.2, 0.8, 0.42, 0.58, 0.28, 0.72`.
- Accept the first spot whose rectangle touches no other arrow, overlaps no placed label and (End-to-end) no box.
- If nothing is clear, fall back to the longest run's middle and let the label audit report it, rather than hiding the failure.

Overview counts are 18 pt bold in the arrow's colour on a white label background; End-to-end step labels are `E2E_LABEL_W` x `E2E_LABEL_H` (38 x 16) and bold.

## Text-fit sizing

draw.io wraps text at render time, but a generator must size boxes before that, so it estimates [C-D27]:

- `wrapped_lines(text, width)` counts lines word by word at a fixed characters-per-line budget; a token longer than the budget is counted as spanning whole lines.
- The budget is conservative because bold text is wider: overview boxes 26 characters per line at font 10 in about 180 units (`OV_CHARS`), End-to-end boxes 27 (`E2E_CHARS`), flow notes 44
  (`NOTE_CHARS`). Line heights are 13, 14 and 15. Measure with an export when a new font size or width is introduced.
- A box's height is its wrapped line count times the line height plus padding, with a minimum (`E2E_MIN_H` 60). A group is only as tall as its content; a row is as tall as its tallest box.
- `soft_breaks()` gives tokens of `LONG_TOKEN` (24) characters or more a zero-width space after each `/ _ . : -`, so a long code path can wrap inside its shape instead of overflowing it. Shorter words
  are unchanged.

## Constants at a glance

| Constant                                                       | Value              | Meaning                                                                           |
| -------------------------------------------------------------- | ------------------ | --------------------------------------------------------------------------------- |
| `OV_HGAP`, `OV_SLOT`, `OV_PAD`, `OV_GRID_COLS`                 | 34, 22, 26, 3      | Box gap, slot width, group padding, grid columns (per group: `group_columns`)     |
| `OV_THIN_SP`, `OV_THIN_JUMP`                                   | 16, 4              | Thin track spacing, thin hop size                                                 |
| `OV_CHANNEL`, `OV_MIN_THIN`, `OV_MIN_HEAD`, `OV_SP`, `OV_JUMP` | 210, 22, 34, 24, 7 | Channel width, thin and thick head clearance, thick track spacing, thick hop size |
| `OV_CHARS`, `OV_LINE_H`                                        | 26, 13             | Overview text budget and line height                                              |
| `E2E_BW`, `E2E_MIN_H`, `E2E_PORT_SP`, `E2E_SP`                 | 210, 60, 24, 24    | End-to-end box width, minimum height, port and track spacing                      |
| `E2E_MIN_CH`, `E2E_MIN_CORR`, `E2E_JUMP`                       | 100, 48, 6         | Minimum channel and corridor, hop size                                            |
| `E2E_CHARS`, `E2E_LINE_H`, `E2E_BOX_PAD`                       | 27, 14, 18         | End-to-end text budget, line height, port padding                                 |
| `NOTE_CHARS`, `NOTE_LINE_H`                                    | 44, 15             | Flow note text budget and line height                                             |
| `LONG_TOKEN`                                                   | 24                 | Shortest token given soft breaks                                                  |

> **Learned 2026-10-20** · flow map authoring · VERIFIED_PRIMARY · Source: smc-resiliency docs/flows/flows.yaml (commits 4d6e1b0, 31ab9eb); `render_flowmap.py --audit` and page exports
> · Falsifier: a mutual `depends_on` that draws cleanly, or a one-group tier that audits clean where the merged tier did not
> Two map-level causes of a bad drawing, both fixed in the map, not the engine: (1) two components that list each other in `depends_on` (an
> activation step and the timer it arms) draw a thin arrow back up through the first box's title; a dependency is one-way, so drop the reverse.
> (2) A tier holding a single small group ("Site services") put three End-to-end labels on other flows' arrows (`labels_on_arrows`); moving the
> group's one box into the group where it actually runs cleared the audit. Try such variants on scratch copies of the map (strip `docs:` entries,
> which resolve against the project root) and keep the first that audits clean.
>
> ```yaml
> # smc-resiliency docs/flows/flows.yaml (excerpt, after the fix)
> - id: revert-timer
>   kind: timer
>   group: On the SMC
>   notes: Covers the case where the swap cuts the box off before the health check can report.
>   # no depends_on: [activate] (the activation step arms it; the reverse edge drew through its title)
> - id: site-units
>   group: On the SMC        # was its own tier "Site services"
> ```

> **Learned 2026-10-20** · flowmap Overview unlinked boxes · VERIFIED_PRIMARY · Source: scripts/flowmap/overview_layout.py `_rows_and_chains` (skills_stuff, this
> change); smc-resiliency docs/flows/flows.yaml · Falsifier: a map without `group_columns` whose drawing changes, or a group set to 1 still drawn side by side
> Boxes with no arrow inside their group sit in a grid of `OV_GRID_COLS` (3) columns, which leaves a wide, empty group when its boxes are few and tall
> neighbours set the row height. The map's `drawing.group_layout: {<group>: vertical | horizontal | grid N}` sets that grid per group (one column, one
> row, N columns); `drawing.group_columns: {<group>: <n>}` is the numeric form, and a group named in both is refused. It changes only the grid of
> unlinked boxes, not the layered rows that arrows inside the group decide. Proved byte-identical for unified-network-controller and the shop example
> (drift checks clean). Groups themselves sit on a grid `groups_per_row` wide in map order, so a fourth group wraps to row 2, column 1 whatever
> it connects to; `drawing.group_cell: {<group>: [row, column]}` (counted from 1) places a group, the rest fill the free cells in map order
> (`overview_layout.grid_cells`; an unknown group, a column past the grid or a shared cell is refused). Screenshots in
> [screenshots/20261020-group-columns/](screenshots/20261020-group-columns/readme.md).
>
> ```python
> # scripts/flowmap/overview.py
> cols = self.profile.group_columns
> self.lay = {gi: layout_group(ids, self.same, cols.get(name, OV_GRID_COLS)) for gi, (name, ids) in enumerate(self.groups.items())}
> # scripts/flowmap/overview_layout.py, _rows_and_chains
> for i in range(0, len(alone), cols):
>     rows.append(alone[i:i + cols])
> ```

> **Learned 2026-10-21** · flow page arrows · VERIFIED_PRIMARY · Source: `scripts/flowmap/pages.py` (`step_edges`), `tests/test_options_page.py` (`test_skipping_arrow_climbs_in_target_column`) · Falsifier: an export where a skipping arrow still crosses the step between
> Flow pages leave routing to draw.io with pinned ports. A forward arrow that skips a column (check 6 to revert 8) entered its target from the
> left, so when step 7 sat in step 8's lane the router ran the arrow through step 7. Entering from below (target lane above) or above (target lane
> below) makes the router run along the source's lane and climb in the target's own column. Screenshot:
> `references/screenshots/20261021-flow-page-climb-arrow/`.
>
> ```python
> # scripts/flowmap/pages.py (step_edges), skill-drawio, 2026-10-21
> climb = [(a, b) for a, b in pairs if index[b] > index[a] + 1 and lane[b] != lane[a]]
> ...
> if (a, b) in climb:
>     style = f"exitX=1;exitY={out_r[a][(a, b)]};entryX={in_v[b][(a, b)]};entryY={1 if lane[b] < lane[a] else 0};"
> ```

> **Learned 2026-10-21** · flow pages: arrows that skip a column · VERIFIED_PRIMARY · Source: `scripts/flowmap/flow_geometry.py` (`skip_arrow`), `scripts/flowmap/pages.py`, `tests/test_shapes.py` (`SkipArrowTests`) · Falsifier: a forward arrow drawn through a step between its ends
> draw.io's own orthogonal route took a gate's arrow straight through the next step in the same lane (smc-resiliency, commissioning flow, register to
> refuse past record), and a lane-changing arrow ran along its source lane through a later step. `render_flowmap.py --audit` did not notice: it audits the
> Overview, End-to-end and option pages only, so flow pages are reviewed by export. The engine now routes every forward arrow that skips a column: in one
> lane over the lane top (under the bottom when blocked), into another lane down or up in the gap after the source column then along the target lane's
> edge; each such arrow takes its own run 10 px from the last, and a path is used only when `_clear` finds no step on it.
>
> ```python
> # scripts/flowmap/flow_geometry.py (skip_arrow), skill-drawio, 2026-10-21
> off = 6 + 10 * track
> if s_top == d_top:   # same lane: over the top, else under the bottom
>     tries = [[(sx + sw / 2, sy), (sx + sw / 2, s_top + off), (dx + dw / 2, s_top + off), (dx + dw / 2, dy)],
>              [(sx + sw / 2, sy + sh), (sx + sw / 2, s_top + s_h - off), (dx + dw / 2, s_top + s_h - off), (dx + dw / 2, dy + dh)]]
> else:
>     turn = sx + sw + gap / 2
>     run_y, end_y = (d_top + off, dy) if d_top > s_top else (d_top + d_h - off, dy + dh)
>     tries = [[(sx + sw, sy + sh / 2), (turn, sy + sh / 2), (turn, run_y), (dx + dw / 2, run_y), (dx + dw / 2, end_y)]]
> ```

> **Learned 2026-10-21** · flow pages: room for arrows, lane heads, notes · VERIFIED_PRIMARY · Source: `scripts/flowmap/flow_geometry.py` (`plan_runs`, `reserve`, `col_gap`), `scripts/flowmap/pages.py` (`_lanes`, `_head_symbol_h`, `_step`), `tests/test_layout_rules.py` · Falsifier: two engine-routed runs on one lane edge at the same y, or a lane-head symbol taller than its text needs
> smc-resiliency's operator reviewed the commissioning page: runs 5 and 6 overlapped, runs sat tight on the lane line (above 3 and 7), arrows 4 and 5
> were squeezed between columns, a cloud lane head overflowed while another stretched to the whole lane, and notes showed only their titles. Rule from
> the review: every look fix is engine code with a `drawing.look` setting, never a hand edit. Now the runs are planned before anything is drawn and each
> lane reserves `runs x track_gap + 10` px on that edge, steps centred below it; the column gap is `look.column_gap`; a shaped lane head is a plain
> panel with the symbol inside, sized by `fit_height` and the lane grown to fit; an empty note is not drawn (`look.empty_notes`), so maps should say
> what a step reads, writes, how it fails and where to look. Screenshot: `references/screenshots/20261021-flow-page-room/`.
>
> ```python
> # scripts/flowmap/flow_geometry.py (plan_runs), skill-drawio, 2026-10-21
> for a, b in pairs:
>     if order[b] <= order[a] + 1:
>         continue
>     key = (lane[b], "bottom" if lane[b] < lane[a] else "top")
>     track[(a, b)] = count.get(key, 0)
>     count[key] = track[(a, b)] + 1
> # scripts/flowmap/pages.py (_step): centred in the lane, below the room kept for arrow runs
> y = lane_y[li] + r_top + (lane_h[li] - r_top - r_bot - h) / 2
> ```

> **Learned 2026-10-21** · flow pages: which side a skip arrow takes · VERIFIED_PRIMARY · Source: `scripts/flowmap/flow_geometry.py` (`plan_runs`, `skip_arrow`), `tests/test_shapes.py` (`PlanRunsTests`) · Falsifier: two same-lane runs side by side, or a lane-changing arrow entering a target's top with nothing in the way of its left side
> The operator's second review of the commissioning page: two over-the-top runs still read as one ("route 5 under shapes 3 and 4 instead"), and the
> arrow into the lower lane should come in from the left. Rule: plan the latest source first; a same-lane run that would lie beside another over-the-top
> run goes under the bottom; into another lane, enter the target's left side through the gap after the source's column unless a step of the target's
> lane lies between. Lanes reserve room only for the runs actually planned on each edge.
>
> ```python
> # scripts/flowmap/flow_geometry.py (plan_runs), skill-drawio, 2026-10-21
> if lane[a] != lane[b]:
>     between = [s["id"] for s in steps if lane[s["id"]] == lane[b] and lo < order[s["id"]] < hi]
>     if not between:
>         route[(a, b)] = ("left", 0)
>         continue
>     side = "bottom" if lane[b] < lane[a] else "top"
> else:
>     beside = [sp for sp in spans.get((lane[a], "top"), []) if sp[0] < hi and lo < sp[1]]
>     side = "bottom" if beside else "top"
> ```

> **Learned 2026-10-21** · flow pages: overlaps found and resolved by the engine · VERIFIED_PRIMARY · Source: `scripts/flowmap/routing.py` (`route_forward`, `cost`, `label_spot`, `branch_label`), `scripts/render_flowmap.py` (`audit`), `tests/test_routing.py` · Falsifier: a flow page whose `--audit` is clean while an arrow crosses a step, or two arrows run alongside within 8 px
> The operator asked for "intelligence in skill-drawio that finds ways to take care of overlaps" after a series of hand-specific fixes. The audit had
> been blind on flow pages (step boxes were not obstacles, forward arrows were draw.io-routed). Now every forward arrow is engine-routed: candidates
> (column gaps, reserved tracks over or under the lane, left/top/bottom entries, a decision's right/top/bottom corner) are scored against what is
> already drawn and the cheapest is drawn, short arrows first so long ones route around them; labels go to the first clear spot along the path. A
> decision's branches carry "Yes"/"No" or the step's `when` cases (operator: decisions always show their cases). Flow pages are in `--audit`, so a new
> overlap fails `just check` instead of reaching a reviewer. Lane heads: heading name, italic kind, blank line, host.
>
> ```python
> # scripts/flowmap/routing.py (cost), skill-drawio, 2026-10-21
> boxes = sum(1 for p, q in segs for cid in page.solid if cid not in ends and seg_hits_rect(p, q, page.rects[cid]))
> along = sum(1 for s in segs for o in others if _along(s, o))
> crosses = sum(1 for s in segs for o in others if crossing(s, o) is not None)
> labels = sum(1 for p, q in segs for m in page.marks if seg_hits_rect(p, q, m.rect, 0))
> ports = sum(1 for pt in (pts[0], pts[-1]) if (round(pt[0]), round(pt[1])) in used)
> return boxes * COST_BOX + (along + labels) * COST_ALONG + ports * COST_PORT + crosses * COST_CROSS + length / 1000
> ```

> **Learned 2026-10-21** · flow pages: a decision's branches chosen together · VERIFIED_PRIMARY · Source: `scripts/flowmap/routing.py` (`route_branches`, `route_flow`, `_candidates`), `tests/test_routing.py` · Falsifier: two branches of one decision crossing when another corner assignment would not
> Routing branch by branch let the shorter branch take the right corner and forced the longer one over it. The operator's fix ("move eight to the
> right and seven to the top") is now the rule: try every assignment of the diamond's corners to its branches and keep the lowest total cost. A
> crossing that no assignment avoids is drawn with arc hops, as on the Overview. Also from this review: a diamond is entered only at its left corner,
> a box's left side offers entries at a third, half and two thirds, a path never runs inside its own target, and a skip arrow keeps to the run its
> lane reserved for it.
>
> ```python
> # scripts/flowmap/routing.py (route_branches), skill-drawio, 2026-10-21
> for ways in permutations(("right", "up", "down"), len(branches)):
>     mark = (len(page.routes), len(page.cells), len(page.marks), set(used))
>     total = sum(route_forward(page, edge, True, gap, tracks, used, (way,), diamond) for (edge, tracks, diamond), way in zip(branches, ways))
>     del page.routes[mark[0]:], page.cells[mark[1]:], page.marks[mark[2]:]
>     ...
>     if best_total is None or total < best_total:
>         best, best_total = ways, total
> ```

