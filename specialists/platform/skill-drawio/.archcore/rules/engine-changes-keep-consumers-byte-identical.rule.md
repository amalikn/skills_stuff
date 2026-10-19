---
title: An engine change meant to change nothing leaves consumers byte-identical
type: rule
status: accepted
tags: [engine, consumers, release]
created: 2026-10-19
Last reviewed: 2026-10-19
---

# Rule: An engine change meant to change nothing leaves consumers byte-identical

Status: accepted (operator brief, 2026-10-19; source `AGENTS.md` "Engine consumers and the byte-identity rule"; promoted 2026-10-19 on the operator's instruction "promote and accept")

## Rule

A refactor or fix that should not change output leaves every consumer's drawing byte-identical: render before and after, `cmp` them, and run the consumer's `just test` and `just check`. A change that
alters drawings is a release, with reviewed samples and every consumer re-rendered.

## Enforcement

In part. This pack's example drift check fails when the engine changes its output. A consumer's own drift check (unified-network-controller `check_flow_map`) fails only when that project's check is
run; nothing in this pack runs it.
