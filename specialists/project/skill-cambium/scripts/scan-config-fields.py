#!/usr/bin/env python3
"""Report which keys in a JSON file look credential-shaped, WITHOUT ever printing their values.

Exists because ad hoc checks of "does this field have a real value" were done by printing the
value to confirm it — twice this session (2026-09-17), on two different device families — each
time exposing a real secret (SNMP community strings, a RADIUS password, a wireless encryption
key) to an agent transcript. This script makes the safe version the path of least resistance:
it reports flag/empty/non-empty per matching key, never the value itself, recursively through
nested dicts and lists.

Uses the same REDACT_KEY_PATTERN convention as cambium_xv2_adapter.py and
cambium_epmp_adapter.py — keep it in sync with those (or import from one, if this ever moves
in-repo relative to them) if a new vendor field name is found to carry a real secret.

Usage:
    scripts/scan-config-fields.py <path-to-json-file>
    scripts/scan-config-fields.py -   # read from stdin

Exit status: 0 if no flagged keys found, 1 if any were found (so it's usable as a gate, e.g.
before archiving a capture file).
"""

from __future__ import annotations

import json
import re
import sys

REDACT_KEY_PATTERN = re.compile(
    r"pass|psk|secret|key|shared|community|radius|credential|token|auth",
    re.IGNORECASE,
)


def find_flagged(obj, path: str = "") -> list[tuple[str, bool]]:
    """Walk obj, return (path, has_nonempty_value) for every credential-shaped key found."""
    found: list[tuple[str, bool]] = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            key_path = f"{path}.{k}" if path else k
            if REDACT_KEY_PATTERN.search(k):
                found.append((key_path, bool(v)))
            else:
                found.extend(find_flagged(v, key_path))
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            found.extend(find_flagged(item, f"{path}[{i}]"))
    return found


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__, file=sys.stderr)
        return 2

    src = sys.stdin if sys.argv[1] == "-" else open(sys.argv[1])
    with src:
        data = json.load(src)

    flagged = find_flagged(data)
    if not flagged:
        print("No flagged keys found.")
        return 0

    print(f"{len(flagged)} flagged key(s) found (values never shown):")
    for key_path, has_value in flagged:
        status = "NON-EMPTY — treat as a real secret" if has_value else "empty"
        print(f"  {key_path}: {status}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
