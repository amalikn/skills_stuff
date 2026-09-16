#!/usr/bin/env bash
# Sourced (not executed) by scripts/graph-*, scripts/validate-ansible-grapher,
# scripts/discover-ansible-project, scripts/clean-generated-graphs, and the justfile.
#
# Selects the managed working-cache venv Python by default and FAILS CLEARLY if it is
# missing — it does not silently fall back to system python3. Fallback is only used
# when explicitly requested via --allow-system-python-fallback or
# ANSIBLE_GRAPHER_ALLOW_SYSTEM_PYTHON_FALLBACK=1, and is always reported (both here and
# by the Python process itself via ANSIBLE_GRAPHER_PYTHON_FALLBACK_USED).
#
# ANSIBLE_GRAPHER_VENV_PYTHON overrides the expected venv path — this exists so tests
# can simulate "managed venv missing" without touching the real venv.
#
# Sets: RESOLVED_PYTHON

_ansible_grapher_venv_python="${ANSIBLE_GRAPHER_VENV_PYTHON:-/Volumes/Data/_ai/_skills/skills-working-cache/skill-ansible-grapher/.venv/bin/python}"
_ansible_grapher_allow_fallback="${ANSIBLE_GRAPHER_ALLOW_SYSTEM_PYTHON_FALLBACK:-false}"

for _ansible_grapher_arg in "$@"; do
    if [ "$_ansible_grapher_arg" = "--allow-system-python-fallback" ]; then
        _ansible_grapher_allow_fallback=true
    fi
done

case "$_ansible_grapher_allow_fallback" in
    true|1|yes|on) _ansible_grapher_allow_fallback=true ;;
    *) _ansible_grapher_allow_fallback=false ;;
esac

if [ -x "$_ansible_grapher_venv_python" ]; then
    RESOLVED_PYTHON="$_ansible_grapher_venv_python"
    unset ANSIBLE_GRAPHER_PYTHON_FALLBACK_USED
elif [ "$_ansible_grapher_allow_fallback" = "true" ]; then
    RESOLVED_PYTHON="python3"
    export ANSIBLE_GRAPHER_PYTHON_FALLBACK_USED=1
    echo "WARNING: managed venv Python missing at '$_ansible_grapher_venv_python' — falling back to system python3 (explicit opt-in via --allow-system-python-fallback / ANSIBLE_GRAPHER_ALLOW_SYSTEM_PYTHON_FALLBACK=1). Runtime isolation is degraded." >&2
else
    _ansible_grapher_cache_dir="$(dirname "$(dirname "$_ansible_grapher_venv_python")")"
    echo "ERROR: managed Python venv missing at '$_ansible_grapher_venv_python'." >&2
    echo "This skill does not silently fall back to system Python. Rebuild the venv:" >&2
    echo "  cd $_ansible_grapher_cache_dir && mise install && mise exec -- python -m venv .venv && .venv/bin/python -m pip install PyYAML" >&2
    echo "Or opt in explicitly (only if you understand the isolation trade-off):" >&2
    echo "  --allow-system-python-fallback   (or ANSIBLE_GRAPHER_ALLOW_SYSTEM_PYTHON_FALLBACK=1)" >&2
    unset _ansible_grapher_venv_python _ansible_grapher_allow_fallback _ansible_grapher_arg _ansible_grapher_cache_dir
    exit 5
fi

unset _ansible_grapher_venv_python _ansible_grapher_allow_fallback _ansible_grapher_arg
