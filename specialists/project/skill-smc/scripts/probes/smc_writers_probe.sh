#!/usr/bin/env bash
# Read-only probe of what writes on an SMC (Pi or x86), and on a Pi its supply voltage history, over Teleport.
#
# usage: smc_writers_probe.sh --proxy <teleport-proxy> [--deadline <seconds>] <node> [<node> ...]
#   e.g. smc_writers_probe.sh --proxy teleport.communitywifi.net.au bungardi-smc01 galiwinku-smc01
#
# Prints one `== <node>` block per box: uptime and the disk's sectors written since boot; the 15 processes that wrote most since they
# started (`proc=<bytes> <seconds running> <pid> <name>`, from /proc/<pid>/io write_bytes); the 15 folders holding the most bytes in files
# changed in the last 24 h (`dir24h=<bytes> <folder>`, a find on the root filesystem at idle I/O priority, cut at 90 s); the journal's size;
# the overlayroot configuration and command line; every cron line (`cron=<file>: <line>`); the journal's top sources in the last hour
# (`journal_1h=<count> <unit or identifier>`); and on a Pi the throttle flags and the kernel's undervoltage lines of the last 7 days.
# Only reads; writes nothing on the box or locally. The proxy is required and never guessed. Each tsh call is cut at the deadline (default
# 240 s): TERM, then KILL (tsh survives SIGALRM, 2026-11-10).
# Exit status: 0 when every node answered, 1 when any did not, 2 on bad usage.
# Origin: smc-resiliency fleet survey 2026-11-10 (nbn_wh writes 4 to 7 GB a day to its card, nbn_accelerate up to 45 GB; undervoltage on wh).
set -u

usage() {
  # Print the header comment as help.
  # Args: none. Returns: 0; the help text on stdout.
  sed -n '2,15p' "$0" | sed 's/^# \{0,1\}//'
}

proxy=""
deadline=240
while [ $# -gt 0 ]; do
  case "$1" in
    --proxy) proxy="${2:-}"; shift 2 ;;
    --proxy=*) proxy="${1#--proxy=}"; shift ;;
    --deadline) deadline="${2:-}"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    -*) echo "unknown option: $1" >&2; usage >&2; exit 2 ;;
    *) break ;;
  esac
done
[ -n "$proxy" ] && [ $# -ge 1 ] || { usage >&2; exit 2; }
case "$deadline" in ''|*[!0-9]*) echo "--deadline must be whole seconds" >&2; exit 2 ;; esac

# Remote command set is fixed here; the script takes node names only, never commands.
REMOTE='
echo uptime_s=$(cut -d. -f1 /proc/uptime)
root=$(findmnt -n -o SOURCE /media/root-ro 2>/dev/null || findmnt -n -o SOURCE /); disk=$(lsblk -sno NAME,TYPE "$root" 2>/dev/null | awk "\$2==\"disk\"{print \$1}" | tail -1 | tr -dc "a-z0-9")
echo disk=$disk sectors_written=$(awk "{print \$7}" /sys/block/$disk/stat 2>/dev/null)
for p in /proc/[0-9]*; do wb=$(awk "/^write_bytes/{print \$2}" $p/io 2>/dev/null); [ -n "$wb" ] && [ "$wb" -gt 0 ] && echo "$wb $(ps -o etimes= -p ${p#/proc/} 2>/dev/null | tr -d " ") ${p#/proc/} $(cat $p/comm 2>/dev/null)"; done | sort -rn | head -15 | sed "s/^/proc=/"
timeout 90 nice -n 19 ionice -c3 find / -xdev -type f -mmin -1440 -printf "%s %h\n" 2>/dev/null | awk "{s[\$2]+=\$1} END{for(d in s) printf \"%d %s\n\", s[d], d}" | sort -rn | head -15 | sed "s/^/dir24h=/"
echo journal=$(journalctl --disk-usage 2>/dev/null | grep -oE "[0-9.]+[KMGT]?B? in the file system|take up [0-9.]+[KMGT]" | tail -1)
echo overlayroot_conf=$(grep -vE "^\s*(#|$)" /etc/overlayroot.conf 2>/dev/null | tr "\n" " ") cmdline_overlay=$(tr " " "\n" < /proc/cmdline | grep -E "^overlayroot" | tr "\n" " ")
if command -v vcgencmd >/dev/null 2>&1; then
  echo throttled=$(vcgencmd get_throttled | cut -d= -f2) volts_core=$(vcgencmd measure_volts core | cut -d= -f2)
  echo undervoltage_lines_7d=$(journalctl -k --since "-7d" 2>/dev/null | grep -ciE "under-?voltage detected") boots_7d=$(journalctl --list-boots --since "-7d" 2>/dev/null | grep -c .)
  journalctl -k --since "-7d" -o short-iso 2>/dev/null | grep -i "voltage" | tail -6 | sed "s/^/voltage_line=/"
fi
for c in /etc/crontab /etc/cron.d/* /var/spool/cron/crontabs/*; do [ -f "$c" ] && grep -vE "^\s*(#|$)|^(SHELL|PATH|MAILTO)=" "$c" | sed "s|^|cron=$(basename $c): |"; done
journalctl --since "-1h" -o json --output-fields=_SYSTEMD_UNIT,SYSLOG_IDENTIFIER 2>/dev/null | grep -oE "\"(_SYSTEMD_UNIT|SYSLOG_IDENTIFIER)\":\"[^\"]+\"" | sort | uniq -c | sort -rn | head -8 | sed "s/^/journal_1h=/"
echo probe_end=ok
'

probe() {
  # Run the fixed read-only command set on one node and print its block.
  # Args: $1 node name (Teleport node). Returns: 0 when the node completed the probe, 1 when unreachable, cut short or past the deadline.
  local node="$1" out rc
  out=$(perl -e '$d=shift; defined(my $p=fork) or die "fork: $!"; if(!$p){exec @ARGV; exit 127} $SIG{ALRM}=sub{kill "TERM",$p; for(1..5){exit 124 if waitpid($p,1)>0; sleep 1} kill "KILL",$p; waitpid($p,0); exit 124}; alarm $d; waitpid($p,0); exit($? & 127 ? 128+($? & 127) : $?>>8)' "$deadline" \
    tsh ssh --proxy="$proxy" "root@$node" "$REMOTE" </dev/null 2>&1)
  rc=$?
  echo "== $node ($proxy)"
  if [ $rc -ne 0 ] || ! printf '%s\n' "$out" | grep -q '^probe_end=ok$'; then
    printf '%s\n' "$out" | tr -d '\033' | grep -m2 -iE 'error|offline|denied|refused|timed out' | sed 's/^/  /'
    echo "unreachable=yes rc=$rc"
    return 1
  fi
  printf '%s\n' "$out" | grep -v '^probe_end=ok$'
}

failed=0
for node in "$@"; do
  probe "$node" || failed=1
  echo
done
exit $failed
