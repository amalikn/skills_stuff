#!/usr/bin/env python3
"""Phase 7 inverse sweep — find what EXISTS that no catalog names, and what an index points at that has MOVED.

WHY THIS SCRIPT EXISTS
----------------------
SKILL.md has always said Phase 7 must run an inverse sweep: "not 'does the catalog name something that
vanished' but 'does anything exist that no catalog names' — only the second grows while you are not
looking." It said it in prose, and nothing implemented it. `verify_completeness.py` blocked on receipts,
coverage, old values, structured configs and the project suite, and passed a run in which the inverse
sweep had simply not happened.

That is the skill's own anti-pattern — "trusting a tool's own report of what it did" — turned inward.
Every other mechanical step was enforced, so the one prose step was the one that got skipped, and the
gate said PASSED.

THE RUN THAT FORCED THIS. A project reorganised `docs/` into five subtrees. The audit passed its gate.
Three defects survived it, one of each kind below:

  1. The repo README's structure table never gained a row for a new top-level directory holding the
     project's most decision-relevant artefact. Nothing existed to compare the tree against a catalog.
  2. Three new subdirectories had no README, while every one of their siblings had one. "A directory
     has an index" is a structural property, not a claim, so the claim taxonomy could not see it.
  3. The knowledge-base index still listed its files as bare names — `01-CONTEXT.md` — after they had
     moved into a subdirectory. Every one of those references still RESOLVED, because `resolve_path()`
     searches bare filenames repo-wide, deliberately and for good reason: requiring a directory would
     have produced 120 false positives on a real project. So a moved file never breaks its own index.
     The reference is not broken. It is DISPLACED, and it sends a human to the wrong place.

The third is the subtle one and the reason this is a separate report rather than a tightening of
`resolve_path()`. Loosening was correct; the missing piece was a second, lower-severity state.

WHAT IT REPORTS
---------------
  ORPHAN-DIR    a directory no catalog file mentions
  UNINDEXED-DIR a directory holding documents but no README, where sibling directories have one
  DISPLACED     a bare-name reference that resolves ONLY via repo-wide search, to a file in a
                different directory from the one citing it

Exit 1 if anything is found, so the Phase 7 gate can block on it.

Usage:
    inverse_sweep.py                          # report; exit 1 on findings
    inverse_sweep.py --record                 # also write the counts into the audit receipts
    inverse_sweep.py --catalog README.md --catalog AGENTS.md    # extra catalog files
    inverse_sweep.py --min-docs 2             # UNINDEXED-DIR threshold (default 2)
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

# Files that are expected to describe the shape of the project. A directory named by ANY of them counts
# as catalogued. Deliberately generous: the finding worth having is "nothing anywhere mentions this",
# not "it is missing from one particular index".
DEFAULT_CATALOGS = ("README.md", "AGENTS.md", "CLAUDE.md", "AI_NAVIGATION.md", "context-map.yaml",
                    "SCRATCHPAD.md", "ROADMAP.md", "docs/README.md")

SKIP_DIR_PARTS = {".git", "__pycache__", "node_modules", ".venv", "venv", ".pytest_cache",
                  ".ai-context", ".remember", ".serena", ".staleness-audit"}
DOC_SUFFIXES = {".md", ".rst", ".txt"}


def skipped(p: Path) -> bool:
    """Prefix-aware, because the audit's own snapshot directory is `.staleness-audit-snapshot-<stamp>`
    and an exact-name skip set does not match it — the first run reported its own snapshot back to it."""
    return any(part in SKIP_DIR_PARTS or part.startswith(".staleness-audit") for part in p.parts)


def tracked_files(root: Path) -> list[Path]:
    """Prefer git's view; fall back to a walk. git is cwd-relative here, which is what we want."""
    try:
        out = subprocess.run(["git", "ls-files"], cwd=root, capture_output=True, text=True, timeout=30)
        if out.returncode == 0 and out.stdout.strip():
            paths = [root / line for line in out.stdout.splitlines() if line.strip()]
            # git ls-files omits untracked-but-present work; add anything on disk it missed.
            seen = set(paths)
            for p in root.rglob("*"):
                if p.is_file() and p not in seen and not skipped(p):
                    paths.append(p)
            return paths
    except (OSError, subprocess.SubprocessError):
        pass
    return [p for p in root.rglob("*") if p.is_file() and not skipped(p)]


