#!/usr/bin/env python3
"""Read-only Graylog search for SMC logs through the apn-graylog Teleport app (references/03_communication-flows.md
"Graylog REST API Access").

Needs: `tsh --proxy=teleport.apn.au apps login apn-graylog` (app cert under ~/.tsh) and the API token in ../.graylog-token
(or GRAYLOG_TOKEN env var).

usage:
  smc_graylog.py search '<lucene>' '<from YYYY-MM-DD HH:MM AEDT>' '<to ...>' [limit=40] [desc|asc]
  smc_graylog.py agg    '<lucene>' <range_seconds> [group_field=tp_site]       # count + first/last timestamp per group

Field notes: every SMC message carries tp_site (bare site), source/_nodename (<site>-smc01), tp_flavor and path. Only some sites
ship logs at all - check `agg '_exists_:tp_site' 604800` before reading an empty result as "no events". Retention is roughly two months.
"""
import glob, json, os, subprocess, sys, urllib.parse
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from smc_prom import AEST

HERE = os.path.dirname(os.path.abspath(__file__))
API = "https://apn-graylog.teleport.apn.au/api"


def _token():
    if os.environ.get("GRAYLOG_TOKEN"):
        return os.environ["GRAYLOG_TOKEN"]
    return open(os.path.join(HERE, "..", ".graylog-token")).read().strip()


def _cert():
    home = os.path.expanduser("~/.tsh/keys/teleport.apn.au")
    cert = next(iter(glob.glob(f"{home}/*-app/teleport.apn.au/apn-graylog-x509.pem")), None)
    if not cert:
        sys.exit("no apn-graylog app cert: run `tsh --proxy=teleport.apn.au apps login apn-graylog`")
    user = cert.split("/")[-3][: -len("-app")]
    return cert, f"{home}/{user}"


def _curl(args):
    cert, key = _cert()
    out = subprocess.run(["curl", "-s", "--cert", cert, "--key", key, "-u", f"{_token()}:token", "-H", "Accept: application/json"] + args,
                         capture_output=True, text=True, timeout=300)
    return json.loads(out.stdout)


def _utc(s):
    t = datetime.strptime(s, "%Y-%m-%d %H:%M").replace(tzinfo=AEST).astimezone(timezone.utc)
    return t.strftime("%Y-%m-%dT%H:%M:%S.000Z")  # this Graylog rejects offsets other than Z


def search(query, frm, to, limit=40, order="desc", fields="timestamp,source,path,message"):
    p = {"query": query, "from": _utc(frm), "to": _utc(to), "limit": limit, "sort": f"timestamp:{order}", "fields": fields}
    return _curl([f"{API}/search/universal/absolute?" + urllib.parse.urlencode(p)])


def aggregate(query, range_s, field="tp_site"):
    body = {"query": query, "timerange": {"type": "relative", "range": range_s}, "group_by": [{"field": field, "limit": 500}],
            "metrics": [{"function": "count"}, {"function": "min", "field": "timestamp"}, {"function": "max", "field": "timestamp"}]}
    return _curl(["-H", "Content-Type: application/json", "-H", "X-Requested-By: cli", "-X", "POST", f"{API}/search/aggregate",
                  "-d", json.dumps(body)])


def _fmt_ms(ms):
    return datetime.fromtimestamp(float(ms) / 1000, AEST).strftime("%Y-%m-%d %H:%M")


if __name__ == "__main__":
    if len(sys.argv) < 4 or sys.argv[1] not in ("search", "agg"):
        sys.exit(__doc__)
    if sys.argv[1] == "search":
        q, frm, to = sys.argv[2:5]
        d = search(q, frm, to, int(sys.argv[5]) if len(sys.argv) > 5 else 40, sys.argv[6] if len(sys.argv) > 6 else "desc")
        if "messages" not in d:
            sys.exit(json.dumps(d)[:400])
        print(f"# total={d.get('total_results')}  {q}  [{frm} .. {to} AEDT]")
        for m in (x["message"] for x in d["messages"]):
            t = datetime.fromisoformat(m["timestamp"].replace("Z", "+00:00")).astimezone(AEST).strftime("%m-%d %H:%M:%S")
            print(t, (m.get("path") or "")[-28:], str(m.get("message", ""))[:170].replace("\n", " "))
    else:
        d = aggregate(sys.argv[2], int(sys.argv[3]), sys.argv[4] if len(sys.argv) > 4 else "tp_site")
        if "datarows" not in d:
            sys.exit(json.dumps(d)[:400])
        print("group\tcount\tfirst_aedt\tlast_aedt")
        for g, n, lo, hi in sorted(d["datarows"], key=lambda r: str(r[0])):
            print(g, n, _fmt_ms(lo), _fmt_ms(hi), sep="\t")
