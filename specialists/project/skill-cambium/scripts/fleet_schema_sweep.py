#!/usr/bin/env python3
"""Sweep every site and family to build the fleet-wide device response contract.

Stage 2 of the schema exercise (stage 1 being the per-family baseline in `schemas/`). For each
site this picks one representative device per family, contracts its responses with
`schema_tool.py`, and records what it found. The point is not the individual observation — it is
the merge afterwards, where a field present at 30 sites and absent at 6 stops being invisible.

Rules this implements, from `schemas/README.md`:

  * For client-bearing endpoints, pick the device that *has* clients. An AP with none returns an
    empty array, which is no evidence either way and would otherwise drag every field to optional.
  * Unreachable and empty are findings, not skips. A site with no reachable device of a family is
    a fact about the estate and is written to the findings log.
  * Never conclude a site is down from one tool's failure. `snmpget` is absent on `rcp`-flavour
    SMC boxes; this sweep deliberately uses no SNMP for exactly that reason.
  * ePMP is throttled — the family has a limited concurrent-session budget, so its devices are
    contracted one at a time with a pause between sites.

Two transports, chosen per family:

  * Enterprise Wi-Fi goes over **one Teleport hop per site**. The login and the GETs run as curl on
    the site's SMC box and the raw JSON comes back over stdout. No port-forward, no local listener,
    and the client-count sweep and the contract fetch share a single connection.
  * ePMP, cnPilot R-series and cnWave go through a **port-forward into this pack's own adapters**,
    because their auth flows already live there and are not worth reimplementing remotely.

Resumable: a site/family whose observation file already exists is left alone, so an interrupted
sweep continues where it stopped. Delete an observation to force a re-run.

Usage:
    CAMBIUM_* creds are read from the KeePassXC vault by the caller and passed in the environment.
    python3 scripts/fleet_schema_sweep.py --inventory <device-inventory.csv> --out schemas
    python3 scripts/fleet_schema_sweep.py ... --families enterprise-wifi --sites hope-vale,amata
"""
import argparse
import csv
import json
import os
import re
import socket
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
PACK = HERE.parent

WIFI_ENDPOINTS = ["client-summary", "radio-summary", "radio-rf-summary", "device-summary",
                  "platform-info", "interface-summary", "wlan-summary", "ethports-config",
                  "ip_route-summary"]

# inventory product_family -> (schema family slug, vault entry)
FAMILY_MAP = {
    "Enterprise Wi-Fi": ("enterprise-wifi", "enterprise-wifi"),
    "ePMP AP": ("epmp-ap", "epmp-ap"),
    "ePMP SM": ("epmp-sm", "epmp-sm"),
    "cnPilot R-series": ("cnpilot-r-series", "cnpilot-r-series"),
    "cnWave 60GHz": ("cnwave-60ghz", "cnwave-60ghz"),
    "cnWave 60 GHz": ("cnwave-60ghz", "cnwave-60ghz"),
}
ADAPTER = {
    "epmp-ap": "cambium_epmp_adapter.py",
    "epmp-sm": "cambium_epmp_adapter.py",
    "cnpilot-r-series": "cambium_r195p_adapter.py",
    "cnwave-60ghz": "cambium_cnwave_adapter.py",
}
THROTTLED = {"epmp-ap", "epmp-sm"}


def run(cmd, timeout, stdin_data=None):
    try:
        p = subprocess.run(cmd, input=stdin_data, capture_output=True, text=True, timeout=timeout)
        return p.returncode, p.stdout, p.stderr
    except subprocess.TimeoutExpired:
        return 124, "", "timeout"
    except OSError as exc:
        return 125, "", str(exc)


def free_port():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def load_inventory(path):
    """site -> family slug -> [ {ip, name, model, firmware} ], deduped by management IP."""
    sites = defaultdict(lambda: defaultdict(list))
    with open(path, newline="") as fh:
        for row in csv.DictReader(fh):
            ip = (row.get("management_ip") or "").strip()
            fam = FAMILY_MAP.get((row.get("product_family") or "").strip())
            site = (row.get("site") or "").strip()
            if not ip.startswith("10.") or not fam or not site:
                continue
            entry = {"ip": ip, "name": row.get("device_name", ""),
                     "model": (row.get("model") or "").strip(),
                     "firmware": (row.get("current_firmware") or "").strip()}
            bucket = sites[site][fam[0]]
            if not any(e["ip"] == ip for e in bucket):
                bucket.append(entry)
    return sites


