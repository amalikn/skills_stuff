"""Parts of a flow map and flow numbers: the flows one page draws and the components they touch, and how each flow is numbered when a
family has a page of its own (`own_page`; operator, 2026-10-26). Stdlib only.

Imported, not run: `from flowmap.map_parts import shared_part, flow_numbers` with the skill's scripts/ on sys.path.
"""

from __future__ import annotations

from dataclasses import replace

from .model import e2e_tier, flow_extras, flow_family
from .profile import Profile

def flows_part(data: dict, flows: list[dict]) -> dict:
    """A part of the map: these flows and the components they touch (step actors and flow_extras), in map order.

    Args:
        data: the validated map.
        flows: the flows to keep.

    Returns:
        A copy of the map holding only those flows and components.
    """
    used = {c for f in flows for c in [s["actor"] for s in f["steps"]] + flow_extras(f)}
    return {**data, "flows": flows, "components": [c for c in data["components"] if c["id"] in used]}


def flow_numbers(data: dict, profile: Profile) -> dict[str, int]:
    """Each flow's number: the shared flows 1, 2, ... in map order, and each `own_page` family's flows 1, 2, ... on their own, since such a
    family tells a story of its own (operator, 2026-10-26: "it should not be starting from 5.x").

    Args:
        data: the validated map.
        profile: the drawing profile (its own_families).

    Returns:
        {flow id: number}; with no own family, the flows' map order.
    """
    seen: dict[str, int] = {}
    out = {}
    for f in data["flows"]:
        fam = flow_family(f, profile) if profile.own_families else ""
        key = fam if fam in profile.own_families else ""
        seen[key] = seen.get(key, 0) + 1
        out[f["id"]] = seen[key]
    return out


def flow_labels(data: dict, profile: Profile) -> dict[str, str]:
    """Each flow's number as tabs, the Overview index and flow pages show it: an own family's flows carry its prefix ("PHP 2").

    Args:
        data: the validated map.
        profile: the drawing profile.

    Returns:
        {flow id: label}.
    """
    nums = flow_numbers(data, profile)
    return {f["id"]: (f"{profile.family_prefix[fam]} {nums[f['id']]}" if (fam := flow_family(f, profile)) in profile.own_families
                      else str(nums[f["id"]])) for f in data["flows"]}


def paged_flows(data: dict, profile: Profile) -> list[dict]:
    """The flows that get a page of their own: all but those of a family with `flow_pages: false` (operator, 2026-10-26: "Don't need
    individual PHP pages"; such a family is read on its End-to-end page).

    Args:
        data: the validated map.
        profile: the drawing profile (its no_flow_pages).

    Returns:
        The flows, in map order.
    """
    return [f for f in data["flows"] if not profile.no_flow_pages or flow_family(f, profile) not in profile.no_flow_pages]


def shared_part(data: dict, profile: Profile) -> dict:
    """The full End-to-end page's part of the map: every flow but those of an `own_page` family, and every component but those only such
    flows touch (operator, 2026-10-26: one change's flows on their own page, never on the full one).

    Args:
        data: the validated map.
        profile: the drawing profile (its own_families).

    Returns:
        The map itself when no family has its own page (the page is then unchanged), else a copy.
    """
    if not profile.own_families:
        return data
    own = [f for f in data["flows"] if flow_family(f, profile) in profile.own_families]
    if not own:
        return data
    shared = [f for f in data["flows"] if f not in own]
    kept = set(c["id"] for c in flows_part(data, shared)["components"])
    only_own = set(c["id"] for c in flows_part(data, own)["components"]) - kept
    return {**data, "flows": shared, "components": [c for c in data["components"] if c["id"] not in only_own]}


def narrowed(profile: Profile, comps: list[dict]) -> Profile:
    """The profile with only the tier columns these components use, kind and default tiers renumbered to match.

    Args:
        profile: the drawing profile.
        comps: the components on the page.

    Returns:
        A copy of the profile; the band below the columns is unchanged.
    """
    keep = sorted({t for t in (e2e_tier(c, profile) for c in comps) if t is not None})
    if not keep:
        return profile
    new = {old: i for i, old in enumerate(keep)}
    return replace(profile, tiers=tuple(profile.tiers[i] for i in keep),
                   kind_tier={k: new[v] for k, v in profile.kind_tier.items() if v in new},
                   default_tier=new.get(profile.default_tier, 0))
