#!/usr/bin/env bash
# Run a command or script on an SMC box through its autossh backdoor when Teleport cannot reach it.
#
# usage: backdoor_exec.sh <site|smc-host> [command]          # command string, or
#        backdoor_exec.sh <site|smc-host> - < script.sh       # script on stdin, run with bash -s
#   e.g. backdoor_exec.sh darlngunaya 'hostname; uptime'
#        backdoor_exec.sh bungardi - < php_package_probe_body.sh
#
# Resolves host, bastion, cluster and port with backdoor-watch.sh, checks the port is listening, then connects
# `ssh -p <port> root@127.0.0.1` from the bastion via a ProxyCommand (`tsh ssh ... nc`), with the fleet root password read
# from KeePassXC (`kp show -s -a Password "$KP_ENTRY"`, default `Network/SMC`) into SSHPASS for `sshpass -e`: the password
# never appears in an argument, a log line or this script's output. Before running anything it reads the box's hostname
# and stops when it is not the target: a backdoor port can be held by another box (family-friendly-smc01's 50501 answered
# as nocprov-smc01, 2026-10-22). FORCE=1 runs anyway. This path has no Teleport session recording: use it only where
# `tsh ssh` itself is what's broken, and for reads unless a change is approved (nbn_wh: reads only, operator 2026-10-22).
# Needs: tsh logged in to the cluster, kp, sshpass, nc on the bastion.
# Exit status: the remote command's status; 2 bad usage; 3 port down; 4 hostname mismatch; 5 no credential.
# Origin: ansible-wifi PHP CVE assessment, 2026-10-22 (references/03_communication-flows.md §Backdoor SSH Access).
set -u

usage() {
  # Print the header comment as help.
  #
  # Args: none.
  # Returns: 0; writes the usage text to stdout.
  sed -n '2,20p' "$0" | sed 's/^# \{0,1\}//'
}

case "${1:-}" in
  ""|-h|--help) usage; [ -n "${1:-}" ] && exit 0; exit 2 ;;
esac
TARGET="$1"; shift
CMD="${1:-hostname}"
HERE="$(cd "$(dirname "$0")" && pwd)"
KP_ENTRY="${KP_ENTRY:-Network/SMC}"

# backdoor-watch.sh prints "Resolved '<t>' -> <host> (<flavour>) -> <bastion> via <cluster>, backdoor port <port>" on
# stderr and "<port> UP|DOWN" on stdout.
check="$(bash "$HERE/backdoor-watch.sh" "$TARGET" check 2>&1)" || { echo "$check" >&2; exit 2; }
resolved="$(echo "$check" | grep '^Resolved ')"
host="$(echo "$resolved" | sed -E "s/^Resolved '[^']*' -> ([^ ]+) .*/\1/")"
bastion="$(echo "$resolved" | sed -E 's/.* -> ([^ ]+) via .*/\1/')"
cluster="$(echo "$resolved" | sed -E 's/.* via ([^,]+),.*/\1/')"
port="$(echo "$resolved" | sed -E 's/.*backdoor port ([0-9]+).*/\1/')"
echo "$resolved" >&2
if ! echo "$check" | grep -q "^$port UP"; then
  echo "backdoor port $port is DOWN on $bastion" >&2
  exit 3
fi

SSHPASS="$(kp show -s -a Password "$KP_ENTRY" 2>/dev/null)"
if [ -z "$SSHPASS" ]; then
  echo "no credential from kp entry '$KP_ENTRY'" >&2
  exit 5
fi
export SSHPASS

bd_ssh() {
  # Open one ssh session to the box through the bastion's backdoor port.
  #
  # Args:
  #   $@: the remote command (one string is safest).
  # Returns: the remote command's exit status; stdin is passed through.
  sshpass -e ssh -q -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR \
    -o PreferredAuthentications=password -o PubkeyAuthentication=no -o ConnectTimeout=30 \
    -o ProxyCommand="tsh ssh --proxy=$cluster root@$bastion nc 127.0.0.1 $port" \
    "root@backdoor-$port" "$@"
}

actual="$(bd_ssh hostname </dev/null | tr -d '\r')"
if [ "$actual" != "$host" ] && [ "${FORCE:-0}" != 1 ]; then
  echo "port $port answers as '$actual', not '$host'; stopping (FORCE=1 to run anyway)" >&2
  unset SSHPASS
  exit 4
fi
echo "connected: $actual via $bastion:$port" >&2

if [ "$CMD" = "-" ]; then
  bd_ssh "bash -s"
else
  bd_ssh "$CMD" </dev/null
fi
rc=$?
unset SSHPASS
exit "$rc"
