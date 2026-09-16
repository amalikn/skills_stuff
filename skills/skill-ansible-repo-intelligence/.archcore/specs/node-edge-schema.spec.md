---
id: node-edge-schema
type: spec
title: Graph node/edge contract
status: accepted
created: 20260703_1545
accepted: 20260703_1604
provenance: promoted by skill-ai-it from schemas/graph.schema.yaml, ARCHITECTURE.md
tags: [schema, graph]
---

# Graph node/edge contract

Every node: id, kind, name, significance (critical|high|normal|low), significance_rule_id, source{path, document, line_start, line_end, content_hash}, resolution{status(resolved|partially_resolved|unresolved|dynamic), confidence, reason}, attributes. Every edge: id, type, from, to, source, resolution, attributes. Source path is always repository-relative; content_hash matches `^sha256:[0-9a-f]{64}$`.
