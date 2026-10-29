#!/usr/bin/env python3
"""What SSH a device behind an SMC offers, read from the SMC with no authentication attempted (nothing counts toward a lockout).

For each address: the server banner, the negotiated key exchange, host key, cipher and MAC, the auth methods offered, or why it failed
("no matching host key type" and so on). Tells a TP-Link `TPSSH` switch from an older `IPSSH-6.6.0` one (SG2428P 4.0.1 offers only ssh-dss,
diffie-hellman-group1-sha1, aes128-cbc, hmac-md5; references/16_tplink-site-switches.md, Learned 2026-10-29) before a driver logs in.

Run: python3 scripts/switch/ssh_handshake_probe.py --proxy teleport.example:443 <site>-smc01 10.255.1.2 10.255.3.1
     (just ssh_handshake_probe <proxy> <node> <ip> ...). Read-only: `ssh -vv` with PreferredAuthentications=none and BatchMode, one tsh
     session for all addresses, under a deadline.
"""

from __future__ import annotations

import argparse
import re
import shlex
import subprocess
import sys

#: Legacy algorithms appended as fallbacks, the same set the TP-Link driver uses, so an old server still shows what it negotiates.
LEGACY = ("-o HostKeyAlgorithms=+ssh-rsa,ssh-dss -o MACs=hmac-sha2-256,hmac-md5 -o KexAlgorithms=+diffie-hellman-group1-sha1 "
          "-o Ciphers=+aes128-cbc")
FIELDS = {
  "banner": re.compile(r"remote software version (\S+)"),
  "protocol": re.compile(r"Remote protocol version ([\d.]+)"),
  "kex": re.compile(r"kex: algorithm: (\S+)"),
  "hostkey": re.compile(r"kex: host key algorithm: (\S+)"),
  "cipher": re.compile(r"kex: server->client cipher: (\S+) MAC: (\S+)"),
  "auth": re.compile(r"Authentications that can continue: (\S+)"),
  "error": re.compile(r"(Unable to negotiate .*|Connection (?:refused|timed out).*|no matching .*)"),
}


def parse(text: str) -> dict[str, str]:
  """Pick the handshake facts out of one `ssh -vv` transcript.

  Args:
    text: the transcript (stderr of ssh -vv).

  Returns:
    {banner, protocol, kex, hostkey, cipher, mac, auth, error}: each present only when the transcript holds it.
  """
  out: dict[str, str] = {}
  for key, rx in FIELDS.items():
    m = rx.search(text)
    if not m:
      continue
    if key == "cipher":
      out["cipher"], out["mac"] = m.group(1), m.group(2)
    else:
      out[key] = m.group(1)
  return out


def remote_script(ips: list[str]) -> str:
  """The shell run on the SMC: one delimited `ssh -vv` per address, no authentication.

  Args:
    ips: the device addresses.

  Returns:
    The script text.
  """
  lines = []
  for ip in ips:
    lines.append(f"echo '===IP {ip}'")
    lines.append(f"timeout 15 ssh -F /dev/null -vv {LEGACY} -o BatchMode=yes -o PreferredAuthentications=none "
                 f"-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o ConnectTimeout=8 probe@{shlex.quote(ip)} true 2>&1")
  return "\n".join(lines) + "\n"


def split(stream: str) -> dict[str, str]:
  """Split the combined output into one transcript per address.

  Args:
    stream: the SMC session's output.

  Returns:
    {ip: transcript}.
  """
  out: dict[str, str] = {}
  current = None
  for line in stream.splitlines():
    if line.startswith("===IP "):
      current = line[6:].strip()
      out[current] = ""
    elif current:
      out[current] += line + "\n"
  return out


def main(argv: list[str] | None = None) -> int:
  """Probe each address from the SMC and print one line per address.

  Args:
    argv: command-line arguments (default sys.argv[1:]).

  Returns:
    0 when every address answered a handshake, 1 when any failed, 2 when the SMC session failed.
  """
  ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
  ap.add_argument("--proxy", required=True, help="the Teleport proxy, host:port (always named)")
  ap.add_argument("--timeout", type=int, default=120, help="deadline for the whole SMC session, seconds")
  ap.add_argument("node", help="the SMC, e.g. aurukun-smc01")
  ap.add_argument("ips", nargs="+", help="device addresses behind the SMC")
  args = ap.parse_args(argv)
  try:
    res = subprocess.run(["tsh", "ssh", f"--proxy={args.proxy}", f"root@{args.node}", "bash -s"], input=remote_script(args.ips),
                         capture_output=True, text=True, timeout=args.timeout)
  except subprocess.TimeoutExpired:
    print(f"{args.node}: no answer within {args.timeout} s", file=sys.stderr)
    return 2
  if res.returncode not in (0, 255) and not res.stdout:
    print(f"{args.node}: tsh failed ({res.returncode}): {res.stderr.strip()[:200]}", file=sys.stderr)
    return 2
  bad = 0
  for ip, text in split(res.stdout).items():
    f = parse(text)
    ok = "auth" in f
    bad += not ok
    print(f"{ip:15} {f.get('banner', '-'):14} proto {f.get('protocol', '-'):4} kex {f.get('kex', '-'):28} hostkey {f.get('hostkey', '-'):10} "
          f"{f.get('cipher', '-')}/{f.get('mac', '-')} auth {f.get('auth', '-')}" + (f"  ERROR {f['error']}" if "error" in f else ""))
  return 1 if bad else 0


if __name__ == "__main__":
  sys.exit(main())
