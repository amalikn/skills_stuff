---
title: System drawings are rendered from a YAML flow map
type: adr
status: accepted
tags: [flowmap, rendering]
created: 2026-10-19
Last reviewed: 2026-10-19
---

# ADR: System drawings are rendered from a YAML flow map

Status: accepted (operator, 2026-10-15, unified-network-controller flow map; sources `references/data-first-diagrams.md`, `sources.yaml` C-D01 and C-D02; promoted 2026-10-19 on the operator's
instruction "promote and accept")

## Context

A system drawing drawn by hand drifts from the system it shows, and nobody can tell when. A drawing generated from data can be checked against that data on every run.

## Decision

A system drawing is rendered from a YAML map of components, flows and dependencies, validated against `schemas/flowmap.schema.json`, rendered deterministically, stamped with a generated banner, and
compared by a drift check in the project's `just check`. It is never drawn or edited by hand; changes go into the map.

## Consequences

- `scripts/render_flowmap.py` exits 1 on drift; `just example-check` runs it in this pack's `just check`; `tests/test_helpers.py` `test_cli_drift_write_and_list` proves it.
- Rendering must stay deterministic and uncompressed for the drift check to mean anything (see rule `drawings-written-uncompressed`).
- Drawings a person made by hand are outside this decision and are never regenerated (rule `hand-edited-drawings-are-source`).
