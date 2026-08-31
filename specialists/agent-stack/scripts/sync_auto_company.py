#!/usr/bin/env python3
"""Safely compare Agent Stack with a chosen Auto Company source revision."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import unicodedata
from datetime import UTC, datetime
from pathlib import Path, PurePosixPath
from typing import Any


SCRIPT_ROOT = Path(__file__).resolve().parent.parent
STATE_PATH = SCRIPT_ROOT / "upstream-state.json"
TRANSLATION_MEMORY_PATH = SCRIPT_ROOT / "translation-memory.json"
DEFAULT_CACHE = Path("/Volumes/Data/_ai/_skills/skills-working-cache/agent-stack/upstreams/auto-company")
DEFAULT_REPORT_ROOT = Path("/Volumes/Data/_ai/_skills/skills-working-cache/agent-stack/update-reports")
TECHNICAL_LETTERS = frozenset("Σαηρκ")


def sha256(path: Path) -> str:
    """Return the SHA-256 digest of one file."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def contains_non_english_script(path: Path) -> bool:
    """Return whether a file contains a script excluded by Agent Stack's English rule."""
    return any(
        ord(character) > 127 and unicodedata.category(character).startswith("L") and character not in TECHNICAL_LETTERS
        for character in path.read_text(encoding="utf-8")
    )


def read_json(path: Path) -> dict[str, Any]:
    """Read a JSON object with a useful error when the file is malformed."""
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"Cannot read {path}: {error}") from error
    if not isinstance(value, dict):
        raise ValueError(f"Expected a JSON object in {path}")
    return value


def write_json(path: Path, value: dict[str, Any]) -> None:
    """Write deterministic, reviewable JSON."""
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def run_git(args: list[str], cwd: Path | None = None) -> str:
    """Run Git and return stdout, surfacing stderr on failure."""
    completed = subprocess.run(
        ["git", *args],
        cwd=cwd,
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode:
        raise RuntimeError(completed.stderr.strip() or f"git {' '.join(args)} failed")
    return completed.stdout.strip()


def git_file_at_commit(repository: Path, commit: str | None, path: str) -> bytes | None:
    """Read one tracked source file from a recorded Git revision when available."""
    if not commit:
        return None
    completed = subprocess.run(
        ["git", "show", f"{commit}:{path}"],
        cwd=repository,
        check=False,
        capture_output=True,
    )
    return completed.stdout if completed.returncode == 0 else None


def upstream_relative_path(canonical_relative: str) -> str:
    """Map a canonical path back to its Auto Company source path."""
    prefix, separator, remainder = canonical_relative.partition("/")
    source_prefixes = {"personas": ".claude/agents", "skills": ".claude/skills"}
    if not separator or prefix not in source_prefixes:
        raise ValueError(f"Unsupported canonical path: {canonical_relative}")
    return f"{source_prefixes[prefix]}/{remainder}"


def source_files(source_root: Path) -> dict[str, Path]:
    """Map Auto Company source files to their canonical Agent Stack paths."""
    mappings = ((".claude/agents", "personas"), (".claude/skills", "skills"))
    files: dict[str, Path] = {}
    for source_prefix, canonical_prefix in mappings:
        source_dir = source_root / source_prefix
        if not source_dir.is_dir():
            raise ValueError(f"Expected source directory is missing: {source_dir}")
        for path in sorted(source_dir.rglob("*")):
            if path.is_file():
                relative = path.relative_to(source_dir).as_posix()
                files[f"{canonical_prefix}/{relative}"] = path
    return files


def canonical_path(relative: str) -> Path:
    """Resolve a tracked relative path beneath the canonical stack root."""
    candidate = PurePosixPath(relative)
    if candidate.is_absolute() or ".." in candidate.parts:
        raise ValueError(f"Unsafe tracked path: {relative}")
    return SCRIPT_ROOT / candidate


def prepare_mirror(cache: Path, upstream_url: str, branch: str, fetch: bool) -> Path:
    """Clone or fetch the upstream repository in the working cache when requested."""
    if cache.exists() and not (cache / ".git").is_dir():
        raise ValueError(f"Working cache exists but is not a Git checkout: {cache}")
    if not cache.exists():
        if not fetch:
            raise ValueError("No upstream mirror exists; rerun with --fetch")
        cache.parent.mkdir(parents=True, exist_ok=True)
        run_git(["clone", "--origin", "origin", "--branch", branch, upstream_url, str(cache)])
    else:
        remote = run_git(["remote", "get-url", "origin"], cache)
        if remote != upstream_url:
            raise ValueError(f"Mirror origin differs from configured upstream: {remote}")
        if fetch:
            run_git(["fetch", "--prune", "origin"], cache)
    if fetch:
        run_git(["checkout", "--detach", f"origin/{branch}"], cache)
    else:
        head = run_git(["rev-parse", "HEAD"], cache)
        configured_ref = run_git(["rev-parse", f"origin/{branch}"], cache)
        if head != configured_ref:
            raise ValueError("Existing mirror is not at its fetched branch revision; rerun with --fetch")
    return cache


def classify(
    source: dict[str, Path], state: dict[str, Any]
) -> tuple[list[dict[str, str]], list[str]]:
    """Classify upstream differences without modifying canonical content."""
    tracked = state.get("tracked", {})
    if not isinstance(tracked, dict):
        raise ValueError("State field 'tracked' must be an object")
    changes: list[dict[str, str]] = []
    unresolved: list[str] = []
    for relative, upstream_file in source.items():
        upstream_hash = sha256(upstream_file)
        record = tracked.get(relative)
        current = canonical_path(relative)
        if record is None:
            if current.exists():
                category = "manual_merge"
            else:
                category = "translation_required" if contains_non_english_script(upstream_file) else "safe_add"
        elif record.get("source_sha256") == upstream_hash:
            continue
        elif record.get("mode") == "translated":
            category = "translation_required"
        elif record.get("mode") == "adapted":
            category = "manual_merge"
        elif contains_non_english_script(upstream_file):
            category = "translation_required"
        elif not current.exists():
            category = "manual_merge"
        elif record.get("canonical_sha256") == sha256(current):
            category = "safe_replace"
        else:
            category = "manual_merge"
        changes.append({"path": relative, "classification": category, "upstream_sha256": upstream_hash})
        if category not in {"safe_add", "safe_replace"}:
            unresolved.append(relative)
    for relative in sorted(tracked):
        if relative not in source:
            changes.append({"path": relative, "classification": "remove_review", "upstream_sha256": ""})
            unresolved.append(relative)
    return changes, unresolved


def apply_safe_changes(source: dict[str, Path], changes: list[dict[str, str]]) -> list[str]:
    """Copy only explicitly safe upstream files into the canonical source tree."""
    applied: list[str] = []
    for change in changes:
        if change["classification"] not in {"safe_add", "safe_replace"}:
            continue
        target = canonical_path(change["path"])
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source[change["path"]], target)
        applied.append(change["path"])
    return applied


