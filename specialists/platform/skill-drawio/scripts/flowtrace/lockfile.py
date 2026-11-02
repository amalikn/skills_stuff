"""The review lock of a flow map: which code each step was last reviewed against, and which steps are suspect now. Stdlib only.

This is the suspect link of requirements traceability (flag raised by a content hash, cleared only by a person who looked; jamb, Jama) applied to
a flow step and the code it cites, with snippetdrift's split of `check` from `accept` and its keeping of the accepted text so a suspect shows a
real diff. The lock (`<map stem>.lock.json` beside the map) holds, per step: when it was reviewed, a hash of its own words, and a fingerprint per
reference. `<map stem>.lock.d/` holds the accepted source of each fingerprint, named by it.

Imported, not run: `from flowtrace import lockfile` with the skill's scripts/ on sys.path.
"""

from __future__ import annotations

import difflib
import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from .fingerprint import fingerprint

#: The step's words that count as its description.
WORDS = ("label", "action", "gate", "failures", "writes", "reads", "branches")
#: Most diff lines one suspect reference shows.
DIFF_LINES = 60


@dataclass
class Finding:
    """One step whose review no longer holds.

    Args:
        step: `<flow>/<step>`.
        action: the step's words, for the reviewer.
        state: "suspect" (cited code changed), "new" (never reviewed) or "broken" (a cited file or symbol is gone).
        refs: [(reference, what happened)].
        diff: unified diff lines against the accepted source, when kept.
        edited: the step's own words changed since its review.
    """

    step: str
    action: str
    state: str
    refs: list[tuple[str, str]] = field(default_factory=list)
    diff: list[str] = field(default_factory=list)
    edited: bool = False


def step_key(flow: dict, step: dict) -> str:
    """A step's key in the lock.

    Args:
        flow: the flow.
        step: the step.

    Returns:
        `<flow>/<step>`.
    """
    return f"{flow['id']}/{step['id']}"


def words_hash(step: dict) -> str:
    """A hash of what the step says.

    Args:
        step: the step.

    Returns:
        16 hex digits.
    """
    return hashlib.sha256(json.dumps({k: step.get(k) for k in WORDS}, sort_keys=True).encode()).hexdigest()[:16]


def lock_paths(root: Path, map_path: str) -> tuple[Path, Path]:
    """Where a map's lock and accepted sources live.

    Args:
        root: the project root.
        map_path: the map, relative to the root.

    Returns:
        (lock file, snapshot folder).
    """
    m = root / map_path
    return m.with_name(f"{m.stem}.lock.json"), m.with_name(f"{m.stem}.lock.d")


def read_lock(path: Path) -> dict:
    """Read a lock.

    Args:
        path: the lock file.

    Returns:
        Its content, or an empty lock when there is none.

    Raises:
        ValueError: the file is not valid JSON.
    """
    if not path.is_file():
        return {"version": 1, "steps": {}}
    return json.loads(path.read_text(encoding="utf-8"))


def _diff(snapshots: Path, old: str, new_text: str) -> list[str]:
    """Diff the accepted source against the current one.

    Args:
        snapshots: the snapshot folder.
        old: the accepted fingerprint.
        new_text: the current source.

    Returns:
        Diff lines without headers, at most DIFF_LINES; empty when the accepted source was not kept.
    """
    kept = snapshots / f"{old}.txt"
    if not kept.is_file():
        return []
    lines = difflib.unified_diff(kept.read_text(encoding="utf-8").splitlines(), new_text.splitlines(), lineterm="", n=1)
    return [ln for ln in lines if not ln.startswith(("---", "+++"))][:DIFF_LINES]


