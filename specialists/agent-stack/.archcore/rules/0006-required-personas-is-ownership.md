Title: Rule 0006 — required_personas is mandatory ownership, not an ideal team
Category: durable-rule
Status: accepted
Promoted: 20260902_0245 by skill-ai-it promote
Accepted: 20260902_0300 by operator
Source: evals/routing-cases.toml
Summary: Four distinct concepts, authored independently: required_personas, preferred_personas, tags, and capability.

# Rule 0006 — required_personas is mandatory ownership, not an ideal team

## Rule

| Concept              | Means                                                                            |
| -------------------- | -------------------------------------------------------------------------------- |
| `required_personas`  | Ownership or independent judgement genuinely mandatory for **this** case          |
| `preferred_personas` | Would improve the route without being required                                    |
| `tags`               | Semantic characteristics of the **task**; they say *why* a generic policy applies |
| capability           | Enough for ordinary fulfilment                                                    |

Do not use `required_personas` to force a complete team. **Never derive tags from `required_personas`** — that fits the tags to the expected answer and destroys
the corpus's ability to test task understanding separately from route correctness.

## Why tags stay a model judgement

A pattern-match over task text agreed with the corpus on only **5 of 21** relevant cases — `auth` matching "authoritative", among worse. A cheap proxy would
manufacture failures.
