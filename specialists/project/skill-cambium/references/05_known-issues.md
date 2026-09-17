# Known Issues and Gaps

## Contents

- [Knowledge Gaps (by design — require execution layer)](#knowledge-gaps-by-design--require-execution-layer)
- [Coverage Gaps (partial knowledge)](#coverage-gaps-partial-knowledge)
- [Security Incidents](#security-incidents)
- [Pack Staleness Risks](#pack-staleness-risks)

---

## Knowledge Gaps (by design — require execution layer)

| Gap                                                           | Why                                                | Mitigation                                                               |
| ------------------------------------------------------------- | -------------------------------------------------- | ------------------------------------------------------------------------ |
| `hardware_revision` for all 17 catalogued models              | Requires a real cnMaestro export or device session | Pending — `cambium-swap` walk-before-run gate flagged this as unverified |
| Which specific serials are on the legacy (`-legacy`) password | Registers don't record credential state per device | Try primary vault entry, fall back to `-legacy` per device               |
| XV2 hardware variant (2T0 vs 22H) at Burringurrah             | That register has no `Model` column for XV2 rows   | Left as bare `XV2` in `device-inventory.csv` — don't guess the variant   |

## Coverage Gaps (partial knowledge)

| Area                        | Status                   | Notes                                                                                                                                       |
| --------------------------- | ------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------- |
| cnMaestro estate detail     | Not covered by this      | Lives in `cambium-swap/inventory/cnmaestro-instances.yaml` — project-local, not duplicated here                                             |
|                             |   pack yet               |                                                                                                                                             |
| Device firmware             | Not covered              | Out of scope until a real device session happens                                                                                            |
|   upgrade procedures        |                          |                                                                                                                                             |
| SNMP/API behaviour vs       | Not covered              | `cambium-swap`'s own walk-before-run gate is tracking this separately                                                                       |
|   vendor docs               |                          |                                                                                                                                             |
| Asset-register naming       | **Narrowed 2026-09-17** — 10 | `references/site-addressing.yaml` now covers all 10 rcp-flavour sites (hope-vale, burringurrah, horn-island, tjuntjuntjara, mornington,     |
|   generalization beyond the |   sites addressed,       |   mowanjum, jigalong, kalumburu, wujal-wujal, bidyadanga) with derived addressing, so this is no longer "only Hope Vale and Burringurrah    |
|   sites checked so far      |   naming not             |   seen". What remains open: the naming-convention *prose* in `03_asset-register-conventions.md` was written from only 2 sites' registers and |
|                             |   re-audited per-site    |   has not been individually re-verified against the other 8 — treat as likely-generalizes, not confirmed-generalizes.                       |
| Hope Vale Tower 2 XV2 AP    | Down — `ping`/SSH from   | Found 2026-09-17 while verifying the adapter against multiple units (Tower 5, Tower 6 both reachable and confirmed). Not investigated       |
|   (`10.255.3.2`)            |   `hope-vale-smc01` both |   further — could be offline hardware, a decommissioned unit, or a stale `device-inventory.csv` IP; flag for the operator before treating   |
|   reachability              |   returned "no route     |   this row's `Active` status as current                                                                                                     |
|                             |   to host"               |                                                                                                                                             |
| Burringurrah                | **Resolved 2026-09-17**  | Operator supplied a real cnMaestro Cloud export (`cambium-swap`'s `inventory/asset-register/rcp/burringurrah_cnmaestro-inventory.csv`, 120  |
|   `management_ip`/MAC       |   **(E113)** — ground truth |   rows, every family). Real R195P subnet is `10.255.11.x`, not the `.10.x` the derivation rule assumed — confirmed live via SSH login       |
|   accuracy for R195P and    |   in hand                |   (`BUR-R195P-1055` and `BUR-R195P-1047`, both real cnPilot hardware). Root cause of the E110/E112 MAC anomaly: a row-misalignment bug in   |
|   every other               |                          |   the original 51-row extract, not a fabricated field — `EXT1055`'s row carried `BUR-R195P-1059`'s MAC. Also corrects E110/E112's working   |
|   Burringurrah family       |                          |   assumption that OUI `bc:a9:93` was XV2-exclusive at Burringurrah — R195P shares that OUI block, so `.11.x` is a mixed XV2+R195P cluster,  |
|                             |                          |   not tellable apart by OUI alone. `device-inventory.csv` itself not yet reconciled against the export — pending operator decision on scope |
|                             |                          |   (51 old rows vs 53-120 real devices per family)                                                                                           |
## Security Incidents

- **2026-09-17 — `snmp_read_community`/`snmp_write_community` briefly exposed in an agent transcript.** While exploring `/api/system-config` to design `get_config()`, an ad hoc redaction regex
  (`pass|psk|secret|key|shared`) did not match the key name `community`, so the device's real SNMP community strings printed to the terminal/conversation transcript before anyone caught it. The local
  file holding the raw response was deleted immediately, but the transcript exposure cannot be undone. **Treat both community strings on this device as compromised — operator decision pending on
  rotation, and on whether the fleet uses a standardized community string that would need rotating everywhere, not just here.** Fix: `scripts/cambium_xv2_adapter.py`'s `REDACT_KEY_PATTERN` now also
  matches `community`, `radius`, `credential`, `token`, and `auth`, and every code path that can return `*-config` data (`get_config()`, `--dump`) redacts through that single pattern before the value
  ever leaves the function — never re-implement redaction ad hoc in a throwaway script again.
- **2026-09-17 — repeat incident, ePMP SM this time: `snmpReadOnlyCommunity`, `snmpReadWriteCommunity`, `wirelessRadiusPassword`, and `wirelessInterfaceEncryptionKey` printed to an agent transcript in
  plaintext.** While probing the newly-discovered `get_param` API's `act=config_regular` payload (see [06_device-api-cli-reference.md](06_device-api-cli-reference.md) ePMP section) for
  credential-shaped keys, the check printed each flagged key's **actual value** to confirm it was "real, not a placeholder" — the exact same category of mistake the XV2 incident above already exists
  to prevent, just on a different device family and without reusing `cambium_xv2_adapter.py`'s `REDACT_KEY_PATTERN`/`redact()` because no adapter code exists for ePMP yet. The local file
  (`sm_get_param_config_regular.json`, scratchpad-only, never committed to any repo) was deleted immediately; the transcript exposure cannot be undone. **Treat this device's SNMP community strings,
  RADIUS password, and wireless encryption key as compromised — same pending operator rotation decision as the first incident, now potentially spanning two device families if the fleet reuses
  values.** Root cause: checking whether a credential-shaped key *has* a value must never involve printing the value itself — `bool(v)` or `len(v)` answers "is it set", full stop. This rule applies
  **before** any ePMP adapter is written, not just inside one once it exists — the mistake happened at the ad hoc investigation stage, the same stage the first incident happened at. Fix: `just
  scan-fields <path>` (`scripts/scan-config-fields.py`) now exists specifically so there's a safe default to reach for instead of an ad hoc inline check — run it on any captured JSON before ever
  looking at it by hand, in this pack or any consuming project.

## Pack Staleness Risks

- **Superseded 2026-09-17, same day as written.** This pack was seeded 2026-09-17 from a single extraction session with everything `USER_STATED` or register-derived. That is no longer the pack's
  overall state: live device sessions the same day produced real, `VERIFIED-OBSERVED` adapter code and data for all four Cambium families (see the new stable_fact in `manifest.json` and
  `references/06_device-api-cli-reference.md`), plus fleet-wide SNMPv2c confirmation. What still stands: evidence-state discipline is per-fact, not pack-wide — always check the specific fact's own
  state (`01_overview.md`'s discipline) rather than assuming either "everything confirmed" or "everything unconfirmed". Genuinely still-`USER_STATED`/unconfirmed items are tracked individually above
  and in `manifest.json known_constraints` (e.g. `hardware_revision`), not as a blanket pack-wide caveat.
- `manifest.json`'s `stable_facts` will drift from `cambium-swap`'s live inventory files over time — the manifest is a snapshot, `cambium-swap/inventory/*.csv` is the live source.
