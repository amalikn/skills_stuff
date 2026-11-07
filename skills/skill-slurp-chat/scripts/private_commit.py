#!/usr/bin/env python3
"""Commit chosen files on top of HEAD through a private index, so files other live sessions staged in a shared repository are never taken.

On 2026-11-05 a peer session's `git commit` in skills_stuff took this session's staged files into its own commit, and minutes later the
same happened the other way round: in a repository several sessions share, the index is shared too. This builds the commit in a temporary
index from HEAD plus only the named paths, then moves the branch only if it still points at that HEAD (`git update-ref <ref> <new> <old>`),
so a concurrent commit makes it stop instead of losing work. The shared index and the working tree are not touched; afterwards the named
paths' index entries are pointed at the committed blobs so `git status` shows them clean.

Run: python3 scripts/private_commit.py --repo <repo> --message-file <msg> <path>[=<source>] ... [--apply]
  <source> is `@work` (default: the working-tree file), `@index` (the shared index's blob) or a file whose text to commit.
Safety: dry run prints the plan and writes nothing; --apply writes git objects, one commit and the branch ref (compare-and-swap), and the
named paths' index entries. Exit 0 ok, 1 bad input, 4 HEAD moved under it (nothing changed), 6 git failed.
"""

import argparse
import os
import subprocess
import sys
import tempfile
from pathlib import Path

GIT_TIMEOUT_S = 60


class Moved(Exception):
  """The branch moved between reading HEAD and updating it."""


def git(repo: Path, *args: str, env: dict | None = None) -> str:
  """Run git and return stripped stdout.

  Args:
    repo: repository root.
    *args: git arguments.
    env: environment (os.environ when None).

  Returns:
    Stdout.

  Raises:
    subprocess.CalledProcessError: git failed.
  """
  out = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, check=True, timeout=GIT_TIMEOUT_S, env=env)
  return out.stdout.decode().strip()


def blob_for(repo: Path, path: str, source: str) -> str:
  """Blob id for one path's content to commit.

  Args:
    repo: repository root.
    path: repository-relative path.
    source: "@work", "@index" or a file path.

  Returns:
    The blob id (written to the object store).
  """
  if source == "@index":
    return git(repo, "rev-parse", f":{path}")
  return git(repo, "hash-object", "-w", "--", path if source == "@work" else source)


def commit(repo: Path, message: Path, specs: list[tuple[str, str]], apply: bool) -> dict:
  """Plan or make the commit.

  Args:
    repo: repository root.
    message: commit message file.
    specs: (path, source) pairs.
    apply: write (False plans only).

  Returns:
    {"head", "branch", "paths", "commit" (when applied)}.

  Raises:
    Moved: the branch no longer points at the HEAD this started from.
  """
  head, branch = git(repo, "rev-parse", "HEAD"), git(repo, "symbolic-ref", "HEAD")
  plan = {"head": head, "branch": branch, "paths": [p for p, _ in specs]}
  if not apply:
    return plan
  with tempfile.TemporaryDirectory() as tmp:
    env = {**os.environ, "GIT_INDEX_FILE": str(Path(tmp) / "index")}
    git(repo, "read-tree", head, env=env)
    blobs = {}
    for path, source in specs:
      blobs[path] = blob_for(repo, path, source)
      mode = git(repo, "ls-files", "-s", "--", path).split(" ")[0] or "100644"
      git(repo, "update-index", "--add", "--cacheinfo", f"{mode},{blobs[path]},{path}", env=env)
    tree = git(repo, "write-tree", env=env)
  new = git(repo, "commit-tree", tree, "-p", head, "-F", str(message))
  try:
    git(repo, "update-ref", branch, new, head)
  except subprocess.CalledProcessError as err:
    raise Moved(f"{branch} moved since {head[:10]}; nothing committed") from err
  for path, blob in blobs.items():
    mode = git(repo, "ls-files", "-s", "--", path).split(" ")[0] or "100644"
    git(repo, "update-index", "--add", "--cacheinfo", f"{mode},{blob},{path}")
  return plan | {"commit": new}


def main(argv: list[str] | None = None) -> int:
  """Parse arguments and run.

  Args:
    argv: arguments (sys.argv when None).

  Returns:
    Exit code.
  """
  p = argparse.ArgumentParser(description="Commit named paths through a private index (dry run unless --apply).")
  p.add_argument("--repo", required=True)
  p.add_argument("--message-file", required=True)
  p.add_argument("paths", nargs="+", help="path[=@work|@index|<file>]")
  p.add_argument("--apply", action="store_true")
  args = p.parse_args(argv)
  repo, msg = Path(args.repo), Path(args.message_file)
  if not (repo / ".git").exists() or not msg.is_file():
    print("private_commit: need a git repository and a message file", file=sys.stderr)
    return 1
  specs = [(s.split("=", 1)[0], s.split("=", 1)[1] if "=" in s else "@work") for s in args.paths]
  try:
    out = commit(repo, msg, specs, args.apply)
  except Moved as err:
    print(f"private_commit: {err}", file=sys.stderr)
    return 4
  except subprocess.CalledProcessError as err:
    print(f"private_commit: git failed: {err.stderr.decode().strip()[:200]}", file=sys.stderr)
    return 6
  verb = f"committed {out['commit'][:10]}" if args.apply else "would commit"
  print(f"{verb} on {out['branch']} (from {out['head'][:10]}): {', '.join(out['paths'])}")
  return 0


if __name__ == "__main__":
  sys.exit(main())
