#!/usr/bin/env python3
"""Read-only Vikunja reads for GoalGuard: instance info, one project's tasks, one task (pilot features 20-21).

Usage:
  python scripts/goal_guard_vikunja.py info
  python scripts/goal_guard_vikunja.py tasks --project-id 7 [--raw]
  python scripts/goal_guard_vikunja.py task --task-id 101
  (or `just vikunja-info`, `just vikunja-tasks 7`)

Inputs:
  GG_VIKUNJA_URL     base URL, e.g. http://localhost:3456
  GG_VIKUNJA_TOKEN   a read-only API token from the secret store (never on the command line, never printed)
  GG_HTTP_TIMEOUT    seconds per call (default 10)
  Example: GG_VIKUNJA_URL=http://localhost:3456 GG_VIKUNJA_TOKEN="$(kp ...)" python scripts/goal_guard_vikunja.py tasks --project-id 7

Safety: read-only; GET requests only, each with a timeout. `tasks --raw` prints Vikunja's objects as returned (save them with a
shell redirect to use as an offline --tasks file); without it the tasks are printed normalised, with the completeness record.
"""

import argparse
import dataclasses

from goal_guard_lib import cli, records, vikunja
from goal_guard_lib import settings as settings_mod


def main() -> int:
  """Parse arguments, call Vikunja and print JSON.

  Returns:
    0 on success; 3 when a task list is incomplete.
  """
  parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
  sub = parser.add_subparsers(dest="command", required=True)
  sub.add_parser("info", help="instance version and limits")
  p_tasks = sub.add_parser("tasks", help="every task of one project")
  p_tasks.add_argument("--project-id", type=int, required=True)
  p_tasks.add_argument("--raw", action="store_true", help="print Vikunja's objects unchanged (a PaginatedTask-shaped object)")
  p_task = sub.add_parser("task", help="one task with its relations")
  p_task.add_argument("--task-id", type=int, required=True)
  args = parser.parse_args()
  client = vikunja.Client(settings_mod.load())
  if args.command == "info":
    info = client.info()
    cli.emit({k: info.get(k) for k in ("version", "max_items_per_page", "webhooks_enabled", "frontend_url")})
    return cli.EXIT_OK
  if args.command == "task":
    cli.emit(dataclasses.asdict(records.parse_vikunja_task(client.task(args.task_id))))
    return cli.EXIT_OK
  raw, completeness = client.project_tasks(args.project_id)
  if args.raw:
    cli.emit({"items": raw, "total": completeness["total"], "page": 1, "total_pages": 1})
  else:
    cli.emit({"completeness": completeness, "tasks": [dataclasses.asdict(records.parse_vikunja_task(t)) for t in raw]})
  return cli.EXIT_OK if completeness["complete"] else cli.EXIT_NEGATIVE


if __name__ == "__main__":
  cli.run(main)
