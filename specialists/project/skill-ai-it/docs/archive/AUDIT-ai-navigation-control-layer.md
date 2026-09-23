# Audit: AI Navigation/Control Layer Support in skill-ai-it

**AUDIT DATE:** 2026-05-29
**PACKAGE:** `skill-ai-it`
**CANONICAL PATH:** `/Volumes/Data/_ai/_skills/skills_stuff/specialists/project/skill-ai-it/`
**INSTALLED PATH:** `~/.hermes/skills/software-development/skill-ai-it/SKILL.md`

---

## 1. Executive Summary

### Overall Verdict: **PARTIAL**

The skill has a **strong foundation** but is **not ready to upgrade** without first addressing several gaps across all four capabilities.

### Capability coverage

| Capability | Status |
|---|---|
| AI navigation map | **Mostly present** — AI_NAVIGATION.md generated for target projects; context mapping table present; read order defined; source-of-truth hierarchy defined. Missing: explicit context-recovery procedure after compaction. |
| File relationship / dependency logic | **Present in key files** — well-documented in README, SKILL, ARCHITECTURE, AI_NAVIGATION, and context-map.yaml. Missing: NOT explicitly documented in AGENTS.md or CLAUDE.md as relationship logic (only as read-order instructions to agents). |
| Agent coherence / compliance checks | **Weak** — drift-audit.md has only 11 shallow checkpoints; does not check companion-file updates, stale references, generated-artifact staleness, or .archcore/ promotion consistency. Much of the compliance burden is in SKILL.md Quality Check Checklist (22 items) but that's SKILL.md orchestration, not a reusable audit pattern. |
| Structured machine-readable context | **Strong** — context-map.yaml and its template both support files, authority, classification, read_order, update_triggers, companion_files, generated_artifacts, task_runners, drift_policy. **Missing explicit schema fields:** audit_checks, promotion_rules, context_recovery. |

### Highest-risk gaps

1. **drift-audit.md is too shallow** — 11 checkpoints cover basic file presence but not companion-update consistency, stale references, or promotion-gate verification.
2. **No context-recovery procedure** — nowhere does the skill tell an agent exactly what to do after a context compaction. The generated context section says "regenerate these" but doesn't give a step-by-step recovery procedure.
3. **context-map.yaml schema lacks explicit audit_checks, promotion_rules, and context_recovery fields** — these are implicit or handled elsewhere, which makes machine-driven validation harder.
4. **templates/context-preflight.sh has a numbering bug** — shows `[5/5]` for step 6 (should be `[5/6]`).
5. **No explicit companion-file update check in drift-audit** — the drift pattern doesn't verify that companion files listed in context-map.yaml `update_rules` were actually updated when their source changed.

---

## 2. Capability Matrix

| Capability | Current support | Files involved | Gaps | Upgrade required |
|---|---|---|---|---|
| **AI navigation map** | Strong — generates AI_NAVIGATION.md with read order, authority hierarchy, context file map, task routing, and generated-context policy | SKILL.md (Phase 4 embedded fallback), templates/AI_NAVIGATION.md, templates/context-map.yaml, AI_NAVIGATION.md (package-level) | No explicit context-compaction recovery procedure; no "how to rebuild agent context from scratch" guide | P1 |
| **File relationship / dependency logic** | Strong — documented in README, SKILL, ARCHITECTURE, AI_NAVIGATION, context-map.yaml, templates/context-map.yaml | README.md (Key rules §58-73), SKILL.md (Phase 4), ARCHITECTURE.md (§Package roles, §Flow), AI_NAVIGATION.md (Context map, Update rules), context-map.yaml (update_rules), templates/context-map.yaml (update_rules) | NOT explicitly documented in AGENTS.md (only as preflight instructions, not as relationship logic); CLAUDE.md is a thin wrapper with no relationship documentation | P2 |
| **Agent coherence / compliance checks** | Weak — SKILL.md has a detailed Quality Check Checklist (22 items) but the reusable patterns/ drift-audit.md is too shallow | SKILL.md (§Quality Check Before Completing, 22 items), patterns/drift-audit.md (11 checkpoints), patterns/script-task-audit-checklist.md (110 lines, thorough) | drift-audit.md missing: companion-update verification, stale-reference detection, generated-artifact staleness, .archcore/ promotion consistency, task-runner consistency, old-tool-reference detection. Many checks exist in SKILL.md QCC but not in the reusable pattern. | P0 |
| **Structured machine-readable context** | Strong — context-map.yaml (both package and template) has rich schema with authority_order, routing, update_rules, drift_policy, generated_context_policy, answer_contract | context-map.yaml (188 lines, 7 sections), templates/context-map.yaml (303 lines, 10 sections) | Missing explicit schema fields: audit_checks (what to validate), promotion_rules (how .archcore/ content flows in), context_recovery (post-compaction rebuild). These are implicit in SKILL.md orchestration only. | P1 |

