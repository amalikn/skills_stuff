# skill-ai-it — Replace mise with Just


You are working on the `skill-ai-it` repository.

**Goal:** replace the current mise-first script/task inventory strategy with a just-preferred, task-runner-neutral strategy.

Important terminology:
- The previous implementation used `mise` as the preferred/default structured task catalog.
- The new strategy must use `just` as the preferred lightweight task catalog.
- `mise` must not be removed entirely. It remains optional for projects that need tool/version/env management.
- The skill must stay task-runner-neutral: respect an existing canonical runner before creating or proposing a new one.

Primary design decision:

Use this hierarchy:

1. Existing project task runner, if already canonical
2. `justfile` as the preferred lightweight new task catalog
3. `scripts/README.md` as the human/agent-readable operational catalog
4. Raw `scripts/` files as implementation only, unknown safety until inspected/cataloged
5. `mise.toml` only when tool/env/version management is needed
6. `Taskfile.yml` only for richer workflow orchestration when justified
7. `Makefile` / `package.json` scripts respected when already established

Do not remove script/task inventory capability.
Do not make `just` mandatory.
Do not make `mise` mandatory.
Do not create both `justfile` and `mise.toml` unless there is a clear documented reason.
Do not invent runnable task behavior without inspecting scripts or receiving explicit project intent.

Required changes:

## 1. README.md

Update all mise-first wording.

Current problematic concepts to replace:
- "`mise.toml` and `.mise/tasks/`, when present, are treated as the canonical runnable task catalog."
- "mise is initialized when its CLI is available and no other task runner is canonical."
- Tool stack section presents "mise tasks" as the primary/default task layer.
- Authority order says `mise tasks + scripts/README.md`.

Replace with:

- Existing task runners are respected first.
- `justfile` is the preferred lightweight runnable task catalog for new/default catalogs.
- `scripts/README.md` is the human/agent-readable script/task inventory.
- `mise.toml` remains optional and is used only when tool/version/env management is needed.
- Raw scripts remain unknown safety until inspected or cataloged.
- `just` is optional and only used/created when appropriate.

Update the package layout tree:
- Add `templates/justfile`.
- Keep `templates/mise.toml` but mark it optional/environment-aware.
- Keep `templates/scripts-README.md`.
- Keep `patterns/script-task-audit-checklist.md`.

Update the Tool stack section:
- Rename or replace "mise tasks" entry with "just".
- Add a smaller "mise" entry as optional tool/env manager.
- Ensure the wording says Graphify and Repomix are support only.
- Ensure the intended authority order becomes something like:

governed docs/source files
-> canonical task runner, preferably justfile for lightweight catalogs
-> scripts/README.md
-> AI_NAVIGATION.md + context-map.yaml
-> Graphify / Repomix generated outputs
-> agent context loading

## 2. ARCHITECTURE.md

Update the `Script and Task Inventory Layer`.

Required wording:
- `justfile` = preferred lightweight executable task catalog for new/default task catalogs.
- Existing canonical task runners must be respected first.
- `scripts/README.md` = operational explanation catalog.
- `mise.toml` = optional environment/tool-version-aware task layer, not default.
- `.mise/tasks/` = optional only when mise is chosen.
- Graphify = relationship discovery only.
- Repomix = context packing only.
- Archcore = durable operational procedure promotion only.
- Raw scripts under `scripts/` are not automatically safe.
- Agents should prefer:
  1. existing canonical runner
  2. `just --list` / `just <task>` when a justfile exists
  3. `scripts/README.md`
  4. raw scripts only after inspection

Remove any architecture claim that mise is the default or preferred task source.

## 3. SKILL.md

Update orchestration logic.

Required behavior:

### Detection order

When detecting project automation, check in this order:

1. `justfile`
2. `Taskfile.yml`
3. `Makefile`
4. `package.json` scripts
5. `mise.toml`
6. `.mise/tasks/`
7. `scripts/`
8. `.github/workflows/`
9. `ansible/`
10. `playbooks/`

### Bootstrap behavior

- If an existing task runner exists, respect it.
- If no task runner exists but scripts/automation are present, prefer proposing or creating `justfile` as the lightweight task catalog.
- Create/update `scripts/README.md` when scripts/tasks/automation are present.
- Do not create `mise.toml` unless:
  - user explicitly asks for mise, or
  - project already uses mise, or
  - tool/version/env management is clearly needed and documented.
