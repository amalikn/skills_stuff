#!/usr/bin/env bash
# Simulates an upstream grapher that exits 0 with normal-looking behavior but produces
# no graph content at all. Used by tests/test-partial-generation-failure.sh.
if [ "$1" = "--version" ]; then
    echo "fake-inventory-grapher 1.0.0"
    exit 0
fi
echo "Processing inventory..." >&2
exit 0
