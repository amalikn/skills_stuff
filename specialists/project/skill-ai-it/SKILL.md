---
name: skill-ai-it
description: "Bootstraps/refreshes a folder's AI governance docs when onboarding a project."
metadata:
  short-description: Bootstrap and maintain AI governance/navigation files from folder content analysis
---

# skill-ai-it — AI Governance + Navigation Bootstrap

## Contents

- [Use When](#use-when)
- [Inputs](#inputs)
- [Operating Modes](#operating-modes)
- [Repeat-Safety Contract](#repeat-safety-contract)
- [Phase 4 — Generate Files](#phase-4--generate-files)
- [Workflow: Applying This Skill to a Project](#workflow-applying-this-skill-to-a-project)

---

Detail lives in one file per topic under [references/](references/readme.md), linked at the step that needs it; open only the one the task needs.

Shipped templates: `templates/AI_NAVIGATION.md`, `templates/AGENTS-navigation-block.md`, `templates/AGENTS-governance-checks-block.md`,
`templates/check_governance.py`, `templates/govcheck/`, `templates/justfile`, `templates/scripts-README.md`, `templates/context-map.yaml`,
`templates/update_rules.yaml`, `templates/repomix.config.json`, `templates/context_preflight.sh`. Patterns: `patterns/archcore-routing.md`,
`patterns/drift-audit.md`, `patterns/memory-bank-structure.md`, `patterns/navigation-control-automation.md`, `patterns/script-task-audit-checklist.md`,
`patterns/governance-checks.md`, `patterns/navigation/`.

## Use When

- Setting up a new project folder that has no README.md / AGENTS.md / CLAUDE.md
- Onboarding an existing folder into the governance stack
- Adding AI navigation/context-routing support to an existing project
- Refreshing governance files and CHANGELOG.md after the project has evolved
- Auditing whether AI agents can find the right project context
- Promoting durable content from scratchpad/memory/docs into navigation, ADR, rule, spec, or roadmap structures
- Bootstrapping a child project under `apn/`, `project_stuff/`, or any managed workspace
- Creating a new skill or specialist pack, or any folder that gets scripts or a task runner — **before its first commit**, even when it already has an `AGENTS.md` copied from a sibling
  (skill-mikrotik, 2026-10-07, was built by hand and shipped with shebang-run recipes and bare `python3` until the operator caught it)
- User says "set up the AI files for this folder", "bootstrap this project", "add AI navigation", "refresh the governance", "audit project context", or invokes `/skill-ai-it`

**Do not invoke** for destructive rewrites. This skill is repeat-safe by design: if governance files already exist, audit and update only missing or stale sections unless the user explicitly requests
regeneration.

---

## Inputs

| Input                | How to obtain                                                        |
| -------------------- | -------------------------------------------------------------------- |
| Target folder path   | Explicit argument, current working directory, or IDE open file       |
| Project context hint | Optional — user may supply a one-liner; otherwise infer from content |

---

## Operating Modes

Determine the mode before editing. If the user does not specify a mode, infer it from existing files and requested action.

| Mode             | Trigger                                               | Behaviour                                                                                                                 |
| ---------------- | ----------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------- |
| `bootstrap`      | New or lightly populated folder                       | Create the base governance scaffold and conditional project files.                                                        |
| `navigation-add` | Existing project lacks `AI_NAVIGATION.md`             | Add the AI navigation starter module and wire it into AGENTS/CLAUDE/README. Where managed blocks already exist, run the   |
|                  |   or `context-map.yaml`                               |   deterministic upgrade sequence rather than hand-editing them.                                                           |
| `refresh`        | Existing governance files are present                 | **Run the deterministic upgrade sequence FIRST** (see [Deterministic Navigation-Control Automation](references/navigation-automation.md#deterministic-navigation-control-automation)) — it rewrites managed |
|                  |                                                       |   blocks, restamps the version, and adds missing `context-map.yaml` keys mechanically. Only then re-scan content, update  |
|                  |                                                       |   routing/index sections, append missing blocks, and preserve custom content by hand.                                     |
| `audit`          | User asks whether context                             | Report missing files, stale sections, routing gaps, drift, and proposed fixes. Do not edit unless requested.              |
|                  |   is complete/stale/conflicting                       |                                                                                                                           |
| `promote`        | User authorizes promotion from                        | Write or propose `.archcore/` content files (adr, rules, specs, guides, plans). Only mode that creates `.archcore/`       |
|                  |   `ARCHCORE_PROMOTION_CANDIDATES.md` or explicitly    |   content. Do not silently promote.                                                                                       |
|                  |   requests durable promotion                          |                                                                                                                           |

### Mode selection rules

- If `README.md`, `AGENTS.md`, and `CLAUDE.md` are missing: use `bootstrap`.
- If base governance exists but `AI_NAVIGATION.md` or `context-map.yaml` is missing: use `navigation-add`.
- If navigation files exist and the user asks to update context: use `refresh`.
- If the user asks what is wrong, missing, stale, or why agents get lost: use `audit`.
- If the user asks to turn notes/decisions into durable project truth: use `promote`.
- If uncertain, run `audit` first and propose the smallest safe update.

---

## Repeat-Safety Contract

This skill must be safe to run many times on the same project.

1. Never overwrite an existing governance file wholesale unless the user explicitly asks for regeneration.
2. Preserve user-authored sections, comments, and local conventions.
3. Add missing sections by heading anchor; update managed blocks only.
4. Prefer `.proposed` files for risky YAML/JSON rewrites.
5. Treat `SCRATCHPAD.md` content marked `KEEP` as protected.
6. Treat `CHANGELOG.md` as the durable project history/governance-change ledger; append entries rather than rewriting historical entries.
7. If the `archcore` CLI is available and `.archcore/` is missing, initialize it with `archcore init` during `bootstrap`, `navigation-add`, or `refresh`; after initialization, treat `.archcore/` as
   structured durable truth.

8. Propose Archcore content changes rather than directly editing Archcore files unless the user explicitly authorizes the content change. `archcore init` itself is allowed when the CLI is available.
9. Run Repomix when its CLI is available. **Graphify is disabled (operator, 2026-10-10)**: do not run it in any mode (see [Graphify initialization and refresh](references/generation-policy.md#graphify-initialization-and-refresh)).
   Treat their outputs (`graphify-out/`, `.ai-context/`, `repomix-output.md`) as disposable support, not canonical truth.
10. On conflict, stop and report the conflict instead of merging assumptions silently.
11. Always report created, updated, skipped, and proposed files separately.

- Read [references/managed-blocks.md](references/managed-blocks.md) before that work (moved verbatim from here): Managed block pattern.

- Read [references/package-layout.md](references/package-layout.md) before that work (moved verbatim from here): Skill Package Layout.

- Read [references/phases-1-3.md](references/phases-1-3.md) before that work (moved verbatim from here): Phase 1 — Inventory; Phase 2 — Understand; Phase 3 — Infer.

## Phase 4 — Generate Files

- Read [references/generation-policy.md](references/generation-policy.md) before that work (moved verbatim from here): File creation/update policy; Markdown quality rules; Archcore initialization and
  promotion candidate reporting; Graphify initialization and refresh; Repomix initialization and refresh.

### Governed files: headers, budgets, rotation and the checker's shape (operator, 2026-10-10)

- **Headers.** Every governed file states its purpose in its type's native header (governance `naming-and-file-summary-guide.md`, "File headers"); `scripts/file_headers.py` reads them all, and `just
  docs <folder>` is the triage view agents use before opening files.
- **Budget.** A file an agent loads whole (AGENTS.md, CLAUDE.md, AI_NAVIGATION.md, SCRATCHPAD.md, CHANGELOG.md, SKILL.md, MEMORY.md) stays within 200 lines and 25 KB for every agent;
  `doc_freshness.py` holds older ones as a shrink-only ratchet. Area rules go in a file read before that work.
- **Rotation.** `just budget --apply` (`scripts/budget_plan.py`): normalise, rotate to `docs/history/`, move non-working-state sections out, audit, `just check`; it names what still holds a file over
  (unfinished, never reported done). Recall `just history <term>`. Pin with `` `PIN` `` or `<!-- PIN -->`.
- **Checker shape.** A project's checker follows `patterns/governance-checks.md` "Structure and growth": entry point, `govcheck/core.py` (this skill's `templates/govcheck/core.py`, identical
  everywhere), `config.py`, `helpers.py`, `checks/<family>.py`, and the `structure` family (`templates/govcheck/checks/structure.py`) policing it. A single-file checker over 800 lines is split with
  `scripts/split_checker.py` at its next change; new projects start in the package layout.

### Document freshness (operator, 2026-10-10)

Every governed project runs `scripts/doc_freshness.py` from this skill (not a copy): `just check` with `--check`, `just stale` to list. Rules, from the front-matter standard in governance
`categories/naming-and-file-summary-guide.md` (freshness keys): a living document past `Review by` (default `Last reviewed` + 30 days; reports, reviews, audits and sources never expire), a
`superseded` file outside `archive/`, a `Depends on` file committed after `Last reviewed`.

- `bootstrap`, `navigation-add`, `refresh`: `scripts/adopt_governed_files.py --project-root . --apply` (recipes incl. `check`, record keys, baseline), then `just stale`; add `just stale` to the
  `AGENTS.md` preflight (outside the managed block).
- `audit`: run `just stale` and report the counts per rule; also report whether the project's LLM wiki page (`/Volumes/Data/_ai/_wiki/wiki_stuff/projects/<folder>.md`) exists and is older than the
  project's newest CHANGELOG entry.
- Prefer fixing over baselining: date an undated living document from its content, move a superseded file to `archive/` (update links and the folder index in the same pass).

---

- Read [references/script-task-inventory.md](references/script-task-inventory.md) before that work (moved verbatim from here): Script and task inventory.

- Read [references/governance-checker.md](references/governance-checker.md) before that work (moved verbatim from here): Governance coherence checker.

### Always-created files

- Read [references/files-readme-agents-claude.md](references/files-readme-agents-claude.md) before that work (moved verbatim from here): README.md; AGENTS.md; CLAUDE.md.

- Read [references/files-records.md](references/files-records.md) before that work (moved verbatim from here): SCRATCHPAD.md; CHANGELOG.md; .markdownlint-cli2.jsonc.

### Conditionally-created files

The files in this section are created only when their specific detection condition is met. State the reason for each conditional file in the audit output.

- Read [references/files-architecture-conventions-roadmap.md](references/files-architecture-conventions-roadmap.md) before that work (moved verbatim from here): ARCHITECTURE.md — create when: code,
  infrastructure, or design decisions are present, or user requests architecture documentation; CONVENTIONS.md — create when: code files present, naming patterns exist, or style/linting rules are
  discoverable; ROADMAP.md — create when: active development, TODOs present, migration/phase structure, or incomplete features detected.

- Read [references/files-ai-navigation.md](references/files-ai-navigation.md) before that work (moved verbatim from here): AI_NAVIGATION.md — create when: missing during `navigation-add`, requested
  explicitly, or project has more than one governance/context source.

- Read [references/files-context-map.md](references/files-context-map.md) before that work (moved verbatim from here): context-map.yaml — create when: `AI_NAVIGATION.md` is created or already exists
  but no machine-readable routing map exists.

- Read [references/files-support.md](references/files-support.md) before that work (moved verbatim from here): repomix.config.json — create when: project has multiple governance/docs/code files and
  Repomix is part of the navigation stack; scripts/context_preflight.sh — optional local artifact, explicit request only; .graphifyignore or .graphifyignore.sample — create when: Graphify is part of
  the navigation stack and no ignore file exists; memory-bank/ structure — create when: project is long-running, conceptual, planning-heavy, or user asks for persistent working context;
  scripts/README.md — create when: scripts, tasks, or automation are present, or when script inventory is explicitly requested; Optional/generated support files.

- Read [references/finishing.md](references/finishing.md) before that work (moved verbatim from here): Phase 5 — Update Parent; Conventions Baked In; Quality Check Before Completing; Audit Output
  Format.

- Read [references/compaction-recovery.md](references/compaction-recovery.md) before that work (moved verbatim from here): Context Compaction Recovery.

## Workflow: Applying This Skill to a Project

When running this skill against a target project, follow this order:

1. **Read existing governance files** — scan README.md, AGENTS.md, CLAUDE.md, AI_NAVIGATION.md, context-map.yaml, CHANGELOG.md.
2. **Detect current skill-generated block versions** — check managed block version strings for upgrade needs.
3. **Detect project-specific customizations** — identify user-authored sections outside managed blocks. Preserve them.
4. **Read `context-map.yaml`** before any file edits — it defines the machine-readable routing map.
5. **Check companion-file update rules** — `context-map.yaml update_rules` tells you what must be updated together.
6. **Generate proposed updates in memory** — plan all changes before writing any file.
7. **Apply only safe managed-block updates** — replace content inside matching managed blocks. Do not duplicate.
8. **Create `.proposed` files** for risky YAML/JSON changes or ambiguous merges.
9. **Regenerate generated outputs** only when requested or when clearly stale. Outputs remain support-only.
10. **Run validation** — verify no duplicate blocks, no stale references, no contradictions.
11. **Append `CHANGELOG.md`** only for durable governance/navigation changes.
12. **Report result** — created, updated, skipped, proposed, drift/conflicts.

Generated outputs (`graphify-out/`, `.ai-context/`) are support artifacts only and are never automatically promoted to canonical truth.

- Read [references/navigation-automation.md](references/navigation-automation.md) before that work (moved verbatim from here): Deterministic Navigation-Control Automation.

- Read [references/background.md](references/background.md) before that work (moved verbatim from here): Public Pattern Inspiration; Required Follow-Up Packaging Task.

- Read [references/pitfalls.md](references/pitfalls.md) before that work (moved verbatim from here): Pitfalls observed in practice.
