#!/usr/bin/env bash
# Offline test of ssh_handshake_time.sh with a fake ssh on SSH_BIN: a pass, a banner-exchange timeout, a refusal and bad usage. No network.
# Run: scripts/access/test_ssh_handshake_time.sh   (or: just test_ssh_handshake_time)
# Exit: 0 all cases pass, 1 a case failed.

set -euo pipefail

here="$(cd "$(dirname "$0")" && pwd)"
probe="$here/ssh_handshake_time.sh"
work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT
fails=0

#######################################
# Write a fake ssh that exits with a given code and stderr text.
# Arguments: $1 path, $2 exit code, $3 stderr text.
# Returns:   0.
#######################################
fake_ssh() {
  printf '#!/usr/bin/env bash\necho "%s" >&2\nexit %s\n' "$3" "$2" >"$1"
  chmod +x "$1"
}

#######################################
# Compare a command's exit code and output with what is expected.
# Arguments: $1 case name, $2 expected exit code, $3 expected output substring, rest the command.
# Returns:   0; counts a failure in $fails.
#######################################
expect() {
  local name="$1" want_rc="$2" want_out="$3" out rc=0
  shift 3
  out="$("$@" 2>&1)" || rc=$?
  if [[ $rc -eq $want_rc && "$out" == *"$want_out"* ]]; then
    echo "PASS $name"
  else
    echo "FAIL $name: rc=$rc out=$out"
    fails=$((fails + 1))
  fi
}

fake_ssh "$work/ok" 0 ""
fake_ssh "$work/slow" 255 "Connection timed out during banner exchange"
fake_ssh "$work/refused" 255 "Permission denied (publickey)"

expect "connects" 0 "timeout=30 rc=0 seconds=0 result=ok" env SSH_BIN="$work/ok" "$probe" host.example 30
expect "default timeouts" 0 "timeout=10 rc=0" env SSH_BIN="$work/ok" "$probe" host.example
expect "banner timeout" 1 "result=timed-out" env SSH_BIN="$work/slow" "$probe" host.example 10
expect "refused" 1 "result=failed" env SSH_BIN="$work/refused" "$probe" host.example 10
expect "no host" 2 "usage" "$probe"
expect "bad timeout" 2 "usage" env SSH_BIN="$work/ok" "$probe" host.example 0
expect "bad host" 2 "usage" env SSH_BIN="$work/ok" "$probe" 'host;rm' 10

[[ $fails -eq 0 ]] && echo "all passed" || exit 1
