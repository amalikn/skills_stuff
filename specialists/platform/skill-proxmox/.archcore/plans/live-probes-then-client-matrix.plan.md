---
title: Live probes, then the client evaluation matrix
type: plan
status: proposed
tags: [evaluation, compatibility]
created: 2026-11-07
---

# Plan: Live probes, then the client evaluation matrix

Status: proposed (2026-11-07; mirrors skill-nautobot's accepted plan)

## Goal

Raise the `UNVERIFIED` items and the lab-only rows to evidenced ones, and test the pack on every target client.

## Steps

1. On a disposable or lab node matching a `compatibility.yaml` row (never a production node), run the read-only probes for each `UNVERIFIED`
   item listed in `SCRATCHPAD.md` (Open items); writes only with the engaging project's approval.
2. Move a row above `observed_install` only with a `test_id`, as the contract requires.
3. Run the client matrix in `tests/eval-procedure.md` (Claude Code, Codex; with and without the skill).
4. Record results in `compatibility.yaml`, `sources.yaml` and a CHANGELOG line.

## Exit criteria

Every claimed environment row has evidence at the layer it claims, and every client in the matrix has a recorded with/without result.

## Blockers

A disposable node and client authentication are operator-controlled.
