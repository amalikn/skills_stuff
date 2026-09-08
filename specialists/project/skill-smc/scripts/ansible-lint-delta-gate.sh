#!/usr/bin/env bash
# Pre-push / CI lint gate: fail only on ansible-lint violations that are NEW — either in a file
# that didn't exist at the upstream merge-base, or on a line the current change actually touched.
# Pre-existing violations in untouched lines of an existing file are allowed through (read from the
# baseline file that lint-baseline-refresh.sh produces), so an unrelated small change doesn't get
# blocked by a large pile of prior debt in the same file.
#
# Promoted 2026-07-31 from local-knowledge-ansible/ansible-wifi/scripts/ansible_lint_delta_gate.sh.
# Genericized: config path is repo-root-relative by default (override with ANSIBLE_LINT_CONFIG) —
# the two source scripts this was promoted from disagreed on that path (one pointed at
# local-knowledge/, the other at local-knowledge-ansible/); making it repo-root-relative removes
# that class of drift entirely.
#
# Usage: ansible-lint-delta-gate.sh <file1> [file2] ...
#   Typically invoked by a pre-push hook with the set of changed ansible files.
set -euo pipefail

repo_root="$(git rev-parse --show-toplevel)"
cd "$repo_root"

ansible_tmp_root="${ANSIBLE_LOCAL_TEMP:-${TMPDIR:-/tmp}/ansible-local-prepush}"
mkdir -p "$ansible_tmp_root"
export ANSIBLE_LOCAL_TEMP="$ansible_tmp_root"
xdg_cache_root="${XDG_CACHE_HOME:-${TMPDIR:-/tmp}/ansible-cache-prepush}"
mkdir -p "$xdg_cache_root"
export XDG_CACHE_HOME="$xdg_cache_root"

ansible_lint_venv="${ANSIBLE_LINT_VENV_BIN:-}"
if [[ -n "$ansible_lint_venv" && -d "$ansible_lint_venv" ]]; then
  export PATH="$ansible_lint_venv:$PATH"
fi

