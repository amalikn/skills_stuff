#!/usr/bin/env bash
set -Eeuo pipefail

die() { printf 'ERROR: %s\n' "$*" >&2; exit 1; }

find_repo_root() {
  local start="${1:-$PWD}"
  if git -C "$start" rev-parse --show-toplevel >/dev/null 2>&1; then
    git -C "$start" rev-parse --show-toplevel
  else
    (cd "$start" && pwd)
  fi
}

repomix_cmd() {
  if command -v repomix >/dev/null 2>&1; then
    printf '%s\n' "repomix"
  elif command -v npx >/dev/null 2>&1; then
    printf '%s\n' "npx --yes repomix"
  else
    die "Repomix not found. Install Repomix or make npx available."
  fi
}

assert_safe_repo() {
  local repo="$1"
  [[ "$repo" != "/" ]] || die "Refusing repository root /"
  [[ "$repo" != "$HOME" ]] || die "Refusing repository root \$HOME"
}

assert_safe_output() {
  local repo="$1"
  local output="$2"
  case "$output" in
    "$repo"/.ai-context/*|.ai-context/*) ;;
    *) die "Output must remain under .ai-context/: $output" ;;
  esac
}

join_csv() {
  local IFS=,
  printf '%s' "$*"
}
