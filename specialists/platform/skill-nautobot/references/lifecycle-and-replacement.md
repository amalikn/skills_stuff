# Lifecycle and replacement

## Decision model

Separate the logical service position from the physical asset that currently occupies it. A Device record may represent one or the other only when that choice is explicit; otherwise model the
relationship and replacement history so a hardware swap does not accidentally become a new service, or erase the history of the old asset.

Plan the replacement before changing status: identify the outgoing and incoming assets, their authoritative identities, custody state, location, service relationship, monitoring identity, dependent
interfaces/IPs, and the acknowledgement that makes cutover complete. A physical move to warehouse or another site is a custody/location question, not proof of lifecycle retirement.

## Identity and audit

Preserve a stable monitoring or consumer identity only when the system's policy says it represents the logical service rather than the physical hardware. Record a replacement mapping and audit trail
instead of reusing a hardware identifier. Capture who performed or approved the handoff through the project's authenticated actor control. A QR label is an efficient lookup aid, not authentication;
a scanned label alone cannot authorize custody or lifecycle change.

## Common mistakes and acceptance

Common mistakes are overwriting the old serial, using a label as proof of actor identity, retaining stale links without an acknowledgement, and declaring a warehouse move a replacement. Acceptance is
an auditable chain from outgoing asset through custody and replacement decision to incoming asset, with downstream service/monitoring behavior verified and a rollback or exception path documented.
Claim N-C06.

## Synthetic replacement walk-through

Service position `POP-EDGE-1` is currently occupied by asset `A-17` (serial `SYN-17`); asset `A-42` (`SYN-42`) is the approved spare. First verify which
record represents the logical position: if the Device is the physical asset, preserve both Device records and use a Relationship/custom model for occupancy history;
if the Device is the logical position, preserve its logical identity but record old/new hardware identities in a separate auditable asset or replacement record. Never
overwrite `SYN-17` and thereby erase who owned the former unit.

Dry-run the transition: identify actor and custody acknowledgement; capture outgoing interface/IP assignments, circuit/service links and monitoring identity; mark
which references follow the service position and which follow the physical unit. On authorized cutover, detach or retire old physical links, attach the new unit,
validate address uniqueness and management reachability, then verify the monitoring mapping still points to the intended logical service **only if continuity is the
approved identity policy**. Record both asset identities and timestamps. A QR label locates `A-42`; it does not prove who accepted custody. If the incoming unit is
unreachable or monitoring binds to the wrong history, hold the replacement in exception state, restore the old linkage where safe, and retain both attempted and
rollback audit entries. Acceptance requires physical custody, logical service continuity, correct IP/interface and monitoring link, and an operator-visible result.
For a cross-platform monitoring identity, read OpenWISP [identity and registration](../../skill-openwisp/references/identity-and-registration.md) only when that link
actually changes.

## Learned

> **Learned 2026-11-18** · design pattern, `reusable_candidate` until a second project uses it · VERIFIED_PRIMARY (one project's app code, read) and USER_STATED (the operator's rule that a Device
> is a position) · Source: unified-network-controller `nautobot/apps/unc-ownership/unc_ownership/inventory/replacement.py` at commit 409ea52e (excerpt below) · Falsifier: a deployment whose
> uniqueness rule validates both records of an exchange together, so nothing needs parking.
>
> When the Device record is the logical position and a second record carries the removed unit, the two records exchange hardware identity (serial, MACs) in one transaction; nothing is deleted
> and the returned unit keeps a record with its real serial. Any value that is unique (a serial under a uniqueness rule, core's unique `asset_tag`) is parked empty on one record first, because each
> save is validated alone and would otherwise find the other record still holding it. History that must follow the physical unit is keyed to an identifier stored with the unit (its asset tag), never
> to the Device primary key: the unit changes record at every swap. Read the project's replacement code before advising "the Device is the unit" or "the Device is the position": on 2026-11-18 advice
> given without that read contradicted a built, decided rule and had to be withdrawn.
>
> ```python
> # replacement.py apply_swap, commit 409ea52e: park, then exchange
> for obj, serial in ((replacement, ""), (in_service, to_position), (replacement, to_staged)):
>     obj.serial = serial
>     setattr(obj, ACK_ATTRIBUTE, True)
>     obj.validated_save()
> ```
>
> No visual surface: no screenshot.
