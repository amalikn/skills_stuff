#!/usr/bin/env python3
"""Rebuild an agent's activity timings from Claude Code session transcripts, for any project and any past days (operator, 2026-11-24).

Each tool call becomes one event (start, end, seconds; AskUserQuestion counts as the operator's answering time), each gap between the agent's
last message and the person's next prompt becomes an operator_wait event, and side agents' tool calls are included with their agent id. Events
are the JSON Lines of the timing record (one per line, a file per month, the schema of continuum's DL-213 record) tagged
`"source": "transcript-backfill"`; calls already in the target (same tool_use_id, or same session and tool starting within 3 s) are skipped, so a
rerun or an overlap with live hooks adds nothing twice.

Run:
  python3 -I agent_timing_backfill.py --project-dir <path the sessions ran in> --from 2026-11-20 [--to 2026-11-24] --out <timings folder>
  ... --apply                                  # writes; without it, prints what it would add
Options: --transcripts <folder> instead of --project-dir; --min-wait 60 (seconds of silence that count as a wait).
Reads ~/.claude/projects/<project path with each non-alphanumeric character as '-'>/*.jsonl and <session>/subagents/*.jsonl.
Writes only <out>/<YYYY-MM>.jsonl, only with --apply. Exit: 0 done or planned; 2 bad arguments or no transcripts. Stdlib only.
Runtime budget: under 10 s for a month of one project's transcripts (one pass per file).
"""

import argparse
import datetime as dt
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

PROJECTS = Path.home() / ".claude" / "projects"
OPERATOR_TOOLS = {"AskUserQuestion"}


def transcripts_for(project_dir):
  """The transcript folder Claude Code uses for sessions started in `project_dir`.

  Args:
    project_dir: the working folder of the sessions.

  Returns:
    The folder path (it may not exist).
  """
  return PROJECTS / re.sub(r"[^A-Za-z0-9]", "-", str(Path(project_dir).resolve()))


def epoch(stamp):
  """Epoch seconds of a transcript timestamp (ISO 8601, `Z` for UTC).

  Args:
    stamp: the timestamp text.

  Returns:
    Seconds since the epoch.
  """
  return dt.datetime.fromisoformat(stamp.replace("Z", "+00:00")).timestamp()


def label(name, tool_input):
  """A short, secret-free label: the description, else the first 120 characters of a command, path or pattern.

  Args:
    name: the tool name.
    tool_input: the tool's input.

  Returns:
    The label.
  """
  if isinstance(tool_input, dict):
    for k in ("description", "command", "file_path", "pattern", "url", "query", "subagent_type", "skill"):
      if tool_input.get(k):
        return " ".join(str(tool_input[k]).split())[:120]
  return name


def is_prompt(entry):
  """Whether a transcript entry is a person's prompt (not a tool result or a system note).

  Args:
    entry: a transcript entry.

  Returns:
    True for a typed prompt.
  """
  if entry.get("type") != "user" or entry.get("isMeta"):
    return False
  content = (entry.get("message") or {}).get("content")
  if isinstance(content, str):
    return not content.startswith("<")
  return isinstance(content, list) and any(b.get("type") == "text" and not str(b.get("text", "")).startswith("<") for b in content)


def events_of(path, session, subagent, window, min_wait):
  """Tool-call and wait events of one transcript file inside the time window.

  Args:
    path: the transcript file.
    session: the session id.
    subagent: the side agent's id, or "" for the main session.
    window: (start, end) epoch bounds.
    min_wait: seconds of silence before a prompt that count as an operator wait (main session only).

  Returns:
    A list of event dicts.
  """
  uses, out, last_agent = {}, [], None
  for line in path.open(errors="replace"):
    try:
      e = json.loads(line)
      t = epoch(e["timestamp"])
    except (ValueError, KeyError, TypeError):
      continue
    if e.get("type") == "assistant":
      last_agent = t
    if not subagent and is_prompt(e) and last_agent and t - last_agent >= min_wait and window[0] <= last_agent < window[1]:
      out.append(event(last_agent, t, "operator_wait", "agent turn ended; waiting for the operator", session, subagent))
    content = (e.get("message") or {}).get("content")
    for b in content if isinstance(content, list) else []:
      if b.get("type") == "tool_use":
        uses[b.get("id")] = (t, b.get("name", ""), label(b.get("name", ""), b.get("input")))
      elif b.get("type") == "tool_result" and b.get("tool_use_id") in uses:
        start, name, text = uses.pop(b["tool_use_id"])
        if window[0] <= start < window[1]:
          kind = "operator_answer" if name in OPERATOR_TOOLS else "tool"
          out.append(event(start, t, kind, text, session, subagent, tool=name, tool_use_id=b["tool_use_id"], ok=not b.get("is_error")))
  return out


