#!/usr/bin/env python3
"""Write a pad_rewrite.py spec that brings item bodies to the writing standard's layout: bold section labels, each starting its own paragraph.

Why (operator, 2026-11-19: "Formatting of all the pad entries for this project are not correct"): Asks, feature requests and tech debt were written
with plain `Serves:` / `Question:` / `Why:` lines separated by single newlines, which Pad shows run together, and a body passed through a markdown
formatter came back hard-wrapped mid-sentence. The standard (docs/pad-usage-guidelines-20261110_1628.md 3.3) wants `**Label:**` at the start of its
own paragraph. This script changes layout only: a known label at the start of a line is bolded and begins a paragraph, a hard-wrapped line is
joined to the sentence it continues, and nothing else is touched (list items, tables, code fences, headings and words stay exactly as they are).
It writes nothing in Pad: review the printed plan, then apply the spec with `pad_rewrite.py <spec> --apply` (body writes guarded by seq).
Run from the project folder whose .pad.toml names the workspace.

Usage:
    python3 pad_format_spec.py --out spec.json                        # every item in the default collections
    python3 pad_format_spec.py --out spec.json --collections asks     # one collection
Options: --collections (default asks feature-requests tech-debt bugs ideas docs plans tasks; never decisions, a generated mirror, nor the
conventions and playbooks library), --pad PATH, --timeout SECONDS.
Exit: 0 spec written (possibly empty), 1 a pad call failed, 2 bad arguments. Budget: one list call per collection plus one show per item
(about 0.2 s each); prints its time.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time

DEFAULT_COLLECTIONS = ("asks", "feature-requests", "tech-debt", "bugs", "ideas", "docs", "plans", "tasks")
NEVER = {"decisions", "conventions", "playbooks"}
# Section labels of the standard (plans, tasks, bugs) and of Asks and feature requests as written in practice.
LABELS = (
  "Serves", "Goal", "Done when", "Out of scope", "Waits on", "Why", "Do", "Writes", "Refs", "Seen", "Evidence", "Cause", "Effect", "Options",
  "Not verified", "Closure", "Question", "Options to weigh", "Agent advice", "Repo", "Finding", "Proposal", "Why now", "Context", "Risk",
  "Impact", "Answer", "Decision", "Next", "Blocked by", "Source", "Sources",
)
LABEL = re.compile(r"^(?:\*\*)?(" + "|".join(re.escape(x) for x in sorted(LABELS, key=len, reverse=True)) + r"|Question \d+(?: \([^)]*\))?)(?::\*\*|\*\*:|:)\s*")
KEEP = re.compile(r"^\s*(?:[-*+] |\d+[.)] |\||#|>|```)")
RETRIES = 5


def pad(args: list[str], timeout: int, binary: str) -> str:
  """Run one pad command and return its stdout, retrying a rate-limited call.

  Args:
    args: arguments after `pad`.
    timeout: seconds before the call is abandoned.
    binary: the pad binary.

  Returns:
    stdout.

  Raises:
    RuntimeError: pad failed, timed out, or stayed rate-limited.
  """
  for attempt in range(RETRIES):
    try:
      p = subprocess.run([binary, *args], capture_output=True, text=True, timeout=timeout, check=False)
    except (subprocess.TimeoutExpired, FileNotFoundError) as exc:
      raise RuntimeError(f"pad {' '.join(args[:3])}: {exc}") from exc
    if p.returncode == 0:
      return p.stdout
    if "rate_limited" not in p.stderr or attempt == RETRIES - 1:
      break
    time.sleep(1.5 * (attempt + 1))
  raise RuntimeError(f"pad {' '.join(args[:3])} exited {p.returncode}: {p.stderr.strip()[-300:]}")


def reformat(body: str) -> str:
  """Lay a body out to the standard without changing a word.

  Args:
    body: the item's markdown.

  Returns:
    The body with each known label bolded at the start of its own paragraph and hard-wrapped prose lines joined; list items, tables, code
    fences, headings and quotes are kept line for line.
  """
  out: list[str] = []
  fenced = False
  for raw in body.replace("\r\n", "\n").split("\n"):
    line = raw.rstrip()
    if line.lstrip().startswith("```"):
      fenced = not fenced
      out.append(line)
      continue
    if fenced:
      out.append(line)
      continue
    if not line.strip():
      if out and out[-1] != "":
        out.append("")
      continue
    m = LABEL.match(line)
    if m:
      if out and out[-1] != "":
        out.append("")
      rest = line[m.end():]
      out.append(f"**{m.group(1)}:** {rest}".rstrip())
      continue
    prev = out[-1] if out else ""
    if prev and not KEEP.match(line) and not KEEP.match(prev) and not prev.lstrip().startswith("```"):
      out[-1] = f"{prev} {line.strip()}"
    elif prev and KEEP.match(line) is None and re.match(r"^\s*(?:[-*+] |\d+[.)] )", prev) and raw.startswith("  "):
      out[-1] = f"{prev} {line.strip()}"  # a wrapped continuation of a list item
    else:
      if KEEP.match(line) is None and prev and KEEP.match(prev):
        out.append("")  # prose after a list or table starts a new paragraph
      out.append(line)
  while out and out[-1] == "":
    out.pop()
  return "\n".join(out)


def words(text: str) -> list[str]:
  """The words of a text, ignoring layout and bold markers.

  Args:
    text: markdown.

  Returns:
    Its whitespace-separated tokens with `**` removed.
  """
  return text.replace("**", "").split()


def main(argv: list[str] | None = None) -> int:
  """Read the items, build the spec, print the plan.

  Args:
    argv: command-line arguments (default sys.argv[1:]).

  Returns:
    The exit code.
  """
  ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
  ap.add_argument("--out", required=True)
  ap.add_argument("--collections", nargs="+", default=list(DEFAULT_COLLECTIONS))
  ap.add_argument("--pad", default="pad")
  ap.add_argument("--timeout", type=int, default=60)
  a = ap.parse_args(argv)
  bad = NEVER.intersection(a.collections)
  if bad:
    print(f"refused: {sorted(bad)} are generated or library collections", file=sys.stderr)
    return 2
  start = time.monotonic()
  items, checked = [], 0
  try:
    for coll in a.collections:
      listed = json.loads(pad(["item", "list", coll, "--all", "--format", "json"], a.timeout, a.pad) or "[]")
      for row in listed:
        shown = json.loads(pad(["item", "show", row["ref"], "--format", "json"], a.timeout, a.pad))
        item = shown.get("item", shown)
        body = item.get("content") or ""
        checked += 1
        new = reformat(body)
        # Pad stores an underscore in some bodies as `\_` (seen 2026-11-19, ASK-29 after a body write): equal for this purpose.
        if new.replace("\\_", "_") == body.replace("\\_", "_"):
          continue
        if words(new) != words(body):
          print(f"SKIP {row['ref']}: reformat would change words (bug in this script); left alone", file=sys.stderr)
          continue
        items.append({"ref": row["ref"], "seq": item.get("seq", row.get("seq")), "body": new})
        print(f"plan {row['ref']}: {row['title'][:70]}")
  except RuntimeError as exc:
    print(exc, file=sys.stderr)
    return 1
  with open(a.out, "w", encoding="utf-8") as f:
    json.dump({"items": items}, f, indent=1, ensure_ascii=False)
  print(f"{checked} item(s) read, {len(items)} to reformat; spec {a.out}; {time.monotonic() - start:.1f} s")
  return 0


if __name__ == "__main__":
  sys.exit(main())
