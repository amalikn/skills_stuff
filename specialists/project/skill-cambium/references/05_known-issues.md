# Known Issues and Gaps

## Contents

- [Knowledge Gaps (by design — require execution layer)](#knowledge-gaps-by-design--require-execution-layer)
- [Coverage Gaps (partial knowledge)](#coverage-gaps-partial-knowledge)
- [Response-Shape Divergence Across the Fleet (sweep 2026-09-20)](#response-shape-divergence-across-the-fleet-sweep-2026-09-20)
- [Security Incidents](#security-incidents)
- [Pack Staleness Risks](#pack-staleness-risks)
- [LLDP on Cambium devices — checked 2026-09-23, partly answered](#lldp-on-cambium-devices--checked-2026-09-23-partly-answered)
- [Failure signatures over the SMC path (mowanjum, 60-plus collector cycles to 2026-09-26)](#failure-signatures-over-the-smc-path-mowanjum-60-plus-collector-cycles-to-2026-09-26)
- [Concurrent SSH reads of R195Ps fail (2026-09-28)](#concurrent-ssh-reads-of-r195ps-fail-2026-09-28)
- [An R195P no vault entry logs in to (2026-09-29)](#an-r195p-no-vault-entry-logs-in-to-2026-09-29)
- [Redaction missed `PWD` keys (fixed 2026-09-30)](#redaction-missed-pwd-keys-fixed-2026-09-30)
- [Dashboard bots monitor AP reachability by pinging from the SMC over Teleport (2026-09-30)](#dashboard-bots-monitor-ap-reachability-by-pinging-from-the-smc-over-teleport-2026-09-30)
- [Fleet SNMP identity gaps (measured 2026-10-05)](#fleet-snmp-identity-gaps-measured-2026-10-05)
- [R195P reports every Wi-Fi client as IPv4 0.0.0.0 to cnMaestro (2026-10-05)](#r195p-reports-every-wi-fi-client-as-ipv4-0000-to-cnmaestro-2026-10-05)
- [`wh` flavour: first device contact (laramba, canteen-creek, 2026-10-07)](#wh-flavour-first-device-contact-laramba-canteen-creek-2026-10-07)
- [Central SMC logs missing in Graylog 2026-09-12 to 2026-10-07 (cross-reference, 2026-10-07)](#central-smc-logs-missing-in-graylog-2026-09-12-to-2026-10-07-cross-reference-2026-10-07)

---

## Knowledge Gaps (by design — require execution layer)

| Gap                                                           | Why                                   | Mitigation                                                                                   |
| ------------------------------------------------------------- | ------------------------------------- | -------------------------------------------------------------------------------------------- |
| `hardware_revision` for all 17 catalogued models              | Requires a real cnMaestro export or   | Pending — `cambium-swap` walk-before-run gate flagged this as unverified                     |
|                                                               |   device session                      |                                                                                              |
| Which specific serials are on the legacy (`-legacy`) password | Registers don't record credential     | Try primary vault entry, fall back to `-legacy` per device                                   |
|                                                               |   state per device                    |                                                                                              |
| XV2 hardware variant (2T0 vs 22H) at Burringurrah             | That register has no `Model` column   | Left as bare `XV2` in `device-inventory.csv` — don't guess the variant                       |
|                                                               |   for XV2 rows                        |                                                                                              |
| R195P `interfaces` schema keyed by interface name             | RESOLVED 2026-09-24                   | `schema_tool` contracts map keys by role (`MAP_ROLES`, schema `x-roles`); all 11             |
|                                                               |                                       |   observations conform; see `schemas/README.md` "Map-shaped responses"                       |

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
## Response-Shape Divergence Across the Fleet (sweep 2026-09-20)

Derived from 111 live observations across all 36 sites — one representative device per family per site. Full per-endpoint breakdown in [../schemas/DIVERGENCE.md](../schemas/DIVERGENCE.md); the
contract itself is in [../schemas](../schemas).

**Enterprise Wi-Fi is far less uniform than a single-site test suggests.** In `client-summary` only **43 of 98 fields are universal; 54 split by model**. `radio-rf-summary` is 7 universal against 9
model-split, `radio-summary` 28 against 19, `device-summary` 31 against 16. An adapter written against an XV2 alone depends on fields that an E500 does not return, and fails silently rather than
loudly because the field is simply absent from the JSON.

**`client-summary` is truncated at 60,000 bytes on busy APs, with HTTP 200.** Confirmed on an AP carrying roughly 60 clients: the body stops mid-record, no pagination parameter is honoured, and the
result will not parse. A busy AP yields nothing rather than partial data, and the 200 status makes it look like a malformed device rather than a capacity limit. Full detail in
`references/06_device-api-cli-reference.md`. This qualifies the REST-over-SNMP finding below — REST wins on field richness and fails on the largest APs.

**`ip6_ll` splits by model, and encodes the client MAC.** It is an `array` on XV2 (10 observations), a `string` on E500 (6), and absent where the client has no link-local (17). It is also EUI-64
derived: the observed `fe80::6885:b9ff:feac:bb89` resolves exactly to client MAC `6A-85-B9-AC-BB-89`, so **it carries the same identifying information as the MAC field** and must be redacted on the
same footing. **Resolved 2026-09-20:** the adapter normalises it to a list on every record, including records where the device omits the key. Wrapping the E500 string and mapping absent to empty is
lossless, whereas normalising to a string would truncate any XV2 client holding more than one address.

**the R-series `interfaces` getter is not contractable as it stands, and that is an adapter bug rather than device divergence.** Its "site-specific fields" are interface *names* used as object keys —
`eth2.17`, `eth2.550`, `wan1.500`, `wan1`, `rai1` — so each site's VLAN configuration shows up as schema fields. A response keyed by site-variable names has no stable shape by construction. It should
return a list of interface objects carrying the name as a value. Until it does, its schema describes one site's VLAN plan, not the family.

**Shapes still unknown after a full sweep**, because nothing anywhere returned a record: the ePMP SM `clients` getter (empty on all 31 observations — an SM has no clients, so this may be correct by
design) and the cnWave `links_count` getter (empty on all 4). the cnWave `gps` getter returned `null` fleet-wide. the ePMP AP `wireless_link` getter is null-or-object, which is contract rather than a
gap.

**Models the single-site baseline never saw**, now in the contract: cnWave **V1000** and **V3000** alongside V5000, and ePMP **Force 300-16** alongside Force 300-25 and 3000L.

### Two sites authenticate only with the `-legacy` credential (2026-09-20)

**kalumburu and mornington run the older local-admin password.** Confirmed by hand on a kalumburu Enterprise Wi-Fi unit: the primary `<secret:keepassxc:cambium-devices/enterprise-wifi>` entry returns
`Invalid username or password`, while `<secret:keepassxc:cambium-devices/enterprise-wifi-legacy>` returns `{"success":true}` on the same device. The same holds for ePMP AP and SM at kalumburu with
their `-legacy` entries, and for mornington's R-series.

This affects 132 devices at kalumburu alone and spans three independent families and two different vendor login paths, so it is a site-level rotation gap rather than a per-family quirk. **Any tool
that assumes one current password per family will report these sites as unreachable rather than as a credential failure** — which is exactly what the first sweep did. The fleet sweep now tries each
family's primary entry and then its `-legacy` fallback.

### Reachability — 121 of 122 site/family pairs contracted

Every pair was attempted. A first pass left 12 gaps; 7 were recovered by restoring the original timeouts (a mid-run retune to 20s forward / 75s adapter / two attempts was too tight), and 4 more by the
`-legacy` credential fallback above. One gap survives:

| Site      | Family        | Devices | Cause                                                                                                 |
| --------- | ------------- | ------- | ----------------------------------------------------------------------------------------------------- |
| hope-vale | cnWave 60 GHz | 7       | TLS handshake EOF on four devices, at full timeout, with both credentials; all units also failed ping |

That one reads as genuinely down hardware rather than an access problem.

### Two defects this sweep found in its own tooling

Both produced confident, wrong output rather than an error, which is why they are recorded here:

1. **A delimiter-parsing bug silently dropped the first endpoint of every Wi-Fi observation.** Slicing the response header on the same `###` separator used by the endpoint blocks consumed the first
   block's delimiter. `client-summary` was first in the list, so **two complete fleet sweeps produced client-bearing data for exactly one site** while every other endpoint parsed cleanly. The counts
   were right, the AP selection was right, and the client list was empty — a failure that looks exactly like "no clients connected".
2. **The device credential was passed as a positional argument to `tsh ssh`**, putting the admin password in the process table on this workstation and on every SMC box the sweep touched, where any
   `ps` reveals it. Fixed by feeding credentials on stdin. The two sweeps that ran before the fix did expose it that way; treat the Enterprise Wi-Fi vault entry accordingly.

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

- **2026-09-21 — `cambium_r195p_adapter.py` refused a second site's units with "REMOTE HOST IDENTIFICATION HAS CHANGED" after a first site's IPs were already in `~/.ssh/known_hosts`.** Caught batch-
  pushing mowanjum's R195P fleet into wc-local's OpenWISP (unified-network-controller) after having already reached devices at other sites earlier the same session. `StrictHostKeyChecking=no` alone
  does **not** cover this: it only auto-accepts a host key never seen before, and still refuses on a *changed* one. This project's site management subnets genuinely overlap (`01_overview.md` "Device
  host keys collide across sites"), so the same IP really is a different real device with a different host key at another site — a legitimate case, not an attack. Fix: added `-o
  UserKnownHostsFile=/dev/null` alongside `StrictHostKeyChecking=no` in `_run()`'s `cmd` list, so no host key is ever persisted or compared across sites in the first place. Any future adapter script
  that shells out to `ssh` against this fleet should carry both options together, not `StrictHostKeyChecking=no` alone.

## Pack Staleness Risks

- **Superseded 2026-09-17, same day as written.** This pack was seeded 2026-09-17 from a single extraction session with everything `USER_STATED` or register-derived. That is no longer the pack's
  overall state: live device sessions the same day produced real, `VERIFIED-OBSERVED` adapter code and data for all four Cambium families (see the new stable_fact in `manifest.json` and
  `references/06_device-api-cli-reference.md`), plus fleet-wide SNMPv2c confirmation. What still stands: evidence-state discipline is per-fact, not pack-wide — always check the specific fact's own
  state (`01_overview.md`'s discipline) rather than assuming either "everything confirmed" or "everything unconfirmed". Genuinely still-`USER_STATED`/unconfirmed items are tracked individually above
  and in `manifest.json known_constraints` (e.g. `hardware_revision`), not as a blanket pack-wide caveat.
- `manifest.json`'s `stable_facts` will drift from `cambium-swap`'s live inventory files over time — the manifest is a snapshot, `cambium-swap/inventory/*.csv` is the live source.

## LLDP on Cambium devices — checked 2026-09-23, partly answered

Operator note, 2026-09-23: is LLDP available on any Cambium family? Checked the same evening from kalumburu-smc01 (unified-network-controller):

- **ePMP (3000L AP, Force 300 SM and master) and E500: LLDP-MIB is not exposed over SNMP.** `snmpbulkwalk .1.0.8802.1.1.2` and `.1.0.8802` answer `No Such Object` on all four units; the R195P returns
  `Error in packet` for the same walk. `VERIFIED_PRIMARY`.
- **ePMP transmits LLDP.** Every one of six ePMP `config_regular` backups (3000L APs and Force 300 SMs) holds `networkLLDP: "1"`, `networkLLDPMode: "1"`, `lldp_user_enabled: "1"`. Which neighbour
  table a unit keeps, if any, is not in `device_props` seen so far — `UNVERIFIED`; nothing to read over REST was found.
- **The SMC cannot see them across the switch.** LLDP frames are link-local (`01:80:c2:00:00:0e`) and are not bridged, so a 70 s `tcpdump ether proto 0x88cc` on `bridge_500` at kalumburu captured
  nothing; the SMC has no `lldpd`. The consumer of ePMP LLDP is the switch port the radio hangs off (the switching-refresh project's ground), not the SMC.
- Enterprise Wi-Fi (XV2/E-series) and cnWave transmit-side support: `UNVERIFIED` (no config key looked for yet).

## Failure signatures over the SMC path (mowanjum, 60-plus collector cycles to 2026-09-26)

What "12 per-device errors" at one site turned out to be when classified (unified-network-controller, CHANGELOG 20260926_1810; devices reached through the SMC over `tsh`): 152 `down` (units switched
off at the site, not faults), 16 TLS EOF, 14 SSH exit 255, 5 credential-lookup timeouts (the vault, not the device), 4 handshake timeouts, and 1 ePMP `auth_failed`, the 2026-09-22 lockout from a
bad-credential attempt (see the lockout note under Security Incidents). Two lessons for anyone reading device errors from this path: classify before counting, because most of a site's "errors" are
units that are off; and rule out the path first, because an expired `tsh` certificate produces the same per-device failures fleet-wide (skill-smc `references/06_failure-modes.md`). Replay evidence
from the same cycles: 151 registered devices, 0 duplicate names or MACs.

## Concurrent SSH reads of R195Ps fail (2026-09-28)

Five R195Ps read at once over SSH through yakanarra-smc01 (unified-network-controller `identify_candidates.py`, one tunnel each): two failed with `SSH connection failed (exit 255)`, `sshpass` missing
the password prompt and ssh falling back to `ssh_askpass`, after the adapter's one retry. Each unit read alone succeeded, twice. REST reads (ePMP, Enterprise Wi-Fi) in parallel through the same SMC
were unaffected. Read R-series units one at a time; the controller's identify serialises them. The serial no longer needs SSH at all: SNMP `serialNumber` (41010) gives it (snmp-oid-registry.yaml).

**Fixed the same day (v0.6.19):** the adapter hands the password to ssh through `SSH_ASKPASS` with `SSH_ASKPASS_REQUIRE=force` (OpenSSH 8.4+), so nothing watches a terminal for the prompt. Five R195Ps
at once, three rounds: 15 of 15 logged in, 1.5 s each (about 4 s under `sshpass`). `sshpass -p` also put the password on the command line, where any local user could read it in `ps`; it is gone.

## An R195P no vault entry logs in to (2026-09-29)

> **Resolved 2026-09-30:** the unit's SSH (Dropbear 2020.81) rejected the correct `cnpilot-r-series` password while its web UI accepted it; a reboot restored SSH logins. When an R195P refuses SSH but
> its web UI works, reboot it before trying other vault entries.

daniel-test-nbn's R195P `HOR-R195P-1001` (serial WFXK0CTQRQBW, 4.7.3-R21, a unit carrying a horn-island name) refuses `cambium-devices/cnpilot-r-series` over SSH (`Permission denied
(publickey,password)`), and the vault has no R-series `-legacy` entry to fall back to, so it has no config backup. SNMP reads and writes work with the apn communities. Not retried: one login attempt
per read, lockout behaviour of the family not established.

## Redaction missed `PWD` keys (fixed 2026-09-30)

The adapters' `REDACT_KEY_PATTERN` (`pass|psk|secret|key|...`) did not match `PWD`, so the R195P reader returned `nvram.DBID_TR_ACS_PWD`, `DBID_TR_CONNECT_PWD` and `DBID_UPGRADE_FTP_PWD` unredacted
(found by unified-network-controller's provisioning template derivation). All four adapters now match `pwd`. Consumers that stored a backup before the fix hold those values
(unified-network-controller: the tjuntjuntjara R195P Golden Config backups, re-taken except 1006, plus Nautobot's change log). Side effect: ePMP `systemConfigFactoryResetKeepPwd` and
`wirelessPMPWDSUnknownMACFlood` now redact too (harmless).


## Dashboard bots monitor AP reachability by pinging from the SMC over Teleport (2026-09-30)

Both production dashboards check AP reachability the same way. A Teleport bot user runs `ping -c 1 <AP management IP>` on the site's SMC through `teleport exec`, one command per AP per poll. There is
no direct device API or SNMP poll on this path; the SMC is the jump host. Counts are from each box's teleport journal over 24h, read 2026-09-30:

| Cluster                                          | Bot user                  | Sites polled (commands/24h)                                                                                           |
| ------------------------------------------------ | ------------------------- | --------------------------------------------------------------------------------------------------------------------- |
| nbn_accelerate (`teleport.communitywifi.net.au`) | `bot-cw-dashboard`        | koonibba 1,314 pings, indulkana 540, warakurna 456, ampilatwatja 432, aurukun-smc03 286, hope-vale 258, arawerr 83,   |
|                                                  |   (54.66.73.128)          |   galiwinku 10, doomadgee 2                                                                                           |
| rcp (`teleport.apn.au`)                          | `bot-apn-dashboard`       | kalumburu 644, mowanjum 423, tjuntjuntjara 378, bidyadanga 204, wujal-wujal 68, horn-island 54, wangkatjungka 43,     |
|                                                  |                           |   yakanarra 21                                                                                                        |

Targets seen: nbn `10.255.0.x` and `10.255.3.x` (e.g. indulkana `10.255.3.60/.61/.110`, koonibba `10.255.0.11-.62`).

Implications for the device layer:

- **Only some sites are polled.** 9 of 31 nbn SMCs and 8 of 18 rcp SMCs had any poll in the window. Dashboard AP status for the other sites does not come from this path. Where it does come from is
  unverified.
- **A failed SMC or Teleport path looks like a down AP.** A dead Teleport agent on the SMC, or a missing `ping`, would most likely show the site's APs as down while they are fine. That is the same
  class of false negative as the `snmpget` finding in skill-smc (2026-09-20). Unverified for these dashboards.
- **The nbn bot does more than ping.** At koonibba and amata it also runs a "usage fix" routine that restarts the SMC firewall and wipes every device's access mark. That is SMC-layer and recorded in
  skill-smc `references/13_known-issues.md` (2026-09-30). It is cross-referenced here because anyone reading `bot-cw-dashboard` activity for AP monitoring will see those commands in the same journal.

Source: read-only surveys, `local-knowledge-ansible/ansible-wifi/issues/nbn-accelerate/koonibba-usage-drop/mark-watch/` (`bot-survey-20260930/`, `rcp-survey-20260930/`). RCP journals only reach
2026-09-28/29, so its counts cover about 1-2 days.

## Fleet SNMP identity gaps (measured 2026-10-05)

Source: UNC capture corpus: newest discovery sweep per site (43 sites, about 4,000 hosts, 2026-09-23 to 2026-09-30) and 44 identify reads, aggregated read-only on 2026-10-05. Counts, not samples; read
before trusting SNMP alone for identity or naming.

- **ePMP default sysName.** 349 ePMP units answer `sysName` = `CambiumNetworks` (Force 300-16 223 of 899, Force 300-25 97 of 491, 3000L 29 of 131). Never name or match a unit on it; use the DNS A
  record, the asset register name or the device API.
- **No serial over SNMP.** The sweep's SNMP read returned no serial for every E500 (87 of 87) and E430H (5 of 5), while every XV2 returned one; also for 21 of 1,176 R195P units. Take those serials
  from the device API (Enterprise Wi-Fi) or leave the field empty; cnWave V-series is already recorded in `snmp-oid-registry.yaml`.
- **MAC notation differs by adapter.** cnPilot and cnWave identify reads return lowercase colon MACs, Enterprise Wi-Fi dash-separated, ePMP upper-case colon. Normalise before comparing.
- **Unknown-family units.** Two units with the Cambium OUI `00:04:56` answer with the net-snmp `sysObjectID` `.1.3.6.1.4.1.8072.3.2.10` and no model, so the family cannot be told from SNMP. Identify
  them with the device API before landing them. UNVERIFIED which product they are.

## R195P reports every Wi-Fi client as IPv4 0.0.0.0 to cnMaestro (2026-10-05)

Symptom: cnMaestro's Wireless Clients list shows `0.0.0.0` in IPv4 Address for every client of a cnPilot R195P (kalumburu screenshot, operator 2026-10-05, suspected fleet-wide). It is a reporting gap,
not a DHCP failure.

- **SMC DHCP is healthy.** At 10 sites (6 apn, 4 nbn) the last hour of `isc-dhcp-server` showed ACKs, no NAKs and no "no free leases". At kalumburu all 8 screenshot MACs held a lease and 6 were
  REACHABLE in the SMC's ARP on `bridge_501`.
- **The AP itself has no client IP.** On KAL-R195P-1014 (4.7.3-R21) `/tmp/stahost`, written by `/bin/device-agent` (the cnMaestro agent), lists every client as `0.0.0.0` while
  `/var/log/wireless_sta.log` shows up to about 100 MB per client. The sibling table `/tmp/allhost` (Mac, IP, AuthState, IfName, IpMode, ...) is empty: it is the R195P's own router-mode LAN host
  table.
- **Regression, not design (operator, 2026-10-05: cnMaestro showed client IPs before).** Nothing changed on the SMC (kalumburu `dhcpd.conf` dated 2026-02-13) or in the R195P TFTP config (all 150
  kalumburu files dated 2026-09-02, still `cns_static_url=https://cloud.cambiumnetworks.com`, `mwan_bridge_type=ip_br`). The unit is nonetheless connected to `52.64.230.196:443`, apn-cnmaestro01:
  Cloud redirected it during the move to on-prem (about 2026-09-26). That move is the one fleet-wide change on record, so it is the lead suspect. UNVERIFIED: how Cloud obtained the IP while the
  agent's `/tmp/stahost` holds none, and the date IPs disappeared. It holds on every firmware seen (4.7-R9, 4.7.2-R10, 4.7.3-R21, 4.8.1-R4), which also points away from the unit.
- **Fleet sample:** 12 R195Ps with clients at kalumburu, burringurrah, horn-island, jigalong, mowanjum and tjuntjuntjara: every client `zero_ip`, every MAC leased on the SMC.
- **Not settled:** whether Enterprise Wi-Fi APs report client IPs. The one E500 client seen (kalumburu, VLAN 500) had no lease, so its `0.0.0.0` was correct. XV2 prints nothing for a non-interactive
  `show wireless clients`; check an nbn site's client list in cnMaestro instead.
- **Tool:** `just client-ip-sweep <site>-smc01 <apn|nbn>` (`scripts/client-ip-sweep.sh`) for the three-layer check. For a client's IP, use the SMC lease (`dhcpd.leases`), not cnMaestro.

## `wh` flavour: first device contact (laramba, canteen-creek, 2026-10-07)

Until 2026-10-07 this pack held nothing about `wh` sites; `site-addressing.yaml` still has no `wh` flavour. Read-only, through `tsh ssh -N -L` port-forwards via each SMC, evidence in
`local-knowledge-ansible/ansible-wifi/issues/wh-fleet/cambium-wh-20261007_1457/` (VERIFIED-OBSERVED 2026-10-07):

| Site          | IP (mgmt VLAN 500) | OUI        | Identified as                                      | How                                       | Result                                            |
| ------------- | ------------------ | ---------- | -------------------------------------------------- | ----------------------------------------- | ------------------------------------------------- |
| laramba       | `10.255.0.20`      | `bc:a9:93` | Enterprise Wi-Fi XV2-2T0,                          | `scripts/cambium_xv2_adapter.py`,         | OK; uptime 34 h while the site switch had 123 d   |
|               |                    |            |   `Laramba_XV2_AP1_IP0_20`, 6.6.0.3-r9, cnMaestro  |   `enterprise-wifi` entry                 |   and the SMC 11 d                                |
|               |                    |            |   `apn-cnmaestro01` connected                      |                                           |                                                   |
| canteen-creek | `10.255.0.20`      | `bc:a9:93` | XV2-2T0, `Canteen_Creek_Central_XV2T0`, 6.6.0.3-r9 | same                                      | OK; uptime 68 d, equal to the site switch's       |
| canteen-creek | `10.255.0.21`      | `00:04:56` | ePMP 1000 Hotspot; web UI is the Falcon stack      | web `POST /api/login`                     | **No login found.** 403 (wrong password) for      |
|               |                    |            |   (`falcon-ng-client-2.0.0`), same as              |   via `scripts/cambium_xv2_adapter.py`    |   `epmp-ap`, `enterprise-wifi` and the MikroTik   |
|               |                    |            |   Enterprise Wi-Fi                                 |                                           |   entry; 404 for `enterprise-wifi-legacy` and     |
|               |                    |            |                                                    |                                           |   `epmp-ap-legacy`, possibly the unit refusing    |
|               |                    |            |                                                    |                                           |   after failures. SSH with `epmp-ap` neither      |
|               |                    |            |                                                    |                                           |   refused nor produced output. Stopped after five |
|               |                    |            |                                                    |                                           |   web attempts                                    |
| canteen-creek | `10.255.0.10`      | `00:04:56` | ePMP point-to-point **AP** (`cambiumDeviceMode 1`), | SSH `show dashboard`, `epmp-ap-legacy`    | OK                                                |
|               |                    |            |   firmware 4.7.0.1, SSID `A8bridge`                |   (`epmp-ap` rejected)                    |                                                   |
| canteen-creek | `10.255.0.11`      | `00:04:56` | ePMP point-to-point **SM** (`cambiumDeviceMode 2`), | same                                      | OK                                                |
|               |                    |            |   firmware 4.7.0.1, associated to                  |                                           |                                                   |
|               |                    |            |   `00:04:56:D3:FA:C6` (`.10`)                      |                                           |                                                   |
| glen-hill     | `10.255.0.20`      | not read   | Enterprise Wi-Fi XV2-2T0, serial `WLYM113B7GGM`,   | unified-network-controller `identify`     | OK, 2026-10-08; landed Staged in Nautobot under   |
|               |                    |            |   hostname `XV2_Hotspot0_GlenHill`, 6.6.0.3-r9     |   (`enterprise-wifi` REST)                |   controller `apn-cnmaestro01`                    |
| engawala      | `10.255.0.10`      | `00:04:56` | ePMP **AP** (`cambiumDeviceMode 1`,                | SSH `show dashboard`                      | OK, 2026-10-08. No partner on the SMC bridge;     |
|               |                    |            |   `cambiumSubModeType 1` TDD, not a PTP sub-mode), |   (`scripts/device-login-probe.sh`),      |   HTTP only (443 closed), so the HTTPS REST       |
|               |                    |            |   firmware 4.7.0.1, serial `E8TA05B3JFPR`, name    |   `epmp-ap` (`epmp-ap-legacy` rejected:   |   adapter fails with a TLS EOF before login       |
|               |                    |            |   `Direction Engawala (no omni)`, SSID `A8bridge`, |   the reverse of canteen-creek)           |                                                   |
|               |                    |            |   5750 MHz, **0 connected SMs**, uptime 127 d,     |                                           |                                                   |
|               |                    |            |   cnMaestro `apn-cnmaestro01` connected            |                                           |                                                   |
| engawala      | `10.255.0.20`      | `bc:a9:93` | Enterprise Wi-Fi (web UI `cnPilot {{modelname}}`,  | unauthenticated `GET /` only; not         | Model UNVERIFIED until `identify` reads it        |
|               |                    |            |   Falcon stack), presumably the `wh` XV2 at `.20`  |   logged in                               |                                                   |

- At both sites `.20` is the Cambium AP, not a MikroTik: on `rct` the same address is a MikroTik Metal 52 ac (skill-mikrotik).
- **2026-10-08 (VERIFIED-OBSERVED, Teleport apn):** glen-hill's `.20` is a third `wh` XV2-2T0 on 6.6.0.3-r9, behind the site's MikroTik RB450Gx4 switch (skill-mikrotik `references/01_overview.md`);
  areyonga's `.20` did not answer. So the `wh` pattern holds at three of four sites read: a Cambium XV2-2T0 AP at `.20` behind a MikroTik switch.
- XV2 `ETH1` `rx_bytes`/`tx_bytes` read `4294967295` on laramba: 32-bit counters pinned at their maximum. Do not compute rates from them.
- **Point-to-point bridges (operator, 2026-10-07):** `rct` sites have none, a single AP each (the MikroTik Metal, skill-mikrotik); most `wh` sites have a single AP and only a handful have an ePMP
  point-to-point bridge. Known `wh` sites with a bridge: **canteen-creek** (`10.255.0.10` AP, `10.255.0.11` SM, VERIFIED-OBSERVED 2026-10-07). Add each new one here with its addresses when found.
  **engawala** (2026-10-08) has only the bridge's AP half: `.10`, SSID `A8bridge` like canteen-creek's pair, no SM associated and none on the site subnet, so there is no live link to read there.
- **ePMP 4.7.0.1 serves HTTP only** (engawala `.10`, 2026-10-08: ports 80 and 22 open, 443 closed). `scripts/cambium_epmp_adapter.py` builds `https://` URLs and fails with `SSL:
  UNEXPECTED_EOF_WHILE_READING` before any login, so no login is spent; read such units over SSH (`show dashboard`).
- canteen-creek `.10` and `.11` print the login banner "change the default SNMP Read-Only Community string" and "... Read-Write Community string": both bridge units still run the factory SNMP
  communities (VERIFIED-OBSERVED 2026-10-07, value not read). Needs an operator decision before any change.
- Login probe: `scripts/device-login-probe.sh` (one attempt per entry, client on the Mac; an empty session is reported as UNCONFIRMED, not accepted).
- Gaps: the ePMP 1000 Hotspot login (canteen-creek `.21`); the rest of the `wh` fleet; a `wh` block in `site-addressing.yaml`.

## Central SMC logs missing in Graylog 2026-09-12 to 2026-10-07 (cross-reference, 2026-10-07)

Owned by skill-smc (`references/13_known-issues.md` 2026-10-07; `03_communication-flows.md` "Graylog Backend Path in AWS"). Recorded here because device-layer investigations read SMC-side logs.

- The ACM cert on `gl.aws.apn.au` expired 2026-09-12 09:59:59 AEST. Every SMC's fluent-bit (`tls.verify On`) stopped shipping until about 11:15 AEDT on 2026-10-07. Logs were not backfilled, so
  **Graylog holds almost no SMC-originated messages for that window**.
- The gap matters for Cambium work wherever the evidence is SMC-side logs: `isc-dhcp-server` leases and ACK/NAK for AP clients, AP or SM syslog sent to the SMC (`syslogServerIPFirst` is the SMC
  management address on ePMP SMs, see `06_device-api-cli-reference.md`), and dashboard-bot activity. Whether AP/SM syslog received by the SMC lands in a file fluent-bit tails is UNVERIFIED. If it
  does, it is in the same gap.
- For that window use on-box files (SMC `/var/log`, AP `/tmp` and logs) or Prometheus. The 2026-10-05 R195P 0.0.0.0 investigation above used on-box evidence and is unaffected.
- Do not read Graylog silence for a site in that window as the site being down. Check Prometheus `up` instead (skill-smc `06_failure-modes.md`).

## Which SM an R195P is cabled to: the AP and the SMC say it, the units do not (2026-10-09)

The R195P sends no LLDP and answers no IF-MIB table over SNMP; its own ARP holds only the gateway, and its `br0` bridge (ports `eth2.1`,
`eth2.501`, `rai0`, `rai1`, `ra0`) floods the site's public VLAN, so every router lists the same ~40 clients there. The Force 300 SM has no bridge,
Q-BRIDGE or ARP table over SNMP, and its REST bridge table lists only itself (as an ePTP master, `cambiumSubModeType` 5, it answers
`cambiumAPBridgeTable` like a 3000L: old-looma ap-ep2p-1, 2026-10-09). Two sources name the SM without any name (old-looma, 4.7.0.1):

- **The 3000L's bridge table** (`cambiumAPBridgeTable`, snmp-oid-registry.yaml): each learnt MAC with the SM it came through. Units appear after
  they pass traffic (ping them from the SMC, wait about 90 s) and age out; Cambium fixed missed and wrong entries in 4.7.1 and 5.11.0, so treat one
  sighting as a sample.
- **The router's own Wi-Fi clients and Option 82**: at low-touch sites the 3000L relays DHCP with Option 82 (`dhcpOption82: 1` on the AP, 0 on the
  SM), and the Remote ID is the SM's radio MAC (its record + 1; ansible-wifi `cnmaestro-provisioning.py` `_remote_id_mac`). The SMC's dhcpd keeps it
  in `/var/lib/dhcp/dhcpd.leases` (212 of 1,949 leases), for the public clients only: the routers' own leases carry none. The clients the router
  learnt on its `ra*`/`rai*` ports, looked up there, name its SM: home-49's and home-17's clients came through sm-47 and sm-16, as the AP table said.

Both disagree with the names for some routers (home-49 is behind sm-47, home-63 behind sm-61): the name number is a third, weaker fact.
unified-network-controller reads all three (topology readers `epmp-ap-bridge`, `smc-dhcp-relay`, `r195p-wifi-clients`). None needs cnMaestro.

## A low-touch install leaves the installer's record in sysDescr (2026-10-09)

At old-looma (rcp, low-touch) 57 of 60 ePMP radios answer sysDescr `.1.3.6.1.2.1.1.1.0` (the unit's `snmpSystemDescription`) with a JSON record the
install wrote: `lotno`, `lat`, `lon`, `confirmed: true`, `align` (e.g. `-64/1`), `test` (e.g. `75/20`) and `variables` (`preferred_ssid`, `seqid`,
`frequency`, `power`, `antenna_gain`). The position equals the unit's typed-in Device Location within 4 m. At non-low-touch hope-vale the fields are
empty. A reader must unescape net-snmp's `\"` before parsing. unified-network-controller uses it for Premises Locations (topology/sources.py
`installer_record`). cnWave controllers' topology also carries sites with a configured position; at old-looma the tower sites lie within 30 m of the
3000L GPS fixes.
