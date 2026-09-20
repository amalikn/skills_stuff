---
Title: Cambium Device Response Schemas
Category: device-reference
Status: current — fleet sweep complete across all 36 sites
Authority: primary — derived from live devices, supersedes MIB mirrors for response shape
Scope: The response contract for every Cambium device family in the APN estate
Last reviewed: 2026-09-20
Summary: Machine-readable contracts for what each Cambium device family actually returns, derived from live observation rather than vendor documentation, with per-site conformance as the mechanism for finding divergence.
---

# Cambium Device Response Schemas

## Contents

- [What this is, and what it is not](#what-this-is-and-what-it-is-not)
- [Why it exists](#why-it-exists)
- [Layers — raw endpoint versus adapter output](#layers--raw-endpoint-versus-adapter-output)
- [How to read a schema](#how-to-read-a-schema)
- [How `required` is derived](#how-required-is-derived)
- [Privacy rules](#privacy-rules)
- [Current coverage](#current-coverage)
  - [The `-legacy` credential finding](#the--legacy-credential-finding)
  - [What the fleet added over a single site](#what-the-fleet-added-over-a-single-site)
  - [Map-shaped responses](#map-shaped-responses)
  - [What the fleet disagrees about](#what-the-fleet-disagrees-about)
  - [Coverage and remaining gaps](#coverage-and-remaining-gaps)
- [Extending the standard](#extending-the-standard)
- [The fleet sweep](#the-fleet-sweep)

## What this is, and what it is not

**It is** a contract: for each device family and each endpoint, the set of fields, their types, which are always present, which vary by model or firmware, and which carry end-user identifying data.
Machine-readable JSON Schema (draft 2020-12) with `x-cambium` annotations, usable by adapter code and by a conformance check.

**It is not** a capture. No response body is stored. Values appear only as `x-candidate-values` on short, low-cardinality, non-identifying fields — `"2.4GHz"`, `"ON"`, `"axa"` — where the value set is
itself part of the contract. Everything else records shape only.

Raw captures remain evidence and live in `cambium-swap/captures/device-queries/`, which is gitignored by that repo's convention. This tree is the tracked, durable standard.

## Why it exists

The vendor mirrors are not the contract, and they are wrong in both directions:

- `cnPilotMIB` describes **16** client-table columns. A live XV2 on `6.6.0.3-r9` returns **95** fields from `client-summary`, including `rssi` and `assoc_time`, neither of which exists in the MIB at
  all.
- `CAMBIUM-PMP80211-MIB` documents **29** columns for `cambiumAPConnectedSTAEntry`. A live ePMP 3000L on `4.7.0.1` returns **42**, thirteen of them undocumented.

Adapter code written against a mirror, or against one device captured once, breaks at the next firmware or the next site. The point of a derived standard is that divergence becomes a reportable event
rather than a runtime surprise.

## Layers — raw endpoint versus adapter output

Every schema declares `x-cambium.layer`. The two are not comparable and must never be merged:

| Layer                | Meaning                                         | Families                                                                |
| -------------------- | ----------------------------------------------- | ----------------------------------------------------------------------- |
| `raw-endpoint`       | The device's own REST response, field for field | Enterprise Wi-Fi (XV2, E-series) — the Falcon UI exposes these directly |
| `adapter-normalized` | The output of this pack's adapter getters       | ePMP AP/SM, cnPilot R-series, cnWave 60 GHz                             |

The split is practical, not principled: only the Falcon families expose raw endpoints conveniently. Contracting the other three at their adapter boundary is still worth having — it is the surface
consuming code actually sees. Raw-endpoint schemas for those families remain open work.

## How to read a schema

Beyond standard JSON Schema keywords:

| Annotation           | Meaning                                                                                                                 |
| -------------------- | ----------------------------------------------------------------------------------------------------------------------- |
| `x-cambium`          | Provenance — family, endpoint, layer, and the models, firmware and sites the contract was derived from                  |
| `x-identifying`      | The field carries end-user identifying data. Values are never recorded, and consuming code should treat it as regulated |
| `x-nullable`         | `null` was observed in this field on at least one device                                                                |
| `x-type-varies`      | The field's type was not consistent across observations — a real portability hazard, not a tooling artifact             |
| `x-candidate-values` | Every value observed, where the field is low-cardinality and non-identifying. A candidate enum, not a closed one        |
| `x-observed-count`   | How many records contributed                                                                                            |
| `x-optional`         | Fields not present on every record-bearing observation, with the count and the sites and models that had them           |
| `x-evidence`         | How much evidence `required` rests on, including observations that returned nothing                                     |

## How `required` is derived

A field is `required` when it appeared on **every observation that actually returned a record**.

The qualifier is the important part. An endpoint that returns an empty array is not evidence that its fields are absent — an AP with no clients attached says nothing about what a client record
contains. Counting those observations would drag every field to optional and destroy the contract. They are excluded from the presence maths and reported separately in `x-evidence`.

This was not a hypothetical: the first merge of the `client-summary` contract for `enterprise-wifi` produced **zero** required fields out of 95, purely because the E500 had no clients associated at capture time.

The practical consequence for the sweep: **for client-bearing endpoints, target the device with clients**, not an arbitrary one. Sweep client counts across a site first, then contract the busiest
device. A site where nothing had a client contributes no evidence for that endpoint and must be recorded as such rather than silently skipped.

## Privacy rules

Never recorded, at any stage, in any file in this tree:

- Client MAC, IP, IPv6 link-local, hostname, username, device type, vendor string.
- SSID — not personal, but site-identifying and of no use in a contract.
- Any value that *looks* like a MAC, IP or hostname regardless of what the field is called (`--strict-pii`, on by default).

Device-side identifiers — AP MAC, radio BSSID, SM MAC, serial — are infrastructure rather than personal, but the standard has no use for them either, so they are not emitted as examples.

## Current coverage

Fleet sweep complete, 2026-09-20. All 36 sites, one representative device per family per site, **122 observations covering 121 of 122 site/family pairs**.

| Family | Endpoints | Fields | Observations | Layer | Models seen |
| --- | --- | --- | --- | --- | --- |
| `enterprise-wifi` | 9 | 381 | 36 | `raw-endpoint` | E500, XV2 |
| `cnwave-60ghz` | 13 | 40 | 5 | `adapter-normalized` | V1000, V3000, V5000 |
| `cnpilot-r-series` | 2 | 8 | 9 | `adapter-normalized` | R195P |
| `epmp-ap` | 4 | 20 | 36 | `adapter-normalized` | Force 300-16, Force 300-25, ePMP 3000L |
| `epmp-sm` | 4 | 14 | 36 | `adapter-normalized` | Force 300-16, Force 300-25 |

`client-summary` rests on **32 record-bearing observations covering 248 real client records**, which is what makes its `required` set meaningful rather than one site's accident.

### What the fleet added over a single site

The single-site baseline would have shipped a contract that was wrong in both directions. Against the fleet: `client-summary` grew 95 → **98** fields, `device-summary` 45 → **47**,
`platform-info` 15 → **16**, `radio-rf-summary` 15 → **16**. Three cnWave models (V1000, V3000, V5000) and two more ePMP models appeared that the baseline never saw.

### What the fleet disagrees about

Full breakdown in [DIVERGENCE.md](DIVERGENCE.md); the run-by-run history, including two sweeps that had to be discarded, is in [SWEEP-LOG.md](SWEEP-LOG.md). The headline: **in `client-summary` only 43 of 98 fields are universal — 54 split by model.** An adapter written against an XV2 alone would depend
on fields more than half of which an E500 does not return. `radio-rf-summary` is worse in proportion: 7 universal against 9 model-split.

Two findings that need a decision rather than a note:

- **`ip6_ll` returns different JSON types across the fleet — `array` on some sites, `string` on others** — and is absent entirely at 17 sites. Any code that indexes it breaks on the other shape. It
  is also an identifying field, so the contract records the conflict without recording values.
- **the R-series `interfaces` getter is not contractable as it stands.** Its six "site-specific fields" are interface *names* used as object keys — `eth2.17`, `eth2.550`, `wan1.500` — so each site's
  VLAN configuration appears as schema fields. That is an adapter design problem, not device divergence: a response keyed by site-variable names has no stable shape. It should return a list of
  interface objects with the name as a value.

### Coverage and remaining gaps

**121 of 122 site/family pairs contracted** across 122 observations. Every pair was attempted; the one shortfall is recorded rather than skipped.

Two rounds of recovery closed 11 of the 12 gaps a first pass left:

- **Timeouts, 7 recovered.** A mid-sweep retune to 20s forward / 75s adapter / two attempts was too tight for the slowest links. Restoring 40s / 180s / four attempts recovered wujal-wujal ePMP SM,
  horn-island R-series and ePMP SM, warakurna ePMP AP and SM, mornington cnWave and ePMP SM.
- **Credentials, 4 recovered.** kalumburu and mornington run the **older local-admin password**, held in the vault's `-legacy` entries. The sweep now tries each family's primary entry and then its
  `-legacy` fallback, which recovered all three kalumburu families and mornington's R-series.

One gap remains: **hope-vale cnWave 60 GHz**, 7 devices, TLS handshake EOF on four devices at full timeout with both credentials. All three units also failed ping earlier, so this reads as genuinely
down hardware rather than an access problem.

### The `-legacy` credential finding

Worth separating from the sweep, because it is an estate fact rather than a tooling one. Two sites authenticate only with the older password, across independent families and vendors' own login
paths. Confirmed by hand before the fallback was added: at kalumburu the primary Enterprise Wi-Fi entry returns `Invalid username or password` while the `-legacy` entry returns `{"success":true}` on
the same device. Credential rotation reached most of the estate but not these sites, and anything that assumes one current password per family will report them as unreachable.

### What the fleet added over a single site

The single-site baseline would have shipped a contract wrong in both directions. Against the fleet: `client-summary` grew 95 → **98** fields, `device-summary` 45 → **47**, `platform-info` 15 → **16**,
`radio-rf-summary` 15 → **16**. Three cnWave models (V1000, V3000, V5000) and two more ePMP models appeared that the baseline never saw.

### What the fleet disagrees about

Full breakdown in [DIVERGENCE.md](DIVERGENCE.md); the run-by-run history is in [SWEEP-LOG.md](SWEEP-LOG.md). The headline: **in `client-summary` only 43 of 98 fields are universal — 54 split by
model.** An adapter written against an XV2 alone would depend on fields more than half of which an E500 does not return. `radio-rf-summary` is worse in proportion: 7 universal against 9 model-split.

**`ip6_ll` returns a different JSON type by model** — an `array` on XV2 (10 observations), a `string` on E500 (6), absent where the client has no link-local (17). It is also **EUI-64 derived, so it
encodes the client's MAC**: the observed `fe80::6885:b9ff:feac:bb89` resolves exactly to the client MAC `6A-85-B9-AC-BB-89`. It carries the same identifying information as the MAC field and is
redacted on the same footing. Normalise it to a list at the adapter boundary — wrapping the E500 string and mapping absent to empty is lossless, while the reverse direction would truncate XV2 clients
holding more than one address.

Shapes still unknown because nothing anywhere returned a record: the ePMP SM `clients` getter (empty on all 36 observations — an SM has no clients, so this is probably correct by design) and the
cnWave `links_count` getter. The cnWave `gps` getter is `null` fleet-wide. The ePMP AP `wireless_link` getter is null-or-object, which is contract rather than a gap.

### Map-shaped responses

The R-series `interfaces` getter returns a **map keyed by interface name**, which is NAPALM's convention and is followed by every adapter in this pack — see the `get_interfaces` docstring in the XV2
adapter. Contracting its keys as fields was a defect in the schema tool, not in the adapter: it made one site's VLAN plan look like the family's schema, surfacing 40 interface names as "site-specific
fields". Such endpoints are now listed in the tool's `MAP_SHAPED` registry and contracted as `additionalProperties` describing the **value** shape, with the observed keys recorded separately. The
R-series interface value is three fields: `ipv4_addresses`, `is_up`, `mac_address`.

## Extending the standard

`scripts/schema_tool.py` has three verbs. `observe` contracts one device, `merge` folds observations into the standard, `check` reports a new observation's divergence from it.

```
# a live Falcon family, through a Teleport port-forward
CAMBIUM_USER=... CAMBIUM_PASS=... python3 scripts/schema_tool.py observe \
    --driver falcon --host localhost:10019 --family enterprise-wifi \
    --model XV2 --firmware 6.6.0.3-r9 --site hope-vale \
    --endpoints client-summary,radio-summary --out schemas/_observations/enterprise-wifi/<site>-<model>-<date>.json

# any family, from its adapter's stdout
python3 scripts/cambium_epmp_adapter.py | python3 scripts/schema_tool.py observe \
    --driver stdin --split-getters --layer adapter-normalized --family epmp-ap ...

python3 scripts/schema_tool.py merge --family epmp-ap schemas/_observations/epmp-ap/*.json --out schemas/epmp-ap/
python3 scripts/schema_tool.py check --standard schemas/epmp-ap --observation <new observation>
```

Observations are kept in `schemas/_observations/` and tracked. They contain no values, they are small, and they are what makes the standard reproducible — a merged schema without its inputs is an
assertion.

`check` exits non-zero on divergence, so it can gate a fleet sweep.

## The fleet sweep

Run 2026-09-20 across all 36 sites by `scripts/fleet_schema_sweep.py`. Rules it implements, which any re-run must keep:

1. **One representative per family per site**, chosen by client count where the endpoint is client-bearing.
2. **Throttle ePMP** — the family has a limited concurrent-session budget; do not run it wide in parallel.
3. **Record unreachable and empty as findings**, never as skips. A site with no reachable device of a family is a fact about the estate.
4. **Verify the jump host before concluding a site is down.** `snmpget` is absent on `rcp`-flavour SMC boxes — a sweep that shells out to a missing binary will report a healthy site as dead. See
   `skill-smc`'s known-issues reference.
5. **Merge, then diff.** Divergence between sites is the output that matters; record it in [references/05_known-issues.md](../references/05_known-issues.md) rather than silently widening the contract.
