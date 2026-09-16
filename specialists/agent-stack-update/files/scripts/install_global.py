#!/usr/bin/env python3
"""Install Agent Stack globally through verified symlinks only."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path


SCRIPT_ROOT = Path(__file__).resolve().parent.parent
MANIFEST_PATH = SCRIPT_ROOT / "manifest.yaml"
CLIENT_ROOTS = {
    "claude": {"agents": Path(".claude/agents"), "skills": Path(".claude/skills")},
    "codex": {"skills": Path(".codex/skills")},
    "agents": {"skills": Path(".agents/skills")},
}
CAPABILITY_PATH = re.compile(r"^\s+- \{id: [^,]+, kind: [^,]+, path: ([^,}]+)")
DEFAULT_EXCLUDED_SKILLS = frozenset({"skill-creator"})


class CollisionError(ValueError):
    """Raised when a client target is not an owned Agent Stack symlink."""


def git_output(args: list[str]) -> str:
    """Run a local Git read command from this Agent Stack checkout."""
    completed = subprocess.run(["git", *args], cwd=SCRIPT_ROOT, check=False, capture_output=True, text=True)
    if completed.returncode:
        raise ValueError(completed.stderr.strip() or f"git {' '.join(args)} failed")
    return completed.stdout.strip()


def canonical_install_root() -> Path:
    """Find the primary Git checkout, or use this extracted archive as its own canonical root.

    Git worktree protection is preserved when Git metadata exists. A distributed ZIP/tar
    intentionally has no worktree graph, so the extracted Agent Stack directory is the only
    available canonical source and is safe to use as such.
    """
    try:
        checkout_root = Path(git_output(["rev-parse", "--show-toplevel"])).resolve()
    except ValueError as exc:
        if "not a git repository" in str(exc).lower():
            return SCRIPT_ROOT.resolve()
        raise
    relative = SCRIPT_ROOT.resolve().relative_to(checkout_root)
    primary_line = next((line for line in git_output(["worktree", "list", "--porcelain"]).splitlines() if line.startswith("worktree ")), None)
    if primary_line is None:
        raise ValueError("Cannot find the repository's primary checkout")
    canonical = Path(primary_line.removeprefix("worktree ")).resolve() / relative
    if not canonical.is_dir():
        raise ValueError(f"Canonical Agent Stack path is missing: {canonical}")
    return canonical


def require_canonical_checkout() -> None:
    """Prevent global links from silently targeting an expendable development worktree."""
    canonical = canonical_install_root()
    if SCRIPT_ROOT.resolve() != canonical:
        raise ValueError(f"Global install must run from the canonical checkout: {canonical}")


def manifest_paths() -> set[str]:
    """Return capability paths recorded in the small, canonical manifest format."""
    return {
        match.group(1)
        for line in MANIFEST_PATH.read_text(encoding="utf-8").splitlines()
        if (match := CAPABILITY_PATH.match(line))
    }


def canonical_entries() -> tuple[list[Path], list[Path], Path]:
    """Return persona files, package directories, and the one single-file skill."""
    personas = sorted((SCRIPT_ROOT / "personas").glob("*.md"))
    packages = sorted(path for path in (SCRIPT_ROOT / "skills").iterdir() if path.is_dir() and (path / "SKILL.md").is_file())
    frontend = SCRIPT_ROOT / "skills/frontend-design.md"
    actual_paths = {
        *(path.relative_to(SCRIPT_ROOT).as_posix() for path in personas),
        *(path.relative_to(SCRIPT_ROOT).as_posix() for path in packages),
        frontend.relative_to(SCRIPT_ROOT).as_posix(),
    }
    if actual_paths != manifest_paths():
        missing = sorted(actual_paths - manifest_paths())
        stale = sorted(manifest_paths() - actual_paths)
        raise ValueError(f"Manifest does not match canonical capabilities; missing={missing}, stale={stale}")
    return personas, packages, frontend


def expected_links(home: Path) -> dict[Path, Path]:
    """Map every client installation target to its canonical source."""
    personas, packages, frontend = canonical_entries()
    links: dict[Path, Path] = {}
    for persona in personas:
        links[home / CLIENT_ROOTS["claude"]["agents"] / persona.name] = persona
    for client in CLIENT_ROOTS:
        if "skills" not in CLIENT_ROOTS[client]:
            continue
        skills_root = home / CLIENT_ROOTS[client]["skills"]
        for package in packages:
            links[skills_root / package.name] = package
        links[skills_root / "frontend-design/SKILL.md"] = frontend
    return links


def selected_links(
    home: Path, clients: set[str], exclude: set[str] | None = None, include: set[str] | None = None
) -> dict[Path, Path]:
    """Filter expected links for requested clients and intentionally excluded skill IDs."""
    excluded = set(DEFAULT_EXCLUDED_SKILLS)
    excluded.difference_update(include or set())
    excluded.update(exclude or set())
    links: dict[Path, Path] = {}
    for target, source in expected_links(home).items():
        client = next(
            (
                client_id
                for client_id, roots in CLIENT_ROOTS.items()
                if any(target.is_relative_to(home / root) for root in roots.values())
            ),
            None,
        )
        if client is None:
            raise ValueError(f"Cannot determine the client for target: {target}")
        skill_id = source.stem if source.is_file() else source.name
        if client in clients and skill_id not in excluded:
            links[target] = source
    return links


def link_state(target: Path, source: Path) -> str:
    """Classify a destination without following an unexpected symlink blindly."""
    if not target.exists() and not target.is_symlink():
        return "missing"
    if target.is_symlink() and target.resolve() == source.resolve():
        return "correct"
    if target.is_symlink():
        return "stale-agent-stack-link" if target.resolve().is_relative_to(SCRIPT_ROOT.resolve()) else "collision"
    return "collision"


def preflight(links: dict[Path, Path]) -> tuple[list[Path], list[Path], list[Path]]:
    """Return missing, correct, and conflicting destinations before any write."""
    missing: list[Path] = []
    correct: list[Path] = []
    collisions: list[Path] = []
    for target, source in links.items():
        if target.name == "SKILL.md" and target.parent.exists() and link_state(target, source) == "missing":
            if not target.parent.is_dir() or any(target.parent.iterdir()):
                collisions.append(target.parent)
                continue
        state = link_state(target, source)
        if state == "missing":
            missing.append(target)
        elif state == "correct":
            correct.append(target)
        else:
            collisions.append(target)
    return missing, correct, collisions


def install(
    home: Path,
    clients: set[str],
    exclude: set[str] | None = None,
    include: set[str] | None = None,
    dry_run: bool = False,
) -> dict[str, list[Path]]:
    """Create verified links after a complete, non-destructive preflight."""
    links = selected_links(home, clients, exclude, include)
    missing, correct, collisions = preflight(links)
    if collisions:
        rendered = ", ".join(str(path) for path in collisions)
        raise CollisionError(f"Refusing to overwrite existing client entries: {rendered}")
    result = {"would_create": missing, "already_present": correct, "created": [], "collisions": []}
    if dry_run:
        return result
    created: list[Path] = []
    try:
        for target in missing:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.symlink_to(links[target])
            if link_state(target, links[target]) != "correct":
                raise RuntimeError(f"Link verification failed: {target}")
            created.append(target)
    except Exception:
        for target in reversed(created):
            if target.is_symlink() and target.resolve() == links[target].resolve():
                target.unlink()
        raise
    result["would_create"] = []
    result["created"] = created
    return result


def uninstall(
    home: Path, clients: set[str], exclude: set[str] | None = None, include: set[str] | None = None
) -> dict[str, list[Path]]:
    """Remove only links that still resolve exactly to canonical Agent Stack sources."""
    removed: list[Path] = []
    preserved: list[Path] = []
    for target, source in selected_links(home, clients, exclude, include).items():
        if not target.exists() and not target.is_symlink():
            continue
        if target.is_symlink() and target.resolve() == source.resolve():
            target.unlink()
            removed.append(target)
            if target.name == "SKILL.md":
                try:
                    target.parent.rmdir()
                except OSError:
                    pass
        else:
            preserved.append(target)
    return {"removed": removed, "preserved": preserved}


def serialise(result: dict[str, list[Path]]) -> str:
    """Render path results as stable JSON for people and automation."""
    return json.dumps({key: [str(path) for path in value] for key, value in result.items()}, indent=2, sort_keys=True)


def parse_args() -> argparse.Namespace:
    """Parse the deliberately narrow global installation interface."""
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group()
    action.add_argument("--status", action="store_true", help="Report link state without writing.")
    action.add_argument("--dry-run", action="store_true", help="Preview an install without writing.")
    action.add_argument("--install", action="store_true", help="Create missing, verified links.")
    action.add_argument("--uninstall", action="store_true", help="Remove only owned links.")
    parser.add_argument("--client", choices=sorted(CLIENT_ROOTS), action="append", help="Limit to one client; defaults to every supported client.")
    parser.add_argument("--exclude", action="append", default=[], help="Keep a named existing skill out of this install.")
    parser.add_argument("--include", action="append", default=[], help="Include a skill normally excluded by default.")
    parser.add_argument("--home", type=Path, default=Path.home(), help="Home directory; intended for tests and controlled installs.")
    return parser.parse_args()


def main() -> int:
    """Run one requested global-install operation."""
    args = parse_args()
    if not any((args.status, args.dry_run, args.install, args.uninstall)):
        raise ValueError("Choose one action: --status, --dry-run, --install, or --uninstall")
    clients = set(args.client or CLIENT_ROOTS)
    exclude = set(args.exclude) - set(args.include)
    if args.status or args.dry_run or args.install:
        require_canonical_checkout()
    if args.status:
        result = {
            str(target): [link_state(target, source)]
            for target, source in selected_links(args.home, clients, exclude, set(args.include)).items()
        }
        print(json.dumps(result, indent=2, sort_keys=True))
    elif args.uninstall:
        print(serialise(uninstall(args.home, clients, exclude, set(args.include))))
    else:
        print(serialise(install(args.home, clients, exclude, set(args.include), dry_run=args.dry_run)))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (CollisionError, RuntimeError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        raise SystemExit(2) from error
