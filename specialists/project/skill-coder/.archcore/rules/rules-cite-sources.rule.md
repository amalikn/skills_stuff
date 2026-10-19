---
title: Every rule says why and cites its source
type: rule
status: accepted
tags: [pack-content, checkers]
created: 2026-10-19
Last reviewed: 2026-10-19
---

# Rule: Every rule says why and cites its source

Status: accepted (stated in `AGENTS.md` "Working rules"; promoted 2026-10-19 on the operator's instruction to add the missing Archcore entries)

## Rule

Every rule in the pack says why in one clause. Every load-bearing rule (one a decision depends on) also has a claim in `sources.yaml` citing its source: an operator rule as `USER_STATED` with its date, an external fact with a primary source and its retrieval date,
and its capture kept verbatim under `documents/` with a `readme.md` index. Material not checked against a source is labelled `UNVERIFIED`, never stated as fact.

## Why

The pack is loaded into other projects as guidance. A rule with no reason cannot be judged when it collides with a project, and a rule with no source cannot be re-checked when the tool or standard it
describes changes.

## Enforcement

`tests/test_package_contract.py`: `test_claim_ledger` (ledger schema) and `test_claim_captures_exist` (each cited capture is present). Which rules
are load-bearing, and that each rule says why, are checked by review: no test can tell a reason from a restatement.
