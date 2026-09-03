#!/usr/bin/env python3
"""Phase 1 — classify every file under the audit root, and refuse to reconcile silently.

WHY THIS EXISTS
---------------
A sweep that greps `*.md` and `*.py` reports clean while never opening the `.parquet` every query
reads, the `.xlsx` that IS the financial model, or the `.json` presets every tool loads. Those are
routinely the most decision-relevant files in a project, and a text sweep cannot open any of them.

So coverage is computed mechanically here rather than asserted by the agent: every file lands in
examined / exempt / out-of-scope, the three must sum to the total, and files needing a non-text
method are called out by name so they cannot be quietly skipped.

Usage:
    coverage_manifest.py [--root .] [--json] [--record]

    --record   write the counts into the audit state (phase 1)

Exit codes: 0 classified · 1 files needing manual attention · 2 error
"""

# claim-scan:examples — paths in these docstrings are runtime artifacts and illustrative
# examples, not references to files that exist in this package.
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

# Classification is by path and extension. Order matters: first match wins, most specific first.
# Each rule is (predicate-substrings, extensions, class, default-state, reason).
RULES = [
    # Raw capture output from live-system audits. Extensions seen in the wild on infra/ops repos:
    # per-host stdout dumps (.txt/.out/.raw/.log), exit-status files (.status), single-line probe
    # results (.line), stderr captures (.err), and tab-separated collector output (.tsv). These are
    # DATED EVIDENCE -- verbatim records of what a host reported at capture time. They are never
    # edited after the fact, so they cannot go stale in the sense this audit hunts; what matters is
    # that they are classified rather than falling into an "other" bucket that reads as coverage.
    # Added 2026-08-26: on smc-file-writing-analysis these were 84 of 493 files (17%), every one of
    # them under artifacts/, and they were the entire reason the gate reported a blind spot.
    (("/artifacts/", "/raw/", "/captures/", "/evidence/"),
     (".status", ".line", ".err", ".raw", ".out", ".tsv"),
     "evidence", "exempt",
     "dated capture -- verbatim evidence of what a host reported at capture time"),
    # Binary/rendered deliverables. Ungreppable, so they must be audited by provenance and freshness
    # against their source, never skipped for being unreadable by a text sweep.
    (None, (".docx", ".pdf", ".html"),
     "rendered-deliverable", "examined-special",
     "audit by provenance + freshness against the source it was generated from, not by grep"),
    (("/.git/", "/__pycache__/", "/node_modules/", "/.venv/", "/.pytest_cache/",
      "/.ruff_cache/", "/.mypy_cache/", "/.tox/", "/.gradle/", "/.serena/",
      ".DS_Store", "/target/", "/.next/", "/.cache/", "node-compile-cache/",
      "/.terraform/", "/vendor/", "/.bundle/"), None,
     "machine-state", "exempt", "machine state, not project content"),
    # Vendored third-party trees — Ansible Galaxy collections, bundled deps. Not yours to audit,
    # and on one real infra repo they were 712 of 999 unclassified files.
    (("collections/ansible_collections/", "/site-packages/", "/third_party/",
      "/external/", "/.venv/"), None,
     "vendored", "exempt", "third-party code — not this project's to fix"),
    # Key material. Classified so it is never silently skipped, and flagged DO-NOT-READ so nobody
    # resolves the gap by opening it.
    ((".id_rsa", ".pem", ".key", "id_ed25519"), (".pem", ".key", ".p12", ".pfx", ".crt", ".pub"),
     "key-material", "examined-special",
     "DO NOT READ VALUES — check only that referenced hosts/paths still exist"),
    # Tooling config: real files, rarely a staleness risk, but they must be CLASSIFIED rather than
    # falling to "other" — an unclassified bulk is a coverage blind spot wearing a tidy label.
    ((".gitignore", ".gitattributes", ".editorconfig", ".watchmanconfig", ".dockerignore",
      ".gitmodules", ".mise.toml", ".python-version", ".nvmrc"), None,
     "tooling-config", "examined", "check referenced paths still exist"),
    (("/archive/", "/snapshots/", ".bak"), None,
     "archive", "exempt", "archives are supposed to contain superseded figures"),
    # Dated capture directories are evidence, not config, even when the files are .json. Without
    # the "-snapshots/" patterns this rule missed 19 immutable register captures on a real project
    # and routed them to "parse this config" — which is both wasted effort and an invitation to
    # edit something that must never be edited.
    (("source-captures/", "/fixtures/", "/cassettes/", "-snapshots/", "/snapshots/",
      "-captures/"), None,
     "evidence", "exempt", "verbatim evidence — byte-compare instead of auditing content"),
    (("/.ai-context/", "graphify-out/", "repomix-output"), None,
     "generated-context", "exempt", "regenerated, not audited"),
    (("CHANGELOG.md",), None,
     "audit-trail", "exempt", "append-only; historical entries are correct as written"),
    (("/.remember/",), None,
     "session-buffer", "exempt", "transient session state"),
    ((), (".eml", ".msg"),
     "correspondence-record", "exempt", "inbound records are verbatim evidence — never edited"),
    ((), (".docx", ".doc", ".pptx", ".ppt", ".odt", ".ods"),
     "office-document", "examined-special", "cannot be grepped — open it, or convert and read"),
    ((), (".parquet", ".xlsx", ".xls", ".db", ".sqlite", ".sqlite3", ".duckdb"),
     "tabular-binary", "examined-special", "cannot be grepped — provenance/schema/freshness"),
    ((), (".csv", ".tsv"),
     "tabular-text", "examined-special", "check derivation and row counts, not just text"),
    (("AGENTS.md", "CLAUDE.md", ".cursor/rules"), None,
     "agent-governance", "examined", ""),
    (("AI_NAVIGATION.md", "context-map.yaml", "docs/README.md"), None,
     "routing", "examined", ""),
    ((".archcore/",), None, "durable-decisions", "examined", ""),
    (("docs/",), None, "knowledge-base", "examined", ""),
    (("process/", "runbook"), None, "process", "examined", ""),
    (("justfile", "Justfile", "Makefile", "Taskfile.yml"), None,
     "task-runner", "examined", ""),
    (("correspondence/",), None, "correspondence", "examined", ""),
    ((), (".lock",), "dependency-lock", "examined", ""),
    ((), (".ipynb",), "notebook", "examined-special", "outputs may predate current code"),
    ((), (".tf", ".tfvars"), "iac", "examined", ""),
    # Templates are CODE. In infra projects they are where the silent failure lives: a renamed
    # variable still renders, still exits 0, and quietly produces the wrong config.
    ((), (".j2", ".jinja", ".jinja2", ".tmpl", ".tpl", ".mustache", ".erb"),
     "template", "examined", "a renamed variable renders silently — trace both directions"),
    ((), (".py", ".sh", ".ts", ".js", ".go", ".rb", ".rs", ".java", ".ps1", ".bat"),
     "code", "examined", ""),
    ((), (".service", ".conf", ".cfg", ".inventory", ".properties", ".env"),
     "runtime-config", "examined", "check referenced hosts, paths and units still exist"),
    (("COPYING", "LICENSE", "LICENCE", "NOTICE"), (".license",),
     "licence", "exempt", "licence text, not a project claim"),
    ((), (".zip", ".tar", ".gz", ".tgz", ".7z"),
     "compressed", "exempt", "opaque bundle — audit its source, not the archive"),
    ((), (".yaml", ".yml", ".json", ".toml", ".ini"),
     "structured-config", "examined-special", "parse with a strict loader; do not read as text"),
    ((), (".md", ".rst", ".txt"), "prose", "examined", ""),
    ((), (".png", ".jpg", ".jpeg", ".svg", ".pdf", ".gif"),
     "media", "examined-special", "open and look — an undated diagram is a finding"),
]

