#!/usr/bin/env bash
# Simulates an upstream grapher that exits 0, writes normal-looking stdout/stderr, but
# never creates the requested output file. Used by tests/test-partial-generation-failure.sh.
if [ "$1" = "--version" ]; then
    echo "fake-playbook-grapher 1.0.0 (with ansible 2.99.0)"
    exit 0
fi
echo "Parsing playbook..." >&2
echo "Done." >&2
exit 0
