#!/usr/bin/env python3
"""Trace management milestones: hub plan baseline -> MVP criterion -> target-map target -> Vikunja task (pilot step 7).

Usage:
  python scripts/goal_guard_trace.py --project examples/project_stuff/apn/demo-spoke --tasks examples/vikunja-tasks.json
  python scripts/goal_guard_trace.py --project <spoke dir> --vikunja [--milestone M1]
  (or `just trace`)

Inputs:
  --project DIR              the spoke folder whose .gg/mappings.yaml holds the milestone links
  --milestone ID             trace one milestone (default: all)
  --tasks FILE | --vikunja   task source
  Example: python scripts/goal_guard_trace.py --project examples/project_stuff/apn/demo-spoke --tasks examples/vikunja-tasks.json --milestone M1

Safety: read-only; reads files in place, runs `git cat-file -e` with a timeout for git:<commit> revisions, and reads Vikunja
with --vikunja. It never edits the hub, the target map, mappings.yaml or Vikunja: a mismatch is reported as REVIEW.

Exit codes: 0 every traced milestone verified; 3 any REVIEW or no milestone found; 2 bad input; 1 Vikunja failure.
"""

import argparse
from pathlib import Path

from goal_guard_lib import cli, project, trace
from goal_guard_lib import settings as settings_mod


def main() -> int:
  """Trace the requested milestones and print the results.

  Returns:
    0 when all are verified, 3 otherwise.
  """
  parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
  parser.add_argument("--project", type=Path, required=True)
  parser.add_argument("--milestone", help="milestone ID to trace (default: all)")
  cli.add_task_source(parser)
  args = parser.parse_args()
  cfg = settings_mod.load()
  proj = project.load(args.project)
  links = [m for m in proj.milestones if args.milestone in (None, str(m.get("milestone_id")))]
  tasks = cli.load_tasks(args, [proj.vikunja_project_id], cfg)
  results = [trace.trace_milestone(proj, link, tasks, cfg.git_timeout) for link in links]
  cli.emit({"project_id": proj.project_id, "tasks_source": tasks.source, "milestones": results})
  return cli.EXIT_OK if results and all(r["result"] == "verified" for r in results) else cli.EXIT_NEGATIVE


if __name__ == "__main__":
  cli.run(main)
