---
Title: Fleet management systems
Category: domain-reference
Status: current
Authority: authored-guidance
Scope: Systems and infrastructure architecture
Last reviewed: 2026-10-29
Summary: >-
  Fleet management architecture for distributed device estates: a source of truth with per-field ownership enforced as permissions, device records as
  network positions, held hardware swaps, estate-wide identity checks, telemetry collectors and on-box spools, vendor-exit dependency mapping by lifecycle
  event, controller identity and recovery, adopt-by-read-back, lifecycle and recovery.
---

# Fleet management systems

## Contents

- [Scope](#scope)
- [Decision rules](#decision-rules)
- [Source of truth and field ownership](#source-of-truth-and-field-ownership)
- [Telemetry collectors and spools](#telemetry-collectors-and-spools)
- [Vendor dependency and controller recovery](#vendor-dependency-and-controller-recovery)
- [Lifecycle and recovery](#lifecycle-and-recovery)
- [Patterns and anti-patterns](#patterns-and-anti-patterns)
- [Failure modes and tests](#failure-modes-and-tests)
- [Worked example](#worked-example)
- [Review checklist](#review-checklist)
- [Further reading](#further-reading)

---

## Scope

- The systems that run a fleet of remote devices: source of truth (SoT), collectors, controllers, operation ledgers and their recovery.
- Field ownership, identity, reconciliation and telemetry delivery over constrained or intermittent backhaul.
- Vendor and controller dependency: what still works when a vendor cloud, licence service or controller is gone.
- Product specifics stay with their packs: skill-nautobot (SoT implementation), skill-openwisp (monitoring), skill-cambium, skill-mikrotik and skill-smc (device and site-box facts). Write safety and
  canaries: [automation and safety](automation-and-safety.md). Rollout waves: [provisioning-and-lifecycle](provisioning-and-lifecycle.md).

## Decision rules

- A SoT is authoritative for what people decide. For facts a device reports, it is a cache. Name the owner class of every field.
- Enforce ownership as a permission on a named service account, not as a convention. Nautobot, for example, has object-based permissions with attribute constraints. VERIFIED_PRIMARY, [nautobot-perms],
  checked 2026-10-29.
- Automation consumes operator-owned (intent) fields only. An observed value never becomes intent without a person or reviewed import.
- One writer per managed artefact, named in data. During a controller migration, switch the writer explicitly; never let two systems co-write.
- Key every downstream system (monitoring, automation, tickets) on a stable record ID, never on serial, MAC, IP or display name.
- Treat a remote operation as unknown until the device state is read back. A queued or delivered message is not a change.
- Classify every vendor dependency by the lifecycle event that needs it (onboard, restore, replace, upgrade), not only by steady state.
- Before choosing a controller DR tier, list the identity elements a restored instance must keep (address, certificates, application ID, licence binding).

## Source of truth and field ownership

| Class     | Written by                              | Example fields                    | On disagreement                         |
| --------- | --------------------------------------- | --------------------------------- | --------------------------------------- |
| Operator  | people or a reviewed import             | role, site, intended VLAN, status | SoT wins; report the drift, never write |
| Device    | collector service account only          | serial, MAC, firmware, uptime     | device wins, after the uniqueness check |
| Inventory | vendor or controller export (bootstrap) | purchase serial, licence tier     | becomes Device once the unit reports it |
| System    | the SoT platform                        | IDs, timestamps, change log       | not editable                            |

- Applicability is a separate axis from ownership. Declare capabilities per device type (rack-mounted, bridged, dual-stack) and derive which fields apply; an absent list means "not yet assessed", an
  explicit empty list means "none".
- Estate-wide uniqueness is the corruption falsifier. A real observation of a serial or MAC is unique; if the value already sits on another record, the read reached the wrong device. Write nothing and
  alarm.
- A device record is a position in the network, not a physical unit. The serial and MAC describe whichever unit fills the slot.
- A changed identity on a known position is a hardware swap. Hold it: the collector writes nothing, raises drift, and an operator acknowledges. The acknowledgement moves the identity, stamps the swap
  and sends the old unit to a decommissioning state.
- Vendor and controller exports are unverified bootstrap. Reconcile them with live read-only sweeps and record corrections in a dated report beside the immutable export.
- Topology inference accumulates evidence across runs (first seen, last seen, missed runs). Keep conflicts visible for a person; never drop a link only because one run did not see it.

```text
HARDWARE SWAP: identity change on a known position is held, not applied

+-----------+   new serial   +----------------+   no   +----------------------------+
| collector |--------------->| serial unique  |------->| write nothing, alarm:      |
| read      |                | estate-wide?   |        | read reached the wrong box |
+-----------+                +-------+--------+        +----------------------------+
                                     | yes
                                     v
                             +----------------+   operator    +----------------------+
                             | hold as drift; |-------------->| move identity, stamp |
                             | write nothing  |  acknowledges | swap, old unit to    |
                             +----------------+               | decommissioning      |
                                                              +----------------------+
```

Operation ledger states: accepted, committed, reverted, partial, unknown. Keep them distinct; only a read-back moves an operation to committed.

## Telemetry collectors and spools

- Decide on purpose whether a telemetry gap during a backhaul outage is acceptable. A central poller turns every outage into a gap; only an edge collector with a buffer turns it into a delay.
- vmagent buffers to local disk when remote storage is unreachable, with a per-destination size cap (`-remoteWrite.maxDiskUsagePerURL`). VERIFIED_PRIMARY, [vmagent], checked 2026-10-29. Most
  off-the-shelf agents still need a thin adapter for a vendor's own API.
- A crash-safe on-box spool writes one batch per cycle: temporary file, fsync, rename, rising sequence number.
- Cap the spool by age and size, drop oldest first, and count every drop. Loss must be bounded and visible.
- Gate readings on a confirmed time sync. Boards without a battery-backed clock boot with a wrong date; reject data with large skew or future timestamps at ingest. NTPv4: [rfc5905].
- Acknowledge a batch only after the stored data passes a check. Delivery is then at-least-once, so make replay idempotent on (device, timestamp).
- Drain newest first (current state), then the backlog oldest first.
- Know which edge filesystems are volatile. A spool on a RAM-backed overlay does not survive a power cut.
- Alarm on the cause, not on every device behind it, and alarm on the health of the monitoring path itself (collector credential expiry, ingest refusals). Keep suppression rules simple: the SRE book
  reports limited success with complex dependency hierarchies. VERIFIED_PRIMARY, [sre-monitoring].
- Track run outcome and per-phase time per collector run. A duration graph without success state hides a credential that expired.
- Measure the observation path you already have before adding a time-series store; keep one store authoritative for health.

## Vendor dependency and controller recovery

| Class | Meaning                                                      | Typical capabilities                 |
| ----- | ------------------------------------------------------------ | ------------------------------------ |
| L0    | fully local                                                  | forwarding, local management         |
| L1    | local, with optional vendor enhancement                      | local UI plus cloud analytics        |
| L2    | local in steady state; needs the vendor for lifecycle events | onboarding, restore, device transfer |
| L3    | depends on a subscription or entitlement                     | licence sync, feature tiers          |
| L4    | vendor cloud service                                         | hosted controller                    |

- Tag each row with its evidence state (documented, observed, inferred). A row becomes observed only through a completed test.
- An on-premises controller can still carry a licence fuse: a grace period after which entitlement loss stops management or re-queues devices. Read the current version's entitlement behaviour and plan
  any emergency exit inside the fuse window.
- Moving from a vendor cloud to the vendor's on-premises product changes an L4 dependency into L2 or L3; it does not remove it.
- Devices bind to the controller address they were given. DHCP option 43 carries opaque vendor-specific data, so its content and precedence over a static setting are vendor behaviour.
  VERIFIED_PRIMARY, [rfc2132]. Hand out a stable name or a reserved address so recovery does not need a fleet-wide change.
- A block-level snapshot of the controller host is a point-in-time copy of the whole volume. VERIFIED_PRIMARY, [ebs-snapshots], checked 2026-10-29. It is the tier that keeps every identity element
  together; an application backup may need the vendor service you are hedging against.
- Record restore preconditions with each backup: versions, licence state, device count and a checksum.
- Re-onboarding every device is the hidden cost of losing controller identity. Count the site visits it would need before choosing a DR tier.
- Pre-agree vendor-distress triggers (insolvency notice, announced end date, licence service unreachable beyond a set period, unpatched critical flaw) and two exit tracks: staged replacement over
  years, and an emergency track that keeps management continuity.
- Keep a local mirror of firmware, MIBs, documentation and signing material for every deployed version. Vendor distress closes access to them first.
- Test a spares strategy against the vendor-loss scenario before buying spares in quantity.

```text
STRANGLER REPLACEMENT OF A CONTROLLER: adopt by read-back, legacy keeps its keys

+------------------+  read values back   +------------------+
| legacy           |-------------------->| new system       |
| controller       |  (no write to unit) | records unit;    |
| (still writer of |                     | changes nothing  |
| its own keys)    |                     +--------+---------+
+--------+---------+                              |
         |  function by function, writer switched explicitly in data
         v                                        v
+------------------+                     +------------------+
| function retired |-------------------->| function owned   |
| (one at a time)  |                     | by new system    |
+------------------+                     +------------------+
```

- Replacing a legacy system bit by bit is the strangler fig pattern. VERIFIED_PRIMARY, [strangler-fig], checked 2026-10-29.
- Never write the legacy controller's control settings while it is in service. Leaving it is a separate decision.

## Lifecycle and recovery

- Make the controller host rebuildable from code (image, configuration, bootstrap). Prove it by destroy, rebuild and diff of a site against the earlier state; onboarding from the live network then
  regenerates the SoT.
- The out-of-band recovery path must not depend on the management plane it recovers (zero-trust proxy, controller, tunnel). It is the last thing an update touches.
- Keep bootstrap identity separate from production identity. A hardware ID is a lookup key, never a credential.
- Prefer platform workload identity for machine join (cloud IAM, instance identity) over long-lived join tokens; a rebuilt or long-offline host then rejoins without a person minting a secret.
- Short-lived certificates hide a broken renewal until they expire. Alarm on renewal failure directly; choose the TTL as a trade between blast radius and how long you can ride out a renewal outage.
- Unattended remote boxes need an immutable or A/B root with automatic rollback, and a write audit that classifies every disk write path before root goes read-only. Lifecycle states and EOL:
  [provisioning-and-lifecycle](provisioning-and-lifecycle.md).

## Patterns and anti-patterns

| Situation                         | Do                                                | Avoid                                | Why                                          |
| --------------------------------- | ------------------------------------------------- | ------------------------------------ | -------------------------------------------- |
| Collector sees a different serial | uniqueness check, then hold for acknowledgement   | overwrite the record                 | a mis-identified read corrupts two records   |
| Downstream keys                   | stable record ID                                  | serial, MAC or IP                    | a swap or re-address breaks every join       |
| Ownership                         | permission on a service account                   | a wiki rule                          | conventions lapse under pressure             |
| Controller migration              | one writer per artefact, switched in data         | both controllers writing             | the last writer wins at random               |
| Telemetry over a fragile backhaul | edge spool with bounded, counted loss             | central polling only                 | outages become silent gaps                   |
| Controller DR                     | block-level snapshot plus surrounding cloud state | application backup only              | identity and licence binding may not restore |
| Vendor-tethered lifecycle         | L0-L4 matrix per capability, tested               | trust "on-premises" in the datasheet | onboarding and restore fail first            |

## Failure modes and tests

| Failure                                | Signal                                   | Test that proves detection and recovery                          |
| -------------------------------------- | ---------------------------------------- | ---------------------------------------------------------------- |
| Read reaches the wrong device          | duplicate serial or MAC across records   | inject a duplicate in lab; nothing is written, alarm raises      |
| Hardware swap applied silently         | identity changed with no acknowledgement | swap a lab unit; record held until the operator job runs         |
| Human edits a device-owned field       | change log shows a non-collector writer  | edit as an operator token; the write is refused by the validator |
| Spool loss during outage               | drop counter rises; gap in stored series | block backhaul past the cap; drops counted, newest drained first |
| Clock wrong after boot                 | readings dated in the past or future     | boot without time sync; no readings until sync, ingest rejects   |
| Monitoring path credential expires     | runs fail fast; graphs look "slow"       | expire the credential in lab; meta-alarm fires                   |
| Licence fuse or vendor cloud loss      | devices re-queued; onboarding refused    | block the vendor endpoint in lab past the documented grace       |
| Controller restored with a new address | devices stay offline after restore       | restore to a new host in lab; devices reconnect by stable name   |

## Worked example

A fleet of 300 sites is moving off a vendor controller. Classify five capabilities, then choose the DR tier.

| Capability           | Class | Evidence   | Consequence if the vendor cloud is gone                 |
| -------------------- | ----- | ---------- | ------------------------------------------------------- |
| Packet forwarding    | L0    | observed   | none                                                    |
| Configuration push   | L1    | documented | works locally                                           |
| Onboard a new device | L2    | documented | blocked: spares cannot be added                         |
| Restore controller   | L2    | inferred   | application restore may fail; test before relying on it |
| Licence sync         | L3    | documented | fuse starts; management loss at the end of the grace    |

1. Steady state survives; lifecycle events do not. The exit plan must finish inside the fuse window or keep management by another path.
2. The application backup depends on the L2 restore row, so the DR tier is a block-level snapshot of the controller host plus its address and DNS.
3. A restore to a new address would need a change on every site; 300 sites at one visit each sets the cost of skipping a stable name.

## Review checklist

- [ ] Every SoT field has an owner class, enforced as a permission on a named account
- [ ] Automation reads operator-owned fields only
- [ ] Downstream systems key on a stable record ID
- [ ] Identity writes pass an estate-wide uniqueness check; swaps held for acknowledgement
- [ ] One writer per managed artefact named in data
- [ ] Operation ledger has unknown and partial states; committed only after read-back
- [ ] Telemetry gap policy decided; spool atomic, capped, counted, time-gated, acked after storage
- [ ] Monitoring path itself is monitored (credentials, ingest refusals, run outcome)
- [ ] L0-L4 dependency matrix per capability, with evidence state; licence fuse window known
- [ ] Controller identity elements listed; DR tier preserves them; restore preconditions stored with each backup
- [ ] Out-of-band path independent of the managed plane; vendor artefacts mirrored locally

## Further reading

Links checked 2026-10-29.

- [nautobot-perms]: Nautobot object-based permissions and constraints; how to enforce field ownership on accounts.
- [vmagent]: vmagent on-disk buffering for unreliable networks and its size cap.
- [rfc5905]: NTPv4; the time base that gated telemetry depends on.
- [rfc2132]: DHCP options including vendor-specific information (option 43).
- [ebs-snapshots]: block-level point-in-time snapshots on one cloud platform.
- [strangler-fig]: Martin Fowler on replacing a legacy system incrementally.
- [sre-monitoring]: SRE book on symptoms, causes and black-box monitoring.
- [DiffSync](https://github.com/networktocode/diffsync): a library for comparing and synchronising two data sources with explicit conflict handling.

[nautobot-perms]: https://docs.nautobot.com/projects/core/en/stable/user-guide/administration/guides/permissions/
[vmagent]: https://docs.victoriametrics.com/victoriametrics/vmagent/
[rfc5905]: https://www.rfc-editor.org/rfc/rfc5905.html
[rfc2132]: https://www.rfc-editor.org/rfc/rfc2132.html
[ebs-snapshots]: https://docs.aws.amazon.com/ebs/latest/userguide/ebs-snapshots.html
[strangler-fig]: https://martinfowler.com/bliki/StranglerFigApplication.html
[sre-monitoring]: https://sre.google/sre-book/monitoring-distributed-systems/
