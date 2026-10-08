#!/usr/bin/env python3
"""Read the settings of the rct site ATA (Dallas Delta DDC_VoIP-m) through each site's SMC, and compare units.

The unit answers only on its web UI (references/17_site-ata-dallas-delta.md). This wrapper sends a small stdlib-only agent
(AGENT below, Python 3.10 compatible) to each SMC over Teleport:

    tsh ssh --proxy=<proxy> root@<node> "python3 -c '<agent>' <ata-ip>"

The agent logs in with the empty PIN (POST /login nextpage=<page>&auth=&login=Enter) -- the empty PIN is what the units in
service have (operator, 2026-10-08: try it) -- reads the pages settings, phonebook and digitmap, and prints
{page: {field: value}} as JSON. Any field whose name matches pin|pass|pwd|pw|secret is dropped ON THE SMC, so no PIN,
password or SIP secret leaves the box; the wrapper drops such names again before printing. It tolerates the unit's
IncompleteRead (the settings page declares 43 bytes more Content-Length than it sends).

Read-only toward the ATA: one login POST per page read, never a form submission. `_registered` is the settings page's
`Registered : Yes|No`, the unit's SIP registration state.

With several nodes it prints which fields differ between units; on 2026-10-08, 83 of 93 settings fields were identical
across five units and the differing ones were auth_id/user_number, sip_proxy, syslog_ip, user_name and the volumes.

Usage:
    ata_settings_read.py --proxy teleport.apn.au adjamarragu-smc01 alamirra-smc01      # summary + field comparison
    ata_settings_read.py --proxy teleport.apn.au --json adjamarragu-smc01               # full JSON per node
    ata_settings_read.py --local 127.0.0.1:8080                                        # run the agent here (lab/test)

Exit status: 0 when every unit was read, 1 when any node or unit could not be read, 2 on bad usage.
"""
import argparse
import json
import re
import shlex
import subprocess
import sys

DEFAULT_IP = "192.168.5.253"
SECRET = re.compile(r"pin|pass|pwd|pw(?![a-z])|secret", re.I)

# Runs ON THE SMC. Keep it Python 3.10 and standard library only; it must not print any secret-named field.
AGENT = r'''
import html, http.client, json, re, sys, urllib.parse, urllib.request
ip = sys.argv[1]
SECRET = re.compile(r"pin|pass|pwd|pw(?![a-z])|secret", re.I)
def fetch(page):
    data = urllib.parse.urlencode({"nextpage": page, "auth": "", "login": "Enter"}).encode()
    try:
        raw = urllib.request.urlopen(urllib.request.Request("http://%s/login" % ip, data=data), timeout=40).read()
    except http.client.IncompleteRead as e:
        raw = e.partial
    return raw.decode("latin-1", "replace")
out = {}
for page in ("settings", "phonebook", "digitmap"):
    try:
        t = fetch(page)
    except Exception as e:
        out[page] = {"_error": str(e)[:80]}
        continue
    f = {}
    for m in re.finditer(r"<input([^>]*)>", t, re.I):
        a = m.group(1)
        n = re.search(r"name=\"?([\w\-]+)", a, re.I)
        if not n or SECRET.search(n.group(1)):
            continue
        ty = re.search(r"type=\"?(\w+)", a, re.I)
        ty = ty.group(1).lower() if ty else "text"
        v = re.search(r"value=\"([^\"]*)\"|value=([^\s>]+)", a, re.I)
        v = html.unescape((v.group(1) if v.group(1) is not None else v.group(2)) if v else "")
        if ty in ("checkbox", "radio"):
            if re.search(r"\bchecked\b", a, re.I):
                f.setdefault(n.group(1), []).append(v or "on")
        elif ty not in ("submit", "button", "reset", "hidden"):
            f[n.group(1)] = v
    for m in re.finditer(r"<select[^>]*name=\"?([\w\-]+)[^>]*>(.*?)</select>", t, re.I | re.S):
        if SECRET.search(m.group(1)):
            continue
        sel = re.search(r"<option[^>]*selected[^>]*>([^<]*)", m.group(2), re.I)
        f[m.group(1)] = sel.group(1).strip() if sel else None
    text = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", re.sub(r"(?is)<(script|style).*?</\1>", " ", t)))
    reg = re.search(r"Registered\s*:\s*(Yes|No)", text, re.I)
    if reg:
        f["_registered"] = reg.group(1).capitalize()
    f["_text_labels"] = re.findall(r"((?:Model|MAC Address|Version No\.|Register(?:ed)?(?: Status)?|Status|Uptime)\s*:?\s*[\w.:\-]+)", text)[:12]
    out[page] = f
print(json.dumps(out))
'''