- Do not create empty task scaffolding if there are no scripts/tasks.

### Navigation-add behavior

- Add navigation pointers to existing runner first.
- If `justfile` exists, route agents to `just --list` and then `scripts/README.md`.
- If `mise.toml` exists, route agents to `mise tasks` only for that project.

### Refresh behavior

- Update managed inventory blocks only.
- Preserve manually written script/task descriptions.
- If drift exists between justfile/tasks/scripts and `scripts/README.md`, report or propose updates.
- Do not silently convert mise to just in target projects. The package-level preference changes, but existing target project choices are respected.

### Audit behavior

Report:
- scripts missing from `scripts/README.md`
- just recipes missing comments/descriptions
- cataloged scripts that no longer exist
- raw scripts not represented in any runner or `scripts/README.md`
- unsafe scripts without safety notes
- projects using both just and mise without documented boundary
- any stale wording that still says mise is default/preferred

### Promote behavior

- Promote only durable operational procedures to Archcore.
- Do not promote every just recipe or script.

Update safety labels if needed. Keep:
- safe
- review-required
- destructive
- external-network
- modifies-files
- requires-secrets
- requires-credentials
- long-running
- unknown

Agents must treat `unknown` as not safe until inspected.

## 4. Add new template

Create:

templates/justfile

Use this content:

# just task catalog for this project.
# Purpose:
# - expose safe, documented project tasks to humans and AI agents
# - avoid agents running arbitrary scripts without context
# - keep runnable entrypoints simple and readable
#
# List tasks:
#   just --list
#
# Run task:
#   just <task>
#
# Safety:
# - Prefer safe/read-only tasks by default.
# - Mark destructive tasks clearly and require review.
# - Keep detailed inputs/outputs/safety notes in scripts/README.md.

set dotenv-load := false

# List available tasks and show script inventory when present
inventory:
    @just --list
    @test -f scripts/README.md && sed -n '1,220p' scripts/README.md || true

# Audit script/task inventory for obvious drift
audit-scripts:
    @echo "== just recipes =="
    @just --list || true
    @echo
    @echo "== script files =="
    @find scripts -maxdepth 2 -type f 2>/dev/null | sort || true
    @echo
    @echo "== uncataloged script candidates =="
    @if [ -d scripts ] && [ -f scripts/README.md ]; then \
      find scripts -maxdepth 2 -type f | sort | while read -r f; do \
        grep -Fq "$f" scripts/README.md || echo "$f"; \
      done; \
    fi

# Run safe local preflight checks
preflight: audit-scripts lint-md

# Lint Markdown files when markdownlint-cli2 is available
lint-md:
    @command -v markdownlint-cli2 >/dev/null && markdownlint-cli2 '**/*.md' || echo 'markdownlint-cli2 not installed; skipped'

Do not add project-specific recipes unless discovered from actual scripts or requested by user.

## 5. Update templates/scripts-README.md

Make it task-runner-neutral with just preferred.

Update execution policy:
- Prefer the existing canonical task runner.
- Prefer `just <task>` when a `justfile` exists.
- Use `mise run <task>` only when the project uses mise.
- Do not run destructive/review-required/unknown scripts without review.
- Raw scripts remain unknown safety until inspected/cataloged.

Update preferred execution order:

1. Existing canonical task runner
2. `just --list` / `just <task>`
3. `scripts/README.md`
4. Other task runners: `Taskfile.yml`, `Makefile`, `package.json`, `mise.toml`
5. Raw scripts after inspection

Update inventory rows so examples use `just inventory`, `just audit-scripts`, and `just preflight` instead of `mise run ...`.

Keep safety labels.

## 6. Keep templates/mise.toml but demote it

Do not delete `templates/mise.toml`.

Update comments at the top:
- This is optional.
- Use when project needs tool/version/env management.
- Do not use as default task catalog if a lightweight `justfile` is enough.
- Do not create alongside an existing canonical runner without documented reason.

Ensure Python example remains non-mandatory and uses `3.14` or org/project-default wording.

## 7. Update AI_NAVIGATION.md

Update `## Script and Task Navigation`.

Required read/execution order:

1. Existing canonical runner if documented
2. `justfile`
3. `scripts/README.md`
4. `Taskfile.yml`
5. `Makefile`
6. `package.json`
7. `mise.toml` / `.mise/tasks/`
8. raw scripts under `scripts/` after inspection

