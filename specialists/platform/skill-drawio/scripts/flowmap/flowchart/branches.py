"""A step's `branches` drawn as diamonds: decisions its words state, expanded into steps for chart, lane and BPMN pages only, so step pages keep their
numbers. Stdlib only.

Imported, not run: `from flowmap.flowchart.branches import expand_branches` with the skill's scripts/ on sys.path.
"""

from __future__ import annotations

import re

from ..model import step_targets


def _short(words: str) -> str:
    """An outcome's words on an arrow: up to its first comma, colon or bracket, cut at a word.

    Args:
        words: the outcome.

    Returns:
        At most 16 characters.
    """
    head = re.split(r"[,:(]", words)[0].strip()
    return head if len(head) <= 16 else head[:16].rsplit(" ", 1)[0]


def _after_answer(words: str) -> str:
    """An outcome's words in a stop box, without the "no: " the arrow already says.

    Args:
        words: the outcome.

    Returns:
        The words after a short answer, else all of them.
    """
    head, sep, rest = words.partition(": ")
    return rest[0].upper() + rest[1:] if sep and len(head) <= 12 and rest else words


def _branch_nodes(step: dict, tag: str, on: str, after: str | None) -> list[dict]:
    """The diamond for one `branches` entry, and a stop for each of its stop outcomes.

    Args:
        step: the step the branch sits before.
        tag: the diamond's id.
        on: where a `run` outcome goes.
        after: where a `skip` outcome goes; None sends it to the flow's end, as a stop.

    Returns:
        The new steps, the diamond first; empty when every outcome goes to one place, which decides nothing.
    """
    branch, when, stops = step["_branch"], {}, []
    for k, text in enumerate(branch["outcomes"]):
        kind, _, words = text.partition(": ")
        short = _short(words)
        target = on if kind == "run" else after if kind == "skip" and after else f"{tag}-stop{k}"
        if target.startswith(f"{tag}-stop"):
            stops.append({"id": target, "actor": step["actor"], "action": words, "label": _after_answer(words)[:80], "via": step["via"], "shape": "terminator", "next": []})
        when[target] = f"{when[target]} / {short}" if target in when else short
    if len(when) < 2:
        return []
    ordered = sorted(when, key=lambda t: t != on)   # the way on first: it runs straight down
    return [{"id": tag, "actor": step["actor"], "action": branch["question"], "label": branch["question"][:80], "via": step["via"], "shape": "decision",
             "next": ordered, "when": {t: when[t] for t in ordered}}] + stops


def expand_branches(flow: dict) -> dict:
    """A flow with each step's `branches` drawn as diamonds before it, so a chart shows what a step's words only say. An outcome is tagged in the
    map: `run: ` goes into the step, `skip: ` past it, `stop: ` to a stop. Step pages ignore the key and keep their numbers.

    Args:
        flow: the flow.

    Returns:
        A flow with the diamonds as steps, or the flow itself when it has no branches.
    """
    steps = flow["steps"]
    if not any(s.get("branches") for s in steps):
        return flow
    out, first = [], {}
    for k, s in enumerate(steps):
        after = (step_targets(steps, k) or [None])[0]
        tail = s["id"]
        built = []
        for i, branch in reversed(list(enumerate(s.get("branches", [])))):
            nodes = _branch_nodes({**s, "_branch": branch}, f"{s['id']}~{i}", tail, after)
            if nodes:
                built = nodes + built
                tail = nodes[0]["id"]
        first[s["id"]] = tail
        out += built + [s]
    redirect = lambda t: first.get(t, t)   # an arrow into a step now enters its first diamond
    fixed = []
    for k, s in enumerate(out):
        if "next" in s:
            keep = s.get("shape") == "decision" and "~" in s["id"]
            s = {**s, "next": s["next"] if keep else [redirect(t) for t in s["next"]],
                 **({"when": {redirect(t): v for t, v in s["when"].items()}} if s.get("when") and not keep else {})}
        fixed.append(s)
    return {**flow, "steps": fixed}
