#!/usr/bin/env python3
"""Derive, merge and enforce the Cambium device response *contract* — a schema, not a snapshot.

The problem this solves: the MIB mirrors are not the contract. `cnPilotMIB` describes 16 client
columns where an XV2 returns 95; `CAMBIUM-PMP80211-MIB` documents 29 ePMP connected-SM columns
where a live 3000L returns 42. Adapter code written against a mirror, or against one device's
response captured once, breaks on the next firmware or the next site.

So the contract is derived from observation and then held as a standard:

  1. `observe`  — pull one device's endpoints and emit a schema for that observation. No values
                  are recorded beyond low-cardinality candidate enums on non-identifying fields.
  2. `merge`    — fold many observations into one standard. A field seen on every observation is
                  `required`; a field seen on some is optional and carries the sites and firmware
                  that had it. This is what makes the standard a standard rather than one site's
                  accident.
  3. `check`    — validate a fresh observation against the standard and report divergence:
                  missing required fields, unknown new fields, and type changes.

Privacy: values that identify an end user are never written, at any stage. PII_FIELDS names them
and `--strict-pii` widens the net to anything that *looks* like a MAC, IP or hostname regardless
of field name. Device-side identifiers (AP MAC, radio BSSID, SM MAC) are infrastructure and are
still never emitted as examples — the standard has no use for them.

Layers: a schema describes either a raw device endpoint (`raw-endpoint`) or an adapter's
normalized getter output (`adapter-normalized`). Only the Enterprise Wi-Fi Falcon families expose
raw endpoints conveniently; ePMP, R195P and cnWave are contracted at their adapter's output. The
layer is recorded in every schema so nobody compares two things that are not the same thing.

Usage:
    # one device, one family, live
    CAMBIUM_USER=... CAMBIUM_PASS=... python3 schema_tool.py observe \\
        --driver falcon --host localhost:10019 --family enterprise-wifi \\
        --model XV2 --site hope-vale --endpoints client-summary,radio-summary \\
        --out obs/hope-vale-xv2.json

    # schema from an adapter's stdout (any family)
    python3 cambium_epmp_adapter.py | python3 schema_tool.py observe \\
        --driver stdin --family epmp-ap --model 'ePMP 3000L' --site hope-vale \\
        --layer adapter-normalized --out obs/hope-vale-epmp.json

    # fold observations into the standard
    python3 schema_tool.py merge --family enterprise-wifi obs/*.json \\
        --out ../schemas/enterprise-wifi/

    # conformance of a new site against the standard
    python3 schema_tool.py check --standard ../schemas/enterprise-wifi \\
        --observation obs/amata-xv2.json
"""
import argparse
import ipaddress
import json
import os
import re
import ssl
import sys
import urllib.error
import urllib.request
from collections import defaultdict
from datetime import datetime, timezone
from http.cookiejar import CookieJar
from pathlib import Path

SCHEMA_DIALECT = "https://json-schema.org/draft/2020-12/schema"

# Field names whose values identify an end user. Never emitted. Widen, never narrow.
PII_FIELDS = {
    "mac", "macaddress", "mac_address", "ip", "ipaddr", "ipaddress", "ip6", "ip6_ll", "ipv6",
    "name", "hostname", "user_name", "username", "client_name", "dev_type", "vendor",
    "ssid",  # an SSID is not personal, but it is site-identifying and has no place in a contract
}
MAC_RE = re.compile(r"^(?:[0-9A-Fa-f]{2}[-:]){5}[0-9A-Fa-f]{2}$")
# A candidate enum must be short, low-cardinality and non-identifying — "2.4GHz", "ON", "axa".
ENUM_MAX_DISTINCT = 8
ENUM_MAX_LEN = 24


def looks_identifying(value):
    """True when a value looks like an address or hostname whatever its field is called."""
    if not isinstance(value, str) or not value:
        return False
    if MAC_RE.match(value):
        return True
    try:
        ipaddress.ip_address(value)
        return True
    except ValueError:
        pass
    return bool(re.match(r"^[A-Za-z0-9_-]+\.[A-Za-z0-9._-]+$", value))


def json_type(value):
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, int):
        return "integer"
    if isinstance(value, float):
        return "number"
    if isinstance(value, str):
        return "string"
    if isinstance(value, list):
        return "array"
    if isinstance(value, dict):
        return "object"
    return "string"