Required rules:
- Prefer `just --list` and `just <task>` when `justfile` exists.
- Use `mise tasks` / `mise run <task>` only when the project uses mise.
- Do not treat mise as default.
- Do not run uncataloged scripts blindly.
- Stop for review on destructive/review-required/unknown tasks.

Update context map table if it includes `templates/mise.toml`:
- Add `templates/justfile`.
- Keep `templates/mise.toml` as optional/env-aware template.
- Keep `patterns/script-task-audit-checklist.md`.

## 8. Update templates/AI_NAVIGATION.md

Make the same target-project-safe changes:
- project-generic wording
- no mandatory `SKILL.md`
- `justfile` preferred when present
- mise optional only when present
- `scripts/README.md` remains operational catalog

## 9. Update context-map.yaml

Update script/task routing.

Ensure `scripts` and `automation` routes read:

- justfile
- scripts/README.md
- Taskfile.yml
- Makefile
- package.json
- mise.toml
- .mise/tasks/
- raw scripts only after inspection

Add `templates/justfile` to templates routing.
Keep `templates/mise.toml` as optional.

Add rules:
- Respect existing canonical runner first.
- Prefer justfile for lightweight new task catalogs.
- Use mise only for environment/tool-version-aware workflows or when already present.
- Treat uncataloged scripts as unknown safety.
- Do not run destructive scripts without explicit review.

Keep YAML valid.

## 10. Update templates/context-map.yaml

Apply the same project-generic routing changes as `context-map.yaml`.
Do not require `SKILL.md` in target projects.
Keep `CHANGELOG.md` authority routing.

## 11. Update templates/AGENTS-navigation-block.md

Update agent instructions:
- Before running project-local automation, inspect:
  - justfile
  - scripts/README.md
  - Taskfile.yml
  - Makefile
  - package.json
  - mise.toml / .mise/tasks/
- Prefer `just` when a justfile exists.
- Use mise only when the project uses mise.
- Treat uncataloged scripts as unknown safety.
- Read recent `CHANGELOG.md` before editing.

## 12. Update templates/repomix.config.json

