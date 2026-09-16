#!/usr/bin/env bash
# Simulates an upstream grapher that exits 0 but writes an invalid/empty artifact at the
# requested -o path. Controlled by $FAKE_GRAPHER_MODE: "empty" (zero-byte file) or
# "garbage" (non-empty but structurally invalid for the requested renderer).
# Used by tests/test-partial-generation-failure.sh.
if [ "$1" = "--version" ]; then
    echo "fake-playbook-grapher 1.0.0 (with ansible 2.99.0)"
    exit 0
fi

out=""
renderer="graphviz"
prev=""
for arg in "$@"; do
    if [ "$prev" = "-o" ] || [ "$prev" = "--output-file-name" ]; then
        out="$arg"
    fi
    if [ "$prev" = "--renderer" ]; then
        renderer="$arg"
    fi
    prev="$arg"
done

case "$renderer" in
    graphviz) ext="svg" ;;
    mermaid-flowchart) ext="mmd" ;;
    json) ext="json" ;;
    *) ext="out" ;;
esac

target="${out}.${ext}"
case "${FAKE_GRAPHER_MODE:-empty}" in
    empty)
        : > "$target"
        ;;
    garbage)
        printf 'this is not valid content for this renderer' > "$target"
        ;;
esac
exit 0
