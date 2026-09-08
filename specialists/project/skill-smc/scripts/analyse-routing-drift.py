#!/usr/bin/env python3
"""analyse-routing-drift.py — correlate live SMC routing state against committed topology.

ORIGIN: written 2026-07-29 for the APN routing-issue investigation
(local-knowledge-ansible/ansible-wifi/issues/apn/routing-issue/). Promoted into skill-smc as a
reusable diagnostic for the "hook covers netplan" discriminator on future WAN-routing/topology-
drift investigations. The DEPLOYED_COMMIT/CANDIDATE_COMMITS below are that investigation's
specific reference points (2026-07-29, rcp flavor) — override with --commit for a different
site/flavor/timeframe rather than trusting the defaults.

Reads a capture directory produced by ``collect-smc-evidence.sh`` and, for each host, works out:

  * ``ecmp``       — interfaces that are nexthops of the multipath default route
  * ``recognised`` — interfaces the generated dhclient hook knows about, evidenced by a source
                     ``ip rule`` and a per-interface routing table
  * ``leased``     — interfaces holding a ``100.64.0.0/10`` address (a Starlink CGNAT lease)
  * ``stray``      — interface carrying ``default via ... metric 100`` in the main table, i.e.
                     the one the hook's ``*)`` fall-through branch treated as backup-class
  * ``orphaned``   — leased but not recognised: present in netplan, absent from the hook's list

It then compares ``recognised`` against the primary-uplink count defined for that site in the
deployed commit. A match is evidence that ``smc_network`` (netplan) and ``smc_application``
(the dhclient hook) were rendered from different topology states.

Read-only. Touches nothing but the local evidence directory and the local git repo.

Usage
    ./analyse-routing-drift.py                          # newest capture
    ./analyse-routing-drift.py evidence/20260729_1352   # specific capture
    ./analyse-routing-drift.py --commit fb419e6c        # compare against a different commit
    ./analyse-routing-drift.py --markdown               # emit a markdown table for the analysis
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
ANSIBLE_REPO = Path("/Volumes/Data/_ansible/ansible-wifi")
DEPLOYED_COMMIT = "fb419e6c1109682d1518f98402d0145fdcef079e"  # 2026-07-29 rcp reference point — override with --commit
TOPOLOGY_DIR = "inventories/rcp/topology_vars"  # override with --flavor for wh/rct/rcp/etc.

# Candidate topology states a box's rendered artifacts might have come from. The hook is compared
# against each so we can say which state smc_application was last rendered from, per site.
CANDIDATE_COMMITS = {
    "fb419e6c (deployed)": "fb419e6c1109682d1518f98402d0145fdcef079e",
    "af2edf56 (rise-multi)": "af2edf56",
}

# switch01 primaries are the 52x series; switch02 mirrors them in the 53x series.
SWITCH01_RANGE = range(521, 531)


def newest_capture() -> Path:
    root = REPO_ROOT / "evidence"
    if not root.is_dir():
        sys.exit(f"no evidence directory at {root} — run 'just collect' first")
    stamps = sorted((p for p in root.iterdir() if p.is_dir()), reverse=True)
    if not stamps:
        sys.exit(f"no captures under {root} — run 'just collect' first")
    return stamps[0]


def read(path: Path) -> str:
    return path.read_text() if path.is_file() else ""


def parse_hook(hostdir: Path) -> list[str]:
    """Extract the interface list from the deployed dhclient hook's matched branch.

    This is the decisive artifact: membership of this list is what decides whether an interface
    gets a per-interface routing table and joins the ECMP pool, or falls through to the ``*)``
    backup-class branch. The file is /etc/dhcp/dhclient-enter-hooks — extensionless.
    """
    hook = read(hostdir / "dhclient-enter-hooks.txt")
    # The matched branch is a case arm listing interfaces separated by '|', ending in ')'.
    m = re.search(r"^\s*((?:[a-z0-9]+\s*\|\s*)+[a-z0-9]+)\s*\)", hook, re.M)
    if not m:
        return []
    return [i.strip() for i in m.group(1).split("|")]


def parse_netplan_vlans(hostdir: Path) -> list[int]:
    """VLAN ids present in the rendered netplan — i.e. what smc_network believes exists."""
    return sorted({int(m.group(1)) for m in re.finditer(r"^\s+vlan(\d+):", read(hostdir / "netplan.txt"), re.M)})


def parse_nat_ifaces(hostdir: Path) -> list[str]:
    """Interfaces masqueraded in nat POSTROUTING — what smc_iptables believes exists.

    'iptables -S' alone would miss this: it dumps only the filter table.
    """
    nat = read(hostdir / "iptables-nat.txt")
    return sorted({m.group(1) for m in re.finditer(r"^-A POSTROUTING -o (\S+) -j MASQUERADE", nat, re.M)})


def parse_live(hostdir: Path) -> dict:
    """Extract routing facts from one host's capture directory."""
    route = read(hostdir / "ip-route.txt")
    rule = read(hostdir / "ip-rule.txt")

    # Multipath default: a bare "default" line followed by indented nexthop lines.
    ecmp: list[str] = []
    in_default = False
    for line in route.splitlines():
        if re.match(r"^default\s*$", line):
            in_default = True
            continue
        if in_default:
            m = re.search(r"nexthop via \S+ dev (\S+)", line)
            if m:
                ecmp.append(m.group(1))
                continue
            in_default = False

    # Single-nexthop default written by the hook's fall-through branch.
    stray = [m.group(1) for m in re.finditer(r"^default via \S+ dev (\S+) metric 100", route, re.M)]

    # Any interface holding a CGNAT lease.
    leased = sorted({m.group(1) for m in re.finditer(r"^100\.64\.0\.0/10 dev (\S+)", route, re.M)})

    # Source rules prove the hook built a per-interface table for that device.
    recognised = sorted({m.group(1) for m in re.finditer(r"lookup (\S+)$", rule, re.M)}
                        - {"local", "main", "default"})

    hook = parse_hook(hostdir)
    return {
        "ecmp": sorted(ecmp),
        "stray": stray,
        "leased": leased,
        "recognised": recognised,
        "orphaned": sorted(set(leased) - set(recognised)),
        "hook": hook,
        "hook_vlans": sorted(int(i[4:]) for i in hook if i.startswith("vlan")),
        "netplan_vlans": parse_netplan_vlans(hostdir),
        "nat_ifaces": parse_nat_ifaces(hostdir),
        # Rules with no corresponding hook entry: the hook cannot have created them in its
        # current form, so they are residue from an earlier render of the hook.
        "stale_rules": sorted(set(recognised) - set(hook)) if hook else [],
    }


