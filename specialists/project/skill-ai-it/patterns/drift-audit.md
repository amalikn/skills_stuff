# Drift Audit Pattern — AI Navigation/Control Layer

Use this pattern when auditing whether AI agents can find and use the correct project context.

This pattern validates the four capabilities: AI navigation map, file relationship/dependency logic, agent coherence/compliance checks, and structured machine-readable context.

---

## 1. Governance File Presence

- [ ] `README.md` exists
- [ ] `AGENTS.md` exists and has a managed navigation block
- [ ] `CLAUDE.md` exists and is a thin wrapper (`@AGENTS.md` only — no duplicate instructions)
- [ ] `AI_NAVIGATION.md` exists and has managed navigation block with version string
- [ ] `context-map.yaml` exists and has managed block with version string
- [ ] `CHANGELOG.md` exists and records recent governance/navigation changes

---

## 2. Managed Block Integrity

- [ ] No duplicate `<!-- BEGIN MANAGED: skill-ai-it:<section> -->` blocks for the same section in the same file
- [ ] No unmatched `<!-- BEGIN MANAGED -->` / `<!-- END MANAGED -->` markers
- [ ] All managed blocks use the new format: `<!-- BEGIN MANAGED: skill-ai-it:<section-name> -->`
- [ ] No stale `<!-- BEGIN skill-ai-it:navigation -->` (old format without `MANAGED:`) still present
- [ ] Managed block version strings match the current skill version

---

## 3. Version Consistency

- [ ] `AI_NAVIGATION.md` carries version string
- [ ] `context-map.yaml` carries version string
- [ ] `templates/AI_NAVIGATION.md` carries version string
- [ ] `templates/context-map.yaml` carries version string
- [ ] `templates/AGENTS-navigation-block.md` carries version string
- [ ] `AGENTS.md` managed block carries version string
- [ ] All version strings agree (mismatch = drift)

---

## 4. Navigation Map Completeness

- [ ] Read-first sequence is explicit
- [ ] Source-of-truth / authority hierarchy is explicit
- [ ] File relationship map (context file table) lists purpose and authority for each file
- [ ] Generated-output policy is documented (`graphify-out/`, `.ai-context/` are support only)
- [ ] Companion update rules exist for each change type
- [ ] Script/task navigation section exists with preferred execution order
- [ ] Context compaction recovery procedure exists
- [ ] Audit procedure exists with runnable checkpoints

---

## 5. Authority Consistency

- [ ] `.archcore/` is given highest authority when present
- [ ] `.archcore/` is treated as optional when absent
- [ ] AGENTS.md / CLAUDE.md is labeled as high authority
- [ ] AI_NAVIGATION.md is labeled as high authority
- [ ] context-map.yaml is labeled as high authority
- [ ] SCRATCHPAD.md is labeled as low/transient authority
- [ ] graphify-out/ and .ai-context/ are labeled as generated support only
- [ ] Authority order is consistent between AI_NAVIGATION.md, README.md, and context-map.yaml

---

## 6. Companion Update Verification

For each change type in `context-map.yaml update_rules`, verify all listed companion files were updated:

| Change type | Required companion updates | Verified? |
|---|---|---|
| `durable_decision` | .archcore/adr, ARCHITECTURE.md, memory-bank/decisionLog.md | — |
| `durable_rule` | .archcore/rules, AGENTS.md, AI_NAVIGATION.md | — |
| `design_contract` | .archcore/specs, ARCHITECTURE.md, docs | — |
| `operating_procedure` | .archcore/guides, README.md, docs | — |
| `plan_change` | .archcore/plans, ROADMAP.md, memory-bank/progress.md | — |
| `routing_change` | AI_NAVIGATION.md, context-map.yaml, AGENTS.md | — |
| `governance_history` | CHANGELOG.md | — |

- [ ] No change type has missing companion updates
- [ ] Companion update is reported, not silently skipped

---

## 7. Generated-Output Policy Enforcement

- [ ] Graphify output (`graphify-out/`) is labeled as generated support, NOT canonical truth
- [ ] Repomix output (`.ai-context/`) is labeled as generated support, NOT canonical truth
- [ ] No generated output is promoted into `.archcore/`, AGENTS.md, or other authoritative files without explicit authorization
- [ ] Regeneration commands are documented:
  - `graphify update .` for Graphify
  - `repomix --config repomix.config.json` for Repomix
