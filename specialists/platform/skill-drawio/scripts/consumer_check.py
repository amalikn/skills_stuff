#!/usr/bin/env python3
"""Render every consumer's flow map to a scratch folder, timed, and compare two such folders byte for byte: the proof an engine change needs.
Never writes a consumer's own drawing.

Why (2026-10-29): each engine change is proved by rendering every project that uses the engine and comparing the drawings with a baseline
(`cmp`); done by hand it missed a consumer (skill-goal-guard) on the day five speed items went in. The consumers are listed in the skill's
consumers.yaml. `--look KEY=JSON` renders as if each map set a look key, to measure a setting before a project adopts it (render_flowmap
refuses --look with --write, so a project's drawing is never written from an override; this writes only into --out). `--engine DIR` renders
with another checkout's scripts/ folder (e.g. a git worktree of the commit before a change), so a baseline can be made after the fact.

Usage:
    consumer_check.py --out /scratch/after                          # render all consumers, print seconds each
    consumer_check.py --out /scratch/after --compare /scratch/before   # ... then cmp each drawing; exit 3 when one differs
    consumer_check.py --out /scratch/before --engine /path/to/old/skill-drawio/scripts --only unc
    consumer_check.py --out /scratch/try --look e2e_row_search=true   # what a look key would draw (scratch only)
Then measure what changed: layout_quality.py AFTER --compare BEFORE.
Exit: 0 rendered (and identical when compared); 1 a render failed or a consumer is missing; 2 bad arguments; 3 a drawing differs.
Runtime: about 13 s for all five consumers (unified-network-controller about 10 s of it).
"""

from __future__ import annotations

import argparse
import filecmp
import json
import subprocess
import sys
import time
from pathlib import Path

#: The oldest Python this script runs on (PyYAML to read the registry).
REQUIRES_PYTHON = (3, 11)
SKILL = Path(__file__).resolve().parents[1]
REGISTRY = SKILL / "consumers.yaml"


def consumers(path: Path = REGISTRY) -> list[dict]:
    """The consumers listed in the registry, each root made absolute (a relative root is the skill's own, e.g. the example).

    Args:
        path: the registry file.

    Returns:
        [{"name", "root", "map", "schema"}].

    Raises:
        ValueError: the registry has no consumers list or an entry lacks a key.
    """
    import yaml
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    out = []
    for c in data.get("consumers") or []:
        if not all(k in c for k in ("name", "root", "map", "schema")):
            raise ValueError(f"{path}: consumer {c!r} needs name, root, map and schema")
        root = Path(c["root"])
        out.append({**c, "root": str(root if root.is_absolute() else SKILL / root)})
    if not out:
        raise ValueError(f"{path}: no consumers")
    return out


def render_one(engine: Path, c: dict, out: Path, looks: dict) -> None:
    """Render one consumer's map into out with the given engine (run in a child process, so each engine is imported fresh).

    Args:
        engine: a skill-drawio scripts/ folder.
        c: the consumer.
        out: the drawing to write; refused when it is the consumer's own drawing.
        looks: look keys laid over the map's.

    Raises:
        RuntimeError: the map has problems, or out is the consumer's own drawing.
    """
    sys.path.insert(0, str(engine))
    from dataclasses import replace
    import render_flowmap
    from flowmap import model, pages
    root = Path(c["root"])
    prof = render_flowmap.profile_for(root, c["map"], c["schema"] or str(render_flowmap.SCHEMA), "")
    if (root / prof.output).resolve() == out.resolve():
        raise RuntimeError(f"{out} is {c['name']}'s own drawing; write to a scratch folder")
    prof = replace(prof, look={**prof.look, **looks})
    data, problems = model.load(root, prof)
    if problems or data is None:
        raise RuntimeError(f"{c['name']}: " + "; ".join(problems or ["map unreadable"]))
    out.write_text(pages.render(data, prof), encoding="utf-8")


def parse_looks(pairs: list[str]) -> dict:
    """Look keys from KEY=JSON pairs (plain text when the value is not JSON).

    Args:
        pairs: the --look values.

    Returns:
        {key: value}.

    Raises:
        ValueError: a pair without "=".
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


def main(argv: list[str] | None = None) -> int:
    """Command line.

    Args:
        argv: arguments (default sys.argv[1:]).

    Returns:
        The exit code, as the module header says.
    """
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", type=Path, required=True, help="the folder the drawings go to (<name>.drawio)")
    ap.add_argument("--compare", type=Path, help="a folder rendered before: cmp each drawing with it")
    ap.add_argument("--engine", type=Path, default=SKILL / "scripts", help="the skill-drawio scripts/ folder to render with (default this one)")
    ap.add_argument("--only", action="append", default=[], help="render only this consumer (repeatable)")
    ap.add_argument("--look", action="append", default=[], metavar="KEY=JSON", help="a look key as if every map set it (repeatable)")
    ap.add_argument("--registry", type=Path, default=REGISTRY, help=argparse.SUPPRESS)
    ap.add_argument("--one", help=argparse.SUPPRESS)   # child mode: render the named consumer only
    args = ap.parse_args(argv)
    try:
        looks = parse_looks(args.look)
        listed = consumers(args.registry)
    except (OSError, ValueError) as exc:
        print(f"consumer_check: {exc}", file=sys.stderr)
        return 2
    if args.one:
        render_one(args.engine.resolve(), next(c for c in listed if c["name"] == args.one), args.out / f"{args.one}.drawio", looks)
        return 0
    unknown = set(args.only) - {c["name"] for c in listed}
    if unknown:
        print(f"consumer_check: not in the registry: {', '.join(sorted(unknown))}", file=sys.stderr)
        return 2
    args.out.mkdir(parents=True, exist_ok=True)
    failed = differs = 0
    for c in listed:
        if args.only and c["name"] not in args.only:
            continue
        if not Path(c["root"]).is_dir():
            print(f"{c['name']:<16} missing: {c['root']}")
            failed += 1
            continue
        cmd = [sys.executable, __file__, "--out", str(args.out), "--engine", str(args.engine), "--registry", str(args.registry), "--one", c["name"]]
        cmd += [x for pair in args.look for x in ("--look", pair)]
        t0 = time.monotonic()
        run = subprocess.run(cmd, capture_output=True, text=True, timeout=900, check=False)
        took = time.monotonic() - t0
        if run.returncode:
            print(f"{c['name']:<16} FAILED {took:.2f}s: {(run.stderr or run.stdout).strip().splitlines()[-1:]}")
            failed += 1
            continue
        verdict = ""
        if args.compare:
            before = args.compare / f"{c['name']}.drawio"
            same = before.is_file() and filecmp.cmp(before, args.out / f"{c['name']}.drawio", shallow=False)
            differs += not same
            verdict = "identical" if same else ("DIFFERS" if before.is_file() else "no baseline")
        print(f"{c['name']:<16} {took:6.2f}s {verdict}")
    return 1 if failed else 3 if differs else 0


if __name__ == "__main__":
    sys.exit(main())
