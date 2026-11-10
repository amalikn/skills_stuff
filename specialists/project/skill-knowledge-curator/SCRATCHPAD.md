---
Title: skill-knowledge-curator Scratchpad
Category: scratchpad
Kind: state
Status: current
Authority: working state only; durable rules live in references/, decisions in docs/catalog.md, changelog.md and project-context
Scope: Current state, open items, next actions and memory pointers for skill-knowledge-curator (alias skill-kc)
Last reviewed: 2026-11-05
Summary: Working state after 2026-11-05; kc roots and kc verify (local oMLX model) built and measured on the MCP pilot; a new labelled corpus is the next step.
Budget: 200 lines, 25 KB
Keep: Next actions=1, Memory pointers=1, Session history=2, Current state=3, Recent decisions=3
Open items tracker: docs/trackers/open-items-20261027_2022.md
---

# SCRATCHPAD

## Current state — KEEP

- Pack built 2026-10-27: `SKILL.md` (alias skill-kc), 8 references, 4 schemas, `scripts/knowledge_curator.py` (kc) over `knowledge_curator_lib/`, 42 tests, `just check` green.
- Installed as symlinks in `~/.claude/skills` and `~/.codex/skills`; `/skill-kc` alias in `~/.claude/CLAUDE.md`.
- 2026-11-01: Continuum fixes built (P1-P4, P8-P10, P12-P16, P18-P21, P25-P28), `kc aliases`, `topics`, `recall`, `status-map`, `triage`, `sample`, 120 tests, `just check` green; gate 0 failed three
  attempts on the MCP pilot: precision 37.5% against 70%, recall 51.1% after triage (references/evaluation.md).
- 2026-11-05: `kc roots` (B3) and `kc verify` (B4: agent export/import, oMLX model `Qwen3.6-35B-A3B-4bit-DWQ`, control pairs, quote check, guarded `--confirm`), triage `documented-evolution`; 133
  tests, `just check` green. Measured: roots 23 of 24 real MCP conflicts in one group; verify safe, clears little (references/evaluation.md).
- Real use: Continuum only (45 sources, 3,496 claims). `render`, `promote`, `archive-plan`, slurp `intake` have not served a real project.
- v2 spec catalogued 2026-10-27 (`docs/knowledge-curator-foss-implementation-spec-v2.md`); conflicts V1-V9 settled; staged roadmap in references/feature-inventory.md, nothing built.

## Open items — KEEP

- `candidates` 1.9 s at 3,496 claims, within budget; `kc drift` precision is low, advisory only.
- Not built: P5, P6, P7, P17, P22-P24 (references/feature-inventory.md, Fixes). P25's predicate list came from Continuum's counts; `must` stays in conflict detection.
- Continuum recorded the operator rulings of 2026-11-01 21:41 (55 decided, 45 open); `cf-73c4a38aa4` left open by the operator. `cl-1334d9309fb3` successor repaired live (`dr-bc8472c67d49`, P27).
  Stale conflicts `cf-3a630057ef` and `cf-7076d1e08a` not yet reviewed there.
- MCP audit cases A-F: optional since 2026-11-01.
- `kc amend` proven live 2026-11-01 21:12: Continuum recorded `cl-88cec07d70a0` and `cl-f3c2d0e95086` under `cf-d846a9dbb3` (`dr-0c0fe64c12f5`, `dr-cc7b80dd7306`); `validate` ok, 61 decisions.
- Semantic evaluation gold set (design 13.2) not built.
- skill-slurp-chat Step 4b wiring: unblocked by gate 0, not started.
- verify: prompt v2 was tuned on v1's errors over the same labels, so its figures are not independent; 47 of 96 v2 verdicts were downgraded because the model quoted metadata (`doc_status`) or elided
  with "...". `verify.py` 308 lines (split planned at 300). Agent arm (`--export`) not run.
