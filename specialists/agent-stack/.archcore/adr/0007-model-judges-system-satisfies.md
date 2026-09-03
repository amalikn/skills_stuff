Title: ADR 0007 — The model judges; the system satisfies constraints
Category: architecture-decision
Status: accepted
Promoted: 20260902_0245 by skill-ai-it promote
Accepted: 20260902_0300 by operator
Source: MEMORY.md, scripts/close_route.py
Summary: Task understanding, ownership and gate judgement belong to the model; capability, strength and runtime closure are computed deterministically.

# ADR 0007 — The model judges; the system satisfies constraints

## Decision

    model  -> task understanding, decision ownership, gate judgement
    system -> capability closure, strength closure, runtime prerequisites

Closure is performed by `scripts/close_route.py`, not remembered by the model.

## Rationale

This was measured three ways rather than argued. Stating closure as a route invariant in the prompt, and putting a derived capability index in front of the model,
moved **nothing** (Baseline v3: 34/60 against v2's 33/60, the only extra pass a parse flake recovering). A three-way Flash / Pro / Claude holdout then showed the
defect was **model-invariant** — `unsatisfied` was 7 / 6 / 7 on an identical catalogue. Running the same rule as code moved the corpus to 47/60 with zero
regressions and lifted every arm 25–40 points.

Where a rule is a lookup against a finite catalogue, a program does it exactly and a model does it sometimes. `runtime_required` taught the same lesson earlier:
it became reliable the moment it stopped being self-reported.

## Consequences

- Closure is a **repair layer**, not the router. It never sets `primary_owner` and never decides which gates are true.
- The prompt keeps the invariant and the capability index regardless: they cost nothing at inference and improve the initial route.
- Current figures live in `MEMORY.md`, deliberately not here — see the index for why.
