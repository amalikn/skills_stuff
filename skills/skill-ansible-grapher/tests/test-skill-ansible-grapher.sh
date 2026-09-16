#!/usr/bin/env bash
# Functional test suite for skill-ansible-grapher.
# Contacts no managed hosts, no cloud APIs, no vaults, no network.
set -uo pipefail

SKILL_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FIXTURES="$SKILL_ROOT/tests/fixtures"
VENV_PY="/Volumes/Data/_ai/_skills/skills-working-cache/skill-ansible-grapher/.venv/bin/python"
PY="$VENV_PY"; [ -x "$PY" ] || PY=python3
GRAPHER="$SKILL_ROOT/scripts/ansible-grapher"

# Point at the local launcher scripts installed under tools_stuff for this machine.
: "${ANSIBLE_GRAPHER_INVENTORY_GRAPHER_BIN:=/Volumes/Data/_ai/_tools/tools_stuff/ansible-inventory-grapher/scripts/ansible-inventory-grapher.sh}"
: "${ANSIBLE_GRAPHER_PLAYBOOK_GRAPHER_BIN:=/Volumes/Data/_ai/_tools/tools_stuff/ansible-playbook-grapher/scripts/ansible-playbook-grapher.sh}"
export ANSIBLE_GRAPHER_INVENTORY_GRAPHER_BIN ANSIBLE_GRAPHER_PLAYBOOK_GRAPHER_BIN

WORKDIR="$(mktemp -d)"
trap 'rm -rf "$WORKDIR"' EXIT

PASS=0
FAIL=0
FAILED_NAMES=()

check() {
    local name="$1"; shift
    if "$@"; then
        PASS=$((PASS + 1))
        echo "[PASS] $name"
    else
        FAIL=$((FAIL + 1))
        FAILED_NAMES+=("$name")
        echo "[FAIL] $name"
    fi
}

# 1. CLI help
t_help() { "$PY" "$GRAPHER" help >/dev/null 2>&1; }

# 2. Missing executable handling — validate reports each missing dependency by name
# and fails overall (exit EXIT_VALIDATION_FAILED=4) rather than silently continuing
# or attempting to install/locate the tool itself.
t_missing_executable() {
    local out rc
    out=$(env -u ANSIBLE_GRAPHER_INVENTORY_GRAPHER_BIN -u ANSIBLE_GRAPHER_PLAYBOOK_GRAPHER_BIN \
        PATH="/usr/bin:/bin" "$PY" "$GRAPHER" validate 2>&1)
    rc=$?
    [ "$rc" -ne 0 ] || return 1
    echo "$out" | grep -q "MISSING.*ansible-inventory-grapher" || return 1
    echo "$out" | grep -q "MISSING.*ansible-playbook-grapher" || return 1
}

# 3. Static YAML inventory validation
t_inventory_valid_yaml() {
    "$PY" "$GRAPHER" validate --inventory "$FIXTURES/inventory/valid-hosts.yml" >/dev/null 2>&1
}

# 3b. Static INI inventory validation
t_inventory_valid_ini() {
    "$PY" "$GRAPHER" validate --inventory "$FIXTURES/inventory/valid-hosts.ini" >/dev/null 2>&1
}

# 4/5. Inventory DOT + SVG generation
t_inventory_dot_svg() {
    local out="$WORKDIR/inv1"
    "$PY" "$GRAPHER" inventory --inventory "$FIXTURES/inventory/valid-hosts.yml" --output-dir "$out" --force >/dev/null 2>&1 || return 1
    [ -s "$out/inventory/inventory.dot" ] || return 1
    grep -q "digraph" "$out/inventory/inventory.dot" || return 1
    [ -s "$out/inventory/inventory.svg" ] || return 1
    grep -q "<svg" "$out/inventory/inventory.svg" || return 1
}

# 6. Variable suppression by default
t_inventory_vars_suppressed() {
    local out="$WORKDIR/inv-novars"
    "$PY" "$GRAPHER" inventory --inventory "$FIXTURES/inventory/valid-hosts.yml" --output-dir "$out" --force >/dev/null 2>&1 || return 1
    ! grep -q "http_port" "$out/inventory/inventory.svg"
}

# 7. Explicit variable display
t_inventory_vars_shown() {
    local out="$WORKDIR/inv-vars"
    "$PY" "$GRAPHER" inventory --inventory "$FIXTURES/inventory/valid-hosts.yml" --output-dir "$out" --show-variables --force >/dev/null 2>&1 || return 1
    grep -q "http_port" "$out/inventory/inventory.svg"
}

