---
Title: skill-ai-it reference: Conditional support files
Category: reference
Status: current
Authority: local-supplement
Scope: On-need reference moved verbatim from SKILL.md
Last reviewed: 2026-10-10
Summary: >-
  Conditional support files; moved verbatim from SKILL.md so SKILL.md stays an orchestration file within budget.
---

# skill-ai-it reference: Conditional support files

Moved verbatim from `SKILL.md` on 2026-10-10 to keep that file within its budget for files loaded whole.

## Contents

- [repomix.config.json — create when: project has multiple governance/docs/code files and Repomix is part of the navigation stack](#repomixconfigjson--create-when-project-has-multiple-governancedocscode-files-and-repomix-is-part-of-the-navigation-stack)
- [scripts/context_preflight.sh — optional local artifact, explicit request only](#scriptscontext_preflightsh--optional-local-artifact-explicit-request-only)
- [.graphifyignore or .graphifyignore.sample — create when: Graphify is part of the navigation stack and no ignore file exists](#graphifyignore-or-graphifyignoresample--create-when-graphify-is-part-of-the-navigation-stack-and-no-ignore-file-exists)
- [memory-bank/ structure — create when: project is long-running, conceptual, planning-heavy, or user asks for persistent working context](#memory-bank-structure--create-when-project-is-long-running-conceptual-planning-heavy-or-user-asks-for-persistent-working-context)
- [scripts/README.md — create when: scripts, tasks, or automation are present, or when script inventory is explicitly requested](#scriptsreadmemd--create-when-scripts-tasks-or-automation-are-present-or-when-script-inventory-is-explicitly-requested)
- [Optional/generated support files](#optionalgenerated-support-files)

#### repomix.config.json — create when: project has multiple governance/docs/code files and Repomix is part of the navigation stack

If present, merge missing includes/ignores only.

Preferred source template: `templates/repomix.config.json`.

```json
{
  "output": {
    "filePath": ".ai-context/governance-pack.md",
    "style": "markdown"
  },
  "include": [
    "AGENTS.md",
    "CLAUDE.md",
    "AI_NAVIGATION.md",
    "README.md",
    "ARCHITECTURE.md",
    "architecture.md",
    "CONVENTIONS.md",
    "ROADMAP.md",
    "roadmap.md",
    "SCRATCHPAD.md",
    "CHANGELOG.md",
    "context-map.yaml",
    "scripts/README.md",
    "scripts/**",
    "justfile",
    "Taskfile.yml",
    "Makefile",
    "package.json",
    "memory-bank/**/*.md",
    ".archcore/**/*.md",
    "docs/**/*.md"
  ],
  "ignore": {
    "customPatterns": [
      "node_modules/**",
      ".git/**",
      "dist/**",
      "build/**",
      "cache/**",
      "runtime/**",
      "__pycache__/**",
      ".venv/**",
      "graphify-out/**",
      ".ai-context/**"
    ]
  }
}
```

#### scripts/context_preflight.sh — optional local artifact, explicit request only

Do not create a repo-local preflight script during normal bootstrap, navigation-add, or refresh runs. The skill package is the maintained source for generic validation/preflight behavior.

Create `scripts/context_preflight.sh` only when the user explicitly asks for a repo-local command or when the target project already has one and the user asks to refresh it. If the file exists, audit
it for drift and propose changes instead of treating it as the source of truth.

Preferred opt-in source template: `templates/context_preflight.sh`.

```bash
#!/usr/bin/env bash
set -euo pipefail

mkdir -p .ai-context

echo "[1/5] Checking governance files..."
for f in AGENTS.md AI_NAVIGATION.md context-map.yaml CHANGELOG.md; do
  if [ ! -f "$f" ]; then
    echo "WARN: missing $f"
  fi
done

echo "[2/5] Checking Archcore..."
if command -v archcore >/dev/null 2>&1; then
  if [ -d ".archcore" ]; then
    archcore status || archcore doctor || true
  else
    archcore init
    archcore status || archcore doctor || true
  fi
else
  echo "INFO: archcore CLI not found; skipping"
fi

echo "[3/5] Running Graphify..."
if [ "${GRAPHIFY_ENABLED:-0}" != 1 ]; then
  echo "INFO: Graphify disabled (operator, 2026-10-10); set GRAPHIFY_ENABLED=1 to run"
elif command -v graphify >/dev/null 2>&1; then
  if [ -f "graphify-out/graph.json" ]; then
    graphify update . || true
  elif graphify update . >/dev/null 2>&1; then
    graphify update . || true
  else
    echo "INFO: graphify CLI found, but this project is not initialized for graph updates"
    echo "INFO: run the project-specific Graphify bootstrap command before expecting graph output"
  fi
else
  echo "INFO: graphify CLI not found; skipping"
fi

echo "[4/5] Building Repomix governance pack..."
if command -v repomix >/dev/null 2>&1; then
  repomix --config repomix.config.json || true
else
  echo "INFO: repomix CLI not found; skipping"
fi

echo "[5/5] Context preflight complete."
```

#### .graphifyignore or .graphifyignore.sample — create when: Graphify is part of the navigation stack and no ignore file exists

Prefer `.graphifyignore.sample` unless the user asks to enforce it.

```gitignore
.git/
node_modules/
.venv/
dist/
build/
__pycache__/
.ai-context/
*.log
```

#### memory-bank/ structure — create when: project is long-running, conceptual, planning-heavy, or user asks for persistent working context

Create only missing files. Do not overwrite existing memory-bank files.

| File                            | Purpose                                           |
| ------------------------------- | ------------------------------------------------- |
| `memory-bank/activeContext.md`  | Current working context and immediate focus       |
| `memory-bank/progress.md`       | Current status, completed work, next actions      |
| `memory-bank/decisionLog.md`    | Decision notes before promotion into Archcore/ADR |
| `memory-bank/systemPatterns.md` | Stable architecture/workflow patterns             |
| `memory-bank/openQuestions.md`  | Questions blocking decisions                      |

#### scripts/README.md — create when: scripts, tasks, or automation are present, or when script inventory is explicitly requested

Preferred source template: `templates/scripts-README.md`.

Create or update `scripts/README.md` from the template. Populate entries for each discovered script or task runner entry. Do not create an empty `scripts/README.md` if no scripts or tasks exist.

**Only "Execution Policy" / "Preferred Execution Order" / "Maintenance Rules" belong inside the `skill-ai-it:scripts` managed block** — that is the exact content
`upgrade_navigation_control_layer.py`'s `build_scripts_block()` regenerates. "Runtimes", "Task Inventory", "Raw Script Inventory", "Safety Labels", and "Notes" are project-specific and must sit
OUTSIDE the markers (the template already places them there). Nesting them inside the managed block, as the template did until 2026-09-18, means the next `nav_upgrade` silently discards them — the
upgrader reports `replaced-managed-block` and that reads like success.

### Optional/generated support files

These are created only on explicit user request or generated by supporting tools. They are not created automatically and are not canonical truth.

| Path                           | Source                                                      | Notes                                         |
| ------------------------------ | ----------------------------------------------------------- | --------------------------------------------- |
| `scripts/context_preflight.sh` | Explicit request only; use `templates/context_preflight.sh` | Local opt-in preflight entrypoint             |
| `graphify-out/`                | Graphify CLI                                                | Generated, rebuildable; not canonical truth   |
| `.ai-context/`                 | Repomix CLI                                                 | Generated context bundle; not canonical truth |
| `docs/` audit reports          | skill-ai-it audit mode                                      | Per-run findings                              |
| `docs/archive/`                | Manual archiving                                            | One-time artifacts no longer needed in root   |

See the `#### scripts/context_preflight.sh` section above under Conditionally-created files for the full template content and generation policy.
