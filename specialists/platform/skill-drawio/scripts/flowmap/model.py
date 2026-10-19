"""The flow map's data model: loading and validating the map, cross-reference rules the schema cannot express, and the questions every page
asks of it (a step's targets, a flow's family, a component's tier and style). PyYAML is imported only when the map is loaded; the rest is stdlib.

A flow map holds components (id, name, kind, group, host, health, optional depends_on, ports, notes, code) and flows (id, title, category,
purpose, trigger, runs_on, owner, ordered steps with actor, action, via, optional reads, writes, code, failures, look, gate, next). The schema
is the project's (the skill ships a generic one in schemas/flowmap.schema.json); validation goes beyond it: ids unique, every actor, runs_on,
owner and dependency a known id, every `code` reference a file that exists and defines its symbol, every step after the first reached by an
arrow.

Imported, not run: `from flowmap import model` with the skill's scripts/ on sys.path.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from code_refs import CodeRefs
from schema_lite import schema_errors

from .profile import Profile

#: Shared geometry: component box width, gap, group heading height and the page margin.
COMP_W, GAP, GROUP_HEAD, MARGIN = 210, 20, 34, 20


@dataclass
class Outcome:
    """What evaluate() found.

    Args:
        problems: schema and reference problems; a non-empty list means nothing is rendered.
        text: the rendered draw.io XML, or None when there were problems.
        drift: True when the file on disk differs from `text`.
    """

    problems: list[str] = field(default_factory=list)
    text: str | None = None
    drift: bool = False


def step_targets(steps: list[dict], k: int) -> list[str]:
    """The steps the k-th step's arrows point to: its `next`, or else the step after it.

    Args:
        steps: a flow's steps in order.
        k: the step's index.

    Returns:
        The target step ids (empty for a last step without `next`).
    """
    s = steps[k]
    return list(s["next"]) if "next" in s else ([steps[k + 1]["id"]] if k + 1 < len(steps) else [])


def _duplicates(kind: str, ids: list) -> list[str]:
    """One message per id used more than once.

    Args:
        kind: what the ids name, for the message.
        ids: the ids in map order.

    Returns:
        The messages, sorted by id.
    """
    return [f"{kind} id `{dup}` is used more than once" for dup in sorted({i for i in ids if ids.count(i) > 1})]


def _component_problems(data: dict, known_c: set, refs: CodeRefs) -> list[str]:
    """Unknown dependencies and broken code references of every component.

    Args:
        data: the loaded map.
        known_c: the component ids.
        refs: the code reference checker.

    Returns:
        The messages, in map order.
    """
    problems = []
    for c in data["components"]:
        for dep in c.get("depends_on", []):
            if dep not in known_c:
                problems.append(f"component {c['id']}: depends_on names unknown component `{dep}`")
        problems += [p for ref in c.get("code", []) if (p := refs.problem(ref, f"component {c['id']}"))]
    return problems


def _step_problems(f: dict, known_c: set, refs: CodeRefs) -> list[str]:
    """A flow's step rules: unique step ids, known actors and `next` targets, code references, and an arrow into every step after the first.

    Args:
        f: the flow.
        known_c: the component ids.
        refs: the code reference checker.

    Returns:
        The messages, in step order.
    """
    fid = f["id"]
    step_ids = [s["id"] for s in f["steps"]]
    problems = [f"flow {fid}: step id `{dup}` is used more than once" for dup in sorted({i for i in step_ids if step_ids.count(i) > 1})]
    for s in f["steps"]:
        where = f"flow {fid} step {s['id']}"
        if s["actor"] not in known_c:
            problems.append(f"{where}: actor names unknown component `{s['actor']}`")
        problems += [f"{where}: next names unknown step `{nxt}`" for nxt in s.get("next", []) if nxt not in step_ids]
        problems += [p for ref in s.get("code", []) if (p := refs.problem(ref, where))]
    reached = {t for k, _s in enumerate(f["steps"]) for t in step_targets(f["steps"], k)}
    problems += [f"flow {fid}: step `{s['id']}` has no arrow into it (add it to an earlier step's `next`)" for s in f["steps"][1:] if s["id"] not in reached]
    return problems


def _flow_problems(f: dict, known_c: set, known_f: set, root: Path, refs: CodeRefs) -> list[str]:
    """One flow's rules: known runs_on, owner, flow and component dependencies, existing docs, then its steps.

    Args:
        f: the flow.
        known_c: the component ids.
        known_f: the flow ids.
        root: the repository root, for docs.
        refs: the code reference checker.

    Returns:
        The messages.
    """
    fid = f["id"]
    problems = [f"flow {fid}: {key} names unknown component `{f[key]}`" for key in ("runs_on", "owner") if f[key] not in known_c]
    deps = f.get("dependencies", {})
    problems += [f"flow {fid}: depends on unknown flow `{dep}`" for dep in deps.get("flows", []) if dep not in known_f]
    problems += [f"flow {fid}: depends on unknown component `{dep}`" for dep in deps.get("components", []) if dep not in known_c]
    problems += [f"flow {fid}: doc `{doc}` does not exist" for doc in f.get("docs", []) if not (root / doc.split("#", 1)[0]).exists()]
    return problems + _step_problems(f, known_c, refs)


def reference_problems(data: dict, root: Path) -> list[str]:
    """Cross-reference rules the schema cannot express.

    Args:
        data: the loaded map (already schema-valid).
        root: the repository root, for code paths and related docs.

    Returns:
        One message per problem: duplicate ids, unknown component or flow ids, missing files or symbols, unreached steps.
    """
    comps = [c["id"] for c in data["components"]]
    flows = [f["id"] for f in data["flows"]]
    problems = _duplicates("component", comps) + _duplicates("flow", flows)
    refs = CodeRefs(root)
    problems += _component_problems(data, set(comps), refs)
    for f in data["flows"]:
        problems += _flow_problems(f, set(comps), set(flows), root, refs)
    return problems


def read_map(root: Path, map_path: str) -> dict | None:
    """Read a map file (PyYAML, imported here so the rest of the package stays stdlib).

    Args:
        root: the project root.
        map_path: the map, relative to the root.

    Returns:
        The loaded map.

    Raises:
        OSError: the file cannot be read.
        ValueError: it is not valid YAML (PyYAML's error, re-raised with the file named).
    """
    import yaml

    try:
        return yaml.safe_load((root / map_path).read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise ValueError(f"{map_path}: {exc}") from exc


def load(root: Path, profile: Profile) -> tuple[dict | None, list[str]]:
    """Read and validate the map.

    Args:
        root: the repository root.
        profile: where the map and schema are.

    Returns:
        (map, problems): the loaded map (None when unreadable) and every schema and reference problem.
    """
    try:
        data = read_map(root, profile.map)
        schema = json.loads((root / profile.schema).read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return None, [f"cannot read {profile.map} or {profile.schema}: {exc}"]
    problems = schema_errors(data, schema)
    if problems:
        return data, problems
    return data, reference_problems(data, root)


def flow_family(flow: dict, profile: Profile) -> str:
    """The family a flow is drawn in on the End-to-end page.

    Args:
        flow: the flow from the map.
        profile: the families.

    Returns:
        The family id (by name, else by the flow's category, else the first family).
    """
    for fam, _name, _colour, ids in profile.families:
        if flow["id"] in ids:
            return fam
    return profile.family_by_category.get(flow["category"], profile.families[0][0])


def e2e_tier(comp: dict, profile: Profile) -> int | None:
    """A component's tier column on the End-to-end page.

    Args:
        comp: the component.
        profile: the tiers.

    Returns:
        The column index, or None for the band below the columns.
    """
    if comp["group"] in profile.below_groups or comp["kind"] in profile.below_kinds:
        return None
    for i, (_name, group_names) in enumerate(profile.tiers):
        if comp["group"] in group_names:
            return i
    return profile.kind_tier.get(comp["kind"], profile.default_tier)


def flow_extras(flow: dict) -> list[str]:
    """The components a flow touches without acting in a step: where it runs, its owner and its component dependencies.

    Args:
        flow: the flow from the map.

    Returns:
        Their ids, sorted, without the step actors.
    """
    actors = {s["actor"] for s in flow["steps"]}
    return sorted(({flow["runs_on"], flow["owner"]} | set(flow.get("dependencies", {}).get("components", []))) - actors)


def comp_style(kind: str, profile: Profile, extra: str = "") -> str:
    """The vertex style for a component kind.

    Args:
        kind: the component kind.
        profile: the kind colours.
        extra: style appended (alignment, font).

    Returns:
        A draw.io style string.
    """
    fill, stroke = profile.style(kind)
    return f"rounded=1;whiteSpace=wrap;html=1;fillColor={fill};strokeColor={stroke};fontSize=11;arcSize=8;{extra}"
