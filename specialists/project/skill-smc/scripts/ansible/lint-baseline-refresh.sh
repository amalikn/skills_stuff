#!/usr/bin/env bash
# Regenerate the ansible-lint baseline-ignore file for the current repo (read by ansible-lint-delta-gate.sh).
#
# Promoted 2026-07-31 from local-knowledge-ansible/ansible-wifi/scripts/lint_baseline_refresh.sh. Pair with ansible-lint-delta-gate.sh, which reads
# the baseline this script produces to allow only NEW violations through a pre-push/CI gate.
#
# Run (from inside the repo, or a linked worktree of the branch the baseline should describe):
#   lint-baseline-refresh.sh             merge: old baseline entries are kept, new ones added (the gate never loses an allowance)
#   lint-baseline-refresh.sh --replace   the new baseline alone replaces the old one
#   ANSIBLE_LINT_VENV_BIN=<venv>/bin    the ansible-lint to use (the pre-push hook's venv, for the same version); ANSIBLE_LINT_CONFIG=<path>
# Fixed 2026-11-20 (smc-resiliency, ansible-wifi push of local/bases-check-mode): the old version deleted the baseline before generating, so a
# failed run left none; it looked for ansible-lint's output in .git/, but `--generate-ignore` writes `.ansible-lint-ignore` in the project root
# (left there as a stray untracked file, which ansible-lint then also reads); and `$repo_root/.git/...` broke in a linked worktree, where .git is
# a file. Now: the result is taken from the root, the root file is put back as it was, the baseline goes to the git common dir (as the gate reads
# it), and the old baseline is kept as <file>.prev until the new one is in place.
# Writes: <git common dir>/.ansible-lint-ignore and .prev; the root .ansible-lint-ignore only transiently (restored, or removed if absent before).
# Exit: 0 baseline written; 1 nothing generated (the old baseline is kept); 2 bad arguments.
set -euo pipefail

mode=merge
case "${1:-}" in
  "") ;;
  --replace) mode=replace ;;
  *)
    echo "usage: lint-baseline-refresh.sh [--replace]" >&2
    exit 2
    ;;
esac

repo_root="$(git rev-parse --show-toplevel)"
cd "$repo_root"
common_dir="$(cd "$(git rev-parse --git-common-dir)" && pwd)"

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

config_file="${ANSIBLE_LINT_CONFIG:-$repo_root/.ansible-lint}"
baseline_file="$common_dir/.ansible-lint-ignore"
root_ignore="$repo_root/.ansible-lint-ignore"

if [[ ! -f "$config_file" ]]; then
  echo "[lint-baseline-refresh] missing config: $config_file (override with ANSIBLE_LINT_CONFIG=<path>)" >&2
  exit 1
fi

tmp_dir="$(mktemp -d "${TMPDIR:-/tmp}/ansible-lint-baseline.XXXXXX")"
had_root=0
if [[ -e "$root_ignore" ]]; then
  had_root=1
  cp -p "$root_ignore" "$tmp_dir/root-ignore.orig"
fi

restore_root() {
  # Put the project-root ignore file back as it was before this run.
  # Args: none. Returns: 0.
  if [[ $had_root -eq 1 ]]; then
    cp -p "$tmp_dir/root-ignore.orig" "$root_ignore"
  else
    unlink "$root_ignore" 2>/dev/null || true
  fi
}
trap 'restore_root; rm -rf "$tmp_dir"' EXIT

mapfile -t lintables < <(git ls-files '*.yml' '*.yaml' '*.j2')
if [[ ${#lintables[@]} -eq 0 ]]; then
  echo "[lint-baseline-refresh] no lintable ansible files found" >&2
  exit 1
fi

echo "[lint-baseline-refresh] generating ($mode) from $(git rev-parse --short HEAD) for $baseline_file"
[[ $had_root -eq 1 ]] && unlink "$root_ignore"
set +e
ansible-lint --offline -c "$config_file" --generate-ignore "${lintables[@]}" >"$tmp_dir/lint.log" 2>&1
lint_rc=$?
set -e
tail -n 3 "$tmp_dir/lint.log"

if [[ ! -s "$root_ignore" ]]; then
  echo "[lint-baseline-refresh] ansible-lint wrote no $root_ignore (rc $lint_rc); the old baseline is kept" >&2
  exit 1
fi

grep -v '^[[:space:]]*$' "$root_ignore" >"$tmp_dir/new"
if [[ $mode == merge && -f "$baseline_file" ]]; then
  grep -v '^[[:space:]]*$' "$baseline_file" >>"$tmp_dir/new"
fi
LC_ALL=C sort -u "$tmp_dir/new" >"$tmp_dir/baseline.sorted"

[[ -f "$baseline_file" ]] && cp -p "$baseline_file" "$baseline_file.prev"
mv "$tmp_dir/baseline.sorted" "$baseline_file"
echo "[lint-baseline-refresh] baseline entries: $(wc -l <"$baseline_file" | tr -d ' ') ($mode; previous kept as $baseline_file.prev)"
if [[ $lint_rc -ne 0 ]]; then
  echo "[lint-baseline-refresh] ansible-lint exited $lint_rc while generating (expected when violations exist)"
fi
