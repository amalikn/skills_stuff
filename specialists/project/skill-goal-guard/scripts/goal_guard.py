#!/usr/bin/env python3
"""Goal Guard scope gate and What's Next: validate a project's records, assess a proposal, rank the next action.

Pilot step 4 rewrite of the v0.1 prototype (kept in git history, commit 1dff9c8): adds the MVP baseline, the BLOCK verdict, the
decision order of references/decision-rules.md and the ranking pipeline of references/whats-next-and-portfolio.md, and reads
tasks from Vikunja (or a saved file) instead of a local portfolio JSON.

Usage:
  python scripts/goal_guard.py validate --project examples/project_stuff/apn/demo-spoke
  python scripts/goal_guard.py assess --project <dir> --proposal <file> --tasks <tasks.json> [--apply]
  python scripts/goal_guard.py next --project <dir> [--project <dir> ...] --vikunja [--date 2026-10-27] [--focus 101] [--task 101]
  (or `just validate`, `just assess`, `just next`)

Inputs:
  --project DIR              a folder holding .gg/project.yaml (repeat for the portfolio; one partition only)
  --proposal FILE            proposal record, YAML or JSON (assess)
  --tasks FILE | --vikunja   offline task file, or a live read with GG_VIKUNJA_URL / GG_VIKUNJA_TOKEN
  GG_PARTITION               the partition this session may act in (apn or me)
  Example: GG_PARTITION=apn python scripts/goal_guard.py assess --project examples/project_stuff/apn/demo-spoke \
             --proposal examples/proposals/proceed.yaml --tasks examples/vikunja-tasks.json

Safety: read-only by default. `assess --apply` appends one line (kind verdict, or park for a PARK) to the project's
.gg/decisions.jsonl through decisions_log.append, the only writer; without --apply it prints the line it would append. It never
writes an approval, never edits Vikunja and never changes the MVP contract.

Exit codes: 0 PROCEED / valid / ranked; 3 PARK, REVIEW, BLOCK or invalid records; 2 bad input; 1 Vikunja or write failure.
"""

import argparse
import datetime as dt
from pathlib import Path

from goal_guard_lib import cli, decide, decisions_log, project, rank, records, yaml_io
from goal_guard_lib import settings as settings_mod


def validate(root: Path) -> dict:
  """Validate one project's records.

  Args:
    root: the project folder.

  Returns:
    {"project_id", "valid", "baseline", "issues"}; valid is False when the MVP has issues or the decision chain is broken.
  """
  proj = project.load(root)
  entries, chain = decisions_log.read(proj.decisions_path)
  state = project.baseline_state(proj, decisions_log.approvals(entries))
  issues = list(chain) + ([proj.mvp_error] if proj.mvp_error else []) + list(proj.mvp.issues if proj.mvp else [])
  if proj.mvp:
    unknown = sorted({c for crits in proj.task_map.values() for c in crits} - proj.mvp.criterion_ids())
    issues += [f"mappings.yaml maps a task to unknown criterion {c}" for c in unknown]
  return {
    "project_id": proj.project_id,
    "partition": proj.partition,
    "valid": not issues,
    "baseline": {"approved": state.approved, "code": state.code, "clause": state.clause, "reason": state.reason},
    "issues": issues,
  }


def cmd_validate(args: argparse.Namespace, cfg: settings_mod.Settings) -> int:
  """Run validate for each --project.

  Args:
    args: parsed arguments.
    cfg: settings (unused; kept for one handler signature).

  Returns:
    0 when every project is valid, 3 otherwise.
  """
  results = [validate(p) for p in args.project]
  cli.emit(results if len(results) > 1 else results[0])
  return cli.EXIT_OK if all(r["valid"] for r in results) else cli.EXIT_NEGATIVE


def cmd_assess(args: argparse.Namespace, cfg: settings_mod.Settings) -> int:
  """Assess one proposal and, with --apply, record the verdict.

  Args:
    args: parsed arguments (one --project, --proposal, a task source, --apply).
    cfg: settings.

  Returns:
    0 for PROCEED, 3 for PARK, REVIEW or BLOCK.

  Raises:
    ConfigError: more than one --project given.
  """
  if len(args.project) != 1:
    raise settings_mod.ConfigError("assess takes exactly one --project")
  proj = project.load(args.project[0])
  entries, _ = decisions_log.read(proj.decisions_path)
  state = project.baseline_state(proj, decisions_log.approvals(entries))
  proposal = records.parse_proposal(yaml_io.load_file(args.proposal))
  tasks = cli.load_tasks(args, [proj.vikunja_project_id], cfg)
  verdict = decide.assess(proposal, proj, state, tasks, cfg.partition, dt.datetime.now().astimezone())
  kind = "park" if verdict.verdict == "PARK" else "verdict"
  payload = verdict.to_dict()
  if kind == "park":
    payload["idea"] = {"title": proposal.description, "why_not_now": verdict.reason, "source_ref": list(proposal.evidence_refs)}
  record = decisions_log.append(
    proj.decisions_path, kind, proposal.proposer or "agent", verdict.contract_revision, verdict.reason, list(proposal.evidence_refs), payload, apply=args.apply
  )
  cli.emit({"verdict": verdict.to_dict(), "tasks_source": tasks.source, "record": record})
  return cli.EXIT_OK if verdict.verdict == "PROCEED" else cli.EXIT_NEGATIVE


def cmd_next(args: argparse.Namespace, cfg: settings_mod.Settings) -> int:
  """Rank task, project and portfolio next actions.

  Args:
    args: parsed arguments (--project ..., a task source, --date, --focus, --task).
    cfg: settings.

  Returns:
    0 always when ranking ran (a BLOCKED portfolio is an answer, reported in the output).
  """
  projects = [project.load(p) for p in args.project]
  baselines = {}
  for proj in projects:
    entries, _ = decisions_log.read(proj.decisions_path)
    baselines[proj.project_id] = project.baseline_state(proj, decisions_log.approvals(entries))
  tasks = cli.load_tasks(args, [p.vikunja_project_id for p in projects], cfg)
  today = records.parse_date(args.date, "--date") if args.date else dt.date.today()
  cli.emit(rank.whats_next(projects, baselines, tasks, today, cfg.deadline_days, args.focus, args.task))
  return cli.EXIT_OK


def main() -> int:
  """Parse arguments and dispatch.

  Returns:
    The exit code of the chosen command.
  """
  parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
  sub = parser.add_subparsers(dest="command", required=True)
  p_val = sub.add_parser("validate", help="validate .gg/ records and the baseline")
  p_val.add_argument("--project", type=Path, action="append", required=True)
  p_ass = sub.add_parser("assess", help="decide a proposal")
  p_ass.add_argument("--project", type=Path, action="append", required=True)
  p_ass.add_argument("--proposal", type=Path, required=True)
  p_ass.add_argument("--apply", action="store_true", help="append the verdict to .gg/decisions.jsonl")
  cli.add_task_source(p_ass)
  p_next = sub.add_parser("next", help="task, project and portfolio next actions")
  p_next.add_argument("--project", type=Path, action="append", required=True)
  p_next.add_argument("--date", help="rank for this date (YYYY-MM-DD); default today")
  p_next.add_argument("--focus", type=int, help="the owner's selected task ID (owner first)")
  p_next.add_argument("--task", type=int, help="also answer for this task")
  cli.add_task_source(p_next)
  args = parser.parse_args()
  cfg = settings_mod.load()
  handlers = {"validate": cmd_validate, "assess": cmd_assess, "next": cmd_next}
  return handlers[args.command](args, cfg)


if __name__ == "__main__":
  cli.run(main)
