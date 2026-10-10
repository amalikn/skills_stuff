"""Evidence files: provenance stated, JSONL contract held, no duplicate YAML keys."""

from __future__ import annotations

import json
import re

from ..core import counted, fail
from ..config import (
    EVIDENCE_DIR,
    EVIDENCE_INDEX,
    EVIDENCE_PROVENANCE_CORRECTED,
    EVIDENCE_PROVENANCE_FIELDS,
    JSONL_EVIDENCE,
    ROOT,
    YAML_SURFACES,
)
from ..helpers import (
    members,
    read,
)

def check_evidence_provenance() -> None:
    """Every markdown capture states where it came from, when, and whether the fetch succeeded.

    Enforces the global source-discipline policy (~/.agents/AGENTS.md, 'Citations travel into the documentation'): a VERIFIED figure means a capture exists that
    someone else can re-open. Presence of a capture FILE is not that — a file with no URL and no HTTP status proves only that somebody wrote something down.

    A capture missing the header is accepted ONLY while it names its correcting capture in EVIDENCE_PROVENANCE_CORRECTED and that capture is on disk.
    """
    if EVIDENCE_DIR is None:
        return
    for item in members(EVIDENCE_DIR, "*.md"):
        if item.name == EVIDENCE_INDEX:
            continue
        counted()
        text = read(f"{EVIDENCE_DIR}/{item.name}") or ""
        missing = [f for f in EVIDENCE_PROVENANCE_FIELDS if f"**{f}**" not in text]
        if not missing:
            continue
        corrector = EVIDENCE_PROVENANCE_CORRECTED.get(item.name)
        if corrector is None:
            fail("evidence-provenance",
                 f"{EVIDENCE_DIR}/{item.name} states no {', '.join(missing)}; a capture nobody can re-open is not evidence")
        elif not (ROOT / EVIDENCE_DIR / corrector).is_file():
            fail("evidence-provenance",
                 f"{EVIDENCE_DIR}/{item.name} defers its provenance to {corrector}, which does not exist")


def check_jsonl_evidence_contract() -> None:
    """Every line of a tracked JSONL evidence file parses and carries the keys its readers require.

    Registered in JSONL_EVIDENCE. These files cross a process boundary: one script appends, another aggregates days later. Both failures here are silent by
    construction — a reader skipping an unparseable line and a reader finding a key absent behave identically to a reader finding nothing to report.

    The `inadequate` rule is the load-bearing one. propose_evolution.py groups those gaps on the skill id BEFORE the colon, which is what makes the aggregation
    exact rather than a guess at what two sentences share. A declaration with no colon groups under its entire sentence, so it can never match another one, and
    a real repeated complaint about a skill silently never reaches the threshold that would surface it.
    """
    for rel, required in JSONL_EVIDENCE.items():
        path = ROOT / rel
        counted()
        if not path.is_file():
            fail("jsonl-evidence", f"{rel} is registered as JSONL evidence but does not exist")
            continue
        for i, line in enumerate(path.read_text().splitlines(), start=1):
            if not line.strip():
                continue
            counted()
            try:
                row = json.loads(line)
            except json.JSONDecodeError as e:
                fail("jsonl-evidence", f"{rel} line {i} does not parse: {e}")
                continue
            missing = [k for k in required if k not in row]
            if missing:
                fail("jsonl-evidence", f"{rel} line {i} is missing {', '.join(missing)}; a reader cannot tell it apart from no evidence at all")
            if rel.endswith("capability-gaps.jsonl"):
                if row.get("kind") not in ("missing", "inadequate"):
                    fail("jsonl-evidence", f"{rel} line {i} has kind {row.get('kind')!r}; expected 'missing' or 'inadequate'")
                if row.get("kind") == "inadequate" and ":" not in (row.get("text") or ""):
                    fail("jsonl-evidence",
                         f"{rel} line {i} declares a skill inadequate without naming it as '<skill-id>: <why>'; "
                         f"the proposer groups on the id before the colon, so this can never aggregate with another report of the same skill")


def check_no_duplicate_yaml_keys() -> None:
    """No YAML mapping in this project defines the same key twice.

    A duplicate key is the quietest defect a structured file can carry: every parser accepts it, the last value wins, and the discarded block leaves no trace.
    Found on 20260903 in context-map.yaml, where the entry describing the file itself read `type: machine_routing_map` immediately followed by
    `type: sync_translation_rules` — two lines orphaned when upstream sync was retired. The file parsed cleanly and every consumer saw context-map.yaml
    described as a sync artifact that no longer exists, while the correct description was silently thrown away.

    Well-formedness proves nothing here, which is why this asserts on the KEY STREAM rather than on whether the load succeeds. Stdlib-only, so it hand-parses
    rather than importing PyYAML: this gate must never fail for an environment reason.
    """
    for rel in sorted(YAML_SURFACES):
        path = ROOT / rel
        counted()
        if not path.is_file():
            fail("yaml-keys", f"{rel} is registered as a YAML surface but does not exist")
            continue
        # Track keys per (indent, block). A new list item (`- `) or a dedent starts a fresh mapping.
        stack: dict[int, dict[str, int]] = {}
        for n, raw in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), start=1):
            if not raw.strip() or raw.lstrip().startswith("#"):
                continue
            indent = len(raw) - len(raw.lstrip())
            body = raw.lstrip()
            fresh = body.startswith("- ")
            if fresh:
                body = body[2:]
                indent += 2
            for deeper in [k for k in stack if k > indent]:
                del stack[deeper]
            if fresh:
                stack[indent] = {}
            m = re.match(r"([A-Za-z_][\w.-]*)\s*:(?:\s|$)", body)
            if not m:
                continue
            key = m.group(1)
            block = stack.setdefault(indent, {})
            counted()
            if key in block:
                fail("yaml-keys", f"{rel} line {n} repeats key {key!r} (first at line {block[key]}); "
                                 f"YAML keeps the LAST value and discards the first without any error")
            else:
                block[key] = n
