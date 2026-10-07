#!/usr/bin/env python3
"""Add, show or remove an SNMP community on a MikroTik behind an SMC, with the community value taken from KeePass and never printed.

usage: mikrotik_snmp_community.py <smc-host> <device-ip> <action> <vault-entry> [--rw] [--allow <cidr>] [--tag <comment>]
  action:  enable   disable the default `public` community, add <vault-entry>'s community (read-only unless --rw) limited to --allow
                    (default 10.255.0.1/32, the SMC), and turn SNMP on
           remove   remove the community whose comment is --tag (default unc-ro); with --disable-snmp also turn SNMP off and re-enable `public`
           show     /snmp print and the community list, the value redacted
  Writes go through scripts/mikrotik_exec.sh with MT_ALLOW_WRITE=1, which this script sets only for enable and remove.

Why (2026-10-07): the community has to appear in the RouterOS command, so this script builds the command itself and replaces the value
with <community> in everything it prints. The command runs on the device over the SSH session from this machine; the SMC only forwards TCP.
"""

from __future__ import annotations

import argparse
import os
import pathlib
import re
import subprocess
import sys

EXEC = pathlib.Path(__file__).resolve().parent / "mikrotik_exec.sh"


def ros_quote(s: str) -> str:
    """Quote a string as one RouterOS CLI argument: double quotes, with backslash, quote and `$` escaped (RouterOS expands `$name` inside double quotes)."""
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"').replace("$", "\\$") + '"'


def main() -> int:
    """Build the RouterOS commands for the action, run them through mikrotik_exec.sh, and print the output with every community redacted.

    The community is read from KeePass here and exists only in this process, the SSH session and the device's config. enable and remove set
    MT_ALLOW_WRITE=1 for that one call; show stays read-only. Every `name=` in the output except the default `public` is replaced with <community>,
    because `print detail` lists ALL communities, not only the one passed in. Returns mikrotik_exec.sh's exit code; 3 when the vault gives no value.
    """
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("smc"); ap.add_argument("ip"); ap.add_argument("action", choices=["enable", "remove", "show"]); ap.add_argument("entry")
    ap.add_argument("--rw", action="store_true", help="grant write access (for a short write test; remove it afterwards)")
    ap.add_argument("--allow", default="10.255.0.1/32", help="addresses allowed to use the community (default: the SMC)")
    ap.add_argument("--tag", default=None, help="comment that marks the community (default unc-ro, or unc-rw-test with --rw)")
    ap.add_argument("--disable-snmp", action="store_true", help="with remove: also turn SNMP off and re-enable the default public community")
    a = ap.parse_args()
    tag = a.tag or ("unc-rw-test" if a.rw else "unc-ro")
    community = subprocess.run(["kp", "show", "-s", "-a", "Password", a.entry], capture_output=True, text=True).stdout.rstrip("\n")
    if not community or "\n" in community:
        print(f"cannot read a one-line community from {a.entry}", file=sys.stderr)
        return 3
    show = ["/snmp print", "/snmp community print detail without-paging"]
    if a.action == "enable":
        cmds = ['/snmp community set [find name="public"] disabled=yes',
                f"/snmp community add name={ros_quote(community)} addresses={a.allow} read-access=yes write-access={'yes' if a.rw else 'no'} comment={tag}",
                "/snmp set enabled=yes"] + show
    elif a.action == "remove":
        cmds = [f'/snmp community remove [find comment="{tag}"]']
        if a.disable_snmp:
            cmds += ["/snmp set enabled=no", '/snmp community set [find name="public"] disabled=no']
        cmds += show
    else:
        cmds = show
    env = dict(os.environ, MT_PY=os.environ.get("MT_PY", sys.executable), MT_ALLOW_WRITE="1" if a.action != "show" else os.environ.get("MT_ALLOW_WRITE", "0"))
    out = subprocess.run([str(EXEC), a.smc, a.ip, *cmds], capture_output=True, text=True, env=env, timeout=600)
    text = (out.stdout + out.stderr).replace(ros_quote(community), "<community>").replace(community, "<community>")
    # Every OTHER community on the device is a secret too: `print detail` lists them all, so redact every name= except the
    # default `public` (2026-10-07: a run with the rw entry printed the ro community in clear).
    text = re.sub(r'name=("(?:[^"\\]|\\.)*"|\S+)', lambda m: m.group(0) if m.group(1) in ('"public"', "public") else "name=<community>", text)
    sys.stdout.write(text)
    return out.returncode


if __name__ == "__main__":
    sys.exit(main())
