#!/usr/bin/env bash
# Real partial-generation-failure tests: fake upstream graphers (substituted via the
# supported ANSIBLE_GRAPHER_*_GRAPHER_BIN override env vars) that exit 0 but produce no,
# empty, or structurally invalid output. Verifies the wrapper never promotes these as
# successful runs. Contacts no managed hosts, no cloud APIs, no network.
set -uo pipefail

SKILL_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FIXTURES="$SKILL_ROOT/tests/fixtures"
FAKE="$FIXTURES/fake-tools"
VENV_PY="/Volumes/Data/_ai/_skills/skills-working-cache/skill-ansible-grapher/.venv/bin/python"
PY="$VENV_PY"; [ -x "$PY" ] || PY=python3
GRAPHER="$SKILL_ROOT/scripts/ansible-grapher"

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

# --- Inventory: exit 0, no DOT content at all ---
t_inventory_exit0_empty_stdout() {
    local out="$WORKDIR/inv-empty"
    local text rc
    text=$(ANSIBLE_GRAPHER_INVENTORY_GRAPHER_BIN="$FAKE/fake-inventory-grapher-exit0-empty-stdout.sh" \
        "$PY" "$GRAPHER" inventory --inventory "$FIXTURES/inventory/valid-hosts.yml" --output-dir "$out" --force 2>&1)
    rc=$?
    [ "$rc" -ne 0 ] || return 1
    [ ! -f "$out/inventory/inventory.dot" ] || return 1
    ! find "$out" -name "*.tmp.*" 2>/dev/null | grep -q . || return 1
    echo "$text" | grep -qi "no DOT output"
}

# --- Inventory: exit 0, garbage (non-DOT) content ---
t_inventory_exit0_garbage_stdout() {
    local out="$WORKDIR/inv-garbage"
    local text rc
    text=$(ANSIBLE_GRAPHER_INVENTORY_GRAPHER_BIN="$FAKE/fake-inventory-grapher-exit0-garbage-stdout.sh" \
        "$PY" "$GRAPHER" inventory --inventory "$FIXTURES/inventory/valid-hosts.yml" --output-dir "$out" --force 2>&1)
    rc=$?
    [ "$rc" -ne 0 ] || return 1
    [ ! -f "$out/inventory/inventory.dot" ] || return 1
    echo "$text" | grep -qi "does not look like valid DOT"
}

# --- Playbook: exit 0, no output file created at all ---
t_playbook_exit0_no_file() {
    local out="$WORKDIR/pb-nofile"
    local text rc
    text=$(ANSIBLE_GRAPHER_PLAYBOOK_GRAPHER_BIN="$FAKE/fake-playbook-grapher-exit0-no-file.sh" \
        "$PY" "$GRAPHER" playbook --playbook "$FIXTURES/playbooks/valid-site.yml" --output-dir "$out" --force 2>&1)
    rc=$?
    [ "$rc" -eq 7 ] || return 1  # EXIT_PARTIAL_FAILURE
    [ ! -f "$out/playbooks/valid-site.svg" ] || return 1
    echo "$text" | grep -qi "exited 0 but the expected primary artifact" && echo "$text" | grep -qi "was not generated"
}

# --- Playbook: exit 0, empty (zero-byte) SVG file ---
t_playbook_exit0_empty_svg() {
    local out="$WORKDIR/pb-empty-svg"
    local rc
    FAKE_GRAPHER_MODE=empty ANSIBLE_GRAPHER_PLAYBOOK_GRAPHER_BIN="$FAKE/fake-playbook-grapher-bad-artifact.sh" \
        "$PY" "$GRAPHER" playbook --playbook "$FIXTURES/playbooks/valid-site.yml" --output-dir "$out" --force >/dev/null 2>&1
    rc=$?
    [ "$rc" -eq 7 ] && [ ! -f "$out/playbooks/valid-site.svg" ]
}

# --- Playbook: exit 0, structurally invalid (non-SVG) content ---
t_playbook_exit0_invalid_svg_markup() {
    local out="$WORKDIR/pb-invalid-svg"
    local rc
    FAKE_GRAPHER_MODE=garbage ANSIBLE_GRAPHER_PLAYBOOK_GRAPHER_BIN="$FAKE/fake-playbook-grapher-bad-artifact.sh" \
        "$PY" "$GRAPHER" playbook --playbook "$FIXTURES/playbooks/valid-site.yml" --output-dir "$out" --force >/dev/null 2>&1
    rc=$?
    [ "$rc" -eq 7 ] && [ ! -f "$out/playbooks/valid-site.svg" ]
}

