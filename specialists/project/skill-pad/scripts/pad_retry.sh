#!/usr/bin/env bash
# Run one pad CLI command, retrying with backoff while the local Pad server rate-limits it (HTTP 429, "Too many requests", rate_limited).
#
# Why (operator, 2026-11-20): every Claude session, agent and script on the Mac shares one limiter (keyed by the Pad user), so a sweep in one
# workspace (about 3,300 requests in 7 minutes on 20 Nov) makes plain `pad item create` / `comment` calls in other sessions fail outright.
# The bulk scripts already back off; this gives single calls the same behaviour.
#
# Run: pad_retry.sh <pad arguments...>          e.g. pad_retry.sh item comment TASK-5 --stdin < note.md
#      just -f <skill-pad>/justfile pad <args>   (the same, through the pack's recipe)
# Stdin, when given, is read once and replayed on every attempt. Output and exit code are those of the last attempt.
# Retries: up to PAD_RETRY_TRIES attempts (default 6), waiting 1, 2, 4, 8, 16 s (or the server's retry_after_seconds when larger); each call
# is cut at PAD_RETRY_TIMEOUT seconds (default 60). PAD_BIN overrides the pad binary (tests).
# Safety: writes exactly what the wrapped pad command writes; a write that failed with 429 was refused by the server, so a retry does not
# duplicate it. Pass --op-key on writes that accept it anyway.
# Exit: the last attempt's exit code; 2 on bad usage.
set -u

pad_bin="${PAD_BIN:-pad}"
tries="${PAD_RETRY_TRIES:-6}"
call_timeout="${PAD_RETRY_TIMEOUT:-60}"

usage() {
  # Print the header comment as help.
  # Args: none. Returns: 0; the help text on stdout.
  sed -n '2,17p' "$0" | sed 's/^# \{0,1\}//'
}

is_rate_limited() {
  # Tell whether a pad call's combined output says it was rate-limited.
  # Args: $1 the output. Returns: 0 when rate-limited, 1 otherwise.
  printf '%s' "$1" | grep -qiE 'too many requests|rate_limited|rate limited|status[= ]?429'
}

retry_after() {
  # The server's suggested wait in whole seconds, when the output carries one.
  # Args: $1 the output. Returns: 0; the number on stdout, or nothing.
  printf '%s' "$1" | grep -oE 'retry_after_seconds"?[: ]+[0-9]+' | grep -oE '[0-9]+$' | head -1
}

main() {
  # Run the wrapped command with retries.
  # Args: the pad arguments. Returns: the last attempt's exit code; 2 on bad usage.
  [ $# -ge 1 ] || { usage >&2; return 2; }
  case "$1" in -h|--help) usage; return 0 ;; esac
  case "$tries" in ''|*[!0-9]*|0) echo "PAD_RETRY_TRIES must be a positive whole number" >&2; return 2 ;; esac
  local input="" have_input=0 out rc wait attempt=1 hint
  if [ ! -t 0 ]; then
    input="$(cat; printf x)"; input="${input%x}"
    have_input=1
  fi
  while :; do
    if [ "$have_input" -eq 1 ]; then
      out="$(printf '%s' "$input" | timeout "$call_timeout" "$pad_bin" "$@" 2>&1)"; rc=$?
    else
      out="$(timeout "$call_timeout" "$pad_bin" "$@" < /dev/null 2>&1)"; rc=$?
    fi
    if ! is_rate_limited "$out" || [ "$attempt" -ge "$tries" ]; then
      printf '%s\n' "$out"
      return "$rc"
    fi
    wait=$(( 1 << (attempt - 1) )); [ "$wait" -gt 16 ] && wait=16
    hint="$(retry_after "$out")"
    [ -n "$hint" ] && [ "$hint" -gt "$wait" ] && wait="$hint"
    echo "pad_retry: rate-limited (attempt $attempt of $tries); waiting ${wait}s" >&2
    sleep "$wait"
    attempt=$((attempt + 1))
  done
}

main "$@"
