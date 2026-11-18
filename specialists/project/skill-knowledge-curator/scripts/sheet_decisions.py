#!/usr/bin/env python3
"""Turn a ticked decision sheet (from decision_sheet.py) into `kc decide` calls: plan by default, `--apply` records them.

Each conflict question must have exactly one `[x]`; an unticked question stays open and is skipped; two ticks stop the run. The ticked option's
bracket gives the action (USE_OTHER --current <claim>, BOTH_APPLY_SCOPED, CORRECTED, DEFER); text after it is the scope note, corrected statement or
deferral reason; an `Other:` tick becomes CORRECTED with its text. The question's Notes paragraph becomes the reason. Contract-gap questions (no
conflict id in the heading) are listed, not recorded: they have no kc conflict. Found in Continuum (2026-11-18): the operator answered 44 questions in
chat; the agent ticked the sheet with a dated note per question and needed exactly this reader, written ad hoc first.

Safety: plan prints one line per call; `--apply` first dry-runs every call through kc and writes nothing unless all pass, then applies them in sheet
order.

Run: python scripts/sheet_decisions.py --project <p> --sheet sheet.md [--actor NAME] [--answer-suffix TEXT] [--apply] (or `just sheet-decisions ...`).
Standard library only; kc runs in a subprocess with a timeout. Exit 0 ok, 1 refused input or a failed call.
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

KC = Path(__file__).resolve().parent / "knowledge_curator.py"
HEAD = re.compile(r"^### (\d+)\. (cf-[0-9a-f]{10}|[^\n]+)$", re.M)
ACTION = re.compile(r"\[(USE_OTHER|BOTH_APPLY_SCOPED|CORRECTED|DEFER)(?: --current (cl-[0-9a-f]{12}))?\]")


def questions(text: str) -> list[tuple[str, str, str]]:
  """Split a sheet into questions.

  Args:
    text: the sheet's Markdown.

  Returns:
    (number, heading id or title, body) per question, in order.
  """
  marks = list(HEAD.finditer(text))
  return [(m[1], m[2].split()[0], text[m.end() : marks[i + 1].start() if i + 1 < len(marks) else len(text)]) for i, m in enumerate(marks)]


def ticked(body: str) -> list[str]:
  """Return each ticked option of a question with its continuation lines joined.

  Args:
    body: one question's text.

  Returns:
    The ticked option lines, whitespace-normalised.
  """
  return [" ".join(m.group(1).split()) for m in re.finditer(r"^- \[x\] (.*?)(?=\n- \[|\n\n|\Z)", body, re.M | re.S)]


def call_for(conflict: str, line: str, body: str, actor: str, suffix: str) -> list[str]:
  """Build the `kc decide` arguments for one ticked line.

  Args:
    conflict: the conflict id.
    line: the ticked option text.
    body: the question's text (its Notes give the reason).
    actor: who decided.
    suffix: text appended to the answer, e.g. a date and channel.

  Returns:
    Arguments after `decide`.
  """
  notes = re.search(r"\*\*Notes:\*\*\s*\n(.*)", body, re.S)
  reason = " ".join((notes[1] if notes else "").split()) or "Ticked on the decision sheet."
  label = line.split(" [")[0].rstrip(":")
  m = ACTION.search(line)
  action, current = (m[1], m[2]) if m else ("CORRECTED", None)
  detail = re.sub(r"\*\*\(Recommended\)\*\*", "", line[m.end() :] if m else line.split(":", 1)[-1]).lstrip(" .:").rstrip()
  detail = re.sub(r"^(Scope|Reason):\s*", "", detail).strip()
  args = [conflict, action, "--actor", actor, "--answer-text", f"{label}{suffix}", "--reason", reason]
  args += ["--current", current] if current else []
  args += {"BOTH_APPLY_SCOPED": ["--scope-note", detail], "CORRECTED": ["--corrected-text", detail]}.get(action, [])
  if action == "DEFER" and detail:
    args[args.index("--reason") + 1] = f"{detail} {reason}".strip()
  return args


def plan(text: str, actor: str, suffix: str) -> tuple[list[dict], list[str]]:
  """Read every question into calls and notes.

  Args:
    text: the sheet's Markdown.
    actor: who decided.
    suffix: answer-text suffix.

  Returns:
    (calls, messages): one call per ticked conflict question; messages for skipped questions.

  Raises:
    ValueError: when a question has more than one tick.
  """
  calls, notes = [], []
  for number, ident, body in questions(text):
    ticks = ticked(body)
    if len(ticks) > 1:
      raise ValueError(f"Q{number}: {len(ticks)} ticks; one per question")
    if not ticks:
      notes.append(f"Q{number}: unticked, stays open")
    elif not ident.startswith("cf-"):
      notes.append(f"Q{number}: contract gap, not a kc conflict: {ticks[0][:80]}")
    else:
      calls.append({"q": int(number), "args": call_for(ident, ticks[0], body, actor, suffix)})
  return calls, notes


def run_kc(project: Path, args: list[str], apply: bool) -> subprocess.CompletedProcess:
  """Run one `kc decide` call.

  Args:
    project: the curated project.
    args: arguments after `decide`.
    apply: write when True; dry run otherwise.

  Returns:
    The completed process.
  """
  cmd = [sys.executable, str(KC), "decide", "--project", str(project), *args] + (["--apply"] if apply else [])
  return subprocess.run(cmd, capture_output=True, text=True, timeout=120)


def main(argv: list[str] | None = None) -> int:
  """Plan or apply the sheet's decisions.

  Args:
    argv: command-line arguments; None uses sys.argv.

  Returns:
    0 when planned or all applied; 1 on refused input or a failed call.
  """
  ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
  ap.add_argument("--project", required=True, type=Path)
  ap.add_argument("--sheet", required=True, type=Path)
  ap.add_argument("--actor", default="operator")
  ap.add_argument("--answer-suffix", default="", help="appended to each answer text, e.g. ' (operator, chat 2026-11-18)'")
  ap.add_argument("--apply", action="store_true")
  a = ap.parse_args(argv)
  try:
    calls, notes = plan(a.sheet.read_text(), a.actor, a.answer_suffix)
  except ValueError as error:
    print(f"refused: {error}", file=sys.stderr)
    return 1
  for n in notes:
    print(n)
  for c in calls:
    print(f"Q{c['q']}: decide {c['args'][0]} {c['args'][1]}")
  if not a.apply:
    print(f"plan: {len(calls)} call(s); --apply records them")
    return 0
  failed = [c for c in calls if run_kc(a.project, c["args"], False).returncode != 0]
  if failed:
    print(f"refused: dry run failed for {', '.join(f'Q{c["q"]}' for c in failed)}; nothing written", file=sys.stderr)
    return 1
  for c in calls:
    r = run_kc(a.project, c["args"], True)
    if r.returncode != 0:
      print(f"Q{c['q']}: apply failed: {(r.stderr or r.stdout).strip()[:200]}", file=sys.stderr)
      return 1
  print(json.dumps({"applied": len(calls)}))
  return 0


if __name__ == "__main__":
  raise SystemExit(main())
