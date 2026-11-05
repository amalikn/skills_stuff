#!/usr/bin/env python3
"""Show which AGENTS.md files Claude Code and Codex load for a folder, and flag a chain that one of them cannot see.

Operator, 2026-11-05: a /Volumes/Data -> workspace -> repo AGENTS.md chain worked for Claude Code but not for Codex, and the Codex fix
(a project-root marker) briefly made a trusted home folder the root of every repo under it. This check reports, for one folder:

- Claude Code: the `@` import chain from the nearest AGENTS.md upward (absolute and relative imports, cycles, missing targets; a relative
  import inside a symlinked file is flagged, because it may resolve from the link's target folder).
- Codex: its global file is `$CODEX_HOME/AGENTS.md` (beside config.toml), compared with the chain's top file; its project root (the nearest folder holding a `project_root_markers` entry, default `.git`; with none, the folder itself, as
  observed with codex-cli 0.166), the AGENTS.override.md / AGENTS.md files it concatenates from that root down to the folder, their total
  bytes against `project_doc_max_bytes` (default 32768) and which file the cut would land in. Codex ignores `@` lines.
- Trust: whether the Codex root is a trusted project in `~/.codex/config.toml`, git repos below it that it would cover without their own
  entry (an error when the root is trusted), and per-repo entries that stop matching once the root moved (a warning).

Behaviour of Codex was observed with `codex exec` on codex-cli 0.166.0 (2026-11-05); the defaults are from that binary's config schema.
Read-only: it writes nothing and runs no subprocess. Runtime: well under a second, plus a bounded scan for git repos (depth 3).

Usage (paths absolute or relative to the current folder):
    python3 agents_chain.py --path /Volumes/Data/_ansible/ansible-malik        # report; exit 0
    python3 agents_chain.py --path . --check                                   # exit 1 on an error finding
    python3 agents_chain.py --path . --codex-config ~/.codex/config.toml --markers .codex-root
"""

from __future__ import annotations

import argparse
import sys
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

DEFAULT_MARKERS = [".git"]
DEFAULT_MAX_BYTES = 32768
DOC_NAMES = ["AGENTS.override.md", "AGENTS.md"]
SCAN_DEPTH = 3
SCAN_SKIP = {"Library", "node_modules", ".Trash", ".cache"}


@dataclass
class Report:
    """Findings for one folder.

    Args:
        claude: AGENTS.md files on the Claude Code import chain, nearest first.
        codex_root: the folder Codex treats as the project root.
        codex_docs: (path, bytes) Codex concatenates, root first.
        lines: report lines, in order.
        errors: count of error findings.
    """

    claude: list[Path] = field(default_factory=list)
    codex_root: Path | None = None
    codex_docs: list[tuple[Path, int]] = field(default_factory=list)
    lines: list[str] = field(default_factory=list)
    errors: int = 0

    def add(self, level: str, text: str) -> None:
        """Record one finding.

        Args:
            level: "error", "warn" or "info".
            text: the message.

        Returns:
            None.
        """
        if level == "error":
            self.errors += 1
        self.lines.append(f"  {level:5} {text}")


def nearest_agents(folder: Path) -> Path | None:
    """The AGENTS.md in the folder or its nearest ancestor.

    Args:
        folder: where an agent starts.

    Returns:
        That AGENTS.md path, or None when there is none up to the filesystem root.
    """
    for d in [folder, *folder.parents]:
        if (d / "AGENTS.md").is_file():
            return d / "AGENTS.md"
    return None


def import_target(doc: Path) -> str | None:
    """The first `@` import line of a file (Claude Code syntax), if any.

    Args:
        doc: the AGENTS.md to read.

    Returns:
        The import target as written, without the `@`, or None.
    """
    for line in doc.read_text(encoding="utf-8", errors="replace").splitlines():
        if line.startswith("@") and len(line) > 1 and not line.startswith("@@"):
            return line[1:].strip()
    return None


