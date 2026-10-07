#!/usr/bin/env bash
set -euo pipefail

mkdir -p .ai-context

echo "[1/6] Checking governance files..."
for f in AGENTS.md AI_NAVIGATION.md context-map.yaml CHANGELOG.md; do
  if [ ! -f "$f" ]; then
    echo "WARN: missing $f"
  fi
done

echo "[2/6] Checking Archcore..."
if command -v archcore >/dev/null 2>&1; then
  if [ -d ".archcore" ]; then
    archcore status || archcore doctor || true
  else
    archcore init
    archcore status || archcore doctor || true
  fi
else
  echo "INFO: archcore CLI not found; skipping"
fi

echo "[3/6] Running Graphify..."
if command -v graphify >/dev/null 2>&1; then
  if [ -f "graphify-out/graph.json" ]; then
    graphify update . || true
  elif graphify update . >/dev/null 2>&1; then
    graphify update . || true
  else
    echo "INFO: graphify CLI found, but this project is not initialized for graph updates"
    echo "INFO: run the project-specific Graphify bootstrap command before expecting graph output"
  fi
else
  echo "INFO: graphify CLI not found; skipping"
fi

echo "[4/6] Building Repomix governance pack..."
if command -v repomix >/dev/null 2>&1; then
  repomix --config repomix.config.json || true
else
  echo "INFO: repomix CLI not found; skipping"
fi

echo "[5/6] Checking context pack freshness..."
if [ -f ".ai-context/governance-pack.md" ] && [ -f "CHANGELOG.md" ]; then
  if [ "CHANGELOG.md" -nt ".ai-context/governance-pack.md" ]; then
    echo "INFO: .ai-context/governance-pack.md may be stale (older than CHANGELOG.md). Regenerate with repomix."
  fi
fi

echo "[6/6] Context preflight complete."