---

## 3. File-by-File Audit

| File | Expected role | Current role | Missing / weak areas | Required upgrade |
|---|---|---|---|---|
| **README.md** | Package overview, authority model, tool stack, usage intent | ✓ Package layout ✓ Key rules ✓ Tool stack ✓ Authority order ✓ Usage intent | Authority model (§103-111) describes data-flow order, not conflict-resolution order — this is coherent but could be clearer. No mention of context-recovery. No explicit companion-file dependency description. | P2 — add context-recovery pointer |
| **SKILL.md** | Orchestration contract — modes, phases, repeat-safety, embedded fallbacks | ✓ 5 operating modes ✓ Repeat-safety contract ✓ 5-phase workflow ✓ Embedded fallback templates ✓ Quality check checklist (22 items) ✓ Audit output format | Very long (1532 lines) — the embedded fallbacks are extensive but make the file hard to navigate. The QCC checklist is strong but is orchestration-specific, not reusable. No explicit context-recovery phrase. Missing: explicit "companion file must be updated" enforcement in Phase 4. | P1 — extract embedded fallback templates; add context-recovery step; tighten QCC to include companion-update check |
| **AGENTS.md** | Agent maintenance rules + navigation block | ✓ Working rules (13 items) ✓ Navigation block (managed) ✓ Maintenance boundaries | The navigation block instructs agents to read AI_NAVIGATION.md and context-map.yaml first, which is correct. But it doesn't document file-relationship / dependency logic — those are elsewhere. No companion-update obligation listed (only in SKILL.md QCC). | P2 — add note about companion-file update obligation |
| **CLAUDE.md** | Thin wrapper around AGENTS.md | ✓ `@AGENTS.md` ✓ "No additions" | Correct as-is. No file-relationship docs needed — that's AGENTS.md's role. | No change needed |
| **AI_NAVIGATION.md** (package) | Package-level context router for agents editing this skill | ✓ Mandatory read order ✓ Source priority ✓ Context map table ✓ Task routing ✓ Script/task navigation ✓ Drift handling ✓ Update rules ✓ Generated context | ✓ Very strong — best-documented file in the package. Context map table lists 20+ files with role and authority. Update rules table is comprehensive. Generated context section present. | P2 — add explicit context-compaction recovery bullet |
| **context-map.yaml** (package) | Machine-readable routing map for this skill package | ✓ authority_order ✓ routing (7 categories) ✓ update_rules (9 types) ✓ drift_policy ✓ answer_contract | Strong schema. But: no audit_checks key, no promotion_rules key, no context_recovery key. bootstrap.required_first_read only lists 5 files (not all companion files). Scripts routing has duplicated `templates/justfile` entries. | P1 — add audit_checks, promotion_rules, context_recovery schema fields; fix justfile duplicate |
| **ARCHITECTURE.md** | Detailed architecture explanation | ✓ Package roles ✓ Flow diagram ✓ Tool stack (Archcore, Graphify, Repomix, just) ✓ Script/task inventory ✓ Runtime model ✓ Repeat-safety model | ✓ Strong. Flow diagram is clear. Source-of-truth direction diagram matches README authority order. No gaps identified. | No change needed |
| **SCRATCHPAD.md** | Ephemeral working notes and open items | ✓ Current state ✓ Open items ✓ Key anchors ✓ Recent decisions ✓ Session history ✓ Next actions ✓ Memory pointers | ✓ Correctly structured. Outdated session history (last entry May 22) but that's content, not structure. | No structural change needed |
| **CHANGELOG.md** | Durable package/governance history ledger | ✓ Chronological entries ✓ Descriptive entries ✓ Comprehensive coverage (30+ entries) | ✓ Strong. Entries are well-structured with "why" notes. | No change needed |
| **ROADMAP.md** | Planned work view | ✓ Completed phases ✓ Near/medium/long-term plans ✓ Out-of-scope | ✓ Reasonable. Lists promote mode as still to be implemented, which is honest. | No change needed |
| **templates/AI_NAVIGATION.md** | Target-project AI navigation template | ✓ Mandatory read order ✓ Source priority (11-level) ✓ Project context files table ✓ Task routing (6 categories) ✓ Script/task navigation ✓ Documentation updates ✓ Drift handling ✓ Update rules ✓ Generated context ✓ Agent answer contract | ✓ Very strong (201 lines). Comprehensive coverage. One minor note: Script and Task Navigation lists "Existing canonical task runner if documented" before "justfile" in the read order, which differs from the embedded fallback in SKILL.md (line 859) where justfile is listed first. | P2 — align read-order with SKILL.md embedded fallback |
| **templates/context-map.yaml** | Target-project machine-readable routing map template | ✓ authority_order (17 entries) ✓ context_sources (archcore, memory_bank, generated) ✓ routing (8 categories) ✓ update_rules (9 types) ✓ drift_policy ✓ generated_context_policy ✓ answer_contract | ✓ Very strong (303 lines). Has ARCHCORE_PROMOTION_CANDIDATES.md in authority_order. Missing: audit_checks, promotion_rules, context_recovery. | P1 — add audit_checks, promotion_rules, context_recovery schema fields |
| **templates/repomix.config.json** | Target-project Repomix config | ✓ Include list (20+ entries) ✓ Ignore list (10 entries) ✓ Output path | ✓ Strong. Includes ARCHCORE_PROMOTION_CANDIDATES.md, justfile, Justfile. Ignores generated/heavy paths. No gap. | No change needed |
| **templates/AGENTS-navigation-block.md** | Managed AGENTS.md navigation block for target projects | ✓ 12 rules covering read order, SCRATCHPAD policy, script safety, companion updates | ✓ Strong. Rule 12 covers scripts/README.md update obligation. | No change needed |
| **templates/justfile** | Lightweight task catalog template | ✓ 4 tasks (inventory, audit-scripts, preflight, lint-md) ✓ Safety notes ✓ Comments | ✓ Fit for purpose as starter template. | No change needed |
| **templates/scripts-README.md** | Script/task inventory template | ✓ Execution policy ✓ Preferred execution order ✓ Task inventory table ✓ Raw script inventory table ✓ Safety labels ✓ Maintenance rules | ✓ Strong — includes managed block markers. | No change needed |
| **templates/context-preflight.sh** | Optional repo-local preflight script | ✓ 6 steps: governance check, Archcore, Graphify, Repomix | **BUG:** Line 46 shows `[5/5]` but should be `[5/6]` (6 steps defined, step 4 shows [4/6], step 5 [5/6] is missing). | P0 — fix `[5/5]` → `[5/6]` |
| **patterns/archcore-routing.md** | Archcore integration guidance | ✓ Core principle ✓ Source mapping ✓ Extraction heuristics (5 categories) ✓ Exclusion table ✓ Candidate report format ✓ Completion gate ✓ Rules (10 items) | ✓ Strong. Extraction heuristics are well-defined. Completion gate covers candidate report verification and promotion-safety. | No change needed |
| **patterns/memory-bank-structure.md** | Memory Bank guidance | ✓ 5-file structure ✓ Rules (4 items) | ✓ Simple and correct. | No change needed |
| **patterns/drift-audit.md** | Drift / coherence audit pattern | 11 checkpoints covering: AGENTS→AI_NAVIGATION pointer, context-map.yaml routing, CHANGELOG presence, .archcore/ routing, memory-bank routing, generated context exclusion, SCRATCHPAD transient marking, managed blocks, .proposed files, drift policy | **Too shallow.** Cannot detect: companion-update verification, stale-file references, generated-artifact staleness, .archcore/ promotion consistency, task-runner consistency, old-tool-reference drift. Also doesn't cross-reference with script-task-audit-checklist.md. | P0 — rewrite with proper depth |
| **patterns/script-task-audit-checklist.md** | Script/task inventory audit | ✓ 8 sections: Discovery, Catalog Coverage, Safety Classification, Inputs/Outputs, Idempotency, Agent Routing, Validation Commands, Audit Verdict | ✓ Strong (110 lines). Thorough checklist. Validation commands are executable. | No change needed |
| **.gitignore** | — | ✓ Present with .DS_Store, .remember/logs/, graphify-out/, .ai-context/ | — | No change needed |