def claude_chain(start: Path, report: Report) -> None:
    """Follow `@` imports from the nearest AGENTS.md and record the chain and its problems.

    Args:
        start: the folder an agent starts in.
        report: the report to fill.

    Returns:
        None.
    """
    doc = nearest_agents(start)
    if doc is None:
        report.add("info", "Claude Code: no AGENTS.md here or above")
        return
    seen: set[Path] = set()
    while doc is not None:
        real = doc.resolve()
        if real in seen:
            report.add("error", f"Claude Code: import cycle at {doc}")
            return
        seen.add(real)
        report.claude.append(doc)
        target = import_target(doc)
        if target is None:
            return
        target_path = Path(target).expanduser()
        if not target_path.is_absolute():
            if doc.is_symlink():
                report.add("warn", f"Claude Code: relative import '{target}' in symlinked {doc} (may resolve from {real.parent})")
            target_path = (doc.parent / target_path)
        if not target_path.is_file():
            report.add("error", f"Claude Code: {doc} imports missing {target_path}")
            return
        doc = target_path


def codex_settings(config: Path) -> tuple[list[str], int, dict[str, str]]:
    """Read the Codex settings this check needs.

    Args:
        config: path to Codex's config.toml (may be absent).

    Returns:
        (project_root_markers, project_doc_max_bytes, {project path: trust_level}).

    Raises:
        tomllib.TOMLDecodeError: when the file exists but is not valid TOML.
    """
    if not config.is_file():
        return list(DEFAULT_MARKERS), DEFAULT_MAX_BYTES, {}
    data = tomllib.loads(config.read_text(encoding="utf-8"))
    trust = {p: str(v.get("trust_level", "")) for p, v in (data.get("projects") or {}).items() if isinstance(v, dict)}
    return list(data.get("project_root_markers", DEFAULT_MARKERS)), int(data.get("project_doc_max_bytes", DEFAULT_MAX_BYTES)), trust


def codex_root(start: Path, markers: list[str]) -> Path:
    """Codex's project root: the nearest folder (start included) holding any marker; the start folder when none does.

    Args:
        start: the folder Codex starts in.
        markers: marker names (files or folders).

    Returns:
        The project root folder.
    """
    for d in [start, *start.parents]:
        if any((d / m).exists() for m in markers):
            return d
    return start


def codex_docs(root: Path, start: Path, report: Report, max_bytes: int) -> None:
    """Record the files Codex concatenates from root down to start and check them against its byte limit.

    Args:
        root: Codex's project root.
        start: the folder Codex starts in.
        report: the report to fill.
        max_bytes: project_doc_max_bytes.

    Returns:
        None.
    """
    rel = start.relative_to(root).parts if start != root else ()
    folders = [root] + [root.joinpath(*rel[: i + 1]) for i in range(len(rel))]
    total = 0
    for d in folders:
        for name in DOC_NAMES:
            if (d / name).is_file():
                size = (d / name).stat().st_size
                report.codex_docs.append((d / name, size))
                if total < max_bytes < total + size:
                    report.add("error", f"Codex: {d / name} is cut at byte {max_bytes - total} of {size} (project_doc_max_bytes {max_bytes})")
                elif total >= max_bytes:
                    report.add("error", f"Codex: {d / name} is not loaded at all (past project_doc_max_bytes {max_bytes})")
                total += size
                break
    report.add("info", f"Codex: {len(report.codex_docs)} file(s), {total} of {max_bytes} bytes")


def git_repos(root: Path, depth: int = SCAN_DEPTH) -> list[Path]:
    """Git repositories strictly below root, to a bounded depth.

    Args:
        root: the folder to scan.
        depth: how many folder levels below root to look.

    Returns:
        Repository folders found (each holds a `.git`).
    """
    found: list[Path] = []
    frontier = [root]
    for _ in range(depth):
        nxt: list[Path] = []
        for d in frontier:
            try:
                children = [c for c in d.iterdir() if c.is_dir() and not c.is_symlink() and c.name not in SCAN_SKIP]
            except OSError:
                continue
            for c in children:
                if (c / ".git").exists():
                    found.append(c)
                nxt.append(c)
        frontier = nxt
    return found


