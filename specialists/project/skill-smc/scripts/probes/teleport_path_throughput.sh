#!/usr/bin/env bash
# teleport_path_throughput.sh — why is a transfer from a Teleport host slow? Read-only probe run from the operator's machine.
#
# Measures, against one host reachable as root@<host> through the tsh ProxyCommand:
#   1. one SSH stream (cat /dev/zero, N seconds) and P streams at once: a per-connection cap shows as streams that add up;
#   2. the server's TCP view of that stream (ss: rtt, cwnd, retransmitted/sent segments): steady resends = packet loss;
#   3. the EC2 ENA allowance counters before/after (bw/pps/conntrack exceeded): an instance-side drop shows as a delta;
#   4. ping loss from here to the first hop past the local router, at 56 and 1400 bytes: loss that grows with packet size
#      points at bit errors on the access line; equal loss at both sizes points at a device dropping packets.
# Written from the 2026-11-05 diagnosis (skill-smc reference 03, Learned 2026-11-05). Nothing on the server is changed.
#
# Usage: teleport_path_throughput.sh <host.teleport.domain> [-s seconds] [-p parallel] [-n pings] [-h]
#   e.g. teleport_path_throughput.sh apn-teleport01.teleport.apn.au -s 15 -p 4 -n 1000
# Runtime: about 2*seconds + 2*(pings/10) + 15 s (defaults: 15 s, 4 streams, 1000 pings -> ~4 min).
set -uo pipefail   # no -e: probes that find nothing must not end the run

usage() {
  # Print usage and exit.
  # Args: $1 exit code. Returns: never.
  sed -n '2,15p' "$0" | sed 's/^# \{0,1\}//'
  exit "${1:-0}"
}

HOST="${1:-}"; [[ -z "$HOST" || "$HOST" == -h ]] && usage 0; shift
SECS=15; PAR=4; PINGS=1000
while getopts "s:p:n:h" o; do
  case "$o" in s) SECS=$OPTARG ;; p) PAR=$OPTARG ;; n) PINGS=$OPTARG ;; h) usage 0 ;; *) usage 2 ;; esac
done
SSH=(ssh -n -o BatchMode=yes -o LogLevel=ERROR -o ConnectTimeout=15 "root@$HOST")

stream() {
  # Pull zeros over one SSH session and print bytes/s.
  # Args: $1 seconds. Returns: bytes per second on stdout (integer).
  local t0 t1 bytes
  t0=$(perl -MTime::HiRes=time -e 'printf "%.3f", time')
  bytes=$("${SSH[@]}" "timeout $1 cat /dev/zero" 2>/dev/null | wc -c | tr -d ' ')
  t1=$(perl -MTime::HiRes=time -e 'printf "%.3f", time')
  awk -v b="$bytes" -v a="$t0" -v z="$t1" 'BEGIN{printf "%d\n", (z>a ? b/(z-a) : 0)}'
}

ena() {
  # Read ENA allowance counters on the server (empty when not EC2/ENA).
  # Args: none. Returns: "name value" lines on stdout.
  "${SSH[@]}" "ethtool -S eth0 2>/dev/null | grep -E 'allowance_exceeded' | tr -d ' ' | tr ':' ' '" 2>/dev/null || true
}

echo "== host: $HOST  ($(date '+%Y-%m-%d %H:%M %Z'))"
MYIP=$("${SSH[@]}" 'echo ${SSH_CLIENT%% *}' 2>/dev/null || true)
echo "   client IP as the server sees it: ${MYIP:-unknown}"

echo "== 1. throughput"
before=$(ena)
( b=$(stream "$SECS"); echo "   one stream: $(awk -v b="$b" 'BEGIN{printf "%.2f MB/s (%.1f Mbit/s)", b/1048576, b*8/1e6}')" ) &
sleep $(( SECS * 2 / 3 ))
echo "== 2. server TCP view: every flow to $MYIP, change over 4 s (loss is a path property, so all flows show it)"
"${SSH[@]}" "snap() { ss -tin state established dst ${MYIP:-0.0.0.0} 2>/dev/null | awk '/^[0-9]/{k=\$3\" \"\$4; next} \
  { s=0; r=0; c=\"\"; if (match(\$0,/segs_out:[0-9]+/)) s=substr(\$0,RSTART+9,RLENGTH-9); \
    if (match(\$0,/retrans:[0-9]+\/[0-9]+/)) { split(substr(\$0,RSTART+8,RLENGTH-8),a,\"/\"); r=a[2] } \
    if (match(\$0,/(cubic|bbr|reno)/)) c=substr(\$0,RSTART,RLENGTH); print k, s, r, c }'; }; \
  snap > /tmp/tpt.a; sleep 4; snap > /tmp/tpt.b; \
  awk 'NR==FNR{s[\$1\" \"\$2]=\$3; r[\$1\" \"\$2]=\$4; next} { k=\$1\" \"\$2; ds=\$3-s[k]; dr=\$4-r[k]; \
    if (ds>100) printf \"   %-48s %s  sent %d  resent %d  loss %.2f%%\\n\", k, \$5, ds, dr, 100*dr/ds }' /tmp/tpt.a /tmp/tpt.b; \
  rm -f /tmp/tpt.a /tmp/tpt.b" 2>/dev/null
wait
after=$(ena)
tot=0
for i in $(seq 1 "$PAR"); do stream "$SECS" > "/tmp/tpt.$$.$i" & done; wait
for i in $(seq 1 "$PAR"); do tot=$(( tot + $(cat "/tmp/tpt.$$.$i" 2>/dev/null || echo 0) )); rm -f "/tmp/tpt.$$.$i"; done
echo "   $PAR streams at once: $(awk -v b="$tot" 'BEGIN{printf "%.2f MB/s total", b/1048576}')  (adds up = per-connection cap; same as one = bandwidth cap)"

echo "== 3. EC2 ENA allowance counters during the single stream (delta)"
if [[ -z "$before" ]]; then echo "   not available (no ethtool/ENA)"; else
  join <(echo "$before" | sort) <(echo "$after" | sort) | awk '{d=$3-$2; printf "   %-32s +%d%s\n", $1, d, (d>0?"  <- instance-side drops":"")}'
fi

echo "== 4. ping loss to the first hop past the local router ($PINGS each, 56 vs 1400 bytes)"
GW=$(route -n get default 2>/dev/null | awk '/gateway/{print $2}'); [[ -z "$GW" ]] && GW=$(ip route show default 2>/dev/null | awk '{print $3; exit}')
HOP=$(traceroute -n -q 1 -w 2 -m 4 "$HOST" 2>/dev/null | awk -v gw="$GW" 'NR>1 && $2 ~ /^[0-9.]+$/ && $2 != gw {print $2; exit}')
for t in "$GW" "$HOP"; do
  [[ -z "$t" ]] && continue
  for sz in 56 1400; do
    ( l=$(ping -q -c "$PINGS" -i 0.1 -s "$sz" "$t" 2>/dev/null | grep -o -E '[0-9.]+% packet loss'); echo "   $t size=$sz: ${l:-no reply}" ) &
  done
done; wait
echo "   first hop: ${HOP:-not found} ($(whois "$HOP" 2>/dev/null | grep -i -m1 -E '^(descr|org-name|OrgName)' | sed 's/^[^:]*: *//'))"
echo "== read: steady retrans with no ENA delta and loss starting past the router = path loss; cubic caps one stream near"
echo "   MSS/RTT * 1.22/sqrt(loss). Parallel streams or BBR on the sender work around it (reference 03, Learned 2026-11-05)."
