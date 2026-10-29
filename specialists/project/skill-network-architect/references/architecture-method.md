---
Title: Architecture method
Category: reference
Status: current
Authority: authored-guidance
Scope: Shared framework for skill-network-architect and skill-systems-architect
Last reviewed: 2026-10-29
Summary: >-
  The shared framework: engagement modes, the end-to-end flow mapped to templates and helpers, evidence labels and layers, decision rules and formulas,
  a copyable checklist per mode, and the structure every domain reference follows.
---

# Architecture method

## Contents

- [Scope](#scope)
- [Evidence labels and layers](#evidence-labels-and-layers)
- [Engagement modes](#engagement-modes)
- [End-to-end flow](#end-to-end-flow)
- [Decision rules](#decision-rules)
- [Quantitative rules](#quantitative-rules)
- [Mode checklists](#mode-checklists)
- [Domain reference structure](#domain-reference-structure)
- [Further reading](#further-reading)

---

## Scope

- This file is the framework for both architect packs. Read it first on every task.
- It defines how to work. Domain references define what is true in each domain.
- Scale the output to the decision. A narrow question gets one answer and its evidence; a site migration gets the full flow.
- Architecture advice never authorises a change. Existing task authorisation governs every write.

## Evidence labels and layers

Label every load-bearing fact. A label describes where the fact came from, not whether the design is right.

| Label              | Meaning                                                                                  | Example                                 | Can it close an acceptance criterion?     |
| ------------------ | ---------------------------------------------------------------------------------------- | --------------------------------------- | ----------------------------------------- |
| VERIFIED_PRIMARY   | Read from the system, or from the primary standard or vendor page, with date and version | `show` output, RFC text                 | yes, at the layer it was observed         |
| VERIFIED_SECONDARY | From a reliable second source                                                            | inventory export, vendor blog           | no; confirm before a change               |
| USER_STATED        | Told by an owner, not checked                                                            | "the backup link is a separate carrier" | no; name the check that would confirm it  |
| UNVERIFIED         | Assumed or inferred                                                                      | typical default timer                   | no; a decision resting on it needs a test |

Evidence also has a layer. A lower layer never closes a criterion that needs a higher one.

```text
EVIDENCE LAYERS: weakest on the left, strongest on the right

+--------+   +--------------+   +-----+   +--------+   +------------------------+
| design |-->| static and   |-->| lab |-->| canary |-->| production observation |
| review |   | model check  |   |     |   |        |   | at the user outcome    |
+--------+   +--------------+   +-----+   +--------+   +------------------------+
```

- Static: lint, schema, the `just` helpers. Model: configuration analysis such as Batfish ([automation and safety](automation-and-safety.md)).
- "Generated", "applied", "API accepted" and "service verified" are different claims. Say which one you have.

## Engagement modes

Pick one mode per request; a request may change mode when evidence changes. Mode names match the SKILL.md Start Here step.

| Mode       | Trigger                                           | Work product                                 | Exit evidence                                              |
| ---------- | ------------------------------------------------- | -------------------------------------------- | ---------------------------------------------------------- |
| Discovery  | the current state is unknown or disputed          | inventory, dependency map, unknowns          | coverage stated; every unread target listed as unknown     |
| Design     | a new service, site or platform                   | requirements, options, target design, ADR    | chosen option traced to requirements                       |
| Review     | an existing design or estate is questioned        | findings ranked by service impact            | each finding tied to an observation                        |
| Incident   | service is degraded now                           | fault domain, next safest check, restoration | restoration measured; cause stays provisional until proven |
| Migration  | state must move from A to B                       | waves, cutover, rollback, acceptance         | rehearsal passed; per-wave gates recorded                  |
| Automation | a tool will change state                          | contract, reconciliation, failure policy     | no-op, failure and recovery tests pass                     |
| Capacity   | demand, growth or failure headroom is in question | demand and failure-scenario model            | units, assumptions and limiting resource explicit          |

## End-to-end flow

```text
END-TO-END FLOW: every stage has a form; any stage may loop back to DISCOVER

+----------+   +---------+   +--------+   +--------+   +--------+   +--------+   +---------+
| DISCOVER |-->| REQUIRE |-->| DESIGN |-->| DECIDE |-->| CHANGE |-->| ACCEPT |-->| OPERATE |
+----------+   +---------+   +--------+   +--------+   +--------+   +--------+   +---------+
      ^                                                                               |
      |                                                                               |
      +------------------ incident, drift or reopen trigger <-------------------------+
```

| Stage    | Question it answers                      | Template                                  | Helpers (network / systems)                                 |
| -------- | ---------------------------------------- | ----------------------------------------- | ----------------------------------------------------------- |
| Discover | what exists, and how sure are we?        | [current-state-discovery]                 | `just ip-plan` on the found plan / host inventory reads     |
| Require  | what must be true, measured how?         | [requirements-and-constraints]            | none; targets come from owners                              |
| Design   | which structure meets the targets?       | [design], [interface-contract]            | `just mtu`, `just link-budget` / `just quorum`, `just ceph` |
| Design   | how much, and what fails together?       | [capacity-model], [failure-mode-analysis] | `just availability` (both) / `just capacity`                |
| Decide   | which option, and what would reopen it?  | [decision-record], [risk-register]        | none                                                        |
| Change   | how do we apply it safely?               | [change-and-validation]                   | canary arithmetic in [automation and safety]                |
| Accept   | did the user outcome change as required? | [test-and-acceptance-plan]                | probes at the user outcome                                  |
| Operate  | who runs it, and what did we learn?      | [post-incident-review]                    | telemetry per the observability reference                   |

[current-state-discovery]: ../templates/current-state-discovery.md
[requirements-and-constraints]: ../templates/requirements-and-constraints.md
[design]: ../templates/design.md
[interface-contract]: ../templates/interface-contract.md
[capacity-model]: ../templates/capacity-model.md
[failure-mode-analysis]: ../templates/failure-mode-analysis.md
[decision-record]: ../templates/decision-record.md
[risk-register]: ../templates/risk-register.md
[change-and-validation]: ../templates/change-and-validation.md
[automation and safety]: automation-and-safety.md
[test-and-acceptance-plan]: ../templates/test-and-acceptance-plan.md
[post-incident-review]: ../templates/post-incident-review.md

- Cross-domain work at any stage uses the [handoff](../templates/handoff.md) and the [collaboration protocol](collaboration-protocol.md).
- Each pack also has domain forms (network: ip-addressing-plan, site-network-design, routing-policy). RUNBOOK.md lists them by stage.

## Decision rules

- Start from service outcomes: users, critical journeys, data classes, owners, budget, horizon and the decision requested.
- Record current, intended and proposed state separately. Never draw intent as fact.
- Ask only questions that can change the decision. Otherwise give a bounded provisional option and the smallest measurement that settles it.
- Every requirement has an ID, owner, target with unit, window, measurement method and consequence of failure.
- Mark each target as a business requirement, a measured baseline or an illustrative assumption.
- Do not impose universal availability percentages, oversubscription ratios, cluster sizes or automation coverage targets ([SRE workbook](https://sre.google/workbook/implementing-slos/)).
- Compare the simplest viable design, a higher-resilience option and a phased option when each is a real alternative.
- Score options on failure coverage, operating effort, staffing, cost of ownership, security, observability and exit cost.
- Document accepted single points of failure. Not every service needs a distributed system.
- Record each decision in an ADR with assumptions, rejected options, consequences and a reopen trigger.
- Do not invent fleet facts, prices, support matrices, entitlements or deadlines. Read version-matched primary sources.

Evidence before commitment:

- Screen feasibility on paper first. List each required function, classify it per candidate and exact version (native, add-on, moved central, not possible) from that version's documentation, and apply
  the rule before buying or benching anything. One required function that is not possible and cannot move elsewhere vetoes the candidate.
- Measure before choosing a platform. Separate investigation (allowed early: inventory, market tests, quotes) from commitment (gated on measured inventory, utilisation and cost). A decision made
  before the evidence is withdrawn, not rejected.
- Compare against the best achievable version of the current state, not today's state. "Do not migrate" or "do not buy" is a valid, successful outcome.
- Fix scoring weights and thresholds before the data arrives. A threshold set after seeing the data is tuned to the answer.
- When a requirement has two readings of different cost, state both and the cost gap, size the expensive reading, label it pending confirmation, and ask what drives it (regulation and contract are
  fixed; preference and convention are negotiable). Oversizing is recoverable; undersizing found after purchase is not.
- Apply the evidence rule to assumed components too. Each one shows why the incumbent capability cannot serve before it enters the design.

Rule outcomes and confirmation:

- Evaluate each rule or acceptance criterion to one of three states: met (confirmed evidence reaches the threshold), unmet, or unclear (the threshold is reachable only with unconfirmed items). A
  boolean result hides missing data.
- Carry the evidence IDs present and the IDs still uncertain with every result. An overall verdict may be "insufficient information".
- Keep proposed and confirmed state apart. Automation and models write proposals; confirmation is an append-only step by a named person or reviewed process; downstream evaluators read only the
  confirmed side.

```text
THREE-STATE RULE OUTCOME: unconfirmed items can make a result unclear, never met

+-----------------+   +------------------------+   yes   +------+
| confirmed items |-->| confirmed >= threshold |-------->| met  |
+-----------------+   +-----------+------------+         +------+
                                  | no
                                  v
+-----------------+   +------------------------+   yes   +---------+
| proposed items  |-->| confirmed + proposed   |-------->| unclear |
| (not confirmed) |   | >= threshold           |         +---------+
+-----------------+   +-----------+------------+
                                  | no
                                  v
                              +-------+
                              | unmet |
                              +-------+
```

AI-assisted pipelines:

- Deterministic core, model at the edge, human at the top. Every step that decides what is true is code that never calls a model; a model may map free text to candidates, draft narrative or critique;
  a person adjudicates.
- Tools a model calls return verifiable facts with a versioned schema, not judgements. The model provider can then change without an engine change.
- Enforce "no model in the core" with a test, and give that test a negative control that proves it can fail.
- A safety backstop must not depend on the component whose failure it guards against, and must not be configurable off.

Checks that cannot fail:

- A vacuous test passes whatever the system does: a data set compared with itself, an assertion on a value the test just wrote, a filter that matched nothing, a check with no failing input on record.
  Treat a check with no demonstrated failure as untested.
- For every new check, run it once on an input that must fail (a negative control) and record the result.
- A test must also tell mechanisms apart. If two mechanisms could produce the same pass or refusal, assert which one acted (audit trail, acting identity).

```text
DEPENDENCY CONTEXT: draw this before choosing products; every arrow means "depends on"

+-------+   +------------------+   +-------------+   +---------+   +-----------------+
| users |-->| business service |-->| application |-->| runtime |-->| compute/storage |
+-------+   +------------------+   +-------------+   +---------+   +-----------------+
                                          |               |
                                          |               |
                                          v               v
                                      +----------+    +-----------------+
                                      | identity |    | network/DNS/NTP |
                                      +----------+    +-----------------+
```

- A redundant component can still share one rack, power feed, DNS service, admin account or update channel. Model the shared item as a series block.

## Quantitative rules

- Carry units through every step. GB is not GiB; Gbit/s is not GiB/s.
- Model four scenarios: normal, maintenance, largest-unit loss, correlated-domain loss.
- Steady-state availability A = MTBF / (MTBF + MTTR). MTTR includes detection, travel, spares and verification.
- Series (all needed): A = A1 x A2 x ... x An. Parallel (any one suffices): A = 1 - (1 - A1) x ... x (1 - An).
  - VERIFIED_PRIMARY, NIST handbook series and parallel models, checked 2026-10-29 (links in Further reading).
  - Both assume independent failures and perfect failover. Run `just availability` for the arithmetic.
- Downtime per year = (1 - A) x 8,760 h: 99% = 87.6 h; 99.9% = 8.76 h; 99.95% = 4.38 h; 99.99% = 52.6 min.
- Error budget = (1 - SLO) x window. Burn rate = observed error ratio / (1 - SLO). 99.9% over 30 days = 43.2 min.
  - VERIFIED_PRIMARY, [SRE workbook: alerting on SLOs](https://sre.google/workbook/alerting-on-slos/), checked 2026-10-29.
- Little's law: items in system = arrival rate x time in system. Use it for queue depth, concurrency and session tables.
- Queue knee (M/M/1): time in system ~ service time / (1 - utilisation). 80% load ~ 5x; 90% ~ 10x.
  - VERIFIED_SECONDARY, [M/M/1 queue](https://en.wikipedia.org/wiki/M/M/1_queue), checked 2026-10-29. Real traffic is burstier; plan for an earlier knee.
- Transfer or restore time = bytes x 8 / (rate x efficiency) + setup + verification. Measure the efficiency.
- Recovery time = detect + decide + provision + transfer + replay + start + validate. A lower bound cannot prove an RTO.
- Cost comparisons include staff, support, energy, spares, bandwidth, training, backup and migration. Never fabricate a current price.

## Mode checklists

Copy the checklist for the chosen mode into the answer. Tick each item or write why it does not apply.

**Discovery**
- [ ] Population, selector and collection window stated
- [ ] Each source labelled, with freshness and targets read / total
- [ ] Every unread target listed as unknown (a sample is a scout)
- [ ] Intent versus observation drift listed, not corrected silently
- [ ] Cheapest discriminating check named for each unknown

**Design**
- [ ] Requirements measurable: unit, window, method, owner
- [ ] Constraints and USER_STATED facts labelled
- [ ] Current and target views drawn separately
- [ ] At least two options compared, including the simplest viable
- [ ] Paper feasibility screen done per candidate and version before any purchase or bench
- [ ] Requirements with two cost readings sized on the expensive one and the driver asked
- [ ] Failure domains and the limiting resource quantified
- [ ] ADR written with a reopen trigger
- [ ] Acceptance tests traced to each requirement

**Review**
- [ ] Scope, owner and revision under review stated
- [ ] Current state labelled; red flags scanned per domain reference
- [ ] Each finding tied to an observation and a requirement
- [ ] Findings ranked by service impact, not by count
- [ ] Shared interfaces sent for peer or specialist review
- [ ] Next measurements named for every open question

**Incident**
- [ ] Symptom, window, affected population and recent changes recorded
- [ ] Observations tagged Observed / Inferred / Unknown
- [ ] One most-likely fault domain with confidence (low / medium / high)
- [ ] One next safest check, read-only first
- [ ] Evidence preserved before any restart or counter clear
- [ ] Restoration measured at the user outcome

**Migration**
- [ ] Independent recovery path proven before the window
- [ ] Waves, gates and abort triggers written
- [ ] Canary covers every stratum (model, version, site type)
- [ ] Point of no return computed from rollback time
- [ ] Rollback rehearsed; forward-repair boundary stated

**Automation**
- [ ] Intent source and one writer per field named
- [ ] No-op detected before touching targets
- [ ] Runtime budget, concurrency, timeouts and retry classes set
- [ ] Timed-out writes treated as unknown until queried
- [ ] Model or lab validation before canary; journal per target
- [ ] Every new check run once against a negative control that must fail

**Capacity**
- [ ] Demand measured at busy hour with units and source
- [ ] Four scenarios modelled (normal, maintenance, unit loss, correlated loss)
- [ ] Limiting resource named now and at the horizon
- [ ] Growth assumption labelled; trigger and lead time set
- [ ] Compared against the best achievable current state; "no change" kept as an option

## Domain reference structure

Every domain reference in both packs uses the same headings, so an agent knows where to look.

| Heading                    | Holds                                                           | Rule                    |
| -------------------------- | --------------------------------------------------------------- | ----------------------- |
| Scope                      | what the file covers and what it routes elsewhere               | 3-6 bullets             |
| Decision rules             | rules with numbers, each with an evidence label and source      | one rule per bullet     |
| Patterns and anti-patterns | table: situation, do, avoid, why                                | named, not generic      |
| Failure modes and tests    | table: failure, signal, test that proves detection and recovery | every row testable      |
| Worked example             | one numeric case, run through a `just` helper where one exists  | real helper output      |
| Review checklist           | `- [ ]` items an agent copies into a review                     | observable items only   |
| Further reading            | primary sources first, one line on why to read each             | link resolved and dated |

- Shared references (method, automation, collaboration, diagrams, tools, research) adapt these headings to their purpose.
- A write-back lands beside the rule it changes, per the SKILL.md write-back contract.

## Further reading

All links resolved 2026-10-29. These serve network and systems work alike.

Structure and documentation:
- [arc42 overview](https://arc42.org/overview): a 12-section architecture document skeleton.
- [C4 model](https://c4model.com/): views that keep each diagram at one level of abstraction.
- [ADR resources](https://adr.github.io/): lightweight decision records and their lifecycle.
- [Nygard: Documenting architecture decisions](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions): the original ADR form.

Trade-off analysis:
- [SEI ATAM collection](https://www.sei.cmu.edu/library/architecture-tradeoff-analysis-method-collection/): scenario-based quality-attribute trade-off reviews.
- [AWS Well-Architected: Reliability pillar](https://docs.aws.amazon.com/wellarchitected/latest/reliability-pillar/welcome.html): failure-domain, recovery and change questions.
- [Azure Well-Architected: Reliability checklist](https://learn.microsoft.com/en-us/azure/well-architected/reliability/checklist): a review checklist to adapt for the Review mode.

Reliability targets and arithmetic:
- [SRE book: Embracing risk](https://sre.google/sre-book/embracing-risk/): availability as a business cost decision.
- [SRE workbook: Implementing SLOs](https://sre.google/workbook/implementing-slos/): turning requirements into measured SLIs and SLOs.
- NIST handbook, series and parallel reliability models:
  - <https://www.itl.nist.gov/div898/handbook/apr/section1/apr181.htm>
  - <https://www.itl.nist.gov/div898/handbook/apr/section1/apr182.htm>
- [Anthropic: Agent Skills best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices): the source of the per-mode checklist pattern.