def record_applied_changes(source: dict[str, Path], state: dict[str, Any], applied: list[str]) -> None:
    """Advance per-file hashes after safe changes without hiding unresolved changes."""
    tracked = state.setdefault("tracked", {})
    for relative in applied:
        target = canonical_path(relative)
        tracked[relative] = {
            "source_sha256": sha256(source[relative]),
            "canonical_sha256": sha256(target),
            "mode": "mirrored",
        }


def record_current(source_root: Path, state: dict[str, Any]) -> dict[str, Any]:
    """Record the source and translated canonical hashes as the comparison baseline."""
    if source_root.resolve().is_relative_to(SCRIPT_ROOT.resolve()):
        raise ValueError("Refusing a source inside Agent Stack; use a reviewed upstream checkout or the working-cache mirror")
    tracked: dict[str, dict[str, str]] = {}
    for relative, source_path in source_files(source_root).items():
        if source_path.resolve().is_relative_to(SCRIPT_ROOT.resolve()):
            raise ValueError("Refusing symlinked Agent Stack content as an upstream source; use the working-cache mirror")
        target = canonical_path(relative)
        if not target.is_file():
            raise ValueError(f"Canonical file is missing: {target}")
        source_hash = sha256(source_path)
        canonical_hash = sha256(target)
        mode = "translated" if contains_non_english_script(source_path) else "mirrored"
        if mode == "mirrored" and source_hash != canonical_hash:
            mode = "adapted"
        tracked[relative] = {"source_sha256": source_hash, "canonical_sha256": canonical_hash, "mode": mode}
    state["tracked"] = tracked
    state["last_imported_commit"] = run_git(["rev-parse", "HEAD"], source_root)
    return state


def write_translation_memory(state: dict[str, Any]) -> None:
    """Persist reviewed English text hashes for deterministic translation reuse."""
    tracked = state.get("tracked", {})
    entries = {
        path: {"source_sha256": item["source_sha256"], "canonical_sha256": item["canonical_sha256"]}
        for path, item in tracked.items()
        if item.get("mode") == "translated"
    }
    write_json(
        TRANSLATION_MEMORY_PATH,
        {"version": 1, "policy": "translation-policy.md", "entries": entries},
    )


def report_directory(report_root: Path) -> Path:
    """Return a timestamped report directory without overwriting a prior run."""
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    candidate = report_root / stamp
    counter = 1
    while candidate.exists():
        candidate = report_root / f"{stamp}-{counter}"
        counter += 1
    return candidate


