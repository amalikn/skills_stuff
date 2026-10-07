#!/usr/bin/env bash
# Run RouterOS CLI commands on a MikroTik behind an SMC, through a Teleport port-forward. Read-only by default.
#
# usage: mikrotik_exec.sh <smc-host> <mikrotik-ip> '<routeros command>' ['<command>' ...]
#   e.g. mikrotik_exec.sh delye-smc01 10.255.0.5 '/system resource print' '/log print where topics~"interface"'
#   TSH_PROXY   Teleport proxy (default teleport.apn.au)
#   MT_ENTRY    KeePass entry holding UserName/Password (default "Network/mikrotik switch & metal ap")
#   MT_ALLOW_WRITE=1  allow commands that are not print/monitor/export (default: refuse them)
#   MT_PY       Python for the output rewrite (default python3; the justfile sets the pinned working-cache venv)
#   MT_BATCH=0  one SSH session per command instead of one for all (default 1; batching cuts a site from ~60 s to ~15 s over satellite)
#
# Why it is built this way (2026-10-07):
#  - The MikroTiks sit on the site management VLAN (10.255.0.0/24) behind the SMC and have no public path. The SMC is the only way in.
#  - The password must never be part of a command that runs on the SMC: Teleport audits every exec command and the SMC ships that audit
#    log to Graylog. So the SMC only forwards TCP (`tsh ssh -N -L`); the SSH client runs here, and sshpass reads the password from the
#    SSHPASS environment variable (`-e`), never argv.
#  - Host keys are not pinned: the local port and the device behind it change per run.
set -u
smc=${1:?usage: mikrotik_exec.sh <smc-host> <mikrotik-ip> '<cmd>' ...}; ip=${2:?mikrotik ip}; shift 2
[ $# -ge 1 ] || { echo "no RouterOS command given" >&2; exit 2; }
proxy=${TSH_PROXY:-teleport.apn.au}
entry=${MT_ENTRY:-Network/mikrotik switch & metal ap}
py=${MT_PY:-python3}

if [ "${MT_ALLOW_WRITE:-0}" != 1 ]; then
  for c in "$@"; do
    # read-only verbs only: print, monitor ... once, export, get, and the :put/:local helpers used to format output
    if ! printf '%s' "$c" | grep -qE '(^|[[:space:]/])(print|export|monitor[^;]*once|get)([[:space:]]|$)|^:put|^:local'; then
      echo "refused (not read-only): $c   (set MT_ALLOW_WRITE=1 deliberately to override)" >&2; exit 2
    fi
  done
fi

user=$(kp show -a UserName "$entry" 2>/dev/null) || { echo "KeePass entry not found: $entry" >&2; exit 3; }
SSHPASS=$(kp show -s -a Password "$entry" 2>/dev/null) || { echo "cannot read password for $entry" >&2; exit 3; }
export SSHPASS

port=$(( 20000 + RANDOM % 20000 ))
tsh --proxy="$proxy" ssh -N -L "127.0.0.1:${port}:${ip}:22" "root@${smc}" >/dev/null 2>&1 &
fwd=$!
trap 'kill $fwd 2>/dev/null; wait $fwd 2>/dev/null' EXIT
for _ in $(seq 1 30); do
  nc -z 127.0.0.1 "$port" 2>/dev/null && break
  sleep 1
done
nc -z 127.0.0.1 "$port" 2>/dev/null || { echo "port-forward via $smc to $ip:22 did not come up" >&2; exit 4; }

# sshrun <remote command>: one SSH session to the device through the forwarded local port; prints its output with carriage returns removed.
# The password reaches ssh only through SSHPASS (`sshpass -e`), never argv. Host keys are not pinned because the local port and the device behind it
# change per run. A "Permission denied" is retried twice with a growing pause (10 s, 20 s): on 2026-10-07 two devices refused the correct password
# for a few minutes and then accepted it.
sshrun() {
  # SSH_ASKPASS_REQUIRE=never: with DISPLAY set, ssh otherwise tries an X11 askpass instead of the sshpass pty. A login that still
  # fails is retried twice: on 2026-10-07 two devices refused the same, correct password for a few minutes, then accepted it.
  local try outp
  for try in 1 2 3; do
    outp=$(SSH_ASKPASS_REQUIRE=never sshpass -e ssh -p "$port" -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR \
      -o ConnectTimeout=20 -o PubkeyAuthentication=no -o NumberOfPasswordPrompts=1 "${user}@127.0.0.1" "$1" 2>&1 | tr -d '\r')
    case "$outp" in *"Permission denied"*) [ "$try" -lt 3 ] && sleep $((try * 10)) && continue ;; esac
    break
  done
  printf '%s\n' "$outp"
}
if [ "${MT_BATCH:-1}" = 1 ]; then
  # One SSH session for all commands (each session costs several satellite round trips). RouterOS runs `;`-separated commands in
  # order; `:put "### N"` marks where command N starts, and the markers are rewritten to the command text below.
  batch=""; i=0
  for c in "$@"; do i=$((i+1)); batch="${batch}:put \"### ${i}\"; ${c}; "; done
  sshrun "$batch" | "$py" -c '
import re, sys
cmds = sys.argv[1:]
for line in sys.stdin:
    m = re.match(r"^### (\d+)\s*$", line)
    print(f"\n### {cmds[int(m.group(1))-1]}" if m else line, end="" if not m else "\n")
' "$@"
else
  for c in "$@"; do echo "### $c"; sshrun "$c"; echo; done
fi
