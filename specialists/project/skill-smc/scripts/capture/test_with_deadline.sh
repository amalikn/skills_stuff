#!/usr/bin/env bash
# test_with_deadline.sh — offline test of the with_deadline helper in the evidence scripts (no network, no box).
# Run: `just test-deadline` or `bash scripts/capture/test_with_deadline.sh`. Read-only: extracts the function from each script and runs local commands.
# Checks, for each script: piped stdin reaches the command, a fast command's exit status is kept, and a slow command is killed at the deadline
# with status 124 (also when the command traps TERM and exits with its own status, as tsh does).

set -uo pipefail
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
fail=0

# check — report one assertion.
#   Args: $1 label, $2 expected, $3 actual.
#   Returns: 0; sets fail=1 on a mismatch.
check() {
  if [[ "$2" == "$3" ]]; then echo "  ok   $1"; else echo "  FAIL $1: expected '$2', got '$3'"; fail=1; fi
}

for script in collect-smc-evidence-full.sh collect-smc-evidence.sh; do
  echo "$script"
  # Load only the function body, so the script's own argument handling never runs.
  eval "$(sed -n '/^with_deadline() {/,/^}/p' "$here/$script")"
  check "function found" "function" "$(type -t with_deadline)"
  check "stdin passes through" "hello" "$(printf 'hello\n' | with_deadline 5 cat)"
  with_deadline 5 sh -c 'exit 3'; check "exit status kept" "3" "$?"
  start=$(date +%s); with_deadline 1 sleep 30; rc=$?; took=$(( $(date +%s) - start ))
  check "killed at deadline (rc 124)" "124" "$rc"
  check "killed at deadline (<= 3 s)" "yes" "$([[ $took -le 3 ]] && echo yes || echo no)"
  with_deadline 1 sh -c 'trap "exit 1" TERM; sleep 30 & wait'; check "TERM-trapping command reports 124" "124" "$?"
  unset -f with_deadline
done
exit $fail
