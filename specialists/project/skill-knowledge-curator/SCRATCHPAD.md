---
Title: skill-knowledge-curator Scratchpad
Category: scratchpad
Kind: state
Status: current
Authority: working state only; durable rules live in references/, decisions in docs/catalog.md, changelog.md and project-context
Scope: Current state, open items, next actions and memory pointers for skill-knowledge-curator (alias skill-kc)
Last reviewed: 2026-10-27
Summary: Working state after 2026-10-27; v1 kernel tested on a synthetic fixture, v2 staged roadmap agreed (nothing built), real-corpus pilot next.
Budget: 200 lines, 25 KB
Keep: Next actions=1, Memory pointers=1, Session history=2, Current state=3, Recent decisions=3
Open items tracker: docs/trackers/open-items-20261027_2022.md
---

# SCRATCHPAD

## Current state — KEEP

- Pack built 2026-10-27: `SKILL.md` (alias skill-kc), 8 references, 4 schemas, `scripts/knowledge_curator.py` (kc) over `knowledge_curator_lib/`, 42 tests, `just check` green.
- Installed as symlinks in `~/.claude/skills` and `~/.codex/skills`; `/skill-kc` alias in `~/.claude/CLAUDE.md`.
- Tested on the synthetic fixture only; a read-only inventory of the MCP audit corpus ran (24 files, 213 sections, 0.14 s, 5 byte-copy pairs).
- v2 spec catalogued 2026-10-27 (`docs/knowledge-curator-foss-implementation-spec-v2.md`); conflicts V1-V9 settled; staged roadmap in references/feature-inventory.md, nothing built.

## Open items — KEEP

- Real-corpus pilot on `/Volumes/Data/_ai/_project/project_stuff/mcp-post-migration-audit` (cases A-F in references/evaluation.md); ledgers in a scratch copy first. Offered to the operator 2026-10-27,
  not yet answered.
- Semantic evaluation gold set (design 13.2) not built.
- skill-slurp-chat Step 4b wiring: after the pilot passes (operator, 2026-10-27).
- NLI signal untested: `just bootstrap-nli` not run (pulls torch); label order of the default model is UNVERIFIED.
- Render's secret regex can false-positive on prose such as "token: abcdef" (fails closed); tune if a pilot hits it.
- v2 stage 1 inputs (spec section 13): Mermaid and draw.io encodings in use, existing shared SQLite index and its routing, slurp overlap; a read-only survey answers the first.
- V7 (`V2-T` test-ID namespace) and V8 (v1 layout) are agent defaults, not asked; confirm with the operator when convenient.
- wiki_stuff `scripts/project_page.py` `section_entries` matches `## Current state` exactly, so a `## Current state — KEEP` heading renders no state on the
  project page (found 2026-10-27); fix belongs in wiki_stuff, not done here.

## Recent decisions — KEEP

- 2026-10-27: derived first, gated promotion per category page, archive plan only, JSONL ledgers plus Markdown views, full design stack, `.kc/` folder (all operator).
- 2026-10-27: `evidence_verified` gate on by default after a review note the operator forwarded.
- 2026-10-27: v2 as a staged roadmap on v1; all four formats; federation within one portfolio; v1 schema kept with v2 mapping; optional model adapter; both promotion paths; slurp Step 4b;
  run envelope, `offline_only`, model allowlist (all operator; catalog v2 section).

## Session history — KEEP

- 2026-10-27: docs moved and renamed, 12 conflicts found and settled with the operator, v1 kernel and references written under skill-coder, skill-coder P-31 write-back.
- 2026-10-27 evening: v2 spec catalogued and renamed, nine conflicts settled in two question rounds, v2 staged roadmap written; slurp and commit.

## Next actions — KEEP

1. Real-corpus pilot (gate 0): copy the MCP audit corpus to a scratch folder, `just kc init` / `inventory --apply`, extract claims by worksheet batches, relate, review with the operator.
2. Record results in references/evaluation.md; then v2 stage 1 (code-level gap matrix) per references/feature-inventory.md.

## Memory pointers — KEEP

- memory-keeper channel `skill-kc`: keys `skill-kc.build-20261027`, `session.closeout.20261027.skill-kc`; checkpoint `slurp-20261027-skill-kc`; v2 session key `skill-kc.v2-spec-20261027`, checkpoint `slurp-20261027-skill-kc-v2`.
- project-context project `skill-knowledge-curator`.
