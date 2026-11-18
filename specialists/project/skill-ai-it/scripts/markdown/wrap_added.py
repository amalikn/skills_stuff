"""Wrap only the Markdown lines a working tree added (per `git diff`) that run past the column limit, outside tables and code fences; words never change.

The governance rule wraps prose at 200 columns but never reflows other people's text, tables, code blocks or source captures. After a scripted edit lengthens many
lines across many pages, this wraps exactly the lines the diff added and leaves every pre-existing long line alone. The word sequence of each file is compared
before and after; a mismatch refuses the write. Found in Continuum (2026-11-18): 36 lengthened lines over 44 architecture pages after a decision pass.

Run: python3 scripts/markdown/wrap_added.py --repo <git dir> [--width 200] [--apply] <file.md> [...]
Safety: plan by default (counts per file); writes the named files only with `--apply`. git runs read-only with a timeout. Exit 0 ok, 1 refused.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import textwrap
from pathlib import Path


def added_lines(repo: Path, path: Path) -> set[str]:
  """Collect the text of lines added to a file relative to HEAD.

  Args:
    repo: a directory inside the git work tree.
    path: the file.

  Returns:
    The set of added line texts; empty for an untracked file.

  Raises:
    subprocess.CalledProcessError: when git fails.
  """
  diff = subprocess.run(["git", "-C", str(repo), "diff", "-U0", "--", str(path.resolve())], capture_output=True, text=True, timeout=30, check=True).stdout
  return {line[1:] for line in diff.splitlines() if line.startswith("+") and not line.startswith("+++")}


def wrap_text(text: str, added: set[str], width: int) -> tuple[str, int]:
  """Wrap added prose lines longer than width.

  Args:
    text: the file's text.
    added: line texts the diff added.
    width: the column limit.

  Returns:
    (new text, number of lines wrapped).

  Raises:
    ValueError: when wrapping would change the word sequence.
  """
  lines, out, fence, count = text.split("\n"), [], False, 0
  for line in lines:
    if line.lstrip().startswith(("```", "~~~")):
      fence = not fence
    if not fence and line in added and len(line) > width and not line.lstrip().startswith("|"):
      indent = "  " if line.startswith(("- ", "* ", "  ")) else ("> " if line.startswith("> ") else "")
      out += textwrap.wrap(line, width, subsequent_indent=indent, break_on_hyphens=False, break_long_words=False)
      count += 1
    else:
      out.append(line)
  new = "\n".join(out)
  if text.replace("> ", "").split() != new.replace("> ", "").split():
    raise ValueError("word sequence would change")
  return new, count


def main(argv: list[str] | None = None) -> int:
  """Plan or apply wrapping for each named file.

  Args:
    argv: command-line arguments; None uses sys.argv.

  Returns:
    0 when planned or written; 1 when a file is refused.
  """
  ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
  ap.add_argument("files", nargs="+", type=Path)
  ap.add_argument("--repo", type=Path, default=Path("."))
  ap.add_argument("--width", type=int, default=200)
  ap.add_argument("--apply", action="store_true")
  a = ap.parse_args(argv)
  total = 0
  for path in a.files:
    try:
      new, count = wrap_text(path.read_text(), added_lines(a.repo, path), a.width)
    except ValueError as error:
      print(f"refused {path}: {error}", file=sys.stderr)
      return 1
    if count:
      print(f"{path}: {count} line(s)")
      total += count
      if a.apply:
        path.write_text(new)
  print(f"{'wrapped' if a.apply else 'plan'}: {total} line(s)")
  return 0


if __name__ == "__main__":
  raise SystemExit(main())
