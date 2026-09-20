# Cambium Fleet Overview

## Contents

- [What This Pack Covers](#what-this-pack-covers)
- [Device Families in APN's Fleet](#device-families-in-apns-fleet)
- [EoL / EoS Snapshot](#eol--eos-snapshot)
- [Evidence-State Discipline](#evidence-state-discipline)
- [Where the Live Data Lives](#where-the-live-data-lives)

---

## What This Pack Covers

Operational knowledge about APN's Cambium wireless fleet — the radio/AP hardware layer, not the SMC box that manages a site around it (see `skill-smc` for that; the two packs are related, see each
pack's `RUNBOOK.md` for the cross-reference). Seeded 2026-09-17 out of the `cambium-swap` project's first real device-credentialing and device-inventory pass.

## Device Families in APN's Fleet

Five families, 17 models catalogued as of 2026-09-17 (source: `cambium-swap/inventory/device-family-matrix.csv`):

| Family           | Models                                                                    | Role                                      |
| ---------------- | ------------------------------------------------------------------------- | ----------------------------------------- |
| Enterprise Wi-Fi | XV2-2T0, XV2-22H, E500, E430                                              | Indoor/outdoor Wi-Fi AP                   |
| cnPilot R-series | R195P                                                                     | Residential CPE / router                  |
| ePMP AP          | ePMP 3000, ePMP 3000L, ePMP 1000, ePMP 1000 2.4 GHz / 5 GHz Connectorized | 5 GHz P2MP backhaul access point          |
| ePMP SM          | Force 300-16, Force 300-25, Force 180                                     | 5 GHz P2MP/P2P backhaul subscriber module |
| cnWave 60 GHz    | V5000, V3000, V2000, V1000                                                | 60 GHz P2MP/P2P millimetre-wave backhaul  |

`ePMP 1000` (all variants) and `Force 180` are legacy — operator: "very old and unsupported, being migrated to MikroTik 'metal' APs and XV2-2T0". Don't recommend them for new deployments.

## EoL / EoS Snapshot

Full detail and dates: `cambium-swap/inventory/device-family-matrix.csv` `eol_status` column. Headline: ePMP 1000 (all variants) and several E-series/Force-180 SKUs are already past End of Support;
XV2/ePMP-3000-family/Force-300/cnWave models are current or have years of support runway.

## Evidence-State Discipline

Borrowed from `cambium-swap`'s own convention — apply it in this pack too. Tag any non-trivial claim:

| Label                | Meaning                                                                                                     |
| -------------------- | ----------------------------------------------------------------------------------------------------------- |
| `VERIFIED-DOC`       | Confirmed against official Cambium or AWS vendor documentation                                              |
| `VERIFIED-OBSERVED`  | Confirmed by direct interaction with a real device/instance                                                 |
| `COMMUNITY-EVIDENCE` | From a vendor employee, customer, or reputable third-party source                                           |
| `USER_STATED`        | Supplied by the operator, not independently verified — most of this pack's current content is at this level |
| `UNKNOWN`            | Not yet collected — never guess a value to fill this in                                                     |

As of 2026-09-17, no cnMaestro export or authenticated device session has happened against APN's real Cambium hardware — everything in this pack is `USER_STATED` (operator-supplied) or extracted from
site asset registers, not `VERIFIED-OBSERVED`. See `05_known-issues.md`.

## Wireless Security Posture Across the Fleet

Derived from the 2026-09-20 36-site sweep — 98 service records and 207 client records across the enterprise Wi-Fi family — and confirmed as intent by the operator on 2026-09-21.

| Field | Every value observed fleet-wide |
| --- | --- |
| `security` (service) | `open`, `wpa2-psk` |
| `key_management` (client) | `NONE`, `PSK` |
| `encryption` (client) | *(empty)*, `WPA2` |
| `cipher` (client) | *(empty)*, `CCMP` |
| `mode` (client) | `bgn`, `ac`, `axa` |

**The open SSIDs are deliberate.** This is public community Wi-Fi and open is the operator's intent, not a misconfiguration or a drift finding. Do not raise it as a defect, and do not "fix" it in a
template or a config push.

Two consequences worth carrying:

- **No WPA3 anywhere on the estate** — no SAE in `key_management`. Management frame protection (802.11w / PMF) is optional under WPA2 and mandatory under WPA3, so PMF is effectively absent fleet-wide.
  Any consumer that needs a per-client `mfp` value can safely assume false **today**, and must re-check the moment WPA3 or OWE appears.
- **Every client is 802.11n or later.** `mode` is never a legacy `bg`, so WMM is negotiated on every association — HT operation requires it, since block-ack and frame aggregation are defined over the
  QoS access categories. A per-client WMM capability flag is therefore derivable from `mode` and never needs fabricating.

## Where the Live Data Lives

This pack documents conventions and stable facts. The actual per-model matrix and per-device inventory are **not duplicated here** — they live in, and are only current in, `cambium-swap`:

- `cambium-swap/inventory/device-family-matrix.csv` — per-model firmware, hardware revision, SSH/SNMP capability, credential vault reference.
- `cambium-swap/inventory/device-inventory.csv` — per-device export (model, MAC, IP, site, credential reference).
- `cambium-swap/inventory/cnmaestro-instances.yaml` — the cnMaestro estate.

Read the file, not this pack's memory of it, before acting on a specific device or model.
