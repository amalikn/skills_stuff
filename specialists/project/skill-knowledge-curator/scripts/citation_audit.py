#!/usr/bin/env python3
"""Audit claim citations on rendered or authored pages against a curator ledger: every cited id, not a sample.

Three subcommands, run in order:
  audit     one row per (page, line, claim id): id exists, latest disposition and successor, keyword overlap between the citing line and the
            claim text plus excerpt, and a triage hint (SUPPORTED-BY-SCRIPT, REVIEW, WRONG-ID, SUPERSEDED-CANDIDATE). Writes rows JSON.
  excerpts  every evidence excerpt behind the cited claims is still at its source path and lines; then a seeded sample of SUPPORTED-BY-SCRIPT
            rows for a person to confirm against the source.
  review    print flagged rows compactly (the cell or clause around the id, and the claim) for hand reading.

Hints are triage only: a person reads every non-SUPPORTED row and the sample. The hint reads one line, so a superseded claim cited in a
side-by-side positions table, a conflict block, or prose whose "superseded" wrapped onto the line above is flagged too; those are
expected. Found in Continuum (2026-11-05): 884 citations on seven pages in 0.26 s; the SUPERSEDED-CANDIDATE hint caught every page that
still presented a superseded claim as current, which `arch-coverage`-style id checks cannot see.

Run: python scripts/citation_audit.py audit --root <project> --out rows.json <page.md> [...] (or `just citation-audit ...`). Read-only on the
project; writes only the --out file. Standard library only. Exit 0 always for audit and review; excerpts exits 1 when an excerpt is missing.
"""

import argparse
import json
import random
import re
import sys
from collections import Counter
from pathlib import Path

ID = re.compile(r"cl-[0-9a-f]{12}")
WORD = re.compile(r"[a-z][a-z0-9_.-]{2,}")
STOP = set(
  "the and for with that this from are not but its into than then when only each must may can has have was were "
  "will one two all any per via who which what does also stays stay source sources claim page".split()
)
HISTORY_WORDS = ("superseded", "historical", "history", "replaced", "earlier", "was ", "v0.1", "deprecated")
FLAGGED = ("REVIEW", "WRONG-ID", "SUPERSEDED-CANDIDATE")


def words(text: str) -> set[str]:
  """Lower-case content words of a text.

  Args:
    text: any string.

  Returns:
    Words of three or more characters, minus stop words.
  """
  return {w.strip(".-") for w in WORD.findall(text.lower())} - STOP


def load_ledger(root: Path) -> tuple[dict, dict]:
  """Load claims and their latest disposition from a project's `.kc/claims.jsonl`.

  Args:
    root: project root.

  Returns:
    (claims, dispositions): claim id to its latest claim record, and claim id to its latest disposition record.
  """
  claims, disp = {}, {}
  with (root / ".kc" / "claims.jsonl").open(encoding="utf-8") as handle:
    for line in handle:
      if not line.strip():
        continue
      rec = json.loads(line)
      if rec.get("record") == "claim":
        claims[rec["claim_id"]] = rec
      elif rec.get("record") == "disposition":
        disp[rec["claim_id"]] = rec
  return claims, disp


def verdict_for(line: str, claim: dict, disposition: str, overlap: float, hits: set[str]) -> str:
  """Pick the triage hint for one citation.

  Args:
    line: the citing line.
    claim: the claim record.
    disposition: the claim's latest disposition.
    overlap: share of claim words found on the line.
    hits: the shared words.

  Returns:
    SUPERSEDED-CANDIDATE, SUPPORTED-BY-SCRIPT or REVIEW.
  """
  low = line.lower()
  if disposition in ("SUPERSEDED", "HISTORICAL") and not any(h in low for h in HISTORY_WORDS):
    return "SUPERSEDED-CANDIDATE"
  if overlap >= 0.34 or len(hits) >= 4:
    return "SUPPORTED-BY-SCRIPT"
  return "REVIEW"


def audit_page(page: str, root: Path, claims: dict, disp: dict) -> list[dict]:
  """Produce one row per claim id cited on each line of a page.

  Args:
    page: page path relative to root.
    root: project root.
    claims: claim records by id.
    disp: latest disposition records by id.

  Returns:
    Row dicts in page order.
  """
  rows = []
  for n, line in enumerate((root / page).read_text(encoding="utf-8").splitlines(), 1):
    ids = ID.findall(line)
    if not ids:
      continue
    cite_words = words(ID.sub(" ", line))
    for cid in dict.fromkeys(ids):
      row = {"page": page, "line": n, "id": cid, "text": line.strip()[:600]}
      claim = claims.get(cid)
      if not claim:
        row.update(verdict="WRONG-ID", overlap=0.0)
        rows.append(row)
        continue
      ev = claim["evidence"][0]
      claim_words = words(claim["claim_text"] + " " + " ".join(e.get("excerpt", "") for e in claim["evidence"]))
      hits = cite_words & claim_words
      overlap = round(len(hits) / max(1, min(len(claim_words), 12)), 2)
      state = disp.get(cid, {}).get("disposition", "CURRENT")
      row.update(
        claim=claim["claim_text"],
        excerpt=ev.get("excerpt", ""),
        src=f"{ev['path']}:{ev['line_start']}",
        disposition=state,
        successor=disp.get(cid, {}).get("successor"),
        overlap=overlap,
        hits=sorted(hits)[:12],
        verdict=verdict_for(line, claim, state, overlap, hits),
      )
      rows.append(row)
  return rows


def norm(text: str) -> str:
  """Collapse whitespace and Markdown emphasis or backticks for comparison.

  Args:
    text: any string.

  Returns:
    Normalised lower-case string.
  """
  return re.sub(r"\s+", " ", re.sub(r"[`*_]", "", text)).strip().lower()


