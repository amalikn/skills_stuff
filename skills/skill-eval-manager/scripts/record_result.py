#!/usr/bin/env python3
"""Append an externally obtained observation or declared invalidation; never execute an eval."""

from __future__ import annotations

import argparse
import json
import sys
import uuid
from typing import Any

from eval_common import RECORDED_VERDICTS, EvalError, append_jsonl, eval_index, iso_now, layer_index, load_document, parse_iso, slice_ids


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--suite", required=True)
    parser.add_argument("--history", required=True)
    parser.add_argument("--eval-id", required=True)
    parser.add_argument("--slice-id", required=True)
    parser.add_argument("--verdict", choices=sorted(RECORDED_VERDICTS))
    parser.add_argument("--measured-value", default="null", help="JSON value measured by the external executor")
    parser.add_argument("--evidence-ref")
    parser.add_argument("--observed-at", default=iso_now())
    parser.add_argument("--recorded-at", default=iso_now())
    parser.add_argument("--observation-id")
    parser.add_argument("--supersedes")
    parser.add_argument("--notes")
    parser.add_argument("--invalidate", action="store_true", help="record a declared invalidation instead of an observation")
    parser.add_argument("--reason", help="declared validity.invalidate_on label for --invalidate")
    parser.add_argument("--reference", help="evidence/reference for --invalidate")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    try:
        suite = load_document(args.suite)
        definitions = eval_index(suite)
        definition = definitions.get(args.eval_id)
        if definition is None:
            raise EvalError(f"unknown eval id {args.eval_id!r}")
        if args.slice_id not in slice_ids(definition):
            raise EvalError(f"unknown population slice {args.slice_id!r}")
        parse_iso(args.recorded_at, "recorded_at")
        if args.invalidate:
            if args.verdict or args.evidence_ref:
                raise EvalError("--invalidate cannot be combined with --verdict or --evidence-ref")
            if not args.reason or args.reason not in definition["validity"]["invalidate_on"]:
                raise EvalError("--reason must be a label declared in validity.invalidate_on")
            if not args.reference:
                raise EvalError("--reference is required for an invalidation")
            record: dict[str, Any] = {"record_type": "invalidation", "recorded_at": args.recorded_at, "suite_id": suite["suite"]["id"], "eval_id": args.eval_id, "population_slice_id": args.slice_id, "reason": args.reason, "reference": args.reference}
            append_jsonl(args.history, record, args.dry_run)
            print(f"{'WOULD_APPEND' if args.dry_run else 'APPENDED'}: invalidation eval={args.eval_id} slice={args.slice_id}")
            return 0
        if not args.verdict or not args.evidence_ref:
            raise EvalError("--verdict and --evidence-ref are required unless --invalidate is used")
        parse_iso(args.observed_at, "observed_at")
        try:
            measured_value = json.loads(args.measured_value)
        except json.JSONDecodeError as error:
            raise EvalError(f"--measured-value must be JSON: {error.msg}") from error
        evidence_layer = definition["evidence"]["layer"]
        declared_layer = layer_index(suite).get(evidence_layer["id"])
        if declared_layer is None or declared_layer["rank"] != evidence_layer["rank"]:
            raise EvalError("suite has invalid declared evidence layer; validate the suite first")
        record = {"record_type": "observation", "observation_id": args.observation_id or str(uuid.uuid4()), "recorded_at": args.recorded_at, "suite_id": suite["suite"]["id"], "eval_id": args.eval_id, "population_slice_id": args.slice_id, "observed_at": args.observed_at, "measured_value": measured_value, "verdict": args.verdict, "evidence": {"ref": args.evidence_ref, "layer": evidence_layer}}
        if args.supersedes:
            record["supersedes"] = args.supersedes
        if args.notes:
            record["notes"] = args.notes
        append_jsonl(args.history, record, args.dry_run)
        print(f"{'WOULD_APPEND' if args.dry_run else 'APPENDED'}: observation={record['observation_id']} verdict={args.verdict}")
        return 0
    except (EvalError, OSError, KeyError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
