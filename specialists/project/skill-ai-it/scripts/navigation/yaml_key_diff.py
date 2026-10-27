#!/usr/bin/env python3
"""Compare a YAML file against a git ref by key, and list the comments the working copy lost.

Why: the navigation upgrade's `update_rules` merge re-serialises `context-map.yaml`, so its line diff runs to hundreds of lines while the real
change is a key or two, and every comment (the purpose header included) is dropped (smc-resiliency refresh, 2026-10-14; references/pitfalls.md).
This prints the real change and the lost comments so they can be checked and restored.

Run: `just nav-check-context-map` in a project, or
`<venv python> scripts/navigation/yaml_key_diff.py --project-root <project> [--file context-map.yaml] [--ref HEAD]`. Needs PyYAML.
Read-only. Exit 0 when no comment was lost, 1 when one was, 2 on a usage or read error.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def load_yaml(text: str):
    """Parse YAML text with PyYAML.

    Args:
        text: the YAML document.

    Returns:
        The parsed object.

    Raises:
        SystemExit: exit 2 when PyYAML is not installed.
    """
    try:
        import yaml
    except ImportError:
        print("ERROR: PyYAML is required; run with the skill's venv python", file=sys.stderr)
        raise SystemExit(2)
    return yaml.safe_load(text)


def key_changes(old, new, prefix: str = "") -> list[str]:
    """Describe how two parsed mappings differ, one line per key, descending one level into changed mappings.

    Args:
        old: the parsed document at the ref.
        new: the parsed working copy.
        prefix: the dotted path of the mapping being compared.

    Returns:
        Lines such as `added: update_rules.governance_navigation`, `removed: x`, `changed: y`.
    """
    if not isinstance(old, dict) or not isinstance(new, dict):
        return [] if old == new else [f"changed: {prefix or '(document)'}"]
    out = []
    for key in sorted(set(old) | set(new), key=str):
        path = f"{prefix}{key}"
        if key not in old:
            out.append(f"added: {path}")
        elif key not in new:
            out.append(f"removed: {path}")
        elif old[key] != new[key]:
            if isinstance(old[key], dict) and isinstance(new[key], dict) and not prefix:
                out.extend(key_changes(old[key], new[key], path + "."))
            else:
                out.append(f"changed: {path}")
    return out


def lost_comments(old_text: str, new_text: str) -> list[str]:
    """List the comment lines of the old text that no longer appear in the new text.

    Args:
        old_text: the file at the ref.
        new_text: the working copy.

    Returns:
        Each lost comment, stripped, prefixed with its line number in the old text.
    """
    kept = {line.strip() for line in new_text.splitlines() if line.strip().startswith("#")}
    return [f"{n}: {line.strip()}" for n, line in enumerate(old_text.splitlines(), 1) if line.strip().startswith("#") and line.strip() not in kept]


def main() -> int:
    """Read the file at the ref and in the working tree, print key changes and lost comments.

    Returns:
        0 when no comment was lost, 1 when one was, 2 on a read error.
    """
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--project-root", default=".")
    ap.add_argument("--file", default="context-map.yaml")
    ap.add_argument("--ref", default="HEAD")
    args = ap.parse_args()
    root = Path(args.project_root).resolve()
    path = root / args.file
    try:
        new_text = path.read_text(encoding="utf-8")
        old_text = subprocess.run(["git", "show", f"{args.ref}:./{args.file}"], cwd=root, check=True, capture_output=True, text=True, timeout=60).stdout
    except (OSError, subprocess.CalledProcessError) as exc:
        print(f"ERROR: cannot read {args.file} at {args.ref} or in the working tree: {exc}", file=sys.stderr)
        return 2
    changes = key_changes(load_yaml(old_text), load_yaml(new_text))
    lost = lost_comments(old_text, new_text)
    print(f"{args.file} vs {args.ref}: {len(changes)} key change(s), {len(lost)} comment(s) lost")
    for line in changes:
        print(f"  {line}")
    for line in lost:
        print(f"  lost comment {line}")
    return 1 if lost else 0


if __name__ == "__main__":
    sys.exit(main())