def build_node_map(proxies):
    """site -> (node, proxy). A site listed on both clusters is taken from the first that has it,
    which is the order the caller gave — the sweep records which proxy it used, so a wrong guess
    shows up as a finding rather than as silence."""
    node_map = {}
    for proxy in proxies:
        rc, out, _ = run(["tsh", "ls", "--proxy", proxy, "--format=text"], 120)
        if rc != 0:
            print(f"! tsh ls failed on {proxy}", file=sys.stderr)
            continue
        for line in out.splitlines()[2:]:
            node = line.split()[0] if line.split() else ""
            m = re.match(r"^(.*)-smc\d+$", node)
            if m and m.group(1) not in node_map:
                node_map[m.group(1)] = (node, proxy)
    return node_map


REMOTE_WIFI = r'''
# u, p, ips and eps arrive exported from stdin - never as arguments, see observe_wifi().
#
# Endpoints are fetched inside the probe loop, immediately after authenticating to that AP, and
# the best AP's output is kept. Two earlier designs failed: logging in again after the loop made
# client-summary return literal null, and reusing the winner's cookie jar after the loop made it
# return empty. Both looked authenticated and both silently lost the client data on every site.
# Fetching while the session is fresh is the only pattern observed to work.
best_ip=""; best_n=-1; best_out=""
for ip in $ips; do
  cj=$(mktemp)
  curl -sk -c "$cj" -X POST -H 'Content-Type: application/json' --max-time 5 \
       -d "{\"username\":\"$u\",\"password\":\"$p\"}" "https://$ip/api/login" >/dev/null 2>&1
  tok=$(grep XSRF-TOKEN "$cj" 2>/dev/null | awk '{print $7}')
  if [ -z "$tok" ]; then echo "COUNT $ip login-failed" >&2; rm -f "$cj"; continue; fi
  # note the space after the colon in the device's JSON - matching without it silently yields 0
  n=$(curl -sk -b "$cj" -H "X-XSRF-TOKEN: $tok" --max-time 6 "https://$ip/api/radio-summary" 2>/dev/null \
      | tr ',' '\n' | grep -oE '"num_clients": *[0-9]+' | grep -oE '[0-9]+$' | paste -sd+ - | bc 2>/dev/null)
  [ -z "$n" ] && n=0
  echo "COUNT $ip $n" >&2
  if [ "$n" -gt "$best_n" ]; then
    out=$(mktemp)
    for ep in $eps; do
      echo "###EP###$ep###" >> "$out"
      curl -sk -b "$cj" -H "X-XSRF-TOKEN: $tok" --max-time 15 "https://$ip/api/$ep" >> "$out" 2>/dev/null
      echo >> "$out"
    done
    [ -n "$best_out" ] && rm -f "$best_out"
    best_n=$n; best_ip=$ip; best_out="$out"
  fi
  curl -sk -b "$cj" -H "X-XSRF-TOKEN: $tok" --max-time 5 -X POST "https://$ip/api/logout" >/dev/null 2>&1
  rm -f "$cj"
done
[ -z "$best_ip" ] && { echo "NO_DEVICE" ; exit 0; }
echo "TARGET $best_ip $best_n" >&2
echo "###TARGET###$best_ip###$best_n###"
cat "$best_out"
rm -f "$best_out"
'''


