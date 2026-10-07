#!/usr/bin/env python3
"""Read-only Prometheus access for SMC fleet analysis, through the local Grafana datasource proxy.

Credentials come from the Grafana MCP entry in ~/.claude.json (GRAFANA_URL + GRAFANA_SERVICE_ACCOUNT_TOKEN), so nothing secret is
stored or printed here. Override with GRAFANA_URL / GRAFANA_TOKEN / PROM_DS_UID env vars, or pick the other cluster's MCP entry with
SMC_GRAFANA_MCP=mcp-grafana-nbn.

Library use (from a sibling script):  from smc_prom import instant, rng, ts
CLI use:                              smc_prom.py '<promql>'          # instant query, one line per series

Times are printed in AEDT (+11) because that is how the operator reads them; the SMC sites themselves are mostly ACST/AWST.
"""
import json, os, sys, urllib.parse, urllib.request
from datetime import datetime, timedelta, timezone

AEST = timezone(timedelta(hours=11))


def _creds():
    url, tok = os.environ.get("GRAFANA_URL"), os.environ.get("GRAFANA_TOKEN")
    if not (url and tok):
        env = json.load(open(os.path.expanduser("~/.claude.json")))["mcpServers"][os.environ.get("SMC_GRAFANA_MCP", "mcp-grafana-apn")]["env"]
        url, tok = url or env["GRAFANA_URL"], tok or env["GRAFANA_SERVICE_ACCOUNT_TOKEN"]
    # APN Grafana's default Prometheus datasource; list others with the Grafana MCP list_datasources tool
    uid = os.environ.get("PROM_DS_UID", "P1809F7CD0C75ACF3")
    return url.rstrip("/") + f"/api/datasources/proxy/uid/{uid}/api/v1/", {"Authorization": "Bearer " + tok}


BASE, HDR = _creds()


def _get(path, params, timeout=120):
    req = urllib.request.Request(BASE + path + "?" + urllib.parse.urlencode(params, doseq=True), headers=HDR)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        d = json.load(r)
    if d.get("status") != "success":
        raise RuntimeError(d)
    return d["data"] if path.startswith("label") else d["data"]["result"]


def instant(expr, t=None):
    p = {"query": expr}
    if t:
        p["time"] = t
    return _get("query", p)


def rng(expr, start, end, step):
    """Range query chunked into <=10k-point windows. Returns {json(labels): [(t, v), ...]}."""
    out, s = {}, start
    while s < end:
        e = min(end, s + step * 10000)
        for series in _get("query_range", {"query": expr, "start": s, "end": e, "step": step}):
            key = json.dumps(series["metric"], sort_keys=True)
            out.setdefault(key, []).extend((float(t), float(v)) for t, v in series["values"])
        s = e + step
    return {k: sorted(set(v)) for k, v in out.items()}


def metric_names(selector):
    return _get("label/__name__/values", {"match[]": selector})


def ts(t):
    return datetime.fromtimestamp(t, AEST).strftime("%Y-%m-%d %H:%M")


def epoch(s):
    """'YYYY-MM-DD HH:MM' in AEDT -> epoch seconds."""
    return int(datetime.strptime(s, "%Y-%m-%d %H:%M").replace(tzinfo=AEST).timestamp())


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    for r in instant(sys.argv[1]):
        print(r["metric"], r["value"][1])
