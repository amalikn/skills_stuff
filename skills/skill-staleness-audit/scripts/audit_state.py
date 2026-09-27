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
    audit_state.py init   [--root .] [--scope "whole project"] [--since REF|last-audit]
    audit_state.py record --phase N --key K --value V [--key K2 --value V2 ...]
    audit_state.py negtest red   --check ID --expect TEXT --cmd "CMD"   # after breaking the project
    audit_state.py negtest green --check ID [--cmd "CMD"]                # after restoring it
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
import hashlib
import json
import shlex
import subprocess
import sys
from datetime import datetime, timezone
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
    # systems_of_record: how many live systems of record (Nautobot, a CMDB, a database the project writes to) hold
    # prose about this project. 0 is a valid answer; not asking is not. Added 2026-09-27 after a stale description sat in
    # Nautobot, outside every file scan, and was found by luck.
    1: ["files_total", "files_examined", "files_exempt", "files_out_of_scope", "defects_found", "systems_of_record"],
    2: ["defects_fixed"],
    3: ["banners_added"],
    4: ["artifacts_total", "artifacts_reasoned", "findings"],
    5: ["checks_added", "checks_negative_tested"],
    6: ["residual_items"],
    7: ["claims_total", "claims_verified", "claims_historical", "claims_residual"],
    8: ["changelog_updated"],
}

# Keys only a command may write. `checks_negative_tested` was a number the agent typed, and on 2026-09-27 a negative test
# that PASSED while the project was broken was still counted. It is now derived from `negtest` evidence.
DERIVED_KEYS = {5: {"checks_negative_tested"}}

# A system-of-record sample must cover every changed object up to this many. Beyond it, read this many and say so.
SOR_SAMPLE_CAP = 50


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

    if p1.get("systems_of_record", 0) not in (0, None):
        changed, read = p1.get("sor_objects_changed"), p1.get("sor_objects_read")
        if not isinstance(changed, int) or not isinstance(read, int):
            issues.append("phase 1: systems_of_record > 0 but sor_objects_changed / sor_objects_read not recorded — "
                          "read back the prose of objects changed since the last audit")
        elif read < min(changed, SOR_SAMPLE_CAP):
            issues.append(f"phase 1: system-of-record sample read {read} of {changed} changed objects "
                          f"(needs {min(changed, SOR_SAMPLE_CAP)})")

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
        derived = negtested_count(ph.get("5", {}))
        if p5.get("checks_negative_tested", derived) != derived:
            issues.append(f"phase 5: checks_negative_tested says {p5.get('checks_negative_tested')} but negtest "
                          f"evidence proves {derived}. The count is derived; it cannot be typed")
        added, tested = p5.get("checks_added"), derived
        if isinstance(added, int) and tested < added:
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


def missing_keys(data: dict) -> dict[str, list[str]]:
    """Required receipt keys absent from a recorded phase. The gate blocks on these, not only on absent phases."""
    out: dict[str, list[str]] = {}
    for n, keys in REQUIRED_KEYS.items():
        entry = data.get("phases", {}).get(str(n))
        if not entry:
            continue
        miss = [k for k in keys if k not in entry.get("data", {})]
        if miss:
            out[str(n)] = miss
    return out


def negtested_count(entry: dict) -> int:
    """Checks with a failing run that matched its expected text, followed by a passing run of the same check."""
    n = 0
    for ev in entry.get("negtests", {}).values():
        red, green = ev.get("red"), ev.get("green")
        if red and green and red.get("ok") and green.get("ok") and green["seq"] > red["seq"]:
            n += 1
    return n


def phase_entry(data: dict, phase: int) -> dict:
    """setdefault that also repairs an entry another script created without the data/notes shape."""
    entry = data["phases"].setdefault(str(phase), {})
    entry.setdefault("data", {})
    entry.setdefault("notes", [])
    return entry