class FieldFacts:
    """What has been observed about one field, across every record and every device."""

    def __init__(self):
        self.types = set()
        self.present = 0
        self.null_count = 0
        self.values = set()
        self.value_overflow = False
        self.child = None          # FieldFacts for array items / nested objects
        self.object_fields = None  # name -> FieldFacts

    def see(self, value, strict_pii, field_name):
        t = json_type(value)
        self.types.add(t)
        self.present += 1
        if t == "null":
            self.null_count += 1
            return
        if t == "object":
            if self.object_fields is None:
                self.object_fields = defaultdict(FieldFacts)
            for k, v in value.items():
                self.object_fields[k].see(v, strict_pii, k)
            return
        if t == "array":
            if self.child is None:
                self.child = FieldFacts()
            for item in value:
                self.child.see(item, strict_pii, field_name)
            return
        if self._enumerable(value, strict_pii, field_name):
            if len(self.values) < ENUM_MAX_DISTINCT:
                self.values.add(value)
            else:
                self.value_overflow = True
        else:
            self.value_overflow = True

    @staticmethod
    def _enumerable(value, strict_pii, field_name):
        if field_name.lower() in PII_FIELDS:
            return False
        if isinstance(value, bool):
            return True
        if isinstance(value, str):
            if len(value) > ENUM_MAX_LEN:
                return False
            if strict_pii and looks_identifying(value):
                return False
            return not looks_identifying(value)
        return False

    def to_schema(self, field_name, total_records):
        types = sorted(self.types - {"null"})
        node = {}
        if not types:
            node["type"] = "null"
        elif len(types) == 1:
            node["type"] = types[0]
        else:
            node["type"] = types
            node["x-type-varies"] = True
        if "null" in self.types:
            node["x-nullable"] = True
        if field_name.lower() in PII_FIELDS:
            node["x-identifying"] = True
            node["x-note"] = "End-user identifying — values are never recorded in this contract."
        if self.values and not self.value_overflow and len(self.values) <= ENUM_MAX_DISTINCT:
            node["x-candidate-values"] = sorted(self.values, key=str)
        if self.child is not None:
            node["items"] = self.child.to_schema(field_name, total_records)
        if self.object_fields is not None:
            node["properties"] = {
                k: v.to_schema(k, total_records) for k, v in sorted(self.object_fields.items())
            }
        node["x-observed-count"] = self.present
        return node


def schema_from_payload(payload, strict_pii):
    """Infer one endpoint's schema. A list of records is contracted at the record level, which is
    the useful unit — how many rows happened to exist at capture time says nothing about shape."""
    root = FieldFacts()
    if isinstance(payload, list):
        records = payload
        shape = "array"
    else:
        records = [payload]
        shape = "object"
    for rec in records:
        root.see(rec, strict_pii, "")
    if shape == "array":
        # Each element was fed to `root` directly, so the record's fields live on root itself —
        # `root.child` is only populated for arrays nested *inside* a record.
        fields = root.object_fields or {}
        body = {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {k: v.to_schema(k, len(records)) for k, v in sorted(fields.items())},
                "required": sorted(k for k, v in fields.items() if v.present == len(records)) if records else [],
            },
        }
    elif root.object_fields is not None:
        fields = root.object_fields
        body = {
            "type": "object",
            "properties": {k: v.to_schema(k, 1) for k, v in sorted(fields.items())},
            "required": sorted(fields),
        }
    else:
        # A scalar response — an integer count, a bare string. Still a contract, just a flat one.
        body = root.to_schema("", 1)
        body.pop("x-observed-count", None)
    body["x-records-observed"] = len(records)
    return body


