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

PATH CLASSES (2026-09-27). A path that does not resolve locally is tried against the project's own SIBLING ROOTS
before it is called broken, and what still does not resolve is split, so "residual" says something:
  VERIFIED     resolves here, or inside a declared sibling checkout (on its pinned branch when one is declared)
  ON-BOX       an absolute system path (/etc, /opt, /var, ...) that lives on a remote host, not this machine
  CONDITIONAL  a "consult when present" path: in the project's CONDITIONAL_PATHS, gitignored (created at run time),
               or on a line that says "when present" / "if present"
  BROKEN       none of the above — the finding
Sibling roots and conditional paths are read from the project's own declarations, never guessed: `SIBLING_ROOTS`,
`SIBLING_BRANCHES` and `CONDITIONAL_PATHS` in scripts/check_governance.py (parsed with `ast`, never executed; the
skill-ai-it governance-checks layer), plus --sibling-root and --conditional. On unified-network-controller 298 of 299
BROKEN rows were these classes, every run, so the residual bucket of 1,007 said nothing about what was left.

HISTORY (2026-09-27). A claim under a dated heading (`## 2026-09-20 session`), or on a line that starts with a date,
is a dated record and is MARKED-HISTORICAL. Version strings are not counts: `6.6.0.3 docs` is not "3 docs".

Usage:
    claim_scan.py [--root .] [--json] [--record] [--include-exempt] [--since REF]
                  [--sibling-root NAME=PATH ...] [--conditional PATH ...]

