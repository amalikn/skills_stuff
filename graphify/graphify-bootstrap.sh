#!/usr/bin/env bash
# graphify-bootstrap — pre-build the structural (free) parts of a graphify graph
# from the CLI, before handing off to a Claude Code session for semantic extraction.
#
# What this does (no LLM, no token cost):
#   1. detect    — file inventory + per-category counts
#   2. AST       — extract code structure (only if code files present)
#   3. build     — networkx graph from AST
#   4. cluster   — Louvain community detection
#   5. export    — graph.json, graph.html (interactive viz)
#
# What it leaves for Claude Code:
#   - semantic extraction for docs/papers/images (LLM-only, requires agent)
#   - community labeling (cheap, naming pass)
#
# Usage:
#   graphify-bootstrap [path]          # default: current dir
#   graphify-bootstrap /path/to/repo
#
# After this completes, run inside a Claude Code session:
#   /graphify <path> --update          # adds semantic edges, merges with bootstrap
#
# Token savings (vs running /graphify cold):
#   100% code     → ~95% reduction (AST handles everything; only labeling burns tokens)
#   50/50 mixed   → ~40% reduction (CLI handles code; agent handles only docs)
#   100% docs     → 0% reduction (no AST work; full semantic burn unavoidable)
#
# Honors .graphifyignore if present.

set -euo pipefail

TARGET="${1:-.}"
TARGET=$(cd "$TARGET" 2>/dev/null && pwd) || { echo "error: $1 not a directory" >&2; exit 1; }

# Resolve the graphify Python interpreter (uv tool install is the canonical path)
GRAPHIFY_BIN=$(command -v graphify 2>/dev/null || true)
if [[ -z "$GRAPHIFY_BIN" ]]; then
    echo "error: 'graphify' CLI not on PATH. Install with: uv tool install graphifyy" >&2
    exit 1
fi
GRAPHIFY_PY=$(head -1 "$(readlink -f "$GRAPHIFY_BIN" 2>/dev/null || readlink "$GRAPHIFY_BIN" || echo "$GRAPHIFY_BIN")" | tr -d '#!')
if [[ -z "$GRAPHIFY_PY" || ! -x "$GRAPHIFY_PY" ]]; then
    GRAPHIFY_PY="python3"
fi

cd "$TARGET"
mkdir -p graphify-out

echo "[bootstrap] Target: $TARGET"
echo "[bootstrap] Python: $GRAPHIFY_PY"

"$GRAPHIFY_PY" - <<'PY'
import json
from pathlib import Path
from graphify.detect import detect, save_manifest
from graphify.extract import collect_files, extract
from graphify.build import build_from_json
from graphify.cluster import cluster, score_all
from graphify.export import to_json, to_html

target = Path('.').resolve()
det = detect(target)
total = det.get('total_files', 0)
words = det.get('total_words', 0)
print(f"[bootstrap] Detected: {total} files, ~{words:,} words")
for cat, files in det.get('files', {}).items():
    if files:
        print(f"[bootstrap]   {cat}: {len(files)} files")

if total == 0:
    print('[bootstrap] No supported files found. Stopping.')
    raise SystemExit(0)

# Collect code files for AST
code_paths = []
for f in det.get('files', {}).get('code', []):
    p = Path(f)
    code_paths.extend(collect_files(p) if p.is_dir() else [p])

if code_paths:
    print(f"[bootstrap] Running AST on {len(code_paths)} code file(s)...")
    ast = extract(code_paths, cache_root=Path('.'))
    print(f"[bootstrap] AST: {len(ast['nodes'])} nodes, {len(ast['edges'])} edges (free, no LLM)")
else:
    ast = {'nodes': [], 'edges': [], 'input_tokens': 0, 'output_tokens': 0}
    print('[bootstrap] No code files — AST step skipped.')

# Build graph + cluster (only meaningful if AST produced nodes)
if ast['nodes']:
    G = build_from_json({'nodes': ast['nodes'], 'edges': ast['edges'], 'hyperedges': []})
    communities = cluster(G)
    cohesion = score_all(G, communities)
    to_json(G, communities, 'graphify-out/graph.json')

    # Save manifest so /graphify --update can detect changed files
    save_manifest(det['files'])

    # Persist Python interpreter path for the slash command's --update step
    Path('graphify-out/.graphify_python').write_text(__import__('sys').executable)

    # HTML viz (skip if too large)
    if G.number_of_nodes() <= 5000:
        labels = {cid: f"Community {cid}" for cid in communities}
        to_html(G, communities, 'graphify-out/graph.html', community_labels=labels)
        viz_msg = f"graph.html written ({G.number_of_nodes()} nodes)"
    else:
        viz_msg = f"graph.html skipped ({G.number_of_nodes()} > 5000 nodes)"

    print(f"[bootstrap] Graph: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges, {len(communities)} communities")
    print(f"[bootstrap] {viz_msg}")
else:
    # Save manifest anyway so --update knows what was detected
    save_manifest(det['files'])
    Path('graphify-out/.graphify_python').write_text(__import__('sys').executable)
    print('[bootstrap] No structural graph built — semantic extraction is the only path.')

# Determine non-code file count for the handoff message
non_code = sum(len(v) for k, v in det.get('files', {}).items() if k != 'code')
print()
print('[bootstrap] CLI work complete. Token cost so far: 0.')
if non_code > 0:
    print(f'[bootstrap] To add semantic edges for {non_code} non-code file(s), run in Claude Code:')
    print(f'[bootstrap]   /graphify "{target}" --update')
else:
    print('[bootstrap] No non-code files to extract. Run /graphify only if you want community labels.')
PY
