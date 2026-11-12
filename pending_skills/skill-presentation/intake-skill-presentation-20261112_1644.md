---
Title: Skill intake: skill-presentation
Category: skill-intake
Status: draft
Authority: >-
  Interview record for the skill-presentation pack: the operator's answers (USER_STATED, 12 Nov 2026) and facts harvested from the engagement conversation and the first hand-written seed; the research plan the seed is built from
Scope: What the operator wants the skill to do, what to harvest from existing work, and which topics still need online research
Last reviewed: 20261112_1644
Summary: >-
  Intake for skill-presentation: answers by round, the material to harvest, neighbour skills and five research topics (the gaps left by the first five research reports) that become research briefs.
---

# Skill intake: skill-presentation

## Contents

- [Parameters](#parameters)
- [Round 1: purpose and callers](#round-1-purpose-and-callers)
- [Round 2: boundaries and safety](#round-2-boundaries-and-safety)
- [Round 3: knowledge to keep](#round-3-knowledge-to-keep)
- [Round 4: quality and install](#round-4-quality-and-install)
- [Material to harvest](#material-to-harvest)
- [Neighbour skills to study](#neighbour-skills-to-study)
- [Research topics](#research-topics)

---

## Parameters

```text intake-parameters
name: skill-presentation
family: specialists/project
short_description: Presentations and reports for any audience: pick the form (deck, Word, Excel, PDF, one-pager), cover business, technical, financial and management views, build from data, render and review. Not diagrams or code.
scripts: yes
operator_context: yes
memory_channel: presentation
related: skill-coder, skill-drawio, skill-commtracker, skill-knowledge-curator
forbidden_terms: Martin, Sandro, Litebooth, Iridium, Cambium, Malik, Uday, Rob, George, APN, enterprise-strategy
```

## Round 1: purpose and callers

- Q1.1 In one sentence, what should an agent be able to do with this skill that it cannot do reliably now? Answer: Decide how a presentation or report must be shaped for its audience and objective,
  cover business, technical, financial and management views in it and translate between them, then build it in the right format (PowerPoint, Word, Excel, PDF) from data and review it as renders before
  it is shown. (USER_STATED, operator 12 Nov 2026: "I'm more technical ... they are thinking about business and cost ... things are not translated properly.")
- Q1.2 Who or what calls it, and in which situations (the operator, another skill, a project)? Give the phrases you would say. Answer: The operator preparing material for managers, sponsors, customers
  or technical leads; any project that turns analysis into a deliverable; a reviewer checking a draft for tilt. Phrases: make a presentation for management; write this up for the business; how should
  I present this to a non-technical audience; turn this into slides, a Word document or a one-pager; management does not see the value; is this covering cost and business, not only technical; review
  my slides before I send them. (harvested from the engagement; USER_STATED where quoted)
- Q1.3 Is it a method or practice for any project, one product or tool, a single-file contract, or personal? Answer: A method and practice for any project: specialists/project. (USER_STATED:
  "skill-presentation ... all sorts of presentations that are possible")
- Q1.4 What should it be called (skill-topic, lowercase) and is a slash alias wanted? Answer: skill-presentation; no slash alias. (USER_STATED, 12 Nov 2026: alias question answered "No alias")
- Q1.5 Is this skill for wider use or for your own use? Answer: Personal use only, not for a wider audience: everything researched and built must fit the operator's own requirements and project work; anything researched that this does not need is recorded as deferred so it can be enabled or built later. Because it is personal, the forbidden names apply to the generic references only and the operator layer may name the operator's projects, stakeholders and tools. (USER_STATED, operator 12 Nov 2026)

## Round 2: boundaries and safety

- Q2.1 What must it not do, and which neighbouring skill owns that instead? Answer: Draw diagrams and flow maps (skill-drawio); write or review code (skill-coder); file and thread stakeholder messages
  (skill-commtracker); audit documents for stale facts (skill-knowledge-curator); state domain facts shown in a deliverable (the domain skill that owns them); send, publish or present a deliverable
  (the operator, always explicitly). (harvested from the first seed; confirmed by the engagement)
- Q2.2 What may it write, what needs your approval or `--apply`, and what must it never do (send, publish, delete, touch live systems)? Answer: It may write only the deliverable's source and its
  derived file and scratch renders; each write script plans first and needs --apply. It never sends or publishes, never puts a credential or private detail into a file, never edits a derived file by
  hand, never copies a work without its licence terms, never presents an unreviewed render, and never invents a figure, date, saving or quote. (USER_STATED rulings of 12 Nov 2026 plus the engagement)
- Q2.3 Will it need scripts (checks, builders, converters), or is it guidance only? Answer: Yes. Release 1 ships the checks (lens coverage, render pages, contrast, geometry, office validate, recalc)
  and the layout helpers from the deck builder; a spec-driven deck builder is release 2. (USER_STATED, 12 Nov 2026: "Layout helpers first")
- Q2.4 Which rules are yours alone (tone, spelling, naming, estate) and belong in an operator layer, and which names must never appear in the shared pack? Answer: Operator layer: no contractions in
  anything drafted for the operator, Australian spelling ("program"), file names slug-YYYYMMDD_hhmm, stakeholder-specific wording rules. In the generic pack: DOCX to PDF always through Word's own PDF
  engine on macOS with LibreOffice only as the fallback when Word is not available (USER_STATED, 12 Nov 2026: "Rule for every document"). Forbidden names: Martin, Sandro, Litebooth, Iridium, Cambium,
  Malik, Uday, Rob, George, APN, enterprise-strategy (USER_STATED, 12 Nov 2026).

## Round 3: knowledge to keep

- Q3.1 Which work has taught you what the skill must hold (sessions, projects, files, transcripts)? List each; the agent harvests them. Answer: The 12 Nov 2026 strategy deck engagement (requirements,
  grid, timeline, flow, cost, component and gap slides built natively, reviewed as renders); the draft strategy document; the Friday status workbook built from data; the two 13 Oct decks and their
  builder; the shared markdown to Word converter; the five web-research reports of 12 Nov 2026 saved in research/. (harvested)
- Q3.2 What went wrong first, and what fixed it? These become rules. Answer: Technical content in discovery order read as complex and expensive (fix: four lenses and answer first); a drawn
  many-to-many tree collapsed into line crossings (fix: a grid); verbatim transcript quotes and meeting narration felt like an investigation (fix: paraphrase, natural tone); a plausible-looking quote
  was invented (fix: re-read and remove); five layout faults visible only in renders (fix: render every slide and look); PowerPoint showed a cached copy of a re-opened file (fix: render a fresh copy
  under a new name); a made-up saving would have destroyed trust (fix: "to be counted" with owner and date). (USER_STATED and observed, 12 Nov 2026)
- Q3.3 Which code or scripts already exist and are likely to be reused (paths)? Answer: the deck builder and its data module (apn enterprise-strategy scripts/build_strategy_pptx.js,
  strategy_deck_data.js); scripts/render_pptx_pages.py; the shared scripts/md_to_docx.py in project_stuff; the weekly workbook builder scripts/weekly_update_xlsx.py and its preview; the Apache-2.0 doc
  skill's scripts/render_docx.py; the Apache-2.0 Anthropic office scripts (validate, recalc, soffice wrapper) after their headers are read. (harvested)
- Q3.4 Which products, formats and versions are in scope, and which are explicitly out? Answer: In scope: PowerPoint (pptxgenjs 4.0.1, python-pptx 1.0.2), Word (docx-js 9.15.3, python-docx 1.2.0,
  pandoc 3.14), Excel (XlsxWriter 3.3.1, openpyxl 3.1.5), PDF (Word export, WeasyPrint 70, Playwright, reportlab), one-page summaries in markdown or Word, rendering with PowerPoint, Word, LibreOffice
  and poppler on macOS. Out: Google Docs and Slides, Keynote (not yet), web dashboards, diagrams (skill-drawio). (harvested; versions from the research record)
- Q3.5 Which existing work must the skill also cover? Answer: The extensive spreadsheet work in the carrier and fibre profitability projects (profitability and scenario workbooks, basis-labelled, timestamped, with an assumptions section and a formula glossary) and the markmap-style markdown mind maps those projects generate from data (profit by group, scenario comparisons, enriched views) and write by hand (target and progress maps); mind maps are a deliverable form of the skill. (USER_STATED, operator 12 Nov 2026)

## Round 4: quality and install

- Q4.1 Give three to five example prompts, including one that must not trigger the skill and one where the agent must stop and ask. Answer: (1) Make a presentation for the executive sponsor who thinks
  the program is too complex and expensive: brief first, four lenses, answer first, to be counted where unknown. (2) Here are our technical changes, turn them into slides for the business: lens
  coverage report, translation table, no technical-only deck. (3) Build a status workbook from this YAML: spreadsheet route, summary sheet first, colour plus label, recalculate and scan. (4) Write a
  Python script that parses a pptx: does not trigger (skill-coder). (5) Send the deck to the customer: stops and asks. (6) Fill in plausible savings: refuses to invent. (7) I edited the pptx by hand,
  regenerate it: warns that regeneration overwrites. (harvested from the first seed)
- Q4.2 What evidence standard applies (primary sources only, or practice accepted if labelled)? Answer: Practice is accepted when labelled USER_STATED, VERIFIED_PRIMARY, VERIFIED_SECONDARY or
  UNVERIFIED with its source; licences are read in the files themselves; load-bearing library behaviour is checked against version-matched documentation. (operator standard, global instructions)
- Q4.3 Which decisions are still open, and which block the build? Answer: Open and not blocking: scripted PowerPoint export prompts on macOS and Keynote support; how to refresh a Word table of
  contents without opening the app; the PDF/UA validator; whether the audience-by-objective form table holds (an unverified synthesis for the operator to review). Nothing blocks the build. (harvested)

## Material to harvest

| Source                                    | Where                                                                    | What to extract                                                               |
| ----------------------------------------- | ------------------------------------------------------------------------ | ----------------------------------------------------------------------------- |
| The engagement conversation of 12         | this session's transcript                                                | operator rulings, mistakes and fixes, the review findings of the deck, the    |
|   Nov 2026                                |                                                                          |   four-lens requirement                                                       |
| The first hand-written seed               | pending_skills/skill-presentation/seed-skill-presentation-20261112_1544.md | lessons, routing, scripts plan, standing rules, scenarios to reuse            |
|                                           |                                                                          |   and correct                                                                 |
| The five research reports                 | pending_skills/skill-presentation/research/research-20261112_1600.md     | licences, library gotchas, the audience-skill gap, rules with evidence labels |
| The three drafted parts                   | pending_skills/skill-presentation/parts/                                 | lenses and translation, the audience brief, choosing the form                 |
| The project builders and workbook scripts | apn enterprise-strategy scripts/, project_stuff scripts/md_to_docx.py    | reusable layout helpers, converters and their docstrings and tests            |
| The profitability projects | apn vocus-profitability and opticomm-profitability: docs/reports (profitability, scenarios, mindmaps), scripts (generate_profit_mindmap-generic.py, generate_hyp_mindmap*.py, gen_profitability_vs_retail.py, opticomm_export_speed_tier_profitability.py), AGENTS.md rules | workbook conventions, markmap mind map form and generators, the archive rule for dated outputs |
| The operator's deliverable survey | pending_skills/skill-presentation/research/research-20261112_1700.md | what the operator actually produces and with which scripts: workbooks, Word and PDF, one deck project |
| The career document builders | me/career/04-resumes/scripts (docx_builder.py, build_resume.py, docx_to_pdf_word.sh, pdf_export.py) | template-clone Word builder, the Word-engine PDF export and its AppleScript gotcha |

## Neighbour skills to study

- skill-nautobot, skill-vagrant, skill-coder, skill-network-architect and skill-systems-architect (the pack standard, read once)
- skill-drawio (diagrams and exports), skill-commtracker, skill-knowledge-curator
- the installed doc, spreadsheet and pdf skills (Apache-2.0)

## Research topics

| Area                                                  | Questions the research must answer                                                    | Products, formats or versions in scope               |
| ----------------------------------------------------- | ------------------------------------------------------------------------------------- | ---------------------------------------------------- |
| Frameworks that combine business, technical,          | Which published frameworks overlay strategic, economic, financial, technical and      | UK Treasury Green Book business case guidance,       |
|   financial and management views                      |   management views in one proposal (five case model business case, balanced           |   ISO/IEC/IEEE 42010 viewpoints, TOGAF views,        |
|                                                       |   scorecard, architecture viewpoints, decision memo and RAID); what exactly are their |   balanced scorecard, benefits realisation           |
|                                                       |   sections and questions; how do practitioners translate technical points into        |                                                      |
|                                                       |   outcome, cost and decision; where do they publish templates                         |                                                      |
| Audience and communication primary sources            | What do the primary pages of Minto (pyramid, SCQA), Knaflic (big idea, who what how), | official pages of the authors and organisations,     |
|                                                       |   Duarte (Resonate), SBAR, BLUF, Amazon narrative and PR/FAQ and Made to Stick        |   Harvard Business Review, government plain-language |
|                                                       |   actually say; which concrete rules can an agent run; which earlier claims marked    |   and digital service guidance                       |
|                                                       |   UNVERIFIED hold when the page is read                                               |                                                      |
| Word to PDF and table of contents fields on macOS     | Can Word be scripted (AppleScript or JXA) to update TOC fields and export PDF         | Microsoft Word for Mac, AppleScript and JXA,         |
|                                                       |   reliably and headlessly, with what permission prompts; how do Word and LibreOffice  |   LibreOffice headless, docx 9.15.3, python-docx     |
|                                                       |   differ in fonts and page breaks; what are the failure modes of docx-js and          |   1.2.0, docx2pdf, pandoc 3.14                       |
|                                                       |   python-docx TOC fields                                                              |                                                      |
| Accessible PDF and document checkers                  | How do Word and Chromium and WeasyPrint produce tagged PDF; which validators          | PDF/UA, WCAG 2.2, WeasyPrint 70, Playwright 1.65,    |
|                                                       |   (veraPDF, PAC, Acrobat checks) can run headless; what is a minimal accessibility    |   Word accessibility checker, PowerPoint             |
|                                                       |   checklist for decks, documents and PDFs with sources                                |   accessibility checker                              |
| Reusable office code and its licence terms            | In the Apache-2.0 office skills and OfficeCLI: which scripts are worth adopting, what | github.com/anthropics/skills skills/pptx docx xlsx   |
|                                                       |   is in each script's header and any NOTICE or third-party file (including the XSD    |   pdf, OfficeCLI, skills.sh, curated skill lists     |
|                                                       |   schemas), what do validate and recalc depend on; what do skills.sh and the curated  |                                                      |
|                                                       |   lists add for presentation and audience skills beyond what is already known         |                                                      |
