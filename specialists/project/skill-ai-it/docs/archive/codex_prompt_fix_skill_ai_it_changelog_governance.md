# Codex Prompt — Fix skill-ai-it CHANGELOG Governance Integration

Use this prompt in Codex from the skill root:

```text
You are editing this local skill package:

/Users/malik.ahmad/_ai/_skills/skills_stuff/specialists/project/skill-ai-it

Goal:
Make `CHANGELOG.md` a first-class governance file across the entire `skill-ai-it` package and generated project templates. Fix any remaining structural issues in `SKILL.md`. The package must be ready for repeat-safe use.

Strict rules:
- Do not delete existing files.
- Do not overwrite user-authored content blindly unless this prompt explicitly says to replace a file.
- Preserve `SKILL.md.bak`.
- Do not modify runtime/cache/generated folders.
- Do not add secrets or machine-local credentials.
- Use exact, minimal edits.
- After editing, run verification commands and report results.
- If a command fails, stop and show the error.

Files to update:
- `SKILL.md`
- `README.md`
- `AGENTS.md`
- `AI_NAVIGATION.md`
- `context-map.yaml`
- `CHANGELOG.md`
- `templates/AI_NAVIGATION.md`
- `templates/context-map.yaml`
- `templates/repomix.config.json`
- `templates/AGENTS-navigation-block.md`
- `patterns/drift-audit.md`

Do not modify unless required:
- `CLAUDE.md`
- `templates/context-preflight.sh`
- `patterns/archcore-routing.md`
- `patterns/memory-bank-structure.md`

Task 1 — Inspect current state:
Run:

cd /Users/malik.ahmad/_ai/_skills/skills_stuff/specialists/project/skill-ai-it
find . -maxdepth 2 -type f | sort
grep -R "CHANGELOG.md" -n SKILL.md README.md AGENTS.md AI_NAVIGATION.md context-map.yaml templates patterns CHANGELOG.md || true
grep -n "Phase 4 — Generate Files" SKILL.md || true
grep -n "#### SCRATCHPAD.md" SKILL.md || true
grep -n "#### CHANGELOG.md" SKILL.md || true

Task 2 — Fix `SKILL.md`:
Ensure all of the following are true:

1. YAML description says bootstrap always creates:
   `README.md`, `AGENTS.md`, `CLAUDE.md`, `SCRATCHPAD.md`, and `CHANGELOG.md`.

2. Use-when section includes:
   “Refreshing governance files and CHANGELOG.md after the project has evolved.”

3. Repeat-Safety Contract includes:
   `CHANGELOG.md` is the durable project history/governance-change ledger and must be appended to, not historically rewritten.

4. Skill package layout includes:

skill-ai-it/
├── SKILL.md
├── README.md
├── AGENTS.md
├── CLAUDE.md
├── AI_NAVIGATION.md
├── context-map.yaml
├── CHANGELOG.md
├── templates/
│   ├── AI_NAVIGATION.md
│   ├── context-map.yaml
│   ├── repomix.config.json
│   ├── AGENTS-navigation-block.md
│   └── context-preflight.sh
└── patterns/
    ├── archcore-routing.md
    ├── memory-bank-structure.md
    └── drift-audit.md

5. Phase 1 inventory detects:
   `CHANGELOG.md` exists → read recent entries to understand project evolution and governance changes.

6. Parent folder scan includes:
   `CHANGELOG.md` — read recent entries to inherit project/package evolution context.

7. Phase 2 read priority includes `CHANGELOG.md` after `README.md`.

8. Parent changelog read instructions exist:
   Read parent `CHANGELOG.md` if present to extract:
   - Recent governance or routing changes
   - Recent template/pattern changes
   - Migration notes that affect repeat-run safety
   - Deprecated or superseded behaviours

9. Phase 3 governance completeness includes `CHANGELOG`.

10. `## Phase 4 — Generate Files` exists immediately before `### File creation/update policy`.

11. File creation/update policy table includes:
   `CHANGELOG.md` | create/update | append navigation addition | append refresh summary | check

12. README template governance pointers include:
   Project change/governance history: [CHANGELOG.md](CHANGELOG.md)

13. `#### SCRATCHPAD.md` and `#### CHANGELOG.md` are separate valid Markdown sections.
   The correct order must be:
   - full SCRATCHPAD section
   - then full CHANGELOG section
   - then AI_NAVIGATION section