---

## 4. Authority Model Audit

### Current authority order (from README §103-111)

```
.archcore/ + governed markdown + source files
        -> justfile / existing task runner + scripts/README.md
        -> AI_NAVIGATION.md + context-map.yaml
        -> Graphify / Repomix generated outputs
        -> agent context loading
```

### Conflict-resolution priority order (from templates/AI_NAVIGATION.md §30-41)

```
1. .archcore/ accepted ADRs, rules, specs, guides, plans
2. AGENTS.md / CLAUDE.md
3. AI_NAVIGATION.md
4. context-map.yaml
5. CHANGELOG.md
6. ARCHITECTURE.md
7. ROADMAP.md
8. memory-bank/activeContext.md
9. memory-bank/progress.md
10. SCRATCHPAD.md
11. old notes, drafts, archived files
```

### Consistency check

| Source | Model described | Consistent with target? |
|---|---|---|
| **README.md** | Data-flow authority order (5 layers) | ✓ Self-consistent |
| **SKILL.md** | Embedded fallback in Phase 4 matches template | ✓ Matches template/AI_NAVIGATION.md exactly |
| **ARCHITECTURE.md** | Both flow diagram and source-truth diagram | ✓ Matches README data-flow model |
| **templates/AI_NAVIGATION.md** | 11-level conflict-resolution priority | ✓ Matches SKILL.md embedded fallback |
| **templates/context-map.yaml** | authority_order with 17 entries | ✓ Covers all files from the 11-level priority |
| **templates/AGENTS-navigation-block.md** | References AI_NAVIGATION.md as first read | ✓ Implicitly defers to AI_NAVIGATION priority |

