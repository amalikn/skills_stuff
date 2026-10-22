#!/usr/bin/env python3
"""Render a plan tracker's Timeline from a YAML file of dated rows, with each row's schedule worked out from today's date.

Operator, 2026-10-21: the Timeline must show where a due date was missed or is slipping, and the marks must not freeze when nobody edits
the page (a side agent found a step would still read "at risk" after its date). So the Schedule column is never typed: LATE (with days),
DUE TODAY, Done, Not yet due come from `due`, `done` and today; At risk, On track and Ahead are a person's `flag`, and a passed due date
shows LATE whatever the flag. A `parked` row (waiting on a decision or another stage) shows Parked until it gets a date again. The page
keeps its hand-written text; only the block between the plan-timeline markers is generated. Piloted in unified-network-controller and
promoted into skill-ai-it on 2026-10-21 when smc-resiliency kept its timeline as data too ("we haven't adapted the timeline method of UNC").

The data file names the page (`render_to`), the sentence saying where the dates come from (`source`, optional `note`) and the columns after
Due and Schedule (`columns`: [{key, header}], default Stage, Step, Where it stands, Next with), so nothing here knows a project.

Reads the YAML and the target page. Without `--write` it writes nothing: it validates, compares the page with a render for today and exits
1 on a problem or a difference. A project's governance check calls evaluate(), fails on a problem and only notes a page that trails today;
a commit gate that renders first keeps every commit current for its day. `--write` replaces the generated block in the page; it touches
nothing outside the markers. Runtime: well under a second (one YAML file, one page; no network).

Usage (run with the project's venv; paths are relative to --project-root, default the current folder):
    python3 plan_timeline.py --project-root .                     # validate and report drift; exit 1 on a problem
    python3 plan_timeline.py --project-root . --write             # render the Timeline block into the page
    python3 plan_timeline.py --project-root . --today 2026-10-24  # as above, for another day (tests, previews)
    python3 plan_timeline.py --project-root . --data docs/trackers/plan-timeline.yaml
"""

from __future__ import annotations

import argparse
import datetime as dt
import sys
from dataclasses import dataclass
from pathlib import Path

import yaml

DATA = "docs/trackers/plan-timeline.yaml"
END = "<!-- END GENERATED: plan-timeline -->"
FLAGS = {"at_risk": "🟡 **At risk**", "on_track": "🟢 On track", "ahead": "🔵 Ahead"}
KINDS = ("plan", "fixed", "extra", "parked")
#: Row fields the renderer itself reads; every other field must be a declared column.
CORE_FIELDS = frozenset({"due", "week", "done", "flag", "kind", "stage", "step", "after"})
DEFAULT_COLUMNS = ({"key": "stage", "header": "Stage"}, {"key": "step", "header": "Step"},
                   {"key": "where", "header": "Where it stands"}, {"key": "next_with", "header": "Next with"})
#: A "Wk of" step is late after the Friday of that week.
WEEK_DEADLINE_DAYS = 4


def begin_marker(data: str) -> str:
    """The BEGIN marker, naming the data file a reader must edit.

    Args:
        data: the data file's repo-relative path.

    Returns:
        The marker line.
    """
    return f"<!-- BEGIN GENERATED: plan-timeline (edit {data}, then `just plan-timeline`) -->"


#: The BEGIN marker for the default data path.
BEGIN = begin_marker(DATA)


@dataclass
class Outcome:
    """What a run found.

    Args:
        problems: validation failures; any one makes the run fail.
        block: the rendered block, or None when the data is invalid.
        drift: True when the page on disk differs from the render.
    """

    problems: list[str]
    block: str | None = None
    drift: bool = False


def _date(value: object, where: str, problems: list[str]) -> dt.date | None:
    """Read a YAML date field.

    Args:
        value: the field as YAML parsed it (a date, a string or None).
        where: the row and field, for the message.
        problems: list the failure is added to.

    Returns:
        The date, or None when absent or invalid.
    """
    if value is None:
        return None
    if isinstance(value, dt.date):
        return value
    try:
        return dt.date.fromisoformat(str(value))
    except ValueError:
        problems.append(f"{where}: {value!r} is not a YYYY-MM-DD date")
        return None


