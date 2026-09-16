---
id: incremental-safe-rebuild
type: adr
title: Incremental = fingerprint short-circuit + safe full rebuild
status: accepted
created: 20260703_1545
accepted: 20260703_1604
provenance: promoted by skill-ai-it from ARCHITECTURE.md
tags: [incremental]
---

# Incremental = fingerprint short-circuit + safe full rebuild

Decision: incremental scan short-circuits when parser+config fingerprint and all file hashes match (outputs already current). Any change triggers a full deterministic rebuild, because cross-file resolution needs the whole graph to stay correct. Incremental-force output is byte-identical to a full scan.