Ensure Repomix includes:
- justfile
- Justfile
- scripts/README.md
- scripts/**
- Taskfile.yml
- Makefile
- package.json
- mise.toml
- .mise/tasks/**

Ensure generated/noise exclusions remain:
- .venv/**
- node_modules/**
- dist/**
- .ai-context/**
- graphify-out/**
- cache/runtime dirs

Keep JSON valid.

## 13. Update AGENTS.md

Update package-level agent instruction:
- `justfile` is the preferred lightweight new task catalog.
- Existing canonical task runners are respected.
- `mise.toml` remains optional for environment/tool-version-aware workflows.
- Before running automation, inspect task catalog and `scripts/README.md`.
- Do not run destructive/review-required/unknown tasks without review.

## 14. Update CLAUDE.md

If it is a thin wrapper pointing to `AGENTS.md`, leave it unchanged.
If it is a normal file, apply the same task-runner changes.

## 15. Update CHANGELOG.md

Append a new dated entry.

Include:
- Replaced mise-first script/task inventory strategy with just-preferred task-runner-neutral strategy.
- Added `templates/justfile`.
- Demoted `templates/mise.toml` to optional env/tool-version template.
- Updated README, ARCHITECTURE, SKILL, AGENTS, AI_NAVIGATION, context maps, templates, Repomix config.
- Preserved existing mise support where projects already use it.
- Clarified raw script safety and runner precedence.

Do not rewrite old changelog history.

## 16. Update SCRATCHPAD.md

If there is an open or stale item saying "decide whether mise/just is preferred" or similar, mark it resolved with:
- Decision: just preferred by default; mise optional for tool/env management.

Do not remove unrelated pending items.

## 17. Add/update validation

Run these checks from repository root:

python - <<'PY'
import pathlib, yaml
for f in ["context-map.yaml", "templates/context-map.yaml"]:
    p = pathlib.Path(f)
    yaml.safe_load(p.read_text())
    print(f"{f}: YAML OK")
PY

python - <<'PY'
import json, pathlib
p = pathlib.Path("templates/repomix.config.json")
json.loads(p.read_text())
print("templates/repomix.config.json: JSON OK")
PY

python - <<'PY'
import tomllib, pathlib
p = pathlib.Path("templates/mise.toml")
tomllib.loads(p.read_text())
print("templates/mise.toml: TOML OK")
PY

bash -n templates/context-preflight.sh

python - <<'PY'
import pathlib
required = [
    "README.md",
    "AGENTS.md",
    "CLAUDE.md",
    "SCRATCHPAD.md",
    "CHANGELOG.md",
    "ARCHITECTURE.md",
    "SKILL.md",
    "AI_NAVIGATION.md",
    "context-map.yaml",
    "templates/AI_NAVIGATION.md",
    "templates/AGENTS-navigation-block.md",
    "templates/context-map.yaml",
    "templates/repomix.config.json",
    "templates/justfile",
    "templates/mise.toml",
    "templates/scripts-README.md",
    "patterns/script-task-audit-checklist.md",
]
missing = [f for f in required if not pathlib.Path(f).exists()]
if missing:
    raise SystemExit("missing files: " + ", ".join(missing))
print("required files: OK")
PY

python - <<'PY'
import pathlib
checks = {
    "README.md": [
        "just",
        "justfile",
        "templates/justfile",
        "mise",
        "scripts/README.md",
        "unknown safety",
    ],
    "ARCHITECTURE.md": [
        "justfile",
        "mise.toml",
        "scripts/README.md",
        "task-runner",
    ],
    "SKILL.md": [
        "justfile",
        "Taskfile.yml",
        "Makefile",
        "package.json",
        "mise.toml",
        "unknown safety",
        "script/task inventory",
    ],
    "AI_NAVIGATION.md": [
        "justfile",
        "just --list",
        "scripts/README.md",
        "mise tasks",
        "Script and Task Navigation",
    ],
    "templates/AI_NAVIGATION.md": [
        "Before editing this project",
        "justfile",
        "scripts/README.md",
        "CHANGELOG.md",
    ],
    "context-map.yaml": [
        "justfile",
        "templates/justfile",
        "scripts/README.md",
        "mise.toml",
    ],
    "templates/context-map.yaml": [
        "justfile",
        "scripts/README.md",
        "mise.toml",
    ],
    "templates/scripts-README.md": [
        "just",
        "justfile",
        "scripts/README.md",
        "unknown",
        "destructive",
    ],
    "templates/justfile": [
        "inventory:",
        "audit-scripts:",
        "preflight:",
        "lint-md:",
    ],
    "CHANGELOG.md": [
        "just",
        "mise",
        "script/task",
    ],
}
for file, terms in checks.items():
    text = pathlib.Path(file).read_text(errors="ignore")
    missing = [t for t in terms if t not in text]
    if missing:
        raise SystemExit(f"{file} missing terms: {missing}")
print("required term checks: OK")
PY

## 18. Stale wording search

Search for stale mise-first wording:

grep -RniE "mise-first|mise.*preferred|preferred.*mise|canonical runnable task catalog.*mise|mise is initialized|mise tasks \\+ scripts/README.md" \
  README.md ARCHITECTURE.md SKILL.md AGENTS.md AI_NAVIGATION.md context-map.yaml templates patterns || true

If hits are intentional historical changelog entries, leave them.
If hits are live instructions, update them.

Also search for missing justfile coverage:

grep -Rni "justfile" README.md ARCHITECTURE.md SKILL.md AGENTS.md AI_NAVIGATION.md context-map.yaml templates patterns CHANGELOG.md

## 19. Output required

After implementation, report:

- Files changed.
- New files added.
- Exact high-level changes by file.
- Validation commands run and results.
- Stale mise-first references found and whether fixed or historical.
- Any assumptions.
- Any remaining unresolved issues.

Constraints:

- Do not remove mise support.
- Do not make just mandatory.
- Do not overwrite custom content wholesale.
- Do not refactor unrelated package logic.
- Preserve existing Archcore, Graphify, Repomix behavior.
- Keep target-project templates generic.
- Keep the patch repeat-safe.
# skill-ai-it — Replace mise with Just Only

You are working on the `skill-ai-it` repository.

Goal: replace the current mise-first script/task inventory strategy with a **just-only** script/task inventory strategy.

Important terminology:
- The previous implementation used `mise` as the preferred/default structured task catalog.
- The new strategy must use `just` as the only supported task catalog layer.
- Remove `mise` support from this skill package.
- Do not keep both `just` and `mise` in the skill strategy.
- The skill must still respect existing target-project task runners such as `Taskfile.yml`, `Makefile`, and `package.json` scripts, but it must not create, promote, document, or recommend `mise.toml` / `.mise/tasks/`.

Primary design decision:

Use this hierarchy:

1. Existing project task runner, if already canonical
2. `justfile` as the preferred and only new lightweight task catalog generated/proposed by `skill-ai-it`
3. `scripts/README.md` as the human/agent-readable operational catalog
4. Raw `scripts/` files as implementation only, unknown safety until inspected/cataloged
5. `Taskfile.yml` only if already present or explicitly chosen by the project
6. `Makefile` / `package.json` scripts respected when already established

Do not remove the script/task inventory capability.
Do not make `just` globally mandatory for every project.
Do not generate a `justfile` if no scripts/tasks/automation exist.
Do not create or recommend `mise.toml` or `.mise/tasks/`.
Do not invent runnable task behavior without inspecting scripts or receiving explicit project intent.

Required changes:

## 1. README.md

Update all mise-first and mise-optional wording.

Remove or replace these concepts wherever they appear:
- `mise` as preferred/default structured task catalog
- `mise.toml` as canonical runnable task catalog
- `.mise/tasks/` as supported task location
- `mise tasks`
- `mise run <task>`
- `templates/mise.toml`
- any wording saying mise remains optional

Replace with:
- Existing task runners are respected first.
- `justfile` is the preferred and only new runnable task catalog generated/proposed by this skill.
- `scripts/README.md` is the human/agent-readable script/task inventory.
- Raw scripts remain unknown safety until inspected or cataloged.
- `just` is optional per target project and only used/created when appropriate.
- `Taskfile.yml`, `Makefile`, and `package.json` scripts are respected when already established, but not replaced automatically.

Update the package layout tree:
- Add `templates/justfile`.
- Remove `templates/mise.toml` from the layout.
- Keep `templates/scripts-README.md`.
- Keep `patterns/script-task-audit-checklist.md`.

Update the Tool stack section:
- Replace `mise tasks` with `just`.
- Remove the separate `mise` tool entry if present.
- Ensure Graphify and Repomix remain support only.
- Ensure the intended authority order becomes:

```text
governed docs/source files
-> existing canonical task runner, or justfile for new lightweight catalogs
-> scripts/README.md
-> AI_NAVIGATION.md + context-map.yaml
-> Graphify / Repomix generated outputs
-> agent context loading
```

## 2. ARCHITECTURE.md

Update the `Script and Task Inventory Layer`.

Required wording:
- `justfile` = preferred and only generated/proposed lightweight executable task catalog.
- Existing canonical task runners must be respected first.
- `scripts/README.md` = operational explanation catalog.
- `Taskfile.yml`, `Makefile`, and `package.json` scripts are respected if already present.
- Graphify = relationship discovery only.
- Repomix = context packing only.
- Archcore = durable operational procedure promotion only.
- Raw scripts under `scripts/` are not automatically safe.
- Agents should prefer:
  1. existing canonical runner
  2. `just --list` / `just <task>` when a justfile exists
  3. `scripts/README.md`
  4. raw scripts only after inspection

Remove any architecture claim that `mise` is default, preferred, optional, supported, or retained.
Remove references to `mise.toml` and `.mise/tasks/`.

## 3. SKILL.md

Update orchestration logic.

Required behavior:

### Detection order

When detecting project automation, check in this order:

1. `justfile`
2. `Taskfile.yml`
3. `Makefile`
4. `package.json` scripts
5. `scripts/`
6. `.github/workflows/`
7. `ansible/`
8. `playbooks/`

Remove `mise.toml` and `.mise/tasks/` from detection order.

### Bootstrap behavior

- If an existing task runner exists, respect it.
- If no task runner exists but scripts/automation are present, prefer proposing or creating `justfile` as the lightweight task catalog.
- Create/update `scripts/README.md` when scripts/tasks/automation are present.
- Do not create `mise.toml`.
- Do not create `.mise/tasks/`.
- Do not mention mise as an option.
- Do not create empty task scaffolding if there are no scripts/tasks.

### Navigation-add behavior

- Add navigation pointers to existing runner first.
- If `justfile` exists, route agents to `just --list` and then `scripts/README.md`.
- Do not route agents to `mise tasks`.
- Do not mention `mise run`.

### Refresh behavior

- Update managed inventory blocks only.
- Preserve manually written script/task descriptions.
- If drift exists between justfile/tasks/scripts and `scripts/README.md`, report or propose updates.
- Do not silently convert existing target-project Taskfile/Makefile/package scripts to just.
- Do not introduce mise into target projects.

### Audit behavior

Report:
- scripts missing from `scripts/README.md`
- just recipes missing comments/descriptions
- cataloged scripts that no longer exist
- raw scripts not represented in any runner or `scripts/README.md`
- unsafe scripts without safety notes
- stale `mise` references in live governance, templates, README, navigation, context maps, or script inventory docs
- target projects using mise as existing local practice, but classify that as external/project-specific, not supported/generated by this skill

### Promote behavior

- Promote only durable operational procedures to Archcore.
- Do not promote every just recipe or script.

Update safety labels if needed. Keep:
- safe
- review-required
- destructive
- external-network
- modifies-files
- requires-secrets
- requires-credentials
- long-running
- unknown

Agents must treat `unknown` as not safe until inspected.

## 4. Add new template

Create:

```text
templates/justfile
```

Use this content:

```just
# just task catalog for this project.
# Purpose:
# - expose safe, documented project tasks to humans and AI agents
# - avoid agents running arbitrary scripts without context
# - keep runnable entrypoints simple and readable
#
# List tasks:
#   just --list
#
# Run task:
#   just <task>
#
# Safety:
# - Prefer safe/read-only tasks by default.
# - Mark destructive tasks clearly and require review.
# - Keep detailed inputs/outputs/safety notes in scripts/README.md.

set dotenv-load := false

# List available tasks and show script inventory when present
inventory:
    @just --list
    @test -f scripts/README.md && sed -n '1,220p' scripts/README.md || true

# Audit script/task inventory for obvious drift
audit-scripts:
    @echo "== just recipes =="
    @just --list || true
    @echo
    @echo "== script files =="
    @find scripts -maxdepth 2 -type f 2>/dev/null | sort || true
    @echo
    @echo "== uncataloged script candidates =="
    @if [ -d scripts ] && [ -f scripts/README.md ]; then \
      find scripts -maxdepth 2 -type f | sort | while read -r f; do \
        grep -Fq "$f" scripts/README.md || echo "$f"; \
      done; \
    fi

# Run safe local preflight checks
preflight: audit-scripts lint-md

# Lint Markdown files when markdownlint-cli2 is available
lint-md:
    @command -v markdownlint-cli2 >/dev/null && markdownlint-cli2 '**/*.md' || echo 'markdownlint-cli2 not installed; skipped'
