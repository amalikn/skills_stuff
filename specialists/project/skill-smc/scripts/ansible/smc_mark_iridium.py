#!/usr/bin/env python3
"""Mark SMCs as Iridium sites in an ansible-wifi checkout: add `smc_bases_iridium: true` to each host's host_vars.

The line goes directly after `site_eclipse_siteid:` (where the generator template puts it), or after the opening `---` when that key is
absent. A host already marked true is left alone; a host with any other `smc_bases_iridium` value, or no host_vars file, is refused.
Plan only unless `--apply` is given. Nothing else in the file is read into output, so no secret values are printed.

Run:
  smc_mark_iridium.py --repo /Volumes/Data/_ansible/ansible-wifi --flavor rct host-a,host-b [--apply]
  just smc_mark_iridium --repo <checkout> --flavor rct <hosts> [--apply]
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

LINE = "smc_bases_iridium: true\n"
KEY_RE = re.compile(r"^smc_bases_iridium:\s*(.*?)\s*$")
ANCHOR_RE = re.compile(r"^site_eclipse_siteid:")


def plan_host(path: Path) -> tuple[str, list[str] | None]:
  """Decide what to do with one host_vars file.

  Args:
    path: the host's host_vars YAML file.

  Returns:
    (status, new_lines): status is "add", "already", "missing" or "conflict: <value>"; new_lines is the file content to write for
    "add", otherwise None.
  """
  if not path.is_file():
    return "missing", None
  lines = path.read_text().splitlines(keepends=True)
  for line in lines:
    m = KEY_RE.match(line)
    if m:
      return ("already", None) if m.group(1) == "true" else (f"conflict: {m.group(1)!r}", None)
  idx = next((i + 1 for i, line in enumerate(lines) if ANCHOR_RE.match(line)), None)
  if idx is None:
    idx = 1 if lines and lines[0].strip() == "---" else 0
  return "add", lines[:idx] + [LINE] + lines[idx:]


def main(argv: list[str] | None = None) -> int:
  """Plan or apply the Iridium mark for the given hosts.

  Args:
    argv: command-line arguments (defaults to sys.argv[1:]).

  Returns:
    0 when every host is added or already marked; 1 when any host is missing or conflicting (nothing is written then).
  """
  ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
  ap.add_argument("--repo", required=True, type=Path, help="ansible-wifi checkout (any branch or worktree)")
  ap.add_argument("--flavor", required=True, help="inventory folder under inventories/, e.g. rct")
  ap.add_argument("hosts", nargs="+", help="host names, comma- or space-separated")
  ap.add_argument("--apply", action="store_true", help="write the files (default: plan only)")
  args = ap.parse_args(argv)

  hosts = [h for chunk in args.hosts for h in chunk.split(",") if h.strip()]
  base = args.repo / "inventories" / args.flavor / "host_vars"
  plans = {h: plan_host(base / f"{h.strip()}.yml") for h in hosts}
  bad = {h: s for h, (s, _) in plans.items() if s not in ("add", "already")}
  for h, (status, _) in plans.items():
    print(f"{h}: {status}")
  if bad:
    print(f"refused: {len(bad)} host(s) missing or conflicting; nothing written", file=sys.stderr)
    return 1
  todo: dict[str, list[str]] = {h: new for h, (s, new) in plans.items() if s == "add" and new is not None}
  if not args.apply:
    print(f"plan: {len(todo)} to add, {len(plans) - len(todo)} already marked (rerun with --apply)")
    return 0
  for h, new in todo.items():
    (base / f"{h.strip()}.yml").write_text("".join(new))
  print(f"applied: {len(todo)} added, {len(plans) - len(todo)} already marked")
  return 0


if __name__ == "__main__":
  sys.exit(main())
