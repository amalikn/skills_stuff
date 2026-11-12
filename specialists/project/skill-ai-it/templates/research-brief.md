---
Title: Research brief template
Category: template
Status: current
Authority: local-supplement
Scope: The prompt a research agent receives for one research topic of a new skill; the front matter is stripped when a brief is written
Last reviewed: 2026-11-12
Summary: Generic web-research prompt with placeholders for the area, scope, questions and the forbidden words; filled by new-skill research-briefs.
---

Research task (web research, read-only, no local file writes) for a new reusable agent skill. Generic research: do NOT use any of these words in a search query, a fetch or your report: {{FORBIDDEN}}

Skill being designed: {{PURPOSE}}

- **Area:** {{AREA}}
- **Products, formats or versions in scope:** {{SCOPE}}

Questions to answer:

{{QUESTIONS}}

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

Brief written {{DATE}} by skill-ai-it `new-skill research-briefs`.
