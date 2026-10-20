"""A project's drawing profile for the flow map: where its files live, how its component kinds are coloured, its End-to-end tier columns and its
flow families. Stdlib only.

Everything that differs between projects lives here; the layout engine reads nothing else project-specific. A project either builds a Profile in
its own thin wrapper (as unified-network-controller does, to keep its constants) or adds an optional `drawing:` block to its map and calls
Profile.from_drawing(), which fills every missing field with a default derived from the map itself.

Imported, not run: `from flowmap.profile import Profile` with the skill's scripts/ on sys.path.
"""

from __future__ import annotations

from dataclasses import dataclass, field

#: Thick arrow and family colours: distinct hues, each at least 4.5:1 on white (blue, green, red, purple, teal, olive, magenta, orange,
#: navy-black, then brown, kept last because next to orange it reads as the same colour).
DISTINCT = ("#1f4e9c", "#1b7a3a", "#b3261e", "#6a3fa0", "#00707a", "#4d6b00", "#a0306e", "#b45309", "#0f172a", "#8a5a00")
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
        group_columns: {group name: columns} for an overview group's unlinked boxes (default OV_GRID_COLS, 3); 1 stacks them.
        tiers: End-to-end tier columns, left to right: (heading, the map groups placed in it).
        below_groups: groups drawn in the band below the columns.
        below_kinds: kinds drawn in that band.
        kind_tier: {kind: column} for a component whose group is in no tier.
        default_tier: the column for anything else.
        families: flow families: (id, legend and layer name, colour, flow ids in it); one draw.io layer each.
        family_by_category: {flow category: family id} for a flow named in no family.
        band_title: the heading of the band below the columns.
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
    tiers: tuple = ()
    below_groups: tuple = ()
    below_kinds: tuple = ()
    kind_tier: dict = field(default_factory=dict)
    default_tier: int = 0
    families: tuple = ()
    family_by_category: dict = field(default_factory=dict)
    band_title: str = "Stores and secrets"

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
                   group_columns={k: int(v) for k, v in (d.get("group_columns") or {}).items()}, tiers=tiers, below_groups=below_groups, below_kinds=below_kinds,
                   kind_tier=dict(d.get("kind_tier") or {}), default_tier=int(d.get("default_tier", 0)), families=families,
                   family_by_category=by_cat, band_title=d.get("band_title", "Stores and secrets"))
