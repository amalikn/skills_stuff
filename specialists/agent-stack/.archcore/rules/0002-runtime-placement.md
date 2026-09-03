Title: Rule 0002 — Runtime placement and interpreter pinning
Category: durable-rule
Status: accepted
Promoted: 20260902_0245 by skill-ai-it promote
Accepted: 20260902_0300 by operator
Source: AGENTS.md
Summary: The venv lives in the working-cache peer, never in the repo, and recipes address it by path rather than through any implicit resolution.

# Rule 0002 — Runtime placement and interpreter pinning

## Rule

- The maintenance venv lives at `skills-working-cache/agent-stack/venv`, **never inside this repo**.
- Recipes address the interpreter **explicitly by path** via the justfile's `{{py}}` variable, and every Python recipe depends on `_require-venv`.

## Why both halves matter

A bare `python3` resolves to whatever the host has on `PATH` — and it *works* on the machine it was written on, which is what makes it worth a gate rather than a
preference. An **implicit** `mise exec -- python` is only marginally better: it happens to land on the venv today, but the dependency is invisible at the call
site and degrades silently if activation stops applying. Observed 2026-09-01: the implicit form made both the pinning and an in-repo venv violation invisible at
every call site simultaneously.

`just runtimes` prints declared versus resolved, so the invariant is checkable in seconds. Both halves are enforced by governance checks.
