---
title: Live probes, then the client evaluation matrix
type: plan
status: accepted
tags: [evaluation, compatibility]
created: 2026-11-07
---

# Plan: Live probes, then the client evaluation matrix

Status: accepted (operator, 2026-11-09, after the archcore review that corrected it). Mirrors skill-nautobot's accepted plan.

## Goal

Raise the `UNVERIFIED` items, the lab-only rows and the documentation-only sections to evidenced ones, and test the pack on every target client.

## Steps

1. On a disposable or lab node matching a `compatibility.yaml` row (never a production node), run the read-only probes for each `UNVERIFIED`
   item listed in `SCRATCHPAD.md` (Open items); writes only with the engaging project's approval.
2. Re-run the operations cookbook on the lab node once it is on 9.2 (pending in its update queue), and record the result as a new
   `compatibility.yaml` row.
3. On a lab cluster of three or more nodes, exercise the sections that rest on documentation alone since 2026-11-09: hyperconverged Ceph
   (`references/storage.md`), migration and resource mappings (`references/qemu-vms.md`), notifications (`references/monitoring-and-metrics.md`)
   and node removal (`references/architecture-and-cluster.md`). Each run that confirms or contradicts a claim (P-C22 to P-C26) is a Learned or
   Disputed entry plus a CHANGELOG line.
4. Move a row to a live layer (`api_accepted` and above) only with a `test_id`, as the contract requires.
5. Run the client matrix in `tests/eval-procedure.md` (Claude Code, Codex; with and without the skill), scenarios P-S01 to P-S20.
6. Record results in `compatibility.yaml`, `sources.yaml` and a CHANGELOG line.

## Exit criteria

Every claimed environment row has evidence at the layer it claims, every documentation-only section has a lab run or an explicit "not
tested" note, and every client in the matrix has a recorded with/without result.

## Blockers

A disposable node, a lab cluster of three nodes (step 3) and client authentication are operator-controlled.