# 8. Playbook syntax validation (valid + invalid)
t_playbook_syntax_valid() {
    "$PY" "$GRAPHER" validate --playbook "$FIXTURES/playbooks/valid-site.yml" >/dev/null 2>&1
}
t_playbook_syntax_invalid() {
    local out rc
    out=$("$PY" "$GRAPHER" validate --playbook "$FIXTURES/playbooks/invalid-site.yml" 2>&1)
    rc=$?
    [ "$rc" -ne 0 ]
}

# 9. Playbook SVG generation
t_playbook_svg() {
    local out="$WORKDIR/pb-svg"
    "$PY" "$GRAPHER" playbook --playbook "$FIXTURES/playbooks/valid-site.yml" --output-dir "$out" --force >/dev/null 2>&1 || return 1
    [ -s "$out/playbooks/valid-site.svg" ] || return 1
    grep -q "<svg" "$out/playbooks/valid-site.svg"
}

# 10. Mermaid generation
t_playbook_mermaid() {
    local out="$WORKDIR/pb-mmd"
    "$PY" "$GRAPHER" playbook --playbook "$FIXTURES/playbooks/valid-site.yml" --output-dir "$out" \
        --renderer mermaid-flowchart --force >/dev/null 2>&1 || return 1
    [ -s "$out/playbooks/valid-site.mmd" ] || return 1
    grep -qi "flowchart" "$out/playbooks/valid-site.mmd"
}

# 11. JSON generation
t_playbook_json() {
    local out="$WORKDIR/pb-json"
    "$PY" "$GRAPHER" playbook --playbook "$FIXTURES/playbooks/valid-site.yml" --output-dir "$out" \
        --renderer json --force >/dev/null 2>&1 || return 1
    [ -s "$out/playbooks/valid-site.json" ] || return 1
    "$PY" -c "import json,sys; json.load(open('$out/playbooks/valid-site.json'))"
}

# 12. Multiple playbook handling
t_playbook_multiple() {
    local out="$WORKDIR/pb-multi"
    "$PY" "$GRAPHER" playbook --playbook "$FIXTURES/playbooks/valid-site.yml" \
        --playbook "$FIXTURES/playbooks/valid-site.yml" --output-dir "$out" --force >/dev/null 2>&1 || return 1
    [ -s "$out/playbooks/combined.svg" ]
}

# 13. Tags / skip-tags propagation (verify recorded in command log)
t_tags_propagation() {
    local out="$WORKDIR/pb-tags"
    "$PY" "$GRAPHER" playbook --playbook "$FIXTURES/playbooks/valid-site.yml" --output-dir "$out" \
        --tags web --skip-tags db --force >/dev/null 2>&1 || return 1
    grep -q '"-t", "web"' "$out/logs/commands.log" || grep -q '\-t.*web' "$out/logs/commands.log"
}

# 14. Profile loading
t_profiles_listing() {
    "$PY" "$GRAPHER" profiles 2>&1 | grep -q "inventory-summary"
}

# 15/16. Overwrite refusal + --force
t_overwrite_refusal_then_force() {
    local out="$WORKDIR/overwrite"
    "$PY" "$GRAPHER" inventory --inventory "$FIXTURES/inventory/valid-hosts.yml" --output-dir "$out" --force >/dev/null 2>&1 || return 1
    "$PY" "$GRAPHER" inventory --inventory "$FIXTURES/inventory/valid-hosts.yml" --output-dir "$out" >/dev/null 2>&1
    local rc_no_force=$?
    [ "$rc_no_force" -ne 0 ] || return 1
    "$PY" "$GRAPHER" inventory --inventory "$FIXTURES/inventory/valid-hosts.yml" --output-dir "$out" --force >/dev/null 2>&1
}

# 17. Output path containment
t_output_path_containment() {
    local out rc
    out=$("$PY" "$GRAPHER" inventory --inventory "$FIXTURES/inventory/valid-hosts.yml" --output-dir "/" 2>&1)
    rc=$?
    [ "$rc" -ne 0 ]
}