**Verdict:** The authority model is consistently described across all files. There are two distinct models (data-flow order in README/ARCHITECTURE, conflict-resolution order in AI_NAVIGATION) but they are complementary rather than contradictory. **No upgrade needed for authority model consistency.**

---

## 5. Context-map Schema Audit

### Package-level `context-map.yaml`

| Schema field | Present? | Details |
|---|---|---|
| `files` | ✓ | Via `authority_order` (11 entries covering all governance files) |
| `authority` | ✓ | 5 levels: highest, high, medium_high, medium, low |
| `classification` | ✓ | Via `type` field in authority_order (skill_contract, package_history, etc.) |
| `read_order` | ✓ | Via `bootstrap.required_first_read` (5 files) |
| `update_triggers` | ✓ | Via `update_rules` (7 triggers: new_mode, new_template, new_pattern, repeat_safety_change, navigation_change, governance_history) |
| `companion_files` | ✓ | Via `update_rules` sections that list multiple files to update together |
| `dependencies` | Partial | Implicit via `routing` sections (file groups read together). Not explicit dependency relationships. |
| `generated_artifacts` | ✓ | Via `generated_output` key under `routing.guidance_patterns` |
| `task_runners` | ✓ | Via `routing.scripts` and `routing.automation` sections |
| `audit_checks` | **MISSING** | No dedicated `audit_checks` key. Some checks exist in SKILL.md QCC but not in the machine-readable schema. |
| `promotion_rules` | **MISSING** | No dedicated `promotion_rules` key. Archcore promotion rules exist only in patterns/archcore-routing.md and SKILL.md. |
| `context_recovery` | **MISSING** | No dedicated `context_recovery` key. No post-compaction rebuild procedure. |

