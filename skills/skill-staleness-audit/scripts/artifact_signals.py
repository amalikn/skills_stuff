#!/usr/bin/env python3
"""Phase 4 — force a per-artifact verdict, and refuse to accept silence as coverage.

WHY THIS EXISTS
---------------
Phase 4 is the pass that finds what a grep structurally cannot: a back-solve against a floor that
moved, an output shape encoding a superseded rule, a projection assuming a year that will not
arrive. Five of the nine defect patterns produce NO STRING TO MATCH.

It is also the phase agents skip, because it is slow and a clean grep feels like completion. So
this emits a worksheet with one row per artifact and a signal scan to prioritise them — and the
count of rows becomes the denominator the Phase 7 gate checks `artifacts_reasoned` against.
Skipping an artifact is fine; skipping the QUESTION is not.

Usage:
    artifact_signals.py [--root .] [--signal VALUE ...] [--out FILE] [--record]

    --signal   a value under audit (e.g. 2500 15% RECOMMENDED). Repeatable.
    --record   write artifacts_total into the audit state (phase 4)

Exit codes: 0 worksheet written · 2 error
"""

from __future__ import annotations

import argparse
import ast
import re
import subprocess
import sys
from pathlib import Path

CODE_EXT = {".py", ".sh", ".ts", ".js", ".go", ".rb", ".rs", ".java", ".r", ".sql"}
GEN_EXT = {".py", ".sh", ".js", ".ts"}

EXEMPT = ("/.git/", "__pycache__", "/node_modules/", "/.venv/", "/archive/",
          "-snapshots/", "source-captures/", "/.ai-context/")

# Assumption signals — the second Phase 4 prompt, "does it assume continuity, completeness or
# availability that is no longer true?" These words are where that assumption usually surfaces.
CONTINUITY = re.compile(
    r"\b(steady[ _-]?state|per[ _-]?year|annual|next year|ongoing|forever|always|"
    r"recurring|renew|indefinit)", re.I)
BACKSOLVE = re.compile(
    r"\b(max[ _]?bid|break[ _-]?even|target|solve|back[ _-]?solve|required|ceiling|"
    r"threshold|floor|minimum|budget)", re.I)
WRITES = re.compile(r"\b(open\([^)]*['\"][wa]|write_text|to_csv|to_parquet|savefig|dump\()")



# AUDIT_SCRATCH: this skill's own snapshot/receipt files are never project files.
# Prefix-aware because the snapshot dir is `.staleness-audit-snapshot-<stamp>`.
# Matches inverse_sweep.py, which already did this; claim_scan/artifact_signals did not,
# so every claim was counted twice and the corpus was half a copy of itself (2026-08-26).
def _is_audit_scratch(rel: str) -> bool:
    parts = str(rel).split("/")
    return any(p == ".staleness-audit" or p.startswith(".staleness-audit-snapshot")
               for p in parts)

def list_files(root: Path) -> list[str]:
    files: list[str] = []
    try:
        out = subprocess.run(["git", "ls-files", "-c", "-o", "--exclude-standard"],
                             cwd=root, capture_output=True,
                             text=True, timeout=60)
        if out.returncode == 0 and out.stdout.strip():
            files = [l.strip() for l in out.stdout.splitlines() if l.strip()]
    except (OSError, subprocess.SubprocessError):
        pass
    # AUDIT_SCRATCH filtering must apply to BOTH branches. It sat only on the rglob fallback until
    # 2026-08-28, and the git branch returned early -- so in any project that does not gitignore
    # `.staleness-audit-snapshot-*`, `git ls-files -o` listed the Phase 0 snapshot and the corpus was
    # half a copy of itself again. That is the SAME defect the comment above records as already fixed:
    # it was fixed in the fallback nobody takes. coverage_manifest.py filters after both branches,
    # which is why its count was right while this one's was doubled. Match it.
    if files:
        return [f for f in files if not _is_audit_scratch(f)]
    return [str(p.relative_to(root)) for p in root.rglob("*")
            if p.is_file() and not _is_audit_scratch(p.relative_to(root))]


def summarise(path: Path) -> str:
    try:
        src = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return "(unreadable)"
    if path.suffix == ".py":
        try:
            doc = ast.get_docstring(ast.parse(src))
            if doc:
                return doc.strip().splitlines()[0][:95]
        except (SyntaxError, ValueError):
            pass
    for line in src.splitlines()[:15]:
        t = line.strip().lstrip("#!").strip()
        if t and not t.startswith(("#!/", "from ", "import ", "set -", "---")):
            return t[:95]
    return "(no description)"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--root", default=".")
    ap.add_argument("--signal", action="append", default=[])
    ap.add_argument("--out", default=None)
    ap.add_argument("--record", action="store_true")
    a = ap.parse_args()

    root = Path(a.root).resolve()
    artifacts = []
    for rel in sorted(list_files(root)):
        if any(e in "/" + rel for e in EXEMPT):
            continue
        if Path(rel).suffix.lower() not in CODE_EXT:
            continue
        fp = root / rel
        try:
            src = fp.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        flags = []
        for s in a.signal:
            if s.lower() in src.lower():
                flags.append(f"signal:{s}")
        if BACKSOLVE.search(src):
            flags.append("back-solve?")
        if CONTINUITY.search(src):
            flags.append("continuity?")
        if fp.suffix in GEN_EXT and WRITES.search(src):
            flags.append("GENERATOR")
        artifacts.append((rel, summarise(fp), flags))

    lines = [
        "# Phase 4 — per-artifact reasoning worksheet",
        "",
        "**One line per artifact. Skipping an artifact is fine; skipping the QUESTION is not.**",
        "",
        "Ask both prompts of each:",
        "",
        "1. Does it print or compute anything whose **meaning** changed, though its wording did not?",
        "2. Does it assume **continuity, completeness, or availability** that is no longer true?",
        "",
        "`GENERATOR` rows get a third: **would running it now revert something?** Run it and diff —",
        "a clean diff proves the output is current and proves nothing about the generator's assumptions.",
        "",
        "Flags are a PRIORITISATION HINT, not an answer. An unflagged artifact still needs a verdict,",
        "and \"clear\" needs a reason — an unfalsifiable verdict is not a verdict.",
        "",
        f"Artifacts: **{len(artifacts)}**",
        "",
        "| Artifact | What it is | Flags | Verdict (fill in) |",
        "|---|---|---|---|",
    ]
    for rel, desc, flags in artifacts:
        lines.append(f"| `{rel}` | {desc.replace('|', '\\|')} | {' '.join(flags) or '—'} | |")

    out = "\n".join(lines) + "\n"
    if a.out:
        Path(a.out).write_text(out, encoding="utf-8")
        print(f"wrote {a.out} — {len(artifacts)} artifacts")
    else:
        print(out)

    if a.record:
        subprocess.run([sys.executable, str(Path(__file__).parent / "audit_state.py"),
                        "--root", str(root), "record", "--phase", "4",
                        "--key", "artifacts_total", "--value", str(len(artifacts))])
        print(f"\nRecorded artifacts_total={len(artifacts)}. The gate compares "
              f"artifacts_reasoned against it — record that when the worksheet is filled.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