def scrub(pages: dict) -> dict:
    """Drop any secret-named field a second time, locally, in case the agent on the box was an older copy."""
    return {page: {k: v for k, v in (fields or {}).items() if not SECRET.search(k)} if isinstance(fields, dict) else fields
            for page, fields in pages.items()}


def read_remote(proxy: str, node: str, ip: str, timeout: int) -> tuple[dict | None, str]:
    """Run the agent on one SMC over Teleport; return (pages, error). pages is None when the node or unit gave no JSON."""
    remote = f"python3 -c {shlex.quote(AGENT)} {shlex.quote(ip)}"
    cmd = ["tsh", "ssh", f"--proxy={proxy}", f"root@{node}", remote]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return None, f"timeout after {timeout}s"
    return parse_output(res.returncode, res.stdout, res.stderr)


def read_local(ip: str, timeout: int) -> tuple[dict | None, str]:
    """Run the agent on this machine against an ATA (or a test server) it can reach directly."""
    try:
        res = subprocess.run([sys.executable, "-c", AGENT, ip], capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return None, f"timeout after {timeout}s"
    return parse_output(res.returncode, res.stdout, res.stderr)


def parse_output(rc: int, stdout: str, stderr: str) -> tuple[dict | None, str]:
    """Take the agent's last JSON line; report the tail of stderr when there is none."""
    for line in reversed(stdout.strip().splitlines()):
        if line.startswith("{"):
            try:
                return scrub(json.loads(line)), ""
            except json.JSONDecodeError:
                break
    detail = (stderr.strip().splitlines() or stdout.strip().splitlines() or [""])[-1][:160]
    return None, f"rc={rc} {detail}".strip()


def unit_errors(pages: dict) -> list[str]:
    """Pages the agent reached but could not read (connection refused, reset, timeout)."""
    return [f"{p}: {f['_error']}" for p, f in pages.items() if isinstance(f, dict) and "_error" in f]


def compare(results: dict[str, dict]) -> list[str]:
    """Per page, count fields identical across all units and list the ones that differ, with each unit's value."""
    lines = []
    nodes = list(results)
    pages = sorted({p for r in results.values() for p in r})
    for page in pages:
        keys = sorted({k for r in results.values() for k in (r.get(page) or {}) if not k.startswith("_")})
        differ = [k for k in keys if len({json.dumps((results[n].get(page) or {}).get(k)) for n in nodes}) > 1]
        lines.append(f"-- {page}: {len(keys)} fields, {len(keys) - len(differ)} identical across {len(nodes)} units")
        for k in differ:
            vals = ", ".join(f"{n}={json.dumps((results[n].get(page) or {}).get(k))}" for n in nodes)
            lines.append(f"   {k}: {vals}")
    return lines


def main() -> int:
    """Parse arguments, read each unit, print a summary (or JSON), and compare when more than one unit was read."""
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("nodes", nargs="*", help="SMC Teleport node names, e.g. adjamarragu-smc01")
    ap.add_argument("--proxy", help="Teleport proxy, e.g. teleport.apn.au (required with nodes; never guessed)")
    ap.add_argument("--ip", default=DEFAULT_IP, help=f"ATA address as seen from the SMC (default {DEFAULT_IP})")
    ap.add_argument("--local", metavar="HOST[:PORT]", help="run the agent on this machine against HOST instead of over Teleport")
    ap.add_argument("--json", action="store_true", help="print the full {node: {page: {field: value}}} JSON")
    ap.add_argument("--timeout", type=int, default=180, help="seconds per node (default 180)")
    args = ap.parse_args()

    if args.local:
        targets = {f"local:{args.local}": lambda: read_local(args.local, args.timeout)}
    elif args.nodes and args.proxy:
        targets = {n: (lambda n=n: read_remote(args.proxy, n, args.ip, args.timeout)) for n in args.nodes}
    else:
        ap.print_usage(sys.stderr)
        print("give --proxy and at least one node, or --local HOST", file=sys.stderr)
        return 2

    results, failed = {}, False
    for name, run in targets.items():
        pages, err = run()
        if pages is None:
            print(f"== {name}: UNREACHABLE {err}", file=sys.stderr)
            failed = True
            continue
        errs = unit_errors(pages)
        if errs:
            print(f"== {name}: ATA not read ({'; '.join(errs)})", file=sys.stderr)
            failed = True
            if len(errs) == len(pages):
                continue
        results[name] = pages

    if args.json:
        print(json.dumps(results, indent=2, sort_keys=True))
    else:
        for name, pages in results.items():
            s = pages.get("settings") or {}
            n_fields = sum(1 for p in pages.values() if isinstance(p, dict) for k in p if not k.startswith("_"))
            print(f"== {name}: registered={s.get('_registered', '?')} fields={n_fields} labels={s.get('_text_labels', [])[:4]}")
        if len(results) > 1:
            print("\n".join(compare(results)))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