def committed_internet_vlans(site: str, commit: str) -> list[int] | None:
    """Every ``role: internet`` VLAN id defined for a site at a commit, both switch series.

    The dhclient hook's case arm is generated from exactly this set, so comparing it against the
    live hook identifies which topology state ``smc_application`` was last rendered from.
    """
    path = f"{commit}:{TOPOLOGY_DIR}/{site}.yml"
    try:
        blob = subprocess.run(
            ["git", "show", path],
            cwd=ANSIBLE_REPO, capture_output=True, text=True, check=True,
        ).stdout
    except subprocess.CalledProcessError:
        return None

    vlans: list[int] = []
    pending = False
    for line in blob.splitlines():
        if re.match(r"^\s+internet\d+:", line):
            pending = True
            continue
        if pending and (m := re.match(r"^\s+vlanid:\s*(\d+)", line)):
            vlans.append(int(m.group(1)))
            pending = False
    return sorted(vlans)


def committed_primaries(site: str, commit: str) -> tuple[int, list[int]] | tuple[None, None]:
    """Count switch01 primary uplinks defined for a site at a given commit."""
    path = f"{commit}:{TOPOLOGY_DIR}/{site}.yml"
    try:
        blob = subprocess.run(
            ["git", "show", path],
            cwd=ANSIBLE_REPO, capture_output=True, text=True, check=True,
        ).stdout
    except subprocess.CalledProcessError:
        return None, None

    vlans: list[int] = []
    current_key = None
    for line in blob.splitlines():
        if m := re.match(r"^\s+(internet\d+):", line):
            current_key = m.group(1)
            continue
        if current_key and (m := re.match(r"^\s+vlanid:\s*(\d+)", line)):
            vid = int(m.group(1))
            if vid in SWITCH01_RANGE:
                vlans.append(vid)
            current_key = None
    return len(vlans), sorted(vlans)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("capture", nargs="?", help="capture directory (default: newest under evidence/)")
    ap.add_argument("--commit", default=DEPLOYED_COMMIT, help="commit to compare topology against")
    ap.add_argument("--flavor", default="rcp", help="inventory flavor, i.e. inventories/<flavor>/topology_vars (default: rcp)")
    ap.add_argument("--markdown", action="store_true", help="emit a markdown table")
    args = ap.parse_args()

    global TOPOLOGY_DIR
    TOPOLOGY_DIR = f"inventories/{args.flavor}/topology_vars"

    capture = Path(args.capture) if args.capture else newest_capture()
    if not capture.is_absolute():
        capture = (REPO_ROOT / capture).resolve()
    if not capture.is_dir():
        sys.exit(f"not a directory: {capture}")

    hostdirs = sorted(p for p in capture.iterdir() if p.is_dir())
    if not hostdirs:
        sys.exit(f"no host directories in {capture}")

    rows = []
    for hostdir in hostdirs:
        site = hostdir.name.removesuffix("-smc01")
        live = parse_live(hostdir)
        count, vlans = committed_primaries(site, args.commit)

        # THE DISCRIMINATOR.
        #
        # smc_network writes netplan; smc_application writes the dhclient hook. An uplink VLAN that
        # netplan creates but the hook's case arm omits will lease normally, get no per-interface
        # table, and fall through to the backup-class '*)' branch. So a site is healthy exactly
        # when the hook covers every uplink VLAN netplan defines.
        #
        # 621/631 are the SMP backup VLANs. They are meant to be absent from the hook — the
        # 'metric 100' route on vlan621 is the intended behaviour, not a fault. Exclude them.
        BACKUP_VLANS = {621, 631}
        netplan_uplinks = {v for v in live["netplan_vlans"] if v not in BACKUP_VLANS}
        hook_vlans = set(live["hook_vlans"])
        uncovered = sorted(netplan_uplinks - hook_vlans)

        if not netplan_uplinks:
            verdict = "no uplink VLANs in netplan"
        elif not hook_vlans:
            verdict = "hook not captured"
        elif uncovered:
            verdict = f"HOOK MISSING {len(uncovered)}: {','.join(str(v) for v in uncovered)}"
        else:
            verdict = "hook covers netplan"

        # Which committed topology state does the deployed hook correspond to?
        hook_matches = [
            label for label, sha in CANDIDATE_COMMITS.items()
            if (cv := committed_internet_vlans(site, sha)) is not None
            and cv == live["hook_vlans"]
        ]

        rows.append({
            "site": site,
            "committed": count if count is not None else "n/a",
            "committed_vlans": ",".join(str(v) for v in vlans) if vlans else "n/a",
            "ecmp": ",".join(live["ecmp"]) or "—",
            "stray": ",".join(live["stray"]) or "—",
            "orphaned": ",".join(live["orphaned"]) or "—",
            "verdict": verdict,
            "hook": " ".join(live["hook"]) or "—",
            "hook_vlans": live["hook_vlans"],
            "netplan_vlans": live["netplan_vlans"],
            "nat_ifaces": len(live["nat_ifaces"]),
            "stale_rules": ",".join(live["stale_rules"]) or "—",
            "hook_matches": ", ".join(hook_matches) or "no committed state",
        })

    if args.markdown:
        print(f"<!-- generated by scripts/analyse-routing-drift.py from {capture.name} -->")
        print("| Site | ECMP members (live) | Stray `metric 100` | Orphaned (leased, no rule) | Stale rules (no hook entry) |")
        print("|---|---|---|---|---|")
        for r in rows:
            print(f"| {r['site']} | `{r['ecmp']}` | `{r['stray']}` | `{r['orphaned']}` | `{r['stale_rules']}` |")
        print()
        print("| Site | `smc_application` hook | `smc_network` netplan VLANs | `smc_iptables` nat ifaces | Hook matches |")
        print("|---|---|---|---|---|")
        for r in rows:
            print(f"| {r['site']} | {len(r['hook_vlans'])} VLANs + physical (`{r['hook']}`) | {len(r['netplan_vlans'])} | {r['nat_ifaces']} | {r['hook_matches']} |")
    else:
        print(f"capture: {capture}")
        print(f"commit:  {args.commit[:12]}\n")
        for r in rows:
            print(f"{r['site']}")
            print(f"  switch01 primaries @ deployed : {r['committed']} ({r['committed_vlans']})")
            print(f"  ECMP members (live)           : {r['ecmp']}")
            print(f"  stray metric-100 default      : {r['stray']}")
            print(f"  orphaned (leased, no ip rule) : {r['orphaned']}")
            print(f"  stale ip rules (no hook entry): {r['stale_rules']}")
            print(f"  hook interfaces               : {r['hook']}")
            print(f"  hook VLANs / netplan / nat    : {len(r['hook_vlans'])} / {len(r['netplan_vlans'])} / {r['nat_ifaces']}")
            print(f"  hook rendered from            : {r['hook_matches']}")
            print(f"  verdict                       : {r['verdict']}\n")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
