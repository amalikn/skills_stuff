"""One End-to-end page per flow family, drawn after the full End-to-end page when `look.e2e_family_pages` is on. Stdlib only.

Why (operator, 2026-10-23): unified-network-controller's End-to-end page draws 31 flows through 73 components, more flows than the palette has
colours. In draw.io, View > Tags (`family-<id>`) or the Layers panel shows one family at a time, but an exported PNG or PDF cannot. A family
page draws only that family's flows and the components they touch (step actors, where each runs, its owner and dependencies), so each page
can be exported and read alone. The full page stays as it is.

Each family page keeps the whole map's flow numbers (x of x.y matches the Overview and the full page), takes colours in its own order (no
colour repeats on it; `look.e2e_family_colours: flow` keeps each flow's full-page colour instead), drops tier columns it does not use, and renames its cell ids `e2e-` to `e2f-<family>-` so every id stays unique in the file.

A family with `own_page: true` (operator, 2026-10-26: one change's flows, "it wont be added to the e2e flow") gets its page even with
`look.e2e_family_pages` off, the full page leaves its flows off (flowmap.map_parts.shared_part), and its flows are numbered from 1 with colours
of their own (flowmap.map_parts.flow_numbers; "it should not be starting from 5.x").

Imported, not run: `from flowmap.e2e_family import family_pages` with the skill's scripts/ on sys.path.
"""

from __future__ import annotations

from drawio.mxfile import Page

from .e2e import routed_e2e
from .map_parts import flow_numbers, flows_part, narrowed
from .model import flow_family
from .profile import Profile


def family_parts(data: dict, profile: Profile) -> list[tuple[str, str, dict]]:
    """Each family's part of the map: its flows and the components they touch, in map order; families with no flow are left out.

    Args:
        data: the validated map.
        profile: the drawing profile (its families).

    Returns:
        [(family id, family name, part)], the part a copy of the map holding only those flows and components.
    """
    parts = []
    for fam, name, _colour, _ids in profile.families:
        flows = [f for f in data["flows"] if flow_family(f, profile) == fam]
        if flows:
            parts.append((fam, name, flows_part(data, flows)))
    return parts


def family_page(data: dict, profile: Profile, fam: str, name: str, part: dict) -> Page:
    """One family's End-to-end page.

    Args:
        data: the whole validated map (for the flow numbers).
        profile: the drawing profile.
        fam: the family id.
        name: the family name.
        part: the family's part of the map (family_parts).

    Returns:
        The page, id `end-to-end-<family>`, its cell ids renamed to `e2f-<family>-`.
    """
    numbers = flow_numbers(data, profile)   # an own family counts from 1; the others keep the full page's numbers
    e2e = routed_e2e(part, narrowed(profile, part["components"]), {f["id"]: numbers[f["id"]] for f in part["flows"]})
    nums = ", ".join(str(numbers[f["id"]]) for f in part["flows"])
    own = fam in profile.own_families
    e2e.title = f"**End-to-end: {name}** (flows {nums}; " + ("drawn on this page only)" if own else "the full End-to-end page shows every flow)")
    page = e2e.page(f"end-to-end-{fam}", f"{profile.look.get('e2e_tab', 'End-to-end')}: {name}")
    page.rename = ("e2e-", f"e2f-{fam}-")
    return page


def family_pages(data: dict, profile: Profile) -> list[Page]:
    """The family End-to-end pages, in the profile's family order: every family with `look.e2e_family_pages` on, else only the families
    with `own_page` (drawn whatever the look says, since the full page leaves their flows off); never one with `e2e_page: false`.

    Args:
        data: the validated map.
        profile: the drawing profile.

    Returns:
        The pages.
    """
    every = profile.look.get("e2e_family_pages")
    return [family_page(data, profile, fam, name, part) for fam, name, part in family_parts(data, profile)
            if (every or fam in profile.own_families) and fam not in profile.no_e2e_pages]
