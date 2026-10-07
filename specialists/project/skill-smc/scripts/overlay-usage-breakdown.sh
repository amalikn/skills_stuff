#!/usr/bin/env bash
# Read-only breakdown of what occupies the overlayroot tmpfs upper layer on SMC boxes, plus the usual suspects behind its growth.
#
# usage: overlay-usage-breakdown.sh <host> [<host> ...]        e.g. overlay-usage-breakdown.sh laramba-smc01 mimbi-smc01
#   TSH_PROXY  Teleport proxy (default teleport.apn.au; nbn_wh/nbn_accelerate use teleport.communitywifi.net.au)
#
# Runs du/find under nice+ionice and only reads. Origin: 2026-10-07 WH investigation, where the upper layer (a 3.9-4.1 GB tmpfs on
# 8 GB Pis) was found to be filled by: auth.log from ~400k `sudo iptables`/`sudo rmtrack` calls a week by the captive portal, uncompressed
# .1 rotations, the journal, squidGuard blocklist rebuilds (db + newdb), snapd refreshes (lxd/core revisions) and apt lists/caches.
set -u
proxy=${TSH_PROXY:-teleport.apn.au}
[ $# -ge 1 ] || { sed -n '2,10p' "$0"; exit 2; }

for host in "$@"; do
  tsh --proxy="$proxy" ssh "root@$host" 'U=/media/root-rw/overlay
[ -d "$U" ] || { echo "== $(hostname): no overlayroot upper dir at $U"; exit 0; }
echo "== $(hostname)  $(uptime -p)"; df -h /media/root-rw | tail -1
echo "-- top dirs (MB, depth 3)"; nice ionice -c3 du -xm --max-depth=3 "$U" 2>/dev/null | sort -n | tail -18
echo "-- top files >20M"; nice ionice -c3 find "$U" -xdev -type f -size +20M -printf "%s %p\n" 2>/dev/null | sort -n | tail -15 \
  | awk "{printf \"%7.0fM %s\n\", \$1/1048576, \$2}"
echo "-- deleted-but-open files (still held in tmpfs)"; find /proc/[0-9]*/fd -lname "*(deleted)" -printf "%l\n" 2>/dev/null | sort | uniq -c | sort -n | tail -5
echo "-- journal"; journalctl --disk-usage 2>/dev/null
echo "-- auth.log top message shapes"; [ -f /var/log/auth.log ] && cut -d" " -f5- /var/log/auth.log | sed -E "s/[0-9]+/N/g" | cut -c1-110 | sort | uniq -c | sort -n | tail -4
echo "-- writers on timers/cron"; systemctl list-timers --all --no-pager 2>/dev/null | grep -E "apt-daily|snap|logrotate" | awk "{print \$(NF-1)}"
crontab -l 2>/dev/null | grep -v "^#" | grep -iE "squid|blocklist"; snap list 2>/dev/null | awk "NR>1{print \"snap:\", \$1, \$3}"' 2>&1
  echo
done
