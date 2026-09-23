#!/usr/bin/env python3
"""Render a derived Markdown scorecard from a suite and append-only history."""

from __future__ import annotations

import argparse
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from eval_common import EvalError, eval_index, load_document, load_jsonl, parse_duration, parse_iso, slice_ids


def escape(value: Any) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--suite", required=True)
    parser.add_argument("--history", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--now", help="ISO-8601 render time; defaults to current UTC")
    args = parser.parse_args()
    try:
        suite = load_document(args.suite)
        now = parse_iso(args.now, "--now") if args.now else datetime.now(timezone.utc)
        records = load_jsonl(args.history)
        definitions = eval_index(suite)
        observations = [record for record in records if record.get("record_type") == "observation"]
        invalidations = [record for record in records if record.get("record_type") == "invalidation"]
        latest: dict[tuple[str, str], dict[str, Any]] = {}
        for record in observations:
            key = (record.get("eval_id"), record.get("population_slice_id"))
            if key not in latest or parse_iso(record["recorded_at"], "recorded_at") > parse_iso(latest[key]["recorded_at"], "recorded_at"):
                latest[key] = record
        invalidated_by: dict[tuple[str, str], tuple[Any, dict[str, Any]]] = {}
        for record in invalidations:
            key = (record.get("eval_id"), record.get("population_slice_id"))
            point = parse_iso(record["recorded_at"], "recorded_at")
            if key not in invalidated_by or point > invalidated_by[key][0]:
                invalidated_by[key] = (point, record)
        rows: list[tuple[str, str, str, str, str, str]] = []
        for eval_id, definition in definitions.items():
            for slice_id in sorted(slice_ids(definition)):
                record = latest.get((eval_id, slice_id))
                if record is None:
                    rows.append((eval_id, slice_id, "not_evaluated", "—", "—", "no observation"))
                    continue
                observed = parse_iso(record["observed_at"], "observed_at")
                max_age = definition["validity"]["max_age"]
                # Age and declared change are distinct ways a verdict dies. Reporting them as one
                # reason merges states that call for different actions: re-run it, versus work out
                # what changed. Naming the trigger is the whole point of invalidate_on.
                expired = now - observed > parse_duration(max_age, f"{eval_id}.validity")
                change = invalidated_by.get((eval_id, slice_id))
                invalidated = change is not None and change[0] > observed
                causes = []
                if invalidated:
                    trigger = change[1].get("reason") or "declared change"
                    ref = change[1].get("reference")
                    causes.append(f"invalidated: {trigger}" + (f" ({ref})" if ref else ""))
                if expired:
                    causes.append(f"expired: older than {max_age}")
                stale = expired or invalidated
                state = "stale" if stale else record["verdict"]
                reason = "; ".join(causes) if stale else "current recorded verdict"
                rows.append((eval_id, slice_id, state, record["verdict"], record["observed_at"], reason))
        counts = Counter(row[2] for row in rows)
        lines = [f"# Evaluation report: {suite['suite']['title']}", "", "## Contents", "", "- [Scorecard](#scorecard)", "- [Interpretation](#interpretation)", "", "## Scorecard", "", f"Rendered at: {now.replace(microsecond=0).isoformat().replace('+00:00', 'Z')}", "", "| Eval | Slice | Derived state | Recorded verdict | Observed at | Reason |", "| --- | --- | --- | --- | --- | --- |"]
        lines.extend(f"| {escape(a)} | {escape(b)} | {escape(c)} | {escape(d)} | {escape(e)} | {escape(f)} |" for a, b, c, d, e, f in rows)
        lines.extend(["", "## Interpretation", "", "This report is a regenerated projection of append-only history. `stale` and `not_evaluated` are computed here and are never recorded verdicts.", "", f"Rows: {len(rows)}. " + ", ".join(f"{state}={counts[state]}" for state in sorted(counts)) + ".", "", f"History records read: {len(records)}; observations retained: {len(observations)}; invalidation events retained: {len(invalidations)}."])
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(f"RENDERED: {output} rows={len(rows)}")
        return 0
    except (EvalError, OSError, KeyError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
