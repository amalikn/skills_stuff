#!/usr/bin/env bash
# Read-only breakdown of what occupies the overlayroot tmpfs upper layer on SMC boxes, plus the usual suspects behind its growth.
#
# usage: overlay-usage-breakdown.sh [--etc] <host> [<host> ...]   e.g. overlay-usage-breakdown.sh laramba-smc01 mimbi-smc01
#   --etc      only the /etc census: every /etc file the box changed since boot (upper-layer files, links and whiteouts with their times);
#              on a box without overlayroot, /etc files modified since boot. Used to find run-time writers under /etc (2026-10-20).
#   TSH_PROXY  Teleport proxy (default teleport.apn.au; nbn_wh/nbn_accelerate use teleport.communitywifi.net.au)
#   HOST_DEADLINE  seconds allowed per host (default 60); a host past it is reported as "deadline" and the run goes on.
#
# Runs du/find under nice+ionice and only reads (reading never triggers overlay copy_up; references/07 section 8). Origin: 2026-10-07 WH investigation, where the upper layer (a 3.9-4.1 GB tmpfs on
# 8 GB Pis) was found to be filled by: auth.log from ~400k `sudo iptables`/`sudo rmtrack` calls a week by the captive portal, uncompressed
# .1 rotations, the journal, squidGuard blocklist rebuilds (db + newdb), snapd refreshes (lxd/core revisions) and apt lists/caches.
set -u
proxy=${TSH_PROXY:-teleport.apn.au}
deadline=${HOST_DEADLINE:-60}
etc_only=0
[ "${1:-}" = "--etc" ] && { etc_only=1; shift; }
[ $# -ge 1 ] || { sed -n '2,14p' "$0"; exit 2; }

# The /etc census, run on the box: upper-layer entries under /etc (f file, l link, c whiteout = deleted) with time and size, or, with no
# overlayroot, /etc files modified since boot.
ETC_CENSUS=$(cat <<'EOF'
U=/media/root-rw/overlay; echo "== $(hostname)  boot $(uptime -s)  ($(uptime -p), from /proc/uptime)"
if [ -d "$U/etc" ]; then echo "-- /etc changed since boot (overlay upper: f file, l link, c whiteout)"
  nice ionice -c3 find "$U/etc" \( -type f -o -type l -o -type c \) -printf "%TY-%Tm-%Td_%TH:%TM %y %s %p\n" 2>/dev/null | sed "s#$U##" | sort -k4
else echo "-- no overlayroot: /etc files modified since boot"
  nice ionice -c3 find /etc -xdev -newermt "$(uptime -s)" \( -type f -o -type l \) -printf "%TY-%Tm-%Td_%TH:%TM %y %s %p\n" 2>/dev/null | sort -k4
fi
EOF
)

# with_deadline — run a command, killing it after $deadline seconds. macOS has no timeout(1), and a perl alarm before exec does not stop tsh
# (it ran past a 60 s alarm, 2026-10-20), so a watcher sends TERM, then KILL 5 s later.
#   Args: the command and its arguments.
#   Returns: the command's exit status (143 or 137 when the deadline killed it).
with_deadline() {
  "$@" & local pid=$!
  ( sleep "$deadline"; kill -TERM "$pid" 2>/dev/null; sleep 5; kill -KILL "$pid" 2>/dev/null ) & local watcher=$!
  wait "$pid"; local rc=$?
  kill "$watcher" 2>/dev/null; wait "$watcher" 2>/dev/null
  return $rc
}

for host in "$@"; do
  if [ $etc_only -eq 1 ]; then
    with_deadline tsh --proxy="$proxy" ssh "root@$host" "$ETC_CENSUS" 2>&1 || echo "== $host: failed or past the ${deadline}s deadline (rc $?)"
    echo; continue
  fi
  with_deadline tsh --proxy="$proxy" ssh "root@$host" 'U=/media/root-rw/overlay
[ -d "$U" ] || { echo "== $(hostname): no overlayroot upper dir at $U"; exit 0; }
echo "== $(hostname)  $(uptime -p)"; df -h /media/root-rw | tail -1
echo "-- top dirs (MB, depth 3)"; nice ionice -c3 du -xm --max-depth=3 "$U" 2>/dev/null | sort -n | tail -18
echo "-- top files >20M"; nice ionice -c3 find "$U" -xdev -type f -size +20M -printf "%s %p\n" 2>/dev/null | sort -n | tail -15 \
  | awk "{printf \"%7.0fM %s\n\", \$1/1048576, \$2}"
echo "-- deleted-but-open files (still held in tmpfs)"; find /proc/[0-9]*/fd -lname "*(deleted)" -printf "%l\n" 2>/dev/null | sort | uniq -c | sort -n | tail -5
echo "-- journal"; journalctl --disk-usage 2>/dev/null
echo "-- auth.log top message shapes"; [ -f /var/log/auth.log ] && cut -d" " -f5- /var/log/auth.log | sed -E "s/[0-9]+/N/g" | cut -c1-110 | sort | uniq -c | sort -n | tail -4
echo "-- writers on timers/cron"; systemctl list-timers --all --no-pager 2>/dev/null | grep -E "apt-daily|snap|logrotate" | awk "{print \$(NF-1)}"
crontab -l 2>/dev/null | grep -v "^#" | grep -iE "squid|blocklist"; snap list 2>/dev/null | awk "NR>1{print \"snap:\", \$1, \$3}"' 2>&1 \
    || echo "== $host: failed or past the ${deadline}s deadline (rc $?)"
  echo
done
