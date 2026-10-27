"""Shared front-end plumbing: task-source arguments, JSON output and the error-to-exit-code mapping.

Imported, not run. Exit codes for every GoalGuard script: 0 success; 1 a GoalGuard failure (Vikunja, refused write); 2 bad input
(record, config, arguments); 3 a negative answer the caller must act on (BLOCK or REVIEW, invalid records, failed trace or verify).
"""

import argparse
import json
import sys
from collections.abc import Callable
from pathlib import Path

from . import settings as settings_mod
from . import tasks as tasks_mod
from .errors import ConfigError, GoalGuardError, RecordError
from .vikunja import Client

EXIT_OK, EXIT_FAIL, EXIT_INPUT, EXIT_NEGATIVE = 0, 1, 2, 3


def add_task_source(parser: argparse.ArgumentParser) -> None:
  """Add the mutually exclusive --tasks FILE / --vikunja options.

  Args:
    parser: the parser to extend.
  """
  group = parser.add_mutually_exclusive_group(required=True)
  group.add_argument("--tasks", type=Path, help="saved Vikunja tasks JSON or a GoalGuard snapshot tasks.json (offline, never live)")
  group.add_argument("--vikunja", action="store_true", help="read live from GG_VIKUNJA_URL with GG_VIKUNJA_TOKEN")


def load_tasks(args: argparse.Namespace, project_ids: list[int], cfg: settings_mod.Settings) -> tasks_mod.TaskSet:
  """Load tasks from the source the arguments name.

  Args:
    args: parsed arguments with tasks or vikunja.
    project_ids: Vikunja project IDs to read when live.
    cfg: settings.

  Returns:
    The TaskSet.

  Raises:
    ConfigError: live read requested for a project with no vikunja_project_id.
  """
  if args.tasks:
    return tasks_mod.from_file(args.tasks)
  if not all(project_ids):
    raise ConfigError("a project has no vikunja_project_id in .gg/project.yaml; link it before a live read")
  return tasks_mod.from_vikunja(Client(cfg), project_ids, cfg.vikunja_url)


def emit(result: object) -> None:
  """Print a result as indented JSON on stdout.

  Args:
    result: plain data.
  """
  print(json.dumps(result, indent=2, ensure_ascii=False, default=str))


def run(main: Callable[[], int]) -> None:
  """Run a front end's main, mapping GoalGuard errors to exit codes and one stderr line.

  Args:
    main: returns the exit code.

  Raises:
    SystemExit: always, with main's code or the mapped error code.
  """
  try:
    code = main()
  except (RecordError, ConfigError) as err:
    print(f"error: {err}", file=sys.stderr)
    code = EXIT_INPUT
  except GoalGuardError as err:
    print(f"error: {err}", file=sys.stderr)
    code = EXIT_FAIL
  sys.exit(code)
