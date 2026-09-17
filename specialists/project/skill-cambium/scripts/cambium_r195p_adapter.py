#!/usr/bin/env python3
"""Minimal Cambium cnPilot R195P (residential CPE) SSH adapter.

Different shape from cambium_xv2_adapter.py/cambium_epmp_adapter.py/cambium_cnwave_adapter.py in this directory: those three talk to a REST
API over HTTPS; R195P has none confirmed. The only access path this project has ever actually exercised live (cambium-swap evidence
E113/E114/E118) is a plain SSH login dropping into a real interactive shell — not a vendor "show"-style CLI (that's XV2's Falcon UI, a
different product line), a real BusyBox/Buildroot userland on a MIPS SoC (MT7621), confirmed live: `uname -a` returned
"Linux <hostname> 2.6.36 ... mips", built by a Flyingvoice/Actiontec-style OEM platform, not Cambium's own Falcon stack.

R195P's `device-family-matrix.csv` row lists "Yes (web UI)" for HTTPS access, but that is `USER_STATED` from vendor docs only — no agent
session has ever actually logged into R195P's web UI this project. Do not assume it works the same way XV2/E500/cnWave's web UIs do
(POST /api/login or /local/userLogin) without checking; R195P is a different, older cnPilot Home Router product line under the hood.

No pure-stdlib SSH client exists (paramiko is a real dependency, not installed per this project's stdlib-only convention for these
adapters) — this adapter shells out to the system `ssh`/`sshpass` binaries instead, the exact same mechanism used to reach every device in
this project by hand. That is a real, if unconventional, trade-off: correctness depends on `ssh`/`sshpass` being on PATH and the caller
already having network access to the device (normally via a `tsh` tunnel through the site's SMC box — see references/
02_device-access-and-vault.md).

Usage:
    CAMBIUM_HOST=10.255.11.55 CAMBIUM_USER=admin CAMBIUM_PASS='...' python3 cambium_r195p_adapter.py

Never hardcode or print CAMBIUM_PASS — pull it from the KeePassXC vault (`kp show -s -a Password cambium-devices/cnpilot-r-series`) into
an env var at the call site.

Confirmed live 2026-09-17 against two real Burringurrah units, BUR-R195P-1047 (10.255.11.47) and BUR-R195P-1055 (10.255.11.55) — see
cambium-swap evidence E113/E114/E118. Deliberately did NOT run `cat /etc/config/*` or any full-config dump this session (this family's SNMP
Get/Set community strings are known to be configured fleet-wide per the Ansible R195P provisioning template — encrypted there, but real —
and this project has two prior secret-exposure incidents on other families from exactly this kind of unscoped dump); get_config() below is
therefore NOT implemented. Add it deliberately, with REDACT_KEY_PATTERN applied, if a real need for it shows up — never as a blind
`cat /etc/config` dump.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys

DEFAULT_SSH_TIMEOUT = 8


class CambiumR195PAdapter:
    """Talks to one cnPilot R195P's real BusyBox/Buildroot shell over SSH, via the system ssh/sshpass binaries."""

    def __init__(self, host: str, username: str, password: str, timeout: int = DEFAULT_SSH_TIMEOUT) -> None:
        self.host = host
        self._username = username
        self._password = password
        self._timeout = timeout

    def _run(self, remote_command: str) -> str:
        """Run one remote shell command over SSH and return its stdout, raising on a non-zero exit or a timeout.

        Uses `sshpass -p <password> ssh ...` — the same pattern this project's own live sessions used by hand. `StrictHostKeyChecking=no`
        matches those sessions too: these are internal management-network devices reached through an already-authenticated Teleport
        tunnel, not internet-facing hosts.
        """
        cmd = [
            "sshpass", "-p", self._password,
            "ssh",
            "-o", "StrictHostKeyChecking=no",
            "-o", f"ConnectTimeout={self._timeout}",
            f"{self._username}@{self.host}",
            remote_command,
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=self._timeout + 5)
        if result.returncode != 0:
            raise RuntimeError(f"SSH command failed (exit {result.returncode}): {remote_command!r} -> {result.stderr.strip()}")
        return result.stdout

    def login(self) -> None:
        """No separate login step — SSH auth happens per-command. Runs one cheap command up front so a bad password/host fails fast and
        loud here, not silently inside the first real getter."""
        self._run("true")

    def logout(self) -> None:
        """No-op: nothing to close. Each _run() is its own short-lived SSH session, same as every other command this adapter runs."""

    def get_facts(self) -> dict:
        """NAPALM-style get_facts, built from real shell commands confirmed live 2026-09-17 (not a vendor "show" command — this product
        line has none): `uname -a` for kernel/hostname/arch, `cat /proc/cpuinfo` for the SoC, and `ifconfig br0`/`ifconfig wan1` for the
        LAN and WAN MAC addresses (confirmed on real units to differ by exactly one — WAN is LAN+1 — the WAN MAC is what shows up in a
        site's ARP table, not the LAN one; see cambium-swap evidence E112/E113 for the addressing bug this distinction resolved)."""
        uname = self._run("uname -a").strip()
        cpu_line = next(
            (line for line in self._run("cat /proc/cpuinfo 2>/dev/null").splitlines() if "system type" in line.lower()),
            "",
        )
        # `ifconfig <name>` exits non-zero when that interface doesn't exist on this unit's config — confirmed live 2026-09-17 that not
        # every real R195P has a standalone `wan1` link (some firmware/config variants only expose it as a VLAN sub-interface, e.g.
        # `wan1.500`). Treat that as a real "unknown", not a fatal error — br0/LAN should always exist, but tolerate its absence too.
        lan_mac = self._try_get_mac("ifconfig br0 2>/dev/null")
        wan_mac = self._try_get_mac("ifconfig wan1 2>/dev/null")

        parts = uname.split()
        hostname = parts[1] if len(parts) > 1 else None
        kernel_version = parts[2] if len(parts) > 2 else None

        return {
            "vendor": "Cambium Networks",
            "model": "R195P",
            "hostname": hostname,
            "kernel_version": kernel_version,
            "soc": cpu_line.split(":", 1)[-1].strip() if cpu_line else None,
            "lan_mac_address": lan_mac,
            "wan_mac_address": wan_mac,
            "raw_uname": uname,
        }

    def get_interfaces(self) -> dict:
        """Per-interface addressing from `ip addr show` — confirmed live to enumerate a large real set on this family (bridge, VLANs,
        wifi radios, WDS, AP-client interfaces; see cambium-swap evidence E118 for the full live list on one unit). Only
        name/state/MAC/IPv4 are parsed here; deeper per-radio stats are not exposed this way on this product line.

        This BusyBox's `ip -o` is not standard iproute2 output: a line with no address to report is the LINK line itself (index, name,
        `<FLAGS>`, `link/ether <mac>`), interleaved with real `... inet <addr> ...` lines for the same interface — confirmed live
        2026-09-17 (a naive parser that assumed one consistent line shape per interface produced duplicate `<name>` and `<name>:` keys
        for the same real interface). Regex-matched instead of split-by-field-position to tolerate that."""
        output = self._run("ip -o addr show 2>&1")
        interfaces: dict[str, dict] = {}
        for line in output.splitlines():
            header = re.match(r"^\d+:\s+([^\s:@]+)", line)
            if not header:
                continue
            name = header.group(1)
            entry = interfaces.setdefault(name, {"ipv4_addresses": []})

            flags = re.search(r"<([A-Z,]+)>", line)
            if flags:
                entry["is_up"] = "UP" in flags.group(1).split(",")

            mac = re.search(r"link/ether\s+([0-9a-fA-F:]{17})", line)
            if mac:
                entry["mac_address"] = mac.group(1).lower()

            addr = re.search(r"\binet\s+(\d+\.\d+\.\d+\.\d+/\d+)", line)
            if addr:
                entry["ipv4_addresses"].append(addr.group(1))
        return interfaces

    def _try_get_mac(self, remote_command: str) -> str | None:
        """Runs remote_command (expected to be an `ifconfig <name>` invocation) and extracts a MAC address from its output, returning
        None if the command fails (e.g. that interface doesn't exist on this unit) rather than raising."""
        try:
            return self._extract_mac(self._run(remote_command))
        except RuntimeError:
            return None

    @staticmethod
    def _extract_mac(text: str) -> str | None:
        for token in text.replace(":", " ").split():
            candidate = token
            if len(candidate) == 12 and all(c in "0123456789abcdefABCDEF" for c in candidate):
                return ":".join(candidate[i:i + 2] for i in range(0, 12, 2)).lower()
        # Fall back to scanning colon-separated tokens directly (ifconfig/ip both print MACs this way).
        for line in text.splitlines():
            for token in line.split():
                if token.count(":") == 5 and len(token) == 17:
                    return token.lower()
        return None


def _cmd_getters(adapter: CambiumR195PAdapter) -> int:
    adapter.login()
    try:
        result = {
            "facts": adapter.get_facts(),
            "interfaces": adapter.get_interfaces(),
        }
        print(json.dumps(result, indent=2))
    finally:
        adapter.logout()
    return 0


def main() -> int:
    host = os.environ.get("CAMBIUM_HOST")
    username = os.environ.get("CAMBIUM_USER")
    password = os.environ.get("CAMBIUM_PASS")
    if not (host and username and password):
        print("Set CAMBIUM_HOST, CAMBIUM_USER, CAMBIUM_PASS (never hardcode the password).", file=sys.stderr)
        return 2

    adapter = CambiumR195PAdapter(host, username, password)
    return _cmd_getters(adapter)


if __name__ == "__main__":
    raise SystemExit(main())
