"""Answer questions from a flow map, so a reader meets the code through the steps that cite it. Every step shown carries its review state: a
suspect step says so, because an index that hides its own staleness is worse than none. Stdlib only.

Imported, not run: `from flowtrace.query import select, digest` with the skill's scripts/ on sys.path.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Ask:
    """What to look for; every field given must hold.

    Args:
        flow: a flow id, or a family id for all its flows.
        file: a path (or the end of one) a step cites.
        writes: words a step's `writes` holds.
        failure: words a step's `failures` holds.
        actor: a component id or name.
        text: words anywhere in the step.
    """

    flow: str = ""
    file: str = ""
    writes: str = ""
    failure: str = ""
    actor: str = ""
    text: str = ""


def _has(items: list, word: str) -> bool:
    """Whether a word sits in a list of texts, ignoring case.

    Args:
        items: the texts.
        word: the word.

    Returns:
        True when any holds it.
    """
    return any(word.lower() in str(x).lower() for x in items)


def flow_ids(data: dict, wanted: str) -> set[str]:
    """The flows a name covers.

    Args:
        data: the loaded map.
        wanted: a flow id or a family id.

    Returns:
        The flow ids.
    """
    for fam in (data.get("drawing") or {}).get("families", []):
        if fam["id"] == wanted:
            return set(fam.get("flows", []))
    return {wanted}


def matches(step: dict, comps: dict, ask: Ask) -> bool:
    """Whether a step answers the question.

    Args:
        step: the step.
        comps: every component by id.
        ask: the question.

    Returns:
        True when every given field holds.
    """
    actor = comps[step["actor"]]["name"]
    every = [step["action"], step["actor"], actor, *step.get("writes", []), *step.get("reads", []), *step.get("failures", []), *step.get("code", [])]
    return all((not ask.file or any(c.partition(":")[0].endswith(ask.file) for c in step.get("code", [])),
                not ask.writes or _has(step.get("writes", []), ask.writes),
                not ask.failure or _has(step.get("failures", []), ask.failure),
                not ask.actor or _has([step["actor"], actor], ask.actor),
                not ask.text or _has(every, ask.text)))


def select(data: dict, ask: Ask) -> list[tuple[dict, list[dict]]]:
    """The steps that answer a question, by flow.

    Args:
        data: the loaded map.
        ask: the question.

    Returns:
        [(flow, its matching steps)], flows with none left out.
    """
    comps = {c["id"]: c for c in data["components"]}
    wanted = flow_ids(data, ask.flow) if ask.flow else None
    out = []
    for f in data["flows"]:
        if wanted is None or f["id"] in wanted:
            steps = [s for s in f["steps"] if matches(s, comps, ask)]
            if steps:
                out.append((f, steps))
    return out


def digest(found: list[tuple[dict, list[dict]]], comps: dict, states: dict) -> list[str]:
    """The answer as text.

    Args:
        found: select()'s result.
        comps: every component by id.
        states: {`<flow>/<step>`: "suspect", "new" or "broken"} from lockfile.findings().

    Returns:
        Lines: a flow's title and trigger, then per step its action, actor, transport, writes, failures and code.
    """
    lines = []
    for f, steps in found:
        lines += [f"## {f['id']}: {f['title']}", f"   {f['purpose']}", f"   trigger: {f['trigger']['kind']}: {f['trigger']['detail']}"]
        for s in steps:
            mark = states.get(f"{f['id']}/{s['id']}")
            lines.append(f"- {s['id']}{f' [{mark.upper()}: check the code]' if mark else ''} ({comps[s['actor']]['name']}, {' + '.join(s['via'])})")
            lines.append(f"    {s['action']}")
            lines += [f"    {name}: {'; '.join(map(str, s[key]))}" for key, name in (("writes", "writes"), ("failures", "fails"), ("code", "code")) if s.get(key)]
            lines += [f"    leads to: {', '.join(s['next'])}"] if s.get("next") else []
    return lines