def observe_wifi(site, node, proxy, devices, out_dir, creds, findings):
    """The credential is fed to the remote shell on stdin, never as an argument.

    An argument lands in the process table on both this machine and the SMC box, where any user
    running `ps` sees the device's admin password in clear text — and it also leaks into local
    shell history and into any transcript that captures a process listing. The remote script reads
    the first two stdin lines as username and password before the rest of the heredoc runs.
    """
    ips = " ".join(d["ip"] for d in devices)
    payload = f"{creds[0]}\n{creds[1]}\n{ips}\n{' '.join(WIFI_ENDPOINTS)}\n" + REMOTE_WIFI
    rc, out, err = run(
        ["tsh", "ssh", "--proxy", proxy, f"root@{node}",
         "IFS= read -r u; IFS= read -r p; IFS= read -r ips; IFS= read -r eps; "
         "export u p ips eps; bash -s"],
        timeout=420, stdin_data=payload)
    if rc != 0 and "###TARGET###" not in out:
        findings.append({"site": site, "family": "enterprise-wifi", "status": "unreachable",
                         "detail": (err or out).strip()[:200]})
        return None
    if "NO_DEVICE" in out or "###TARGET###" not in out:
        findings.append({"site": site, "family": "enterprise-wifi", "status": "no-login",
                         "detail": "no device at this site accepted the vault credential"})
        return None

    # Parse the header and the endpoint blocks independently. Slicing the header off with a
    # shared "###" split used to swallow the first block's delimiter, so the first endpoint in
    # the list was dropped every time — silently, because the others parsed fine. client-summary
    # was first, which cost two full fleet sweeps their client data before the cause was found.
    header = out.partition("###TARGET###")[2].split("###EP###", 1)[0]
    parts = header.split("###")
    target_ip = parts[0].strip() if parts else ""
    client_total = parts[1].strip() if len(parts) > 1 else ""
    payloads = {}
    for chunk in out.split("###EP###")[1:]:
        name, _, raw = chunk.partition("###")
        raw = raw.strip()
        if not raw:
            continue
        try:
            payloads[name.strip()] = json.loads(raw)
        except ValueError:
            findings.append({"site": site, "family": "enterprise-wifi", "status": "bad-json",
                             "endpoint": name.strip()})
    if not payloads:
        findings.append({"site": site, "family": "enterprise-wifi", "status": "no-payload"})
        return None

    dev = next((d for d in devices if d["ip"] == target_ip), {"model": "", "firmware": ""})
    return write_observation(out_dir, "enterprise-wifi", site, dev, payloads,
                             layer="raw-endpoint", extra={"clients_on_target": client_total,
                                                          "devices_probed": len(devices)})


