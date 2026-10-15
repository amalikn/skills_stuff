#!/usr/bin/env bash
# Read-only summary of an SMC's client DNS capture for a time window: top clients, top domains, and each top client's domains.
#
# usage: dns_capture_top.sh --proxy <teleport-proxy> --date YYYYMMDD [--from HH:MM] [--to HH:MM] [--top N] [--bridge IF] <node>
#   e.g. dns_capture_top.sh --proxy teleport.communitywifi.net.au --date 20261009 --from 16:00 --to 23:59 koonibba-smc01
#
# Reads the url_capture pcaps (/url_capture/YYYYMM/<node>-<bridge>-<date>-*.pcap, written by /url_capturev1.sh with
# filter "dst port 53") on the box and prints three tables: queries per client IP, queries per registrable-ish domain (last two
# labels), and the top five domains for each of the N busiest clients. Times are the box's local time. DNS shows names, not
# bytes: use it to say which services a busy device used, never how much each moved. Squid keeps about 3 days of logs, so for
# older spikes these pcaps are the only per-client record left.
# Only reads; a temp file on the box is removed on exit. Writes nothing locally.
# Exit status: 0 on output, 1 when no capture file matched or the node was unreachable, 2 on bad usage.
# Origin: Koonibba 9 Oct 2026 usage spike (references/13_known-issues.md, 2026-09-30 bot entry, update 2026-10-15).
set -u

usage() {
  # Print the header comment as help.
  # Args: none. Returns: 0; the help text on stdout.
  sed -n '2,16p' "$0" | sed 's/^# \{0,1\}//'
}

proxy="" day="" from="00:00" to="23:59" top=5 bridge="bridge_501"
while [ $# -gt 0 ]; do
  case "$1" in
    --proxy) proxy="${2:-}"; shift 2 ;;
    --date) day="${2:-}"; shift 2 ;;
    --from) from="${2:-}"; shift 2 ;;
    --to) to="${2:-}"; shift 2 ;;
    --top) top="${2:-}"; shift 2 ;;
    --bridge) bridge="${2:-}"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    -*) echo "unknown option: $1" >&2; usage >&2; exit 2 ;;
    *) break ;;
  esac
done
[ -n "$proxy" ] && [ $# -eq 1 ] || { usage >&2; exit 2; }
node="$1"
[[ "$day" =~ ^[0-9]{8}$ ]] || { echo "--date must be YYYYMMDD" >&2; exit 2; }
[[ "$from" =~ ^[0-9]{2}:[0-9]{2}$ && "$to" =~ ^[0-9]{2}:[0-9]{2}$ && "$top" =~ ^[0-9]+$ && "$bridge" =~ ^[a-z0-9_]+$ ]] || {
  echo "bad --from/--to (HH:MM), --top (integer) or --bridge" >&2; exit 2; }

# Values are validated above, so they can be placed in the fixed remote command set safely.
REMOTE='
set -u
files=$(ls /url_capture/'"${day:0:6}"'/*-'"$bridge"'-'"$day"'-*.pcap 2>/dev/null)
[ -n "$files" ] || { echo "no capture for '"$day"' on '"$bridge"'"; exit 1; }
t=$(mktemp); trap "rm -f $t" EXIT
for f in $files; do tcpdump -nn -tttt -r "$f" 2>/dev/null; done | awk -v a="'"$from"'" -v b="'"$to"':59" "\$2>=a && \$2<=b" > "$t"
dom() { grep -oE "(A|AAAA|HTTPS)\? [^ ]+" | awk "{print \$2}" | awk -F. "{n=NF; if (n>=3) print \$(n-2)\".\"\$(n-1); else print \$0}"; }
echo "files: $files"
echo "queries in window: $(wc -l < "$t")"
echo "== top clients"
awk "{split(\$4,a,\".\"); print a[1]\".\"a[2]\".\"a[3]\".\"a[4]}" "$t" | sort | uniq -c | sort -rn | head -'"$top"'
echo "== top domains"
dom < "$t" | sort | uniq -c | sort -rn | head -25
echo "== top domains per busiest client"
for ip in $(awk "{split(\$4,a,\".\"); print a[1]\".\"a[2]\".\"a[3]\".\"a[4]}" "$t" | sort | uniq -c | sort -rn | head -'"$top"' | awk "{print \$2}"); do
  printf "%s: " "$ip"; grep " $ip\." "$t" | dom | sort | uniq -c | sort -rn | head -5 | awk "{printf \"%s(%s) \", \$2, \$1}"; echo
done
'
tsh --proxy="$proxy" ssh "root@$node" "$REMOTE"
