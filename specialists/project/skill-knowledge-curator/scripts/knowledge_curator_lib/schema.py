"""jsonschema seam: validates agent input records against schemas/*.schema.json (Draft 2020-12).

Imported, not run. The only module that imports jsonschema. Upgrade test: tests/test_seams.py. Safety: reads the skill's own
schema files; no writes.
"""

import functools
import json

from jsonschema import Draft202012Validator

from .settings import SCHEMA_DIR

RECORD_SCHEMAS = {"claim": "claim-input", "section_status": "section-status-input", "relation": "relation-input"}


@functools.cache
def load(name: str) -> dict:
  """Load one schema document.

  Args:
    name: schema file stem, e.g. "claim-input".

  Returns:
    The parsed schema.
  """
  return json.loads((SCHEMA_DIR / f"{name}.schema.json").read_text(encoding="utf-8"))


@functools.cache
def _validator(name: str) -> Draft202012Validator:
  """Compiled validator for one schema.

  Args:
    name: schema file stem.

  Returns:
    The validator.
  """
  return Draft202012Validator(load(name))


def errors(name: str, instance) -> list[str]:
  """Validate an instance and list every violation.

  Args:
    name: schema file stem.
    instance: the record to check.

  Returns:
    Messages of the form "path: message", sorted; empty when valid.
  """
  found = []
  for err in _validator(name).iter_errors(instance):
    where = "/".join(str(p) for p in err.absolute_path) or "(root)"
    found.append(f"{where}: {err.message}")
  return sorted(found)


def record_errors(record: dict) -> list[str]:
  """Validate an agent input record by its "record" field.

  Args:
    record: one input record.

  Returns:
    Violations; an unknown record type is itself a violation.
  """
  kind = record.get("record") if isinstance(record, dict) else None
  if kind not in RECORD_SCHEMAS:
    return [f"record: unknown record type {kind!r} (expected one of {', '.join(sorted(RECORD_SCHEMAS))})"]
  return errors(RECORD_SCHEMAS[kind], record)
