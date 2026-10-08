# API and writers

## Reader contract

The project experienced unordered pagination that produced a distorted, incomplete object set. Stable ordering is therefore a tested reusable pattern, not decorative API hygiene. Ask the source API
for a unique stable order or use its documented cursor/snapshot guarantee, follow only its returned continuation, impose a finite page bound, and record page identity plus stable object identity.

Sorting does not create a snapshot. Stop and report ambiguity when a continuation repeats, a page fails to advance, an expected identity repeats, an identity disappears between pages, a page is empty
before completion, or the source changes during traversal. Blind deduplication can hide both missing and duplicated data, so it does not prove completeness. Retrying may be appropriate only for named,
idempotent read failures; it cannot repair changing-data semantics.

## Writer contract

Keep readers and writers separately identifiable. The caller owns authentication, authorization, base URL, retry policy, and secret delivery; reusable guidance must not embed them. A writer should
declare its service identity and owned fields, read enough existing state to decide idempotence, produce a reviewable plan, support dry-run without mutation, and report an ownership conflict rather
than overwriting another authority.

Before a write ask: Which object identity is authoritative? Which fields may this identity own? Does the desired state already exist? Does a partial failure have a safe retry? Is a mutation allowed
by the governing project? If any answer is missing, fail closed with diagnostics that distinguish authentication, permission, model validation, ownership conflict, pagination ambiguity, and transport
failure. Do not treat a successful request as evidence that downstream workers or external devices changed.

Relationship serialization, query depth, permissions, pagination, and Job/API details vary by release and query options. Confirm the exact endpoint and product version before integration code relies
on a response shape. Acceptance means the read set is complete under its stated contract and every planned write has explicit authority, identity, idempotence, and an observable outcome. Claims N-C03
and N-C13.

## Reader algorithm and failure example

UNC's `nautobot_paging.listing()` sets `limit` and `sort=id` on the first request; callers follow returned `next`. Its regression test proves those two operations,
**not** a generic snapshot or duplicate detector. Before using a list to plan writes, enforce the extra reader contract:

```text
Pseudocode, not an executable Nautobot client:
seen_urls = {}; seen_ids = {}; pages = 0
request first URL with verified unique ordering (or documented cursor)
while URL exists:
    reject repeated URL; increment pages; reject pages > finite bound
    GET; retry only named transient read errors, with capped attempts/backoff
    require complete response shape; reject missing or repeated stable IDs
    append results; follow the returned next exactly
compare count/identity manifest if available; otherwise label snapshot completeness unproved
```

Synthetic failure: page 1 yields `a,b` and `next=offset=2`; page 2 yields `b,c`. Four rows are not four objects: reject repeated `b`, do not silently
deduplicate to `a,b,c`, since `d` may have been skipped. A repeated continuation, missing `results`, premature empty page with `next`, or page-bound overflow is an
error. Sorting alone cannot prevent concurrent insert/delete from moving an offset boundary; use a documented cursor/snapshot, or re-read against a stable manifest and
state remaining uncertainty. No mutation may rely on ambiguous traversal.

## Writer decision and observable result

Match by immutable authoritative identity before mutable name/address. Dry-run output should give action, matched ID and corroboration, before/after **owned fields**,
unchanged fields, conflicts and dependent links. Reject ambiguous matches and missing ownership. On apply, validate server-side, record per-object success/failure,
re-read affected objects and relationships, and distinguish an API save from a downstream Job/device outcome. A partial batch is not success: retry idempotent records
only after re-reading current state and expose compensation/rollback. Verify exact relationship serialization in the target version's schema or a disposable fixture;
this reference promises no one shape. Read [authority and modeling](authority-and-modeling.md) and [staged onboarding](staged-onboarding.md) for combined tasks.

> **Learned 2026-10-08** · Nautobot 3.2.3 · VERIFIED_PRIMARY · Source: a get-or-create seed on one deployment, its dry run reordered and re-run: no Manufacturer created, then created on apply with `cpu_architecture` set; nautobot/core/api/serializers.py line 782 (CustomFieldModelSerializerMixin) in the installed source · Falsifier: a dry run of such a seed that leaves a new object, or a POST whose `custom_fields` are ignored on create
> A seed built from get-or-create helpers writes on a dry run whenever a helper call sits above the dry-run branch: taxonomy (Platform, Manufacturer, Device Type, interface templates) is created before the plan is printed. Plan with GET only and put every get-or-create below the branch. A create may carry `custom_fields` in the same POST (a Device Type's select value set at birth), so no follow-up PATCH is needed for a field the seed states.