Exit codes: 0 no unverified claims · 1 claims need attention · 2 error
"""

from __future__ import annotations

import argparse
import ast
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

# Not preceded by a digit, dot, comma, letter or `v`: `6.6.0.3 docs`, `v2 files` and the `225` inside `1,225` are not
# counts. Thousands separators are part of the number, so `1,225 checks` is claimed as 1225.
COUNT_RE = re.compile(
    r"(?<![\w.,])(\d{1,3}(?:,\d{3})+|\d{1,5})\s+(files?|checks?|documents?|docs|entries|records?|scripts?|surfaces?|rules?|"
    r"specs?|ADRs?|tests?|sites?|devices?|rows?|models?)\b", re.I)
DATE_RE = re.compile(
    r"(?:last\s+reviewed|last\s+updated|as\s+at|snapshot|generated)\s*[:\-—]?\s*"
    r"(\d{4}-\d{2}-\d{2}|\d{1,2}\s+\w+\s+\d{4})", re.I)
UNIQUE_RE = re.compile(
    r"\b(the only|only one|sole|exactly one|no other|unique(?:ly)?)\b[^.\n]{0,90}", re.I)
DATE_TOKEN = re.compile(r"\b(?:20\d\d-[01]\d-[0-3]\d|20\d\d[01]\d[0-3]\d(?:_\d{4})?)\b")
DATED_LINE = re.compile(r"^\s*(?:[-*+]\s+|\|\s*|\d+\.\s+)?(?:\*\*|`)?(?:20\d\d-[01]\d-[0-3]\d|20\d{6}(?:_\d{4})?)")
HEADING = re.compile(r"^(#{1,6})\s+(.*)")
CONDITIONAL_PHRASES = ("when present", "if present", "if it exists", "when it exists", "if exists", "(if any)",
                       "when available", "if available", "consult when")
# Absolute paths that name a location on a managed HOST, not on the machine running the audit.
ON_BOX_PREFIXES = ("/etc/", "/opt/", "/var/", "/usr/", "/srv/", "/run/", "/root/", "/home/", "/boot/", "/lib/",
                   "/proc/", "/sys/", "/dev/", "/mnt/", "/tmp/")
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

# A research report's verbatim upstream pulls sit beside it in `<slug>-sources-<YYYYMMDD_hhmm>/` (unified-network-controller
# rule, 2026-09-29). Upstream links there cannot resolve locally and must never be edited; the folder's own readme.md is
# authored and stays audited.
DATED_SOURCES = re.compile(r"-sources-\d{8}_\d{4}/(?!readme\.md$)")

def is_exempt(rel: str) -> bool:
    p = "/" + rel
    return any(e in p for e in EXEMPT) or bool(DATED_SOURCES.search(p))


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


def project_declarations(root: Path) -> dict:
    """SIBLING_ROOTS / SIBLING_BRANCHES / CONDITIONAL_PATHS from scripts/check_governance.py, by `ast` only."""
    out: dict = {"SIBLING_ROOTS": {}, "SIBLING_BRANCHES": {}, "CONDITIONAL_PATHS": set()}
    f = root / "scripts" / "check_governance.py"
    if not f.is_file():
        return out
    try:
        tree = ast.parse(f.read_text(encoding="utf-8"))
    except (SyntaxError, UnicodeDecodeError, OSError):
        return out
    for node in tree.body:
        target = (node.target if isinstance(node, ast.AnnAssign) else
                  node.targets[0] if isinstance(node, ast.Assign) and len(node.targets) == 1 else None)
        if not isinstance(target, ast.Name) or target.id not in out or node.value is None:
            continue
        val = node.value
        if isinstance(val, ast.Call) and getattr(val.func, "id", "") in {"frozenset", "set", "tuple", "dict"}:
            val = val.args[0] if val.args else ast.Constant(value=None)
        try:
            lit = ast.literal_eval(val)
        except ValueError:
            continue
        if lit is None:
            continue
        out[target.id] = set(lit) if target.id == "CONDITIONAL_PATHS" else dict(lit)
    return out


class Siblings:
    """Resolve a path inside a declared sibling checkout: working tree, or the pinned ref when one is declared."""

    def __init__(self, root: Path, roots: dict[str, str], branches: dict[str, str]) -> None:
        self.bases: dict[str, Path] = {}
        self.pinned: dict[str, set[str]] = {}
        self._names: dict[str, set[str]] = {}
        for name, rel in roots.items():
            base = (root / rel).resolve()
            if not base.is_dir():
                continue
            if name in branches:
                r = subprocess.run(["git", "ls-tree", "-r", "--name-only", branches[name]], cwd=base,
                                   capture_output=True, text=True, timeout=60)
                if r.returncode == 0:
                    self.pinned[name] = {ln for ln in r.stdout.splitlines() if ln}
                continue
            self.bases[name] = base

    def names(self, name: str) -> set[str]:
        if name not in self._names:
            if name in self.pinned:
                self._names[name] = {f.rsplit("/", 1)[-1] for f in self.pinned[name]}
            else:
                self._names[name] = {p.name for p in self.bases[name].rglob("*")
                                     if ".git" not in p.parts and "node_modules" not in p.parts}
        return self._names[name]

    def resolve(self, tok: str) -> str | None:
        clean = tok.rstrip("/")
        head, _, rest = clean.partition("/")
        for name, base in self.bases.items():
            # `cambium-swap/inventory/x.csv` names the sibling by its own name first
            if (base / clean).exists() or (rest and head in (name, base.name) and (base / rest).exists()):
                return name
        for name, files in self.pinned.items():
            for cand in (clean, rest if head == name else None):
                if cand and (cand in files or any(f.startswith(cand + "/") for f in files)):
                    return name
        if "/" not in clean:
            for name in list(self.bases) + list(self.pinned):
                if clean in self.names(name):
                    return name
        return None


def gitignored(root: Path, toks: list[str]) -> set[str]:
    if not toks:
        return set()
    try:
        r = subprocess.run(["git", "check-ignore", "--no-index", "--stdin"], cwd=root, input="\n".join(toks),
                           capture_output=True, text=True, timeout=60)
    except (OSError, subprocess.SubprocessError):
        return set()
    return {ln.strip() for ln in r.stdout.splitlines() if ln.strip()}


def changed_since(root: Path, ref: str | None) -> set[str] | None:
    """Files changed since REF (committed, uncommitted and untracked), cwd-relative, or None when no focus is set."""
    if not ref:
        return None
    r = subprocess.run(["git", "diff", "--name-only", "--relative", ref], cwd=root, capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit(f"ERROR: --since {ref}: {r.stderr.strip()}")
    u = subprocess.run(["git", "ls-files", "-o", "--exclude-standard"], cwd=root, capture_output=True, text=True)
    return {ln for ln in (r.stdout + u.stdout).splitlines() if ln}


def focus_ref(root: Path, given: str | None) -> tuple[str | None, str]:
    """--since wins (a commit, or `last-audit` resolved as `audit_state.py init` does); otherwise the focus recorded by init.

    `last-audit` used to reach git as a revision name and fail, though init accepted it (2026-09-28)."""
    if given:
        from audit_state import resolve_since
        try:
            return resolve_since(root, given)
        except ValueError as exc:
            raise SystemExit(f"ERROR: {exc}") from None
    st = root / ".staleness-audit" / "state.json"
    if st.is_file():
        since = json.loads(st.read_text(encoding="utf-8")).get("since")
        if since:
            return since["sha"], f"{since['ref']} (from audit state)"
    return None, ""


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
    ap.add_argument("--since", default=None, help="focus: flag claims in files changed since this commit")
    ap.add_argument("--sibling-root", action="append", default=[],
                    help="NAME=PATH of a sibling checkout path claims may point into (adds to SIBLING_ROOTS)")
    ap.add_argument("--conditional", action="append", default=[],
                    help="a path that is 'consult when present' (adds to CONDITIONAL_PATHS)")
    a = ap.parse_args()

    root = Path(a.root).resolve()
    count_map = {}
    for spec in a.count_map:
        if '=' not in spec:
            sys.stderr.write(f"ERROR: --count-map needs unit=glob, got {spec!r}\n")
            return 2
        k, v = spec.split('=', 1)
        count_map[k.lower().rstrip('s')] = v
    decl = project_declarations(root)
    for spec in a.sibling_root:
        if "=" not in spec:
            sys.stderr.write(f"ERROR: --sibling-root needs NAME=PATH, got {spec!r}\n")
            return 2
        k, v = spec.split("=", 1)
        decl["SIBLING_ROOTS"][k] = v
    conditional = set(decl["CONDITIONAL_PATHS"]) | set(a.conditional)
    siblings = Siblings(root, decl["SIBLING_ROOTS"], decl["SIBLING_BRANCHES"])
    ref, ref_label = focus_ref(root, a.since)
    changed = changed_since(root, ref)
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
        is_md = fp.suffix.lower() in {".md", ".rst"}
        heads: list[tuple[int, bool]] = []    # (level, dated) of the enclosing headings
        fence = False

        for i, line in enumerate(text.splitlines(), 1):
            if is_md and line.lstrip().startswith(("```", "~~~")):
                fence = not fence
            h = HEADING.match(line) if is_md and not fence else None
            if h:
                lvl = len(h.group(1))
                heads = [x for x in heads if x[0] < lvl] + [(lvl, bool(DATE_TOKEN.search(h.group(2))))]
            dated = is_md and (any(d for _, d in heads) or bool(DATED_LINE.match(line)))
            historical = dated or any(m in line.lower() for m in HISTORICAL_MARKERS)

            for m in COUNT_RE.finditer(line):
                claimed, unit = int(m.group(1).replace(",", "")), m.group(2)
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
                via = "here" if resolve_path(root, fp.parent, tok) else siblings.resolve(tok)
                if via:
                    state = "VERIFIED"
                elif tok in conditional or tok.rstrip("/") in conditional or \
                        any(ph in line.lower() for ph in CONDITIONAL_PHRASES):
                    state = "CONDITIONAL"
                elif tok.startswith(ON_BOX_PREFIXES):
                    state = "ON-BOX"
                else:
                    state = "BROKEN"
                claims.append({"type": "path", "file": rel, "line": i, "state": state,
                               "claim": tok, "actual": None, "via": via})

    # Gitignored paths are created at run time (outputs, caches, receipts): conditional on having run, not broken.
    ignored = gitignored(root, sorted({c["claim"] for c in claims if c["state"] == "BROKEN"}))
    for c in claims:
        if c["state"] == "BROKEN" and c["claim"] in ignored:
            c["state"] = "CONDITIONAL"
    for c in claims:
        c["changed"] = changed is not None and c["file"] in changed

    tally: dict[str, int] = {}
    for c in claims:
        tally[c["state"]] = tally.get(c["state"], 0) + 1

    problems = [c for c in claims if c["state"] in {"MISMATCH", "BROKEN"}]
    manual = [c for c in claims if c["state"] == "NEEDS-MANUAL"]
    explained = [c for c in claims if c["state"] in {"CONDITIONAL", "ON-BOX"}]
    if changed is not None:
        # Focus mode reorders what a human reads; it never shrinks what is counted.
        problems.sort(key=lambda c: not c["changed"])
        manual.sort(key=lambda c: not c["changed"])

    if a.json:
        print(json.dumps({"total": len(claims), "tally": tally, "since": ref_label or None,
                          "problems": problems, "needs_manual": manual, "claims": claims}, indent=2))
    else:
        print(f"Claim scan — {root}")
        print("=" * 78)
        for k in sorted(tally):
            print(f"  {k:20s} {tally[k]:5d}")
        print("-" * 78)
        print(f"  {'TOTAL':20s} {len(claims):5d}")
        if explained:
            print(f"  ({len(explained)} path claims explained, not broken: CONDITIONAL and ON-BOX are residual classes,")
            print("   recorded separately so the residual bucket says what it holds)")
        if changed is not None:
            cp = sum(c["changed"] for c in problems)
            cm = sum(c["changed"] for c in manual)
            print(f"\n  FOCUS since {ref_label}: {len(changed)} changed files — {cp} problem(s), {cm} manual claim(s) "
                  f"in them, listed first. Totals above are whole-project.")

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
                        str(len(manual) + len(problems) + len(explained)),
                        "--key", "claims_residual_manual", "--value", str(len(manual)),
                        "--key", "claims_residual_broken", "--value", str(len(problems)),
                        "--key", "claims_residual_conditional", "--value", str(tally.get("CONDITIONAL", 0)),
                        "--key", "claims_residual_on_box", "--value", str(tally.get("ON-BOX", 0))])

    return 1 if (problems or manual) else 0


if __name__ == "__main__":
    sys.exit(main())
