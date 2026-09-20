#!/usr/bin/env python3
"""Derive an SNMP table schema from a live `snmpwalk -On` capture.

The existing `schemas/` tree contracts the REST and getter layers. SNMP is a third layer with its own shape —
numeric OIDs, columns rather than names, and values that are all strings on the wire — and nothing contracted
it until now. This tool builds that contract the same way `fleet_schema_sweep.py` builds the others: derived
from live observation, never authored.

Input is the raw output of `snmpwalk -On`, one `OID = TYPE: value` line per row. Output matches the existing
schema convention exactly, so a reader does not have to learn a second one.

Two SNMP-specific facts the output records, because both have already cost a wrong reading:

* **A table entry OID ends in `.1`, the Entry node**, and a row reads `<entry>.<column>.<index>`. Using the
  table OID instead shifts column and index by one, and every row then parses as a separate object carrying
  only its first field. This produced 420 "subscriber links" for an access point with 10 on 2026-09-21.
* **A scalar is instance `.0` of its object.** `cambiumAPNumberOfConnectedSTA` answers at `....10.0`, not at
  `....10`, so an exact-match lookup on the bare OID silently returns nothing.

Usage:

    python3 scripts/snmp_schema_from_walk.py \\
        --walk <raw.txt> --entry .1.3.6.1.4.1.17713.21.1.2.30.1 \\
        --family epmp-ap --name snmp-connected-sta \\
        --columns <json map of column-number to name> \\
        --model ePMP-3000L --firmware 4.7.0.1 --site hope-vale
"""

from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

LINE = re.compile(r"^(?P<oid>\.[\d.]+)\s*=\s*(?P<type>[A-Za-z0-9-]+):?\s*(?P<value>.*)$")

#: SNMP type token -> JSON Schema type. Everything the agent returns is a string on the wire; this records
#: what the agent DECLARED, which is the more useful contract for an adapter author.
SNMP_TYPES = {
    "INTEGER": "integer", "Gauge32": "integer", "Counter32": "integer", "Counter64": "integer",
    "Unsigned32": "integer", "Timeticks": "integer", "STRING": "string", "Hex-STRING": "string",
    "OID": "string", "IpAddress": "string",
}

#: Column names that carry an end-user identifier. Values are counted, never recorded.
IDENTIFYING = {"mac", "connectedSTAMAC", "ip", "connectedSTAIP", "hostname", "name",
               "connectedSTAClickTHostName", "connectedSTAClickTHWAddr"}


def parse_walk(path: Path) -> dict[str, tuple[str, str]]:
    """`{oid: (snmp_type, value)}` from an `snmpwalk -On` capture, skipping absent-object responses."""
    out: dict[str, tuple[str, str]] = {}
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        match = LINE.match(line.strip())
        if not match:
            continue
        value = match.group("value").strip().strip('"')
        if "No Such" in line or "No more variables" in line:
            continue
        out[match.group("oid")] = (match.group("type"), value)
    return out


def build(walk: dict[str, tuple[str, str]], entry: str, columns: dict[int, str]) -> dict:
    prefix = entry.rstrip(".") + "."
    rows: dict[str, dict[int, tuple[str, str]]] = defaultdict(dict)
    for oid, (snmp_type, value) in walk.items():
        if not oid.startswith(prefix):
            continue
        remainder = oid[len(prefix):].split(".")
        if len(remainder) < 2 or not remainder[0].isdigit():
            continue
        rows[".".join(remainder[1:])][int(remainder[0])] = (snmp_type, value)

    properties: dict[str, dict] = {}
    seen: dict[int, list[tuple[str, str]]] = defaultdict(list)
    for row in rows.values():
        for column, pair in row.items():
            seen[column].append(pair)

    for column in sorted(seen):
        name = columns.get(column, f"column_{column}")
        pairs = seen[column]
        declared = SNMP_TYPES.get(pairs[0][0], "string")
        prop: dict = {"type": declared, "x-oid-column": column, "x-snmp-type": pairs[0][0],
                      "x-observed-count": len(pairs)}
        if name in IDENTIFYING:
            prop["x-identifying"] = True
            prop["x-note"] = "End-user identifying — values are never recorded in this contract."
        else:
            distinct = sorted({v for _, v in pairs})
            if len(distinct) <= 8:
                prop["x-candidate-values"] = distinct
        if column not in columns:
            prop["x-undocumented-in-mib"] = True
        properties[name] = prop

    return {"properties": properties, "row_count": len(rows)}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--walk", required=True, type=Path)
    ap.add_argument("--entry", required=True, help="table ENTRY oid, ending in the Entry node (usually .1)")
    ap.add_argument("--family", required=True)
    ap.add_argument("--name", required=True, help="schema basename, e.g. snmp-connected-sta")
    ap.add_argument("--columns", type=Path, help="JSON file mapping column number to MIB name")
    ap.add_argument("--model", default=None)
    ap.add_argument("--firmware", default=None)
    ap.add_argument("--site", default=None)
    ap.add_argument("--out-root", type=Path, default=Path(__file__).resolve().parent.parent / "schemas")
    args = ap.parse_args()

    columns: dict[int, str] = {}
    if args.columns:
        columns = {int(k): v for k, v in json.loads(args.columns.read_text(encoding="utf-8")).items()}

    built = build(parse_walk(args.walk), args.entry, columns)
    if not built["properties"]:
        print(f"no rows under {args.entry} — nothing written")
        return 1

    names = sorted(built["properties"])
    schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": f"cambium/{args.family}/{args.name}.schema.json",
        "title": f"Cambium {args.family} — {args.name}",
        "description": (
            "Derived from a live SNMP walk, not from a MIB mirror. The live agent may expose more columns than "
            "the mirror documents; those carry `x-undocumented-in-mib`. `x-oid-column` is the column number "
            "under the table ENTRY oid — note the entry ends in `.1` and a row reads "
            "`<entry>.<column>.<index>`. No end-user identifying values are recorded."
        ),
        "x-cambium": {
            "family": args.family,
            "endpoint": args.name,
            "layer": "snmp",
            "entry_oid": args.entry,
            "observations": built["row_count"],
            "models": [args.model] if args.model else [],
            "firmware": [args.firmware] if args.firmware else [],
            "sites": [args.site] if args.site else [],
            "generated_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        },
        "type": "array",
        "items": {
            "type": "object",
            "properties": {name: built["properties"][name] for name in names},
            "required": names,
            "x-records-observed": built["row_count"],
        },
        "x-observed-count": built["row_count"],
    }

    out_dir = args.out_root / args.family
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{args.name}.schema.json"
    out_path.write_text(json.dumps(schema, indent=1) + "\n", encoding="utf-8")
    print(f"wrote {out_path} — {len(names)} columns, {built['row_count']} rows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