# --- Playbook: exit 0, empty JSON artifact ---
t_playbook_exit0_empty_json() {
    local out="$WORKDIR/pb-empty-json"
    local rc
    FAKE_GRAPHER_MODE=empty ANSIBLE_GRAPHER_PLAYBOOK_GRAPHER_BIN="$FAKE/fake-playbook-grapher-bad-artifact.sh" \
        "$PY" "$GRAPHER" playbook --playbook "$FIXTURES/playbooks/valid-site.yml" --renderer json --output-dir "$out" --force >/dev/null 2>&1
    rc=$?
    [ "$rc" -eq 7 ] && [ ! -f "$out/playbooks/valid-site.json" ]
}

# --- Playbook: exit 0, invalid (non-JSON) content where JSON was requested ---
t_playbook_exit0_invalid_json() {
    local out="$WORKDIR/pb-invalid-json"
    local rc
    FAKE_GRAPHER_MODE=garbage ANSIBLE_GRAPHER_PLAYBOOK_GRAPHER_BIN="$FAKE/fake-playbook-grapher-bad-artifact.sh" \
        "$PY" "$GRAPHER" playbook --playbook "$FIXTURES/playbooks/valid-site.yml" --renderer json --output-dir "$out" --force >/dev/null 2>&1
    rc=$?
    [ "$rc" -eq 7 ] && [ ! -f "$out/playbooks/valid-site.json" ]
}

# --- Playbook: exit 0, Mermaid output missing a supported graph declaration ---
t_playbook_exit0_invalid_mermaid() {
    local out="$WORKDIR/pb-invalid-mmd"
    local rc
    FAKE_GRAPHER_MODE=garbage ANSIBLE_GRAPHER_PLAYBOOK_GRAPHER_BIN="$FAKE/fake-playbook-grapher-bad-artifact.sh" \
        "$PY" "$GRAPHER" playbook --playbook "$FIXTURES/playbooks/valid-site.yml" --renderer mermaid-flowchart --output-dir "$out" --force >/dev/null 2>&1
    rc=$?
    [ "$rc" -eq 7 ] && [ ! -f "$out/playbooks/valid-site.mmd" ]
}

# --- Manifest is never written for a project run whose sub-step failed ---
t_project_manifest_not_written_on_failure() {
    local out="$WORKDIR/project-fail"
    ANSIBLE_GRAPHER_PLAYBOOK_GRAPHER_BIN="$FAKE/fake-playbook-grapher-exit0-no-file.sh" \
        "$PY" "$GRAPHER" project --project-root "$FIXTURES/project" \
        --inventory "$FIXTURES/inventory/valid-hosts.yml" \
        --playbook "$FIXTURES/playbooks/valid-site.yml" \
        --output-dir "$out" --force >/dev/null 2>&1
    [ ! -f "$out/manifest.json" ]
}

check "Inventory: exit 0 + empty stdout -> failure, no DOT, no promotion"       t_inventory_exit0_empty_stdout
check "Inventory: exit 0 + garbage stdout -> rejected as invalid DOT"           t_inventory_exit0_garbage_stdout
check "Playbook: exit 0 + no file created -> exit 7, missing artifact"         t_playbook_exit0_no_file
check "Playbook: exit 0 + empty SVG -> rejected, removed"                      t_playbook_exit0_empty_svg
check "Playbook: exit 0 + invalid SVG markup -> rejected, removed"             t_playbook_exit0_invalid_svg_markup
check "Playbook: exit 0 + empty JSON -> rejected, removed"                     t_playbook_exit0_empty_json
check "Playbook: exit 0 + invalid JSON -> rejected, removed"                   t_playbook_exit0_invalid_json
check "Playbook: exit 0 + invalid Mermaid -> rejected, removed"                t_playbook_exit0_invalid_mermaid
check "Project: manifest not written when a sub-step fails"                    t_project_manifest_not_written_on_failure

echo
echo "=== $PASS passed, $FAIL failed ==="
if [ "$FAIL" -ne 0 ]; then
    echo "Failed: ${FAILED_NAMES[*]}"
    exit 1
fi
exit 0
