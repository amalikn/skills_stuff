#!/usr/bin/env python3
"""Read-only GPS / position probe of Cambium units from their site's SMC (get + bulkwalk only). Coordinate values are never printed.

usage: gps_probe.py '<plan json>'
  plan: {"node": "<site>-smc01", "proxy": "teleport.apn.au", "units": [{"ip": "10.255.x.y", "label": "...", "kind": "epmp|walk", "arm": ".1.3.6.1.4.1..."}]}
  kind epmp  GETs the CAMBIUM-PMP80211-MIB GPS and location objects (cambiumGPS*, cambiumDeviceLatitude/Longitude, systemDeviceLoc*, sync source)
  kind walk  bulkwalks `arm` and reports coordinate-like values and gps/latitude text, without values
Each coordinate is reported only as empty, 0, "present, AU-plausible" or "present, NOT AU-plausible"; with two or more units it prints the distance
between their positions. Uses unified-network-controller's wc-local/scripts/smc/smc_snmp.py (net-snmp on the SMC: rcp and nbn_accelerate sites only)
and the read-only community from KeePass. Written for the GPS check of 2026-10-07 (operator: which devices give GPS coordinates).
"""
import json, re, subprocess, sys
sys.path.insert(0, "/Volumes/Data/_ai/_project/project_stuff/apn/unified-network-controller/wc-local/scripts/smc")
import smc_snmp as S

E = ".1.3.6.1.4.1.17713.21"
EPMP = {
    "cambiumDeviceLatitude": E + ".1.1.18.0", "cambiumDeviceLongitude": E + ".1.1.19.0",
    "cambiumEffectiveSyncSource": E + ".1.1.7.0",
    "cambiumGPSCurrentSyncState": E + ".1.3.1.0", "cambiumGPSLatitude": E + ".1.3.2.0", "cambiumGPSLongitude": E + ".1.3.3.0",
    "cambiumGPSHeight": E + ".1.3.4.0", "cambiumGPSTime": E + ".1.3.5.0", "cambiumGPSNumTrackedSat": E + ".1.3.6.0",
    "cambiumGPSNumVisibleSat": E + ".1.3.7.0", "cambiumGPSDeviceInfo": E + ".1.3.9.0",
    "systemDeviceLocLatitude": E + ".3.6.1.6.0", "systemDeviceLocLongitude": E + ".3.6.1.7.0",
    "wirelessInterfaceSyncSource": E + ".3.8.2.14.0",
}
COORDS = {"cambiumDeviceLatitude", "cambiumDeviceLongitude", "cambiumGPSLatitude", "cambiumGPSLongitude",
          "systemDeviceLocLatitude", "systemDeviceLocLongitude"}
NUM = re.compile(r"-?\d{1,3}\.\d{3,}")


def redact(name, v):
    if name in COORDS or NUM.fullmatch(v.strip('"') or "x"):
        s = v.strip('"').strip()
        if not s:
            return "<empty>"
        try:
            f = float(s)
        except ValueError:
            return f"<non-numeric len {len(s)}>"
        if f == 0:
            return "0"
        au = (-45 <= f <= -9) if "Lat" in name or "lat" in name else (112 <= f <= 155)
        return "present, AU-plausible" if au else "present, NOT AU-plausible"
    return v


def community(proxy):
    entry = S.COMMUNITY_KEYS[(proxy, "ro")]
    return subprocess.run(["kp", "show", "-s", "-a", "Password", entry], capture_output=True, text=True).stdout.rstrip("\n")


