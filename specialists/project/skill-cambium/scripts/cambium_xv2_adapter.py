#!/usr/bin/env python3
"""Minimal Cambium Enterprise Wi-Fi (XV2/Falcon UI) REST adapter.

Implements the vendor-adapter getters from the Option 3 controller architecture (see cambium-swap's docs/migration/controller-option3/
option-3-architecture.md and docs/migration/controller-option3/cambium-vendor-adapter-data-points.md) using nothing but the Python standard
library: no requests, no schema, no code generation.

This exists to answer a real question rather than settle it by opinion: does a Cambium adapter need a formal CLI/API grammar
(command-schema.json, OpenAPI generation, Tree-sitter/ANTLR, an AI extraction pipeline) before it can be written? Answer, confirmed live
against a real Hope Vale device 2026-09-17: no. See skill-walk-before-run's ledger.jsonl for the RESOLVED entry this test closes.

Auth flow (reverse-engineered from the device's own served JS, not guessed — see references/02_device-access-and-vault.md): POST /api/login
with a JSON body, then every following call needs both the session cookies AND an X-XSRF-TOKEN header echoing the XSRF-TOKEN cookie value.

This adapter also covers the older Enterprise Wi-Fi E-series (E500, E430) — confirmed live 2026-09-17 (cambium-swap evidence E118): same
Falcon-family REST API and CLI, no separate adapter needed. See references/06_device-api-cli-reference.md's "Enterprise Wi-Fi E-series"
section for the specific units and firmware confirmed.

Usage:
    # Run the implemented getters, print JSON to stdout:
    CAMBIUM_HOST=localhost:10001 CAMBIUM_USER=admin CAMBIUM_PASS='...' python3 cambium_xv2_adapter.py

    # Explore arbitrary raw endpoints (writes one redacted JSON file per endpoint to a dir, never
    # prints raw content to stdout/stderr — see REDACT_KEY_PATTERN before trusting an unfamiliar
    # endpoint's output):
    CAMBIUM_HOST=... CAMBIUM_USER=... CAMBIUM_PASS=... python3 cambium_xv2_adapter.py \
        --dump radio-summary,wlan-summary,events --dump-dir /tmp/xv2-dump

Never hardcode or print CAMBIUM_PASS — pull it from the KeePassXC vault (`kp show -s -a Password cambium-devices/enterprise-wifi`) into an
env var at the call site, per skill-cambium's own device-access rule.

SECRET-EXPOSURE INCIDENT (2026-09-17): an early exploration pass printed /api/system-config's snmp_read_community/snmp_write_community
values to a terminal transcript because the ad hoc redaction used that session only matched pass/psk/secret/key/shared — not "community".
REDACT_KEY_PATTERN below is the single, deliberately broad, hard-coded fix: every dict key matching it is redacted everywhere this module
ever returns or writes device data, in get_config() and in --dump. Widen it, never narrow it, if another vendor field name is found to
carry a real secret.
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


class CambiumXV2Adapter:
    """Talks to one Enterprise Wi-Fi XV2/XE-family AP's local REST API over HTTPS."""

    def __init__(self, host: str, username: str, password: str, verify_tls: bool = False) -> None:
        self.base_url = f"https://{host}"
        self._username = username
        self._password = password
        self._xsrf_token: str | None = None

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

    def _request(self, method: str, path: str, body: dict | None = None):
        url = f"{self.base_url}{path}"
        data = json.dumps(body).encode("utf-8") if body is not None else None
        headers = {"Content-Type": "application/json"} if data is not None else {}
        if self._xsrf_token:
            headers["X-XSRF-TOKEN"] = self._xsrf_token

        req = urllib.request.Request(url, data=data, headers=headers, method=method)
        try:
            with self._opener.open(req, timeout=10) as resp:
                raw = resp.read().decode("utf-8")
        except urllib.error.HTTPError as exc:
            raise RuntimeError(f"{method} {path} -> HTTP {exc.code}: {exc.read().decode('utf-8', 'replace')}") from exc

        for cookie in self._cookiejar:
            if cookie.name == "XSRF-TOKEN":
                self._xsrf_token = cookie.value

        return json.loads(raw) if raw else {}

    def get_raw(self, endpoint: str):
        """Public escape hatch for exploring an endpoint not yet wrapped by a getter below.

        Returns the RAW (unredacted) response — callers that might print, log, or write this to
        disk must redact() it themselves first. Used by --dump, which does exactly that.
        """
        path = endpoint if endpoint.startswith("/api/") else f"/api/{endpoint}"
        return self._request("GET", path)

    def login(self) -> None:
        result = self._request("POST", "/api/login", {"username": self._username, "password": self._password})
        if not result.get("success"):
            raise RuntimeError(f"Cambium login failed: {result}")

    def logout(self) -> None:
        self._request("POST", "/api/logout")

    def get_facts(self) -> dict:
        """NAPALM-style get_facts: device identity, firmware, uptime, cnMaestro connection state."""
        platform = self._request("GET", "/api/platform-info")
        summary = self._request("GET", "/api/device-summary")
        return {
            "vendor": "Cambium Networks",
            "model": platform.get("model") or summary.get("model"),
            "hostname": summary.get("hostname"),
            "serial_number": summary.get("serial_number"),
            "os_version": summary.get("version"),
            "uptime_seconds": summary.get("uptime"),
            "mac_address": summary.get("device_mac"),
            "cnmaestro_status": summary.get("cns_status"),
        }

    def get_interfaces(self) -> dict:
        """NAPALM-style get_interfaces: per-port link state and counters.

        device-summary carries link/speed/duplex in TWO places that disagree: `port_stats[].link` is not reliable (observed "DOWN" on
        Tower 1's ETH1 while it was physically up and passing traffic — confirmed live 2026-09-17), while `port_status[].link` (a separate
        array, integer 1/0) matched reality. Use port_status as authoritative for link/speed/duplex; port_stats for counters only.
        """
        summary = self._request("GET", "/api/device-summary")

        status_by_port = {
            p["device"]: p for p in summary.get("port_status", []) if p.get("device")
        }

        interfaces = {}
        for port in summary.get("port_stats", []):
            name = port.get("device")
            if not name:
                continue
            status = status_by_port.get(name, {})
            interfaces[name] = {
                "is_up": bool(status.get("link", 0)),
                "speed": status.get("speed", port.get("speed")),
                "duplex": "FULL" if status.get("duplex") == 1 else ("HALF" if status.get("duplex") == 0 else port.get("duplex")),
                "rx_bytes": port.get("rx_bytes"),
                "tx_bytes": port.get("tx_bytes"),
                "rx_errors": port.get("rx_errs"),
                "tx_errors": port.get("tx_errs"),
            }
        return interfaces

    def get_radios(self) -> dict:
        """Per-radio operational state, channel/power, and utilization — merges radio-summary (state, channel, power, client/traffic
        counters) with radio-rf-summary (channel utilization, noise floor), by list position (both are ordered by radio index; neither
        response carries a shared join key — confirmed by inspecting both live 2026-09-17)."""
        summary = self._request("GET", "/api/radio-summary") or []
        rf = self._request("GET", "/api/radio-rf-summary") or []

        radios = {}
        for i, radio in enumerate(summary):
            device_id = radio.get("device", i)
            rf_stats = rf[i] if i < len(rf) else {}
            radios[device_id] = {
                "band": radio.get("band"),
                "mac": radio.get("mac"),
                "state": radio.get("radio_state"),
                "channel": radio.get("channel"),
                "channel_width": radio.get("channel-width"),
                "power": radio.get("power"),
                "num_clients": radio.get("num_clients"),
                "num_wlans": radio.get("num_wlans"),
                "utilization_pct": rf_stats.get("total_cu"),
                "noise_floor": rf_stats.get("nf"),
                "packet_error_rate": rf_stats.get("per"),
            }
        return radios

    def get_wlans(self) -> dict:
        """SSID/WLAN definitions and stats — merges wlan-summary (security, VLAN, traffic counters) with wlan-interface-summary (per-band
        BSSID/link status), joined on SSID name. (/api/wlan-config 500'd on this firmware when queried with no params — not used; wlan
        definitions come from wlan-summary instead, which is sufficient for read/monitoring use.)
        """
        summary = self._request("GET", "/api/wlan-summary") or []
        interfaces = self._request("GET", "/api/wlan-interface-summary") or []

        by_ssid: dict[str, dict] = {}
        for wlan in summary:
            ssid = wlan.get("ssid")
            if not ssid:
                continue
            by_ssid[ssid] = {
                "security": wlan.get("security"),
                "vlan": wlan.get("vlan"),
                "guest_access": wlan.get("guest_access"),
                "num_clients": wlan.get("num_clients"),
                "tx_bytes": wlan.get("tx_bytes"),
                "rx_bytes": wlan.get("rx_bytes"),
                "bands": [],
            }
        for iface in interfaces:
            ssid = iface.get("ssid")
            if ssid not in by_ssid:
                continue
            by_ssid[ssid]["bands"].append({
                "band": iface.get("band"),
                "bssid": iface.get("bssid"),
                "status": iface.get("status"),
                "clients": iface.get("clients"),
            })
        return by_ssid

    # `ip6_ll` is the one field whose JSON *type* differs by model, so it is normalised here rather
    # than left for every consumer to special-case. Fleet sweep 2026-09-20: array on XV2 (10 of 32
    # record-bearing observations), string on E500 (6), absent where the client has no link-local
    # address (17). A list is the lossless target — wrapping the E500 string and mapping absent to
    # empty keeps every value, whereas normalising to a string would silently truncate any XV2
    # client holding more than one address.
    #
    # Treat the result as identifying data. An IPv6 link-local address is EUI-64 derived, so it
    # encodes the client MAC: observed `fe80::6885:b9ff:feac:bb89` resolves exactly to MAC
    # `6A-85-B9-AC-BB-89`. Redact it on the same footing as `mac`, not as ordinary telemetry.
    IPV6_LL_FIELD = "ip6_ll"

    def get_clients(self) -> list:
        """Currently-associated wireless stations. Empty list is a real, valid state (observed live 2026-09-17 — no clients connected at
        query time), not a parsing failure.

        `ip6_ll` is normalised to a list on every record, including records where the device omitted it — see the note above the method
        for why a list is the lossless direction and why the value is identifying."""
        clients = self._request("GET", "/api/client-summary") or []
        for client in clients:
            if not isinstance(client, dict):
                continue
            value = client.get(self.IPV6_LL_FIELD)
            if isinstance(value, list):
                client[self.IPV6_LL_FIELD] = [v for v in value if v]
            elif value:
                client[self.IPV6_LL_FIELD] = [value]
            else:
                client[self.IPV6_LL_FIELD] = []
        return clients

    def get_config(self) -> dict:
        """Config snapshot for backup/diff — the read path this family needs since SNMP config is unsupported (evidence E34). REDACTS
        every credential-shaped field via REDACT_KEY_PATTERN before returning; callers must never bypass this by calling the underlying
        endpoints directly without also redacting (get_raw() intentionally does not redact — see its docstring)."""
        merged = {
            "system": self._request("GET", "/api/system-config"),
            "network": self._request("GET", "/api/network-config"),
            "vlan": self._request("GET", "/api/vlan-config"),
            "dhcp": self._request("GET", "/api/dhcp-config"),
            "firewall": self._request("GET", "/api/firewall-config"),
            "service": self._request("GET", "/api/service-config"),
        }
        return redact(merged)

    def get_events(self, limit: int = 100) -> list:
        """Local event log — most-recent-first strings, as the device returns them (already human-readable, e.g. "Sep 17 14:15:22
        WIFI-4-CLIENT-DISCONNECTED ..."). Capped at `limit` since the raw log observed live 2026-09-17 was 41KB / hundreds of entries."""
        events = self._request("GET", "/api/events") or []
        return events[:limit]


