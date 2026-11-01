---
Title: skill-knowledge-curator Scratchpad
Category: scratchpad
Kind: state
Status: current
Authority: working state only; durable rules live in references/, decisions in docs/catalog.md, changelog.md and project-context
Scope: Current state, open items, next actions and memory pointers for skill-knowledge-curator (alias skill-kc)
Last reviewed: 2026-11-01
Summary: Working state after 2026-11-01; Continuum pilot fixes built and committed, gate 0 passed, remaining findings and v2 stage 1 next.
Budget: 200 lines, 25 KB
Keep: Next actions=1, Memory pointers=1, Session history=2, Current state=3, Recent decisions=3
Open items tracker: docs/trackers/open-items-20261027_2022.md
---

# SCRATCHPAD

## Current state — KEEP

- Pack built 2026-10-27: `SKILL.md` (alias skill-kc), 8 references, 4 schemas, `scripts/knowledge_curator.py` (kc) over `knowledge_curator_lib/`, 42 tests, `just check` green.
- Installed as symlinks in `~/.claude/skills` and `~/.codex/skills`; `/skill-kc` alias in `~/.claude/CLAUDE.md`.
- 2026-11-01: Continuum fixes built (P1-P4, P8-P10, P12-P16, P18-P21, P25-P27), 82 tests, `just check` green; gate 0 passed on the scratch rerun (references/evaluation.md).
- Real use: Continuum only (45 sources, 3,496 claims). `render`, `promote`, `archive-plan`, slurp `intake` have not served a real project.
- v2 spec catalogued 2026-10-27 (`docs/knowledge-curator-foss-implementation-spec-v2.md`); conflicts V1-V9 settled; staged roadmap in references/feature-inventory.md, nothing built.

## Open items — KEEP

- `candidates` 1.9 s at 3,496 claims, within budget; `kc drift` precision is low, advisory only.
- Not built: P5, P6, P7, P17, P22-P24 (references/feature-inventory.md, Fixes). P25's predicate list came from Continuum's counts; `must` stays in conflict detection.
- Continuum recorded the operator rulings of 2026-11-01 21:41 (55 decided, 45 open); `cf-73c4a38aa4` left open by the operator. Repair pending there: `cl-1334d9309fb3` successor back to `cl-c9b26284d37f` (`kc amend cf-1c11b8d333 --set-successor`, P27).
- MCP audit cases A-F: optional since 2026-11-01.
- `kc amend` proven live 2026-11-01 21:12: Continuum recorded `cl-88cec07d70a0` and `cl-f3c2d0e95086` under `cf-d846a9dbb3` (`dr-0c0fe64c12f5`, `dr-cc7b80dd7306`); `validate` ok, 61 decisions.
- Semantic evaluation gold set (design 13.2) not built.
- skill-slurp-chat Step 4b wiring: unblocked by gate 0, not started.
- NLI signal untested: `just bootstrap-nli` not run (pulls torch); label order of the default model is UNVERIFIED.
- Render's secret regex can false-positive on prose such as "token: abcdef" (fails closed); tune if a pilot hits it.
- v2 stage 1 inputs (spec section 13): Mermaid and draw.io encodings in use, existing shared SQLite index and its routing, slurp overlap; a read-only survey answers the first.
- V7 (`V2-T` test-ID namespace) and V8 (v1 layout) are agent defaults, not asked; confirm with the operator when convenient.
- Wiki page shows no Recent changes: `project_page.py` reads dated CHANGELOG headings, this changelog keeps dated bullets under `## Unreleased`. Undecided: dated
  headings here (`just changelog-entry`) or teach the generator to read bullets.

## Recent decisions — KEEP

- 2026-11-01: gate 0 = Continuum plus rerun; `kc amend` for P19; priorities 1-6 built; Continuum ledger read-only this session (all operator).
- 2026-10-27: derived first, gated promotion per category page, archive plan only, JSONL ledgers plus Markdown views, full design stack, `.kc/` folder (all operator).
- 2026-10-27: `evidence_verified` gate on by default after a review note the operator forwarded.
- 2026-10-27: v2 as a staged roadmap on v1; all four formats; federation within one portfolio; v1 schema kept with v2 mapping; optional model adapter; both promotion paths; slurp Step 4b;
  run envelope, `offline_only`, model allowlist (all operator; catalog v2 section).

## Session history — KEEP

- 2026-11-01: findings reviewed, diagram redrawn, Continuum fixes built and measured on a scratch copy; Rust not needed (operator asked; runtimes are seconds, the cost is agent tokens).
- 2026-10-27: docs moved and renamed, 12 conflicts found and settled with the operator, v1 kernel and references written under skill-coder, skill-coder P-31 write-back.
- 2026-10-27 evening: v2 spec catalogued and renamed, nine conflicts settled in two question rounds, v2 staged roadmap written; slurp and commit.
- 2026-10-27 20:30: wiki_stuff `project_page.py` fixed for annotated headings (`45423a3`); commit here blocked by skill-ai-it's in-progress script move.

## Next actions — KEEP

1. Run a second real corpus (MCP audit), since Continuum is the only real test so far, then v2 stage 1 (gap matrix).

## Memory pointers — KEEP

- memory-keeper channel `skill-kc`: keys `skill-kc.build-20261027`, `session.closeout.20261027.skill-kc`; checkpoint `slurp-20261027-skill-kc`; v2 session key `skill-kc.v2-spec-20261027`, checkpoint `slurp-20261027-skill-kc-v2`; handoff key `skill-kc.handoff-20261027`, checkpoint `slurp-20261027-skill-kc-handoff`.
- project-context project `skill-knowledge-curator`.
