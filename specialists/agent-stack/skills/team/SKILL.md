---
name: team
description: Form the smallest sufficient temporary persona team for a task using Agent Stack routing ownership and non-overlap rules. Normally invoked by skill-agent-stack rather than directly by the operator.
argument-hint: "[task description]"
disable-model-invocation: true
---

# Form a Temporary Agent Stack Team

Use root `routing.toml` and the persona files under `personas/`. This skill chooses **personas only**; `skill-agent-stack` separately chooses procedural skills.

## Task

$ARGUMENTS

## Selection Algorithm

1. Identify the concrete decision/output and affected domains.
2. Select exactly one primary persona whose `owns`/`intents` best match that decision.
3. Add supporting personas only for non-duplicative required inputs or gates.
4. Add `critic-munger` only for material/high-risk/weak-evidence decisions or explicit independent review.
5. Keep the normal team to 1–4 domain personas. Exceed four only when the task truly contains multiple independent decisions.
6. Reject ornamental roles: shared vocabulary or general usefulness is not a reason to select a persona.

## Ownership Rules

- CEO: enterprise direction, strategic priority, resource allocation.
- CFO: economic viability, financial guardrails, pricing economics.
- CTO: technical architecture and technology strategy.
- Product: product outcome, scope, requirements/prioritisation.
- Interaction: behaviour, workflows, state transitions.
- UI: visual hierarchy/design system/interface presentation.
- Full-Stack: application implementation.
- DevOps: delivery mechanism and operational readiness.
- QA: quality risk and release confidence.
- Research: evidence synthesis and source quality.
- Marketing: market message and marketing channels.
- Sales: sales process, qualification, conversion.
- Operations: operating process and pilot execution.
- Critic: independent challenge; not the primary domain owner.

## Required Output

```markdown
Primary: <persona> — <decision it owns>
Support:
- <persona> — <unique input/gate>
Excluded plausible roles:
- <persona> — <why unnecessary>
Sequence: <handoff order>
```

Explicitly naming excluded plausible roles is required for non-trivial routing because it guards against team inflation.
