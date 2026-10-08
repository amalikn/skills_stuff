#!/usr/bin/env python3
"""Return one MikroTik switch's ports to their factory MACs (`reset-mac-address`), with a saved before-state, a read-back and a JSON summary.

usage: mikrotik_mac_reset.py <smc-host> <device-ip> --out <capture-dir> [--proxy teleport.apn.au] [--apply] [--wait 20] [--readback-timeout 600]
  Plan only by default: reads the switch, saves the before-state, reports each port's mac-address against its orig-mac-address and each
  bridge's mac, and says what an apply would change. Nothing is written to the device.
  --apply  runs `/interface ethernet reset-mac-address [find]` (MT_ALLOW_WRITE=1 for that one call), waits --wait seconds, reads the switch
           back, retrying every 30 s until --readback-timeout (the SMC's Teleport tunnel drops for 4-5 minutes after the reset: 20-mile,
           adjamarragu, areyonga 2026-10-08), and verifies that every port's mac-address equals its orig-mac-address and that every
           auto-mac bridge now carries one of the ports' factory MACs. The verdict is the read-back's: the reset's own SSH session is closed
           by the switch as its MACs change, so its exit code is recorded, not judged.
  stdout: one JSON object (serial, model, firmware, before/after per port and bridge, result) for updating an inventory; the human report
  goes to stderr. Exit 0 on plan, nothing to do, or a verified apply; 1 when verification fails; 2 on bad arguments; otherwise the
  exit code of the failed read (4: the port-forward did not come up).

One switch at a time (operator rule, 2026-10-08): the script takes exactly one SMC and one address and refuses lists. Run it, read the
result, then the next switch.

Why (references/05_known-issues.md #11): the provisioning script sets the same five `mac-address=` values on every RB450Gx4, so switches at
different sites share port MACs. Proven on glen-hill-switch01 2026-10-08 (operator approved): `reset-mac-address [find]` exists on RouterOS
7.8, returned ether1-ether5 to their orig-mac-address, the four `auto-mac=yes` bridges followed at once without a reboot, switch and AP
answered ping throughout, and the SMC re-learned the switch by ARP within three minutes. A bridge with `auto-mac=no` keeps its admin MAC and
is reported, not judged. No secret passes through this script: mikrotik_exec.sh reads the login from KeePass into SSHPASS only.
"""

from __future__ import annotations

import argparse
import datetime
import ipaddress
import json
import os
import pathlib
import re
import subprocess
import sys
import time

WRAPPER = pathlib.Path(__file__).resolve().parent / "mikrotik_exec.sh"
READ_CMDS = [
    "/system routerboard print",
    "/interface ethernet print detail without-paging",
    "/interface bridge print detail without-paging",
]
RESET_CMD = "/interface ethernet reset-mac-address [find]"


# ------------------------------------------------------------------------------------------------------------- parsing


def sections(text: str) -> dict[str, str]:
    """Split mikrotik_exec.sh output into {command: output} on its `### <command>` headers.

    Text before the first header (none in normal output) is dropped; a command whose header is missing maps to nothing, which the callers
    treat as an unreadable switch rather than an empty one.
    """
    out: dict[str, str] = {}
    cur = None
    for line in text.splitlines():
        if line.startswith("### "):
            cur = line[4:].strip()
            out[cur] = ""
        elif cur is not None:
            out[cur] += line + "\n"
    return out


def parse_detail(text: str) -> list[dict[str, str]]:
    """Parse a RouterOS `print detail` listing into one dict per item, with `_flags` holding the flag letters.

    An item starts on a line `<index> <flags> key=value ...` and continues on indented lines until the next index line. Quoted values
    keep their content without the quotes. `;;;` comment lines and the `Flags:` legend are ignored.
    """
    items: list[dict[str, str]] = []
    cur: dict[str, str] | None = None
    for line in text.splitlines():
        if line.strip().startswith(";;;") or line.startswith("Flags:"):
            continue
        m = re.match(r"^\s*(\d+)\s+([A-Z ]*?)\s*(?=[\w-]+=)", line)
        if m:
            cur = {"_index": m.group(1), "_flags": m.group(2).replace(" ", "")}
            items.append(cur)
        if cur is None:
            continue
        for k, quoted, bare in re.findall(r'([\w-]+)=(?:"([^"]*)"|(\S+))', line):
            cur[k] = quoted if quoted or not bare else bare
    return items


def parse_routerboard(text: str) -> dict[str, str]:
    """Parse `/system routerboard print` (one `key: value` per line) into a dict."""
    out = {}
    for line in text.splitlines():
        m = re.match(r"^\s*([\w-]+):\s*(.*?)\s*$", line)
        if m:
            out[m.group(1)] = m.group(2)
    return out


