# Passive ingestion

## Neutral observation boundary

For closed firmware, treat OpenWISP as a passive monitoring consumer unless a supported control path is separately proven. Normalize vendor output into a versioned neutral observation before NetJSON
DeviceMonitoring mapping: stable identity, source, captured-at UTC time, sampling time, interfaces/resources, units, counters, freshness, and declared vendor semantics. Keep vendor-specific naming,
wireless interpretation, and transport detail at the adapter boundary rather than laundering them into a platform model.

Represent interface state as up, down, or unknown. Omit a field that was not observed; do not fabricate zero or false. Represent down only when the source explicitly reports an administratively or
operationally disabled interface. Counters require non-negative values, named units, and the interval or sampling time needed to interpret change. Ingestion time and source observation time are
different facts, especially for backfill.

## Mapping limits

Map only fields supported by the target version-pinned NetJSON DeviceMonitoring schema. Put required richer fields behind a named top-level extension with a consumer test; the existence of an extension
does not promise stock charts or health rules. The project found that richer point-to-multipoint and high-frequency radio data may not fit a standard wireless representation naturally. Preserve that
lossiness as a design decision rather than inventing semantics. Claim O-C13 is the project-derived known/unknown/down pattern.

## Verification

Reject malformed required identity, counters, and ambiguous timestamps before any network action. A later mapper must prove offline transformation, accepted payload, worker processing, Metric
persistence, recent point, health evaluation, and graph separately. This guidance package contains no runnable mapper. Claim O-C05.

## Synthetic neutral observation → target schema

Input at `2026-10-01T10:00:00Z`: logical ID `11111111-2222-3333-4444-555555555555`, Ethernet `eth0` state **unknown**, `rx_bytes=1000`
bytes sampled at 10:00, radio `wlan0` explicitly disabled, CPU utilisation 12%, and one peer signal `-62 dBm`. The collector receives it at 10:05.

| Neutral fact                  | UNC 1.3 DeviceMonitoring mapping                                            | Retained/omitted/limit                                                                 |
| ----------------------------- | --------------------------------------------------------------------------- | -------------------------------------------------------------------------------------- |
| Logical ID, source and        | Registration identifies Device; backfill `time` query parameter carries     | Source/provenance kept in collector evidence, not claimed as stock metric              |
|   capture time                |   capture time                                                              |                                                                                        |
| `eth0` unknown                | `interfaces[].name/type/statistics`, omit `up`                              | Never infer `up=false` from absent state                                               |
| `wlan0` explicitly off        | Wireless interface with `up=false`, no `wireless` object                    | Avoid unsupported/null frequency; down is observed, not guessed                        |
| `rx_bytes=1000`               | `statistics.rx_bytes`                                                       | Monotone counter in bytes; reset/wrap requires sampling logic outside payload          |
| CPU 12%                       | Only map if target metric semantics can be represented honestly             | UNC's load/CPU encoding is a local compatibility choice, not generic load average      |
| Peer `-62 dBm`                | Named extension (UNC uses `wireless_links`)                                 | Top-level acceptance does not create a stock chart; register                           |
|                               |                                                                             |   metric/consumer separately                                                           |

The project's `backfill_timestamp()` emits `%d-%m-%Y_%H:%M:%S.%f`, **not ISO 8601**, from the observation's source time. Its function docstring says the exact
running-instance behavior was unverified, while contract tests and later project comments assert accepted pushes. Official OpenWISP 26.09 monitoring docs specify the
same query format, but that does not prove every 1.3 deployment; test the effective endpoint. Reject naive source time, record UTC assumption, and distinguish source
time, submission time and stored point time. Backfill may correctly store an old point yet fail freshness/health; do not mark it current because ingestion is recent.
The original tests verify schema shape and metric-producing fields for local fixtures/captures, not Celery, storage or charts. See
[verification and troubleshooting](verification-and-troubleshooting.md) for those independent proofs.

> **Learned 2026-10-05** · OpenWISP 26.09.0 deployment · VERIFIED_PRIMARY · Source: measured over 119 discovery sweeps, 44 identify reads and 36 DNS zones of one deployment, about 4,000 units at 43 sites, 2026-09-23 to 2026-10-01 (UNC capture corpus, aggregated read-only) · Falsifier: an SNMP read that returns running firmware for these families
> A one-pass SNMP read gave model for 99.9% of answering units but firmware only for one family of four; firmware for the others has to come from the device API or a controller. Omit what a source does not report rather than filling it.
