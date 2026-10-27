#!/usr/bin/env python3
"""Snapshot one project's Vikunja tasks, verify a snapshot, and restore it into a clean test instance (pilot step 8).

Usage:
  python scripts/goal_guard_snapshot.py export --project <dir> --vikunja [--out DIR] [--apply]
  python scripts/goal_guard_snapshot.py export --project <dir> --raw-tasks saved.json [--out DIR] [--apply]
  python scripts/goal_guard_snapshot.py verify --snapshot <out>/<partition>/<project_id>
  python scripts/goal_guard_snapshot.py restore --snapshot <dir> --target-project-id 3 [--apply]
  (or `just snapshot-export`, `just snapshot-verify`, `just snapshot-restore`)

Inputs:
  --project DIR            the project folder (.gg/project.yaml names its partition and Vikunja project)
  --vikunja | --raw-tasks  read live, or from raw Vikunja JSON saved by `goal_guard_vikunja.py tasks --raw`
  --out DIR                snapshot root (default GG_DATA_DIR/snapshots, the data peer: payloads stay out of repositories)
  --target-project-id N    an EMPTY project on the test instance named by GG_VIKUNJA_URL (restore)
  Example: python scripts/goal_guard_snapshot.py export --project examples/project_stuff/apn/demo-spoke \
             --raw-tasks examples/vikunja-tasks.json --out /tmp/gg-snapshots

Safety: export and restore print their plan and write only with --apply. export writes atomically and refuses a partial read;
verify writes nothing. restore checks the snapshot first, refuses a target project holding tasks Goal Guard did not restore, creates
tasks and relations through the Vikunja seam, and reads everything back. Point GG_VIKUNJA_URL at a TEST instance for restore:
restoring into the live instance needs conflict handling that is not built (references/snapshot-and-restore.md, Restore step 3).

Exit codes: 0 done or plan printed; 3 verification failed or restore read-back mismatched; 2 bad input; 1 Vikunja or refused write.
"""

import argparse
from pathlib import Path

from goal_guard_lib import cli, project, restore, snapshot, vikunja, yaml_io
from goal_guard_lib import settings as settings_mod
from goal_guard_lib.errors import RecordError


def _raw_tasks(args: argparse.Namespace, proj: project.Project, cfg: settings_mod.Settings) -> tuple[list[dict], dict, dict]:
  """Read the raw tasks to export.

  Args:
    args: parsed arguments.
    proj: the project.
    cfg: settings.

  Returns:
    (tasks, completeness, source).

  Raises:
    RecordError: the raw file holds no task list.
  """
  if args.raw_tasks:
    data = yaml_io.load_file(args.raw_tasks)
    items = data.get("items") if isinstance(data, dict) else data
    if not isinstance(items, list):
      raise RecordError(f"{args.raw_tasks}: expected raw Vikunja tasks")
    own = [t for t in items if int(t.get("project_id") or 0) == proj.vikunja_project_id]
    total = data.get("total") if isinstance(data, dict) else None
    complete = total is None or total == len(items)
    return own, {"total": len(own), "fetched": len(own), "complete": complete}, {"instance": f"file:{args.raw_tasks}", "version": "unknown"}
  client = vikunja.Client(cfg)
  version = str(client.info().get("version", "unknown"))
  items, completeness = client.project_tasks(proj.vikunja_project_id)
  return items, completeness, {"instance": cfg.vikunja_url, "version": version}


def main() -> int:
  """Dispatch export, verify or restore.

  Returns:
    The exit code.
  """
  parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
  sub = parser.add_subparsers(dest="command", required=True)
  p_exp = sub.add_parser("export")
  p_exp.add_argument("--project", type=Path, required=True)
  src = p_exp.add_mutually_exclusive_group(required=True)
  src.add_argument("--vikunja", action="store_true")
  src.add_argument("--raw-tasks", type=Path)
  p_exp.add_argument("--out", type=Path)
  p_exp.add_argument("--apply", action="store_true")
  p_ver = sub.add_parser("verify")
  p_ver.add_argument("--snapshot", type=Path, required=True)
  p_res = sub.add_parser("restore")
  p_res.add_argument("--snapshot", type=Path, required=True)
  p_res.add_argument("--target-project-id", type=int, required=True)
  p_res.add_argument("--apply", action="store_true")
  args = parser.parse_args()
  cfg = settings_mod.load()
  if args.command == "export":
    proj = project.load(args.project)
    items, completeness, source = _raw_tasks(args, proj, cfg)
    cli.emit(snapshot.export(proj, items, completeness, source, args.out or cfg.data_dir / "snapshots", args.apply))
    return cli.EXIT_OK
  if args.command == "verify":
    result = snapshot.verify(args.snapshot)
    parent = (
      snapshot.verify_parent(args.snapshot.parent) if (args.snapshot.parent / "manifest.json").exists() else {"ok": False, "issues": ["no parent manifest"]}
    )
    result.pop("tasks", None)
    cli.emit({**result, "parent": parent})
    return cli.EXIT_OK if result["ok"] and parent["ok"] else cli.EXIT_NEGATIVE
  result = restore.restore(args.snapshot, vikunja.Client(cfg), args.target_project_id, args.apply)
  cli.emit(result)
  return cli.EXIT_OK if not result["applied"] or result["verify"]["ok"] else cli.EXIT_NEGATIVE


if __name__ == "__main__":
  cli.run(main)