def resolve_since(root: Path, ref: str) -> tuple[str, str]:
    """REF or `last-audit` -> (sha, how). `last-audit` is the commit that added the newest staleness-audit report."""
    if ref == "last-audit":
        reports = sorted(p for p in root.rglob("staleness-audit-*.md")
                         if not any(part.startswith(".staleness-audit") for part in p.relative_to(root).parts))
        if not reports:
            raise ValueError("--since last-audit: no staleness-audit-*.md report found under the root")
        newest = max(reports, key=lambda p: p.name)
        r = subprocess.run(["git", "log", "-1", "--format=%H", "--diff-filter=A", "--", str(newest)], cwd=root,
                           capture_output=True, text=True)
        if r.returncode != 0:
            raise ValueError(f"--since last-audit: git cannot read history here ({r.stderr.strip()[:120]})")
        sha = r.stdout.strip()
        if not sha:
            raise ValueError(f"--since last-audit: {newest.name} is not committed")
        return sha, f"last-audit ({newest.name})"
    r = subprocess.run(["git", "rev-parse", "--verify", f"{ref}^{{commit}}"], cwd=root, capture_output=True, text=True)
    if r.returncode != 0:
        raise ValueError(f"--since {ref}: not a commit")
    return r.stdout.strip(), ref


def cmd_init(a) -> int:
    root = Path(a.root).resolve()
    p = state_path(root)
    if p.is_file() and not a.force:
        sys.stderr.write(f"ERROR: audit already in progress ({p}). Use --force to restart.\n")
        return 2
    doc = {
        "root": str(root),
        "scope": a.scope,
        "started": a.started or "(timestamp not supplied)",
        "phases": {},
    }
    if a.since:
        try:
            sha, how = resolve_since(root, a.since)
        except ValueError as e:
            sys.stderr.write(f"ERROR: {e}\n")
            return 2
        doc["since"] = {"sha": sha, "ref": how}
    save(root, doc)
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
    if doc.get("since"):
        print(f"focus: changed since {doc['since']['ref']} = {doc['since']['sha'][:12]} "
              f"(scanners flag these; coverage and denominators stay whole-project)")
    return 0


def cmd_record(a) -> int:
    root = Path(a.root).resolve()
    data = load(root)
    if len(a.key) != len(a.value):
        sys.stderr.write("ERROR: --key and --value must be given in pairs\n")
        return 2
    refused = [k for k in a.key if k in DERIVED_KEYS.get(a.phase, set())]
    if refused:
        sys.stderr.write(f"REFUSED: {', '.join(refused)} is derived from evidence and cannot be typed. "
                         f"Run: audit_state.py negtest red|green --check <id> ...\n")
        return 2
    entry = phase_entry(data, a.phase)
    for k, v in zip(a.key, a.value):
        entry["data"][k] = coerce(v)
    if a.phase == 5:
        entry["data"]["checks_negative_tested"] = negtested_count(entry)
    save(root, data)
    missing = [k for k in REQUIRED_KEYS.get(a.phase, []) if k not in entry["data"]]
    print(f"phase {a.phase} ({PHASES.get(a.phase, '?')}) recorded: {entry['data']}")
    if missing:
        print(f"  still missing: {', '.join(missing)}")
    return 0


def cmd_note(a) -> int:
    root = Path(a.root).resolve()
    data = load(root)
    phase_entry(data, a.phase)["notes"].append(a.text)
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
    missing = [k for k in REQUIRED_KEYS.get(a.phase, []) if k not in entry.get("data", {})]
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
        print(json.dumps({**data, "reconcile_issues": issues, "missing_keys": missing_keys(data)}, indent=2))
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
        missing = [k for k in REQUIRED_KEYS.get(n, []) if k not in entry.get("data", {})]
        mark = "~" if missing else "x"
        if missing:
            incomplete.append(n)
        print(f"  [{mark}] {n}  {title}")
        for k, v in entry.get("data", {}).items():
            print(f"          {k}: {v}")
        for cid, ev in entry.get("negtests", {}).items():
            legs = ", ".join(f"{leg} {'ok' if ev[leg]['ok'] else 'REFUSED'}" for leg in ("red", "green") if leg in ev)
            print(f"          negtest {cid}: {legs}")
        for note in entry.get("notes", []):
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


