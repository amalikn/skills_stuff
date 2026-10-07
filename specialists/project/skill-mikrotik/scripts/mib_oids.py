#!/usr/bin/env python3
"""Resolve MIKROTIK-MIB object names to numeric OIDs (stdlib only).

Usage: mib_oids.py <mikrotik.mib> [name-regex]
Prints: name<TAB>oid<TAB>syntax<TAB>units<TAB>status
"""
import re
import sys

ROOTS = {"enterprises": "1.3.6.1.4.1", "iso": "1"}


def parse(path):
    """Map every object a MIB defines to (parent, index, macro, syntax, units, status).

    A stdlib regex pass, not a full SMI parser: comments are stripped, then each `::= { parent index }` assignment is paired with the last definition
    header before it. That suits MIKROTIK-MIB's flat layout; a parent imported from another MIB resolves only as far as ROOTS reaches.
    """
    txt = open(path, encoding="latin-1").read()
    txt = re.sub(r"--[^\n]*", "", txt)
    defs = {}
    head = re.compile(r"(\w[\w-]*)\s+(OBJECT-TYPE|OBJECT IDENTIFIER|MODULE-IDENTITY|OBJECT-IDENTITY|NOTIFICATION-TYPE|"
                      r"OBJECT-GROUP|MODULE-COMPLIANCE|NOTIFICATION-GROUP)(?!\s*,)")
    prev = 0
    for m in re.finditer(r"::=\s*\{\s*([\w-]+)\s+(\d+)\s*\}", txt):
        seg = txt[prev:m.start()]
        prev = m.end()
        heads = list(head.finditer(seg))
        if not heads:
            continue
        h = heads[-1]
        name, body = h.group(1), seg[h.end():]
        parent, idx = m.groups()
        syn = re.search(r"SYNTAX\s+(.+?)\n\s*(?:UNITS|MAX-ACCESS|ACCESS)", body, re.S)
        units = re.search(r'UNITS\s+"([^"]*)"', body)
        status = re.search(r"STATUS\s+(\w+)", body)
        defs[name] = (parent, idx, h.group(2), " ".join(syn.group(1).split()) if syn else "",
                      units.group(1) if units else "", status.group(1) if status else "")
    return defs


def resolve(defs, name, seen=None):
    """The numeric OID of a name, found by walking parent links up to a known root in ROOTS. Raises KeyError for a parent defined in another MIB."""
    if name in ROOTS:
        return ROOTS[name]
    parent, idx = defs[name][0], defs[name][1]
    return resolve(defs, parent) + "." + idx


def main():
    """Print name, OID, syntax, units and status for every object, or only names matching the optional regex; '?' marks a name that cannot be resolved."""
    defs = parse(sys.argv[1])
    rx = re.compile(sys.argv[2]) if len(sys.argv) > 2 else None
    for n, d in defs.items():
        if rx and not rx.search(n):
            continue
        try:
            oid = resolve(defs, n)
        except KeyError:
            oid = "?"
        print(f"{n}\t{oid}\t{d[3][:60]}\t{d[4]}\t{d[5]}")


if __name__ == "__main__":
    main()