def event(start, end, kind, name, session, subagent, **extra):
  """One event in the timing record's schema.

  Args:
    start: start (epoch seconds).
    end: end (epoch seconds).
    kind: tool, operator_answer or operator_wait.
    name: label.
    session: session id.
    subagent: side agent id or "".
    extra: tool, tool_use_id, ok.

  Returns:
    The event dict.
  """
  actor = "operator" if kind.startswith("operator") else "agent"
  e = {"start": round(start, 3), "end": round(end, 3), "seconds": round(end - start, 3), "actor": actor, "kind": kind, "name": name}
  e.update({"session": session, "source": "transcript-backfill", **extra})
  if subagent:
    e["subagent"] = subagent
  return e


def existing(out):
  """Keys of events already in the target: tool_use_ids, and (session, tool or kind, start second) for events without one.

  Args:
    out: the timings folder.

  Returns:
    (ids, starts): a set of ids and a dict of (session, key) to start times.
  """
  ids, starts = set(), defaultdict(list)
  for f in sorted(out.glob("*.jsonl")) if out.exists() else []:
    for line in f.read_text(errors="replace").splitlines():
      try:
        e = json.loads(line)
      except ValueError:
        continue
      if e.get("tool_use_id"):
        ids.add(e["tool_use_id"])
      starts[(e.get("session", ""), e.get("tool") or e.get("kind"))].append(e.get("start", 0))
  return ids, starts


def new_only(events, ids, starts):
  """Drop events already recorded (same tool_use_id, or same session and tool within 3 s of an existing start).

  Args:
    events: candidate events.
    ids: recorded tool_use_ids.
    starts: recorded starts by (session, tool or kind).

  Returns:
    The events to add.
  """
  keep = []
  for e in events:
    near = starts.get((e["session"], e.get("tool") or e["kind"]), [])
    if e.get("tool_use_id") in ids or any(abs(s - e["start"]) < 3 for s in near):
      continue
    keep.append(e)
  return keep


def write(events, out):
  """Append events to <out>/<YYYY-MM>.jsonl by the month of their end.

  Args:
    events: the events.
    out: the timings folder.

  Raises:
    OSError: when a file cannot be written.
  """
  out.mkdir(parents=True, exist_ok=True)
  by_month = defaultdict(list)
  for e in sorted(events, key=lambda e: e["end"]):
    by_month[dt.datetime.fromtimestamp(e["end"]).strftime("%Y-%m")].append(e)
  for month, es in by_month.items():
    with (out / f"{month}.jsonl").open("a") as f:
      f.writelines(json.dumps(e, separators=(",", ":")) + "\n" for e in es)


def day_start(text):
  """Epoch seconds of local midnight at the start of a day.

  Args:
    text: the day, YYYY-MM-DD.

  Returns:
    Seconds since the epoch.

  Raises:
    ValueError: when the text is not a date.
  """
  return dt.datetime.strptime(text, "%Y-%m-%d").timestamp()


def main(argv=None):
  """Plan or write the backfill.

  Args:
    argv: arguments; None uses sys.argv.

  Returns:
    0 done or planned; 2 bad arguments or no transcripts.
  """
  p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
  src = p.add_mutually_exclusive_group(required=True)
  src.add_argument("--project-dir")
  src.add_argument("--transcripts")
  p.add_argument("--from", dest="since", required=True, help="first local day, YYYY-MM-DD")
  p.add_argument("--to", dest="until", help="last local day, YYYY-MM-DD (default: --from)")
  p.add_argument("--out", required=True, help="the timing record's folder")
  p.add_argument("--min-wait", type=float, default=60)
  p.add_argument("--apply", action="store_true")
  a = p.parse_args(argv)
  folder = Path(a.transcripts) if a.transcripts else transcripts_for(a.project_dir)
  if not folder.is_dir():
    print(f"backfill: no transcripts at {folder}", file=sys.stderr)
    return 2
  window = (day_start(a.since), day_start(a.until or a.since) + 86400)
  events = []
  for f in sorted(folder.glob("*.jsonl")):
    events += events_of(f, f.stem, "", window, a.min_wait)
    for sub in sorted((folder / f.stem / "subagents").glob("*.jsonl")):
      events += events_of(sub, f.stem, sub.stem, window, a.min_wait)
  out = Path(a.out)
  ids, starts = existing(out)
  add = new_only(events, ids, starts)
  kinds = defaultdict(int)
  for e in add:
    kinds[e["kind"]] += 1
  print(f"backfill: {len(events)} events in {a.since}..{a.until or a.since} from {folder.name}; {len(add)} new {dict(kinds)}")
  if a.apply and add:
    write(add, out)
    print(f"backfill: wrote {len(add)} events to {out}")
  elif add:
    print("backfill: plan only; --apply writes")
  return 0


if __name__ == "__main__":
  raise SystemExit(main())
