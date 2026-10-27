"""PyYAML seam: the only module that imports yaml (safe_load / safe_dump only).

Imported, not run. Upgrade test: tests/test_seams.py. Safety: parses and formats text; no I/O.
"""

import yaml

from .errors import InputError


def load(text: str):
  """Parse YAML text safely.

  Args:
    text: YAML document.

  Returns:
    The parsed value (dict, list, scalar or None).

  Raises:
    InputError: the text is not valid YAML.
  """
  try:
    return yaml.safe_load(text)
  except yaml.YAMLError as err:
    raise InputError(f"invalid YAML: {err}") from err


def dump(value) -> str:
  """Format a value as block-style YAML with keys in insertion order.

  Args:
    value: plain data (dict, list, scalars).

  Returns:
    The YAML text.
  """
  return yaml.safe_dump(value, sort_keys=False, allow_unicode=True, default_flow_style=False)
