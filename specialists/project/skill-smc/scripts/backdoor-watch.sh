#!/usr/bin/env bash
# Check, and optionally watch, an SMC box's autossh backdoor: the raw reverse tunnel that
# `autossh-teleport-openssh` keeps open to the project bastion on port 50000 + site_eclipse_siteid.
# Run this before reporting any box as unreachable — a box missing from `tsh ls` can still be up
# behind this tunnel (references/03_communication-flows.md §Backdoor SSH Access).
#
# Written 2026-10-07 for kupungarri-smc01 (wh), which drops off Teleport repeatedly. A box in a
# reboot or WAN-flap loop may hold the tunnel for only a minute or two, so a single check misses it;
# watch mode polls the bastion's listener and prints one line per UP/DOWN change.
#
# Usage:
#   scripts/backdoor-watch.sh <site|smc-host> [check|history|watch]
#
#   check    (default) is the port listening on the bastion right now
#   history  per-day count of "cannot listen to port: <port>" in the bastion's auth logs; these
#            mean the box reconnected while a stale session still held the port, so the backdoor
#            was unusable even though the box was up
#   watch    poll the listener every INTERVAL seconds for DURATION seconds, one line per change
#
# Environment:
#   INTERVAL=10      watch poll interval, seconds
#   DURATION=7200    watch length, seconds
#   UNTIL_UP=0       1 = stop watching at the first UP (for a "tell me when" background job)
#   PORT=<n>         skip the inventory lookup and use this port
#
# Site -> host -> siteid -> port is resolved from ansible-wifi's inventory, never hardcoded.
# Only the flavour -> cluster/bastion split is a fixed table (references/03_communication-flows.md).
# Read-only: runs `ss` and `grep` on the bastion, never connects onward to the SMC box. To get a
# shell once it is UP: `tsh ssh --proxy <cluster> root@<bastion>` then `ssh -p <port> root@127.0.0.1`.
#
# Requires an active `tsh login --proxy=<cluster>` session; this script does not log in for you.

set -euo pipefail

TARGET="${1:?Usage: backdoor-watch.sh <site|smc-host> [check|history|watch]}"
MODE="${2:-check}"
INTERVAL="${INTERVAL:-10}"
DURATION="${DURATION:-7200}"
UNTIL_UP="${UNTIL_UP:-0}"

INV_ROOT="/Volumes/Data/_ansible/ansible-wifi/inventories"

cluster_for_flavour() {
  case "$1" in
    nbn_accelerate|nbn_wh) echo "teleport.communitywifi.net.au cw-teleport01" ;;
    rcp|rct|wh) echo "teleport.apn.au apn-teleport01" ;;
    *) echo "" ;;
  esac
}

# Accept either a site name (kupungarri) or an SMC host (kupungarri-smc01).
case "$TARGET" in
  *-smc0[0-9]) SMC_HOST="$TARGET"; INV_FILE="$(grep -lx "$TARGET" "$INV_ROOT"/*/prod 2>/dev/null | head -1 || true)" ;;
  *)
    INV_FILE="$(grep -l "^\[${TARGET}_smc_bases\]" "$INV_ROOT"/*/prod 2>/dev/null | head -1 || true)"
    SMC_HOST=""
    if [ -n "$INV_FILE" ]; then
      SMC_HOST="$(awk -v grp="[${TARGET}_smc_bases]" '
        $0 == grp { found=1; next }
        found && /^\[/ { exit }
        found && NF { print $1; exit }
      ' "$INV_FILE")"
    fi
    ;;
esac

if [ -z "${INV_FILE:-}" ] || [ -z "$SMC_HOST" ]; then
  echo "Cannot resolve '$TARGET' in $INV_ROOT/*/prod. Use the site name or the exact SMC host." >&2
  exit 1
fi

FLAVOUR="$(basename "$(dirname "$INV_FILE")")"
read -r CLUSTER BASTION <<<"$(cluster_for_flavour "$FLAVOUR")"
if [ -z "${CLUSTER:-}" ]; then
  echo "Flavour '$FLAVOUR' is not in cluster_for_flavour(); extend it." >&2
  exit 1
fi

if [ -z "${PORT:-}" ]; then
  SITEID="$(grep -h -E '^site_eclipse_siteid:' "$INV_ROOT/$FLAVOUR/host_vars/$SMC_HOST.yml" 2>/dev/null \
    | head -1 | awk '{print $2}' | tr -d "'\"" || true)"
  if [ -z "$SITEID" ]; then
    echo "No site_eclipse_siteid in $INV_ROOT/$FLAVOUR/host_vars/$SMC_HOST.yml. Pass PORT=<50000+siteid>." >&2
    exit 1
  fi
  PORT=$((50000 + SITEID))
fi

echo "Resolved '$TARGET' -> $SMC_HOST ($FLAVOUR) -> $BASTION via $CLUSTER, backdoor port $PORT" >&2

remote() { tsh ssh --proxy "$CLUSTER" "root@$BASTION" "$1"; }

case "$MODE" in
  check)
    remote "if ss -tln | grep -qE '127\\.0\\.0\\.1:$PORT\\b'; then echo '$PORT UP'; else echo '$PORT DOWN'; fi"
    ;;
  history)
    remote "zcat -f \$(ls -tr /var/log/auth.log*) 2>/dev/null > /tmp/backdoor-watch-auth.\$\$
      echo \"auth log span: \$(head -1 /tmp/backdoor-watch-auth.\$\$ | cut -c1-15) -> \$(tail -1 /tmp/backdoor-watch-auth.\$\$ | cut -c1-15)\"
      echo \"bind failures on $PORT per day (stale session holding the port):\"
      grep 'cannot listen to port: $PORT\$' /tmp/backdoor-watch-auth.\$\$ | awk '{print \$1, \$2}' | uniq -c
      echo \"last: \$(grep 'cannot listen to port: $PORT\$' /tmp/backdoor-watch-auth.\$\$ | tail -1 | cut -c1-15)\"
      rm -f /tmp/backdoor-watch-auth.\$\$"
    ;;
  watch)
    # One tsh session for the whole watch: the loop runs on the bastion, not one login per poll.
    remote "prev=''; end=\$(( \$(date +%s) + $DURATION ))
      echo \"watch start \$(date '+%F %T %Z') port $PORT every ${INTERVAL}s for ${DURATION}s\"
      while [ \$(date +%s) -lt \$end ]; do
        if ss -tln | grep -qE '127\\.0\\.0\\.1:$PORT\\b'; then s=UP; else s=DOWN; fi
        if [ \"\$s\" != \"\$prev\" ]; then echo \"\$(date '+%F %T') $PORT \$s\"; prev=\$s; fi
        if [ '$UNTIL_UP' = 1 ] && [ \"\$s\" = UP ]; then break; fi
        sleep $INTERVAL
      done
      echo \"watch end \$(date '+%F %T')\""
    ;;
  *)
    echo "Unknown mode '$MODE' (check|history|watch)." >&2
    exit 1
    ;;
esac