### Template-level `templates/context-map.yaml`

| Schema field | Present? | Details |
|---|---|---|
| `files` | ✓ | Via `authority_order` (17 entries — includes .archcore, memory-bank, ARCHCORE_PROMOTION_CANDIDATES) |
| `authority` | ✓ | Includes `generated_support` level |
| `classification` | ✓ | More granular types than package-level |
| `read_order` | ✓ | Via `bootstrap.required_first_read` |
| `update_triggers` | ✓ | Via `update_rules` (9 triggers) |
| `companion_files` | ✓ | Via `update_rules.also_consider` fields |
| `dependencies` | Partial | Implicit via routing groups |
| `generated_artifacts` | ✓ | Via `generated_context_policy.regenerate_after` |
| `task_runners` | ✓ | Via scripts/automation routing sections |
| `audit_checks` | **MISSING** | Not present in schema |
| `promotion_rules` | **MISSING** | Not present in schema |
| `context_recovery` | **MISSING** | Not present in schema |

---

## 6. AI_NAVIGATION Audit

### Package-level `AI_NAVIGATION.md`

| Requirement | Present? | Details |
|---|---|---|
| Read-first sequence | ✓ | 8-item mandatory read order |
| Source-of-truth hierarchy | ✓ | 9-level source priority table |
| Generated-output policy | ✓ | Generated context section + context map table shows `Generated support` / `Generated artifact` |
| File relationship map | ✓ | Context map table (20+ files, 3 columns: path, role, authority) |
| Companion update rules | ✓ | Update rules table (8 change types × their companion files) |
| Task execution policy | ✓ | Script and Task Navigation section (7-item read order, just-preferred, uncataloged script rules) |
| Compaction recovery procedure | **MISSING** | No section titled "Context compaction recovery" or similar. The Generated context section says "Regenerate these after large changes" but doesn't give a step-by-step procedure. |
| Audit procedure | ✓ | "Audit package consistency" section with 6-item checklist |

### Template `templates/AI_NAVIGATION.md`

| Requirement | Present? | Details |
|---|---|---|
| Read-first sequence | ✓ | 7-item mandatory read order |
| Source-of-truth hierarchy | ✓ | 11-level source priority |
| Generated-output policy | ✓ | Generated context section + context map table |
| File relationship map | ✓ | Project context files table (20+ entries) |
| Companion update rules | ✓ | Update rules table (9 change types) |
| Task execution policy | ✓ | Script and Task Navigation section |
| Compaction recovery procedure | **MISSING** | Not present in template |
| Audit procedure | ✓ | Drift handling section with stop-and-report policy |

---

## 7. Agent Instructions Audit

### `AGENTS.md` (package-level)

