#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  repo_knowledge_capture.sh <setup|snapshot|history-init|history-commit|restore> <repo-path> [snapshot-name]
USAGE
}

if [[ $# -lt 2 ]]; then
  usage >&2
  exit 1
fi

command="$1"
repo_input="$2"
snapshot_name="${3:-}"

require_repo() {
  git -C "$repo_input" rev-parse --show-toplevel
}

ensure_history_identity() {
  if [[ -z "$(git -C "$history_dir" config --local --get user.name || true)" ]]; then
    git -C "$history_dir" config --local user.name "repo-knowledge-capture"
  fi
  if [[ -z "$(git -C "$history_dir" config --local --get user.email || true)" ]]; then
    git -C "$history_dir" config --local user.email "repo-knowledge-capture@local.invalid"
  fi
}

repo_root="$(require_repo)"
repo_name="$(basename "$repo_root")"
knowledge_base="${REPO_KNOWLEDGE_ROOT:-$HOME/_ansible/local-knowledge}/$repo_name"
snapshots_dir="$knowledge_base/snapshots"
history_dir="$knowledge_base/history"
exclude_file="$repo_root/.git/info/exclude"
script_artifacts=(".serena" ".smart-coding-cache" "AGENTS.md" ".agents" ".vscode")

ensure_dirs() {
  mkdir -p "$snapshots_dir"
}

copy_artifact() {
  local src="$1"
  local dest_parent="$2"
  if [[ -e "$src" ]]; then
    cp -R "$src" "$dest_parent/"
  fi
}

replace_artifact() {
  local src="$1"
  local dest="$2"
  rm -rf "$dest"
  if [[ -e "$src" ]]; then
    cp -R "$src" "$dest"
  fi
}

latest_snapshot_name() {
  if [[ ! -d "$snapshots_dir" ]]; then
    return 1
  fi
  find "$snapshots_dir" -mindepth 1 -maxdepth 1 -type d -print | sed 's#^.*/##' | sort | tail -n 1
}

case "$command" in
  setup)
    mkdir -p "$(dirname "$exclude_file")"
    touch "$exclude_file"
    grep -qxF '.serena/' "$exclude_file" || printf '%s\n' '.serena/' >> "$exclude_file"
    grep -qxF '.smart-coding-cache/' "$exclude_file" || printf '%s\n' '.smart-coding-cache/' >> "$exclude_file"
    grep -qxF 'AGENTS.md' "$exclude_file" || printf '%s\n' 'AGENTS.md' >> "$exclude_file"
    grep -qxF '.agents/' "$exclude_file" || printf '%s\n' '.agents/' >> "$exclude_file"
    grep -qxF '.vscode/' "$exclude_file" || printf '%s\n' '.vscode/' >> "$exclude_file"
    printf 'exclude_file=%s\n' "$exclude_file"
    ;;

  snapshot)
    ensure_dirs
    ts="$(date '+%Y%m%d_%H%M')"
    target="$snapshots_dir/$ts"
    mkdir -p "$target"
    copy_artifact "$repo_root/.serena" "$target"
    copy_artifact "$repo_root/.smart-coding-cache" "$target"
    copy_artifact "$repo_root/AGENTS.md" "$target"
    copy_artifact "$repo_root/.agents" "$target"
    copy_artifact "$repo_root/.vscode" "$target"
    printf 'snapshot=%s\n' "$target"
    ;;

  history-init)
    ensure_dirs
    mkdir -p "$history_dir"
    if [[ ! -d "$history_dir/.git" ]]; then
      git -C "$history_dir" init >/dev/null
    fi
    ensure_history_identity
    printf 'history=%s\n' "$history_dir"
    ;;

  history-commit)
    ensure_dirs
    mkdir -p "$history_dir"
    if [[ ! -d "$history_dir/.git" ]]; then
      git -C "$history_dir" init >/dev/null
    fi
    ensure_history_identity
    snap="${snapshot_name:-$(latest_snapshot_name || true)}"
    if [[ -z "$snap" ]]; then
      echo 'No snapshot available to commit.' >&2
      exit 1
    fi
    src="$snapshots_dir/$snap"
    if [[ ! -d "$src" ]]; then
      echo "Snapshot not found: $snap" >&2
      exit 1
    fi
    rm -rf "$history_dir/current"
    mkdir -p "$history_dir/current"
    for artifact in "${script_artifacts[@]}"; do
      if [[ -e "$src/$artifact" ]]; then
        cp -R "$src/$artifact" "$history_dir/current/$artifact"
      fi
    done
    printf '%s\n' "$snap" > "$history_dir/LATEST_SNAPSHOT"
    git -C "$history_dir" add -A
    if [[ -n "$(git -C "$history_dir" status --porcelain)" ]]; then
      git -C "$history_dir" commit -m "snapshot $snap for $repo_name" >/dev/null
      printf 'commit=created\n'
    else
      printf 'commit=unchanged\n'
    fi
    printf 'history=%s\n' "$history_dir"
    ;;

  restore)
    if [[ -z "$snapshot_name" ]]; then
      echo 'restore requires a snapshot name' >&2
      exit 1
    fi
    src="$snapshots_dir/$snapshot_name"
    if [[ ! -d "$src" ]]; then
      echo "Snapshot not found: $snapshot_name" >&2
      exit 1
    fi
    replace_artifact "$src/.serena" "$repo_root/.serena"
    replace_artifact "$src/.smart-coding-cache" "$repo_root/.smart-coding-cache"
    replace_artifact "$src/AGENTS.md" "$repo_root/AGENTS.md"
    replace_artifact "$src/.agents" "$repo_root/.agents"
    replace_artifact "$src/.vscode" "$repo_root/.vscode"
    printf 'restored=%s\n' "$src"
    ;;

  *)
    usage >&2
    exit 1
    ;;
esac
