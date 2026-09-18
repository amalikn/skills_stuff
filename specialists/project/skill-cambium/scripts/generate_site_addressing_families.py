#!/usr/bin/env python3
"""Derive two parts of references/site-addressing.yaml straight from cambium-swap's inventory data
— the same computations this pack's evidence E124/E125/E126/E129 did by hand:

1. The `families:` block for one or more sites, from their reconciled cnMaestro-export inventory
   CSVs (per-site octet_pattern/host_count by device family).
2. `--oui-audit`: the `oui_reference:` block's coverage, from the consolidated
   inventory/device-inventory.csv — which real MAC OUI prefixes appear there but have no entry in
   site-addressing.yaml yet (the gap E129 found by hand after the file went unmaintained through
   22 sites' worth of new exports).

Both print YAML/text to stdout for review/merge; NEITHER writes the target file directly, since
site-addressing.yaml also carries hand-authored live-session notes (SSH/REST/SNMP verification
narrative, cross-site OUI-reuse cautions) neither computation can derive or preserve.

octet_pattern/host_count/trust in the families: output, and host_count/site in the OUI audit
output, always mean method: cnmaestro-export (the CSV itself is the evidence) — a site or OUI that
has also been live-verified (SSH/REST/SNMP session) should keep or add that richer verification by
hand; this script only ever proposes the export-derived facts.

Usage:
  generate_site_addressing_families.py --flavour nbn_accelerate --site amata
  generate_site_addressing_families.py --flavour rcp --all
  generate_site_addressing_families.py --all --all-flavours   # every site in the inventory root
  generate_site_addressing_families.py --oui-audit             # OUI blocks missing from oui_reference
"""
import argparse
import csv
import glob
import os
import re
from collections import Counter, defaultdict

DEFAULT_INVENTORY_ROOT = "/Volumes/Data/_ai/_project/project_stuff/apn/cambium-swap/inventory/asset-register"
DEFAULT_DEVICE_INVENTORY = "/Volumes/Data/_ai/_project/project_stuff/apn/cambium-swap/inventory/device-inventory.csv"
DEFAULT_SITE_ADDRESSING_YAML = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                             "references", "site-addressing.yaml")

FAMILY_MAP = {
    "XV2-2": "enterprise-wifi-xv2", "XV2-2T0": "enterprise-wifi-xv2", "XV2-22H": "enterprise-wifi-xv2",
    "ePMP Force 300-16 SM": "epmp-sm", "ePMP Force 300-25 SM": "epmp-sm",
    "ePMP Force 300-16 AP": "epmp-ap", "ePMP Force 300-25 AP": "epmp-ap", "ePMP 3000L AP": "epmp-ap",
    "60 GHz cnWave V5000 DN": "cnwave-60ghz", "60 GHz cnWave V3000 CN": "cnwave-60ghz",
    "60 GHz cnWave V3000 DN": "cnwave-60ghz", "60 GHz cnWave V2000 CN": "cnwave-60ghz",
    "60 GHz cnWave V2000 DN": "cnwave-60ghz", "60 GHz cnWave V1000 CN": "cnwave-60ghz",
    "60 GHz cnWave V1000 DN": "cnwave-60ghz", "60 GHz cnWave CN": "cnwave-60ghz", "60 GHz cnWave DN": "cnwave-60ghz",
    "cnPilot e500": "enterprise-wifi-eseries", "cnPilot e430H": "enterprise-wifi-eseries",
    "cnPilot e430W": "enterprise-wifi-eseries",
    "cnPilot r195P": "cnpilot-r195p",
}

# RCP exports use "IPv4 Address"; nbn_accelerate exports use "IP Address" — same data, different header.
IP_FIELD_CANDIDATES = ["IP Address", "IPv4 Address"]


def find_site_files(inventory_root, flavour, site):
    pattern = os.path.join(inventory_root, flavour, f"{site}_cnmaestro-inventory.csv" if site else "*_cnmaestro-inventory.csv")
    return sorted(glob.glob(pattern))


def ip_field(fieldnames):
    for cand in IP_FIELD_CANDIDATES:
        if cand in fieldnames:
            return cand
    raise ValueError(f"no known IP column in {fieldnames}")


def compute_families(csv_path):
    family_octets = defaultdict(Counter)
    with open(csv_path, newline="") as f:
        reader = csv.DictReader(f)
        ipf = ip_field(reader.fieldnames)
        for r in reader:
            fam = FAMILY_MAP.get(r["Device Type"])
            ip = r.get(ipf, "")
            if fam and ip and ip not in ("N/A", "-", ""):
                octet = ".".join(ip.split(".")[:3]) + ".x"
                family_octets[fam][octet] += 1
    return family_octets


def render_site(site, family_octets, indent="    "):
    lines = [f"{indent}families:"]
    for fam, octets in sorted(family_octets.items()):
        total = sum(octets.values())
        dominant, dcount = octets.most_common(1)[0]
        lines.append(f"{indent}  {fam}:")
        lines.append(f'{indent}    octet_pattern: "{dominant}"')
        lines.append(f"{indent}    trust: verified")
        lines.append(f"{indent}    verified:")
        lines.append(f'{indent}      date: "2026-09-18"')
        lines.append(f"{indent}      method: cnmaestro-export")
        lines.append(f"{indent}      host_count: {dcount}")
        others = [f"{o} ({c} hosts)" for o, c in octets.most_common() if o != dominant]
        if others:
            note = f"dominant pattern shown ({dcount}/{total} hosts); also present: {', '.join(others)}"
            lines.append(f'{indent}    notes: "{note}"')
    return "\n".join(lines)