```

Do not add project-specific recipes unless discovered from actual scripts or requested by user.

## 5. Update templates/scripts-README.md

Make it task-runner-neutral with `just` as the only generated/proposed new task catalog.

Update execution policy:
- Prefer the existing canonical task runner.
- Prefer `just <task>` when a `justfile` exists.
- Do not use `mise run <task>`.
- Do not document `mise` as a supported path.
- Do not run destructive/review-required/unknown scripts without review.
- Raw scripts remain unknown safety until inspected/cataloged.

Update preferred execution order:

1. Existing canonical task runner
2. `just --list` / `just <task>`
3. `scripts/README.md`
4. Other existing task runners: `Taskfile.yml`, `Makefile`, `package.json`
5. Raw scripts after inspection

Update inventory rows so examples use:
- `just inventory`
- `just audit-scripts`
- `just preflight`

Remove any examples using:
- `mise run ...`
- `mise tasks`
- `mise.toml`
- `.mise/tasks/`

Keep safety labels.

## 6. Remove templates/mise.toml

Delete or archive:

```text
templates/mise.toml
```

Preferred action:
- Move it to `docs/archive/templates/mise.toml` if archive policy prefers preserving old templates.
- Otherwise delete it.

After moving/deleting it:
- Remove it from README package layout.
- Remove it from AI_NAVIGATION.md.
- Remove it from context-map.yaml.
- Remove it from templates/context-map.yaml.
- Remove it from templates/repomix.config.json includes.
- Remove it from required-file validation checks.
- Remove it from any package consistency checklist.

## 7. Update AI_NAVIGATION.md

Update `## Script and Task Navigation`.