def directories(root: Path) -> list[str]:
    out = set()
    for p in root.rglob("*"):
        if not p.is_dir() or skipped(p):
            continue
        rel = p.relative_to(root).as_posix()
        if rel and not rel.startswith("."):
            out.add(rel)
    return sorted(out)


def catalog_text(root: Path, extra: list[str]) -> str:
    """Every catalog in the project, not a fixed pair of them.

    The finding worth having is "nothing ANYWHERE mentions this" — so the catalog set has to be
    everywhere the project actually writes indexes. The original list named only the root README and
    docs/README.md, which meant a project using per-directory READMEs (trackers/README.md,
    scripts/README.md) or a generated index had no way to declare a directory catalogued: the gate
    invokes this script with no --catalog, so there was no channel for it at all. Reading every
    README.md plus the named governance files matches the stated intent instead of under-reading it.
    """
    parts = []
    seen: set[Path] = set()
    for name in list(DEFAULT_CATALOGS) + list(extra):
        f = root / name
        if f.is_file() and f not in seen:
            seen.add(f)
            try:
                parts.append(f.read_text(encoding="utf-8"))
            except (OSError, UnicodeDecodeError):
                continue
    # Every catalog at EVERY depth, not only at the audit root. A workspace may nest self-contained
    # projects (portfolio/tracks/<name>/), and a nested project catalogues its own directories in its
    # OWN AGENTS.md / README.md / context-map.yaml. Reading only the audit root's copies reported 33
    # directories as orphans that their own project documents perfectly well — a false-positive rate
    # that buries the real finding, which is the one thing this sweep exists to surface.
    for name in DEFAULT_CATALOGS:
        for f in root.rglob(name):
            if f.is_file() and f not in seen and not skipped(f):
                seen.add(f)
                try:
                    parts.append(f.read_text(encoding="utf-8"))
                except (OSError, UnicodeDecodeError):
                    continue
    return "\n".join(parts)


def find_orphan_dirs(root: Path, cats: str) -> list[str]:
    out = []
    for d in directories(root):
        # A directory is catalogued if its path OR its leaf name appears. Leaf-name matching keeps the
        # false-positive rate down on projects that write `scripts/` rather than the full path.
        leaf = d.rsplit("/", 1)[-1]
        # NOT \b: a leaf like ".archcore" begins with a non-word char, so \b requires a word char
        # immediately before it and never matches — every dot-directory was a false orphan. The
        # lookbehind excludes only word chars and '-', so a normal `parent/leaf/` path still
        # matches while `draw/` does not satisfy a leaf of `raw`.
        if d in cats or f"{d}/" in cats or re.search(rf"(?<![\w-]){re.escape(leaf)}/", cats):
            continue
        out.append(d)
    return out


def find_unindexed_dirs(root: Path, min_docs: int) -> list[str]:
    """A directory with documents but no README, where at least one sibling HAS one.

    The sibling test is what keeps this from firing on projects that simply do not use per-directory
    READMEs. The finding is INCONSISTENCY — a convention the project follows everywhere else and broke
    here, usually because the directory is new.
    """
    by_parent: dict[str, list[str]] = {}
    for d in directories(root):
        by_parent.setdefault(d.rsplit("/", 1)[0] if "/" in d else "", []).append(d)

    out = []
    for _parent, sibs in by_parent.items():
        has_readme = {s for s in sibs if (root / s / "README.md").is_file()}
        if not has_readme:
            continue                      # this parent does not use the convention; nothing to be consistent with
        for s in sibs:
            if s in has_readme:
                continue
            docs = [p for p in (root / s).glob("*") if p.is_file() and p.suffix in DOC_SUFFIXES]
            if len(docs) >= min_docs:
                out.append(f"{s}  ({len(docs)} documents, siblings have READMEs)")
    return sorted(out)


