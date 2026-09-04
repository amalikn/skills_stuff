Title: Plan 0003 — Holdout 2 protocol
Category: plan
Status: accepted
Proposed: 20260902_1140 direct, per .archcore/README.md step 2
Accepted: 20260904_1150 by operator
Source: docs/routing-evaluation/holdout24-analysis-20260902_1120.md, .archcore/specs/0006-runner-qualification.md
Summary: What must be true before a second blind corpus is authored, and the order in which it is spent.

# Plan 0003 — Holdout 2 protocol

Holdout 24 is spent. A second one is the only way to get unseen evidence again, and it is worth authoring **only once the things that spoiled the first are fixed**.

## Preconditions, in order

1. **Runner qualified** for at least the corpus size, per [spec 0006](../specs/0006-runner-qualification.md). This is the blocker; it is not negotiable and it is cheap.
2. **The harness can describe a failure it did not cause** — stdout captured alongside stderr on a non-zero exit, and the exit code surfaced. Until then every runner fault is the same opaque line.
3. **The gate-judgement question is settled or deliberately parked.** All 19 scored cases set all four gates true, and every stored arm since gates were defined does the same. A second holdout run
   before this is understood will measure the same constant again and learn nothing new from it.
4. **A new freeze recorded after the last edit**, verified by `just freeze-check`, captured beside the results.

## Authoring rules, unchanged from Holdout 24

Blind to every previous corpus, including the spent 24. Task text first and in full; ownership, gates and capabilities assigned afterwards from the task as written. No deliberate gate balancing. Both
directions of `runtime_required` asserted honestly. Integrity tests over the new file before it is run.

## What the spent 24 may and may not be used for

**May:** become regression cases in the development corpus, once their independence is already gone; inform which ownership boundaries are worth resolving; be re-scored under a later scorer to compare
scorers, never to compare routers.

**May not:** be tuned against, be quietly amended into agreement with the router, or be cited again as unseen evidence. The three ownership failures stay exactly as authored.

## Status drift is the failure this plan exists to prevent twice

Executing Holdout 24 produced evidence while `MEMORY.md` and `SCRATCHPAD.md` still said it was unexecuted. That is the same class of defect as a stale constant: a claim nothing verifies. Reconciled by
hand on 20260902; the durable fix is to derive run status from the stored rows rather than restate it, since every row already carries its own provenance stamp.
