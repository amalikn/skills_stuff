Title: Rule 0009 — A provenance stamp covers inputs, not neighbours
Category: durable-rule
Status: accepted
Promoted: 20260902_0245 by skill-ai-it promote
Accepted: 20260902_0300 by operator
Source: scripts/evaluate_routing.py
Summary: Stamp what reaches the model, and make the eval consume the same routing contract production uses.

# Rule 0009 — A provenance stamp covers inputs, not neighbours

## Rules

- Result rows carry `prompt_inputs`, naming which stamped files actually reach the model.
- The eval builds its prompt from a marked block **inside the production orchestrator skill**, so the two cannot state different contracts.
- A missing contract block **raises**; it never falls back to a default.

## Why

`orchestrator_sha` once recorded a file the prompt never read. It raised an alarm that proved nothing — and, worse, hid a real gap: the eval was scoring routing
principles kept as a literal inside the evaluator, so eval/production drift was structurally undetectable. A silent fallback would restore exactly that.
