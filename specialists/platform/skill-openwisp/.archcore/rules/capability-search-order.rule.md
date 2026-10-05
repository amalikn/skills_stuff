---
title: Capability search order
type: rule
status: accepted
tags: [capability, extension]
created: 2026-10-05
---

# Rule: Capability search order

Status: accepted (operator, 2026-10-05)

Promoted by `skill-ai-it promote` on 2026-10-05 from `ARCHCORE_PROMOTION_CANDIDATES.md` (now deleted); operator authorized promotion of all candidates. Candidate sources: `AGENTS.md` (Working rules), `SKILL.md` (Search before building). USER_STATED 2026-10-01.

## Rule

Before building anything for OpenWISP, search in this order and state at each step why the previous level cannot meet the acceptance test:

1. Existing OpenWISP core capability.
2. Installed or maintained provider apps/modules and relevant NTC tooling.
3. Supported extension points of those components.
4. Compatible external FOSS and its supported seams.
5. A from-scratch component, only when the acceptance test still cannot be met.

Prefer add-ons. Log every core patch so it is reapplied, adapted or retired after an upgrade, with a regression test on the behaviour it relies on.

## Enforcement

Judgement, applied at design time; no automated check. `SKILL.md` (Search before building) restates the order for the agent at the point of decision; this document is the durable source.
