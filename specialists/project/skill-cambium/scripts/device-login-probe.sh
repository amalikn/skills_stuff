#!/usr/bin/env bash
# Find which KeePass entry logs in to a device behind an SMC, over SSH, without exposing any password. Read-only.
#
# usage: device-login-probe.sh <smc-host> <device-ip> '<read-only command>' <entry> [<entry> ...]
#   e.g. device-login-probe.sh canteen-creek-smc01 10.255.0.21 'show dashboard' \
#          cambium-devices/epmp-ap cambium-devices/epmp-ap-legacy cambium-devices/epmp-sm cambium-devices/epmp-sm-legacy
#   PTY=1      type the command into an interactive session (CLIs that ignore an exec command); PTY_WAIT seconds to wait for output
#   LINES_OUT  lines of output to print on success (default 25)
#   TSH_PROXY  Teleport proxy (default teleport.apn.au; nbn sites use teleport.communitywifi.net.au)
#
# One password prompt per entry (NumberOfPasswordPrompts=1), entries tried in the order given, stops at the first that works and prints
# the entry name and the first lines of the command output. The password goes from `kp` into SSHPASS for sshpass -e on this Mac; the SMC
# only forwards TCP (tsh ssh -N -L), so nothing secret reaches the Teleport audit log or Graylog (references/02_device-access-and-vault.md).
# Space the probes: some families throttle rapid logins (R195P dropbear, references/06_device-api-cli-reference.md).
set -u
smc=${1:?usage: device-login-probe.sh <smc> <ip> '<cmd>' <entry>...}; ip=${2:?ip}; cmd=${3:?command}; shift 3
[ $# -ge 1 ] || { echo "give at least one KeePass entry" >&2; exit 2; }
proxy=${TSH_PROXY:-teleport.apn.au}
port=$(( 20000 + RANDOM % 20000 ))
tsh --proxy="$proxy" ssh -N -L "127.0.0.1:${port}:${ip}:22" "root@${smc}" >/dev/null 2>&1 &
fwd=$!
trap 'kill $fwd 2>/dev/null; wait $fwd 2>/dev/null' EXIT
for _ in $(seq 1 30); do nc -z 127.0.0.1 "$port" 2>/dev/null && break; sleep 1; done
nc -z 127.0.0.1 "$port" 2>/dev/null || { echo "$smc $ip: port 22 not reachable through the SMC" >&2; exit 4; }

for entry in "$@"; do
  user=$(kp show -a UserName "$entry" 2>/dev/null) || { echo "$entry: not in KeePass"; continue; }
  SSHPASS=$(kp show -s -a Password "$entry" 2>/dev/null); export SSHPASS
  sshopts=(-p "$port" -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=20 -o PubkeyAuthentication=no
           -o NumberOfPasswordPrompts=1)
  if [ "${PTY:-0}" = 1 ]; then
    # Some CLIs (ePMP 1000 Hotspot, 2026-10-07) accept the login but print nothing for a non-interactive command: type it into a PTY session.
    out=$( { sleep 3; printf '%s\n' "$cmd"; sleep "${PTY_WAIT:-6}"; printf 'exit\n'; sleep 1; } | SSH_ASKPASS_REQUIRE=never sshpass -e ssh -tt "${sshopts[@]}" \
          "${user}@127.0.0.1" 2>&1 | tr -d '\r')
  else
    out=$(SSH_ASKPASS_REQUIRE=never sshpass -e ssh "${sshopts[@]}" "${user}@127.0.0.1" "$cmd" 2>&1 | tr -d '\r')
  fi
  unset SSHPASS
  case "$out" in
    *"Permission denied"*|*"Authentication failed"*|*"Too many authentication"*) echo "$smc $ip: $entry ($user) rejected" ;;
    "") echo "$smc $ip: $entry ($user) UNCONFIRMED - login not refused but no output (2026-10-07: the ePMP 1000 Hotspot did this for a password its web login rejects)" ;;
    *) echo "$smc $ip: $entry ($user) ACCEPTED"; printf '%s\n' "$out" | head -${LINES_OUT:-25}; exit 0 ;;
  esac
  sleep "${GAP:-5}"
done
echo "$smc $ip: no entry accepted"; exit 1
