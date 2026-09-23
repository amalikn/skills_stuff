#!/usr/bin/env python3
"""Shared, dependency-light helpers for skill-eval-manager scripts."""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

RECORDED_VERDICTS = {"pass", "fail", "inconclusive", "error", "blocked"}
FALSIFIABILITY_METHODS = {
    "injected_fault", "fixture", "mutation", "counterexample", "historical_failure", "analytical_proof"
}
EXECUTOR_TYPES = {"command", "manual", "query", "external"}


class EvalError(ValueError):
    """A user-correctable evaluation contract error."""


def load_document(path: str | Path) -> Any:
    """Load JSON or YAML. JSON is accepted as dependency-free YAML-compatible input."""
    source = Path(path)
    text = source.read_text(encoding="utf-8")
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        try:
            import yaml  # type: ignore[import-not-found]
        except ModuleNotFoundError as error:
            raise EvalError(
                f"{source}: ordinary YAML needs PyYAML; install an OSI-licensed PyYAML or use JSON-compatible YAML"
            ) from error
        try:
            return yaml.safe_load(text)
        except Exception as error:  # PyYAML has several parser exception classes.
            raise EvalError(f"{source}: cannot parse YAML: {error}") from error


def iso_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def parse_iso(value: str, context: str) -> datetime:
    if not isinstance(value, str) or not value:
        raise EvalError(f"{context}: timestamp is required")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as error:
        raise EvalError(f"{context}: invalid ISO-8601 timestamp {value!r}") from error
    if parsed.tzinfo is None:
        raise EvalError(f"{context}: timestamp must include a timezone")
    return parsed.astimezone(timezone.utc)


def parse_duration(value: str, context: str) -> timedelta:
    if not isinstance(value, str) or len(value) < 2 or value[-1] not in {"d", "h", "m"}:
        raise EvalError(f"{context}: max_age must be a positive duration such as 30d, 12h, or 15m")
    try:
        amount = int(value[:-1])
    except ValueError as error:
        raise EvalError(f"{context}: invalid max_age {value!r}") from error
    if amount < 1:
        raise EvalError(f"{context}: max_age must be positive")
    return {"d": timedelta(days=amount), "h": timedelta(hours=amount), "m": timedelta(minutes=amount)}[value[-1]]


def load_jsonl(path: str | Path) -> list[dict[str, Any]]:
    history = Path(path)
    if not history.exists():
        return []
    records: list[dict[str, Any]] = []
    for number, line in enumerate(history.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError as error:
            raise EvalError(f"{history}:{number}: invalid JSONL: {error.msg}") from error
        if not isinstance(record, dict):
            raise EvalError(f"{history}:{number}: each history line must be an object")
        record["_line"] = number
        records.append(record)
    return records


def append_jsonl(path: str | Path, record: dict[str, Any], dry_run: bool = False) -> None:
    payload = json.dumps(record, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    if dry_run:
        print(payload)
        return
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("a", encoding="utf-8") as handle:
        handle.write(payload + "\n")


def layer_index(suite: dict[str, Any]) -> dict[str, dict[str, Any]]:
    layers = suite.get("layers", [])
    return {layer["id"]: layer for layer in layers if isinstance(layer, dict) and "id" in layer}


def eval_index(suite: dict[str, Any]) -> dict[str, dict[str, Any]]:
    evals = suite.get("evals", [])
    return {item["id"]: item for item in evals if isinstance(item, dict) and "id" in item}


def slice_ids(eval_definition: dict[str, Any]) -> set[str]:
    population = eval_definition.get("population", {})
    slices = population.get("slices", []) if isinstance(population, dict) else []
    return {item["id"] for item in slices if isinstance(item, dict) and "id" in item}
