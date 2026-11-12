---
Title: Skill seed: skill-presentation
Category: skill-seed
Status: draft
Authority: >-
  Design brief for the skill-presentation pack, written by the operator with an agent from a real deck-building engagement (2026-11-12) and web research of existing office-document skills and libraries;
  the pack is built from it with `new-skill scaffold`
Scope: How an agent decides what a presentation or report must say for its audience, shapes it so business, technical, financial and management views are all covered, builds it in the right format, and reviews it
Last reviewed: 20261112_1544
Summary: >-
  Seed for skill-presentation: audience and objective brief, the four-lens overlay and translation, story structure, views, per-format build routes (PowerPoint, Word, Excel, PDF), render-and-review loop, and honesty rules.
---

# Skill seed: skill-presentation

## Contents

- [Parameters](#parameters)
- [Purpose and users](#purpose-and-users)
- [Trigger phrases](#trigger-phrases)
- [Non-goals and neighbours](#non-goals-and-neighbours)
- [Source material](#source-material)
- [What was learned](#what-was-learned)
- [Vocabulary](#vocabulary)
- [Outputs and artifacts](#outputs-and-artifacts)
- [Task routing](#task-routing)
- [Scripts plan](#scripts-plan)
- [Templates and assets](#templates-and-assets)
- [Standing rules](#standing-rules)
- [Safety boundaries](#safety-boundaries)
- [Evidence plan](#evidence-plan)
- [Acceptance scenarios](#acceptance-scenarios)
- [Write-back](#write-back)
- [Install and registry](#install-and-registry)
- [Open questions](#open-questions)
- [Build order and done](#build-order-and-done)

---

## Parameters

```text seed-parameters
name: skill-presentation
family: specialists/project
short_description: Presentations and reports for any audience: pick the form (deck, Word, Excel, PDF, one-pager), cover business, technical, financial and management views, build from data, render and review. Not diagrams or code.
aliases:
scripts: yes
operator_context: yes
memory_channel: presentation
related: skill-coder, skill-drawio, skill-commtracker, skill-knowledge-curator
forbidden_terms: Martin, Sandro, Litebooth, Iridium, Cambium, Malik, enterprise-strategy, APN, Uday, Rob, George
```

## Purpose and users

An agent that builds a presentation or report today produces what the author knows (technical detail in order of discovery) rather than what the audience needs to decide. This skill makes the agent
work in the opposite order: first the audience and the objective, then the story, then the four views every management-facing deliverable must carry (business, technical, financial, management), then
the format, then the build and a rendered review. Its distinctive job is translation: a technical person speaking to people who think in outcomes, cost and risk needs each technical point restated as
the outcome it changes, what it costs or saves, and what the audience must decide, with the technical detail kept underneath. It covers decks, Word documents, spreadsheets, PDFs and one-page
summaries, and the same content can be rebuilt into more than one of them.

Users: the operator preparing material for managers, sponsors, customers or technical leads; any skill or project that must turn analysis into a deliverable; a reviewer checking a draft for tilt (too
technical, no cost, no decision).

## Trigger phrases

- make a presentation for management
- write this up for the business
- how should I present this to a non-technical audience
- build the deck, the document or the spreadsheet for this
- turn this into slides, a Word document or a one-pager
- management does not see the value, how do I explain it
- is this presentation covering cost and business, not only technical
- review my slides before I send them

## Non-goals and neighbours

| Not this skill's job                                                             | Owner                           |
| -------------------------------------------------------------------------------- | ------------------------------- |
| Drawing diagrams, flowcharts, swimlanes and roadmaps from a data map             | skill-drawio                    |
| Writing or reviewing code and scripts, including this pack's own scripts         | skill-coder                     |
| Filing and threading stakeholder messages, emails and transcripts                | skill-commtracker               |
| Auditing a project's documents for stale or conflicting facts                    | skill-knowledge-curator         |
| The facts of a domain (network, systems, vendor products) shown in a deliverable | the domain skill that owns them |
| Sending, publishing or presenting a deliverable to anyone                        | the operator, always explicitly |

## Source material

| Source                                                                                         | Where                                                | Label              | Capture                 |
| ---------------------------------------------------------------------------------------------- | ---------------------------------------------------- | ------------------ | ----------------------- |
| A deck-building engagement: requirements, grid, timeline, flow, cost, component and gap slides | session of 2026-11-12, project deck builder and its  | USER_STATED        | not needed              |
|   built natively and reviewed by render                                                        |   review findings                                    |                    |                         |
| Operator rulings on tone and content for management material (no verbatim transcript quotes,   | operator, 2026-11-12                                 | USER_STATED        | not needed              |
|   not an investigative report, no invented figures, honest gaps)                               |                                                      |                    |                         |
| Anthropic office skills (pptx, docx, xlsx, pdf): workflows, scripts, gotchas                   | github.com/anthropics/skills, folders skills/pptx,   | VERIFIED_PRIMARY   | SKILL.md files captured |
|                                                                                                |   docx, xlsx, pdf, commit of 2026-11-06              |                    |   verbatim              |
|                                                                                                |                                                      |                    |   under documents/      |
| Licence of those four folders: Apache License 2.0 (each folder's LICENSE.txt), moved to Apache | gh api contents of each folder, read 2026-11-12      | VERIFIED_PRIMARY   | LICENSE.txt             |
|   2.0 by commit 2026-11-06                                                                     |                                                      |                    |   headers captured      |
| Locally installed doc, spreadsheet and pdf skills (Apache-2.0 LICENSE.txt) and the             | skills_stuff/skills/doc,                             | VERIFIED_PRIMARY   | read in place           |
|   render_docx.py helper                                                                        |   spreadsheet; ~/.codex/skills/pdf                   |                    |                         |
| Library facts: pptxgenjs 4.0.1, python-pptx 1.0.2, docx (npm) 9.15.3, python-docx 1.2.0,       | official docs and package indexes, read 2026-11-12   | VERIFIED_SECONDARY | version table           |
|   pandoc 3.14, openpyxl 3.1.5, XlsxWriter 3.3.1, WeasyPrint 70.0, Playwright                   |   by research agents                                 |                    |   in sources.yaml       |
| WCAG 2.2 contrast and non-text contrast; Microsoft accessibility guidance                      | w3.org/WAI/WCAG22/Understanding,                     | VERIFIED_PRIMARY   | pages captured          |
|                                                                                                |   support.microsoft.com                              |                    |   under documents/      |
| Communication method: pyramid principle, SCQA, action titles, storytelling-with-data,          | books and guides named in references; not all read   | UNVERIFIED         | none until read         |
|   resonate-style audience framing, BLUF, decision memos                                        |   in full                                            |                    |                         |
| Audience-first skills: doc-coauthoring (five meta-questions, context-free reader test), a pyramid-principle skill, a presentation coach skill; Duarte, Minto and Amazon PR/FAQ pages | research record, section Audience and structure | VERIFIED_PRIMARY for the skills and pages read, UNVERIFIED for books | research/research-20261112_1600.md |
| Existing agent skills for decks and documents (frontend-slides, slide-wright, OfficeCLI,       | GitHub metadata read 2026-11-12; code mostly unread  | UNVERIFIED         | none                    |
|   awesome lists)                                                                               |                                                      |                    |                         |

All research, captures and part files are kept for good in this seed's own folder (`research/`, `parts/`) and are never deleted or moved after the build; the research record is `research/research-20261112_1600.md`.

## What was learned

| Lesson                                                                                                        | Evidence                     | Becomes                                               |
| ------------------------------------------------------------------------------------------------------------- | ---------------------------- | ----------------------------------------------------- |
| A technical author tilts every deliverable technical; management reads business, cost and risk and sees       | operator 2026-11-12; the     | the four-lens model, the translation chain            |
|   "complex and expensive" even when the work is sound. The fix is a fixed overlay of four views on every      |   engagement's feedback loop |   and lens_coverage.py                                |
|   item, not more explanation.                                                                                 |                              |                                                       |
| Start from the audience's stated requirements, then show which program step delivers each, in which phase and | engagement 2026-11-12        | story-and-structure.md; the requirement-by-phase and  |
|   by what date; technical detail goes underneath, not first.                                                  |                              |   requirement-to-technical grid views                 |
| One message per slide, an action title, a visual per slide: the grid (many-to-many), heatmap (state by        | the eight-slide deck,        | views-and-visuals.md and the layout helpers           |
|   phase), timeline (dates), flow (from reactive to proactive), cost tree (drivers and levers) and component   |   reviewed as renders        |                                                       |
|   cards each answer one question.                                                                             |                              |                                                       |
| Never invent a figure. Where a number does not exist, show an explicit "to be counted" box and ask for the    | operator ruling and the      | honesty-and-evidence.md; a standing rule              |
|   data, with an owner and a date; state dates as at a day and colour by state.                                |   cost slide                 |                                                       |
| Paraphrase what stakeholders said; no verbatim transcript quotes in management material, and a natural tone   | operator                     | honesty-and-evidence.md; operator layer               |
|   rather than an investigative report that cites meetings and message times.                                  |   correction 2026-11-12      |                                                       |
| A many-to-many mapping drawn as lines between boxes collapses into overlaps; a grid with dots has no          | operator rejection of a      | views-and-visuals.md decision rule                    |
|   crossings and reads in seconds.                                                                             |   drawn tree; the            |                                                       |
|                                                                                                               |   grid accepted              |                                                       |
| Content is data and layout is code: markdown holds the wording, a data module the figures, a builder the      | the project's deck and       | build-from-data.md; a standing rule                   |
|   layout; the office file is derived and rebuilt, never hand-edited.                                          |   workbook builders          |                                                       |
| Render every slide to an image and look; the first render of the deck showed five fault classes: headline     | render review 2026-11-12     | render-and-review.md fault list                       |
|   wrapping onto its subtitle, a note overlapping a table, dashed boxes too short for their text, column       |                              |   and deck_geometry_check.py                          |
|   headers colliding with the subtitle, and cards mostly empty.                                                |                              |                                                       |
| PowerPoint may serve a cached copy when a file is re-opened by the same path; export from a fresh copy under  | observed 2026-11-12          | render_pages.py copies to a fresh                     |
|   a new name or the render shows the old deck.                                                                |                              |   name; render-and-review.md                          |
| A passing LibreOffice render does not prove PowerPoint will open the file: pptxgenjs can emit chart XML       | Anthropic pptx SKILL.md,     | powerpoint.md; office_validate.py                     |
|   PowerPoint rejects. Validate with the Anthropic validator and open once in PowerPoint.                      |   read 2026-11-12            |                                                       |
| pptxgenjs gotchas: hex colours without #, never share an options object between calls, native charts, real    | Anthropic pptx SKILL.md;     | powerpoint.md                                         |
|   bullets not a literal bullet character, notes through addNotes, masters for branding, LAYOUT_WIDE is 13.3   |   PptxGenJS docs             |                                                       |
|   by 7.5 inches.                                                                                              |                              |                                                       |
| Reading order for screen readers follows the order elements are added, alt text on every image, unique slide  | WCAG 2.2 and                 | accessibility-and-contrast.md; contrast_check.py      |
|   titles; text contrast at least 4.5 to 1 and non-text cues 3 to 1; colour is never the only status signal.   |   Microsoft guidance         |                                                       |
| Formulas, not pasted totals: openpyxl stores no cached values, so recalculate headlessly and scan for errors; | Anthropic xlsx SKILL.md      | spreadsheets.md; recalc_check.py                      |
|   the exit code of a recalc tool does not equal a clean workbook, read its JSON.                              |                              |                                                       |
| XlsxWriter creates new files only and caches 0 for a formula unless a value is given; openpyxl edits existing | XlsxWriter docs              | spreadsheets.md decision rule                         |
|   files; choose the route by whether the file exists.                                                         |                              |                                                       |
| Word: use real styles, a numbering config not literal bullets, table widths in DXA, shading CLEAR, a          | Anthropic docx SKILL.md;     | word-documents.md                                     |
|   reference.docx for house style through pandoc, and update TOC fields after build.                           |   pandoc manual              |                                                       |
| PDF: author in Word or HTML and export for fidelity; WeasyPrint and Playwright do not guarantee tagged or     | library docs read 2026-11-12 | pdf-output.md                                         |
|   accessible output, so validate; do not bundle PyMuPDF without accepting its AGPL.                           |                              |                                                       |
| Generated reports for status (weekly workbook from data) are previewed and confirmed before sending; the      | operator practice            | build-from-data.md and the status workbook helper     |
|   workbook is rendered only after the wording is agreed.                                                      |                              |                                                       |
| The right form depends on audience and objective: a sceptical sponsor wants a short answer-first document     | engagement and research      | choose-the-form.md decision table                     |
|   with a decision; a technical lead wants detail and diagrams; a customer wants outcomes and price.           |                              |                                                       |
| Answering a sceptical stakeholder defensively (technical depth first, jargon, status without outcomes, no     | engagement 2026-11-12        | audience-and-objective-brief.md failure modes         |
|   decision asked) loses the room; lead with their requirements, concede what is unknown, show the plan and    |                              |                                                       |
|   the dates.                                                                                                  |                              |                                                       |
| Ask the audience and impact questions first and test the draft on a reader with no context; block drafting while the audience, purpose or decision is unknown. | doc-coauthoring and a coach skill, read 2026-11-12 | audience-and-objective-brief.md; the reader test in render-and-review.md |
| State the governing thought in one sentence, answer first, group points so one rebuttal does not collapse the case; make the audience the hero; restrict length because long attachments avoid choosing what matters. | pyramid-principle skill, Duarte and Amazon pages | story-and-structure.md |
| Existing Anthropic and OpenAI office skills are visual-design and file-format guides; neither holds audience, | research 2026-11-12          | purpose; sources.yaml negative finding                |
|   story or lens guidance, so that part of this pack is new.                                                   |                              |                                                       |

## Vocabulary

- lens: one of four views of the same item (business, technical, financial, management)
- translation chain: feature, capability, outcome, value, cost, decision
- tilt: a deliverable whose content sits mostly in one lens
- action title: a slide or section title that states the conclusion as a sentence
- view: a standard visual form (grid, heatmap, timeline, flow, cost tree, component cards, RAG table)
- as-at date: the day a status or figure was read; every status carries one
- derived file: an office file rebuilt from its source and never edited by hand
- brief: the one-page audience-and-objective record written before any slide

## Outputs and artifacts

| Output                           | Format and name                                    | Saved in                          | Reader                        |
| -------------------------------- | -------------------------------------------------- | --------------------------------- | ----------------------------- |
| Audience and objective brief     | markdown, brief-<slug>-YYYYMMDD_hhmm.md            | the project's docs area           | the operator and the reviewer |
| Content source for a deliverable | markdown plus a data file                          | the project's docs or slides area | the builder script            |
| Deck                             | .pptx rebuilt from source, same stem as the source | beside its source                 | the audience                  |
| Document                         | .docx (and optionally .pdf) rebuilt from markdown  | beside its source                 | the audience                  |
| Workbook                         | .xlsx rebuilt from a data file                     | beside its source                 | the audience                  |
| One-page summary                 | markdown or .docx                                  | beside its source                 | senior reader                 |
| Lens coverage report             | text printed by lens_coverage.py                   | terminal, optionally the brief    | the author                    |
| Rendered review pages            | PNG per page                                       | a scratch folder, never committed | the author                    |

## Task routing

| Task                                      | Reference file                  | Contents                                                                                                               |
| ----------------------------------------- | ------------------------------- | ---------------------------------------------------------------------------------------------------------------------- |
| Decide the form for an audience           | choose-the-form.md              | Audience by objective decision table, deck versus document versus workbook versus one-pager versus PDF, length and     |
|   and objective                           |                                 |   detail, repurposing one source into several formats                                                                  |
| Write the audience and objective brief    | audience-and-objective-brief.md | The questions that fill the brief, audience types, what each already believes, what the decision is, handling a        |
|                                           |                                 |   sceptical stakeholder, failure modes and fixes                                                                       |
| Cover business, technical, financial and  | lenses-and-translation.md       | The four lenses, the translation chain, the translation table, the lens coverage check, tilt and how to correct it, a  |
|   management views                        |                                 |   worked example                                                                                                       |
| Structure the story                       | story-and-structure.md          | Answer first, pyramid and SCQA, action titles, executive summary, appendix, requirement to deliverable to date         |
|                                           |                                 |   traceability, how to say what is not known                                                                           |
| Choose the visual for a message           | views-and-visuals.md            | Grid, heatmap, timeline, flow, cost tree, component cards, RAG table, chart choice, palette, overlap rules, when to    |
|                                           |                                 |   hand a diagram to skill-drawio                                                                                       |
| Keep content as data and rebuild the file | build-from-data.md              | Markdown source, data module, builder, derived files, naming and versioning, plan then apply, previews before          |
|                                           |                                 |   sending, repurposing                                                                                                 |
| Build or edit a PowerPoint deck           | powerpoint.md                   | pptxgenjs and python-pptx routes, layouts and masters, notes, alt text, fonts, native charts, validation, known        |
|                                           |                                 |   corruption traps, editing a template                                                                                 |
| Build or edit a Word document             | word-documents.md               | docx-js, python-docx and pandoc routes, styles and numbering, tables, TOC, comments and tracked changes, reference     |
|                                           |                                 |   document, accessibility                                                                                              |
| Build or edit a spreadsheet               | spreadsheets.md                 | XlsxWriter versus openpyxl, formulas and recalculation, error scan, conventions, RAG sheets, summary sheet first,      |
|                                           |                                 |   print setup                                                                                                          |
| Produce a PDF                             | pdf-output.md                   | Export from Word or HTML versus generate directly, WeasyPrint, Playwright, reportlab, tagged PDF, page images,         |
|                                           |                                 |   library licences                                                                                                     |
| Render and review before showing          | render-and-review.md            | Render per format, fresh-copy rule, the fault list, the review checklist, stop rule, geometry and contrast checks      |
| Make it accessible and legible            | accessibility-and-contrast.md   | Contrast ratios, colour not the only signal, reading order, alt text, font sizes, document language, headings          |
| Keep claims honest                        | honesty-and-evidence.md         | No invented figures, to-be-counted boxes, evidence labels, as-at dates, paraphrase over quotation, tone,               |
|                                           |                                 |   naming sources                                                                                                       |

## Scripts plan

| Script               | Does                                                                 | Origin                                    | Safety                   | Test                            |
| -------------------- | -------------------------------------------------------------------- | ----------------------------------------- | ------------------------ | ------------------------------- |
| lens_coverage.py     | Reads a content spec (markdown table or list of items tagged by      | new                                       | read-only                | tests/test_lens_coverage.py     |
|                      |   lens) and reports items missing a lens and the share of content    |                                           |                          |                                 |
|                      |   per lens; flags tilt                                               |                                           |                          |                                 |
| render_pages.py      | Renders a pptx, docx, xlsx or pdf to page PNGs through LibreOffice   | reuse (the Apache-2.0 doc skill's         | modifies files only      | tests/test_render_pages.py      |
|                      |   or PowerPoint on a fresh copy under a new name, with a timeout on  |   render_docx.py, extended; the           |   under a scratch folder |                                 |
|                      |   every call                                                         |   PowerPoint export approach from         |                          |                                 |
|                      |                                                                      |   the engagement)                         |                          |                                 |
| contrast_check.py    | Computes WCAG contrast ratios for colour pairs and for text and fill | new                                       | read-only                | tests/test_contrast_check.py    |
|                      |   colours found in a pptx or a palette file                          |                                           |                          |                                 |
| deck_geometry_check.py | Reads a pptx and reports shapes outside the slide, overlapping text  | new                                       | read-only                | tests/test_deck_geometry_check.py |
|                      |   boxes, text that cannot fit its box (estimate), and small fonts    |                                           |                          |                                 |
| office_validate.py   | Validates a pptx or docx against the OOXML schemas to catch files    | reuse (Anthropic skills office validate   | read-only                | tests/test_office_validate.py   |
|                      |   PowerPoint or Word refuses                                         |   scripts, Apache-2.0, notices kept)      |                          |                                 |
| recalc_check.py      | Recalculates a workbook headlessly and reports formula errors from   | reuse (Anthropic xlsx recalc script,      | modifies the workbook    | tests/test_recalc_check.py      |
|                      |   the tool's JSON, not its exit code                                 |   Apache-2.0, notices kept)               |   copy only with --apply |                                 |
| md_to_docx.py        | Builds a Word document from markdown with real styles and tables;    | reuse (the operator's shared converter,   | writes one .docx only    | tests/test_md_to_docx.py        |
|                      |   the .docx is derived                                               |   promoted into this pack)                |   with --apply           |                                 |
| deck_builder.js      | Builds a deck from a content spec using the layout helpers (table,   | reuse (the engagement's                   | writes one .pptx only    | tests/test_deck_builder.js      |
|                      |   grid, heatmap, timeline, flow, tree, cards) and notes              |   builder, generalised)                   |   with --apply           |                                 |

## Templates and assets

- `templates/brief.md`: the audience and objective brief, copied and filled before any build; placeholders are `<angle brackets>`.
- `templates/lens-spec.md`: the content spec lens_coverage.py reads, one row per item with its business, technical, financial and management line.
- `templates/translation-table.md`: the technical term to outcome to cost to decision table to fill per project.
- `templates/review-checklist.md`: the render-and-review checklist for any format.
- `examples/`: a small deck source, a document source and a workbook source in generic wording, each rebuildable by the pack's scripts.

## Standing rules

| Rule                                                                                                | Reason                                                                    | Decided by         |
| --------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------- | ------------------ |
| Write the audience and objective brief before any slide, page or sheet; if the audience or the      | a build from the author's knowledge tilts technical and misses what the   | operator,          |
|   decision is unknown, ask                                                                          |   audience decides                                                        |   2026-11-12       |
| Every item in a management-facing deliverable carries four lenses (business, technical, financial,  | the audience reads business, cost and risk; technical-only material is    | operator,          |
|   management); a missing lens is shown as an explicit gap, never left out                           |   read as complexity and cost                                             |   2026-11-12       |
| Lead with the audience's requirements and the answer; put technical detail underneath or in         | management needs the business layer on top                                | operator,          |
|   an appendix                                                                                       |                                                                           |   2026-11-12       |
| Never invent a figure, date, quote or saving; show "to be counted" with an owner and a date and     | a made-up number destroys trust in the rest                               | operator,          |
|   label evidence                                                                                    |                                                                           |   2026-11-12       |
| Paraphrase what people said; no verbatim transcript quotes and no meeting-by-meeting narration in   | it reads as an investigation, not a plan                                  | operator,          |
|   management material                                                                               |                                                                           |   2026-11-12       |
| The office file is derived from its source and never edited by hand; rebuild it                     | hand edits drift from the source and are overwritten                      | operator, 2026-10  |
| Render every page to an image and look before showing anyone; fix, re-render only what changed,     | most layout faults are visible only in a render                           | operator,          |
|   then stop                                                                                         |                                                                           |   2026-11-12       |
| Validate a pptx or docx before delivery and open a pptx once in PowerPoint                          | a LibreOffice render passing proves nothing about PowerPoint              | research,          |
|                                                                                                     |                                                                           |   2026-11-12       |
| Colour is never the only status signal; contrast meets WCAG 2.2                                     | accessibility and printing in grey                                        | WCAG 2.2           |
| Sending, publishing or presenting a deliverable is the operator's decision; the skill never sends   | outward actions are the operator's                                        | operator,          |
|                                                                                                     |                                                                           |   2026-11-12       |

## Safety boundaries

- Reads: the project's source material the task names, and the deliverable being reviewed.
- Writes: only the deliverable's source and its derived file, and scratch renders; each write script plans first and needs `--apply`.
- Never: send or publish a deliverable, put a credential or a person's private detail into a file, copy a licensed work without its licence terms, edit a derived file by hand, or present an unreviewed
  render.

## Evidence plan

| Claim                                                                         | Evidence and source                                  | Falsifier                                                     |
| ----------------------------------------------------------------------------- | ---------------------------------------------------- | ------------------------------------------------------------- |
| The pptx, docx, xlsx and pdf folders of Anthropic's skills repo are Apache    | each folder's LICENSE.txt read through the GitHub    | a later commit changes a folder's licence, or a script        |
|   License 2.0 as of the commit of 2026-11-06                                  |   API on 2026-11-12                                  |   carries a different header                                  |
| A LibreOffice render passing does not prove PowerPoint will open a            | Anthropic pptx SKILL.md statement about chart XML    | a documented case where a validated and LibreOffice-clean     |
|   pptxgenjs file                                                              |                                                      |   file is refused by PowerPoint is absent, or the claim is    |
|                                                                               |                                                      |   withdrawn upstream                                          |
| openpyxl writes formulas without cached values, so readers see none           | Anthropic xlsx SKILL.md and openpyxl documentation   | openpyxl begins to compute values on save                     |
|   until recalculated                                                          |                                                      |                                                               |
| XlsxWriter creates new files only and stores 0 as an uncached formula result  | XlsxWriter documentation                             | XlsxWriter gains read and modify support or                   |
|                                                                               |                                                      |   calculates results                                          |
| WCAG 2.2 requires 4.5 to 1 contrast for normal text and 3 to 1 for large text | w3.org Understanding documents                       | a newer WCAG version changes the thresholds                   |
|   and meaningful non-text cues                                                |                                                      |                                                               |
| WeasyPrint and Playwright can emit tagged PDF but neither guarantees validity | library documentation                                | a library documents guaranteed PDF/UA output                  |
| Re-opening a deck at the same path in PowerPoint can show a cached copy       | observed in the engagement on 2026-11-12             | repeated exports from the same path always show the           |
|                                                                               |                                                      |   current file                                                |
| A context-free reader test and a blocked-until-known audience are used by public skills, but none maps audience and objective to a form | doc-coauthoring and a coach skill read 2026-11-12 | a public skill that publishes an audience-by-objective form table is found |
| Existing public office skills hold no audience, story or lens guidance        | negative finding from the 2026-11-12 survey of       | a published skill that teaches audience-driven structure      |
|                                                                               |   anthropics/skills and openai/skills                |   is found                                                    |

## Acceptance scenarios

| Prompt                                                                 | Expected behaviour                                                                                                          |
| ---------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------- |
| Make a presentation for the executive sponsor who thinks our program   | Writes the audience and objective brief first, applies the four lenses, leads with requirements and the answer, shows cost  |
|   is too complex and expensive                                         |   as to be counted where unknown, then builds and reviews renders                                                           |
| Here are our technical changes; turn them into slides for the business | Runs lens_coverage, reports missing business and financial lenses, builds a translation table, and does not produce a       |
|                                                                        |   technical-only deck                                                                                                       |
| Build a status workbook from this YAML for the weekly update           | Uses the spreadsheet route, summary sheet first, colour plus label for state, recalculates and scans for errors, previews   |
|                                                                        |   before saving                                                                                                             |
| Convert this markdown report to a Word document                        | Uses the Word route with real styles and the shared converter, writes the derived file only with --apply, renders pages     |
|                                                                        |   and reviews                                                                                                               |
| Write a Python script that parses a pptx                               | Does not use this skill; hands to skill-coder                                                                               |
| Draw the architecture as a swimlane diagram                            | Hands the diagram to skill-drawio and only places its export in the deliverable                                             |
| Send the finished deck to the customer                                 | Stops and asks; the skill never sends                                                                                       |
| The cost slide has no numbers yet, just fill in plausible savings      | Refuses to invent figures, shows to be counted with an owner and date, and says what data is needed                         |
| I edited the pptx by hand, regenerate it                               | Warns that regeneration overwrites hand edits, asks which side is the source, and does not overwrite without confirmation   |

## Write-back

- Learned entries go to: the focused reference (lenses-and-translation.md, views-and-visuals.md, powerpoint.md, word-documents.md, spreadsheets.md, pdf-output.md, render-and-review.md), and the
  translation table template when a new translation proves useful.
- Stays in the project: audience names, figures, the content of any deliverable, and project-specific wording rules (these live in the pack's operator layer when they are the operator's).

## Install and registry

- Install targets: `~/.claude/skills`, `~/.codex/skills`, `~/.hermes/skills/domain` (symlinks to the canonical folder).
- Registry rows: skills_stuff `.agents/skill-surfaces.md` and `skills.md`; a "Shared tools and skills" line in the project-area AGENTS.md files is for the operator to approve.

## Open questions

| Question                                                                                                                          | Blocking | Owner    |
| --------------------------------------------------------------------------------------------------------------------------------- | -------- | -------- |
| Does PowerPoint on macOS allow scripted PDF export without a permission prompt each run, and is Keynote worth supporting          | later    | operator |
| Which route refreshes a Word table of contents reliably without opening the app: LibreOffice headless or Word through AppleScript | later    | agent    |
| Which PDF/UA validator to adopt (veraPDF or another)                                                                              | later    | agent    |
| Whether to generalise the engagement's deck builder into a spec-driven builder in the first release or ship layout helpers only   | later    | operator |
| Which slash alias, if any, for this skill                                                                                         | later    | operator |

## Build order and done

1. `new-skill check-seed` passes (no `TODO(seed)` left, every table filled or its row deleted).
2. `new-skill scaffold` plan read; then `--apply` writes the skeleton; the seed stays in `pending_skills/`.
3. Run `skill-ai-it bootstrap` on the new folder (governance files, task runner, checker), then `just bootstrap` and `just check`.
4. Write the references in this order: lenses-and-translation, audience-and-objective-brief, story-and-structure, choose-the-form, views-and-visuals, render-and-review, then the four format
   references, then honesty and accessibility.
5. Write the scripts with skill-coder in this order: lens_coverage, render_pages, contrast_check, deck_geometry_check, then the reused ones with their licence notices (office_validate, recalc_check,
   md_to_docx), then deck_builder; each with tests first, a catalogue row, a recipe and a code-map entry.
6. Capture the Anthropic SKILL.md files and licence headers verbatim under `documents/research-sources-20261112/` with a sha256 table; record every claim in `sources.yaml` with its falsifier.
7. Turn `Acceptance scenarios` into `tests/scenarios.md`, run them, and record the result in `tests/eval-procedure.md`.
8. `skill_pack_check.py <pack> --strict` reports no error and no `planned` row; `just check` passes.
9. Install by symlink, add the registry rows, add the CHANGELOG `## Unreleased` line, and commit in `skills_stuff` (the operator decides when to push).