def missing_excerpts(root: Path, rows: list[dict], claims: dict) -> tuple[int, list[tuple[str, str, str]]]:
  """Check that each cited claim's evidence excerpts are still at their source lines (one line of slack each side).

  Args:
    root: project root.
    rows: audit rows.
    claims: claim records by id.

  Returns:
    (records checked, failures as (claim id, location, reason)).
  """
  cache, bad, checked = {}, [], 0
  for cid in sorted({r["id"] for r in rows if r["id"] in claims}):
    for ev in claims[cid]["evidence"]:
      path = root / ev["path"]
      if path not in cache:
        cache[path] = path.read_text(encoding="utf-8").splitlines() if path.exists() else None
      lines = cache[path]
      checked += 1
      if lines is None:
        bad.append((cid, ev["path"], "missing file"))
        continue
      start, end = int(ev["line_start"]), int(ev["line_end"])
      window = norm(" ".join(lines[max(0, start - 2) : end + 1]))
      if norm(ev.get("excerpt", ""))[:120] not in window:
        bad.append((cid, f"{ev['path']}:{start}-{end}", "excerpt not at lines"))
  return checked, bad


def segment(text: str, cid: str) -> str:
  """Return the table cell or the clause before a claim id.

  Args:
    text: the citing line.
    cid: claim id.

  Returns:
    The cell (tables) or up to 260 characters before the id (prose).
  """
  if text.startswith("|"):
    cell = next((c.strip() for c in text.split("|") if cid in c), text)
    return text[:260] if cell == cid or len(cell) < 30 else cell[:260]
  i = text.find(cid)
  return text[max(0, i - 260) : i]


def cmd_audit(args: argparse.Namespace) -> int:
  """Audit the pages and write rows; print per-page verdict counts.

  Args:
    args: parsed arguments (root, out, pages).

  Returns:
    Exit code 0.
  """
  claims, disp = load_ledger(args.root)
  rows = [r for p in args.pages for r in audit_page(p, args.root, claims, disp)]
  args.out.write_text(json.dumps(rows, indent=1), encoding="utf-8")
  for p in args.pages:
    c = Counter(r["verdict"] for r in rows if r["page"] == p)
    print(f"{p}: {sum(c.values())} {dict(sorted(c.items()))}")
  return 0


def cmd_excerpts(args: argparse.Namespace) -> int:
  """Check excerpts and print a seeded sample of script-supported rows.

  Args:
    args: parsed arguments (root, rows, fraction, seed).

  Returns:
    Exit code 1 when any excerpt is missing, else 0.
  """
  rows = json.loads(args.rows.read_text(encoding="utf-8"))
  claims, _ = load_ledger(args.root)
  checked, bad = missing_excerpts(args.root, rows, claims)
  print(f"evidence records checked: {checked}; failures: {len(bad)}")
  for b in bad:
    print("  BAD", *b)
  sup = [r for r in rows if r["verdict"] == "SUPPORTED-BY-SCRIPT"]
  random.Random(args.seed).shuffle(sup)
  for r in sup[: max(1, round(len(sup) * args.fraction))] if sup else []:
    print(f"## {r['page']}:{r['line']} {r['id']}")
    print("  PAGE:", segment(r["text"], r["id"]))
    print("  EXCERPT:", r["excerpt"][:200])
  return 1 if bad else 0


def cmd_review(args: argparse.Namespace) -> int:
  """Print flagged rows for hand reading.

  Args:
    args: parsed arguments (rows, verdict).

  Returns:
    Exit code 0.
  """
  rows = json.loads(args.rows.read_text(encoding="utf-8"))
  wanted = {args.verdict} if args.verdict else set(FLAGGED)
  for r in rows:
    if r["verdict"] in wanted:
      print(f"## {r['page']}:{r['line']} {r['id']} {r['verdict']} overlap={r.get('overlap')}")
      print("  PAGE:", segment(r["text"], r["id"]))
      if r.get("claim"):
        print("  CLAIM:", r["claim"][:300], f"[{r.get('disposition')}]")
  return 0


def build_parser() -> argparse.ArgumentParser:
  """Build the command-line parser.

  Args:
    None.

  Returns:
    The parser with audit, excerpts and review subcommands.
  """
  ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
  sub = ap.add_subparsers(dest="cmd", required=True)
  a = sub.add_parser("audit", help="one row per cited claim id")
  a.add_argument("--root", required=True, type=Path)
  a.add_argument("--out", required=True, type=Path)
  a.add_argument("pages", nargs="+")
  a.set_defaults(func=cmd_audit)
  e = sub.add_parser("excerpts", help="excerpts still at their lines, plus a sample")
  e.add_argument("--root", required=True, type=Path)
  e.add_argument("--rows", required=True, type=Path)
  e.add_argument("--fraction", type=float, default=0.10)
  e.add_argument("--seed", type=int, default=20261105)
  e.set_defaults(func=cmd_excerpts)
  r = sub.add_parser("review", help="print flagged rows")
  r.add_argument("--rows", required=True, type=Path)
  r.add_argument("--verdict", choices=[*FLAGGED, "SUPPORTED-BY-SCRIPT"])
  r.set_defaults(func=cmd_review)
  return ap


def main(argv: list[str] | None = None) -> int:
  """Run one subcommand.

  Args:
    argv: arguments, default sys.argv[1:].

  Returns:
    The subcommand's exit code.
  """
  args = build_parser().parse_args(argv)
  return args.func(args)


if __name__ == "__main__":
  sys.exit(main())
