# Static Pack vs MCP

Use MCP for dynamic exploration and unknown file scope.

Use static packs for reproducible audits, fixed evidence, human review, and local LLM input.

## Ambiguous Routing

When more than one route is valid:

1. Prefer the route with the smallest safe context footprint.
2. Prefer static output when reproducibility is required.
3. Prefer MCP when scope is unknown and interactive discovery is available.
4. Prefer full source over compression when implementation correctness matters.
5. Prefer project-specific governance over skill defaults.
6. If ambiguity materially affects safety, cost, privacy, or correctness, ask the user.
7. Otherwise, choose the safest route and record the decision.

## Escalation Authority

The user or project owner is the escalation authority for unresolved routing decisions. The skill must not invent an additional approval authority.
