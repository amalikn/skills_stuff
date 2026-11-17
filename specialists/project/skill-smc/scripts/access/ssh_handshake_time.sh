#!/usr/bin/env bash
# Time the ssh handshake to one SMC through its Teleport ProxyCommand, once per connect timeout given, and say whether each would pass.
# Answers "Ansible says UNREACHABLE (banner exchange timed out) but tsh ssh works": compare the measured seconds with ansible_ssh_timeout
# (ssh plugin default 10; smc_change playbooks set 30 since 2026-11-17).
#
# Run:   scripts/access/ssh_handshake_time.sh <host-fqdn> [timeout_seconds ...]      (default timeouts: 10 30)
#        just ssh_handshake_time wujal-wujal-booth-smc01.teleport.apn.au 10 30
# Safety: safe, external-network, requires-credentials (a valid tsh login for the host's proxy). Runs only `true` as root over ssh, with
#         BatchMode and no connection sharing, so each try is a fresh handshake. Writes nothing on the SMC or locally.
# Env:   SSH_BIN (default ssh) for tests; SSH_USER (default root).
# Output: one line per timeout: `timeout=<t> rc=<rc> seconds=<s> result=<ok|timed-out|failed>`.
# Exit:  0 every try connected, 1 at least one try failed or timed out, 2 bad usage.

set -euo pipefail

#######################################
# Print usage and exit 2.
# Arguments: none.
# Outputs:   usage on stderr.
# Returns:   never (exits 2).
#######################################
usage() {
  echo "usage: $0 <host-fqdn> [timeout_seconds ...]" >&2
  exit 2
}

#######################################
# Try one ssh connection with a connect timeout and report it.
# Arguments: $1 host, $2 connect timeout in seconds.
# Outputs:   one result line on stdout.
# Returns:   0 connected, 1 failed or timed out.
#######################################
try_once() {
  local host="$1" limit="$2" start rc=0 err took result
  err="$(mktemp)"
  start="$(date +%s)"
  "${SSH_BIN:-ssh}" -o BatchMode=yes -o ConnectTimeout="$limit" -o ControlMaster=no -o ControlPath=none \
    "${SSH_USER:-root}@${host}" true </dev/null >/dev/null 2>"$err" || rc=$?
  took=$(($(date +%s) - start))
  if [[ $rc -eq 0 ]]; then
    result=ok
  elif grep -qi 'timed out' "$err"; then
    result=timed-out
  else
    result=failed
  fi
  rm -f "$err"
  echo "timeout=${limit} rc=${rc} seconds=${took} result=${result}"
  [[ $rc -eq 0 ]]
}

main() {
  [[ $# -ge 1 ]] || usage
  local host="$1" status=0 limit
  shift
  [[ "$host" =~ ^[A-Za-z0-9][A-Za-z0-9.-]*$ ]] || usage
  [[ $# -ge 1 ]] || set -- 10 30
  for limit in "$@"; do
    [[ "$limit" =~ ^[0-9]+$ && "$limit" -gt 0 ]] || usage
  done
  for limit in "$@"; do
    try_once "$host" "$limit" || status=1
  done
  return "$status"
}

main "$@"
