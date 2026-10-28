#!/usr/bin/env bash
# pin-funnel-hourly.sh — read-only hourly captive-portal funnel for SMC boxes, yesterday vs today.
#
# ORIGIN: written 2026-10-28 when sites reported low PIN use the morning after the PHP CVE-2026-109618
# upgrade. It answers "did a change break issuance, or did fewer users reach the portal?" by placing
# each stage of the funnel side by side per hour (see ../../references/14_pin-activation-diagnosis.md §14.9):
#   DHCPACK       clients on the WiFi (journal)
#   squid / 302   HTTP from unpinned clients on 3128, and the redirects squid sent to the portal
#   apache        all portal hits (access.log), and wifi/access 302 (PIN issued) / 200 (PIN refused)
# plus dpkg upgrades in the window, so a change time can be lined up against the hour the funnel moved.
# A drop that starts at squid (redirects fall, DHCP steady) is upstream of the portal and its PHP;
# a drop that starts at wifi/access (302 falls, 200 or 5xx rise) is the portal itself.
#
# SAFETY CONTRACT: remote commands read logs only; one temp file in /tmp is written and removed. Host names are the only input.
#
# Usage
#   ./pin-funnel-hourly.sh --proxy teleport.communitywifi.net.au galiwinku-smc01 doomadgee-smc01
set -euo pipefail

# remote_probe: print the remote read-only script on stdout.
#   Args: none.
#   Returns: the bash text piped to each SMC.
remote_probe() {
    cat <<'EOF'
L=/var/log/apache2; Q=/var/log/squid
y=$(date -d yesterday +%d/%b/%Y); t=$(date +%d/%b/%Y)
echo "## $(hostname) at $(date '+%F %T %Z')"
echo "dpkg upgrades since yesterday:"
grep -h "^$(date -d yesterday +%F)\|^$(date +%F)" /var/log/dpkg.log | grep ' upgrade ' | awk '{print "  "$1, substr($2,1,5), $4, $6}' | sort -u | head -15
for d in "$y" "$t"; do
  echo "day $d  hour: dhcpack squid squid302 apache issued302 refused200"
  since=$(date -d "$(echo "$d" | tr / ' ')" +%F)
  journalctl --since "$since" --until "$since 23:59:59" --no-pager 2>/dev/null | grep DHCPACK \
    | awk '{print "D", substr($3,1,2)}' > /tmp/.pf.$$
  zcat -f $Q/access.log $Q/access.log.1 2>/dev/null | awk -v d="$d" '{if (strftime("%d/%b/%Y",$1)==d) {h=strftime("%H",$1); print "S", h; if ($4 ~ /\/302$/) print "R", h}}' >> /tmp/.pf.$$
  zcat -f $L/access.log $L/access.log.1 2>/dev/null | grep -F "[$d:" \
    | awk '{split($4,a,":"); print "A", a[2]; if ($7 ~ /wifi\/access/) {if ($9==302) print "I", a[2]; if ($9==200) print "F", a[2]}}' >> /tmp/.pf.$$
  awk '{c[$1" "$2]++; h[$2]=1} END {for (k in h) printf "  %s: %6d %6d %6d %6d %6d %6d\n", k, c["D "k], c["S "k], c["R "k], c["A "k], c["I "k], c["F "k]}' /tmp/.pf.$$ | sort
  rm -f /tmp/.pf.$$
done
EOF
}

# main: run the probe on each host through Teleport.
#   Args: --proxy <teleport proxy>, then one or more SMC host names.
#   Returns: exit 0; a host that fails prints its error and the loop continues.
#   Raises: exit 2 on missing arguments.
main() {
    [[ ${1:-} == --proxy && -n ${2:-} && -n ${3:-} ]] || { echo "usage: $0 --proxy <proxy> <host> [<host> ...]" >&2; exit 2; }
    local proxy=$2; shift 2
    for host in "$@"; do
        remote_probe | timeout 180 tsh --proxy="$proxy" ssh "root@$host" 'bash -s' || echo "## $host: probe failed rc=$?"
    done
}

main "$@"
