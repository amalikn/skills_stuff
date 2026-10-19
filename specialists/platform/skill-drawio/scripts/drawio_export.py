#!/usr/bin/env python3
"""Export draw.io pages to PNG (or SVG, JPG, PDF) with the desktop app, for self-review: one image per page asked for. Writes only the images.

Pages are counted from 1, as the draw.io CLI counts them; `--layers 0` keeps only the base layer (proves the colour layers hide what they
should). Each export runs under a timeout. Review loop: references/export-and-self-review.md.

Usage:
    drawio_export.py FILE.drawio --out-dir DIR [--pages 1,2] [--layers 0] [--scale 2] [--binary PATH] [--timeout 120]
Exit: 0 when every image was written, 1 when an export failed, 2 on bad arguments or no draw.io binary.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from drawio import export

#: The oldest Python this script runs on (stdlib only).
REQUIRES_PYTHON = (3, 11)


def main(argv: list[str] | None = None) -> int:
    """Command line.

    Args:
        argv: arguments (default sys.argv[1:]).

    Returns:
        0, 1 or 2 as the module header says.
    """
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("file", type=Path)
    ap.add_argument("--out-dir", type=Path, required=True)
    ap.add_argument("--pages", default="1", help="comma-separated pages, counted from 1 (default 1)")
    ap.add_argument("--layers", default="", help="comma-separated layer indexes to keep (default all; 0 is the base layer)")
    ap.add_argument("--scale", type=float, default=1.0)
    ap.add_argument("--format", default="png", choices=("png", "svg", "jpg", "pdf"))
    ap.add_argument("--binary", default="", help="the draw.io binary (default: found on PATH or in the usual places)")
    ap.add_argument("--timeout", type=int, default=export.TIMEOUT_S, help="seconds per export before it is killed")
    args = ap.parse_args(argv)
    try:
        binary = export.find_binary(args.binary)
        page_list = [int(p) for p in args.pages.split(",") if p.strip()]
        layers = tuple(int(x) for x in args.layers.split(",") if x.strip())
    except (FileNotFoundError, ValueError) as exc:
        print(f"drawio_export: {exc}", file=sys.stderr)
        return 2
    args.out_dir.mkdir(parents=True, exist_ok=True)
    rc = 0
    for page in page_list:
        suffix = f"-layers{'-'.join(map(str, layers))}" if layers else ""
        out = args.out_dir / f"{args.file.stem}-p{page}{suffix}.{args.format}"
        try:
            print(f"wrote {export.run(export.export_argv(binary, args.file, out, page, layers, args.scale), args.timeout)}")
        except (RuntimeError, ValueError) as exc:
            print(f"drawio_export: page {page}: {exc}", file=sys.stderr)
            rc = 1
    return rc


if __name__ == "__main__":
    sys.exit(main())
