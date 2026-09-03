Title: Spec 0004 — Route closure contract
Category: design-contract
Status: accepted
Promoted: 20260902_0245 by skill-ai-it promote
Accepted: 20260902_0300 by operator
Source: scripts/close_route.py
Summary: What the deterministic repair layer may and may not do. Defined mostly by its prohibitions.

# Spec 0004 — Route closure contract

## What closure DOES

- Adds the minimum provider declaring an unmet `required_capability` at the required strength.
- Escalates to the gate's persona where the task's tags match `persona_mandatory_when_tags`.
- Recomputes `runtime_required` from the selected skills.
- Reports tool prerequisites still to be confirmed.

## What closure MUST NOT do

- Set or change `primary_owner`.
- Decide which gates are true.
- Remove anything the model selected.
- Breach the case's team cap — it **refuses and reports** instead, because trading one hard failure for another is not a repair.

## Selection rule

Deliberately boring, because a repair that varies run to run cannot be regression-tested: the gate's `default_skill` wins if it qualifies; otherwise prefer a
skill over a persona, then a provider that opens no new runtime prerequisite, then one already related to the route, then lexicographic order.

Nine regression tests enforce this contract, each tied to an observed defect rather than restating the implementation.