- [ ] Generated outputs are excluded from AI_NAVIGATION.md authority-order source-of-truth layers

---

## 8. Archcore Promotion Gate Verification

- [ ] `.archcore/` init is allowed in bootstrap, navigation-add, refresh modes
- [ ] `.archcore/` content write is ONLY allowed in `promote` mode
- [ ] `ARCHCORE_PROMOTION_CANDIDATES.md` exists when `.archcore/` is present
- [ ] No `.archcore/adr/`, `.archcore/rules/`, `.archcore/specs/`, `.archcore/guides/`, or `.archcore/plans/` content files were created outside `promote` mode
- [ ] Sources explicitly excluded from promotion:
  - CHANGELOG.md
  - generated files (.ai-context/, graphify-out/)
  - unmarked SCRATCHPAD sections
  - draft/obsolete roadmap items
- [ ] Promotion extraction heuristics follow patterns/archcore-routing.md

---

## 9. Context Compaction Recovery

- [ ] Context recovery procedure exists in AI_NAVIGATION.md
- [ ] Procedure includes: read AI_NAVIGATION → load .archcore/ → regenerate graphify-out/ → regenerate .ai-context/ → verify SCRATCHPAD → verify CHANGELOG → verify companion consistency
- [ ] Recovery steps are idempotent (safe to run multiple times)
- [ ] Label convention exists: `Context recovered via skill-ai-it context-recovery procedure`

---

## 10. Script and Task Consistency

- [ ] `justfile` / `Justfile` tasks are documented or discoverable via `just --list`
- [ ] `scripts/README.md` exists when scripts/ directory has executable files
- [ ] `scripts/README.md` catalogs every important script with: purpose, inputs, outputs, safety label, idempotency
- [ ] No deleted scripts remain referenced in `scripts/README.md`
- [ ] No uncataloged scripts exist in `scripts/` (all represented in inventory)
- [ ] Safety labels are present: safe, review-required, destructive, unknown, etc.
- [ ] Agent routing in AI_NAVIGATION.md and context-map.yaml correctly routes script/task questions
- [ ] `unknown` safety scripts are not treated as safe

---

## 11. Stale Reference Detection

- [ ] No references to removed tools (e.g. `mise.toml`, `mise tasks`)
- [ ] No references to old task runners that no longer exist
- [ ] No references to old governance assumptions (e.g. treat generated output as truth)
- [ ] All file paths in AI_NAVIGATION.md context map table resolve to actual files
- [ ] All file paths in context-map.yaml resolve to actual files
- [ ] References to `.archcore/` are either accurate (if present) or correctly noted as optional (if absent)
- [ ] References to `memory-bank/` are either accurate (if present) or correctly noted as optional (if absent)

---

## 12. Repeat-Run Safety

- [ ] Re-running the skill does not create duplicate managed blocks
- [ ] Re-running the skill does not overwrite user-authored content
- [ ] Re-running the skill does not duplicate CHANGELOG entries for the same change
- [ ] Managed blocks are updated in place, not appended
- [ ] Scripts/README.md managed blocks are updated in place, not appended
- [ ] Existing `.proposed` files are recognized and not re-proposed unless stale

---

## 13. Cross-Reference: AI_NAVIGATION.md vs context-map.yaml

- [ ] All files listed in AI_NAVIGATION.md context map are also in context-map.yaml authority_order
- [ ] Authority levels agree between both files
- [ ] Routing categories in AI_NAVIGATION.md match routing sections in context-map.yaml
- [ ] Update rules in AI_NAVIGATION.md match update_rules in context-map.yaml
- [ ] Generated context entries listed in AI_NAVIGATION.md match generated_context_policy in context-map.yaml

---

## Output Format

Report drift findings in this structure:

```markdown
### Drift findings

| Check | Status | Details |
|---|---|---|
| <check name> | PASS | — |
| <check name> | FAIL | <specific violation> |
| <check name> | WARN | <non-blocking concern> |

### Recommended actions

- <specific file> — <exact fix>
- <specific file> — <exact fix>

### Severity

- **Blocker**: prevents safe governance/navigation operation
- **Non-blocker**: degrades quality but operationally safe
```
