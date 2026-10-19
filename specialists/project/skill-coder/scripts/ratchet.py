#!/usr/bin/env python3
"""A shrink-only baseline for code-quality counts: old code may carry findings it was adopted with, new findings fail, and a fixed one must be
recorded so it cannot come back. Stdlib only.

Why: a rule adopted on an existing code base (a size limit, a docstring standard, a timeout on every call) cannot be met in one change. The
operator's pattern in unified-network-controller (docstring baseline, import-layer baseline, R34 code size, 2026-10-08 to 2026-10-13) is a
baseline file that only tightens. Every checker in this pack uses this module for it.

Baseline file: JSON {key: number}. A key is whatever the checker counts per (a file path, or `path::function`).

Imported, not run: `from ratchet import compare, load, save`.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

#: The oldest Python this script runs on: it runs with the target project's own interpreter (the pack's contract test parses it at this grammar).
REQUIRES_PYTHON = (3, 11)


@dataclass
class Verdict:
    """What compare() found.

    Args:
        regressions: keys over their allowance, as "key: found N, allowed M".
        improved: keys now under their allowance, as "key: found N, baseline M" (record them with save()).
        gone: baseline keys no longer present (record with save()).
    """

    regressions: list[str] = field(default_factory=list)
    improved: list[str] = field(default_factory=list)
    gone: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        """True when nothing regressed and the baseline is current.

        Returns:
            Whether the check passes.
        """
        return not (self.regressions or self.improved or self.gone)


def load(path: Path) -> dict[str, float]:
    """Read a baseline; a missing file is an empty baseline (every finding is new).

    Args:
        path: the baseline JSON file.

    Returns:
        {key: allowed value}.

    Raises:
        ValueError: when the file is not a JSON object of numbers.
    """
    if not path.is_file():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not all(isinstance(v, (int, float)) for v in data.values()):
        raise ValueError(f"{path}: a baseline is a JSON object of numbers")
    return data


def compare(found: dict[str, float], baseline: dict[str, float]) -> Verdict:
    """Hold today's counts to the baseline.

    Args:
        found: {key: value} measured now (only keys over the limit, or with a non-zero count).
        baseline: {key: allowed value}; a key not in it is allowed 0.

    Returns:
        The verdict.
    """
    out = Verdict()
    for key in sorted(found):
        allowed = baseline.get(key, 0)
        if found[key] > allowed:
            out.regressions.append(f"{key}: found {found[key]:g}, allowed {allowed:g}")
        elif found[key] < allowed:
            out.improved.append(f"{key}: found {found[key]:g}, baseline {allowed:g}")
    out.gone = sorted(k for k in baseline if k not in found)
    return out


def save(path: Path, found: dict[str, float]) -> None:
    """Write today's counts as the baseline (on adoption, or after an improvement), sorted so the diff is readable.

    Args:
        path: the baseline JSON file.
        found: {key: value}.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(dict(sorted(found.items())), indent=1) + "\n", encoding="utf-8")


def report(verdict: Verdict, what: str, baseline_path: Path) -> list[str]:
    """Human-readable lines for a verdict.

    Args:
        verdict: compare()'s result.
        what: what is counted, for the messages ("module lines").
        baseline_path: the baseline file, named in the fix hint.

    Returns:
        One line per finding, each saying what to do.
    """
    lines = [f"FAIL {what}: {r} — fix the code (a baseline is only for code adopted with the finding)" for r in verdict.regressions]
    lines += [f"STALE {what}: {r} — record the improvement: rerun with --write-baseline ({baseline_path})" for r in verdict.improved]
    lines += [f"STALE {what}: {k} is in the baseline but no longer found — rerun with --write-baseline" for k in verdict.gone]
    return lines
