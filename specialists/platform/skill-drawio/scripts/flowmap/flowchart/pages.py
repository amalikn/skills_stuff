"""Which flowchart pages a map asks for: `drawing.look.flowcharts` (plain) and `drawing.look.swimlanes` (vertical lanes), `drawing.look.bpmn` (the lanes in BPMN symbols), each a list of flow ids,
`family:<id>` for a family joined into one chart, or "all". Stdlib only.

Imported, not run: `from flowmap.flowchart.pages import flowchart_pages` with the skill's scripts/ on sys.path.
"""

from __future__ import annotations

from drawio.mxfile import Page

from .page import chart_page
from .graph import stitched
from ..model import flow_family
from ..profile import Profile


def chart_flows(data: dict, profile: Profile, key: str = "flowcharts") -> list[dict]:
    """The flows a look key names, a family joined into one.

    Args:
        data: the validated map.
        profile: the drawing profile.
        key: `flowcharts`, `swimlanes` or `bpmn`.

    Returns:
        The flows to chart, in the order listed (`"all"`: every flow in map order); empty by default.
    """
    wanted = profile.look.get(key) or []
    flows = {f["id"]: f for f in data["flows"]}
    if wanted == "all":
        return list(flows.values())
    out = []
    for item in wanted:
        if not item.startswith("family:"):
            out.append(flows[item])
            continue
        family = item.split(":", 1)[1]
        members = [f for f in data["flows"] if flow_family(f, profile) == family]
        title = next(name for fam, name, *_ in profile.families if fam == family)
        # The chain starts at the first flow a command starts (a symptom flow comes before it), and a flow joins only when it follows the one before:
        # a rollback has a command of its own, and never runs after the proof.
        first = next((k for k, f in enumerate(members) if f["trigger"]["kind"] == "command"), 0)
        chain = members[first:first + 1] + [f for f in members[first + 1:] if f["trigger"]["kind"] == "after"]
        out.append({**stitched(family, chain), "title": title})
    return out


def _named(flows: list[dict]) -> list[dict]:
    """The flows with a title that is unique among them, since a tab is named by it (four changes each have a "Step by step").

    Args:
        flows: the flows to chart.

    Returns:
        The flows; one sharing its title shows its id instead.
    """
    titles = [f["title"] for f in flows]
    return [{**f, "title": f["id"]} if titles.count(f["title"]) > 1 else f for f in flows]


def flowchart_pages(data: dict, profile: Profile, flow_page_ids: set) -> list[Page]:
    """Every flowchart and swimlane page.

    Args:
        data: the validated map.
        profile: the drawing profile.
        flow_page_ids: the flows that have a flow page, for links.

    Returns:
        The pages: plain charts, then swimlanes, then BPMN, each in chart_flows() order.
    """
    plain = _named(chart_flows(data, profile))
    comps = {c["id"]: c for c in data["components"]}
    ids = ({w["id"] for w in plain}, flow_page_ids)
    return [chart_page(f, comps, profile, ids) for f in plain] + [chart_page(f, comps, profile, ids, mode) for mode, key in (("lanes", "swimlanes"), ("bpmn", "bpmn"))
                                                                  for f in _named(chart_flows(data, profile, key))]