class FalconDriver:
    """Enterprise Wi-Fi (XV2 and cnPilot E-series share the Falcon UI): POST /api/login, then
    session cookies plus an X-XSRF-TOKEN header echoing the XSRF-TOKEN cookie."""

    def __init__(self, host, user, password):
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        self.host = host
        self.jar = CookieJar()
        self.opener = urllib.request.build_opener(
            urllib.request.HTTPSHandler(context=ctx),
            urllib.request.HTTPCookieProcessor(self.jar))
        self.xsrf = None
        self.user, self.password = user, password

    def _req(self, method, path, body=None):
        data = json.dumps(body).encode() if body is not None else None
        req = urllib.request.Request(f"https://{self.host}{path}", data=data, method=method)
        if data:
            req.add_header("Content-Type", "application/json")
        if self.xsrf:
            req.add_header("X-XSRF-TOKEN", self.xsrf)
        with self.opener.open(req, timeout=20) as resp:
            raw = resp.read().decode()
        for c in self.jar:
            if c.name == "XSRF-TOKEN":
                self.xsrf = c.value
        return json.loads(raw) if raw else {}

    def login(self):
        if not self._req("POST", "/api/login", {"username": self.user, "password": self.password}).get("success"):
            raise SystemExit("login rejected")

    def fetch(self, endpoint):
        return self._req("GET", f"/api/{endpoint}")


def cmd_observe(args):
    endpoints = {}
    if args.driver == "falcon":
        user, password = os.environ.get("CAMBIUM_USER"), os.environ.get("CAMBIUM_PASS")
        if not (user and password):
            raise SystemExit("CAMBIUM_USER and CAMBIUM_PASS must be set")
        dev = FalconDriver(args.host, user, password)
        dev.login()
        for ep in [e.strip() for e in args.endpoints.split(",") if e.strip()]:
            try:
                endpoints[ep] = schema_from_payload(dev.fetch(ep), args.strict_pii)
            except (urllib.error.URLError, urllib.error.HTTPError, ValueError, OSError) as exc:
                endpoints[ep] = {"x-error": f"{type(exc).__name__}: {exc}"}
                print(f"  {ep}: {type(exc).__name__}", file=sys.stderr)
    elif args.driver == "stdin":
        payload = json.load(sys.stdin)
        # An adapter prints one object of named getters; contract each getter separately.
        if isinstance(payload, dict) and args.split_getters:
            for name, value in payload.items():
                endpoints[name] = schema_from_payload(value, args.strict_pii)
        else:
            endpoints[args.endpoints or "response"] = schema_from_payload(payload, args.strict_pii)
    else:
        raise SystemExit(f"unknown driver: {args.driver}")

    doc = {
        "x-observation": {
            "captured_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "family": args.family,
            "model": args.model,
            "firmware": args.firmware,
            "site": args.site,
            "layer": args.layer,
            "driver": args.driver,
            "strict_pii": args.strict_pii,
        },
        "endpoints": endpoints,
    }
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(doc, indent=2) + "\n")
    print(args.out)


def _merge_node(a, b):
    """Union two schema nodes. Types union; nullability and variance are sticky; candidate values
    union until they stop being a candidate enum; observation counts add."""
    if a is None:
        return json.loads(json.dumps(b))
    out = json.loads(json.dumps(a))
    ta = out.get("type")
    tb = b.get("type")
    types = set(ta if isinstance(ta, list) else [ta]) | set(tb if isinstance(tb, list) else [tb])
    types.discard(None)
    out["type"] = sorted(types)[0] if len(types) == 1 else sorted(types)
    if len(types) > 1:
        out["x-type-varies"] = True
    for flag in ("x-nullable", "x-identifying", "x-type-varies"):
        if b.get(flag):
            out[flag] = True
    va, vb = out.get("x-candidate-values"), b.get("x-candidate-values")
    if va is not None and vb is not None:
        merged = sorted(set(va) | set(vb), key=str)
        if len(merged) <= ENUM_MAX_DISTINCT:
            out["x-candidate-values"] = merged
        else:
            out.pop("x-candidate-values", None)
    else:
        out.pop("x-candidate-values", None)
    out["x-observed-count"] = out.get("x-observed-count", 0) + b.get("x-observed-count", 0)
    if "items" in a or "items" in b:
        out["items"] = _merge_node(a.get("items"), b.get("items")) if b.get("items") else a.get("items")
    if "properties" in a or "properties" in b:
        props = dict(a.get("properties", {}))
        for k, v in b.get("properties", {}).items():
            props[k] = _merge_node(props.get(k), v)
        out["properties"] = props
    return out