| Instruction | Present? | Details |
|---|---|---|
| Read AI_NAVIGATION.md first | ✓ | Navigation block rule 1 explicitly says "Read AI_NAVIGATION.md" |
| Read context-map.yaml before changing files | ✓ | Navigation block rule 2 |
| Inspect companion-file rules before edits | **PARTIAL** | Rule 11 says "identify which governance files must be updated" but no explicit companion-file rule |
| Update CHANGELOG.md for governance/navigation changes | **PARTIAL** | Rule 7 says to append CHANGELOG.md for material changes (implied but not explicit) |
| Avoid treating Graphify/Repomix output as canonical truth | **MISSING** | Not mentioned in AGENTS.md (it's in README, SKILL, ARCHITECTURE, AI_NAVIGATION) |
| Use task runners before raw scripts | ✓ | Rules 28-30 cover task-runner first, just-preferred, uncataloged as unknown safety |
| Run audit/check commands where defined | **MISSING** | No instruction to run audit commands programmatically |

### `templates/AGENTS-navigation-block.md`

| Instruction | Present? | Details |
|---|---|---|
| Read AI_NAVIGATION.md first | ✓ | Rule 1 |
| Read context-map.yaml before changing files | ✓ | Rule 2 |
| Inspect companion-file rules before edits | **PARTIAL** | Rule 11 says "identify which governance files must be updated" |
| Update CHANGELOG.md for governance/navigation changes | ✓ | Rule 3 implies this (read CHANGELOG.md entries) but update is implied — Rule 12 covers scripts/README.md but not CHANGELOG.md explicitly |
| Avoid treating Graphify/Repomix output as canonical truth | **MISSING** | Not in the navigation block template |
| Use task runners before raw scripts | ✓ | Rule 9 |
| Run audit/check commands where defined | **MISSING** | Not in navigation block |

### `CLAUDE.md`

Correct as-is (thin wrapper). No instruction upgrades needed.

---

## 8. Drift and Coherence Audit (`patterns/drift-audit.md`)

### Detection capability assessment

| Detection requirement | Can current drift-audit.md detect? | Details |
|---|---|---|
| Contradictory authority claims | **Weak** | Checkpoint 11 says "drift/conflict policy says stop-and-report" but doesn't actually scan for contradictions |
| Stale read order | **Weak** | Checkpoint 2 confirms AI_NAVIGATION points to context-map.yaml, but doesn't verify read-order freshness |
| Missing companion updates | **MISSING** | No checkpoint checks whether companion files were updated together |
| Stale generated artifact references | **MISSING** | No checkpoint checks whether graphify-out/ or .ai-context/ references are stale |
| Uncataloged scripts | **MISSING** | Not in drift-audit.md (handled in script-task-audit-checklist.md, but drift-audit doesn't cross-reference it) |
| Missing task runner documentation | **MISSING** | No checkpoint checks scripts/README.md presence or completeness |
| Stale Graphify/Repomix assumptions | **MISSING** | No checkpoint checks whether Graphify/Repomix references in governance files are current |
| .archcore/ promotion inconsistencies | **MISSING** | Checkpoint 5 confirms .archcore/ is "present and routed" but doesn't check promotion gates |

### Current drift-audit.md content (27 lines, 11 checkpoints)

```
1. AGENTS → AI_NAVIGATION pointer            ✓
2. AI_NAVIGATION → context-map.yaml pointer  ✓
3. CHANGELOG exists                          ✓
4. context-map.yaml routing present          ✓
5. .archcore/ present/routed                 ✓
6. memory-bank/ present/routed               ✓
7. Generated context excluded from truth     ✓
8. SCRATCHPAD marked transient               ✓
9. Repeat-run managed blocks exist           ✓
10. Risky YAML/JSON uses .proposed           ✓
11. Drift/conflict policy stop-and-report    ✓
```

The current pattern is a good starting point but needs to be expanded to cover the full audit surface.

---

## 9. Upgrade Recommendations

### P0 — Required before upgrade

| File | Change required | Reason |
|---|---|---|
| `patterns/drift-audit.md` | Rewrite to add companion-update verification, stale-reference detection, generated-artifact staleness, .archcore/ promotion consistency, task-runner consistency, cross-reference to script-task-audit-checklist.md | Current pattern is too shallow (11 checkpoints) to detect most forms of drift. |
| `templates/context-preflight.sh` | Fix `[5/5]` → `[5/6]` on line 46 | Numbering bug — 6 steps defined, step counter says 5. |

### P1 — Should upgrade now

| File | Change required | Reason |
|---|---|---|
| `context-map.yaml` (both package and template) | Add `audit_checks`, `promotion_rules`, `context_recovery` schema fields with meaningful structure | These are implicit in SKILL.md orchestration but absent from the machine-readable schema. |
| `SKILL.md` | Add context-compaction recovery step to Phase 4 or as a new section | No explicit post-compaction rebuild procedure exists anywhere in the package. |
| `templates/AI_NAVIGATION.md` | Add "Context compaction recovery" section with step-by-step procedure | Agents need to know exactly what to do after compaction. |
| `AI_NAVIGATION.md` (package) | Add "Context compaction recovery" section | Same gap at package level. |
| `AGENTS.md` | Add explicit instruction: do not treat Graphify/Repomix output as canonical truth | This rule exists in README, SKILL, ARCHITECTURE, AI_NAVIGATION — but not in AGENTS.md where agents look first. |
| `AGENTS.md` | Add explicit instruction: update companion files when changing sources | Rule 11 ("identify which governance files must be updated") is too vague. |
| `templates/AGENTS-navigation-block.md` | Add companion-update obligation note | Same gap as AGENTS.md at template level. |
| `context-map.yaml` (package) | Fix duplicate `templates/justfile` entry in `generated_templates.read` | Line 71-72 shows `templates/justfile` twice. |

### P2 — Optional improvement

| File | Change required | Reason |
|---|---|---|
| `SKILL.md` | Extract embedded fallback templates into actual template files | SKILL.md is 1532 lines; embedded content makes navigation harder. (Already listed as follow-up task in SKILL.md itself.) |
| `templates/AI_NAVIGATION.md` | Align Script and Task Navigation read-order with SKILL.md embedded fallback | Template lists "Existing canonical runner" first; SKILL.md embedded fallback lists "justfile" first. Minor but creates confusion. |
| `README.md` | Add brief context-recovery pointer | Completeness. |
| `context-map.yaml` (package) | Expand `bootstrap.required_first_read` to include more companion files | Currently only 5 files listed; update_rules references 9 triggers with different companion sets. |

---

## 10. No-Change Areas

These files and sections are already good enough and should **not** be rewritten wholesale:

| File | Reason |
|---|---|
| **CLAUDE.md** | Correct as thin wrapper. No content to add. |
| **ARCHITECTURE.md** | Well-structured, accurate, covers all tool-stack roles and flow. |
| **CHANGELOG.md** | Comprehensive, well-formatted, includes rationale notes. No rewrite needed. |
| **ROADMAP.md** | Honest about what's implemented and what's pending. No rewrite needed. |
| **SCRATCHPAD.md** | Structure is correct. Content is stale by nature (captures last session) but structural change not needed. |
| **templates/repomix.config.json** | Complete include/ignore set. Includes ARCHCORE_PROMOTION_CANDIDATES.md. |
| **templates/justfile** | Lightweight and appropriate. 4 tasks with safety notes. |
| **templates/scripts-README.md** | Well-structured with managed blocks, safety labels, maintenance rules. |
| **patterns/archcore-routing.md** | Strong extraction heuristics, exclusion table, completion gate. |
| **patterns/memory-bank-structure.md** | Simple, correct, 4 rules. |
| **patterns/script-task-audit-checklist.md** | Thorough (110 lines, 8 sections) with executable validation commands. |
| **templates/AGENTS-navigation-block.md** | 12 clear rules covering read order, script safety, companion updates (rule 12). |

---

## 11. Final Implementation Plan

### Stage 1: Update schema/templates

1. **Fix `templates/context-preflight.sh`** — `[5/5]` → `[5/6]`
2. **Add `audit_checks` to `context-map.yaml`** — schema field with expected validation rules
3. **Add `promotion_rules` to `context-map.yaml`** — schema field capturing Archcore promotion gates
4. **Add `context_recovery` to `context-map.yaml`** — schema field for post-compaction rebuild instructions
5. **Propagate same three fields to `templates/context-map.yaml`**
6. **Fix duplicate `templates/justfile` entry in package `context-map.yaml`**

### Stage 2: Update SKILL.md orchestration

7. **Add context-compaction recovery procedure** — new section or Phase 4 step: step-by-step rebuild instructions (read AI_NAVIGATION → load .archcore/ → regenerate graphify-out/ → regenerate .ai-context/ → verify SCRATCHPAD.md → verify CHANGELOG.md is current)
8. **Strengthen Quality Check Checklist** — add explicit companion-update verification check item

### Stage 3: Update README / ARCHITECTURE

9. **Add brief context-recovery pointer to README.md** — one-sentence pointer to the compaction recovery procedure in SKILL.md
10. **ARCHITECTURE.md** — no changes needed (already strong)

### Stage 4: Update AGENTS/CLAUDE instructions

11. **Add to `AGENTS.md` navigation block** — rule: "Do not treat Graphify/Repomix output as canonical truth"
12. **Add to `AGENTS.md` navigation block** — rule: "Update all companion files listed in context-map.yaml update_rules when changing source files" (strengthen rule 11)
13. **Propagate both additions to `templates/AGENTS-navigation-block.md`**

### Stage 5: Update drift-audit and script audit patterns

14. **Rewrite `patterns/drift-audit.md`** — expand from 11 to ~20+ checkpoints covering:
    - Companion-file update verification
    - Stale-file reference detection
    - Generated-artifact staleness checks
    - .archcore/ promotion-gate verification
    - Task-runner consistency checks
    - Cross-reference to script-task-audit-checklist.md
    - Old-tool-reference detection
    - SCRATCHPAD KEEP vs governance-drift consistency

### Stage 6: Run validation

15. Run `just --list` on the package (if justfile present at package root — check)
16. Validate context-map.yaml files are valid YAML
17. Validate templates/context-preflight.sh is syntactically valid bash
18. Confirm all cross-file references resolve

### Stage 7: Update CHANGELOG.md

19. Append entry documenting all changes from stages 1-6, using timestamp format `20260529_HHMM`

---

## Summary of all files that need changes

| File | Stage | Priority | Change type |
|---|---|---|---|
| `templates/context-preflight.sh` | 1 | P0 | Fix line 46 numbering |
| `patterns/drift-audit.md` | 5 | P0 | Rewrite with full depth |
| `context-map.yaml` | 1 | P1 | Add 3 schema fields, fix duplicate |
| `templates/context-map.yaml` | 1 | P1 | Add 3 schema fields |
| `SKILL.md` | 2 | P1 | Add compaction recovery section |
| `templates/AI_NAVIGATION.md` | 2 | P1 | Add compaction recovery section |
| `AI_NAVIGATION.md` | 2 | P1 | Add compaction recovery section |
| `AGENTS.md` | 4 | P1 | Add 2 rules |
| `templates/AGENTS-navigation-block.md` | 4 | P1 | Add companion-update instruction |
| `README.md` | 3 | P2 | Add recovery pointer |
| `templates/AI_NAVIGATION.md` | 3 | P2 | Align read-order with embedded fallback |

**Files requiring no changes:** `CLAUDE.md`, `ARCHITECTURE.md`, `CHANGELOG.md`, `ROADMAP.md`, `SCRATCHPAD.md`, `templates/repomix.config.json`, `templates/justfile`, `templates/scripts-README.md`, `patterns/archcore-routing.md`, `patterns/memory-bank-structure.md`, `patterns/script-task-audit-checklist.md`, `.gitignore`.

---

**AUDIT COMPLETE: AUDIT-ai-navigation-control-layer.md created**
