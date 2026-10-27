"""Claude Code PreToolUse adapter, DRAFT (pilot step 6; references/enforcement-and-hooks.md). Pure decision plus an optional capture.

Imported, not run. Status: built from the Claude Code hooks reference (https://code.claude.com/docs/en/hooks, read 2026-10-27 for
Claude Code 2.1.310): input arrives on stdin with session_id, transcript_path, cwd, permission_mode, hook_event_name, tool_name,
tool_input (Write: file_path, content); exit 2 blocks the tool call and stderr is the reason; on exit 0, stdout JSON may carry
hookSpecificOutput.{hookEventName, permissionDecision, permissionDecisionReason, additionalContext}. VERIFIED_PRIMARY for those
facts from the page; UNVERIFIED on this machine until --capture records real payloads and one blocked action is observed. Edit,
MultiEdit and NotebookEdit field names (file_path, notebook_path) are from the Claude Code tool schemas, not the hooks page.

What it gates (Edit, Write, MultiEdit, NotebookEdit on a file inside a .gg/-registered project):
  1. a protected record (.gg/mvp.yaml, decisions.jsonl, internal targets, project.yaml, protected_paths) -> deny (MVP-007, MVP-011)
  2. no approved baseline -> deny (MVP-001)
  3. no PROCEED verdict in decisions.jsonl within GG_VERDICT_MAX_HOURS, or one against another contract revision -> deny: run assess
  4. a file not in that verdict's proposed_files -> deny: one PROCEED covers the files its proposal named, not the whole project
A file outside every registered project is not governed. Bash and other tools are not gated: shell writes bypass file-edit hooks,
and doctor reports that path as unsupported. On pass the hook prints nothing: printing "allow" would skip the user's permission prompt.

Modes: advisory (default) never blocks; it adds the would-be denial as additionalContext. blocking exits 2. A payload the hook does
not recognise is denied in blocking mode and warned in advisory mode: an adapter that guesses wrong must not let writes through silently.
"""

import datetime as dt
import json
import uuid
from dataclasses import dataclass
from pathlib import Path

from . import decisions_log, project
from .errors import GoalGuardError
from .settings import Settings

WRITE_TOOLS = {"Write": "file_path", "Edit": "file_path", "MultiEdit": "file_path", "NotebookEdit": "notebook_path"}
MODES = ("advisory", "blocking")


@dataclass(frozen=True)
class Outcome:
  """What the hook process does.

  Args:
    exit_code: 0 or 2.
    stdout: JSON text for stdout, or "".
    stderr: the block reason (exit 2), or "".
    decision: allow, deny, warn or ignore, for captures and tests.
    reason: the rule that decided.
  """

  exit_code: int
  stdout: str
  stderr: str
  decision: str
  reason: str


def deny(mode: str, reason: str) -> Outcome:
  """Turn a denial into the mode's outcome.

  Args:
    mode: advisory or blocking.
    reason: why Goal Guard would block.

  Returns:
    Exit 2 with stderr in blocking mode; exit 0 with additionalContext in advisory mode.
  """
  text = f"Goal Guard: {reason}"
  if mode == "blocking":
    return Outcome(2, "", text, "deny", reason)
  context = {"hookSpecificOutput": {"hookEventName": "PreToolUse", "additionalContext": f"{text} (advisory mode: not blocked; stop and run assess)"}}
  return Outcome(0, json.dumps(context), "", "warn", reason)


def _allow(reason: str) -> Outcome:
  """Pass silently.

  Args:
    reason: why the call passes.

  Returns:
    Exit 0 with no output.
  """
  return Outcome(0, "", "", "allow", reason)


