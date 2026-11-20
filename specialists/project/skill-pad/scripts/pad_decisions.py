#!/usr/bin/env python3
"""Mirror a project's decisions into its Pad workspace's `decisions` collection: one item per decided conflict and one per architecture or process row of a decision log.

Operator, 2026-11-18 (continuum): decisions belong in a dedicated Pad section, not in versions.toml. The project's records stay the truth: a
skill-knowledge-curator ledger (`.kc/decisions.jsonl`, folded with `.kc/conflicts.jsonl` for the question) and a Markdown decision log whose rows read
`| DL-nnn | YYYY-MM-DD | architecture or process | decision | reason | ... |`. Each Pad item carries `decision_ref` (conflict id or DL id); every version of a conflict's
decision is listed, newest current, with the claims it made current and superseded. Items are matched on `decision_ref`: new ones are created with an
op-key, changed bodies are rewritten (read back with `pad item show`), unchanged ones are left alone. Create the collection once with
`conventions/collection-schemas/decisions.json`.

Usage (from the project folder, whose .pad.toml names the workspace):
    python3 pad_decisions.py --project-root .                     # plan: how many to create and update
    python3 pad_decisions.py --project-root . --limit 1 --apply   # canary one create
    python3 pad_decisions.py --project-root . --apply             # write
Options: --decision-log PATH (default docs/architecture-review/DECISION-LOG.md; skipped when absent), --pad PATH, --timeout SECONDS (60).
Safety: plan by default; writes to Pad only with --apply; reads the project files only. Runtime budget: 60 s for about 110 items (rate-limited writes back off).
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
from pathlib import Path

DL_ROW = re.compile(r"^\| (DL-\d{3}) \| (\d{4}-\d{2}-\d{2}) \| (architecture|process) \| (.+?) \| (.*?) \| .*\|$")


def pad(binary: str, timeout: int, *args: str) -> str:
    """Run one pad command, backing off on a rate limit.

    Args:
        binary: the pad executable.
        timeout: seconds per call.
        *args: arguments after `pad`.

    Returns:
        The command's stdout.

    Raises:
        RuntimeError: when the command fails, or is still rate limited after five attempts.
    """
    for attempt in range(5):
        r = subprocess.run([binary, *args], capture_output=True, text=True, timeout=timeout)
        if r.returncode == 0:
            return r.stdout
        if "rate_limited" not in r.stderr + r.stdout:
            raise RuntimeError(f"pad {' '.join(args[:3])}: {(r.stderr or r.stdout).strip()[:300]}")
        time.sleep(1 + attempt)
    raise RuntimeError("pad: still rate limited after five attempts")


def fold(path: Path, key: str) -> dict:
    """Fold an append-only JSONL ledger into the latest merged record per key.

    Args:
        path: the JSONL file (absent means empty).
        key: the record key to group on.

    Returns:
        key value -> merged record.
    """
    out: dict = {}
    if path.is_file():
        for line in path.read_text().splitlines():
            if line.strip():
                r = json.loads(line)
                out[r[key]] = {**out.get(r[key], {}), **r}
    return out


def recommendation(text: str) -> str:
    """Read from a decision's reason whether the agent's recommendation was followed.

    Args:
        text: reason or decision text.

    Returns:
        followed, not-followed or none.
    """
    if "went against the (Recommended)" in text or "against the agent" in text:
        return "not-followed"
    return "followed" if ("followed the (Recommended)" in text or "followed the recommendation" in text) else "none"


def conflict_items(kc: Path) -> list[dict]:
    """Build one desired item per decided conflict from a curator ledger.

    Args:
        kc: the project's .kc folder.

    Returns:
        Desired items: ref, title, status, date, category, recommendation, body.
    """
    by_cf: dict = {}
    ledger = kc / "decisions.jsonl"
    for line in (ledger.read_text().splitlines() if ledger.is_file() else []):
        if line.strip():
            d = json.loads(line)
            by_cf.setdefault(d["conflict_id"], []).append(d)
    meta, items = fold(kc / "conflicts.jsonl", "conflict_id"), []
    for cf, versions in sorted(by_cf.items()):
        last, c = versions[-1], meta.get(cf, {})
        question = " ".join(c.get("question", "").split())
        rows = "\n".join(
            f"| v{n} | {v['decided_at'][:10]} | `{v['decision_id']}` | {v['action']} | {' '.join(str(v.get('answer_text') or '').split())} | "
            f"{', '.join(v.get('current_claims') or [])} | {', '.join(v.get('superseded_claims') or [])} |"
            for n, v in enumerate(versions, 1)
        )
        scope = f"Scope: {last['scope_note']}\n" if last.get("scope_note") else ""
        body = (
            f"Serves: .kc/decisions.jsonl ({cf})\nQuestion ({c.get('severity', '?')}): {question}\n"
            f"Current: v{len(versions)} `{last['decision_id']}` {last['action']}; reason: {' '.join(last.get('reason', '').split())}\n{scope}\n"
            "| Version | Date | Decision | Action | Answer | Current claims | Superseded claims |\n| --- | --- | --- | --- | --- | --- | --- |\n"
            f"{rows}\n\nGenerated by skill-pad pad_decisions.py; the ledger is the truth. Read-only view: change a decision in chat or the decision log; edits made here are overwritten at the next sync."
        )
        category = c.get("topic_key") or ",".join(c.get("categories") or []) or "conflict"
        status = "deferred" if last["action"] == "DEFER" else "accepted"
        items.append({"ref": cf, "title": f"{cf}: {question[:90]}", "status": status, "date": last["decided_at"][:10], "category": category,
                      "recommendation": recommendation(last.get("reason", "")), "body": body})
    return items


def table_rows(lines: list[str]) -> list[list[str]]:
    """Read Markdown table rows as cell lists, joining the continuation rows the Markdown hook writes when it wraps a long row.

    A row whose first cell is empty continues the row above it: each of its non-empty cells is appended, with a space, to the same cell above
    (2026-11-20: wrapped rows were read as their first line only, so long decisions and reasons reached Pad cut short). Separator rows are skipped.

    Args:
        lines: the file's lines.

    Returns:
        One list of stripped cells per logical row, in order.
    """
    rows: list[list[str]] = []
    for line in lines:
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if all(re.fullmatch(r":?-+:?", c) for c in cells if c):
            continue
        if rows and not cells[0] and len(cells) == len(rows[-1]):
            rows[-1] = [f"{a} {b}".strip() if b else a for a, b in zip(rows[-1], cells)]
        else:
            rows.append(cells)
    return rows


def log_items(path: Path) -> list[dict]:
    """Build one desired item per architecture or process row of a decision log (process rows since 2026-11-19: the operator wants every decision in Pad).

    Columns are `ID | Date | Kind | Decision | Reason | ...`; wrapped rows are joined first (table_rows). An optional `Status` column (2026-11-20) sets the
    Pad status: accepted, deferred, rejected, or "superseded by DL-nnn" (status superseded, with the replacing decision named in the body); without it
    every row is accepted, as before.

    Args:
        path: the decision log (absent means none).

    Returns:
        Desired items for its DL rows.
    """
    items = []
    status_col = None
    for cells in table_rows(path.read_text().splitlines() if path.is_file() else []):
        if cells and cells[0].lower() in ("id", "ref") and "status" in [c.lower() for c in cells]:
            status_col = [c.lower() for c in cells].index("status")
            continue
        m = DL_ROW.match("| " + " | ".join(cells) + " |") if len(cells) >= 6 else None
        if not m:
            continue
        dl, date, kind, decision, reason = m.groups()
        raw = cells[status_col].lower() if status_col is not None and status_col < len(cells) else "accepted"
        sup = re.search(r"superseded by (DL-\d{3})", raw, re.IGNORECASE)
        status = "superseded" if sup else raw if raw in ("accepted", "deferred", "rejected") else "accepted"
        tail = f"\nSuperseded by: {sup.group(1).upper()}" if sup else ""
        body = (f"Serves: {path.name} ({dl})\nDecision: {decision}\nReason: {reason}{tail}\n\nGenerated by skill-pad pad_decisions.py; the decision log is the truth. "
                "Read-only view: change a decision in chat or the decision log; edits made here are overwritten at the next sync.")
        items.append({"ref": dl, "title": f"{dl}: {decision[:90]}", "status": status, "date": date, "category": "decision-log" if kind == "architecture" else "decision-log-process",
                      "recommendation": recommendation(decision), "body": body})
    return items


def plan(want: list[dict], have: dict, body_of) -> tuple[list[dict], list[dict]]:
    """Split desired items into creates and updates.

    Args:
        want: desired items.
        have: decision_ref -> Pad item ref already present.
        body_of: callable returning the current body of a Pad item ref.

    Returns:
        (items to create, items to update).
    """
    creates = [w for w in want if w["ref"] not in have]
    updates = [w for w in want if w["ref"] in have and body_of(have[w["ref"]]).strip() != w["body"].strip()]
    return creates, updates


def existing(binary: str, timeout: int) -> dict:
    """Read the items already in the decisions collection, including closed ones.

    Args:
        binary: the pad executable.
        timeout: seconds per call.

    Returns:
        decision_ref -> Pad item ref.
    """
    data = json.loads(pad(binary, timeout, "item", "list", "decisions", "--all", "--format", "json", "--limit", "1000") or "[]")
    out = {}
    for it in data.get("items", data) if isinstance(data, dict) else data:
        fields = it.get("fields") or {}
        fields = json.loads(fields) if isinstance(fields, str) else fields
        if fields.get("decision_ref"):
            out[fields["decision_ref"]] = it.get("ref")
    return out


def apply(binary: str, timeout: int, creates: list[dict], updates: list[dict], have: dict, prefix: str) -> None:
    """Write the creates and updates to Pad.

    Args:
        binary: the pad executable.
        timeout: seconds per call.
        creates: items to create.
        updates: items to rewrite.
        have: decision_ref -> Pad item ref.
        prefix: op-key prefix (the project folder name).

    Returns:
        None.

    Raises:
        RuntimeError: when a pad call fails.
    """
    for w in creates:
        fields = [f"status={w['status']}", f"category={w['category']}", f"decision_date={w['date']}", f"decision_ref={w['ref']}", f"recommendation={w['recommendation']}"]
        pad(binary, timeout, "item", "create", "decisions", w["title"], "--content", w["body"], *[x for f in fields for x in ("--field", f)], "--op-key", f"{prefix}-decision-{w['ref']}")
    for w in updates:
        pad(binary, timeout, "item", "update", have[w["ref"]], "--content", w["body"], "--field", f"status={w['status']}", "--replace", "--comment", "Source changed; re-mirrored by pad_decisions.py")


def main(argv: list[str] | None = None) -> int:
    """Plan or apply the mirror.

    Args:
        argv: command-line arguments; None uses sys.argv.

    Returns:
        0 when planned or applied; 1 when a pad call fails.
    """
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    ap.add_argument("--project-root", type=Path, default=Path("."))
    ap.add_argument("--decision-log", type=Path, default=Path("docs/architecture-review/DECISION-LOG.md"))
    ap.add_argument("--pad", default="pad")
    ap.add_argument("--timeout", type=int, default=60)
    ap.add_argument("--limit", type=int, help="create at most N items (canary)")
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args(argv)
    root = a.project_root.resolve()
    try:
        have = existing(a.pad, a.timeout)
        want = conflict_items(root / ".kc") + log_items(root / a.decision_log)

        def body_of(ref: str) -> str:
            """Read one Pad item's current body.

            Args:
                ref: the Pad item ref.

            Returns:
                Its content.
            """
            return json.loads(pad(a.pad, a.timeout, "item", "show", ref, "--format", "json")).get("content", "")

        creates, updates = plan(want, have, body_of)
        creates = creates[: a.limit] if a.limit else creates
        print(f"decisions: {len(want)} wanted, {len(creates)} to create, {len(updates)} to update")
        if not a.apply:
            print("plan only; --apply writes to Pad")
            return 0
        apply(a.pad, a.timeout, creates, updates, have, root.name)
    except RuntimeError as error:
        print(f"pad_decisions: {error}", file=sys.stderr)
        return 1
    print(f"applied: {len(creates)} created, {len(updates)} updated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
