#!/usr/bin/env bash
# Read an SMC's uplink health over Teleport: is a Teleport, backdoor or slow-run problem the box, Teleport or the site's link? Read-only.
#
# usage: smc_link_health.sh <smc-host> [--proxy <teleport proxy>] [--pings N]
#   e.g. smc_link_health.sh banana-well-smc01
#        smc_link_health.sh koonibba-smc01 --proxy teleport.communitywifi.net.au --pings 30
#
# Prints, from the box: clock and NTP sync; for every WAN leg, packet loss and RTT to its first hop and to the Teleport proxy (loss already
# at the first hop is the site link, not Teleport). Legs: each WAN interface has its own routing table (named after it, filled by
# ansible-wifi's dhclient hook `add_default_gateway`) and a rule `from <its address> lookup <it>`; the main table holds only a multipath
# default over all legs, written by the portal (`model/wifi/gateway.php`, `nexthop ... weight 1`), so one ping to the proxy measures
# whichever leg the flow hash picks. Each leg is pinged from its own address so its rule picks its table (2026-11-06, bidyadanga and
# warburton). Then: Teleport warn/error lines per 10 minutes over the last hour and the most frequent kinds;
# the session-upload backlog; the autossh backdoor's restart count and last lines; and the WAN rate over 10 s (a lossy link with an idle WAN
# is the link itself, not load). A gateway may rate-limit pings to itself: trust loss at the first hop when the proxy path shows it
# too (banana-well 10:1 gw 33%, proxy 0% on 6 pings; 30 pings each: both 30%). Nothing is changed on the box. Runtime: about 20 s per leg with 20 pings (pings run leg by leg), plus 10 s.
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
proxy=__PROXY__
# One line per leg: the rules `from <address> lookup <table>` (not local, main, default); a box without them falls back to the main default.
legs=$(ip rule | awk '$2=="from" && $3!="all" && $4=="lookup" && $5!~/^(local|main|default)$/ {print $3, $5}')
# A rule whose address is no longer on the box is stale (the hook deletes only the rule for the new address): reported, not pinged.
stale=$(echo "$legs" | while read -r src tbl; do [ -n "$src" ] && ! ip -4 -o addr show | grep -qw "$src" && echo "$src->$tbl"; done | tr '\n' ' ')
legs=$(echo "$legs" | while read -r src tbl; do [ -n "$src" ] && ip -4 -o addr show | grep -qw "$src" && echo "$src $tbl"; done)
# Legs with no table of their own (role starlink, others): a single-path default in main, measured by binding to the device.
ruled=$(echo "$legs" | while read -r _ tbl; do ip route show table "$tbl" default 2>/dev/null | grep -oE 'dev [^ ]+' | head -1 | cut -d' ' -f2; done)
plain=$(ip route show table main default | grep -E '^default via' | grep -oE 'dev [^ ]+' | cut -d' ' -f2 | grep -vxF "$ruled" || true)
for d in $plain; do legs=$(printf '%s\n%s' "$legs" "dev:$d main"); done
[ -n "$legs" ] || legs="- main"
[ -n "$stale" ] && echo "== stale rules (address not on the box): $stale"
echo "== loss per WAN leg to its first hop and to the proxy (${proxy:-unknown}), $p pings each"
echo "$legs" | while read -r src tbl; do
  [ -z "$src" ] && continue
  if [ "${src#dev:}" != "$src" ]; then
    dev=${src#dev:}; gw=$(ip route show table main default dev "$dev" 2>/dev/null | grep -oE 'via [0-9.]+' | head -1 | cut -d' ' -f2); opt=(-I "$dev")
  else
    gw=$(ip route show table "$tbl" default 2>/dev/null | grep -oE 'via [0-9.]+' | head -1 | cut -d' ' -f2)
    dev=$(ip route show table "$tbl" default 2>/dev/null | grep -oE 'dev [^ ]+' | head -1 | cut -d' ' -f2)
    opt=(); [ "$src" != "-" ] && opt=(-I "$src")
  fi
  echo "  leg $tbl (dev ${dev:-?}, src $src, gw ${gw:-none})"
  [ -n "$gw" ] && ping "${opt[@]}" -c "$p" -i 0.5 -q -W 3 "$gw" 2>&1 | tail -2 | sed 's/^/    gw    /'
  [ -n "$proxy" ] && ping "${opt[@]}" -c "$p" -i 0.5 -q -W 3 "$proxy" 2>&1 | tail -2 | sed 's/^/    proxy /'
done
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
devs=$(printf '%s\n%s\n' "$ruled" "$plain" | grep -v '^$' | sort -u)
if [ -n "$devs" ]; then
  declare -A r1 t1
  for d in $devs; do r1[$d]=$(cat "/sys/class/net/$d/statistics/rx_bytes"); t1[$d]=$(cat "/sys/class/net/$d/statistics/tx_bytes"); done
  sleep 10
  echo "== WAN rate per leg over 10 s"
  for d in $devs; do
    echo "  $d: rx $(( ($(cat /sys/class/net/$d/statistics/rx_bytes) - ${r1[$d]}) * 8 / 10000 )) kbit/s, tx $(( ($(cat /sys/class/net/$d/statistics/tx_bytes) - ${t1[$d]}) * 8 / 10000 )) kbit/s"
  done
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
