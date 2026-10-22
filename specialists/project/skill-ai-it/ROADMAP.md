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

- [x] **`just check` fails on the plan tracker template** (fixed 2026-10-22 21:35: real date in the template; `--init` stamps today) (found 2026-10-22 21:24, before and after this slurp's edit): doc freshness reads
  `templates/plan-tracker.md` as a living document whose `Last reviewed: {today}` is no date (from 28dfe0b). Exempt templates with placeholders from
  freshness, or give the template a real date the init step rewrites.
- [x] **Rotation keeps decision-cited log entries** (answered 2026-10-22 21:30: the consumer reads the archives, as the rotation contract says; smc-resiliency's `check_decision_records` fixed and proved failing on an uncited stamp) (smc-resiliency, 2026-10-22 21:11) — `rotate_records.py` protects a stamp cited by a live file only
  in working-state files (`cited_stamps`, LIVE_SURFACES). Rotating smc-resiliency's CHANGELOG moved entry 20261022_1442, the only CHANGELOG citation of
  SCRATCHPAD decision 20261021_1723, and the project's `check_decision_records` failed; the rotation was undone by hand. Fix: also keep a log entry
  holding the only citation of a live `KEEP` decision stamp, or let decision checks read the archives; add a test.
- [ ] **Governance checker rollout** — adopt `scripts/check_governance.py` across existing projects via `refresh`. Each adoption is a Tier 3 authoring exercise, not a copy: the universal checks come from
  the template, but the invariants worth enforcing are project-specific and must be read out of that project's own stated rules.
- [ ] **Re-upgrade projects on the previous version stamp** — `me/llm-m2max`, `apn/vocus-profitability`, `apn/opticomm-profitability`.
- [ ] **Role check rollout** — `role_check.py` and the header adoption canaried on cambium-swap 2026-10-14 (check green, idempotent). The other
  governed projects adopt at their next slurp; the per-project commands are in CHANGELOG `20261014_1002`. Then shrink each baseline by fixing
  README quick starts, dated ROADMAP phases and README status sections.
- [ ] **Projects with AI_NAVIGATION.md but no version stamp** — skill-smc, skill-cambium, agent-stack, aws-to-local, equinix-cost-cutting,
  voip-analysis, smc-file-writing-analysis, career, of-si, islam, llm-m2max, japan/tracks/jdm, of-si/skill-workplace-strategy. Not by
  `nav_upgrade`: the 2026-10-14 canary on agent-stack re-serialised context-map.yaml (comments lost), refused AGENTS.md (pre-2026-09-23 block
  with project content) and failed `just check`; reverted. 11 of 13 have a hand-written AI_NAVIGATION.md the upgrader only proposes over.
  Each needs `/skill-ai-it refresh` by an agent, one project at a time, merging the proposed block by hand.
- [ ] **Upgrader keeps `context-map.yaml` comments** — the `update_rules` merge in `upgrade_navigation_control_layer.py` re-dumps the whole file, losing
  comments and quoting, including the purpose header the header standard requires (agent-stack canary and smc-resiliency refresh, 2026-10-14;
  hand recovery in [references/pitfalls.md](references/pitfalls.md)). Fix: merge with a round-trip loader (ruamel.yaml) or insert the new keys as
  text, and fall back to a `.proposed` file rather than rewriting the live one. Done when a test upgrades a commented `context-map.yaml` and every
  comment survives. Unblocks the unstamped-projects item above.

## Archcore

- [ ] **`promote` mode implementation** — flesh out the promote mode workflow: read `ARCHCORE_PROMOTION_CANDIDATES.md`, resolve each candidate, write `.archcore/` files with provenance headers and
  `status: proposed`.
- [ ] **`ARCHCORE_PROMOTION_CANDIDATES.md` template** — add a template file under `templates/` so the format is governed and consistent across projects.

## Target map

- [ ] **plan_timeline.py over the module budget** (2026-10-22): 420 lines before `link_ids`, 486 after (skill-coder budget 400). Split it the way
  `target_map.py` is planned: schema and validation, schedule, renderer, `link_ids` (or move the heading lookup into `anchor_links.py`), command line.
  Gate: the existing 202 tests and a byte-identical render in unified-network-controller and smc-resiliency.
- [ ] **Adopt `anchor_links.py` in smc-resiliency** (2026-10-22): its session has an uncommitted govcheck copy of the same rule; told directly and
  through the hub (es inbox 20261022_1745). Done when its `just check` calls the skill copy.
- [ ] **Target map standard: bootstrap and governance standard left (module promoted 2026-10-21).** Done 2026-10-21: `scripts/target_map.py` and
  `scripts/plan_timeline.py` live here with their tests and [reference](references/target-map-and-timeline.md); unified-network-controller runs them
  (renders byte-identical) and smc-resiliency adopted both. Left: `bootstrap` offers a starter map (`--init`), the checker template gains
  `check_target_map`/`check_plan_timeline`, a governance standard whose field table is the `--schema` output, and `target_map.py` (1,702
  lines, over skill-coder's module budget) split into a package: schema, readers, validator, renderer, starter, command line. History of the pilot: A project-root `target-map.yaml`, beside `context-map.yaml`, is the source of truth for
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

- [ ] **`upgrade_navigation_control_layer.py` writes without `--apply`** (found 2026-10-21, unified-network-controller): it writes unless
  `--dry-run` is given, against the write-gate rule (skill-coder `safety-and-writes`), and `budget_plan.py` tells the user to run it bare when AGENTS.md
  is over budget. It failed early there only because PyYAML was missing. Give it `--apply` (plan by default) and print the plan command in the budget hint.
- [ ] **Budget audit reported a line LOST that was not** (2026-10-21, unified-network-controller, `just budget --apply`): "SCRATCHPAD.md: 2 line(s)
  lost" for a line held only in an unchanged `docs/trackers/open-items-*.md` (not in HEAD's SCRATCHPAD, not in any rotation); a plan re-run showed
  no loss. Find which snapshot the audit compares with (likely one taken before an earlier move of open items) and make it compare with HEAD.
- [ ] **Rotation audit reports lines rewrapped by the markdown hook as LOST** (2026-10-22, smc-resiliency): editing SCRATCHPAD after a rotation lets the
  wrap hook reflow untouched entries to 200 columns, and `audit_rotations.py` compares line by line, so 16 unchanged lines read as lost. A change that
  excused any lost line whose words appear in order anywhere in the record, archives or trackers was written and **reverted** (operator, 2026-10-22
  14:39: keep the audit strict; such text could pass when the same words appear elsewhere). Until a reviewed design is approved (for example, match
  only inside the same dated entry), baseline rewrapped lines by hand with a reason, after checking their text whitespace-normalised.
- [ ] **check_code_map covers shell and every code folder** (found 2026-10-20, smc-resiliency): the template globs `*.py` under
  `MODULE_ROOTS` only, so `.sh` scripts escape the map; smc-resiliency's split checker covers `.sh` and `spike/`. Take the roots from `code-map.toml`
  `roots` and include shell.
- [ ] **`budget_plan.py` audit reports SCRATCHPAD lines LOST when none were removed** (2026-10-15, ansible-wifi-root-governance): `just budget --apply` printed "LOST SCRATCHPAD.md: 85 line(s) lost, e.g. '**Newest thread (2026-10-07, 13:36) ...'" and exited 1, yet `git diff` on SCRATCHPAD.md shows additions only and the quoted line is still in the file. The CHANGELOG rotation in the same run was correct. Reproduce on that project and fix the audit comparison. Reproduced again 2026-10-22 12:26 on the same project: same 85 lines, same quoted line, SCRATCHPAD left intact at 160 lines (additions only), CHANGELOG rotation correct (211 to 195).
- [ ] **`audit_rotations.py` reports a line another tool replaced inside its own block as LOST** (2026-10-21, enterprise-strategy): `just budget --apply` exited 1 with "LOST SCRATCHPAD.md: 1 line(s) lost, e.g. '<!-- Outbox: add `- [ ] to unc, smc: text`...'": apn `scripts/project_sync.py` had replaced its outbox help comment on purpose (hub-and-spoke wording), and the audit compares against HEAD. The rotation itself was correct. Skip lines inside `<!-- project-sync:*:start/end -->` blocks in the audit, as `rotate_records.py` already does (`SYNC_MARK`).

- [ ] **`audit` mode refinement** — structured output format for audit findings (missing files, stale sections, routing gaps, drift) so agents can act on audit output without ambiguity.
- [ ] **Context-preflight validation** — extend `templates/context_preflight.sh` to check for `ARCHCORE_PROMOTION_CANDIDATES.md` freshness and warn if candidates are stale relative to governance files.
- [ ] **Candidate freshness tracking** — add a `generated_on` timestamp and source file checksums to `ARCHCORE_PROMOTION_CANDIDATES.md` so refresh mode can diff rather than rescan from scratch.

## Ideas

- [x] **Plan tracker timeline as data** (2026-10-21, candidate in unified-network-controller `code-map.toml`; promoted 2026-10-21 as `scripts/plan_timeline.py`): `scripts/render/plan_timeline.py`
  renders a plan tracker's Timeline from YAML with the schedule worked out from the dates (late, due today, done), plus its govcheck and
  `commit-gate`. Promote here once a second project (smc-resiliency) keeps its timeline as data.
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
