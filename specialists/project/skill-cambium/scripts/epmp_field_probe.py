#!/usr/bin/env python3
"""Read-only probe of one ePMP unit's configuration and status fields through its site's SMC: which fields exist, set or empty, values withheld.

Written for the 2026-10-09 checks (unified-network-controller D10): which Force 300 fields can hold a typed-in position (systemDeviceLocLatitude,
Longitude, Height, sysLocation, snmpSystemDescription; no azimuth), and what a low-touch install leaves in snmpSystemDescription (the installer's
JSON record: lotno, lat, lon, confirmed, align, test, variables). One REST login per unit (the credential chain keeps ePMP to three logins, its
fourth inside about twenty minutes is locked out), logged out at once; nothing is written.

Values are never printed for coordinates and secrets; a field is reported `set` or `empty`, other short values are shown. `--installer` decodes
the installer's record and prints its keys with coordinates withheld.

Uses unified-network-controller's collector helpers (tunnels through the SMC, the vault chain) like gps_probe.py uses its smc_snmp.

Usage:
    epmp_field_probe.py --node old-looma-smc01 --proxy teleport.apn.au --ip 10.255.4.33 [--family epmp-sm] [--pattern 'Loc|azim|height'] [--installer]
"""

from __future__ import annotations

import argparse
import json
import re
import sys

UNC = "/Volumes/Data/_ai/_project/project_stuff/apn/unified-network-controller/wc-local/scripts"
sys.path.insert(0, UNC)
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from cambium_epmp_adapter import CambiumEPMPAdapter

from collector import batch_push_devices as b

HIDE = re.compile(r"lat|lon|coord|pass|secret|key|psk|community|token", re.I)
DEFAULT_PATTERN = r"Loc|location|azim|height|elev|tilt|heading|bearing|altitude|antenna|Gain|sysLocation|snmpSystemDescription|DeviceName"


def walk(obj, path: str = ""):
    """Every leaf of a nested config as (dotted path, value).

    Args:
        obj: a dict or list from the device.
        path: the path so far.

    Yields:
        (path, value) for each leaf; lists contribute their first two items.
    """
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield from walk(v, f"{path}.{k}" if path else k)
    elif isinstance(obj, list):
        for i, v in enumerate(obj[:2]):
            yield from walk(v, f"{path}[{i}]")
    else:
        yield path, obj


def state(key: str, value) -> str:
    """How a field is reported.

    Args:
        key: the field's name.
        value: its value.

    Returns:
        `empty`, `set` (value withheld) or `set: <short value>`.
    """
    v = str(value).strip()
    if v in ("", "0", "0.0", "None", "0.000000"):
        return "empty"
    if HIDE.search(key) or len(v) > 80:
        return "set"
    return f"set: {v[:60]!r}"


def main(argv: list[str] | None = None) -> int:
    """Log in once, read config and status, report the matching fields.

    Args:
        argv: arguments (default sys.argv[1:]).

    Returns:
        0 when the unit was read, 1 when it could not be.
    """
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--node", required=True, help="the site's SMC node, e.g. old-looma-smc01")
    ap.add_argument("--proxy", required=True, help="its Teleport proxy (from the site's flavour), e.g. teleport.apn.au")
    ap.add_argument("--ip", required=True)
    ap.add_argument("--family", default="epmp-sm", choices=["epmp-sm", "epmp-ap"])
    ap.add_argument("--pattern", default=DEFAULT_PATTERN, help="regular expression on field names")
    ap.add_argument("--installer", action="store_true", help="decode the installer's record in snmpSystemDescription")
    args = ap.parse_args(argv)
    specs, ports = b.open_tunnels([{"name": "unit", "ip": args.ip, "rport": 443}], 0, args.node, args.proxy)
    try:
        def attempt(key):
            a = CambiumEPMPAdapter(f"127.0.0.1:{ports['unit']}", "admin", b.kp_password(key))
            a.login()
            try:
                return a.get_config(), a.get_raw_param("status")
            finally:
                a.logout()
        cfg, status = b.with_vault_chain(f"cambium-devices/{args.family}", attempt)
    except Exception as exc:  # the reason is reported; nothing else to clean up beyond the tunnel
        print(f"not read: {type(exc).__name__}: {str(exc)[:160]}")
        return 1
    finally:
        b.close_tunnels(specs)
    pat = re.compile(args.pattern, re.I)
    record = None
    for name, obj in (("config", cfg), ("status", status)):
        for path, value in walk(obj):
            leaf = path.split(".")[-1]
            if leaf == "snmpSystemDescription":
                record = value
            if pat.search(leaf):
                print(f"{name:6} {leaf:45} {state(leaf, value)}")
    if args.installer:
        try:
            doc = json.loads(str(record or ""))
        except ValueError:
            print("installer record: none (snmpSystemDescription is not JSON)")
            return 0
        print("installer record:")
        for path, value in walk(doc):
            print(f"  {path:40} {'<withheld>' if HIDE.search(path) else str(value)[:50]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
