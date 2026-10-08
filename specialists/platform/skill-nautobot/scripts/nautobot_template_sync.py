"""Add the interfaces a Device Type's templates promise but its existing Devices lack. Plans by default; writes only with --apply. Stdlib only.

Why: Nautobot copies a Device Type's interface templates onto a Device only when the Device is created
(`InterfaceTemplate.instantiate`, called from `Device.save` for a new object). A template added to the type later never reaches the
Devices that already exist. Seen on 3.2.3 (2026-10-08): a template added to an ATA's type after its Device was created did not appear on
that Device. This module finds those gaps and creates the missing interfaces the way instantiation would: name, label, type, port_type,
mgmt_only, speed, duplex and description from the template, status Active. An interface that already exists by name is never touched,
whatever its type, so a hand-made or renamed port is left alone.

Usage as a library:
    from nautobot_template_sync import plan, payloads
    missing = plan(devices, templates, interfaces)                      # REST dicts; pure, no I/O
    bodies = payloads(missing, status_id)                               # POST bodies for /api/dcim/interfaces/
Usage as a CLI (NAUTOBOT_URL, NAUTOBOT_TOKEN in the environment; the token is never printed):
    python3 nautobot_template_sync.py --device-type "DDC_VoIP-m" [--device-type ...] [--manufacturer "Dallas Delta Corp"] [--apply]
Exit 0 when nothing is missing or every create succeeded, 1 when interfaces are missing (plan) or a create failed, 2 on bad input or a
failed read.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from typing import Callable

from nautobot_paging import PagingError, listing, traverse

#: Template fields copied onto the new interface, as InterfaceTemplate.instantiate does on 3.2.3 (empty values are left out of the body).
COPIED = ("name", "label", "type", "port_type", "mgmt_only", "speed", "duplex", "description")


def _ref_id(value) -> str | None:
    """The id of a REST foreign-key value: a nested dict's `id`, or the value itself when it is already an id."""
    return value.get("id") if isinstance(value, dict) else value


def _choice(value):
    """A REST choice field's value: `{"value": "1000base-t", "label": ...}` at depth>0, or the plain string."""
    return value.get("value") if isinstance(value, dict) else value


def plan(devices: list[dict], templates: list[dict], interfaces: list[dict]) -> list[tuple[dict, dict]]:
    """[(device, template)] for every template of a device's type whose name no interface on that device carries, in input order.

    Inputs are REST dicts: devices with `id`, `name`, `device_type`; templates with `device_type` and the COPIED fields; interfaces with
    `device` and `name`. A template on a module type (no `device_type`) is ignored: module templates instantiate with the module.
    """
    by_type: dict[str, list[dict]] = {}
    for t in templates:
        dt = _ref_id(t.get("device_type"))
        if dt:
            by_type.setdefault(dt, []).append(t)
    have: dict[str, set[str]] = {}
    for i in interfaces:
        have.setdefault(_ref_id(i.get("device")), set()).add(i.get("name"))
    missing = []
    for d in devices:
        names = have.get(d["id"], set())
        for t in by_type.get(_ref_id(d.get("device_type")), []):
            if t.get("name") not in names:
                missing.append((d, t))
    return missing


def payloads(missing: list[tuple[dict, dict]], status_id: str) -> list[dict]:
    """POST bodies for /api/dcim/interfaces/: the device, status, and each COPIED template field that holds a value."""
    bodies = []
    for d, t in missing:
        body = {"device": d["id"], "status": status_id}
        for field in COPIED:
            value = _choice(t.get(field))
            if value not in (None, ""):
                body[field] = value
        if "mgmt_only" not in body:
            body["mgmt_only"] = bool(t.get("mgmt_only"))
        bodies.append(body)
    return bodies


