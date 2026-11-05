#!/bin/sh
# Remote half of smc_gateway_loss.sh: runs ON the SMC (sent on stdin to `sh -s <pings>`). Read-only.
# Prints one line: "gw=<ip> loss=<pct> rtt=<ms> rx=<kbit/s> tx=<kbit/s>" for the default gateway (the site link's first hop) and the WAN rate
# over 5 s; loss and rtt are "?" when ping printed none. POSIX sh: the SMC's /bin/sh is dash.
# With a second argument "speed", also: dl=<KB/s> from a 5 MB Cloudflare speed-test download and bb=<KB/s> from bitbucket.org over HTTPS
# (both to /dev/null, 60 s cap each), to tell a slow site link from a slow destination (NBN ticket evidence, 2026-11-05).
# Run: sh smc_gateway_loss_remote.sh <pings> [speed]   (normally: tsh ssh root@<smc> "sh -s 20 speed" < smc_gateway_loss_remote.sh)
# Exit: 0.
pings=${1:-20}
mode=${2:-}
gw=$(ip route show default | awk '{print $3; exit}')
dev=$(ip route show default | awk '{print $5; exit}')
out=$(ping -c "$pings" -i 0.3 -W 3 "$gw" 2>/dev/null)
loss=$(printf '%s\n' "$out" | grep -oE '[0-9.]+% packet loss' | cut -d% -f1)
rtt=$(printf '%s\n' "$out" | awk -F/ '/^rtt|^round-trip/ {print $5}')
r1=$(cat "/sys/class/net/$dev/statistics/rx_bytes")
t1=$(cat "/sys/class/net/$dev/statistics/tx_bytes")
sleep 5
r2=$(cat "/sys/class/net/$dev/statistics/rx_bytes")
t2=$(cat "/sys/class/net/$dev/statistics/tx_bytes")
speed=""
if [ "$mode" = speed ]; then
  dl=$(curl -s -o /dev/null --max-time 60 -w '%{speed_download}' 'https://speed.cloudflare.com/__down?bytes=5000000' | awk '{printf "%.0f", $1 / 1024}')
  bb=$(curl -s -o /dev/null --max-time 60 -w '%{speed_download}' 'https://bitbucket.org/' | awk '{printf "%.0f", $1 / 1024}')
  speed=" dl=${dl:-?} bb=${bb:-?}"
fi
echo "gw=$gw loss=${loss:-?} rtt=${rtt:-?} rx=$(((r2 - r1) * 8 / 5000)) tx=$(((t2 - t1) * 8 / 5000))$speed"
