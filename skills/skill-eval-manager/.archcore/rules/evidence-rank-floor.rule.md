---
title: Evidence rank is at least the claim rank
type: rule
status: accepted
tags: [evidence, contract]
provenance: promoted from SKILL.md quality gate by skill-ai-it promote on 20260923_1311
---

# Rule: Evidence rank is at least the claim rank

> Evidence rank is at least the claim rank; lower-ranked evidence never proves a higher-ranked claim.

## Why

Without this floor, a transport-level acknowledgement becomes a claimed user-visible outcome. "API returned 201" is transport evidence and cannot prove a stored, rendered, or durable claim.

## Scope

Layer names and ranks are project-declared and must be monotonic. The default vocabulary is transport 10, stored 20, rendered 30, durable 40; a finance suite may instead use parsed, posted,
reconciled, signed-off. The rule is about the ranks, never the names.

## Enforcement

Executable. `scripts/validate_suite.py` checks the general rule and rejects a suite that violates it. This document states the reasoning; it does not restate the check.

## Source

[SKILL.md](../../SKILL.md) quality gate; [references/02_defining-evals.md](../../references/02_defining-evals.md) "Layer design".
