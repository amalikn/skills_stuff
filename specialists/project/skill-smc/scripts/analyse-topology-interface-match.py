#!/usr/bin/env python3
# ORIGIN: written 2026-07-30 for the APN routing-issue investigation
# (local-knowledge-ansible/ansible-wifi/issues/apn/routing-issue/). Promoted into skill-smc for
# reuse on future WAN-routing/topology-drift investigations at any site, any flavor.
"""analyse-topology-interface-match.py — cross-check topology_vars against a site's real hardware.

Catches the class of bug found live at New Looma (2026-07-30): topology_vars/<site>.yml can define
physical interface names, VLAN parent links, or VLAN IDs that do not match what the box actually
has — a `role: internet` WAN interface named for a *different SMC hardware model's* NIC naming
scheme, a VLAN's parent (`switch01`/`switch02`) pointing at the wrong physical NIC, or a VLAN that
exists on the box but is entirely undefined in topology_vars (and vice versa). None of
`yamllint`/`ansible-lint`/`ansible-playbook --syntax-check` catch any of this — they only confirm
the YAML is well-formed, not that the values are correct for the specific box. See
`skill-smc/references/08_ansible-authoring.md`'s "Mandatory pre-check" note for the incident this
script was written to prevent recurring silently.

Reads a capture directory produced by `collect-smc-evidence.sh` (needs `netplan`, `dhclient-units`
and, if present, `dmidecode-model` — the last is optional and only used for the cross-model naming
hint) plus the site's committed `topology_vars/<site>.yml`. Touches nothing else — no SSH, no
writes, no git changes. Two-directional check:

  * topology -> box: every physical interface name and VLAN/parent pairing topology_vars declares
    is checked against what netplan actually defines for that box.
  * box -> topology: every VLAN netplan defines with a `macaddress:` line (i.e. rendered as
    `role: internet`/`nbn-modem` at template time — the deterministic-render signal documented in
    `../references/03_communication-flows.md`) is checked for a matching topology_vars entry.

Usage
    ./analyse-topology-interface-match.py <site>                       # newest capture
    ./analyse-topology-interface-match.py <site> evidence/20260730_1524
    ./analyse-topology-interface-match.py <site> --flavor rct
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
ANSIBLE_REPO = Path("/Volumes/Data/_ansible/ansible-wifi")

# Known SMC hardware models in this fleet and the physical NIC naming scheme each uses. Extend
# this as new models are confirmed live — see the dmidecode check in the pre-check note in
# skill-smc/references/08_ansible-authoring.md. This is a hint for the operator, not gospel: a
# model not listed here just skips the naming-scheme sanity check rather than failing.
KNOWN_MODELS = {
    "BOXER-6404": {"eno1", "enp1s0", "enp2s0", "enp3s0", "enp4s0"},
    "BOXER-6641": {"eno1", "enp1s0", "enp2s0", "enp3s0", "enp4s0"},
}


def read(path: Path) -> str:
    return path.read_text() if path.is_file() else ""


def newest_capture() -> Path:
    root = REPO_ROOT / "evidence"
    if not root.is_dir():
        sys.exit(f"no evidence directory at {root} — run 'just collect' first")
    stamps = sorted((p for p in root.iterdir() if p.is_dir()), reverse=True)
    if not stamps:
        sys.exit(f"no captures under {root} — run 'just collect' first")
    return stamps[0]


def parse_topology(site: str, flavor: str) -> dict:
    """Parse the committed topology_vars/<site>.yml from the working tree (not a specific commit —
    this tool is for pre-deploy/pre-edit sanity checking of what's about to ship, not historical
    drift analysis; use analyse-routing-drift.py for that)."""
    path = ANSIBLE_REPO / "inventories" / flavor / "topology_vars" / f"{site}.yml"
    if not path.is_file():
        sys.exit(f"no topology_vars file at {path}")
    lines = path.read_text().splitlines()

    entries: dict[str, dict] = {}
    current = None
    for line in lines:
        if m := re.match(r"^        (\w+):\s*$", line):
            current = m.group(1)
            entries[current] = {}
            continue
        if current is None:
            continue
        if m := re.match(r"^          name:\s*(\S+)", line):
            entries[current]["name"] = m.group(1)
        elif m := re.match(r"^          role:\s*(\S+)", line):
            entries[current]["role"] = m.group(1)
        elif m := re.match(r"^          type:\s*(\S+)", line):
            entries[current]["type"] = m.group(1)
        elif m := re.match(r"^          vlanid:\s*(\d+)", line):
            entries[current]["vlanid"] = int(m.group(1))
        elif m := re.match(r"^          interface:\s*(\S+)", line):
            entries[current]["parent_key"] = m.group(1)
        elif re.match(r"^      \w", line) or re.match(r"^\S", line):
            # dedent back out of the interfaces: block entirely
            if not re.match(r"^        \w", line):
                current = None

    # Resolve each VLAN/physical entry's parent to a real device name via switch01/switch02 (or
    # any other bare `name:`-only entry acting as a trunk parent).
    for key, e in entries.items():
        pk = e.get("parent_key")
        if pk and pk in entries and "name" in entries[pk]:
            e["parent_device"] = entries[pk]["name"]
    return entries


def parse_netplan(hostdir: Path) -> dict:
    blob = read(hostdir / "netplan.txt")
    ethernets = set(re.findall(r"^\s{4}(\w[\w\d]*):\s*$", blob, re.MULTILINE))
    # vlan<id>: / link: <parent> / optional macaddress: <mac>, in whatever order the renderer wrote.
    # The SAME vlan id can legitimately appear MORE THAN ONCE — e.g. the management/public/
    # provisioning VLANs are tagged on both switch01 and switch02 and bridged together — so this
    # is a list of every device per id, not a single entry.
    vlans: dict[int, list[dict]] = {}
    for m in re.finditer(
        r"^\s{4}(\S+):\s*\n((?:\s{6}.*\n)*)", blob, re.MULTILINE
    ):
        name, body = m.group(1), m.group(2)
        idm = re.search(r"id:\s*(\d+)", body)
        linkm = re.search(r"link:\s*(\S+)", body)
        if not idm or not linkm:
            continue
        vlans.setdefault(int(idm.group(1)), []).append({
            "name": name,
            "link": linkm.group(1),
            "has_mac": bool(re.search(r"macaddress:", body)),
        })
    return {"ethernets": ethernets, "vlans": vlans}


def parse_active_dhclient(hostdir: Path) -> set[str]:
    blob = read(hostdir / "dhclient-units.txt")
    return set(re.findall(r"dhclient@(\S+?)\.service\s+loaded\s+active\s+running", blob))


def parse_model(hostdir: Path) -> str | None:
    blob = read(hostdir / "dmidecode-model.txt").strip()
    return blob or None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("site", help="site name, e.g. new-looma (matches topology_vars/<site>.yml and evidence/<capture>/<site>-smc01/)")
    ap.add_argument("capture", nargs="?", help="evidence capture dir; defaults to newest")
    ap.add_argument("--flavor", default="rcp", help="inventory flavor (default: rcp)")
    args = ap.parse_args()

    capture = Path(args.capture) if args.capture else newest_capture()
    hostdir = capture / f"{args.site}-smc01"
    if not hostdir.is_dir():
        sys.exit(f"no {hostdir} in this capture — run 'just collect-sites \"{args.site}\"' first")

    topo = parse_topology(args.site, args.flavor)
    live = parse_netplan(hostdir)
    active = parse_active_dhclient(hostdir)
    model = parse_model(hostdir)

    print(f"site:    {args.site}")
    print(f"capture: {capture}")
    if model:
        known = KNOWN_MODELS.get(model)
        print(f"model:   {model}" + ("" if known else "  (not in KNOWN_MODELS — add it once confirmed)"))
    print()

    problems = []

    # Direction 1: topology -> box, for plain physical interfaces (internetNN/switchNN with a
    # bare `name:`, no vlanid — the WAN NICs and the LAN-trunk NICs). Bridges/loopback also have
    # a bare `name:` with no vlanid but are virtual, not real NICs — skip those explicitly.
    for key, e in sorted(topo.items()):
        if "vlanid" in e or "name" not in e or e.get("type") in {"bridge", "loopback"}:
            continue
        name = e["name"]
        if name not in live["ethernets"]:
            problems.append(
                f"PHYSICAL NAME NOT ON BOX: {key} names '{name}', which does not exist in this "
                f"box's netplan ethernets at all ({sorted(live['ethernets'])})"
            )
        elif model and (known := KNOWN_MODELS.get(model)) and name not in known:
            problems.append(
                f"NAME NOT TYPICAL FOR MODEL: {key} names '{name}', not a NIC name previously "
                f"confirmed on a {model} — double-check before trusting this"
            )

    # Direction 1b: topology -> box, for VLAN entries — parent device + vlan id must both match.
    # A vlan id can legitimately have more than one live device (management/public/provisioning
    # are tagged on both switch01 and switch02 with the same id and bridged) — a topology entry
    # matches if ANY live device sharing that id has the expected parent link.
    topo_vlan_ids: set[int] = set()
    for key, e in sorted(topo.items()):
        if "vlanid" not in e:
            continue
        vid = e["vlanid"]
        topo_vlan_ids.add(vid)
        parent = e.get("parent_device")
        live_devices = live["vlans"].get(vid, [])
        if not live_devices:
            problems.append(
                f"VLAN MISSING FROM BOX: {key} (vlanid {vid}, role {e.get('role', '?')}) has no "
                f"matching vlan{vid} entry in this box's live netplan at all"
            )
        elif parent and not any(d["link"] == parent for d in live_devices):
            links = ", ".join(sorted({d["link"] for d in live_devices}))
            problems.append(
                f"WRONG PARENT: {key} (vlanid {vid}) says its parent is '{parent}' "
                f"({e.get('parent_key')}), but live netplan has vlan{vid} only on: {links}"
            )

    # Direction 2: box -> topology. Any VLAN device with a macaddress: line was role:internet/
    # nbn-modem at render time (the template only emits macaddress: for those roles) — if
    # topology_vars doesn't mention that vlan id anywhere, it's a real interface with nothing
    # tracking it.
    for vid, devices in sorted(live["vlans"].items()):
        if vid in topo_vlan_ids:
            continue
        for v in devices:
            if v["has_mac"]:
                active_note = " (currently ACTIVE/leased)" if v["name"] in active else ""
                problems.append(
                    f"VLAN MISSING FROM TOPOLOGY: live vlan{vid} on '{v['link']}' has a "
                    f"macaddress line (role:internet at render time) but no topology_vars entry "
                    f"defines it{active_note}"
                )

    if not problems:
        print("MATCH — every topology_vars interface/VLAN resolves correctly against this box's "
              "live netplan, and every real (macaddress-bearing) VLAN on the box is represented "
              "in topology_vars. Safe to proceed on the physical-interface axis (this does not "
              "replace the routing-drift check in analyse-routing-drift.py).")
        return 0

    print(f"{len(problems)} problem(s) found:\n")
    for p in problems:
        print(f"  - {p}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