Required read/execution order:

1. Existing canonical runner if documented
2. `justfile`
3. `scripts/README.md`
4. `Taskfile.yml`
5. `Makefile`
6. `package.json`
7. raw scripts under `scripts/` after inspection

Required rules:
- Prefer `just --list` and `just <task>` when `justfile` exists.
- Do not use `mise tasks`.
- Do not use `mise run <task>`.
- Do not treat mise as default or optional.
- Do not run uncataloged scripts blindly.
- Stop for review on destructive/review-required/unknown tasks.

Update context map table:
- Add `templates/justfile`.
- Remove `templates/mise.toml`.
- Keep `templates/scripts-README.md`.
- Keep `patterns/script-task-audit-checklist.md`.

## 8. Update templates/AI_NAVIGATION.md

Make the same target-project-safe changes:
- project-generic wording
- no mandatory `SKILL.md`
- `justfile` preferred when present
- no mise references
- `scripts/README.md` remains operational catalog

## 9. Update context-map.yaml

Update script/task routing.

Ensure `scripts` and `automation` routes read:

- justfile
- scripts/README.md
- Taskfile.yml
- Makefile
- package.json
- raw scripts only after inspection

Add `templates/justfile` to templates routing.
Remove `templates/mise.toml` from templates routing.
Remove `mise.toml` and `.mise/tasks/` from script/automation routing.

