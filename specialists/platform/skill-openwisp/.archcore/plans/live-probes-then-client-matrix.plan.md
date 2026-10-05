---
title: Live probes, then the client evaluation matrix
type: plan
status: accepted
tags: [evaluation, compatibility]
created: 2026-10-05
---

# Plan: Live probes, then the client evaluation matrix

Status: accepted (operator, 2026-10-05)

Promoted by `skill-ai-it promote` on 2026-10-05 from `ARCHCORE_PROMOTION_CANDIDATES.md` (now deleted); operator authorized promotion of all candidates. Candidate source: `SCRATCHPAD.md` (KEEP, Open items); origin memory-keeper `unc-platform-skills-0-2-0-posthook-handoff-20261002`.

## Goal

Raise release claims from PARTIAL to evidenced by testing behaviour on a real install and the pack on every target client.

## Steps

1. Stand up a disposable, version-pinned OpenWISP matching a `compatibility.yaml` row. Never a production instance.
2. Run the behavioural probes for that row and move its `validation_layer` above `observed_install` only with a `test_id`, as the contract requires.
3. With operator-controlled authentication, run the full client matrix in `tests/eval-procedure.md` (Claude Code, Codex; with and without the skill).
4. Record results in `compatibility.yaml`, `sources.yaml` and a CHANGELOG line; widen release claims only for what passed.

## Exit criteria

Every claimed environment row has live evidence at the layer it claims, and every client in the matrix has a recorded with/without result.

## Blockers

Client authentication and a disposable install are operator-controlled.
