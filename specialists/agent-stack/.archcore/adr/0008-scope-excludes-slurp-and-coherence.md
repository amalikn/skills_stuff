Title: ADR 0008 — skill-slurp-chat and skill-project-coherence stay out of Agent Stack
Category: architecture-decision
Status: accepted
Promoted: 20260902_0245 by skill-ai-it promote
Accepted: 20260902_0300 by operator
Source: SCRATCHPAD.md
Summary: Operator scope decision, 2026-09-01, with a git revert as evidence.

# ADR 0008 — skill-slurp-chat and skill-project-coherence stay out of Agent Stack

## Decision

Do not add `skill-slurp-chat` or `skill-project-coherence` to Agent Stack. A brief addition was fully reverted.

## Consequences

- The library stays at 52 capabilities and 37 packages; no managed links for either remain.
- Pre-existing standalone installs of those skills under Claude and Codex were preserved and are out of scope for this project.
