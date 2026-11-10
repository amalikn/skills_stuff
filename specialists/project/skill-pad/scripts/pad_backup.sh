#!/usr/bin/env bash
# pad_backup.sh: back up the local Pad database (pad.db under ~/.pad, which points at malik1tb) to a second disk, keeping the newest N copies.
#
# Why: Pad keeps every task, plan and history in one SQLite file; Git holds only .pad.toml (operator, 2026-11-10: "do pad backup to a different
# path", OneDrive pad_backups). `pad db backup` writes an online-safe copy (SQLite VACUUM INTO), so the server may keep running.
#
# Usage:
#   bash pad_backup.sh                 # plan: what would be written and pruned
#   bash pad_backup.sh --apply         # write pad-YYYYMMDD_HHMM.db, prune beyond PAD_BACKUP_KEEP (default 30)
# Settings (environment): PAD_BACKUP_DIR (default ~/Library/CloudStorage/OneDrive-Personal/pad_backups), PAD_BACKUP_KEEP (30),
#   PAD_BACKUP_TIMEOUT seconds (120).
# Scheduled nightly by launchd: pad_backup.plist beside this file, symlinked into ~/Library/LaunchAgents.
# Exit: 0 done or plan clean, 1 the database or target is missing or the backup failed, 2 bad arguments.
# Budget: a few seconds for a personal database; the run prints its measured time.
set -euo pipefail

DEST="${PAD_BACKUP_DIR:-$HOME/Library/CloudStorage/OneDrive-Personal/pad_backups}"
KEEP="${PAD_BACKUP_KEEP:-30}"
TIMEOUT_S="${PAD_BACKUP_TIMEOUT:-120}"
DB="${PAD_DB_PATH:-$HOME/.pad/pad.db}"

# die: print a message to stderr and exit 1.
#   Args: $1 message.
#   Returns: never.
die() { echo "pad_backup: $1" >&2; exit 1; }

# with_timeout: run a command, stopping it after a number of seconds (macOS has no coreutils timeout by default).
#   Args: $1 seconds; the rest is the command.
#   Returns: the command's status, or 124 when it was stopped.
with_timeout() {
  local secs=$1; shift
  "$@" & local pid=$!
  ( sleep "$secs"; kill -TERM "$pid" 2>/dev/null ) & local watcher=$!
  local rc=0; wait "$pid" || rc=$?
  kill "$watcher" 2>/dev/null || true
  [ "$rc" = 143 ] && return 124
  return "$rc"
}

apply=0
case "${1:-}" in
  --apply) apply=1 ;;
  "") ;;
  *) echo "usage: pad_backup.sh [--apply]" >&2; exit 2 ;;
esac

start=$(date +%s)
[ -f "$DB" ] || die "no database at $DB (is malik1tb mounted, and has 'pad init' run?)"
[ -d "$DEST" ] || die "no backup folder $DEST"
out="$DEST/pad-$(date +%Y%m%d_%H%M).db"
mapfile_list=$(ls -1t "$DEST"/pad-*.db 2>/dev/null || true)
prune=$(printf '%s\n' "$mapfile_list" | sed '/^$/d' | tail -n +"$KEEP")

if [ "$apply" = 0 ]; then
  echo "PLAN: would write $out from $DB; would prune $(printf '%s\n' "$prune" | sed '/^$/d' | wc -l | tr -d ' ') old backup(s) beyond $KEEP; --apply to run"
  exit 0
fi

with_timeout "$TIMEOUT_S" pad db backup --cron --output "$out" || die "pad db backup failed or timed out (${TIMEOUT_S}s)"
[ -s "$out" ] || die "backup file is empty: $out"
printf '%s\n' "$prune" | sed '/^$/d' | while IFS= read -r old; do rm -f -- "$old"; done
echo "pad_backup: wrote $out ($(du -h "$out" | cut -f1)); kept newest $KEEP; $(( $(date +%s) - start ))s"
