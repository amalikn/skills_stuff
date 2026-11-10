#!/bin/sh
# pad_monitor.sh: the live Pad push/watch feed for one agent session, run by the Claude Code Monitor tool when skill-pad's connect mode runs.
#
# Why: the operator runs skill-pad, not Pad's Claude Code plugin (operator, 2026-11-10: "develop our own skill and not rely on the plugin"). The plugin
# starts the same loop from its monitors.json; here the agent starts it with Monitor and re-arms it when the Monitor deadline (30 minutes at most) ends it.
# Adapted from Pad's plugin/scripts/pad-monitor.sh at v0.19.2 (Apache-2.0, Perpetual Software LLC; verbatim copy in
# references/upstream/v0.19.2/plugin_scripts_pad-monitor.sh). Behaviour kept: consent gate, per-session lock, reconnect loop. Changed: a missing pad
# exits with one stderr line instead of sleeping an hour (a Monitor should end, not hang), and the backoff is a setting.
#
# Usage (from the agent, after `pad session arm`):
#   Monitor command: sh <skill-pad>/scripts/pad_monitor.sh      description: "Pad pushes and item events", timeout_ms 1800000
# Settings (environment): PAD_MONITOR_BACKOFF seconds between reconnects (5), PAD_BIN the pad binary (pad).
# Safety: read-only towards Pad apart from `pad session register` (a local 0600 record under ~/.pad/sessions). Every stdout line is one event; only
#   `pad watch` writes to stdout.
# Exit: 0 consent absent or withdrawn, or another live monitor holds this session's stream; 1 pad not found.
# Budget: idle cost is one sleeping shell and one pad process; each reconnect costs one `pad session should-arm` call.

set -u

PAD_BIN="${PAD_BIN:-pad}"
BACKOFF="${PAD_MONITOR_BACKOFF:-5}"

# --- 0. pad must be installed.
if ! "$PAD_BIN" watch --help >/dev/null 2>&1; then
  echo "pad_monitor: pad CLI not found (PAD_BIN=$PAD_BIN)" >&2
  exit 1
fi

# --- 0.5. Presence: record this session in the local registry before the gate (an unarmed session still registers). Never fatal.
"$PAD_BIN" session register >/dev/null 2>&1 || true

# --- 1. Lock key: the Claude Code messaging socket names the session; the working folder is the fallback.
sock="${CLAUDE_CODE_MESSAGING_SOCKET:-}"
if [ -n "$sock" ]; then
  key="sess-$(printf '%s' "$sock" | cksum | cut -d' ' -f1)"
else
  key="repo-$(pwd | cksum | cut -d' ' -f1)"
fi
lock="${TMPDIR:-/tmp}/pad-monitor-${key}.lock"

# acquire_lock: take the per-session lock directory, stealing it from a holder that is no longer running.
#   Args: none (reads $lock).
#   Returns: 0 when this process now holds the lock; 1 when a live peer holds it, or a peer is mid-startup (pid not written yet), so this one stays out.
acquire_lock() {
  while :; do
    if mkdir "$lock" 2>/dev/null; then
      echo $$ >"$lock/pid"
      return 0
    fi
    holder=$(cat "$lock/pid" 2>/dev/null || true)
    [ -z "$holder" ] && return 1
    kill -0 "$holder" 2>/dev/null && return 1
    rm -rf "$lock" 2>/dev/null || true
  done
}

acquire_lock || exit 0

# On exit free the lock; on INT/TERM stop the stream child first, so a new monitor cannot take the lock while the old stream is still closing.
child=
trap 'rm -rf "$lock" 2>/dev/null' 0
trap 'if [ -n "$child" ]; then kill "$child" 2>/dev/null; wait "$child" 2>/dev/null; fi; exit 130' INT TERM

# --- 2/3. Consent gate before every stream attempt; a `pad session disarm` ends the loop at the next reconnect (the stream also drops itself on disarm).
while "$PAD_BIN" session should-arm >/dev/null 2>&1; do
  "$PAD_BIN" watch --stream --for-session &
  child=$!
  wait "$child"
  child=
  sleep "$BACKOFF"
done
exit 0
