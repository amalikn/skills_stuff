#!/usr/bin/env python3
"""Hover texts and draw.io tags for the flow map's pages, and the End-to-end colour and layer groups. Stdlib only.

A tooltip adds detail on hover in draw.io; an exported PNG or PDF has none, so a box or note keeps every must-read fact and a tooltip only
adds to it (operator, 2026-10-23). Tags (drawio.cell.tag) let a reader select, hide or show related cells across layers in the Tags dialog:
`flow-<id>`, `family-<id>`, `step-arrow`, `connector`, `kind-<kind>`, `group-<group>`, `gate`, `decision`, `back-arrow`, `fails`.

draw.io shows a `tooltip` attribute as HTML after `Graph.sanitizeHtml` (jgraph/drawio `Graph.js`, `convertValueToTooltip`, read 2026-10-23), so
every hover text here is escaped HTML: a bold title, bold field names, and a bullet list where a field holds more than one item (operator,
2026-10-23: "use bold and bullets where makes sense"). Escaping also keeps text such as `<change>` from being read as a tag and dropped.

Imported, not run: `from flowmap.tips import comp_tip, step_tip` with the skill's scripts/ on sys.path.
"""

from __future__ import annotations

import re

from drawio.cell import tag
from drawio.mxfile import label

from .model import flow_extras, flow_family, status_text
from .profile import DISTINCT, Profile


#: A tooltip bullet list, kept tight (draw.io's tooltip box has little room).
LIST = "<ul style='margin:2px 0 2px 0;padding-left:16px;'>"   # single quotes: the XML attribute keeps its double quotes


#: Text a tooltip sets in code style: a path (has a slash), a file name with a known extension, a snake_case name or setting (`a_b=c`), a flag.
CODEISH = re.compile(r"(?<![\w`])(--?[a-z][\w-]*|[\w.<>*-]*/[\w./<>*-]+|[\w<>-]+\.(?:ya?ml|py|json|sh|md|j2|cfg|conf|ini|txt|drawio|deb|tgz)"
                     r"|[a-z0-9]+(?:_[a-z0-9]+)+(?:=[\w.-]+)?)(?![\w`])")


def code_spans(text: str) -> str:
    """Mark commands, paths, file names and snake_case names as `code`, outside spans already marked (operator, 2026-10-23).

    Args:
        text: a plain-text line.

    Returns:
        The line with those tokens in backticks, which label() sets in a monospace font.
    """
    parts = text.split("`")
    return "`".join(CODEISH.sub(r"`\1`", p) if i % 2 == 0 else p for i, p in enumerate(parts))


def _fmt(text: str) -> str:
    """One tooltip line as HTML: code spans marked, then escaped and formatted by label().

    Args:
        text: a plain-text line.

    Returns:
        The line's HTML.
    """
    return label(code_spans(text))


def tip_html(title: str, *rows) -> str:
    """One tooltip as HTML: a bold title, then each row; a row is a text line or (name, items).

    Args:
        title: the title line (plain text; `**bold**` and `code` spans are formatted as in labels).
        rows: a str is one line; (name, items) is "**name:** item" for one item, or the bold name over a bullet list for several;
            empty rows and empty item lists are dropped.

    Returns:
        The HTML.
    """
    out = [f"<b>{_fmt(title)}</b>"]
    for row in rows:
        if isinstance(row, str):
            out += [f"<div>{_fmt(row)}</div>"] if row else []
            continue
        name, items = row
        items = [x for x in ([items] if isinstance(items, str) else items) if x]
        if len(items) == 1:
            out.append(f"<div><b>{label(name)}:</b> {_fmt(items[0])}</div>")
        elif items:
            out.append(f"<div><b>{label(name)}</b></div>{LIST}" + "".join(f"<li>{_fmt(x)}</li>" for x in items) + "</ul>")
    return "".join(out[:1] + ["<br>"] + out[1:]) if len(out) > 1 else out[0]


def comp_tip(comp: dict) -> str:
    """A component's hover text, the same on every page: kind, host, ports, health, notes and status.

    Args:
        comp: the component from the map.

    Returns:
        The tooltip HTML.
    """
    return tip_html(f"{comp['name']} ({comp['kind']})", ("Host", comp["host"]), ("Ports", ", ".join(str(p) for p in comp.get("ports", []))),
                    ("Health", comp["health"]), ("Notes", comp.get("notes", "")), ("Status", status_text(comp) if comp.get("status") else ""))