def snapshot(text: str) -> dict:
    """Turn one read of the three READ_CMDS into {routerboard, ports, bridges}; raises ValueError when a section is missing or empty."""
    sec = sections(text)
    missing = [c for c in READ_CMDS if not sec.get(c, "").strip()]
    if missing:
        raise ValueError(f"no output for: {', '.join(missing)}")
    ports = [p for p in parse_detail(sec[READ_CMDS[1]]) if "name" in p]
    bridges = [b for b in parse_detail(sec[READ_CMDS[2]]) if "name" in b]
    if not ports:
        raise ValueError("no ethernet ports parsed")
    return {"routerboard": parse_routerboard(sec[READ_CMDS[0]]), "ports": ports, "bridges": bridges}


# ------------------------------------------------------------------------------------------------------------- judging


def plan(before: dict) -> dict:
    """What an apply would change: the ports whose mac-address differs from orig-mac-address, and the auto-mac bridges not on a factory MAC."""
    origs = {p.get("orig-mac-address", "").upper() for p in before["ports"]}
    ports = [p["name"] for p in before["ports"] if p.get("mac-address", "").upper() != p.get("orig-mac-address", "").upper()]
    bridges = [b["name"] for b in before["bridges"] if b.get("auto-mac") == "yes" and b.get("mac-address", "").upper() not in origs]
    return {"ports_to_reset": ports, "bridges_expected_to_follow": bridges}


def judge(before: dict, after: dict | None) -> dict:
    """Build the JSON summary: per port and bridge the before (and after) MAC and whether it is right, plus the overall verdict.

    A port is right when mac-address equals orig-mac-address. An auto-mac bridge is right when its MAC is one of the ports' factory MACs
    (RouterOS picks the MAC of one of its ports, so which one is not checked). A bridge with auto-mac=no is reported with ok=None.
    With after=None (plan mode) the verdicts are taken from the before-state; an item missing from the read-back is not ok.
    """
    state = after or before
    origs = {p.get("orig-mac-address", "").upper() for p in state["ports"]}
    after_ports = {p["name"]: p for p in after["ports"]} if after else {}
    after_bridges = {b["name"]: b for b in after["bridges"]} if after else {}
    ports, bridges = [], []
    for p in before["ports"]:
        a = after_ports.get(p["name"], {}) if after else p
        row = {"name": p["name"], "orig_mac": p.get("orig-mac-address"), "before_mac": p.get("mac-address")}
        if after is not None:
            row["after_mac"] = a.get("mac-address")
        row["ok"] = bool(a) and a.get("mac-address", "").upper() == a.get("orig-mac-address", "").upper()
        ports.append(row)
    for b in before["bridges"]:
        a = after_bridges.get(b["name"], {}) if after else b
        row = {"name": b["name"], "auto_mac": b.get("auto-mac"), "before_mac": b.get("mac-address")}
        if after is not None:
            row["after_mac"] = a.get("mac-address")
        row["ok"] = None if b.get("auto-mac") != "yes" else (bool(a) and a.get("mac-address", "").upper() in origs)
        bridges.append(row)
    rb = before["routerboard"]
    all_ok = all(r["ok"] for r in ports) and all(r["ok"] is not False for r in bridges)
    return {"serial": rb.get("serial-number"), "model": rb.get("model"), "firmware": rb.get("current-firmware"),
            "ports": ports, "bridges": bridges, "plan": plan(before), "all_factory": all_ok}


# ------------------------------------------------------------------------------------------------------------- device calls


def run_routeros(smc: str, ip: str, proxy: str, cmds: list[str], write: bool = False) -> tuple[int, str, str]:
    """Run RouterOS commands through mikrotik_exec.sh (argument list, no shell); returns (exit code, stdout, stderr).

    MT_ALLOW_WRITE=1 is set only when write is True and is removed from the inherited environment otherwise, so a read can never become a
    write because the caller's shell had the variable set.
    """
    env = dict(os.environ, TSH_PROXY=proxy)
    env.pop("MT_ALLOW_WRITE", None)
    if write:
        env["MT_ALLOW_WRITE"] = "1"
    r = subprocess.run([str(WRAPPER), smc, ip, *cmds], capture_output=True, text=True, env=env)
    return r.returncode, r.stdout, r.stderr


def read_switch(smc: str, ip: str, proxy: str, out: pathlib.Path, label: str, retries: int = 1, pause: int = 10) -> tuple[int, dict | None]:
    """Read the switch, save the raw output as <out>/<label>.txt, and parse it; retried `retries` times after a `pause` s pause on a failed read.

    Returns (0, snapshot) or (exit code, None). A read that exits 0 but cannot be parsed counts as failed with code 1, since a half-read
    switch must never be judged.
    """
    rc = 1
    for attempt in range(retries + 1):
        rc, text, err = run_routeros(smc, ip, proxy, READ_CMDS)
        (out / f"{label}.txt").write_text(text + (f"\n# stderr\n{err}" if err.strip() else ""), encoding="utf-8")
        if rc == 0:
            try:
                return 0, snapshot(text)
            except ValueError as e:
                print(f"{label}: unparseable read ({e})", file=sys.stderr)
                rc = 1
        else:
            print(f"{label}: read failed (exit {rc}): {err.strip()[:200]}", file=sys.stderr)
        if attempt < retries:
            time.sleep(pause)
    return rc, None


