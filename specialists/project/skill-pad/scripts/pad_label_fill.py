#!/usr/bin/env python3
"""Write a pad_rewrite.py spec that adds each missing required label of the per-collection templates, inventing nothing.

Why (operator, 2026-11-20: "Extend and enforce"; docs/pad-usage-guidelines-20261110_1628.md 3.3, Templates by collection): item-check fails an
item that lacks a required label, and the standard says "nothing is invented to fill one: a required label with nothing to say reads 'not
recorded' with the date of the pass". This script does exactly that, after pad_format_spec.py has bolded the labels already there:
  - Asks: a missing **Question:** takes the item's title (the question as asked).
  - Conventions: a missing **Rule:** labels the first unlabelled paragraph (its words unchanged); a missing **Source:** reads not recorded.
  - Every other missing required label: `**<Label>:** not recorded (template pass <date>)`, placed after the paragraph of the nearest
    required label before it in the template's order, else at the top.
  - Feature requests need Serves and Why only when the body is more than one line (a one-line request is the operator's words, kept).
It writes nothing in Pad: review the plan, then `pad_rewrite.py <spec> --apply` (body writes guarded by seq). Run from the project folder.

Usage:
    python3 pad_label_fill.py --refs TASK-1,ASK-2 --out spec.json [--date 2026-11-21]
Options: --pad PATH, --timeout SECONDS.
Exit: 0 spec written (possibly empty), 1 a pad call failed, 2 bad arguments. Budget: one show per ref (about 0.2 s each); prints its time.
"""

from __future__ import annotations

import argparse
import datetime
import json
import re
import subprocess
import sys
import time

# Kept in step with pad_item_check.py LABELS (tests/test_pad_label_fill.py checks it); decisions are a generated mirror, never filled.
REQUIRED = {
  "plans": ("Serves", "Goal", "Done when", "Out of scope", "Waits on"),
  "tasks": ("Serves", "Why", "Do", "Done when", "Writes", "Refs"),
  "bugs": ("Seen", "Evidence", "Effect", "Closure"),
  "tech-debt": ("Serves", "Why", "Do", "Done when"),
  "ideas": ("Serves", "Why", "Do"),
  "asks": ("Question",),
  "feature-requests": ("Serves", "Why"),
  "conventions": ("Rule", "Source"),
}
BOLD = re.compile(r"^\*\*([^*:]+):\*\*")
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
  p = None
  for attempt in range(RETRIES):
    try:
      p = subprocess.run([binary, *args], capture_output=True, text=True, timeout=timeout, check=False)
    except (subprocess.TimeoutExpired, FileNotFoundError) as exc:
      raise RuntimeError(f"pad {' '.join(args[:3])}: {exc}") from exc
    if p.returncode == 0:
      return p.stdout
    if "rate_limited" not in (p.stderr + p.stdout) or attempt == RETRIES - 1:
      break
    time.sleep(1.5 * (attempt + 1))
  raise RuntimeError(f"pad {' '.join(args[:3])} exited {p.returncode if p else '?'}: {(p.stderr if p else '').strip()[-300:]}")


def fill(collection: str, title: str, body: str, date: str) -> str:
  """The body with every missing required label added; unchanged when none is missing or the collection has no template here.

  Args:
    collection: the collection slug.
    title: the item title (an ask's question).
    body: the current body.
    date: the pass date for `not recorded`.

  Returns:
    The new body.
  """
  required = REQUIRED.get(collection)
  if not required:
    return body
  paras = [p for p in body.strip().split("\n\n")] if body.strip() else []
  if collection == "feature-requests" and len(body.strip().splitlines()) <= 1:
    return body
  present = {m.group(1).strip() for p in paras if (m := BOLD.match(p))}
  for i, label in enumerate(required):
    if label in present:
      continue
    if collection == "conventions" and label == "Rule":
      j = next((k for k, p in enumerate(paras) if not BOLD.match(p)), None)
      if j is not None:
        paras[j] = f"**Rule:** {paras[j]}"
        present.add("Rule")
        continue
    text = title if (collection == "asks" and label == "Question") else f"not recorded (template pass {date})"
    before = [k for k, p in enumerate(paras) if (m := BOLD.match(p)) and m.group(1).strip() in required[:i]]
    at = before[-1] + 1 if before else 0
    paras.insert(at, f"**{label}:** {text}")
    present.add(label)
  return "\n\n".join(paras)


def main(argv: list[str] | None = None) -> int:
  """Read the items, build the spec, print the plan.

  Args:
    argv: command-line arguments (default sys.argv[1:]).

  Returns:
    The exit code.
  """
  ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
  ap.add_argument("--refs", required=True)
  ap.add_argument("--out", required=True)
  ap.add_argument("--date", default=datetime.date.today().isoformat())
  ap.add_argument("--pad", default="pad")
  ap.add_argument("--timeout", type=int, default=60)
  a = ap.parse_args(argv)
  start, items = time.monotonic(), []
  try:
    for ref in [r.strip() for r in a.refs.split(",") if r.strip()]:
      shown = json.loads(pad(["item", "show", ref, "--format", "json"], a.timeout, a.pad))
      item = shown.get("item", shown)
      body = item.get("content") or ""
      new = fill(item.get("collection_slug", ""), item.get("title", ""), body, a.date)
      if new != body:
        items.append({"ref": ref, "seq": item.get("seq"), "body": new})
        print(f"plan {ref}: {item.get('title', '')[:70]}")
  except RuntimeError as exc:
    print(exc, file=sys.stderr)
    return 1
  with open(a.out, "w", encoding="utf-8") as f:
    json.dump({"items": items}, f, indent=1, ensure_ascii=False)
  print(f"{len(items)} item(s) to fill; spec {a.out}; {time.monotonic() - start:.1f} s")
  return 0


if __name__ == "__main__":
  sys.exit(main())
