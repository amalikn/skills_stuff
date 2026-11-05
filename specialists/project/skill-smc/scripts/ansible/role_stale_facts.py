"""List an Ansible role's facts that can carry over between two runs of the role in one ansible-playbook process.

A fact set only under a condition (a when, a loop, a rescue, or inside a guarded block or include) and read with `is defined` or `| default(`
keeps the first run's value in the second: host facts outlive an import_playbook, and Ansible cannot unset one (`meta: clear_facts` keeps
set_fact values). Each fact listed needs a reset at the run's start to a value its readers take for "not set". Read-only; reads files only.

Run: role_stale_facts.py <role dir> [--reset-file tasks/load_spec.yml]
  e.g. role_stale_facts.py /Volumes/Data/_ansible/local-knowledge-ansible/ansible-wifi/roles/smc_change --reset-file tasks/load_spec.yml
With --reset-file, facts already set (to anything) in that file are marked reset, so the list shows what is still unprotected.
Exit: 0 nothing unprotected; 1 facts listed without a reset; 2 bad usage.
Origin: smc_change, 2026-11-05: a second change in smc_change_multiple.yml skipped a host as done for the first (skill-smc reference 19).
"""

from __future__ import annotations

import argparse
import collections
import re
import sys
from pathlib import Path

import yaml

SETTERS = ("ansible.builtin.set_fact", "set_fact")
INCLUDES = ("ansible.builtin.include_tasks", "include_tasks", "ansible.builtin.import_tasks", "import_tasks")


def walk(tasks: list, name: str, guarded: bool, found: dict[str, dict[str, set]]) -> None:
  """Collect set_fact keys, marking those set under a condition.

  Args:
    tasks: a task list as loaded from YAML.
    name: the file it came from, for the report.
    guarded: True inside a guarded block, a rescue or a guarded include.
    found: {"cond": {key: files}, "plain": {key: files}}, filled in place.

  Returns:
    None.
  """
  for task in tasks or []:
    if not isinstance(task, dict):
      continue
    here = guarded or "when" in task or "loop" in task or "with_items" in task
    for part in ("block", "rescue", "always"):
      if part in task:
        walk(task[part], name, here or part == "rescue", found)
    setter = next((task[k] for k in SETTERS if k in task), None)
    if isinstance(setter, dict):
      for key in setter:
        if key != "cacheable":
          found["cond" if here else "plain"][key].add(name)


def guarded_includes(tasks: list, guarded: bool, out: set[str]) -> None:
  """Collect the task files included under a condition.

  Args:
    tasks: a task list as loaded from YAML.
    guarded: True inside a guarded block.
    out: file names (as written in the include), filled in place.

  Returns:
    None.
  """
  for task in tasks or []:
    if not isinstance(task, dict):
      continue
    here = guarded or "when" in task or "loop" in task
    for part in ("block", "rescue", "always"):
      if part in task:
        guarded_includes(task[part], here or part == "rescue", out)
    target = next((task[k] for k in INCLUDES if k in task), None)
    if isinstance(target, dict):
      target = target.get("file")
    if here and isinstance(target, str):
      out.add(Path(target.split("}}")[-1].strip("/ ")).name)


def scan(role: Path, reset_file: str | None) -> list[tuple[str, int, list[str], bool]]:
  """Find conditionally set facts that are read with `is defined` or `| default(`.

  Args:
    role: the role folder (with tasks/).
    reset_file: a task file, relative to the role, whose set_fact keys count as reset; or None.

  Returns:
    (fact, reads, files that set it, reset) for each fact found, sorted by name.

  Raises:
    yaml.YAMLError: a task file does not parse.
  """
  files = sorted((role / "tasks").rglob("*.yml"))
  docs = {f: yaml.safe_load(f.read_text()) for f in files}
  included: set[str] = set()
  for doc in docs.values():
    guarded_includes(doc if isinstance(doc, list) else [], False, included)
  found: dict[str, dict[str, set]] = {"cond": collections.defaultdict(set), "plain": collections.defaultdict(set)}
  for f, doc in docs.items():
    walk(doc if isinstance(doc, list) else [], str(f.relative_to(role / "tasks")), f.name in included, found)
  reset: set[str] = set()
  if reset_file:
    plain: dict[str, dict[str, set]] = {"cond": collections.defaultdict(set), "plain": collections.defaultdict(set)}
    walk(yaml.safe_load((role / reset_file).read_text()) or [], reset_file, False, plain)
    reset = set(plain["plain"]) | set(plain["cond"])
  source = "\n".join(f.read_text() for f in files + sorted((role / "templates").glob("*")) if f.is_file())
  out = []
  for key in sorted(set(found["cond"])):
    reads = len(re.findall(re.escape(key) + r"\s*(is (not )?defined|\|\s*default\()", source))
    if reads:
      out.append((key, reads, sorted(found["cond"][key] | found["plain"][key]), key in reset))
  return out


def main() -> int:
  """Print the report and return the exit status.

  Returns:
    0 nothing unprotected, 1 facts without a reset, 2 bad usage.
  """
  parser = argparse.ArgumentParser(description="Role facts that can carry over between two runs of the role in one process (read-only).")
  parser.add_argument("role", type=Path, help="the role folder")
  parser.add_argument("--reset-file", help="task file (relative to the role) that resets facts at the run's start")
  args = parser.parse_args()
  if not (args.role / "tasks").is_dir():
    print(f"no tasks/ under {args.role}", file=sys.stderr)
    return 2
  rows = scan(args.role, args.reset_file)
  for key, reads, where, is_reset in rows:
    print(f"{'reset' if is_reset else 'OPEN '}  {key:40} reads={reads:2}  set in {', '.join(where)}")
  open_rows = [r for r in rows if not r[3]]
  print(f"{len(rows)} conditionally set facts read with is defined/default; {len(open_rows)} without a reset")
  return 1 if open_rows else 0


if __name__ == "__main__":
  sys.exit(main())
