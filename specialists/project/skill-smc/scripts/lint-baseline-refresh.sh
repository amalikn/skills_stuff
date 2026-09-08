#!/usr/bin/env bash
# Regenerate the ansible-lint baseline-ignore file for the current repo.
#
# Promoted 2026-07-31 from local-knowledge-ansible/ansible-wifi/scripts/lint_baseline_refresh.sh.
# Genericized: config path is repo-root-relative by default (override with ANSIBLE_LINT_CONFIG),
# not a hardcoded path to one specific checkout. Pair with ansible-lint-delta-gate.sh, which reads
# the baseline this script produces to allow only NEW violations through a pre-push/CI gate.
set -euo pipefail

repo_root="$(git rev-parse --show-toplevel)"
cd "$repo_root"

ansible_tmp_root="${ANSIBLE_LOCAL_TEMP:-${TMPDIR:-/tmp}/ansible-local-prepush}"
mkdir -p "$ansible_tmp_root"
export ANSIBLE_LOCAL_TEMP="$ansible_tmp_root"
xdg_cache_root="${XDG_CACHE_HOME:-${TMPDIR:-/tmp}/ansible-cache-prepush}"
mkdir -p "$xdg_cache_root"
export XDG_CACHE_HOME="$xdg_cache_root"

# Optional pinned venv for a stable ansible-lint version across sessions — set ANSIBLE_LINT_VENV_BIN
# to override, or leave unset to use whatever ansible-lint is already on PATH.
ansible_lint_venv="${ANSIBLE_LINT_VENV_BIN:-}"
if [[ -n "$ansible_lint_venv" && -d "$ansible_lint_venv" ]]; then
  export PATH="$ansible_lint_venv:$PATH"
fi

config_file="${ANSIBLE_LINT_CONFIG:-$repo_root/.ansible-lint}"
baseline_file="$repo_root/.git/.ansible-lint-ignore"

if [[ ! -f "$config_file" ]]; then
  echo "[lint-baseline-refresh] missing config: $config_file" >&2
  echo "[lint-baseline-refresh] override with ANSIBLE_LINT_CONFIG=<path>" >&2
  exit 1
fi

tmp_dir="$(mktemp -d "${TMPDIR:-/tmp}/ansible-lint-baseline.XXXXXX")"
trap 'rm -rf "$tmp_dir"' EXIT

echo "[lint-baseline-refresh] regenerating baseline at $baseline_file"

mapfile -t lintables < <(git ls-files '*.yml' '*.yaml' '*.j2')
if [[ ${#lintables[@]} -eq 0 ]]; then
  echo "[lint-baseline-refresh] no lintable ansible files found" >&2
  exit 1
fi

rm -f "$baseline_file"
set +e
ansible-lint --offline -c "$config_file" --generate-ignore "${lintables[@]}"
lint_rc=$?
set -e

if [[ ! -f "$baseline_file" ]]; then
  echo "[lint-baseline-refresh] baseline file was not generated" >&2
  exit 1
fi

grep -v '^[[:space:]]*$' "$baseline_file" | LC_ALL=C sort -u > "$tmp_dir/baseline.sorted"
mv "$tmp_dir/baseline.sorted" "$baseline_file"

echo "[lint-baseline-refresh] baseline entries: $(wc -l < "$baseline_file" | tr -d ' ')"
if [[ $lint_rc -ne 0 ]]; then
  echo "[lint-baseline-refresh] ansible-lint exited non-zero while generating baseline (expected when violations exist)"
fi
