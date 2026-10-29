---
Title: Automation engineering and safe execution
Category: reference
Status: current
Authority: authored-guidance
Scope: Shared by skill-network-architect and skill-systems-architect
Last reviewed: 2026-10-29
Summary: >-
  How to design automation that changes network or system state: intent and ownership, reconciliation, validation tiers including configuration-model
  checks, fleet limits, canary arithmetic, failure modes and a review checklist.
---

# Automation engineering and safe execution

## Contents

- [Scope](#scope)
- [Decision rules](#decision-rules)
- [Validation tiers](#validation-tiers)
- [Patterns and anti-patterns](#patterns-and-anti-patterns)
- [Failure modes and tests](#failure-modes-and-tests)
- [Worked example](#worked-example)
- [Review checklist](#review-checklist)
- [Further reading](#further-reading)

---

## Scope

- Any automation that writes: configuration pushes, provisioning, fleet upgrades, controller jobs, reconciliation loops.
- Both domains. Network transports and systems tooling are listed under Decision rules.
- Cutover waves and change classes live in each pack's migration reference. Code quality lives in skill-coder.
- Platform specifics stay with the platform pack: skill-smc (SMC, ansible-wifi), skill-cambium, skill-mikrotik, skill-nautobot, skill-openwisp.

## Decision rules

Intent and ownership:
- Define the intent schema, identities, dependencies and one authoritative writer per field before choosing a controller.
- Intent may live in Nautobot, NetBox, Git, a database or a validated file. The store does not decide the architecture.
- Prefer, in order: an existing supported capability, a supported extension, a maintained FOSS adapter, then custom code for a proven gap.
- Use stable identities, never display names.

Reconciliation:
- Separate discovery, candidate build, approval where required, apply and verify.
- Detect a no-op before connecting to every target.
- Protect concurrent writers with locks, version or ETag checks, or an equivalent supported mechanism.
- Declare handling for stale observations, missing inventory, duplicate identity, partial apply and unsupported capability.
- A dry run may still read secrets, call APIs or skip unsupported paths. Read the adapter's documentation.

Transport and tooling:
- Network: Ansible network collections, Nornir, Netmiko, NAPALM, NETCONF/RESTCONF, gNMI, vendor APIs.
- Systems: image pipelines, package repositories, Ansible/Salt/Puppet, OpenTofu, cloud-init, PowerShell, platform APIs.
- Choose a structured interface over screen scraping when the platform supports one.
- Model candidate, running and startup state, atomicity, and commit-confirm or equivalent recovery.
- Pin images and dependencies. Protect state and plan files. Record reboot needs and dependency order.

Fleet limits (numbers are arithmetic, not fleet facts):
- Set a runtime budget, bounded concurrency, per-target timeout, overall deadline, retry classes and maximum attempts.
- Retry transient reads conservatively. A timed-out write is an unknown outcome until queried.
- Canary detection: P(defect on fraction p seen in n random canaries) = 1 - (1 - p)^n.
  - Required n >= ln(1 - C) / ln(1 - p). At C = 95%: p = 50% needs 5; 20% needs 14; 10% needs 29.
  - Defects follow strata (model, version, site or host type). Cover every stratum before enlarging a random sample.
- Fleet wall time ~ max(N / concurrency x p95 per-target time, N / rate limit) + slowest target + retries.
- Cap a batch at what the team can recover inside the window. Re-measure when the population grows.
- Journal target ID, old and candidate revision, operation ID, status and verification. Resume from the journal, not from loop position.

Security and recovery:
- Never put keys or passwords in examples, logs, process arguments or artefacts.
- Use least-privilege credentials, verified host identity and an approved secret store.
- Keep out-of-band access and break-glass identity independent of the service being changed.
- Configuration rollback, traffic rollback and data recovery are three different things. Data changes may need forward repair.

Test design for automation and acceptance:
- One operation per test. Each test sets up its own state, performs one write or one change, asserts the result and cleans up. A test that depends on
  the state another test left behind fails or passes for reasons nobody can read.
- Isolate tests from each other and from production: separate targets, accounts or namespaces, and no shared mutable fixture between tests.
- Give every check a negative control: an input or target where the check must fail. A check that has never failed may be vacuous (see
  [architecture method](architecture-method.md#decision-rules)).
- Assert which mechanism acted. A refusal from a permission layer and a refusal from a validator look alike; read the audit trail for the acting
  identity and the component that refused.
- Turn every real incident into a regression test that asserts the behaviour (what is refused or withheld), not incidental output text.

## Validation tiers

Name the tier each check belongs to. A pass at one tier says nothing about a higher one.

```text
VALIDATION TIERS BEFORE A WRITE: each tier must pass before the next one runs

+-------------+   +--------------+   +-----+   +--------+   +------------+
| static lint |-->| config model |-->| lab |-->| canary |-->| production |
| and schema  |   | verification |   |     |   |        |   | batches    |
+-------------+   +--------------+   +-----+   +--------+   +------------+
                         ^                         ^              ^
                         |                         |              |
                  candidate configs        state assertions before and after
                  (no device access)       each step (collected live state)
```

Configuration-model verification is a named step for network changes:
- Batfish builds a model from device configurations, without device access. VERIFIED_PRIMARY, upstream README read 2026-10-29.
  - Use it for reachability, ACL and firewall change impact, routing policy, and current-versus-planned equivalence.
  - Licence Apache-2.0, checked on the repository 2026-10-29. Latest release seen: v2026.08.27.
- SuzieQ polls and normalises live state, then runs assertions on it. VERIFIED_PRIMARY, upstream README read 2026-10-29.
  - Use it to assert BGP, OSPF and interface state before and after each step. Vendor coverage is listed in its README.
  - Licence Apache-2.0, checked on the repository 2026-10-29. Latest release seen: v0.24.0 (2025-05-09).
- Both model or collect what they support. An unsupported feature is invisible to them, so list it as untested.
- Systems equivalent: plan output (OpenTofu `plan`), Ansible check mode with diff, image tests. The same tier rules apply.

```text
RECONCILIATION LOOP: intent and observation meet only in the plan

+------------------+     +------------------+
| intent + owner   |     | observed state   |
| (one writer per  |     | (read-only       |
| field)           |     | collection)      |
+------------------+     +------------------+
          |                        |
          +-----------+------------+
                      |
                      v
            +------------------+   no-op   +------+
            | bounded plan     |---------->| done |
            | diff per target  |           +------+
            +------------------+
                      | changes
                      v
            +------------------+   +--------+   +---------+
            | apply via tiers  |-->| verify |-->| journal |
            +------------------+   +--------+   +---------+
```

## Patterns and anti-patterns

| Situation                     | Do                                       | Avoid                            | Why                                              |
| ----------------------------- | ---------------------------------------- | -------------------------------- | ------------------------------------------------ |
| Intent and telemetry disagree | raise a finding to the field's writer    | let a collector overwrite intent | observation is not ownership                     |
| Write times out               | query the outcome by operation ID        | blind retry                      | a duplicate write can break a working target     |
| First fleet run               | canary one target per stratum, then soak | a random 5% sample               | stratum defects hide from random samples         |
| Platform has commit-confirm   | use it with a timer above verify time    | rely on a manual revert          | the management path may be the thing that breaks |
| Estimating runtime            | measure p95 per phase on real targets    | extrapolate from one lab device  | the slow tail sets the window                    |
| Config change on a network    | run config-model checks first            | treat "push succeeded" as proof  | a valid push can still drop traffic              |
| Writing a test suite          | one operation per test, own setup and cleanup | chain tests through shared state | order-dependent passes hide defects              |

## Failure modes and tests

| Failure                            | Signal                                                 | Test that proves detection and recovery                         |
| ---------------------------------- | ------------------------------------------------------ | --------------------------------------------------------------- |
| Partial apply on a target          | journal shows apply without verify                     | kill the run mid-batch in lab; resume from journal              |
| Two writers fight over one field   | value flaps between revisions                          | run both writers in lab; expect a lock or version refusal       |
| Stale observation drives a change  | plan built from data older than its freshness limit    | feed an old snapshot; expect refusal                            |
| Management path lost after a write | target stops answering; service may still pass traffic | lab change that drops the mgmt VLAN; commit-confirm must revert |
| Credential or secret leaks to logs | secret pattern in logs or argv                         | grep run logs and process list in a test run                    |
| Rate limit or API quota hit        | 429 or throttling errors rising                        | run at full concurrency against a staging API                   |
| Vacuous check passes forever       | check has no recorded failing input                    | run it on a negative control; it must fail                      |

## Worked example

Fleet of 300 sites, 4 router models x 2 firmware versions = 8 strata. Measured p95 per target 40 s. Concurrency 10. API limit 2 targets/s.

| Step                             | Arithmetic                                                 | Result               |
| -------------------------------- | ---------------------------------------------------------- | -------------------- |
| Concurrency-bound time           | 300 / 10 x 40 s                                            | 1,200 s              |
| Rate-bound time                  | 300 / 2 per s                                              | 150 s                |
| Wall time                        | max(1,200, 150) + slowest target 180 s + 10% retries 120 s | 1,500 s = 25 min     |
| Canary, stratum-based            | one per stratum                                            | 8 targets            |
| Same 8 as a random sample        | 1 - (1 - 0.2)^8 for a defect on 20% of sites               | 83% chance to see it |
| Random sample for 95% at p = 20% | ln(0.05) / ln(0.8) = 13.4                                  | 14 targets           |

- The stratum canary covers every model and firmware with 8 targets. A random 14 covers only common defects.
- Budget the window on 25 min plus rollback time, not on the lab best case.

## Review checklist

- [ ] Intent source and one writer per field named
- [ ] No-op detected before any connection to targets
- [ ] Validation tier stated for every check; config-model step run or marked untested
- [ ] Runtime budget, concurrency, timeouts, retries and deadline set from measured p95
- [ ] Timed-out writes held as unknown until queried
- [ ] Canary covers every stratum; gates and abort triggers written
- [ ] Journal fields defined; resume works from the journal
- [ ] No secret in logs, argv or artefacts; break-glass path independent
- [ ] Evidence claim stated: generated, applied, accepted, or service verified
- [ ] Tests isolated, one operation each; every check has a negative control on record

## Further reading

All links resolved 2026-10-29.

- [Batfish repository](https://github.com/batfish/batfish): what the configuration model can answer, and supported vendors.
- [SuzieQ documentation](https://suzieq.readthedocs.io/en/latest/): poller, normalised tables and assertions.
- [RFC 6241 NETCONF](https://www.rfc-editor.org/rfc/rfc6241.html): candidate datastore, validate and confirmed commit.
- [Ansible check mode and diff](https://docs.ansible.com/projects/ansible/latest/playbook_guide/playbooks_checkmode.html): what a dry run proves.
- Ansible network best practices, inventory and connection examples:
  - <https://docs.ansible.com/projects/ansible/latest/network/user_guide/network_best_practices_2.5.html>
- [OpenTofu documentation](https://opentofu.org/docs/): plan, state and drift for provisioning.
- [SRE workbook: Canarying releases](https://sre.google/workbook/canarying-releases/): canary against a control population.
- [SRE book: Eliminating toil](https://sre.google/sre-book/eliminating-toil/): which repeat work deserves automation.