14. `#### CHANGELOG.md` section must say:
   - Always create during bootstrap.
   - If it exists, append entries only.
   - Do not rewrite historical entries.
   - It is the durable project history/governance-change ledger.
   - It is not a scratchpad.
   - It must not contain long terminal logs or unverified speculation.
   - Include initial bootstrap format and repeat-run append format.

15. Embedded `AI_NAVIGATION.md` fallback must include:
   - `CHANGELOG.md` in project context files table
   - `CHANGELOG.md` in source/update rules
   - rule: governance or navigation files changed → append `CHANGELOG.md`

16. Embedded `context-map.yaml` fallback must include:
   - `CHANGELOG.md` in `authority_order`
   - `CHANGELOG.md` in documentation routing
   - `CHANGELOG.md` in governance/history update rules

17. Embedded `repomix.config.json` fallback must include:
   `CHANGELOG.md` in the `include` array.

18. Conventions baked in must include:
   `CHANGELOG.md` is the durable project/governance history ledger; append to it on meaningful bootstrap, navigation, refresh, audit, or promote runs.

19. Quality check must include:
   `CHANGELOG.md` created or appended for meaningful governance/navigation changes.

20. Audit output format must include:
   `CHANGELOG.md` appended summary of meaningful governance/navigation changes.

Task 3 — Replace external governance files with consistent versions:

Replace `README.md` with this content:

# skill-ai-it

Reusable AI governance and navigation bootstrap skill for project folders.

## Purpose

`skill-ai-it` analyzes a target folder and creates or refreshes governance, context-routing, and AI navigation files.

It supports mixed projects where content may include code, scripts, Markdown design notes, architecture docs, roadmap files, scratchpads, changelogs, and conceptual planning documents.

## Modes

| Mode | Purpose |
|---|---|
| `bootstrap` | Create initial governance scaffold for a new/light project |
| `navigation-add` | Add AI navigation starter files to an existing project |
| `refresh` | Safely update managed sections without overwriting custom content |
| `audit` | Report missing/stale/conflicting governance/context files |
| `promote` | Propose durable promotion from scratchpad/memory/docs into Archcore/ADR/rules/specs/plans |

## Package layout

```text
skill-ai-it/
├── SKILL.md
├── README.md
├── AGENTS.md
├── CLAUDE.md
├── AI_NAVIGATION.md
├── context-map.yaml
├── CHANGELOG.md
├── templates/
│   ├── AI_NAVIGATION.md
│   ├── context-map.yaml
│   ├── repomix.config.json
│   ├── AGENTS-navigation-block.md
│   └── context-preflight.sh
└── patterns/
    ├── archcore-routing.md
    ├── memory-bank-structure.md
    └── drift-audit.md
```

## Key rules

- `SKILL.md` owns orchestration logic.
- `templates/` owns reusable generated-file templates.
- `patterns/` owns optional guidance modules.
- `CHANGELOG.md` owns durable package history and governance/navigation change history.
- Repeat runs must be safe and must not overwrite user-authored content wholesale.
- Existing files should be updated through managed blocks or `.proposed` files.
- `.archcore/`, if present in a target project, is treated as durable structured truth.
- `graphify-out/` and `.ai-context/` are generated support artifacts, not canonical truth.

## Usage intent

Use this skill when asked to:

- bootstrap a project
- add AI navigation
- refresh governance
- audit context drift
- make agent context less fragile after compaction
- create repeat-safe context-routing files
- append durable governance/navigation changes to `CHANGELOG.md`

Replace `AGENTS.md` with this content:

Title: skill-ai-it Agent Policy
Category: agent-governance-guide
Status: current
Authority: local-supplement
Scope: skill-ai-it package maintenance
Last reviewed: 2026-05-22
Summary: Rules for maintaining the skill-ai-it package.

# AGENTS.md

## Working rules

- Treat `SKILL.md` as the orchestration contract.
- Treat `templates/` as the source for reusable generated-file content.
- Treat `patterns/` as reusable optional guidance modules.
- Treat `CHANGELOG.md` as the durable package history and governance/navigation change ledger.
- Do not let embedded fallback examples in `SKILL.md` drift away from external templates.
- If a template changes, check whether the matching fallback/example in `SKILL.md` should also change.
- If `SKILL.md` changes the expected package layout, update `README.md`, `AI_NAVIGATION.md`, and `context-map.yaml`.
- If `SKILL.md`, templates, patterns, or governance routing changes materially, append a concise entry to `CHANGELOG.md`.
- Preserve repeat-safe behaviour:
  - no wholesale overwrites
  - use managed blocks
  - write `.proposed` files for risky YAML/JSON changes
  - report created/updated/skipped/proposed files separately