def _days(n: int) -> str:
    """A day count in words.

    Args:
        n: the number of days.

    Returns:
        "1 day" or "n days".
    """
    return f"{n} day" + ("" if n == 1 else "s")


def deadline(row: dict) -> dt.date | None:
    """The last day a row can be done without being late.

    Args:
        row: a validated row (its `due` already a date).

    Returns:
        `due`, or that week's Friday for a `week: true` row; None for a row without a due date.
    """
    due = row.get("due")
    if due is None:
        return None
    return due + dt.timedelta(days=WEEK_DEADLINE_DAYS) if row.get("week") else due


def due_label(row: dict, with_year: bool = False) -> str:
    """The Due cell as people read it.

    Args:
        row: a validated row.
        with_year: add the year (the timeline spans more than one year, so "Wk of 25 Jan" alone is ambiguous; smc-resiliency, 2026-10-21).

    Returns:
        "Fri 16 Oct", "Wk of 25 Jan 2027", "Not in the plan" for an extra row, or "No date" for a parked row without one.
    """
    due = row.get("due")
    if due is None:
        return "No date" if row.get("kind") == "parked" else "Not in the plan"
    day = f"{due.day} {due:%b}" + (f" {due.year}" if with_year else "")
    return f"Wk of {day}" if row.get("week") else f"{due:%a} {day}"


def in_order(rows: list[dict]) -> list[dict]:
    """Rows in due-date order (a week row counts from its Monday); an undated row with `after: <stage>` follows that stage's row, the other
    undated rows come last in file order (operator, 2026-10-21: order by Due; unplanned work "in the logical order, not everything at the bottom").

    Args:
        rows: validated rows, in file order.

    Returns:
        The rows ordered: on one date extra rows before plan rows; otherwise the sort is stable, so rows with the same date and kind, or
        placed after the same stage, keep their file order.
    """
    # on one date an extra row (work outside the plan) comes before the plan rows it feeds
    dated = sorted((r for r in rows if r.get("due") is not None), key=lambda r: (r["due"], r.get("kind", "plan") != "extra"))
    placed = {}
    for r in rows:
        if r.get("due") is None and r.get("after"):
            placed.setdefault(r["after"], []).append(r)
    out: list[dict] = []
    for r in dated:
        out.append(r)
        out.extend(placed.pop(r.get("stage") or "", []) if r.get("stage") else [])
    return out + [r for r in rows if r.get("due") is None and not r.get("after")]


def schedule(row: dict, today: dt.date) -> tuple[str, str]:
    """Work out a row's Schedule cell.

    Args:
        row: a validated row.
        today: the date to judge against.

    Returns:
        (cell text, state) where state is one of done, late, today, flagged, open, fixed, extra, parked. An extra row (work the plan does not
        list) with a `due` is scheduled like a plan row, so needed work outside the plan can still show LATE.
    """
    kind = row.get("kind", "plan")
    if kind == "extra" and row.get("due") is None:   # an extra row with a target date is tracked like a plan row (smc-resiliency, 2026-10-21)
        return "➖ Unscheduled", "extra"
    if kind == "parked":
        return "⏸️ Parked", "parked"
    if kind == "fixed":
        return ("📌 Fixed date" if row["due"] >= today else "📌 Passed"), "fixed"
    end, done = deadline(row), row.get("done")
    if done is not None:
        late = (done - end).days
        return (f"✅ Done {done.day} {done:%b}" + (f", {_days(late)} late" if late > 0 else "")), "done"
    if today > end:
        return f"🔴 **LATE: {_days((today - end).days)}**", "late"
    if today == end:
        return "🟠 **DUE TODAY**", "today"
    if row.get("flag"):
        return FLAGS[row["flag"]], "flagged"
    return "⚪ Not yet due", "open"


def columns_of(data: dict, data_path: str = DATA) -> tuple[list[dict], list[str]]:
    """The columns after Due and Schedule, from the data's `columns` or the defaults.

    Args:
        data: the parsed YAML document.
        data_path: the data file's path, for messages.

    Returns:
        (columns as {key, header}, problems).
    """
    raw = data.get("columns")
    if raw is None:
        return [dict(c) for c in DEFAULT_COLUMNS], []
    if not isinstance(raw, list) or not all(isinstance(c, dict) and c.get("key") and c.get("header") for c in raw):
        return [], [f"{data_path}: `columns` must be a list of {{key, header}}"]
    return [{"key": str(c["key"]), "header": str(c["header"])} for c in raw], []


