#!/usr/bin/env python3
"""Governance coherence checks for skill-goal-guard: the pack's own rules as assertions that fail (skill-ai-it bootstrap, 2026-10-27).

Usage:
  python scripts/check_governance.py [--select FAMILY,...] [--json] [--timings]
  (or `just governance`; `just check` runs it)

Safety: read-only; reads the pack's files and writes nothing. Exit 0 when every check passes, 1 otherwise.
"""

import sys

from govcheck.checks import CHECKS
from govcheck.core import run

if __name__ == "__main__":
  sys.exit(run(CHECKS))
