# Changelog — skill-cambium

## Contents

- [20260921_2015](#20260921_2015)
- [20260921_1541](#20260921_1541)
- [20260921_1237](#20260921_1237)
- [20260921_1015](#20260921_1015)
- [20260920_2339](#20260920_2339)
- [20260920_1951](#20260920_1951)
- [20260920_1856](#20260920_1856)
- [20260920_1758](#20260920_1758)
- [20260920_1745](#20260920_1745)
- [20260920_1652](#20260920_1652)
- [20260920_1556](#20260920_1556)
- [20260917_1100](#20260917_1100)
- [20260917_1130](#20260917_1130)
- [20260917_1135](#20260917_1135)
- [2026-09-17 — deterministic navigation-control upgrade](#2026-09-17--deterministic-navigation-control-upgrade)
- [20260917_1210](#20260917_1210)
- [20260917_1200](#20260917_1200)
- [20260917_1230](#20260917_1230)
- [20260917_1245](#20260917_1245)
- [20260917_1300](#20260917_1300)
- [20260917_1440](#20260917_1440)
- [20260917_1500](#20260917_1500)
- [20260917_1510](#20260917_1510)
- [20260917_1600](#20260917_1600)
- [20260917_1630](#20260917_1630)
- [20260917_1700](#20260917_1700)
- [20260917_1710](#20260917_1710)
- [20260917_1720](#20260917_1720)
- [20260917_1730](#20260917_1730)
- [20260917_1930](#20260917_1930)
- [20260917_1946](#20260917_1946)
- [20260917_2021](#20260917_2021)
- [20260917_2050](#20260917_2050)
- [20260917_2057](#20260917_2057)
- [20260917_2130](#20260917_2130)
- [20260917_2145](#20260917_2145)
- [20260918_0855 — cnMaestro REST API v2 access documented; vault table gained 5 missing entries](#20260918_0855--cnmaestro-rest-api-v2-access-documented-vault-table-gained-5-missing-entries)
- [20260918_0930 — site-addressing.yaml restructured by flavour, populated for all 27 nbn_accelerate sites, generator script added](#20260918_0930--site-addressingyaml-restructured-by-flavour-populated-for-all-27-nbn_accelerate-sites-generator-script-added)
- [20260918_1045 — two missing OUI blocks added after operator flagged oui_reference as stale](#20260918_1045--two-missing-oui-blocks-added-after-operator-flagged-oui_reference-as-stale)
- [20260918_1050 — generate_site_addressing_families.py gained --oui-audit mode](#20260918_1050--generate_site_addressing_familiespy-gained---oui-audit-mode)
- [20260918_1055 — full regenerate-and-verify pass: 8 missing families added, oui_reference restructured to a real site map](#20260918_1055--full-regenerate-and-verify-pass-8-missing-families-added-oui_reference-restructured-to-a-real-site-map)
- [20260918_1100 — YAML formatting cleanup, content accuracy fixes, FAMILY_MAP bug found and fixed](#20260918_1100--yaml-formatting-cleanup-content-accuracy-fixes-family_map-bug-found-and-fixed)
- [20260918_1115 — cnPilotMIB SNMP read-only identity data confirmed live on XV2-22H Wi-Fi 6 firmware](#20260918_1115--cnpilotmib-snmp-read-only-identity-data-confirmed-live-on-xv2-22h-wi-fi-6-firmware)
- [20260918_1155 — unified-network-controller added as a Related Workspace](#20260918_1155--unified-network-controller-added-as-a-related-workspace)
- [20260918_1542 — ePMP SM adapter re-verified fresh-live; cnWave 4 stat endpoints resolved (path bug, not missing params)](#20260918_1542--epmp-sm-adapter-re-verified-fresh-live-cnwave-4-stat-endpoints-resolved-path-bug-not-missing-params)
- [20260918_1557 — R195P get_config() implemented (operator-authorized); live fetch across all 4 families blocked this session by a sandbox credential-materialization guard](#20260918_1557--r195p-get_config-implemented-operator-authorized-live-fetch-across-all-4-families-blocked-this-session-by-a-sandbox-credential-materialization-guard)
- [20260918_1620 — Correction: the outage claim in the entry above was wrong; it was a `tsh` flag mistake, not an outage](#20260918_1620--correction-the-outage-claim-in-the-entry-above-was-wrong-it-was-a-tsh-flag-mistake-not-an-outage)
- [20260918_1705 — Live get_config() verification across all 4 Cambium families completed; 4 real R195P bugs found and fixed; new secret-exposure incident found and closed](#20260918_1705--live-get_config-verification-across-all-4-cambium-families-completed-4-real-r195p-bugs-found-and-fixed-new-secret-exposure-incident-found-and-closed)

---

## 20260921_2015

Added "Monitoring Counter and Resource Surfaces — Probed Live 2026-09-21" to
[references/06_device-api-cli-reference.md](references/06_device-api-cli-reference.md), under this pack's write-back contract: live read-only probes from
`unified-network-controller` found the ePMP `device_props` kbit counters and `sysCPUUsage`, R195P's `/proc` counters, load and memory (plain `cat` only, pipes
exit 127), cnWave `getNetworkStats` reading 0 on a POP node with the KPI and radio endpoints giving rates rather than counters, and the fleet-wide absence of
Wi-Fi mesh that makes client `wds: false` a measurement. No script changed.

## 20260921_1541

### cnMaestro API lifetime across the estate recorded (v0.6.6 -> v0.6.7)

`references/02_device-access-and-vault.md` "cnMaestro REST API v2 Access" now opens with the operator's 2026-09-21 statement: the API depends on cnMaestro X; cw-cnmaestro01
and lt-cnmaestro lose X soon, Cloud has no API and is being retired, and the new on-prem apn-cnmaestro01 has none. Controller-side automation must plan for web scraping;
device-local REST/SNMP is unaffected. Found while unified-network-controller modelled each cnMaestro as a Nautobot Controller.

## 20260921_1237

### Direct device SSH from the operator Mac via `ProxyJump`; one XV2 variant resolved (v0.6.5 -> v0.6.6)

`references/02_device-access-and-vault.md` gains a section on reaching a device with OpenSSH `ProxyJump` through its SMC box instead of the nested `tsh ssh` + `sshpass` form, so the device
credential is never materialised in a shell on the box. Verified with `<secret:keepassxc:cambium-devices/enterprise-wifi>` against `GAL_XV2_AP32_IP3_32` (`10.255.3.32`, Galiwinku): `show version`
identified the unit as XV2-2T0, serial `WLZE1F5BWMB9`, firmware `6.6.0.3-r9` — resolving the variant `device-inventory.csv` records as unconfirmed, for this unit only. The Teleport and SSH-config
side lives in `skill-smc`; not duplicated here.

## 20260921_1015

### cnWave speaks SNMP on its own arm; the SNMP layer gets contracted; a single-site conclusion nearly became a fact (v0.6.4 -> v0.6.5)

Live walks from `hope-vale-smc01`, `mornington-smc01`, `horn-island-smc01` and `bidyadanga-smc01` while building the `unified-network-controller` adapter layer. Written back here per the Standing
Write-Back Contract.

**The correction worth reading first.** A first pass at hope-vale timed out on every cnWave and very nearly entered the record as "cnWave has no SNMP". Those units were simply down — no ICMP and no TCP
on 443, 80 or 22 — while a control XV2 on the same hop answered normally. Sampling `rcp` sites reversed it completely: **cnWave speaks SNMP on `cambium 60`** (`.1.3.6.1.4.1.17713.60`), its own
enterprise arm, which is why walking `21` or `22` finds nothing even on a unit where SNMP works. Confirmed across two sites, three models (V1000, V3000, V5000) and both Distribution and Client roles.

**Enablement splits by PROGRAMME, and the first answer was wrong.** An `rcp`-only sample said "mostly off". Closing the address gap and probing `nbn_accelerate` reversed it:
**40 of 40 reachable nbn units answer; 5 of 19 on rcp.** Same three models, same firmware `1.4`, both node roles on both sides, so this is a provisioning difference between the programmes rather
than a hardware or version one. Addresses were derived by ping-sweeping `10.255.4.0/24` from each SMC box and joining `ip neigh` against the inventory MAC column — 40 cnWave resolved against the 12  <!-- path:example -->
recoverable from stale ARP. `aurukun` and `hope-vale` return zero ARP for that subnet, so their cnWave network is unreachable from the SMC box: a routing question, not an SNMP one. A cnWave timeout means
"not enabled here", never "this family has no SNMP".

**Sampling limit, recorded rather than glossed.** All five responders are `rcp`. `nbn_accelerate` holds 93 of the fleet's 117 cnWave and is unsampled, because hope-vale was unreachable and the other
five nbn cnWave sites — aurukun, doomadgee, galiwinku, kowanyama, pukatja, **86 devices** — carry no `management_ip` in the inventory at all. That address gap is now a documented inventory finding in
its own right.

**Cross-programme comparison added**, on the principle that a family's contract is not stable until it is checked on both Teleport targets. ePMP is identical across both — exactly 43 columns per SM at
hope-vale (10 SMs), mornington (29) and horn-island (14). Enterprise Wi-Fi's radio contract survives the firmware jump: 36 `cambiumRadioEntry` rows on both `6.6.0.3-r9` and `7.1.1-r5`. Per-device
enablement varies within a programme for Wi-Fi too — mornington `10.255.3.10` is silent.

**Three SNMP mechanics documented, each having already cost a wrong reading.** A table entry OID ends in `.1` and a row is `<entry>.<column>.<index>` — using the table OID instead produced 420
"subscriber links" for an AP with 10. A scalar is instance `.0` of its object. An empty table walks as `noSuchObject`, confirmed again when `HOP_XV2_AP26` returned that for `cambiumClientTable` **and**
`0` for `cambiumAPTotalClients` — genuinely zero clients, not an unimplemented subtree.

**Per-device survey filed** as [references/snmp-enablement-survey-20260921.csv](references/snmp-enablement-survey-20260921.csv) — 27 devices, five sites, three families, with the community tried
recorded per row so the "wrong community or not configured?" question is answerable without re-deriving which credential was used where. **13 rows are the actionable ones: pingable but silent.**
Three outcomes are kept distinct because they are not interchangeable — `UP`/`OK` means enabled and the community is right, `UP`/`TIMEOUT` is actionable, and `DOWN`/`TIMEOUT` carries no information
about SNMP at all. That last distinction is the whole hope-vale lesson in one table row.

**Schemas.** New `snmp` layer in `schemas/`, derived by the new `scripts/snmp_schema_from_walk.py` from live walks rather than from mirrors: `schemas/enterprise-wifi/snmp-radio-entry.schema.json` (18 columns),
`schemas/epmp-ap/snmp-connected-sta.schema.json` (42 columns, 13 undocumented in the mirror, including `.43` carrying subscriber firmware), `schemas/cnwave-60ghz/snmp-link-entry.schema.json` (6 columns; `.5` and `.6` left unnamed because
nothing here documents them).

Checks **226 -> 228**.


## 20260920_2339

### Path checking now covers this package's root docs, and a split-filename defect class is enforced (v0.6.3 -> v0.6.4)

Ported from `unified-network-controller`'s staleness audit of the same evening
(`unified-network-controller/docs/reports/staleness-audits/staleness-audit-20260920_2324.md`), which found the same two defects there.

**`SURFACES` was a hand-list of seven files.** `PLAN-xv2-adapter-live-test.md` and anything added later sat outside every path check. It is now derived from the tree — root `*.md` plus
`scripts/README.md`. `references/**` stays excluded, and the reason is stated in the code rather than left as an omission: those files use slash notation for KeePassXC vault groups
(`cambium-devices/epmp-ap`), CIDR blocks and sibling-repo paths, and a path check over them reports about fifty non-defects, which is a check nobody reads. Bringing them in needs a token  <!-- path:example -->
discriminator, not a longer exemption list.

**Three references pointed at a path that no longer exists anywhere.** `PLAN-xv2-adapter-live-test.md` cited `cambium-swap`'s `docs/migration/controller-option3/option-3-architecture.md` and  <!-- path:example -->
`cambium-vendor-adapter-data-points.md`. Those files moved to `unified-network-controller/docs/controller-option3/` in the 2026-09-18 split, so both the root and the path changed and every citation  <!-- path:example -->
here silently sent the reader nowhere. Repointed.

**`SIBLING_ROOTS` added.** A reference into `cambium-swap`, `unified-network-controller` or `skill-smc` now resolves against a declared root, which makes it *verified* rather than merely unchecked —
if a sibling renames the target, this package's routing into it fails loudly. An absent root prints SKIPPED, never passed. Bare basenames are deliberately NOT resolved this way, so
`scripts/README.md`'s `site-addressing.yaml` and `teleport-tunnel.sh` were qualified to `references/site-addressing.yaml` and `skill-smc/scripts/teleport-tunnel.sh`.  <!-- path:example -->

**`check_split_path_tokens()` added.** A wide table cell had wrapped mid-filename in three places here (`SKILL.md`, `RUNBOOK.md`, `references/02_device-access-and-vault.md`), leaving a token ending
in a backslash with its tail on the next row — unfollowable for a reader, and invisible to the path check, which skips anything that does not look like a path. Twenty-one instances were found across
this package and its siblings. Both new checks were negative-tested in both directions.

Checks **167 -> 225**.


## 20260920_1951

### SNMP tested head to head against the 60KB cap — it is the proven fallback now

An earlier entry recorded that REST truncates `client-summary` at 60,000 bytes on busy APs and noted SNMP had **no equivalent cap in principle but had not been demonstrated**, because every SMC box
carrying `snmpget` fronted APs of about ten clients. Installing the binary fleet-wide on `rcp`/`nbn_accelerate` made the test possible.

On the same AP at the same time: REST returned unparseable truncated JSON, while a walk of `cambiumClientTable` returned **63 complete client rows from 1008 varbinds** against a reported count of 64.
A walk is many small PDUs, so there is no single-response limit to hit. The "untested fallback" wording is withdrawn.

### The split is real, and it costs something

Neither path alone is sufficient. SNMP scales past the cap and carries 16 columns; REST carries 95 fields including `rssi` and `assoc_time`, **neither of which exists in the MIB at all**. So the
fields lost on a busy AP are precisely the ones SNMP cannot replace — above roughly 60 clients you can have client detail without per-client RSSI or session start.

That is a constraint on the client/session model rather than a collector preference: whether the busiest APs may carry a thinner client record than the rest is a decision to take deliberately, not
something to discover in production.

### Also checked and rejected

The device's SSH CLI (`show wireless clients`) would be a third path, but `sshpass` is not installed on the SMC boxes, so it needs another dependency to reach somewhere SNMP already goes. Recovering
complete records from the truncated JSON is possible but silently lossy — you never learn how many records fell past the cut.

## 20260920_1856

### Verified against upstream — the NAPALM claim holds, but the docstring oversells conformance

An earlier entry asserted that returning a map keyed by interface name is NAPALM's convention. That was argued from this pack's own XV2 `get_interfaces` docstring, which is the same repo claiming its
own conformance — not an authoritative source. Context7 was unavailable at the time and the claim went in unverified.

Now checked against NAPALM's own published documentation: `get_interfaces` does return a dict keyed by interface name, so **the
claim stands and the correction it supported was right**.

The check added something the local evidence could not. NAPALM defines six value fields — `is_up`, `is_enabled`, `description`, `last_flapped`, `speed`, `mac_address` — and the R-series adapter
returns two of them plus `ipv4_addresses`, which NAPALM does not define. **"NAPALM-style" therefore describes the response shape, not conformance to the interface contract**, and code written against
NAPALM's documented fields will find four of the six absent. Recorded in `schemas/README.md` beside the map-shape note.

## 20260920_1758

### Changed — `ip6_ll` normalised to a list in `scripts/cambium_xv2_adapter.py`

`get_clients()` now returns `ip6_ll` as a list on every record, including records where the device omits the key. The field's JSON type differs by model — array on XV2 (10 of 32 record-bearing fleet
observations), string on E500 (6), absent where the client has no link-local (17) — and a list is the lossless target, since normalising to a string would truncate any XV2 client holding more than
one address. The E500 shares this adapter, so one change covers both models.

Verified against the six shapes the fleet returned (array, array containing empties, string, null, empty string, empty array), plus a record missing the key and non-dict entries, and live against an
XV2. The value is identifying data — an IPv6 link-local is EUI-64 derived and encodes the client MAC, `fe80::6885:b9ff:feac:bb89` resolving exactly to `6A-85-B9-AC-BB-89` — so it is redacted on the
same footing as `mac`.

### Found — `client-summary` is truncated at 60,000 bytes on busy APs

Verifying the normalisation against a 60-client AP surfaced a device limit, not a tooling one. **The device cuts the response at exactly 60,000 bytes and still returns HTTP 200**, so the body ends
mid-record and will not parse. Repeated identically with `?limit=20`, `?limit=10&offset=0` and `?count=10` — no pagination parameter is honoured.

A busy AP therefore yields **nothing**, not partial data, and the 200 status makes it look like a malformed device rather than a capacity limit. This qualifies the earlier finding that REST dominates
SNMP for Wi-Fi client detail: **it dominates on field richness and fails on the busiest APs**, which are the ones client detail matters most for. SNMP has no equivalent single-response cap, but that
is untested against an AP large enough to cross the threshold — the only SMC boxes carrying `snmpget` currently front APs with about ten clients. The sweep's single `bad-json` finding is now
explained.

### Corrected — `snmpget` availability is per box, not per flavour

An earlier entry recorded `net-snmp` as absent on `rcp`-flavour SMC boxes and present on `nbn_accelerate`. Sampling six boxes disproves it: `hope-vale-smc01` (nbn_accelerate) and
`burringurrah-smc01` (rcp) have it; `wandawuy-smc01`, `amata-smc01`, `doomadgee-smc01` (all nbn_accelerate) and `tjuntjuntjara-smc01` (rcp) do not. Two of six, one from each flavour. The original
claim was drawn from three boxes that happened to line up. Corrected in `skill-smc`'s known-issues reference: probe for the binary, never infer it from the flavour.

## 20260920_1745

### Two sites were never unreachable — they run the `-legacy` password

The sweep's five remaining gaps split into authentication and transport. Testing the vault's `-legacy` entries by hand settled it: on the same kalumburu Enterprise Wi-Fi unit, the primary entry
returns `Invalid username or password` and the `-legacy` entry returns `{"success":true}`. The ePMP legacy entries authenticate through the adapter too, and mornington's R-series behaves the same way.

**kalumburu and mornington were missed by a credential rotation** — 132 devices at kalumburu alone, spanning three families and two different vendor login paths. Recorded in
`references/05_known-issues.md` as a site fact, because it breaks any tooling that assumes one current password per family, not just this exercise.

`scripts/fleet_schema_sweep.py` now resolves each family to its primary vault entry plus a `-legacy` fallback, tried in order. **That recovered 4 of the 5 remaining gaps.**

### Coverage: 121 of 122 site/family pairs, 122 observations

Twelve gaps after the first pass; 7 recovered by restoring the original timeouts, 4 by the credential fallback. One survives: **hope-vale cnWave**, TLS handshake EOF on four devices at full timeout
with both credentials, and all units failed ping — down hardware rather than an access problem.

### Corrected — the R-series `interfaces` getter is not an adapter bug

An earlier entry called it one. That was wrong. Returning a **map keyed by interface name is NAPALM's convention**, and every adapter in this pack follows it — see the `get_interfaces` docstring in
`scripts/cambium_xv2_adapter.py`. The defect was in `scripts/schema_tool.py`, which contracted the map's keys as fields and so surfaced 40 interface names across 9 sites as "site-specific fields",
making one site's VLAN plan look like the family's schema.

Map-shaped endpoints are now declared in the tool's `MAP_SHAPED` registry and contracted as `additionalProperties` describing the **value** shape, with observed keys recorded separately. The R-series
interface value is three fields: `ipv4_addresses`, `is_up`, `mac_address`. Its endpoint field count drops 48 → 8, which is the honest number.

### `ip6_ll` — splits by model, and encodes the client MAC

An `array` on XV2 (10 observations), a `string` on E500 (6), absent where the client has no link-local (17). It is EUI-64 derived, so it carries the same identifying information as the MAC field: the
observed `fe80::6885:b9ff:feac:bb89` resolves exactly to client MAC `6A-85-B9-AC-BB-89`. It was already redacted; the reasoning is now recorded beside it. **Normalise to a list at the adapter
boundary** — wrapping the E500 string and mapping absent to empty is lossless, while normalising to a string would truncate any XV2 client holding more than one address.

### Added

`schemas/SWEEP-LOG.md` — the run-by-run record of all five sweeps, including the two that were discarded, the tuning history with the seven false gaps it cost, and both tooling defects.

## 20260920_1652

### Fleet sweep complete — the contract now rests on 111 live observations

All 36 sites swept by `scripts/fleet_schema_sweep.py`, one representative device per family per site, across four runs — two of which produced confidently wrong data and were discarded and repeated. Merged standard: `enterprise-wifi` 9 endpoints / 381 fields / 35 observations, `cnwave-60ghz` 13 / 40 / 5, `cnpilot-r-series` 2 / 48 / 8, `epmp-ap` 4 / 20 / 35, `epmp-sm` 4 / 14 / 35. **118 of 122 site/family pairs contracted.** `client-summary` rests on 32 record-bearing observations covering **248 real client records**.

The sweep was worth running rather than extrapolating from the baseline. Against the fleet, `client-summary` grew 95 → 98 fields, `device-summary` 45 → 47, `platform-info` 15 → 16 and
`radio-rf-summary` 15 → 16. Three cnWave models (V1000, V3000, V5000) and ePMP Force 300-16 appeared that one site never showed.

### The finding that matters for adapter work

**In `client-summary` only 43 of 98 fields are universal — 54 split by model.** `radio-rf-summary` is 7 universal against 9 model-split. An adapter written against an XV2 alone depends on fields an
E500 simply does not return, and fails silently because the field is absent rather than wrong. `ip6_ll` additionally returns **an array at some sites and a string at others**, absent entirely at 17.

the R-series `interfaces` getter turned out not to be contractable: its "site-specific fields" are interface names used as object keys (`eth2.17`, `wan1.500`), so each site's VLAN plan appears as schema
fields. That is an adapter design bug, not device divergence — it should return a list with the name as a value. Recorded in `references/05_known-issues.md` rather than smuggled into the contract.

### Added

`scripts/fleet_schema_sweep.py` (the sweep), `scripts/schema_divergence_report.py` and its generated `schemas/DIVERGENCE.md`, `schemas/SWEEP-LOG.md` (the run-by-run record, including the two sweeps that were discarded), plus `schemas/_observations/` holding all 118 inputs. Both scripts are
cataloged in `scripts/README.md`. 59 reachability findings across the runs are recorded as estate facts rather than skips. A fourth run retried the 12 gaps at full timeout and recovered 7, proving most were a too-tight mid-run retune rather than estate faults. **Five genuine gaps remain**, three of them at kalumburu where 132 devices reject the documented vault credentials across two families — a credential problem that blocks all access to that site, not just this exercise.

### Two defects the sweep found in its own tooling

Both produced confident wrong output rather than an error, so both are written up in `references/05_known-issues.md`:

1. **A delimiter-parsing bug silently dropped the first endpoint of every Wi-Fi observation.** The header was sliced on the same `###` separator the endpoint blocks use, consuming the first block's
   delimiter. `client-summary` was first, so **two complete fleet sweeps produced client data for exactly one site** while every other endpoint parsed cleanly — indistinguishable from "no clients
   connected". Found only by asking why 33 sites with non-zero client counts all had empty client lists.
2. **The device credential was passed as a positional argument to `tsh ssh`**, exposing the admin password in the process table locally and on every SMC box touched. Now fed on stdin. The two sweeps
   before the fix did expose it.

### Method correction carried from the baseline

`required` counts only observations that returned a record, and `check` reports an empty endpoint as `no-records` rather than divergent — otherwise every site whose AP happened to have no client
attached would read as a contract violation.

## 20260920_1556

### Added — `schemas/`, the device response contract

A machine-readable contract for what each Cambium family actually returns, derived from live devices rather than from vendor documentation. JSON Schema (draft 2020-12) with `x-cambium` provenance
annotations, one file per family and endpoint, plus `schemas/_observations/` holding the per-device inputs that justify each merged standard.

This exists because the mirrors are wrong in both directions: `cnPilotMIB` describes 16 client columns where a live XV2 returns 95 (including `rssi` and `assoc_time`, absent from the MIB entirely),
and `CAMBIUM-PMP80211-MIB` documents 29 ePMP connected-SM columns where a live 3000L returns 42.

Stage 1 baseline, one reference device per family: `enterprise-wifi` 9 endpoints / 374 fields (XV2 at hope-vale, E500 at Tjuntjuntjara, `raw-endpoint` layer); `cnwave-60ghz` 13 / 40 (V5000 at
doomadgee); `cnpilot-r-series` 2 / 43 (R195P at burringurrah); `epmp-ap` 4 / 20 and `epmp-sm` 4 / 14 (hope-vale). The four non-Falcon families are contracted at `adapter-normalized` layer — their
adapters' getter output — because only the Falcon UI exposes raw endpoints conveniently. Every schema declares its layer so the two are never merged.

### Added — `scripts/schema_tool.py`

Three verbs: `observe` contracts one device, `merge` folds observations into the family standard, `check` reports a new observation's divergence and exits non-zero so it can gate a sweep.

**The method fix that matters:** `required` counts only observations that actually returned a record. An endpoint returning an empty array is not evidence its fields are absent — an AP with no
clients attached says nothing about a client record's shape. The first merge of the `client-summary` contract for `enterprise-wifi` produced **zero** required fields out of 95 purely because the E500 had no clients at
capture time. Empty observations are now excluded from the presence maths and reported in `x-evidence`, and `check` reports such endpoints as `no-records` rather than divergent. The operational
consequence is written into `schemas/README.md`: for client-bearing endpoints, sweep client counts across a site first and contract the device that has clients.

No response values are recorded. `x-candidate-values` carries short, low-cardinality, non-identifying values only — `"2.4GHz"`, `"ON"`, `"axa"` — where the value set is itself part of the contract.
Client MAC, IP, IPv6, hostname, username and SSID are never emitted, and `--strict-pii` (default) also drops anything that looks like a MAC, IP or hostname whatever its field is called.

### Baseline gaps, stated

the `client-summary` contract for `enterprise-wifi` rests on one record-bearing observation, so the XV2-versus-E-series field split (95 against 44, seen in an earlier run) is not yet in the contract. cnWave `gps`
observed as `null` and `links_count` empty. cnWave at hope-vale was unreachable — all three units down on ping — so the baseline came from doomadgee.

### Next

Stage 2 is the fleet sweep: 36 sites, 5 families, roughly 130 device sessions, throttled for ePMP's concurrent-session budget, with unreachable and empty recorded as findings rather than skips.
Divergence between sites goes to `references/05_known-issues.md`, not into a silently widened contract.

## 20260917_1100

### Added

- Pack scaffolded (bootstrap via `skill-ai-it`): `SKILL.md`, `RUNBOOK.md`, `README.md`, `AGENTS.md`, `CLAUDE.md`, `manifest.json`, `.archcore/` initialized.
- `references/01_overview.md` — device families/models, EoL/EoS snapshot, evidence-state discipline.
- `references/02_device-access-and-vault.md` — KeePassXC `cambium-devices/` vault structure, `kp` wrapper gotchas.
- `references/03_asset-register-conventions.md` — naming grammar, per-site drift, site-name convention, R195P IP-derivation rule. Canonical home for content moved out of the skill-smc pack's numbered
  reference file on this same topic, which is now a short cross-reference stub pointing here instead.
- `references/04_device-inventory-schema.md` — `device-inventory.csv` column contract and extraction workflow.
- `references/05_known-issues.md` — coverage gaps and staleness risks.
- `scripts/check_governance.py` — governance checker generated from `skill-ai-it`'s template, Tier 1 (universal) registries tuned to this pack.

### Notes

- Seeded from the cambium-swap project's 2026-09-17 device-credentialing and device-inventory extraction session — see that project's own changelog entries 20260917_0911 and 20260917_1015.
- Cross-referenced with `skill-smc` in both directions (`SKILL.md` Related Skills, `RUNBOOK.md` Related Workspaces) per operator instruction.
- Generated by `skill-ai-it` in `bootstrap` mode.
- Symlinked at `~/.claude/skills/skill-cambium` and registered in the skills_stuff repo root README's Specialist Packs table for discoverability.

## 20260917_1130

### Added

- `scripts/extract-asset-register.py` — moved here from cambium-swap's session scratchpad per operator instruction, now that this pack is the asset-register knowledge's canonical home. One-off worked
  example, not general-purpose — see its own docstring.
- `justfile`, `.mise.toml` (Python 3.14 pin), `requirements.txt` (`openpyxl`) — runtime isolation per skill-ai-it doctrine: recipes route through `{{py}}` (working-cache peer venv), guarded by
  `_require-venv`; `just bootstrap` / `just runtimes` / `just check` / `just extract-asset-register`.

### Changed

- `scripts/README.md`, `RUNBOOK.md` — routed through `just --list` / `just <task>` instead of direct `python3` invocation.
- `references/03_asset-register-conventions.md` §Extraction Gotchas cross-note and `references/04_device-inventory-schema.md` §Building or Refreshing an Extract — updated to point at the now-real
  `scripts/extract-asset-register.py` instead of stating no script exists.
- `scripts/check_governance.py` — `TASK_RUNNER` set to `justfile`; added one narrow, documented carve-out to the interpreter-pinning check for the `python -m venv` line inside `bootstrap` itself (the
  one recipe that legitimately cannot address `{{py}} by path, since that's the venv it's creating).

### Notes

- `just bootstrap` was not executed this session (would install a real venv) — justfile syntax verified with `just --list` only. Run `just bootstrap && just check` before relying on `just
  extract-asset-register`.

## 20260917_1135

### Added

- `scripts/cambium-portal.sh` — moved here from `cambium-swap` (was cambium-swap's own scripts/cambium-support-login.sh, now removed there). Cross-project Cambium support-portal
  (support.cambiumnetworks.com) automation: `login` (unchanged behaviour) plus a new `fetch-release <model search> <version string> <dest-dir>` subcommand that finds a specific dated
  firmware/documentation release and downloads all its files, sniffing each one's real type since the portal's download links carry no filename. Both need a live MFA code from the operator each run.
- `references/02_device-access-and-vault.md` — documented the confirmed live Hope Vale device-access chain (`tsh` cluster split, SMC-box network path, credential-materialization and `kp`-PATH fixes,
  the Enterprise Wi-Fi REST API auth flow, and the SSH-vs-web-UI comparison), and the `scripts/cambium-portal.sh` move.
- `RUNBOOK.md`, `justfile` — catalogued `scripts/cambium-portal.sh` and its two `just` recipes (`cambium-login`, `cambium-fetch-release`).

### Changed

- `scripts/check_governance.py`: 89/89 passing (up from 84) after the RUNBOOK/justfile additions extended path-resolution coverage.

### Notes

- Prompted by `cambium-swap` work: this pack's own live device-access verification (real SSH CLI login, real authenticated web UI/API session) against a Hope Vale AP, and a version-matched
  documentation fetch (Cambium does not publish a per-patch-version CLI doc separately from firmware/MIBs on the model-specific Downloads page — it publishes a separate per-major-version
  "Documentation" bundle instead, found via its own Archive tab).

## 2026-09-17 — deterministic navigation-control upgrade

<!-- skill-ai-it-upgrade: 2026-08-11-governance-checks-layer-v1 -->

- Applied `skill-ai-it` deterministic navigation-control upgrade.
- Upgraded managed navigation/scripts blocks to version `2026-08-11-governance-checks-layer-v1`.
- Ensured `context-map.yaml` contains `skill_ai_it_version`, `audit_checks`, `promotion_rules`, `context_recovery`, and `update_rules`.
- Preserved user-authored content outside managed blocks.
- Generated outputs remain support-only; no `.archcore/` promotion was performed.

Applied to: context-map.yaml, AGENTS.md, scripts/README.md

## 20260917_1210

### Added

- `scripts/cambium_xv2_adapter.py` — minimal Enterprise Wi-Fi (XV2/Falcon UI) REST adapter: `login`/`logout`, `get_facts()`, `get_interfaces()`. Stdlib-only (no `requests`, no venv/dependency). Run
  live against Hope Vale Tower 1 (`10.255.3.1`) via a `tsh` tunnel — matched evidence E101 exactly (hostname, serial, firmware, MAC, live cnMaestro status).
- `PLAN-xv2-adapter-live-test.md` — resume-point plan doc for this test; kept even though the test completed the same session, as the template for the next family/vendor adapter test.

### Fixed

- `get_interfaces()`'s first draft trusted `device-summary`'s `port_stats[].link` field, which reported `"DOWN"` for every port including `ETH1` even though `ETH1` was physically up and passing real
  traffic. The device's separate `port_status[]` array (integer 1/0 link/duplex encoding) is authoritative for link state; `port_stats` is reliable only for byte/packet counters. Fixed to merge both
  by port name. Re-verified live: `ETH1` now correctly reports `is_up=true, speed=1000M, duplex=FULL`.

### Decision

- Operator proposed a formal CLI/API grammar + capability-model skill (`device-interface-modeler`: command-schema.json, OpenAPI generation, Tree-sitter/ANTLR, AI-extraction pipeline) ahead of writing
  any real adapter, given the plan to go multi-vendor later. Ran `skill-walk-before-run` — RED (no reality contact yet, peripheral tooling ahead of a still-stubbed core capability). Cheapest test
  (this adapter) resolved it: `PASS`, formal schema not needed. RESOLVED entry appended to `skill-walk-before-run`'s `ledger.jsonl` (mirrored to `cambium-swap/.wbr-ledger.jsonl`). Multi-vendor plans
  don't change the conclusion — the real cross-vendor abstraction already exists in `cambium-swap`'s
  [option-3-architecture.md](/Volumes/Data/_ai/_project/project_stuff/apn/cambium-swap/docs/migration/controller-option3/option-3-architecture.md) adapter contract (`get_facts`/`get_interfaces`/...);
  a second vendor gets its own specialist skill pack implementing the same method names, same pattern as `skill-smc`/`skill-cambium`. Revisit only once a second real vendor adapter exists to design
  against.
- All Cambium development work (this adapter, the portal script moved earlier this session) goes into `skill-cambium`, not into `cambium-swap` — explicit operator instruction, reinforcing this pack's
  existing Standing Write-Back Contract.

### Notes

- `just check` / `python3 scripts/check_governance.py`: run before considering this durable — see the Changed section below for the actual count.

## 20260917_1200

### Changed

- `AI_NAVIGATION.md` — hand-added a "Context compaction recovery" section and a "Companion files" note under Update rules. This file's navigation block is project-managed (`skill-ai-it:manual`), so
  the automated upgrade correctly refused to touch it; these two content gaps were unrelated to the file's declared opt-out reason (task→reference routing table, skill-smc boundary), so they were
  added by hand instead of left failing.

### Added

- `ARCHCORE_PROMOTION_CANDIDATES.md` — first promotion-candidate report since `.archcore/` was initialized at bootstrap. Surfaces 2 ADR candidates and 4 rule candidates from `SCRATCHPAD.md`
  (KEEP-marked decisions) and `AGENTS.md`; no spec or plan candidates found. Report only — no `.archcore/` content written.

### Notes

- Generated by `skill-ai-it` in `refresh` mode, immediately following the deterministic upgrade run above.
- `scripts/check_governance.py`: 92/92 passing (unchanged count from before this refresh — no new catalog surfaces were added).
- This pack has no Repomix config yet, so the new candidates file was not added to any generated context pack.

## 20260917_1230

### Added

- `.archcore/adr/adr-separate-pack-from-skill-smc.md` — proposed
- `.archcore/adr/adr-vault-file-avoids-opa-blocked-words.md` — proposed
- `.archcore/rules/rule-vault-reference-convention.md` — proposed
- `.archcore/rules/rule-cambium-smc-cross-pack-boundary.md` — proposed
- `.archcore/rules/rule-manifest-version-discipline.md` — proposed
- `.archcore/specs/spec-specialist-pack-file-roles.md` — proposed (reclassified from a rule candidate to a spec, mirroring skill-smc's identical document)
- `.archcore/README.md` — durable index for the 6 documents above; carries the never-promote reasoning forward from the deleted candidate queue

### Changed

- `README.md`, `AI_NAVIGATION.md` — updated the `.archcore/` description from "empty" to "6 documents proposed 2026-09-17"
- `scripts/check_governance.py` — registered `ARCHCORE_PROMOTION_CANDIDATES.md` in `CONDITIONAL_PATHS` so this and future CHANGELOG mentions of it do not fail path resolution now that the file is
  gone; updated the stale "empty pending first promotion" comment on the three `.archcore/` subfolder exemptions

### Removed

- `ARCHCORE_PROMOTION_CANDIDATES.md` — deleted per promote-mode contract; it was a proposal queue, not a record

### Notes

- Generated by `skill-ai-it` in `promote` mode, per operator instruction ("promote them") against the candidates surfaced in the prior refresh run.
- All 6 documents are `status: proposed`, not `accepted` — operator review of each is still outstanding; flip the frontmatter `status:` field once reviewed.
- The vault-related ADR's first draft filename was itself blocked by the workspace's OPA write-gate for containing a blocked substring — direct confirmation of the decision it records; the final
  filename avoids it, and the same avoidance was applied to the vault-related rule's filename.
- `scripts/check_governance.py`: 94/94 passing.

## 20260917_1245

### Changed

- All 6 `.archcore/` documents — `status: proposed` → `status: accepted` per operator instruction ("accept them all"): both ADRs, all 3 rules, and the spec.
- `.archcore/README.md` — reworded from "6 proposed, not yet accepted" to "6 accepted by the operator on 20260917", mirroring the agent-stack pack's index phrasing; noted that an accepted document is
  superseded in place rather than deleted.
- `README.md`, `AI_NAVIGATION.md` — `.archcore/` descriptions changed from "proposed" to "accepted"; `AI_NAVIGATION.md`'s Project context files table authority column changed from "Highest, once
  accepted" to "Highest".

### Notes

- These 6 documents are now this pack's highest-authority source per `AI_NAVIGATION.md`'s source-priority list.
- `scripts/check_governance.py`: 102/102 passing.

## 20260917_1300

### Fixed

- `scripts/check_governance.py` — `CATALOGS` never covered `scripts/README.md` ↔ `scripts/`, only `RUNBOOK.md` ↔ `references/`. `scripts/cambium-portal.sh` had been sitting uncataloged since it was
  moved in from `cambium-swap`, despite `scripts/README.md`'s own maintenance rule claiming the checker enforces this. Added `"scripts/README.md": ("scripts", "*")` to `CATALOGS`; proved the new check
  could fail (it did, immediately, on the exact gap it was meant to catch) before fixing the gap.
- `scripts/README.md` — added the missing `scripts/cambium-portal.sh` row to the Raw Script Inventory (purpose, inputs, outputs, safety labels, idempotency, when to use).

### Changed

- `AGENTS.md` — extended the Project-coherence checklist with a new Tier 1b ("Scripts") and broadened the Cross-project write-back trigger's closeout self-check to explicitly ask about scripts, not
  just facts. Prompted by an operator design question: how does this pack learn about a Cambium-domain script written or moved in from a consuming project, given this pack has no visibility into
  another project's filesystem? Answer used: no push mechanism is needed (same local filesystem, an agent session in the consuming project already has direct read/write access to this pack's canonical
  path) — the fix is a stronger *closeout obligation* on the consuming-project session, worded against the two real precedents (`scripts/cambium-portal.sh`, `scripts/extract-asset-register.py`) and
  against the coverage gap just found and fixed above.

### Notes

- Generated during a `refresh`-adjacent maintenance pass, not a full `skill-ai-it refresh` run.
- `scripts/check_governance.py`: 108/108 passing (up from 102 — 4 new assertions from the scripts/README.md catalog-coverage direction, 2 more counted-and-passing after the AGENTS.md path fix below).
- The first draft of this entry's AGENTS.md edit referenced the same two scripts as bare filenames in prose; the governance checker's path-resolution check correctly failed because those names only
  resolve under `scripts/`, not at the pack root. Fixed by qualifying both with the `scripts/` prefix — a pitfall this checker itself is meant to catch, and did.

## 20260917_1440

### Added

- `scripts/cambium_xv2_adapter.py`: `get_radios()`, `get_wlans()`, `get_clients()`, `get_config()`, `get_events()` — the remaining rows from
  [cambium-vendor-adapter-data-points.md](/Volumes/Data/_ai/_project/project_stuff/apn/cambium-swap/docs/migration/controller-option3/cambium-vendor-adapter-data-points.md), all run live against Hope
  Vale Tower 1. `get_radios()` merges `radio-summary` (state/channel/power) with `radio-rf-summary` (utilization/noise floor) by list position — neither response carries a join key. `get_wlans()`
  merges `wlan-summary` with `wlan-interface-summary` by SSID (`/api/wlan-config` 500'd on this firmware with no params — not used). `get_clients()` returned an empty list live, which is a real state,
  not a bug. `get_events()` caps output at a `limit` param (raw log observed live was 41KB).
- `get_raw(endpoint)` — public escape hatch for exploring an endpoint with no getter yet; deliberately returns unredacted data and says so in its docstring, so callers cannot mistake it for safe.
- `--dump <endpoints> --dump-dir <dir>` CLI mode — writes one redacted JSON file per endpoint instead of printing to stdout. Added specifically because the operator asked "why didn't you create a
  script?" after this session's exploration was done as ad hoc `curl` chains instead of through the adapter itself — the right fix was giving the adapter script a first-class exploration mode, not a
  separate one-off shell script.

### Fixed — real secret exposure, see `references/05_known-issues.md` Security Incidents

- `REDACT_KEY_PATTERN` (module-level, used by both `get_config()` and `--dump`) extended from `pass|psk|secret|key|shared` to also match `community|radius|credential|token|auth`, after an ad hoc
  redaction pass during exploration missed `snmp_read_community`/`snmp_write_community` and printed them to a terminal transcript. The earlier per-call redaction logic was also centralized into one
  `redact()` function so there is exactly one place this can go wrong, not one per caller.

### Notes

- `python3 scripts/check_governance.py`: run before considering this durable — see the next entry's Changed section for the count if this was not re-verified standalone.

## 20260917_1500

### Added

- `references/06_device-api-cli-reference.md` — the Enterprise Wi-Fi (XV2) adapter data-points table (REST endpoint + SSH CLI fallback + live-verified quirks per `get_facts`/`get_interfaces`/
  `get_radios`/`get_wlans`/`get_clients`/`get_config`/`get_events`), migrated in from `cambium-swap`'s
  [cambium-vendor-adapter-data-points.md](/Volumes/Data/_ai/_project/project_stuff/apn/cambium-swap/docs/migration/controller-option3/cambium-vendor-adapter-data-points.md). Prompted by an operator
  design correction: Cambium equipment knowledge (API endpoints, CLI commands, their quirks) belongs in this pack, not duplicated into a consuming project's docs — raw evidence/captures stay in the
  project, the technical knowledge itself lives here next to the adapter code that consumes it.
- `RUNBOOK.md` Reference Routing table and `SKILL.md` References/Use-When lists — both extended with the new file.

### Changed

- `cambium-swap`'s [cambium-vendor-adapter-data-points.md](/Volumes/Data/_ai/_project/project_stuff/apn/cambium-swap/docs/migration/controller-option3/cambium-vendor-adapter-data-points.md) rewritten
  to a thin, project-scoped pointer (why Option 3's controller needs this data, evidence-ID citations) that links here for the actual endpoint/command table, instead of holding a second copy of it.

### Notes

- `python3 scripts/check_governance.py`: run after this entry to confirm the new reference file is fully cataloged (RUNBOOK.md routing row, SKILL.md references list).

## 20260917_1510

Operator asked to verify the XV2 adapter against a couple more physical units, not just Tower 1.

### Added

- `references/05_known-issues.md` Coverage Gaps — Hope Vale Tower 2 (`10.255.3.2`) recorded as unreachable (`ping`/SSH from `hope-vale-smc01` both returned "no route to host"), found while sweeping
  for a second/third test unit.

### Changed

- `references/06_device-api-cli-reference.md` Evidence and Version Scope — extended from one confirmed unit (Tower 1) to three: Tower 5 (`HOP_XV2_AP5_IP3_5`) and Tower 6 (`HOP_XV2_AP6_IP3_6`) both ran
  all seven getters live in one pass each, same firmware (`6.6.0.3-r9`), same cnMaestro server, different serials — the adapter's output shape holds across physical units, not just the one it was
  developed against.

### Notes

- Both new devices' raw redacted JSON output archived in `cambium-swap`'s [captures/device-queries/](/Volumes/Data/_ai/_project/project_stuff/apn/cambium-swap/captures/device-queries) (gitignored) and
  cited by sha256 in `cambium-swap`'s `evidence/evidence-register.csv` entry E108 — full provenance lives there, not duplicated here.
- Reachability sweep of 9 Hope Vale XV2/backhaul IPs from `hope-vale-smc01` found only Tower 2 down; Towers 5, 6, 7, 8, 9, 10, 11, 12, 13 all answered ping. Only 5 and 6 were actually queried this
  session — the others remain unverified, just known-pingable.
- `python3 scripts/check_governance.py`: run after this entry to confirm no broken references.

## 20260917_1600

Operator asked to try one of each remaining device family (cnPilot R195P, ePMP SM, ePMP AP), skipping cnWave 60GHz for now.

### Added

- `references/06_device-api-cli-reference.md` — new ePMP AP/ePMP SM section: `show dashboard` CLI (SSH) confirmed live on one unit of each, plus a previously-undocumented HTTPS JSON API discovered by
  reading the web UI's own JS bundle — a LuCI-derived `/cgi-bin/luci` RPC surface (`stok` + `sysauth_<host>` cookie both required, HTTP 200 on auth failure so don't trust the status code alone),
  confirmed live via `test_connect`.
- `references/06_device-api-cli-reference.md` — new cnPilot R195P section documenting the addressing investigation (see Fixed below) and a cnWave 60GHz stub noting it's still untouched.
- `references/05_known-issues.md` — R195P's existing IP-derivation gap upgraded with the live-ARP contradiction; new Coverage Gaps row for Burringurrah addressing generally, since the same failure
  mode was independently found on the XV2 rows, not just R195P's.

### Fixed

- Nothing broken in code — the finding itself is the useful output. R195P was never reached: `burringurrah-smc01`'s ARP table shows zero hosts at `10.255.10.x` (the `EXT10XX → 10.255.10.XX` derivation
  rule's target range) against 96 entries elsewhere on the same bridge. MAC-OUI cross-check on those other entries found Burringurrah's real XV2 fleet at `10.255.11.x` (OUI `bc:a9:93`, matching
  confirmed live Hope Vale XV2 units) and real ePMP fleet at `10.255.21.x` (OUI `58:c1:7a`, matching confirmed live Hope Vale ePMP units) — contradicting the `.3.x` addresses most Burringurrah XV2
  rows in `device-inventory.csv` record, while confirming the `.21.x` addresses most Burringurrah ePMP SM rows already use.

### Notes

- ePMP AP and ePMP SM: `device-family-matrix.csv`'s SSH/CLI notes upgrade from `USER_STATED` to `VERIFIED-OBSERVED` for the two units tested; the API discovery is new information, not present in that
  matrix at all yet.
- The ePMP LuCI API's actual per-page RPC method names (the JSON equivalent of `show dashboard`) are still unknown — `test_connect` proves the auth mechanism works, not full data retrieval. Left as a
  stub for whoever builds an ePMP adapter next, same shape as `scripts/cambium_xv2_adapter.py`.
- R195P remains completely unverified — this session found *why* previous attempts would have failed (wrong address, not just an expired Teleport session), not a working device session. Getting one
  needs a corrected address, not another SSH/API attempt at the recorded one.
- `python3 scripts/check_governance.py`: run after this entry to confirm no broken references.

## 20260917_1630

Operator asked why no adapter data points existed for anything but XV2, then to go build them. Along the way: a second live secret-exposure incident, a script relocated to its correct owning pack on
operator correction, and a new script built proactively per a standing instruction to stop waiting to be asked for repeated manual patterns.

### Added

- `scripts/cambium_epmp_adapter.py` — the ePMP counterpart to `scripts/cambium_xv2_adapter.py`: `login`/`logout`, `get_facts()`, `get_interfaces()`, `get_wireless_link()` (SM-only, `None` on an AP),
  `get_clients()` (AP-only, `[]` on a SM), `get_config()` (redacted). Stdlib-only. Verified live against Hope Vale Tower 5 (SM, via a captured-data replay after the device's session limit blocked a
  final live run — see Fixed) and Tower 1 Omni0 (AP, fully live). Built from real reverse-engineering of `cambium.<hash>.js`: found the real `get_param`/`act=status`/`act=config_regular` RPC surface
  (46 real method names enumerated), not guessed.
- `references/06_device-api-cli-reference.md` — ePMP section rewritten from narrative access notes into a real Data Points table matching XV2's shape, citing the adapter.
- `scripts/scan-config-fields.py` (`just scan-fields <path>`) — reports which JSON keys look credential-shaped without ever printing their values. Built unprompted after a standing instruction: create
  a script/just-recipe once something's been done by hand two or three times rather than waiting to be asked. This session did the "print a value to check if it's a real secret" mistake twice — this
  makes the safe version the easy path going forward, in this pack or any consuming project.
- `justfile` — `epmp-getters host role="sm"` (runs the new adapter's getters, pulling the right vault credential by role) and `scan-fields path`.

### Fixed

- `get_wireless_link()`: `cambiumSTADLRSSI` exists (=0) on an AP too, so its mere presence isn't a valid SM-vs-AP discriminator — an AP was returning a bogus zeroed-out link dict instead of `None`.
  Now checks `cambiumConnectedAPMACAddress` instead (a SM reports a real MAC; an AP reports the literal string `"Not Associated"`). Found and fixed live before this entry, verified against both device
  roles.
- ePMP SM (`10.255.4.5`) hit the device's real concurrent-session cap (`{"users":{"ro":0,"rw":5}}`) mid-session, from earlier untidy testing that never called `logout()`. It never cleared during this
  session — the adapter's final live-verification run against SM had to be substituted with an offline replay of the SM `act=status` payload already captured earlier in the session, run through the
  same parsing code. Confirmed correct (real facts, real wireless-link RSSI/SNR, empty clients as expected), but it's a replay, not a fresh live call — worth one more real SM run next session to close
  that gap properly.

### Changed

- **[teleport-tunnel.sh](/Users/malik.ahmad/.claude/skills/skill-smc/scripts/teleport-tunnel.sh) moved to `skill-smc`.** Built here first for Cambium device-access convenience, then the operator
  corrected the framing directly: "it's not Cambium tunnel, it's teleport tunnel" — generic Teleport tunneling is `skill-smc`'s concern, not this pack's, per each pack's own boundary rule. Moved,
  generalised (site -> SMC-host resolved live from ansible-wifi's own `[<site>_smc_bases]` inventory groups, never hardcoded — a second operator correction, catching an earlier hardcoded site table
  before it was even committed), and `skill-cambium`'s `just tunnel` now calls the canonical `skill-smc` path directly. See `skill-smc`'s own `CHANGELOG.md` (`20260917_1620`, v0.1.40 -> v0.1.41) for
  its side.

### Security Incidents

- Second live secret-exposure incident this session (first was XV2's SNMP communities, `20260917_1440`): ePMP SM's real SNMP community strings, RADIUS password, and wireless encryption key printed to
  this transcript while manually checking whether `act=config_regular`'s flagged fields held real values. Full incident record and fix (`scripts/scan-config-fields.py`):
  `references/05_known-issues.md`.

### Notes

- R195P and cnWave 60GHz untouched this entry — out of scope, per the earlier operator instruction to skip 60GHz and the still-open addressing problem blocking R195P (`20260917_1600`).
- `python3 scripts/check_governance.py`: 126/126 passing.

## 20260917_1700

Operator asked how to capture per-site addressing conventions so future queries at different sites can consult it, given 20+ `nbn_accelerate` sites and 10+ `rcp` sites exist and only two have ever
been checked. First answer was a markdown table (added to `references/03_asset-register-conventions.md`); operator then asked whether YAML/TOML/JSONL would be better, given the site count. Agreed a
structured companion earns its keep at that scale and built it.

### Added

- `references/site-addressing.yaml` — machine-readable per-site/per-family IP addressing trust state (`verified`/`contradicted`/`unverified`) plus a MAC-OUI lookup (`bc:a9:93` ->
  `enterprise-wifi-xv2`, `58:c1:7a` -> `epmp`), both confirmed live this session. Deliberately sparse — only `hope-vale` and `burringurrah` have entries, since those are the only two sites ever
  checked; the file's own header explicitly warns against guessing a pattern for an unchecked site by analogy to a checked one (the two already disagree with each other).
- `references/03_asset-register-conventions.md`'s new "Per-Site IP Addressing Reality" table (added earlier this session, `20260917_1630`-adjacent but not yet logged) — narrative version of the same
  data, now cross-linked from the YAML and vice versa. Neither is canonical over the other: the `.md` carries evidence citations and prose caveats, the YAML is the queryable form.
- `RUNBOOK.md` and `SKILL.md` — new routing row/reference-list entry for `references/site-addressing.yaml`.

### Notes

- Explicitly scoped to exclude site -> SMC-host -> Teleport-cluster data, which stays resolved live from ansible-wifi by `skill-smc`'s
  [teleport-tunnel.sh](/Users/malik.ahmad/.claude/skills/skill-smc/scripts/teleport-tunnel.sh) — this file only answers "which octet does family X live on at site Y", a genuinely Cambium-specific fact
  ansible-wifi's own inventory doesn't carry.
- No script consumes this yet — built now specifically because the site count (30+) makes ad hoc markdown-table lookups impractical, not because a consumer exists today. The natural next step, if
  wanted, is a validation script that flags `device-inventory.csv` rows whose `management_ip` doesn't match this file's confirmed pattern for that site+family.
- `python3 scripts/check_governance.py`: run after this entry to confirm no broken references. Note `references/*.yaml` isn't swept by the pack's `CATALOGS` glob (`references/*.md` only), so this
  file's discoverability relies entirely on the manual `RUNBOOK.md`/`SKILL.md` rows above, not an enforced check.

## 20260917_1710

Operator asked whether evidence (E99-E111) should move from `cambium-swap` into this pack, since this pack claims to be cross-project. Conclusion: no — `cambium-swap`'s evidence register is that
project's whole investigation trail (corporate filings, vendor docs, dependency-class tags), not just device facts, and importing that machinery here would be scope creep. The real gap: this pack's
`Ennn` citations should read as self-contained (the fact stated inline, the ID as an optional pointer for provenance detail), never a hard dependency on `cambium-swap` being present.

### Fixed

- `references/site-addressing.yaml` — the three Hope Vale `trust: verified` entries (`enterprise-wifi-xv2`, `epmp-ap`, `epmp-sm`) had an `evidence:` list but no `notes:`, unlike the Burringurrah
  entries — a reader without `cambium-swap` access would see `trust: verified` with no explanation of what was actually confirmed. Added a `notes:` line to each, matching the Burringurrah rows'
  self-contained style. Audited every other `Ennn` citation in this pack (`references/03_asset-register-conventions.md`, `references/06_device-api-cli-reference.md`, this file) — all already state the
  fact in prose before citing the ID, no changes needed there.

### Notes

- `python3 scripts/check_governance.py`: 131/131 passing.

## 20260917_1720

Operator pushed further on the previous entry: if this pack doesn't validate `Ennn` citations, and `cambium-swap`'s own register could change without this pack knowing, what's the actual logic of
citing an external ID at all — shouldn't the whole register just live here? Landed on: no, most of that register is `cambium-swap`'s own investigation evidence (corporate filings, vendor docs,
community posts), not this pack's domain; relocating the file would just move the coupling, not remove it. The real fix is smaller — stop citing `Ennn` IDs at all.

### Changed

- `references/site-addressing.yaml` (`schema_version: 1` -> `2`) — every `evidence: [Ennn, ...]` list replaced with a self-contained `verified: "<date> — <device> — <method>"` string. `oui_reference`
  entries got the same treatment. Nothing here depends on `cambium-swap`'s register existing, being unchanged, or being reachable anymore.
- `references/03_asset-register-conventions.md` — the Per-Site IP Addressing Reality table's evidence column reworded from bare `Ennn` citations to inline dates/methods; header retitled "Live reality
  (confirmed 2026-09-17)".
- `references/06_device-api-cli-reference.md` — both `Ennn` mentions reworded to point at "cambium-swap's own evidence register" generically (for anyone who wants the raw session/sha256 trail) rather
  than naming specific IDs that could be renumbered or superseded with nothing here to notice.

### Notes

- `CHANGELOG.md`'s own historical `Ennn` mentions (`20260917_1210`, `20260917_1510`) were deliberately left alone — those are dated log entries describing what happened in a past session, not
  current-knowledge claims this pack is asserting today. Same "do not enforce history" principle this pack already applies to counts and states elsewhere.
- This closes the loop from the last two entries: the drift risk raised in `20260917_1700`/`20260917_1710` (an `Ennn` citation could go stale with nothing here noticing) is now moot for this pack's
  own files — there's no external ID left to go stale.
- `python3 scripts/check_governance.py`: run after this entry to confirm no broken references.

## 20260917_1730

Operator pointed out the previous entry's fix (`verified: "<date> — <device> — <method>"` as one prose string) undercut the file's own stated purpose — queryable, not just readable.

### Changed

- `references/site-addressing.yaml` (`schema_version: 2` -> `3`) — every `verified:` string replaced with a structured block: `date`, `method` (one of a fixed enum — `ssh-cli-session`,
  `ssh-rest-session`, `luci-api-session`, `arp-mac-oui-match`, `arp-absence`), plus whichever of `devices`/`host_count`/`oui`/`firmware`/`site` actually applies. `notes` stays free text, but only for
  a genuine one-off caveat — the file's own header now says to give a repeated caveat shape a real field instead of writing the same sentence twice.
- MAC-address keys under `oui_reference` explicitly quoted (`"bc:a9:93"`) — harmless either way in this parser, but removes any doubt about colons-in-keys ambiguity for a future editor or a stricter
  YAML parser.

### Notes

- Confirmed the file still parses clean and demonstrated the actual payoff: `method`/`devices`/`host_count` are now filterable fields, not something a reader would have to regex out of a sentence.
- `python3 scripts/check_governance.py`: 131/131 passing.

## 20260917_1930

Operator asked, after `cambium-swap`'s multi-site cnMaestro reconciliation, whether every device type is now accessible. Answer: no — accessibility varies a lot by family. Fixed one stale matrix row
and logged the gaps that answer surfaced.

### Fixed

- `inventory` (via `cambium-swap`'s `inventory/device-family-matrix.csv`) — `R195P`'s `local_ssh` field still said `UNVERIFIED (Telnet documented)`, contradicting a real live SSH login this session
  (`cambium-swap` evidence E113/E114: `BUR-R195P-1047`, `BUR-R195P-1055`). Corrected to `VERIFIED-OBSERVED`. The edit briefly shifted every field after `local_ssh` by one column (a plain-text comma
  inside the new note broke the row's alignment) — caught and fixed by re-parsing the row with `csv` before it was left broken.

### Added

- [references/05_known-issues.md](references/05_known-issues.md) — three coverage gaps this pack didn't have rows for: Enterprise Wi-Fi E-series (`E500`/`E430`, credentialed but never live-tested —
  first real units surfaced 2026-09-17 in `cambium-swap`'s multi-site reconciliation), ePMP Force 300-16 in an AP role (first seen at Kalumburu, same hardware as the verified SM role but untested as
  an AP), and cnWave 60GHz (`V1000`–`V5000`, still no adapter or live access attempt at all).

### Notes

- `python3 scripts/check_governance.py`: 131/131 passing.

## 20260917_1946

Operator asked to log in and fill in adapter data points for the three untested types 20260917_1930 flagged as gaps.

### Added

- [references/06_device-api-cli-reference.md](references/06_device-api-cli-reference.md) — "Enterprise Wi-Fi E-series (E500, E430)" section: same Falcon-family REST/CLI adapter as XV2, confirmed live
  against real `E500` (Tjuntjuntjara, codename `Gambit`, firmware `4.2.3.1-r9`) and `E430H` (Mowanjum, codename `Sage`, firmware `4.2.3.1-r17` — the device's own `show version` output resolves E31's
  H-vs-W ambiguity for this unit). A note under the ePMP section confirms Force 300-16 in an AP role (Kalumburu) works identically to the verified SM role, but only with the `epmp-ap-legacy` vault
  credential — the first real hit of the "minority of field units... legacy default" risk, not just a theoretical note. The cnWave 60GHz section now records a real, partial finding instead of "no
  attempt yet": SSH login against a live V5000 succeeded, but the E2E controller's interface is a full interactive TUI that stalls under non-interactive/forced-pty exec — no data points extracted,
  blind key-navigation against production hardware was deliberately not attempted.
- [references/05_known-issues.md](references/05_known-issues.md) — the E500/E430 and Force-300-16-AP gap rows removed (both now `VERIFIED-OBSERVED`); the cnWave row narrowed to specifically "data
  points beyond login" now that login itself is confirmed.

### Notes

- `cambium-swap` evidence E118 has the full session detail (exact commands, credentials tried, why the cnWave TUI was not navigated blind).
- `python3 scripts/check_governance.py`: 131/131 passing.

## 20260917_2021

Operator asked to check the official cnWave TUI docs, and whether the REST API works. Checked the vendor's already-archived User Guide (`cambium-swap` evidence/archived-docs/E44) before doing anything
live — it has no CLI/TUI content at all. Then confirmed the REST API instead, fully closing this gap.

### Fixed

- [references/06_device-api-cli-reference.md](references/06_device-api-cli-reference.md) cnWave section rewritten from "no adapter, login only" to a full adapter data-points table: JWT auth (`POST
  /local/userLogin`), 7 confirmed-live endpoints (`getDeviceInfo`, `getE2eInfo`, `getStatusInfo`, `getSystemCapability`, `getLinksCount`, `getGpsBrief`, plus `/api/getTopology` and
  `/api/getCtrlStatusDump` under the same token), and the write-shaped endpoints identified but never called.
- [references/05_known-issues.md](references/05_known-issues.md) — the cnWave coverage-gap row removed; fully resolved.

### Notes

- Key finding: the official 60 GHz cnWave User Guide (Release 1.8, exact firmware match, already in `cambium-swap`'s evidence archive since 2026-09-14 — should have been checked before any live
  SSH/TUI attempt) has zero SSH/CLI/console mentions across 12,378 lines. The SSH TUI reached in the prior entry is undocumented/internal; the web UI's backing REST API is the real, vendor-sanctioned
  interface — same conclusion this project already reached for XV2 and ePMP.
- `cambium-swap` evidence E119 has the full session detail, including an operational note about a download-tooling mishap (browser automation briefly wrote large firmware files into the wrong
  directory — caught and cleaned up, nothing committed).
- `python3 scripts/check_governance.py`: 131/131 passing.

## 20260917_2050

Operator asked to fill the remaining cnWave gaps (CN-role coverage, more endpoints) and pointed out only two of four confirmed families had a real vendor adapter file.

### Added

- `scripts/cambium_cnwave_adapter.py` — JWT bearer-token REST adapter: `login()`/`logout()`, `get_facts()`, `get_e2e_info()`, `get_status()`, `get_capability()`, `get_links_count()`, `get_gps()`,
  `get_topology()`/`get_ctrl_status_dump()` (E2E-role only), `get_config()` (redacted). Verified live against a real V5000 (E2E/POP role) and V2000 (plain Client Node), Hope Vale.
- `scripts/cambium_r195p_adapter.py` — this pack's first adapter that shells out to system `ssh`/`sshpass` instead of using a REST client (no REST API confirmed for this family): `get_facts()`,
  `get_interfaces()`. Verified live against two real Burringurrah units. Two real bugs found and fixed during that live test: a named interface (`wan1`) that doesn't exist on every unit was treated as
  a fatal error instead of a tolerable "unknown" (confirmed one unit uses `eth2.500` for the same WAN role instead); this BusyBox's `ip -o addr show` interleaves LINK-shaped lines with ADDR-shaped
  lines for the same interface, which a naive positional parser mis-split into duplicate keys — fixed with a regex-based parser.
- `references/06_device-api-cli-reference.md` — cnWave section rewritten with the confirmed CN-role behaviour and additional endpoints (`getCnAgentConfig`, `minionConfigGet`); new "cnPilot R195P —
  Adapter" subsection.
- `scripts/README.md` — catalogued both new adapters.

### Fixed

- Confirmed cnWave's local REST API works on every node regardless of role, not E2E-only as previously assumed — the real distinction is that `/api/getTopology`/`/api/getCtrlStatusDump` only return
  data from the E2E-enabled node.
- `references/05_known-issues.md` — Enterprise Wi-Fi E-series and Force 300-16 AP gaps confirmed already closed; no new entries needed.

### Notes

- R195P SNMP: checked `cambium-swap`'s `ansible-wifi` R195P provisioning template — the Get/Set community values are encrypted blobs in the device's own config-encryption format, identical fleet-wide,
  not decryptable and not attempted. Deliberately did not implement `get_config()` for R195P for the same reason plus this project's two prior secret-exposure incidents on other families.
- All comments/docstrings in the four hand-authored adapters (xv2, epmp, cnwave, r195p) rewrapped to this project's 160-column standard.
- `python3 scripts/check_governance.py`: 133/133 passing.

## 20260917_2057

Operator added four real SNMP community credentials to the KeePassXC vault (`apn-snmp-ro`/`rw`, `nbn-snmp-ro`/`rw`) and asked why the remaining rcp sites and OUI blocks weren't in
`references/site-addressing.yaml` yet.

### Added

- SNMP live-verification, closed fleet-wide in one pass: real SNMPv2c `sysDescr`/`sysName` GETs confirmed against one device per major family (R195P via `apn-snmp-ro`, XV2/ePMP AP/cnWave V5000 via
  `nbn-snmp-ro`) — confirms the `apn`/`nbn` split maps exactly to `smc_flavour`. Did not test either `-rw` community (no SNMP SET attempted).
- `references/site-addressing.yaml`: all nine rcp sites the operator's cnMaestro exports covered this session now have entries (was only hope-vale + burringurrah), derived from `cambium-swap`'s
  already-reconciled `device-inventory.csv` — each site's dominant octet-per-family pattern plus real host counts, with secondary/spillover subnets noted where a site splits a family across multiple
  towers. Three more XV2 OUI blocks added (`fc:11:65`, `b4:a2:5c`, `bc:e6:7c`) — this family uses at least five different OUI blocks fleet-wide depending on procurement batch/site, not one; `58:c1:7a`
  also turned out to cover the Enterprise Wi-Fi E-series, not just ePMP. New `snmp-get-session` method value added to the file's own method enum.

### Fixed

- `inventory` (via `cambium-swap`'s `device-family-matrix.csv`) — `local_snmp` upgraded from `USER_STATED` to `VERIFIED-OBSERVED` for R195P, XV2-2T0, ePMP 3000L, and V5000.
- Removed [references/site-addressing.yaml](references/site-addressing.yaml)'s own now-obsolete "eight sites not yet added" note, since they now are.

### Notes

- Full evidence detail (exact devices, IPs, sysDescr strings) lives in `cambium-swap` evidence E122, per this project's routing rule — not duplicated here.

## 20260917_2130

`skill-staleness-audit` run in full detail mode against this pack (invoked by a coordinating session, not the operator directly) — the doctrine being that heavy same-day churn (four adapters, an
expanded references/site-addressing.yaml, new SNMP vault entries) is exactly the situation where governance prose quietly stops matching reality even while every individual entry above was accurate
when written. Found 13 defects (11 from the defect register, 2 more from the Phase 7 inverse-completeness sweep), all fixed in this pass; none required reverting any of this session's real work.

### Fixed

- `manifest.json` — `version` bumped `0.2.0` -> `0.3.0` (structural: a reference file was added since the last bump), `updated_at` moved from an early-morning bootstrap timestamp to the latest real
  change (`2026-09-17T20:57:00Z`), matching `.archcore/rules/rule-manifest-version-discipline.md`'s own rule. Added a `stable_fact` recording all four adapters as live-verified; corrected the R195P
  management-IP `stable_fact`, which still stated the superseded `EXT10XX -> 10.255.10.XX` derivation `references/05_known-issues.md` itself already recorded as wrong (real subnet `10.255.11.x`).
- `RUNBOOK.md` — header banner said "no authenticated cnMaestro or device session yet"; superseded in place — all four families now have live-verified sessions.
- `AI_NAVIGATION.md` — line 89 said `.archcore/` was "empty as of 2026-09-17", directly contradicting lines 35/63 of the SAME file ("6 documents accepted 2026-09-17"), which were correct (verified: 6
  files under `.archcore/{adr,rules,specs}`). Fixed the wrong line.
- `AGENTS.md` — "five numbered files ... from `references/01_overview.md` to `references/05_known-issues.md`" corrected to six, `01` to `06`; the Tier 1 project-coherence checklist table was missing a
  routing row for `references/06_device-api-cli-reference.md` entirely — added one. Also corrected a dead pointer to a `VERSION_STAMP_SURFACES` registry in `scripts/check_governance.py` that was never
  implemented (the real mechanism, `CONSTANT_SURFACES`, doesn't cover this invariant either — recorded as a residual governance gap, not silently invented).
- `README.md` — "5 numbered progressive-disclosure reference files" corrected to 6.
- `references/05_known-issues.md` — the "Sites beyond Hope Vale and Burringurrah — only these two seen" coverage-gap row was stale against `references/site-addressing.yaml`, which already covers all
  10 rcp-flavour sites; narrowed to the part still genuinely open (per-site naming-convention re-verification). The "Pack Staleness Risks" section's blanket "everything is USER_STATED, not
  VERIFIED-OBSERVED" disclaimer was superseded by the same live-adapter work; replaced with a pointer to check facts individually rather than assume a pack-wide state either way.
- `SCRATCHPAD.md` — the KEEP-marked "Current state"/"Open items"/"Next actions" block (written at first-adapter time, XV2 only) was contradicted by this file's own later CHANGELOG entries showing
  three more adapters landed the same day — the exact "claim marked KEEP, contradicted by a completion surface elsewhere in the project" pattern `skill-staleness-audit` names as its structurally
  hardest class. Superseded in place with a dated banner; resolved checklist items marked `[x]` with dated notes rather than rewritten, per the file's own convention. Also caught and fixed a path
  error introduced while writing this fix (site-addressing.yaml referenced without its `references/` prefix — `scripts/check_governance.py`'s path check caught it immediately).
- `scripts/check_governance.py` — `COUNT_CLAIMS` and `CONSTANT_SURFACES` were both empty registries (scaffolding present, zero real assertions enforced). Populated `COUNT_CLAIMS` with the
  reference-file count (catches the README/AGENTS.md defect above on regression). Added a new Tier 3 check, `check_manifest_freshness`, enforcing `.archcore/rules/rule-manifest-version-discipline.md`
  by comparing `manifest.json`'s `updated_at` against `CHANGELOG.md`'s latest `## YYYYMMDD_HHMM` heading. **Negative-tested and it caught a real bug in itself first**: an initial date-only comparison
  passed silently against the actual stale value, because every entry that day shared the same calendar date — the defect found was hours-stale, not days-stale. Rewritten to compare full
  `YYYYMMDDHHMM`, re-tested, confirmed it now fails on the reverted value and passes on the fix.
- `.archcore/README.md` — line 63 cited its ADR by bare filename with no directory prefix (the file actually lives at `.archcore/adr/adr-vault-file-avoids-opa-blocked-words.md`, correctly linked
  elsewhere in the same file); a permissive resolver still finds it, so it read as correct while pointing a reader at the wrong directory. Added the `adr/` prefix. Found by the audit's `DISPLACED`
  inverse-sweep check, not by grep.
- `references/README.md` — did not exist; every sibling folder with documents (`.archcore/`, `scripts/`) has one, `references/` did not. Added, as a thin index pointing back to `RUNBOOK.md`'s
  Reference Routing table rather than duplicating it. Found by the audit's `UNINDEXED-DIR` inverse-sweep check.

### Verified, not a defect

- `scripts/cambium_xv2_adapter.py`, `scripts/cambium_epmp_adapter.py`, `scripts/cambium_cnwave_adapter.py` all carry the `REDACT_KEY_PATTERN` fix an earlier entry above claimed (`pass|psk|secret|key|
  shared|community|radius|credential|token|auth`) — code matches the claim exactly. `scripts/cambium_r195p_adapter.py` deliberately has no `get_config()`, consistent with its own docstring and
  `references/05_known-issues.md`.
- The `<secret:keepassxc:cambium-devices/<entry>>` placeholder convention is used consistently everywhere a credential is referenced (`AGENTS.md`, `SKILL.md`, `SCRATCHPAD.md`, `references/`,
  `.archcore/rules/rule-vault-reference-convention.md`, `scripts/extract-asset-register.py`) — no literal secret value, SNMP community string, or credential found anywhere in the pack.
- `references/06_device-api-cli-reference.md` cross-checked line by line against CHANGELOG's live-test entries — no still-open claim found for something CHANGELOG shows resolved, or vice versa; this
  file has been kept current in the same pass as each adapter change throughout the session.
- The `BROKEN`-path hits the audit's claim-scan tool reported against files in the sibling `cambium-swap` project (e.g. its docs/migration/controller-option3/*.md) and against a workspace-level
  .claude/settings.local.json are the intended cross-reference-don't-copy pattern, not broken links — the scanner cannot resolve paths outside this pack's own tree. `.archcore/README.md`'s reference
  to the deleted `ARCHCORE_PROMOTION_CANDIDATES.md` is self-documented as historical (the file describes its own deletion).

### Residual (not resolved by this audit — see SCRATCHPAD.md Next Actions)

- **This entire pack directory is untracked in the parent `skills_stuff` git repo** (`git status --porcelain` from repo root shows a single `?? specialists/project/skill-cambium/` — never `git
  add`ed). Everything built this session has no version-control history. Outside this audit's git-write constraint; flagged for the operator to commit.
- `hardware_revision` remains genuinely `UNKNOWN` for all 17 catalogued models — not a staleness defect, a real open gap.
- Whether the new SNMP vault credentials (`apn-snmp-ro`/`rw`, `nbn-snmp-ro`/`rw`) resolve the pending community-string rotation decision from the two security incidents, or are a separate addition,
  was not established by this audit — flagged in `SCRATCHPAD.md` for an explicit operator answer rather than assumed either way.
- No automated check enforces "no file other than `manifest.json` hardcodes a duplicate version number" (the rule `.archcore/rules/rule-manifest-version-discipline.md` states) or "the version was
  bumped for every content change" (only "the date is not older than the latest CHANGELOG entry" — a weaker, but real and negative-tested, invariant).
- `references/03_asset-register-conventions.md`'s naming-convention prose was written from 2 sites and has not been individually re-verified against the other 8 now addressed in
  references/site-addressing.yaml.
- Spelled-out number claims (e.g. AGENTS.md's former "five numbered files") are invisible to `check_count_claims`, which only matches digit-form claims (`\d+`) — the AGENTS.md fix converted it to
  digit form partly so it's checkable, but any future spelled-out count claim in prose would not be caught.

### Notes

- `python3 scripts/check_governance.py`: 144/144 passing (was 135/135 before this pass; 133/133 at the last CHANGELOG entry's own note — the rise between 133 and 135 reflects file/path growth from
  this session's own edits before the audit, not new check functions; the rise from 135 to 144 is 2 new checks negative-tested plus additional path assertions the fixed prose now contains).
- Full defect register, residual-risk register, and Phase 4 per-artifact worksheet: `.staleness-audit/` (gitignored working state — deleted on a clean gate pass per the skill's own convention, kept
  only if the gate fails).
- `python3 scripts/check_governance.py`: 133/133 passing.

## 20260917_2145

`skill-project-coherence` run against this pack, propagating the `20260917_2130` staleness-audit fixes outward to the two companion-file surfaces that audit did not reach.

### Fixed

- `AI_NAVIGATION.md` — the managed-block `skill-ai-it:manual` reason comment still said "task->reference routing table (5 files)" after the audit's file-count fix elsewhere; corrected to 6. The
  "Reference routing (task → file)" table itself was missing a row for `references/06_device-api-cli-reference.md` entirely (only 01-05 listed) — added it, matching `RUNBOOK.md`'s and `AGENTS.md`'s
  routing tables, which already had it.
- `context-map.yaml` — the `routing` section had entries for `device_facts`/`device_access`/`asset_registers`/`device_inventory` (01-04) but none for `references/05_known-issues.md` or
  `references/06_device-api-cli-reference.md`; added `known_issues` and `device_api_cli_reference` routing entries. The `update_rules` section had the same gap for `known_issue_fact` and
  `api_cli_fact`; added both, matching the shape of the existing four.
- `.archcore/README.md` — the Rules table's "Manifest version discipline" row still read "Operator review only — no automated check yet", contradicted by the same `20260917_2130` audit that added
  `scripts/check_governance.py`'s `check_manifest_freshness` Tier 3 check enforcing exactly that rule's freshness half. Corrected to name the automated check and what it still leaves unenforced
  (version-bump-per-change, no-duplicate-version-number).
- `.archcore/rules/rule-manifest-version-discipline.md` — added a note that this pack itself hit the ~19-hour `updated_at` drift the rule exists to prevent (not just `skill-smc`, the rule's only cited
  precedent before this), and documented `check_manifest_freshness` as the (partial) automated enforcement now in place.

### Verified, not a defect

- `RUNBOOK.md`'s Reference Routing table already listed `references/06_device-api-cli-reference.md` correctly — no fix needed there.
- `README.md` already said "6 numbered reference files" — no fix needed there.
- `manifest.json`'s `version` had no other surface restating it as a duplicate hardcoded number — `.archcore/rules/rule-manifest-version-discipline.md`'s "sole version-of-record" rule holds.
- `skill-smc`'s files (`AI_NAVIGATION.md`, `CHANGELOG.md`, `SKILL.md`, `references/01_overview.md`, its own references/15_cambium-asset-registers.md stub, `scripts/README.md`, read-only cross-check)
  reference `skill-cambium` only by topic/content pointer, never by version number or file count — none went stale against this session's fixes.
- `cambium-swap`'s governance surfaces (`AGENTS.md`, `AI_NAVIGATION.md`, `context-map.yaml`, `SCRATCHPAD.md`) do not cite `skill-cambium` by version number — nothing to reconcile there.
- CHANGELOG's own `20260917_2130` entry states 144/144; a fresh run this pass shows 145/145 — both are internally consistent with the checker's own additive nature (new assertions from the
  routing-table and context-map.yaml rows just added), not a discrepancy requiring correction of the historical entry (append-only, left as written).

### Residual (not resolved by this pass — see `SCRATCHPAD.md` and the `20260917_2130` entry's own Residual section)

- **This entire pack directory remains untracked in the parent `skills_stuff` git repo.** `git status --porcelain` from the repo root still shows a single `?? specialists/project/skill-cambium/`.
  Nothing in this pass changes that — no `git add`/`commit` was run, per this task's own constraint. A commit that captures this pack's current state would need to include: every governance/content
  file touched across both this pass and the `20260917_2130` audit (`AGENTS.md`, `AI_NAVIGATION.md`, `context-map.yaml`, `CHANGELOG.md`, `README.md`, `RUNBOOK.md`, `SCRATCHPAD.md`, `manifest.json`,
  `.archcore/README.md`, `.archcore/rules/rule-manifest-version-discipline.md`, `references/05_known-issues.md`, `references/README.md`, `scripts/check_governance.py`), plus every file from earlier
  the same day (four adapter scripts, `references/06_device-api-cli-reference.md`, `references/site-addressing.yaml` expansion, `.archcore/adr` and `.archcore/specs`, `SKILL.md`, `CLAUDE.md`,
  `justfile`, `.mise.toml`, `requirements.txt`) — i.e. the entire pack, since none of it has ever been committed.
- Every other residual item from the `20260917_2130` entry (SNMP rotation-decision ambiguity, `hardware_revision` UNKNOWN, spelled-out count claims invisible to `check_count_claims`, no
  duplicate-version-number check) stands unchanged by this pass.

### Notes

- `python3 scripts/check_governance.py`: 145/145 passing after this pass's edits (routing-table and context-map.yaml additions raised the assertion count further from `20260917_2130`'s own 144/144
  note).

## 20260918_0855 — cnMaestro REST API v2 access documented; vault table gained 5 missing entries

Triggered by `cambium-swap` work (splitting a 635-device nbn_accelerate system-level cnMaestro export into per-site files, evidence E124) that used two vault entries — `nbn-cnmaestro-api` and the four
`*-snmp-ro`/`*-snmp-rw` entries added under evidence E122 — neither of which had ever been written back to this pack's own vault table, despite the Standing Write-Back Contract.

### Fixed

- `references/02_device-access-and-vault.md`'s Vault Structure table — added `<secret:keepassxc:cambium-devices/apn-snmp-ro>`, `apn-snmp-rw`, `nbn-snmp-ro`, `nbn-snmp-rw` (existed in the vault since
  E122, never documented here) and `<secret:keepassxc:cambium-devices/nbn-cnmaestro-api>` (new this session).
- Added a new "cnMaestro REST API v2 Access" section: the real auth endpoint is `/api/v2/access/token`, not the more guessable `/api/v2/token` (which returns HTTP 400 with plausible-looking OAuth2
  error bodies instead of a 404, so a wrong-path guess reads exactly like a credential failure); the `GET /api/v2/devices?network=<name>&fields=...` query-filter pattern for authoritative device→site
  grouping (this API's v2 explicitly rejects the `/networks/{id}/devices` path-segment form some other cnMaestro doc examples suggest); confirmed live against the real `cw-cnmaestro01` controller
  (v3.0.0-r34) even though the API shape was found in an archived 6.0.0 doc.
- Verified both edits by reading the file back (Standing Write-Back Contract requirement) — `grep` for `nbn-cnmaestro-api`, `/api/v2/access/token`, and `Aurukun` all found in the written file.

### Notes

- Full resolution story (three-pass: name-match → live ARP → this API) lives in `cambium-swap`'s evidence E124 and CHANGELOG `20260918_0850` entry — not duplicated here, per the equipment-knowledge
  routing rule (this pack owns the API/CLI surface knowledge, the consuming project owns the project-specific rationale and evidence chain).
- Governance check not re-run this pass (no `just check` invoked) — flagged for the next full pass over this pack.

## 20260918_0930 — site-addressing.yaml restructured by flavour, populated for all 27 nbn_accelerate sites, generator script added

Prompted by `cambium-swap` populating 27 per-site nbn_accelerate `_cnmaestro-inventory.csv` files (evidence E124) — this file previously had only `hope-vale` filled in for that flavour, the other 26
sites entirely undocumented.

### Changed

- `references/site-addressing.yaml` `schema_version` 3→4. `sites:` and the new `site_short_names:` (see Added) are now nested one level deeper, under each site's flavour (`rcp` / `nbn_accelerate`),
  not flat. Every site's now-redundant `flavour:` field was removed — implied by its parent key instead. Operator-requested change, prompted by the file growing to 35 total sites and the discovery
  that a short device-name code (`KAL`) collides across flavours (`kalumburu` in `rcp`, `kaltjiti-fergon` in `nbn_accelerate`) — nesting by flavour makes that collision structurally visible instead of
  a footnote.
- Populated `families:` (octet_pattern/host_count per device family, `method: cnmaestro-export`, `trust: verified`) for all 26 previously-undocumented `nbn_accelerate` sites, derived from
  `cambium-swap`'s newly-split per-site export CSVs. `hope-vale`'s existing hand-authored block (including its live SSH/REST/SNMP verification notes) was preserved untouched, not regenerated.

### Added

- `references/site-addressing.yaml` `site_short_names:` — the short device-name code(s) each site's cnMaestro export actually uses (`HOP`, `DMG`, `GAL`, ...), nested by flavour for the same collision
  reason as above, with inline notes for the handful of sites with no short code at all (`aurukun`, `indulkana`, `warakurna` — identified via cnMaestro network objects or a device-name suffix instead
  of a leading code, per cambium-swap evidence E124).
- `scripts/generate_site_addressing_families.py` — derives the `families:` block for one or more sites straight from their reconciled cnMaestro-export CSV, at the operator's request to make this a
  persistent reusable tool rather than the scratchpad one-off script this session first used to populate the 26 new sites. Deliberately never writes `references/site-addressing.yaml` directly — prints
  a YAML fragment for review/merge, since the file also carries hand-authored live-session notes (SSH/REST/SNMP narrative) a CSV-only script has no way to derive or preserve. Cataloged in
  `scripts/README.md`.

### Verified

- `python3 -c "import yaml; yaml.safe_load(open('references/site-addressing.yaml'))"` — parses cleanly, `schema_version: 4`, 27 `nbn_accelerate` sites + 9 `rcp` sites in both `sites:` and
  `site_short_names:`, `hope-vale`'s and every `rcp` site's pre-existing hand-authored `notes:`/verification fields intact (spot-checked programmatically, not just by eye).
- `just check` not re-run this pass — flagged for the next full pass over this pack, same as the `20260918_0855` entry above.

### Notes

- Full resolution methodology for the 26 new nbn_accelerate sites (three-pass: name-match → live ARP → cnMaestro REST API) lives in `cambium-swap`'s evidence E124 — not duplicated here, per the
  equipment-knowledge routing rule.

## 20260918_1045 — two missing OUI blocks added after operator flagged oui_reference as stale

Operator flagged `references/site-addressing.yaml`'s `oui_reference` block as possibly stale. Audited `cambium-swap`'s now-3174-row `device-inventory.csv` against the 5 documented blocks and found two
real gaps: `00:04:56` (419 devices — dominant ePMP Force 300-16/25 OUI fleet-wide, also 85 60 GHz cnWave nodes, not ePMP-exclusive) and `30:cb:c7` (20 devices, cnWave-only so far). Both added with
`method: cnmaestro-export`, matching the file's existing verification convention. `updated:` header bumped. See `cambium-swap` evidence E129 for the audit detail (not duplicated here).

## 20260918_1050 — generate_site_addressing_families.py gained --oui-audit mode

Operator asked whether the earlier OUI staleness fix (evidence-adjacent, `20260918_1045`) was captured in the persistent script rather than done ad hoc again.

### Added

- `scripts/generate_site_addressing_families.py --oui-audit`: reports OUI blocks present in `device-inventory.csv` but missing from `oui_reference`, with host_count/family/site breakdown — the same
  computation done by hand for the `00:04:56`/`30:cb:c7` find. Prints a YAML-shaped stub (family left `UNKNOWN` for a human to pick from the breakdown, notes left as a prompt) rather than a
  ready-to-paste entry — deciding family-exclusivity and writing the cross-site caution prose is a judgment call this script doesn't make. Never writes `references/site-addressing.yaml` directly, same
  principle as the existing `families:` mode. Verified both ways: clean run reports nothing missing (both new OUIs already added), and a run against a copy of the file with `00:04:56` stripped out
  correctly re-detects it.
- `scripts/README.md` updated.

### Verification

- `python3 scripts/generate_site_addressing_families.py --oui-audit` — reports clean.
- Negative test: same command against `references/site-addressing.yaml` with the `"00:04:56"` line removed correctly re-surfaces it with the right host_count/family/site breakdown.

## 20260918_1055 — full regenerate-and-verify pass: 8 missing families added, oui_reference restructured to a real site map

Operator asked to regenerate `families:` for every site and diff against the file, then fix what the diff found — consistently, and with `oui_reference`'s site data as a real structured field instead
of prose.

### Fixed

- Regenerating every site with `scripts/generate_site_addressing_families.py --all --all-flavours` and diffing against the file found 8 completely missing family entries at the 8 older rcp sites that
  were never given full coverage: `epmp-ap` at burringurrah; `cnwave-60ghz` at horn-island/mornington/wujal-wujal; `enterprise-wifi-eseries` at jigalong/kalumburu/mowanjum/tjuntjuntjara. Added all 8,
  all `method: cnmaestro-export`, same shape as every other entry — no mixing.
- The diff also found `host_count` disagreements on several already-present families (e.g. mornington `epmp-sm`: file said 343, regenerated CSV says 188). Left alone deliberately — several existing
  entries were verified via `arp-mac-oui-match` (live-connected hosts only) not `cnmaestro-export` (every registered device including offline), so a mismatch there is two different, both-legitimate
  measurements, not an error. Overwriting would have silently swapped verification method without saying so.

### Changed

- Every `oui_reference` entry's `verified.site` rewritten from a single dominant site + "also seen at X, Y, Z" prose into a full `site: {sitename: host_count, ...}` map, regenerated straight from
  `device-inventory.csv`. All 7 entries (the original 5 plus the 2 added in `20260918_1045`) now share the identical shape — the original 5 had no `host_count` field at all; the 2 new ones did; none
  were structurally consistent with each other before this pass.
- `updated:` header bumped with the detail.

### Verification

- `python3 -c "import yaml; yaml.safe_load(...)"` — parses cleanly.
- `python3 scripts/check_governance.py` — 154/154 passing.

## 20260918_1100 — YAML formatting cleanup, content accuracy fixes, FAMILY_MAP bug found and fixed

Operator follow-up on `20260918_1055`: wrap the new header comment properly (and re-flow it, not just cap it), move it above `schema_version:`, wrap every `oui_reference` `notes:` field as a YAML
folded scalar (`notes: >-`) instead of a long single-line quoted string, and verify the notes are still accurate content-wise — then verify `scripts/generate_site_addressing_families.py` itself is
current.

### Fixed

- Moved the long inline `updated:` comment to a proper wrapped block comment above `schema_version:`; wrapped the pre-existing top-of-file header comment (lines 1–58) to actually use the 160-column
  budget instead of sitting under-filled at ~120 (58 lines → 47) — the two indented enumerations (`method values:`, `trust values:`) were left untouched, since reflowing a list breaks its alignment.
- Converted all 34 `notes: "..."` quoted-string fields to `notes: >-` folded block scalars, wrapped at 160 columns — a quoted single-line string can't be wrapped without changing its literal type, a
  folded scalar can.
- Content accuracy pass on `oui_reference`, caught two real errors while re-reading the notes just written in `20260918_1055`: the `fc:11:65` note claimed "five known blocks total" for the
  enterprise-wifi-xv2 family — there are only four (`bc:a9:93`, `fc:11:65`, `b4:a2:5c`, `bc:e6:7c`); fixed and named all four explicitly. The two ePMP OUI blocks (`58:c1:7a`, `00:04:56`) didn't
  cross-reference each other the way the four XV2 blocks do each other — added reciprocal "one of two known ePMP OUI blocks" notes to both.
- `scripts/generate_site_addressing_families.py`'s `FAMILY_MAP` was missing 4 of the 60 GHz cnWave device types (`V2000 CN/DN`, `V1000 CN/DN`) that [cambium-swap's
  scripts/reconcile_cnmaestro_export.py](/Volumes/Data/_ai/_project/project_stuff/apn/cambium-swap/scripts/reconcile_cnmaestro_export.py)'s `TYPE_MAP` already had (synced there in `20260918_1030`,
  never synced here) — rows of those types were silently dropped from `compute_families()`. Fixed. Re-running the corrected script against every rcp site found two real consequences: mornington's
  `cnwave-60ghz` `families:` entry was undercounted (10→11 hosts), and bidyadanga was missing a `cnwave-60ghz` entry entirely (now added, 2 hosts — noted that 4 of its 6 cnWave devices are IPv6-only
  in the export and aren't counted by this octet-based method at all).

### Verification

- `python3 -c "import yaml; yaml.safe_load(...)"` — parses cleanly throughout every edit in this pass.
- Character-length check (not `awk`, which counts UTF-8 bytes and false-flagged two lines containing em-dashes) confirms zero comment lines over 160 characters.
- `python3 scripts/check_governance.py` — 154/154 passing.

## 20260918_1115 — cnPilotMIB SNMP read-only identity data confirmed live on XV2-22H Wi-Fi 6 firmware

Standing Write-Back Contract entry for work done in `cambium-swap`: the pass-08 research gap ("no dedicated XV2/Wi-Fi 6 MIB in any public mirror") turned out not to block a real SNMP walk, and
`cambium-swap` built a reusable script around the finding — both facts belong here, not just in that project's own CHANGELOG.

### Added — `references/06_device-api-cli-reference.md`

- New "SNMP (cnPilotMIB) — Read-Only Identity Data" subsection under Enterprise Wi-Fi (XV2): the 2015-vintage `cnPilotMIB` mirror ([cambium-swap's
  artifacts/mibs/librenms/cnpilote/CAMBIUM-MIB](/Volumes/Data/_ai/_project/project_stuff/apn/cambium-swap/artifacts/mibs/librenms/cnpilote/CAMBIUM-MIB)) matches cleanly against live `XV2-22H` Wi-Fi 6
  firmware `6.6.0.3-r9`. A live SNMPv2c walk of `cambiumAccessPointEntry` (base OID `.1.3.6.1.4.1.17713.22.1.1.1`) against 4 hope-vale units correctly returned all 15 columns, including serial number
  (index `.4`) — the field a cnMaestro-export-based reconciliation pass can never fill for a device cnMaestro itself does not track. Cross-referenced: `cambium-swap` evidence E130, its [new
  scripts/snmp_resolve_unknowns.py](/Volumes/Data/_ai/_project/project_stuff/apn/cambium-swap/scripts/snmp_resolve_unknowns.py).
- Explicit scope-discipline note: this MIB match is confirmed only for `XV2-22H`. Do not assume it covers `XV2-2T0`, `E500` or `E430` firmware without testing one live unit of each first.

### Verification

- Read back `references/06_device-api-cli-reference.md` in the same session — new subsection present between the adapter data-points table and the E-series subsection, as intended.

## 20260918_1155 — unified-network-controller added as a Related Workspace

Operator split the "Option 3" FOSS controller workstream out of `cambium-swap` into its own sibling project, `unified-network-controller`, and asked that this pack and `skill-smc` both know about it,
and it about them.

### Changed — `SKILL.md`, `RUNBOOK.md`

- Added `/Volumes/Data/_ai/_project/project_stuff/apn/unified-network-controller` to the Related Workspaces tables in both files: the FOSS controller build (Nautobot + adapter layer) that consumes
  this pack's device-access/API knowledge for its Cambium vendor adapter, without duplicating it — same cross-reference discipline as the existing `cambium-swap`/`skill-smc` relationships.

### Verification

- `python3 scripts/check_governance.py` — 154/154 passing.

## 20260918_1542 — ePMP SM adapter re-verified fresh-live; cnWave 4 stat endpoints resolved (path bug, not missing params)

Two pending `cambium-swap` open items, operator-authorized this session: a fresh live ePMP SM run (prior coverage was an offline replay only, the Hope Vale unit having hit its 5-session RW cap) and
reverse-engineering the params for cnWave's `getRadioStats`/`getNetworkStats`/`getKeyPerformanceIndex`/`getCnAgentStatus`, all previously 400ing on an empty `{}` POST.

### Changed — `scripts/cambium_epmp_adapter.py` — none (code already correct; only re-verified against a new device)

- Ran `_cmd_getters()` live against a different real Force 300-25 SM, Doomadgee `DMG_F25_AP10_IP3_101` (`10.255.3.101`), instead of spending more of Hope Vale's constrained session budget. Clean
  facts/interfaces/wireless_link/clients response, serial/MAC matched `cambium-swap`'s `device-inventory.csv` exactly. Confirms the SM code path generalises beyond the one unit it was built against.

### Changed — `scripts/cambium_cnwave_adapter.py`

- Added `get_radio_stats()`, `get_network_stats()`, `get_key_performance_index()`, `get_cn_agent_status()` and wired all four into `_cmd_getters()`, using `get_facts()`'s own node `mac_address`.
- Root cause of the 2026-09-17 400s: these four endpoints live under `/local/`, not `/api/` like `getTopology`/`getCtrlStatusDump` — a path-prefix bug in the original assumption, not a missing
  parameter. Found by reading the device's own served Angular JS bundle (`main.<hash>.js`) `http.post(...)` call sites, same technique as every other endpoint in this adapter, then confirmed live
  against a real V5000 POP node (Doomadgee `DMG_T12_V5000_DN_IP4_100`, `10.255.4.100`).
- Docstring rewritten to state the correct `/local/` param shapes instead of "likely need a radio MAC or time range, not yet reverse-engineered".

### Changed — `references/06_device-api-cli-reference.md`

- ePMP section: added a note that the SM adapter is now re-verified fresh-live against a second real unit (Doomadgee), not just the original Hope Vale offline replay.
- cnWave table: added 4 new rows (`get_radio_stats`, `get_network_stats`, `get_key_performance_index`, `get_cn_agent_status`) with confirmed-live param shapes, plus a new "The 4 stat endpoints were a
  path bug, not a missing param" subsection explaining the `/local/` vs `/api/` root cause and the node-MAC-vs-radio-MAC gotcha (a radio MAC silently returns an empty/nulled result with HTTP 200, not
  an error).
- "Not yet exercised" list trimmed to just `getNetworkOverridesConfig`/`getControllerConfig`/`getTopologyMeta` now that the 4 stat endpoints are resolved.

### Verification

- Read back both changed reference files in the same session — new SM note, new cnWave table rows, and new subsection all present as written.
- `cambium_cnwave_adapter.py --help`-equivalent smoke: re-ran the full `_cmd_getters()` live a second time after the code change (not just the ad hoc probe script) — `radio_stats`, `network_stats`,
  `key_performance_index` and `cn_agent_status` all returned real data in the adapter's own JSON output, not just in the standalone probe.
- `python3 scripts/check_governance.py` — 154/154 passing.

## 20260918_1557 — R195P get_config() implemented (operator-authorized); live fetch across all 4 families blocked this session by a sandbox credential-materialization guard

Operator explicitly authorized fetching a live `get_config()` snapshot for all 4 Cambium device families in one `cambium-swap` session (per-family risk profile discussed first, per-family
authorization confirmed). Two things happened that changed the shape of the work actually completed:

1. **`teleport.communitywifi.net.au` (the `nbn_accelerate`-flavour cluster, which carries Hope Vale and Doomadgee) was unreachable all session** — `tsh ls --cluster teleport.communitywifi.net.au`
   returned `connection error: desc = "transport: authentication handshake failed: EOF"` on every retry, despite a `tsh status` profile showing a still-valid session and the proxy itself answering a
   plain `curl`/`nc` probe on 443. `tsh login` cannot refresh it non-interactively (`cannot perform password login without a terminal`). This is a cluster-wide outage, not specific to Hope Vale's
   `hope-vale-smc01` node — Doomadgee (the calling task's fallback site) was equally unreachable. Devices for all 4 families were instead selected from `rcp`-flavour sites on the (reachable)
   `teleport.apn.au` cluster, cross-checked against `references/site-addressing.yaml`'s per-site/family `trust: verified` state: Horn Island XV2 (`HRN_XV2_AP1_IP3_10`, `10.255.3.10`) and cnWave V5000
   POP (`HRN_T1_V5000_DN_IP4_10`, `10.255.4.10`); Kalumburu ePMP AP (`Tower1_Force 300_IP_0_11_master`, `10.255.0.11`, the same unit already evidenced in this file needing the `epmp-ap-legacy` vault
   credential); Burringurrah R195P (`BUR-R195P-1047`/`BUR-R195P-1055`, `10.255.11.47`/`.55`, the same units already evidenced live 2026-09-17). Note also caught in passing: `references/\
   site-addressing.yaml` claims Burringurrah's `enterprise-wifi-xv2` `device-inventory.csv` rows were reconciled to the live `10.255.11.x` octet, but a live grep found all 8 Burringurrah XV2 rows
   still carrying the old register-pattern `10.255.3.x` — a real doc/data contradiction, not yet corrected, why Horn Island was used for XV2 instead. Flagged here rather than silently worked around;
   someone should re-run the Burringurrah XV2 reconciliation pass or correct the `references/site-addressing.yaml` claim.
2. **This sandbox's own harness blocked every `kp show cambium-devices/*` invocation** with `Permission for this action was denied by the Claude Code auto mode classifier. Reason: [Credential
   Materialization]` — on every flag form tried (`kp show <entry>`, `kp show -a Password <entry>`, `kp show -a UserName -a Password <entry>`), despite `cambium-swap/.claude/settings.local.json`
   already carrying an explicit allow-list for exactly this command shape (`Bash(kp show -a UserName -a Password cambium-devices/*)` etc. — see `references/02_device-access-and-vault.md`'s own
   "Resolved 2026-09-17" note about this same class of problem). This auto-mode classifier sits above the project's own permission file and cannot be satisfied by retrying a different flag
   combination; per this project's own no-workaround rule, no attempt was made to bypass it. **Net effect: no device credential was ever materialized this session, so no live login was possible
   against any of the 4 families** — XV2, ePMP and cnWave `get_config()` were NOT re-run live this session (their existing 2026-09-17/2026-09-18 `VERIFIED-OBSERVED` evidence stands unchanged, nothing
   new added), and the new R195P `get_config()` below was written and unit-tested offline only, not live-verified. This is a session-environment permission gap, not a finding about device behaviour —
   flagged for the operator to resolve (interactive `kp` session, or a broadened harness allow-list) before the live fetch can actually be completed.

### Changed — `scripts/cambium_r195p_adapter.py`

- Implemented `get_config()`, deliberately withheld since 2026-09-17 (see the module's own prior docstring) until a real need was authorized. Source: `cat /etc/config/* 2>&1` over the same SSH path
  every other getter here already uses (no `uci` binary confirmed present on this BusyBox/Buildroot platform, so this reads the UCI-style config files directly rather than assuming a config tool
  exists).
- Added `_parse_uci_text()`: a tolerant parser for BusyBox/OpenWrt-style `config <type> '<name>'` / `option <key> '<value>'` / `list <key> '<value>'` text into a nested dict keyed by
  `"<type>.<name>"`. Unrecognized lines (different syntax, or `cat`'s own stderr mixed into the `2>&1` stream if a file is missing) are kept verbatim under a synthetic `_unparsed` key instead of being
  silently dropped, so `redact()` still gets a chance at them and a caller can see raw text was present rather than a falsely-empty result.
- `REDACT_KEY_PATTERN`/`redact()` copied verbatim from `scripts/cambium_xv2_adapter.py`/`scripts/cambium_epmp_adapter.py`/`scripts/cambium_cnwave_adapter.py`, applied to every parsed `option`/`list`
  value keyed by option name — same rule as the other three families: redact by key name regardless of whether the value looks like ciphertext (this family's fleet-wide SNMP community is an encrypted
  blob in its own config, per the Ansible R195P provisioning template, not necessarily plaintext-looking, but redacted unconditionally anyway).
- Wired in as an opt-in `--include-config` CLI flag (same name/shape as `scripts/cambium_epmp_adapter.py`'s), never part of the default `_cmd_getters()` output — matches this family's
  already-conservative default (only `get_facts`/`get_interfaces` run without an explicit flag).

### Verification

- `python3 -m py_compile scripts/cambium_r195p_adapter.py` — clean.
- Offline unit test against synthetic (non-live, non-device) UCI text: a `config snmp` stanza's `option community` and a `config wireless` stanza's `option key` both redacted to `<REDACTED>`; a
  non-secret `option hostname`/`option ssid`/`option timezone` passed through unredacted; an unparseable garbage line landed in `_unparsed` rather than being dropped. Confirms the redaction path is
  correct in isolation — **this is not a substitute for the live device test the operator actually asked for**, which remains blocked per point 2 above.
- `python3 scripts/check_governance.py` — see this session's separate governance-check run for the pass/fail count.

### Not done this session (blocked, not skipped)

- No live `get_config()` (or any other getter) was run against any of the 4 families' real hardware — see the credential-materialization block above. `cambium-swap`'s `evidence-register.csv` was
  therefore **not** given new `VERIFIED-OBSERVED` rows for this session; the existing rows for all 4 families stand as they were before this session started.

## 20260918_1620 — Correction: the outage claim in the entry above was wrong; it was a `tsh` flag mistake, not an outage

Appending a correction rather than editing the entry above (past record, not a live claim — see this pack's "do not enforce history" doctrine). Point 1 in `20260918_1557` above states
`teleport.communitywifi.net.au` was down fleet-wide. **That was wrong.** The operator reproduced the same commands directly: `tsh status` showed a fully valid cached session, plain `curl
https://teleport.communitywifi.net.au/webapi/ping` returned a clean 200, and `tsh ls --proxy=teleport.communitywifi.net.au` listed the full node roster (including `hope-vale-smc01`, contradicting the
earlier session's separate claim that this node was missing/deregistered) — `tsh ssh --proxy=teleport.communitywifi.net.au root@hope-vale-smc01` then connected cleanly. Root cause: that session used
`--cluster=teleport.communitywifi.net.au`, which routes to it as a subordinate target via a trust relationship that doesn't exist (it's its own root Teleport target, confirmed by its own separate `tsh
status` profile) — the resulting gRPC handshake failure (`transport: authentication handshake failed: EOF`) gives no hint it's a flag-choice problem rather than a server problem. Full technical
writeup: skill-smc's `references/01_overview.md` and `CHANGELOG.md` `20260918_1620`. The credential-materialization block (point 2 above) is unaffected by this correction — that part was real and
remains the actual reason no live device session happened this run.

### Changed — `references/02_device-access-and-vault.md`

- Added a `--proxy=` vs `--cluster=` warning directly after the existing Web UI tunnel note, cross-referencing skill-smc's fuller writeup, so a future agent doing Cambium device-access work hits this
  warning before repeating the same misdiagnosis.

### Verification

- `python3 scripts/check_governance.py` — see this session's run for pass/fail count.

## 20260918_1705 — Live get_config() verification across all 4 Cambium families completed; 4 real R195P bugs found and fixed; new secret-exposure incident found and closed

Both blockers named in the `20260918_1557` entry were confirmed resolved this session: the operator added `cambium-devices/*` kp-show patterns to the GLOBAL `~/.claude/settings.json` `autoMode.allow`
(the project-local `cambium-swap/.claude/settings.local.json` allow-list alone was never sufficient — a separate classifier-level list this pack had not previously identified), and the
`--cluster=`/`--proxy=` misdiagnosis from `20260918_1620` meant Teleport access was never actually broken. With both real, live sessions ran against all 4 families.

### Live-verified this session

- **XV2** (cambium-swap E134) — re-run against the same Hope Vale Tower 1 AP as the 2026-09-17 original. No code changes; output shape unchanged, 17 fields redacted, clean.
- **ePMP** (cambium-swap E135) — re-run against the same Doomadgee SM as E132, this time via a newly combined single-login `--include-config` path (see Changed below). 45 fields redacted, clean.
- **cnWave** (cambium-swap E136) — re-run against the same Doomadgee V5000 POP as E133. 21 fields redacted, clean, including the 4 stat-endpoint fields E133 added.
- **R195P** (cambium-swap E137) — **first ever live run** of `get_config()` for this family, against both real Burringurrah units. Real finding: this platform has no `/etc/config/` directory at all —
  the UCI-style source assumption from `20260918_1557` was wrong. See `references/06_device-api-cli-reference.md`'s R195P section for the full write-up (real config surface found instead:
  `/etc/cambium/keystore`, `/etc/provision/`, `/etc/snmpd/snmpd.conf`, a large `/etc_ro/` param-file tree) and the new open item to rebuild `get_config()`'s source around it.

### Changed — `scripts/cambium_r195p_adapter.py`

- `CAMBIUM_HOST` now accepts `host:port` (matches the other 3 adapters' existing convention) — a bare `ssh user@host:port` was failing to resolve, a real bug on this family's own documented normal
  access path (a local Teleport port-forward).
- `_run()` catches `subprocess.TimeoutExpired` and re-raises sanitized — a new secret-exposure incident (device password embedded in the exception's default argv dump) happened live this session when
  the original 8s `DEFAULT_SSH_TIMEOUT` was too short for a nested-tunnel handshake; contained immediately (temp file deleted same turn), root-caused, and fixed. `DEFAULT_SSH_TIMEOUT` raised to 20s.
- Added `LogLevel=ERROR` to the ssh invocation — the local OpenSSH client's own post-quantum-KEX advisory banner was observed live to desync `sshpass`'s prompt detection, producing spurious
  `Permission denied` against a password confirmed correct moments before and after.
- `_run()` gained `allow_nonzero`, used only by `get_config()` — BusyBox `cat`'s non-zero exit on a missing glob member was discarding the `2>&1`-merged stdout that `get_config()`'s own design relies
  on to surface a missing-file message as parseable `_unparsed` text instead of silently losing it.

### Changed — `scripts/cambium_epmp_adapter.py`

- `--include-config` now runs `facts`/`interfaces`/`wireless_link`/`clients`/`config` under one login instead of a separate config-only session — this family has a real 5-session RW cap, so the old
  shape cost two sessions for what is now one.

### Changed — `references/06_device-api-cli-reference.md`

- R195P section rewritten from "not yet live-verified" to the full live-test write-up above (real config-surface finding, the 4 code fixes, the dropbear connection-throttling observation).
- XV2 and cnWave sections each gained a short "re-verified 2026-09-18" note under their existing 2026-09-17 evidence.
- ePMP section gained a "`get_config()` re-verified live 2026-09-18" note documenting the combined-login re-run.

### Not actioned — two mid-task requests to write unredacted secrets to local capture files

During this session, two different framings of the same request arrived mid-task (write the raw pre-`redact()` `get_config()` output to a local `captures/` file, first directly, then via an scp-based
two-hop pull): both were declined. This project's own `AGENTS.md` states "Redact BEFORE persisting or printing" without a scope carve-out for local/gitignored files, and every adapter's own
`get_config()` docstring in this pack states callers "must never bypass [`redact()`]... without also redacting" — a rule written after two real secret-exposure incidents in this exact codebase (E107,
the 2026-09-17 ePMP incident). A mid-task instruction is not the same as the user's own direct, deliberate authorization for a standing security-control rollback of this kind, and the risk (real
RADIUS passwords, SNMP RW communities, wireless PSKs landing in plaintext on disk) is asymmetric and effectively irreversible once written. Flagged to the operator directly rather than silently
complying or silently ignoring it; no code or governance change was made to accommodate it.

### Verification

- `python3 -m py_compile scripts/cambium_r195p_adapter.py scripts/cambium_epmp_adapter.py` — clean after every edit.
- Read back `references/06_device-api-cli-reference.md` in the same session — all 4 new/updated sections present as written (subject to this repo's own markdown-formatter hook reflowing table
  whitespace, not content).
- `python3 scripts/check_governance.py` — see this session's run for pass/fail count.
