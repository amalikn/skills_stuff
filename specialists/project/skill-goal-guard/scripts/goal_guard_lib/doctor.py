"""Minimal doctor: report which Goal Guard paths are enforced and which are only advisory (pilot feature 12; GG-421, GG-423).

Imported, not run. Read-only: it reads .gg/ records, Claude Code settings files, file modes and the captures folder, and with
check_vikunja calls GET /info. It never writes, never installs a hook and never claims "enforced" without recorded evidence of an
observed block (project.yaml enforcement.observed_block_ref pointing at an existing file).

Settings files checked: .claude/settings.json and .claude/settings.local.json in the project folder and each ancestor up to the
git top level (the shared apn repository may start sessions at its root), plus the user's ~/.claude/settings.json.
"""

import json
import os
import subprocess
from pathlib import Path

from . import decisions_log, project, vikunja
from .errors import GoalGuardError
from .hook import WRITE_TOOLS
from .settings import Settings

HOOK_SCRIPT = "goal_guard_hook.py"


def _git_top(root: Path, timeout: float) -> Path:
  """Find the git top level above a folder.

  Args:
    root: the project folder.
    timeout: seconds for git.

  Returns:
    The top-level folder, or root itself when git fails or the folder is not in a repository.
  """
  try:
    run = subprocess.run(["git", "-C", str(root), "rev-parse", "--show-toplevel"], capture_output=True, text=True, timeout=timeout, check=False)
  except OSError, subprocess.TimeoutExpired:
    return root
  return Path(run.stdout.strip()).resolve() if run.returncode == 0 and run.stdout.strip() else root


def settings_files(root: Path, timeout: float, home: Path) -> list[Path]:
  """List the Claude Code settings files that can register a hook for sessions in this project.

  Args:
    root: the project folder (resolved).
    timeout: seconds for git.
    home: the user's home folder.

  Returns:
    Existing files, nearest first, then the user's settings.
  """
  top = _git_top(root, timeout)
  folders = [root] + [p for p in root.parents if p.is_relative_to(top)]
  found = [f for d in folders for f in (d / ".claude" / "settings.json", d / ".claude" / "settings.local.json") if f.is_file()]
  user = home / ".claude" / "settings.json"
  return found + ([user] if user.is_file() else [])


def hook_entries(path: Path) -> tuple[list[dict], str]:
  """Find Goal Guard PreToolUse entries in one settings file.

  Args:
    path: a settings JSON file.

  Returns:
    (entries, error): each {"file", "matcher", "mode", "tools", "command"}; error is "" or why the file could not be read.
  """
  try:
    data = json.loads(path.read_text(encoding="utf-8"))
  except (OSError, json.JSONDecodeError) as err:
    return [], f"{path}: unreadable ({err})"
  out = []
  for group in (data.get("hooks") or {}).get("PreToolUse") or []:
    matcher = str(group.get("matcher") or "")
    for h in group.get("hooks") or []:
      command = str(h.get("command") or "")
      if HOOK_SCRIPT not in command:
        continue
      names = set(matcher.split("|")) if matcher not in ("", "*") else set(WRITE_TOOLS)
      out.append(
        {
          "file": str(path),
          "matcher": matcher,
          "mode": "blocking" if "--mode blocking" in command else "advisory",
          "tools": sorted(set(WRITE_TOOLS) & names),
          "capture": "--capture" in command,
        }
      )
  return out, ""


