"""The words in a flow page's step box and note. Split from flowmap.pages to keep that module within its size budget. Stdlib only.

Imported, not run: `from flowmap.step_text import step_lines, note_lines` with the skill's scripts/ on sys.path.
"""

from __future__ import annotations

from drawio.mxfile import BLANK, heading

#: A step note's sections, in reading order: (step key, heading, whether its items are code).
NOTE_SECTIONS = (("reads", "Reads", False), ("writes", "Writes", False), ("code", "Code", True), ("failures", "Fails", False), ("look", "Look", False))


def action_clauses(text: str) -> list[str]:
    """An action's clauses: split on "; " outside brackets only, so a bracketed aside stays whole (operator review 2026-10-22: "(the operator's
    click; agents never approve)" was cut into two bullets).

    Args:
        text: the step's action.

    Returns:
        The non-empty clauses, stripped.
    """
    out, depth, cur, i = [], 0, "", 0
    while i < len(text):
        if depth == 0 and text.startswith("; ", i):
            out, cur, i = out + [cur], "", i + 2
            continue
        depth = max(0, depth + (text[i] in "([{") - (text[i] in ")]}"))
        cur, i = cur + text[i], i + 1
    return [c.strip() for c in out + [cur] if c.strip()]


def step_lines(step: dict, number: int, bullets: bool = True, scale: int = 100) -> list[str]:
    """A step box's text: the bold title, a blank line, the action, a blank line, the transport in italics, the gate in bold and the status.

    Args:
        step: the step from the map.
        number: its position in the flow.
        bullets: set an action of clauses joined by "; " one clause a line (`drawing.look.action_bullets`).
        scale: the title's size, percent of the box font (`drawing.look.heading_scale`).

    Returns:
        Label lines for drawio.mxfile.label().
    """
    clauses = action_clauses(step["action"])
    action = [step["action"]] if not bullets else clauses if len(clauses) == 1 else [f"• {c}" for c in clauses]   # one clause a line: long actions read as a list
    return ([heading(f"**{number}. {step['id']}**", scale), BLANK] + action + [BLANK, f"*via {' + '.join(step['via'])}*"]
            + ([f"**GATE: {step['gate']}**"] if step.get("gate") else [])
            + ([f"*{step['status']['state']} since {step['status']['since']}*"] if step.get("status") else []))


def note_lines(step: dict, number: int) -> list[str]:
    """A step note as sections: the title, then per non-empty section a blank line, a bold heading and one bullet per item (code in monospace).

    Args:
        step: the step from the map.
        number: its position in the flow.

    Returns:
        Label lines for drawio.mxfile.label().
    """
    out = [f"**{number}. {step['id']}**"]
    for key, heading, is_code in NOTE_SECTIONS:
        if step.get(key):
            out += [BLANK, f"**{heading}**"] + [f"• `{item}`" if is_code else f"• {item}" for item in step[key]]
    return out
