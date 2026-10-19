#!/usr/bin/env python3
"""Find entry-point scripts that write without a dry-run default: every writer takes `--apply`, or is registered with the reason it may not.
Read-only. Stdlib only.

Promoted from unified-network-controller `check_write_gates` (2026-10-19). Why (operator, 2026-10-06): a test script wrote to production devices
and a seeding script could delete real records on a bare run. The rule: read is the default; a script that changes anything prints its plan and
changes nothing until it is run with `--apply` (a subcommand such as `apply` counts when registered). A registered exception names its own gate.

A writer is an entry point (the language's main marker) whose text matches a write pattern. The patterns are a heuristic and project-specific
writes are added in the config; a registered exception that no longer writes, no longer exists or now takes `--apply` fails too, so the register
cannot go stale.

Config (JSON, optional; every key optional):
    {"roots": ["scripts"], "suffixes": [".py", ".sh"], "write_patterns": ["\\\\.delete\\\\("], "apply_pattern": "--apply",
     "exceptions": {"scripts/collector.py": "pushes metrics by design; --dry-run reads only"}}

Usage:
    write_gates.py --project-root . [--config scripts/write-gates.json] [--list]
Exit: 0 when every writer is gated or registered and the register is current, 1 otherwise, 2 on bad arguments.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import code_map

#: The oldest Python this script runs on: it runs with the target project's own interpreter (the pack's contract test parses it at this grammar).
REQUIRES_PYTHON = (3, 11)

#: Write patterns every project starts with, any language: changes to a live system (HTTP writes, SQL changes) and recursive deletion. Matched
#: case-sensitively (`"delete"` as an action name is not an HTTP DELETE). Writing a local generated file is not a live write (a renderer's
#: `--write` is its own gate); add project-specific writes (an SNMP set, a client library's create call) in the config.
DEFAULT_WRITES = (
    r"""["'](?:POST|PATCH|PUT|DELETE)["']""",
    r"\b(?:requests|httpx|session|client)\.(?:post|patch|put|delete)\(",
    r"\bshutil\.rmtree\(",
    r"\b(?:INSERT\s+INTO|UPDATE\s+\w+\s+SET|DELETE\s+FROM|DROP\s+TABLE|ALTER\s+TABLE|TRUNCATE\s+TABLE)\b",
    r"\bfetch\([^)]*method:\s*[\"'](?:POST|PUT|PATCH|DELETE)",
)
#: Further patterns for shell scripts only (in other languages these words are mostly prose in docstrings): recursive or forced removal,
#: package installs, service control.
SHELL_WRITES = (
    r"\brm\s+-[a-z]*[rf][a-z]*\b",
    r"\b(?:apt|apt-get|dnf|yum|brew)\s+install\b|\bpip3?\s+install\b",
    r"\bsystemctl\s+(?:restart|stop|start|enable|disable)\b",
)
SHELL_SUFFIXES = (".sh", ".bash")
#: What marks a file as an entry point, per suffix.
ENTRY = {".py": r"""__name__\s*==\s*["']__main__["']""", ".sh": r"^#!", ".bash": r"^#!", ".js": r"^#!|process\.argv", ".ts": r"^#!|process\.argv",
         ".go": r"^func main\(", ".rs": r"^fn main\("}
DEFAULT_APPLY = r"--apply\b"


def load_config(path: Path | None, cmap: dict | None = None) -> dict:
    """The checker's settings: the JSON config if given, else the code map's [write_gates] section, defaults filled in.

    Args:
        path: the JSON config, or None.
        cmap: a loaded code map (code_map.load), or None.

    Returns:
        {"roots", "suffixes", "write_patterns", "apply_pattern", "exceptions"}.

    Raises:
        ValueError: when the file is not a JSON object.
    """
    cfg = json.loads(path.read_text(encoding="utf-8")) if path else code_map.section(cmap or {}, "write_gates")
    if not isinstance(cfg, dict):
        raise ValueError("write-gates config must be a JSON object")
    return {"roots": cfg.get("roots", ["scripts"]), "suffixes": cfg.get("suffixes", sorted(ENTRY)),
            "write_patterns": list(DEFAULT_WRITES) + list(cfg.get("write_patterns", [])),
            "apply_pattern": cfg.get("apply_pattern", DEFAULT_APPLY), "exceptions": dict(cfg.get("exceptions", {}))}


