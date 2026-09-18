#!/usr/bin/env bash
# Open a tsh local-port-forward tunnel from this workstation to any device reachable from a site's
# SMC box — Cambium APs/SMs, or anything else on that site's management network. Generic Teleport
# tunneling, not tied to any one device vendor.
#
# Site -> SMC-host is resolved live from ansible-wifi's own inventory (never hardcoded here — a
# site list drifts, ansible-wifi's inventory is the canonical source): each site has a
# `[<site>_smc_bases]` group in exactly one `inventories/<flavour>/prod` file; the first host under
# that group is the SMC box to tunnel through. Only the flavour->cluster split is a small fixed
# table below — a structural fact about the two Teleport clusters (see references/01_overview.md's
# "Cluster split" table), not per-site data ansible-wifi's inventory encodes directly.
#
# Usage:
#   scripts/teleport-tunnel.sh <site> <target_ip> [local_port] [target_port] [duration_seconds]
#
# Examples:
#   scripts/teleport-tunnel.sh hope-vale 10.255.3.1 20001 443 120     # a Cambium XV2's web UI
#   scripts/teleport-tunnel.sh burringurrah 10.255.11.45              # defaults: port 20000/443/120s
#
# Defaults: local_port=20000, target_port=443, duration_seconds=120.
# Prints the localhost URL to use once the tunnel is confirmed listening, then blocks for
# duration_seconds (same lifetime as the underlying `tsh ssh ... sleep N` tunnel). Run in the
# background (`&`, or your tool's background-task support) if you need to keep working while it's
# open — this script does not background itself.
#
# Requires: an active `tsh login --proxy=<cluster>` session for the target site's cluster already
# in place — this script does not log in for you (rcp/rct/wh-flavour clusters need interactive MFA).

set -euo pipefail

SITE="${1:?Usage: teleport-tunnel.sh <site> <target_ip> [local_port] [target_port] [duration_seconds]}"
TARGET_IP="${2:?Usage: teleport-tunnel.sh <site> <target_ip> [local_port] [target_port] [duration_seconds]}"
LOCAL_PORT="${3:-20000}"
TARGET_PORT="${4:-443}"
DURATION="${5:-120}"

ANSIBLE_INVENTORY_ROOT="/Volumes/Data/_ansible/ansible-wifi/inventories"

# Flavour dirs are grouped into exactly two Teleport clusters — see references/01_overview.md's
# "Cluster split" table if this ever needs a third.
cluster_for_flavour() {
  case "$1" in
    nbn_accelerate|nbn_wh|cw) echo "teleport.communitywifi.net.au" ;;
    rcp|rct|wh|apn) echo "teleport.apn.au" ;;
    *) echo "" ;;
  esac
}

INVENTORY_FILE="$(grep -rl "^\[${SITE}_smc_bases\]" "$ANSIBLE_INVENTORY_ROOT"/*/prod 2>/dev/null | head -1 || true)"
if [ -z "$INVENTORY_FILE" ]; then
  echo "No '[${SITE}_smc_bases]' group found under $ANSIBLE_INVENTORY_ROOT/*/prod. Is '$SITE' the right site name (check ansible-wifi's own inventories directly)?" >&2
  exit 1
fi

FLAVOUR="$(basename "$(dirname "$INVENTORY_FILE")")"
SMC_HOST="$(awk -v grp="[${SITE}_smc_bases]" '
  $0 == grp { found=1; next }
  found && /^\[/ { exit }
  found && NF { print $1; exit }
' "$INVENTORY_FILE")"

if [ -z "$SMC_HOST" ]; then
  echo "Found '[${SITE}_smc_bases]' in $INVENTORY_FILE but no host listed under it." >&2
  exit 1
fi

CLUSTER="$(cluster_for_flavour "$FLAVOUR")"
if [ -z "$CLUSTER" ]; then
  echo "Site '$SITE' resolved to flavour '$FLAVOUR' (from $INVENTORY_FILE), which isn't in this script's flavour->cluster table. Extend cluster_for_flavour() — check references/01_overview.md for the right cluster." >&2
  exit 1
fi

echo "Resolved '$SITE' -> smc-host '$SMC_HOST' (flavour '$FLAVOUR', from $INVENTORY_FILE) -> cluster '$CLUSTER'" >&2
echo "Opening tunnel: localhost:${LOCAL_PORT} -> ${TARGET_IP}:${TARGET_PORT} via ${SMC_HOST}, ${DURATION}s window" >&2

tsh ssh --proxy "$CLUSTER" -L "${LOCAL_PORT}:${TARGET_IP}:${TARGET_PORT}" "root@${SMC_HOST}" sleep "$DURATION" &
TUNNEL_PID=$!

for _ in $(seq 1 20); do
  if nc -z -w1 localhost "$LOCAL_PORT" 2>/dev/null; then
    echo "Tunnel up: https://localhost:${LOCAL_PORT}/" >&2
    break
  fi
  sleep 0.5
done

wait "$TUNNEL_PID"
