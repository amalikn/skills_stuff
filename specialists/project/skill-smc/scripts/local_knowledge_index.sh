#!/usr/bin/env bash
# Show what lives and what is moving in the local-only ansible-wifi knowledge folder (local-knowledge-ansible), read-only.
#
# usage: local_knowledge_index.sh [--root DIR] [--repo DIR] [--days N] [--per-dir N]
#   --root     local-knowledge folder for ansible-wifi (default $LK_ROOT or /Volumes/Data/_ansible/local-knowledge-ansible/ansible-wifi)
#   --repo     the ansible-wifi checkout it is symlinked into (default $LK_REPO or /Volumes/Data/_ansible/ansible-wifi)
#   --days     window for "recently changed" (default 14)
#   --per-dir  how many recent entries to list per top-level folder (default 8)
#   e.g. just local_knowledge_index        or        bash scripts/local_knowledge_index.sh --days 3
#
# Prints three parts: (1) every symlink in the repo (depth 2) that points into the knowledge folder, and whether git ignores
# it, which is how local-only playbooks, roles and governance files appear in ansible-wifi without reaching Bitbucket;
# (2) per top-level folder, its file count and the newest entries changed within --days; (3) uncommitted changes in the
# knowledge folder's own git repository. Reads only: find, readlink, git status/check-ignore. Exit 0, or 2 on bad arguments.
set -euo pipefail

ROOT="${LK_ROOT:-/Volumes/Data/_ansible/local-knowledge-ansible/ansible-wifi}"
REPO="${LK_REPO:-/Volumes/Data/_ansible/ansible-wifi}"
DAYS=14
PER_DIR=8

# usage: print the header comment as help.
#   Args: none. Returns: nothing; prints to stdout.
usage() { sed -n '2,15p' "$0" | sed 's/^# \{0,1\}//'; }

while [ $# -gt 0 ]; do
  case "$1" in
    --root) ROOT="$2"; shift 2 ;;
    --repo) REPO="$2"; shift 2 ;;
    --days) DAYS="$2"; shift 2 ;;
    --per-dir) PER_DIR="$2"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "unknown argument: $1" >&2; usage >&2; exit 2 ;;
  esac
done
[ -d "$ROOT" ] || { echo "no such folder: $ROOT" >&2; exit 2; }

# links: list repo symlinks (depth 2) that resolve into ROOT, with git's ignore status.
#   Args: none (uses REPO, ROOT). Returns: nothing; prints "path -> target [ignored|TRACKED?]".
links() {
  [ -d "$REPO/.git" ] || { echo "  (no git checkout at $REPO)"; return 0; }
  find "$REPO" -maxdepth 2 -type l -not -path "$REPO/collections/*" -print 2>/dev/null | sort | while read -r l; do
    t=$(readlink "$l")
    case "$t" in "$ROOT"*|"$(dirname "$ROOT")"*) ;; *) continue ;; esac
    rel=${l#"$REPO"/}
    if git -C "$REPO" check-ignore -q "$rel" 2>/dev/null; then s=ignored; else s="NOT IGNORED"; fi
    printf '  %-34s -> %s [%s]\n' "$rel" "${t#"$ROOT"/}" "$s"
  done
}

# recent: per top-level folder of ROOT, file count and newest entries changed within DAYS.
#   Args: none (uses ROOT, DAYS, PER_DIR). Returns: nothing; prints one block per folder.
recent() {
  for d in "$ROOT"/*/; do
    name=$(basename "$d")
    n=$(find "$d" -type f -not -path '*/.git/*' 2>/dev/null | wc -l | tr -d ' ')
    printf '  %-30s %6s files\n' "$name/" "$n"
    find "$d" -mindepth 1 -maxdepth 2 -mtime "-$DAYS" -not -path '*/.git*' -not -path '*/cache/*' -print 2>/dev/null \
      | while read -r p; do printf '%s\t%s\n' "$(stat -f %m "$p" 2>/dev/null || stat -c %Y "$p")" "$p"; done \
      | sort -rn | head -n "$PER_DIR" \
      | while IFS=$'\t' read -r ts p; do
          printf '      %s  %s\n' "$(date -r "$ts" '+%Y-%m-%d %H:%M' 2>/dev/null || date -d "@$ts" '+%Y-%m-%d %H:%M')" "${p#"$d"}"
        done
  done
}

echo "== Symlinks from $REPO into the knowledge folder"
links
echo
echo "== $ROOT: top-level folders, entries changed in the last $DAYS days"
recent
echo
echo "== Uncommitted in the knowledge repository (this folder only)"
top=$(git -C "$ROOT" rev-parse --show-toplevel 2>/dev/null || true)
if [ -n "$top" ]; then
  git -C "$top" status --short -- "$ROOT" | head -40
else
  echo "  (not a git repository)"
fi
