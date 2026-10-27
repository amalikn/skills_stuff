#!/usr/bin/env python3
"""Start a project's plan tracker page and check that it keeps its shape.

Operator, 2026-10-22: "Ensure that plan tracker setup and maintenance is written back to skill-ai-it ... so that all the projects can follow it."
Piloted in smc-resiliency (2026-10-21) and unified-network-controller; both pages share this shape: Where we are (with an "As of" date), the
generated Timeline, What next, Which document to follow, Decided but not yet in the designs, the generated Stages, How this page is kept.

`--init` prints the starter page (templates/plan-tracker.md) and, with `--apply`, writes it when the page does not exist; it never overwrites.
The default run checks the page and lists problems; `--check` exits 1 on any. Problems:
  - a required section is missing (matched by heading prefix, so "Decided but not yet in a design" passes);
  - Where we are has no "As of YYYY-MM-DD" line;
  - a What next row has no link (every row links to where its work starts);
  - a What next row is split over continuation rows (blank first cell): the markdown hook splits a row whose rendered width passes 200
    columns, and a split row reads as two items in the table a reader starts from;
  - a detail block under What next (a `### ` heading) has no "Done when".
What next is a one-line table plus one detail block per row (operator, 2026-10-22, smc-resiliency: "I'm still not able to understand what is
really required next and what would the done when really make sense"): the row links to its block (`#<heading slug>`), and the block says what
is needed, why now, what is in hand and a Done when checklist.
Notes (never fail): a What next row with no link to a detail block on the page; a split row in any other hand-written table; the "As of" date is older than the newest CHANGELOG entry's date; a
generated block marker is absent.

Read-only unless `--init --apply`. Runtime: well under a second (one page and the CHANGELOG headings; no network, no subprocess).

Usage:
    python3 plan_tracker.py --project-root .                    # report
    python3 plan_tracker.py --project-root . --check            # exit 1 on a problem
    python3 plan_tracker.py --project-root . --init             # print the starter page
    python3 plan_tracker.py --project-root . --init --apply     # write it (only when absent)
"""

from __future__ import annotations

import argparse
import datetime as dt
import re
import sys
from pathlib import Path

PAGE = "docs/trackers/plan-tracker.md"
TEMPLATE = Path(__file__).resolve().parents[2] / "templates/plan-tracker.md"
SECTIONS = ("Where we are", "What next", "Which document to follow", "Decided but not yet in", "Stages", "How this page is kept")
MARKERS = ("BEGIN GENERATED: plan-timeline", "BEGIN GENERATED: target-map")
_AS_OF = re.compile(r"^As of (\d{4}-\d{2}-\d{2})", re.M)
_CHANGELOG_STAMP = re.compile(r"^## (\d{4})(\d{2})(\d{2})_\d{4}", re.M)
_GENERATED = re.compile(r"<!-- BEGIN GENERATED:.*?<!-- END GENERATED:[^>]*-->", re.S)
_LINK = re.compile(r"\]\([^)\s]+\)")
_IN_PAGE = re.compile(r"\]\(#([^)\s]+)\)")
_DETAIL = re.compile(r"^### (.+)$", re.M)


def slug(heading: str) -> str:
    """The anchor GitHub and VS Code give a heading.

    Args:
        heading: the heading text, without the hashes.

    Returns:
        Lower case, punctuation other than hyphens and underscores dropped, spaces as hyphens.
    """
    return re.sub(r"[^\w\- ]", "", heading.strip().lower()).replace(" ", "-")


def detail_blocks(body: str) -> dict[str, str]:
    """The `### ` blocks inside a section body, by anchor.

    Args:
        body: section text.

    Returns:
        {heading slug: block text up to the next `### ` heading}.
    """
    parts = _DETAIL.split(body)
    return {slug(parts[i]): parts[i + 1] for i in range(1, len(parts) - 1, 2)}


def sections(text: str) -> dict[str, str]:
    """Split a page into its level-2 sections.

    Args:
        text: the page.

    Returns:
        {heading text: body up to the next level-2 heading}.
    """
    parts = re.split(r"^## (.+)$", text, flags=re.M)
    return {parts[i].strip(): parts[i + 1] for i in range(1, len(parts) - 1, 2)}


def find(secs: dict[str, str], prefix: str) -> str | None:
    """The body of the first section whose heading starts with prefix.

    Args:
        secs: output of sections().
        prefix: heading prefix.

    Returns:
        The body, or None when no heading matches.
    """
    return next((body for head, body in secs.items() if head.startswith(prefix)), None)


