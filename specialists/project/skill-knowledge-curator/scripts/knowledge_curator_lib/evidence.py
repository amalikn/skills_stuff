"""Evidence spans: verify a cited excerpt against the source bytes, and re-check stored evidence later.

Imported, not run. A span is valid only when the file still has the inventoried hash and the whitespace-normalised excerpt occurs
inside the cited lines; nothing is cited unchecked (design doc 5.2). When a source changed, recheck() looks for the excerpt
elsewhere and reports it relocated or broken. Safety: reads source files below the project root.
"""

from . import ids, ledger
from .state import State

MAX_WINDOW = 60


class Reader:
  """Cached reads of project files for one run.

  Args:
    st: current state.
  """

  def __init__(self, st: State):
    """Create the reader.

    Args:
      st: current state.
    """
    self.st = st
    self._cache: dict[str, tuple[str, str] | None] = {}

  def read(self, rel: str) -> tuple[str, str] | None:
    """Hash and text of one file.

    Args:
      rel: project-relative path.

    Returns:
      (sha256, text) or None when the file is missing or not UTF-8.
    """
    if rel not in self._cache:
      path = ledger.contained(self.st.root, rel)
      try:
        data = path.read_bytes()
        self._cache[rel] = (ids.sha256_bytes(data), data.decode("utf-8"))
      except OSError, UnicodeDecodeError:
        self._cache[rel] = None
    return self._cache[rel]


def _sections_overlapping(st: State, version_id: str, start: int, end: int) -> list[str]:
  """Sections of a source version whose lines overlap a span.

  Args:
    st: current state.
    version_id: source version.
    start: first line.
    end: last line.

  Returns:
    Sorted section IDs.
  """
  return sorted(s["section_id"] for s in st.sections.values() if s["source_version_id"] == version_id and s["line_start"] <= end and s["line_end"] >= start)


def verify_span(reader: Reader, span: dict) -> tuple[dict | None, str | None, bool]:
  """Check one agent-supplied span and build its evidence record.

  Args:
    reader: file reader.
    span: {source_path, line_start, line_end, excerpt}.

  Returns:
    (evidence record or None, error message or None, True when the failure is a changed source).
  """
  st, rel = reader.st, span["source_path"]
  src = st.source_by_path().get(rel)
  if src is None:
    return None, f"{rel}: not in the inventory (run kc inventory, or the path is excluded)", False
  got = reader.read(rel)
  if got is None:
    return None, f"{rel}: missing or unreadable", False
  sha, text = got
  if sha != src["sha256"]:
    return None, f"{rel}: changed since inventory (run kc inventory)", True
  lines = text.splitlines()
  start, end = span["line_start"], span["line_end"]
  if start > end or end > len(lines):
    return None, f"{rel}: lines {start}-{end} outside the file ({len(lines)} lines)", False
  if ids.norm_ws(span["excerpt"]) not in ids.norm_ws("\n".join(lines[start - 1 : end])):
    return None, f"{rel}:{start}-{end}: excerpt not found in the cited lines", False
  rec = {
    "source_id": src["source_id"],
    "source_version_id": src["source_version_id"],
    "source_sha256": sha,
    "path": rel,
    "line_start": start,
    "line_end": end,
    "excerpt": span["excerpt"],
    "excerpt_sha256": ids.sha256_text(ids.norm_ws(span["excerpt"])),
    "section_ids": _sections_overlapping(st, src["source_version_id"], start, end),
  }
  rec["evidence_id"] = ids.make_id("ev", rec["source_version_id"], start, end, rec["excerpt_sha256"])
  return rec, None, False


def _locate(lines: list[str], excerpt: str) -> tuple[int, int] | None:
  """Find the shortest line window containing an excerpt.

  Args:
    lines: file lines.
    excerpt: text to find (whitespace-normalised comparison).

  Returns:
    (first, last) 1-based lines, or None.
  """
  want = ids.norm_ws(excerpt)
  for i in range(len(lines)):
    for j in range(i, min(len(lines), i + MAX_WINDOW)):
      if want in ids.norm_ws("\n".join(lines[i : j + 1])):
        return i + 1, j + 1
  return None


def recheck(reader: Reader, ev: dict) -> dict:
  """Re-verify stored evidence against the live file.

  Args:
    reader: file reader.
    ev: stored evidence record.

  Returns:
    {"status": valid | relocated | broken | missing, "lines": [first, last] when found}.
  """
  got = reader.read(ev["path"])
  if got is None:
    return {"status": "missing"}
  sha, text = got
  lines = text.splitlines()
  span = "\n".join(lines[ev["line_start"] - 1 : ev["line_end"]])
  if sha == ev["source_sha256"] or ids.norm_ws(ev["excerpt"]) in ids.norm_ws(span):
    return {"status": "valid", "lines": [ev["line_start"], ev["line_end"]]}
  found = _locate(lines, ev["excerpt"])
  return {"status": "relocated", "lines": list(found)} if found else {"status": "broken"}