def step_finding(root: Path, flow: dict, step: dict, entry: dict | None, cache: dict, snapshots: Path) -> Finding | None:
    """Judge one step against its lock entry.

    Args:
        root: the project root.
        flow: the flow.
        step: the step.
        entry: its lock entry, or None.
        cache: the file text cache.
        snapshots: the snapshot folder.

    Returns:
        The finding, or None when the review holds.
    """
    key, refs = step_key(flow, step), step.get("code", [])
    if entry is None:
        return Finding(key, step["action"], "new") if refs else None
    finding = Finding(key, step["action"], "suspect", edited=entry.get("words") != words_hash(step))
    for ref in refs:
        now, text = fingerprint(root, ref, cache)
        was = entry["refs"].get(ref)
        if now is None:
            finding.state = "broken"
            finding.refs.append((ref, "file or symbol gone"))
        elif was is None:
            finding.refs.append((ref, "newly cited"))
        elif was != now:
            finding.refs.append((ref, "changed"))
            finding.diff += [f"{ref}:"] + _diff(snapshots, was, text)
    finding.refs += [(ref, "no longer cited") for ref in entry["refs"] if ref not in refs]
    return finding if finding.refs else None


def findings(root: Path, map_path: str, data: dict) -> list[Finding]:
    """Every step whose review no longer holds.

    Args:
        root: the project root.
        map_path: the map, relative to the root.
        data: the loaded map.

    Returns:
        The findings, in map order.

    Raises:
        ValueError: the lock is not valid JSON.
    """
    lock_path, snapshots = lock_paths(root, map_path)
    steps, cache = read_lock(lock_path)["steps"], {}
    out = [step_finding(root, f, s, steps.get(step_key(f, s)), cache, snapshots) for f in data["flows"] for s in f["steps"]]
    return [x for x in out if x]


def selected(data: dict, targets: list[str]) -> list[tuple[dict, dict]]:
    """The steps an accept covers.

    Args:
        data: the loaded map.
        targets: `all`, `<flow>`, `<flow>/<step>`, or a cited file path.

    Returns:
        [(flow, step)]; a step is listed once.
    """
    out = []
    for f in data["flows"]:
        for s in f["steps"]:
            cited = {r.partition(":")[0] for r in s.get("code", [])}
            if "all" in targets or f["id"] in targets or step_key(f, s) in targets or cited & set(targets):
                out.append((f, s))
    return out


def accept(root: Path, map_path: str, data: dict, targets: list[str], who: str) -> list[str]:
    """Record a review: the chosen steps take the code as it is now. Steps no longer in the map leave the lock, as do sources nothing cites.

    Args:
        root: the project root.
        map_path: the map, relative to the root.
        data: the loaded map.
        targets: as selected().
        who: the reviewer, recorded with the time.

    Returns:
        The step keys accepted.

    Raises:
        ValueError: a chosen step cites a file or symbol that is gone (fix the map first).
    """
    lock_path, snapshots = lock_paths(root, map_path)
    lock = read_lock(lock_path)
    cache: dict = {}
    when = datetime.now().astimezone().isoformat(timespec="seconds")
    done = []
    for f, s in selected(data, targets):
        prints = {}
        for ref in s.get("code", []):
            now, text = fingerprint(root, ref, cache)
            if now is None:
                raise ValueError(f"{step_key(f, s)}: `{ref}` is gone; fix the map before accepting")
            prints[ref] = now
            snapshots.mkdir(parents=True, exist_ok=True)
            (snapshots / f"{now}.txt").write_text(text, encoding="utf-8")
        lock["steps"][step_key(f, s)] = {"reviewed": when, "by": who, "words": words_hash(s), "refs": prints}
        done.append(step_key(f, s))
    live = {step_key(f, s) for f in data["flows"] for s in f["steps"]}
    lock["steps"] = {k: v for k, v in sorted(lock["steps"].items()) if k in live}
    lock_path.write_text(json.dumps(lock, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    used = {h for e in lock["steps"].values() for h in e["refs"].values()}
    for kept in snapshots.glob("*.txt") if snapshots.is_dir() else []:
        if kept.stem not in used:
            kept.unlink()
    return done
