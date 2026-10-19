---
Title: Layout and routing for generated drawings
Category: skill-reference
Status: current
Authority: The skill's renderer code (scripts/flowmap/, scripts/drawio/mxfile.py, scripts/drawio/route.py) as read on 2026-10-19; the code wins over this summary
Scope: >-
  How a generator places boxes and routes arrows so a static draw.io export is clean: layered rows, barycentre ordering, channels and tracks, port spreading,
  interval track assignment, crossing-cutting local search, label placement and text-fit sizing
Last reviewed: 2026-10-19
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
| `OV_HGAP`, `OV_SLOT`, `OV_PAD`, `OV_GRID_COLS`                 | 34, 22, 26, 3      | Box gap, slot width, group padding, grid columns                                  |
| `OV_THIN_SP`, `OV_THIN_JUMP`                                   | 16, 4              | Thin track spacing, thin hop size                                                 |
| `OV_CHANNEL`, `OV_MIN_THIN`, `OV_MIN_HEAD`, `OV_SP`, `OV_JUMP` | 210, 22, 34, 24, 7 | Channel width, thin and thick head clearance, thick track spacing, thick hop size |
| `OV_CHARS`, `OV_LINE_H`                                        | 26, 13             | Overview text budget and line height                                              |
| `E2E_BW`, `E2E_MIN_H`, `E2E_PORT_SP`, `E2E_SP`                 | 210, 60, 24, 24    | End-to-end box width, minimum height, port and track spacing                      |
| `E2E_MIN_CH`, `E2E_MIN_CORR`, `E2E_JUMP`                       | 100, 48, 6         | Minimum channel and corridor, hop size                                            |
| `E2E_CHARS`, `E2E_LINE_H`, `E2E_BOX_PAD`                       | 27, 14, 18         | End-to-end text budget, line height, port padding                                 |
| `NOTE_CHARS`, `NOTE_LINE_H`                                    | 44, 15             | Flow note text budget and line height                                             |
| `LONG_TOKEN`                                                   | 24                 | Shortest token given soft breaks                                                  |