def report(root: Path, cfg: Settings, check_vikunja: bool, home: Path) -> dict:
  """Build the doctor report for one project.

  Args:
    root: the project folder.
    cfg: settings.
    check_vikunja: also call Vikunja's /info.
    home: the user's home folder.

  Returns:
    {"project_id", "records", "baseline", "approval_signature", "hooks", "paths", "captures", "vikunja", "problems"}.
  """
  problems = []
  proj = project.load(root)
  entries, chain = decisions_log.read(proj.decisions_path)
  problems += chain
  state = project.baseline_state(proj, decisions_log.approvals(entries))
  if not state.approved:
    problems.append(f"baseline: {state.reason}")
  hooks, unreadable = wired_hooks(proj.root, cfg.git_timeout, home)
  problems += unreadable
  paths = path_statuses(proj, hooks)
  captures = cfg.runtime_dir / "captures"
  capture_count = len(list(captures.glob("*.json"))) if captures.is_dir() else 0
  vk = vikunja_status(cfg) if check_vikunja else {"checked": False}
  if vk.get("error"):
    problems.append(f"vikunja: {vk['error']}")
  return {
    "project_id": proj.project_id,
    "partition": proj.partition,
    "records": _records(proj, len(entries), not chain),
    "baseline": {"approved": state.approved, "code": state.code, "reason": state.reason},
    "approval_signature": project.verify_approval_commit(proj, cfg.git_timeout) if proj.mvp else "no contract",
    "hooks": hooks,
    "paths": paths,
    "captures": {"folder": str(captures), "count": capture_count, "needed": "at least one real payload per gated tool before trusting the adapter"},
    "vikunja": vk,
    "problems": problems,
  }


def wired_hooks(root: Path, timeout: float, home: Path) -> tuple[list[dict], list[str]]:
  """Collect Goal Guard hook entries from every settings file that applies to the project.

  Args:
    root: the project folder.
    timeout: seconds for git.
    home: the user's home folder.

  Returns:
    (hooks, unreadable): the entries found, and one message per settings file that could not be read.
  """
  hooks, unreadable = [], []
  for f in settings_files(root, timeout, home):
    found, err = hook_entries(f)
    hooks += found
    if err:
      unreadable.append(err)
  return hooks, unreadable


def _records(proj: project.Project, decisions: int, chain_ok: bool) -> dict:
  """Summarise the project's records.

  Args:
    proj: the project.
    decisions: number of decisions.jsonl entries.
    chain_ok: whether the hash chain holds.

  Returns:
    {"mvp", "mvp_issues", "decisions", "chain_ok"}.
  """
  issues = list(proj.mvp.issues) if proj.mvp else [proj.mvp_error or "absent"]
  return {"mvp": proj.mvp.revision if proj.mvp else None, "mvp_issues": issues, "decisions": decisions, "chain_ok": chain_ok}


def path_statuses(proj: project.Project, hooks: list[dict]) -> list[dict]:
  """Say, per write path, whether it is enforced, advisory or unsupported; enforced needs an observed block on record.

  Args:
    proj: the project.
    hooks: Goal Guard hook entries found in settings files.

  Returns:
    [{"path", "status"}] for each gated tool, shell writes and the protected records.
  """
  observed_ref = str((proj.config.get("enforcement") or {}).get("observed_block_ref") or "")
  observed = bool(observed_ref) and (proj.root / observed_ref).is_file()
  paths = []
  for tool in WRITE_TOOLS:
    wired = [h for h in hooks if tool in h["tools"]]
    if not wired:
      status = "advisory: no hook (rules and AGENTS.md only)"
    elif any(h["mode"] == "blocking" for h in wired):
      status = "enforced: blocking hook with an observed block on record" if observed else "blocking hook wired, block NOT yet observed: report as advisory"
    else:
      status = "advisory hook (warns, never blocks)"
    paths.append({"path": f"{tool} tool", "status": status})
  paths.append({"path": "Bash and other shell writes", "status": "unsupported: bypass file-edit hooks (enforcement-and-hooks.md, What hooks cannot do)"})
  writable = [str(p.relative_to(proj.root)) for p in proj.protected_paths() if p.is_file() and p.is_relative_to(proj.root) and os.access(p, os.W_OK)]
  status = f"writable by this user: {writable}; only the hook guards them" if writable else "read-only by file mode"
  paths.append({"path": "protected .gg/ records", "status": status})
  return paths


def vikunja_status(cfg: Settings) -> dict:
  """Call Vikunja's /info once.

  Args:
    cfg: settings.

  Returns:
    {"checked": True, "ok", "version"} or {"checked": True, "ok": False, "error", "token_set"}; the token itself is never included.
  """
  try:
    info = vikunja.Client(cfg).info()
  except GoalGuardError as err:
    return {"checked": True, "ok": False, "error": str(err), "token_set": bool(cfg.vikunja_token)}
  return {"checked": True, "ok": True, "version": info.get("version"), "token_set": True}
