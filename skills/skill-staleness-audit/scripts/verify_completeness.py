#!/usr/bin/env python3
"""Phase 7 — the exit gate. Refuses to pass an audit that cannot show its work.

WHY THIS EXISTS
---------------
Phases 0–6 find and fix. Without a gate, the audit ends on an agent's assertion that it is
complete — and assertions nobody checked are how the defects got there in the first place.

This checks the things that are mechanically checkable and BLOCKS on them:
  * every phase has a receipt, and the receipts reconcile arithmetically
  * coverage: examined + exempt + out-of-scope == total files
  * claims: verified + historical + residual == total claims
  * artifacts_reasoned == artifacts_total       (Phase 4 was not skipped)
  * checks_negative_tested == checks_added      (no check that cannot fail)
  * no old value survives outside audit-trail surfaces
  * every governed YAML/JSON parses, with no duplicate keys
  * evidence still byte-matches its committed form

What it CANNOT check, and says so rather than implying coverage: whether any claim about the
external world is still true. That is stated in the output so the report cannot overclaim.

Usage:
    verify_completeness.py [--root .] [--old-value V ...] [--suite "just check"] [--json]

Exit codes: 0 gate passed · 1 gate FAILED · 2 error
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

SWEEP_EXEMPT = ("/archive/", "CHANGELOG.md", "/.git/", "/.ai-context/", "/.remember/",
                "source-captures/", "-snapshots/", "/snapshots/", "__pycache__",
                "/node_modules/", "/.venv/", ".staleness-audit/",
                # the snapshot dir is `.staleness-audit-snapshot-<stamp>/` -- matched NEITHER
                # ".staleness-audit/" nor "-snapshots/", so the gate scanned its own pre-fix
                # copy for surviving old values and would fail on its own scratch (2026-08-26)
                ".staleness-audit-snapshot",
                # Point-in-time backup trees. A backup records what a file SAID on a date; rewriting it to clear a
                # surviving old value destroys the only evidence of the pre-change state, which is the same reason
                # `source-captures/` is exempt. Added 2026-09-03 after `.agent-stack-update-backups/<stamp>/` failed
                # the gate on a repo whose live tree was fully corrected -- and where an earlier session had already
                # modified one such backup by accident and had to revert it.
                "-update-backups/", "/backups/", ".backup/")

HERE = Path(__file__).resolve().parent


def run(cmd: list[str], cwd: Path) -> tuple[int, str]:
    try:
        r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=900)
        return r.returncode, (r.stdout or "") + (r.stderr or "")
    except (OSError, subprocess.SubprocessError) as e:
        return 127, str(e)


def check_state(root: Path, fails: list[str], warns: list[str]) -> dict:
    rc, out = run([sys.executable, str(HERE / "audit_state.py"),
                   "--root", str(root), "status", "--json"], root)
    if rc == 2 or not out.strip().startswith("{"):
        fails.append("no audit state found — phases were never recorded. Run: just audit-init")
        return {}
    data = json.loads(out)
    for issue in data.get("reconcile_issues", []):
        fails.append(f"state: {issue}")
    for n in range(0, 8):
        if str(n) not in data.get("phases", {}):
            fails.append(f"state: phase {n} has no receipt — it was skipped or never recorded")
    return data


def strip_jsonc_comments(raw: str) -> str:
    r"""Remove // and /* */ comments from JSONC, WITHOUT touching string literals.

    A regex cannot do this. `"@/*": ["./src/*"]` is an ordinary tsconfig path alias, and `/\*.*?\*/` starts matching inside that string and runs to the next
    `*/` anywhere later in the file, silently destroying structure — the parse then fails with "Invalid control character", pointing at a line that is perfectly
    fine. Observed 2026-09-03 while adding JSONC support, which is the skill's own rule about round-trip fidelity probes arriving by the short route.

    So: one pass, tracking whether we are inside a string and whether the previous character escaped this one. Comments are replaced by a space rather than
    deleted so byte offsets in any subsequent error message stay near the truth.
    """
    out = []
    i, n = 0, len(raw)
    in_str = esc = False
    while i < n:
        c = raw[i]
        if in_str:
            out.append(c)
            if esc:
                esc = False
            elif c == "\\":
                esc = True
            elif c == '"':
                in_str = False
            i += 1
            continue
        if c == '"':
            in_str = True
            out.append(c)
            i += 1
            continue
        if c == "/" and i + 1 < n and raw[i + 1] == "/":
            while i < n and raw[i] != "\n":
                i += 1
            continue
        if c == "/" and i + 1 < n and raw[i + 1] == "*":
            j = raw.find("*/", i + 2)
            i = n if j == -1 else j + 2
            out.append(" ")
            continue
        out.append(c)
        i += 1
    return "".join(out)


def check_old_values(root: Path, values: list[str], fails: list[str]) -> int:
    hits = 0
    if not values:
        return 0
    pattern = re.compile("|".join(re.escape(v) for v in values))
    for p in root.rglob("*"):
        if not p.is_file() or p.suffix.lower() not in {".md", ".py", ".yaml", ".yml", ".json"}:
            continue
        rel = "/" + str(p.relative_to(root))
        if any(e in rel for e in SWEEP_EXEMPT):
            continue
        try:
            for i, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
                if pattern.search(line):
                    fails.append(f"old value survives: {p.relative_to(root)}:{i}")
                    hits += 1
        except (OSError, UnicodeDecodeError):
            continue
    return hits


def check_structured(root: Path, fails: list[str], warns: list[str]) -> int:
    """Parse every governed YAML/JSON. Duplicate keys parse fine and silently discard a block."""
    checked = 0
    try:
        import yaml

        class NoDup(yaml.SafeLoader):
            pass

        def mapping(loader, node, deep=False):
            seen = set()
            for k, _ in node.value:
                key = loader.construct_object(k, deep=deep)
                if key in seen:
                    raise ValueError(f"duplicate key {key!r}")
                seen.add(key)
            return yaml.SafeLoader.construct_mapping(loader, node, deep)

        NoDup.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, mapping)
        has_yaml = True
    except ImportError:
        has_yaml = False
        warns.append("PyYAML absent — YAML duplicate-key detection SKIPPED, not passed")

    for p in root.rglob("*"):
        if not p.is_file():
            continue
        rel = "/" + str(p.relative_to(root))
        if any(e in rel for e in SWEEP_EXEMPT):
            continue
        try:
            if p.suffix == ".json":
                raw = p.read_text(encoding="utf-8")
                try:
                    json.loads(raw)
                except json.JSONDecodeError:
                    # JSONC. tsconfig.json, components.json and most editor/tooling configs carry // comments and
                    # trailing commas BY CONVENTION -- the tools that read them accept it, and strict json.loads does
                    # not. Reporting that as a structural defect is a false positive that survived three audits on one
                    # repo as a permanently unaccepted residual. Strip comments and trailing commas, then re-parse: a
                    # file that still fails is genuinely malformed, which is the finding worth having.
                    stripped = re.sub(r",(\s*[}\]])", r"\1", strip_jsonc_comments(raw))
                    json.loads(stripped)
                checked += 1
            elif p.suffix in {".yaml", ".yml"} and has_yaml:
                yaml.load(p.read_text(encoding="utf-8"), Loader=NoDup)
                checked += 1
        except ValueError as e:
            fails.append(f"structured config: {p.relative_to(root)}: {e}")
        except Exception as e:  # noqa: BLE001 - report, do not crash the gate
            fails.append(f"structured config: {p.relative_to(root)}: {type(e).__name__}: {e}")
    return checked


def check_inverse_sweep(root: Path, fails: list[str], warns: list[str]) -> int:
    """Run the inverse sweep and BLOCK on it.

    Phase 7 always required this — "does anything exist that no catalog names" — and until 2026-08-12
    it was prose with nothing behind it, so a run in which it never happened still reached GATE PASSED.
    Three defects walked through that hole on a real project: a new top-level directory absent from the
    repo README, three new subdirectories with no index while every sibling had one, and an index still
    listing files by the bare names they had before they moved into a subdirectory.

    Every OTHER step of this gate was mechanical, which is precisely why the prose one was the one that
    got skipped. A gate that enforces the easy checks and trusts the hard one is not a gate.
    """
    script = Path(__file__).parent / "inverse_sweep.py"
    if not script.is_file():
        warns.append("inverse_sweep.py not found — the inverse sweep did NOT run (SKIPPED, not passed)")
        return -1
    code, out = run([sys.executable, str(script), "--root", str(root), "--record"], root)
    found = 0
    for line in out.splitlines():
        if "INVERSE SWEEP FOUND" in line:
            try:
                found = int(line.split("FOUND")[1].split("ITEM")[0].strip())
            except (IndexError, ValueError):
                found = 1
    if code != 0:
        fails.append(f"inverse sweep found {found} item(s) — the catalog and the tree disagree "
                     f"(run scripts/inverse_sweep.py for the list)")
    return found


def cleanup_snapshots(root: Path, keep: bool) -> list[str]:
    """Remove the audit's own scratch state — snapshots AND receipts — but ONLY after the gate has passed.

    WHY THIS EXISTS. `snapshot_worktree.sh` copies the entire worktree before the audit touches
    anything, which is correct: it is the safety net for a run that goes wrong. Nothing ever removed
    them. They are gitignored, so they accumulate invisibly — a project that has been audited three
    times is carrying three full copies of itself, and the next `rglob` over the tree walks all of
    them. On the run that added this, two had already piled up and were being reported back to the
    scanners as unregistered surfaces until the skip lists were patched.

    WHY ONLY ON PASS, AND WHY THAT IS NOT A DETAIL. A FAILED gate is exactly when the snapshot is
    needed — something is wrong and the pre-audit state is the thing you compare against. Deleting it
    on failure would remove the evidence at the moment it becomes useful. So: pass deletes, fail
    keeps, and `--keep-snapshot` opts out of deletion entirely.

    THE RECEIPTS GO TOO, AND LEAVING THEM WAS A BUG, NOT CAUTION. `.staleness-audit/state.json` is
    per-run scratch: it exists so the Phase 7 gate can do arithmetic on what each phase measured. Once
    the gate has PASSED and the run is written into the project's change log, it has served its whole
    purpose. Leaving it behind actively breaks the next run — `audit_state.py init` refuses to start
    while a previous state file exists, so the second audit of a project fails with "audit already in
    progress" and has to be forced. Scratch that blocks the next run is not a safety net.

    Deletion is scoped to the literal `.staleness-audit-snapshot-*` prefix and `.staleness-audit/`,
    both created by this skill, and refuses anything that is not a directory. The `.gitignore` entry
    stays — it is correct for the next run.
    """
    import shutil
    removed = []
    targets = sorted(root.glob(".staleness-audit-snapshot-*"))
    state_dir = root / ".staleness-audit"
    if state_dir.is_dir():
        targets.append(state_dir)
    for d in targets:
        if not d.is_dir():
            continue
        if keep:
            removed.append(f"KEPT {d.name} (--keep-snapshot)")
            continue
        try:
            shutil.rmtree(d)
            removed.append(f"removed {d.name}")
        except OSError as e:
            removed.append(f"could NOT remove {d.name}: {e}")
    return removed


def check_evidence(root: Path, fails: list[str], warns: list[str]) -> None:
    rc, out = run(["git", "diff", "--name-only", "HEAD"], root)
    if rc != 0:
        warns.append("git unavailable — evidence byte-comparison SKIPPED, not passed")
        return
    prefix = root.name + "/"
    for line in out.splitlines():
        rel = line.strip()
        if not rel:
            continue
        shown = rel[len(prefix):] if rel.startswith(prefix) else rel
        if any(e in "/" + shown for e in ("source-captures/", "-snapshots/", "/snapshots/")):
            fails.append(f"evidence modified: {shown} differs from its committed bytes")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--keep-snapshot", action="store_true",
                    help="do not delete .staleness-audit-snapshot-* even when the gate passes")
    ap.add_argument("--root", default=".")
    ap.add_argument("--old-value", action="append", default=[],
                    help="a value that must no longer appear outside audit trails. Repeatable.")
    ap.add_argument("--suite", default=None, help="project check command, e.g. 'just check'")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    root = Path(a.root).resolve()
    fails: list[str] = []
    warns: list[str] = []

    state = check_state(root, fails, warns)

    rc, out = run([sys.executable, str(HERE / "coverage_manifest.py"),
                   "--root", str(root), "--json"], root)
    cov = json.loads(out) if out.strip().startswith("{") else {}
    if cov:
        if cov["examined"] + cov["exempt"] != cov["total"]:
            fails.append("coverage does not reconcile")
        if cov.get("unclassified", 0) / max(cov["total"], 1) >= 0.05:
            fails.append(f"{cov['unclassified']} files unclassified — coverage blind spot")

    sweep_hits = check_old_values(root, a.old_value, fails)
    parsed = check_structured(root, fails, warns)
    inverse = check_inverse_sweep(root, fails, warns)
    check_evidence(root, fails, warns)

    suite_rc = None
    if a.suite:
        suite_rc, suite_out = run(a.suite.split(), root)
        if suite_rc != 0:
            fails.append(f"project check suite FAILED (`{a.suite}`)")
            warns.append(suite_out.strip().splitlines()[-1] if suite_out.strip() else "")

    result = {
        "passed": not fails,
        "failures": fails,
        "warnings": [w for w in warns if w],
        "coverage": cov,
        "structured_parsed": parsed,
        "old_value_hits": sweep_hits,
        "suite_exit": suite_rc,
    }

    if a.json:
        print(json.dumps(result, indent=2))
    else:
        print("=" * 78)
        print(f"COMPLETENESS GATE — {root}")
        print("=" * 78)
        if cov:
            print(f"  coverage      : {cov['examined']} examined + {cov['exempt']} exempt "
                  f"= {cov['total']} total")
        print(f"  structured    : {parsed} files parsed (duplicate keys checked)")
        print(f"  old-value hits: {sweep_hits}")
        print(f"  inverse sweep : {'NOT RUN' if inverse < 0 else str(inverse) + ' item(s)'}")
        if suite_rc is not None:
            print(f"  suite         : exit {suite_rc}")
        if warns:
            print("\n  WARNINGS (skipped, NOT passed):")
            for w in result["warnings"]:
                print(f"    ! {w}")
        if fails:
            print(f"\n  FAILURES ({len(fails)}):")
            for f in fails[:40]:
                print(f"    ✗ {f}")
            if len(fails) > 40:
                print(f"    … and {len(fails) - 40} more")
            print("\nGATE FAILED — the audit is NOT complete. Do not report it as such.")
            kept = [d.name for d in sorted(root.glob(".staleness-audit-snapshot-*")) if d.is_dir()]
            if (root / ".staleness-audit").is_dir():
                kept.append(".staleness-audit (receipts)")
            if kept:
                # Deliberate: a failed gate is exactly when the pre-audit state is worth having.
                print(f"  Snapshot(s) KEPT for diagnosis: {', '.join(kept)}")
        else:
            for line in cleanup_snapshots(root, a.keep_snapshot):
                print(f"  snapshot: {line}")
            print("\nGATE PASSED.")
            print("  Every checkable claim is verified, marked historical, or listed as residual.")
            print("  This does NOT establish that any claim about the external world is still true")
            print("  — market prices, regulations, vendor terms and third-party behaviour cannot be")
            print("  settled by reading the project. For those the audit verified the provenance")
            print("  label and as-at date only. Say so in the report.")
        print("=" * 78)

    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
