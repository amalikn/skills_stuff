#!/usr/bin/env python3
"""SNMP v2c get / walk / set against a device behind an SMC, run FROM the SMC with no net-snmp installed.

usage: snmp_via_smc.py <smc-host> <device-ip> <vault-entry> <op> [op ...]
  op:  get:<oid>              e.g. get:.1.3.6.1.2.1.1.5.0
       walk:<oid>             GETNEXT until the OID leaves the subtree (max 400 rows)
       set:<oid>:s:<value>    OCTET STRING set (s), or set:<oid>:i:<int> INTEGER set
  TSH_PROXY  Teleport proxy (default teleport.apn.au)

Why (2026-10-07): SNMP is UDP and does not cross a Teleport port-forward, and the rct and wh SMCs carry no net-snmp (snmpget/snmpset
absent; RouterOS 7.8 has /tool snmp-get and snmp-walk but no snmp-set). So a stdlib BER client is sent to the SMC as `python3 -c`,
and the community follows on stdin: never on a command line (Teleport audits exec commands and ships them to Graylog), never
printed, never written to disk. The community comes from KeePass (`kp show -s -a Password <entry>`) on this machine.
Read-only unless an op is `set:`; a set is the caller's decision.
"""

from __future__ import annotations

import json
import os
import shlex
import subprocess
import sys

AGENT = r'''
import json, random, socket, sys
# Runs ON THE SMC as `python3 -c`. Line 1 of stdin is the community, line 2 the request {"ip", "ops"}; neither ever touches argv or disk.
community = sys.stdin.readline().rstrip("\n").encode()
req = json.loads(sys.stdin.readline())
ip = req["ip"]

# ---------- BER encoding (SNMPv2c messages are BER: tag, length, value) ----------

def enc_len(n):
    """BER length octets: one byte below 128, else 0x80 | byte-count followed by the length in big-endian bytes."""
    if n < 0x80: return bytes([n])
    b = n.to_bytes((n.bit_length() + 7) // 8, "big"); return bytes([0x80 | len(b)]) + b
def tlv(t, v):
    """One BER element: tag byte, encoded length, value bytes."""
    return bytes([t]) + enc_len(len(v)) + v
def enc_int(n):
    """A BER INTEGER: two's complement, big-endian, the minimum number of bytes (with a sign bit to spare)."""
    return tlv(0x02, n.to_bytes(max(1, (n.bit_length() + 8) // 8), "big", signed=True))
def enc_oid(s):
    """A BER OBJECT IDENTIFIER from dotted text: the first two arcs packed as 40*a+b, every later arc base-128 with the high bit set on all
    bytes but the last."""
    p = [int(x) for x in s.strip(".").split(".")]
    out = bytes([40 * p[0] + p[1]])
    for n in p[2:]:
        c = [n & 0x7f]; n >>= 7
        while n: c.insert(0, 0x80 | (n & 0x7f)); n >>= 7
        out += bytes(c)
    return tlv(0x06, out)
# ---------- BER decoding ----------
def dec(b, i):
    """Decode the element at offset i of bytes b: returns (tag, value bytes, offset just past it), handling long-form lengths."""
    t = b[i]; l = b[i + 1]; i += 2
    if l & 0x80:
        k = l & 0x7f; l = int.from_bytes(b[i:i + k], "big"); i += k
    return t, b[i:i + l], i + l
def dec_oid(v):
    """OBJECT IDENTIFIER value bytes back to dotted text with a leading dot, the inverse of enc_oid."""
    p = [v[0] // 40, v[0] % 40]; n = 0
    for x in v[1:]:
        n = (n << 7) | (x & 0x7f)
        if not x & 0x80: p.append(n); n = 0
    return "." + ".".join(map(str, p))
def value(t, v):
    """A varbind value as (type name, Python value). Strings decode as UTF-8, else hex; Counter32, Gauge32, TimeTicks and Counter64 become ints;
    the SNMPv2 exceptions (noSuchObject, noSuchInstance, endOfMibView) come back by name so a caller can tell absent from empty."""
    if t == 0x02: return "INTEGER", int.from_bytes(v, "big", signed=True)
    if t == 0x04:
        try: return "STRING", v.decode()
        except UnicodeDecodeError: return "HEX", v.hex(":")
    if t == 0x06: return "OID", dec_oid(v)
    if t == 0x40: return "IPADDR", ".".join(map(str, v))
    if t in (0x41, 0x42, 0x43, 0x46): return {0x41: "COUNTER32", 0x42: "GAUGE32", 0x43: "TIMETICKS", 0x46: "COUNTER64"}[t], int.from_bytes(v, "big")
    if t == 0x05: return "NULL", None
    return {0x80: "noSuchObject", 0x81: "noSuchInstance", 0x82: "endOfMibView"}.get(t, "TAG%02x" % t), v.hex()

# ---------- one SNMP exchange ----------
def request(pdu_tag, binds):
    """Send one SNMPv2c PDU (0xA0 get, 0xA1 getnext, 0xA3 set) to the device over UDP 161 and parse the response.

    Three tries, 3 s each, because the SMC-to-device hop crosses a busy site switch. Returns (error-status, error-index, rows) with rows as
    (oid, type, value); (None, None, []) means no reply at all, which the caller reports as `timeout`.
    """
    rid = random.randint(1, 2**31 - 1)
    vb = b"".join(tlv(0x30, enc_oid(o) + val) for o, val in binds)
    pdu = tlv(pdu_tag, enc_int(rid) + enc_int(0) + enc_int(0) + tlv(0x30, vb))
    msg = tlv(0x30, enc_int(1) + tlv(0x04, community) + pdu)
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM); s.settimeout(3)
    for _ in range(3):
        s.sendto(msg, (ip, 161))
        try: data = s.recv(65535)
        except socket.timeout: continue
        _, body, _ = dec(data, 0); i = 0
        _, _, i = dec(body, i); _, _, i = dec(body, i)
        _, pdu_b, _ = dec(body, i); j = 0
        _, _, j = dec(pdu_b, j); _, es, j = dec(pdu_b, j); _, ei, j = dec(pdu_b, j)
        _, vbl, _ = dec(pdu_b, j); rows = []; k = 0
        while k < len(vbl):
            _, one, k = dec(vbl, k); _, ov, m = dec(one, 0); vt, vv, _ = dec(one, m)
            rows.append((dec_oid(ov),) + value(vt, vv))
        return int.from_bytes(es, "big"), int.from_bytes(ei, "big"), rows
    return None, None, []

# ---------- run the requested ops, one JSON line each ----------
ERR = {0: "noError", 2: "noSuchName", 4: "readOnly", 6: "noAccess", 7: "wrongType", 10: "wrongValue", 16: "authorizationError", 17: "notWritable"}
for op in req["ops"]:
    kind, rest = op.split(":", 1)
    if kind == "get":
        es, ei, rows = request(0xA0, [(rest, tlv(0x05, b""))])
    elif kind == "set":
        oid, typ, val = rest.split(":", 2)
        enc = tlv(0x04, val.encode()) if typ == "s" else enc_int(int(val))
        es, ei, rows = request(0xA3, [(oid, enc)])
    else:
        rows, cur, es = [], rest, 0
        while len(rows) < 400:
            es, ei, r = request(0xA1, [(cur, tlv(0x05, b""))])
            if es is None or es or not r or not (r[0][0] + ".").startswith(rest.rstrip(".") + ".") or r[0][1] == "endOfMibView": break
            rows.append(r[0]); cur = r[0][0]
    status = "timeout" if es is None else ERR.get(es, "error%d" % es)
    print(json.dumps({"op": op if kind != "set" else "set:" + rest.split(":", 1)[0], "status": status, "rows": rows}))
'''


