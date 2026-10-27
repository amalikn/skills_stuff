#!/usr/bin/env bash
# Read-only probe of a site's device addresses from its SMC, over Teleport: is each unit there, and what TLS certificate does it present.
#
# usage: site_device_probe.sh --proxy <teleport-proxy> [--deadline <seconds>] <node> <ip> [<ip> ...]
#   e.g. site_device_probe.sh --proxy teleport.apn.au kakalpurannha-homeland-smc01 10.255.3.20 10.255.3.21
#
# For each IP, run on the SMC: its ARP entry (`ip neigh`), one ping, and the certificate the unit presents on 443 (a TLS handshake only,
# never a login): subject, issuer, validity dates, serial. Answers "is a radio cnMaestro lost still working on site" and "when does its
# web certificate expire" without touching the device (unified-network-controller U1.2, 2026-10-21: 16 SMCs, 49 addresses, about 1 s each).
# The proxy is required and never guessed (a node name can exist on both clusters). IPs must be dotted IPv4; nothing else reaches the box.
# Only reads; writes nothing on the box or locally. Every tsh call has a deadline (default 90 s, `--deadline`).
# Exit status: 0 when the SMC answered for every IP, 1 when it was unreachable or cut off by the deadline, 2 on bad usage.
# Origin: unified-network-controller U1.2 (docs/reports/u1/, 2026-10-21); a radio's MAC in ARP may be its cnMaestro MAC +1 (skill-cambium).
set -u

usage() {
  # Print the header comment as help.
  sed -n '2,13p' "$0" | sed 's/^# \{0,1\}//'
}

proxy=""
deadline=90
while [ $# -gt 0 ]; do
  case "$1" in
    --proxy) proxy="${2:-}"; shift 2 ;;
    --proxy=*) proxy="${1#--proxy=}"; shift ;;
    --deadline) deadline="${2:-}"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    --) shift; break ;;
    -*) echo "unknown option: $1" >&2; usage >&2; exit 2 ;;
    *) break ;;
  esac
done
[ -n "$proxy" ] && [ $# -ge 2 ] || { usage >&2; exit 2; }
case "$deadline" in ''|*[!0-9]*) echo "--deadline must be whole seconds" >&2; exit 2 ;; esac
node="$1"; shift
for ip in "$@"; do
  [[ "$ip" =~ ^[0-9]{1,3}(\.[0-9]{1,3}){3}$ ]] || { echo "not a dotted IPv4 address: $ip" >&2; exit 2; }
done

# The remote command set is fixed here and sent on stdin; the only arguments that reach the box are the validated IPs.
REMOTE='
for ip in "$@"; do
  echo "== $ip"
  ip neigh show "$ip"
  ping -c1 -W2 "$ip" >/dev/null 2>&1 && echo "ping: ok" || echo "ping: no reply"
  c=$(echo | timeout 8 openssl s_client -connect "$ip:443" 2>/dev/null | openssl x509 -noout -subject -issuer -startdate -enddate -serial 2>/dev/null)
  [ -n "$c" ] && echo "$c" || echo "tls443: no certificate presented"
done
echo probe_end=ok
'

echo "== $node ($proxy)"
out=$(printf '%s' "$REMOTE" | perl -e 'alarm shift; exec @ARGV' "$deadline" tsh ssh --proxy="$proxy" "root@$node" "bash -s -- $*" 2>&1)
rc=$?
if [ $rc -ne 0 ] || ! printf '%s\n' "$out" | grep -q '^probe_end=ok$'; then
  printf '%s\n' "$out" | tail -3 | sed 's/^/  /'
  echo "unreachable=yes rc=$rc (check the backdoor before calling it down: backdoor-watch.sh <site>)"
  exit 1
fi
printf '%s\n' "$out" | grep -v '^probe_end=ok$'
