#!/usr/bin/env python3
"""Apply a central convention baseline (conventions/apn-baseline.toml) to one Pad workspace: rewrite the template's conventions, create the rest.

Operator, 2026-11-10: "capture the conventions centrally so that other projects can copy the same". Run from a project folder whose .pad.toml names
the workspace (or pass --workspace). For each baseline entry the script finds the workspace convention by its baseline title or by the template
title it `replaces`; an existing one whose title, body, trigger, scope, priority, status or commands differ is updated in place (guarded by its
seq, with a comment), a missing one is created (idempotency key skill-pad-<id>-<workspace>). Conventions outside the baseline are left alone.

Usage:
    python3 pad_conventions.py --project smc-resiliency                    # plan: same / update / create per convention
    python3 pad_conventions.py --project smc-resiliency --apply            # write
    python3 pad_conventions.py --project smc-resiliency --only writing-standard --apply   # one entry; the rest stay as the workspace has them
Options: --workspace SLUG (default: the project name), --trackers "ROADMAP, ..." (fills {trackers}), --only ID[,ID] (default: all), --baseline FILE,
--pad PATH, --timeout SECONDS.
Exit: 0 done or plan clean, 1 a pad call failed, 2 bad arguments. Budget: a few seconds (one list plus one call per change); prints its time.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
import tomllib
from pathlib import Path

BASELINE = Path(__file__).resolve().parents[1] / "conventions" / "apn-baseline.toml"
FIELDS = ("trigger", "scope", "priority", "category")


def load_baseline(path: Path, project: str, trackers: str) -> list[dict]:
    """The baseline conventions with {project} and {trackers} filled in.

    Args:
        path: the baseline TOML file.
        project: the project folder name.
        trackers: the project's tracker list, for {trackers}.

    Returns:
        One dict per convention (id, title, content, fields, replaces, commands).
    """
    def fill(text: str) -> str:
        return text.replace("{project}", project).replace("{trackers}", trackers)

    return [{**c, "title": fill(c["title"]), "content": fill(c["content"])} for c in tomllib.loads(path.read_text(encoding="utf-8"))["convention"]]


def pad(args: list[str], timeout: int, binary: str = "pad") -> str:
    """Run one pad command and return its stdout.

    Args:
        args: the arguments after `pad`.
        timeout: seconds before the call is abandoned.
        binary: the pad binary.

    Returns:
        stdout.

    Raises:
        RuntimeError: pad failed or timed out.
    """
    try:
        p = subprocess.run([binary, *args], capture_output=True, text=True, timeout=timeout)
    except (subprocess.TimeoutExpired, FileNotFoundError) as exc:
        raise RuntimeError(f"pad {' '.join(args[:3])}: {exc}") from exc
    if p.returncode != 0:
        raise RuntimeError(f"pad {' '.join(args[:3])} exited {p.returncode}: {p.stderr.strip()[-300:]}")
    return p.stdout


def plan(baseline: list[dict], existing: list[dict]) -> list[tuple[str, dict, dict | None, list[str]]]:
    """Decide per baseline entry: same, update (with the differing fields) or create.

    Args:
        baseline: from load_baseline().
        existing: the workspace's conventions (`pad item list conventions --all --format json --full`).

    Returns:
        (action, baseline entry, existing item or None, differing field names) per entry.
    """
    by_title = {i["title"]: i for i in existing}
    out = []
    for b in baseline:
        item = by_title.get(b["title"]) or by_title.get(b.get("replaces", ""))
        if item is None:
            out.append(("create", b, None, []))
            continue
        f = item.get("fields") or {}
        f = json.loads(f) if isinstance(f, str) else f
        diff = [k for k in FIELDS if b.get(k) and f.get(k) != b[k]]
        diff += ["title"] if item["title"] != b["title"] else []
        diff += ["content"] if (item.get("content") or "").strip() != b["content"].strip() else []
        diff += ["status"] if f.get("status") != "active" else []
        diff += ["commands"] if b.get("commands") and f.get("commands") != b["commands"] else []
        out.append(("update" if diff else "same", b, item, diff))
    return out


def apply(actions: list, workspace: str, timeout: int, binary: str) -> None:
    """Write the planned updates and creates.

    Args:
        actions: from plan().
        workspace: the workspace slug.
        timeout: seconds per pad call.
        binary: the pad binary.

    Returns:
        None.

    Raises:
        RuntimeError: a pad call failed.
    """
    for action, b, item, diff in actions:
        fields = {k: b[k] for k in FIELDS if b.get(k)} | {"status": "active"} | ({"commands": b["commands"]} if b.get("commands") else {})
        if action == "update":
            pad(["item", "update", item["ref"], "--workspace", workspace, "--expected-seq", str(item["seq"]), "--title", b["title"],
                 "--content", b["content"], "--fields-json", json.dumps(fields),
                 "--comment", f"skill-pad baseline {b['id']}: {', '.join(diff)} brought in line (conventions/apn-baseline.toml)"], timeout, binary)
        elif action == "create":
            pad(["item", "create", "convention", b["title"], "--workspace", workspace, "--content", b["content"], "--fields-json", json.dumps(fields),
                 "--op-key", f"skill-pad-{b['id']}-{workspace}"], timeout, binary)


def select_entries(baseline: list[dict], only: str | None) -> list[dict]:
    """Keep only the named baseline entries, so one new convention can be added without rewriting a workspace's own wording of the others.

    Why (operator, 2026-11-10): a plain apply also overwrote conventions a project had worded more richly; `--only writing-standard` creates just
    the new one.

    Args:
        baseline: from load_baseline().
        only: comma-separated entry ids, or None for every entry.

    Returns:
        The selected entries, in baseline order.

    Raises:
        ValueError: an id that the baseline does not hold (nothing is planned or written).
    """
    if not only:
        return baseline
    wanted = [x.strip() for x in only.split(",") if x.strip()]
    unknown = sorted(set(wanted) - {b["id"] for b in baseline})
    if unknown:
        raise ValueError(f"unknown baseline id(s): {', '.join(unknown)}")
    return [b for b in baseline if b["id"] in wanted]


def main(argv: list[str] | None = None) -> int:
    """Plan, and with --apply write, the baseline conventions in one workspace.

    Args:
        argv: command-line arguments (None reads sys.argv).

    Returns:
        The exit code: 0 done or plan clean, 1 a pad call failed.
    """
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--project", required=True, help="the project folder name; fills {project}")
    ap.add_argument("--workspace", help="the Pad workspace slug (default: the project name)")
    ap.add_argument("--trackers", default="ROADMAP, SCRATCHPAD open items and its docs/trackers", help="fills {trackers}")
    ap.add_argument("--baseline", type=Path, default=BASELINE)
    ap.add_argument("--apply", action="store_true", help="write; without it only the plan is printed")
    ap.add_argument("--pad", default="pad")
    ap.add_argument("--timeout", type=int, default=60)
    ap.add_argument("--only", help="comma-separated baseline ids to plan or apply (default: all); the others are left as the workspace has them")
    a = ap.parse_args(argv)
    started, ws = time.monotonic(), a.workspace or a.project
    try:
        selected = select_entries(load_baseline(a.baseline, a.project, a.trackers), a.only)
    except ValueError as exc:
        print(f"pad_conventions: {exc}", file=sys.stderr)
        return 2
    try:
        existing = json.loads(pad(["item", "list", "conventions", "--all", "--workspace", ws, "--format", "json", "--full"], a.timeout, a.pad))
        actions = plan(selected, existing)
        for action, b, item, diff in actions:
            print(f"{action:6} {b['id']:15} {item['ref'] if item else '-':9} {', '.join(diff)}")
        if a.apply:
            apply(actions, ws, a.timeout, a.pad)
    except RuntimeError as exc:
        print(f"pad_conventions: {exc}", file=sys.stderr)
        return 1
    n = sum(x[0] != "same" for x in actions)
    print(f"{'applied' if a.apply else 'PLAN:'} {n} change(s) in workspace {ws}; {time.monotonic() - started:.1f} s" + ("" if a.apply else "; --apply to write"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
