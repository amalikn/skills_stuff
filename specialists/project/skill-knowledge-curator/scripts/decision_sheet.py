#!/usr/bin/env python3
"""Turn the `kc review` queue into a tick-box decision sheet the operator fills in, one question per open conflict.

Each question shows the curator's question, every position with its claim id, source file and lines, and the curator's assessment, then one
checkbox per `kc decide` action (USE_OTHER per position, BOTH_APPLY_SCOPED, CORRECTED, DEFER) plus Other, and a Notes line. Optional
recommendations mark one option "(Recommended)" with a reason; they are advice, never a decision, and nothing is recorded until the operator
ticks a box and the agent runs `kc decide`. Operator preference (Continuum, 2026-11-05): questions in one Markdown file with checkboxes and an
Other option on each, so 40 conflicts are answered in one sitting instead of rounds of four.

Positions are matched to claim ids by exact claim text, limited to the conflict's own claims, so a tick maps to one `--current` id; the script
exits 1 if any position cannot be matched.

Run: kc review --project <p> > review.md; python scripts/decision_sheet.py --project <p> --review review.md --out sheet.md
[--severity P2] [--exclude cf-...] [--recs recs.json] [--title "..."] (or `just decision-sheet ...`). Read-only on the project; writes --out.
recs.json: {"cf-...": {"kind": "A" | "B" | "BOTH" | "CORRECTED" | "DEFER", "reason": "...", "why": "optional: why it is needed now"}}.
Conflicts with a "why" are listed first. Standard library only.
"""

import argparse
import json
import re
import sys
from pathlib import Path

REC = " **(Recommended)**"
HEADER = re.compile(r"### (cf-[0-9a-f]+) · (P\d) · (\S+)")
ROW = re.compile(r"^\| ([A-Z]) \| (.*?) \| [^|]* \| [^|]* \| `([^`]*)` (L[\d-]+)", re.M)


def read_jsonl(path: Path) -> list[dict]:
  """Read one ledger file.

  Args:
    path: a JSONL file.

  Returns:
    Its records, in file order.
  """
  with path.open(encoding="utf-8") as handle:
    return [json.loads(line) for line in handle if line.strip()]


def parse_review(text: str, conflicts: dict, by_text: dict) -> tuple[list[dict], list[tuple[str, str]]]:
  """Parse the `kc review` Markdown into question items and match each position to its claim id.

  Args:
    text: review queue Markdown.
    conflicts: conflict records by id.
    by_text: claim text to the set of claim ids carrying it.

  Returns:
    (items, unmatched): items in queue order, and (conflict id, position letter) pairs with no unique claim id.
  """
  items, unmatched = [], []
  for block in re.split(r"\n(?=### cf-)", text):
    m = HEADER.match(block)
    if not m:
      continue
    cid, sev, kind = m.groups()
    question = re.search(r"\*\*Question:\*\* (.*)", block)
    assess = re.search(r"\*\*Assessment:\*\* (.*)", block)
    own = set(conflicts.get(cid, {}).get("claims", []))
    positions = []
    for letter, ptext, src, lines in ROW.findall(block):
      ptext = ptext.replace("\\|", "|").strip()
      ids = by_text.get(ptext, set()) & own or by_text.get(ptext, set())
      claim = next(iter(ids)) if len(ids) == 1 else None
      if not claim:
        unmatched.append((cid, letter))
      positions.append({"letter": letter, "text": ptext, "src": src.removeprefix("docs/research/"), "lines": lines, "claim": claim})
    items.append(
      {
        "cid": cid,
        "sev": sev,
        "kind": kind,
        "topic": conflicts.get(cid, {}).get("topic_key", ""),
        "question": question[1] if question else "",
        "assess": assess[1] if assess else "",
        "positions": positions,
      }
    )
  return items, unmatched


def render_item(n: int, item: dict, rec: dict | None) -> list[str]:
  """Render one question.

  Args:
    n: question number.
    item: parsed review item.
    rec: optional recommendation {kind, reason, why}.

  Returns:
    Markdown lines.
  """
  kind = (rec or {}).get("kind")
  out = [f"### {n}. {item['cid']} ({item['sev']}, {item['topic']}, {item['kind']})", "", f"**Question:** {item['question']}", ""]
  if rec and rec.get("why"):
    out += [f"**Why now:** {rec['why']}", ""]
  for p in item["positions"]:
    out.append(f"- **{p['letter']}** `{p['claim']}`, {p['src']} {p['lines']}: {p['text']}")
  out += ["", f"**Curator assessment:** {item['assess']}", ""]
  if rec:
    out += [f"**Agent recommendation:** {rec['reason']}", ""]
  out += ["Choose one:", ""]
  for p in item["positions"]:
    out.append(f"- [ ] {p['letter']} is current [USE_OTHER --current {p['claim']}]" + (REC if kind == p["letter"] else ""))
  out += [
    "- [ ] Both apply, in different scopes [BOTH_APPLY_SCOPED]" + (REC if kind == "BOTH" else "") + ". Scope: ",
    "- [ ] Neither; the correct statement is [CORRECTED]" + (REC if kind == "CORRECTED" else "") + ": ",
    "- [ ] Defer; keep it open, publish neither as settled [DEFER]" + (REC if kind == "DEFER" else "") + ". Reason: ",
    "- [ ] Other: ",
    "",
    "**Notes:**",
    "",
  ]
  return out


