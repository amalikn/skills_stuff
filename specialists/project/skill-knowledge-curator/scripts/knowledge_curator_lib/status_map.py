"""Status map: what each document says about itself, with the line that proves it (research B1).

Imported, not run. Reads each live file's opening lines for a status line or banner and takes its place in a numbered series from the file
name. Absence means unknown, never current. Safety: reads sources only.
"""

import re
from pathlib import Path

from .evidence import Reader
from .state import State

TOP_LINES = 12
_OVER = re.compile(r"\b(superseded|replaced by)\b", re.IGNORECASE)
_PAST = re.compile(r"\b(historical|retired)\b", re.IGNORECASE)
_NOW = re.compile(r"^\W*status\W+current\b", re.IGNORECASE)
_NUMBER = re.compile(r"\d+")


def _order(path: str) -> int | None:
  """Place in a numbered series, from the first number in the file name.

  Args:
    path: project path.

  Returns:
    The number, or None.
  """
  found = _NUMBER.search(Path(path).stem)
  return int(found.group()) if found else None


def _named(line: str, paths: list[str], own: str) -> list[str]:
  """Other files a banner names, by their stem's first word.

  Args:
    line: the banner.
    paths: live paths.
    own: this file.

  Returns:
    Named paths.
  """
  low = line.lower()
  stems = {p: re.split(r"[-_]", Path(p).stem.lower())[0] for p in paths if p != own}
  return sorted(p for p, stem in stems.items() if re.search(rf"\b{re.escape(stem)}\b", low))


def _classify(lines: list[str]) -> tuple[str, int | None, str]:
  """Status from a file's opening lines; a superseded or historical mark wins over a current one.

  Args:
    lines: file lines.

  Returns:
    (status, 1-based line or None, quote).
  """
  found = ("unknown", None, "")
  for n, line in enumerate(lines[:TOP_LINES], 1):
    if line.lstrip().startswith("|"):
      continue
    if _OVER.search(line):
      return "superseded", n, line.strip()
    if _PAST.search(line):
      return "historical", n, line.strip()
    if _NOW.search(line) and found[0] == "unknown":
      found = ("current", n, line.strip())
  return found


def files(st: State) -> dict:
  """Status signals for every live file.

  Args:
    st: current state.

  Returns:
    {path: {status, line, quote, replaced_by, order}}.
  """
  reader, paths, out = Reader(st), sorted(st.source_by_path()), {}
  for path in paths:
    got = reader.read(path)
    status, line, quote = _classify(got[1].splitlines() if got else [])
    out[path] = {"status": status, "line": line, "quote": quote, "replaced_by": _named(quote, paths, path), "order": _order(path)}
  return out
