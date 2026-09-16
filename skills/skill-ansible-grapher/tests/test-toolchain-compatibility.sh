#!/usr/bin/env bash
# Toolchain provenance / Ansible-version-alignment / Python-runtime-hardening /
# development-version-policy tests. Contacts no managed hosts, no cloud APIs, no network.
set -uo pipefail

SKILL_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FIXTURES="$SKILL_ROOT/tests/fixtures"
VENV_PY="/Volumes/Data/_ai/_skills/skills-working-cache/skill-ansible-grapher/.venv/bin/python"
PY="$VENV_PY"; [ -x "$PY" ] || PY=python3
GRAPHER="$SKILL_ROOT/scripts/ansible-grapher"

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
        PASS=$((PASS + 1)); echo "[PASS] $name"
    else
        FAIL=$((FAIL + 1)); FAILED_NAMES+=("$name"); echo "[FAIL] $name"
    fi
}

# 1. Matching Ansible versions (inventory-grapher's own venv genuinely pins the same
# ansible-core as the system validation binary on this machine — see docs/tool-capabilities.md)
t_matching_versions() {
    local out
    out=$("$PY" "$GRAPHER" validate --format json 2>/dev/null)
    echo "$out" | "$PY" -c "
import json, sys
d = json.load(sys.stdin)
c = [x for x in d['checks'] if x['name'] == 'inventory_ansible_version_match'][0]
assert c['status'] == 'PASS', c
assert c['details']['version_match'] is True
"
}

# 2. Mismatched Ansible versions in warning (default, non-strict) mode
t_mismatch_warn_mode() {
    local out
    out=$("$PY" "$GRAPHER" validate --format json 2>/dev/null)
    echo "$out" | "$PY" -c "
import json, sys
d = json.load(sys.stdin)
c = [x for x in d['checks'] if x['name'] == 'playbook_ansible_version_match'][0]
assert c['status'] == 'WARN', c
assert c['details']['version_match'] is False
assert d['status'] in ('WARN', 'FAIL')  # depends on other checks; must not be silently PASS
"
}

# 3. Mismatched Ansible versions in strict mode -> FAIL, promotes overall to FAIL
t_mismatch_strict_mode() {
    local rc
    "$PY" "$GRAPHER" validate --playbook "$FIXTURES/playbooks/valid-site.yml" --strict-ansible-version-match >/dev/null 2>&1
    rc=$?
    [ "$rc" -ne 0 ]
}

# 4. Unknown Ansible version -> UNKNOWN status, not silently treated as compatible
t_unknown_version() {
    local out
    out=$(ANSIBLE_GRAPHER_INVENTORY_GRAPHER_BIN="$FIXTURES/fake-tools/fake-inventory-grapher-unknown-version.sh" \
        "$PY" "$GRAPHER" validate --format json 2>/dev/null)
    echo "$out" | "$PY" -c "
import json, sys
d = json.load(sys.stdin)
c = [x for x in d['checks'] if x['name'] == 'inventory_ansible_version_match'][0]
assert c['status'] == 'UNKNOWN', c
assert c['details']['version_match'] is None
"
}

# 4b. Unknown version in strict mode -> FAIL (never treated as a pass)
t_unknown_version_strict_fails() {
    local rc
    ANSIBLE_GRAPHER_INVENTORY_GRAPHER_BIN="$FIXTURES/fake-tools/fake-inventory-grapher-unknown-version.sh" \
        "$PY" "$GRAPHER" validate --strict-ansible-version-match >/dev/null 2>&1
    rc=$?
    [ "$rc" -ne 0 ]
}

# 5. Managed venv missing -> shim fails clearly (exit 5), not a silent fallback
t_managed_venv_missing_fails_clearly() {
    local out rc
    out=$(ANSIBLE_GRAPHER_VENV_PYTHON=/nonexistent/python "$SKILL_ROOT/scripts/validate-ansible-grapher" 2>&1)
    rc=$?
    [ "$rc" -eq 5 ] && echo "$out" | grep -q "does not silently fall back"
}

# 6. Explicit system Python fallback opt-in succeeds
t_explicit_fallback_succeeds() {
    ANSIBLE_GRAPHER_VENV_PYTHON=/nonexistent/python ANSIBLE_GRAPHER_ALLOW_SYSTEM_PYTHON_FALLBACK=1 \
        "$SKILL_ROOT/scripts/validate-ansible-grapher" --format json >/dev/null 2>&1
}

