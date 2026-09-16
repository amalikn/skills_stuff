---
id: ruamel-round-trip
type: adr
title: Use ruamel round-trip mode for line provenance
status: accepted
created: 20260703_1545
accepted: 20260703_1604
provenance: promoted by skill-ai-it from ARCHITECTURE.md
tags: [yaml, parsing]
---

# Use ruamel round-trip mode for line provenance

Decision: load YAML with ruamel `typ="rt"` rather than `"safe"`. Safe mode discards line/column info (`.lc`) required for source provenance. Round-trip mode preserves it and is still safe (no arbitrary Python object construction); `!vault`/`!unsafe` are registered as opaque constructors.
