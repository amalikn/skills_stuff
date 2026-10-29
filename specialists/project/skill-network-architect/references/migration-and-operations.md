---
Title: Network migration and operations
Category: domain-reference
Status: current
Authority: authored-guidance
Scope: Network architecture
Last reviewed: 2026-10-29
Summary: >-
  Cutovers, change classes, waves, canary and batch sizing, abort and recovery, and operating ownership after delivery, with failure tests, a worked
  example run through `just mtu` and a review checklist.
---

# Network migration and operations

## Contents

- [Scope](#scope)
- [Decision rules](#decision-rules)
- [Patterns and anti-patterns](#patterns-and-anti-patterns)
- [Failure modes and tests](#failure-modes-and-tests)
- [Worked example](#worked-example)
- [Review checklist](#review-checklist)
- [Further reading](#further-reading)

---

## Scope

- Moving network state from A to B: cutovers, readdressing, WAN or tunnel changes, fleet-wide configuration or firmware waves.
- Operating ownership after delivery: alerts, backups, lifecycle, drills, post-incident review.
- Form: [change and validation](../templates/change-and-validation.md). Automation rules: [automation and safety](automation-and-safety.md).
- Target-specific execution: skill-smc (SMC, ansible-wifi), skill-mikrotik, skill-cambium. Automation code: skill-coder.

## Decision rules

Discovery before cutover:
- Inventory current and target paths, management access, addressing, DNS, firewall rules, monitoring and support contacts.
- Prove an independent recovery route works before the change, not during it.
- Order by dependency: addressing before routes; reachability before AAA; policy before publishing; monitoring before traffic.

Change classes (generic; map to the organisation's own process):

| Class     | Use when                                                | Control                                                           |
| --------- | ------------------------------------------------------- | ----------------------------------------------------------------- |
| Standard  | repeatable, proven, small blast radius, tested rollback | pre-approved procedure; still journal and verify                  |
| Normal    | new or larger change                                    | review, rehearsal, scheduled window, named rollback owner         |
| Emergency | restoring service now                                   | smallest fix; record as you go; review and reconcile intent after |

- A failed standard change becomes a normal change until its procedure is fixed.

Waves and timing:
- Per wave write target IDs, prechecks, candidate diff, apply step, wait criteria, service tests, abort threshold and owner.
- Test rollback before relying on it. Keep a journal and the previous known state.
- NETCONF confirmed-commit reverts unless confirmed; default confirm-timeout 600 s. VERIFIED_PRIMARY, RFC 6241 s8.4, checked 2026-10-29.
  - Vendor CLIs differ and some have no equivalent. Set the timer above the slowest verification over the management path.
- Point of no return (PNR) = window end - (rollback time + rollback verification + margin). Past it, forward repair only.

```text
CHANGE WINDOW TIMELINE: past the point of no return (PNR), only forward repair remains

T-7d       T-1d       T0         T0+apply   T0+verify  PNR                  end
|          |          |          |          |          |                    |
rehearse   freeze,    precheck   change     service    point of             window
+ backup   go/no-go   baseline   applied    tests      no return            closes

                      |<------ rollback allowed ------>|<-- forward fix --->|
```

Canary and batch sizing:
- Max batch <= engineers x recoveries per engineer-hour x hours left in the window.
- Random canaries catch only common defects: P(seen) = 1 - (1 - p)^n. At 95%: p = 50% needs 5; 20% needs 14; 10% needs 29.
- A 6-target random canary reliably catches only defects on about 40% or more of the fleet. Pick one canary per stratum instead.
- Canary against a control population (SRE workbook, VERIFIED_PRIMARY, checked 2026-10-29).
- Soak long enough for the slowest cycle: lease renewal, rekey, route refresh, daily job or busy hour.
- Grow batches only while gates pass. Never widen after a skipped or inconclusive gate.

```text
CANARY AND BATCH GATES: widen only after a passed gate; any failed gate stops the run

+---------------+     +---------------+     +---------------+     +---------------+     +---------------+
| canary        |---->| soak          |-G-->| batch 1       |-G-->| batch 2       |-G-->| rest          |
| 1 per stratum |     | slowest cycle |     | small         |     | larger        |     | capped        |
+---------------+     +---------------+     +---------------+     +---------------+     +---------------+
Legend: G = gate (mgmt reachable, SLIs vs control, error budget left, staff free); X = failed gate

X any gate fails:
+---------------------------------------------+
| stop, hold the population, recover, re-plan |
+---------------------------------------------+
```

Abort and recover:
- Abort on lost management access, unexpected route propagation, a failed critical transaction, unbounded errors or too little time to recover.
- A timed-out write is not retried until its outcome is queried.
- Restored configuration is not restored service. Routes, sessions, DNS caches and clients converge later.
- Forward repair may be safer than rollback once dependent systems changed. Record the decision and its authorisation.
- A remote change that can cut the management path needs commit-confirm, out-of-band access or a scheduled revert. Otherwise do not run it remotely.

Operations after delivery:
- Name owners for alerts, configuration backup, certificate and key rotation, firmware lifecycle, spares and restore drills.
- Reconcile emergency changes into intent after stabilisation.
- Review runbooks after a real incident or a platform upgrade.
- Hold blameless reviews on agreed triggers with the [post-incident review](../templates/post-incident-review.md) form.

## Patterns and anti-patterns

| Situation                    | Do                                                           | Avoid                              | Why                                        |
| ---------------------------- | ------------------------------------------------------------ | ---------------------------------- | ------------------------------------------ |
| Tunnel or WAN change         | run `just mtu` on old and new stacks; DF-probe the real path | assuming 1500 end to end           | a new header silently breaks large packets |
| First wave of a fleet change | one canary per model, firmware and site type                 | a random 5%                        | stratum defects hide from random samples   |
| Change near window end       | stop starting targets at the PNR                             | "just one more batch"              | rollback cannot finish in time             |
| Successful canary            | continue through gates; report canary only                   | calling the migration complete     | the canary is not the fleet                |
| Emergency fix applied        | reconcile intent the same week                               | leaving device and inventory apart | the next push reverts the fix              |

## Failure modes and tests

| Failure                                  | Signal                                         | Test                                                            |
| ---------------------------------------- | ---------------------------------------------- | --------------------------------------------------------------- |
| Management path cut by the change        | target unreachable after apply                 | lab change dropping the mgmt VLAN; confirmed-commit must revert |
| Rollback slower than planned             | rollback overruns its budget                   | timed rollback rehearsal on the canary                          |
| MTU shortfall after encapsulation change | large transfers stall; small pings pass        | `just mtu` before; DF-set probe at payload size after           |
| Gate passes on stale data                | SLIs from a dead collector look clean          | check collector freshness as a gate input                       |
| Hidden dependency (DNS, AAA, monitoring) | service fails though the network change passed | dependency list in the MOP; test each after apply               |

## Worked example

Migrating 40 sites from IPoE to PPPoE under an existing WireGuard tunnel. The overlay needs payload MTU 1440.

```json
{"schema_version": 1, "paths": [
  {"id": "old-ipoe-wireguard", "underlay_mtu": 1500, "layers": ["wireguard-ipv4"], "required_payload_mtu": 1420},
  {"id": "new-pppoe-wireguard", "underlay_mtu": 1500, "layers": ["pppoe", "wireguard-ipv4"], "required_payload_mtu": 1440}]}
```

Real output of `just mtu`, run 2026-10-29 (exit 1, findings):

| Path                | payload_mtu | tcp_mss_ipv4 | Finding                                                            |
| ------------------- | ----------- | ---------- | ------------------------------------------------------------------ |
| old-ipoe-wireguard  | 1440        | 1400       | none                                                               |
| new-pppoe-wireguard | 1432        | 1392       | 8 short of 1440; raise the underlay to 1508 or lower the inner MTU |

- Decision before any wave: request baby jumbo (1508) from the carrier, or set the tunnel inner MTU to 1432 and clamp MSS.
- Window 02:00-05:00. Rollback 25 min + verify 10 min + margin 15 min = 50 min. PNR = 04:10.
- Two engineers, 3 site recoveries per hour each, 2 h usable before the PNR: max batch = 2 x 3 x 2 = 12 sites.
- Plan: canary 4 sites (one per router model and access type), soak 24 h past a lease renewal, then batches of 12, 12 and 12.

## Review checklist

- [ ] Independent recovery path proven before the window
- [ ] Change class stated; MOP has per-step rollback or "forward repair only" with reason
- [ ] `just mtu` run for every changed encapsulation; DF probe planned
- [ ] PNR computed from measured rollback time; no target starts after it
- [ ] Canary covers every stratum; soak covers the slowest cycle
- [ ] Batch size capped by recovery capacity, not by ambition
- [ ] Gates read fresh data and include management reachability
- [ ] Owners named for alerts, backups, lifecycle and drills after delivery

## Further reading

All links resolved 2026-10-29.

Rollout and release:
- [SRE workbook: Canarying releases](https://sre.google/workbook/canarying-releases/): canary versus control, population and duration.
- [SRE book: Release engineering](https://sre.google/sre-book/release-engineering/): reproducible builds and staged rollout.
- [SRE book: Eliminating toil](https://sre.google/sre-book/eliminating-toil/): which repeat changes deserve automation.

Change and configuration control:
- [NIST SP 800-128](https://csrc.nist.gov/pubs/sp/800/128/upd1/final): baselines, change control and monitoring as one process.
- [RFC 6241 NETCONF](https://www.rfc-editor.org/rfc/rfc6241.html): candidate datastore, validate, confirmed commit.
- [Ansible check mode and diff](https://docs.ansible.com/projects/ansible/latest/playbook_guide/playbooks_checkmode.html): what a dry run proves.

Incidents and learning:
- [SRE book: Managing incidents](https://sre.google/sre-book/managing-incidents/): roles and handoffs during a failed cutover.
- [SRE book: Postmortem culture](https://sre.google/sre-book/postmortem-culture/): blameless review structure.
- [NIST SP 800-61 Rev. 3](https://csrc.nist.gov/pubs/sp/800/61/r3/final): when a migration incident is also a security incident.
