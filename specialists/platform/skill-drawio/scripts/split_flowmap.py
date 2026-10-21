#!/usr/bin/env python3
"""Split a long flow map into parts (parts/master.yaml plus one file per section) and assemble flows.yaml from them, without changing what it loads to.

Components split by their `group` (when each group's components are contiguous), flows at section comment lines (`  # ==== <title>`), and an
`options` block into its own part. parts/master.yaml keeps everything else and an include line per part; flows.yaml is then generated from the
parts by assemble_flowmap.py, complete and without pointers (operator, 2026-10-21, as unified-network-controller builds its catalog). Before
writing, the split is proved: the assembled map must load to exactly the data the original map loads to. Promoted 2026-10-21 after smc-resiliency's and unified-network-
controller's maps were split by hand the same day.

Run (from the project root, with the project's interpreter, PyYAML present):
    python3 <skill-drawio>/scripts/split_flowmap.py --map docs/flows/flows.yaml            # plan: the parts and their line counts
    python3 <skill-drawio>/scripts/split_flowmap.py --map docs/flows/flows.yaml --apply    # write the parts and the new master
Writes only with --apply, only the master and files under its parts folder. Exit: 0 done or planned; 1 the split would change the data or a
part exists already; 2 bad arguments.
"""

from __future__ import annotations

import argparse
import re
import sys
import tempfile
from pathlib import Path

from assemble_flowmap import assemble
from flowmap.model import expand_includes

REQUIRES_PYTHON = (3, 11)

SECTION = re.compile(r"^  # =+ (?P<title>.+?)\s*$")
TOP = re.compile(r"^(?P<key>[a-z_]+):")


def slug(text: str) -> str:
    """A file-name slug for a group or section title.

    Args:
        text: the title.

    Returns:
        Lower case words joined by hyphens.
    """
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:40] or "part"


def top_blocks(lines: list[str]) -> list[tuple[str, int, int]]:
    """The map's top-level keys with their line ranges.

    Args:
        lines: the map's lines.

    Returns:
        (key, first line index, end index) per top-level key, in file order.
    """
    starts = [(m.group("key"), i) for i, line in enumerate(lines) if (m := TOP.match(line))]
    return [(k, i, starts[n + 1][1] if n + 1 < len(starts) else len(lines)) for n, (k, i) in enumerate(starts)]


def split_components(body: list[str]) -> list[tuple[str, list[str]]] | None:
    """Components cut where the `group` changes; None when a group appears in two runs (the split would reorder them).

    Args:
        body: the lines under `components:`.

    Returns:
        (part name, lines) per group, or None.
    """
    items, cur = [], []
    for line in body:   # lines before the first item (a comment) stay with it
        if line.startswith("  - ") and any(x.startswith("  - ") for x in cur):
            items.append(cur)
            cur = []
        cur.append(line)
    if cur:
        items.append(cur)
    runs: list[tuple[str, list[str]]] = []
    for item in items:
        g = next((m.group(1).strip().strip('"') for x in item if (m := re.match(r"^    group:\s*(.+)$", x))), "other")
        if runs and runs[-1][0] == g:
            runs[-1][1].extend(item)
        elif any(r[0] == g for r in runs):
            return None
        else:
            runs.append((g, list(item)))
    return [(f"components-{slug(g)}", lines) for g, lines in runs]


def split_sections(body: list[str], prefix: str) -> list[tuple[str, list[str]]]:
    """A list cut at section comment lines; one part when it has none.

    Args:
        body: the lines under the key.
        prefix: the part name prefix (for example "flows").

    Returns:
        (part name, lines) per section.
    """
    parts: list[tuple[str, list[str]]] = []
    for line in body:
        m = SECTION.match(line)
        if m or not parts:
            parts.append((f"{prefix}-{slug(m.group('title'))}" if m else prefix, []))
        parts[-1][1].append(line)
    return [(n, ls) for n, ls in parts if any(x.strip() for x in ls)]


