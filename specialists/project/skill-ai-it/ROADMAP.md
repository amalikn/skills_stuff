# Roadmap — skill-ai-it

Status: active development. See `CHANGELOG.md` for completed work; see `SCRATCHPAD.md` for open items.

---

## Completed phases

### Phase 1 — Initial navigation module (2026-05-22)

Bootstrapped the core skill package: `AI_NAVIGATION.md`, `context-map.yaml`, operating modes, repeat-safety contract, CHANGELOG governance integration.

### Phase 2 — Tool-stack integration (2026-05-22)

Added active CLI invocation for Graphify and Repomix; Archcore initialization when CLI available; preflight template; script/task inventory (`scripts/README.md`); `just`-preferred task runner
strategy.

### Phase 3 — Coherence and governance hardening (2026-05-22)

Full coherence sweep across all templates, patterns, and governance files; markdown quality rules enforcement in Phase 4 workflow; mise excision; `ARCHITECTURE.md` added; local preflight opt-in
policy.

### Phase 4 — Archcore promotion candidate reporting (2026-05-23)

Report-first approach for Archcore: `bootstrap` and `refresh` emit `ARCHCORE_PROMOTION_CANDIDATES.md` after `archcore init`. Extraction heuristics added to `patterns/archcore-routing.md`. Only
`promote` mode writes `.archcore/` content. See `CHANGELOG.md` entry `20260523_0000`.

---

## Planned work

### Near-term

- ~~**Sync installed copy**~~ — **obsolete as of 2026-08-11.** Both `~/.claude/skills/skill-ai-it` and `~/.agents/skills/skill-ai-it` are now symlinks to canonical, so there is nothing to sync and
  nothing that can drift. Retained here only to explain why the step disappeared. Former text: copy updated `SKILL.md` (and other changed files) to `~/.claude/skills/skill-ai-it/` after each
  meaningful package change. Operational step; not part of canonical package authoring. **The durable fix is to symlink the install back to canonical** — `~/.agents/skills/skill-ai-it` already is one;
  `~/.claude/skills/skill-ai-it` is still a copy and has silently fallen behind twice.
- **Governance checker rollout** — adopt `scripts/check_governance.py` across existing projects via `refresh`. Each adoption is a Tier 3 authoring exercise, not a copy: the universal checks come from
  the template, but the invariants worth enforcing are project-specific and must be read out of that project's own stated rules.
- **Re-upgrade projects on the previous version stamp** — `me/llm-m2max`, `apn/vocus-profitability`, `apn/opticomm-profitability`.
- **`promote` mode implementation** — flesh out the promote mode workflow: read `ARCHCORE_PROMOTION_CANDIDATES.md`, resolve each candidate, write `.archcore/` files with provenance headers and
  `status: proposed`.
- **`ARCHCORE_PROMOTION_CANDIDATES.md` template** — add a template file under `templates/` so the format is governed and consistent across projects.

### Medium-term

- **`audit` mode refinement** — structured output format for audit findings (missing files, stale sections, routing gaps, drift) so agents can act on audit output without ambiguity.
- **Context-preflight validation** — extend `templates/context-preflight.sh` to check for `ARCHCORE_PROMOTION_CANDIDATES.md` freshness and warn if candidates are stale relative to governance files.
- **Candidate freshness tracking** — add a `generated_on` timestamp and source file checksums to `ARCHCORE_PROMOTION_CANDIDATES.md` so refresh mode can diff rather than rescan from scratch.

### Longer-term / ideas

- **ADR template** — a starter `.archcore/adr/` template for common decision types (tool choice, data model, boundary design).
- **Rules template** — a starter `.archcore/rules/` template structured around source-of-truth, update policy, and authorization gates.
- **Multi-agent handoff pack** — a `repomix`-compatible config that bundles only the durable-truth layer (`.archcore/` + governance docs) for context-efficient agent handoffs.
- **Cross-project candidate deduplication** — when multiple related projects share a parent `AGENTS.md`, surface only project-specific candidates (not inherited global rules) in each project's report.

---

## Out of scope

- `skill-ai-it` generates governance scaffolding. It does not store project-specific content.
- `skill-ai-it` does not manage secrets, credentials, or machine-local paths.
- Runtime caches (`graphify-out/`, `.ai-context/`) are not maintained here — they are regenerated per project.
