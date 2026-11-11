#!/usr/bin/env python3
"""Check a design document's examples and structure: every fenced TOML, YAML, JSON or Python example parses, every table row has its
header's cell count, and every internal `#anchor` link resolves to a heading.

Why (operator, 2026-11-11, unified-network-controller session): a long plan with map formats, TOML/YAML/JSON examples and code excerpts was
edited many times; a pipe inside backticks split a table row, a TOML header landed in a YAML block, and renumbered sections broke anchors.
Each was caught only by running this logic by hand after every edit. Use it on any Markdown file whose examples readers will copy.

Run: `just md-examples <file.md> [...]` or `python3 scripts/markdown/md_examples_check.py <file.md> [...]`. Read-only; exit 1 on a finding.
JSON blocks may be one document or JSON Lines. YAML needs PyYAML (imported only when a YAML block exists). Runtime: well under a second for a
1,600-line file.
"""

from __future__ import annotations

import argparse
import ast
import json
import re
import sys
import tomllib
from pathlib import Path

FENCE = re.compile(r"^```(\w+)?\n(.*?)^```", re.S | re.M)
HEADING = re.compile(r"^#{1,6} (.+)$", re.M)
LINK = re.compile(r"\]\(#([^)]+)\)")
PIPE = re.compile(r"(?<!\\)\|")  # a cell border; `\|` is a literal pipe inside a cell (GitHub Markdown)


def slug(heading: str) -> str:
  """GitHub-style anchor for a heading.

  Args:
      heading: the heading text without the leading hashes.
  Returns:
      The anchor: lower case, punctuation other than `-` and `_` dropped, spaces as hyphens.
  """
  return re.sub(r"[^\w\- ]", "", heading.strip().lower()).replace(" ", "-")


def check_examples(text: str) -> list[str]:
  """Parse every fenced example in a supported language.

  Args:
      text: the Markdown file's text.
  Returns:
      One finding per block that does not parse, with its language and first line.
  """
  findings = []
  for m in FENCE.finditer(text):
    lang, body = (m.group(1) or "").lower(), m.group(2)
    line = text[: m.start()].count("\n") + 1
    try:
      if lang == "toml":
        tomllib.loads(body)
      elif lang in ("yaml", "yml"):
        import yaml  # third-party at the edge: only when a YAML block exists

        try:
          list(yaml.safe_load_all(body))
        except yaml.YAMLError as exc:
          raise ValueError(str(exc)) from exc
      elif lang in ("json", "jsonl"):
        stripped = body.strip()
        try:
          json.loads(stripped)
        except json.JSONDecodeError:
          for row in stripped.splitlines():
            json.loads(row)
      elif lang == "python":
        ast.parse(body)
      else:
        continue
    except (tomllib.TOMLDecodeError, ValueError, SyntaxError) as exc:  # a parse error is the finding; JSONDecodeError is a ValueError
      findings.append(f"line {line}: {lang} example does not parse: {str(exc).splitlines()[0][:120]}")
  return findings


def check_tables(text: str) -> list[str]:
  """Every row of a pipe table has as many cells as its header.

  Args:
      text: the Markdown file's text; fenced blocks are skipped.
  Returns:
      One finding per row with a different cell count (a pipe inside backticks splits a cell).
  """
  lines = FENCE.sub(lambda m: "\n" * m.group(0).count("\n"), text).split("\n")
  findings, k = [], 0
  while k < len(lines):
    is_header = lines[k].startswith("|") and k + 1 < len(lines) and lines[k + 1].startswith("|")
    if is_header and set(lines[k + 1].replace("|", "").strip()) <= set("-: "):
      cells, m = len(PIPE.findall(lines[k])), k + 2
      while m < len(lines) and lines[m].startswith("|"):
        if len(PIPE.findall(lines[m])) != cells:
          findings.append(f"line {m + 1}: table row has {len(PIPE.findall(lines[m])) - 1} cells, header has {cells - 1}")
        m += 1
      k = m
    else:
      k += 1
  return findings


def check_anchors(text: str) -> list[str]:
  """Every internal `](#anchor)` link names a heading in the file.

  Args:
      text: the Markdown file's text.
  Returns:
      One finding per anchor with no matching heading.
  """
  body = FENCE.sub("", text)
  heads = {slug(h) for h in HEADING.findall(body)}
  return [f"broken anchor #{a}" for a in sorted(set(LINK.findall(body))) if a not in heads]


def check_file(path: Path) -> list[str]:
  """All checks on one file.

  Args:
      path: a Markdown file.
  Returns:
      Findings, each prefixed with the file name.
  """
  text = path.read_text(encoding="utf-8")
  return [f"{path}: {f}" for f in check_examples(text) + check_tables(text) + check_anchors(text)]


def main(argv: list[str] | None = None) -> int:
  """Command line entry.

  Args:
      argv: arguments (default: sys.argv[1:]).
  Returns:
      0 when every file is clean, 1 on a finding.
  """
  ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
  ap.add_argument("files", nargs="+", type=Path)
  args = ap.parse_args(argv)
  findings = [f for p in args.files for f in check_file(p)]
  for f in findings:
    print(f)
  print(f"{'FAIL' if findings else 'OK'}: {len(args.files)} file(s), {len(findings)} finding(s)")
  return 1 if findings else 0


if __name__ == "__main__":
  sys.exit(main())
