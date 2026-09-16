#!/usr/bin/env bash
# Fake ansible-inventory-grapher whose --version output carries no parseable version or
# embedded ansible-core version, and is not a venv-wrapper launcher. Used to exercise the
# UNKNOWN toolchain-compatibility path (tests/test-toolchain-compatibility.sh).
if [ "$1" = "--version" ]; then
    echo "fake-inventory-grapher-tool-no-version-here"
    exit 0
fi
echo 'digraph { "all" -> "ungrouped"; }'
exit 0
