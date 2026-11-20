#!/usr/bin/env python3
"""Check a rewrite spec keeps every word of the bodies it replaces, before `just rewrite --apply`. Read-only.

Why (2026-11-20, unc): 83 bug bodies were restructured into the bug template by sub-agents told to keep every word; before applying, each new body
was compared with the item's current body as a multiset of words, so a dropped or reworded sentence shows up. Label words added by the template
(Seen, Evidence, Effect, Closure, ...) and the "not recorded" filler are allowed extras; nothing of the original may be missing.

Run (from the project folder whose .pad.toml names the workspace):
    python3 pad_spec_words.py spec.json [--allow WORD ...] [--workspace SLUG]
Spec: the `just rewrite` format, {"items": [{"ref": "BUG-5", "body": "..."}]}; items without a body are skipped.
Exit: 0 every body keeps its words; 1 at least one item lost words (listed); 2 bad spec or a pad call failed.
Safety: reads Pad through `pad item show`; writes nothing. Runtime: one pad call per item (about 0.2 s each), rate limits retried.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
from collections import Counter
from pathlib import Path

RETRIES = 5
BACKOFF_S = 1.5
WORD = re.compile(r"[a-z0-9]+")


def words(text: str) -> Counter:
  """The words of a text as a multiset, lowercased, markup and punctuation dropped.

  Args:
    text: a body.

  Returns:
    word -> count.
  """
  return Counter(WORD.findall(text.lower()))


def lost(old: str, new: str, allow: set[str]) -> Counter:
  """The words of the old body the new one no longer holds.

  Args:
    old: the current body.
    new: the body the spec would write.
    allow: words that may go (a label word an old plain label turned into, e.g. "evidence").

  Returns:
    word -> how many copies are missing; empty when every word is kept.
  """
  missing = words(old) - words(new)
  for w in allow:
    missing.pop(w, None)
  return missing


def pad_show(ref: str, extra: list[str], timeout: int) -> str:
  """An item's current body, retrying a rate limit.

  Args:
    ref: the item ref.
    extra: global pad flags (--workspace).
    timeout: seconds per call.

  Returns:
    The body.

  Raises:
    RuntimeError: pad failed for another reason or kept refusing.
  """
  for attempt in range(RETRIES):
    p = subprocess.run(["pad", "item", "show", ref, "--format", "json", *extra], capture_output=True, text=True, timeout=timeout)
    if p.returncode == 0:
      return json.loads(p.stdout).get("content") or ""
    if "rate_limited" not in p.stderr + p.stdout or attempt == RETRIES - 1:
      raise RuntimeError(f"pad item show {ref}: {(p.stderr or p.stdout).strip()[-200:]}")
    time.sleep(BACKOFF_S * (attempt + 1))
  raise RuntimeError(f"pad item show {ref}: rate limited")


def main(argv: list[str] | None = None) -> int:
  """Compare every body in the spec with the item's current body.

  Args:
    argv: the command line (default sys.argv).

  Returns:
    0 clean, 1 words lost, 2 bad spec or pad failure.
  """
  ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
  ap.add_argument("spec", type=Path)
  ap.add_argument("--allow", nargs="*", default=[], help="words that may disappear (a plain label made bold, e.g. cause)")
  ap.add_argument("--workspace", default=None)
  ap.add_argument("--timeout", type=int, default=30)
  a = ap.parse_args(argv)
  started = time.monotonic()
  try:
    items = [i for i in json.loads(a.spec.read_text()).get("items", []) if "body" in i]
  except (OSError, ValueError, AttributeError) as error:
    print(f"pad_spec_words: bad spec: {error}", file=sys.stderr)
    return 2
  extra = ["--workspace", a.workspace] if a.workspace else []
  bad = 0
  try:
    for it in items:
      missing = lost(pad_show(it["ref"], extra, a.timeout), it["body"], {w.lower() for w in a.allow})
      if missing:
        bad += 1
        print(f"{it['ref']}: lost {sum(missing.values())} word(s): {', '.join(sorted(missing))[:200]}")
  except RuntimeError as error:
    print(f"pad_spec_words: {error}", file=sys.stderr)
    return 2
  print(f"{len(items)} body(ies) checked, {bad} lost words; {time.monotonic() - started:.1f} s")
  return 1 if bad else 0


if __name__ == "__main__":
  sys.exit(main())
