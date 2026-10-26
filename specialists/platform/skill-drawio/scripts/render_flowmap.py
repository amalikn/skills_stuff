#!/usr/bin/env python3
"""Validate a project's flow map (YAML) and render it as one multi-page draw.io file, or report drift: the generic front end of the flowmap package.

A project with no wrapper of its own points this at its map; the optional `drawing:` block in the map sets kind colours, End-to-end tiers,
families and the output path (flowmap.profile.Profile.from_drawing). The default schema is the skill's schemas/flowmap.schema.json.

Usage (from the project root):
    render_flowmap.py --map docs/flows/flows.yaml                # validate and report drift; exit 1 on a problem or a stale drawing
    render_flowmap.py --map docs/flows/flows.yaml --write        # validate and write the drawing (files only)
    render_flowmap.py --map docs/flows/flows.yaml --list         # one line per flow (read only)
    render_flowmap.py --map docs/flows/flows.yaml --audit        # layout audit of the routed pages (read only)
    render_flowmap.py --map docs/flows/flows.yaml --audit --look e2e_loops=true   # audit as if the map set a look key (read only)
Exit: 0 valid and current (or written); 1 on a problem, drift or an audit fault; 2 on bad arguments.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import replace
from pathlib import Path

from drawio.audit import faults, page_audit
from flowmap import e2e, e2e_family, model, options, overview, pages
from flowmap.profile import Profile, look_report

#: The oldest Python this script runs on (stdlib; PyYAML to read the map).
REQUIRES_PYTHON = (3, 11)
SCHEMA = Path(__file__).resolve().parents[1] / "schemas" / "flowmap.schema.json"


def profile_for(root: Path, map_path: str, schema: str, output: str) -> Profile:
    """The profile for a map, from its `drawing:` block.

    Args:
        root: the project root.
        map_path: the map, relative to the root.
        schema: the schema file.
        output: the drawing path ("" for the map's own or the default).

    Returns:
        The profile.

    Raises:
        OSError: the map cannot be read.
        ValueError: it is not valid YAML.
    """
    data = model.read_map(root, map_path) or {}
    return Profile.from_drawing(data, map_path, schema, "skill-drawio scripts/render_flowmap.py", output)


def audit(root: Path, profile: Profile) -> list[str]:
    """Every layout fault on the routed pages.

    Args:
        root: the project root.
        profile: the profile.

    Returns:
        "<page>: <fault>: <id>" lines; empty when clean (problems in the map are returned as lines too).
    """
    data, problems = model.load(root, profile)
    if problems or data is None:
        return [f"map: {p}" for p in problems]
    return ([f"Overview: {f}" for f in faults(page_audit(overview.overview_page(data, profile)))]
            + [f"End-to-end: {f}" for f in faults(page_audit(e2e.end_to_end_page(data, profile)))]
            + [f"{p.name}: {f}" for p in e2e_family.family_pages(data, profile) for f in faults(page_audit(p))]
            + [f"{name}: {f}" for pid, name, block in model.option_blocks(data)
               for f in faults(page_audit(options.options_page(data, profile, block, pid, name)))]
            + [f"Flow {i + 1} ({fl['id']}): {f}" for i, fl in enumerate(data["flows"])   # flow pages too (2026-10-21: overlaps went unseen)
               for f in faults(page_audit(pages.flow_page(fl, {c["id"]: c for c in data["components"]}, i + 1, profile)))])


def look_overrides(pairs: list[str]) -> dict:
    """Look keys given on the command line.

    Args:
        pairs: "key=value" strings; the value is JSON (true, 12, "sub"), or plain text when it is not JSON.

    Returns:
        {key: value}.

    Raises:
        ValueError: a pair has no "=" or an empty key.
    """
    out = {}
    for pair in pairs:
        key, sep, raw = pair.partition("=")
        if not sep or not key.strip():
            raise ValueError(f"--look wants KEY=VALUE, got {pair!r}")
        try:
            out[key.strip()] = json.loads(raw)
        except json.JSONDecodeError:
            out[key.strip()] = raw
    return out


def with_looks(profile: Profile, pairs: list[str], auditing: bool) -> Profile | None:
    """The profile with `--look` keys laid over the map's, to try a setting without editing the map (2026-10-26).

    Args:
        profile: the map's profile.
        pairs: the `--look` values.
        auditing: whether --audit was given; overrides are refused otherwise, so nothing is written from them.

    Returns:
        The profile (unchanged without pairs), or None after printing why the overrides were refused.
    """
    if not pairs:
        return profile
    if not auditing:
        print("render_flowmap: --look needs --audit", file=sys.stderr)
        return None
    try:
        return replace(profile, look={**profile.look, **look_overrides(pairs)})
    except ValueError as exc:
        print(f"render_flowmap: {exc}", file=sys.stderr)
        return None


def main(argv: list[str] | None = None) -> int:
    """Command line.

    Args:
        argv: arguments (default sys.argv[1:]).

    Returns:
        0, 1 or 2 as the module header says.
    """
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--root", type=Path, default=Path("."), help="the project root (default: the current folder)")
    ap.add_argument("--map", required=True, help="the map, relative to the root")
    ap.add_argument("--schema", default=str(SCHEMA), help="the JSON Schema (default: the skill's generic one)")
    ap.add_argument("--output", default="", help="the drawing (default: drawing.output, else <map folder>/drawio/<map stem>.drawio)")
    mode = ap.add_mutually_exclusive_group()
    mode.add_argument("--write", action="store_true", help="write the drawing")
    mode.add_argument("--list", action="store_true", help="one line per flow (read only)")
    mode.add_argument("--audit", action="store_true", help="layout audit of the Overview, End-to-end, decision and flow pages (read only)")
    ap.add_argument("--look", action="append", default=[], metavar="KEY=JSON",
                    help="with --audit: a drawing.look key as if the map set it, to try a setting first (repeatable; value as JSON)")
    args = ap.parse_args(argv)
    root = args.root.resolve()
    try:
        profile = profile_for(root, args.map, args.schema, args.output)
    except (OSError, ValueError) as exc:
        print(f"render_flowmap: {exc}", file=sys.stderr)
        return 2
    profile = with_looks(profile, args.look, args.audit)
    if profile is None:
        return 2
    if args.list:
        data, problems = model.load(root, profile)
        print("\n".join(pages.flow_list(data) + [f"problem: {p}" for p in problems]))
        return 1 if problems else 0
    if args.audit:
        found = audit(root, profile)
        print("\n".join(found) or "audit: clean (no layout fault on the Overview, End-to-end, decision or flow pages)")
        return 1 if found else 0
    outcome = pages.evaluate(root, profile)
    for p in outcome.problems:
        print(f"problem: {p}")
    if outcome.problems:
        return 1
    if args.write:
        try:
            print(f"wrote {pages.write_drawing(root, profile, outcome).relative_to(root)}")
            print("\n".join(look_report(model.read_map(root, profile.map) or {})))
        except FileExistsError as exc:
            print(f"render_flowmap: {exc}", file=sys.stderr)
            return 1
        return 0
    if outcome.drift:
        print(f"drift: {profile.output} differs from what {profile.map} renders; rerun with --write")
        return 1
    print(f"ok: {profile.map} is valid and {profile.output} is current")
    return 0


if __name__ == "__main__":
    sys.exit(main())
