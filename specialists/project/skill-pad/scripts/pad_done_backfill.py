#!/usr/bin/env python3
"""Backfill the closing statement of closed work items that have none, built only from the item's own comments.

Why (docs/pad-usage-guidelines-20261110_1628.md 3.3, "An item tells its whole story"): item-check fails a closed plan, task, bug or tech-debt item
with no `DONE:` or `CLOSED:` comment. Items closed before the rule, or closed with a free-form note, have their story in earlier comments. This
script writes one `<date> <time> AEDT DONE:` comment per item that quotes where the story is (the newest substantive comment, cut, with its id
and date) and says that the closing statement was written later from those comments; what it cannot know reads "not recorded". It invents
nothing and edits no existing comment.

Usage:
    python3 pad_done_backfill.py --refs TASK-1,TD-2              # plan: prints each comment it would add
    python3 pad_done_backfill.py --refs TASK-1,TD-2 --apply      # adds them
Options: --stamp "2026-11-21 19:45" (default: now, local), --pad PATH, --timeout SECONDS.
Exit: 0 done or planned, 1 a pad call failed, 2 bad arguments. Budget: one show per ref and one comment per write (about 0.3 s each).
"""

from __future__ import annotations

import argparse
import datetime
import json
import re
import subprocess
import sys
import time

CLOSING = re.compile(r"\b(DONE|CLOSED):")
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


def field(item: dict, name: str) -> str:
  """A field of an item; Pad returns `fields` as a JSON string (2026-11-21), older builds as an object.

  Args:
    item: the item from `pad item show --format json`.
    name: the field name.

  Returns:
    Its value as text, or "?".
  """
  f = item.get("fields") or {}
  if isinstance(f, str):
    try:
      f = json.loads(f)
    except json.JSONDecodeError:
      return "?"
  return str(f.get(name, "?")) if isinstance(f, dict) else "?"


def statement(title: str, status: str, comments: list[dict], stamp: str) -> str | None:
  """The DONE comment for an item, or None when it already has a closing statement.

  Args:
    title: the item title.
    status: its closed status.
    comments: its comments (dicts with id, body or content, created_at), oldest first.
    stamp: `YYYY-MM-DD HH:MM` for the comment header.

  Returns:
    The comment text, or None.
  """
  texts = [(c.get("id", "?"), (c.get("body") or c.get("content") or "").strip(), str(c.get("created_at", ""))[:10]) for c in comments]
  if any(CLOSING.search(t) for _, t, _ in texts):
    return None
  real = [t for t in texts if len(t[1]) > 40]
  if real:
    cid, text, date = real[-1]
    one = " ".join(text.split())
    result = f"as recorded in comment {cid[:8]} ({date}): {one[:400]}{'...' if len(one) > 400 else ''}"
    evidence = ", ".join(f"{c[:8]} ({d})" for c, _, d in real[-3:])
  else:
    result, evidence = "not recorded (the item has no substantive comment)", "not recorded"
  return (
    f"{stamp} AEDT DONE:\n"
    f"- **What:** {title} (status {status})\n"
    f"- **Result:** {result}\n"
    f"- **Evidence:** comments {evidence}\n"
    f"- **Not verified:** this closing statement was written in a later template pass from the item's own comments; anything they do not say is not recorded\n"
    f"- **Next:** none recorded"
  )


def main(argv: list[str] | None = None) -> int:
  """Read each item, plan or add its closing statement.

  Args:
    argv: command-line arguments (default sys.argv[1:]).

  Returns:
    The exit code.
  """
  ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
  ap.add_argument("--refs", required=True)
  ap.add_argument("--stamp", default=datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
  ap.add_argument("--apply", action="store_true")
  ap.add_argument("--pad", default="pad")
  ap.add_argument("--timeout", type=int, default=60)
  a = ap.parse_args(argv)
  start, n = time.monotonic(), 0
  try:
    for ref in [r.strip() for r in a.refs.split(",") if r.strip()]:
      shown = json.loads(pad(["item", "show", ref, "--format", "json"], a.timeout, a.pad))
      item = shown.get("item", shown)
      comments = json.loads(pad(["item", "comments", ref, "--format", "json"], a.timeout, a.pad) or "[]")
      comments = comments.get("comments", comments) if isinstance(comments, dict) else comments
      status = field(item, "status")
      text = statement(item.get("title", ""), status, comments, a.stamp)
      if text is None:
        continue
      n += 1
      print(f"{'add' if a.apply else 'plan'} {ref}: {text.splitlines()[2][:110]}")
      if a.apply:
        pad(["item", "comment", ref, text], a.timeout, a.pad)
  except (RuntimeError, json.JSONDecodeError) as exc:
    print(exc, file=sys.stderr)
    return 1
  print(f"{n} closing statement(s) {'added' if a.apply else 'planned'}; {time.monotonic() - start:.1f} s")
  return 0


if __name__ == "__main__":
  sys.exit(main())