def validate(data: object, data_path: str = DATA) -> tuple[list[dict], list[str]]:
    """Check the YAML's shape and normalise its rows.

    Args:
        data: the parsed YAML document.
        data_path: the data file's path, for messages.

    Returns:
        (rows with dates parsed, problems).
    """
    problems: list[str] = []
    if not isinstance(data, dict) or not isinstance(data.get("rows"), list):
        return [], [f"{data_path}: expected a mapping with a `rows` list"]
    columns, problems = columns_of(data, data_path)
    known = CORE_FIELDS | {c["key"] for c in columns}
    rows: list[dict] = []
    for n, raw in enumerate(data["rows"], 1):
        where = f"{data_path} row {n}"
        if not isinstance(raw, dict):
            problems.append(f"{where}: not a mapping")
            continue
        row = dict(raw)
        for key in sorted(set(row) - known):
            problems.append(f"{where}: field `{key}` is neither a core field nor a declared column")
        kind = row.get("kind", "plan")
        if kind not in KINDS:
            problems.append(f"{where}: kind {kind!r} is not one of {', '.join(KINDS)}")
        row["due"] = _date(row.get("due"), f"{where} due", problems)
        row["done"] = _date(row.get("done"), f"{where} done", problems)
        if kind not in ("extra", "parked") and row["due"] is None:
            problems.append(f"{where}: a {kind} row needs `due`")
        if row.get("flag") is not None and row["flag"] not in FLAGS:
            problems.append(f"{where}: flag {row['flag']!r} is not one of {', '.join(FLAGS)}")
        if not row.get("step"):
            problems.append(f"{where}: `step` is empty")
        if row.get("after") and row["due"] is not None:
            problems.append(f"{where}: `after` places an undated row; a row with `due` is placed by its date")
        rows.append(row)
    stages = {r.get("stage") for r in rows if r.get("due") is not None and r.get("stage")}
    for n, row in enumerate(rows, 1):
        if row.get("after") and row["after"] not in stages:
            problems.append(f"{data_path} row {n}: `after: {row['after']}` names no dated row's stage")
    return rows, problems


def render(rows: list[dict], source: str, today: dt.date, columns: list[dict] | None = None, note: str = "", data_path: str = DATA) -> str:
    """Render the generated block: legend, counts and the table.

    Args:
        rows: validated rows; shown in due-date order (`in_order`).
        source: the sentence naming where the dates come from.
        today: the date the schedule is judged against.
        columns: the columns after Due and Schedule; default DEFAULT_COLUMNS.
        note: a sentence printed after the source one (how to read a project-specific column).
        data_path: the data file's path, named in the BEGIN marker.

    Returns:
        The block, markers included, ending without a newline.
    """
    columns = list(columns or DEFAULT_COLUMNS)
    rows = in_order(rows)
    years = {r["due"].year for r in rows if r.get("due")}
    cells, states = [], {}
    for row in rows:
        text, state = schedule(row, today)
        states.setdefault(state, []).append(row.get("stage") or "")
        cells.append((due_label(row, len(years) > 1), text, *(str(row.get(c["key"], "") or "") for c in columns)))
    at_risk = [r.get("stage", "") for r in rows if r.get("flag") == "at_risk" and schedule(r, today)[1] == "flagged"]

    def count(icon: str, word: str, ids: list[str]) -> str:
        """One part of the count line.

        Args:
            icon: the state's icon.
            word: the state in words ("late").
            ids: the stage ids in that state.

        Returns:
            For example "🔴 1 late (U1.1)".
        """
        return f"{icon} {len(ids)} {word}" + (f" ({', '.join(ids)})" if ids else "")

    parts = [count("🔴", "late", states.get("late", [])), count("🟠", "due today", states.get("today", [])), count("🟡", "at risk", at_risk)]
    if states.get("parked"):
        parts.append(count("⏸️", "parked", states["parked"]))
    lines = [
        begin_marker(data_path),
        f"Dates and steps are {source}." + (f" {note}" if note else ""),
        "",
        f"Schedule as of **{today:%a} {today.day} {today:%b %Y}**, worked out from the dates on each render: 🔴 **LATE** the due date passed and the step is not done (days late);",
        "🟠 **DUE TODAY**; ✅ Done; ⚪ Not yet due; 📌 an outside date; ➖ not in the plan. A person sets 🟡 **At risk** (blocked or short of time),",
        "🟢 On track and 🔵 Ahead; a passed due date shows LATE whatever is set.",
    ]
    if states.get("parked"):
        lines.append("⏸️ Parked: waiting on a decision or on other stages, without a date; the row says why.")
    lines += [
        "",
        "Now: **" + ", ".join(parts) + "**.",
        "",
        "| Due | Schedule | " + " | ".join(c["header"] for c in columns) + " |",
        "| --- | --- | " + " | ".join("---" for _ in columns) + " |",
    ]
    lines += ["| " + " | ".join(c) + " |" for c in cells]
    lines.append(END)
    return "\n".join(lines)


