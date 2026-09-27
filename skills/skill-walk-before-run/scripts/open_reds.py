#!/usr/bin/env python3
"""List every unresolved RED for one project in skill-walk-before-run's ledger. Read-only.

Added in v0.1.3 at the operator's request (2026-09-27): a run names ONE assumption (Step 0), so REDs
opened earlier on other assumptions stayed invisible unless someone went looking. This lists them all,
so each run's output can carry the full open set beside its own verdict.

A RED is closed only by a later RESOLVED entry whose assumption restates it (compared after collapsing
whitespace), as schemas/ledger-entry.md requires. A later RESOLVED whose assumption merely overlaps
(a shared opening of PARTIAL_PREFIX characters) does not close it; it is shown as a possible partial
resolution, because a RESOLVED written against a narrowed assumption leaves the rest of the RED open.
Two or more waivers on one assumption are flagged, as SKILL.md says they are a finding.

Reads ledger.jsonl beside SKILL.md; falls back to <project-root>/.wbr-ledger.jsonl only when the ledger
is missing or unreadable, and says so. Never writes anything.

Usage:
    python3 open_reds.py --project <name> [--project-root <path>] [--json]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
LEDGER_PATH = SKILL_DIR / "ledger.jsonl"
PARTIAL_PREFIX = 60


def norm(text: str) -> str:
    return " ".join((text or "").split())


def read_entries(path: Path) -> list[dict]:
    entries = []
    for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            entries.append(json.loads(line))
        except json.JSONDecodeError:
            print(f"open_reds.py: {path.name} line {n} is not JSON; skipped", file=sys.stderr)
    return entries


def open_reds(entries: list[dict], project: str) -> list[dict]:
    """Unresolved REDs for `project`, oldest first, each with its waiver count and any partial resolutions."""
    mine = [e for e in entries if e.get("project") == project]
    reds: dict[str, dict] = {}
    for e in mine:
        key = norm(e.get("assumption", ""))
        if e.get("verdict") == "RED":
            rec = reds.setdefault(key, {"opened": e.get("ts"), "assumption": e.get("assumption"), "next_test": e.get("next_test"),
                                        "waivers": 0, "partial": []})
            rec["next_test"] = e.get("next_test") or rec["next_test"]
            rec["waivers"] += bool(e.get("waiver"))
        elif e.get("verdict") == "RESOLVED":
            if key in reds:
                del reds[key]
            else:
                for rkey, rec in reds.items():
                    if rkey[:PARTIAL_PREFIX] == key[:PARTIAL_PREFIX]:
                        rec["partial"].append({"ts": e.get("ts"), "result": e.get("result"), "assumption": e.get("assumption")})
    return list(reds.values())


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--project", required=True, help="the project name exactly as the ledger records it")
    ap.add_argument("--project-root", default=None, help="the project's root, for the .wbr-ledger.jsonl fallback")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    args = ap.parse_args(argv)

    source = LEDGER_PATH
    try:
        entries = read_entries(LEDGER_PATH)
    except OSError as exc:
        mirror = Path(args.project_root) / ".wbr-ledger.jsonl" if args.project_root else None
        if mirror is None or not mirror.is_file():
            print(f"open_reds.py: ledger unreadable ({exc}) and no mirror to fall back to", file=sys.stderr)
            return 1
        source, entries = mirror, read_entries(mirror)
        print(f"open_reds.py: ledger unreadable ({exc}); read the project mirror {mirror}", file=sys.stderr)

    found = open_reds(entries, args.project)
    if args.json:
        print(json.dumps({"project": args.project, "source": str(source), "open": found}, indent=1))
        return 0
    if not found:
        print(f"{args.project}: no unresolved RED in {source.name}")
        return 0
    print(f"{args.project}: {len(found)} unresolved RED(s) in {source.name}")
    for n, rec in enumerate(found, 1):
        print(f"\n{n}. opened {rec['opened']}" + (f" — {rec['waivers']} waivers: a finding" if rec["waivers"] >= 2 else
                                                   f" — {rec['waivers']} waiver" if rec["waivers"] else ""))
        print(f"   assumption: {rec['assumption']}")
        print(f"   next test:  {rec['next_test']}")
        for p in rec["partial"]:
            print(f"   partial?    RESOLVED {p['result']} {p['ts']} on a narrower assumption: {p['assumption']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
