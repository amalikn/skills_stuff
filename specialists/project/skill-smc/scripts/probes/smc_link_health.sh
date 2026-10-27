#!/usr/bin/env bash
# Read an SMC's uplink health over Teleport: is a Teleport, backdoor or slow-run problem the box, Teleport or the site's link? Read-only.
#
# usage: smc_link_health.sh <smc-host> [--proxy <teleport proxy>] [--pings N]
#   e.g. smc_link_health.sh banana-well-smc01
#        smc_link_health.sh koonibba-smc01 --proxy teleport.communitywifi.net.au --pings 30
#
# Prints, from the box: clock and NTP sync; packet loss and RTT to the first hop (default gateway) and to the Teleport proxy (loss already at
# the first hop is the site link, not Teleport); Teleport warn/error lines per 10 minutes over the last hour and the most frequent kinds;
# the session-upload backlog; the autossh backdoor's restart count and last lines; and the WAN rate over 10 s (a lossy link with an idle WAN
# is the link itself, not load). A gateway may rate-limit pings to itself: trust loss at the first hop when the proxy path shows it
# too (banana-well 10:1 gw 33%, proxy 0% on 6 pings; 30 pings each: both 30%). Nothing is changed on the box. Runtime: about 1 minute with 20 pings (more on a satellite link).
# Needs: tsh logged in to the proxy's cluster.
# Exit status: the remote shell's status; 2 bad usage.
# Origin: banana-well-smc01 Teleport errors, ansible-wifi PHP rollout 2026-10-27 (references/03_communication-flows.md, banana-well entry):
# 1,595 errors an hour, 30-40% loss at the first hop with the WAN idle, clock synced: the link.
set -u

usage() {
  # Print the header comment as help.
  #
  # Args: none.
  # Returns: 0; writes the usage text to stdout.
  sed -n '2,17p' "$0" | sed 's/^# \{0,1\}//'
}

host="" proxy="" pings=20
while [ $# -gt 0 ]; do
  case "$1" in
    -h|--help) usage; exit 0 ;;
    --proxy) proxy="${2:-}"; shift 2 ;;
    --pings) pings="${2:-}"; shift 2 ;;
    -*) usage; exit 2 ;;
    *) host="$1"; shift ;;
  esac
done
[ -n "$host" ] || { usage; exit 2; }
case "$pings" in ''|*[!0-9]*) echo "--pings needs a number" >&2; exit 2 ;; esac

remote=$(cat <<'EOF'
p=__PINGS__
echo "== $(hostname)  clock $(date -u +%FT%TZ)  ntp_synced=$(timedatectl show -p NTPSynchronized --value 2>/dev/null)  $(uptime -p)"
gw=$(ip route | awk '/^default/{print $3; exit}')
proxy=__PROXY__
echo "== loss to first hop ($gw) and to the proxy (${proxy:-unknown})"
[ -n "$gw" ] && ping -c "$p" -i 0.5 -q -W 3 "$gw" 2>&1 | tail -2 | sed 's/^/  gw    /'
[ -n "$proxy" ] && ping -c "$p" -i 0.5 -q -W 3 "$proxy" 2>&1 | tail -2 | sed 's/^/  proxy /'
echo "== teleport warn/error lines per 10 min, oldest first (last hour)"
for m in 60 50 40 30 20 10; do
  printf '  -%sm %s\n' "$m" "$(journalctl -u teleport --since "-$m min" --until "-$((m - 10)) min" --no-pager 2>/dev/null | grep -ciE 'error|warn')"
done
echo "== most frequent teleport error kinds (last hour)"
journalctl -u teleport --since '-60 min' --no-pager 2>/dev/null | grep -oE 'Original Error: [^]]{0,110}' | sort | uniq -c | sort -rn | head -5
echo "== session uploads pending: $(find /var/lib/teleport/log/upload -type f 2>/dev/null | wc -l) file(s), $(du -sh /var/lib/teleport/log/upload 2>/dev/null | cut -f1)"
echo "== autossh backdoor"
for u in $(systemctl list-units --no-legend --plain 'autossh*' 2>/dev/null | awk '{print $1}'); do
  echo "  $u $(systemctl is-active "$u")  restarts: $(journalctl -u "$u" --no-pager 2>/dev/null | grep -oE 'starting ssh \(count [0-9]+\)' | tail -1)"
done
dev=$(ip route | awk '/^default/{print $5; exit}')
if [ -n "$dev" ]; then
  r1=$(cat "/sys/class/net/$dev/statistics/rx_bytes"); t1=$(cat "/sys/class/net/$dev/statistics/tx_bytes"); sleep 10
  r2=$(cat "/sys/class/net/$dev/statistics/rx_bytes"); t2=$(cat "/sys/class/net/$dev/statistics/tx_bytes")
  echo "== WAN $dev over 10 s: rx $(( (r2 - r1) * 8 / 10000 )) kbit/s, tx $(( (t2 - t1) * 8 / 10000 )) kbit/s"
fi
EOF
)
# The proxy to ping is the one the controller reaches the box through: --proxy, else the logged-in tsh profile's host.
target=${proxy:-$(tsh status 2>/dev/null | grep -m1 'Profile URL' | grep -oE 'https?://[^[:space:]]+')}
target=${target#https://}; target=${target%%:*}; target=${target%%/*}
remote=${remote//__PINGS__/$pings}
remote=${remote//__PROXY__/$target}
args=()
[ -n "$proxy" ] && args+=(--proxy="$proxy")
exec tsh ${args[@]+"${args[@]}"} ssh "root@$host" "$remote"
