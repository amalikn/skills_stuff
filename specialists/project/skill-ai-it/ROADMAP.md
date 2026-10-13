---
Title: Roadmap
Category: roadmap
Status: current
Authority: canonical
Scope: Current phase and open milestones of skill-ai-it
Summary: Current phase and open milestones; done items move to docs/history (just rotate).
Kind: roadmap
Budget: 200 lines, 25 KB
Archive: docs/history/ (roadmap-*.md, `just rotate`)
Last reviewed: 2026-10-14
---

# Roadmap — skill-ai-it

## Current phase

**2026-10-14.** The package governs itself (`just check`, budgets, rotation, freshness, file roles) and every root file has a defined role and
loading tier ([references/governed-file-roles.md](references/governed-file-roles.md)) that `just roles` and the audit check. Open work is fleet adoption of the checker
and records tooling, the `promote` mode, and the target-map promotion decision.

## Fleet adoption

- [ ] **Governance checker rollout** — adopt `scripts/check_governance.py` across existing projects via `refresh`. Each adoption is a Tier 3 authoring exercise, not a copy: the universal checks come from
  the template, but the invariants worth enforcing are project-specific and must be read out of that project's own stated rules.
- [ ] **Re-upgrade projects on the previous version stamp** — `me/llm-m2max`, `apn/vocus-profitability`, `apn/opticomm-profitability`.
- [x] **README budget across projects** (2026-10-14): `adopt_governed_files.py` adds `Budget: 200 lines, 25 KB` to every README it heads and
  grandfathers an over-budget one in the freshness baseline; README.md stays off the default list so no project fails at once.
- [ ] **Role check rollout** — `role_check.py` and the header adoption canaried on cambium-swap 2026-10-14 (check green, idempotent). The other
  governed projects adopt at their next slurp; the per-project commands are in CHANGELOG `20261014_1002`. Then shrink each baseline by fixing
  README quick starts, dated ROADMAP phases and README status sections.
- [ ] **Projects with AI_NAVIGATION.md but no version stamp** — skill-smc, skill-cambium, agent-stack, aws-to-local, equinix-cost-cutting,
  voip-analysis, smc-file-writing-analysis, career, of-si, islam, llm-m2max, japan/tracks/jdm, of-si/skill-workplace-strategy. Not by
  `nav_upgrade`: the 2026-10-14 canary on agent-stack re-serialised context-map.yaml (comments lost), refused AGENTS.md (pre-2026-09-23 block
  with project content) and failed `just check`; reverted. 11 of 13 have a hand-written AI_NAVIGATION.md the upgrader only proposes over.
  Each needs `/skill-ai-it refresh` by an agent, one project at a time, merging the proposed block by hand.

## Archcore

- [ ] **`promote` mode implementation** — flesh out the promote mode workflow: read `ARCHCORE_PROMOTION_CANDIDATES.md`, resolve each candidate, write `.archcore/` files with provenance headers and
  `status: proposed`.
- [ ] **`ARCHCORE_PROMOTION_CANDIDATES.md` template** — add a template file under `templates/` so the format is governed and consistent across projects.

## Target map