def splice(page: str, block: str) -> str:
    """Put the block between the markers of the page.

    Args:
        page: the page's text.
        block: the rendered block, markers included (its first line is the BEGIN marker).

    Returns:
        The page with its generated block replaced.

    Raises:
        ValueError: when the page lacks the markers or holds them more than once or out of order.
    """
    begin = block.split("\n", 1)[0]
    start, stop = page.find(begin), page.find(END)
    if page.count(begin) != 1 or page.count(END) != 1 or stop < start:
        raise ValueError("the page needs exactly one plan-timeline BEGIN marker followed by one END marker")
    return page[:start] + block + page[stop + len(END):]


def evaluate(root: Path, today: dt.date, data_path: str = DATA) -> Outcome:
    """Validate the data and compare the page with a render for today.

    Args:
        root: the project root.
        today: the date to judge against.
        data_path: the data file, relative to root.

    Returns:
        The outcome; `block` is None when the data is invalid.
    """
    path = root / data_path
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        return Outcome([f"{data_path}: cannot be read ({exc})"])
    rows, problems = validate(data, data_path)
    if problems:
        return Outcome(problems)
    columns, _ = columns_of(data, data_path)
    block = render(rows, str(data.get("source", "")).strip(), today, columns, " ".join(str(data.get("note", "")).split()), data_path)
    page_path = root / str(data.get("render_to", ""))
    try:
        page = page_path.read_text(encoding="utf-8")
        drift = splice(page, block) != page
    except (OSError, ValueError) as exc:
        return Outcome([f"{data.get('render_to')}: {exc}"], block)
    return Outcome([], block, drift)


def main(argv: list[str] | None = None) -> int:
    """Command line: validate and report, or `--write` the block.

    Args:
        argv: arguments (default: sys.argv).

    Returns:
        0 when valid and current (or written), 1 otherwise.
    """
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--project-root", type=Path, default=Path("."), help="the project holding the data file (default: the current folder)")
    ap.add_argument("--data", default=DATA, help=f"the data file, relative to the project root (default {DATA})")
    ap.add_argument("--write", action="store_true", help="render the Timeline block into the page")
    ap.add_argument("--today", type=dt.date.fromisoformat, default=dt.date.today(), help="judge against this date (YYYY-MM-DD)")
    args = ap.parse_args(argv)
    root = args.project_root.resolve()
    outcome = evaluate(root, args.today, args.data)
    for p in outcome.problems:
        print(f"plan-timeline: {p}", file=sys.stderr)
    if outcome.problems:
        return 1
    data = yaml.safe_load((root / args.data).read_text(encoding="utf-8"))
    page_path = root / str(data["render_to"])
    if args.write:
        if outcome.drift:
            page_path.write_text(splice(page_path.read_text(encoding="utf-8"), outcome.block), encoding="utf-8")
            print(f"wrote the Timeline block in {data['render_to']} (as of {args.today})")
        else:
            print(f"{data['render_to']} Timeline already current")
        return 0
    if outcome.drift:
        print(f"{data['render_to']}: the Timeline differs from a render for {args.today}; run `just plan-timeline`", file=sys.stderr)
        return 1
    print(f"{data['render_to']} Timeline current for {args.today}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
