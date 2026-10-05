# Authority and modelling

## Decision model

Treat Nautobot as the record of accepted intent, not an unfiltered event store. For each object and field, name the authority, writer, evidence class, and review path before deciding where it lives.
Useful state classes are intended state, observed state, and evidence about an observation. A collector may propose an observation; it does not acquire authority to redefine intent.

Location describes physical geography and hierarchy. Tenant describes an administrative or service ownership boundary when that boundary matters. Namespace is the IPAM uniqueness boundary; it is not a
substitute for either geography or tenancy. Namespaces allow otherwise overlapping address records, and a site-scoped Namespace was a tested project solution for genuinely independent address domains,
not a universal default. Claim N-C02 is the documented model principle; the concrete split needs local justification.

## Modelling choices

Use Devices, Interfaces, Prefixes, and IP Addresses for their native meanings. A project-derived rule retained the narrowest containing Prefix mask on an address rather than defaulting every address to
`/32`; that preserves the usable routing fact but still requires validation against the local IPAM design. Do not use a host route merely to make an import convenient. Claim N-C14 is this worked
pattern, not a core Nautobot guarantee.

Use a Relationship for a durable fact between existing objects. Use a custom field for a bounded attribute whose lifecycle belongs to its existing object. Consider a custom model only when the concept
has its own identity, lifecycle, permissions, relations, and query needs. The project Wireless Link object is a worked case: native models did not adequately represent its durable semantics. It does
not prove that every radio association needs a custom model. Keep physical topology, logical service topology, and transient telemetry separate.

Keep Device Status as an approved lifecycle state. Health, freshness, signal, and reachability are observations or policy outputs; a critical observation does not silently turn an Active device into
a retired or failed lifecycle object. An explicit policy may create a review task or a controlled transition, but telemetry alone does not decide it.

Do not put secrets, raw polling payloads, high-rate time series, uncorroborated neighbour claims, or an external system's entire schema into Nautobot merely because it has an extension seam. Preserve
only the durable intent or the bounded evidence needed to govern it.

## Failure clues and acceptance

Conflicting writers, a Location used to dodge IP uniqueness, a custom field carrying an independent lifecycle, and a monitoring process overwriting Status are modelling failures. Before acceptance,
verify the object owner, write permissions, uniqueness boundary, parent Prefix/mask, relationship cardinality, lifecycle policy, and the version-specific model/API behavior actually relied on.
Claims N-C01, N-C02, and N-C14.

## Ownership is a contract, not automatically enforcement

Record each field's authority, permitted writer, evidence source, transition rule and actual enforcement hook separately. A catalog documents ownership; it does not
block an API client. In the UNC worked app, an ownership catalog supplies classes while `wc_ownership` loads it at import and CustomValidators compare stored and
incoming Device/Interface data on UI/API validation. It guards configured classes and custom-field keys on **updates**, not creation. A named writer or group may
bypass the guard; acknowledged replacement is a separate exception. Applicability also checks creation, but is disabled by default there. An unreadable catalog
returns no guarded fields and logs an error; unknown device types do not trigger applicability refusal. Direct writes that skip model validation require a separate
test. Thus a green catalog check or registered validator does not prove every write path is protected.

| Synthetic field     | State                     | Authority and writer           | Required transition evidence                             |
| ------------------- | ------------------------- | ------------------------------ | -------------------------------------------------------- |
| `service_role`      | Intent                    | Service owner; operator writer | Reviewed change; collector edit refused                  |
| `reported_serial`   | Hardware observation      | Device read; collector writer  | UI/API human edit refused; replacement exception audited |
| `monitoring_health` | Observation               | Monitoring; sync writer        | Source time retained; never changes lifecycle Status     |
| `rack_position`     | Hardware-dependent intent | Facilities; operator writer    | Applicable device type; create/update validation         |

If ownership information is absent, stale or contradictory, stop the proposed write. Inspect the *effective loaded* catalog and process restart state; compare it with
registered validators and permissions. A fail-open validator preserves availability but degrades the control, so alert on it and block automated writes until repaired.

Synthetic modeling decision: two independent sites both use `192.0.2.10` inside approved `192.0.2.0/27` Prefixes. If their address spaces are genuinely independent,
use separate Namespaces; Locations identify geography and Tenants administrative ownership, neither substitutes for IP uniqueness. Link each address to its site's
interface and retain `/27`, the narrowest containing Prefix. If one site has a more-specific approved `/28`, confirm it is the interface's intended network before
selecting that mask. Failure case: forcing `/32` to avoid a duplicate or selecting the wrong overlapping Prefix hides a routing/design conflict. A Relationship suits a
durable association between existing objects; a custom field a bounded attribute; a custom model a concept with independent identity, lifecycle and permissions.
Read [staged onboarding](staged-onboarding.md) for promotion and [API and writers](api-and-writers.md) before automating updates.

> **Learned 2026-10-05** · Nautobot 3.2.3 · VERIFIED_PRIMARY · Source: nautobot/extras/management/__init__.py lines 107-170 and extras/models/roles.py line 37 in the installed source · Falsifier: a 3.2.x post_upgrade or migrate run that recreates a deleted default Role
> Default Statuses and Roles are created only by data migrations that have already run, so a deleted built-in is never recreated by `migrate` or `post_upgrade`. Treat them as shared taxonomy: a cleanup script reports candidates and stops, and recovery is from the change log ([operations cookbook](operations-cookbook.md) section 9).

> **Learned 2026-10-05** · Nautobot 3.2.3 deployment · VERIFIED_PRIMARY · Source: measured over 119 discovery sweeps, 44 identify reads and 36 DNS zones of one deployment, about 4,000 units at 43 sites, 2026-09-23 to 2026-10-01 (UNC capture corpus, aggregated read-only) · Falsifier: a fleet with a duplicated non-empty serial
> Serial may be legitimately empty (7% of units, concentrated in a few models whose SNMP returns none) but was unique whenever present (0 duplicates in 3,043). Enforce uniqueness only for non-empty values and let the identity source fill the gap later.

> **Learned 2026-10-05** · Nautobot 3.2.3 deployment · VERIFIED_PRIMARY · Source: measured over 119 discovery sweeps, 44 identify reads and 36 DNS zones of one deployment, about 4,000 units at 43 sites, 2026-09-23 to 2026-10-01 (UNC capture corpus, aggregated read-only) · Falsifier: a fleet whose device-reported names are unique and descriptive
> Do not name or key devices on SNMP sysName: one family returned a generic default on 349 units, default-pattern names repeated across sites, and 11 duplicate-name groups existed inside single sites. DNS A records named 98% of live units; 13% of in-subnet records pointed at nothing, so a dangling record is a warning, not an error.
