#!/usr/bin/env bash
# Read-only probe of who holds apt's lists lock on SMC boxes, over Teleport.
#
# usage: apt_lock_probe.sh [--parallel N] --proxy <teleport-proxy> <node> [<node> ...]
#   e.g. apt_lock_probe.sh --proxy teleport.apn.au illeparratye-smc01 hoppys-camp-smc01
#        apt_lock_probe.sh --proxy teleport.apn.au $(cat nodes.txt)
#
# Prints one `APTLOCK|<node>|host=<hostname>|key=value|...` line per box: apt_info (every running node_exporter
# `python3 /usr/local/lib/apt_info.py` job as pid:age-seconds), lists_lock (pid(command) holding /var/lib/apt/lists/lock, from
# lslocks, or free), dpkg_locks (holders of the dpkg and archives locks as path:pid(command):age), newest_list (date of the newest *Release/*InRelease list, i.e. the last successful apt update) and apt_busy
# (dpkg, apt, apt-get or unattended-upgrade processes running now). A stuck apt_info.py holding the lock for days, with an old
# newest_list, is the 2026-10-28 failure: apt updates fail with "Could not get lock /var/lib/apt/lists/lock ... (python3)".
# Only reads; writes nothing on the box or locally.
# Exit status: 0 when every node answered, 1 when any node was unreachable or gave no probe line, 2 on bad usage.
# Origin: ansible-wifi php-cve-2026-109618 rct run, apt_pin "Refresh apt lists" failures, 2026-10-28.
set -u

usage() {
  # Print the header comment as help.
  #
  # Args: none.
  # Returns: 0; writes the usage text to stdout.
  sed -n '2,15p' "$0" | sed 's/^# \{0,1\}//'
}

# The on-box probe. Kept in one quoted heredoc so nothing expands locally. Lock owner by path (lslocks), not inode: an inode number
# alone matched an unrelated lock on another device (delye-smc01, fluent-bit, 2026-10-28).
read -r -d '' PROBE <<'EOF'
kv() { printf '|%s=%s' "$1" "$(printf '%s' "$2" | tr '\n|' ' /' | sed -E 's/ +/ /g; s/ $//')"; }
jobs_=$(pgrep -f '^python3 /usr/local/lib/apt_info\.py' | while read -r p; do printf '%s:%s ' "$p" "$(ps -o etimes= -p "$p" | tr -d ' ')"; done)
lock=$(lslocks -n -o PID,COMMAND,PATH 2>/dev/null | awk '$3=="/var/lib/apt/lists/lock"{print $1"("$2")"; exit}')
others=$(lslocks -n -o PID,COMMAND,PATH 2>/dev/null | awk '$3 ~ /^\/var\/(lib\/dpkg\/lock(-frontend)?|cache\/apt\/archives\/lock)$/ {print $3":"$1"("$2")"}' \
  | while IFS= read -r l; do p=${l#*:}; p=${p%%(*}; printf '%s:%ss ' "$l" "$(ps -o etimes= -p "$p" | tr -d ' ')"; done)
newest=$(ls -t --time-style=+%F -l /var/lib/apt/lists/*_InRelease /var/lib/apt/lists/*_Release 2>/dev/null | awk 'NR==1{print $6}')
busy=$(for c in dpkg apt apt-get unattended-upgr; do pgrep -x "$c" >/dev/null && printf '%s ' "$c"; done)
out="$(kv host "$(hostname)")$(kv apt_info "${jobs_:-none}")$(kv lists_lock "${lock:-free}")"
out="$out$(kv dpkg_locks "${others:-free}")$(kv newest_list "${newest:-unknown}")$(kv apt_busy "${busy:-none}")"
echo "APTLOCK|$NODE$out"
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
    *) break ;;
  esac
done
if [ -z "$proxy" ] || [ $# -eq 0 ]; then
  usage >&2
  exit 2
fi

probe_one() {
  # Run the probe on one node and print its APTLOCK line, or a FAIL line.
  #
  # Args:
  #   $1: node name as Teleport knows it.
  # Returns: 0 when a probe line came back, 1 otherwise; prints one line either way.
  local node="$1" line
  line="$(timeout 60 tsh ssh --proxy="$proxy" "root@$node" "NODE=$node bash -s" <<<"$PROBE" 2>&1 | tr -d '\r' | grep '^APTLOCK|' | head -1)"
  if [ -n "$line" ]; then
    echo "$line"
    return 0
  fi
  echo "APTLOCK|$node|FAIL=no probe line (unreachable or Teleport error)"
  return 1
}

rc=0
running=0
for node in "$@"; do
  probe_one "$node" &
  running=$((running + 1))
  if [ "$running" -ge "$parallel" ]; then
    wait -n || rc=1
    running=$((running - 1))
  fi
done
while [ "$running" -gt 0 ]; do
  wait -n || rc=1
  running=$((running - 1))
done
exit "$rc"