def _run_capture(cmd: str, cwd: Path) -> tuple[int, str]:
    try:
        r = subprocess.run(shlex.split(cmd), cwd=cwd, capture_output=True, text=True, timeout=900)
        return r.returncode, (r.stdout or "") + (r.stderr or "")
    except (OSError, subprocess.SubprocessError, ValueError) as e:
        return 127, f"could not run: {e}"


def cmd_negtest(a) -> int:
    """Record one leg of a negative test by RUNNING the check, never by taking the agent's word for it.

    red   — the project has been broken on purpose. The check must exit non-zero AND print --expect, so a failure for
            some unrelated reason (a syntax error, a missing tool) is not mistaken for the check firing.
    green — the break has been undone. The same check must exit 0, and --expect must no longer appear: text that also
            shows in a passing run is not failure-specific, so the red leg proved nothing.
    Both legs keep an excerpt and a sha256 of the output, and the count the gate uses is derived from them.
    """
    root = Path(a.root).resolve()
    data = load(root)
    entry = phase_entry(data, 5)
    tests = entry.setdefault("negtests", {})
    ev = tests.setdefault(a.check, {})
    if a.leg == "red":
        if not a.expect or not a.cmd:
            sys.stderr.write("ERROR: negtest red needs --expect TEXT and --cmd CMD\n")
            return 2
        cmd, expect = a.cmd, a.expect
    else:
        if "red" not in ev:
            sys.stderr.write(f"REFUSED: check {a.check!r} has no red leg. Break the project and run the red leg first\n")
            return 1
        cmd, expect = a.cmd or ev["red"]["cmd"], ev["red"]["expect"]
    rc, out = _run_capture(cmd, root)
    seq = 1 + max((leg.get("seq", 0) for t in tests.values() for leg in t.values() if isinstance(leg, dict)),
                  default=0)
    hit = expect in out
    if a.leg == "red":
        ok = rc != 0 and hit
        why = ("" if ok else "the check exited 0 while the project was broken — it cannot fail, or the break did not "
               "reach it" if rc == 0 else f"the check failed (exit {rc}) but its output lacks {expect!r} — it failed "
               "for some other reason")
    else:
        ok = rc == 0 and not hit
        why = ("" if ok else f"the check still fails (exit {rc}) after the restore" if rc != 0 else
               f"{expect!r} also appears in the passing output, so it is not failure-specific and the red leg proves "
               "nothing — re-run red with a failure-specific --expect")
    lines = out.splitlines()
    excerpt = [ln for ln in lines if expect in ln][:5] + ["…"] + lines[-5:]
    ev[a.leg] = {"ok": ok, "cmd": cmd, "expect": expect, "exit": rc, "seq": seq,
                 "at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                 "output_sha256": hashlib.sha256(out.encode()).hexdigest(), "excerpt": excerpt}
    entry["data"]["checks_negative_tested"] = negtested_count(entry)
    save(root, data)
    if not ok:
        sys.stderr.write(f"REFUSED ({a.leg}): {why}\n")
        for ln in excerpt:
            sys.stderr.write(f"    {ln}\n")
        return 1
    print(f"negtest {a.check} {a.leg}: exit {rc}, evidence recorded. "
          f"checks_negative_tested = {entry['data']['checks_negative_tested']}")
    return 0


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
    p.add_argument("--since", default=None,
                   help="focus mode: a commit, or `last-audit`. Scanners flag files changed since it")
    p.set_defaults(fn=cmd_init)

    p = sub.add_parser("negtest"); p.add_argument("leg", choices=["red", "green"])
    p.add_argument("--check", required=True, help="a short name for the check under test")
    p.add_argument("--expect", default=None, help="red only: text the failing check must print")
    p.add_argument("--cmd", default=None, help="the check command; green defaults to red's")
    p.set_defaults(fn=cmd_negtest)

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
