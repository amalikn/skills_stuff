#!/usr/bin/env bash
# Read-only AVR firmware probe for RCT SMCs (the tstik board's AVR), over Teleport.
#
# usage: rct_avr_probe.sh [--parallel N] --proxy <teleport-proxy> <node> [<node> ...]
#   e.g. rct_avr_probe.sh --proxy teleport.apn.au mooloowa-smc01 gilroyd-smc01
#        QUERY=1 rct_avr_probe.sh --proxy teleport.apn.au warehouse-rct01
#
# Prints one `AVRPROBE|<node>|host=<hostname>|key=value|...` line per box: avr (AVRVersion as tstik's Stats page shows it; tstik drops the
# minor's leading zero, so 3.7 is V3.07), tini (TiniVer), stats_age_s (seconds since update:stats last wrote stats.json; cron runs it every
# 5 minutes), tstik (rct-tstik HEAD), loader (py_avrloader_v2.py / py_avrloader.py in /home), overlay (1 = overlayroot), and with QUERY=1
# avr_query (the version the AVR itself reports through the loader, two-digit minor with v2). Default mode only reads files: no serial
# traffic. QUERY=1 sends one version request on /dev/ttyS0 after waiting for cron's update:stats to finish (the two collide on the unlocked
# port: tstik re-runs stty and flushes before every send). Writes nothing on the box or locally.
# Exit status: 0 when every node answered, 1 when any node was unreachable or gave no probe line, 2 on bad usage.
# Origin: ansible-wifi rct-tstik-iridium-update, 2026-10-28 (references/06_failure-modes.md, AVR entries).
set -u

usage() {
  # Print the header comment as help.
  #
  # Args: none.
  # Returns: 0; writes the usage text to stdout.
  sed -n '2,15p' "$0" | sed 's/^# \{0,1\}//'
}

# The on-box probe. Kept in one quoted heredoc so nothing expands locally. Every pgrep is anchored at "^php " (a pattern without ^ also
# matches this shell's own command line, which holds the probe text).
read -r -d '' PROBE <<'EOF'
kv() { printf '|%s=%s' "$1" "$(printf '%s' "$2" | tr '\n|' ' /' | sed -E 's/ +/ /g; s/ $//')"; }
t=/var/www/html/rct-tstik; s=$t/storage/stats.json
val() { python3 -c "import json,sys; print(json.load(open(sys.argv[1])).get(sys.argv[2],{}).get('value',''))" "$s" "$1" 2>/dev/null; }
out="$(kv avr "$(val AVRVersion)")$(kv tini "$(val TiniVer)")"
out="$out$(kv stats_age_s "$( [ -f "$s" ] && echo $(( $(date +%s) - $(stat -c %Y "$s") )) )")"
out="$out$(kv tstik "$(git -C "$t" rev-parse --short HEAD 2>/dev/null)")"
out="$out$(kv loader "$(cd /home 2>/dev/null && ls py_avrloader_v2.py py_avrloader.py 2>/dev/null | tr '\n' ' ')")"
out="$out$(kv overlay "$(mount | grep -c 'on / type overlay')")"
if [ "${QUERY:-0}" = 1 ]; then
  l=/home/py_avrloader_v2.py; [ -f "$l" ] || l=/home/py_avrloader.py
  for i in $(seq 1 60); do pgrep -f '^php [a]rtisan update:stats' >/dev/null || break; sleep 1; done
  q=$( [ -f "$l" ] && printf 'q\n' | timeout 60 python3 "$l" -d /dev/ttyS0 -m 2>&1 | grep -o 'AVR version=[0-9.]*' | head -n 1 | cut -d= -f2)
  out="$out$(kv avr_query "${q:-no answer or no loader}")"
fi
echo "AVRPROBE$(kv host "$(hostname)")$out"
EOF

proxy=""
parallel=8
while [ $# -gt 0 ]; do
  case "$1" in
    --proxy) proxy="${2:-}"; shift 2 ;;
    --proxy=*) proxy="${1#--proxy=}"; shift ;;
    --parallel) parallel="${2:-8}"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    --) shift; break ;;
    -*) echo "unknown option: $1" >&2; usage >&2; exit 2 ;;
    *) break ;;
  esac
done
if [ -z "$proxy" ] || [ $# -eq 0 ]; then
  usage >&2
  exit 2
fi

probe_one() {
  # Run the probe on one node and print its AVRPROBE line, or a FAIL line.
  #
  # Args:
  #   $1: node name as Teleport knows it.
  # Returns: 0 when a probe line came back, 1 otherwise; prints one line either way.
  local node="$1" line
  line="$(timeout 180 tsh ssh --proxy="$proxy" "root@$node" "QUERY=${QUERY:-0} bash -s" <<<"$PROBE" 2>&1 | tr -d '\r' | grep '^AVRPROBE|' | head -1)"
  if [ -n "$line" ]; then
    echo "AVRPROBE|$node|${line#AVRPROBE|}"
    return 0
  fi
  echo "FAIL|$node|no probe output (Teleport unreachable? check scripts/access/backdoor-watch.sh)"
  return 1
}

rc=0
running=0
pids=()
for node in "$@"; do
  probe_one "$node" &
  pids+=("$!")
  running=$((running + 1))
  if [ "$running" -ge "$parallel" ]; then
    wait "${pids[0]}" || rc=1
    pids=("${pids[@]:1}")
    running=$((running - 1))
  fi
done
for pid in "${pids[@]+"${pids[@]}"}"; do
  wait "$pid" || rc=1
done
exit "$rc"