- Keep `CLAUDE.md` as a thin wrapper around this file.
- Keep this package tool-agnostic: it should work for Codex, Claude Code, and local LLM workflows.

<!-- BEGIN skill-ai-it:navigation -->

## AI navigation and context preflight

Before editing this skill package:

1. Read `AI_NAVIGATION.md`.
2. Read `context-map.yaml`.
3. Read `SKILL.md`.
4. Read recent entries in `CHANGELOG.md`.
5. Read relevant files under `templates/` and `patterns/`.
6. If changing a generated-file template, check whether `SKILL.md` still has matching fallback/reference content.
7. If sources conflict, stop and report the conflict before editing.

<!-- END skill-ai-it:navigation -->

## Maintenance boundaries

- Do not add runtime/cache/generated outputs to the skill package.
- Do not store project-specific target outputs here.
- Do not add secrets or machine-local credentials.
- Keep examples generic and reusable.

Replace `AI_NAVIGATION.md` with this content:

# AI Navigation — skill-ai-it

Purpose: this file is the context entrypoint for agents maintaining `skill-ai-it`.

This package is a reusable AI governance/navigation bootstrap skill. It must remain repeat-safe, template-driven, changelog-aware, and tool-agnostic.

<!-- BEGIN skill-ai-it:navigation -->

## Mandatory read order

Before editing this skill package, read:

1. `AGENTS.md`
2. `AI_NAVIGATION.md`
3. `context-map.yaml`
4. `SKILL.md`
5. Recent entries in `CHANGELOG.md`
6. Relevant files under `templates/`
7. Relevant files under `patterns/`

## Source priority

When sources conflict, use this priority:

1. `SKILL.md` orchestration rules
2. External files under `templates/`
3. External files under `patterns/`
4. `AGENTS.md`
5. `CHANGELOG.md`
6. `AI_NAVIGATION.md`
7. `context-map.yaml`
8. `README.md`

Note: for generated output content, external template files win over embedded fallback examples in `SKILL.md`.

## Context map

| Path | Role | Authority |
|---|---|---|
| `SKILL.md` | Main skill contract and orchestration logic | Highest |
| `CHANGELOG.md` | Durable package history and governance/navigation change ledger | High |
| `templates/AI_NAVIGATION.md` | Target-project AI navigation template | High |
| `templates/context-map.yaml` | Target-project routing-map template | High |
| `templates/repomix.config.json` | Target-project Repomix config template | High |
| `templates/AGENTS-navigation-block.md` | Managed AGENTS navigation block | High |
| `templates/context-preflight.sh` | Context preflight script template | High |
| `patterns/archcore-routing.md` | Archcore integration guidance | Medium-high |
| `patterns/memory-bank-structure.md` | Memory Bank guidance | Medium-high |
| `patterns/drift-audit.md` | Drift audit guidance | Medium-high |
| `README.md` | Human overview | Medium |
| `AGENTS.md` | Agent maintenance rules | High |
| `CLAUDE.md` | Claude wrapper | Medium |

## Task routing

### Change skill behaviour

Read:

1. `SKILL.md`
2. `CHANGELOG.md`
3. `AGENTS.md`
4. `context-map.yaml`
5. Affected template/pattern files

### Change generated project output

Read:

1. Matching file under `templates/`
2. Matching fallback/example section in `SKILL.md`
3. `patterns/` file if behaviour is conceptual rather than a direct template

### Change Archcore/memory/Graphify/Repomix guidance

Read:

1. `patterns/archcore-routing.md`
2. `patterns/memory-bank-structure.md`
3. `patterns/drift-audit.md`
4. `SKILL.md`
5. affected template files

### Audit package consistency

Check:

1. Package layout in `SKILL.md`
2. Files listed in `README.md`
3. Files listed in `context-map.yaml`
4. Actual files under `templates/` and `patterns/`
5. Recent entries in `CHANGELOG.md`

## Drift handling

If `SKILL.md` and external templates disagree:

1. Identify the conflict.
2. Decide whether orchestration or template content is authoritative.
3. Update both if needed.
4. Append `CHANGELOG.md` if the change is meaningful.
5. Do not silently leave mismatched examples.

## Update rules