def _cmd_getters(adapter: CambiumXV2Adapter) -> int:
    adapter.login()
    try:
        result = {
            "facts": adapter.get_facts(),
            "interfaces": adapter.get_interfaces(),
            "radios": adapter.get_radios(),
            "wlans": adapter.get_wlans(),
            "clients": adapter.get_clients(),
            "config": adapter.get_config(),
            "events": adapter.get_events(limit=20),
        }
        print(json.dumps(result, indent=2))
    finally:
        adapter.logout()
    return 0


def _cmd_dump(adapter: CambiumXV2Adapter, endpoints: list[str], dump_dir: str) -> int:
    os.makedirs(dump_dir, exist_ok=True)
    adapter.login()
    try:
        for ep in endpoints:
            ep = ep.strip()
            if not ep:
                continue
            try:
                raw = adapter.get_raw(ep)
            except RuntimeError as exc:
                print(f"{ep}: ERROR — {exc}", file=sys.stderr)
                continue
            out_path = os.path.join(dump_dir, f"{ep.strip('/').replace('/', '_')}.json")
            with open(out_path, "w") as f:
                json.dump(redact(raw), f, indent=1)
            print(f"{ep}: wrote {out_path}", file=sys.stderr)
    finally:
        adapter.logout()
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--dump", help="comma-separated list of raw /api/<name> endpoints to fetch and save (redacted) instead of running the getters")
    parser.add_argument("--dump-dir", default="/tmp/cambium-xv2-dump", help="directory to write --dump output into (default: /tmp/cambium-xv2-dump)")
    args = parser.parse_args()

    host = os.environ.get("CAMBIUM_HOST")
    username = os.environ.get("CAMBIUM_USER")
    password = os.environ.get("CAMBIUM_PASS")
    if not (host and username and password):
        print("Set CAMBIUM_HOST, CAMBIUM_USER, CAMBIUM_PASS (never hardcode the password).", file=sys.stderr)
        return 2

    adapter = CambiumXV2Adapter(host, username, password)

    if args.dump:
        return _cmd_dump(adapter, args.dump.split(","), args.dump_dir)
    return _cmd_getters(adapter)


if __name__ == "__main__":
    raise SystemExit(main())