def main() -> int:
    """Read the community from KeePass, send AGENT to the SMC as `python3 -c`, pass the community and the ops on stdin, and print the agent's JSON lines.

    The community never appears on a command line (Teleport audits exec commands and ships them to Graylog) and is replaced by <community> in
    anything printed. Returns the remote exit code; 2 for an unknown op, 3 when the vault entry gives no one-line value.
    """
    if len(sys.argv) < 5:
        print(__doc__, file=sys.stderr)
        return 2
    smc, ip, entry, ops = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4:]
    for op in ops:
        if op.split(":", 1)[0] not in ("get", "walk", "set"):
            print(f"unknown op: {op}", file=sys.stderr)
            return 2
    community = subprocess.run(["kp", "show", "-s", "-a", "Password", entry], capture_output=True, text=True).stdout.rstrip("\n")
    if not community or "\n" in community:
        print(f"cannot read a one-line community from {entry}", file=sys.stderr)
        return 3
    proxy = os.environ.get("TSH_PROXY", "teleport.apn.au")
    stdin = community + "\n" + json.dumps({"ip": ip, "ops": ops}) + "\n"
    out = subprocess.run(["tsh", f"--proxy={proxy}", "ssh", f"root@{smc}", "python3 -c " + shlex.quote(AGENT)],
                         input=stdin, capture_output=True, text=True, timeout=600)
    text = (out.stdout + out.stderr).replace(community, "<community>")
    sys.stdout.write(text)
    return out.returncode


if __name__ == "__main__":
    sys.exit(main())
