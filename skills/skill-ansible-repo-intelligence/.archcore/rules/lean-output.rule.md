---
id: lean-output
type: rule
title: Lean output — exactly five artifacts
status: accepted
created: 20260703_1545
accepted: 20260703_1604
provenance: promoted by skill-ai-it from AGENTS.md, validator
tags: [design, contract]
---

# Lean output — exactly five artifacts

Only five persistent artifacts are generated under `.ai-context/`: manifest.yaml, ANSIBLE_REPO_MAP.md, graph.yaml, diagnostics.yaml, cache/scan-state.yaml. No per-role summaries, no per-index files, no diagrams. The validator fails the scan if any forbidden redundant index appears.
