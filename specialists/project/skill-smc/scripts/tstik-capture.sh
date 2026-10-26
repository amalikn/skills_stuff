#!/usr/bin/env bash
# Read-only capture of an RCT box's TSTIK state and power-reset history, plus its eth0 link history, to a local folder.
#
# usage: tstik-capture.sh <host> [outdir]          e.g. tstik-capture.sh arrkapa-smc01 ./capture
#        WAIT_UP=1 MAX_WAIT=86400 POLL=120 tstik-capture.sh <host> [outdir]   # poll Teleport until the box appears, then capture
#   TSH_PROXY  Teleport proxy (default teleport.apn.au)
#
# What and why (2026-10-07, arrkapa): the TSTIK logic is the rct-tstik Laravel app ON THE SMC (cron `php artisan update:stats`), not
# AVR firmware. Each run pings the phone UI (192.168.5.253), Sky Muster NTD (192.168.100.1), MikroTik switch (10.255.0.5), AP (10.255.0.20)
# and 8.8.8.8/1.1.1.1, and power-cycles a rail through the AVR when a counter passes its limit: switch after 11 failed switch/AP runs
# or 71 failed internet runs, NTD after 11 failed modem runs or 35 failed internet runs, phone after 11 failed UI runs.
# storage/stats.json is only the latest snapshot; the history is storage/logs/laravel.log*, rotated by size, so only a few days, UTC.
# The limits above count cron runs. Read as every minute on arrkapa (2026-10-07); root's crontab on warehouse-rct01, alice-well, cave-hill and
# adjamarragu (2026-10-26) runs it every 5 minutes (switch reset after ~55 min of failed pings there). 04-cron.txt shows the box's own schedule.
# Each run also reads the AVR over serial (~24 reads, `Total Read Data[126,...]`); `Unable to read the data from AVR` means the read failed.
# Every RCT SMC has an AVR except the bench Pi php-rct-smc01 (operator, 2026-10-26). laravel.log also holds many network ERROR lines (cURL 6/28,
# socket_connect) that are normal on satellite sites; 07-tstik-avr-and-errors.txt counts them apart from AVR errors.
# The kernel log since boot holds eth0 link up/down events (cable or switch power) - it survives until the box reboots.
# storage/config.json is NOT copied (site configuration, may hold credentials).
set -u
host=${1:?usage: tstik-capture.sh <host> [outdir]}
proxy=${TSH_PROXY:-teleport.apn.au}
out=${2:-./tstik-capture-${host}-$(date +%Y%m%d_%H%M)}

if [ "${WAIT_UP:-0}" = 1 ]; then
  deadline=$(( $(date +%s) + ${MAX_WAIT:-86400} ))
  until tsh ls --proxy="$proxy" 2>/dev/null | awk '{print $1}' | grep -qx "$host"; do
    [ "$(date +%s)" -ge "$deadline" ] && { echo "$(date '+%F %T') $host never appeared in Teleport"; exit 3; }
    sleep "${POLL:-120}"
  done
  echo "$(date '+%F %T') $host is in Teleport, capturing"
fi

mkdir -p "$out"
run() {  # run <name> <remote command>
  tsh --proxy="$proxy" ssh "root@$host" "$2" > "$out/$1" 2>&1
  echo "$1: $(wc -l < "$out/$1" | tr -d ' ') lines"
}
T=/var/www/html/rct-tstik/storage
run 00-identity.txt "hostname; uptime; date; mount | grep -c ' / type overlay' | sed 's/^/overlay_root_mounts=/'"
run 01-stats.json "cat $T/stats.json"
# laravel.log is rotated by size (rise-logcaps logrotate): laravel.log, .1, .N.gz - a few days in all. Timestamps are UTC.
run 02-tstik-actions.log "cd $T/logs && ls -la && zgrep -hE 'Resetting|Failed [0-9]+ Times|Emergency|Maintenance' \$(ls -tr laravel.log*) | tail -5000"
run 03-tstik-resets-per-day.txt "cd $T/logs && echo 'UTC day / action / count'; zgrep -hE 'Resetting (Switch|Modem|Phone)' \$(ls -tr laravel.log*) | sed -E 's/^\\[([0-9-]+) .*(Resetting [A-Za-z]+).*/\\1 \\2/' | sort | uniq -c; echo 'log span:'; zcat -f \$(ls -tr laravel.log*) | grep -m1 -oE '^\\[[0-9-]+ [0-9:]+\\]'; tail -1 laravel.log | grep -oE '^\\[[0-9-]+ [0-9:]+\\]'"
run 04-cron.txt "crontab -l 2>/dev/null | grep -i tstik"
run 05-kernel-link.log "journalctl -k --no-pager -o short-iso 2>/dev/null | grep -iE 'eth0|genet|link is|carrier|usb.*(disconnect|reset)' | tail -2000"
run 06-eth0-counters.txt "ip -s -s link show eth0; for d in eth0.500 eth0.501 vlan521 vlan522; do ip -s link show \$d 2>/dev/null | head -6; done; ethtool eth0 2>/dev/null"
run 07-tstik-avr-and-errors.txt "cd $T/logs && echo 'file / AVR reads / empty reads / AVR errors / local.ERROR'; for f in \$(ls -tr laravel.log*); do printf '%s ' \$f; zcat -f \$f | awk '/Total Read Data\\[126/{r++} /Total Read Data\\[\\]/{e++} /Unable to read the data from AVR/{a++} /local\\.ERROR/{x++} END{print r+0, e+0, a+0, x+0}'; done; echo 'error kinds (all files):'; zcat -f \$(ls -tr laravel.log*) | grep -aoE 'local\\.(ERROR|CRITICAL|ALERT|EMERGENCY): [^{[]{0,70}' | sort | uniq -c | sort -rn | head -15"
echo "saved to $out"
