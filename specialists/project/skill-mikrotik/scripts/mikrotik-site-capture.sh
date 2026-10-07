#!/usr/bin/env bash
# Deep read-only capture of one site's MikroTiks (switch and AP) behind an SMC, for incident analysis.
#
# usage: mikrotik-site-capture.sh <smc-host> <outdir>
#        WAIT_UP=1 MAX_WAIT=86400 POLL=120 mikrotik-site-capture.sh <smc-host> <outdir>   # wait for the SMC to appear in Teleport first
#   DEVICES  MikroTik IPs (default "10.255.0.5 10.255.0.20")
#
# Captures per device: identity, resource (uptime, version), routerboard, health (voltage, temperature), interface detail
# (link-downs, last link-down time), ethernet stats (FCS/alignment errors), one-shot port monitor (speed, duplex, link partner),
# bridge ports and VLANs, the full in-memory log, and `/export terse show-sensitive=no` style config (RouterOS 7: `/export terse`
# hides sensitive values by default; hide-sensitive is the 6.x flag). The RouterOS memory log is lost when the device reboots, so
# capture before any power-cycle.
set -u
smc=${1:?usage: mikrotik-site-capture.sh <smc-host> <outdir>}; out=${2:?outdir}
here=$(cd "$(dirname "$0")" && pwd)
proxy=${TSH_PROXY:-teleport.apn.au}
if [ "${WAIT_UP:-0}" = 1 ]; then
  deadline=$(( $(date +%s) + ${MAX_WAIT:-86400} ))
  until tsh ls --proxy="$proxy" 2>/dev/null | awk '{print $1}' | grep -qx "$smc"; do
    [ "$(date +%s)" -ge "$deadline" ] && { echo "$(date '+%F %T') $smc never appeared in Teleport"; exit 3; }
    sleep "${POLL:-120}"
  done
  echo "$(date '+%F %T') $smc is in Teleport, capturing"
fi
mkdir -p "$out"
for ip in ${DEVICES:-10.255.0.5 10.255.0.20}; do
  "$here/mikrotik-exec.sh" "$smc" "$ip" \
    '/system identity print' '/system resource print' '/system routerboard print' '/system health print' \
    '/interface print detail without-paging' '/interface ethernet print stats without-paging' \
    '/interface ethernet monitor [find] once' '/interface bridge port print without-paging' \
    '/interface bridge vlan print without-paging' '/ip address print' '/log print without-paging' \
    '/export terse' > "$out/${smc}_${ip}.txt" 2>&1
  echo "$ip: $(wc -l < "$out/${smc}_${ip}.txt" | tr -d ' ') lines -> $out/${smc}_${ip}.txt"
done
