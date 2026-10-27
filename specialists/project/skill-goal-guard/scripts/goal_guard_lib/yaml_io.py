"""The PyYAML seam: the only module that imports yaml (skill-coder dependencies.md). Upgrade test: tests/test_trace_excel_yaml.py (Seams).

Imported, not run. safe_load only (never yaml.load), so a record cannot construct Python objects. JSON files are YAML too, so
proposals and task files may be either.
"""

from pathlib import Path

import yaml

from .errors import RecordError


def load_file(path: Path) -> object:
  """Parse one YAML or JSON file.

  Args:
    path: the file to read.

  Returns:
    The parsed value (dict, list, scalar), or None for an empty file.

  Raises:
    RecordError: the file is missing, unreadable or not valid YAML; the message names the file.
  """
  try:
    text = path.read_text(encoding="utf-8")
  except OSError as err:
    raise RecordError(f"cannot read {path}: {err.strerror}") from err
  try:
    return yaml.safe_load(text)
  except yaml.YAMLError as err:
    raise RecordError(f"{path} is not valid YAML: {err}") from err


def dump_text(value: object) -> str:
  """Render a value as block-style YAML with keys in insertion order.

  Args:
    value: plain data (dict, list, str, int, float, bool, None).

  Returns:
    The YAML text, ending in a newline.
  """
  return yaml.safe_dump(value, sort_keys=False, allow_unicode=True, default_flow_style=False)
