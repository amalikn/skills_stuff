#!/usr/bin/env python3
"""Apply a reviewed rewrite of Pad items from a JSON spec: bodies, titles and tags, comment type prefixes, and note and decide entries.

Why (operator, 2026-11-10: "update all the opened plans and tasks ... to follow the usage guidelines"): bringing a workspace to the writing
standard (docs/pad-usage-guidelines-20261110_1628.md, section 3.3) is dozens of guarded writes; a spec reviewed first and applied by one script keeps
them repeatable and safe. Run from the project folder whose .pad.toml names the workspace.

Spec (JSON):
    {"items":    [{"ref": "TASK-30", "seq": 55, "title": "...", "body": "...", "tags": ["prod-write"], "fields": {"due_date": "2026-11-13"}}],
     "comments": [{"ref": "TASK-30", "id": "<comment-id>", "type": "FINDING"},   # add the type word only
                  {"ref": "TASK-30", "id": "<comment-id>", "body": "<whole new text>"}],   # replace the text (skipped when equal)
     "notes":    [{"ref": "TASK-30", "summary": "...", "details": "...", "key": "<stable key>"}],
     "decides":  [{"ref": "TASK-30", "decision": "...", "rationale": "...", "key": "<stable key>"}]}
Each part is optional. A body write is guarded by the spec's `seq` (a conflict means someone changed the item: re-read, never force); a comment
gains `TYPE: ` after its leading timestamp, or at the start, and is skipped when it already carries a type; notes and decisions use the key as an
idempotency key, so a rerun adds nothing twice.

Usage:
    python3 pad_rewrite.py spec.json            # plan: what would change, per item
    python3 pad_rewrite.py spec.json --apply    # write
Options: --pad PATH (default pad), --timeout SECONDS (60).
Exit: 0 done or plan printed, 1 a pad call failed (later writes are not attempted), 2 bad arguments or spec.
Budget: about 0.3 s per write (one pad call each); prints its time.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
from pathlib import Path

TYPES = ("FINDING", "BLOCKED", "RISK", "CORRECTION", "HANDOFF", "NEXT")
STAMP = re.compile(r"^(?P<stamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}(?: [A-Z]{3,5})?)(?P<sep>:?\s*)")


def prefixed(body: str, kind: str) -> str | None:
  """Return the comment body with its type word added, or None when it already has one.

  Args:
    body: the comment text.
    kind: one of TYPES.

  Returns:
    The new body (`<stamp> TYPE: rest`, or `TYPE: rest` without a stamp), or None if a type word is already present.

  Raises:
    ValueError: an unknown type.
  """
  if kind not in TYPES:
    raise ValueError(f"unknown comment type {kind}")
  m = STAMP.match(body)
  rest = body[m.end():] if m else body
  if any(rest.startswith(t + ":") for t in TYPES) or any(body.startswith(t + " ") or body.startswith(t + ":") for t in TYPES):
    return None
  return f"{m.group('stamp')} {kind}: {rest}" if m else f"{kind}: {rest}"


def commands(spec: dict, comment_bodies: dict[str, str]) -> list[tuple[str, list[str], str | None]]:
  """Turn a spec into the ordered pad calls to make.

  Args:
    spec: the parsed spec (see module docstring).
    comment_bodies: comment id -> its current body, read from the workspace.

  Returns:
    (label, argv after `pad`, stdin text or None) per write, in the order items, comments, notes, decides.

  Raises:
    ValueError: an item without `seq` but with a body, a comment id not found, or an unknown type.
  """
  out = []
  for it in spec.get("items", []):
    argv = ["item", "update", it["ref"]]
    if it.get("title"):
      argv += ["--title", it["title"]]
    if "tags" in it:
      argv += ["--tags", json.dumps(it["tags"])]
    if it.get("fields"):
      argv += ["--fields-json", json.dumps(it["fields"])]
    stdin = None
    if it.get("body"):
      if "seq" not in it:
        raise ValueError(f"{it['ref']}: a body write needs the seq it was drafted from")
      argv += ["--stdin", "--expected-seq", str(it["seq"])]
      stdin = it["body"]
    if len(argv) > 3:
      out.append((f"update {it['ref']}", argv, stdin))
  for c in spec.get("comments", []):
    if c["id"] not in comment_bodies:
      raise ValueError(f"{c['ref']}: comment {c['id']} not found")
    if "body" in c:
      new = None if c["body"] == comment_bodies[c["id"]] else c["body"]
    else:
      new = prefixed(comment_bodies[c["id"]], c["type"])
    if new is not None:
      out.append((f"comment {c['ref']} {c['id'][:8]} {c.get('type', 'body')}", ["item", "comment-edit", c["ref"], c["id"], "--stdin"], new))
  for n in spec.get("notes", []):
    argv = ["item", "note", n["ref"], n["summary"], "--op-key", n["key"]] + (["--details", n["details"]] if n.get("details") else [])
    out.append((f"note {n['ref']}", argv, None))
  for d in spec.get("decides", []):
    argv = ["item", "decide", d["ref"], d["decision"], "--op-key", d["key"]] + (["--rationale", d["rationale"]] if d.get("rationale") else [])
    out.append((f"decide {d['ref']}", argv, None))
  return out


def pad(argv: list[str], timeout: int, binary: str, stdin: str | None = None) -> str:
  """Run one pad command.

  Args:
    argv: arguments after the binary.
    timeout: seconds before the call is stopped.
    binary: the pad executable.
    stdin: text fed on stdin, or None.

  Returns:
    The command's stdout.

  Raises:
    RuntimeError: a non-zero exit or a timeout, with pad's stderr.
  """
  try:
    r = subprocess.run([binary, *argv], input=stdin, capture_output=True, text=True, timeout=timeout)
  except subprocess.TimeoutExpired as exc:
    raise RuntimeError(f"pad {' '.join(argv[:3])} timed out after {timeout}s") from exc
  if r.returncode != 0:
    raise RuntimeError(f"pad {' '.join(argv[:3])} failed: {r.stderr.strip()[:400]}")
  return r.stdout


def main(argv: list[str] | None = None) -> int:
  """Plan, and with --apply write, the spec's changes.

  Args:
    argv: command-line arguments (None reads sys.argv).

  Returns:
    The exit code: 0 done or plan printed, 1 a pad call failed, 2 bad arguments or spec.
  """
  ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
  ap.add_argument("spec", type=Path)
  ap.add_argument("--apply", action="store_true", help="write; without it only the plan is printed")
  ap.add_argument("--pad", default="pad")
  ap.add_argument("--timeout", type=int, default=60)
  a = ap.parse_args(argv)
  started = time.monotonic()
  try:
    spec = json.loads(a.spec.read_text(encoding="utf-8"))
    bodies: dict[str, str] = {}
    for ref in sorted({c["ref"] for c in spec.get("comments", [])}):
      for c in json.loads(pad(["item", "comments", ref, "--format", "json"], a.timeout, a.pad) or "[]"):
        bodies[c["id"]] = c["body"]
    todo = commands(spec, bodies)
  except (OSError, ValueError, KeyError, RuntimeError) as exc:
    print(f"pad_rewrite: {exc}", file=sys.stderr)
    return 2
  for label, cmd, stdin in todo:
    print(("apply " if a.apply else "plan  ") + label)
    if a.apply:
      try:
        pad(cmd, a.timeout, a.pad, stdin)
      except RuntimeError as exc:
        print(f"pad_rewrite: {exc}", file=sys.stderr)
        return 1
  print(f"{'applied' if a.apply else 'PLAN:'} {len(todo)} write(s); {time.monotonic() - started:.1f} s" + ("" if a.apply else "; --apply to write"))
  return 0


if __name__ == "__main__":
  sys.exit(main())