def find_displaced_refs(root: Path, files: list[Path]) -> list[str]:
    """An INDEX that lists files which have moved into one of its own subdirectories.

    NOT broken — deliberately a separate, softer state. The reference resolves; it simply points a
    reader at a directory the file left.

    SCOPED HARD, and the first version was not. Flagging every bare-name reference that resolves
    elsewhere produced 52 findings on a real project and almost all were prose: a CHANGELOG entry
    citing `cell_map.py`, an AGENTS.md citing `sevs-register-findings.json`. Prose legitimately writes
    a filename without a directory — that is exactly why `resolve_path()` is permissive, and a check
    that reintroduces those false positives is worse than no check, because it will be muted.

    The signal worth having is narrower: a **README** — a file whose job is to index its own directory
    — listing names that now live in a SUBDIRECTORY of it. That is what a reorganisation leaves
    behind, it is invisible to any resolver, and it is what sent a reader to `docs/` for a file that
    had moved to `docs/kb/`. The repo-root README is excluded: everything is its descendant, so it
    would match all prose.
    """
    name_index: dict[str, list[Path]] = {}
    for f in files:
        name_index.setdefault(f.name, []).append(f)

    out = []
    for f in files:
        if f.name != "README.md" or f.parent == root:
            continue
        rel = f.relative_to(root).as_posix()
        if skipped(f) or "archive/" in rel:
            continue
        try:
            text = f.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        for tok in set(re.findall(r"`([A-Za-z0-9][A-Za-z0-9._-]*\.(?:md|py|yaml|yml|json))`", text)):
            if (f.parent / tok).exists() or (root / tok).exists():
                continue                                  # resolves locally or from the root: fine
            hits = name_index.get(tok, [])
            if len(hits) != 1:
                continue                                  # absent (claim_scan's job) or ambiguous
            target = hits[0].relative_to(root).as_posix()
            # Not displaced when the citing line ALSO names the directory the file lives in: an index
            # row whose subject is `skill-jdm/` is entitled to list `SKILL.md` as its contents, and
            # calling that a displaced reference is a false positive on correct documentation.
            parent_leaf = hits[0].parent.name
            if any(f"{parent_leaf}/" in ln for ln in text.splitlines() if f"`{tok}`" in ln):
                continue
            # Only a move INTO this index's own subtree. Anything else is prose about another part
            # of the project, which an index is entitled to do.
            if hits[0].parent != f.parent and hits[0].is_relative_to(f.parent):
                out.append(f"{rel} cites `{tok}` -> actually at {target}")
    return sorted(out)


def main() -> int:
    ap = argparse.ArgumentParser(description=(__doc__ or "").split("\n")[0])
    ap.add_argument("--root", default=".")
    ap.add_argument("--catalog", action="append", default=[], help="extra catalog file (repeatable)")
    ap.add_argument("--min-docs", type=int, default=2, help="UNINDEXED-DIR threshold (default 2)")
    ap.add_argument("--record", action="store_true", help="write counts into .staleness-audit/state.json")
    a = ap.parse_args()

    root = Path(a.root).resolve()
    files = tracked_files(root)
    cats = catalog_text(root, a.catalog)

    orphan = find_orphan_dirs(root, cats)
    unindexed = find_unindexed_dirs(root, a.min_docs)
    displaced = find_displaced_refs(root, files)

    print("=" * 78)
    print(f"INVERSE SWEEP — {root}")
    print("=" * 78)
    print(f"  directories       : {len(directories(root))}")
    print(f"  catalog sources   : {len([c for c in list(DEFAULT_CATALOGS) + a.catalog if (root / c).is_file()])}")
    print()

    for label, rows, note in (
        ("ORPHAN-DIR", orphan, "exists but no catalog file names it"),
        ("UNINDEXED-DIR", unindexed, "documents but no README, where siblings have one"),
        ("DISPLACED", displaced, "reference resolves, but to a file in another directory"),
    ):
        if rows:
            print(f"  {label} ({len(rows)}) — {note}")
            for r in rows[:40]:
                print(f"      {r}")
            if len(rows) > 40:
                print(f"      … and {len(rows) - 40} more")
            print()

    total = len(orphan) + len(unindexed) + len(displaced)
    if a.record:
        state = root / ".staleness-audit" / "state.json"
        if state.is_file():
            doc = json.loads(state.read_text(encoding="utf-8"))
            doc.setdefault("phases", {}).setdefault("7", {}).update({
                "inverse_orphan_dirs": len(orphan),
                "inverse_unindexed_dirs": len(unindexed),
                "inverse_displaced_refs": len(displaced),
            })
            state.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
            print("  recorded into .staleness-audit/state.json")

    if total:
        print(f"INVERSE SWEEP FOUND {total} ITEM(S) — the catalog and the tree disagree.")
        print("=" * 78)
        return 1
    print("INVERSE SWEEP CLEAN — every directory is catalogued and indexed, no displaced references.")
    print("=" * 78)
    return 0


if __name__ == "__main__":
    sys.exit(main())