# Endpoints whose response is a MAP keyed by a site-variable name rather than a record with fixed
# fields. The adapter layer follows NAPALM's convention here (see cambium_xv2_adapter.py's
# get_interfaces docstring), so an interface map is correct and deliberate. Contracting its keys as
# fields is what is wrong: it makes one site's VLAN plan look like the family's schema. For these,
# the contract describes the VALUE shape under `additionalProperties` and records what the keys are.
MAP_SHAPED = {
    ("cnpilot-r-series", "interfaces"): "interface name, e.g. eth2.17, wan1.500 — varies per site",
}


def collapse_map(node, key_meaning):
    """Fold a map's per-key schemas into one value schema under `additionalProperties`."""
    target = node.get("items", node)
    props = target.pop("properties", {}) or {}
    merged = None
    for spec in props.values():
        merged = _merge_node(merged, spec)
    target["additionalProperties"] = merged or {"type": "object"}
    target["x-map-keyed-by"] = key_meaning
    target["x-keys-observed"] = sorted(props)
    target.pop("required", None)
    target.pop("x-optional", None)
    return node


def cmd_merge(args):
    obs = [json.loads(Path(p).read_text()) for p in args.observations]
    obs = [o for o in obs if o["x-observation"]["family"] == args.family]
    if not obs:
        raise SystemExit(f"no observations for family {args.family}")

    by_endpoint = defaultdict(list)
    for o in obs:
        for ep, node in o["endpoints"].items():
            if "x-error" not in node:
                by_endpoint[ep].append((o["x-observation"], node))

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    written = []
    for ep, entries in sorted(by_endpoint.items()):
        merged = None
        for _, node in entries:
            merged = _merge_node(merged, node)

        # Required = present on every observation that actually returned a record.
        #
        # An endpoint that returned an empty array is not evidence that its fields are absent — a
        # radio with no clients attached says nothing about what a client record contains. Counting
        # it would drag every field to "optional" and destroy the contract. Such observations are
        # excluded from the presence maths and counted separately, so a reader can see how much
        # evidence the `required` set actually rests on.
        bearing = [(meta, node) for meta, node in entries
                   if (node.get("items", node).get("properties") or {})]
        empty = [meta["site"] for meta, node in entries
                 if not (node.get("items", node).get("properties") or {})]
        seen = defaultdict(int)
        sites_with = defaultdict(set)
        for meta, node in bearing:
            for k in (node.get("items", node).get("properties") or {}):
                seen[k] += 1
                sites_with[k].add(f"{meta['site']}/{meta['model']}")
        target = merged.get("items", merged)
        total = len(bearing)
        target["required"] = sorted(k for k, c in seen.items() if c == total) if total else []
        target["x-optional"] = {
            k: {"observed_on": c, "of": total, "seen_at": sorted(sites_with[k])}
            for k, c in sorted(seen.items()) if c < total
        }
        target["x-evidence"] = {
            "observations_with_records": total,
            "observations_empty": len(empty),
            "empty_at": sorted(empty),
            "note": ("`required` rests only on observations that returned a record. Endpoints empty "
                     "at capture time contribute nothing either way."),
        }

        key_meaning = MAP_SHAPED.get((args.family, ep))
        if key_meaning:
            merged = collapse_map(merged, key_meaning)

        doc = {
            "$schema": SCHEMA_DIALECT,
            "$id": f"cambium/{args.family}/{ep}.schema.json",
            "title": f"Cambium {args.family} — {ep}",
            "description": (
                "Derived from live observation, not from vendor documentation. Fields listed in "
                "`required` were present on every device observed; `x-optional` names the rest with "
                "how often they appeared. No end-user identifying values are recorded."
            ),
            "x-cambium": {
                "family": args.family,
                "endpoint": ep,
                "layer": entries[0][0]["layer"],
                "observations": total,
                "models": sorted({e[0]["model"] for e in entries if e[0].get("model")}),
                "firmware": sorted({e[0]["firmware"] for e in entries if e[0].get("firmware")}),
                "sites": sorted({e[0]["site"] for e in entries if e[0].get("site")}),
                "generated_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            },
            **{k: v for k, v in merged.items() if not k.startswith("x-records")},
        }
        path = out_dir / f"{ep}.schema.json"
        path.write_text(json.dumps(doc, indent=2) + "\n")
        written.append((ep, total, len((merged.get("items", merged)).get("properties", {})),
                        merged.get("type"), len(entries)))
    for ep, n, fields, typ, seen_total in written:
        if fields:
            detail = f"{fields} fields from {n} observation(s)"
        elif typ == "null":
            detail = f"observed as null on {seen_total} observation(s) — endpoint exists, no data"
        elif typ == "array":
            detail = f"empty on all {seen_total} observation(s) — shape unknown, needs a bearing sample"
        else:
            detail = f"scalar ({typ}) from {seen_total} observation(s)"
        print(f"{ep}: {detail} -> {out_dir / (ep + '.schema.json')}")


def cmd_check(args):
    obs = json.loads(Path(args.observation).read_text())
    std_dir = Path(args.standard)
    report = {"observation": str(args.observation), "standard": str(std_dir),
              "site": obs["x-observation"].get("site"), "model": obs["x-observation"].get("model"),
              "firmware": obs["x-observation"].get("firmware"), "endpoints": {}}
    worst = "conformant"
    for ep, node in obs["endpoints"].items():
        std_path = std_dir / f"{ep}.schema.json"
        if "x-error" in node:
            report["endpoints"][ep] = {"status": "error", "detail": node["x-error"]}
            worst = "divergent"
            continue
        if not std_path.exists():
            report["endpoints"][ep] = {"status": "no-standard", "detail": "endpoint absent from the standard"}
            worst = "divergent"
            continue
        std = json.loads(std_path.read_text())
        std_t, obs_t = std.get("items", std), node.get("items", node)
        # An endpoint that returned nothing cannot diverge from anything. Reporting it as divergent
        # would flag every site whose AP happened to have no client attached.
        if not (obs_t.get("properties") or {}):
            report["endpoints"][ep] = {
                "status": "no-records",
                "detail": "endpoint returned no record at capture time — contributes no evidence",
            }
            continue
        std_props, obs_props = std_t.get("properties", {}), obs_t.get("properties", {})
        missing_required = sorted(set(std_t.get("required", [])) - set(obs_props))
        unknown = sorted(set(obs_props) - set(std_props))
        type_changes = {}
        for k in sorted(set(std_props) & set(obs_props)):
            s, o = std_props[k].get("type"), obs_props[k].get("type")
            s_set = set(s if isinstance(s, list) else [s])
            o_set = set(o if isinstance(o, list) else [o])
            if not o_set <= s_set:
                type_changes[k] = {"standard": s, "observed": o}
        status = "conformant" if not (missing_required or unknown or type_changes) else "divergent"
        if status == "divergent":
            worst = "divergent"
        report["endpoints"][ep] = {"status": status, "missing_required": missing_required,
                                   "unknown_fields": unknown, "type_changes": type_changes}
    report["status"] = worst
    text = json.dumps(report, indent=2)
    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(text + "\n")
        print(args.out)
    else:
        print(text)
    return 0 if worst == "conformant" else 1


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    o = sub.add_parser("observe", help="contract one device's responses")
    o.add_argument("--driver", choices=["falcon", "stdin"], required=True)
    o.add_argument("--host", help="host:port for a live driver, usually a Teleport port-forward")
    o.add_argument("--endpoints", default="", help="comma-separated endpoints (falcon), or a name (stdin)")
    o.add_argument("--family", required=True)
    o.add_argument("--model", default="")
    o.add_argument("--firmware", default="")
    o.add_argument("--site", required=True)
    o.add_argument("--layer", choices=["raw-endpoint", "adapter-normalized"], default="raw-endpoint")
    o.add_argument("--split-getters", action="store_true", help="stdin driver: contract each top-level key separately")
    o.add_argument("--strict-pii", action="store_true", default=True)
    o.add_argument("--out", required=True)
    o.set_defaults(func=cmd_observe)

    m = sub.add_parser("merge", help="fold observations into the family standard")
    m.add_argument("observations", nargs="+")
    m.add_argument("--family", required=True)
    m.add_argument("--out", required=True)
    m.set_defaults(func=cmd_merge)

    c = sub.add_parser("check", help="conformance of one observation against the standard")
    c.add_argument("--standard", required=True)
    c.add_argument("--observation", required=True)
    c.add_argument("--out")
    c.set_defaults(func=cmd_check)

    args = ap.parse_args()
    raise SystemExit(args.func(args) or 0)


if __name__ == "__main__":
    main()