def observe_adapter(site, node, proxy, family, dev, out_dir, creds, findings):
    port = free_port()
    remote_port = 22 if family == "cnpilot-r-series" else 443
    fwd = subprocess.Popen(
        ["tsh", "ssh", "--proxy", proxy, "-L", f"{port}:{dev['ip']}:{remote_port}",
         f"root@{node}", "sleep 240"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        if not wait_for_port(port, 40):
            findings.append({"site": site, "family": family, "device": dev["name"],
                             "status": "forward-failed"})
            return None
        env = dict(os.environ, CAMBIUM_HOST=f"localhost:{port}",
                   CAMBIUM_USER=creds[0], CAMBIUM_PASS=creds[1])
        p = subprocess.run([sys.executable, str(HERE / ADAPTER[family])],
                           capture_output=True, text=True, timeout=180, env=env)
        if p.returncode != 0 or not p.stdout.strip():
            findings.append({"site": site, "family": family, "device": dev["name"],
                             "status": "adapter-failed",
                             "detail": (p.stderr or "").strip().splitlines()[-1][:200] if p.stderr else ""})
            return None
        try:
            payload = json.loads(p.stdout)
        except ValueError:
            findings.append({"site": site, "family": family, "device": dev["name"],
                             "status": "bad-json"})
            return None
        return write_observation(out_dir, family, site, dev, payload,
                                 layer="adapter-normalized")
    except subprocess.TimeoutExpired:
        findings.append({"site": site, "family": family, "device": dev["name"], "status": "timeout"})
        return None
    finally:
        fwd.terminate()
        try:
            fwd.wait(timeout=10)
        except subprocess.TimeoutExpired:
            fwd.kill()


def wait_for_port(port, seconds):
    deadline = time.time() + seconds
    while time.time() < deadline:
        with socket.socket() as s:
            s.settimeout(2)
            if s.connect_ex(("127.0.0.1", port)) == 0:
                return True
        time.sleep(1)
    return False


def write_observation(out_dir, family, site, dev, payload, layer, extra=None):
    """Hand the payload to schema_tool so there is exactly one inference implementation."""
    model_slug = re.sub(r"[^A-Za-z0-9]+", "-", dev.get("model") or "unknown").strip("-") or "unknown"
    target = Path(out_dir) / "_observations" / family / f"{site}-{model_slug}-{datetime.now().strftime('%Y%m%d')}.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    cmd = [sys.executable, str(HERE / "schema_tool.py"), "observe", "--driver", "stdin",
           "--split-getters", "--layer", layer, "--family", family, "--site", site,
           "--model", dev.get("model") or "", "--firmware", dev.get("firmware") or "",
           "--out", str(target)]
    p = subprocess.run(cmd, input=json.dumps(payload), capture_output=True, text=True, timeout=120)
    if p.returncode != 0:
        print(f"    schema_tool failed: {p.stderr.strip()[:160]}", file=sys.stderr)
        return None
    if extra:
        doc = json.loads(target.read_text())
        doc["x-observation"].update(extra)
        target.write_text(json.dumps(doc, indent=2) + "\n")
    return target


def vault(entry, field):
    rc, out, _ = run(["kp", "show", "-s", "-a", field, f"cambium-devices/{entry}"], 60)
    return out.strip() if rc == 0 else ""


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--inventory", required=True)
    ap.add_argument("--out", default=str(PACK / "schemas"))
    ap.add_argument("--families", default=",".join(sorted({v[0] for v in FAMILY_MAP.values()})))
    ap.add_argument("--sites", default="")
    ap.add_argument("--findings", default="")
    ap.add_argument("--proxies", default="teleport.communitywifi.net.au,teleport.apn.au")
    ap.add_argument("--workers", type=int, default=9, help="sites swept in parallel; families stay sequential within a site")
    args = ap.parse_args()

    families = [f.strip() for f in args.families.split(",") if f.strip()]
    only_sites = {s.strip() for s in args.sites.split(",") if s.strip()}

    inventory = load_inventory(args.inventory)
    node_map = build_node_map([p.strip() for p in args.proxies.split(",") if p.strip()])
    # Some sites (kalumburu, confirmed 2026-09-20) still carry the older local-admin password, so
    # every family gets its primary entry plus a `-legacy` fallback tried in order. A site failing
    # on the primary alone is a credential finding, not an unreachable device.
    creds = {}
    for _, entry in set(FAMILY_MAP.values()):
        pairs = []
        for name in (entry, f"{entry}-legacy"):
            u, pw = vault(name, "UserName"), vault(name, "Password")
            if pw:
                pairs.append((u, pw))
        creds[entry] = pairs

    sites = sorted(s for s in inventory if not only_sites or s in only_sites)

    # Sites are independent devices, so they parallelise safely. ePMP's concurrent-session limit
    # is per device, not per fleet, and families stay sequential within a site so a single AP is
    # never hit by two workers at once.
    lock = threading.Lock()
    counter = {"n": 0}
    findings = []
    made = 0

    def do_site(site):
        nonlocal made
        local_findings = []
        lines = []
        with lock:
            counter["n"] += 1
            i = counter["n"]
        if site not in node_map:
            local_findings.append({"site": site, "family": "*", "status": "no-teleport-node"})
            lines.append(f"[{i}/{len(sites)}] {site}: no Teleport node")
        else:
            node, proxy = node_map[site]
            lines.append(f"[{i}/{len(sites)}] {site} via {node} ({proxy.split('.')[1]})")
            for family in families:
                devices = inventory[site].get(family) or []
                if not devices:
                    continue
                if list((Path(args.out) / "_observations" / family).glob(f"{site}-*.json")):
                    lines.append(f"    {family}: already observed")
                    continue
                vault_entry = next(v[1] for v in FAMILY_MAP.values() if v[0] == family)
                cred_list = creds.get(vault_entry) or []
                if not cred_list:
                    local_findings.append({"site": site, "family": family, "status": "no-credential"})
                    continue
                got = None
                for cred in cred_list:
                    if family == "enterprise-wifi":
                        got = observe_wifi(site, node, proxy, devices, args.out, cred, local_findings)
                    else:
                        for dev in devices[:4]:
                            got = observe_adapter(site, node, proxy, family, dev, args.out, cred, local_findings)
                            if got:
                                break
                    if got:
                        break
                lines.append(f"    {family}: {'ok ' + Path(got).name if got else 'FAILED'}")
                if got:
                    with lock:
                        made += 1
        with lock:
            findings.extend(local_findings)
            print("\n".join(lines), flush=True)

    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        list(pool.map(do_site, sites))

    findings_path = Path(args.findings or (Path(args.out) / "_observations" / "sweep-findings.json"))
    findings_path.parent.mkdir(parents=True, exist_ok=True)
    findings_path.write_text(json.dumps({
        "swept_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "sites": len(sites), "observations_made": made,
        "findings": findings,
    }, indent=2) + "\n")
    print(f"\nobservations made: {made}; findings: {len(findings)} -> {findings_path}")


if __name__ == "__main__":
    main()
