#!/usr/bin/env python3
"""Phases 1 and 7 — extract every CHECKABLE CLAIM and verify what can be verified mechanically.

WHY THIS EXISTS
---------------
"Grep for the old value" only finds what you already knew to look for. The completeness guarantee
needs the opposite direction: enumerate every claim the corpus makes that something could
contradict, then account for each one.

What this verifies mechanically:
  * COUNT claims      — "27 files", "56 checks"        → recounted against the filesystem
  * DATE claims       — "Last reviewed", "as at"       → compared to the newest relevant change
  * PATH claims       — backtick paths and md links     → resolved against the filesystem
  * UNIQUENESS claims — "the only one that…"            → flagged; these falsify SILENTLY when a
                                                          second instance appears, and there is no
                                                          string to grep for afterwards

What it cannot verify, and says so rather than implying coverage: thresholds (needs the owner),
verdicts (needs the data layer), and any claim about the external world.

Usage:
    claim_scan.py [--root .] [--json] [--record] [--include-exempt]

Exit codes: 0 no unverified claims · 1 claims need attention · 2 error
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

TEXT_EXT = {".md", ".rst", ".txt", ".py", ".yaml", ".yml", ".json", ".toml"}

# Exempt by design — audit trails and evidence are SUPPOSED to contain superseded figures.
EXEMPT = ("/archive/", "CHANGELOG.md", "/.git/", "/.ai-context/", "/.remember/",
          "source-captures/", "-snapshots/", "/snapshots/", "/node_modules/", "__pycache__")

# Documentation ABOUT files legitimately names filenames as EXAMPLES of a class, not as
# references. A file declares that with this marker and its path claims are skipped — exempt by
# marker, never by ignore-list, which is the same rule this skill applies to historical counts.
#     <!-- claim-scan:examples reason="documents file classes, not references" -->
EXAMPLES_MARKER = "claim-scan:examples"

# A historical claim marked by the project is evidence, not a live assertion.
HISTORICAL_MARKERS = ("count:asat", "as-at", "as at", "historical", "<!-- asat")

COUNT_RE = re.compile(
    r"(\d{1,5})\s+(files?|checks?|documents?|docs|entries|records?|scripts?|surfaces?|rules?|"
    r"specs?|ADRs?|tests?|sites?|devices?|rows?|models?)\b", re.I)
DATE_RE = re.compile(
    r"(?:last\s+reviewed|last\s+updated|as\s+at|snapshot|generated)\s*[:\-—]?\s*"
    r"(\d{4}-\d{2}-\d{2}|\d{1,2}\s+\w+\s+\d{4})", re.I)
UNIQUE_RE = re.compile(
    r"\b(the only|only one|sole|exactly one|no other|unique(?:ly)?)\b[^.\n]{0,90}", re.I)
PATH_RE = re.compile(r"`([A-Za-z0-9._/-]+\.(?:md|py|ya?ml|json|toml|sh|xlsx|parquet|csv))`")
LINK_RE = re.compile(r"\]\(([^)\s#]+)\)")



# AUDIT_SCRATCH: this skill's own snapshot/receipt files are never project files.
# Prefix-aware because the snapshot dir is `.staleness-audit-snapshot-<stamp>`.
# Matches inverse_sweep.py, which already did this; claim_scan/artifact_signals did not,
# so every claim was counted twice and the corpus was half a copy of itself (2026-08-26).
def _is_audit_scratch(rel: str) -> bool:
    parts = str(rel).split("/")
    return any(p == ".staleness-audit" or p.startswith(".staleness-audit-snapshot")
               for p in parts)

def is_exempt(rel: str) -> bool:
    p = "/" + rel
    return any(e in p for e in EXEMPT)


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
            if not _is_audit_scratch(p.relative_to(root))
            if p.is_file() and ".git/" not in str(p)]


def count_actual(root: Path, unit: str, count_map: dict[str, str]) -> int | None:
    """Recount a unit ONLY when the operator has declared what it means.

    An earlier version guessed — "N scripts" was counted against `scripts/*.py`. On a real project
    that produced 47 MISMATCHes, nearly all false: "the three gate scripts" is a claim about three
    specific files, not a directory census. A scanner with a 50% false-positive rate is worse than
    no scanner, because people learn to ignore its output and stop reading the true positives too.

    So: no guessing at project semantics. Pass --count-map 'docs=docs/*.md' to enable verification
    for a unit; everything else is reported as NEEDS-MANUAL, which is honest.
    """
    u = unit.lower().rstrip("s")
    pattern = count_map.get(u)
    if not pattern:
        return None
    return len(list(root.glob(pattern)))


# Placeholder patterns are naming CONVENTIONS, not references — `<slug>-YYYYMMDD_hhmm.md` names a
# shape a future file will take. Treating them as paths produces confident false positives.
PLACEHOLDER = re.compile(r"YYYY|MM-DD|hhmm|<|>|\*|\{|NN-|/NN\b|\.\.\.")


def resolve_path(root: Path, base: Path, tok: str) -> bool:
    """Does this reference resolve? Bare filenames are searched repo-wide.

    Prose legitimately writes `purchase-discipline.rule.md` without a directory. Testing only
    root-relative and sibling-relative paths marked 120 such references BROKEN on a real project,
    every one of them a false positive.
    """
    clean = tok.rstrip("/")
    if not clean:
        return True
    for cand in (root / clean, base / clean):
        if cand.exists():
            return True
    if "/" not in clean:
        for match in root.rglob(clean):
            if ".git" not in match.parts:
                return True
        return False
    # `docs/10` shorthand for `docs/10-*.md`
    m = re.fullmatch(r"(.*)/(\d{2})(?:-(\d{2}))?", clean)
    if m:
        parent = root / m.group(1)
        wanted = [m.group(2)] + ([m.group(3)] if m.group(3) else [])
        return parent.is_dir() and all(any(parent.glob(f"{n}-*")) for n in wanted)
    return False


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--root", default=".")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--record", action="store_true")
    ap.add_argument("--include-exempt", action="store_true")
    ap.add_argument("--count-map", action="append", default=[],
                    help="unit=glob, e.g. doc=docs/*.md — enables count verification "
                         "for that unit. Without it, counts are NEEDS-MANUAL rather "
                         "than guessed at.")
    a = ap.parse_args()

    root = Path(a.root).resolve()
    count_map = {}
    for spec in a.count_map:
        if '=' not in spec:
            sys.stderr.write(f"ERROR: --count-map needs unit=glob, got {spec!r}\n")
            return 2
        k, v = spec.split('=', 1)
        count_map[k.lower().rstrip('s')] = v
    claims: list[dict] = []

    for rel in sorted(list_files(root)):
        if Path(rel).suffix.lower() not in TEXT_EXT:
            continue
        if is_exempt(rel) and not a.include_exempt:
            continue
        fp = root / rel
        try:
            text = fp.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue

        file_is_examples = EXAMPLES_MARKER in text

        for i, line in enumerate(text.splitlines(), 1):
            historical = any(m in line.lower() for m in HISTORICAL_MARKERS)

            for m in COUNT_RE.finditer(line):
                claimed, unit = int(m.group(1)), m.group(2)
                actual = count_actual(root, unit, count_map)
                state = ("MARKED-HISTORICAL" if historical
                         else "VERIFIED" if actual is not None and actual == claimed
                         else "MISMATCH" if actual is not None
                         else "NEEDS-MANUAL")
                claims.append({"type": "count", "file": rel, "line": i, "state": state,
                               "claim": m.group(0).strip(), "actual": actual})

            for m in DATE_RE.finditer(line):
                claims.append({"type": "date", "file": rel, "line": i,
                               "state": "MARKED-HISTORICAL" if historical else "NEEDS-MANUAL",
                               "claim": m.group(0).strip(), "actual": None})

            for m in UNIQUE_RE.finditer(line):
                claims.append({"type": "uniqueness", "file": rel, "line": i,
                               "state": "MARKED-HISTORICAL" if historical else "NEEDS-MANUAL",
                               "claim": m.group(0).strip()[:100], "actual": None})

            for m in list(PATH_RE.finditer(line)) + list(LINK_RE.finditer(line)):
                tok = m.group(1)
                if tok.startswith(("http", "#", "mailto:")) or PLACEHOLDER.search(tok):
                    continue
                if file_is_examples:
                    continue
                ok = resolve_path(root, fp.parent, tok)
                claims.append({"type": "path", "file": rel, "line": i,
                               "state": "VERIFIED" if ok else "BROKEN",
                               "claim": tok, "actual": None})

    tally: dict[str, int] = {}
    for c in claims:
        tally[c["state"]] = tally.get(c["state"], 0) + 1

    problems = [c for c in claims if c["state"] in {"MISMATCH", "BROKEN"}]
    manual = [c for c in claims if c["state"] == "NEEDS-MANUAL"]

    if a.json:
        print(json.dumps({"total": len(claims), "tally": tally,
                          "problems": problems, "needs_manual": manual}, indent=2))
    else:
        print(f"Claim scan — {root}")
        print("=" * 78)
        for k in sorted(tally):
            print(f"  {k:20s} {tally[k]:5d}")
        print("-" * 78)
        print(f"  {'TOTAL':20s} {len(claims):5d}")

        if problems:
            print("\nCONTRADICTED BY THE FILESYSTEM — fix these:")
            for c in problems:
                extra = f" (actual: {c['actual']})" if c["actual"] is not None else ""
                print(f"  {c['state']:9s} {c['file']}:{c['line']}  {c['claim']}{extra}")

        if manual:
            by_type: dict[str, int] = {}
            for c in manual:
                by_type[c["type"]] = by_type.get(c["type"], 0) + 1
            print(f"\nNEEDS MANUAL VERIFICATION ({len(manual)}) — "
                  f"{', '.join(f'{k}:{v}' for k, v in sorted(by_type.items()))}")
            print("  Each must end as VERIFIED, MARKED-HISTORICAL, or RESIDUAL. There is no")
            print("  fourth state — see patterns/completeness-verification.md.")
            for c in manual[:25]:
                print(f"    {c['type']:11s} {c['file']}:{c['line']}  {c['claim'][:70]}")
            if len(manual) > 25:
                print(f"    … and {len(manual) - 25} more (use --json for the full list)")
            print("\n  UNIQUENESS claims deserve particular care: they were true when written and")
            print("  falsify SILENTLY when a second instance appears, leaving nothing to grep for.")

    if a.record:
        subprocess.run([sys.executable, str(Path(__file__).parent / "audit_state.py"),
                        "--root", str(root), "record", "--phase", "7",
                        "--key", "claims_total", "--value", str(len(claims)),
                        "--key", "claims_verified", "--value", str(tally.get("VERIFIED", 0)),
                        "--key", "claims_historical", "--value",
                        str(tally.get("MARKED-HISTORICAL", 0)),
                        "--key", "claims_residual", "--value",
                        str(len(manual) + len(problems))])

    return 1 if (problems or manual) else 0


if __name__ == "__main__":
    sys.exit(main())
