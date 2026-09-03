#!/usr/bin/env python3
"""Audit state machine — the spine that makes the phases enforceable rather than advisory.

WHY THIS EXISTS
---------------
Prose phases are advisory. An agent under time pressure skips the expensive ones (per-artifact
reasoning, negative-testing) and reports completion, because nothing can tell the difference
between "I did Phase 4" and "I said I did Phase 4".

So each phase writes a RECEIPT here, and the Phase 7 gate refuses to pass unless every receipt
exists and reconciles. A receipt records what was actually measured — file counts, claim counts,
artifacts reasoned about — not a boolean. A boolean is just a claim, and this whole skill exists
because of claims nobody checked.

State lives in `.staleness-audit/state.json` under the audit root. It is working state, not a
durable artifact: add it to .gitignore and delete it when the audit closes.

Usage:
    audit_state.py init   [--root .] [--scope "whole project"]
    audit_state.py record --phase N --key K --value V [--key K2 --value V2 ...]
    audit_state.py note   --phase N --text "..."
    audit_state.py status [--json]
    audit_state.py require --phase N          # exit 1 if that phase has no receipt
    audit_state.py reset

Exit codes: 0 ok · 1 requirement not met · 2 usage/state error
"""

# claim-scan:examples — paths in these docstrings are runtime artifacts and illustrative
# examples, not references to files that exist in this package.
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

STATE_DIR = ".staleness-audit"
STATE_FILE = "state.json"

PHASES = {
    0: "Snapshot before touching anything",
    1: "Defect register + coverage accounting",
    2: "Fix in dependency order",
    3: "Supersession visible in-file",
    4: "Per-artifact reasoning",
    5: "Checks that can fail",
    6: "Residual-risk register",
    7: "Completeness verification (exit gate)",
    8: "Persist and close",
}

# Receipts a phase must carry before it counts as done. Presence AND plausibility are both
# checked — a coverage receipt whose numbers do not reconcile is not a completed phase.
REQUIRED_KEYS = {
    0: ["snapshot_path", "files_snapshotted"],
    1: ["files_total", "files_examined", "files_exempt", "files_out_of_scope", "defects_found"],
    2: ["defects_fixed"],
    3: ["banners_added"],
    4: ["artifacts_total", "artifacts_reasoned", "findings"],
    5: ["checks_added", "checks_negative_tested"],
    6: ["residual_items"],
    7: ["claims_total", "claims_verified", "claims_historical", "claims_residual"],
    8: ["changelog_updated"],
}


def state_path(root: Path) -> Path:
    return root / STATE_DIR / STATE_FILE


def load(root: Path) -> dict:
    p = state_path(root)
    if not p.is_file():
        sys.stderr.write(f"ERROR: no audit in progress under {root}. Run: audit_state.py init\n")
        sys.exit(2)
    return json.loads(p.read_text(encoding="utf-8"))


def save(root: Path, data: dict) -> None:
    p = state_path(root)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def coerce(v: str):
    """Numbers stay numbers so the gate can do arithmetic on them."""
    try:
        return int(v)
    except ValueError:
        pass
    try:
        return float(v)
    except ValueError:
        pass
    if v.lower() in {"true", "false"}:
        return v.lower() == "true"
    return v


def reconcile_issues(data: dict) -> list[str]:
    """Arithmetic the gate enforces. Presence of a receipt is not enough."""
    issues: list[str] = []
    ph = data.get("phases", {})

    p1 = ph.get("1", {}).get("data", {})
    if p1:
        total = p1.get("files_total")
        parts = [p1.get("files_examined"), p1.get("files_exempt"), p1.get("files_out_of_scope")]
        if all(isinstance(x, int) for x in [total] + parts) and sum(parts) != total:
            issues.append(
                f"phase 1: coverage does not reconcile — "
                f"{'+'.join(str(x) for x in parts)} = {sum(parts)}, but files_total = {total}"
            )

    p4 = ph.get("4", {}).get("data", {})
    if p4:
        tot, done = p4.get("artifacts_total"), p4.get("artifacts_reasoned")
        if isinstance(tot, int) and isinstance(done, int) and done < tot:
            issues.append(
                f"phase 4: only {done} of {tot} artifacts reasoned about. Skipping an artifact is "
                f"fine; skipping the question is not — record a verdict for each"
            )

    p5 = ph.get("5", {}).get("data", {})
    if p5:
        added, tested = p5.get("checks_added"), p5.get("checks_negative_tested")
        if isinstance(added, int) and isinstance(tested, int) and tested < added:
            issues.append(
                f"phase 5: {added} checks added but only {tested} negative-tested. A check that "
                f"never fires breaks nothing and passes forever"
            )

    p7 = ph.get("7", {}).get("data", {})
    if p7:
        total = p7.get("claims_total")
        parts = [p7.get("claims_verified"), p7.get("claims_historical"), p7.get("claims_residual")]
        if all(isinstance(x, int) for x in [total] + parts) and sum(parts) != total:
            issues.append(
                f"phase 7: claim matrix does not reconcile — "
                f"{'+'.join(str(x) for x in parts)} = {sum(parts)}, but claims_total = {total}"
            )

    return issues