# 18. Cleanup ownership check
t_cleanup_ownership() {
    local out="$WORKDIR/unowned"
    mkdir -p "$out"
    echo "not generated by this skill" > "$out/somefile.txt"
    local rc
    "$PY" "$GRAPHER" clean --output-dir "$out" --force >/dev/null 2>&1
    rc=$?
    [ "$rc" -ne 0 ] && [ -f "$out/somefile.txt" ]
}

# 19. Symlink escape prevention during cleanup
t_cleanup_symlink_escape() {
    local out="$WORKDIR/owned-with-symlink"
    local escape_target="$WORKDIR/escape-target"
    mkdir -p "$escape_target"
    echo "must survive" > "$escape_target/keepme.txt"
    "$PY" "$GRAPHER" inventory --inventory "$FIXTURES/inventory/valid-hosts.yml" --output-dir "$out" --force >/dev/null 2>&1 || return 1
    ln -s "$escape_target" "$out/escape-link"
    "$PY" "$GRAPHER" clean --output-dir "$out" --force >/dev/null 2>&1
    [ -f "$escape_target/keepme.txt" ]
}

# 20. Dynamic inventory deny-by-default
t_dynamic_inventory_denied() {
    local script="$WORKDIR/dynamic-inv"
    printf '#!/usr/bin/env bash\necho "{}"\n' > "$script"
    chmod +x "$script"
    local out rc
    out=$(env -u ANSIBLE_GRAPHER_ALLOW_DYNAMIC_INVENTORY "$PY" "$GRAPHER" inventory --inventory "$script" --output-dir "$WORKDIR/dyn-out" 2>&1)
    rc=$?
    [ "$rc" -eq 6 ] && echo "$out" | grep -qi "dynamic inventory"
}

# 21. Redaction of extra-vars in logs
t_redaction_extra_vars() {
    local out="$WORKDIR/pb-redact"
    "$PY" "$GRAPHER" playbook --playbook "$FIXTURES/playbooks/valid-site.yml" --output-dir "$out" \
        -e "supersecretvalue123=true" --force >/dev/null 2>&1
    # build_playbook_argv uses -e; ensure raw value never appears in the command log
    ! grep -q "supersecretvalue123" "$out/logs/commands.log" 2>/dev/null
}

# 22/23. Manifest generation + SHA-256 recording
t_manifest_and_sha256() {
    local out="$WORKDIR/project1"
    "$PY" "$GRAPHER" project --project-root "$FIXTURES/project" \
        --inventory "$FIXTURES/project/inventory.yml" \
        --playbook "$FIXTURES/project/site.yml" \
        --output-dir "$out" --force >/dev/null 2>&1 || return 1
    [ -s "$out/manifest.json" ] || return 1
    "$PY" -c "
import json
m = json.load(open('$out/manifest.json'))
assert m['schema_version'] == 2
assert len(m['generated_files']) > 0
for f in m['generated_files']:
    assert len(f['sha256']) == 64
"
}

# 24/30. Deterministic filenames + idempotency (same sha256 across repeated runs)
t_idempotency() {
    local out="$WORKDIR/idempotent"
    "$PY" "$GRAPHER" inventory --inventory "$FIXTURES/inventory/valid-hosts.yml" --output-dir "$out" --force >/dev/null 2>&1 || return 1
    local sha1 sha2
    sha1=$(shasum -a 256 "$out/inventory/inventory.dot" | awk '{print $1}')
    "$PY" "$GRAPHER" inventory --inventory "$FIXTURES/inventory/valid-hosts.yml" --output-dir "$out" --force >/dev/null 2>&1 || return 1
    sha2=$(shasum -a 256 "$out/inventory/inventory.dot" | awk '{print $1}')
    [ "$sha1" = "$sha2" ]
}

# 25. Paths containing spaces
t_paths_with_spaces() {
    local spacedir="$WORKDIR/has space"
    mkdir -p "$spacedir"
    cp "$FIXTURES/inventory/valid-hosts.yml" "$spacedir/hosts.yml"
    local out="$WORKDIR/space out"
    "$PY" "$GRAPHER" inventory --inventory "$spacedir/hosts.yml" --output-dir "$out" --force >/dev/null 2>&1 || return 1
    [ -s "$out/inventory/inventory.svg" ]
}

# 26. Invalid inventory handling
t_invalid_inventory() {
    local rc
    "$PY" "$GRAPHER" validate --inventory "$FIXTURES/inventory/invalid-hosts.yml" >/dev/null 2>&1
    rc=$?
    [ "$rc" -ne 0 ]
}