def render_sheet(items: list[dict], recs: dict, title: str, stamp: str) -> str:
  """Render the whole sheet: front matter, instructions, then questions needed now first.

  Args:
    items: parsed items to include.
    recs: recommendations by conflict id.
    title: sheet title.
    stamp: YYYYMMDD_hhmm for Last reviewed.

  Returns:
    The Markdown document.
  """
  now = [i for i in items if recs.get(i["cid"], {}).get("why")]
  later = [i for i in items if i not in now]
  lines = [
    "---",
    f"Title: {title}",
    "Category: decision-sheet",
    "Status: current",
    "Authority: working-state",
    f"Scope: {len(items)} open conflicts from the kc review queue, one tick-box question each, for the operator",
    f"Last reviewed: {stamp}",
    "Summary: Tick one box per question or write in Other. (Recommended) marks agent advice only; nothing is decided until the agent runs kc decide.",
    "---",
    "",
    f"# {title}",
    "",
    "How to answer: change `[ ]` to `[x]` on one option per question. Write any detail after the colon on that line, or under **Notes**. Leave a "
    "question untouched to keep it open. Each option names its `kc decide` action and claim id, so the answer is recorded exactly.",
    "",
  ]
  if any(i["cid"] in recs for i in items):
    lines += ["**(Recommended)** marks the agent's suggestion, with the reason under **Agent recommendation**. Only the operator resolves a conflict.", ""]
  n = 0
  groups = (("Part 1: needed now", now), ("Part 2: other open conflicts", later)) if now else (("Open conflicts", later),)
  for heading, group in groups:
    if not group:
      continue
    lines += [f"## {heading}", ""]
    for item in group:
      n += 1
      lines += render_item(n, item, recs.get(item["cid"]))
  return "\n".join(lines).rstrip() + "\n"


def main(argv: list[str] | None = None) -> int:
  """Build the sheet.

  Args:
    argv: arguments, default sys.argv[1:].

  Returns:
    0 on success, 1 when a position has no unique claim id or a recommendation names an unknown option, 2 on a missing ledger.
  """
  ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
  ap.add_argument("--project", required=True, type=Path)
  ap.add_argument("--review", required=True, type=Path, help="saved `kc review` output")
  ap.add_argument("--out", required=True, type=Path)
  ap.add_argument("--severity", action="append", help="keep only these severities (repeatable)")
  ap.add_argument("--exclude", action="append", default=[], help="conflict ids to leave out (repeatable)")
  ap.add_argument("--recs", type=Path, help="recommendations JSON")
  ap.add_argument("--title", default="Operator decision sheet")
  ap.add_argument("--stamp", default="00000000_0000", help="YYYYMMDD_hhmm from `date`")
  a = ap.parse_args(argv)
  kc = a.project / ".kc"
  if not (kc / "claims.jsonl").is_file() or not (kc / "conflicts.jsonl").is_file():
    print(f"no ledger under {kc}", file=sys.stderr)
    return 2
  by_text: dict[str, set[str]] = {}
  for rec in read_jsonl(kc / "claims.jsonl"):
    if rec.get("claim_text"):
      by_text.setdefault(rec["claim_text"].strip(), set()).add(rec["claim_id"])
  conflicts = {r["conflict_id"]: r for r in read_jsonl(kc / "conflicts.jsonl")}
  items, unmatched = parse_review(a.review.read_text(encoding="utf-8"), conflicts, by_text)
  items = [i for i in items if (not a.severity or i["sev"] in a.severity) and i["cid"] not in a.exclude]
  unmatched = [u for u in unmatched if u[0] in {i["cid"] for i in items}]
  recs = json.loads(a.recs.read_text(encoding="utf-8")) if a.recs else {}
  bad = [cid for cid, r in recs.items() if r.get("kind") not in {"BOTH", "CORRECTED", "DEFER", *"ABCDEF"}]
  if unmatched or bad:
    for cid, letter in unmatched:
      print(f"unmatched position: {cid} {letter}", file=sys.stderr)
    for cid in bad:
      print(f"unknown recommendation kind: {cid}", file=sys.stderr)
    return 1
  a.out.write_text(render_sheet(items, recs, a.title, a.stamp), encoding="utf-8")
  print(f"{a.out}: {len(items)} questions, {sum(1 for i in items if i['cid'] in recs)} with a recommendation")
  return 0


if __name__ == "__main__":
  sys.exit(main())