def known_ouis(site_addressing_yaml_path):
    """Lowercase colon-form OUI keys already in oui_reference — stdlib-only parse (no PyYAML
    dependency for this script), since the key form is fixed and simple ('  "xx:yy:zz":' lines)."""
    ouis = set()
    with open(site_addressing_yaml_path) as f:
        text = f.read()
    in_oui_block = False
    for line in text.splitlines():
        if line.startswith("oui_reference:"):
            in_oui_block = True
            continue
        if in_oui_block:
            if line and not line.startswith(" "):
                break
            m = re.match(r'^\s{2}"([0-9a-fA-F:]{8})":\s*$', line)
            if m:
                ouis.add(m.group(1).lower())
    return ouis


def audit_oui(device_inventory_path, site_addressing_yaml_path):
    known = known_ouis(site_addressing_yaml_path)
    oui_data = defaultdict(lambda: {"total": 0, "families": Counter(), "sites": Counter()})
    with open(device_inventory_path, newline="") as f:
        for r in csv.DictReader(f):
            mac = re.sub(r"[^0-9A-Fa-f]", "", r.get("mac_address", ""))
            if len(mac) != 12:
                continue
            oui = ":".join([mac[0:2], mac[2:4], mac[4:6]]).lower()
            d = oui_data[oui]
            d["total"] += 1
            d["families"][r.get("product_family", "UNKNOWN")] += 1
            d["sites"][r.get("site", "UNKNOWN")] += 1

    missing = {oui: d for oui, d in oui_data.items() if oui not in known}
    if not missing:
        print(f"# no OUI blocks in {device_inventory_path} are missing from {site_addressing_yaml_path}'s oui_reference")
        return
    print(f"# OUI blocks present in {device_inventory_path} but missing from oui_reference:")
    for oui, d in sorted(missing.items(), key=lambda kv: -kv[1]["total"]):
        top_site, site_n = d["sites"].most_common(1)[0]
        print(f'  "{oui}":')
        print(f"    # host_count={d['total']}  families={dict(d['families'].most_common())}")
        print(f"    family: UNKNOWN  # pick the dominant one from the families breakdown above — never guess")
        print(f"    verified:")
        print(f'      date: "REPLACE-WITH-TODAY"')
        print(f"      method: cnmaestro-export")
        print(f"      site: {top_site}  # most common of {dict(d['sites'].most_common())}")
        print(f"      host_count: {site_n}")
        print(f'    notes: "REPLACE — state whether this OUI is family-exclusive or shared, per the file\'s existing entries\' style"')
        print()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--inventory-root", default=DEFAULT_INVENTORY_ROOT,
                     help=f"directory holding <flavour>/*_cnmaestro-inventory.csv (default: {DEFAULT_INVENTORY_ROOT})")
    ap.add_argument("--flavour", choices=["rcp", "nbn_accelerate"], help="restrict to one flavour subdirectory")
    ap.add_argument("--all-flavours", action="store_true", help="scan every flavour subdirectory under --inventory-root")
    ap.add_argument("--site", help="a single site slug (matches <site>_cnmaestro-inventory.csv)")
    ap.add_argument("--all", action="store_true", help="every site found for the selected flavour(s)")
    ap.add_argument("--oui-audit", action="store_true",
                     help="report OUI blocks in device-inventory.csv missing from oui_reference, instead of computing families:")
    ap.add_argument("--device-inventory", default=DEFAULT_DEVICE_INVENTORY,
                     help=f"path to the consolidated device-inventory.csv, for --oui-audit (default: {DEFAULT_DEVICE_INVENTORY})")
    ap.add_argument("--site-addressing-yaml", default=DEFAULT_SITE_ADDRESSING_YAML,
                     help=f"path to site-addressing.yaml, for --oui-audit (default: {DEFAULT_SITE_ADDRESSING_YAML})")
    args = ap.parse_args()

    if args.oui_audit:
        audit_oui(args.device_inventory, args.site_addressing_yaml)
        return

    if not args.site and not args.all:
        ap.error("give --site <slug> or --all, or --oui-audit")
    if args.all_flavours:
        flavours = ["rcp", "nbn_accelerate"]
    elif args.flavour:
        flavours = [args.flavour]
    else:
        ap.error("give --flavour <rcp|nbn_accelerate> or --all-flavours")

    for flavour in flavours:
        paths = find_site_files(args.inventory_root, flavour, args.site)
        if not paths:
            print(f"# no *_cnmaestro-inventory.csv found under {flavour}/ matching site={args.site!r}")
            continue
        print(f"  {flavour}:")
        for path in paths:
            site = os.path.basename(path).replace("_cnmaestro-inventory.csv", "")
            family_octets = compute_families(path)
            if not family_octets:
                print(f"    {site}: {{}}  # no recognised device types with a usable IP in {path}")
                continue
            print(f"    {site}:")
            print(render_site(site, family_octets, indent="      "))


if __name__ == "__main__":
    main()