def cmd_init(a) -> int:
    root = Path(a.root).resolve()
    p = state_path(root)
    if p.is_file() and not a.force:
        sys.stderr.write(f"ERROR: audit already in progress ({p}). Use --force to restart.\n")
        return 2
    save(root, {
        "root": str(root),
        "scope": a.scope,
        "started": a.started or "(timestamp not supplied)",
        "phases": {},
    })
    gitignore = root / ".gitignore"
    line = f"{STATE_DIR}/"
    try:
        existing = gitignore.read_text(encoding="utf-8") if gitignore.is_file() else ""
        if line not in existing:
            with gitignore.open("a", encoding="utf-8") as f:
                f.write(("" if existing.endswith("\n") or not existing else "\n")
                        + f"{line}\n")
            print(f"added '{line}' to .gitignore")
    except OSError:
        print(f"NOTE: could not update .gitignore — add '{line}' by hand")
    print(f"audit initialised: {p}\nscope: {a.scope}")
    return 0


def cmd_record(a) -> int:
    root = Path(a.root).resolve()
    data = load(root)
    if len(a.key) != len(a.value):
        sys.stderr.write("ERROR: --key and --value must be given in pairs\n")
        return 2
    entry = data["phases"].setdefault(str(a.phase), {"data": {}, "notes": []})
    for k, v in zip(a.key, a.value):
        entry["data"][k] = coerce(v)
    save(root, data)
    missing = [k for k in REQUIRED_KEYS.get(a.phase, []) if k not in entry["data"]]
    print(f"phase {a.phase} ({PHASES.get(a.phase, '?')}) recorded: {entry['data']}")
    if missing:
        print(f"  still missing: {', '.join(missing)}")
    return 0


def cmd_note(a) -> int:
    root = Path(a.root).resolve()
    data = load(root)
    data["phases"].setdefault(str(a.phase), {"data": {}, "notes": []})["notes"].append(a.text)
    save(root, data)
    print(f"phase {a.phase} note added")
    return 0


def cmd_require(a) -> int:
    root = Path(a.root).resolve()
    data = load(root)
    entry = data["phases"].get(str(a.phase))
    if not entry:
        sys.stderr.write(f"BLOCKED: phase {a.phase} ({PHASES[a.phase]}) has no receipt.\n")
        return 1
    missing = [k for k in REQUIRED_KEYS.get(a.phase, []) if k not in entry["data"]]
    if missing:
        sys.stderr.write(f"BLOCKED: phase {a.phase} incomplete — missing {', '.join(missing)}\n")
        return 1
    print(f"phase {a.phase} satisfied")
    return 0


def cmd_status(a) -> int:
    root = Path(a.root).resolve()
    data = load(root)
    issues = reconcile_issues(data)
    if a.json:
        print(json.dumps({**data, "reconcile_issues": issues}, indent=2))
        return 1 if issues else 0

    print(f"Staleness audit — {data['root']}")
    print(f"Scope: {data['scope']}")
    print("-" * 72)
    incomplete = []
    for n, title in PHASES.items():
        entry = data["phases"].get(str(n))
        if not entry:
            print(f"  [ ] {n}  {title}")
            incomplete.append(n)
            continue
        missing = [k for k in REQUIRED_KEYS.get(n, []) if k not in entry["data"]]
        mark = "~" if missing else "x"
        if missing:
            incomplete.append(n)
        print(f"  [{mark}] {n}  {title}")
        for k, v in entry["data"].items():
            print(f"          {k}: {v}")
        for note in entry["notes"]:
            print(f"          note: {note}")
        if missing:
            print(f"          MISSING: {', '.join(missing)}")
    print("-" * 72)
    if issues:
        print("RECONCILIATION FAILURES:")
        for i in issues:
            print(f"  ✗ {i}")
    if incomplete:
        print(f"Incomplete phases: {', '.join(str(i) for i in incomplete)}")
    if not issues and not incomplete:
        print("All phases recorded and reconciling.")
        return 0
    return 1


def cmd_reset(a) -> int:
    root = Path(a.root).resolve()
    p = state_path(root)
    if p.is_file():
        p.unlink()
        print(f"removed {p}")
    else:
        print("no state to remove")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--root", default=".", help="audit root (default: cwd)")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("init"); p.add_argument("--scope", default="whole project")
    p.add_argument("--started", default=""); p.add_argument("--force", action="store_true")
    p.set_defaults(fn=cmd_init)

    p = sub.add_parser("record"); p.add_argument("--phase", type=int, required=True)
    p.add_argument("--key", action="append", default=[])
    p.add_argument("--value", action="append", default=[])
    p.set_defaults(fn=cmd_record)

    p = sub.add_parser("note"); p.add_argument("--phase", type=int, required=True)
    p.add_argument("--text", required=True); p.set_defaults(fn=cmd_note)

    p = sub.add_parser("require"); p.add_argument("--phase", type=int, required=True)
    p.set_defaults(fn=cmd_require)

    p = sub.add_parser("status"); p.add_argument("--json", action="store_true")
    p.set_defaults(fn=cmd_status)

    p = sub.add_parser("reset"); p.set_defaults(fn=cmd_reset)

    a = ap.parse_args()
    return a.fn(a)


if __name__ == "__main__":
    sys.exit(main())
