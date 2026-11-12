Research task (web research, read-only, no local file writes) for a new reusable agent skill. Generic research: do NOT use any of these words in a search query, a fetch or your report: Martin, Sandro, Litebooth, Iridium, Cambium, Malik, Uday, Rob, George, APN, enterprise-strategy

Skill being designed: Decide how a presentation or report must be shaped for its audience and objective, cover business, technical, financial and management views in it and translate between them, then build it in the right format (PowerPoint, Word, Excel, PDF) from data and review it as renders before it is shown.

Area: Word to PDF and table of contents fields on macOS Products, formats or versions in scope: Microsoft Word for Mac, AppleScript and JXA, LibreOffice headless, docx 9.15.3, python-docx 1.2.0, docx2pdf, pandoc 3.14

Questions to answer: - Can Word be scripted (AppleScript or JXA) to update TOC fields and export PDF reliably and headlessly, with what permission prompts
- how do Word and LibreOffice differ in fonts and page breaks
- what are the failure modes of docx-js and python-docx TOC fields

How to research:
1. Prefer primary sources: official documentation, the project's own repository, licence files, standards pages. Read a page before tagging a claim `VERIFIED_PRIMARY`; tag what you did not read
   `UNVERIFIED`; say which pages blocked you or returned errors instead of guessing.
2. Find existing agent skills or public examples for this area (GitHub search; github.com/anthropics/skills and github.com/openai/skills; curated lists). For the best few, read the actual SKILL.md and
   report how they are structured and what they decide.
3. For every library, tool or code you may recommend, give its current version, last-updated date and licence, quoting the licence wording exactly with the file path. Say clearly when copying is NOT
   permitted (copyleft, source-available, no licence).
4. Look for failure modes, known bugs and pitfalls, not only what works.
5. Record negative findings (nothing found for X) so they are not searched again.

Return a structured report under 1000 words: (a) a table of sources with URL, what it is, licence, last-updated, usefulness 1 to 5; (b) the most valuable concrete rules and learnings, each tagged
`VERIFIED_PRIMARY`, `VERIFIED_SECONDARY` or `UNVERIFIED` with its source URL; (c) pitfalls and failure modes; (d) code or scripts worth adopting with licence status; (e) negative findings and open
questions.

Brief written 2026-11-12 by skill-ai-it `new-skill research-briefs`.