def plan(text: str) -> tuple[list[str], dict[str, list[str]]]:
    """The new master and its parts.

    Args:
        text: the map's text.

    Returns:
        (master lines, {part name: part lines dedented by two}).
    """
    lines = text.splitlines()
    master, parts = [], {}
    blocks = top_blocks(lines)
    master += lines[:blocks[0][1]] if blocks else lines
    for key, a, b in blocks:
        body = lines[a + 1:b]
        trail = []
        while body and not body[-1].strip():
            trail.insert(0, body.pop())
        if key == "components":
            cut = split_components(body) or [("components", body)]
        elif key == "flows":
            cut = split_sections(body, "flows")
        elif key == "options":
            cut = [("options", body)]
        else:
            master += lines[a:b]
            continue
        master.append(lines[a])
        for name, ls in cut:   # each part opens with a `#%` header (dropped when assembled), as a catalog part does
            what = name.split("-", 1)[1].replace("-", " ") if "-" in name else name
            header = [f"#% Part: {key}, {what}", f"#% Lands under: {key}"]
            parts[name] = header + [x[2:] if x.startswith("  ") else x for x in ls]
            master.append(f"  #@include {name}.yaml")
        master += trail
    return master, parts


def proved(map_path: Path, master: list[str], parts: dict[str, list[str]]) -> bool:
    """True when the split master, expanded, loads to the same data as the original map.

    Args:
        map_path: the original map.
        master: the new master's lines.
        parts: the parts' lines.

    Returns:
        Whether the loaded data is equal.
    """
    import yaml

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        for name, ls in parts.items():
            (root / f"{name}.yaml").write_text("\n".join(ls) + "\n", encoding="utf-8")
        (root / "master.yaml").write_text("\n".join(master) + "\n", encoding="utf-8")
        return yaml.safe_load(expand_includes(root / "master.yaml")) == yaml.safe_load(map_path.read_text(encoding="utf-8"))


def main(argv: list[str] | None = None) -> int:
    """Plan or apply the split.

    Args:
        argv: command-line arguments; None reads sys.argv.

    Returns:
        0 planned or written; 1 not provable, or parts exist already.
    """
    if sys.version_info < REQUIRES_PYTHON:
        print(f"needs Python {REQUIRES_PYTHON[0]}.{REQUIRES_PYTHON[1]} or newer", file=sys.stderr)
        return 2
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--map", required=True, type=Path, help="the flow map to split")
    ap.add_argument("--apply", action="store_true", help="write the parts and the new master (default: plan only)")
    args = ap.parse_args(argv)
    text = args.map.read_text(encoding="utf-8")
    if "#@include" in text or text.startswith("# GENERATED from"):
        print(f"{args.map} is split already (it has #@include lines or is generated from parts)")
        return 1
    master, parts = plan(text)
    for name, ls in parts.items():
        print(f"  parts/{name}.yaml  {len(ls)} lines")
    print(f"  parts/master.yaml  {len(master)} lines (the map was {len(text.splitlines())})")
    if not proved(args.map, master, parts):
        print("refused: the split master does not load to the same data as the map")
        return 1
    print("proved: the split loads to the same data")
    if not args.apply:
        print("plan only; rerun with --apply to write")
        return 0
    folder = args.map.parent / "parts"
    taken = [n for n in [*parts, "master"] if (folder / f"{n}.yaml").exists()]
    if taken:
        print(f"refused: parts exist already: {', '.join(taken)}")
        return 1
    folder.mkdir(exist_ok=True)
    for name, ls in parts.items():
        (folder / f"{name}.yaml").write_text("\n".join(ls) + "\n", encoding="utf-8")
    (folder / "master.yaml").write_text("\n".join(master) + "\n", encoding="utf-8")
    text, _stray = assemble(folder / "master.yaml", (folder / "master.yaml").as_posix(), "just flows")
    args.map.write_text(text, encoding="utf-8")
    print(f"wrote {len(parts)} parts and master.yaml under {folder}, and assembled {args.map} from them")
    return 0


if __name__ == "__main__":
    sys.exit(main())
