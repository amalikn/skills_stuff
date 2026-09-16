---
title: Evidence-First Answering Guide
status: accepted
date: 20260525
provenance: docs/evidence-contract.md, schemas/evidence-bundle.schema.yaml, SKILL.md
---

# Evidence-First Answering Guide

## Principle

Every answer must be grounded in a retrieved EvidenceBundle. The agent must never answer a factual question about project documents, contracts, rates, or wiki articles from training knowledge. If there is no valid bundle, report `RETRIEVAL_NOT_READY` and stop.

## Required answer discipline

1. **Retrieve first.** Run the appropriate rag-tools command before answering.
2. **Answer only from `excerpt`.** The `excerpt` field is the only permitted answer source.
3. **Do not infer.** If an amount, date, clause reference, or identifier is not in the excerpt, do not state it.
4. **Say "not found."** If the evidence does not support the question, say "not found in retrieved evidence" — do not guess.
5. **Surface warnings.** If `retrieval_warnings` is non-empty, surface it in the answer — do not silently use low-confidence evidence.
6. **Cite the source.** Minimum citation is `source_file`. Preferred: `source_file` + (`section_id` OR `heading`).

## Bundle validity check

Before answering from a bundle, verify:

- [ ] `source_file` is present and is an absolute file path (not a Qdrant collection name)
- [ ] `excerpt` is non-empty
- [ ] `retrieval_mode` matches the mode actually used
- [ ] `retrieval_warnings` inspected — warn the user if populated

If `excerpt` is empty → bundle is invalid → do not answer → report `RETRIEVAL_NOT_READY`.

## Good answer pattern

```
Retrieved from: /path/to/source.md § C2.11 (direct_structured_lookup)

The rebate period 3 credit rate is [exact text from excerpt].
```

## Bad answer pattern (forbidden)

```
The rebate credit rate is approximately 12% based on typical wholesale billing agreements.
```
(Invented; not from excerpt — forbidden even if plausible.)

## When multiple bundles conflict

- Do not merge conflicting excerpts into a single answer.
- Report both excerpts and their sources.
- State: "Sources conflict. [Source A] states [X]. [Source B] states [Y]. Manual review required."

## Retrieval warning handling

| Warning | Required action |
|---|---|
| `source file missing` | Report file missing; do not answer |
| `vector RAG score < 0.5` | Flag as low-confidence; do not treat as authoritative |
| `fallback used` | State which mode was used; note fallback in citation |
| `partial match` | Limit claim to what is actually in the excerpt |
| `structured lookup — no exact section ID match` | State section was not found; do not guess nearby content |

## Checklist

See `checklists/evidence-bundle-validation.md` for the full bundle validation gate.

## Related

- [specs/evidence-bundle-contract.md](../specs/evidence-bundle-contract.md)
- [schemas/evidence-bundle.schema.yaml](../../schemas/evidence-bundle.schema.yaml)
- [docs/evidence-contract.md](../../docs/evidence-contract.md)
- [checklists/evidence-bundle-validation.md](../../checklists/evidence-bundle-validation.md)
- [dynamic-retrieval-routing.md](dynamic-retrieval-routing.md)
