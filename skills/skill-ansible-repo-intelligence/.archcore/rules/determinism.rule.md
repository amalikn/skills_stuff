---
id: determinism
type: rule
title: Deterministic output
status: accepted
created: 20260703_1545
accepted: 20260703_1604
provenance: promoted by skill-ai-it from CONVENTIONS.md, ARCHITECTURE.md
tags: [determinism, quality]
---

# Deterministic output

Two scans of unchanged sources must produce byte-identical graph.yaml, ANSIBLE_REPO_MAP.md and diagnostics.yaml. Every emitted collection is sorted by a stable key; content hashes are CRLF/BOM-normalized (cross-clone identical); no timestamps live inside content-derived hashes; no random IDs.
