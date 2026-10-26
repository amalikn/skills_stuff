"""Click a colour to see it alone: draw.io custom-link actions that dim everything else on the End-to-end and Overview pages, and undo it on
a second click. Stdlib only.

Why (operator, 2026-10-26): tracing one flow among 31 on the End-to-end page is hard. With `look.click_isolate` on, every End-to-end step
arrow, its label, every dashed connector and each legend row, and on the Overview every thick arrow, its count, its dots and its legend
row, carries a `data:action/json` link. One click shows that colour alone (everything else at a low opacity, the other legend rows too); a
second click on it shows everything again; a click on another colour switches to it. The operator asked for one click each way, with no
"Show all" button (2026-10-26).

How a stateless link toggles without touching the file. Every action here is marked `"transient": true` (draw.io 32.5.5 makes a link
clicked on a cell a saved change unless an action says otherwise: executeCustomActions with the cell given). A transient action changes
the drawn state only:
nothing is saved, the file is not marked changed, and a reload or a view refresh restores it). A transient `toggleStyle` decides per cell:
a cell holding the given value goes back to the default, any other cell takes the value (Graph.nextToggleStyleValue). So each colour dims
the rest with its own value, the same opacity to the eye: 15.001 for the first colour, 15.002 for the second. A click toggles `opacity` and
`textOpacity` on every dimmable cell with its colour's value, then sets its own colour's cells to 100. A second click finds the cells holding
that value and restores them; a click on another colour finds a different value and dims them as its own, so switching takes one click.
In the editor a click runs a link directly only on a cell whose layer is locked (Graph click handler), so the clickable layers are locked.

Imported, not run: `from flowmap.isolate import isolate_link` with the skill's scripts/ on sys.path.
"""

from __future__ import annotations

import json

from drawio.cell import tag

#: The tag every component box on the End-to-end page gets when isolation is on, so a click dims boxes as well as arrows.
BOX_TAG = "box"
#: The tag of legend rows and swatches that take part, so the other rows dim too.
LEGEND_TAG = "legend"
#: Everything a click on the End-to-end page dims: step arrows and labels, dashed connectors, component boxes, legend rows.
E2E_DIMMED = ("step-arrow", "connector", BOX_TAG, LEGEND_TAG)
#: Everything a click on the Overview dims: thick arrows with their counts and dots, thin arrows, legend rows.
OV_DIMMED = ("ov-thick", "ov-thin", LEGEND_TAG)
#: Opacity of the rest when `look.click_isolate` is true rather than a number.
DIM = 0.15


def dim_level(look: dict) -> float | None:
    """The opacity the rest of the page takes on a click, from `look.click_isolate`.

    Args:
        look: the profile's look settings.

    Returns:
        None when isolation is off; DIM for true; the number given otherwise.
    """
    value = look.get("click_isolate", False)
    if value is False or value is None:
        return None
    return DIM if value is True else float(value)


def group_tag(look: dict, group: str) -> str:
    """The tag shared by every cell of one End-to-end colour group: `flow-<id>` with per-flow layers (`look.e2e_layers: flow`), else `family-<id>`.

    Args:
        look: the profile's look settings.
        group: the group id (a flow id or a family id).

    Returns:
        The tag.
    """
    return tag("flow" if look.get("e2e_layers", "family") == "flow" else "family", group)


def isolate_link(index: int, dimmed: tuple, keep: str, dim: float) -> str:
    """The link that shows one colour alone, or everything again when it already is; transient, so the file never changes.

    Args:
        index: the colour's position on its page (0 for the first); it makes the colour's dim value its own.
        dimmed: the tags of every cell a click dims.
        keep: the colour's own tag.
        dim: the opacity of the rest (0 to 1).

    Returns:
        The `data:action/json,...` link text.
    """
    value, keys = f"{dim * 100:.0f}.{index + 1:03d}", ("opacity", "textOpacity")
    # "transient" is explicit: a click on a cell runs its link with the cell given, and then draw.io defaults to a saved change
    actions = [{"toggleStyle": {"tags": list(dimmed), "tagsMatch": "or", "key": k, "value": value, "defaultValue": "100", "transient": True}}
               for k in keys]
    actions += [{"style": {"tags": [keep], "key": k, "value": "100", "transient": True}} for k in keys]
    for act in actions[1:]:
        act["immediate"] = True
    return "data:action/json," + json.dumps({"actions": actions}, separators=(",", ":"))


def ov_cell(gid: str, index: int, dim: float | None, base: str) -> dict:
    """The tags and click link of one Overview cell in a colour group: a thick arrow (its count takes the arrow's), a dot, a legend row.

    Args:
        gid: the colour group: a target group index for a thick colour, "inside" for the thin grey arrows.
        index: the colour's position among the Overview's colours (isolate_link).
        dim: the opacity of the rest, or None when isolation is off.
        base: the cell's kind tag (`ov-thick`, `ov-thin`, LEGEND_TAG).

    Returns:
        Box or edge keyword arguments: {} when off, else `tags` and `link`.
    """
    if dim is None:
        return {}
    own = "ov-thin" if gid == "inside" else tag("into", gid)
    return {"tags": tuple(dict.fromkeys((base, own))), "link": isolate_link(index, OV_DIMMED, own, dim)}
