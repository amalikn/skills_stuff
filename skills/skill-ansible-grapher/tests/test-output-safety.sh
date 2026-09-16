#!/usr/bin/env bash
# Output-safety focused tests: containment, overwrite, cleanup ownership, dry-run clean.
set -uo pipefail

SKILL_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FIXTURES="$SKILL_ROOT/tests/fixtures"
VENV_PY="/Volumes/Data/_ai/_skills/skills-working-cache/skill-ansible-grapher/.venv/bin/python"
PY="$VENV_PY"; [ -x "$PY" ] || PY=python3
GRAPHER="$SKILL_ROOT/scripts/ansible-grapher"

: "${ANSIBLE_GRAPHER_INVENTORY_GRAPHER_BIN:=/Volumes/Data/_ai/_tools/tools_stuff/ansible-inventory-grapher/scripts/ansible-inventory-grapher.sh}"
export ANSIBLE_GRAPHER_INVENTORY_GRAPHER_BIN

WORKDIR="$(mktemp -d)"
trap 'rm -rf "$WORKDIR"' EXIT

PASS=0
FAIL=0
FAILED_NAMES=()

check() {
    local name="$1"; shift
    if "$@"; then
        PASS=$((PASS + 1)); echo "[PASS] $name"
    else
        FAIL=$((FAIL + 1)); FAILED_NAMES+=("$name"); echo "[FAIL] $name"
    fi
}

# Refuse "/" as output dir
t_reject_root() {
    "$PY" "$GRAPHER" inventory --inventory "$FIXTURES/inventory/valid-hosts.yml" --output-dir "/" >/dev/null 2>&1
    [ $? -ne 0 ]
}

# Refuse $HOME as output dir
t_reject_home() {
    "$PY" "$GRAPHER" inventory --inventory "$FIXTURES/inventory/valid-hosts.yml" --output-dir "$HOME" >/dev/null 2>&1
    [ $? -ne 0 ]
}

# clean refuses a directory that exists but was never touched by this skill
t_clean_refuses_unmarked_dir() {
    local d="$WORKDIR/plain"
    mkdir -p "$d"
    echo "user data" > "$d/important.txt"
    "$PY" "$GRAPHER" clean --output-dir "$d" --force >/dev/null 2>&1
    [ $? -ne 0 ] && [ -f "$d/important.txt" ]
}

# clean without --force is a dry-run (no deletion)
t_clean_dry_run_no_force() {
    local out="$WORKDIR/dryrun"
    "$PY" "$GRAPHER" inventory --inventory "$FIXTURES/inventory/valid-hosts.yml" --output-dir "$out" --force >/dev/null 2>&1 || return 1
    "$PY" "$GRAPHER" clean --output-dir "$out" >/dev/null 2>&1
    [ -d "$out" ] && [ -f "$out/inventory/inventory.dot" ]
}

# clean --force actually removes an owned directory
t_clean_force_removes_owned_dir() {
    local out="$WORKDIR/realclean"
    "$PY" "$GRAPHER" inventory --inventory "$FIXTURES/inventory/valid-hosts.yml" --output-dir "$out" --force >/dev/null 2>&1 || return 1
    "$PY" "$GRAPHER" clean --output-dir "$out" --force >/dev/null 2>&1
    [ ! -d "$out" ]
}

# clean refuses a symlinked output_dir itself
t_clean_refuses_symlinked_root() {
    local real="$WORKDIR/real-target"
    "$PY" "$GRAPHER" inventory --inventory "$FIXTURES/inventory/valid-hosts.yml" --output-dir "$real" --force >/dev/null 2>&1 || return 1
    local link="$WORKDIR/link-to-real"
    ln -s "$real" "$link"
    "$PY" "$GRAPHER" clean --output-dir "$link" --force >/dev/null 2>&1
    [ $? -ne 0 ] && [ -f "$real/inventory/inventory.dot" ]
}

# No leftover .tmp.* files after a successful atomic write
t_no_leftover_tmp_files() {
    local out="$WORKDIR/atomic"
    "$PY" "$GRAPHER" inventory --inventory "$FIXTURES/inventory/valid-hosts.yml" --output-dir "$out" --force >/dev/null 2>&1 || return 1
    ! find "$out" -name "*.tmp.*" | grep -q .
}

# Ownership marker has the expected schema
t_ownership_marker_schema() {
    local out="$WORKDIR/marker-check"
    "$PY" "$GRAPHER" inventory --inventory "$FIXTURES/inventory/valid-hosts.yml" --output-dir "$out" --force >/dev/null 2>&1 || return 1
    "$PY" -c "
import json
d = json.load(open('$out/.ansible-grapher-owned'))
assert d['schema'] == 'ansible-grapher-owned'
"
}

check "Reject '/' as output directory"          t_reject_root
check "Reject \$HOME as output directory"       t_reject_home
check "Clean refuses unmarked directory"        t_clean_refuses_unmarked_dir
check "Clean without --force is dry-run"        t_clean_dry_run_no_force
check "Clean --force removes owned directory"   t_clean_force_removes_owned_dir
check "Clean refuses symlinked output root"     t_clean_refuses_symlinked_root
check "No leftover .tmp files after write"      t_no_leftover_tmp_files
check "Ownership marker schema is valid"        t_ownership_marker_schema

echo
echo "=== $PASS passed, $FAIL failed ==="
if [ "$FAIL" -ne 0 ]; then
    echo "Failed: ${FAILED_NAMES[*]}"
    exit 1
fi
exit 0
