# Extensions: researched or considered, not used now

## Scope

This skill is for the operator's own use, so work that was researched or considered and is not needed now is recorded here instead of built. Each item says why it is not used, where the evidence is (the research records in the seed folder of the pack's origin, `pending_skills/skill-presentation/research/`) and how to enable it. When the skill is extended, start here, then move the item out of this list.

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
