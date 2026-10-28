#!/usr/bin/env bash
# pin-fleet-check.sh — read-only one-line-per-SMC portal health check after a change batch.
#
# ORIGIN: written 2026-10-28 to clear the 11 nbn_accelerate SMCs patched by PHP CVE-2026-109618 the night before, after two
# sites reported low PIN use (see ../../references/14_pin-activation-diagnosis.md §14.9). One line per host:
#   php            running PHP version and the installed php8.1-common Debian revision
#   up             time of the last php8.1-common dpkg upgrade (line a change up against the numbers)
#   yday / today   wifi/access 302 issued / 200 refused, midnight to the current hour, so the two days compare like for like
#   deny0_hours    today's hours with more than 300 squid lines and zero TCP_DENIED: unpinned clients were not caught
#                  by the portal (the 2026-10-28 Galiwinku fail-open); a short gap on a quiet site can fall under 300 and be missed
#   php_errs       PHP fatal/parse/warning or segfault lines in Apache error.log (today's file only, it rotates daily)
#   portal         HTTP code from http://127.0.0.1/
#   marks          ECLIPSE_MARK rules (PINs valid now; boxes that share a site list, such as aurukun-smc01..03, show the same count)
# Follow up a flagged host with pin-funnel-hourly.sh for the per-hour picture.
#
# SAFETY CONTRACT: remote commands read logs, dpkg, iptables -S and one local curl. Host names are the only input.
#
# Usage
#   ./pin-fleet-check.sh --proxy teleport.communitywifi.net.au [--parallel 6] amata-smc01 galiwinku-smc01 ...
set -euo pipefail

# remote_probe: print the remote read-only script on stdout.
#   Args: none.
#   Returns: the bash text piped to each SMC; it prints one summary line.
remote_probe() {
    cat <<'EOF'
H=$(date +%H); y=$(date -d yesterday +%d/%b/%Y); t=$(date +%d/%b/%Y)
L=/var/log/apache2; Q=/var/log/squid
pin() { zcat -f $L/access.log $L/access.log.1 $L/other_vhosts_access.log $L/other_vhosts_access.log.1 2>/dev/null | grep -F "[$1:" | grep 'wifi/access' \
  | awk -v H=$H '{split($4,a,":"); if (a[2]<H) {if($9==302) s++; if($9==200) f++}} END{printf "%d/%d", s, f}'; }
deny0=$(zcat -f $Q/access.log 2>/dev/null | awk -v d="$(date +%d)" '{if (strftime("%d",$1)==d) {h=strftime("%H",$1); n[h]++; if ($4 ~ /DENIED/) x[h]++}} END{for (k in n) if (n[k]>300 && x[k]+0==0) printf "%s,", k}')
up=$(grep -h ' upgrade php8.1-common' /var/log/dpkg.log 2>/dev/null | tail -1 | awk '{print $1"_"substr($2,1,5)}')
perr=$(grep -ciE 'PHP (Fatal|Parse|Warning)|segfault|exit signal' $L/error.log 2>/dev/null || true)
portal=$(curl -s -o /dev/null -w '%{http_code}' --max-time 10 http://127.0.0.1/)
printf "%-24s php=%s/%s up=%s until=%sh yday=%s today=%s deny0_hours=[%s] php_errs=%s portal=%s marks=%s\n" \
  "$(hostname)" "$(php -r 'echo PHP_VERSION;' 2>/dev/null)" "$(dpkg-query -W -f='${Version}' php8.1-common 2>/dev/null | sed 's/.*ubuntu//')" \
  "${up:-none}" "$H" "$(pin $y)" "$(pin $t)" "${deny0%,}" "${perr:-0}" "$portal" "$(iptables -t mangle -S ECLIPSE_MARK 2>/dev/null | grep -c CONNMARK)"
EOF
}

# main: run the probe on every host through Teleport, a bounded number at a time, and print the lines sorted by host.
#   Args: --proxy <teleport proxy>, optional --parallel <n> (default 6), then one or more SMC host names.
#   Returns: exit 0; a host that fails prints "<host> FAILED rc=<n>" in its place.
#   Raises: exit 2 on missing arguments.
main() {
    local proxy="" parallel=6
    while [[ ${1:-} == --* ]]; do
        case $1 in
            --proxy) proxy=${2:-}; shift 2 ;;
            --parallel) parallel=${2:-6}; shift 2 ;;
            *) echo "unknown option $1" >&2; exit 2 ;;
        esac
    done
    [[ -n $proxy && $# -gt 0 ]] || { echo "usage: $0 --proxy <proxy> [--parallel n] <host> [<host> ...]" >&2; exit 2; }
    local probe; probe=$(remote_probe)
    export proxy probe
    printf '%s\n' "$@" | xargs -P "$parallel" -I{} bash -c \
        'printf "%s" "$probe" | timeout 120 tsh --proxy="$proxy" ssh "root@$1" "bash -s" 2>/dev/null || echo "$1 FAILED rc=$?"' _ {} | sort
}

main "$@"
