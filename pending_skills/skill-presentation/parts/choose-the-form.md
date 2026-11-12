# Choose the form: deck, document, workbook, PDF or one-pager

## Scope

Pick the form from the audience and the objective, not from habit. The table below is a synthesis from practice and the 2026-11-12 research (no published source maps audience and objective to form),
so every cell is `UNVERIFIED` until the operator reviews it and a result confirms it. It is a starting point the brief overrides.

## Contents of this reference

- [Rule of thumb](#rule-of-thumb)
- [Decision table](#decision-table)
- [Length and detail](#length-and-detail)
- [One source, several forms](#one-source-several-forms)
- [When not to make a deck](#when-not-to-make-a-deck)

## Rule of thumb

Read alone: a memo (Word) or a one-pager. Discussed live: a short deck. Recurring numbers: a spreadsheet or dashboard. Detailed reference for a technical reader: a document with diagrams. A fixed
  layout for print or
signature: PDF exported from the source. When the decision is the point, put the decision and the options on the first page of whatever form.

## Decision table

| Audience, objective | Inform                  | Align                     | Decide                           | Persuade                   | Report status               | Request resources          |
| ------------------- | ----------------------- | ------------------------- | -------------------------------- | -------------------------- | --------------------------- | -------------------------- |
| Executive sponsor   | One-pager, answer first | Short deck, 3 to 5 slides | Decision memo: options,          | Deck, 5 to 8 slides,       | One-page RAG with           | Memo with cost and benefit |
|                     |                         |                           |   recommendation, cost           |   action titles            |   outcomes first            |                            |
| Sceptical           | Word memo, answer first | Short deck, objections    | Options memo naming              | Memo with evidence and FAQ | Outcomes table,             | Memo with the risks stated |
|   stakeholder       |                         |   stated up front         |   the objection                  |                            |   no narrative              |                            |
| Technical lead      | Word specification      | Document plus diagram     | Decision record                  | Document                   | Dashboard or spreadsheet    | Specification with a       |
|                     |                         |                           |                                  |                            |                             |   cost table               |
| Operations team     | Runbook, checklist      | Short deck plus Q and A   | Not applicable                   | Rarely                     | Dashboard                   | Not applicable             |
| Customer            | One-pager               | Not applicable            | Proposal                         | Benefit-led deck           | Summary                     | Proposal                   |
| Board               | One or two page paper   | Not applicable            | Paper with a clear resolution    | Short deck                 | One-page dashboard          | Paper with an annex        |

## Length and detail

- Deck: one message per slide; the titles read alone tell the story; 5 to 8 slides for a decision, with an appendix for detail.
- Memo: one to two pages answer first; the technical lens in an appendix.
- Workbook: a summary sheet first, one table per sheet, units and sources noted.
- Detail goes underneath the first screen or page, never before the answer.

## One source, several forms

Keep one content source (markdown plus a data file). The deck, the document and the workbook are derived from it by builders and are never edited by hand; pandoc can build a Word document from
markdown with a reference document, and a PDF is exported from the Word or HTML source. A change is made in the source and every form is rebuilt, so the forms cannot disagree.

## When not to make a deck

- The audience will read it alone and decide later: write a memo.
- The content is a table of numbers that will be updated: build a workbook.
- A conversation is needed to resolve an objection: a one-page brief and a meeting, not a deck.
- The audience has not agreed the requirements: agree those first; a deck presented before the requirements reads as a point solution.

## Matching the chart to the management question (12 Nov 2026)

Source: apn enterprise-strategy program pack, 12 Nov 2026 (commits e743df34 to 09068983; operator review in session bba30cc3).

- "When does each piece land, and what does it answer?" A timeline fishbone, one page per workstream (build-from-data, Timeline pages).
- "What is each need getting?" An Ishikawa with the needs as bones read as "random stuff written under each heading". Offer candidates side
  by side and let the operator choose: a benefits map (project, change, what the business sees, need met), coverage by quarter (shaded),
  today and after (a table with how it will be shown), an outcome roadmap (now, next, later). Mark each with an "Option" chip.
- "Where is the mechanism?" The operator asked where A/B recovery and the monitoring detail were. Add a "how it works" backing page right
  after each project page: a recovery ladder (if this happens, the box does this, so the business gets this, how far it is proven) and a
  monitoring flow (devices, collector, record, alarm engine, NOC, with the alarm list). Keep it as backing, so the story stays short.