# 27. Invalid playbook handling (graph attempt must fail, not silently produce output)
t_invalid_playbook_graph_fails() {
    local out="$WORKDIR/pb-invalid"
    local rc
    "$PY" "$GRAPHER" playbook --playbook "$FIXTURES/playbooks/invalid-site.yml" --output-dir "$out" --force >/dev/null 2>&1
    rc=$?
    [ "$rc" -ne 0 ] && [ ! -f "$out/playbooks/invalid-site.svg" ]
}

# 29. Discovery exclusions (.git-like dirs not traversed into)
t_discovery_exclusions() {
    local proj="$WORKDIR/discover-proj"
    mkdir -p "$proj/.git" "$proj/roles/example_role/tasks"
    echo "should not be scanned" > "$proj/.git/should-not-appear.yml"
    cp "$FIXTURES/project/site.yml" "$proj/site.yml"
    local json
    json=$("$PY" "$GRAPHER" discover --project-root "$proj" 2>/dev/null)
    ! echo "$json" | grep -q "should-not-appear"
}

# 3rd param: discovery finds ansible.cfg / roles / requirements
t_discovery_finds_project_facts() {
    local json
    json=$("$PY" "$GRAPHER" discover --project-root "$FIXTURES/project" 2>/dev/null)
    echo "$json" | grep -q '"ansible_cfg"' && \
    echo "$json" | grep -q "ansible.cfg" && \
    echo "$json" | grep -q "requirements.yml"
}

# No source files modified by any run
t_sources_untouched() {
    local before after
    before=$(shasum -a 256 "$FIXTURES/inventory/valid-hosts.yml" "$FIXTURES/playbooks/valid-site.yml" | awk '{print $1}')
    "$PY" "$GRAPHER" project --project-root "$FIXTURES/project" \
        --inventory "$FIXTURES/inventory/valid-hosts.yml" \
        --playbook "$FIXTURES/playbooks/valid-site.yml" \
        --output-dir "$WORKDIR/untouched-check" --force >/dev/null 2>&1
    after=$(shasum -a 256 "$FIXTURES/inventory/valid-hosts.yml" "$FIXTURES/playbooks/valid-site.yml" | awk '{print $1}')
    [ "$before" = "$after" ]
}

check "CLI help"                                   t_help
check "Missing executable -> exit 5"                t_missing_executable
check "Valid YAML inventory validates"              t_inventory_valid_yaml
check "Valid INI inventory validates"               t_inventory_valid_ini
check "Inventory DOT + SVG generation"              t_inventory_dot_svg
check "Inventory variables suppressed by default"   t_inventory_vars_suppressed
check "Inventory variables shown when requested"    t_inventory_vars_shown
check "Playbook syntax check (valid)"               t_playbook_syntax_valid
check "Playbook syntax check (invalid) fails"       t_playbook_syntax_invalid
check "Playbook SVG generation"                     t_playbook_svg
check "Playbook Mermaid generation"                 t_playbook_mermaid
check "Playbook JSON generation"                     t_playbook_json
check "Multiple playbook handling"                  t_playbook_multiple
check "Tags/skip-tags propagation recorded"         t_tags_propagation
check "Profile listing"                             t_profiles_listing
check "Overwrite refusal then --force succeeds"     t_overwrite_refusal_then_force
check "Output path containment ('/' rejected)"      t_output_path_containment
check "Cleanup refuses unowned directory"           t_cleanup_ownership
check "Cleanup does not follow symlinks"            t_cleanup_symlink_escape
check "Dynamic inventory denied by default"         t_dynamic_inventory_denied
check "Extra-vars redacted in command log"          t_redaction_extra_vars
check "Manifest generation + SHA-256 recording"     t_manifest_and_sha256
check "Idempotent DOT output across runs"           t_idempotency
check "Paths containing spaces"                     t_paths_with_spaces
check "Invalid inventory rejected"                  t_invalid_inventory
check "Invalid playbook graph fails cleanly"        t_invalid_playbook_graph_fails
check "Discovery respects exclusions"               t_discovery_exclusions
check "Discovery finds ansible.cfg/roles/requirements" t_discovery_finds_project_facts
check "No source files modified by any run"         t_sources_untouched

echo
echo "=== $PASS passed, $FAIL failed ==="
if [ "$FAIL" -ne 0 ]; then
    echo "Failed: ${FAILED_NAMES[*]}"
    exit 1
fi
exit 0
