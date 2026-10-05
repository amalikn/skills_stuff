# Staged onboarding

## State machine

Use `observation → identity candidates → corroboration → ambiguity or Staged object → review → promotion`. Preserve source, capture time, vantage, confidence, and the facts used to reach each state.
An observation is never an instruction to create or overwrite production inventory.

One identifier is insufficient: labels move, addresses are reused, serials may be absent, and a service name can survive a hardware replacement. Corroborate with independent evidence such as a stable
management identity, serial, physical record, existing inventory, or an authenticated handoff. When facts disagree, retain the candidates and contradiction rather than selecting the most convenient
match. An ambiguity queue is a valid result and a reason to stop automation.

## Brownfield and greenfield

For brownfield onboarding, reconcile what exists against intended inventory and represent safe candidates as Staged. A discovered name is an observation; an intended name is an approved convention.
Do not silently rename an existing intended object to match a poll result. Handle moved units, replacements, duplicate identities, and stale records as separate review cases with a visible proposed
action and rollback path. Dry-run output should show create, adopt, link, rename, skip, and ambiguity actions distinctly.

Greenfield provisioning begins with approved intent and controlled creation; brownfield onboarding begins with uncertain evidence. Treating them as the same bulk-import workflow is a common source of
accidental duplicate records and ownership loss.

## Promotion acceptance

Promote only after a reviewer accepts the corroborated identity, field ownership, intended name, Location/Namespace/Tenant placement, lifecycle state, and downstream linkage. Stop when identity is
ambiguous, the writer lacks ownership, a pre-existing record has contradictory authority, or the plan would create a duplicate. This is a project-derived brownfield pattern, not a promise that a
particular Nautobot workflow automates it. Claim N-C05.

## Identity decisions and a dry-run plan

| Evidence                                         | Proposed action                | Stop condition                                    |
| ------------------------------------------------ | ------------------------------ | ------------------------------------------------- |
| New, corroborated identity and approved location | Create Staged                  | Another record has the stable ID                  |
| Existing stable ID with matching physical facts  | Adopt existing                 | Its owner/intent conflicts with observation       |
| Existing Device, missing association only        | Link after relationship review | Link already points elsewhere                     |
| Unsupported or out-of-scope observation          | Skip with reason               | Never reinterpret skip as accepted inventory      |
| Serial/MAC/name candidates disagree              | Hold for identity review       | No automatic tie-break by address or name         |
| Hardware appears at another site                 | Hold as moved-hardware case    | No silent Location rewrite                        |
| Old unit gone and new unit serves same role      | Replacement workflow           | Do not overwrite old serial or monitoring history |
| Two records claim one stable identity            | Duplicate investigation        | Do not create a third record                      |

Synthetic capture: `obs-41` at 10:00 UTC reports serial `SYN-21`, MAC `02:00:00:00:00:21`, and site `A`; inventory has a Staged Device with that serial
and MAC but no interface link. Dry run: `adopt existing Device D-21; link management interface after confirming ownership; no rename; no status change; 0 writes`.
If a second Device has the same serial at site `B`, plan becomes `hold conflicting identity D-21/D-22; 0 writes`. The reviewer sees both source times and the
independent evidence; the importer cannot resolve it by first match. For promotion, require reviewed identity, intended placement and field writer, reachable
dependent links, a fresh dry-run diff, authorized actor and a visible postcondition (the right Device and links, not just an API response). The UNC site-prefix and
operator batch rules are **project policy examples**, not Nautobot defaults. Read [authority and modeling](authority-and-modeling.md) for writer ownership and
[lifecycle and replacement](lifecycle-and-replacement.md) for swaps.
