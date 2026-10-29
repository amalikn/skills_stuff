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

> **Learned 2026-10-13** · Nautobot 3.2.3 · VERIFIED_SECONDARY · Source: observed against a live 3.2.3 API (a site whose devices sit in child Locations) · Falsifier: `/dcim/cables/?location_id=<site>` returning Cables whose ends are in the site's child Locations
> `/dcim/cables/?location_id=<id>` returns only Cables with an end at that exact Location, not its child Locations; read a site's Cables by device instead (`device_id=` repeated). Keep the repeated ids per query small: forty `device_id` parameters in one query string reset the connection behind a reverse proxy, ten worked.

> **Learned 2026-10-15** · Nautobot 3.2.3 · VERIFIED_PRIMARY · Source: timed read-only reads of three sites on one deployment (old-looma 140 Devices in 62 child Locations) · Falsifier: `/dcim/interfaces/?location=<site>` returning the interfaces of Devices in its child Locations, or depth-1 Cables taking as long as depth 2
> On Devices `?location=<id>` takes the whole subtree; on interfaces and the app's wireless links it is the exact Location only, and `/dcim/cables/?location=<uuid>` is rejected (400). Reading a site per child Location therefore double-counts Devices. Read Devices once by the site, then interfaces, Cables and links by `device_id` (rear and front ports take `device=`, they have no `device_id` filter) in batches of 25. Cables at depth 1 resolved through the interface, port and circuit-termination ids already read are about three times faster than depth 2: 4 min 26 s became 70 s for seven sites, identical Cables.

> **Learned 2026-10-29** · Nautobot 3.2.3 · VERIFIED_PRIMARY · Source: live REST reads as a read-only writer token on one deployment
> (unified-network-controller `wc-local/scripts/topology/topology_push.py` `cable_links`, a8c58f9; `src/unc/tasks/tower_rename.py`, af389e8)
> · Falsifier: a 3.2.x release accepting `cabled` or `location_id`.
> Two NetBox-style filter names answer HTTP 400 `Unknown filter field`: `/dcim/interfaces/?cabled=true` (use `has_cable=true`) and
> `/dcim/devices/?location_id=<uuid>` (use `location=<uuid>`, which takes a pk or a name). A site's wiring: read its Devices once by the site
> (subtree), then their cabled interfaces by `device_id` in batches of 10 with `depth=1`, and pair each with its `connected_endpoint.id`
> inside the same rows (a far end outside them is another site or a front port). A site-level `interfaces?location=` read is the exact
> Location only: it silently lost every Cable of the units moved into towers on the second run (one site, 19 Cables before the move).

```python
ids = [d["id"] for d in pages(f"/dcim/devices/?location={loc['id']}&depth=0&limit=1000", role="importer")]
for i in range(0, len(ids), 10):   # 40 ids in one query string reset the connection; 10 work
    rows += pages(f"/dcim/interfaces/?{'&'.join(f'device_id={x}' for x in ids[i:i + 10])}&has_cable=true&depth=1&limit=1000", role="importer")
owner = {r["id"]: ((r.get("device") or {}).get("name"), r["name"]) for r in rows}
for r in rows:
    far = (r.get("connected_endpoint") or {}).get("id")
    if far in owner and (far, r["id"]) not in seen:   # one link per Cable
        seen.add((r["id"], far))
```

