#!/usr/bin/env python3
"""Check that each project copy of a canonical Vagrantfile exists and is byte-identical to it. Read-only.

Why: a project keeps a copy of the Vagrantfile its lab runs on (operator 2026-10-21: "for the Vagrant files always keep a copy locally as
well"); a copy that drifts from the canonical file describes a lab nobody runs. Generic form of smc-resiliency's check_vagrant_copies
(scripts/govcheck/checks/paths.py @ a124c13a), promoted to skill-vagrant 2026-11-07.

Usage:
  vagrant_copy_check.py <copy>=<canonical> [<copy>=<canonical> ...] [--require-canonical]

  A missing canonical file is skipped (the canonical workspace may not be mounted) unless --require-canonical is given.

Safety: reads the named files only. Exit: 0 all copies match; 1 a copy is missing or differs (or a required canonical is missing); 2 bad arguments.
"""

from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path


def compare(copy: Path, canonical: Path, require_canonical: bool = False) -> tuple[str, str]:
  """Compare one copy with its canonical file.

  Args:
    copy: the project's copy.
    canonical: the canonical Vagrantfile.
    require_canonical: treat a missing canonical file as a failure.

  Returns:
    (status, message): status is "ok", "skipped" or "fail".
  """
  if not copy.is_file():
    return "fail", f"{copy} is missing: copy it from {canonical}"
  if not canonical.is_file():
    if require_canonical:
      return "fail", f"canonical {canonical} is missing"
    return "skipped", f"canonical {canonical} is not present; {copy} not compared"
  a, b = copy.read_bytes(), canonical.read_bytes()
  if a != b:
    return "fail", (
      f"{copy} differs from {canonical} (sha256 {hashlib.sha256(a).hexdigest()[:12]} vs {hashlib.sha256(b).hexdigest()[:12]}): copy the canonical file over it"
    )
  return "ok", f"{copy} matches {canonical}"


def parse_pair(text: str) -> tuple[Path, Path]:
  """Split a `<copy>=<canonical>` argument.

  Args:
    text: the argument.

  Returns:
    (copy, canonical) paths.

  Raises:
    argparse.ArgumentTypeError: when there is no `=` or a side is empty.
  """
  copy, sep, canonical = text.partition("=")
  if not sep or not copy or not canonical:
    raise argparse.ArgumentTypeError(f"expected <copy>=<canonical>, got {text!r}")
  return Path(copy), Path(canonical)


def main(argv: list[str] | None = None) -> int:
  """Command line.

  Args:
    argv: arguments (default sys.argv[1:]).

  Returns:
    0 when every copy matches, 1 when one is missing or differs (argparse exits 2 on bad arguments).
  """
  ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
  ap.add_argument("pairs", nargs="+", type=parse_pair, help="<copy>=<canonical>")
  ap.add_argument("--require-canonical", action="store_true", help="fail when a canonical file is absent")
  args = ap.parse_args(argv)
  failed = False
  for copy, canonical in args.pairs:
    status, message = compare(copy, canonical, args.require_canonical)
    print(f"{status}: {message}")
    failed |= status == "fail"
  return 1 if failed else 0


if __name__ == "__main__":
  sys.exit(main())