| Change type | Update |
|---|---|
| New operating mode | `SKILL.md`, `README.md`, `context-map.yaml`, `CHANGELOG.md` |
| New template | `templates/`, `SKILL.md`, `README.md`, `context-map.yaml`, `CHANGELOG.md` |
| New pattern | `patterns/`, `SKILL.md`, `README.md`, `context-map.yaml`, `CHANGELOG.md` |
| Repeat-safety change | `SKILL.md`, `AGENTS.md`, relevant templates, `CHANGELOG.md` |
| Context-routing change | `AI_NAVIGATION.md`, `context-map.yaml`, `AGENTS.md`, `CHANGELOG.md` |
| Any meaningful governance/navigation change | `CHANGELOG.md` |

<!-- END skill-ai-it:navigation -->

Replace `context-map.yaml` with this content:

version: 1

project:
  name: skill-ai-it
  type: reusable_ai_skill
  context_policy: "SKILL.md is the orchestration contract; templates/ and patterns/ are reusable content sources; CHANGELOG.md is the durable package/governance history ledger."

bootstrap:
  required_first_read:
    - AGENTS.md
    - AI_NAVIGATION.md
    - context-map.yaml
    - SKILL.md
    - CHANGELOG.md

authority_order:
  - path: "SKILL.md"
    type: skill_contract
    authority: highest
  - path: "CHANGELOG.md"
    type: package_history
    authority: high
  - path: "templates"
    type: reusable_templates
    authority: high
  - path: "patterns"
    type: reusable_patterns
    authority: medium_high
  - path: "AGENTS.md"
    type: agent_maintenance_rules
    authority: high
  - path: "AI_NAVIGATION.md"
    type: context_router
    authority: high
  - path: "context-map.yaml"
    type: machine_routing_map
    authority: high
  - path: "README.md"
    type: human_overview
    authority: medium
  - path: "CLAUDE.md"
    type: claude_wrapper
    authority: medium

routing:
  skill_orchestration:
    description: "Changes to modes, phases, repeat-safety, file creation policy, or lifecycle behaviour."
    read:
      - "SKILL.md"
      - "CHANGELOG.md"
      - "AGENTS.md"
      - "AI_NAVIGATION.md"
      - "context-map.yaml"

  generated_templates:
    description: "Changes to project files generated by the skill."
    read:
      - "templates/**/*.md"
      - "templates/**/*.yaml"
      - "templates/**/*.json"
      - "templates/**/*.sh"
      - "SKILL.md"
      - "CHANGELOG.md"

  guidance_patterns:
    description: "Changes to optional guidance modules such as Archcore, Memory Bank, or drift audit."
    read:
      - "patterns/**/*.md"
      - "SKILL.md"
      - "AI_NAVIGATION.md"
      - "CHANGELOG.md"

  package_docs:
    description: "Changes to skill package documentation and maintenance rules."
    read:
      - "README.md"
      - "CHANGELOG.md"
      - "AGENTS.md"
      - "AI_NAVIGATION.md"
      - "context-map.yaml"
      - "CLAUDE.md"

update_rules:
  new_mode:
    update:
      - "SKILL.md"
      - "README.md"
      - "context-map.yaml"
      - "CHANGELOG.md"

  new_template:
    update:
      - "templates"
      - "SKILL.md"
      - "README.md"
      - "AI_NAVIGATION.md"
      - "context-map.yaml"
      - "CHANGELOG.md"

  new_pattern:
    update:
      - "patterns"
      - "SKILL.md"
      - "README.md"
      - "AI_NAVIGATION.md"
      - "context-map.yaml"
      - "CHANGELOG.md"

  repeat_safety_change:
    update:
      - "SKILL.md"
      - "AGENTS.md"
      - "README.md"
      - "CHANGELOG.md"

  navigation_change:
    update:
      - "AI_NAVIGATION.md"
      - "context-map.yaml"
      - "AGENTS.md"
      - "CHANGELOG.md"

  governance_history:
    update:
      - "CHANGELOG.md"

drift_policy:
  on_conflict:
    action: "stop_and_report"
    required_output:
      - conflicting_files
      - higher_authority_source
      - recommended_fix
      - assumptions

answer_contract:
  require_source_paths: true
  unsupported_answer: "not found in skill package context"
  distinguish_assumptions: true
  do_not_invent_state: true

Task 4 — Replace external templates/patterns:

