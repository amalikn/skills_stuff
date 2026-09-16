#!/usr/bin/env bash
# Simulates an upstream grapher that exits 0 and prints non-empty but non-DOT garbage.
# Used by tests/test-partial-generation-failure.sh.
if [ "$1" = "--version" ]; then
    echo "fake-inventory-grapher 1.0.0"
    exit 0
fi
echo "not a graph at all, just some unrelated text"
exit 0
