#!/usr/bin/env python3
"""Summarise V8 .cpuprofile files (VS Code extension host, Node, Chrome): self time per extension, hottest functions, hottest stacks. Read-only. Stdlib only.

Why (Learned 2026-10-28, ansible-wifi): VS Code's Git view went stale and each git call took ~950 ms although the same command took 70 ms on the
CLI. The extension host was pinned, and exthost.log named an extension and saved a .cpuprofile per stall. Reading those profiles by hand is not
practical; this reduces each one to the extension, the functions and the call chain that burn the time, which is what points at the cause
(there: Foam re-labelling every note against every same-named note, fed by symlinked snapshot folders).

Profiles live where exthost.log says (`UNRESPONSIVE extension host: '<ext>' took N% ... saved PROFILE here: 'file://...'`), usually
$TMPDIR/exthost-*.cpuprofile. Stacks show only frames from the extension under study: `--ext` names it, else the one with the most self time.

Usage:
    cpuprofile_summary.py PROFILE [PROFILE ...] [--top 6] [--ext foam.foam-vscode]
Exit: 0 when every profile was read, 1 when one could not be read or parsed, 2 on bad arguments.
"""

from __future__ import annotations

import argparse
import collections
import json
import re
import sys
from pathlib import Path

#: The oldest Python this script runs on: it runs with the target project's own interpreter (the pack's contract test parses it at this grammar).
REQUIRES_PYTHON = (3, 11)

#: The extension folder in a script URL, e.g. .../extensions/foam.foam-vscode-0.46.0/out/... -> foam.foam-vscode-0.46.0.
EXT_DIR = re.compile(r"/extensions/([^/]+)/")


def ext_of(url: str) -> str:
    """Name the owner of a call frame from its script URL.

    Args:
        url: the frame's script URL (empty for native frames and the garbage collector).

    Returns:
        The extension folder name, "core" for other scripts (VS Code itself, Node), or "(native/gc)" when there is no URL.
    """
    m = EXT_DIR.search(url or "")
    if m:
        return m.group(1)
    return "core" if url else "(native/gc)"


def summarise(prof: dict, top: int = 6, ext: str | None = None) -> dict:
    """Reduce one parsed profile to self time by extension, by function and by stack of the extension under study.

    Args:
        prof: the parsed .cpuprofile JSON (keys nodes, samples, timeDeltas).
        top: how many rows to keep in each list.
        ext: substring naming the extension whose frames make up the stacks; None picks the extension with the most self time.

    Returns:
        A dict with total_ms, ext (the one studied), and lists by_ext, by_fn, by_stack of (label, percent of total) rows, largest first.
    """
    nodes = {n["id"]: n for n in prof["nodes"]}
    parent = {c: n["id"] for n in prof["nodes"] for c in n.get("children", [])}
    self_us: collections.Counter = collections.Counter()
    for sid, dt in zip(prof["samples"], prof["timeDeltas"]):
        self_us[sid] += dt
    total = sum(self_us.values()) or 1
    by_ext: collections.Counter = collections.Counter()
    by_fn: collections.Counter = collections.Counter()
    for nid, us in self_us.items():
        cf = nodes[nid]["callFrame"]
        by_ext[ext_of(cf["url"])] += us
        by_fn[f"{cf['functionName'] or '(anon)'}  {ext_of(cf['url'])}:{cf['lineNumber']}"] += us
    studied = ext or next((e for e, _ in by_ext.most_common() if e not in ("core", "(native/gc)")), "")
    by_stack: collections.Counter = collections.Counter()
    for nid, us in self_us.items():
        chain, cur = [], nid
        while cur in nodes:  # innermost frame first, up to the root
            f = nodes[cur]["callFrame"]
            if studied and studied in ext_of(f["url"]):
                chain.append(f"{f['functionName'] or '(anon)'}:{f['lineNumber']}")
            cur = parent.get(cur)
        if chain:
            by_stack[" <- ".join(chain[:8])] += us

    def rows(c: collections.Counter) -> list[tuple[str, float]]:
        """Top rows of a counter as percentages of the profile's total.

        Args:
            c: microseconds per label.

        Returns:
            Up to `top` (label, percent) pairs, largest first.
        """
        return [(k, round(v * 100 / total, 1)) for k, v in c.most_common(top)]

    return {"total_ms": round(total / 1000), "ext": studied, "by_ext": rows(by_ext), "by_fn": rows(by_fn), "by_stack": rows(by_stack)}


def render(name: str, s: dict) -> str:
    """Format one summary for the console.

    Args:
        name: the profile's file name, for the heading.
        s: a summary from summarise().

    Returns:
        The text block, one row per line.
    """
    out = [f"== {name}  total {s['total_ms']} ms  stacks for: {s['ext'] or '(none)'}"]
    for kind in ("ext", "fn", "stack"):
        out += [f"  {kind:5} {pct:5.1f}%  {label}" for label, pct in s[f"by_{kind}"]]
    return "\n".join(out)


def main(argv: list[str] | None = None) -> int:
    """Summarise each profile named on the command line.

    Args:
        argv: command-line arguments; None reads sys.argv.

    Returns:
        0 when every profile was read, 1 when one could not be read or parsed.
    """
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("profiles", nargs="+", type=Path, help=".cpuprofile files")
    ap.add_argument("--top", type=int, default=6, help="rows per list (default 6)")
    ap.add_argument("--ext", help="extension (substring) whose frames form the stacks; default: the one with the most self time")
    args = ap.parse_args(argv)
    rc = 0
    for p in args.profiles:
        try:
            with p.open(encoding="utf-8") as fh:
                prof = json.load(fh)
            print(render(p.name, summarise(prof, args.top, args.ext)))
        except (OSError, ValueError, KeyError) as exc:
            print(f"== {p.name}  unreadable: {exc}", file=sys.stderr)
            rc = 1
    return rc


if __name__ == "__main__":
    sys.exit(main())
