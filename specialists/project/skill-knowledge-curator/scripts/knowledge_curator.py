#!/usr/bin/env python3
"""Knowledge Curator (kc) command line: the deterministic kernel behind the skill.

Commands: inventory project Markdown, take agent-extracted claims with verified evidence, find duplicates and
conflicts, record operator decisions, render derived knowledge pages, promote a page to authoritative, and plan archives.

The agent does the reading (claim extraction from `worksheet` batches, pair classification from `candidates`); this CLI is the
deterministic kernel that checks and records it (references/workflow.md).

Usage:
  python scripts/knowledge_curator.py <command> --project <dir> [options]   (or `just kc <command> <dir> ...`)
  commands: init, inventory, worksheet, coverage, claims, candidates, relate, review, decide, render, promote,
            archive-plan, query, intake, validate, report
  Example: python scripts/knowledge_curator.py inventory --project tests/fixtures/pilot

Inputs:
  --project DIR      project root; ledgers live in DIR/.kc/
  --file FILE        claims or relations input (.json or .jsonl), checked against schemas/
  --payload FILE     intake payload (schemas/intake-payload.schema.json)
  KC_ACTOR           name recorded on decisions and promotions (default project-owner)

Safety: read-only by default. With --apply: init writes .kc/config.yaml; inventory, claims, relate, decide and promote append to
.kc/*.jsonl; render writes knowledge/ pages (never a promoted page) and .kc/proposals/; review and archive-plan write a report
under .kc/. Nothing ever edits, moves or deletes a source document or a governing file, commits or pushes.

Exit codes: 0 ok; 1 bad input; 2 review needed (nothing changed); 3 validation failed; 4 conflict blocker; 5 source changed;
6 I/O, lock or restore failure.
"""

import argparse
import sys
import time
from pathlib import Path

from knowledge_curator_lib import settings
from knowledge_curator_lib.commands import COMMANDS, emit
from knowledge_curator_lib.errors import InputError, KcError


class Parser(argparse.ArgumentParser):
  """ArgumentParser whose usage errors exit 1 (bad input), keeping exit 2 for "review needed"."""

  def error(self, message: str):
    """Print usage and exit 1.

    Args:
      message: argparse's message.

    Raises:
      SystemExit: always, code 1.
    """
    self.print_usage(sys.stderr)
    self.exit(1, f"{self.prog}: error: {message}\n")


def build_parser() -> Parser:
  """Command-line parser.

  Returns:
    The parser.
  """
  p = Parser(prog="kc", description="Knowledge Curator: deterministic kernel. Read-only unless --apply.")
  sub = p.add_subparsers(dest="command", required=True, parser_class=Parser)
  for name in COMMANDS:
    s = sub.add_parser(name)
    s.add_argument("--project", required=True, help="project root")
    if name in ("init", "inventory", "claims", "relate", "review", "decide", "render", "promote", "archive-plan"):
      s.add_argument("--apply", action="store_true", help="write (default: plan only)")
    if name in ("claims", "relate"):
      s.add_argument("--file", required=True)
  sub.choices["worksheet"].add_argument("--batch", type=int, default=1)
  d = sub.choices["decide"]
  d.add_argument("conflict")
  d.add_argument("action", choices=settings.ACTIONS)
  d.add_argument("--reason", required=True)
  for opt in ("--current", "--scope-note", "--corrected-text", "--answer-text", "--actor"):
    d.add_argument(opt)
  r = sub.choices["render"]
  r.add_argument("--check", action="store_true", help="exit 3 when pages differ from a fresh rendering")
  pr = sub.choices["promote"]
  pr.add_argument("--page", required=True, help="e.g. knowledge/architecture.md")
  pr.add_argument("--approve-digest")
  pr.add_argument("--reason")
  pr.add_argument("--actor")
  pr.add_argument("--revoke", action="store_true")
  q = sub.choices["query"]
  q.add_argument("text")
  q.add_argument("--limit", type=int, default=10)
  q.add_argument("--history", action="store_true", help="include superseded and historical claims")
  sub.choices["intake"].add_argument("--payload", required=True)
  return p


def main(argv: list[str] | None = None) -> int:
  """Run one command.

  Args:
    argv: arguments (sys.argv when None).

  Returns:
    Process exit code.
  """
  args = build_parser().parse_args(argv)
  root = Path(args.project)
  if not root.is_dir():
    print(f"kc: project folder not found: {root}", file=sys.stderr)
    return InputError.exit_code
  start = time.perf_counter()
  try:
    result = COMMANDS[args.command](root, args)
  except KcError as err:
    print(f"kc {args.command}: {err}", file=sys.stderr)
    return err.exit_code
  if args.command != "review":
    emit({**result, "elapsed_s": round(time.perf_counter() - start, 3)} if isinstance(result, dict) else result)
  return 0


if __name__ == "__main__":
  sys.exit(main())
