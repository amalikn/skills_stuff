#!/usr/bin/env python3
"""Claude Code PreToolUse hook for Goal Guard, DRAFT: advisory by default; blocking only after a captured payload and an observed block.

Not run by hand: Claude Code runs it with the hook payload on stdin. Register it in the project's .claude/settings.json by merging
(never overwriting existing hooks); `goal_guard_doctor.py` reports whether it is wired. Example entry (timeout in seconds):

  {"hooks": {"PreToolUse": [{"matcher": "Edit|Write|MultiEdit|NotebookEdit", "hooks": [{"type": "command", "timeout": 10,
    "command": "/Volumes/Data/_ai/_skills/skills-working-cache/skill-goal-guard/.venv/bin/python
                /Volumes/Data/_ai/_skills/skills_stuff/specialists/project/skill-goal-guard/scripts/goal_guard_hook.py --capture"}]}]}}

Usage (testing by hand):
  echo '{"hook_event_name":"PreToolUse","tool_name":"Write","tool_input":{"file_path":"x"},"cwd":"."}' | python scripts/goal_guard_hook.py
  python scripts/goal_guard_hook.py --mode blocking < captured-payload.json
  (or `just hook-test <payload.json>`)

Inputs:
  stdin                       the hook payload (JSON)
  --mode advisory|blocking    advisory (default) never blocks; blocking exits 2 with the reason on stderr
  --capture                   save a redacted copy of each payload and decision under GG_RUNTIME_DIR/captures (the pilot's fixtures)
  GG_VERDICT_MAX_HOURS        how long a PROCEED verdict covers edits to its files (default 2)
  Example: python scripts/goal_guard_hook.py --mode advisory --capture < payload.json

Safety: reads the project's .gg/ records only. Its one write is the --capture fixture in the runtime peer, which never fails the
hook. Measured budget: well under the 10 s timeout above (see scripts/readme.md for the measured time); no network call is made.
"""

import argparse
import datetime as dt
import json
import sys

from goal_guard_lib import hook
from goal_guard_lib import settings as settings_mod
from goal_guard_lib.errors import ConfigError


def main() -> int:
  """Read the payload, decide, optionally capture, and answer Claude Code.

  Returns:
    0 (pass or advisory) or 2 (blocked).
  """
  parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
  parser.add_argument("--mode", choices=hook.MODES, default="advisory")
  parser.add_argument("--capture", action="store_true")
  args = parser.parse_args()
  now = dt.datetime.now().astimezone()
  text = sys.stdin.read()
  try:
    payload = json.loads(text)
  except json.JSONDecodeError:
    payload = text[:2000]
  try:
    cfg = settings_mod.load()
  except ConfigError as err:
    outcome = hook.deny(args.mode, f"settings error ({err}); failing closed")
    cfg = None
  else:
    try:
      outcome = hook.evaluate(payload, cfg, args.mode, now)
    except Exception as err:  # a bug here must not let a write through: exit 1 is a non-blocking error in Claude Code
      outcome = hook.deny(args.mode, f"internal error {type(err).__name__}: {err}; failing closed")
  if args.capture and cfg is not None:
    hook.capture(payload, outcome, cfg.runtime_dir / "captures", now)
  if outcome.stdout:
    print(outcome.stdout)
  if outcome.stderr:
    print(outcome.stderr, file=sys.stderr)
  return outcome.exit_code


if __name__ == "__main__":
  sys.exit(main())
