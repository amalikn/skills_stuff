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
cambium-swap evidence E113/E114/E118. Deliberately did NOT run `cat /etc/config/*` or any full-config dump that session (this family's SNMP
Get/Set community strings are known to be configured fleet-wide per the Ansible R195P provisioning template — encrypted there, but real —
and this project has two prior secret-exposure incidents on other families from exactly this kind of unscoped dump).

get_config() ADDED 2026-09-18 under explicit operator authorization to fetch a live snapshot across all 4 Cambium device families in one
session (cambium-swap evidence E134-series) — the condition this docstring originally asked for ("a real need... never as a blind default")
is now met. It wraps the exact `cat /etc/config/* 2>&1` dump this docstring spent a year deliberately avoiding, but never returns it
unredacted: the raw UCI-style text is parsed into a nested dict and passed through the same REDACT_KEY_PATTERN/redact() shape used verbatim
by cambium_xv2_adapter.py/cambium_epmp_adapter.py/cambium_cnwave_adapter.py, keyed by option name so the fleet-wide SNMP community (an
encrypted blob in this family's own config, not necessarily plaintext-looking) is redacted by key name regardless of whether the value looks
like ciphertext — same rule the other three adapters already apply. Opt-in only, via `--include-config` (same flag name/shape as
cambium_epmp_adapter.py), never part of the default `_cmd_getters()` output.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys

REDACT_KEY_PATTERN = re.compile(
    r"pass|psk|secret|key|shared|community|radius|credential|token|auth",
    re.IGNORECASE,
)


def redact(obj):
    """Recursively replace any dict value whose key looks credential-shaped with a placeholder.

    Copied verbatim from cambium_xv2_adapter.py / cambium_epmp_adapter.py / cambium_cnwave_adapter.py in this directory — deliberately not
    re-derived, per this project's standing rule after two prior secret-exposure incidents on other families.
    """
    if isinstance(obj, dict):
        return {
            k: "<REDACTED>" if REDACT_KEY_PATTERN.search(k) else redact(v)
            for k, v in obj.items()
        }
    if isinstance(obj, list):
        return [redact(x) for x in obj]
    return obj


DEFAULT_SSH_TIMEOUT = 20
# Was 8 (fine for the direct-tunnel path this constant was originally tested against, 2026-09-17).
# Live-tested 2026-09-18 through a nested Teleport --proxy= tunnel to a device reachable only via a
# site's SMC box: the device's own sshd (dropbear) answers its banner instantly (confirmed with a
# raw socket probe), but the fuller key-exchange + password-auth round trip over that extra hop
# exceeded the old 8s ConnectTimeout and raised subprocess.TimeoutExpired. Bumped to 20s rather than
# reverting the nested-tunnel access path, since that path is this family's documented normal case.


class CambiumR195PAdapter:
    """Talks to one cnPilot R195P's real BusyBox/Buildroot shell over SSH, via the system ssh/sshpass binaries."""

    def __init__(self, host: str, username: str, password: str, timeout: int = DEFAULT_SSH_TIMEOUT) -> None:
        # Accept "host:port" the same way CAMBIUM_HOST is already written for the other 3 (HTTPS)
        # adapters in this directory, e.g. "localhost:20004" for a local Teleport port-forward —
        # this family's own module docstring says the normal access path IS a tsh tunnel through
        # the site's SMC box, so a bare `ssh user@host:port` (which ssh parses as a literal,
        # unresolvable hostname) was a real bug on the documented default path, not an edge case.
        if ":" in host:
            hostname, _, port_str = host.rpartition(":")
            if port_str.isdigit():
                self.host = hostname
                self._port: str | None = port_str
            else:
                self.host = host
                self._port = None
        else:
            self.host = host
            self._port = None
        self._username = username
        self._password = password
        self._timeout = timeout

    def _run(self, remote_command: str, allow_nonzero: bool = False) -> str:
        """Run one remote shell command over SSH and return its stdout, raising on a non-zero exit or a timeout.

        Uses `sshpass -p <password> ssh ...` — the same pattern this project's own live sessions used by hand. `StrictHostKeyChecking=no`
        matches those sessions too: these are internal management-network devices reached through an already-authenticated Teleport
        tunnel, not internet-facing hosts.

        `allow_nonzero` (added 2026-09-18, first live get_config() run): `get_config()`'s own `cat /etc/config/* 2>&1` deliberately merges
        BusyBox `cat`'s stderr into the captured stdout stream so a missing config file shows up as parseable text under `_unparsed`
        rather than being lost — see that method's and `_parse_uci_text()`'s docstrings. But BusyBox `cat` exits non-zero as soon as ANY
        one of several glob-matched files fails to open, even though the useful output for every other file is still on stdout. The
        default strict behaviour below raised on that non-zero exit and discarded the merged stdout entirely, silently defeating the
        `2>&1` design intent — confirmed live against a real Burringurrah unit (not every `/etc/config/*` type exists on every unit, so
        this is the common case here, not a rare edge case). Only `get_config()` opts into tolerating this.
        """
        cmd = [
            "sshpass", "-p", self._password,
            "ssh",
            "-o", "StrictHostKeyChecking=no",
            "-o", f"ConnectTimeout={self._timeout}",
            # LogLevel=ERROR added 2026-09-18: the local OpenSSH client's own "not using a
            # post-quantum key exchange" advisory banner is written before the password prompt and
            # was observed live to desync sshpass's naive prompt-pattern matching (three
            # ssh_askpass fallback attempts, then a real "Permission denied" against a password that
            # is in fact correct) — silencing client-side advisory/warning banners avoids the
            # desync without changing auth behaviour.
            "-o", "LogLevel=ERROR",
        ]
        if self._port:
            cmd += ["-p", self._port]
        cmd += [
            f"{self._username}@{self.host}",
            remote_command,
        ]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=self._timeout + 5)
        except subprocess.TimeoutExpired as exc:
            # SECRET-EXPOSURE INCIDENT (2026-09-18, live R195P test): subprocess.TimeoutExpired's
            # default __str__/repr embeds the FULL argv it was given, including the `sshpass -p
            # <password>` pair above — an uncaught instance of this exception prints the real
            # device password to whatever captures the traceback (a terminal transcript, a log
            # file). Never let this exception surface with its default message; re-raise sanitized,
            # same discipline as the REDACT_KEY_PATTERN rule elsewhere in this project after two
            # prior incidents of this same class (E107 and the 2026-09-17 ePMP incident).
            raise RuntimeError(f"SSH command timed out after {exc.timeout}s: {remote_command!r}") from None
        if result.returncode != 0 and not allow_nonzero:
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

    def get_config(self) -> dict:
        """Config snapshot for backup/diff — see the module docstring's 2026-09-18 note for why this was deliberately unbuilt until now
        and what changed. Source: `cat /etc/config/* 2>&1` over the same SSH path every other getter here uses (BusyBox has no `uci`
        binary confirmed on this platform — see 03_asset-register-conventions.md — so this reads the UCI-style config files directly
        rather than shelling a config tool that may not exist). Parses the raw UCI text into a nested dict and REDACTS every
        credential-shaped option via REDACT_KEY_PATTERN before returning — callers must never call `_run("cat /etc/config/*")` directly
        and print/log/persist the result themselves, same rule as every other family's get_config()."""
        raw = self._run("cat /etc/config/* 2>&1", allow_nonzero=True)
        return redact(self._parse_uci_text(raw))

    @staticmethod
    def _parse_uci_text(text: str) -> dict:
        """Best-effort parse of BusyBox/OpenWrt-style UCI config text into a nested dict keyed by `"<type>.<name>"` per `config` stanza,
        each holding its `option`/`list` key-value pairs. Never confirmed live before this method (no prior session ran the underlying
        dump), so this tolerates any line shape gracefully rather than assuming one: an unrecognized line (a different config-file
        syntax entirely, or `cat`'s own "No such file" stderr text mixed into the same 2>&1 stream) is kept verbatim under a synthetic
        `_unparsed` key instead of being silently dropped, so redact() still gets a chance to scrub anything credential-shaped in it and
        a caller can see the raw text was there rather than getting a falsely-empty result."""
        sections: dict = {}
        current: dict | None = None
        for line in text.splitlines():
            stripped = line.strip()
            if not stripped:
                continue

            config_match = re.match(r"^config\s+(\S+)(?:\s+'([^']*)'|\s+\"([^\"]*)\"|\s+(\S+))?", stripped)
            if config_match:
                kind = config_match.group(1)
                name = config_match.group(2) or config_match.group(3) or config_match.group(4) or f"section{len(sections)}"
                current = {}
                sections[f"{kind}.{name}"] = current
                continue

            option_match = re.match(r"^(option|list)\s+(\S+)\s+(?:'([^']*)'|\"([^\"]*)\"|(\S+))", stripped)
            if option_match and current is not None:
                key = option_match.group(2)
                value = option_match.group(3)
                if value is None:
                    value = option_match.group(4)
                if value is None:
                    value = option_match.group(5)
                if option_match.group(1) == "list":
                    existing = current.get(key)
                    if not isinstance(existing, list):
                        existing = [] if existing is None else [existing]
                    existing.append(value)
                    current[key] = existing
                else:
                    current[key] = value
                continue

            sections.setdefault("_unparsed", [])
            sections["_unparsed"].append(stripped)
        return sections


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
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "--include-config",
        action="store_true",
        help="also fetch and print the redacted /etc/config/* snapshot (get_config) alongside facts/interfaces",
    )
    args = parser.parse_args()

    host = os.environ.get("CAMBIUM_HOST")
    username = os.environ.get("CAMBIUM_USER")
    password = os.environ.get("CAMBIUM_PASS")
    if not (host and username and password):
        print("Set CAMBIUM_HOST, CAMBIUM_USER, CAMBIUM_PASS (never hardcode the password).", file=sys.stderr)
        return 2

    adapter = CambiumR195PAdapter(host, username, password)

    if args.include_config:
        adapter.login()
        try:
            result = {
                "facts": adapter.get_facts(),
                "interfaces": adapter.get_interfaces(),
                "config": adapter.get_config(),
            }
            print(json.dumps(result, indent=2))
        finally:
            adapter.logout()
        return 0

    return _cmd_getters(adapter)


if __name__ == "__main__":
    raise SystemExit(main())