- project_stuff `mcp-post-migration-audit`: README warning now confirmed and nine reports carry correction notes (2026-11-05), NOT committed (operator asked to push skills_stuff only).
- NLI signal untested: `just bootstrap-nli` not run (pulls torch); label order of the default model is UNVERIFIED.
- Render's secret regex can false-positive on prose such as "token: abcdef" (fails closed); tune if a pilot hits it.
- v2 stage 1 inputs (spec section 13): Mermaid and draw.io encodings in use, existing shared SQLite index and its routing, slurp overlap; a read-only survey answers the first.

## Recent decisions — KEEP

- 2026-11-05: build B3 + B4 with an oMLX model arm (no download); triage history clears as `documented-evolution`; measure on fixtures, MCP labels and Continuum; V7, V8 confirmed; dated changelog
  headings; mcp-data warning confirmed and reports corrected (all operator; docs/catalog.md).
- 2026-11-01: gate 0 = Continuum plus rerun; `kc amend` for P19; priorities 1-6 built; Continuum ledger read-only this session (all operator).
- 2026-10-27: derived first, gated promotion per category page, archive plan only, JSONL ledgers plus Markdown views, full design stack, `.kc/` folder (all operator).
- 2026-10-27: `evidence_verified` gate on by default after a review note the operator forwarded.
- 2026-10-27: v2 as a staged roadmap on v1; all four formats; federation within one portfolio; v1 schema kept with v2 mapping; optional model adapter; both promotion paths; slurp Step 4b; run
  envelope, `offline_only`, model allowlist (all operator; catalog v2 section).

## Session history — KEEP

- 2026-11-05: B3 and B4 built under skill-coder; two oMLX runs on the MCP pilot (v1 refuted 75 of 96, v2 kept 83% of real); skill-coder P-56, P-57 write-back; changelog converted to day headings.
- 2026-11-01: findings reviewed, diagram redrawn, Continuum fixes built and measured on a scratch copy; Rust not needed (operator asked; runtimes are seconds, the cost is agent tokens).
- 2026-10-27: docs moved and renamed, 12 conflicts found and settled with the operator, v1 kernel and references written under skill-coder, skill-coder P-31 write-back.
- 2026-10-27 evening: v2 spec catalogued and renamed, nine conflicts settled in two question rounds, v2 staged roadmap written; slurp and commit.
- 2026-10-27 20:30: wiki_stuff `project_page.py` fixed for annotated headings (`45423a3`); commit here blocked by skill-ai-it's in-progress script move.

## Next actions — KEEP

0. Resume the UNC pilot (`skills-data/skill-knowledge-curator/unc-pilot-20261105/`, readme has the pass marks): precision on a blind sample of 40 open
   conflicts, `kc triage`, `kc roots` purity, `kc verify` agent arm against the oMLX arm, then compare with the marks. Recall now 60.8% (gate 80%).
   Offer the stale-document list (pilot `findings.md`) to the UNC owners; never edit UNC from here.
1. Review the project_stuff audit corrections and commit them there (not done by this session). The local-llm README oMLX entry in tools_stuff is uncommitted too (folder untracked).
   The Continuum session's citation_audit and decision_sheet work in this pack is its own to commit.
2. Held: P29, v2 stage 1, slurp Step 4b; research B5 (`kc resolve`) needs an adjudicated set first.

## Memory pointers — KEEP

- 2026-11-01 close: memory-keeper `session.closeout.20261101.skill-kc`, `skill-kc.mcp-pilot-20261101`; checkpoint `slurp-20261101-skill-kc-close`; record `docs/session-record-*`; pilot data
  `skills-data/skill-knowledge-curator/mcp-pilot-20261101/`.
- memory-keeper channel `skill-kc`: keys `skill-kc.build-20261027`, `session.closeout.20261027.skill-kc`; checkpoint `slurp-20261027-skill-kc`; v2 session key `skill-kc.v2-spec-20261027`, checkpoint
  `slurp-20261027-skill-kc-v2`; handoff key `skill-kc.handoff-20261027`, checkpoint `slurp-20261027-skill-kc-handoff`.
- project-context project `skill-knowledge-curator`.
