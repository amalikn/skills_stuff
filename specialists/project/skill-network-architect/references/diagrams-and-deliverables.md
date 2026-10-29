---
Title: Diagrams and architecture deliverables
Category: reference
Status: current
Authority: authored-guidance
Scope: Shared by skill-network-architect and skill-systems-architect
Last reviewed: 2026-10-29
Summary: >-
  Which views to draw, the ASCII diagram conventions both packs use, a diagram review checklist, the architecture pack and its arc42 and C4 mapping,
  the skill-drawio handoff and evidence hygiene.
---

# Diagrams and architecture deliverables

## Contents

- [Scope](#scope)
- [Decision rules](#decision-rules)
- [ASCII diagram conventions](#ascii-diagram-conventions)
- [Diagram review checklist](#diagram-review-checklist)
- [Architecture pack](#architecture-pack)
- [Drawio handoff](#drawio-handoff)
- [Evidence hygiene](#evidence-hygiene)
- [Further reading](#further-reading)

---

## Scope

- What to draw, how to draw it in plain text, how to check a drawing, and what a full deliverable contains.
- Rendered diagrams are skill-drawio's job. This file owns the meaning; skill-drawio owns the layout.
- Templates referenced: [design](../templates/design.md), [decision record](../templates/decision-record.md), [change](../templates/change-and-validation.md), [handoff](../templates/handoff.md).

## Decision rules

- Draw one concept per diagram. Split views when combining them hides meaning.
- Draw current and target state as separate diagrams. Never mix them in one view.
- Mark each item planned, observed, unknown or retired in text. Colour alone carries no meaning.
- Two drawn lines do not prove separate ducts, carriers, chassis or power. Say what was verified.
- Show reverse paths for stateful flows, and draw management and out-of-band planes explicitly.

| View     | Answers                               | Typical content                                   |
| -------- | ------------------------------------- | ------------------------------------------------- |
| Physical | what is connected to what, where      | racks, power feeds, cables, ducts, radios         |
| Logical  | how traffic is segmented and routed   | VLANs, VRFs, subnets, routing domains             |
| Traffic  | which flows cross which path          | source, destination, protocol, direction          |
| Trust    | where policy is enforced              | zones, boundaries, enforcement points             |
| Failure  | what fails together and what survives | shared-risk groups, failover paths                |
| Recovery | how service comes back                | bootstrap order, independent access, restore path |

## ASCII diagram conventions

Both packs use these rules for every fenced `text` diagram.

| Element       | Convention                                                                                         |
| ------------- | -------------------------------------------------------------------------------------------------- |
| Character set | ASCII only; no box-drawing or arrow glyphs                                                         |
| Width         | 110 columns or fewer                                                                               |
| Title         | first line, upper case name, a colon, then what the reader should see                              |
| Box           | `+----+` corners and vertical-bar sides; one space of padding inside each side                     |
| Arrow         | `-->` and `<--` horizontal; `v` and `^` vertical; arrow points in the request or traffic direction |
| Failure       | `X` on the failed element or link                                                                  |
| Boundary      | a full line of `====` (trust) or `::::` (failure domain) carrying its label                        |
| Legend        | one line under the diagram whenever a symbol beyond boxes and arrows is used                       |
| Alignment     | character-exact; check each block against a column ruler before handing it over                    |

```text
TRUST AND FAILURE VIEW (example): primary WAN lost; traffic moves to the secondary

+---------+   +-------------+
| clients |-->| site router |
| VLAN 20 |   | 2 uplinks   |
+---------+   +-------------+
                 |       |
==== trust boundary: site firewall (inbound denied, listed outbound allowed) ====
                 |       |
                 X       |
                 |       v
        +----------+  +----------+
        | ISP-A    |  | ISP-B    |
        | fibre 1G |  | 4G 50M   |
        +----------+  +----------+

Legend: --> traffic direction   X failed link   ==== trust boundary, labelled
```

## Diagram review checklist

Run it before any diagram is handed over. The general items paraphrase the idea of the C4 model review checklist (credit below).

General:
- [ ] Title states the view and the scope; current or target is explicit
- [ ] Every element has a name and a type (device, service, zone, link)
- [ ] Every arrow has a label or an obvious meaning, and points in the stated direction
- [ ] Technology is named where it matters (protocol, medium, port)
- [ ] Each symbol is in the legend; status is in text, not only colour
- [ ] Nothing is drawn as fact that was not observed or decided

Network and systems items:
- [ ] Every link shows medium, speed and VLAN/VRF where known
- [ ] Trust zones are bounded and each boundary names its enforcement point
- [ ] Failure domains and shared-risk groups are marked
- [ ] Management and out-of-band paths are drawn, or stated as absent
- [ ] Redundant paths say what proves them separate (survey, carrier record) or say UNVERIFIED
- [ ] ASCII blocks pass the conventions above: width, ruler check, legend

## Architecture pack

A full engagement delivers these items. A narrow question delivers the decision and its evidence only.

| Pack item                         | Template                              | arc42 section                      | C4 view               |
| --------------------------------- | ------------------------------------- | ---------------------------------- | --------------------- |
| Decision and outcome              | design s1                             | 1 Introduction and goals           | system context        |
| Requirements and constraints      | requirements-and-constraints          | 1 goals, 2 constraints, 10 quality | -                     |
| Evidence, current state, unknowns | current-state-discovery               | 3 Context and scope                | landscape             |
| Target views and interfaces       | design s4-s6, interface-contract      | 5 Building blocks, 7 Deployment    | container, deployment |
| Failure and recovery behaviour    | failure-mode-analysis, capacity-model | 6 Runtime, 8 Concepts              | dynamic               |
| Decisions                         | decision-record                       | 9 Architecture decisions           | -                     |
| Risks                             | risk-register                         | 11 Risks and technical debt        | -                     |
| Waves, canary, rollback           | change-and-validation                 | -                                  | -                     |
| Acceptance                        | test-and-acceptance-plan              | 10 Quality                         | -                     |
| Operations and learning           | post-incident-review                  | -                                  | -                     |

- arc42 has 12 sections, from goals to glossary. VERIFIED_PRIMARY, [arc42 overview](https://arc42.org/overview), checked 2026-10-29.
- C4 is software-centric. Use its context and deployment views for infrastructure; keep RF and cabling detail in separate views.
  - VERIFIED_PRIMARY, [c4model.com](https://c4model.com/), checked 2026-10-29.
- Template values are examples. They are never discovered facts.

## Drawio handoff

- Supply stable component IDs, typed links, flow direction, boundary and failure-domain membership, labels and status.
- Ask skill-drawio to render and to inspect the export. It may ask either architect to resolve an ambiguity.
- Check whether a drawing is generated or hand-edited before changing it. Update the source map; never regenerate over hand edits.
- After rendering, check each arrow against the interface contract. The renderer does not judge architecture content.
- No draw.io binary, generator or proprietary stencil is required by these packs.

## Evidence hygiene

- Keep secrets, customer identifiers and raw infrastructure dumps out of reusable skill files.
- Keep project evidence in the project. Link it by stable ID and timestamp.
- Every report states population, time range, unit and freshness.
- For ansible-wifi reports separate collector output, aggregation, interpretation and recommendation. Field meaning belongs to skill-smc.
- Do not call a report row an outage without a validated signal and time correlation.

## Further reading

All links resolved 2026-10-29.

Frameworks:
- [C4 model](https://c4model.com/): abstraction levels and notation-independent diagram rules.
- [C4 model review checklist](https://c4model.com/diagrams/checklist): source of the general checklist idea above (CC BY 4.0, Simon Brown; paraphrased).
- [arc42 overview](https://arc42.org/overview) and [arc42 documentation](https://docs.arc42.org/home/): section-by-section guidance.
- [ADR resources](https://adr.github.io/) and [MADR template](https://adr.github.io/madr/): decision record formats.

Diagrams as code:
- [Structurizr documentation](https://docs.structurizr.com/): several C4 views generated from one model.
- [Mermaid](https://mermaid.js.org/) and [PlantUML](https://plantuml.com/): text-defined diagrams that diff in review.