Add rules:
- Respect existing canonical runner first.
- Prefer justfile for lightweight new task catalogs.
- Treat uncataloged scripts as unknown safety.
- Do not run destructive scripts without explicit review.

Keep YAML valid.

## 10. Update templates/context-map.yaml

Apply the same project-generic routing changes as `context-map.yaml`.
Do not require `SKILL.md` in target projects.
Keep `CHANGELOG.md` authority routing.
Remove all mise references.

## 11. Update templates/AGENTS-navigation-block.md

Update agent instructions:
- Before running project-local automation, inspect:
  - justfile
  - scripts/README.md
  - Taskfile.yml
  - Makefile
  - package.json
- Prefer `just` when a justfile exists.
- Treat uncataloged scripts as unknown safety.
- Read recent `CHANGELOG.md` before editing.

Remove mise references.

## 12. Update templates/repomix.config.json

Ensure Repomix includes:
- justfile
- Justfile
- scripts/README.md
- scripts/**
- Taskfile.yml
- Makefile
- package.json

Remove:
- mise.toml
- .mise/tasks/**

Ensure generated/noise exclusions remain:
- .venv/**
- node_modules/**
- dist/**
- .ai-context/**
- graphify-out/**
- cache/runtime dirs

Keep JSON valid.

## 13. Update AGENTS.md

Update package-level agent instruction:
- `justfile` is the preferred and only new lightweight task catalog generated/proposed by this skill.
- Existing canonical task runners are respected.
- Before running automation, inspect task catalog and `scripts/README.md`.
- Do not run destructive/review-required/unknown tasks without review.

Remove any mise references.

## 14. Update CLAUDE.md

If it is a thin wrapper pointing to `AGENTS.md`, leave it unchanged.
If it is a normal file, apply the same just-only task-runner changes and remove mise references.

## 15. Update CHANGELOG.md

Append a new dated entry.

Include:
- Replaced mise-first / mise-optional script/task inventory strategy with just-only task catalog strategy.
- Added `templates/justfile`.
- Removed or archived `templates/mise.toml`.
- Removed mise routing from README, ARCHITECTURE, SKILL, AGENTS, AI_NAVIGATION, context maps, templates, and Repomix config.
- Preserved respect for existing Taskfile/Makefile/package script runners.
- Clarified raw script safety and runner precedence.

Do not rewrite old changelog history.
Historical changelog entries may still mention mise as history.

## 16. Update SCRATCHPAD.md

If there is an open or stale item saying "decide whether mise/just is preferred" or similar, mark it resolved with:

```text
Decision: just-only for generated/proposed task catalogs; mise removed from this skill package.
```

Do not remove unrelated pending items.

## 17. Add/update validation

Run these checks from repository root:

```bash
python - <<'PY'
import pathlib, yaml
for f in ["context-map.yaml", "templates/context-map.yaml"]:
    p = pathlib.Path(f)
    yaml.safe_load(p.read_text())
    print(f"{f}: YAML OK")
PY
```

```bash
python - <<'PY'
import json, pathlib
p = pathlib.Path("templates/repomix.config.json")
json.loads(p.read_text())
print("templates/repomix.config.json: JSON OK")
PY
```

```bash
bash -n templates/context-preflight.sh
```

```bash
python - <<'PY'
import pathlib
required = [
    "README.md",
    "AGENTS.md",
    "CLAUDE.md",
    "SCRATCHPAD.md",
    "CHANGELOG.md",
    "ARCHITECTURE.md",
    "SKILL.md",
    "AI_NAVIGATION.md",
    "context-map.yaml",
    "templates/AI_NAVIGATION.md",
    "templates/AGENTS-navigation-block.md",
    "templates/context-map.yaml",
    "templates/repomix.config.json",
    "templates/justfile",
    "templates/scripts-README.md",
    "patterns/script-task-audit-checklist.md",
]
missing = [f for f in required if not pathlib.Path(f).exists()]
if missing:
    raise SystemExit("missing files: " + ", ".join(missing))
print("required files: OK")
PY
```

```bash
python - <<'PY'
import pathlib
forbidden_existing = [
    "templates/mise.toml",
]
existing = [f for f in forbidden_existing if pathlib.Path(f).exists()]
if existing:
    raise SystemExit("forbidden files still present: " + ", ".join(existing))
print("forbidden active mise template files: OK")
PY
```

```bash
python - <<'PY'
import pathlib
checks = {
    "README.md": [
        "just",
        "justfile",
        "templates/justfile",
        "scripts/README.md",
        "unknown safety",
    ],
    "ARCHITECTURE.md": [
        "justfile",
        "scripts/README.md",
        "task-runner",
    ],
    "SKILL.md": [
        "justfile",
        "Taskfile.yml",
        "Makefile",
        "package.json",
        "unknown safety",
        "script/task inventory",
    ],
    "AI_NAVIGATION.md": [
        "justfile",
        "just --list",
        "scripts/README.md",
        "Script and Task Navigation",
    ],
    "templates/AI_NAVIGATION.md": [
        "Before editing this project",
        "justfile",
        "scripts/README.md",
        "CHANGELOG.md",
    ],
    "context-map.yaml": [
        "justfile",
        "templates/justfile",
        "scripts/README.md",
    ],
    "templates/context-map.yaml": [
        "justfile",
        "scripts/README.md",
    ],
    "templates/scripts-README.md": [
        "just",
        "justfile",
        "scripts/README.md",
        "unknown",
        "destructive",
    ],
    "templates/justfile": [
        "inventory:",
        "audit-scripts:",
        "preflight:",
        "lint-md:",
    ],
    "CHANGELOG.md": [
        "just",
        "script/task",
    ],
}
for file, terms in checks.items():
    text = pathlib.Path(file).read_text(errors="ignore")
    missing = [t for t in terms if t not in text]
    if missing:
        raise SystemExit(f"{file} missing terms: {missing}")
print("required term checks: OK")
PY
```

## 18. Stale mise wording search

Search for stale mise wording in live/current instruction surfaces:

```bash
grep -RniE "mise|mise\.toml|\.mise/tasks|mise tasks|mise run" \
  README.md ARCHITECTURE.md SKILL.md AGENTS.md AI_NAVIGATION.md context-map.yaml templates patterns || true
```

Expected result:
- No hits in live/current instruction surfaces.
- Historical hits in CHANGELOG.md or docs/archive are allowed.

If hits appear in live instruction files, fix them.

Also search for justfile coverage:

```bash
grep -Rni "justfile" README.md ARCHITECTURE.md SKILL.md AGENTS.md AI_NAVIGATION.md context-map.yaml templates patterns CHANGELOG.md
```

## 19. Output required

After implementation, report:

- Files changed.
- New files added.
- Files deleted or archived.
- Exact high-level changes by file.
- Validation commands run and results.
- Stale mise references found and whether fixed or historical.
- Any assumptions.
- Any remaining unresolved issues.

Constraints:

- Remove mise support from this skill package.
- Do not make just globally mandatory for all target projects.
- Do not overwrite custom content wholesale.
- Do not refactor unrelated package logic.
- Preserve existing Archcore, Graphify, Repomix behavior.
- Keep target-project templates generic.
- Keep the patch repeat-safe.