def main():
    plan = json.loads(sys.argv[1])  # {"node":..,"proxy":..,"units":[{"ip":..,"label":..,"kind":"epmp|walk","arm":".."}]}
    domain = plan["proxy"].removeprefix("teleport.")
    com = community(plan["proxy"])
    cmds, keys = [], []
    for u in plan["units"]:
        cmds.append(S.get(u["ip"], ".1.3.6.1.2.1.1.1.0", ".1.3.6.1.2.1.1.6.0")); keys.append((u, "sys"))
        if u["kind"] == "epmp":
            cmds.append(S.get(u["ip"], *EPMP.values())); keys.append((u, "epmp"))
            cmds.append(S.bulkwalk(u["ip"], E + ".1.3")); keys.append((u, "gpswalk"))
            cmds.append(S.bulkwalk(u["ip"], E + ".1.1")); keys.append((u, "fw"))
        for arm in u.get("walk", []):
            cmds.append(S.bulkwalk(u["ip"], arm)); keys.append((u, "walk:" + arm))
    res = S.run(plan["node"], domain, com, cmds, timeout=600)
    inv = {v: k for k, v in EPMP.items()}
    for (u, what), (rc, out) in zip(keys, res):
        out = out.replace(com, "<community>") if com else out
        vals = S.parse(out)
        print(f"== {u['label']} {u['ip']} [{what}] rc={rc} values={len(vals)}")
        if what == "sys":
            d = vals.get(".1.3.6.1.2.1.1.1.0", "")
            print("   sysDescr:", d[:70], "| sysLocation:", "<set>" if vals.get(".1.3.6.1.2.1.1.6.0") else "<empty>")
            if not vals:
                print("   ", out.strip()[:120])
        elif what == "epmp":
            for o, v in vals.items():
                print(f"   {inv.get(o, o)} = {redact(inv.get(o, ''), v)}")
            import math
            def fl(k):
                try: return float(vals.get(EPMP[k], "").strip('"'))
                except ValueError: return None
            pairs = {"device": ("cambiumDeviceLatitude", "cambiumDeviceLongitude"), "gps": ("cambiumGPSLatitude", "cambiumGPSLongitude"),
                     "config": ("systemDeviceLocLatitude", "systemDeviceLocLongitude")}
            pts = {n: (fl(a), fl(b)) for n, (a, b) in pairs.items() if fl(a) is not None and fl(b) is not None}
            names = list(pts)
            for i in range(len(names)):
                for j in range(i + 1, len(names)):
                    (la1, lo1), (la2, lo2) = pts[names[i]], pts[names[j]]
                    km = 111.2 * math.hypot(la1 - la2, (lo1 - lo2) * math.cos(math.radians(la1)))
                    print(f"   distance {names[i]}<->{names[j]}: {km:.3f} km")
            PTS.append((u["label"], pts))
            missing = [k for k, o in EPMP.items() if o not in vals]
            if missing:
                print("   missing/NoSuch:", missing)
        elif what == "fw":
            print("   version-like:", sorted({v.strip('"') for v in vals.values() if re.fullmatch(r'"?\d+\.\d+(\.\d+)+"?', v)})[:4])
        else:
            if what == "gpswalk":
                subs = sorted({".".join(o.split(".")[:13]) for o in vals})
                print("   subtrees:", subs[:12])
            hits = [(o, v) for o, v in vals.items()
                    if re.search(r"gps|lat|long|satel", v, re.I) or NUM.fullmatch(v.strip('"').strip() or "x")]
            coordlike = []
            for o, v in hits:
                try:
                    f = float(v.strip('"'))
                    if -45 <= f <= -9 or 112 <= f <= 155:
                        coordlike.append(o)
                except ValueError:
                    pass
            print(f"   coordinate-like numeric values: {len(coordlike)} {coordlike[:8]}")
            txt = [(o, v[:50]) for o, v in hits if re.search(r"gps|satel|latit|longit", v, re.I)]
            print(f"   gps/lat text values: {txt[:8]}")


PTS = []

if __name__ == "__main__":
    import math
    main()
    for i in range(len(PTS)):
        for j in range(i+1, len(PTS)):
            a, b = PTS[i][1].get("device") or PTS[i][1].get("gps"), PTS[j][1].get("device") or PTS[j][1].get("gps")
            if a and b:
                print(f"   inter-unit {PTS[i][0]}<->{PTS[j][0]}: {111.2*math.hypot(a[0]-b[0],(a[1]-b[1])*math.cos(math.radians(a[0]))):.2f} km")
