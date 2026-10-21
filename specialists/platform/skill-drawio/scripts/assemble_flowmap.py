#!/usr/bin/env python3
"""Assemble a flow map from its parts: parts/master.yaml and the files its `#@include` lines name become one complete, generated flows.yaml.

The parts are the source and flows.yaml is built from them, as unified-network-controller builds nautobot/catalog.yaml from its catalog parts
(operator, 2026-10-21: "it was being built by the individual files, it was not using pointers"). The generated file carries a banner, holds
no include lines and no part header lines (`#% ...`), and every reader (the renderer, a person, an agent) reads it whole. A part that no include names is refused, so nothing
silently drops out of the map.

Run (from the project root, with the project's interpreter):
    python3 <skill-drawio>/scripts/assemble_flowmap.py --master docs/flows/parts/master.yaml --out docs/flows/flows.yaml           # drift check
    python3 <skill-drawio>/scripts/assemble_flowmap.py --master docs/flows/parts/master.yaml --out docs/flows/flows.yaml --write   # build it
Writes only with --write, only the output file. Exit: 0 current or written; 1 drift, a stray part or an unreadable part; 2 bad arguments.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from flowmap.model import expand_includes

REQUIRES_PYTHON = (3, 11)
#: A part's own header lines (what it is, where it lands) start with this and stay out of the generated map, as the catalog's do.
PART_HEADER = "#%"


def banner(master: str, command: str) -> str:
    """The generated file's first lines.

    Args:
        master: the master's path, as the project names it.
        command: the command that rebuilds the file.

    Returns:
        Two YAML comment lines and a blank line.
    """
    return (f"# GENERATED from {master} and the parts it includes, by skill-drawio's assemble_flowmap.py (`{command}`).\n"
            "# Edit the parts, never this file: the check fails when it differs from what the parts assemble to.\n\n")


def assemble(master: Path, master_name: str, command: str) -> tuple[str, list[str]]:
    """The generated text, and every part file beside the master that no include names.

    Args:
        master: the master file.
        master_name: its path as written in the banner.
        command: the rebuild command named in the banner.

    Returns:
        (the full text, stray part paths).

    Raises:
        OSError: a part cannot be read.
        ValueError: a part is included twice.
    """
    used: list[Path] = []
    body = "".join(line + "\n" for line in expand_includes(master, used).splitlines() if not line.lstrip().startswith(PART_HEADER))
    folder = master.resolve().parent
    stray = [p.name for p in sorted(folder.glob("*.yaml")) if p.resolve() not in used and p.resolve() != master.resolve()]
    return banner(master_name, command) + body, stray


def main(argv: list[str] | None = None) -> int:
    """Check or write the generated map.

    Args:
        argv: command-line arguments; None reads sys.argv.

    Returns:
        0 current or written; 1 drift, stray parts or an unreadable part.
    """
    if sys.version_info < REQUIRES_PYTHON:
        print(f"needs Python {REQUIRES_PYTHON[0]}.{REQUIRES_PYTHON[1]} or newer", file=sys.stderr)
        return 2
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--master", required=True, type=Path, help="parts/master.yaml")
    ap.add_argument("--out", required=True, type=Path, help="the generated flows.yaml")
    ap.add_argument("--command", default="just flows", help="the rebuild command named in the banner")
    ap.add_argument("--write", action="store_true", help="write the output (default: report drift only)")
    args = ap.parse_args(argv)
    try:
        text, stray = assemble(args.master, args.master.as_posix(), args.command)
    except (OSError, ValueError) as exc:
        print(f"cannot assemble {args.master}: {exc}")
        return 1
    if stray:
        print(f"refused: parts no #@include names: {', '.join(stray)}")
        return 1
    current = args.out.read_text(encoding="utf-8") if args.out.is_file() else ""
    if args.write:
        if current != text:
            args.out.write_text(text, encoding="utf-8")
        print(f"wrote {args.out} from {args.master}")
        return 0
    if current != text:
        print(f"drift: {args.out} differs from what {args.master} assembles to; run with --write")
        return 1
    print(f"ok: {args.out} is what {args.master} assembles to")
    return 0


if __name__ == "__main__":
    sys.exit(main())
