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
- End-to-end page: a link to a column on the right leaves its box's right side and enters the target's left side (mirrored for the left). A link inside one column always uses the channel on that column's right, never the left: the last column gets a right-hand channel when it has such links (operator, 2026-10-26). One channel gives a straight line (same row) or a "z" with one
  track; two channels give a "far" route along a horizontal **corridor** next to the source row (`_plan`), or a "row" route the crossing search may pick: down
  its first channel to the entry port, then straight along the target's row when no box or port sits on that row in between (`crossing_search.row_free`). Channels are at least `E2E_MIN_CH` (100) wide, corridors `E2E_MIN_CORR` (48), and tracks
  `E2E_SP` (24) apart.

> **Learned 2026-10-19** · flowmap End-to-end · VERIFIED_PRIMARY · Source: scripts/flowmap/e2e_grid.py `nch`; tests/test_layout_rules.py
> test_one_column_end_to_end_page_draws_and_passes_every_audit · Falsifier: a one-tier map whose page raises or fails an audit
> Channels sit between tier columns, so a map with one tier had none and a link inside that column raised IndexError. The grid now keeps at
> least one channel (on the right of a single column) and the page widens to hold it; maps with two or more tiers render unchanged.

> **Learned 2026-10-26** · End-to-end in-column links on the right · VERIFIED_PRIMARY · Source: `scripts/flowmap/e2e_grid.py` (`__init__`,
> `_plan`); `tests/test_crossing_search.py` InColumnLinks · Falsifier: an in-column link entering or leaving a box's left side
> A link inside one column used the channel on its right, except in the last column, which used its left channel, shared with every arrow
> coming in from the column before, while its right side stayed empty (ansible-wifi etc-hosts-hostname page; operator: "what stops us using
> the right side?", then: always the right, not a per-link search choice). The last column now gets its own right-hand channel when it has
> in-column links, as a one-column page already did. Measured (right channel alone): etc-hosts 15 -> 8, shop example 11 -> 8; PHP 22, UNC
> 3,689 unchanged (no in-column links in their last column).

> **Learned 2026-10-26** · End-to-end row moves · VERIFIED_PRIMARY · Source: `scripts/flowmap/crossing_search.py` (`row_free`, `row_move`,
> `_set_kinds`), `scripts/flowmap/e2e_grid.py` (`_size`, `_verticals`, `_corridors`), `scripts/flowmap/e2e.py` (`points`, `_runs_ok`);
> `tests/test_crossing_search.py` RowMoves (fixture `tests/fixtures/row_move.yaml`); screenshot `references/screenshots/20261026-row-moves/`
> · Falsifier: a far link that crosses a link into the same box although its target row is free and a row route with swapped ports would not
> On ansible-wifi's PHP page 1.1 (Wi-Fi user -> portal, far) crossed 5.1 (role -> portal, z) whatever the order (operator: "again overlap of
> 1.1 and 5.1 could have been avoided"): the far corridor runs above the portal's ports, and 5.1's track is shared with another link, so a
> joint port-and-track move would drag that link too. A far link may now run along its target's row (kind "row"): `row_move` tries the switch
> alone and with a neighbouring entry-port swap in both searches and keeps it only on a strict drop. Its corridor track stays reserved, and
> `_size` makes row links far again, so a page laid out again (loops) has both runs. Measured: PHP page 22 -> 21 (1.1 and 5.1 apart),
> unified-network-controller full page 3,689 -> 3,613 in 16.6 s (16.5 s before), the shop example unchanged.
>
> ```python
> # scripts/flowmap/crossing_search.py _search (skills_stuff, 2026-10-26)
> for link in grid.links:   # in both searches: a row move only keeps a strict drop
>     if (link.kind == "row" or (link.kind == "far" and row_free(grid, link))) and row_move(grid, link):
>         changed = True
> ```

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

> **Learned 2026-10-21** · flow pages: route on connection points, like the Overview · VERIFIED_PRIMARY · Source: `scripts/flowmap/routing.py` (`_ports`, `_joins`, `_valid`, `cost`, `route_flow`), `scripts/flowmap/flow_geometry.py` (`label_gaps`, `run_ys`), `tests/test_routing.py` · Falsifier: two branches of a decision leaving one point, or a target entered twice on one side when another side is free
> The operator's next review: runs still shared, several arrows entered one side, and "the Overview uses different connection points; use top,
> right, left, any". The router now pairs every exit with every entry through the corridors, rejects paths that leave or arrive against their port or
> run inside their own boxes, and costs a reused side. An arrow into a decision prefers its left corner because a decision with branches keeps its
> top and bottom for them (an arrow parked on the top corner had pushed both branches onto the right one). Yes/no branches are green and red. Column
> gaps grow to fit their labels. Checked on every flow page of both consumers by a scan of faults, crossings and shared starts (all zero).
> Screenshots: `references/screenshots/20261021-flow-router/`.

> **Learned 2026-10-22** · flow pages: arrows that cross needlessly are redrawn · VERIFIED_PRIMARY · Source: smc-resiliency operator review, 2026-10-22 ("again unnecessary overlap for the arrows fix it in the skill-drawio"); `scripts/flowmap/uncross.py` (`uncross`), `scripts/flowmap/pages.py` (`flow_page`), `tests/test_routing.py` (`test_uncross_redraws_a_crossing_pair`); screenshots `references/screenshots/20261022-uncross/` · Falsifier: a flow page where two arrows cross and drawing them in the other order (each leaving its source the same way) would not
> The router is greedy: shortest arrows first, each choosing the cheapest path against what is already drawn, never revisited. Three arrows
> into one box, one coming down from a lane above, left the early arrow on the middle entry and the later Yes branch on the upper entry, so
> the descent crossed it (a crossing costs 30, two extra bends to the free lower entry 8 plus length). The repair is a pass after routing:
> for each pair of forward arrows that cross, take both up and draw them again in the other order, each keeping its exit side, and keep the
> result only when the page's crossing count falls; at most three rounds, each only ever lowering the count. `drawing.look.uncross: "off"`
> keeps the greedy order. Measured: smc-resiliency 11 flow pages 1 -> 0 crossings, unified-network-controller 24 pages 0 -> 0 (unchanged),
> example map current; the pass takes under 0.5 s for a whole map's flow pages. A test renders the fixture with the pass off to prove it
> still finds the crossing.
>
> ```python
> # scripts/flowmap/uncross.py (skills_stuff, 2026-10-22)
> for a, b in pairs:
>     snap, count = _snapshot(page), _crossings(page)
>     sides = {a: _take_up(page, a), b: _take_up(page, b)}
>     for cid in (b, a):   # the other order: the arrow drawn second last time now chooses first
>         edge, diamonds = drawn[cid]
>         route_forward(page, edge, diamonds, corridors, _used(page, reserved), (sides[cid],))
>     if _crossings(page) < count:
>         improved = True
>     else:
>         _restore(page, snap)
> ```

> **Learned 2026-10-22** · option pages: one track per decision arrow · VERIFIED_PRIMARY · Source: unified-network-controller Options page, operator review 2026-10-22; `scripts/flowmap/options.py` (`_group_row`, `TRACK`), `tests/test_options_page.py` (`test_two_evaluated_options_get_their_own_tracks`); screenshot `references/screenshots/20261022-option-tracks/` · Falsifier: two arrows from one decision box sharing a run, or a drop crossing an arrow still running right
> Every arrow from a decision box to its options started at one point and ran at one height, so a question with two options under evaluation
> (or two chosen) drew two arrows on one run (audit `shared_runs`). Each arrow now has its own track: the one to the nearest option keeps the band
> (its arrowhead keeps the head room the audit asks for), each farther one runs a track higher, spaced 18 px or less so all fit between the
> question box and the band. Nearest lowest means no arrow's drop crosses one still running right. One target draws exactly as before, so
> existing pages are byte-identical (smc-resiliency's option pages audited clean). The test fails with the old code.
>
> ```python
> # scripts/flowmap/options.py (skills_stuff, 2026-10-22)
> for k, (i, o) in enumerate(targets):
>     ty = band - k * min(TRACK, (HEAD_GAP / 2 - 6) / max(len(targets) - 1, 1))
>     cx = x0 + i * (COL_W + GAP) + COL_W / 2
>     page.route(f"{dec}-to-{o['id']}", dec, f"opt-{g['id']}-{o['id']}-head", [(MARGIN + DEC_W, ty), (cx, ty), (cx, heads_top)],
>                style, klass="thick", ignore=(f"opt-{g['id']}",))
> ```

> **Learned 2026-10-27** · decision branches on flow pages · VERIFIED_PRIMARY · Source: `scripts/flowmap/routing.py` (`cost`,
> `route_branches`, `COST_SIBLING_CROSS`), measured on local-knowledge-ansible smc_change flows (Apply page 2 -> 1 crossings, total 88 -> 85
> with the gap fix) · Falsifier: two branches of one decision crossing each other when another corner assignment draws them apart
> Two faults made a decision's branches cross (operator review: "overlap of 7 and 10 could have been easily avoided"). (1) `route_flow`
> reserves a branchy decision's top and bottom by putting them in `used["sides"]`, so `cost` charged COST_SIDE (120) to the very branches
> they were reserved for; a reserved corner is now free for the decision's own branches until a sibling takes it (`used["taken"]`). (2) A
> crossing cost 30 against 120 for a shared side, so a crossing assignment could still win; two branches of one decision crossing each
> other now add COST_SIBLING_CROSS (400) when the assignments are compared.
>
> ```python
> own_corner = src in used.get("branchy", ()) and (src, out_side) not in used.get("taken", ())
> sides = ((src, out_side) in used["sides"] and not own_corner) + ((dst, in_side) in used["sides"])
> ...
> total += COST_SIBLING_CROSS * sum(1 for i, a in enumerate(mine) for b in mine[i + 1:]
>                                   for s in segments(a.points) for o in segments(b.points) if crossing(s, o) is not None)
> ```

> **Learned 2026-10-27** · Overview thin-arrow tracks · VERIFIED_PRIMARY · Source: `scripts/drawio/route.py` (`gap_order`,
> `GAP_EXHAUSTIVE`), `tests/test_layout_rules.py` (six real runs) · Falsifier: a row gap of at most 7 runs left with more crossings than
> its best order
> Neighbour swaps that each strictly lower a row gap's crossings stop at local minima: six runs on the smc_change Overview kept 2 crossings
> where an order with 0 exists (operator: "this overlap would have been avoided as well"). Gaps of up to 7 runs now try every order (the
> given order kept unless one is strictly better); larger gaps swap any two runs. Render time unchanged (0.5 s).

> **Learned 2026-10-27** · two arrows into one decision corner · VERIFIED_PRIMARY · Source: `scripts/flowmap/routing.py` (`cost`, `shared`),
> `scripts/flowmap/uncross.py` (`unshare`, `_shared_corners`), skills_stuff 93c0205; screenshot `references/screenshots/20261027-labels-routing/
> unshare-decision-corner.png` · Falsifier: a flow page where two arrows end at the same decision corner while another corner was free
> A diamond has one point per corner, so a second arrow there merges into the first for its last run (operator: "why is the arrow 13
> overlapping?"). A shared decision corner costs as a crossed box, but the greedy order still let the first arrow take the only corner a later
> branch could reach; the `unshare` pass redraws such a pair in the other order and keeps it only when that pair no longer shares and nothing
> else got worse (`drawing.look.unshare`).
>
> ```python
> shared = sum(1 for cid, pt in ((src, pts[0]), (dst, pts[-1])) if cid in used.get("diamonds", ()) and (round(pt[0]), round(pt[1])) in used["points"])
> ```

> **Learned 2026-10-27** · uncross tiers and shared runs · VERIFIED_PRIMARY · Source: `scripts/flowmap/uncross.py` (`_redraw_pair`,
> `_step_aside`, `_alongside`), `scripts/flowmap/route_costs.py` (`_crosses`, `_overlaps`), skills_stuff 7f00335~2..7f00335; screenshot
> `uncross-third-arrow-steps-aside.png` · Falsifier: a crossing pair the repair leaves crossing when another exit side or a lower-ranked path
> clears it without a box hit or a shared run
> A crossing pair is redrawn with the same exit sides, then every other pair of exit sides, then paths ranked by fewest crossings (the cost
> rates a crossing 30 below a flat run into the target's top 150), letting a third arrow that the pair now runs along step aside; a result is
> kept only with fewer crossings, no more shared decision corners and no more runs lying along another arrow's. Trading a crossing for a
> shared run fooled the crossing count twice (Apply 10/12, fw-x86 4 -> 6 and 5 -> 6): `count_crossings.py --compare` now counts shared runs.
> smc-resiliency fw-x86 back to 0 after two-line labels first made it 1 (operator: "no.. fix the skill").

> **Learned 2026-10-27** · End-to-end joint track swap · VERIFIED_PRIMARY · Source: `scripts/flowmap/crossing_search.py` (`tracks_together`,
> polish in `improve`), skills_stuff 7f00335; screenshot `e2e-joint-track-swap.png` · Falsifier: an E2E page where swapping two crossing links'
> neighbouring vertical and horizontal tracks together lowers its crossings after improve()
> A link leaving its box above another on the inner vertical track and the outer horizontal one crosses it twice, and either swap alone still
> crosses once (operator: "2.3 and 2.7 overlap could have been avoided"). The joint swap runs as a polish after the searches: taken inside them
> it steered the joint search to 82 crossings against 56. smc_change E2E 56 -> 50; other maps unchanged.

> **Learned 2026-10-27** · decisions sized to their text · VERIFIED_PRIMARY · Source: `scripts/flowmap/pages.py` (`size_steps`), look keys
> `decision_aspect` 0.6 and `decision_max_width` 560, skills_stuff 7871fd3, 5d648c6; screenshots `decision-sized-label-centred.png`,
> `long-decision-max-width.png` · Falsifier: a diamond wider than it needs at decision_aspect, or taller than wide below decision_max_width
> A fixed 380 px made a short question a flat sliver ("box 2 unnecessarily elongated horizontally") and a long one a tall kite
> ("disproportionately elongated vertically"). A decision starts at the step width and widens in 20 px steps until its height is at most
> 0.6 times its width, up to 560 px.

> **Learned 2026-10-27** · flow-page arrow labels · VERIFIED_PRIMARY · Source: `scripts/flowmap/routing.py` (`branch_label`, `label_size`,
> `LABEL`, `route_forward`), `scripts/flowmap/route_costs.py` (`label_spot`, `lane_colour`, `SPLIT_GAP`), skills_stuff 93c0205, 7871fd3,
> 5d648c6, ada3e9f; screenshots `two-line-label-straddles-flat-run.png`, `split-label-vertical-run.png` · Falsifier: a branch label on one
> line, a white box on a tinted lane, a label beside its line where its line had room, or a two-line label struck through by a vertical line
> Operator standards: a branch label is two lines, step number then case ("9\nstill busy ... make this a standard"); a label sits on its line,
> at the middle of the arrow's straight run (points straight through are merged first) and 8 px clear of every box; its background is the
> colour its lane shows (fill at the lane's opacity over white), not white ("remove white background"); a two-line label on a vertical run
> is two cells, number right-aligned left of the line and case left-aligned right of it, no background. The background request was first
> answered by also moving labels off the line and re-aligning them; the operator rejected that ("why other changes have been done to the
> text?"): a style request changes only that style.
>
> ```python
> cx, cy, across = label_spot(page, cid, pts, width, height, split)
> if across:   # number left of a vertical line, case right of it, no background needed
>     ...
> style = LABEL.format(colour=colour, background=lane_colour(page, cx, cy))
> ```
