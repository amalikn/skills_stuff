#!/usr/bin/env python3
"""Minimal Cambium ePMP (ePMP AP / ePMP SM, LuCI-derived firmware) REST adapter.

Same shape and rationale as cambium_xv2_adapter.py in this directory, for the ePMP family instead of Enterprise Wi-Fi. Stdlib-only Python,
no schema, no code generation.

Auth flow and RPC mechanics (reverse-engineered live 2026-09-17 from the device's own served JS, cambium.<hash>.js — nowhere documented in
the vendor CLI/user guides, which predate this API surface or simply don't cover it): the web UI is a LuCI-derived stack (confirmed by the
literal LuCI 404 page at unregistered paths). Login is `POST /cgi-bin/luci` (no stok yet) with form-urlencoded `username`/`password`;
success returns JSON `{"stok": "...", "userRole": "...", ...}` plus a `Set-Cookie: sysauth_<host>=<value>`. Every authenticated call after
that needs **both** the `stok` in the URL path AND the `sysauth_<host>` cookie — `POST /cgi-bin/luci/;stok=<stok>/admin/<method>`. A bare
POST with no body 411s ("Length Required"); always send an explicit (even empty) urlencoded body. Auth failure returns **HTTP 200** with
`{"msg":"auth_failed","success":0}` in the body — never trust the status code alone, check `success`.

The one RPC method this adapter actually uses is `get_param` with a form field `act=<section>`: `act=status` returns live telemetry
(identity, interfaces, wireless link/STA table) under a top-level `device_props` dict; `act=config_regular` returns the full device config
(~800 keys) under the same shape — **loaded with real credential-shaped values** (SNMP community strings, RADIUS password, wireless
encryption key all confirmed live and non-empty on a real device) — see REDACT_KEY_PATTERN below and the Known Issues doc before ever
touching this method again. Other real `act=*`/`ajax()` method names exist (`get_log`, `get_chart`, `link_test`, `traceroute`, `set_param`,
`reboot`, `reset_to_def`, ...) but are not wrapped here — see the module docstring's sibling doc, references/06_device-api-cli-reference.md,
for the full enumerated list found in the JS. Never call a write/destructive method (`set_param`, `reboot`, `reset_to_def`,
`disconnect_sta`, `ap_list_flush`, ...) against a production device without explicit operator authorization, same rule as XV2.

Confirmed live 2026-09-17 in an **AP** role too, not just SM (Force 300-16 at Kalumburu, cambium-swap evidence E118) — same `get_param`/
`act=status` shape, but that specific unit needed the `epmp-ap-legacy` vault credential, not the primary `epmp-ap` one.

Usage:
    CAMBIUM_HOST=localhost:20045 CAMBIUM_USER=admin CAMBIUM_PASS='...' python3 cambium_epmp_adapter.py

Never hardcode or print CAMBIUM_PASS — pull it from the KeePassXC vault (`kp show -s -a Password cambium-devices/epmp-sm` or
`cambium-devices/epmp-ap`) into an env var at the call site.

SECRET-EXPOSURE INCIDENT (2026-09-17): while manually checking whether `act=config_regular`'s credential-shaped keys held real values (as
opposed to guessing this adapter's design from field names alone), the check printed the actual values to a transcript — the same mistake
the XV2 incident this pattern already exists to prevent, just made again ad hoc before this file existed. REDACT_KEY_PATTERN and redact()
below are copied verbatim from cambium_xv2_adapter.py specifically so this never has to be reinvented ad hoc again. Checking "does this
field have a value" must only ever use bool()/len() on the value, never print or log it.
"""

from __future__ import annotations

import argparse
import http.cookiejar
import json
import os
import re
import ssl
import sys
import urllib.error
import urllib.parse
import urllib.request

REDACT_KEY_PATTERN = re.compile(
    r"pass|psk|secret|key|shared|community|radius|credential|token|auth",
    re.IGNORECASE,
)