def report(summary: dict) -> None:
    """Print the per-port and per-bridge table to stderr for the operator; the JSON on stdout is for machines."""
    after = any("after_mac" in r for r in summary["ports"])
    print(f"switch {summary['smc']} {summary['ip']}  serial {summary['serial']}  {summary['model']}  RouterOS {summary['firmware']}", file=sys.stderr)
    for r in summary["ports"]:
        tail = f"  after {r['after_mac']}" if after else ""
        print(f"  port   {r['name']:<16} mac {r['before_mac']}  orig {r['orig_mac']}{tail}  {'ok' if r['ok'] else 'DIFFERS'}", file=sys.stderr)
    for r in summary["bridges"]:
        tail = f"  after {r['after_mac']}" if after else ""
        verdict = {None: "auto-mac=no, not judged", True: "ok", False: "NOT a factory MAC"}[r["ok"]]
        print(f"  bridge {r['name']:<16} mac {r['before_mac']}{tail}  {verdict}", file=sys.stderr)
    print(f"result: {summary['result']}   capture: {summary['capture_dir']}", file=sys.stderr)


# ------------------------------------------------------------------------------------------------------------- main


def main(argv: list[str] | None = None) -> int:
    """Read and save the before-state, plan, and with --apply reset, read back and verify; print the JSON summary on stdout.

    Refuses a comma or space separated list of hosts or addresses (one switch at a time). With --apply and nothing to change, writes
    nothing. A failed write is still followed by a read-back, so the JSON shows the state the switch was left in.
    """
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("smc", help="the switch's SMC Teleport node, e.g. glen-hill-smc01")
    ap.add_argument("ip", help="the switch's address behind the SMC, e.g. 10.255.0.5")
    ap.add_argument("--out", required=True, type=pathlib.Path, help="capture folder (an investigation folder, never this pack)")
    ap.add_argument("--proxy", default="teleport.apn.au", help="Teleport proxy, passed as TSH_PROXY (default teleport.apn.au)")
    ap.add_argument("--apply", action="store_true", help="run reset-mac-address; without it nothing is written")
    ap.add_argument("--wait", type=int, default=20, help="seconds between the reset and the read-back (default 20)")
    ap.add_argument("--readback-timeout", type=int, default=600,
                    help="seconds to keep retrying the read-back, every 30 s, while the SMC's tunnel is down (default 600)")
    a = ap.parse_args(argv)
    if re.search(r"[,\s]", a.smc + a.ip):
        print("one switch at a time: give one SMC and one address", file=sys.stderr)
        return 2
    try:
        ipaddress.IPv4Address(a.ip)
    except ValueError:
        print(f"not an IPv4 address: {a.ip}", file=sys.stderr)
        return 2
    stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    out = a.out / f"mac-reset-{a.smc}-{a.ip}-{stamp}"
    out.mkdir(parents=True, exist_ok=True)

    rc, before = read_switch(a.smc, a.ip, a.proxy, out, "before")
    if before is None:
        return rc
    summary = {"smc": a.smc, "ip": a.ip, "proxy": a.proxy, "capture_dir": str(out), "mode": "apply" if a.apply else "plan"}
    summary.update(judge(before, None))
    if not summary["plan"]["ports_to_reset"]:
        summary["result"] = "nothing_to_do"
    elif not a.apply:
        summary["result"] = "planned"
    else:
        wrc, wout, werr = run_routeros(a.smc, a.ip, a.proxy, [RESET_CMD], write=True)
        (out / "reset.txt").write_text(wout + (f"\n# stderr\n{werr}" if werr.strip() else ""), encoding="utf-8")
        time.sleep(a.wait)
        rrc, after = read_switch(a.smc, a.ip, a.proxy, out, "after", retries=max(1, a.readback_timeout // 30), pause=30)
        if after is None:
            summary["result"] = f"readback_failed (write exit {wrc}, read exit {rrc})"
        else:
            summary.update(judge(before, after))
            summary["write_exit"] = wrc
            summary["result"] = "pass" if summary["all_factory"] else f"fail (write exit {wrc})"
    (out / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    report(summary)
    print(json.dumps(summary, indent=2))
    return 0 if summary["result"] in ("nothing_to_do", "planned", "pass") else 1


if __name__ == "__main__":
    sys.exit(main())
