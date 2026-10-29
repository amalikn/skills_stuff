---
Title: Bidirectional collaboration protocol
Category: reference
Status: current
Authority: authored-guidance
Scope: Shared by skill-network-architect and skill-systems-architect
Last reviewed: 2026-10-29
Summary: >-
  How the two peer architects and the specialist skills hand work to each other: ownership, the handoff and interface contracts, review states,
  disagreement, failure modes and a review checklist.
---

# Bidirectional collaboration protocol

## Contents

- [Scope](#scope)
- [Roles and ownership](#roles-and-ownership)
- [Decision rules](#decision-rules)
- [Review states](#review-states)
- [Patterns and anti-patterns](#patterns-and-anti-patterns)
- [Failure modes and tests](#failure-modes-and-tests)
- [Review checklist](#review-checklist)
- [Further reading](#further-reading)

---

## Scope

- Any request that crosses the network and systems boundary, or needs a platform or tool specialist.
- Both directions: an architect asks a specialist for facts; a specialist asks an architect for a design decision.
- Forms: [handoff](../templates/handoff.md) for the request and reply; [interface contract](../templates/interface-contract.md) for a shared interface.
- This protocol never authorises spawning agents, messaging other chats or sending external messages.

## Roles and ownership

Both architects are peers. The coordinator is chosen per request and owns integration only.

When inventory (intent) and observation disagree about a component, the inventory owner (skill-nautobot) decides intent, the platform pack supplies the observation, and the architect owning that row
records which one is wrong and why. Keep the observed record until the disagreement is resolved.

| Area         | Network owns                           | Systems owns                             | Both review                   |
| ------------ | -------------------------------------- | ---------------------------------------- | ----------------------------- |
| Connectivity | addressing, routing, VLAN/VRF, WAN, RF | host bonding and bridges                 | host uplinks, MTU             |
| Policy       | firewalls, segmentation, NAT           | host firewall, service identity          | trust boundaries              |
| Services     | DNS/DHCP/NTP transport and placement   | identity directory, PKI, OS time client  | DNS and time dependencies     |
| Data         | storage transport paths                | storage, backup, recovery                | backup paths, rebuild traffic |
| Change       | network convergence                    | OS, hypervisor, endpoint lifecycle       | sequencing, failure domains   |
| Placement    | cable plant, patching, radio mounts    | rack, host, PSU and power-feed placement | shared racks, power domains   |

```text
WHO ASKS WHOM: requests go down a line; results and reviews return on the same line

                         +------------------------+
                         | user / project owner   |
                         +------------------------+
                                     |
                         +------------------------+
                         | coordinator for this   |
                         | request (either one)   |
                         +------------------------+
                          |                     |
                    +-----------+  peer   +-----------+
                    | network   |<------->| systems   |
                    | architect |         | architect |
                    +-----------+         +-----------+
                          |                     |
                +--------------------+  +--------------------+
                | equipment packs:   |  | tool packs:        |
                | smc, cambium,      |  | coder, drawio,     |
                | mikrotik           |  | nautobot, openwisp |
                +--------------------+  +--------------------+
```

Either architect may use any specialist; the split above is the usual one, not a rule.

| Specialist     | Architect asks it for                                  | It asks an architect for                                     |
| -------------- | ------------------------------------------------------ | ------------------------------------------------------------ |
| skill-nautobot | intent model, field ownership, inventory relations     | topology meaning, ownership conflicts, reconciliation policy |
| skill-openwisp | registration, monitoring, freshness, alerts            | service impact, telemetry needs, controller scaling          |
| skill-drawio   | render an agreed component and flow map                | missing links, trust zones, failure domains                  |
| skill-coder    | code to a defined contract, with tests                 | interfaces, invariants, failure policy                       |
| skill-smc      | SMC discovery, operations, ansible-wifi report meaning | site architecture, report anomalies, migration impact        |
| skill-cambium  | radio and AP facts per model and firmware              | RF and backhaul design, capacity, resilience                 |
| skill-mikrotik | RouterOS facts and supported operations                | VLAN and routing design, MTU, recovery effects               |

## Decision rules

Handoff:
- Fill the handoff envelope: request ID, sender, recipient, coordinator, mode, objective, scope, exclusions, authorisation.
- Attach evidence with path, version, timestamp, units and evidence label.
- State acceptance checks, stop conditions, runtime budget and where the reply goes.
- The receiver accepts or narrows scope, names missing evidence and replies under the same request ID.
- An acknowledgement is not acceptance evidence.
- Never send secrets; say where an authorised operator obtains them.

Specialists:
- A listed name is an integration contract, not a dependency. Check the skill is installed and read its entry point first.
- Respect its scope, read-only limits and version support. Never invent a tool, permission or API for it.
- Missing specialist: proceed with the generic design and mark specialist facts UNVERIFIED.
- SMC meaning, fleet topology and ansible-wifi report fields are USER_STATED until skill-smc confirms them.

Interfaces:
- One interface contract per boundary: identities, flows, MTU, DNS and time dependencies, budgets, failure behaviour, writer, test.
- Storage adds multipath, latency sensitivity, rebuild traffic and isolation. Hosts add bond mode, bridge/VLAN semantics and failover.
- One authoritative writer per field. Desired state and observed health are separate fields.
- An observation raises a finding; it never rewrites intent or lifecycle state.

Disagreement:
- Never settle a conflict by seniority or tool popularity. Name the measurement that would discriminate.
- Record both positions until the measurement lands. Escalate business trade-offs to the user and continue unaffected work.
- One agent switching perspectives must record each review and must not claim the reviews were independent.

## Review states

```text
REVIEW STATES: acceptance binds to one revision; a material change reopens review

+----------+   +-----------------+   +----------+   +----------+   +-------------+   +----------+
| proposed |-->| evidence-needed |-->| reviewed |-->| accepted |-->| implemented |-->| verified |
+----------+   +-----------------+   +----------+   +----------+   +-------------+   +----------+
     |                                                   |
     v                                                   v
+-------------+                                     +-------------------+
| rejected    |                                     | superseded        |
| reason kept |                                     | old revision kept |
+-------------+                                     +-------------------+
```

## Patterns and anti-patterns

| Situation                      | Do                                           | Avoid                            | Why                                         |
| ------------------------------ | -------------------------------------------- | -------------------------------- | ------------------------------------------- |
| Storage VLAN for a new cluster | one interface contract, both architects sign | each side configures its half    | MTU and failover mismatch hides at the seam |
| Specialist not installed       | generic design, specialist facts UNVERIFIED  | guessing model-specific commands | invented facts read as verified             |
| Peer disagrees on a figure     | name the discriminating measurement          | defer to the louder reviewer     | the measurement settles it once             |
| Report field looks wrong       | ask skill-smc what it measures               | reinterpret the column           | report semantics belong to the pack         |
| Accepted design changes later  | reopen review on the new revision            | edit the accepted copy           | acceptance binds to a revision              |

## Failure modes and tests

| Failure                     | Signal                                   | Test                                                             |
| --------------------------- | ---------------------------------------- | ---------------------------------------------------------------- |
| Two writers for one field   | value flips between tools                | interface contract names one writer; drift check flags the other |
| Handoff lost in a long chat | no reply under the request ID            | coordinator lists open request IDs at each checkpoint            |
| Scope creep in the receiver | reply touches excluded targets           | compare reply targets against the envelope exclusions            |
| Stale evidence in a handoff | timestamps older than the freshness need | receiver rejects evidence past the stated limit                  |

## Review checklist

- [ ] Coordinator named; envelope complete; authorisation quoted
- [ ] Evidence carries path, time, units and label
- [ ] Interface contract exists for every shared boundary, with one writer per field
- [ ] Specialist installed and its entry point read, or its facts marked UNVERIFIED
- [ ] Reply under the same request ID, with validation layer stated
- [ ] Open disagreements recorded with the measurement that would settle them

## Further reading

All links resolved 2026-10-29.

- [Team Topologies key concepts](https://teamtopologies.com/key-concepts): collaboration, X-as-a-service and facilitating modes between owners.
- [SRE book: Communication and collaboration](https://sre.google/sre-book/communication-and-collaboration/): cross-team design reviews and shared ownership.
- [SRE book: Managing incidents](https://sre.google/sre-book/managing-incidents/): explicit roles and clean handoffs under pressure.
- [arc42 section 3: Context and scope](https://docs.arc42.org/section-3/): documenting external interfaces and their owners.
- [C4 model](https://c4model.com/): drawing the boundary each architect owns before negotiating the interface.
- [ADR resources](https://adr.github.io/): recording a cross-domain decision both reviewers can cite.

Optional inbound line for specialist maintainers (paste into a specialist's own instructions if wanted):
- "For connectivity, traffic, RF or convergence design, request skill-network-architect review."
- "For compute, storage, OS, identity, endpoint or recovery design, request skill-systems-architect review."
- "Use the handoff contract, keep specialist ownership, return concrete evidence. Skill availability is not authorisation."