def write_report(
    source_root: Path,
    source: dict[str, Path],
    changes: list[dict[str, str]],
    commit: str,
    prior_commit: str | None,
    applied: list[str],
    report_root: Path,
) -> Path:
    """Write a reviewable report and proposal copies for non-automatic changes."""
    directory = report_directory(report_root)
    directory.mkdir(parents=True)
    proposal_root = directory / "proposals"
    previous_root = directory / "previous-upstream"
    unavailable_baselines: list[str] = []
    for change in changes:
        if change["classification"] in {"safe_add", "safe_replace"}:
            continue
        proposal = proposal_root / change["path"]
        proposal.parent.mkdir(parents=True, exist_ok=True)
        if change["classification"] != "remove_review":
            shutil.copy2(source[change["path"]], proposal)
        previous = git_file_at_commit(source_root, prior_commit, upstream_relative_path(change["path"]))
        if previous is None:
            unavailable_baselines.append(change["path"])
        else:
            baseline = previous_root / change["path"]
            baseline.parent.mkdir(parents=True, exist_ok=True)
            baseline.write_bytes(previous)
    translation_paths = [change["path"] for change in changes if change["classification"] == "translation_required"]
    if translation_paths:
        lines = [
            "# Translation Brief",
            "",
            "Use the current canonical English file as the translation memory. Preserve its wording for unchanged material; translate only new or materially changed source content.",
            "",
            "Read `../../translation-policy.md` before preparing a replacement. Compare the original source in `previous-upstream/`, the new source in `proposals/`, and the current English file.",
            "",
            "## Files Requiring Translation",
            "",
            *[f"- `{path}`" for path in translation_paths],
            "",
        ]
        (directory / "translation-brief.md").write_text("\n".join(lines), encoding="utf-8")
    write_json(
        directory / "report.json",
        {
            "upstream_commit": commit,
            "previous_upstream_commit": prior_commit,
            "changes": changes,
            "applied": applied,
            "baseline_unavailable": unavailable_baselines,
            "generated_at": datetime.now(UTC).isoformat(),
        },
    )
    return directory


def parse_args() -> argparse.Namespace:
    """Parse the deliberately narrow sync command-line interface."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="Print classifications without writing canonical files.")
    parser.add_argument("--apply", action="store_true", help="Apply only safe additions and replacements.")
    parser.add_argument("--fetch", action="store_true", help="Clone or fetch the upstream mirror before comparison.")
    parser.add_argument("--upstream-url", help="Override the configured upstream Git URL.")
    parser.add_argument("--branch", help="Override the configured upstream branch.")
    parser.add_argument("--working-cache", type=Path, default=DEFAULT_CACHE, help="Disposable upstream mirror location.")
    parser.add_argument("--source", type=Path, help="Use a local Auto Company checkout instead of the mirror.")
    parser.add_argument("--report-dir", type=Path, default=DEFAULT_REPORT_ROOT, help="Working-cache location for reports and source proposals.")
    parser.add_argument("--record-current", action="store_true", help="Record a local source checkout as the import baseline.")
    parser.add_argument("--status", action="store_true", help="Print configured state without accessing a mirror or network.")
    return parser.parse_args()


def main() -> int:
    """Run one safe comparison, optional fetch, or baseline-recording operation."""
    args = parse_args()
    if args.dry_run and args.apply:
        raise ValueError("Choose either --dry-run or --apply, not both")
    state = read_json(STATE_PATH)
    if args.upstream_url:
        state["upstream_url"] = args.upstream_url
    if args.branch:
        state["branch"] = args.branch
    upstream_url = str(state["upstream_url"])
    branch = str(state["branch"])

    if args.status:
        tracked = state.get("tracked", {})
        translated = sum(item.get("mode") == "translated" for item in tracked.values())
        print(
            json.dumps(
                {
                    "upstream_url": upstream_url,
                    "branch": branch,
                    "last_imported_commit": state.get("last_imported_commit"),
                    "tracked_files": len(tracked),
                    "translated_files": translated,
                },
                indent=2,
            )
        )
        return 0

    if args.record_current:
        if args.source is None:
            raise ValueError("--record-current requires --source")
        write_json(STATE_PATH, record_current(args.source.resolve(), state))
        write_translation_memory(state)
        print(json.dumps({"recorded": len(state["tracked"]), "state": str(STATE_PATH)}, indent=2))
        return 0

    source_root = args.source.resolve() if args.source else prepare_mirror(args.working_cache, upstream_url, branch, args.fetch)
    source = source_files(source_root)
    commit = run_git(["rev-parse", "HEAD"], source_root)
    changes, unresolved = classify(source, state)
    applied: list[str] = []
    report: Path | None = None
    if args.apply:
        applied = apply_safe_changes(source, changes)
        report = write_report(
            source_root,
            source,
            changes,
            commit,
            state.get("last_imported_commit"),
            applied,
            args.report_dir,
        )
        if not unresolved:
            state = record_current(source_root, state)
            write_json(STATE_PATH, state)
            write_translation_memory(state)
        elif applied:
            record_applied_changes(source, state, applied)
            write_json(STATE_PATH, state)
            write_translation_memory(state)
    result = {
        "upstream_commit": commit,
        "changes": changes,
        "applied": applied,
        "unresolved": unresolved,
        "report": str(report) if report else None,
        "state_advanced": bool(args.apply and not unresolved),
    }
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (RuntimeError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        raise SystemExit(2) from error