SPECIAL_METHOD = {
    "key-material": "DO NOT READ VALUES — verify referenced hosts/paths only",
    "office-document": "open it (or convert to text) — figures inside are invisible to every grep",
    "tabular-binary": "provenance → schema → row count → freshness against SOURCE, not mtime",
    "tabular-text": "header + row count + derivation; confirm the source is still current",
    "structured-config": "parse with a strict loader; check duplicate keys and misplaced keys",
    "notebook": "compare output cells against current code",
    "media": "open it; check for removed components and missing capture dates",
}


# A timestamp in the FILENAME is the generalisable signal that a file is a dated capture, and it
# generalises past any one project's directory names. Matched before the extension rules, because
# `sevs-criteria-20260810_2005.json` is evidence first and JSON second — classifying it as config
# sends an auditor to "parse this" for a file that must never be edited at all.
# Covers `-YYYYMMDD_hhmm`, `-YYYYMMDD`, and `-YYYY-MM-DD` in the stem.
DATED_STEM = re.compile(r"[-_](?:\d{8}(?:_\d{4,6})?|\d{4}-\d{2}-\d{2})(?:[-_.]|$)")

# Directories whose dated files are working output rather than evidence — do not exempt these.
NOT_EVIDENCE_DIRS = ("/reports/", "/logs/", "/output/", "/build/", "/dist/")


