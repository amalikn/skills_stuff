#!/usr/bin/env python3
"""Report what GoalGuard really enforces for a project: records, baseline, hook wiring, captures, Vikunja (pilot feature 12).

Usage:
  python scripts/goal_guard_doctor.py --project examples/project_stuff/apn/demo-spoke
  python scripts/goal_guard_doctor.py --project <dir> --vikunja
  (or `just doctor <project>`)

Inputs:
  --project DIR   the project folder holding .gg/project.yaml
  --vikunja       also call GET /api/v2/info with GG_VIKUNJA_URL and GG_VIKUNJA_TOKEN
  Example: python scripts/goal_guard_doctor.py --project /Volumes/Data/_ai/_project/project_stuff/apn/unified-network-controller --vikunja

Safety: read-only. It reads records and settings files and never installs, edits or removes a hook. It reports a path as
"enforced" only with an observed block on record; everything else is reported as advisory (references/enforcement-and-hooks.md).

Exit codes: 0 no problems; 3 problems listed; 2 bad input.
"""

import argparse
from pathlib import Path

from goal_guard_lib import cli, doctor
from goal_guard_lib import settings as settings_mod


def main() -> int:
  """Build and print the report.

  Returns:
    0 with no problems, 3 otherwise.
  """
  parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
  parser.add_argument("--project", type=Path, required=True)
  parser.add_argument("--vikunja", action="store_true")
  args = parser.parse_args()
  result = doctor.report(args.project, settings_mod.load(), args.vikunja, Path.home())
  cli.emit(result)
  return cli.EXIT_OK if not result["problems"] else cli.EXIT_NEGATIVE


if __name__ == "__main__":
  cli.run(main)
