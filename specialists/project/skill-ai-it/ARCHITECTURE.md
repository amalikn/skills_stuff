# skill-ai-it Architecture

## Contents

- [Four capabilities](#four-capabilities)
- [Package roles](#package-roles)
- [Flow](#flow)
- [Tool stack](#tool-stack)
- [Script and Task Inventory Layer](#script-and-task-inventory-layer)
- [Runtime model](#runtime-model)
- [Repeat-safety model](#repeat-safety-model)
- [Managed block behavior](#managed-block-behavior)
- [Existing-project upgrade behavior](#existing-project-upgrade-behavior)
- [Context compaction recovery](#context-compaction-recovery)
- [Drift/coherence audit](#driftcoherence-audit)
- [Deterministic navigation-control automation](#deterministic-navigation-control-automation)
`skill-ai-it` is a reusable governance/navigation skill. It analyzes a target folder, infers what project context exists, and creates or refreshes repeat-safe guidance files without making the target
project depend on this skill package at runtime.

## Four capabilities

The skill provides four first-class capabilities:

| Capability | Implementation |
|---|---|
| **AI navigation map** | `AI_NAVIGATION.md` (template + embedded fallback) — read order, authority hierarchy, file map, generated-output policy, companion update rules, context compaction recovery, audit procedure. |
| **File relationship / dependency logic** | `context-map.yaml` authority_order + update_rules + routing define explicit file relationships and companion-file obligations. |
| **Agent coherence / compliance checks** | `patterns/drift-audit.md` validates managed block integrity, authority consistency, companion updates, generated-output policy, .archcore/ promotion gates, stale references, and repeat-run safety. |
| **Executable project coherence** | `patterns/governance-checks.md` + `templates/check_governance.py` generate a self-contained, stdlib-only `scripts/check_governance.py` per target project, turning that project's governance claims into assertions that fail. Drift-audit is a checklist the agent runs; this is a gate the project runs. Distinct layers — the checker polices its own coverage so it extends as the project grows. |
| **Structured machine-readable context** | `context-map.yaml` file registry with authority levels, classification, read_order, update_triggers, companion_files, dependencies, generated_artifacts, task_runners, audit_checks, promotion_rules, and context_recovery. |

## Package roles

| Area | Role |
|---|---|
| `SKILL.md` | Orchestration contract: modes, phases, repeat-safety rules, and embedded fallbacks. |
| `templates/` | Reusable generated-file templates for target projects. |
| `patterns/` | Optional guidance modules for concepts that may apply to a target project. |
| `README.md` | Human overview of the skill package. |
| `AI_NAVIGATION.md` | Maintenance router for agents editing this skill package. |
| `context-map.yaml` | Machine-readable routing map for this skill package. |
| `CHANGELOG.md` | Durable package history and governance/navigation change ledger. |

## Flow

```text
Operator request
      |
      v
skill-ai-it / SKILL.md
      |
      +--> Inventory target folder
      |        |
      |        +--> README / AGENTS / CHANGELOG / existing docs
      |        +--> code, configs, scripts, generated context
      |
      +--> Infer mode
      |        |
      |        +--> bootstrap
      |        +--> navigation-add
      |        +--> refresh
      |        +--> audit
      |        +--> promote
      |
      +--> Apply governed outputs
               |
               +--> Governance files
               |      README.md
               |      AGENTS.md
               |      CLAUDE.md
               |      SCRATCHPAD.md
               |      CHANGELOG.md
               |      AI_NAVIGATION.md
               |      context-map.yaml
               |
               +--> Durable truth layer
               |      .archcore/
               |        archcore init → .archcore/ container (bootstrap/refresh)
               |        candidates report → ARCHCORE_PROMOTION_CANDIDATES.md
               |        promote → .archcore/ content files (explicit only)
               |
               +--> Script/task inventory layer
               |      justfile (preferred lightweight catalog)
               |      existing runner (Taskfile.yml / Makefile / package.json)
               |      scripts/README.md
               |      just --list / just <task>  (when justfile present)
               |
               +--> Active context generation (CLIs invoked when available)
                      graphify update .      → graphify-out/
                      repomix --config ...   → .ai-context/
```

```text
Source-of-truth direction

.archcore/ + governed markdown + source files
              |
              v
justfile / existing task runner + scripts/README.md
              |
              v
AI_NAVIGATION.md + context-map.yaml
              |
              v
Graphify and Repomix generated outputs
              |
              v
Agent navigation and context loading

Generated outputs do not flow back into source-of-truth unless reviewed and promoted.
```

## Tool stack

### Archcore

Archcore provides structured durable project truth under `.archcore/`.

`skill-ai-it` uses Archcore when the `archcore` CLI is available. During `bootstrap`, `navigation-add`, or `refresh`, the skill initializes `.archcore/` with `archcore init` when it is missing. After
initialization, target-project routing should treat `.archcore/` as active structured truth for durable decisions, rules, specs, guides, and plans.

`archcore init` is setup. Creating or changing Archcore content files remains governed: propose ADRs, rules, specs, guides, or plans unless the user explicitly authorizes those content changes.

During `bootstrap` and `refresh`, after `archcore init`, `skill-ai-it` scans existing governance files and writes `ARCHCORE_PROMOTION_CANDIDATES.md` — a structured report of durable content candidates
(decisions, rules, specs, guides, plans) with source references and confidence ratings. This bridges the gap between `archcore init` (setup) and `promote` (content creation). No `.archcore/` content
files are created until `promote` mode is explicitly invoked.

### Graphify

Graphify produces generated relationship/navigation artifacts under `graphify-out/`, such as `GRAPH_REPORT.md` and `graph.json`.

`skill-ai-it` actively invokes `graphify update .` on every `bootstrap`, `navigation-add`, and `refresh` run when the CLI is available. If `graphify-out/` is missing, `graphify update .` initializes
it; if already present, it refreshes the graph. Graphify is a required tool for full skill operation — when unavailable, the Graphify step is skipped and reported.

Graphify output remains generated support, not canonical truth. Answers and durable decisions should be grounded in source files, `.archcore/`, or governance docs.

### Repomix

Repomix builds deterministic AI-readable context packs, usually under `.ai-context/`, from `repomix.config.json`.

`skill-ai-it` actively runs `repomix --config repomix.config.json` on every `bootstrap`, `navigation-add`, and `refresh` run when the CLI is available. If `repomix.config.json` is missing, the skill
creates it from `templates/repomix.config.json` first, then runs Repomix. Repomix output is generated support, not source-of-truth content. The config file is governed; the generated `.ai-context/`
output is rebuildable.

## Script and Task Inventory Layer

Project-local automation needs a separate inventory layer because raw scripts do not explain their purpose, side effects, or safety.

- `justfile` is the preferred lightweight task catalog for new projects. Agents use `just --list` to discover tasks and `just <task>` to run them.
- Existing task runners take priority: if the project already has a `Taskfile.yml`, `Makefile`, or `package.json` scripts, that remains the canonical runner.
- `scripts/README.md` is the human/agent-readable operational catalog. Created during bootstrap and refresh when scripts or tasks exist.
- Graphify is relationship discovery only; it can help find related scripts and files, but it does not certify script safety.
- Repomix is context packing only; it can include scripts and catalogs in an AI context bundle, but it does not decide what is safe to run.
- Archcore is for durable operational procedure promotion only; stable, accepted procedures may be promoted into `.archcore/guides/`, but not every script becomes Archcore truth automatically.
- Raw scripts under `scripts/` are not automatically safe.
- Agent preference order: existing canonical runner → `just --list` / `just <task>` → `scripts/README.md` → other runners → raw scripts after inspection.
- If only raw scripts exist, the skill should generate or propose `scripts/README.md` inventory entries before agents rely on them.

## Runtime model

The skill package is the maintained source for generic behavior. Target projects should not need local copies of the skill logic.

Repo-local scripts such as `scripts/context-preflight.sh` are explicit opt-in artifacts only. They can be useful as compatibility wrappers, but they must not become a second source of truth for
generic Archcore, Graphify, or Repomix behavior.

## Repeat-safety model

The skill favors reversible, scoped changes:

- update managed blocks instead of overwriting files wholesale
- append `CHANGELOG.md` instead of rewriting history
- write `.proposed` files for risky YAML/JSON changes
- report created, updated, skipped, and proposed files separately
- keep generated support artifacts separate from canonical truth

## Managed block behavior

All managed sections use the standard format:

```markdown
<!-- BEGIN MANAGED: skill-ai-it:<section-name> -->
<!-- skill-ai-it-version: <version-string> -->
...managed content...
<!-- END MANAGED: skill-ai-it:<section-name> -->
```

- Re-running the skill updates existing managed blocks in place, without duplication.
- User-authored content outside managed blocks is preserved.
- If a block exists with an older version, it is upgraded in place.
- If a block is missing, it is inserted at the correct location.
- If a project has no managed blocks (pre-upgrade), the skill inserts them without overwriting existing content.

## Existing-project upgrade behavior

When run against an existing project generated by an older version of the skill:

| Condition | Action |
|---|---|
| File missing | Create from current template |
| File exists with current managed block/version | Refresh only if source inputs changed |
| File exists with older managed block/version | Upgrade managed block only |
| File exists without managed block | Insert managed block without overwriting existing content |
| File has user-authored content | Preserve it |
| File has conflicting manual governance content | Stop and report, unless user explicitly approves |
| context-map.yaml has older schema | Add missing keys without removing custom keys |

## Context compaction recovery

After context compaction, rebuild agent context in this order:

1. Read `AI_NAVIGATION.md`
2. Load `.archcore/` if present
3. Regenerate `graphify-out/`: `graphify update .`
4. Regenerate `.ai-context/`: `repomix --config repomix.config.json`
5. Verify `SCRATCHPAD.md` — populate if empty
6. Verify `CHANGELOG.md` is current
7. Verify `AI_NAVIGATION.md` and `context-map.yaml` companion consistency

Label recovered entries: `Context recovered via skill-ai-it context-recovery procedure`.

## Drift/coherence audit

Use `patterns/drift-audit.md` for comprehensive drift detection. The drift audit validates:

- Managed block integrity (no duplicates, no version mismatch)
- Authority hierarchy consistency between AI_NAVIGATION.md, README.md, and context-map.yaml
- Companion-file update completeness (all files in update_rules updated together)
- Generated-output policy compliance (graphify-out/, .ai-context/ are support only)
- .archcore/ promotion gate enforcement (only promote mode writes content)
- Stale reference detection (removed tools, old task runners, superseded assumptions)
- Script/task catalog consistency (catalog matches actual files)
- Repeat-run safety (no duplicate blocks, no overwrites of user content)

## Deterministic navigation-control automation

For existing-project refresh, use deterministic Python scripts that perform idempotent, machine-verified upgrades:

| Script | Purpose |
|---|---|
| `scripts/upgrade_navigation_control_layer.py` | Idempotent managed-block upgrade, marker fix, context-map key addition |
| `scripts/validate_navigation_control_layer.py` | Coherence validation with pass/warn/fail output |
| `scripts/check_expected_diff.py` | Git-diff check against expected governance file changes |

Also see:

- `templates/update_rules.yaml` — default companion-file update rules template
- `patterns/navigation-control-automation.md` — explains when to run scripts, exit codes, .proposed handling
- `templates/justfile` — includes `nav-upgrade`, `nav-upgrade-dry-run`, `nav-validate`, `nav-check-diff` targets

**Key rules:**

- Scripts are the primary mechanism. Markdown patterns are policy/explanation.
- Always use `--dry-run` first. `.proposed` files written when YAML merging is risky.
- Scripts do not create `.archcore/`, `.ai-context/`, or `graphify-out/`.
- Generated outputs remain support-only. No automatic promotion.