Replace `templates/AI_NAVIGATION.md` with a target-project template that includes:
- mandatory read order including `CHANGELOG.md`
- source priority including `CHANGELOG.md`
- planning and governance task routing that reads `CHANGELOG.md`
- update rule: governance or navigation files changed → append `CHANGELOG.md`

Replace `templates/context-map.yaml` with a target-project template that includes:
- `CHANGELOG.md` in `bootstrap.required_first_read`
- `CHANGELOG.md` in `authority_order`
- `CHANGELOG.md` in planning/governance/documentation routing
- update rule `governance_history` → `CHANGELOG.md`

Replace `templates/repomix.config.json` so the include array contains:
- `CHANGELOG.md` immediately after `SCRATCHPAD.md`

Replace `templates/AGENTS-navigation-block.md` so the managed preflight block includes:
3. Read recent entries in [CHANGELOG.md](CHANGELOG.md).

Replace `patterns/drift-audit.md` so checkpoints include:
3. Confirm `CHANGELOG.md` exists and recent governance/navigation changes are recorded.

Task 5 — Replace or update `CHANGELOG.md`:
Ensure `CHANGELOG.md` has a top entry:

## 2026-05-22 — CHANGELOG governance integration

### Changed

- Promoted `CHANGELOG.md` to a first-class governance file for both the skill package and generated project governance.
- Updated `SKILL.md`, package governance files, templates, and drift-audit pattern to route, read, and update `CHANGELOG.md`.
- Fixed the `SKILL.md` SCRATCHPAD/CHANGELOG section ordering so each governance file has its own valid section.

### Notes

- `CHANGELOG.md` is now treated as a durable package/project history ledger and should be appended on meaningful bootstrap, navigation-add, refresh, audit, or promote runs.

Keep the older 2026-05-22 entry below it.

Task 6 — Verification:
Run exactly:

cd /Users/malik.ahmad/_ai/_skills/skills_stuff/specialists/project/skill-ai-it

grep -R "CHANGELOG.md" -n SKILL.md README.md AGENTS.md AI_NAVIGATION.md context-map.yaml templates patterns CHANGELOG.md

grep -n "## Phase 4 — Generate Files" SKILL.md
grep -n "#### SCRATCHPAD.md" SKILL.md
grep -n "#### CHANGELOG.md" SKILL.md
grep -n "#### AI_NAVIGATION.md" SKILL.md

python3 - <<'PY'
from pathlib import Path
p = Path("SKILL.md").read_text()
a = p.index("#### SCRATCHPAD.md")
b = p.index("#### CHANGELOG.md")
c = p.index("#### AI_NAVIGATION.md")
assert a < b < c, "section order must be SCRATCHPAD -> CHANGELOG -> AI_NAVIGATION"
assert "## Phase 4 — Generate Files" in p
assert "CHANGELOG.md" in p
print("SKILL.md structural checks passed")
PY

python3 - <<'PY'
from pathlib import Path
required = [
    "README.md",
    "AGENTS.md",
    "CLAUDE.md",
    "AI_NAVIGATION.md",
    "context-map.yaml",
    "CHANGELOG.md",
    "templates/AI_NAVIGATION.md",
    "templates/context-map.yaml",
    "templates/repomix.config.json",
    "templates/AGENTS-navigation-block.md",
    "templates/context-preflight.sh",
    "patterns/archcore-routing.md",
    "patterns/memory-bank-structure.md",
    "patterns/drift-audit.md",
]
missing = [f for f in required if not Path(f).exists()]
assert not missing, f"missing files: {missing}"
for f in [
    "README.md",
    "AGENTS.md",
    "AI_NAVIGATION.md",
    "context-map.yaml",
    "templates/AI_NAVIGATION.md",
    "templates/context-map.yaml",
    "templates/repomix.config.json",
    "templates/AGENTS-navigation-block.md",
    "patterns/drift-audit.md",
]:
    txt = Path(f).read_text()
    assert "CHANGELOG.md" in txt, f"{f} missing CHANGELOG.md reference"
print("package governance/template checks passed")
PY

Task 7 — Final report:
Return:
- files changed
- verification output
- whether the package is ready to use
- any remaining caveats

Ready criteria:
- grep returns multiple `CHANGELOG.md` references across `SKILL.md`, package governance files, templates, and patterns.
- Python structural checks pass.
- Section order is `SCRATCHPAD -> CHANGELOG -> AI_NAVIGATION`.
- `CHANGELOG.md` has the governance integration entry at top.
```
