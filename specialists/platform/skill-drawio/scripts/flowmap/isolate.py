"""Click a flow to see it alone: draw.io custom-link actions that dim every other flow on the End-to-end page. Stdlib only.

Why (operator, 2026-10-26): tracing one flow among 31 on the End-to-end page is hard. With `look.e2e_click_isolate` on, every step arrow and
its label carries a `data:action/json` link: clicking it sets every step arrow, connector and component box to a low opacity, then brings the
cells tagged with that arrow's flow (its arrows, labels, connectors and the boxes it touches) back to full. A legend row does the same, and
"Show all flows" puts everything back. The effect is transient: draw.io never saves it, and a refresh also restores the page.

draw.io 32.5.5 runs `{"opacity": {selector, "value": v}}` (Graph.setOpacityForNodes) on cells chosen by `tags` (with `tagsMatch` "or"); a
click runs the link on a locked cell or in the viewer, otherwise from the link in the cell's hover box. Arrows and labels are drawn locked.

Imported, not run: `from flowmap.isolate import isolate_link` with the skill's scripts/ on sys.path.
"""

from __future__ import annotations

import json

from drawio.cell import tag

#: The tag every component box on the End-to-end page gets when isolation is on, so a click can dim boxes as well as arrows.
BOX_TAG = "box"
#: Everything a click dims: step arrows and their labels, dependency connectors, component boxes.
DIMMED_TAGS = ("step-arrow", "connector", BOX_TAG)
#: Opacity of the rest when `look.e2e_click_isolate` is true rather than a number.
DIM = 0.15
#: Appended to a clickable cell's style: draw.io runs a locked cell's link on a click in the editor too.
LOCKED = "locked=1;"


def dim_level(look: dict) -> float | None:
    """The opacity the rest of the page takes on a click, from `look.e2e_click_isolate`.

    Args:
        look: the profile's look settings.

    Returns:
        None when isolation is off; DIM for true; the number given otherwise.
    """
    value = look.get("e2e_click_isolate", False)
    if value is False or value is None:
        return None
    return DIM if value is True else float(value)


def group_tag(look: dict, group: str) -> str:
    """The tag shared by every cell of one colour group: `flow-<id>` with per-flow layers (`look.e2e_layers: flow`), else `family-<id>`.

    Args:
        look: the profile's look settings.
        group: the group id (a flow id or a family id).

    Returns:
        The tag.
    """
    return tag("flow" if look.get("e2e_layers", "family") == "flow" else "family", group)


def _link(actions: list[dict]) -> str:
    """A custom link running actions in order.

    Args:
        actions: the action objects.

    Returns:
        The `data:action/json,...` link text.
    """
    return "data:action/json," + json.dumps({"actions": actions}, separators=(",", ":"))


def isolate_link(tag: str, dim: float) -> str:
    """The link that shows one flow (or family) alone: everything dimmed, then the cells with its tag back to full.

    Args:
        tag: the flow's or family's tag (`flow-<id>`, `family-<id>`).
        dim: the opacity of the rest.

    Returns:
        The link text.
    """
    return _link([{"opacity": {"tags": list(DIMMED_TAGS), "tagsMatch": "or", "value": dim}},
                  {"opacity": {"tags": [tag], "value": 1}, "immediate": True}])


def reset_link() -> str:
    """The link that shows every flow again.

    Returns:
        The link text.
    """
    return _link([{"opacity": {"tags": list(DIMMED_TAGS), "tagsMatch": "or", "value": 1}}])