def client(base: str, token: str) -> Callable[..., dict | list]:
    """A minimal REST caller: call(method, path_or_url, body=None) -> parsed JSON; raises RuntimeError with the HTTP status on failure."""
    api = base.rstrip("/")
    api = api if api.endswith("/api") else api + "/api"

    def call(method: str, path: str, body=None):
        """One request; `path` is an API path (`/dcim/...`) or an absolute `next` URL from a listing."""
        url = path if path.startswith("http") else api + path
        req = urllib.request.Request(url, data=json.dumps(body).encode() if body is not None else None, method=method,
                                     headers={"Authorization": f"Token {token}", "Accept": "application/json", "Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                raw = resp.read()
            return json.loads(raw) if raw else {}
        except urllib.error.HTTPError as e:
            raise RuntimeError(f"{method} {path} -> HTTP {e.code}: {e.read().decode(errors='replace')[:300]}") from None
        except (urllib.error.URLError, ConnectionError) as e:
            raise RuntimeError(f"{method} {path} -> {e}") from None

    return call


def read_inventory(get: Callable[[str], dict], models: list[str], manufacturer: str | None) -> tuple[list[dict], list[dict], list[dict]]:
    """(devices, templates, interfaces) of the named Device Type models, each listing traversed fail-closed.

    Raises LookupError for a model Nautobot does not have, and lets RuntimeError (HTTP or network) and PagingError through.
    Interfaces are read 50 devices at a time with repeated `device=` filters.
    """
    types = []
    for model in models:
        q = {"model": model, **({"manufacturer": manufacturer} if manufacturer else {})}
        found = traverse(get, listing("/dcim/device-types/?" + urllib.parse.urlencode(q)))
        if not found:
            raise LookupError(f"no device type {model!r}")
        types += found
    devices, templates, interfaces = [], [], []
    for dt in types:
        devices += traverse(get, listing(f"/dcim/devices/?device_type={dt['id']}"))
        templates += traverse(get, listing(f"/dcim/interface-templates/?device_type={dt['id']}"))
    for n in range(0, len(devices), 50):
        ids = "&".join(f"device={d['id']}" for d in devices[n:n + 50])
        interfaces += traverse(get, listing(f"/dcim/interfaces/?{ids}"))
    return devices, templates, interfaces


def main(argv: list[str] | None = None) -> int:
    """Read the named device types, their templates, devices and interfaces; print what is missing; create it with --apply."""
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--device-type", action="append", required=True, help="Device Type model; repeat for several")
    ap.add_argument("--manufacturer", default=None, help="limit the model lookup to this Manufacturer name")
    ap.add_argument("--apply", action="store_true", help="create the missing interfaces (default: plan only)")
    a = ap.parse_args(argv)
    base, token = os.environ.get("NAUTOBOT_URL"), os.environ.get("NAUTOBOT_TOKEN")
    if not base or not token:
        print("set NAUTOBOT_URL and NAUTOBOT_TOKEN", file=sys.stderr)
        return 2
    call = client(base, token)

    def get(url: str) -> dict:
        """The one-argument GET that traverse() pages with."""
        return call("GET", url)

    try:
        devices, templates, interfaces = read_inventory(get, a.device_type, a.manufacturer)
    except (RuntimeError, PagingError, LookupError) as err:
        print(err, file=sys.stderr)
        return 2
    missing = plan(devices, templates, interfaces)
    for d, t in missing:
        print(f"{d.get('name')}: missing {t.get('name')!r} ({_choice(t.get('type'))})")
    print(f"{len(devices)} device(s), {len(templates)} template(s), {len(missing)} interface(s) missing", file=sys.stderr)
    if not missing:
        return 0
    if not a.apply:
        print("plan only; --apply creates them", file=sys.stderr)
        return 1
    statuses = call("GET", "/extras/statuses/?name=Active&content_types=dcim.interface")["results"]
    if not statuses:
        print("no Active status for dcim.interface", file=sys.stderr)
        return 2
    bodies = payloads(missing, statuses[0]["id"])
    try:
        for n in range(0, len(bodies), 100):
            call("POST", "/dcim/interfaces/", bodies[n:n + 100])
    except RuntimeError as e:
        print(e, file=sys.stderr)
        return 1
    print(f"created {len(bodies)} interface(s)", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
