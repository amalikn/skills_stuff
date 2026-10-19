---
title: Generated drawings are written uncompressed
type: rule
status: accepted
tags: [file-format, drift]
created: 2026-10-19
Last reviewed: 2026-10-19
---

# Rule: Generated drawings are written uncompressed

Status: accepted (sources `references/file-format.md`, `scripts/drawio/mxfile.py` `mxfile()`; promoted 2026-10-19 on the operator's instruction "promote and accept")

## Rule

Generated drawings are written with `compressed="false"`, so they diff in review and the drift check can compare them byte for byte.

## Enforcement

`mxfile()` writes `compressed="false"`; the drift check (ADR `flow-maps-are-data`) depends on it.
