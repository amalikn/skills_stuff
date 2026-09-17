#!/usr/bin/env python3
"""Minimal Cambium cnWave 60GHz (Terragraph-based) REST adapter.

Talks to a cnWave node's own local web UI backend — the same one the onboard "60 GHz cnWave" Angular SPA calls — not the SSH TUI. The SSH
TUI (E2E controller's interactive console) has no official documentation at all (checked the vendor's own 60 GHz cnWave User Guide, Release
1.8 — zero SSH/CLI/console mentions across 12,378 lines, see cambium-swap evidence E119) and no scriptable form was found; this REST API is
the real, vendor-sanctioned adapter path, same conclusion already reached for XV2 and ePMP.

Auth flow (reverse-engineered from the device's own served JS, main.<hash>.js — not guessed): POST /local/userLogin with a JSON body returns
{"success":true,"message":"<JWT>"}. Every following call sends "Authorization: Bearer <JWT>" — no cookies involved, unlike XV2.

Role matters here, confirmed live 2026-09-17 against two real Hope Vale nodes:
- A POP/E2E-role node (V5000, onboard E2E controller) answers get_topology/get_ctrl_status_dump with real network-wide data.
- A plain Client Node (V2000) answers every /local/* getter fine (it's still a real device with its own facts/config), but
  /local/getE2eInfo reports {"enabled": false, "available": true} and the /api/* endpoints (topology, controller status) return an EMPTY
  body — those are E2E-controller-only, not per-node. Check get_e2e_info().get("enabled") before trusting get_topology() or
  get_ctrl_status_dump() to return anything.

Several endpoints seen in the JS bundle return HTTP 400 with an empty body when called with `{}` (getRadioStats, getNetworkStats,
getKeyPerformanceIndex, getCnAgentStatus, and — inconsistently, only on some nodes — getGpsBrief) — they likely need parameters not yet
reverse-engineered (a radio MAC, a time range, ...). get_gps() below tolerates this and returns None rather than raising; the others are not
wrapped at all, treat as a known gap, not a bug in this adapter.

SNMP is documented (SNMPv2c RO/RW + SNMPv3, MIB TERRAGRAPH-RADIO-MIB) but never confirmed live — no community string is known. The R195P
Ansible template's SNMP Get/Set community values are encrypted blobs in the device's own config-encryption format, identical across every
site (one fleet-wide value) — not something to reverse-engineer, and not this device family's community string anyway. Do not guess vendor
default communities beyond a single harmless "public" try.

Usage:
    CAMBIUM_HOST=10.255.4.100 CAMBIUM_USER=admin CAMBIUM_PASS='...' python3 cambium_cnwave_adapter.py

Never hardcode or print CAMBIUM_PASS — pull it from the KeePassXC vault (`kp show -s -a Password cambium-devices/cnwave-60ghz`) into an env
var at the call site.
"""

from __future__ import annotations

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