def redact(obj):
    """Recursively replace any dict value whose key looks credential-shaped with a placeholder."""
    if isinstance(obj, dict):
        return {
            k: "<REDACTED>" if REDACT_KEY_PATTERN.search(k) else redact(v)
            for k, v in obj.items()
        }
    if isinstance(obj, list):
        return [redact(x) for x in obj]
    return obj


class CambiumEPMPAdapter:
    """Talks to one ePMP AP or ePMP SM's local LuCI-derived JSON API over HTTPS."""

    def __init__(self, host: str, username: str, password: str, verify_tls: bool = False) -> None:
        self.base_url = f"https://{host}"
        self._username = username
        self._password = password
        self._stok: str | None = None

        ctx = ssl.create_default_context()
        if not verify_tls:
            # Device presents a self-signed cert on its management interface — expected here, not a security bypass for anything
            # internet-facing.
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE

        self._cookiejar = http.cookiejar.CookieJar()
        self._opener = urllib.request.build_opener(
            urllib.request.HTTPCookieProcessor(self._cookiejar),
            urllib.request.HTTPSHandler(context=ctx),
        )

    def _post(self, path: str, form: dict | None = None) -> dict:
        url = f"{self.base_url}{path}"
        body = urllib.parse.urlencode(form or {}).encode("utf-8")
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        req = urllib.request.Request(url, data=body, headers=headers, method="POST")
        try:
            with self._opener.open(req, timeout=10) as resp:
                raw = resp.read().decode("utf-8")
        except urllib.error.HTTPError as exc:
            raise RuntimeError(f"POST {path} -> HTTP {exc.code}: {exc.read().decode('utf-8', 'replace')}") from exc
        return json.loads(raw) if raw else {}

    def login(self) -> None:
        result = self._post("/cgi-bin/luci", {"username": self._username, "password": self._password})
        stok = result.get("stok")
        if not stok:
            raise RuntimeError(f"Cambium ePMP login failed: {result}")
        self._stok = stok

    def logout(self) -> None:
        if self._stok:
            self._post(f"/cgi-bin/luci/;stok={self._stok}/admin/logout")
        self._stok = None

    def get_raw_param(self, act: str) -> dict:
        """Public escape hatch: raw (unredacted) get_param response for a given `act` section.

        Callers that might print, log, or persist this must redact() it themselves first — see the module docstring's incident note.
        `act=status` is safe (telemetry only, confirmed no credential-shaped keys); `act=config_regular` is NOT (confirmed real secrets
        present).
        """
        if not self._stok:
            raise RuntimeError("login() first")
        return self._post(f"/cgi-bin/luci/;stok={self._stok}/admin/get_param", {"act": act})

    def get_facts(self) -> dict:
        """NAPALM-style get_facts: device identity, firmware, uptime, cnMaestro connection state."""
        props = self.get_raw_param("status").get("device_props", {})
        return {
            "vendor": "Cambium Networks",
            "hostname": props.get("cambiumEffectiveDeviceName"),
            "serial_number": props.get("cambiumEPMPMSN"),
            "os_version": props.get("cambiumCurrentuImageVersion"),
            "uptime": props.get("cambiumSystemUptime"),
            "mac_address": props.get("cambiumWirelessMACAddress") or props.get("cambiumLANMACAddress"),
            "cnmaestro_status": props.get("cambiumCnsServConsStat"),
        }

    def get_interfaces(self) -> dict:
        """LAN (Ethernet) port state. ePMP has one LAN port (two on some AP models, LAN2 fields exist but read 0/unused on the units
        tested)."""
        props = self.get_raw_param("status").get("device_props", {})
        return {
            "LAN": {
                "is_up": bool(props.get("cambiumLANStatus")),
                "speed_mbps": props.get("cambiumLANSpeedStatus"),
                "duplex_full": bool(props.get("cambiumLANModeStatus")),
                "mac_address": props.get("cambiumLANMACAddress"),
            },
            "LAN2": {
                "is_up": bool(props.get("cambiumLAN2Status")),
                "speed_mbps": props.get("cambiumLAN2SpeedStatus"),
                "duplex_full": bool(props.get("cambiumLAN2ModeStatus")),
            },
        }

    def get_wireless_link(self) -> dict | None:
        """SM-side only: this unit's single uplink to its paired AP (RSSI/SNR/distance/frequency). Returns None on an AP (which has no
        single uplink — see get_clients() instead).

        Real bug found and fixed live 2026-09-17: `cambiumSTADLRSSI` exists (=0) on an AP too, so its mere presence isn't a valid SM-vs-AP
        discriminator — an AP was returning a bogus zeroed-out link dict instead of None. `cambiumConnectedAPMACAddress` is the real
        signal: a SM reports a real MAC; an AP reports the literal string "Not Associated"."""
        props = self.get_raw_param("status").get("device_props", {})
        connected_ap_mac = props.get("cambiumConnectedAPMACAddress")
        if not connected_ap_mac or connected_ap_mac == "Not Associated":
            return None
        return {
            "connected_ap_mac": props.get("cambiumConnectedAPMACAddress"),
            "frequency_mhz": props.get("cambiumSTAConnectedRFFrequency"),
            "downlink_rssi": props.get("cambiumSTADLRSSI"),
            "downlink_snr": props.get("cambiumSTADLSNR"),
            "distance_km": props.get("cambiumSTADistanceKm"),
        }

    def get_clients(self) -> list:
        """AP-side only: every currently-associated SM, with per-station RF telemetry. Empty list on an SM (which has no stations of its
        own)."""
        props = self.get_raw_param("status").get("device_props", {})
        table = props.get("cambiumAPConnectedSTATable")
        if not table:
            return []
        return [
            {
                "hostname": sta.get("connectedClickTHostName"),
                "mac_address": sta.get("connectedSTAMAC"),
                "ip_address": sta.get("connectedSTAIP"),
                "software_version": sta.get("connectedSTASoftwareVersion"),
                "model_name": sta.get("connectedSTAModelName"),
                "downlink_rssi": sta.get("connectedSTADLRSSI"),
                "downlink_snr": sta.get("connectedSTADLSNR"),
                "uplink_rssi": sta.get("connectedSTAULRSSI"),
                "uplink_snr": sta.get("connectedSTAULSNR"),
                "distance_m": sta.get("connectedSTADistance"),
                "session_time": sta.get("connectedSTASessionTime"),
            }
            for sta in table
        ]

    def get_config(self) -> dict:
        """Config snapshot for backup/diff. REDACTS every credential-shaped field via REDACT_KEY_PATTERN before returning — confirmed
        necessary live, this section carries real SNMP community strings, a RADIUS password, and a wireless encryption key in plaintext
        from the device. Callers must never bypass this by calling get_raw_param('config_regular') directly without also redacting."""
        props = self.get_raw_param("config_regular").get("device_props", {})
        return redact(props)


def _cmd_getters(adapter: CambiumEPMPAdapter) -> int:
    adapter.login()
    try:
        result = {
            "facts": adapter.get_facts(),
            "interfaces": adapter.get_interfaces(),
            "wireless_link": adapter.get_wireless_link(),
            "clients": adapter.get_clients(),
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
        help="also fetch and print the redacted config_regular snapshot (get_config)",
    )
    args = parser.parse_args()

    host = os.environ.get("CAMBIUM_HOST")
    username = os.environ.get("CAMBIUM_USER")
    password = os.environ.get("CAMBIUM_PASS")
    if not (host and username and password):
        print("Set CAMBIUM_HOST, CAMBIUM_USER, CAMBIUM_PASS (never hardcode the password).", file=sys.stderr)
        return 2

    adapter = CambiumEPMPAdapter(host, username, password)

    if args.include_config:
        adapter.login()
        try:
            print(json.dumps(adapter.get_config(), indent=2))
        finally:
            adapter.logout()
        return 0

    return _cmd_getters(adapter)


if __name__ == "__main__":
    raise SystemExit(main())