def classify(rel: str) -> tuple[str, str, str]:
    p = "/" + rel
    ext = Path(rel).suffix.lower()

    if DATED_STEM.search(Path(rel).stem) and not any(d in p for d in NOT_EVIDENCE_DIRS):
        return ("evidence", "exempt",
                "dated capture — verbatim evidence of what a source said on that date")

    for subs, exts, cls, state, reason in RULES:
        if subs and any(s in p for s in subs):
            return cls, state, reason
        if exts and ext in exts:
            return cls, state, reason
    return "other", "examined", ""


AUDIT_SCRATCH = (".staleness-audit/", ".staleness-audit-snapshot-")


def _is_audit_scratch(rel: str) -> bool:
    """True for this skill's own snapshot/receipt files, which are never project files."""
    return rel.startswith(AUDIT_SCRATCH) or any(("/" + m) in rel for m in AUDIT_SCRATCH)


def list_files(root: Path, scope: str | None) -> list[str]:
    try:
        # -o --exclude-standard matches snapshot_worktree.sh: include untracked-but-not-ignored
        # files, exclude gitignored ones. Without -o, a project whose files are all untracked
        # returns EMPTY here, silently falls through to the rglob branch below, and that branch
        # has no gitignore awareness -- so the audit's own scratch gets classified as project
        # files. Found 2026-08-26 on smc-file-writing-analysis (0 tracked files, 486 untracked).
        out = subprocess.run(["git", "ls-files", "-c", "-o", "--exclude-standard"],
                             cwd=root, capture_output=True, text=True, timeout=60)
        if out.returncode == 0 and out.stdout.strip():
            files = [l.strip() for l in out.stdout.splitlines() if l.strip()]
        else:
            raise RuntimeError
    except (OSError, subprocess.SubprocessError, RuntimeError):
        # AUDIT_SCRATCH: never classify this audit's own working files as project files.
        # The Phase 0 snapshot is a full copy of the tree, so without this the corpus is
        # doubled and every percentage is computed against a corpus half made of itself.
        files = [str(p.relative_to(root)) for p in root.rglob("*")
                 if p.is_file() and not _is_audit_scratch(str(p.relative_to(root)))
                 and ".git/" not in str(p)]
    files = [f for f in files if not _is_audit_scratch(f)]
    if scope:
        files = [f for f in files if f.startswith(scope)]
    return sorted(files)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--root", default=".")
    ap.add_argument("--scope", default=None, help="restrict to a subtree")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--record", action="store_true", help="write counts into audit state")
    a = ap.parse_args()

    root = Path(a.root).resolve()
    files = list_files(root, a.scope)
    if not files:
        sys.stderr.write(f"ERROR: no files found under {root}\n")
        return 2

    by_class: dict[str, list[str]] = defaultdict(list)
    states = {"examined": 0, "examined-special": 0, "exempt": 0}
    reasons: dict[str, str] = {}
    for f in files:
        cls, state, reason = classify(f)
        by_class[cls].append(f)
        states[state] = states.get(state, 0) + 1
        if reason:
            reasons[cls] = reason

    examined = states["examined"] + states["examined-special"]
    exempt = states["exempt"]
    total = len(files)
    special = {c: v for c, v in by_class.items() if c in SPECIAL_METHOD}

    if a.json:
        print(json.dumps({
            "total": total, "examined": examined, "exempt": exempt, "out_of_scope": 0,
            "by_class": {k: len(v) for k, v in sorted(by_class.items())},
            "needs_special_method": {k: v for k, v in special.items()},
            "reasons": reasons,
            "unclassified": len(by_class.get("other", [])),
            "unclassified_files": by_class.get("other", [])[:50],
        }, indent=2))
    else:
        print(f"Coverage manifest — {root}" + (f" (scope: {a.scope})" if a.scope else ""))
        print("=" * 78)
        for cls in sorted(by_class):
            note = f"   [{SPECIAL_METHOD[cls]}]" if cls in SPECIAL_METHOD else \
                   (f"   — {reasons[cls]}" if cls in reasons else "")
            print(f"  {cls:22s} {len(by_class[cls]):5d}{note}")
        print("-" * 78)
        print(f"  {'TOTAL':22s} {total:5d}")
        print(f"  {'examined':22s} {examined:5d}")
        print(f"  {'exempt':22s} {exempt:5d}")
        print(f"  {'reconciles':22s} {'YES' if examined + exempt == total else 'NO'}")

        if special:
            print()
            print("FILES A TEXT SWEEP CANNOT AUDIT — do not skip these:")
            for cls, fl in sorted(special.items()):
                print(f"\n  {cls} ({len(fl)}) — {SPECIAL_METHOD[cls]}")
                for f in fl[:20]:
                    print(f"      {f}")
                if len(fl) > 20:
                    print(f"      … and {len(fl) - 20} more")

    if a.record:
        rc = subprocess.run([sys.executable, str(Path(__file__).parent / "audit_state.py"),
                             "--root", str(root), "record", "--phase", "1",
                             "--key", "files_total", "--value", str(total),
                             "--key", "files_examined", "--value", str(examined),
                             "--key", "files_exempt", "--value", str(exempt),
                             "--key", "files_out_of_scope", "--value", "0"])
        if rc.returncode != 0:
            return 2

    unclassified = len(by_class.get("other", []))
    pct = (unclassified / total * 100) if total else 0.0
    # Guarded: printing this in --json mode appends prose after the JSON document and every
    # downstream parser dies on "Extra data". Machine output must stay machine-readable.
    if unclassified and not a.json:
        print()
        if pct >= 5.0:
            print(f"!! {unclassified} files ({pct:.1f}%) are UNCLASSIFIED — this is a coverage blind "
                  f"spot, not a tidy remainder.")
            print("   The rule list does not cover this project's shape. Extend RULES in this script")
            print("   (and patterns/coverage-manifest.md) before trusting the accounting above.")
        else:
            print(f"   {unclassified} files ({pct:.1f}%) unclassified — inspect and classify:")
        for f in by_class.get("other", [])[:15]:
            print(f"      {f}")
        if unclassified > 15:
            print(f"      … and {unclassified - 15} more")

    return 1 if (special or pct >= 5.0) else 0


if __name__ == "__main__":
    sys.exit(main())
