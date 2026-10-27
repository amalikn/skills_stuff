"""Stable identifiers, hashing and text normalisation shared by every curator module.

Imported, not run. IDs are content-derived so reruns on unchanged input produce the same IDs (INV-011). Safety: pure functions.
"""

import hashlib
import json
import re

_WS = re.compile(r"\s+")


def sha256_bytes(data: bytes) -> str:
  """SHA-256 of bytes.

  Args:
    data: the bytes.

  Returns:
    64 lowercase hex digits.
  """
  return hashlib.sha256(data).hexdigest()


def sha256_text(text: str) -> str:
  """SHA-256 of UTF-8 text.

  Args:
    text: the text.

  Returns:
    64 lowercase hex digits.
  """
  return sha256_bytes(text.encode("utf-8"))


def canonical(value) -> str:
  """Canonical JSON: sorted keys, no spaces, UTF-8 kept.

  Args:
    value: JSON-compatible data.

  Returns:
    The canonical string.
  """
  return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def make_id(prefix: str, *parts, length: int = 12) -> str:
  """Content-derived ID.

  Args:
    prefix: e.g. "cl" or "src".
    *parts: values hashed in order (canonical JSON).
    length: hex digits kept.

  Returns:
    "<prefix>-<hex>".
  """
  return f"{prefix}-{sha256_text(canonical(list(parts)))[:length]}"


def norm(text: str) -> str:
  """Whitespace-collapsed, lower-cased text for comparison keys.

  Args:
    text: any text.

  Returns:
    The normalised text.
  """
  return _WS.sub(" ", text or "").strip().lower()


def norm_ws(text: str) -> str:
  """Whitespace-collapsed text with case kept (excerpt matching).

  Args:
    text: any text.

  Returns:
    The normalised text.
  """
  return _WS.sub(" ", text or "").strip()
