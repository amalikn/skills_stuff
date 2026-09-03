#!/usr/bin/env python3
"""Verify that this checkout still matches the recorded evaluation freeze.

A freeze record is a claim about five files. Nothing else in the project verifies it, and the failure it guards against is silent: a baseline and a holdout can
be compared as though they measured the same thing while one of them was scored by a different scorer, against a different catalogue, or with a different
closure module. The stored rows carry the evidence — this script is what turns them into a precondition you can run BEFORE spending a single-use holdout.

Deliberately NOT part of `just preflight`. Preflight answers "is this repository internally valid"; this answers "does this repository match one particular
evaluation snapshot". Those are different questions and a legitimate catalogue change must be able to pass the first while failing the second. Wiring this into
preflight would convert a historical reference into a permanent prohibition on changing the catalogue — which the project's own rule against enforcing history
forbids.

Two properties worth stating because they are what make the check trustworthy:

  * The live hashes come from `evaluate_routing.run_provenance`, the SAME function that stamps them into every result row. A second implementation here could
    drift from the stamping one and would then verify a freeze nobody's rows were ever measured against.
  * The expected hashes are parsed from MEMORY.md, which owns measured figures per `.archcore/README.md`. Copying them into a second data file would create two
    records of one fact, and the check would pass while the human-readable one was stale.

Exit 0 on match, 1 on drift, 2 when the record itself cannot be read. Never writes anything.
"""
from __future__ import annotations

import argparse
import hashlib
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MEMORY = ROOT / "MEMORY.md"
SECTION = "### Frozen measurement contract"

sys.path.insert(0, str(Path(__file__).resolve().parent))
from evaluate_routing import run_provenance  # noqa: E402  — the stamping implementation is the only correct source of live hashes

# Reported without the `_sha` suffix; the record and the provenance rows both use the full key.
STAMPS = ("routing_catalogue_sha", "eval_corpus_sha", "orchestrator_sha", "harness_sha", "closure_sha")

# Artifacts the freeze covers that no RUN stamps by default. The unseen holdout is the case: a run that measures it stamps its hash as `eval_corpus_sha`, so a
# checkout where nobody has run it yet carries the hash nowhere at all. Hashed here directly, by the same 16-character rule, so the corpus cannot be edited
# between authoring and execution without the freeze noticing — which for a single-use corpus is the whole game.
LOCAL_ARTIFACTS = {"holdout_corpus_sha": ROOT / "evals" / "holdout-cases.toml"}
ALL_KEYS = STAMPS + tuple(LOCAL_ARTIFACTS)


def _local_sha(path: Path) -> str | None:
    """Same 16-character truncation the harness uses, so a recorded hash means one thing everywhere."""
    if not path.is_file():
        return None
    return hashlib.sha256(path.read_bytes()).hexdigest()[:16]


def recorded() -> dict[str, str]:
    """Frozen hashes as MEMORY.md states them.

    Anchored on `^\\|\\s*` rather than on hand-authored cell spacing, because `table-reflow` pads every cell to align the column and this project mandates
    running it. A pattern written against the unpadded form goes red the first time the required formatter touches the file it is required to touch.
    """
    if not MEMORY.is_file():
        raise SystemExit(f"freeze record not found: {MEMORY}")
    text = MEMORY.read_text(encoding="utf-8")
    start = text.find(SECTION)
    if start == -1:
        raise SystemExit(f"freeze record not found: no '{SECTION}' section in MEMORY.md")
    # The section ends at the next heading of the same or higher level, so a later section's table can never be read as part of the record.
    rest = text[start + len(SECTION):]
    end = re.search(r"^#{1,3} ", rest, re.M)
    block = rest[: end.start()] if end else rest

    found: dict[str, str] = {}
    for row in re.finditer(r"^\|\s*`([a-z_]+)`\s*\|\s*`([0-9a-f]{16})`\s*\|", block, re.M):
        found[row.group(1)] = row.group(2)
    missing = [s for s in ALL_KEYS if s not in found]
    if missing:
        raise SystemExit(f"freeze record incomplete: MEMORY.md states no hash for {', '.join(missing)}")
    return found


def main() -> int:
    ap = argparse.ArgumentParser(description="Verify this checkout against the recorded evaluation freeze.")
    ap.add_argument("--quiet", action="store_true", help="print only the verdict line and any drift")
    args = ap.parse_args()

    expected = recorded()
    live = run_provenance(argparse.Namespace(provider=None, model=None, runner=None, command=None))
    # run_provenance never sees these, by construction; hash them here.
    for key, path in LOCAL_ARTIFACTS.items():
        live[key] = _local_sha(path)

    drifted: list[tuple[str, str, str]] = []
    width = max(len(s.removesuffix("_sha")) for s in ALL_KEYS)
    for stamp in ALL_KEYS:
        want, got = expected[stamp], live.get(stamp)
        label = stamp.removesuffix("_sha")
        if got is None:
            # A stamp the harness no longer produces is drift of the worst kind: the record names something the rows will not carry.
            drifted.append((label, want, "absent — the harness no longer stamps this"))
        elif got != want:
            drifted.append((label, want, got))
        elif not args.quiet:
            print(f"{label:{width}}  {want}  OK")

    if not drifted:
        if not args.quiet:
            print()
        print("FREEZE CHECK: PASS")
        return 0

    print()
    for label, want, got in drifted:
        print(f"{label}\nexpected: {want}\nactual:   {got}\n")
    print("FREEZE CHECK: FAIL")
    print("This repository no longer matches the recorded evaluation freeze.")
    print("Runs made now are not comparable to that snapshot. Either restore the artifact, or record a NEW freeze and re-measure — never compare across it.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