def table_rows(body: str) -> list[list[str]]:
    """Data rows of the markdown tables in a section body: in each run of `|` lines, the first is the header and the second the delimiter.

    Args:
        body: section text.

    Returns:
        One list of stripped cells per data row.
    """
    rows: list[list[str]] = []
    block: list[str] = []
    for line in body.splitlines() + [""]:
        if line.startswith("|"):
            block.append(line)
            continue
        for row in block[2:]:
            rows.append([c.strip() for c in row.strip().strip("|").split("|")])
        block = []
    return rows


def check(root: Path, page: str = PAGE) -> tuple[list[str], list[str]]:
    """Check a project's plan tracker page.

    Args:
        root: the project root.
        page: the page, relative to root.

    Returns:
        (problems, notes); problems fail `--check`, notes never do.
    """
    path = root / page
    if not path.is_file():
        return [f"{page} does not exist; start it with --init --apply"], []
    text = path.read_text(encoding="utf-8")
    hand = _GENERATED.sub("", text)
    secs = sections(hand)
    problems, notes = [], []
    for name in SECTIONS:
        if find(secs, name) is None:
            problems.append(f"{page}: no section starting `## {name}`")
    where = find(secs, "Where we are") or ""
    as_of = _AS_OF.search(where)
    if not as_of:
        problems.append(f"{page}: Where we are has no `As of YYYY-MM-DD` line")
    nxt = find(secs, "What next") or ""
    blocks = detail_blocks(nxt)
    for anchor, block in blocks.items():
        if "Done when" not in block:
            problems.append(f"{page}: What next block #{anchor} has no `Done when`")
    for cells in table_rows(nxt):
        row = " ".join(cells)
        if cells and cells[0] and not _LINK.search(row):
            problems.append(f"{page}: What next row {cells[0]} has no link to where its work starts")
        elif cells and cells[0] and not any(a in blocks for a in _IN_PAGE.findall(row)):
            notes.append(f"{page}: What next row {cells[0]} links to no detail block on this page (what is needed, why now, in hand, Done when)")
    for head, body in secs.items():
        if any(not c[0] and any(c[1:]) for c in table_rows(body) if c):
            # The markdown hook splits a row whose rendered width passes 200 columns; What next is where a reader starts, so there it fails.
            (problems if head.startswith("What next") else notes).append(
                f"{page}: a row in `{head}` is split over continuation rows (rendered wider than 200 columns); shorten it to one line")
    for marker in MARKERS:
        if marker not in text:
            notes.append(f"{page}: no `{marker}` block (generated by {'plan_timeline.py' if 'timeline' in marker else 'target_map.py'})")
    changelog = root / "CHANGELOG.md"
    if as_of and changelog.is_file():
        stamps = [dt.date(int(y), int(m), int(d)) for y, m, d in _CHANGELOG_STAMP.findall(changelog.read_text(encoding="utf-8"))]
        if stamps and max(stamps) > dt.date.fromisoformat(as_of.group(1)):
            notes.append(f"{page}: As of {as_of.group(1)} is older than the newest CHANGELOG entry ({max(stamps)}); is Where we are current?")
    return problems, notes


def init(root: Path, page: str, apply: bool) -> int:
    """Print the starter page, or write it when absent.

    Args:
        root: the project root.
        page: the page, relative to root.
        apply: write the page (only when it does not exist).

    Returns:
        0 on success, 1 when the page exists and --apply was given.
    """
    today = dt.date.today().isoformat()
    # The template carries a real date so the skill's own freshness check passes; a new page is stamped with today.
    body = re.sub(r"^Last reviewed: .*$", f"Last reviewed: {today}", TEMPLATE.read_text(encoding="utf-8"), count=1, flags=re.M)
    body = body.replace("{today}", today)
    path = root / page
    if not apply:
        print(f"plan: would write {path} ({len(body.splitlines())} lines); rerun with --apply\n")
        print(body)
        return 0
    if path.exists():
        print(f"refusing: {path} exists; never overwritten")
        return 1
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")
    print(f"wrote {path}: replace every TODO, add the Timeline and target-map embeds (just plan-timeline, just target-map)")
    return 0


def main(argv: list[str] | None = None) -> int:
    """Run --init or the check.

    Args:
        argv: command-line arguments (default sys.argv[1:]).

    Returns:
        The exit code.
    """
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--project-root", type=Path, default=Path("."))
    ap.add_argument("--page", default=PAGE)
    ap.add_argument("--check", action="store_true", help="exit 1 on a problem")
    ap.add_argument("--init", action="store_true", help="print (or with --apply write) the starter page")
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args(argv)
    if args.init:
        return init(args.project_root, args.page, args.apply)
    problems, notes = check(args.project_root, args.page)
    for line in problems:
        print(f"problem: {line}")
    for line in notes:
        print(f"note: {line}")
    if not problems:
        print(f"OK — plan tracker: {len(SECTIONS)} sections; What next rows linked and on one line, detail blocks with Done when")
    return 1 if problems and args.check else 0


if __name__ == "__main__":
    sys.exit(main())
