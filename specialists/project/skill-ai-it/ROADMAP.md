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

- **Target map standard — promote after the pilot (pilot started 2026-09-27 in `unified-network-controller`).** A project-root `target-map.yaml`, beside `context-map.yaml`, is the source of truth for
  a project's goals, targets and per-criterion status, and its tracker markdown is generated from it. The context map says where things are; the target map says where the project is going and how far
  it has got. Pilot files: [target-map.yaml](/Volumes/Data/_ai/_project/project_stuff/apn/unified-network-controller/target-map.yaml),
  [scripts/target_map.py](/Volumes/Data/_ai/_project/project_stuff/apn/unified-network-controller/scripts/target_map.py) (generic validator and renderer; `--schema` prints every field's level,
  mandatory, recommended, optional or rejected, with its reason), `check_target_map` in
  [scripts/check_governance.py](/Volumes/Data/_ai/_project/project_stuff/apn/unified-network-controller/scripts/check_governance.py), the pre-commit hook
  [scripts/githooks/pre-commit](/Volumes/Data/_ai/_project/project_stuff/apn/unified-network-controller/scripts/githooks/pre-commit) with the `install-hooks` recipe, and
  [tests/test_target_map.py](/Volumes/Data/_ai/_project/project_stuff/apn/unified-network-controller/tests/test_target_map.py). Staleness guards: a change-log entry naming a target after its
  `reviewed` moment fails, as does a map or `pending` criterion unverified for seven days. **Gate:** promote no earlier than 2026-10-04 and only if the pilot has caught real drift without false
  alarms. **Promotion:** copy the module, the check and the hook into `templates/`, make `bootstrap` offer a starter map (inline mode when a project has no plan document), teach `refresh` and the
  upgrader to carry them, and write a governance standard whose field table is the `--schema` output (check the governance sync map). Open question from the pilot: whether a source should be allowed
  to be only partly tracked (today every heading a source defines needs a target).
  **Gaps to close before promotion** (found 2026-09-27, asking how the skill would generate a map):
  - **`--init`:** `target_map.py` only validates, renders (`--write`) and prints the schema; nothing creates a map. Add `--init` printing a starter map: source mode, one target per plan heading
    (`state: not started`, `exit_met: false`, one `status: not run` criterion per numbered acceptance test, text left in the plan), reusing the renderer's plan reader; inline mode, one goal and one
    target with placeholder name, exit condition and criteria text that fail the check until filled. `bootstrap` calls it; it never assigns a status above `not run`.
  - **`--sync`:** when a plan gains a heading, the check fails until a target is added by hand. Add `--sync` appending missing targets as `not started`, never changing existing ones; settle it
    together with the open question on partly tracked sources.
  - **Generic header template:** the pilot's `target-map.yaml` header and section comments (2026-09-27) explain the fields but carry UNC wording (P0, the plan's §1.6, `[vSMC]`, `[plan≠]`). Ship a
    generic version under `templates/` for `--init` to emit; the UNC wording stays in the pilot.

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
