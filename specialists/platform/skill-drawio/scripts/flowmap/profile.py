"""A project's drawing profile for the flow map: where its files live, how its component kinds are coloured, its End-to-end tier columns and its
flow families. Stdlib only.

Everything that differs between projects lives here; the layout engine reads nothing else project-specific. A project either builds a Profile in
its own thin wrapper (as unified-network-controller does, to keep its constants) or adds an optional `drawing:` block to its map and calls
Profile.from_drawing(), which fills every missing field with a default derived from the map itself.

Imported, not run: `from flowmap.profile import Profile` with the skill's scripts/ on sys.path.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .colours import spread_colours
from .shapes import DEFAULT_IO_VIAS

#: The drawing's look, settable per map under `drawing.look` (operator, 2026-10-21: aesthetics belong in the engine and in the YAML, never by
#: hand). Defaults are the choices of the 2026-10-21 reviews; a map that sets nothing draws as they decided.
DEFAULT_LOOK = {
    "group_fill": "#ffffff",       # Overview group boxes: opaque, so the editor grid never shows through a dashed box
    "shapes": True,                # flowchart symbols on flow pages (flowmap.shapes); False draws every step as a rectangle
    "step_width": 220,             # a step box's width on a flow page
    "decision_width": 380,         # a decision's width, in its wider column, so a diamond grows sideways
    "decision_aspect": 0.6,        # a decision widens from the step width until no taller than this times its width (short text: small)
    "decision_max_width": 560,     # a long decision may widen past decision_width up to this, so it stays a diamond, not a tall kite
    "decision_fit": "inscribed",   # a diamond's text fills the half-width, half-height rectangle a rhombus holds; "widen": the 2026-10-27 rule
    "decision_min_width": 160,     # the narrowest diamond under decision_fit inscribed (operator review 2026-11-07: diamonds "extra large")
    "store_insets": "on",          # a store step's text kept off the cylinder's rims (operator review 2026-11-07); "off" for the old cylinder
    "step_chars": 38,              # characters a line a step box is sized for, at step_width and font 10 (46 overflowed: a rendered process box holds
                                   # about 38, measured on UNC's Tech stack page, operator review 2026-11-06)
    "back_arrows": "short-first",  # return arrows: "short-first" (along the source's lane when clear) or "below-lanes" (always the band)
    "action_bullets": True,        # an action written as clauses joined by "; " is set one clause a line
    "component_shapes": True,      # Overview and End-to-end boxes take their lane head's symbol (operator, 2026-10-21); False draws rounded boxes
    "heading_scale": 125,          # a box's heading line (component name, step title, option head, decision) at this % of the box's font
    "column_gap": 80,              # space between step columns on a flow page, room for a labelled arrow (was 50 px; operator review 2026-10-21)
    "track_gap": 12,               # spacing of engine-routed arrow runs along a lane edge; each lane reserves room for the runs planned on it
    "empty_notes": "hide",         # a step note with nothing under its title: "hide" (not drawn) or "show"
    "branch_labels": "yes-no",     # a decision's two branches labelled Yes and No (a step's `when` names other cases); "off" for numbers only
    "arrow_corners": "rounded",    # flow-page arrows turn with rounded corners as on the Overview; "square" for sharp corners
    "max_aspect": 0.8,             # a step box taller than this times its width is widened instead (long text: wider, not tall and narrow)
    "uncross": "on",               # redraw two flow arrows that cross in the other order, kept when crossings drop (operator review 2026-10-22); "off"
    "straight_first": "on",        # an arrow to the very next step that can run straight across is drawn first (operator review 2026-11-07); "off"
    "back_button": "on",           # a step page's `‹ E2E page` button to its family's End-to-end page (operator review 2026-11-07); "off"
    "e2e_left_channel": "on",      # End-to-end: the first column's in-column links take a channel on its left, as the last's take one on its right (2026-11-07)
    "branch_order": "longest",     # a decision's branches route at their longest branch's turn (2026-10-26); "first": at their shortest's
    "e2e_layers": "family",        # End-to-end colours and layers per "family", or per "flow" (each x of x.y its own; operator, 2026-10-23)
    "connector_width": 1.25,       # End-to-end dashed connector stroke width; 2 matches the step arrows (operator asked for bold, 2026-10-23)
    "e2e_family_pages": False,     # also one End-to-end page per family after the full one, only that family's flows and boxes (operator, 2026-10-23)
    "e2e_step_total": False,       # End-to-end labels add the flow's step count n: "sub" (x.y, n lowered), "sup" or "slash" (x.y/n), and the
                                   # legend gives each flow's count; true means "sub" (operator, 2026-10-26: x.y/n, then a subscript instead)
    "e2e_label_font": 10,          # End-to-end arrow label font size; the label box grows to fit (operator asked for 12, 2026-10-26)
    "last_row_align": "left",      # Overview groups on a part-filled last grid row: "left", or "centre" under the row above (operator, 2026-10-27)
    "click_isolate": False,        # a click on an End-to-end or Overview arrow or legend row shows its colour alone, on a step page one arrow, on either a box its arrows; a second all; true or the dim opacity (2026-10-26)
    "overview_group_search": False, # Overview: move unpinned groups to the grid cells where thick arrows cross least (operator, 2026-10-28)
    "overview_row_search": False,  # Overview: swap boxes inside a group row to cut crossings between rows, after barycentre (operator, 2026-10-28)
    "e2e_band_search": True,       # E2E: swap two boxes in the band below the columns when the real routes then cross less (operator, 2026-11-02)
    "e2e_row_search": False,       # E2E: swap boxes inside a column to cut crossings the grid implies, after barycentre (operator, 2026-10-28)
    "e2e_loops": False,            # a step done by the same box as the step before is a loop on that box's top or bottom (operator, 2026-10-26)
    "lock_base_layer": False,      # every page's background layer ("1") drawn locked (operator, 2026-10-26)
    "chart_tab": "Chart",          # flowchart page tab names: "<chart_tab>: <title>" (operator, 2026-11-06: "Step by step" for a chained family)
    "e2e_tab": "E2E",              # E2E tab names: "<e2e_tab> flow" and "<e2e_tab>: <family>" (operator asked for "E2E" 2026-10-26; the default since 2026-11-11)
    "e2e_family_colours": "page",  # family-page flow colours: "page" (restart on each page, no repeats) or "flow" (full-page colour; operator, 2026-10-26)
    "fold": "off",                 # a long flow page in rows: "off", "serpentine" (every second row right to left) or "z" (operator, 2026-10-27)
    "step_pages": [],              # one step page per entry, folded serpentine: `family:<id>` chains the family (as flowcharts) (operator, 2026-11-06)
    "flowcharts": [],              # regular flowchart pages (flowmap.flowchart): flow ids, `family:<id>` for a family as one chart, or "all" (operator, 2026-11-02)
    "bpmn": [],                    # the same lanes in BPMN symbols; same values as flowcharts (operator, 2026-11-02)
    "swimlanes": [],               # the same chart in vertical lanes, one per actor; same values as flowcharts (operator, 2026-11-02)
    "label_clearance": 6,          # least space between an arrow label and another arrow on a flow page, in px (operator, 2026-11-02)
    "route_under": True,           # flow pages: arrows may also run just below the boxes they pass; the router takes that when it scores cleaner (operator, 2026-11-02)
    "run_spacing": 40,             # flow pages: least space between parallel arrows in px, and keeps long runs off lane edges (operator, 2026-11-02)
    "fold_after": 7,               # columns per row when `fold` is on; a flow sets its own with `layout: {fold, fold_after}`
    "fold_lanes": "used",          # a folded row draws only the lanes its steps use ("used") or every lane of the flow ("all"; operator, 2026-11-06)
}

#: Thick arrow and family colours: distinct hues, each at least 4.5:1 on white (blue, green, red, purple, teal, olive, magenta, orange,
#: navy-black, then brown, kept last because next to orange it reads as the same colour). The second ten (operator, 2026-10-23: extend the
#: palette) were picked farthest-first by CIEDE2000 and each sits at least 13.8 from every other colour and the thin grey, above the first
#: ten's closest pair (green and olive, 13.1): chocolate, sky, maroon, pine, fuchsia, ultramarine, mustard, bronze, plum, jade.
DISTINCT = ("#1f4e9c", "#1b7a3a", "#b3261e", "#6a3fa0", "#00707a", "#4d6b00", "#a0306e", "#b45309", "#0f172a", "#8a5a00",
            "#572f19", "#0f7ab3", "#71142b", "#195744", "#c200c2", "#0000c2", "#857700", "#574b19", "#680863", "#008571")
#: Default (fill, stroke) pairs for component kinds a profile does not name, in order of first use.
KIND_PALETTE = (("#dae8fc", "#6c8ebf"), ("#d5e8d4", "#82b366"), ("#fff2cc", "#d6b656"), ("#ffe6cc", "#d79b00"), ("#e1d5e7", "#9673a6"),
                ("#f8cecc", "#b85450"), ("#f5f5f5", "#666666"), ("#dfe7f3", "#3d5a80"), ("#e6e6e6", "#4d4d4d"), ("#fff8e1", "#bf9000"))


@dataclass(frozen=True)
class Profile:
    """One project's settings for rendering its flow map.

    Args:
        map: the map file, relative to the project root.
        schema: the JSON Schema file (relative to the root, or absolute).
        output: the .drawio file written.
        generator: the script named in the generated banner.
        host: the `<mxfile host>` attribute.
        command: the command that regenerates the drawing (named in the banner and page titles).
        check: the command that fails on drift (named in the banner).
        kind_style: {component kind: (fill, stroke)}, in legend order.
        groups_per_row: overview groups per grid row.
        group_columns: {group name: columns} for an overview group's unlinked boxes (default OV_GRID_COLS, 3); 1 stacks them, 0 puts
            them in one row. Built from the map's `group_columns` and `group_layout` (see layout_columns).
        group_cells: {group name: (row, column)} counted from 0, from the map's `group_cell` (counted from 1); other groups fill the rest.
        tiers: End-to-end tier columns, left to right: (heading, the map groups placed in it).
        below_groups: groups drawn in the band below the columns.
        below_kinds: kinds drawn in that band.
        kind_tier: {kind: column} for a component whose group is in no tier.
        default_tier: the column for anything else.
        families: flow families: (id, legend and layer name, colour, flow ids in it); one draw.io layer each.
        family_by_category: {flow category: family id} for a flow named in no family.
        own_families: families with `own_page: true`, drawn only on their own End-to-end page and left off the full one, their flows numbered
            from 1 on their own (operator, 2026-10-26).
        family_prefix: {own family id: the word before its flow numbers on tabs and the index, `prefix` else the family name}.
        no_flow_pages: families with `flow_pages: false`: no page per flow and no index row, only their End-to-end page (operator, 2026-10-26).
        chain_all: families with `chain: all`: a family chart joins every flow in map order, not only those triggered `after` the one before
            (operator, 2026-11-06: one step-by-step page for the smc-resiliency tech stack).
        no_e2e_pages: `own_page` families with `e2e_page: false`: no End-to-end page of their own, only their flow pages (operator,
            2026-10-26: one step-by-step page for a change, telling the change itself).
        band_title: the heading of the band below the columns.
        kind_shapes: {component kind: flow page shape} from `drawing.kind_shapes` (flowmap.shapes.DEFAULT_KIND_SHAPES fills the rest).
        io_vias: transports that cross a network, lower case, from `drawing.io_vias` (default flowmap.shapes.DEFAULT_IO_VIAS).
        look: the drawing's look, DEFAULT_LOOK overlaid with `drawing.look`.
        flow_colours: {flow id: colour} for the whole map, spread so flows sharing a box differ (flowmap.colours; operator, 2026-11-06);
            empty for a profile built in code, where the pages spread their own flows.
    """

    map: str
    schema: str
    output: str
    generator: str
    host: str = "flowmap"
    command: str = "just flows"
    check: str = "just check"
    kind_style: dict = field(default_factory=dict)
    groups_per_row: int = 3
    group_columns: dict = field(default_factory=dict)
    group_cells: dict = field(default_factory=dict)
    tiers: tuple = ()
    below_groups: tuple = ()
    below_kinds: tuple = ()
    kind_tier: dict = field(default_factory=dict)
    default_tier: int = 0
    families: tuple = ()
    family_by_category: dict = field(default_factory=dict)
    own_families: frozenset = frozenset()
    family_prefix: dict = field(default_factory=dict)
    no_flow_pages: frozenset = frozenset()
    no_e2e_pages: frozenset = frozenset()
    chain_all: frozenset = frozenset()
    band_title: str = "Stores and secrets"
    kind_shapes: dict = field(default_factory=dict)
    io_vias: tuple = DEFAULT_IO_VIAS
    look: dict = field(default_factory=lambda: dict(DEFAULT_LOOK))
    flow_colours: dict = field(default_factory=dict)

    def style(self, kind: str) -> tuple[str, str]:
        """A kind's (fill, stroke).

        Args:
            kind: the component kind.

        Returns:
            The profile's pair; raises KeyError for a kind the profile does not name (from_drawing() names every kind in the map).
        """
        return self.kind_style[kind]

    @classmethod
    def from_drawing(cls, data: dict, map_path: str, schema: str, generator: str, output: str = "") -> Profile:
        """A profile from a map's optional `drawing:` block, with defaults derived from the map.

        Defaults: kinds coloured from KIND_PALETTE in order of first use; one tier column per group (groups in `below.groups` and components of
        `below.kinds` go in the band); one family per flow category, coloured from DISTINCT; the output beside the map as `<map stem>.drawio`.

        Args:
            data: the loaded map.
            map_path: the map file, relative to the project root.
            schema: the schema file.
            generator: the script named in the banner.
            output: the drawing path; overrides `drawing.output`.

        Returns:
            The profile.
        """
        d = data.get("drawing") or {}
        comps, flows = data.get("components", []), data.get("flows", [])
        named = {k: tuple(v) for k, v in (d.get("kinds") or {}).items()}
        kinds = list(named) + [k for k in dict.fromkeys(c["kind"] for c in comps) if k not in named]
        style = {k: named.get(k, KIND_PALETTE[i % len(KIND_PALETTE)]) for i, k in enumerate(kinds)}
        below = d.get("below") or {}
        below_groups, below_kinds = tuple(below.get("groups", ())), tuple(below.get("kinds", ()))
        groups = [g for g in dict.fromkeys(c["group"] for c in comps) if g not in below_groups]
        tiers = tuple((t["name"], tuple(t["groups"])) for t in d["tiers"]) if d.get("tiers") else tuple((g, (g,)) for g in groups)
        cats = list(dict.fromkeys(f["category"] for f in flows)) or ["flows"]
        families = (tuple((f["id"], f["name"], f["colour"], tuple(f.get("flows", ()))) for f in d["families"]) if d.get("families")
                    else tuple((c, c.capitalize(), DISTINCT[i % len(DISTINCT)], ()) for i, c in enumerate(cats)))
        by_cat = dict(d.get("family_by_category") or ({} if d.get("families") else {c: c for c in cats}))
        stem = map_path.rsplit("/", 1)
        out = output or d.get("output") or (f"{stem[0]}/drawio/" if len(stem) > 1 else "drawio/") + stem[-1].rsplit(".", 1)[0] + ".drawio"
        return cls(map=map_path, schema=schema, output=out, generator=generator, host=d.get("host", "flowmap"),
                   command=d.get("command", "just flows"), check=d.get("check", "just check"), kind_style=style,
                   groups_per_row=int(d.get("groups_per_row", 3)),
                   group_columns=group_columns(d),
                   group_cells={k: (int(v[0]) - 1, int(v[1]) - 1) for k, v in (d.get("group_cell") or {}).items()}, tiers=tiers, below_groups=below_groups, below_kinds=below_kinds,
                   kind_tier=dict(d.get("kind_tier") or {}), default_tier=int(d.get("default_tier", 0)), families=families,
                   family_by_category=by_cat, own_families=frozenset(f["id"] for f in d.get("families") or () if f.get("own_page")),
                   family_prefix={f["id"]: f.get("prefix", f["name"]) for f in d.get("families") or () if f.get("own_page")},
                   no_flow_pages=frozenset(f["id"] for f in d.get("families") or () if f.get("flow_pages") is False),
                   chain_all=frozenset(f["id"] for f in d.get("families") or () if f.get("chain") == "all"),
                   no_e2e_pages=frozenset(f["id"] for f in d.get("families") or () if f.get("own_page") and f.get("e2e_page") is False),
                   band_title=d.get("band_title", "Stores and secrets"),
                   kind_shapes=dict(d.get("kind_shapes") or {}), io_vias=tuple(v.lower() for v in d.get("io_vias", DEFAULT_IO_VIAS)),
                   look={**DEFAULT_LOOK, **(d.get("look") or {})}, flow_colours=spread_colours(flows, DISTINCT) if flows else {})

def layout_columns(spec: str) -> int:
    """Columns for a `group_layout` value.

    Args:
        spec: "vertical", "horizontal" or "grid N".

    Returns:
        1 for vertical, 0 (one row, however many boxes) for horizontal, N for a grid.

    Raises:
        ValueError: on any other value.
    """
    if spec == "vertical":
        return 1
    if spec == "horizontal":
        return 0
    word, _, n = spec.partition(" ")
    if word == "grid" and n.isdigit() and int(n) > 0:
        return int(n)
    raise ValueError(f"group_layout: {spec!r} is not vertical, horizontal or grid N")


def group_columns(drawing: dict) -> dict:
    """{group name: columns} from a drawing block's `group_columns` and `group_layout`.

    Args:
        drawing: the map's `drawing:` block.

    Returns:
        The merged columns per group.

    Raises:
        ValueError: when both settings name the same group, or a layout value is not understood.
    """
    cols = {k: int(v) for k, v in (drawing.get("group_columns") or {}).items()}
    for group, spec in (drawing.get("group_layout") or {}).items():
        if group in cols:
            raise ValueError(f"group {group!r} is in both group_columns and group_layout: keep one")
        cols[group] = layout_columns(spec)
    return cols


def look_report(data: dict) -> list[str]:
    """What a map's `drawing.look` pins, so a pin is never invisible (operator, 2026-10-21: a pinned value stops following the skill's
    defaults).

    Args:
        data: the loaded map.

    Returns:
        One line naming every pinned key and its value, or that the defaults apply; plus a warning line per pin equal to today's default
        (it does nothing now and would block the next change to that default).
    """
    look = (data.get("drawing") or {}).get("look") or {}
    if not look:
        return ["look: skill-drawio defaults (nothing pinned)"]
    lines = ["look: pinned " + ", ".join(f"{k}={v}" for k, v in sorted(look.items()))]
    lines += [f"warning: look.{k} is pinned to the current default ({v}); remove it to follow future defaults"
              for k, v in sorted(look.items()) if DEFAULT_LOOK.get(k) == v]
    return lines
