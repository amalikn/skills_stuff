---
title: Project values live in a Profile, never in the engine
type: adr
status: accepted
tags: [flowmap, engine]
created: 2026-10-19
Last reviewed: 2026-10-19
---

# ADR: Project values live in a Profile, never in the engine

Status: accepted (operator brief, 2026-10-19; sources `SKILL.md` "Using the flow-map engine", `scripts/flowmap/profile.py`; promoted 2026-10-19 on the operator's instruction "promote and accept")

## Context

The engine came out of one project (unified-network-controller). Any value of that project left in the engine would leak into every other project's drawings.

## Decision

Everything that differs between projects lives in a `Profile`. The engine holds no project's values. `Profile.from_drawing()` derives defaults from the map's optional `drawing:` block, so a project
with no code of its own still sets them.

## Consequences

- The 2026-10-19 review found two project values in `Profile` defaults (`default_tier=2`, band title "Credentials and stores"); both are neutral now (0, "Stores and secrets"), and the source project
  passes its own values with its drawing byte-identical.
- `tests/test_helpers.py` `test_profile_defaults`, and the example and minimal maps rendering with no project code (`test_example_is_current_clean_and_complete`,
  `test_minimal_map_renders_clean_and_deterministic`), enforce it.