class CambiumCnWaveAdapter:
    """Talks to one cnWave 60GHz node's local REST API over HTTPS (POP/E2E role or plain CN)."""

    def __init__(self, host: str, username: str, password: str, verify_tls: bool = False) -> None:
        self.base_url = f"https://{host}"
        self._username = username
        self._password = password
        self._token: str | None = None

        ctx = ssl.create_default_context()
        if not verify_tls:
            # Device presents a self-signed cert on its management interface — expected here, not a security bypass for anything
            # internet-facing.
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
        self._opener = urllib.request.build_opener(urllib.request.HTTPSHandler(context=ctx))

    def _request(self, path: str, body: dict | None = None):
        url = f"{self.base_url}{path}"
        data = json.dumps(body if body is not None else {}).encode("utf-8")
        headers = {"Content-Type": "application/json"}
        if self._token:
            headers["Authorization"] = f"Bearer {self._token}"

        req = urllib.request.Request(url, data=data, headers=headers, method="POST")
        try:
            with self._opener.open(req, timeout=10) as resp:
                raw = resp.read().decode("utf-8")
        except urllib.error.HTTPError as exc:
            raise RuntimeError(f"POST {path} -> HTTP {exc.code}: {exc.read().decode('utf-8', 'replace')}") from exc

        return json.loads(raw) if raw else {}

    def get_raw(self, endpoint: str):
        """Public escape hatch for exploring an endpoint not yet wrapped by a getter below.

        Returns the RAW (unredacted) response — callers that might print, log, or write this to disk must redact() it themselves first.
        """
        path = endpoint if endpoint.startswith("/") else f"/local/{endpoint}"
        return self._request(path)

    def login(self) -> None:
        result = self._request("/local/userLogin", {"username": self._username, "password": self._password})
        if not result.get("success"):
            raise RuntimeError(f"Cambium login failed: {result}")
        self._token = result["message"]

    def logout(self) -> None:
        self._request("/local/userLogout")

    def get_facts(self) -> dict:
        """NAPALM-style get_facts: device identity, firmware, uptime. `type` distinguishes role — "POP" for a node running the onboard E2E
        controller, "CN" for a plain Client Node."""
        info = self._request("/local/getDeviceInfo")
        return {
            "vendor": "Cambium Networks",
            "role": info.get("type"),
            "model": info.get("model"),
            "hostname": info.get("name"),
            "serial_number": info.get("msn"),
            "os_version": info.get("swVer"),
            "firmware_version": info.get("fwVersion", "").strip(),
            "uptime_seconds": info.get("uptime"),
            "mac_address": info.get("mac"),
            "ipv4_address": info.get("ipv4Address"),
        }

    def get_e2e_info(self) -> dict:
        """Whether THIS node runs the E2E controller. Check enabled=True before trusting get_topology()/get_ctrl_status_dump() to return
        network-wide data — on a plain Client Node those calls succeed but return an empty body (confirmed live 2026-09-17)."""
        return self._request("/local/getE2eInfo")

    def get_status(self) -> dict:
        """onboardStatus (is the E2E controller running on this box) and, if so, its own internal tcp:// URL."""
        return self._request("/local/getStatusInfo")

    def get_capability(self) -> dict:
        return self._request("/local/getSystemCapability")

    def get_links_count(self):
        return self._request("/local/getLinksCount")

    def get_gps(self):
        """Confirmed live to 400 with an empty body on at least one real node (no GPS fix, or a missing param this adapter doesn't send
        yet) — tolerate that specific failure and return None rather than raising, since it is a real, observed device response, not a
        bug in this client."""
        try:
            return self._request("/local/getGpsBrief")
        except RuntimeError as exc:
            if "HTTP 400" in str(exc):
                return None
            raise

    def get_topology(self) -> dict:
        """Full network topology (nodes, links, sites) — E2E-controller-only. Returns an empty dict on a plain Client Node; call
        get_e2e_info() first if that distinction matters."""
        return self._request("/api/getTopology")

    def get_ctrl_status_dump(self) -> dict:
        """Per-node status as seen by the E2E controller, including the underlying open-source Terragraph release string (cnWave is built
        on Meta's Terragraph platform) — E2E-controller-only, same caveat as get_topology()."""
        return self._request("/api/getCtrlStatusDump")

    def get_config(self) -> dict:
        """Config snapshot for backup/diff, merging the two confirmed-live config-read endpoints. REDACTS every credential-shaped field via
        REDACT_KEY_PATTERN before returning — not yet seen a real secret in this family's config live, but the pattern applies
        unconditionally per this project's standing rule after two prior incidents on other families."""
        merged = {
            "cn_agent": self._request("/local/getCnAgentConfig"),
            "minion": self._request("/local/minionConfigGet"),
        }
        return redact(merged)


def _cmd_getters(adapter: CambiumCnWaveAdapter) -> int:
    adapter.login()
    try:
        e2e = adapter.get_e2e_info()
        result = {
            "facts": adapter.get_facts(),
            "e2e_info": e2e,
            "status": adapter.get_status(),
            "capability": adapter.get_capability(),
            "links_count": adapter.get_links_count(),
            "gps": adapter.get_gps(),
            "config": adapter.get_config(),
        }
        if e2e.get("enabled"):
            result["topology"] = adapter.get_topology()
            result["ctrl_status_dump"] = adapter.get_ctrl_status_dump()
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

    adapter = CambiumCnWaveAdapter(host, username, password)
    return _cmd_getters(adapter)


if __name__ == "__main__":
    raise SystemExit(main())