def writers(root: Path, cfg: dict, skip: set[str]) -> dict[str, bool]:
    """Every entry point that writes, and whether it takes the apply flag.

    Args:
        root: the project root.
        cfg: load_config()'s result.
        skip: repo-relative files never examined (the checker and its config).

    Returns:
        {path: has apply flag}.
    """
    write = re.compile("|".join(f"(?:{p})" for p in cfg["write_patterns"]))
    shell = re.compile("|".join(f"(?:{p})" for p in SHELL_WRITES))
    apply = re.compile(cfg["apply_pattern"])
    out: dict[str, bool] = {}
    for folder in cfg["roots"]:
        base = root / folder
        for path in sorted(base.rglob("*")) if base.is_dir() else []:
            rel = path.relative_to(root).as_posix()
            if not path.is_file() or path.suffix not in cfg["suffixes"] or rel in skip or "__pycache__" in path.parts:
                continue
            text = path.read_text(encoding="utf-8", errors="replace")
            writes = write.search(text) or (path.suffix in SHELL_SUFFIXES and shell.search(text))
            if re.search(ENTRY.get(path.suffix, r"$^"), text, re.M) and writes:
                out[rel] = bool(apply.search(text))
    return out


def problems(found: dict[str, bool], exceptions: dict[str, str]) -> list[str]:
    """Unregistered ungated writers and stale register entries.

    Args:
        found: writers()'s result.
        exceptions: {path: reason} from the config.

    Returns:
        One message per problem.
    """
    out = [f"{rel} writes without taking --apply: make it plan by default with --apply, or register it with its gate and reason"
           for rel, gated in sorted(found.items()) if not gated and rel not in exceptions]
    for rel, reason in sorted(exceptions.items()):
        if not str(reason).strip():
            out.append(f"exception {rel} has no reason")
        elif rel not in found:
            out.append(f"exception {rel} no longer exists or no longer writes: remove it")
        elif found[rel]:
            out.append(f"exception {rel} now takes --apply: remove it")
    return out


def main(argv: list[str] | None = None) -> int:
    """Command line.

    Args:
        argv: arguments (default sys.argv[1:]).

    Returns:
        0 when clean, 1 on a problem, 2 on bad arguments.
    """
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--project-root", type=Path, default=Path("."))
    ap.add_argument("--config", type=Path, help="JSON config (roots, suffixes, write_patterns, apply_pattern, exceptions)")
    ap.add_argument("--list", action="store_true", help="print every writer found and whether it is gated")
    ap.add_argument("--code-map", type=Path, help="the project's code-map.toml (default: code-map.toml at the root when present)")
    args = ap.parse_args(argv)
    root = args.project_root.resolve()
    try:
        cfg = load_config(args.config, code_map.for_root(root, args.code_map))
    except (OSError, ValueError) as exc:
        print(f"write_gates: {exc}", file=sys.stderr)
        return 2
    skip = {Path(__file__).resolve().relative_to(root).as_posix()} if Path(__file__).resolve().is_relative_to(root) else set()
    found = writers(root, cfg, skip)
    if args.list:
        for rel, gated in found.items():
            print(f"{'gated   ' if gated else 'UNGATED '} {rel}" + (f"  ({cfg['exceptions'][rel]})" if rel in cfg["exceptions"] else ""))
    issues = problems(found, cfg["exceptions"])
    for line in issues:
        print(f"FAIL write-gate: {line}")
    if not issues:
        print(f"write_gates: OK, {len(found)} writer(s), every one gated or registered")
    return 1 if issues else 0


if __name__ == "__main__":
    sys.exit(main())