# 7. Fallback is recorded as degraded runtime isolation, not silently "managed"
t_fallback_recorded_as_degraded() {
    local out
    out=$(ANSIBLE_GRAPHER_VENV_PYTHON=/nonexistent/python ANSIBLE_GRAPHER_ALLOW_SYSTEM_PYTHON_FALLBACK=1 \
        "$SKILL_ROOT/scripts/validate-ansible-grapher" --format json 2>/dev/null)
    echo "$out" | "$PY" -c "
import json, sys
d = json.load(sys.stdin)
c = [x for x in d['checks'] if x['name'] == 'python_runtime_isolation'][0]
assert c['status'] == 'WARN', c
"
}

# 8. Development-version warning (the real installed playbook grapher is 2.11.0-dev0)
t_development_version_warning() {
    local out
    out=$("$PY" "$GRAPHER" validate --format json 2>/dev/null)
    echo "$out" | "$PY" -c "
import json, sys
d = json.load(sys.stdin)
c = [x for x in d['checks'] if x['name'] == 'playbook_grapher_release_status'][0]
assert c['details']['release_status'] == 'development', c
assert c['status'] == 'WARN'  # allow_development_tool_versions defaults to true
"
}

# 9. Development version rejected under ci-light (strict + disallowed) unless overridden
t_development_version_rejected_ci_light() {
    local out rc
    out=$("$PY" "$GRAPHER" project --project-root "$FIXTURES/project" \
        --inventory "$FIXTURES/inventory/valid-hosts.yml" \
        --playbook "$FIXTURES/playbooks/valid-site.yml" \
        --profile ci-light --output-dir "$WORKDIR/ci-light-reject" --force 2>&1)
    rc=$?
    [ "$rc" -ne 0 ] && echo "$out" | grep -qi "development version"
}

# 10. Development version allowed by explicit override even under ci-light
t_development_version_allowed_override() {
    "$PY" "$GRAPHER" project --project-root "$FIXTURES/project" \
        --inventory "$FIXTURES/inventory/valid-hosts.yml" \
        --playbook "$FIXTURES/playbooks/valid-site.yml" \
        --profile ci-light --output-dir "$WORKDIR/ci-light-allow" --force \
        --allow-ansible-version-mismatch --allow-development-tool-versions >/dev/null 2>&1
}

# 19. Provenance fields present in the project manifest
t_manifest_has_provenance() {
    local out="$WORKDIR/provenance-check"
    "$PY" "$GRAPHER" project --project-root "$FIXTURES/project" \
        --inventory "$FIXTURES/inventory/valid-hosts.yml" \
        --playbook "$FIXTURES/playbooks/valid-site.yml" \
        --output-dir "$out" --force >/dev/null 2>&1 || return 1
    "$PY" -c "
import json
m = json.load(open('$out/manifest.json'))
assert 'toolchain_compatibility' in m
assert 'runtime' in m
assert len(m['toolchain_compatibility']) >= 1
for entry in m['toolchain_compatibility']:
    for key in ('status', 'validation_ansible_version', 'grapher_label', 'grapher_ansible_version', 'strict_mode', 'reasons'):
        assert key in entry, (entry, key)
assert 'python_executable' in m['runtime']
"
}

# 20. Compatibility verdict shown in the final console report
t_final_report_shows_compatibility() {
    local out="$WORKDIR/report-check"
    local text
    text=$("$PY" "$GRAPHER" inventory --inventory "$FIXTURES/inventory/valid-hosts.yml" --output-dir "$out" --force 2>&1)
    echo "$text" | grep -q "Toolchain compatibility:"
}

check "Matching Ansible versions -> PASS"                        t_matching_versions
check "Mismatched versions, warn mode -> WARN (not silent)"      t_mismatch_warn_mode
check "Mismatched versions, strict mode -> FAIL"                 t_mismatch_strict_mode
check "Unknown version -> UNKNOWN, not silently compatible"      t_unknown_version
check "Unknown version + strict mode -> FAIL"                    t_unknown_version_strict_fails
check "Managed venv missing -> shim fails clearly (exit 5)"      t_managed_venv_missing_fails_clearly
check "Explicit system Python fallback succeeds"                 t_explicit_fallback_succeeds
check "Fallback recorded as degraded runtime isolation"          t_fallback_recorded_as_degraded
check "Development version -> WARN by default"                   t_development_version_warning
check "Development version rejected under ci-light"              t_development_version_rejected_ci_light
check "Development version allowed by explicit override"         t_development_version_allowed_override
check "Manifest includes provenance/compatibility fields"        t_manifest_has_provenance
check "Final report shows compatibility verdict"                 t_final_report_shows_compatibility

echo
echo "=== $PASS passed, $FAIL failed ==="
if [ "$FAIL" -ne 0 ]; then
    echo "Failed: ${FAILED_NAMES[*]}"
    exit 1
fi
exit 0
