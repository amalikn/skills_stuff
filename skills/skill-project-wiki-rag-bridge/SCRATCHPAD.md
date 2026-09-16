# SCRATCHPAD

Agent working memory for skill-project-wiki-rag-bridge.
Use for: draft plans, terminal output, intermediate analysis, refactor outlines.
Cleared between sessions unless content is explicitly marked KEEP.

---

<!-- KEEP: updated 20260531 — all phases complete, governance refreshed -->

## Current state <!-- KEEP -->

**Phase:** All phases complete — `SKILL_DYNAMIC_RETRIEVAL_ALIGNED`. Skill installed.

Skill created 2026-05-24 (governance-ready). 2026-05-25: audit SKILL_DYNAMIC_RETRIEVAL_OUTDATED → full dynamic retrieval update applied (Phases 1–10). Prompts 02b/02c, 4 templates, 3 schemas, 2 checklists, 3 docs, 3 examples created. Coherence sweep + Archcore promotion complete (5 candidates promoted: 3 specs, 2 guides). Skill installed to `~/.claude/skills/`, `~/.codex/skills/`, `~/.hermes/skills/`. Repomix regenerated. 2026-05-31: skill-ai-it bootstrap run — SCRATCHPAD next-actions updated, repomix refreshed.

---

## Open items <!-- KEEP -->

- [x] Run `skill-project-coherence` sweep — complete 20260525_0130
- [x] Install skill to `~/.claude/skills/`, `~/.codex/skills/`, `~/.hermes/skills/` — complete 20260525
- [x] Regenerate `.ai-context/governance-pack.md` via repomix — complete 20260525
- [x] Archcore promotion for new schemas/docs — 5 candidates promoted (3 specs, 2 guides) 20260525
- [ ] Validate skill against a second real project (beyond vocus-profitability)
- [ ] Confirm rag-tools venv path is current: `tools-working-cache/rag-tools/.venv/`

---

## Key anchors

| Item | Detail |
|---|---|
| Skill entry | `SKILL.md` |
| Human guide | `README.md` |
| Workflow prompts | `prompts/00–09-*.md` |
| Gate checklists | `checklists/*.md` |
| Authority model | `docs/authority-model.md` |
| Collection policy | `docs/collection-naming-policy.md` |
| Schemas | `schemas/*.schema.yaml` |
| Templates | `templates/` |
| Examples | `examples/vocus-profitability/`, `examples/generic-project/` |
| rag-tools venv | `tools-working-cache/rag-tools/.venv/` |
| Qdrant wiki prefix | `rag__wiki_<domain>` |
| Qdrant project prefix | `rag__project_<slug>` |

---

## Recent decisions

- 2026-05-24 — Skill scoped to multi-project (not Vocus-specific). Vocus is reference example only.
- 2026-05-24 — Collection naming enforced by policy only (Qdrant has no built-in multi-tenancy).
- 2026-05-24 — Embedding model locked to `sentence-transformers/all-MiniLM-L6-v2` (384 dims) — cannot mix.
- 2026-05-24 — Archcore initialized; durable rules/ADRs/specs extracted from existing skill content.

---

## Session history (summaries — full detail in mcp-project-context)

### 2026-05-31 — Governance refresh + ARCHITECTURE.md + SETUP.md <!-- KEEP -->
- skill-ai-it bootstrap: SCRATCHPAD next-actions cleaned; repomix regenerated; CHANGELOG appended
- ARCHITECTURE.md created: 3 detailed text diagrams (layer model, retrieval flow, collection isolation); vector_rag Python-only constraint documented; all 13 CLI commands annotated
- SETUP.md created: corrected rag-tools venv path (tools-working-cache not tools_stuff); install commands for all 3 runtimes; first-use sequence
- Evidence basis: mcp-project-context note (slurp-20260531-skill-pwrb-architecture-setup)

### 2026-05-25 — Dynamic retrieval audit + Phase 1 SKILL.md update <!-- KEEP -->
- context-mode Node.js fix: better-sqlite3 upgraded to 12.10.0; Node 22 pinned via `mcp-working-cache/context-mode/bin/node` symlink; plugin.json patched to use symlink
- Audit confirmed `SKILL_DYNAMIC_RETRIEVAL_OUTDATED`; all 6 dynamic CLI commands missing, no EvidenceBundle contract, no profiling step, vector-RAG-only framing
- Phase 1 SKILL.md: 8 edits applied; new Dynamic retrieval strategy section (routing table, all 6 CLI commands, EvidenceBundle contract, readiness label); Steps 4b/4c added to workflow; 2 new safety rules; 3 new agent behavior items; 4 readiness labels; 290→367 lines
- Evidence basis: mcp-project-context notes (checkpoint: slurp-20260525-phase1-skill-md-complete)

### 2026-05-24 — Full governance + archcore (bootstrap + promote)
- Created full skill package: SKILL.md, README.md, CHANGELOG.md, prompts, checklists, schemas, templates, examples, docs
- skill-ai-it bootstrap: AGENTS.md, CLAUDE.md, AI_NAVIGATION.md, context-map.yaml, SCRATCHPAD.md, repomix.config.json; archcore init + 3 ADRs, 2 rules, 2 specs, 2 guides
- skill-ai-it promote: 3 more specs + 2 more guides; all ARCHCORE_PROMOTION_CANDIDATES.md items promoted — no remaining candidates
- Evidence basis: CHANGELOG.md + mcp-project-context notes (slurp-20260524)

---

## Next actions <!-- KEEP: updated 20260531 -->

- Validate skill against a second real project (beyond vocus-profitability)
- Confirm rag-tools venv path still current: `tools-working-cache/rag-tools/.venv/`

---

## Memory pointers (navigation only — content is above)

- memory-keeper: worker mode — writes unavailable; read via search tool
- project-context: skills_stuff project (b8c5525e); channel skill-project-wiki-rag-bridge; checkpoint slurp-20260531-skill-pwrb-architecture-setup
- claude-mem observations: 5509–5536 (Phase 1–9), S1444–S1535 (session records); get_observations([IDs]) for details
