#!/usr/bin/env python3
"""Print what an existing draw.io drawing says, as text or JSON: per page its labelled boxes and its connections (by the labels of their ends),
compressed pages decoded. Read-only: a hand-drawn drawing is source and is never rewritten.

Usage:
    drawio_read.py FILE.drawio [...] [--json OUT] [--geometry]
    (--geometry adds every shape's rectangle and every line's path in page coordinates, group offsets resolved)
Exit: 0 when every file was read, 1 when one could not be, 2 on bad arguments.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from drawio import read

#: The oldest Python this script runs on (stdlib only).
REQUIRES_PYTHON = (3, 11)


def summary(name: str, pages: list[dict]) -> list[str]:
    """Text lines for one file.

    Args:
        name: the file name.
        pages: from drawio.read.pages().

    Returns:
        The lines.
    """
    out = [f"== {name}"]
    for p in pages:
        out.append(f"-- page {p['name']!r}: {len(p['boxes'])} boxes, {len(p['edges'])} connections")
        out += [f"   box  {b['label']}" for b in p["boxes"]]
        out += [f"   edge {e['source']!r} -> {e['target']!r}" + (f" ({e['label']})" if e["label"] else "") for e in p["edges"]]
    return out


def main(argv: list[str] | None = None) -> int:
    """Command line.

    Args:
        argv: arguments (default sys.argv[1:]).

    Returns:
        0, 1 or 2 as the module header says.
    """
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("files", type=Path, nargs="+")
    ap.add_argument("--json", type=Path, help="also write everything read as JSON to this file")
    ap.add_argument("--geometry", action="store_true", help="include shapes and line paths in the JSON")
    args = ap.parse_args(argv)
    rc, everything = 0, {}
    for f in args.files:
        try:
            pages = read.pages(f.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            print(f"drawio_read: {f}: {exc}", file=sys.stderr)
            rc = 1
            continue
        print("\n".join(summary(f.name, pages)))
        everything[str(f)] = pages if args.geometry else [{k: p[k] for k in ("name", "boxes", "edges")} for p in pages]
    if args.json:
        args.json.write_text(json.dumps(everything, indent=2) + "\n", encoding="utf-8")
        print(f"wrote {args.json}")
    return rc


if __name__ == "__main__":
    sys.exit(main())
