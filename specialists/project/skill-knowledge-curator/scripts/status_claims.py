#!/usr/bin/env python3
"""Claims for what each document says about itself, and relations where its Status line and its own banner disagree.

Extractors leave front matter as context, so a file whose `Status:` says current while its banner says superseded has no claim for kc to
pair: three relate agents on the UNC pilot hit this (2026-11-05). This makes one claim per declared Status line and per superseded or
historical banner near the top, deterministically; with `--relations` it pairs them as a P2 true-conflict when the Status line reads
current-like (current, adopted, adoption-ready, approved, authoritative, working direction) and the banner says otherwise.

Run: python scripts/status_claims.py <project> > status.json, then `kc claims --project <project> --file status.json --apply`;
     then python scripts/status_claims.py <project> --relations > rel.json, then `kc relate --project <project> --file rel.json --apply`
     (or `just status-claims <project> [--relations]`). Read-only: prints JSON, writes nothing.
"""

import argparse
import json
import re
import sys
from pathlib import Path

from knowledge_curator_lib import mdparse, state
from knowledge_curator_lib.evidence import Reader

BANNER_LINES = 40
# A banner opens its line (after quote and emphasis marks) or says so within its first words; a list item, a line about other files, or a
# partial supersession ("superseded in part") is not one: on the UNC pilot those were 14 of 23 raw hits.
_BANNER = re.compile(r"^[\s>*_]*(?:reviewed [^:]{0,30}:\s*)?(superseded|historical|archived)\b(?!\s+in\s+part)", re.IGNORECASE)
_CURRENT_LIKE = re.compile(r"\b(current|adopted|adoption-ready|approved|authoritative|working direction)\b", re.IGNORECASE)
_TOPIC_KEY = "doc-status"


def _excerpt(line: str) -> str:
  """The line as an excerpt: blockquote marks and edge spaces dropped (kc compares whitespace-normalised).

  Args:
    line: source line.

  Returns:
    Excerpt text.
  """
  return re.sub(r"^\s*>\s?", "", line).strip()


def _claim(path: str, line_no: int, line: str, predicate: str, obj: str) -> dict:
  """One self-description claim.

  Args:
    path: project path.
    line_no: 1-based line.
    line: source line.
    predicate: "declares status" or "banner says".
    obj: the status value.

  Returns:
    Claim input record.
  """
  stem = Path(path).stem
  return {
    "record": "claim",
    "subject": f"{stem} document",
    "predicate": predicate,
    "object": obj[:160],
    "claim_text": f"{stem} {predicate}: {obj[:200]}",
    "kind": "observed",
    "epistemic_status": "OBSERVED",
    "primary_category": "governance",
    "subcategories": ["policy"],
    "topic_key": f"{_TOPIC_KEY}.{stem}",
    "disposition": "CURRENT",
    "labels": ["document-status"],
    "evidence": [{"source_path": path, "line_start": line_no, "line_end": line_no, "excerpt": _excerpt(line)}],
  }


def _banner(lines: list[str], skip: int | None) -> tuple[int, str] | None:
  """First superseded or historical banner in a file's top lines, other than its Status line.

  Args:
    lines: file lines.
    skip: the Status line number, or None.

  Returns:
    (1-based line, banner word), or None.
  """
  for n, line in enumerate(lines[:BANNER_LINES], 1):
    if n == skip or line.lstrip().startswith("|"):
      continue
    found = _BANNER.match(line)
    if found:
      return n, found.group(1).lower()
  return None


def scan(st: state.State) -> list[dict]:
  """Self-description findings per live file.

  Args:
    st: current state.

  Returns:
    [{path, status: (line, value) or None, banner: (line, word) or None, lines}].
  """
  reader, out = Reader(st), []
  for path in sorted(st.source_by_path()):
    got = reader.read(path)
    if not got:
      continue
    text = got[1]
    status = mdparse.status_line(text)
    lines = text.splitlines()
    out.append({"path": path, "status": status, "banner": _banner(lines, status[0] if status else None), "lines": lines})
  return out


def claims(found: list[dict]) -> list[dict]:
  """Claim records for every Status line and banner.

  Args:
    found: from scan.

  Returns:
    Claim inputs.
  """
  recs = []
  for f in found:
    if f["status"]:
      n, value = f["status"]
      recs.append(_claim(f["path"], n, f["lines"][n - 1], "declares status", value))
    if f["banner"]:
      n, word = f["banner"]
      recs.append(_claim(f["path"], n, f["lines"][n - 1], "banner says", word))
  return recs


def relations(st: state.State, found: list[dict]) -> list[dict]:
  """P2 true-conflicts where a current-like Status line sits under a superseded or historical banner; needs the claims ingested.

  Args:
    st: current state.
    found: from scan.

  Returns:
    Relation inputs (only pairs whose two claims are in the ledger).
  """
  by_key = {}
  for cid, c in st.claims.items():
    ev = c["evidence"][0] if c["evidence"] else None
    if ev and "document-status" in (c.get("labels") or []):
      by_key[(ev["path"], ev["line_start"])] = cid
  recs = []
  for f in found:
    if not (f["status"] and f["banner"] and _CURRENT_LIKE.search(f["status"][1])):
      continue
    a, b = by_key.get((f["path"], f["status"][0])), by_key.get((f["path"], f["banner"][0]))
    if not (a and b):
      continue
    recs.append(
      {
        "record": "relation",
        "claims": sorted([a, b]),
        "relation": "true-conflict",
        "severity": "P2",
        "conflict_type": "status-line-vs-banner",
        "recommended_current": b,
        "question": f"{f['path']} says Status '{f['status'][1][:80]}' but its banner says {f['banner'][1]}: correct the Status line?",
        "reason": f"Line {f['status'][0]} declares '{f['status'][1][:80]}'; line {f['banner'][0]} marks the file {f['banner'][1]}.",
      }
    )
  return recs


def main(argv: list[str] | None = None) -> int:
  """Print claims or relations as JSON.

  Args:
    argv: arguments (sys.argv when None).

  Returns:
    Exit code (0; 1 when the project folder is missing).
  """
  p = argparse.ArgumentParser(description="Status-line and banner claims, and their conflicts (read-only).")
  p.add_argument("project")
  p.add_argument("--relations", action="store_true", help="print relations for claims already ingested")
  args = p.parse_args(argv)
  root = Path(args.project)
  if not root.is_dir():
    print(f"status_claims: project folder not found: {root}", file=sys.stderr)
    return 1
  st = state.load(root)
  found = scan(st)
  out = relations(st, found) if args.relations else claims(found)
  print(json.dumps(out, indent=1, ensure_ascii=False))
  print(f"status_claims: {len(out)} record(s) from {len(found)} file(s)", file=sys.stderr)
  return 0


if __name__ == "__main__":
  sys.exit(main())
