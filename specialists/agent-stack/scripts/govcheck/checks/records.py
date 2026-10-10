"""Durable records stay truthful: status markers resolved, archcore contract, derived files fresh, constants in sync, append-only grain."""

from __future__ import annotations

import re

from ..core import counted, fail
from ..config import (
    APPEND_ONLY_TABLES,
    ASAT_MARKER,
    CONSTANT_SURFACES,
    DERIVED,
    ROOT,
    SCAN_SUFFIXES,
    SELF_FILES,
)
from ..helpers import (
    read,
    table_rows,
    without_code,
)

def check_status_markers_resolved() -> None:
    """No governed surface leaves a pending status marker standing after the thing it describes has landed.

    Rule: MEMORY.md and SCRATCHPAD.md are read as current truth, so "in flight", "pending", "TBD" or "awaiting" in a RESULTS table is not a note, it is a false
    statement about the project's state. Found 2026-09-01: MEMORY.md's baselines table still read `v3 | in flight` after v3 had completed and been classified a
    negative result, which is the single most misleading thing a truth document can do.

    Deliberately narrow: only table rows are checked. Prose legitimately says "the run in flight when X happened" as history, and a marker inside a `count:asat`
    line is a dated record.
    """
    PENDING = ("in flight", "in-flight", "pending", "tbd", "awaiting", "not yet run")
    for surface in ("MEMORY.md", "SCRATCHPAD.md"):
        text = read(surface)
        if text is None:
            continue
        for n, line in enumerate(without_code(text).splitlines(), 1):
            if not line.startswith("|") or ASAT_MARKER in line:
                continue
            low = line.lower()
            for marker in PENDING:
                if marker in low:
                    counted()
                    fail("status", f"{surface}:{n} table row still reports {marker!r}; resolve it or mark the line count:asat")
                    break
            else:
                counted()


def check_archcore_document_contract() -> None:
    """Every .archcore/ document declares a valid status and carries its provenance.

    Rule: `.archcore/README.md` — durable truth is the highest authority in this project, so a document there must say which of the three states it is in and
    where it came from. A document with no `Source:` cannot be traced back to what it was promoted from, and a status outside the set is a state nobody has
    defined the meaning of. Both are cheap to check and expensive to discover late.

    `superseded` is deliberately in the allowed set: an accepted document is superseded IN PLACE with a dated banner, never deleted, because the superseded
    reasoning is usually the part a later reader needs.
    """
    VALID = {"proposed", "accepted", "superseded"}
    base = ROOT / ".archcore"
    if not base.is_dir():
        return
    for doc in sorted(base.rglob("*.md")):
        if doc.name == "README.md":
            continue
        rel = doc.relative_to(ROOT).as_posix()
        head = doc.read_text().split("\n# ", 1)[0]
        counted()
        status = next((ln.split(":", 1)[1].strip() for ln in head.splitlines() if ln.startswith("Status:")), None)
        if status not in VALID:
            fail("archcore", f"{rel} declares status {status!r}; must be one of {sorted(VALID)}")
        counted()
        if not any(ln.startswith("Source:") for ln in head.splitlines()):
            fail("archcore", f"{rel} has no Source: line; a promoted document must name what it was promoted from")


def check_derived_freshness() -> None:
    """Generated artifacts are not older than the sources they are generated from.

    Freshness only — it proves a rebuild happened, not that the rebuild used the right source. Where the generator can stamp its source into the output, add a
    provenance check alongside this one; see patterns/governance-checks.md.
    """
    for output, inputs in DERIVED.items():
        out = ROOT / output
        if not out.is_file():
            fail("derived", f"{output} is registered as generated but does not exist")
            counted()
            continue
        for src in inputs:
            source = ROOT / src
            counted()
            if not source.is_file():
                fail("derived", f"{output} declares input `{src}` which does not exist")
            elif out.stat().st_mtime < source.stat().st_mtime:
                fail("derived", f"{output} is older than its input `{src}` — regenerate it")


def check_constant_sync() -> None:
    """Facts restated across surfaces stay identical, and no unregistered file restates them.

    Duplication here is deliberate: the operator must read the value at the point of decision without following a pointer. So the duplication stays and the sync
    is enforced. Orphan detection is the half that makes it self-extending.
    """
    for name, entry in CONSTANT_SURFACES.items():
        pattern = re.compile(str(entry["pattern"]))
        registered = {str(s) for s in entry["surfaces"]}  # type: ignore[union-attr]
        owner = str(entry.get("owner", ""))

        for surface in sorted(registered):
            text = read(surface)
            counted()
            if text is None:
                fail("constant", f"{name}: registered surface {surface} does not exist")
            elif not pattern.search(without_code(text)):
                fail("constant", f"{name}: {surface} is registered but no longer states it (owner: {owner or 'unset'})")

        for path in sorted(ROOT.rglob("*")):
            if not path.is_file() or path.suffix not in SCAN_SUFFIXES:
                continue
            rel = path.relative_to(ROOT).as_posix()
            if rel in registered or rel.startswith(".") or "/." in rel or rel in SELF_FILES:
                continue
            counted()
            if pattern.search(without_code(path.read_text(encoding="utf-8", errors="ignore"))):
                fail("constant", f"{name}: {rel} states it but is not registered in CONSTANT_SURFACES")


def check_append_only_grain() -> None:
    """Every row of an append-only table stamps its pass, and no pass records the same entity twice.

    Registered in APPEND_ONLY_TABLES. Two distinct failures, both silent: a row with an EMPTY pass column cannot be ordered against any other row, so nothing
    can say which measurement is current; and a REPEATED (entity, pass) pair means one pass measured one entity twice, so every count and every aggregate over
    the table is wrong by however many rows were duplicated. Neither shows up as an error — the table still parses and the report still renders.

    A re-measurement is a NEW pass. Reusing the previous pass identifier to record one is the defect this catches.
    """
    for rel, (entity_col, pass_col) in APPEND_ONLY_TABLES.items():
        rows = table_rows(rel)
        if not rows:
            counted()
            if not (ROOT / rel).is_file():
                fail("append-only-grain", f"{rel} is registered as append-only but does not exist")
            continue
        seen: dict[tuple[str, str], int] = {}
        for i, row in enumerate(rows, start=2):  # line 1 is the header
            counted()
            if entity_col not in row or pass_col not in row:
                fail("append-only-grain",
                     f"{rel} has no {entity_col!r}/{pass_col!r} column; the registered grain does not match the table")
                break
            pass_id = (row.get(pass_col) or "").strip()
            if not pass_id:
                fail("append-only-grain", f"{rel} line {i} has empty {pass_col}; the pass is the grain")
                continue
            key = ((row.get(entity_col) or "").strip(), pass_id)
            if key in seen:
                fail("append-only-grain",
                     f"{rel} line {i} repeats {entity_col} {key[0]!r} for pass {pass_id} (first seen line {seen[key]}); "
                     f"a re-measurement is a NEW pass, so give it a new {pass_col}")
            else:
                seen[key] = i
