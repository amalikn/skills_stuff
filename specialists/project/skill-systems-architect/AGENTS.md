---
Title: Skill maintenance and operating boundaries
Category: governance
Status: current
Authority: authored-guidance
Scope: Portable architecture skill pack
Last reviewed: 2026-10-29
Summary: Skill maintenance and operating boundaries for evidence-based architecture work.
---

# Skill maintenance and operating boundaries

This file governs work inside this skill folder. It is not a global agent policy and grants no deployment or messaging permission.
The host may not automatically load a skill-local AGENTS.md; SKILL.md explicitly asks for it.

- Read SKILL.md and only relevant references. Preserve the name/directory match and portable frontmatter.
- Keep principles in references; project state, credentials and fleet-specific commands stay in the consuming project.
- The two architects are peers; either may lead. Use [collaboration protocol](references/collaboration-protocol.md) in either direction.
- Specialist contracts are optional. Read installed entry points before invocation and respect narrower scope.
- Add ASCII diagrams when they clarify paths, layers, trust or failure domains.
- Change source documents, run `just check` and record new evidence and a CHANGELOG entry.
- A new citation: run `just fetch-sources --apply` (local copy) and `just ledger --apply` (sources.json); `just check` fails on an
  uncatalogued URL. Run `just links` before a release; it uses the network and is not part of `just check`.
- References follow the backbone in architecture-method.md (Scope, Decision rules, Patterns, Failure modes and tests, Worked
  example, Review checklist, Further reading); `just check` enforces ASCII diagrams within 110 columns, lines within 200, RFC
  links to the .html text and no contractions.
- Invoke `skill-coder` before adding or changing any script in this pack (operator, 2026-10-20; the skills_stuff root rule); recipes run
  through the working-cache venv (`just bootstrap`), never a bare interpreter.
- The six shared references (architecture method, automation and safety, collaboration protocol, diagrams and deliverables, FOSS tool
  selection, research and attribution) and `scripts/check_package.py` live in skill-network-architect; skill-systems-architect symlinks
  to them. Edit them there only.
- Never describe a static check as a lab, product, production or cross-host integration test.
- Keep scripts offline and read-only unless a later explicitly scoped requirement justifies a separate apply interface.
- Verify reference links, JSON fixtures, scenario arithmetic and negative tests before release.
- Review attribution before importing external text or code; record the upstream license in sources.json.
- Keep a change reversible; do not overwrite installed skills or hand-edited project files as part of validation.

## Operator rules (2026-10-29)

- Quality, not namesake: every reference follows the backbone in architecture-method.md, states its numbers with evidence labels and sources,
  and ends with Further reading of authoritative online material; the field is too wide to hold locally, so depth is linked.
- Local copies of cited material: RFCs, PDFs and pages are kept in `sources/` (`just fetch-sources --apply`, all-scraper for blocked pages)
  and every cited URL is in sources.json (`just ledger --apply`); `just check` fails on an uncatalogued citation.
- Markdown wrapped at 200 columns, bullets and tables over long prose, ASCII diagrams within 110 columns; `just check` enforces them.
- APN-specific knowledge is contained in skill-network-architect `operator/apn/` (the systems pack reads it by path); the general references
  stay operator-neutral. No customer, community or people names, IPs, credentials, prices, margins or invoice figures anywhere in the pack.
- Knowledge harvested from the operator's personal projects is concepts and architecture only, never personal information.
- A harvest feeds every skill that owns a finding (platform, device, practice packs), through that skill's own write-back contract.
