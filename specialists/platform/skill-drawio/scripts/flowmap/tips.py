#!/usr/bin/env python3
"""Hover texts and draw.io tags for the flow map's pages, and the End-to-end colour and layer groups. Stdlib only.

A tooltip adds detail on hover in draw.io; an exported PNG or PDF has none, so a box or note keeps every must-read fact and a tooltip only
adds to it (operator, 2026-10-23). Tags (drawio.cell.tag) let a reader select, hide or show related cells across layers in the Tags dialog:
`flow-<id>`, `family-<id>`, `step-arrow`, `connector`, `kind-<kind>`, `group-<group>`, `gate`, `decision`, `back-arrow`, `fails`.

Imported, not run: `from flowmap.tips import comp_tip, step_tip` with the skill's scripts/ on sys.path.
"""

from __future__ import annotations

from drawio.cell import tag

from .model import flow_extras, flow_family, status_text
from .profile import DISTINCT, Profile


def comp_tip(comp: dict) -> str:
    """A component's hover text, the same on every page: kind, host, ports, health, notes and status.

    Args:
        comp: the component from the map.

    Returns:
        The lines, joined by newlines.
    """
    ports = ", ".join(str(p) for p in comp.get("ports", []))
    return "\n".join(x for x in (f"{comp['name']} ({comp['kind']})", f"host: {comp['host']}", f"ports: {ports}" if ports else "",
                                 f"health: {comp['health']}", comp.get("notes", ""),
                                 f"status: {status_text(comp)}" if comp.get("status") else "") if x)


def step_tip(step: dict, number: str, actor: str) -> str:
    """A flow step's hover text: everything the map says about it, so a box can stay short and the detail is a hover away.

    Args:
        step: the step from the map.
        number: its x.y number.
        actor: the acting component's name.

    Returns:
        The lines, joined by newlines.
    """
    joined = (("via", "via"), ("reads", "reads"), ("writes", "writes"), ("failures", "fails"), ("look", "look"), ("code", "code"))
    when = "; ".join(f"{label} -> {target}" for target, label in (step.get("when") or {}).items())
    return "\n".join(x for x in (f"{number} {step['id']} ({actor})", step["action"], f"GATE: {step['gate']}" if step.get("gate") else "",
                                 f"branches: {when}" if when else "", f"runs flow {step['flow']} (click to open)" if step.get("flow") else "",
                                 *(f"{name}: " + "; ".join(step[key]) for key, name in joined if step.get(key))) if x)


def e2e_groups(data: dict, profile: Profile) -> tuple[tuple, dict]:
    """The End-to-end colour and layer groups: the profile's families, or one per flow when `look.e2e_layers` is "flow".

    Args:
        data: the validated map.
        profile: the project's drawing profile.

    Returns:
        (groups as (id, legend and layer name, colour, flow titles), {flow id: group id}).
    """
    flows = data["flows"]
    if profile.look.get("e2e_layers", "family") == "flow":
        groups = tuple((f["id"], f"{i}. {f['title']}", DISTINCT[(i - 1) % len(DISTINCT)], (f["title"],)) for i, f in enumerate(flows, 1))
        return groups, {f["id"]: f["id"] for f in flows}
    of = {f["id"]: flow_family(f, profile) for f in flows}
    return (tuple((fam, name, col, tuple(f["title"] for f in flows if of[f["id"]] == fam)) for fam, name, col, _ids in profile.families),
            of)


def need(flow: dict, cid: str) -> str:
    """Why a flow is joined to a component it does not act in, as the connector's hover text phrase.

    Args:
        flow: the flow from the map.
        cid: the component id.

    Returns:
        "runs on", "is owned by" and/or "depends on", joined.
    """
    why = [w for w, hit in (("runs on", flow["runs_on"] == cid), ("is owned by", flow["owner"] == cid),
                            ("depends on", cid in flow.get("dependencies", {}).get("components", []))) if hit]
    return " and ".join(why) or "uses"


def step_arrow_tip(flow: dict, number: int, k: int, ends: tuple[str, str], stayed: list[str]) -> str:
    """An End-to-end step arrow's hover text: the steps that stayed in its source since the last arrow, then the step it leads into.

    Args:
        flow: the flow from the map.
        number: the flow's number (the x of x.y).
        k: the step's index (y - 1).
        ends: (source component name, target component name).
        stayed: lines for the steps before it that drew no arrow.

    Returns:
        The lines, joined by newlines.
    """
    s = flow["steps"][k]
    return "\n".join([*stayed, f"{number}.{k + 1} {flow['title']}, step {k + 1} {s['id']}: {ends[0]} to {ends[1]}", s["action"]]
                     + ([f"via {', '.join(s['via'])}"] if s.get("via") else []))


def connector_tip(users: list[dict], near: str, name: str, cid: str) -> str:
    """A dashed connector's hover text: it is not a step, and why each flow drawn with it needs the component.

    Args:
        users: the flows in the connector's group that need the component.
        near: the name of the actor it is joined from.
        name: the component's name.
        cid: the component's id.

    Returns:
        The lines, joined by newlines.
    """
    return "\n".join([f"Not a step; joined from {near}"] + [f"{g['title']} {need(g, cid)} {name}" for g in users])


def comp_tags(comp: dict, flows: list[dict]) -> tuple:
    """A component box's tags: its kind, its group, and every flow that acts in it or needs it.

    Args:
        comp: the component from the map.
        flows: every flow in the map.

    Returns:
        The tags.
    """
    touch = [f["id"] for f in flows if comp["id"] in {s["actor"] for s in f["steps"]} or comp["id"] in flow_extras(f)]
    return (tag("kind", comp["kind"]), tag("group", comp["group"]), *(tag("flow", f) for f in touch))


def step_tags(step: dict, shape: str) -> tuple:
    """A flow step box's tags: its shape when it is a decision, a gate, a step that can fail, a step that runs another flow.

    Args:
        step: the step from the map.
        shape: its flow-page shape name.

    Returns:
        The tags.
    """
    return tuple(t for t, hit in (("decision", shape == "decision"), ("gate", bool(step.get("gate"))), ("fails", bool(step.get("failures"))),
                                  (tag("runs-flow", step.get("flow", "")), bool(step.get("flow")))) if hit)
