#!/usr/bin/env python3
"""Validate an eval suite and optional append-only JSONL history without executing checks."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from eval_common import (
    EXECUTOR_TYPES,
    FALSIFIABILITY_METHODS,
    RECORDED_VERDICTS,
    EvalError,
    eval_index,
    layer_index,
    load_document,
    load_jsonl,
    parse_duration,
    parse_iso,
    slice_ids,
)


def nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def validate_schema_files(root: Path, errors: list[str]) -> None:
    for name in ("eval-definition.schema.json", "observation.schema.json", "falsifiability.schema.json"):
        path = root / "schemas" / name
        try:
            parsed = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(parsed, dict) or "$schema" not in parsed or "title" not in parsed:
                errors.append(f"schema {name}: missing $schema or title")
        except (OSError, json.JSONDecodeError) as error:
            errors.append(f"schema {name}: invalid JSON: {error}")
    try:
        observation = json.loads((root / "schemas" / "observation.schema.json").read_text(encoding="utf-8"))
        allowed = observation["properties"]["verdict"]["enum"]
        if set(allowed) != RECORDED_VERDICTS:
            errors.append("observation schema: verdict enum must be exactly the five recorded verdicts")
    except (KeyError, TypeError, json.JSONDecodeError, OSError) as error:
        errors.append(f"observation schema: cannot inspect verdict enum: {error}")


def validate_layer(reference: Any, layers: dict[str, dict[str, Any]], context: str, errors: list[str]) -> dict[str, Any] | None:
    if not isinstance(reference, dict):
        errors.append(f"{context}: layer object is required")
        return None
    layer_id, rank = reference.get("id"), reference.get("rank")
    if not nonempty(layer_id) or not isinstance(rank, int) or rank < 0:
        errors.append(f"{context}: layer needs a non-empty id and non-negative integer rank")
        return None
    declared = layers.get(layer_id)
    if declared is None:
        errors.append(f"{context}: layer {layer_id!r} is not declared by suite.layers")
        return None
    if declared.get("rank") != rank:
        errors.append(f"{context}: layer {layer_id!r} has rank {rank}, declared rank is {declared.get('rank')}")
        return None
    return declared


def validate_suite(suite: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(suite, dict):
        return ["suite: top level must be an object"]
    if suite.get("schema_version") != "0.1":
        errors.append("suite.schema_version must be '0.1'")
    metadata = suite.get("suite")
    if not isinstance(metadata, dict) or not nonempty(metadata.get("id")) or not nonempty(metadata.get("title")):
        errors.append("suite: suite.id and suite.title are required")
    layers_raw = suite.get("layers")
    if not isinstance(layers_raw, list) or not layers_raw:
        errors.append("suite.layers must be a non-empty list")
        layers: dict[str, dict[str, Any]] = {}
    else:
        layers = layer_index(suite)
        ids = [item.get("id") for item in layers_raw if isinstance(item, dict)]
        ranks = [item.get("rank") for item in layers_raw if isinstance(item, dict)]
        if len(ids) != len(layers_raw) or any(not nonempty(item) for item in ids):
            errors.append("suite.layers: every layer needs a non-empty id")
        if len(set(ids)) != len(ids):
            errors.append("suite.layers: layer ids must be unique")
        if any(not isinstance(rank, int) or rank < 0 for rank in ranks) or len(set(ranks)) != len(ranks):
            errors.append("suite.layers: ranks must be unique non-negative integers")
    evals = suite.get("evals")
    if not isinstance(evals, list) or not evals:
        return errors + ["suite.evals must be a non-empty list"]
    eval_ids: set[str] = set()
    for position, definition in enumerate(evals, start=1):
        context = f"eval[{position}]"
        if not isinstance(definition, dict):
            errors.append(f"{context}: must be an object")
            continue
        eval_id = definition.get("id")
        if not nonempty(eval_id):
            errors.append(f"{context}: id is required")
        elif eval_id in eval_ids:
            errors.append(f"{context}: duplicate id {eval_id!r}")
        else:
            eval_ids.add(eval_id)
        if not nonempty(definition.get("claim")):
            errors.append(f"{context}: claim is required")
        population = definition.get("population")
        if not isinstance(population, dict) or not nonempty(population.get("definition")) or not nonempty(population.get("denominator_source")):
            errors.append(f"{context}: population needs definition and denominator_source")
        else:
            slices = population.get("slices")
            if not isinstance(slices, list) or not slices:
                errors.append(f"{context}: population.slices must be non-empty")
            else:
                identifiers = []
                for slice_item in slices:
                    if not isinstance(slice_item, dict) or not nonempty(slice_item.get("id")) or not isinstance(slice_item.get("denominator"), int) or slice_item["denominator"] < 1:
                        errors.append(f"{context}: every population slice needs id and positive denominator")
                    else:
                        identifiers.append(slice_item["id"])
                if len(identifiers) != len(set(identifiers)):
                    errors.append(f"{context}: population slice ids must be unique")
        oracle = definition.get("oracle")
        if not isinstance(oracle, dict) or not nonempty(oracle.get("description")) or not nonempty(oracle.get("path")):
            errors.append(f"{context}: oracle needs description and path")
        elif oracle.get("independent") is not True or oracle.get("routes_through_evaluated_path") is not False:
            errors.append(f"{context}: oracle must be independent and must not route through the evaluated path")
        claim_layer = validate_layer(definition.get("observation_layer"), layers, f"{context}.observation_layer", errors)
        evidence = definition.get("evidence")
        evidence_layer = None
        if not isinstance(evidence, dict) or not nonempty(evidence.get("ref")):
            errors.append(f"{context}: evidence.ref is required")
        else:
            evidence_layer = validate_layer(evidence.get("layer"), layers, f"{context}.evidence.layer", errors)
        if claim_layer and evidence_layer and evidence_layer["rank"] < claim_layer["rank"]:
            errors.append(f"{context}: evidence rank {evidence_layer['rank']} cannot prove claim rank {claim_layer['rank']}")
        executor = definition.get("executor")
        if not isinstance(executor, dict) or executor.get("type") not in EXECUTOR_TYPES or not nonempty(executor.get("ref")):
            errors.append(f"{context}: executor needs supported type and reference")
        tier = definition.get("tier")
        if not isinstance(tier, dict) or not nonempty(tier.get("id")) or not nonempty(tier.get("runner")):
            errors.append(f"{context}: tier needs id and runner")
        validity = definition.get("validity")
        if not isinstance(validity, dict):
            errors.append(f"{context}: validity is required")
        else:
            try:
                parse_duration(validity.get("max_age"), f"{context}.validity")
            except EvalError as error:
                errors.append(str(error))
            labels = validity.get("invalidate_on")
            if not isinstance(labels, list) or any(not nonempty(item) for item in labels) or len(labels) != len(set(labels)):
                errors.append(f"{context}: validity.invalidate_on must be a unique list of labels")
        falsifiability = definition.get("falsifiability")
        if not isinstance(falsifiability, dict) or falsifiability.get("method") not in FALSIFIABILITY_METHODS or not nonempty(falsifiability.get("ref")):
            errors.append(f"{context}: falsifiability needs a supported method and reference")
        else:
            try:
                parse_iso(f"{falsifiability.get('verified_at')}T00:00:00Z", f"{context}.falsifiability.verified_at")
            except EvalError:
                errors.append(f"{context}: falsifiability.verified_at must be an ISO date")
    return errors


def validate_history(records: list[dict[str, Any]], suite: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    definitions, layers = eval_index(suite), layer_index(suite)
    suite_id = suite.get("suite", {}).get("id")
    for record in records:
        location = f"history:{record.get('_line', '?')}"
        record_type = record.get("record_type")
        if record_type == "observation":
            if record.get("verdict") not in RECORDED_VERDICTS:
                errors.append(f"{location}: recorded verdict must be one of {', '.join(sorted(RECORDED_VERDICTS))}; derived states are forbidden")
            for key in ("observation_id", "recorded_at", "suite_id", "eval_id", "population_slice_id", "observed_at"):
                if not nonempty(record.get(key)):
                    errors.append(f"{location}: {key} is required")
            if record.get("suite_id") != suite_id:
                errors.append(f"{location}: suite_id does not match suite")
            definition = definitions.get(record.get("eval_id"))
            if definition is None:
                errors.append(f"{location}: unknown eval_id {record.get('eval_id')!r}")
                continue
            if record.get("population_slice_id") not in slice_ids(definition):
                errors.append(f"{location}: unknown population slice")
            for key in ("recorded_at", "observed_at"):
                try:
                    parse_iso(record.get(key), f"{location}.{key}")
                except EvalError as error:
                    errors.append(str(error))
            evidence = record.get("evidence")
            if not isinstance(evidence, dict) or not nonempty(evidence.get("ref")):
                errors.append(f"{location}: evidence.ref is required")
                continue
            evidence_layer = validate_layer(evidence.get("layer"), layers, f"{location}.evidence.layer", errors)
            claim_layer = definition.get("observation_layer")
            if evidence_layer and isinstance(claim_layer, dict) and evidence_layer["rank"] < claim_layer.get("rank", -1):
                errors.append(f"{location}: evidence rank cannot prove this claim layer")
        elif record_type == "invalidation":
            definition = definitions.get(record.get("eval_id"))
            if definition is None:
                errors.append(f"{location}: invalidation has unknown eval_id")
                continue
            if record.get("population_slice_id") not in slice_ids(definition):
                errors.append(f"{location}: invalidation has unknown population slice")
            valid_reasons = definition.get("validity", {}).get("invalidate_on", [])
            if record.get("reason") not in valid_reasons:
                errors.append(f"{location}: invalidation reason is not declared by eval validity policy")
            try:
                parse_iso(record.get("recorded_at"), f"{location}.recorded_at")
            except EvalError as error:
                errors.append(str(error))
        else:
            errors.append(f"{location}: record_type must be observation or invalidation")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--suite", required=True, help="YAML or JSON suite definition")
    parser.add_argument("--history", help="optional JSONL history to validate")
    args = parser.parse_args()
    errors: list[str] = []
    validate_schema_files(Path(__file__).resolve().parents[1], errors)
    try:
        suite = load_document(args.suite)
        errors.extend(validate_suite(suite))
        records: list[dict[str, Any]] = []
        if args.history:
            records = load_jsonl(args.history)
            if isinstance(suite, dict):
                errors.extend(validate_history(records, suite))
    except (EvalError, OSError) as error:
        errors.append(str(error))
        records = []
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print(f"INVALID: {len(errors)} error(s)", file=sys.stderr)
        return 1
    print(f"VALID: suite={suite['suite']['id']} evals={len(suite['evals'])} layers={len(suite['layers'])} history_records={len(records)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
