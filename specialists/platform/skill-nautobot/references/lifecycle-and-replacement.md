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
