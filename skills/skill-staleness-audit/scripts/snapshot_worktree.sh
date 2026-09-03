#!/usr/bin/env bash
# Phase 0 — snapshot every modified and untracked file before the audit touches anything.
#
# WHY THIS EXISTS, AND WHY IT VERIFIES ITS OWN OUTPUT
# ---------------------------------------------------
# In the run this skill was extracted from, a `git checkout --` used to undo an unwanted
# reformat destroyed uncommitted work, because the repo carried a large uncommitted working
# tree and the file's own enforcing check lived only there too.
#
# The snapshot taken immediately afterwards then captured ZERO files and reported success.
# Cause: the project was a SUBDIRECTORY of its git repo, so `git status --porcelain` emitted
# repo-root-relative paths (`jdm/docs/...`) which do not resolve from a cwd already inside
# `jdm/`. Every copy silently failed, and the script printed nothing to say so.
#
# Hence two non-negotiables here:
#   1. Use `git ls-files`, which is CWD-relative. Never `git status --porcelain` for paths.
#   2. VERIFY the resulting file count and exit non-zero if it is zero while the tree is dirty.
#      A safety net that silently catches nothing is worse than none, because it is trusted.
#
# Usage:
#   ./snapshot_worktree.sh [DEST]
#     DEST defaults to ./.staleness-audit-snapshot-<UTC timestamp>
#
# Exit codes: 0 ok (including a genuinely clean tree) · 1 verification failed · 2 not a git repo

set -euo pipefail

DEST="${1:-}"
if [ -z "$DEST" ]; then
  DEST="./.staleness-audit-snapshot-$(date -u +%Y%m%d_%H%M%S)"
fi

if ! git rev-parse --git-dir >/dev/null 2>&1; then
  echo "ERROR: not a git repository." >&2
  echo "       Phase 0 is MANDATORY without version control — copy the tree manually before editing." >&2
  exit 2
fi

ROOT="$(git rev-parse --show-toplevel)"
CWD="$(pwd)"
if [ "$ROOT" != "$CWD" ]; then
  echo "NOTE: git root is '$ROOT', which is not the current directory."
  echo "      Repo-root-relative output (git status --porcelain, git diff --name-only) will NOT"
  echo "      resolve from here. This script uses git ls-files, which is cwd-relative."
fi

# -m modified, -o untracked, honouring .gitignore. Cwd-relative by design.
mapfile -t FILES < <(git ls-files -m -o --exclude-standard)

if [ "${#FILES[@]}" -eq 0 ]; then
  echo "Working tree is clean — nothing to snapshot."
  echo "Proceed, but note that any pre-existing uncommitted work would have appeared here."
  exit 0
fi

mkdir -p "$DEST"
COPIED=0
for f in "${FILES[@]}"; do
  [ -f "$f" ] || continue          # skip deletions and directories
  mkdir -p "$DEST/$(dirname "$f")"
  cp -p "$f" "$DEST/$f"
  COPIED=$((COPIED + 1))
done

ACTUAL="$(find "$DEST" -type f | wc -l | tr -d ' ')"

echo "Snapshot: $DEST"
echo "  candidates from git ls-files : ${#FILES[@]}"
echo "  copied                       : $COPIED"
echo "  verified on disk             : $ACTUAL"

# The verification that the original failure needed and did not have.
if [ "$ACTUAL" -eq 0 ]; then
  echo "ERROR: the tree is dirty but the snapshot is EMPTY — the safety net caught nothing." >&2
  echo "       Do not proceed. Check for a path-resolution mismatch before editing anything." >&2
  exit 1
fi
if [ "$ACTUAL" -ne "$COPIED" ]; then
  echo "ERROR: copied $COPIED but found $ACTUAL on disk — snapshot is incomplete." >&2
  exit 1
fi

echo "OK — safe to begin the audit. Restore any file with:"
echo "  cp \"$DEST/<path>\" \"<path>\""
