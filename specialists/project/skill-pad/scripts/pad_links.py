#!/usr/bin/env python3
"""Make Pad item references clickable and record their typed relations.

Why (operator, 2026-11-20, continuum ASK-251): "why are these references not links ... so that I can click on them", and "the relationship is not
established ... you should be utilizing the relationship section for each item so that there is proper dependency". An item body that names
`TASK-245` or `DL-058` as plain text gives no backlink and no dependency; Pad resolves `[[REF]]` wiki-links (backlinks, the related view) and
keeps typed relations (blocks, implements, split-from, supersedes) as the dependency graph.

What it does, for the items named (or every item updated since a date):
  1. Bodies, and comments an agent wrote (2026-11-20): a bare reference to an existing item (`TASK-12`, `ASK-251`, `DECIS-148`, any collection prefix in the workspace) becomes `[[REF]]`;
     a decision-log id (`DL-058`), a conflict id (`cf-0e7a848021`) or a register id (`D17`, `S20`, `X2`; 2026-11-20, unc; never `D17-03` or `D3.6`)
     that a decisions-collection item mirrors (field `decision_ref`) becomes
     `[[DECIS-n|DL-058]]`, shown as the id. Text already inside `[[...]]`, inline code or a fenced block, and the item's own ref, are left alone; decision
     mirrors, playbooks and conventions are skipped (generated, or library text whose sample refs like TASK-5 would link to real items).
     Writes are guarded by the item's `seq` (`--expected-seq`): a conflict means someone changed it; re-run, never force.
  2. Relations, from an optional JSON spec: [{"type": "blocks" | "implements" | "split-from" | "supersedes", "from": "TASK-1", "to": "PLAN-2"}]
     (`blocks`: from blocks to; `implements`: from implements to; `split-from`: from was split from to; `supersedes`: from supersedes to).
     Relations already listed by `pad item related` are skipped.

Usage (from the project folder whose .pad.toml names the workspace):
    python3 pad_links.py --refs ASK-251,FR-248                  # plan
    python3 pad_links.py --since 2026-11-20 --relations rel.json --apply
Options: --pad PATH (pad binary), --timeout SECONDS (60). Safety: plan by default; Pad writes only with --apply; reads no project files.
Exit codes: 0 done or nothing to do; 1 a write failed (the rest still ran); 2 bad arguments. Runtime budget: 60 s for about 50 items.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time

REF = re.compile(r"\b([A-Z][A-Z0-9]{1,9}-\d+)\b")
DECISION_ID = re.compile(r"\b(DL-\d{3}|cf-[0-9a-f]{10}|[DSX]\d{1,3})\b(?![.\-]\w)")
PROTECTED = re.compile(r"```.*?```|`[^`\n]*`|\[\[[^\]]*\]\]", re.S)
VERBS = {"blocks": "block", "implements": "implements", "split-from": "split-from", "supersedes": "supersedes"}


def pad(binary: str, timeout: int, *args: str, stdin: str | None = None) -> str:
  """Run one pad command, backing off on a rate limit.

  Args:
    binary: the pad executable.
    timeout: seconds per call.
    *args: arguments after `pad`.
    stdin: text for standard input, if any.

  Returns:
    The command's stdout.

  Raises:
    RuntimeError: the command failed, or is still rate limited after five attempts.
  """
  for attempt in range(5):
    r = subprocess.run([binary, *args], input=stdin, capture_output=True, text=True, timeout=timeout)
    if r.returncode == 0:
      return r.stdout
    if "rate_limited" not in r.stderr + r.stdout:
      raise RuntimeError(f"pad {' '.join(args[:3])}: {(r.stderr or r.stdout).strip()[:300]}")
    time.sleep(1 + attempt)
  raise RuntimeError("pad: still rate limited after five attempts")


def index(binary: str, timeout: int) -> tuple[list[dict], dict[str, str]]:
  """Every item in the workspace, and decision ids mapped to the mirror item that holds them.

  Args:
    binary: the pad executable.
    timeout: seconds per call.

  Returns:
    (items, {decision_ref: item ref}).
  """
  data = json.loads(pad(binary, timeout, "item", "list", "--all", "--format", "json", "--limit", "5000") or "[]")
  items = data.get("items", data) if isinstance(data, dict) else data
  decisions = {}
  for it in items:
    fields = it.get("fields") or {}
    fields = json.loads(fields) if isinstance(fields, str) else fields
    if fields.get("decision_ref"):
      decisions[fields["decision_ref"]] = it["ref"]
  return items, decisions


def linked(body: str, own: str, refs: set[str], decisions: dict[str, str]) -> str:
  """Rewrite bare references in body as wiki-links, leaving protected spans alone.

  Args:
    body: the item body.
    own: the item's own ref (never linked to itself).
    refs: every existing item ref.
    decisions: decision id -> mirror item ref.

  Returns:
    The rewritten body (equal to body when nothing applies).
  """

  def plain(text: str) -> str:
    text = REF.sub(lambda m: f"[[{m[1]}]]" if m[1] in refs and m[1] != own else m[0], text)
    return DECISION_ID.sub(lambda m: f"[[{decisions[m[1]]}|{m[1]}]]" if m[1] in decisions else m[0], text)

  out, last = [], 0
  for m in PROTECTED.finditer(body):
    out += [plain(body[last : m.start()]), m[0]]
    last = m.end()
  return "".join([*out, plain(body[last:])])


def relation_present(binary: str, timeout: int, rel: dict) -> bool:
  """Is this relation already listed around its source item?

  Args:
    binary: the pad executable.
    timeout: seconds per call.
    rel: {"type", "from", "to"}.

  Returns:
    True when `pad item related <from>` already names the target.
  """
  return re.search(rf"\b{re.escape(rel['to'])}\b", pad(binary, timeout, "item", "related", rel["from"])) is not None


def link_comments(binary: str, timeout: int, ref: str, refs: set[str], decisions: dict[str, str], apply: bool) -> int:
  """Link the references in an item's agent-written comments, as in bodies (2026-11-20, operator: a status comment read "Unblocked: ASK-237
  answered" with no link). A comment written by a person is left as written; a comment's author is the only one who may edit it.

  Args:
    binary: the pad executable.
    timeout: seconds per call.
    ref: the item's ref.
    refs: every existing item ref.
    decisions: decision id -> mirror item ref.
    apply: write when True, else print the plan.

  Returns:
    The number of failed writes.
  """
  data = json.loads(pad(binary, timeout, "item", "comments", ref, "--format", "json") or "[]")
  failed = 0
  for c in data.get("comments", data) if isinstance(data, dict) else data:
    if c.get("created_by") != "agent" or c.get("deleted"):
      continue
    new = linked(c.get("body") or "", ref, refs, decisions)
    if new == (c.get("body") or ""):
      continue
    print(f"{'write' if apply else 'plan'}: {ref} comment {c['id'][:8]}")
    if apply:
      try:
        pad(binary, timeout, "item", "comment-edit", ref, c["id"], "--stdin", stdin=new)
      except RuntimeError as e:
        failed += 1
        print(f"FAIL {ref} comment {c['id'][:8]}: {e}")
  return failed


def main(argv: list[str] | None = None) -> int:
  """Command line entry.

  Args:
    argv: arguments (default sys.argv[1:]).

  Returns:
    The exit code.
  """
  p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
  p.add_argument("--refs", default="", help="comma list of item refs")
  p.add_argument("--since", default="", help="every item updated on or after YYYY-MM-DD")
  p.add_argument("--relations", default="", help="JSON spec of typed relations")
  p.add_argument("--apply", action="store_true")
  p.add_argument("--pad", default="pad")
  p.add_argument("--timeout", type=int, default=60)
  a = p.parse_args(argv)
  if not a.refs and not a.since and not a.relations:
    p.error("give --refs, --since or --relations")
  items, decisions = index(a.pad, a.timeout)
  refs = {it["ref"] for it in items}
  targets = [r for r in a.refs.split(",") if r] + [it["ref"] for it in items if a.since and str(it.get("updated_at", "")) >= a.since]
  failed = 0
  for ref in dict.fromkeys(targets):
    if ref.startswith(("DECIS-", "PLAYB-", "CONVE-")):
      continue  # decision mirrors are generated (pad_decisions.py); playbooks and conventions come from Pad's library with sample refs
    it = json.loads(pad(a.pad, a.timeout, "item", "show", ref, "--format", "json"))
    new = linked(it.get("content") or "", ref, refs, decisions)
    if new != (it.get("content") or ""):
      print(f"{'write' if a.apply else 'plan'}: {ref} body ({len(REF.findall(new))} refs)")
      if a.apply:
        try:
          pad(a.pad, a.timeout, "item", "update", ref, "--stdin", "--expected-seq", str(it["seq"]), stdin=new)
        except RuntimeError as e:
          failed += 1
          print(f"FAIL {ref}: {e}")
    failed += link_comments(a.pad, a.timeout, ref, refs, decisions, a.apply)
  for rel in json.loads(open(a.relations).read()) if a.relations else []:
    if rel["type"] not in VERBS or relation_present(a.pad, a.timeout, rel):
      print(f"skip: {rel}")
      continue
    print(f"{'write' if a.apply else 'plan'}: {rel['from']} {rel['type']} {rel['to']}")
    if a.apply:
      try:
        pad(a.pad, a.timeout, "item", VERBS[rel["type"]], rel["from"], rel["to"])
      except RuntimeError as e:
        failed += 1
        print(f"FAIL {rel}: {e}")
  return 1 if failed else 0


if __name__ == "__main__":
  sys.exit(main())
