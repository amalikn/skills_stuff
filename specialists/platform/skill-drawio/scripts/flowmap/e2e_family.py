"""One End-to-end page per flow family, drawn after the full End-to-end page when `look.e2e_family_pages` is on. Stdlib only.

Why (operator, 2026-10-23): unified-network-controller's End-to-end page draws 31 flows through 73 components, more flows than the palette has
colours. In draw.io, View > Tags (`family-<id>`) or the Layers panel shows one family at a time, but an exported PNG or PDF cannot. A family
page draws only that family's flows and the components they touch (step actors, where each runs, its owner and dependencies), so each page
can be exported and read alone. The full page stays as it is.

Each family page keeps the whole map's flow numbers (x of x.y matches the Overview and the full page), takes colours in its own order (no
colour repeats on it), drops tier columns it does not use, and renames its cell ids `e2e-` to `e2f-<family>-` so every id stays unique in the file.

Imported, not run: `from flowmap.e2e_family import family_pages` with the skill's scripts/ on sys.path.
"""

from __future__ import annotations

from dataclasses import replace

from drawio.mxfile import Page

from .e2e import EndToEnd
from .model import e2e_tier, flow_extras, flow_family
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
        if not flows:
            continue
        used = {c for f in flows for c in [s["actor"] for s in f["steps"]] + flow_extras(f)}
        parts.append((fam, name, {**data, "flows": flows, "components": [c for c in data["components"] if c["id"] in used]}))
    return parts


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
    numbers = {f["id"]: i for i, f in enumerate(data["flows"], 1)}
    e2e = EndToEnd(part, narrowed(profile, part["components"]), {f["id"]: numbers[f["id"]] for f in part["flows"]})
    nums = ", ".join(str(numbers[f["id"]]) for f in part["flows"])
    e2e.title = f"**End-to-end: {name}** (flows {nums}; the full End-to-end page shows every flow)"
    page = e2e.page(f"end-to-end-{fam}", f"End-to-end: {name}")
    page.rename = ("e2e-", f"e2f-{fam}-")
    return page


def family_pages(data: dict, profile: Profile) -> list[Page]:
    """The family End-to-end pages, in the profile's family order; none unless `look.e2e_family_pages` is on.

    Args:
        data: the validated map.
        profile: the drawing profile.

    Returns:
        The pages.
    """
    if not profile.look.get("e2e_family_pages"):
        return []
    return [family_page(data, profile, fam, name, part) for fam, name, part in family_parts(data, profile)]