if [[ $# -eq 0 ]]; then
  echo "[ansible-lint-delta] no ansible files provided; skipping"
  exit 0
fi

declare -a files=()
for path in "$@"; do
  [[ -n "$path" ]] || continue
  [[ -e "$path" ]] || continue
  files+=("$path")
done

if [[ ${#files[@]} -eq 0 ]]; then
  echo "[ansible-lint-delta] no existing ansible files provided; skipping"
  exit 0
fi

config_file="${ANSIBLE_LINT_CONFIG:-$repo_root/.ansible-lint}"
baseline_file="$repo_root/.git/.ansible-lint-ignore"

if [[ ! -f "$config_file" ]]; then
  echo "[ansible-lint-delta] missing config: $config_file" >&2
  echo "[ansible-lint-delta] override with ANSIBLE_LINT_CONFIG=<path>" >&2
  exit 1
fi

declare -A baseline_pairs=()
if [[ -f "$baseline_file" ]]; then
  while IFS= read -r line; do
    [[ -n "$line" ]] || continue
    [[ "$line" =~ ^# ]] && continue
    path="${line%% *}"
    rule="${line#* }"
    [[ -n "$path" && -n "$rule" ]] || continue
    baseline_pairs["$path|$rule"]=1
  done < "$baseline_file"
fi

empty_tree="$(git hash-object -t tree /dev/null)"
if git rev-parse --verify '@{upstream}' >/dev/null 2>&1; then
  base_ref="$(git merge-base HEAD '@{upstream}')"
elif git rev-parse --verify 'origin/master' >/dev/null 2>&1; then
  base_ref="$(git merge-base HEAD 'origin/master')"
elif git rev-parse --verify 'origin/main' >/dev/null 2>&1; then
  base_ref="$(git merge-base HEAD 'origin/main')"
else
  base_ref="$empty_tree"
fi

declare -A new_file=()
for path in "${files[@]}"; do
  if git cat-file -e "$base_ref:$path" >/dev/null 2>&1; then
    new_file["$path"]=0
  else
    new_file["$path"]=1
  fi
done

declare -A changed_ranges=()
current_file=""
diff_out="$(git diff -U0 --no-color --no-ext-diff --no-prefix "$base_ref" HEAD -- "${files[@]}" || true)"
while IFS= read -r line; do
  if [[ "$line" =~ ^\+\+\+\ (.+)$ ]]; then
    current_file="${BASH_REMATCH[1]}"
    continue
  fi
  if [[ -z "$current_file" ]]; then
    continue
  fi
  if [[ "$line" =~ ^@@\ -[0-9]+(,[0-9]+)?\ \+([0-9]+)(,([0-9]+))?\ @@ ]]; then
    start="${BASH_REMATCH[2]}"
    count="${BASH_REMATCH[4]:-1}"
    if [[ "$count" == "0" ]]; then
      continue
    fi
    end=$((start + count - 1))
    if [[ -n "${changed_ranges[$current_file]:-}" ]]; then
      changed_ranges["$current_file"]+=",${start}:${end}"
    else
      changed_ranges["$current_file"]="${start}:${end}"
    fi
  fi
done <<< "$diff_out"

line_is_changed() {
  local file="$1"
  local line_no="$2"
  local ranges chunk start end
  ranges="${changed_ranges[$file]:-}"
  [[ -n "$ranges" ]] || return 1
  IFS=',' read -r -a chunks <<< "$ranges"
  for chunk in "${chunks[@]}"; do
    start="${chunk%%:*}"
    end="${chunk##*:}"
    if (( line_no >= start && line_no <= end )); then
      return 0
    fi
  done
  return 1
}

command -v ansible-lint >/dev/null 2>&1 || {
  echo "[ansible-lint-delta] ansible-lint is required but not installed" >&2
  exit 1
}

set +e
lint_output="$(ansible-lint -p --offline -c "$config_file" -i /dev/null "${files[@]}" 2>&1)"
lint_rc=$?
set -e

if [[ $lint_rc -eq 0 ]]; then
  echo "[ansible-lint-delta] clean"
  exit 0
fi

declare -a blocking=()
parsed=0

while IFS= read -r line; do
  [[ -n "$line" ]] || continue
  if [[ "$line" =~ ^([^:]+):([0-9]+):[[:space:]]*([[:alnum:]_:-]+(\[[^]]+\])?):[[:space:]] ]]; then
    parsed=1
    file="${BASH_REMATCH[1]}"
    line_no="${BASH_REMATCH[2]}"

    rule="${BASH_REMATCH[3]}"

    # skip third-party collection files auto-discovered via import resolution
    if [[ "$file" == collections/* ]]; then
      continue
    fi

    # skip files that existed before and have no changed lines (pre-existing violations we didn't introduce)
    if [[ "${new_file[$file]:-0}" -eq 0 && -z "${changed_ranges[$file]:-}" ]]; then
      continue
    fi

    if [[ "$line" == *"(warning)"* ]]; then
      continue
    fi

    if [[ "${new_file[$file]:-0}" -eq 1 ]]; then
      blocking+=("$line")
      continue
    fi

    if line_is_changed "$file" "$line_no"; then
      blocking+=("$line")
      continue
    fi

    if [[ -n "${baseline_pairs[$file|$rule]:-}" ]]; then
      continue
    fi

    blocking+=("$line")
  fi
done <<< "$lint_output"

if [[ ${#blocking[@]} -gt 0 ]]; then
  echo "[ansible-lint-delta] blocking violations (${#blocking[@]}):" >&2
  printf '%s\n' "${blocking[@]}" >&2
  exit 1
fi

if [[ $parsed -eq 1 ]]; then
  echo "[ansible-lint-delta] no new violations (only baseline/unchanged findings)"
  exit 0
fi

echo "[ansible-lint-delta] lint command failed unexpectedly" >&2
printf '%s\n' "$lint_output" >&2
exit 1