- [ ] **Target map standard — promote after the pilot (pilot started 2026-09-27 in `unified-network-controller`).** A project-root `target-map.yaml`, beside `context-map.yaml`, is the source of truth for
  a project's goals, targets and per-criterion status, and its tracker markdown is generated from it. The context map says where things are; the target map says where the project is going and how far
  it has got. Pilot files: [target-map.yaml](/Volumes/Data/_ai/_project/project_stuff/apn/unified-network-controller/target-map.yaml),
  [scripts/render/target_map.py](/Volumes/Data/_ai/_project/project_stuff/apn/unified-network-controller/scripts/render/target_map.py) (generic validator and renderer; `--schema` prints every field's level,
  mandatory, recommended, optional or rejected, with its reason), `check_target_map` in
  [scripts/check_governance.py](/Volumes/Data/_ai/_project/project_stuff/apn/unified-network-controller/scripts/check_governance.py), the pre-commit hook
  [scripts/githooks/pre-commit](/Volumes/Data/_ai/_project/project_stuff/apn/unified-network-controller/scripts/githooks/pre-commit) with the `install-hooks` recipe, and
  [tests/test_target_map.py](/Volumes/Data/_ai/_project/project_stuff/apn/unified-network-controller/tests/test_target_map.py). Staleness guards: a change-log entry naming a target after its
  `reviewed` moment fails, as does a map or `pending` criterion unverified for seven days. **Gate:** promote no earlier than 2026-10-04 and only if the pilot has caught real drift without false
  alarms. **Promotion:** copy the module, the check and the hook into `templates/`, make `bootstrap` offer a starter map (inline mode when a project has no plan document), teach `refresh` and the
  upgrader to carry them, and write a governance standard whose field table is the `--schema` output (check the governance sync map). Open question from the pilot: whether a source should be allowed
  to be only partly tracked (today every heading a source defines needs a target). **Gaps to close before promotion** (found 2026-09-27, asking how the skill would generate a map). **All three built
  in the pilot 2026-09-27 20:05** (unified-network-controller CHANGELOG `20260927_2005`): `--init`, `--sync`, and a generic starter header (`STARTER_HEADER` in `scripts/render/target_map.py`), plus a rule
  that fails the check on any value still starting with `TODO`. Promotion copies them; the gate date is unchanged:
  - **`--init`:** `target_map.py` only validates, renders (`--write`) and prints the schema; nothing creates a map. Add `--init` printing a starter map: source mode, one target per plan heading
    (`state: not started`, `exit_met: false`, one `status: not run` criterion per numbered acceptance test, text left in the plan), reusing the renderer's plan reader; inline mode, one goal and one
    target with placeholder name, exit condition and criteria text that fail the check until filled. `bootstrap` calls it; it never assigns a status above `not run`.
  - **`--sync`:** when a plan gains a heading, the check fails until a target is added by hand. Add `--sync` appending missing targets as `not started`, never changing existing ones; settle it
    together with the open question on partly tracked sources.
  - **Generic header template:** the pilot's `target-map.yaml` header and section comments (2026-09-27) explain the fields but carry UNC wording (P0, the plan's §1.6, `[vSMC]`, `[plan≠]`). Ship a
    generic version under `templates/` for `--init` to emit; the UNC wording stays in the pilot.

## Audit and preflight

- [ ] **`audit` mode refinement** — structured output format for audit findings (missing files, stale sections, routing gaps, drift) so agents can act on audit output without ambiguity.
- [ ] **Context-preflight validation** — extend `templates/context_preflight.sh` to check for `ARCHCORE_PROMOTION_CANDIDATES.md` freshness and warn if candidates are stale relative to governance files.
- [ ] **Candidate freshness tracking** — add a `generated_on` timestamp and source file checksums to `ARCHCORE_PROMOTION_CANDIDATES.md` so refresh mode can diff rather than rescan from scratch.

## Ideas

- [ ] **ADR template** — a starter `.archcore/adr/` template for common decision types (tool choice, data model, boundary design).
- [ ] **Rules template** — a starter `.archcore/rules/` template structured around source-of-truth, update policy, and authorization gates.
- [ ] **Multi-agent handoff pack** — a `repomix`-compatible config that bundles only the durable-truth layer (`.archcore/` + governance docs) for context-efficient agent handoffs.
- [ ] **Cross-project candidate deduplication** — when multiple related projects share a parent `AGENTS.md`, surface only project-specific candidates (not inherited global rules) in each project's report.

## Completed

Done items move to `docs/history/roadmap-*.md` (`just rotate`; find one with `just history <term>`).


## Out of scope

- `skill-ai-it` generates governance scaffolding. It does not store project-specific content.
- `skill-ai-it` does not manage secrets, credentials, or machine-local paths.
- Runtime caches (`graphify-out/`, `.ai-context/`) are not maintained here — they are regenerated per project.
