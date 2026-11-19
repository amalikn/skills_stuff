"""Estimate what a no-change re-run of a playbook costs on a slow link: tasks per role and the patterns that do work on every run.

Over Teleport and satellite each task that touches an SMC costs about 5-8 s whatever it does (smc_change check run on alkngarrija-smc01,
2026-10-26), so the task count and the always-working patterns decide how long a re-run of smc_bases takes. Reads role task files only
(never group_vars, host_vars or vaults); writes nothing.

Run: role_rerun_cost.py --repo <ansible-wifi> [--playbook smc_bases.yml ...] [--role <name> ...] [--json]
  e.g. role_rerun_cost.py --repo /Volumes/Data/_ansible/ansible-wifi --playbook smc_bases.yml --playbook smc_prometheus.yml
Counts: tasks (named tasks in roles/<role>/tasks/*.yml, comments skipped; files included from elsewhere are not counted), per-item package
loops (one apt call per item), update_cache without cache_valid_time, get_url without checksum, command/shell/expect and their creates:
guards, git checkouts, state: absent (a delete before a re-create, e.g. a repo wiped then cloned).
Exit: 0 report printed; 2 bad usage or a role folder missing.
Origin: smc_bases converge-and-skip plan, 2026-11-19 (local-knowledge-ansible plans/smc-bases-converge-skip-plan-20261119_1808.md).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

PATTERNS = {
  "update_cache": re.compile(r"^\s*update_cache:\s*(yes|true|True)\b", re.M),
  "cache_valid_time": re.compile(r"^\s*cache_valid_time:", re.M),
  "get_url": re.compile(r"^\s*(ansible\.builtin\.)?get_url:", re.M),
  "checksum": re.compile(r"^\s*checksum:", re.M),
  "cmd_shell": re.compile(r"^\s*(ansible\.builtin\.)?(command|shell|expect):", re.M),
  "creates": re.compile(r"^\s*creates:", re.M),
  "git": re.compile(r"^\s*(ansible\.builtin\.)?git:", re.M),
  "absent": re.compile(r"^\s*state:\s*absent\b", re.M),
}
TASK = re.compile(r"^\s*- name:", re.M)
TASK_BLOCK = re.compile(r"^\s*- name:.*?(?=^\s*- name:|\Z)", re.M | re.S)
PKG = re.compile(r"^\s+(ansible\.builtin\.)?(package|apt|dnf|yum):", re.M)
LOOP = re.compile(r"^\s+(loop|with_items):", re.M)
COLUMNS = ["tasks", "pkg_loops", *PATTERNS]


def strip_comments(text: str) -> str:
  """Drop whole-line comments so commented-out tasks are not counted.

  Args:
    text: YAML file content.

  Returns:
    The text without lines whose first non-blank character is '#'.

  Raises:
    Nothing.
  """
  return "\n".join(line for line in text.splitlines() if not line.lstrip().startswith("#"))


def scan_text(text: str) -> dict[str, int]:
  """Count tasks and re-run-cost patterns in one task file's text.

  Args:
    text: task file content.

  Returns:
    Mapping of column name to count.

  Raises:
    Nothing.
  """
  body = strip_comments(text)
  counts = {"tasks": len(TASK.findall(body)), "pkg_loops": 0}
  for key, rx in PATTERNS.items():
    counts[key] = len(rx.findall(body))
  for block in TASK_BLOCK.findall(body):
    if PKG.search(block) and LOOP.search(block) and "{{ item }}" in block:
      counts["pkg_loops"] += 1
  return counts


def scan_role(role_dir: Path) -> dict[str, int]:
  """Sum the counts over a role's tasks/*.yml.

  Args:
    role_dir: path to roles/<role>.

  Returns:
    Mapping of column name to count.

  Raises:
    FileNotFoundError: when the role has no tasks folder.
  """
  tasks_dir = role_dir / "tasks"
  if not tasks_dir.is_dir():
    raise FileNotFoundError(f"no tasks folder: {tasks_dir}")
  total = dict.fromkeys(COLUMNS, 0)
  for path in sorted(tasks_dir.glob("*.yml")):
    for key, value in scan_text(path.read_text(encoding="utf-8")).items():
      total[key] += value
  return total


def roles_in_playbook(text: str) -> list[str]:
  """List the roles a playbook names under `roles:`, in order, without duplicates.

  Args:
    text: playbook content.

  Returns:
    Role names in first-seen order.

  Raises:
    Nothing.
  """
  names: list[str] = []
  in_roles, indent = False, 0
  for line in strip_comments(text).splitlines():
    stripped = line.strip()
    if re.match(r"^roles:\s*$", stripped):
      in_roles, indent = True, len(line) - len(line.lstrip())
      continue
    if in_roles and stripped and (len(line) - len(line.lstrip())) <= indent and not stripped.startswith("-"):
      in_roles = False
    if in_roles:
      match = re.match(r"^-\s*(?:role:\s*)?([A-Za-z0-9_.-]+)\s*$", stripped) or re.match(r"^-\s*role:\s*([A-Za-z0-9_.-]+)", stripped)
      if match and match.group(1) not in names:
        names.append(match.group(1))
  return names


def main(argv: list[str] | None = None) -> int:
  """Print one row per role and a total.

  Args:
    argv: command-line arguments (default sys.argv[1:]).

  Returns:
    Exit code: 0 printed, 2 bad usage or missing role.

  Raises:
    Nothing; errors are printed and mapped to exit 2.
  """
  parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
  parser.add_argument("--repo", required=True, type=Path)
  parser.add_argument("--playbook", action="append", default=[])
  parser.add_argument("--role", action="append", default=[])
  parser.add_argument("--json", action="store_true")
  args = parser.parse_args(argv)
  roles = list(args.role)
  for playbook in args.playbook:
    path = args.repo / playbook
    if not path.is_file():
      print(f"no such playbook: {path}", file=sys.stderr)
      return 2
    roles += [r for r in roles_in_playbook(path.read_text(encoding="utf-8")) if r not in roles]
  if not roles:
    print("give --playbook or --role", file=sys.stderr)
    return 2
  rows = {}
  for role in roles:
    try:
      rows[role] = scan_role(args.repo / "roles" / role)
    except FileNotFoundError as err:
      print(err, file=sys.stderr)
      return 2
  total = {c: sum(r[c] for r in rows.values()) for c in COLUMNS}
  if args.json:
    print(json.dumps({"roles": rows, "total": total}, indent=2))
    return 0
  print("role".ljust(28) + "".join(c[:10].rjust(11) for c in COLUMNS))
  for role, row in rows.items():
    print(role.ljust(28) + "".join(str(row[c]).rjust(11) for c in COLUMNS))
  print("TOTAL".ljust(28) + "".join(str(total[c]).rjust(11) for c in COLUMNS))
  return 0


if __name__ == "__main__":
  sys.exit(main())
