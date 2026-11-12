# Lenses and translation: business, technical, financial and management

## Scope

Every management-facing deliverable (deck, document, workbook, one-pager) must let four kinds of reader find what they need: someone who thinks in outcomes (business), someone who needs to know how it
works (technical), someone who weighs cost and return (financial), and someone who must decide, resource and track it (management). A technical author tilts the whole deliverable technical; the
audience then reads "complex and expensive" whatever the merit. This reference gives the fixed overlay that prevents that, the chain that translates a technical point into the other three views, and
the check that finds tilt.

## Contents of this reference

- [The four lenses](#the-four-lenses)
- [Mapping to published frameworks](#mapping-to-published-frameworks)
- [The translation chain](#the-translation-chain)
- [The translation table](#the-translation-table)
- [Applying the overlay to a deliverable](#applying-the-overlay-to-a-deliverable)
- [The lens coverage check](#the-lens-coverage-check)
- [The lens mind map](#the-lens-mind-map)
- [Failure modes](#failure-modes)
- [Worked example](#worked-example)

## The four lenses

Each item (a program step, a feature, a recommendation, a section) is described once per lens. A lens that cannot be filled is shown as an explicit `GAP: <reason and who closes it>`; it is never
omitted.

| Lens       | The reader asks                                          | Fill with                                                             | Never                                                |
| ---------- | -------------------------------------------------------- | --------------------------------------------------------------------- | ---------------------------------------------------- |
| Business   | What does this change for the organisation, its          | The outcome in the audience's words, the requirement it serves, who   | Component names, protocol names, internal acronyms   |
|            |   customers and its competitiveness? Which requirement   |   benefits, the risk to the business if it is not done                |                                                      |
|            |   does it serve?                                         |                                                                       |                                                      |
| Technical  | How does it work, what does it depend on, and how do we  | What changes, how it is tested, dependencies, constraints, version    | Detail beyond what the reader needs to trust the     |
|            |   know it works?                                         |   and date of the evidence                                            |   claim (the rest goes underneath or in an appendix) |
| Financial  | What does it cost, what does it save or avoid, who bears | One-off and recurring cost, the saving or avoided cost, the basis of  | An invented or rounded-to-look-good number           |
|            |   it, and how sure are we?                               |   the estimate, the evidence label, payback, or `to be counted` with  |                                                      |
|            |                                                          |   an owner and a date                                                 |                                                      |
| Management | What must I decide, who owns it, by when, and what could | The decision or ask, the owner, the milestone and date, status as at  | Status with no decision, or a date with no owner     |
|            |   go wrong?                                              |   a day, dependencies and resources, the top risk and its mitigation  |                                                      |

## Mapping to published frameworks

The overlay is not new: the UK Treasury "five case model" business case asks five questions of any proposal (Strategic: is there a robust case for change; Economic: best value for money; Commercial: is it commercially
viable; Financial: is it financially viable; Management: is it achievable), and ISO/IEC/IEEE 42010 organises description around stakeholder concerns, with a viewpoint and a view per concern and decisions recorded against
the concerns. Mapping used here (the lead's inference, not a published method; apply the public-sector guidance proportionately):

| Lens | Five case model | Architecture view |
| --- | --- | --- |
| Business | Strategic case (the case for change, the requirements served) | the stakeholder concerns the view answers |
| Financial | Economic case (value for money) and Financial case (affordability, funding) | not covered by the standard; add cost and return |
| Management | Management case (delivery, risks, milestones) and Commercial case (suppliers, contracts) | decisions and rationale recorded against concerns |
| Technical | outside the five cases (they assume a solution) | the viewpoint that specifies how the technical view is built |

Design rule: list the audience's concerns first, then give each concern one view from this table, so every concern has an answer and no lens is filled for its own sake.

## The translation chain

Translate a technical statement by walking six links, and stop only when the last link is a decision:

1. **Feature**: what it is, in technical words.
2. **Capability**: what it lets the organisation do that it could not.
3. **Outcome**: what changes for the business or customer.
4. **Value**: why that matters (availability, speed, compliance, competitiveness, risk).
5. **Cost**: what it costs to build and run and what it saves or avoids, labelled by evidence.
6. **Decision**: what the audience must approve, fund, or accept, by when.

If a link cannot be written, that is the finding: the item has no outcome (question the item), no cost basis (mark `to be counted`), or no decision (the audience may not be the right one).

## The translation table

Keep one table per project from `templates/translation-table.md`, filled before the build and reused across deliverables.

| Technical statement                       | Capability                     | Business outcome           | Financial effect                    | Management ask or risk                 | Evidence    |
| ----------------------------------------- | ------------------------------ | -------------------------- | ----------------------------------- | -------------------------------------- | ----------- |
| A box rolls back a failed update          | Updates stop being a visit     | Sites stay up through      | Fewer visits: to be counted, owner  | Approve a canary on two sites by date  | USER_STATED |
|   by itself                               |                                |   a change                 |   and date                          |                                        |             |
| Health is reported from every device to   | Faults are seen before         | Fewer and shorter outages  | Fewer escalations: to be counted    | Approve the alert path to the          | UNVERIFIED  |
|   one place                               |   customers call               |                            |                                     |   operations team                      |             |

## Applying the overlay to a deliverable

- **Deck:** the opening slides carry business, financial and management views (the answer, the cost and the decision); technical views are one level down, each slide with a one-line pointer to its
  technical detail. Where a slide is mainly technical, add a four-line strip (Business, Technical, Financial, Management) so the other three views are visible on the same slide.
- **Document:** the executive summary is written in the first three lenses; the technical lens is a section or an appendix, linked from each claim.
- **Workbook:** one row per item with four lens columns; a summary sheet first; the technical column last.
- **Weighting by audience:** a sponsor wants business, financial and management heavy; a technical lead wants technical and management; a customer wants business and financial. All four lenses still
  appear for every item, in the audience's order.

## The lens coverage check

`lens_coverage.py` reads the content spec (`templates/lens-spec.md`, one row per item and one cell per lens) and reports:

- items with a lens cell empty and not marked `GAP`;
- the share of items filled per lens, and the share of words per lens;
- tilt: any lens filled in fewer than 70% of items, or one lens holding more than 55% of the words, are conventions (`UNVERIFIED`) to tune per project;
- cells that repeat another lens's text (a faked lens);
- a `GAP` without an owner.
It reads text only and cannot judge quality; a reader reads the output as a prompt, then fixes the content.

## The lens mind map

For a one-glance check, draw the item as a mind map (see mind-maps.md and `templates/lens-mindmap.md`): the root is the decision; four branches, Business, Technical, Financial, Management; under each, one line per link
of the translation chain; every unknown is a `GAP: <reason and owner>` leaf. A branch with no leaves is a missing lens.

## Failure modes

- Translating by adding adjectives ("robust", "streamlined") instead of an outcome and a number or a gap.
- The business lens carrying component names or acronyms the audience does not use.
- A financial lens with a figure no one can trace; fix by `to be counted` plus the data request.
- A management lens with a status and no decision, or a date and no owner.
- All four lenses present on the summary and only technical beneath it; the overlay must hold at item level.
- Treating the audience's request for cost savings as met by the technical lens ("simpler", "fewer parts") without the financial view.

## Worked example

Item: a lab-proven recovery path for a remote box. Technical: the box boots a fallback image when an update fails, tested on a bench device, results as at a date. Business: sites keep running through
a software change, which serves the requirement for availability. Financial: avoids visits for failed updates; the number of visits has not been counted, so `to be counted`, owner, date; the build
effort is known. Management: approve a canary on two sites by a date, owner named, top risk a stuck update on a remote site mitigated by a manual recovery card. Coverage check: four lenses filled, one
`GAP` with an owner.

## Plain words and honest claims (12 Nov 2026)

Source: apn enterprise-strategy program pack, 12 Nov 2026 (commits e743df34 to 09068983; operator review in session bba30cc3).

- No shorthand that needs another page or a reference: "levels 1 to 6", "voice first", step codes leading a line ("these numbers will
  make no sense") and vague verbs ("restart themselves": say a frozen box is reset by its watchdog). Plain words lead; a code may follow,
  small.
- A benefit line carries the proof state of what delivers it: "designed to", "tests to come", "once running". A timeline that says boxes
  "recover on their own" while the how-it-works page shows no level fully proven over-promises.
- Drop figures that will be redone ("all of it will be done again from scratch, so don't give them false hopes"): a count from a build
  that is being replaced reads as a commitment.
- A field finish date that depends on site visits is not a commitment: give the target for the image to be ready and say the site dates
  come from the visit schedule, run by run.