def trust_check(root: Path, trust: dict[str, str], report: Report) -> None:
    """Flag trust that spreads to repos nobody trusted, and per-repo trust that no longer matches.

    Args:
        root: Codex's project root.
        trust: {project path: trust_level} from config.toml.
        report: the report to fill.

    Returns:
        None.
    """
    level = trust.get(str(root), "")
    report.add("info", f"Codex trust for root {root}: {level or 'no entry (Codex asks)'}")
    repos = [r for r in git_repos(root) if r != root]
    if level == "trusted":
        untrusted = [r for r in repos if trust.get(str(r)) != "trusted"]
        if untrusted:
            names = ", ".join(str(r) for r in untrusted[:5]) + (" ..." if len(untrusted) > 5 else "")
            report.add("error", f"Codex: trusted root covers {len(untrusted)} repo(s) without their own trust entry: {names}")
    else:
        stale = [r for r in repos if trust.get(str(r)) == "trusted"]
        if stale:
            report.add("warn", f"Codex: {len(stale)} per-repo trust entr(y/ies) below the root no longer apply (root is the project now)")


def run(start: Path, config: Path, markers: list[str] | None) -> Report:
    """Build the full report for one folder.

    Args:
        start: the folder an agent starts in.
        config: Codex config.toml path.
        markers: marker override, or None to use the config's.

    Returns:
        The filled report.
    """
    report = Report()
    claude_chain(start, report)
    cfg_markers, max_bytes, trust = codex_settings(config)
    use = markers or cfg_markers
    if len(use) > 1:
        report.add("info", f"Codex: markers {use}: the nearest folder holding any of them wins")
    report.codex_root = codex_root(start, use)
    codex_docs(report.codex_root, start, report, max_bytes)
    missing = [p for p in report.claude if p.resolve() not in {d.resolve() for d, _ in report.codex_docs}]
    codex_global = config.parent / "AGENTS.md"
    for p in list(missing):
        if codex_global.is_file() and p.read_bytes() == codex_global.read_bytes():
            missing.remove(p)
            report.add("info", f"Codex: {p} is the global policy; Codex reads its identical copy {codex_global}")
        elif codex_global.is_file() and p == report.claude[-1]:
            missing.remove(p)
            report.add("warn", f"Codex: global {codex_global} differs from the chain's top {p}; Codex uses its own copy")
    if missing:
        report.add("warn", "Codex: does not load " + ", ".join(str(p) for p in missing) + " (above its root; it ignores @ imports)")
    trust_check(report.codex_root, trust, report)
    return report


def main(argv: list[str] | None = None) -> int:
    """Command-line entry point.

    Args:
        argv: arguments (defaults to sys.argv[1:]).

    Returns:
        Exit code: 0, or 1 with --check when an error was found; 2 on a bad argument or unreadable config.
    """
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--path", default=".", help="folder an agent starts in (default: current folder)")
    ap.add_argument("--codex-config", default="~/.codex/config.toml", help="Codex config.toml (default: ~/.codex/config.toml)")
    ap.add_argument("--markers", nargs="+", help="override project_root_markers, e.g. --markers .codex-root")
    ap.add_argument("--check", action="store_true", help="exit 1 when an error is found")
    args = ap.parse_args(argv)
    start = Path(args.path).expanduser().resolve()
    if not start.is_dir():
        print(f"not a folder: {start}", file=sys.stderr)
        return 2
    try:
        report = run(start, Path(args.codex_config).expanduser(), args.markers)
    except tomllib.TOMLDecodeError as exc:
        print(f"cannot parse Codex config: {exc}", file=sys.stderr)
        return 2
    print(f"== {start}")
    print("  Claude Code chain: " + (" -> ".join(str(p) for p in report.claude) or "none"))
    print(f"  Codex root: {report.codex_root}")
    print("  Codex loads: " + (", ".join(f"{p} ({n} B)" for p, n in report.codex_docs) or "none"))
    print("\n".join(report.lines))
    return 1 if (args.check and report.errors) else 0


if __name__ == "__main__":
    sys.exit(main())
