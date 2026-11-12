---
Title: Skill seed: skill-presentation
Category: skill-seed
Status: draft
Authority: >-
  Design brief for the skill-presentation pack, produced through the new-skill intake interview (intake-skill-presentation-20261112_1644.md, answers USER_STATED 12 Nov 2026), a harvest of the operator's own deliverables and generators, and ten web-research reports; supersedes the hand-written seed of 12 Nov 1544, which stays in this folder as a record; for personal use
Scope: How an agent decides what a presentation or report must say for its audience, covers business, technical, financial and management views and translates between them, and builds it as a deck, Word document, workbook, PDF or markdown mind map that fits the operator's own project work
Last reviewed: 20261112_1653
Summary: >-
  Seed for skill-presentation (personal): audience and objective brief, the four-lens overlay and translation, story, the operator's real deliverables (profitability workbooks, mind maps, career documents, decks), per-format routes, render-and-review, honesty rules, and a deferred list of everything researched but not used.
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
- [Deferred and extensions](#deferred-and-extensions)
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
forbidden_terms: Martin, Sandro, Litebooth, Iridium, Cambium, Malik, Uday, Rob, George, APN, enterprise-strategy
```

## Purpose and users

This is a personal skill for the operator's own work, not a product for a wider audience. An agent that builds a presentation or report today produces what the author knows, in the order the author
found it: technical detail first, little cost, no decision. This skill makes the agent work in the opposite order for the operator's real deliverables: first the audience and the objective, then the
story, then the four views every management-facing deliverable must carry (business, technical, financial, management), then the form and the build, then a rendered review. Its distinctive job is
translation: a technical person speaking to people who think in outcomes, cost and risk needs each technical point restated as the outcome it changes, what it costs or saves, and what the audience
must decide, with the technical detail kept underneath. It covers what the operator actually produces: profitability and scenario workbooks and their markdown mind maps, management decks and status
workbooks, Word documents and PDFs including role-targeted resumes and cover letters, and one-page summaries.

Users: the operator preparing material for sponsors, finance and commercial readers, technical leads, recruiters and customers; any of the operator's projects that turns analysis into a deliverable; a
reviewer checking a draft for tilt (too technical, no cost, no decision).

## Trigger phrases

- make a presentation for management
- write this up for the business
- how should I present this to a non-technical audience
- build the deck, the document or the spreadsheet for this
- turn this into slides, a Word document or a one-pager
- make a mind map of this decision or this breakdown
- build the profitability workbook for this scenario
- tailor my resume or cover letter for this role
- management does not see the value, how do I explain it
- is this presentation covering cost and business, not only technical
- review my slides before I send them

## Non-goals and neighbours

| Not this skill's job                                                        | Owner                              |
| --------------------------------------------------------------------------- | ---------------------------------- |
| Drawing diagrams, flowcharts, swimlanes and roadmaps from a data map        | skill-drawio                       |
| Writing or reviewing code and scripts, including this pack's own scripts    | skill-coder                        |
| Filing and threading stakeholder messages, emails and transcripts           | skill-commtracker                  |
| Auditing a project's documents for stale or conflicting facts               | skill-knowledge-curator            |
| The profitability model and its data (what the numbers are)                 | the project that owns the analysis |
| The domain facts shown in a deliverable (network, systems, vendor products) | the domain skill that owns them    |
| Sending, publishing or presenting a deliverable to anyone                   | the operator, always explicitly    |

## Source material

| Source                                                                                   | Where                                           | Label                              | Capture            |
| ---------------------------------------------------------------------------------------- | ----------------------------------------------- | ---------------------------------- | ------------------ |
| The operator's requirements and rulings for this skill (personal use, four lenses, Word  | intake-skill-presentation-20261112_1644.md      | USER_STATED                        | in the intake      |
|   engine for every document, release 1 scope, mind maps and profitability work)          |                                                 |                                    |                    |
| A deck-building engagement: requirements, grid, timeline, flow, cost, component and gap  | session of 2026-11-12 and the project           | USER_STATED                        | not needed         |
|   slides built natively and reviewed by render                                           |   deck builder                                  |                                    |                    |
| The operator's own deliverables and generators: workbooks, mind maps, Word and PDF       | research/research-20261112_1700.md, sections on | VERIFIED_PRIMARY (local files)     | in the             |
|   builders, the Word-engine PDF script                                                   |   the operator's deliverables and the           |                                    |   research record  |
|                                                                                          |   profitability work                            |                                    |                    |
| Round 1 research: Anthropic office skills, library facts, WCAG, audience skills          | research/research-20261112_1600.md              | VERIFIED_PRIMARY and UNVERIFIED    | in the             |
|                                                                                          |                                                 |   as labelled                      |   research record  |
| Round 2 research: five case model, audience primary sources, Word and TOC on macOS,      | research/research-20261112_1700.md              | VERIFIED_PRIMARY, VERIFIED_SECONDARY | in the             |
|   accessible PDF, office code licences                                                   |                                                 |   and UNVERIFIED as labelled       |   research record  |
| The five research briefs and the intake that produced them                               | research/briefs/ and the intake                 | USER_STATED                        | kept in the        |
|                                                                                          |                                                 |                                    |   seed folder      |
| Licence of the four Anthropic office folders: Apache License 2.0 (LICENSE.txt), no       | gh api and file reads, 2026-11-12               | VERIFIED_PRIMARY                   | in the             |
|   per-file headers or NOTICE; schema licences unread                                     |                                                 |                                    |   research record  |

All research, captures and part files stay in this seed's folder for good (`research/`, `parts/`); nothing here is deleted or moved after the build.

## What was learned

| Lesson                                                                                                              | Evidence                          | Becomes                                    |
| ------------------------------------------------------------------------------------------------------------------- | --------------------------------- | ------------------------------------------ |
| A technical author tilts every deliverable technical; management reads business, cost and risk and sees "complex    | operator 2026-11-12               | the four-lens model, the translation chain |
|   and expensive". The fix is a fixed overlay of four views on every item, not more explanation.                     |                                   |   and lens_coverage.py                     |
| A published framework already overlays these views: the five case model (strategic, economic, commercial,           | research record 2, Frameworks     | lenses-and-translation.md mapping table    |
|   financial, management, each tested by one question); ISO 42010 gives views per stakeholder concern. Use them as   |   that overlay views              |                                            |
|   the mapping, proportionately.                                                                                     |                                   |                                            |
| Start from the audience's stated requirements, then show which step delivers each, in which phase and by what date; | engagement 2026-11-12             | story-and-structure.md; the requirement    |
|   technical detail goes underneath.                                                                                 |                                   |   grid and phase views                     |
| One message per slide with an action title; Minto's frame is Situation, Complication, Question (not SCQA); a Big    | research record 2,                | story-and-structure.md                     |
|   Idea is one complete sentence with a point of view and the stakes; storyboard before opening software.            |   Audience methods                |                                            |
| Never invent a figure. Where a number does not exist, show "to be counted" with an owner and a date, and state the  | operator ruling and the           | honesty-and-evidence.md; a standing rule   |
|   day a status was read.                                                                                            |   cost slide                      |                                            |
| Paraphrase what stakeholders said; no verbatim transcript quotes and no meeting-by-meeting narration in             | operator correction 2026-11-12    | honesty-and-evidence.md                    |
|   management material.                                                                                              |                                   |                                            |
| A many-to-many mapping drawn as lines collapses into overlaps; a grid with dots has no crossings.                   | operator rejection of a           | views-and-visuals.md                       |
|                                                                                                                     |   drawn tree                      |                                            |
| Content is data and layout is code: markdown holds the wording, a data file the figures, a builder the layout; the  | the project's deck, workbook and  | build-from-data.md; a standing rule        |
|   office file is derived and never hand-edited.                                                                     |   resume builders                 |                                            |
| Render every page to an image and look; the first deck render had five fault classes (wrapped headline, overlapping | render review 2026-11-12          | render-and-review.md; deck_geometry_check.py |
|   note, short dashed boxes, colliding headers, empty cards).                                                        |                                   |                                            |
| PowerPoint may show a cached copy of a re-opened path: render a fresh copy under a new name.                        | observed 2026-11-12               | render_pages.py; render-and-review.md      |
| A LibreOffice render passing does not prove PowerPoint will open a pptxgenjs file; validate against the schemas and | Anthropic pptx SKILL.md           | powerpoint.md; office_validate.py          |
|   open once in PowerPoint.                                                                                          |                                   |                                            |
| pptxgenjs gotchas: hex colours without #, never share an options object between calls, native charts, real bullets, | Anthropic pptx SKILL.md;          | powerpoint.md                              |
|   notes through addNotes, masters, LAYOUT_WIDE is 13.3 by 7.5 inches.                                               |   PptxGenJS docs                  |                                            |
| DOCX to PDF goes through Microsoft Word's own PDF engine on macOS (operator rule, now for every document); in       | docx_to_pdf_word.sh header;       | word-documents.md; word_to_pdf.py          |
|   AppleScript use `active document` inline after `open` (a stored reference fails with -2753); delete Word's lock   |   forum report                    |                                            |
|   files; the first scripted run raises permission dialogs, so it is not unattended.                                 |                                   |                                            |
| A table of contents field made by docx-js or python-docx is empty until an application evaluates it; no tested      | research record 2, Word, PDF      | word-documents.md; open question           |
|   script refreshes it and exports PDF on Word for Mac.                                                              |   and TOC                         |                                            |
| Word documents for roles are built by cloning a template and replacing text so styles survive, then exporting       | me/career docx_builder.py         | career-documents.md                        |
|   through Word.                                                                                                     |                                   |                                            |
| Workbooks: formulas not pasted totals; openpyxl stores no cached values; recalculate headlessly and read the tool's | Anthropic xlsx SKILL.md;          | spreadsheets.md; recalc_check.py           |
|   JSON, not its exit code; XlsxWriter creates, openpyxl edits.                                                      |   library docs                    |                                            |
| The operator's analysis workbooks follow a convention: basis in the file name and a timestamp, an Exclusions and    | profitability projects, files and | analysis-workbooks.md                      |
|   Assumptions block, a column glossary with a formula note per derived column, baseline and what-if columns with a  |   scripts read 2026-11-12         |                                            |
|   delta, direct and shared costs split, one canonical file named.                                                   |                                   |                                            |
| Mind maps are a deliverable form: markmap-compatible markdown with the headline in the H1, a blockquote of base     | profitability projects,           | mind-maps.md; mindmap_render.py;           |
|   facts, a legend, status icons per node, bold key numbers; generated from data for breakdowns and written by hand  |   generators and maps             |   templates/lens-mindmap.md                |
|   for plans.                                                                                                        |   read 2026-11-12                 |                                            |
| Superseded dated outputs move to an archive folder beside them during every sweep; only the latest of each report   | vocus AGENTS.md hard rule         | analysis-workbooks.md; archive_dated.py    |
| Render and review mind maps in the VS Code Markmap extension (gera2ld.markmap-vscode, Open as markmap); the PNG export is the render to look at | one renderer, already installed, so reviews are repeatable | operator tooling, verified 2026-11-12 |
|   type stays active (operator rule, 2026-06-05).                                                                    |                                   |                                            |
| Playwright `page.pdf` has tagged and outline off by default; WeasyPrint needs `--pdf-tags` and valid HTML           | library docs, read 2026-11-12     | pdf-output.md (checks deferred)            |
|   structure; neither guarantees an accessible PDF.                                                                  |                                   |                                            |
| Existing public office skills are format and visual-design guides; none holds audience, story or lens guidance, so  | research record 1 and 2           | purpose; sources.yaml negative finding     |
|   that part is new.                                                                                                 |                                   |                                            |
| Ask the audience and impact questions first and test the draft on a reader with no context; block drafting while    | doc-coauthoring and a coach skill | audience-and-objective-brief.md            |
|   the audience, purpose or decision is unknown.                                                                     |                                   |                                            |

## Vocabulary

- lens: one of four views of the same item (business, technical, financial, management)
- translation chain: feature, capability, outcome, value, cost, decision
- tilt: a deliverable whose content sits mostly in one lens
- action title: a slide or section title that states the conclusion as a sentence
- view: a standard visual form (grid, heatmap, timeline, flow, cost tree, component cards, RAG table, mind map)
- markmap: markdown headings and bullets that render as an interactive mind map
- basis: the cost or revenue basis a workbook is built on, stated in its name (for example base or enriched)
- as-at date: the day a status or figure was read; every status carries one
- derived file: an office file rebuilt from its source and never edited by hand
- brief: the one-page audience-and-objective record written before any slide

## Outputs and artifacts

| Output                               | Format and name                                                | Saved in                                              | Reader                         |
| ------------------------------------ | -------------------------------------------------------------- | ----------------------------------------------------- | ------------------------------ |
| Audience and objective brief         | markdown, brief-<slug>-YYYYMMDD_hhmm.md                        | the project's docs area                               | the operator and the reviewer  |
| Content source for a deliverable     | markdown plus a data file                                      | the project's docs or slides area                     | the builder script             |
| Deck                                 | .pptx rebuilt from source, same stem as the source             | beside its source                                     | the audience                   |
| Document                             | .docx and .pdf (PDF through Word's engine) rebuilt from source | beside its source                                     | the audience                   |
| Analysis or scenario workbook        | .xlsx, basis and timestamp in the name                         | the project's reports folder, older versions archived | finance and commercial readers |
| Mind map                             | markmap markdown, <slug>-YYYYMMDD_hhmm.md                      | the project's mindmaps folder                         | the operator and management    |
| Role-targeted resume or cover letter | .docx and .pdf from a template clone                           | the career folder                                     | recruiters and hiring managers |
| One-page summary                     | markdown or .docx                                              | beside its source                                     | a senior reader                |
| Lens coverage report                 | text printed by lens_coverage.py                               | terminal, optionally the brief                        | the author                     |
| Rendered review pages                | PNG per page                                                   | a scratch folder, never committed                     | the author                     |

## Task routing

| Task                                          | Reference file                  | Contents                                                                                                           |
| --------------------------------------------- | ------------------------------- | ------------------------------------------------------------------------------------------------------------------ |
| Decide the form for an audience and objective | choose-the-form.md              | Audience by objective decision table, deck versus document versus workbook versus mind map versus one-pager versus |
|                                               |                                 |   PDF, length and detail, repurposing one source into several formats                                              |
| Write the audience and objective brief        | audience-and-objective-brief.md | The questions that fill the brief, audience types including finance, recruiters and technical leads, what each     |
|                                               |                                 |   already believes, what the decision is, handling a sceptical stakeholder, failure modes and fixes                |
| Cover business, technical, financial and      | lenses-and-translation.md       | The four lenses, the mapping to the five case model and architecture views, the translation chain and table, the   |
|   management views                            |                                 |   lens coverage check, tilt and how to correct it, the lens mind map, a worked example                             |
| Structure the story                           | story-and-structure.md          | Answer first, pyramid and SCQ, Big Idea, action titles, storyboard first, executive summary, appendix, requirement |
|                                               |                                 |   to deliverable to date traceability, how to say what is not known                                                |
| Choose the visual for a message               | views-and-visuals.md            | Grid, heatmap, timeline, flow, cost tree, component cards, RAG table, mind map, chart choice, palette, overlap     |
|                                               |                                 |   rules, when to hand a diagram to skill-drawio                                                                    |
| Keep content as data and rebuild the file     | build-from-data.md              | Markdown source, data module, builder, derived files, naming and versioning, plan then apply, the archive rule,    |
|                                               |                                 |   previews before sending, repurposing                                                                             |
| Build a markdown mind map                     | mind-maps.md                    | The markmap form, the data mind map shape (headline, base facts, legend, status icons), hand-written plan maps,    |
|                                               |                                 |   the four-lens mind map, generating from data, rendering in the VS Code Markmap extension (gera2ld.markmap-vscode), review                                               |
| Build or edit a profitability, scenario or    | analysis-workbooks.md           | The operator's workbook convention, basis in the name, assumptions block, formula glossary, baseline and what-if   |
|   analysis workbook                           |                                 |   columns, canonical file, archiving, recalculation and error scan                                                 |
| Build or edit a spreadsheet in general        | spreadsheets.md                 | XlsxWriter versus openpyxl, formulas and recalculation, error scan, conventions, RAG sheets, summary sheet first,  |
|                                               |                                 |   print setup                                                                                                      |
| Build or edit a PowerPoint deck               | powerpoint.md                   | pptxgenjs and python-pptx routes, layouts and masters, notes, alt text, fonts, native charts, validation, known    |
|                                               |                                 |   corruption traps, editing a template                                                                             |
| Build or edit a Word document                 | word-documents.md               | docx-js, python-docx and pandoc routes, template cloning, styles and numbering, tables, TOC, the Word engine for   |
|                                               |                                 |   PDF, accessibility basics                                                                                        |
| Build a role-targeted resume or cover letter  | career-documents.md             | Audience (recruiter, hiring manager, applicant tracking), template clone builder, tailoring rules, honesty, Word   |
|                                               |                                 |   export to PDF, file naming                                                                                       |
| Produce a PDF                                 | pdf-output.md                   | Word export first, HTML routes (WeasyPrint, Playwright) when needed, tagged PDF flags, page images, what           |
|                                               |                                 |   is deferred                                                                                                      |
| Render and review before showing              | render-and-review.md            | Render per format, fresh-copy rule, the fault list, the review checklist, stop rule, geometry and contrast checks  |
| Make it legible and accessible                | accessibility-and-contrast.md   | Contrast ratios, colour not the only signal, reading order, alt text, font sizes, headings; PDF checkers           |
|                                               |                                 |   are deferred                                                                                                     |
| Keep claims honest                            | honesty-and-evidence.md         | No invented figures, to-be-counted boxes, evidence labels, as-at dates, paraphrase over quotation, tone,           |
|                                               |                                 |   naming sources                                                                                                   |
| Extend the skill later                        | extensions.md                   | Everything researched or considered and not used now, why, where the evidence is and how to enable it              |

| pptxgenjs 3.12 reads a text box's margin as points, a table cell's margin below 1 as inches; convert inches to points in the one box helper or every card's text sits on its border | enterprise-strategy build_strategy_pptx.js, a3e29af7; slide XML lIns read 2026-11-12 | powerpoint.md; deck_layout.js |
| PowerPoint for Mac asks "Grant File Access" once per new folder outside its container; render into ~/Library/Containers/com.microsoft.Powerpoint/Data/tmp, or an unanswered prompt fails the export (-9074, "User cancelled") | enterprise-strategy render_pptx_pages.py, 6c262ea9; operator question 2026-11-12 | render_pages.py; render-and-review.md |
| Export the fresh copy by name, never "active presentation": with another window on the same deck open, the older window was exported and the render looked current but was stale | enterprise-strategy render_pptx_pages.py and its test, 6c262ea9 | render_pages.py; render-and-review.md |
| One data file can feed two formats: PowerPoint (pptxgenjs) and draw.io (skill-drawio drawio.mxfile) at one geometry, 100 px per inch; draw.io export has no Calibri, so it uses Helvetica and Georgia | enterprise-strategy one_pagers_data.json, build_one_pagers_pptx.js, build_one_pagers_drawio.py, ee9046df | build-from-data.md |
| A generated file carries a drift check (fresh render compared with the file) in the project's check, proven once to fail by changing the data | enterprise-strategy one-pagers-check, ee9046df | build-from-data.md; a standing rule |
| No internal codes a reader must look up: requirement codes stay out of management pages, a plan step keeps its code beside a description ("R2.4 · first two sites"); enforce it with a check | operator 2026-11-12; check_plain_requirement_names, 6c262ea9 | honesty-and-evidence.md; lens_coverage.py |
| No date or recommendation nobody gave: "to agree on <meeting>" or "to confirm"; a side review caught agent-proposed dates and a "recommended" tag | operator 2026-11-12 | honesty-and-evidence.md |
| When prices are ruled out, show cost as reductions and as counts (days on site per install, visits per site, faults found first) with a baseline to take | operator 2026-11-12 | lenses-and-translation.md (financial lens) |
| A business story for management: mission, what we heard (paraphrased), every requirement for every solution, a before-and-after in the audience's own example, where the money is, what comes later with its next decision, a priority question; the traceability grid goes to an appendix | operator review of the strategy deck against the 10 Nov meeting, 2026-11-12 | story-and-structure.md |
| A menu card (a function as rows, each platform as a column, cost rows) lets management choose the cheaper option and see in writing what it gives up | operator direction 2026-11-12 | views-and-visuals.md |
| One-pager pack: an overview and one page per project, each mapping what we heard, business need to technical requirement to what changes, cost reduction, ongoing support and a timeline | operator request 2026-11-12; enterprise-strategy one-pagers-20261112_1752 | choose-the-form.md (one-pager); templates |

## Scripts plan

| Script               | Does                                                              | Origin                                         | Safety                 | Test                            |
| -------------------- | ----------------------------------------------------------------- | ---------------------------------------------- | ---------------------- | ------------------------------- |
| lens_coverage.py     | Reads a content spec (markdown table or list of items tagged by   | new                                            | read-only              | tests/test_lens_coverage.py     |
|                      |   lens) and reports items missing a lens and the share per lens;  |                                                |                        |                                 |
|                      |   flags tilt                                                      |                                                |                        |                                 |
| render_pages.py      | Renders a pptx, docx, xlsx or pdf to page PNGs on a fresh copy    | reuse (the project's render_pptx_pages.py,     | modifies files only    | tests/test_render_pages.py      |
|                      |   under a new name, with a timeout on every call; PowerPoint renders into its own container (no access prompt) and exports the copy by name (enterprise-strategy 6c262ea9) |   extended to other formats; the Apache-2.0    |   under a              |                                 |
|                      |                                                                   |   doc skill's render_docx.py)                  |   scratch folder       |                                 |
| word_to_pdf.py       | Exports a .docx to .pdf through Word's own engine by AppleScript  | reuse (the operator's pdf_export.py            | writes PDFs beside the | tests/test_word_to_pdf.py       |
|                      |   with the `active document` pattern, removes lock files, reports |   and docx_to_pdf_word.sh)                     |   inputs only          |                                 |
|                      |   permission dialogs; LibreOffice only when Word is not available |                                                |   with --apply         |                                 |
| contrast_check.py    | Computes WCAG contrast ratios for colour pairs and for text and   | new                                            | read-only              | tests/test_contrast_check.py    |
|                      |   fill colours found in a pptx or a palette file                  |                                                |                        |                                 |
| deck_geometry_check.py | Reads a pptx and reports shapes outside the slide, overlapping    | new                                            | read-only              | tests/test_deck_geometry_check.py |
|                      |   text boxes, text that cannot fit its box (estimate) and         |                                                |                        |                                 |
|                      |   small fonts                                                     |                                                |                        |                                 |
| office_validate.py   | Validates a pptx against the OOXML schemas to catch files         | reuse (Anthropic office validate scripts,      | read-only              | tests/test_office_validate.py   |
|                      |   PowerPoint refuses; the schemas are referenced, not copied      |   Apache-2.0, licence text kept)               |                        |                                 |
| recalc_check.py      | Recalculates a workbook headlessly and reports formula errors     | reuse (Anthropic xlsx recalc script,           | modifies the workbook  | tests/test_recalc_check.py      |
|                      |   from the tool's JSON, not its exit code; sets a timeout         |   Apache-2.0, licence text kept)               |   copy only            |                                 |
|                      |                                                                   |                                                |   with --apply         |                                 |
| md_to_docx.py        | Builds a Word document from markdown with real styles and tables; | reuse (the operator's shared converter,        | writes one .docx only  | tests/test_md_to_docx.py        |
|                      |   the .docx is derived                                            |   promoted into this pack)                     |   with --apply         |                                 |
| mindmap_render.py    | Writes a markmap mind map from a table (profit or any breakdown   | reuse (the profitability projects' generic     | writes one .md only    | tests/test_mindmap_render.py    |
|                      |   by group, status icons, legend) or from a lens spec (four-lens  |   mind map generator, generalised)             |   with --apply         |                                 |
|                      |   map of an initiative)                                           |                                                |                        |                                 |
| archive_dated.py     | Plans, then moves superseded timestamped report files (md, xlsx,  | new (from the operator's archive rule)         | plan by default; moves | tests/test_archive_dated.py     |
|                      |   csv with an older stamp on the same slug) into an archive       |                                                |   only with --apply;   |                                 |
|                      |   folder beside them, keeping the latest                          |                                                |   never deletes        |                                 |
| drawio_pages.py      | Draws page layouts (cards, tables, milestone lines) to draw.io from the same data as the deck, with the generated banner, page_audit() and a drift check | reuse (enterprise-strategy build_one_pagers_drawio.py on skill-drawio drawio.mxfile, ee9046df) | writes one .drawio only with --write | tests/test_drawio_pages.py |
| deck_layout.js       | The layout helpers from the deck builder (box, line, table, grid, | reuse (the project's build_strategy_pptx.js and build_brief_pptx.js: layout helpers, masters, notes, text diagrams, markdown wording split; | writes one .pptx only  | tests/test_deck_layout.js       |
|                      |   timeline bars, chevrons, cards) for building a deck             |   generalised; a spec-driven builder           |   when called          |                                 |
|                      |   in pptxgenjs                                                    |   is deferred)                                 |   with --apply         |                                 |

## Templates and assets

- `templates/brief.md`: the audience and objective brief, filled before any build.
- `templates/lens-spec.md`: the content spec lens_coverage.py reads, one row per item with its business, technical, financial and management line.
- `templates/lens-mindmap.md`: a four-lens markmap (root is the decision; branches are business, technical, financial, management) to fill for any initiative.
- `templates/translation-table.md`: the technical term to outcome to cost to decision table to fill per project.
- `templates/analysis-workbook-notes.md`: the assumptions block and column glossary layout used by the operator's workbooks.
- `templates/review-checklist.md`: the render-and-review checklist for any format.
- `examples/`: a small deck source, a mind map, a document source and a workbook spec in generic wording, each rebuildable by the pack's scripts.

## Standing rules

| Rule                                                                                                               | Reason                                                    | Decided by          |
| ------------------------------------------------------------------------------------------------------------------ | --------------------------------------------------------- | ------------------- |
| This is a personal skill: build for the operator's own projects and recurring deliverables; record anything        | the skill is not for a wider audience; deferred items can | operator,           |
|   researched that this does not need under deferred, do not build it                                               |   be enabled later                                        |   2026-11-12        |
| Write the audience and objective brief before any slide, page or sheet; if the audience or the decision is         | a build from the author's knowledge tilts technical and   | operator,           |
|   unknown, ask                                                                                                     |   misses what the audience decides                        |   2026-11-12        |
| Every item in a management-facing deliverable carries four lenses (business, technical, financial, management); a  | the audience reads business, cost and risk;               | operator,           |
|   missing lens is shown as an explicit gap, never left out                                                         |   technical-only material is read as complexity and cost  |   2026-11-12        |
| Lead with the audience's requirements and the answer; put technical detail underneath or in an appendix            | management needs the business layer on top                | operator,           |
|                                                                                                                    |                                                           |   2026-11-12        |
| Never invent a figure, date, quote or saving; show "to be counted" with an owner and a date and label evidence     | a made-up number destroys trust in the rest               | operator,           |
|                                                                                                                    |                                                           |   2026-11-12        |
| Paraphrase what people said; no verbatim transcript quotes and no meeting-by-meeting narration in                  | it reads as an investigation, not a plan                  | operator,           |
|   management material                                                                                              |                                                           |   2026-11-12        |
| The office file is derived from its source and never edited by hand; rebuild it                                    | hand edits drift from the source and are overwritten      | operator, 2026-10   |
| Convert DOCX to PDF through Microsoft Word's own PDF engine on macOS, for every document; use LibreOffice only     | fidelity of fonts and page breaks                         | operator,           |
|   when Word is not available and say so                                                                            |                                                           |   2026-11-12        |
| Render every page to an image and look before showing anyone; fix, re-render only what changed, then stop          | most layout faults are visible only in a render           | operator,           |
|                                                                                                                    |                                                           |   2026-11-12        |
| Validate a pptx before delivery and open it once in PowerPoint                                                     | a LibreOffice render passing proves nothing               | research,           |
|                                                                                                                    |   about PowerPoint                                        |   2026-11-12        |
| Analysis workbooks name their basis and carry a timestamp, hold an Exclusions and Assumptions block and a formula  | readers must know what each number rests on               | operator practice,  |
|   glossary, and name one canonical file                                                                            |                                                           |   profitability     |
|                                                                                                                    |                                                           |   projects          |
| Superseded dated outputs move to an archive folder beside them during a sweep; only the latest of each report type | the active folder shows the current answer                | operator,           |
|   stays active                                                                                                     |                                                           |   2026-06-05        |
| Colour is never the only status signal; text contrast meets WCAG 2.2                                               | legibility and printing in grey                           | WCAG 2.2            |
| Sending, publishing or presenting a deliverable is the operator's decision; the skill never sends                  | outward actions are the operator's                        | operator,           |
|                                                                                                                    |                                                           |   2026-11-12        |
| Forbidden names apply to the generic references only; the operator layer may name the operator's projects,         | the skill is personal and aligned to the operator's work  | operator,           |
|   stakeholders and tools                                                                                           |                                                           |   2026-11-12        |

## Safety boundaries

- Reads: the project's source material the task names, and the deliverable being reviewed.
- Writes: only the deliverable's source and its derived file, and scratch renders; each write script plans first and needs `--apply`.
- Never: send or publish a deliverable, put a credential or a person's private detail into a file, edit a derived file by hand, delete (archive instead), or present an unreviewed render.

## Evidence plan

| Claim                                                                             | Evidence and source                                   | Falsifier                                                |
| --------------------------------------------------------------------------------- | ----------------------------------------------------- | -------------------------------------------------------- |
| The pptx, docx, xlsx and pdf folders of Anthropic's skills repo are Apache        | each folder's LICENSE.txt and a file                  | a later commit changes a licence or adds a NOTICE        |
|   License 2.0 with no per-file headers or NOTICE                                  |   search, 2026-11-12                                  |                                                          |
| A LibreOffice render passing does not prove PowerPoint will open a pptxgenjs file | Anthropic pptx SKILL.md statement about chart XML     | a documented case where a validated, LibreOffice-clean   |
|                                                                                   |                                                       |   file is refused is absent, or the claim is             |
|                                                                                   |                                                       |   withdrawn upstream                                     |
| openpyxl writes formulas without cached values; XlsxWriter creates new files only | Anthropic xlsx SKILL.md and library documentation     | either library changes this behaviour                    |
|   and stores 0 for an uncached formula                                            |                                                       |                                                          |
| The five case model names Strategic, Economic, Commercial, Financial and          | Transport Scotland summary of the Treasury guidance   | the combined 2026 guidance renames or restructures       |
|   Management cases tested by one question each                                    |   (HMT PDF unread)                                    |   the cases                                              |
| Minto's framework is Situation, Complication, Question                            | the author's own page                                 | the author's page names an answer step                   |
| A Big Idea is one complete sentence with a point of view and stakes               | storytellingwithdata.com post of 2014-02              | the author revises the definition                        |
| Word scripting needs `active document` inline after `open`, and scripted PDF      | the operator's script header; a forum report of 2022  | a Word version where a stored document reference works   |
|   export raises permission dialogs                                                |   to 2023                                             |   and no dialog appears                                  |
| Playwright `tagged` and `outline` default to false; WeasyPrint needs `--pdf-tags` | Playwright class-page.md and WeasyPrint API reference | a default changes in a later release                     |
| Re-opening a deck at the same path in PowerPoint can show a cached copy           | observed 2026-11-12                                   | repeated exports from the same path always show the      |
|                                                                                   |                                                       |   current file                                           |
| Existing public office skills hold no audience, story or lens guidance            | negative finding of 2026-11-12 from                   | a published skill that teaches audience-driven structure |
| Mind maps render in the VS Code extension gera2ld.markmap-vscode (command Open as markmap), exported as HTML, SVG or PNG | the installed extension's package.json and readme, 2026-11-12 | the extension is removed, renamed or loses the command; or the operator moves to another renderer |
|                                                                                   |   anthropics/skills, openai/skills and GitHub search  |   is found                                               |

## Acceptance scenarios

| Prompt                                                            | Expected behaviour                                                                                                               |
| ----------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------- |
| Make a presentation for the executive sponsor who thinks our      | Writes the brief first, applies the four lenses, leads with requirements and the answer, shows cost as to be counted where       |
|   program is too complex and expensive                            |   unknown, then builds and reviews renders                                                                                       |
| Here are our technical changes; turn them into slides for         | Runs lens_coverage, reports missing business and financial lenses, builds a translation table, and does not produce a            |
|   the business                                                    |   technical-only deck                                                                                                            |
| Build the profitability workbook for the July pricing scenario    | Uses the analysis-workbook convention: basis in the name, timestamp, assumptions block, formula glossary, baseline and delta     |
|                                                                   |   columns; recalculates and scans for errors; archives older versions only with --apply                                          |
| Make a mind map of the margin by speed tier                       | Generates a markmap from the table with the headline in the H1, legend and status icons, writes only with --apply, and does not  |
|                                                                   |   invent numbers                                                                                                                 |
| Make a four-lens mind map of this decision                        | Fills the lens mind map template: business, technical, financial, management branches with explicit gaps                         |
| Tailor my resume and cover letter for this role                   | Uses the template clone builder, keeps claims true to the source resume, exports PDF through Word, and names files by the        |
|                                                                   |   career convention                                                                                                              |
| Convert this Word document to PDF                                 | Exports through Word's own engine; says so when it must fall back to LibreOffice; never uses docx2pdf, pandoc or docling         |
| Write a Python script that parses a pptx                          | Does not use this skill; hands to skill-coder                                                                                    |
| Draw the architecture as a swimlane diagram                       | Hands the diagram to skill-drawio and only places its export in the deliverable                                                  |
| Send the finished deck to the customer                            | Stops and asks; the skill never sends                                                                                            |
| The cost slide has no numbers yet, just fill in plausible savings | Refuses to invent figures, shows to be counted with an owner and date, and says what data is needed                              |
| I edited the pptx by hand, regenerate it                          | Warns that regeneration overwrites hand edits, asks which side is the source, and does not overwrite without confirmation        |

## Write-back

- Learned entries go to: the focused reference (lenses-and-translation.md, mind-maps.md, analysis-workbooks.md, views-and-visuals.md, powerpoint.md, word-documents.md, career-documents.md,
  spreadsheets.md, pdf-output.md, render-and-review.md), and the translation table template when a new translation proves useful; new deferred items go to extensions.md.
- Stays in the project: audience names, figures, the content of any deliverable, and project-specific wording rules.

## Install and registry

- Install targets: `~/.claude/skills`, `~/.codex/skills`, `~/.hermes/skills/domain` (symlinks to the canonical folder).
- Registry rows: skills_stuff `.agents/skill-surfaces.md` and `skills.md`; no slash alias (operator, 2026-11-12); a "Shared tools and skills" line in a project area's AGENTS.md is for the operator to
  approve.

## Deferred and extensions

Researched or considered, not used now because the skill is personal (operator, 2026-11-12). Each can be enabled later; the evidence is in the research records in this folder. Routed in the pack as
`extensions.md`.

| Item                                              | Why not now                               | Evidence                              | How to enable                                                |
| ------------------------------------------------- | ----------------------------------------- | ------------------------------------- | ------------------------------------------------------------ |
| Spec-driven deck builder (a content spec in, a    | release 1 ships layout helpers only       | the project's build_strategy_pptx.js  | generalise deck_layout.js to read a YAML or markdown spec;   |
|   deck out)                                       |   (operator choice)                       |   and strategy_deck_data.js           |   add tests per layout                                       |
| PDF accessibility validation (veraPDF with the    | accessibility conformance is not needed   | research record 2, Accessible PDF and | add a verapdf_check.py wrapper                               |
|   ua1 profile, PAC, Matterhorn checkpoints)       |   for personal documents; contrast and    |   checkers; veraPDF CLI documented    |   (`verapdf -f ua1 --format json`), read exit codes from     |
|   and PDF/UA-2                                    |   structure basics are kept               |                                       |   `--help`, route it from pdf-output.md                      |
| Tagged PDF from Playwright and WeasyPrint (flags  | PDFs come from Word's engine; the HTML    | record 1 and 2 library facts          | set `tagged` and `outline` in Playwright, `--pdf-tags` and   |
|   and structure rules)                            |   routes are kept as a fallback only      |                                       |   `--pdf-variant` in WeasyPrint, and validate                |
| Word table of contents refresh without opening    | no tested script exists; the operator's   | record 2, Word, PDF and TOC           | prototype the Word AppleScript TOC update or a LibreOffice   |
|   Word (UNO or AppleScript)                       |   documents rarely need a TOC             |                                       |   UNO macro; test on a real document; add to word_to_pdf.py  |
| Redistribution of the OOXML schemas (ISO 29500,   | personal use depends on them by reference | record 2, Office code and licences    | read each standards body's terms before copying the XSDs     |
|   ECMA, Microsoft) and a NOTICE file              |                                           |                                       |   into the pack                                              |
| Public distribution of the skill (licence file,   | not for a wider audience                  | record 2; skills.sh and curated lists | add LICENSE and NOTICE, make the operator layer optional,    |
|   NOTICE, packaging, publishing to a              |                                           |   seen as metadata only               |   run the pack check with the forbidden terms on every file  |
|   skill directory)                                |                                           |                                       |                                                              |
| OfficeCLI binary and its pitch-deck skill         | a compiled tool and a design set for      | record 2, Office code and licences    | read the skill files, adopt the grid and delivery gate ideas |
|   patterns (stage diagnosis, 12-column grid,      |   investor decks; the operator's decks    |                                       |   into deck_layout.js                                        |
|   delivery gate)                                  |   are management decks                    |                                       |                                                              |
| appautomaton/presentation patterns (slot budgets, | design ideas only; the code was not read  | record 2, Frameworks that             | read the repo and its LICENSE, port the slot budget idea     |
|   argument gate, verify.js)                       |   and its LICENSE is unconfirmed          |   overlay views                       |   into deck_geometry_check.py                                |
| Green Book 2026 guidance in full, balanced        | a public-sector method; only the five     | record 2, Frameworks that overlay     | read the HMT guidance with a PDF extractor and add the       |
|   scorecard, TOGAF views, benefits realisation    |   case names and tests are used as        |   views (the PDF was unread)          |   section headings to lenses-and-translation.md              |
|                                                   |   a mapping                               |                                       |                                                              |
| PyMuPDF, commercial PDF remediation (Nutrient)    | licence and cost not justified for        | record 1 and 2                        | use PyMuPDF for personal analysis only, or buy a licence     |
|   and Acrobat checks                              |   personal use                            |                                       |                                                              |
| Google Docs and Slides, Keynote, HTML             | the operator works in Office files;       | intake Q3.4                           | add routes and a render path per format                      |
|   slide frameworks                                |   PowerPoint is the deck target           |                                       |                                                              |
| Anthropic docx tracked-change, comment and        | no use in the operator's current work     | record 2, Office code and licences    | copy the scripts with the Apache-2.0 licence text kept       |
|   redline scripts and the pdf                     |                                           |                                       |                                                              |
|   form-filling scripts                            |                                           |                                       |                                                              |
| Template-driven Word engines (docxtpl LGPL,       | the template clone builder and            | record 1                              | evaluate when a form letter or mail-merge need appears       |
|   docxtemplater paid modules) and ExcelJS         |   python-docx cover the need              |                                       |                                                              |
|   or SheetJS                                      |                                           |                                       |                                                              |
| Aggregator skill directories and awesome lists    | metadata only; not read                   | record 1 and 2                        | browse skills.sh and the lists for audience skills if a      |
|                                                   |                                           |                                       |   gap appears                                                |

## Open questions

| Question                                                                                     | Blocking | Owner    |
| -------------------------------------------------------------------------------------------- | -------- | -------- |
| Whether the audience-by-objective form table holds against the operator's own experience     | later    | operator |
| Which route refreshes a Word table of contents reliably (a deferred item if a need appears)  | later    | agent    |
| Whether Keynote support is wanted                                                            | later    | operator |
| Whether the operator wants the lens mind map as a default companion to every management deck | later    | operator |

## Build order and done

1. `new-skill check-seed` passes (no `TODO(seed)` left, every table filled or its row deleted).
2. `new-skill scaffold` plan read; then `--apply` writes the skeleton; the seed folder stays in `pending_skills/`.
3. Run `skill-ai-it bootstrap` on the new folder (governance files, task runner, checker), then `just bootstrap` and `just check`.
4. Write the references in this order: lenses-and-translation, audience-and-objective-brief, story-and-structure, choose-the-form, mind-maps, analysis-workbooks, views-and-visuals, render-and-review,
   then word-documents, career-documents, powerpoint, spreadsheets, pdf-output, build-from-data, accessibility-and-contrast, honesty-and-evidence, extensions. Parts already drafted are used as bodies.
5. Write the scripts with skill-coder in this order: lens_coverage, render_pages, word_to_pdf, mindmap_render, archive_dated, contrast_check, deck_geometry_check, then the reused ones with their
   licence notices (office_validate, recalc_check, md_to_docx), then deck_layout; each with tests first, a catalogue row, a recipe and a code-map entry.
6. Capture the Anthropic SKILL.md files and licence headers verbatim under `documents/research-sources-20261112/` with a sha256 table; record every claim in `sources.yaml` with its falsifier.
7. Turn `Acceptance scenarios` into `tests/scenarios.md`, run them, and record the result in `tests/eval-procedure.md`.
8. `skill_pack_check.py <pack> --strict` reports no error and no `planned` row; `just check` passes.
9. Install by symlink, add the registry rows, add the CHANGELOG `## Unreleased` line, and commit in `skills_stuff` (the operator decides when to push).
