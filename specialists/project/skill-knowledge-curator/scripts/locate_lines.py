#!/usr/bin/env python3
"""Fill in or correct the line numbers of claim evidence from the excerpt text, before `kc claims` checks it.

Extractors quote the words and get the lines wrong: four of six agents on the UNC pilot (2026-11-05) each wrote their own finder for this.
Evidence whose cited lines already hold the excerpt is left alone. For the rest, the excerpt is searched in its source file
whitespace-normalised; a single match sets line_start/line_end, a hint (the given line_start) picks the nearest of several matches, and none
or an ambiguous match is reported and left as written.

Run: python scripts/locate_lines.py --project <dir> <claims.json> > fixed.json   (or `just locate-lines <dir> <claims.json>`).
Output: the records with corrected lines on stdout; a summary and every unresolved excerpt on stderr. Exit 0 when all resolve, 3 when any
does not. Safety: read-only; reads the project's sources, writes nothing.
"""

import argparse
import json
import re
import sys
from pathlib import Path

_SPACE = re.compile(r"\s+")
_QUOTE = re.compile(r"^\s*>\s?")


def _norm(text: str) -> str:
  """Whitespace-folded text with blockquote marks dropped, as kc compares excerpts.

  Args:
    text: any text.

  Returns:
    Folded text.
  """
  return _SPACE.sub(" ", " ".join(_QUOTE.sub("", line) for line in text.splitlines())).strip()


def find(lines: list[str], excerpt: str, max_span: int = 40) -> list[tuple[int, int]]:
  """Every line span whose folded text contains the excerpt, shortest first per start line.

  Args:
    lines: file lines.
    excerpt: quoted words.
    max_span: longest span tried, in lines.

  Returns:
    1-based (start, end) spans.
  """
  want, hits = _norm(excerpt), []
  if not want:
    return hits
  for start in range(len(lines)):
    if want.split(" ")[0] not in lines[start] and want[:20] not in _norm(lines[start]):
      continue
    for end in range(start, min(start + max_span, len(lines))):
      if want in _norm("\n".join(lines[start : end + 1])):
        hits.append((start + 1, end + 1))
        break
  return hits


def fix(records: list[dict], root: Path) -> tuple[list[dict], list[str], int]:
  """Correct evidence lines in place.

  Args:
    records: claim inputs (others pass through).
    root: project root.

  Returns:
    (records, unresolved messages, number of evidence items changed).
  """
  cache: dict[str, list[str]] = {}
  unresolved, changed = [], 0
  for n, rec in enumerate(records):
    for ev in rec.get("evidence") or []:
      path = ev.get("source_path", "")
      if path not in cache:
        file = root / path
        cache[path] = file.read_text(encoding="utf-8").splitlines() if file.is_file() else []
      given = (ev.get("line_start"), ev.get("line_end"))
      if all(isinstance(x, int) and x >= 1 for x in given) and _norm(ev.get("excerpt", "")) in _norm("\n".join(cache[path][given[0] - 1 : given[1]])):
        continue
      hits = find(cache[path], ev.get("excerpt", ""))
      if not hits:
        unresolved.append(f"[{n}] {path}: excerpt not found: {ev.get('excerpt', '')[:80]!r}")
        continue
      hint = ev.get("line_start") or 0
      start, end = min(hits, key=lambda h: (abs(h[0] - hint), h[1] - h[0]))
      if len(hits) > 1 and not hint:
        unresolved.append(f"[{n}] {path}: {len(hits)} matches and no line hint: {ev.get('excerpt', '')[:60]!r}")
        continue
      if (ev.get("line_start"), ev.get("line_end")) != (start, end):
        ev["line_start"], ev["line_end"] = start, end
        changed += 1
  return records, unresolved, changed


def main(argv: list[str] | None = None) -> int:
  """Print corrected records.

  Args:
    argv: arguments (sys.argv when None).

  Returns:
    Exit code: 0 all resolved, 1 bad input, 3 some unresolved.
  """
  p = argparse.ArgumentParser(description="Correct claim evidence lines from excerpts (read-only).")
  p.add_argument("--project", required=True)
  p.add_argument("file")
  args = p.parse_args(argv)
  root = Path(args.project)
  records = json.loads(Path(args.file).read_text(encoding="utf-8"))
  if not root.is_dir() or not isinstance(records, list):
    print("locate_lines: need a project folder and a JSON array of records", file=sys.stderr)
    return 1
  records, unresolved, changed = fix(records, root)
  print(json.dumps(records, indent=1, ensure_ascii=False))
  print(f"locate_lines: {changed} evidence item(s) corrected, {len(unresolved)} unresolved", file=sys.stderr)
  for msg in unresolved:
    print(f"  {msg}", file=sys.stderr)
  return 3 if unresolved else 0


if __name__ == "__main__":
  sys.exit(main())