def step_tip(step: dict, number: str, actor: str) -> str:
    """A flow step's hover text: everything the map says about it, so a box can stay short and the detail is a hover away.

    Args:
        step: the step from the map.
        number: its x.y number.
        actor: the acting component's name.

    Returns:
        The tooltip HTML.
    """
    lists = (("via", "Via"), ("reads", "Reads"), ("writes", "Writes"), ("failures", "Fails"), ("look", "Look"), ("code", "Code"))
    return tip_html(f"{number} {step['id']} ({actor})", step["action"], ("Gate", step.get("gate", "")),
                    ("Branches", [f"{label_} -> {target}" for target, label_ in (step.get("when") or {}).items()]),
                    ("Runs flow", f"{step['flow']} (click to open)" if step.get("flow") else ""),
                    *((name, step.get(key, [])) for key, name in lists))


def flow_arrow_tip(number: int, src: tuple, dst: tuple, actor: str, back: bool) -> str:
    """A flow page arrow's hover text: the step it leads into, after which step, and what happens there.

    Args:
        number: the flow's number.
        src: (index, step) the arrow leaves.
        dst: (index, step) it leads into.
        actor: the name of the component acting in the target step.
        back: True for an arrow back to an earlier step.

    Returns:
        The tooltip HTML.
    """
    (i, a), (j, b) = src, dst
    return tip_html(f"{number}.{j + 1} {b['id']}" + (" (back)" if back else ""), b["action"], ("After", f"{i + 1} {a['id']}"),
                    ("Done by", actor), ("When", (a.get("when") or {}).get(b["id"], "")), ("Via", b.get("via", [])))


def e2e_groups(data: dict, profile: Profile, numbers: dict | None = None) -> tuple[tuple, dict]:
    """The End-to-end colour and layer groups: the profile's families, or one per flow when `look.e2e_layers` is "flow".

    Args:
        data: the validated map, or one family's part of it.
        profile: the project's drawing profile.
        numbers: {flow id: its number in the whole map} when data is a part; a part names each flow by that number, takes colours in its
            own order (so no colour repeats on its page; with `look.e2e_family_colours` "flow", the colour at that number, as on the full
            page) and leaves out families with no flow on it.

    Returns:
        (groups as (id, legend and layer name, colour, flow titles), {flow id: group id}).
    """
    flows = data["flows"]
    if profile.look.get("e2e_layers", "family") == "flow":
        num = numbers or {f["id"]: i for i, f in enumerate(flows, 1)}
        whole = numbers and profile.look.get("e2e_family_colours", "page") == "flow"   # a part keeps each flow's full-page colour
        groups = tuple((f["id"], f"{num[f['id']]}. {f['title']}", DISTINCT[((num[f["id"]] if whole else i) - 1) % len(DISTINCT)], (f["title"],))
                       for i, f in enumerate(flows, 1))
        return groups, {f["id"]: f["id"] for f in flows}
    of = {f["id"]: flow_family(f, profile) for f in flows}
    groups = tuple((fam, name, col, tuple(f["title"] for f in flows if of[f["id"]] == fam)) for fam, name, col, _ids in profile.families)
    return (tuple(g for g in groups if g[3]) if numbers else groups), of


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


def needs_tip(title: str, pairs: list[tuple[dict, list[dict]]]) -> str:
    """An Overview dependency's hover text: who needs whom, each need with the needed component's health check.

    Args:
        title: the title line (the arrow or dot it describes).
        pairs: (component, the components it needs) per component that depends.

    Returns:
        The tooltip HTML.
    """
    return tip_html(title, *((f"{c['name']} needs", [f"**{n['name']}** (health: {n['health']})" for n in ns]) for c, ns in pairs if ns))


def step_arrow_tip(flow: dict, number: int, k: int, ends: tuple[str, str], stayed: list[str]) -> str:
    """An End-to-end step arrow's hover text: the step it leads into, then the steps that stayed in its source since the last arrow.

    Args:
        flow: the flow from the map.
        number: the flow's number (the x of x.y).
        k: the step's index (y - 1).
        ends: (source component name, target component name).
        stayed: "x.y id: action" for the steps before it that drew no arrow (same component).

    Returns:
        The tooltip HTML.
    """
    s = flow["steps"][k]
    return tip_html(f"{number}.{k + 1} {flow['title']}: step {k + 1} {s['id']}", s["action"], ("From", ends[0]), ("To", ends[1]),
                    ("Via", s.get("via", [])), (f"Earlier in {ends[0]} (no arrow)", stayed))


def connector_tip(users: list[dict], near: str, name: str, cid: str) -> str:
    """A dashed connector's hover text: it is not a step, and why each flow drawn with it needs the component.

    Args:
        users: the flows in the connector's group that need the component.
        near: the name of the actor it is joined from.
        name: the component's name.
        cid: the component's id.

    Returns:
        The tooltip HTML.
    """
    return tip_html(f"{name}: not a step", ("Joined from", near), ("Why", [f"**{g['title']}** {need(g, cid)} {name}" for g in users]))


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
