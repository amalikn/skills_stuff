#!/usr/bin/env python3
"""Report whether ansible-wifi commits have reached the deploy branch, whether each would cherry-pick clean, and who is in an inventory group.

Run it through just: just ansible_change_reach <commit> [<commit> ...]   (recipe sets --repo and --base)
  or directly: ansible_change_reach.py --repo <ansible-wifi> --base rise [--inventory inventories/rcp/prod --group smc_ltp] <commit> ...
Read-only: git rev-parse/branch/merge-base/merge-tree and ansible-inventory --graph; nothing is checked out, fetched or written. The group
graph is read from the working tree, so it is shown only when HEAD is the base branch and the inventory path has no local changes.
Exit 0 when every commit is on the base branch, 1 when one is not (or is unknown), 2 on bad usage.
Written 2026-10-27 after a tracker review found an inventory fix committed in August but present only on side branches.
"""

import argparse
import os
import re
import subprocess
import sys

GIT_TIMEOUT = 60
INVENTORY_TIMEOUT = 120


def run(args, cwd, timeout=GIT_TIMEOUT):
  """Run a command and capture its output.

  Args:
    args: the command as an argument list.
    cwd: the directory to run it in.
    timeout: seconds before the command is killed.

  Returns:
    (exit code, stdout, stderr); exit code 124 when it timed out.
  """
  try:
    done = subprocess.run(args, cwd=cwd, capture_output=True, text=True, timeout=timeout, check=False)
  except subprocess.TimeoutExpired:
    return 124, "", f"timed out after {timeout}s: {' '.join(args)}"
  return done.returncode, done.stdout, done.stderr


def is_ancestor(repo, commit, ref):
  """Say whether a commit is reachable from a ref.

  Args:
    repo: the git working tree.
    commit: the commit to look for.
    ref: the branch or ref to search.

  Returns:
    True when reachable, False when not, None when the ref does not exist.
  """
  if run(["git", "rev-parse", "--verify", "--quiet", ref], repo)[0] != 0:
    return None
  return run(["git", "merge-base", "--is-ancestor", commit, ref], repo)[0] == 0


def cherry_pick_state(repo, commit, base):
  """Simulate cherry-picking a commit onto a branch without touching the working tree.

  Args:
    repo: the git working tree.
    commit: the commit to apply.
    base: the branch it would land on.

  Returns:
    "clean", "conflict", or "unknown: <reason>" (git older than 2.40 has no --merge-base on merge-tree).
  """
  code, _out, err = run(["git", "merge-tree", "--write-tree", "--merge-base", f"{commit}^", base, commit], repo)
  if code == 0:
    return "clean"
  if code == 1:
    return "conflict"
  return f"unknown: {err.strip().splitlines()[0] if err.strip() else f'exit {code}'}"


def reach(repo, commit, base):
  """Collect where one commit is and whether it has reached the base branch.

  Args:
    repo: the git working tree.
    commit: the commit, short or full hash, or any revision.
    base: the deploy branch name, e.g. rise.

  Returns:
    A dict with commit, found, subject, date, branches, on_base, on_origin_base and cherry_pick.
  """
  code, out, _err = run(["git", "show", "-s", "--format=%h%x09%cs%x09%s", f"{commit}^{{commit}}"], repo)
  if code != 0:
    return {"commit": commit, "found": False}
  short, date, subject = out.strip().split("\t", 2)
  _c, branches, _e = run(["git", "branch", "-a", "--format=%(refname:short)", "--contains", commit], repo)
  on_base = is_ancestor(repo, commit, base)
  info = {
    "commit": short, "found": True, "subject": subject, "date": date,
    "branches": [b for b in branches.split() if b and not b.endswith("/HEAD")],
    "on_base": on_base, "on_origin_base": is_ancestor(repo, commit, f"origin/{base}"),
  }
  info["cherry_pick"] = "already on base" if on_base else cherry_pick_state(repo, commit, base)
  return info


def graph_hosts(text):
  """Read host names from `ansible-inventory --graph` output.

  Args:
    text: the command's stdout.

  Returns:
    Host names in the order shown, without duplicates; group lines (those with @) are skipped.
  """
  hosts = []
  for line in text.splitlines():
    match = re.match(r"^[\s|]*--([^@\s].*)$", line)
    if match and match.group(1).strip() not in hosts:
      hosts.append(match.group(1).strip())
  return hosts


def group_members(repo, base, inventory, group):
  """List a group's hosts from the working tree, when the working tree shows the base branch.

  Args:
    repo: the git working tree.
    base: the deploy branch the tree must be on.
    inventory: inventory path relative to repo.
    group: the group to graph.

  Returns:
    (hosts, None) on success, or (None, reason) when the graph is not shown.
  """
  head = run(["git", "rev-parse", "--abbrev-ref", "HEAD"], repo)[1].strip()
  if head != base:
    return None, f"HEAD is {head}, not {base}: check out {base} to read the group"
  if run(["git", "diff", "--quiet", "HEAD", "--", inventory], repo)[0] != 0:
    return None, f"{inventory} has local changes: the graph would not show {base}"
  code, out, err = run(["ansible-inventory", "-i", inventory, "--graph", group], repo, INVENTORY_TIMEOUT)
  if code != 0:
    return None, f"ansible-inventory failed: {err.strip().splitlines()[-1] if err.strip() else f'exit {code}'}"
  return graph_hosts(out), None


def main(argv=None):
  """Parse arguments, print one block per commit and the group, and exit.

  Args:
    argv: argument list; sys.argv[1:] when None.

  Returns:
    0 when every commit is on the base branch, 1 otherwise.

  Raises:
    SystemExit: 2 on bad usage (argparse) or a repo path that is not a git working tree.
  """
  parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
  parser.add_argument("commits", nargs="+", help="commits to look for")
  parser.add_argument("--repo", required=True, help="the ansible-wifi git working tree")
  parser.add_argument("--base", required=True, help="the deploy branch, e.g. rise")
  parser.add_argument("--inventory", help="inventory path relative to --repo, e.g. inventories/rcp/prod")
  parser.add_argument("--group", help="group to list from --inventory, e.g. smc_ltp")
  args = parser.parse_args(argv)
  if bool(args.inventory) != bool(args.group):
    parser.error("--inventory and --group go together")
  if not os.path.isdir(args.repo) or run(["git", "rev-parse", "--git-dir"], args.repo)[0] != 0:
    parser.error(f"not a git working tree: {args.repo}")

  missing = 0
  for commit in args.commits:
    info = reach(args.repo, commit, args.base)
    if not info["found"]:
      print(f"{commit}: not found in {args.repo}")
      missing += 1
      continue
    origin = {True: "yes", False: "no", None: "no such ref"}[info["on_origin_base"]]
    print(f"{info['commit']} {info['date']} {info['subject']}")
    print(f"  on {args.base}: {'yes' if info['on_base'] else 'no'}   on origin/{args.base}: {origin}")
    print(f"  branches: {', '.join(info['branches']) or '(none)'}")
    print(f"  cherry-pick onto {args.base}: {info['cherry_pick']}")
    missing += 0 if info["on_base"] else 1

  if args.group:
    hosts, reason = group_members(args.repo, args.base, args.inventory, args.group)
    if hosts is None:
      print(f"group {args.group}: not shown ({reason})")
    else:
      print(f"group {args.group} on {args.base} ({len(hosts)}): {', '.join(hosts) or '(empty)'}")
  return 1 if missing else 0


if __name__ == "__main__":
  sys.exit(main())