def evaluate(payload: object, cfg: Settings, mode: str, now: dt.datetime) -> Outcome:
  """Decide one PreToolUse call.

  Args:
    payload: the parsed stdin JSON (anything; it is checked here).
    cfg: settings (verdict age limit).
    mode: advisory or blocking.
    now: the current time (timezone-aware).

  Returns:
    The Outcome.
  """
  if not isinstance(payload, dict) or not isinstance(payload.get("tool_name"), str) or "hook_event_name" not in payload:
    return deny(mode, "unrecognised hook payload (no hook_event_name or tool_name); failing closed for writes")
  if payload["hook_event_name"] != "PreToolUse":
    return Outcome(0, "", "", "ignore", f"event {payload['hook_event_name']} is not gated")
  tool = payload["tool_name"]
  if tool not in WRITE_TOOLS:
    return Outcome(0, "", "", "ignore", f"tool {tool} is not gated")
  tool_input = payload.get("tool_input")
  raw = tool_input.get(WRITE_TOOLS[tool]) if isinstance(tool_input, dict) else None
  if not isinstance(raw, str) or not raw:
    return deny(mode, f"unrecognised {tool} input (no {WRITE_TOOLS[tool]}); failing closed")
  cwd = Path(str(payload.get("cwd") or "."))
  target = Path(raw) if Path(raw).is_absolute() else cwd / raw
  resolved = target.resolve()
  root = project.find_root(target)
  # The session's own project can protect files outside it (a hub plan in protected_paths), so check both projects' lists.
  session_root = project.find_root(cwd)
  for candidate in dict.fromkeys(r for r in (root, session_root) if r is not None):
    try:
      guard = project.load(candidate)
    except GoalGuardError as err:
      return deny(mode, f"cannot read the Goal Guard records of {candidate.name} ({err}); failing closed")
    if resolved in guard.protected_paths():
      shown = resolved.relative_to(candidate) if resolved.is_relative_to(candidate) else resolved
      return deny(mode, f"{shown} is protected by {guard.project_id}; changes go through the owner's change request (MVP-011)")
  if root is None:
    return _allow("outside every Goal Guard project")
  reason = _verdict_gap(project.load(root), resolved, cfg, now)
  return deny(mode, reason) if reason else _allow(f"a current PROCEED covers {resolved.relative_to(root)}")


def _verdict_gap(proj: project.Project, resolved: Path, cfg: Settings, now: dt.datetime) -> str:
  """Check that an approved baseline and a current PROCEED verdict cover this file.

  Args:
    proj: the project the file is in.
    resolved: the resolved target file.
    cfg: settings (verdict age limit).
    now: the current time.

  Returns:
    "" when the write is covered, otherwise the reason it is not.
  """
  entries, chain = decisions_log.read(proj.decisions_path)
  if chain:
    return f"decisions.jsonl chain is broken ({chain[0]}); the owner repairs it"
  state = project.baseline_state(proj, decisions_log.approvals(entries))
  if not state.approved:
    return f"{state.reason} ({state.clause})"
  last = decisions_log.latest_verdict(entries)
  verdict = (last or {}).get("payload", {})
  if not last or verdict.get("verdict") != "PROCEED":
    return f"no PROCEED verdict on record for {proj.project_id}; write a proposal and run goal_guard.py assess --apply"
  try:
    age = now - dt.datetime.fromisoformat(str(last.get("at")))
  except ValueError:
    return "the last verdict has no readable time; run assess again"
  if age > dt.timedelta(hours=cfg.verdict_max_hours):
    return f"the last PROCEED verdict is {age.total_seconds() / 3600:.1f} h old (limit {cfg.verdict_max_hours:g} h); assess again"
  if verdict.get("contract_revision") != (proj.mvp.revision if proj.mvp else None):
    return "the last PROCEED verdict was against another contract revision; assess again"
  files = (verdict.get("details") or {}).get("proposed_files") or []
  if resolved not in {(proj.root / f).resolve() for f in files}:
    shown = resolved.relative_to(proj.root)
    return f"{shown} is not in the files of PROCEED {verdict.get('proposal_id')} ({files or 'none listed'}); assess a proposal that lists it"
  return ""


def _redact(value: object) -> object:
  """Shorten long strings in a payload before it is captured (file contents, edits).

  Args:
    value: payload data.

  Returns:
    The same structure with strings over 200 characters replaced by "<N chars>".
  """
  if isinstance(value, dict):
    return {k: _redact(v) for k, v in value.items()}
  if isinstance(value, list):
    return [_redact(v) for v in value]
  if isinstance(value, str) and len(value) > 200:
    return f"<{len(value)} chars>"
  return value


def capture(payload: object, outcome: Outcome, folder: Path, now: dt.datetime) -> Path | None:
  """Save a redacted payload and the outcome as a fixture (the --capture write gate); never raises.

  Args:
    payload: the parsed stdin, or the raw text when it did not parse.
    outcome: what the hook decided.
    folder: captures folder in the runtime peer.
    now: capture time.

  Returns:
    The file written, or None when writing failed (the hook must still answer).
  """
  tool = payload.get("tool_name", "unknown") if isinstance(payload, dict) else "unparsed"
  path = folder / f"{now.strftime('%Y%m%d_%H%M%S')}-{tool}-{uuid.uuid4().hex[:6]}.json"
  record = {
    "captured_at": now.isoformat(timespec="seconds"),
    "payload": _redact(payload),
    "decision": outcome.decision,
    "reason": outcome.reason,
    "exit_code": outcome.exit_code,
  }
  try:
    folder.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
  except OSError:
    return None
  return path
