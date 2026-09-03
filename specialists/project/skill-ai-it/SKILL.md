---
name: skill-ai-it
description: >
  Analyzes a folder's existing content and bootstraps or refreshes AI
  governance, navigation, and context-routing files tailored to what it finds.
  Creates README.md, AGENTS.md, CLAUDE.md, SCRATCHPAD.md, and CHANGELOG.md
  always during bootstrap; creates ARCHITECTURE.md, CONVENTIONS.md, ROADMAP.md,
  AI_NAVIGATION.md, context-map.yaml, repomix.config.json, optional script/task
  inventory files, and local preflight scripts only when explicitly requested. Supports safe
  repeat runs that audit, append, refresh, or propose changes without
  overwriting existing governance content. Updates parent folder index and
  routing rules. Invoke when setting up a new project folder, onboarding an
  existing folder into the AI governance stack, adding AI navigation support,
  refreshing context routing, or bootstrapping child projects under apn/ or
  project_stuff/.
metadata:
  short-description: Bootstrap and maintain AI governance/navigation files from folder content analysis
---

# skill-ai-it — AI Governance + Navigation Bootstrap

## Contents

- [Use When](#use-when)
- [Inputs](#inputs)
- [Operating Modes](#operating-modes)
- [Repeat-Safety Contract](#repeat-safety-contract)
- [Skill Package Layout](#skill-package-layout)
- [Phase 1 — Inventory](#phase-1-inventory)
- [Phase 2 — Understand](#phase-2-understand)
- [Phase 3 — Infer](#phase-3-infer)
- [Phase 4 — Generate Files](#phase-4-generate-files)
- [Phase 5 — Update Parent](#phase-5-update-parent)
- [Conventions Baked In](#conventions-baked-in)
- [Quality Check Before Completing](#quality-check-before-completing)
- [Context Compaction Recovery](#context-compaction-recovery)
- [Workflow: Applying This Skill to a Project](#workflow-applying-this-skill-to-a-project)
- [Deterministic Navigation-Control Automation](#deterministic-navigation-control-automation)
- [Audit Output Format](#audit-output-format)
- [Public Pattern Inspiration](#public-pattern-inspiration)
- [Required Follow-Up Packaging Task](#required-follow-up-packaging-task)

---

## Use When

- Setting up a new project folder that has no README.md / AGENTS.md / CLAUDE.md
- Onboarding an existing folder into the governance stack
- Adding AI navigation/context-routing support to an existing project
- Refreshing governance files and CHANGELOG.md after the project has evolved
- Auditing whether AI agents can find the right project context
- Promoting durable content from scratchpad/memory/docs into navigation, ADR, rule, spec, or roadmap structures
- Bootstrapping a child project under `apn/`, `project_stuff/`, or any managed workspace
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

| Mode             | Trigger                                      | Behaviour                                                                                                                          |
| ---------------- | -------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| `bootstrap`      | New or lightly populated folder              | Create the base governance scaffold and conditional project files.                                                                 |
| `navigation-add` | Existing project lacks `AI_NAVIGATION.md` or | Add the AI navigation starter module and wire it into AGENTS/CLAUDE/README. Where managed blocks already exist, run the            |
|                  |   `context-map.yaml`                         |   deterministic upgrade sequence rather than hand-editing them.                                                                    |
| `refresh`        | Existing governance files are present        | **Run the deterministic upgrade sequence FIRST** (see                                                                              |
|                  |                                              |   [Deterministic Navigation-Control Automation](#deterministic-navigation-control-automation)) — it rewrites managed blocks,       |
|                  |                                              |   restamps the version, and adds missing `context-map.yaml` keys mechanically. Only then re-scan content, update routing/index     |
|                  |                                              |   sections, append missing blocks, and preserve custom content by hand.                                                            |
| `audit`          | User asks whether context is                 | Report missing files, stale sections, routing gaps, drift, and proposed fixes. Do not edit unless requested.                       |
|                  |   complete/stale/conflicting                 |                                                                                                                                    |
| `promote`        | User authorizes promotion from               | Write or propose `.archcore/` content files (adr, rules, specs, guides, plans). Only mode that creates `.archcore/` content. Do    |
|                  |   `ARCHCORE_PROMOTION_CANDIDATES.md` or      |   not silently promote.                                                                                                            |
|                  |   explicitly requests durable promotion      |                                                                                                                                    |

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
9. Run Graphify and Repomix when their CLIs are available; treat their outputs (`graphify-out/`, `.ai-context/`, `repomix-output.md`) as disposable support, not canonical truth.
10. On conflict, stop and report the conflict instead of merging assumptions silently.
11. Always report created, updated, skipped, and proposed files separately.

### Managed block pattern

When adding repeat-refreshable content into existing files, wrap it with comments using the standard format:

```markdown
<!-- BEGIN MANAGED: skill-ai-it:<section-name> -->
<!-- skill-ai-it-version: 2026-08-11-governance-checks-layer-v1 -->
...managed content...
<!-- END MANAGED: skill-ai-it:<section-name> -->
```

- `<section-name>` describes the managed section (e.g. `navigation`, `scripts`).

#### The upgrader will not overwrite project-authored content

Two guards, added 2026-08-12 after a dry run against a real project would have removed **222 lines** from its `AI_NAVIGATION.md` — every supersession chain, every gate reference and the whole
domain-routing table — reporting only `replaced-old-block`, which reads like a successful migration.

1. **Provenance.** A block this skill wrote carries a `skill-ai-it-version:` line. A block **without** one was either never written by the skill or has been hand-edited since, so the upgrader
   **refuses to replace it**, writes the generic block to `<file>.proposed-<section>-block`, and flags the run for manual review. Note the original bug was worse than "replaces managed blocks": the
   old-style-marker branch is tested **first** and matches preferentially, so legacy markers were the *most* exposed, not the least.
2. **Explicit opt-out.** A project that has deliberately taken ownership declares it inside the block:

   ```markdown
   <!-- BEGIN skill-ai-it:navigation -->
   <!-- skill-ai-it:manual reason="project-authored routing rules" -->
   ```

The upgrader then never touches that block — including **never inserting** the section if it is absent, because a file that declares itself project-managed and omits a section has decided it does not
want it. The validator reports it as a pass, not a missing-block failure. `--force` overrides both guards and **discards** the current contents; it exists for the case where you have read the
`.proposed` file and decided against your own content.

**Why the opt-out matters as much as the guard.** Without it, a project that has legitimately diverged is permanently red in the validator. A validator that always fails is one nobody reads, and the
next *real* failure goes unnoticed with it. "Expected failures" is not a stable state — it is a slow way of turning the check off.

**Both constants are restated in both scripts on purpose** (`MANUAL_TOKEN`, `VERSION_MARKER`). Drift between them would let the upgrader skip a block the validator still fails, which is the worst of
both.
- The version line must be the first comment inside the managed block.
- On repeat runs, replace only content inside the matching managed block.
- If a block is absent, append it under the most relevant existing heading.
- If a block exists with an older version string, upgrade it in place. Do not duplicate.

---

## Skill Package Layout

This skill is expected to be packaged with reusable template and pattern files. The embedded examples in this `SKILL.md` are fallback/reference content only; when the files below exist, use them as
the source for generated content.

```text
skill-ai-it/
├── SKILL.md
├── README.md
├── AGENTS.md
├── CLAUDE.md
├── AI_NAVIGATION.md
├── context-map.yaml
├── CHANGELOG.md
├── ARCHITECTURE.md
├── templates/
│   ├── AI_NAVIGATION.md
│   ├── context-map.yaml
│   ├── repomix.config.json
│   ├── AGENTS-navigation-block.md
│   ├── AGENTS-governance-checks-block.md
│   ├── scripts-README.md
│   ├── check_governance.py
│   └── context-preflight.sh
└── patterns/
    ├── archcore-routing.md
    ├── memory-bank-structure.md
    ├── drift-audit.md
    ├── governance-checks.md
    └── script-task-audit-checklist.md
```

### Template precedence

1. Prefer files under `templates/` for generated project files.
2. Prefer files under `patterns/` for optional guidance modules.
3. Use embedded examples in this `SKILL.md` only when the separate template/pattern files are missing.
4. If a template file and embedded example disagree, the external template file wins.
5. On repeat runs, never overwrite target project files wholesale; apply managed blocks or write `.proposed` files as defined in the Repeat-Safety Contract.

---

## Phase 1 — Inventory

1. List the target folder's contents 3 levels deep (files and subdirectories), excluding heavy/generated folders such as `.git`, `node_modules`, `.venv`, `dist`, `build`, `__pycache__`, `.ai-context`,
   and `graphify-out` unless the user asks to inspect them.
2. Classify what you find:

| Signal                                                                                                 | Inference                                                                             |
| ------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------- |
| `.py`, `.ts`, `.js`, `.go`, `.rb`, `.rs`, `.java` files                                                | Code project                                                                          |
| `docker-compose.yml`, `Dockerfile`, `Makefile`, `*.tf`                                                 | Infrastructure / ops                                                                  |
| `*.eml`, `communications/` folder                                                                      | Communications tracking                                                               |
| `*.md` files only, no code                                                                             | Docs / knowledge base                                                                 |
| Mix of the above                                                                                       | Mixed project                                                                         |
| `AI_NAVIGATION.md`, `context-map.yaml`                                                                 | AI navigation module already present                                                  |
| `.archcore/`                                                                                           | Structured durable project truth present                                              |
| `archcore` CLI available and `.archcore/` missing                                                      | Initialize `.archcore/` with `archcore init` in bootstrap/navigation-add/refresh mode |
| `justfile`, `Justfile`                                                                                 | just task catalog present — preferred lightweight runnable task catalog               |
| `scripts/`, `Makefile`, `Taskfile.yml`, `justfile`, `package.json` scripts, or common automation files | Script/task inventory useful; create or refresh `scripts/README.md`                   |
| `memory-bank/`                                                                                         | Memory Bank-style project memory present                                              |
| `graphify-out/`, `.ai-context/`                                                                        | Generated AI context/navigation artifacts present                                     |
| `repomix.config.json`                                                                                  | Deterministic context-pack config present                                             |
| `README.md` exists                                                                                     | Read it first before generating                                                       |
| `CHANGELOG.md` exists                                                                                  | Read recent entries to understand project evolution and governance changes            |
| `AGENTS.md` exists                                                                                     | Update, do not overwrite                                                              |

3. Check the **parent folder** for:
   - `AGENTS.md` — read it to inherit conventions, routing patterns, internal domain
   - `README.md` — note its Folder index section for later update
   - `AI_NAVIGATION.md` — read it to inherit context routing patterns
   - `context-map.yaml` — read it to inherit machine-readable routing conventions
   - `CHANGELOG.md` — read recent entries to inherit project/package evolution context

---

## Phase 2 — Understand

Read the **3–5 most informative files** in the target folder. Priority order:

1. Existing `AI_NAVIGATION.md` and `context-map.yaml` (if present — navigation authority)
2. Existing `README.md` (if present)
3. Existing `CHANGELOG.md` (if present — recent project/governance evolution)
4. Existing `AGENTS.md` or `CLAUDE.md` (if present — update mode, not create)
5. Existing `.archcore/` index/status/context files, if present
6. Existing `memory-bank/activeContext.md`, `memory-bank/progress.md`, and `memory-bank/decisionLog.md`, if present
7. Primary code entry point (`main.*`, `index.*`, `app.*`, `__init__.py`)
8. Key config (`package.json`, `pyproject.toml`, `go.mod`, `*.yaml` service config)
9. Most recently modified `.md` file (captures active work context)

Read parent AGENTS.md to extract:
- `@` import chain (for AGENTS.md inheritance)
- Internal domain (e.g. `apn.net.au`)
- Naming conventions, routing rules

Read parent `AI_NAVIGATION.md` / `context-map.yaml` if present to extract:
- Authority order
- Existing routing categories
- Archcore, memory-bank, Graphify, and Repomix conventions
- Generated context locations
- Drift/conflict handling rules

Read parent `CHANGELOG.md` if present to extract:
- Recent governance or routing changes
- Recent template/pattern changes
- Migration notes that affect repeat-run safety
- Deprecated or superseded behaviours

**If content is insufficient to infer purpose**, ask:
> "What is the purpose of this folder? One sentence is enough."

---

## Phase 3 — Infer

From inventory + content reads, determine:

| Field                    | How to infer                                                                                                                                                              |
| ------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Project name             | Folder name, formatted (e.g. `aurukun-fni` → "Aurukun FNI")                                                                                                               |
| Purpose                  | From README, code comments, config descriptions, or folder name semantics                                                                                                 |
| Technology stack         | From file extensions, package manifests, imports                                                                                                                          |
| Participants | From git log (`git log --format="%an" | sort -u`), email headers in EML files, or existing docs |
| Internal domain          | From parent AGENTS.md; default `apn.net.au` for APN projects                                                                                                              |
| Subfolder roles          | From subfolder names and their contents                                                                                                                                   |
| Project type             | Code / docs / ops / comms / mixed (drives conditional file creation)                                                                                                      |
| Governance completeness  | Presence/quality of README, AGENTS, CLAUDE, SCRATCHPAD, CHANGELOG, AI_NAVIGATION, context-map, roadmap, architecture docs                                                 |
| Navigation maturity      | Whether task-to-file routing, source priority, drift policy, and generated-context rules exist                                                                            |
| Structured truth backend | Presence of `.archcore/`, ADRs, rules, specs, guides, plans, memory-bank, Graphify, Repomix                                                                               |
| Script/task inventory    | Presence of `justfile`, `scripts/README.md`, other task runners (Taskfile.yml, Makefile, package.json), raw scripts, safety labels, inputs/outputs, and stale/missing     |
|                          |   catalog entries                                                                                                                                                         |
| Coherence invariants     | Claims the governance surfaces make that the filesystem can contradict: counts, index links, path references, catalogs, generated artifacts and their sources, and any    |
|                          |   threshold or canonical value restated in more than one file. Each becomes a check — see `patterns/governance-checks.md` for the artifact-to-check inference table       |
| Repeat-run risk          | Existing custom sections, `KEEP` blocks, managed blocks, user-authored YAML/JSON, and generated artifacts                                                                 |
| Runtime requirements     | Interpreters the scripts/recipes actually invoke (`python3`, `node`, `npx`), and whether each is pinned in `.mise.toml`. Derive the working-cache peer path from the      |
|                          |   source root — see *Runtime isolation*                                                                                                                                   |
| Active development?      | Presence of TODOs, WIP markers, incomplete docs, recent git commits                                                                                                       |

---

## Phase 4 — Generate Files

### File creation/update policy

| File                           | Bootstrap                      | Navigation-add               | Refresh                                                                                | Audit      |
| ------------------------------ | -----------------------------: | ---------------------------: | -------------------------------------------------------------------------------------: | ---------: |
| `README.md`                    | create/update                  | update pointers              | update index/pointers only                                                             | check      |
| `AGENTS.md`                    | create/update                  | add navigation block         | refresh managed block only                                                             | check      |
| `CLAUDE.md`                    | create/update                  | ensure wrapper               | ensure wrapper                                                                         | check      |
| `SCRATCHPAD.md`                | create/update                  | update memory pointers       | append/protect KEEP                                                                    | check      |
| `CHANGELOG.md`                 | create/update                  | append navigation addition   | append refresh summary                                                                 | check      |
| `.archcore/`                   | initialize if CLI available    | initialize if CLI available  | initialize if CLI available                                                            | check      |
| Graphify / `graphify-out/`     | run if CLI available           | run if CLI available         | run if CLI available                                                                   | check      |
| `repomix.config.json`          | initialize if CLI available    | initialize if CLI available  | run to refresh context pack                                                            | check      |
| `AI_NAVIGATION.md`             | create if useful               | create                       | update managed sections only                                                           | check      |
| `context-map.yaml`             | create if useful               | create                       | write `.proposed` if risky                                                             | check      |
| `scripts/README.md`            | create if scripts/tasks exist  | add pointer if scripts/tasks | create from template if scripts/tasks exist and file missing; update managed blocks if | check      |
|                                |                                |   exist                      |   exists                                                                               |            |
| `justfile`                     | create from template if no     | no unless needed             | propose only if drift/conflict                                                         | check      |
|                                |   canonical runner exists and  |                              |                                                                                        |            |
|                                |   scripts/automation present   |                              |                                                                                        |            |
| `scripts/check_governance.py`  | create from template, tuned to | add if governance surfaces   | **create from template if missing**; if present, extend registries for new artifacts — | run it,    |
|                                |   inferred invariants          |   exist                      |   never narrow an existing check                                                       |   report   |
|                                |                                |                              |                                                                                        |   failures |
|                                |                                |                              |                                                                                        |   and      |
|                                |                                |                              |                                                                                        |   coverage |
|                                |                                |                              |                                                                                        |   gaps     |
| `scripts/context-preflight.sh` | explicit request only          | explicit request only        | audit/propose only                                                                     | check      |
| `ARCHITECTURE.md`              | conditional                    | no unless needed             | update pointers only                                                                   | check      |
| `CONVENTIONS.md`               | conditional                    | no unless needed             | update pointers only                                                                   | check      |
| `ROADMAP.md`                   | conditional                    | no unless needed             | update progress only                                                                   | check      |

---

### Markdown quality rules

Apply these rules to every markdown file created or updated by this skill. Authority:
[`/Volumes/Data/_ai/governance/categories/markdown-guide.md`](/Volumes/Data/_ai/governance/categories/markdown-guide.md).

**Naming**
- Time-bound files: `<slug>-YYYYMMDD_hhmm.md` (e.g. `design-notes-20260522_1400.md`).
- Stable entrypoints (`README.md`, `AGENTS.md`, `CLAUDE.md`, `SCRATCHPAD.md`, `.agents/*.md`) keep their exact names — do not rename them.
- Metadata timestamp fields (`Last reviewed`, `Last updated`, etc.) use `YYYYMMDD_hhmm` format.

**Table of contents**
- Any file that exceeds 100 lines **must** have a TOC.
- Generate the TOC automatically when creating or first extending a file past 100 lines.
- Place the TOC immediately after the document's main `#` heading (after any frontmatter, before the first section).
- Use a `## Contents` heading for the TOC section. Exclude the `#` title from the TOC itself.
- TOC anchors follow GitHub-flavored markdown: lowercase, spaces → hyphens, special characters stripped.
- When editing any long file that already has a TOC, update the TOC in the same pass — reflect any added or removed section headings before finishing.

**Links and references**
- In `README.md`, `readme.md`, and similar index files, references to other markdown files must be written as markdown links, not plain paths or filenames.
- Metadata fields (`Source of truth`, `Synced from`, `Synced to`) that name a specific file must render that file as a markdown link.
- Keep generic filename patterns and placeholders as code literals (e.g. `` `<slug>-YYYYMMDD_hhmm.md` ``) unless they refer to a single concrete existing document.

**Quality pass**
- After writing or editing a markdown file, fix malformed list structure, awkward rendering, and stale headings in the same pass.
- Treat `README.md` as a navigation and inventory surface: lead with folder index and governance pointers, not prose.

---

### Archcore initialization and promotion candidate reporting

Before generating or refreshing governance files, check whether the `archcore` CLI is available.

- If `archcore` is available and `.archcore/` is missing in `bootstrap`, `navigation-add`, or `refresh` mode, run `archcore init`.
- If `archcore init` succeeds, update `AI_NAVIGATION.md` and `context-map.yaml` so `.archcore/` is active structured truth, not disabled or optional-only state.
- If `archcore` is unavailable, keep `.archcore/` optional in routing and report that Archcore initialization was skipped.
- If the user requested `audit` only, report whether initialization would run in refresh mode, but do not create `.archcore/` unless the user asked for changes.

`archcore init` is a setup action. Do not populate ADRs, rules, specs, guides, or plans unless the user explicitly authorizes those content changes.

#### Promotion candidate reporting

After `archcore init` (or when `.archcore/` already exists in `bootstrap` or `refresh` mode), inspect existing governance files and emit `ARCHCORE_PROMOTION_CANDIDATES.md`:

**Source files to inspect:** `README.md`, `AGENTS.md`, `ARCHITECTURE.md`, `ROADMAP.md`, `CONVENTIONS.md`, `SCRATCHPAD.md`, `memory-bank/decisionLog.md`

**Do not inspect:** `CHANGELOG.md` (history only, not truth source), generated files (`.ai-context/`, `graphify-out/`, `repomix-output.md`).

**Extraction rules:** apply heuristics from [`patterns/archcore-routing.md`](patterns/archcore-routing.md).

**Output:** write `ARCHCORE_PROMOTION_CANDIDATES.md` in the project root. Format per `patterns/archcore-routing.md`. Do not create any `.archcore/` content files — report only.

**Tell the user:** "Review `ARCHCORE_PROMOTION_CANDIDATES.md`, then run `/skill-ai-it promote` to authorize writing Archcore content."

- On `refresh`: re-scan and update `ARCHCORE_PROMOTION_CANDIDATES.md`; do not overwrite existing `.archcore/` content.
- On `audit`: report what candidates would be surfaced; do not write the file.
- On `promote`: read `ARCHCORE_PROMOTION_CANDIDATES.md`; write or propose `.archcore/` content files with provenance headers and `status: proposed`; write or update `.archcore/README.md` as the index;
  carry any still-relevant *never promote* reasoning into that index; then **delete `ARCHCORE_PROMOTION_CANDIDATES.md`**.

#### The candidates file is transient — promote deletes it

`ARCHCORE_PROMOTION_CANDIDATES.md` is a **proposal queue**, not a record. It exists between the run that surfaces candidates and the run that promotes them, and `promote` removes it.

Two reasons, and the second is the one that bites:

1. **A queue that outlives its proposals becomes a stale second index.** Once the documents exist, a file listing them under a name that says "candidates" is a governance surface misdescribing its own
   contents — and a later session reading it cannot tell a pending proposal from a completed one.
2. **It lives at the repo root, which `bootstrap` and `refresh` both rewrite.** Anything durable recorded there is destroyed by the next skill invocation with no trace. Observed 2026-08-25: a
   post-promotion ledger was written into it and would have been silently erased on the next refresh.

**The durable index is `.archcore/README.md`**, written or updated by `promote`: what each document governs, the `status:` of the set, how to propose another, and — carried out of the candidates file
before it is deleted — what is **deliberately never promoted** and why. That last table is the part a future scan needs, or it re-proposes the same rejected candidates every refresh.

Point the project's orphan check at `.archcore/README.md`, not at the candidates file. Register the candidates filename in the checker's `CONDITIONAL_PATHS` with its reason, so historical mentions in
`CHANGELOG.md` do not fail path resolution once the file is gone — history is not a live claim.

---

### Graphify initialization and refresh

Run `graphify update .` whenever the `graphify` CLI is available, in all active modes (`bootstrap`, `navigation-add`, `refresh`).

- If `graphify-out/` is missing and the CLI is available, `graphify update .` will initialize and populate it.
- If `graphify-out/` already exists, `graphify update .` refreshes the graph on every run.
- Treat `graphify-out/GRAPH_REPORT.md` and `graphify-out/graph.json` as disposable generated support — always regenerable, never canonical truth.
- In `audit` mode: report whether Graphify would run, but do not invoke it unless the user requests changes.

---

### Repomix initialization and refresh

Run Repomix whenever the `repomix` CLI is available, in all active modes (`bootstrap`, `navigation-add`, `refresh`).

- If `repomix.config.json` is missing and the CLI is available, create it from `templates/repomix.config.json`, then run `repomix --config repomix.config.json`.
- If `repomix.config.json` already exists, run `repomix --config repomix.config.json` to refresh the context pack.
- Treat `repomix-output.md` and `.ai-context/` as disposable generated support — always regenerable, never canonical truth.
- In `audit` mode: report whether Repomix would run, but do not invoke it unless the user requests changes.

---

### Script and task inventory

When a target project contains scripts or automation, help agents identify runnable entrypoints, purpose, inputs, outputs, side effects, and safety.

Primary executable source of truth — detection order:

1. `justfile` / `Justfile`
2. `Taskfile.yml`
3. `Makefile`
4. `package.json` scripts
5. raw scripts under `scripts/`
6. `.github/workflows/`, `ansible/`, `playbooks/` (CI/ops runners)

Human/agent-readable operational catalog:

- `scripts/README.md`

Preferred source template:

- `templates/scripts-README.md`

Audit reference: `patterns/script-task-audit-checklist.md`.

#### Mode behavior

- `bootstrap`: if the target has scripts, tasks, or automation files, create or update `scripts/README.md`. If no canonical task runner exists but scripts/automation are present, prefer creating
  `justfile` from `templates/justfile` as the lightweight task catalog. Do not create empty task scaffolding when no scripts/tasks exist.
- `navigation-add`: add navigation pointers to the existing canonical runner first. If a `justfile` exists, route agents to `just --list` then `scripts/README.md`.
- `refresh`: create `scripts/README.md` from `templates/scripts-README.md` if scripts or tasks exist and the file is missing. If the file exists, update managed inventory blocks only. Do not overwrite
  manually written script descriptions. If drift exists between the task runner and `scripts/README.md`, report or propose updates.
- `audit`: report scripts missing from `scripts/README.md`, tasks missing descriptions, cataloged scripts that no longer exist, raw scripts not represented in `scripts/README.md`, and potentially
  unsafe scripts without safety notes.
- `promote`: promote only stable, durable operational procedures to Archcore. Do not promote every script automatically.

#### Task safety labels

Use these labels in `scripts/README.md` and when reporting script/task safety:

- `safe`
- `review-required`
- `destructive`
- `external-network`
- `modifies-files`
- `requires-secrets`
- `requires-credentials`
- `long-running`
- `unknown`

Treat `unknown` as not safe until inspected.

Agents must prefer cataloged tasks over raw script execution. Prefer `just <task>` when a `justfile` exists. Do not run destructive, review-required, or unknown-safety tasks without review.

#### Runtime isolation — recipes must not call a bare interpreter

**A generated `justfile` never calls bare `python3`, `node`, `npx`, or `ruby`.** A bare interpreter resolves to whatever the host has on `PATH`, which is not what the project's `.mise.toml` pins.

This is the failure mode that makes it worth a rule rather than a preference: **it works.** A recipe calling bare `python3` runs correctly on the machine it was written on, passes every check, and
keeps working until the host's Homebrew updates or the operator switches machines — at which point it fails somewhere inside a script, reading like a code bug rather than an environment one. Observed
2026-08-25: a freshly bootstrapped project pinned Python 3.14 and Node 26 in `.mise.toml` while every recipe silently used Homebrew's 3.14.7 and Node 26.7.0. Nothing in the project could detect it.

**Generate these three things together, or none of them works:**

1. **`.mise.toml` in the project**, pinning every runtime the recipes use. Pin **Node as well as Python** when any recipe shells out to a JS tool — pinning only Python leaves `mise exec -- node`
   falling through to the host, which looks pinned and is not.
2. **Interpreter variables at the top of the `justfile`**, and every recipe going through them:
   ```just
   wc := "<the working-cache peer for this project>"
   py := wc + "/.venv/bin/python"
   nd := "mise exec -- node"
   ```
3. **A `_require-venv` guard that every Python recipe depends on**, so a missing venv fails with a rebuild instruction instead of silently falling back to the host — which is the same defect wearing a
   different hat.

Also generate `just bootstrap` (builds the venv from the mise pins; safe to re-run) and `just runtimes` (prints the resolved interpreters). `runtimes` is the one that makes the invariant *observable*
— without it, "the recipes use the pinned runtime" is an assumption nobody can check in under a minute.

**The venv lives in the working-cache peer, never in the repo.** A repo carries source and evidence; a venv is rebuildable runtime, and mixing them puts a large disposable tree in the same history as
the durable one. Derive the peer path from the source root:

| Source root                        | Working-cache peer                         | Project depth |
| ---------------------------------- | ------------------------------------------ | ------------- |
| `project_stuff/<group>/<project>/` | `project-working-cache/<group>/<project>/` | 2             |
| `mcp_stuff/<project>/`             | `mcp-working-cache/<project>/`             | 1             |
| `skills_stuff/<project>/`          | `skills-working-cache/<project>/`          | 1             |
| `tools_stuff/<project>/`           | `tools-working-cache/<project>/`           | 1             |

For a track nested below that depth (`project_stuff/me/uae/atar/`), extend the peer path to match the track (`project-working-cache/me/uae/atar/`) so the venv sits beside the bytecode cache the
`usercustomize.py` router already writes there.

**`uv run` is not the primary path.** It resolves its own interpreter independently of mise — tested 2026-08-25, `uv run python3` selected Homebrew's 3.14.7 while mise pinned 3.14.5 — so it is the
same class of drift, not a fix for it. Use `uv run --with <pkg>` only where a recipe needs throwaway third-party packages and the exact patch version genuinely does not matter; say so in a comment
where you do.

**Do not add a `.python-version` file alongside `.mise.toml`.** Two files stating the version is two places for it to drift. `.mise.toml` owns the pin.

**Declare third-party dependencies in `requirements.txt`, and have `bootstrap` install them.** Pinning the interpreter without declaring the packages does not remove the hidden host dependency — it
relocates it, and the failure arrives later and reads worse. This is not hypothetical: the moment the 2026-08-25 project switched off the host interpreter, `just nav-validate` failed on a missing
PyYAML that had been supplied invisibly by Homebrew's Python for the whole session. Nothing had ever declared it.

Keep the project's **own** scripts stdlib-only where you can, and say so in the file. The governance gate in particular must never fail for environment reasons — a check that cannot run is
indistinguishable from a check that passes, and it is the one thing you cannot afford to be ambiguous. `requirements.txt` then covers only what the project calls *out* to.

#### justfile — embedded fallback

If `templates/justfile` is unavailable, write the justfile from this embedded fallback and adapt it to the project:

```just
# just task catalog for this project.
# Usage: just --list | just <task>
#
# Recipes go through {{py}} / {{nd}}, never a bare interpreter — see "Runtime isolation" above.

set dotenv-load := false

wc := "<working-cache peer for this project>"
py := wc + "/.venv/bin/python"
nd := "mise exec -- node"

# List available tasks
default:
    @just --list

# Build the working-cache venv from the mise-pinned runtimes. Safe to re-run.
bootstrap:
    @mkdir -p "{{wc}}"
    @test -f "{{wc}}/.mise.toml" || cp .mise.toml "{{wc}}/.mise.toml"
    @cd "{{wc}}" && mise install && mise exec -- python -m venv .venv
    @test -f requirements.txt && {{py}} -m pip install --quiet --upgrade pip -r requirements.txt || true
    @{{py}} -c "import sys; print('venv ready:', sys.version.split()[0], sys.executable)"

# Fail early rather than falling back to the host interpreter
_require-venv:
    @test -x "{{py}}" || { echo "venv missing at {{py}} — run: just bootstrap" >&2; exit 1; }

# Report which runtimes the recipes will actually use
runtimes:
    @printf 'python  '; {{py}} -c "import sys; print(sys.version.split()[0], sys.executable)" 2>/dev/null || echo "MISSING — run: just bootstrap"
    @printf 'node    '; {{nd}} --version 2>/dev/null || echo "MISSING — pin node in .mise.toml"

# Audit script/task inventory for drift
audit-scripts:
    @echo "== just recipes =="; just --list || true
    @echo; echo "== script files =="; find scripts -maxdepth 2 -type f 2>/dev/null | sort || true

# Governance coherence checks — must exit 0 before durable work is called complete
check: _require-venv
    @{{py}} scripts/check_governance.py

# Run safe local preflight checks
preflight: runtimes audit-scripts check

# Lint Markdown files when markdownlint-cli2 is available
lint-md:
    @command -v markdownlint-cli2 >/dev/null && markdownlint-cli2 '**/*.md' || echo 'markdownlint-cli2 not installed; skipped'
```

Add project-specific tasks by inspecting `scripts/` and adapting to the discovered pipeline.

---

### Governance coherence checker

Every governed project gets `scripts/check_governance.py` — a stdlib-only script that turns the project's governance **claims** into assertions that fail. Doctrine, the seven check families, and the
artifact-to-check inference table live in `patterns/governance-checks.md`; read it before generating or extending a checker.

Source template: `templates/check_governance.py`. AGENTS.md managed block: `templates/AGENTS-governance-checks-block.md`.

The checker is **self-contained per project** — no shared runtime, no import from a canonical package. Universal checks are seeded from the template; project-specific checks are authored into the same
file. A project's checker is free to diverge as its invariants diverge, which is the point.

#### What makes it intelligent rather than generic

A generic linter cannot see a project's real integrity risks, because those risks are domain-shaped. The generated checker has three tiers:

- **Tier 1 (universal)** — path resolution, index links, count claims, catalog coverage. Copied from the template and tuned. Always present.
- **Tier 2 (conditional)** — generated only when the trigger artifact exists: a task runner, a structured-document class with a declared contract, a supersession chain.
- **Tier 3 (inferred)** — encodes *this project's* stated rules. For each rule the project states, ask: **what observable state would prove this rule was violated?** That answer is the check.

Two discipline rules on Tier 3, both load-bearing:

- **Every Tier 3 check cites the project rule it enforces**, in its docstring or failure message. A check whose justification cannot be located is a check the next agent deletes when it becomes
  inconvenient.
- **Never invent an invariant the project has not stated.** Manufacturing governance the operator never agreed to is worse than leaving a gap. Report the candidate invariant as a proposal instead.

#### Self-policing coverage — how it stays fine-tuned

The hardest failure mode is not a check that breaks; it is a new file that nothing checks. So the checker must fail on **uncovered** surfaces, not only incorrect ones. Generate an orphan check for
every catalog the project maintains: a document in `docs/` that the index does not link, a script absent from `scripts/README.md`, a file restating a registered constant without being registered.

This is what converts "keep the checker updated" from an intention recorded in a document into a blocking condition. Adding a file turns the build red until it is registered somewhere — the agent
extends the checker because it cannot proceed otherwise.

The asymmetry matters and is easy to half-implement: *catalog names something that vanished* and *something exists that no catalog names* are different defects, and only the second grows silently.
Generate both directions.

#### Mode behavior

- `bootstrap`: create from template with Tier 1 only, tuned to whatever catalogs and surfaces exist. Typically 10–40 assertions. Wire it into the task runner (`just check`) and add the AGENTS.md
  managed block. Do not generate Tier 2/3 scaffolding for structure the project does not yet have.
- `navigation-add`: create if governance surfaces exist and no checker does; otherwise add the AGENTS.md block and the runner recipe only.
- `refresh`: **this is the adoption path for projects that predate the capability.** If no checker exists, create one from the template exactly as `bootstrap` would, tuned to the invariants the
  project has accumulated since it was set up — which is usually a richer set than it had at bootstrap, so expect more than the bootstrap baseline. Wire it into the task runner and add the AGENTS.md
  managed block in the same pass. If a checker already exists, extend its registries to cover artifacts added since the last run — new catalogs, new generated outputs, new constant surfaces. **Never
  narrow an existing check to make a run green.**
- `audit`: run the checker, report failures verbatim, and separately report *coverage gaps* — artifact classes present in the project that no check covers. The second list is the more valuable output.
- `promote`: promote a stable invariant to a rule/spec document when the operator asks, then cite that document from the check.

#### Non-negotiables to state in the target project's AGENTS.md

- When a check fails, **fix the project, not the check**. Broadening an ignore-list or exempting the failing file converts a real finding into a permanent blind spot.
- A new check must be **able to fail** — prove it by breaking the project deliberately and watching it go red.
- **Text matching does not verify behavior.** Grepping for a threshold's characters does not prove the logic implements it; a script's output can state a rule its code no longer applies. Where a check
  must verify behavior, execute the behavior and assert on the result.
- **Do not enforce history.** Counts recorded as past facts are evidence, not live claims — exempt them by marker rather than editing the record to satisfy a linter.

---

### Always-created files

#### README.md

Create if missing. If it exists, add a **Governance pointers** section and update **Folder index** only.

```markdown
# <Project Name>

<One-sentence purpose.>

## Purpose

<2–3 sentences on what this project area is for and why it exists.>

## Context

<Optional. Fill only when meaningful background exists — e.g. engagement history,
external parties, triggering event. Omit section if nothing useful to say.>

## Folder index

- [<subfolder>/](<subfolder>/)
  <One-line role description.>
  Index: [<subfolder>/readme.md](<subfolder>/readme.md) ← only if index exists

## Governance pointers

- Local agent guidance: [AGENTS.md](AGENTS.md)
- Parent area guidance: [../AGENTS.md](../AGENTS.md)
- AI navigation entrypoint: [AI_NAVIGATION.md](AI_NAVIGATION.md)
- Machine-readable context map: [context-map.yaml](context-map.yaml)
- Project change/governance history: [CHANGELOG.md](CHANGELOG.md)
- Canonical governance root: [/Volumes/Data/_ai/governance/README.md](/Volumes/Data/_ai/governance/README.md)
```

#### AGENTS.md

Create if missing. If it exists, add missing sections only — do not overwrite existing rules.

```markdown
@<absolute-or-relative path to nearest parent AGENTS.md>

Title: <Project Name> Agent Policy
Category: agent-governance-guide
Status: current
Authority: local-supplement
Scope: <inferred scope — one line>
Last reviewed: <YYYY-MM-DD>
Summary: <One-line summary of what this policy governs.>

# AGENTS.md

## Working rules

<Rules derived from content analysis. Examples:>
- Treat [communications/](communications/) as the canonical location for all correspondence.
- When processing EML files for this project, use `<internal domain>` as the internal domain.
  Mark senders/recipients on other domains as `**[External]**`.
- Log correspondence to [communications/communications-tracking.md](communications/communications-tracking.md)
  using the `skill-commtracker` workflow.
- Follow naming convention: `<slug>-YYYYMMDD_hhmm.md` for time-bound notes.
- Keep [README.md](README.md) current when adding subfolders or significant documents.

<!-- BEGIN MANAGED: skill-ai-it:navigation -->
<!-- skill-ai-it-version: 2026-08-11-governance-checks-layer-v1 -->

## AI navigation and context preflight

Before answering, planning, editing, or creating files in this project:

1. Read [AI_NAVIGATION.md](AI_NAVIGATION.md).
2. Read [context-map.yaml](context-map.yaml).
3. Read recent entries in [CHANGELOG.md](CHANGELOG.md).
4. Load relevant `.archcore/` context if present.
5. Load relevant `memory-bank/` files if present.
6. Consult generated context when available:
   - `graphify-out/GRAPH_REPORT.md`
   - `.ai-context/governance-pack.md`
7. Before making durable changes, inspect companion-file rules in `context-map.yaml update_rules`. Update all companion files when changing source files.
8. If sources conflict, stop and report the conflict instead of guessing.
9. Do not treat `SCRATCHPAD.md` as durable truth unless content is marked `KEEP` or promoted into `.archcore/`, ROADMAP, or memory-bank.
10. Do not treat Graphify (`graphify-out/`) or Repomix (`.ai-context/`) output as canonical truth. These are generated support artifacts only, always rebuildable.
11. Before running scripts or automation, inspect `justfile`, `scripts/README.md`, `Taskfile.yml`, `Makefile`, and `package.json` when present. Prefer `just --list` and `just <task>` when a `justfile` exists.
12. Treat uncataloged scripts as `unknown` safety until inspected.
13. Run defined audit/check commands before completing work. Where `scripts/check_governance.py` exists, that includes it — and when it fails, fix the project, not the check. Adding a new artifact class, generated output, or a constant restated across files requires extending its registries in the same pass.
14. When adding, modifying, or removing scripts or tasks, update `scripts/README.md` to reflect the change — purpose, inputs, outputs, safety label, and idempotency.
15. After making changes, update `CHANGELOG.md` for all durable governance/navigation changes.
16. Preserve user-authored content outside managed sections. Do not rewrite custom project notes.

<!-- END MANAGED: skill-ai-it:navigation -->

<Insert the governance-checks managed block here verbatim from `templates/AGENTS-governance-checks-block.md`, with `<RUNNER CHECK COMMAND>` replaced by this project's actual command (e.g. `just check`).>

## Canonical governance linkage

- Parent area guidance: [../AGENTS.md](../AGENTS.md)
- Cross-repo governance root: [/Volumes/Data/_ai/governance/README.md](/Volumes/Data/_ai/governance/README.md)
```

#### CLAUDE.md

Always create as thin wrapper. Never duplicate AGENTS.md content here.

```markdown
@AGENTS.md

## Claude-specific additions
# No project-specific Claude additions at this time.
# Add here only if this project needs Claude Code behaviour that differs from global policy.
```

Repeat-run rule: if `CLAUDE.md` already contains `@AGENTS.md`, do not rewrite it. Only append Claude-specific additions if explicitly needed.

#### SCRATCHPAD.md

Always create (or update if exists). Populated from live memory systems — not a blank template.

**Step 1 — Query all three memory sources** using the inferred project name and folder name as search terms. Try at least two query variations per source before declaring empty.

| Source                | Tool                                    | Query strategy                                 |
| --------------------- | --------------------------------------- | ---------------------------------------------- |
| `memory-keeper`       | `context_search`                        | project name, folder name, channel name        |
| `mcp-project-context` | `list_projects` + `get_project_context` | match project name; use project ID             |
| `claude-mem`          | `search`                                | project name, key participants, topic keywords |

**Step 2 — Synthesize results** into the SCRATCHPAD structure below. SCRATCHPAD owns current state, anchors, open items, and session summaries (2–3 bullets per session — not full detail). Deep session
logs and file-change lists belong in memory-keeper, not here. Structured task tracking belongs in project-context, not here.

Populate every section from found data. If a source returns nothing, note "no results" in Memory pointers and infer content from folder reads (Phase 2).

**Step 3 — Write SCRATCHPAD.md.** Mark synthesized content `KEEP`.

```markdown
# SCRATCHPAD

Agent working memory for <project name>.
Use for: draft plans, terminal output, intermediate analysis, refactor outlines.
Cleared between sessions unless content is explicitly marked KEEP.

---

<!-- KEEP: populated <YYYY-MM-DD> from memory-keeper + mcp-project-context + claude-mem -->

## Current state

**Phase:** <current phase from project-context or last memory-keeper session>

<2–4 sentences: what the project is, where it stands, what just happened, what comes next.>

---

## Open items

- [ ] <Item — include enough context to act on without querying other sources>

---

## Key anchors

| Item | Detail |
|---|---|
| <key path, contact, fact> | <value> |

---

## Recent decisions

- <YYYY-MM-DD> — <Decision. Brief rationale if known.>

---

## Session history (summaries — full detail in memory-keeper)

### <YYYY-MM-DD> — <session title>
- <2–3 bullets: what was done, decisions made, key outcome>
- Evidence basis: memory-keeper key `<key>`

---

## Next actions

- <Specific next action>

---

## Memory pointers (navigation only — content is above)

- memory-keeper channel: `<channel>` / key(s): `<key1>`, `<key2>`
- project-context project ID: `<uuid>`
- claude-mem: <results found / no results>
```

**If all three sources return no results**: write minimal SCRATCHPAD with current-state inferred from folder content (Phase 2 reads) and note: `<!-- no prior memory — populate after first closeout
-->`

---

#### CHANGELOG.md

Always create during bootstrap. If it exists, append entries only; do not rewrite historical entries.

Use CHANGELOG.md as the durable project history and governance-change ledger. It is not a scratchpad and must not contain long terminal logs or unverified speculation.

```markdown
# Changelog — <Project Name>

## <YYYYMMDD_HHMM>

### Added

- Initial governance scaffold created.

### Changed

- <Governance/navigation/context changes made during this run.>

### Notes

- Generated by `skill-ai-it` in `<bootstrap | navigation-add | refresh | audit | promote>` mode.
```

Repeat-run append format:

```markdown
## <YYYYMMDD_HHMM>

### Changed

- <file> — <brief exact change>

### Skipped

- <file> — <reason>

### Proposed only

- <file.proposed> — <reason>
```

---

### Conditionally-created files

The files in this section are created only when their specific detection condition is met. State the reason for each conditional file in the audit output.

#### ARCHITECTURE.md — create when: code, infrastructure, or design decisions are present, or user requests architecture documentation

Preferred source: derive from project inventory and content reads. No external template — write from analysis.

```markdown
# Architecture — <Project Name>

## Overview

<One paragraph on what this project is and how its parts connect.>

## Components

| Component | Role |
|---|---|
| <name> | <purpose> |

## Key decisions

- <Decision or constraint that shapes the architecture.>
```

#### CONVENTIONS.md — create when: code files present, naming patterns exist, or style/linting rules are discoverable

Preferred source: derive from existing code and naming conventions. No external template.

```markdown
# Conventions — <Project Name>

## Naming

| Thing | Pattern | Example |
|---|---|---|
| Time-bound docs | `<slug>-YYYYMMDD_hhmm.md` | `design-notes-20260422_1400.md` |
| <language> files | <pattern from existing code> | <example> |

## Code style

<Derived from existing code. List only rules that are non-obvious or project-specific.
Do not restate language defaults.>

## Anti-patterns

- <Pattern to avoid and why>
```

#### ROADMAP.md — create when: active development, TODOs present, migration/phase structure, or incomplete features detected

Preferred source: derive from TODOs, scratchpad, and memory systems. No external template.

```markdown
# Roadmap — <Project Name>

## Current phase

**Phase <N>:** <Description.>

## Next milestones

- [ ] <Milestone>

## Completed

- [x] <Completed milestone>
```

#### AI_NAVIGATION.md — create when: missing during `navigation-add`, requested explicitly, or project has more than one governance/context source

Create as the human-readable context router. If it exists, preserve custom content and update only the managed routing sections.

Preferred source template: `templates/AI_NAVIGATION.md`.

```markdown
# AI Navigation — <Project Name>

Purpose: this file is the project context entrypoint for AI agents. It tells agents where project truth lives, what to read first, what is authoritative, what is temporary, and what must be updated after work.

This file is a router, not the full knowledge store.

<!-- BEGIN MANAGED: skill-ai-it:navigation -->
<!-- skill-ai-it-version: 2026-08-11-governance-checks-layer-v1 -->

## Mandatory read order

Before answering, planning, editing, or creating files in this project, read in this order:

1. `AGENTS.md`
2. `AI_NAVIGATION.md`
3. `context-map.yaml`
4. `CHANGELOG.md`
5. Relevant `.archcore/` documents, if present
6. Relevant `memory-bank/` files, if present
7. Relevant project docs/code based on the task

If available, also consult:

- `graphify-out/GRAPH_REPORT.md`
- `.ai-context/governance-pack.md`

## Source priority

When sources conflict, use this priority:

1. `.archcore/` accepted ADRs, rules, specs, guides, and plans
2. `AGENTS.md` / `CLAUDE.md`
3. `AI_NAVIGATION.md`
4. `context-map.yaml`
5. `CHANGELOG.md`
6. `ARCHITECTURE.md` / `architecture.md`
7. `ROADMAP.md` / `roadmap.md`
8. `memory-bank/activeContext.md`
9. `memory-bank/progress.md`
10. `SCRATCHPAD.md` / `scratchpad.md`
11. old notes, drafts, archived files

`SCRATCHPAD.md` is temporary unless promoted into Archcore, roadmap, or memory-bank, or explicitly marked `KEEP`.

## Project context files

| File / Path | Role | Authority |
|---|---|---|
| `AGENTS.md` | Universal agent instruction file | High |
| `CLAUDE.md` | Claude-specific bootstrap file | High |
| `AI_NAVIGATION.md` | Human-readable AI routing file | High |
| `context-map.yaml` | Machine-readable routing map | High |
| `.archcore/adr/` | Architecture decisions | Highest |
| `.archcore/rules/` | Durable project/agent rules | Highest |
| `.archcore/specs/` | Technical/design contracts | Highest |
| `.archcore/guides/` | Operational guides | High |
| `.archcore/plans/` | Approved implementation plans | High |
| `ARCHITECTURE.md` / `architecture.md` | Human-readable architecture overview | Medium-high |
| `ROADMAP.md` / `roadmap.md` | Human-readable roadmap | Medium-high |
| `memory-bank/activeContext.md` | Current working context | Medium |
| `memory-bank/progress.md` | Progress and current state | Medium |
| `memory-bank/decisionLog.md` | Decision notes before promotion | Medium |
| `SCRATCHPAD.md` / `scratchpad.md` | Temporary notes | Low |
| `CHANGELOG.md` | Durable project/governance change history | Medium-high |
| `docs/` | Supporting documentation | Depends on file |
| `graphify-out/` | Generated navigation graph | Generated support |
| `.ai-context/governance-pack.md` | Generated deterministic context pack | Generated support |

## Task routing

### Architecture/design questions

Read:

1. `.archcore/adr/`
2. `.archcore/specs/`
3. `ARCHITECTURE.md` / `architecture.md`
4. `docs/**/*.md`

Do not answer from scratchpad alone.

### Planning/status questions

Read:

1. `.archcore/plans/`
2. `ROADMAP.md` / `roadmap.md`
3. `CHANGELOG.md`
4. `memory-bank/progress.md`
5. `memory-bank/activeContext.md`
6. `SCRATCHPAD.md` / `scratchpad.md`

Report uncertainty if these disagree.

### Agent/governance questions

Read:

1. `AGENTS.md`
2. `CLAUDE.md`
3. `AI_NAVIGATION.md`
4. `context-map.yaml`
5. `CHANGELOG.md`
6. `.archcore/rules/`

### Implementation/code questions

Read:

1. `AGENTS.md`
2. `context-map.yaml`
3. Relevant `.archcore/specs/`
4. Relevant source files
5. Relevant tests
6. `graphify-out/GRAPH_REPORT.md`, if present

Use code navigation tools where available.

## Script and Task Navigation

For script, task, or automation questions, read in this order:

1. `justfile` / `Justfile`
2. `scripts/README.md`
3. `Taskfile.yml`
4. `Makefile`
5. `package.json`
6. `patterns/script-task-audit-checklist.md`, if present
7. Raw scripts under `scripts/`

Prefer `just --list` and `just <task>` when a `justfile` exists.

Do not run uncataloged scripts blindly. Treat uncataloged scripts as `unknown safety` until inspected.

If the catalog is stale, propose an update to `scripts/README.md` or the relevant task runner.

If a task is marked `destructive`, `review-required`, or `unknown`, stop and request review before execution.

### Documentation updates

Before updating docs, check:

1. `.archcore/`
2. `README.md`
3. `CHANGELOG.md`
4. `ARCHITECTURE.md` / `architecture.md`
5. `ROADMAP.md` / `roadmap.md`
6. `memory-bank/`
7. `docs/`

After updates, ensure related files are not left inconsistent.

## Drift handling

If files disagree:

1. Stop.
2. Identify the conflicting files.
3. State which source has higher authority.
4. Propose the smallest correction.
5. Do not silently merge conflicting assumptions.

## Update rules

| Change type | Update |
|---|---|
| New durable decision | Add/propose `.archcore/adr/` |
| New agent/project rule | Add/propose `.archcore/rules/` |
| New architecture contract | Add/propose `.archcore/specs/` |
| New operating procedure | Add/propose `.archcore/guides/` |
| New implementation plan | Add/propose `.archcore/plans/` |
| Progress change | Update `memory-bank/progress.md` |
| Current working state changed | Update `memory-bank/activeContext.md` |
| Temporary note | Add to `SCRATCHPAD.md` only if not durable |
| Context routing changed | Update `AI_NAVIGATION.md` and `context-map.yaml` |
| Governance or navigation files changed | Append `CHANGELOG.md` |

## Generated context

Generated files are useful but not authoritative by themselves.

| Generated file | Purpose |
|---|---|
| `graphify-out/GRAPH_REPORT.md` | Relationship/navigation overview |
| `graphify-out/graph.json` | Machine-readable graph |
| `.ai-context/governance-pack.md` | Deterministic context bundle |
| `.ai-context/repo-pack.md` | Larger project/repo context bundle |

Regenerate these after large documentation, architecture, or source changes.

## Agent answer contract

When answering from project context:

1. Prefer cited file paths.
2. Do not invent project state.
3. Say “not found in project context” if unsupported.
4. Distinguish confirmed facts from assumptions.
5. Ask only when required; otherwise proceed with stated assumptions.

<!-- END MANAGED: skill-ai-it:navigation -->
```

#### context-map.yaml — create when: `AI_NAVIGATION.md` is created or already exists but no machine-readable routing map exists

Create as the machine-readable context routing map. If it exists, avoid full regeneration unless the user requests it. For repeat runs, write `context-map.proposed.yaml` when changing more than one
top-level section.

Preferred source template: `templates/context-map.yaml`.

```yaml
version: 1

project:
  name: <project-slug>
  context_policy: "AI_NAVIGATION.md is the human-readable router; this file is the machine-readable routing map."

bootstrap:
  required_first_read:
    - AGENTS.md
    - AI_NAVIGATION.md
    - context-map.yaml
    - CHANGELOG.md

authority_order:
  - path: ".archcore/adr"
    type: architecture_decisions
    authority: highest
  - path: ".archcore/rules"
    type: durable_rules
    authority: highest
  - path: ".archcore/specs"
    type: design_contracts
    authority: highest
  - path: ".archcore/guides"
    type: operating_guides
    authority: high
  - path: ".archcore/plans"
    type: approved_plans
    authority: high
  - path: "AGENTS.md"
    type: agent_instructions
    authority: high
  - path: "CLAUDE.md"
    type: claude_specific_instructions
    authority: high
  - path: "AI_NAVIGATION.md"
    type: context_router
    authority: high
  - path: "ARCHITECTURE.md"
    type: architecture_overview
    authority: medium_high
  - path: "ROADMAP.md"
    type: roadmap
    authority: medium_high
  - path: "memory-bank/activeContext.md"
    type: active_context
    authority: medium
  - path: "memory-bank/progress.md"
    type: progress_state
    authority: medium
  - path: "memory-bank/decisionLog.md"
    type: working_decision_log
    authority: medium
  - path: "SCRATCHPAD.md"
    type: transient_notes
    authority: low
  - path: "CHANGELOG.md"
    type: project_history
    authority: medium_high

context_sources:
  archcore:
    enabled: true
    root: ".archcore"
    read_first_for:
      - architecture_decision
      - governance_rule
      - design_contract
      - implementation_plan
      - operating_procedure
      - durable_project_truth

  memory_bank:
    enabled: true
    root: "memory-bank"
    files:
      active_context: "memory-bank/activeContext.md"
      progress: "memory-bank/progress.md"
      decisions: "memory-bank/decisionLog.md"
      patterns: "memory-bank/systemPatterns.md"
      open_questions: "memory-bank/openQuestions.md"

  generated:
    graphify:
      enabled: true
      root: "graphify-out"
      preferred_files:
        - "graphify-out/GRAPH_REPORT.md"
        - "graphify-out/graph.json"

    repomix:
      enabled: true
      root: ".ai-context"
      preferred_files:
        - ".ai-context/governance-pack.md"
        - ".ai-context/repo-pack.md"

routing:
  architecture:
    description: "Architecture, design, topology, components, boundaries, trade-offs."
    read:
      - ".archcore/adr"
      - ".archcore/specs"
      - "ARCHITECTURE.md"
      - "architecture.md"
      - "docs/**/*.md"
    avoid_as_authority:
      - "SCRATCHPAD.md"
      - "scratchpad.md"

  planning:
    description: "Roadmap, work breakdown, current status, next steps."
    read:
      - ".archcore/plans"
      - "ROADMAP.md"
      - "roadmap.md"
      - "CHANGELOG.md"
      - "memory-bank/progress.md"
      - "memory-bank/activeContext.md"
      - "SCRATCHPAD.md"

  governance:
    description: "Agent behaviour, project rules, file update rules, workflow rules."
    read:
      - "AGENTS.md"
      - "CLAUDE.md"
      - "AI_NAVIGATION.md"
      - "context-map.yaml"
      - "CHANGELOG.md"
      - ".archcore/rules"

  implementation:
    description: "Code, scripts, configs, tests, automation."
    read:
      - "AGENTS.md"
      - "AI_NAVIGATION.md"
      - "context-map.yaml"
      - ".archcore/specs"
      - ".archcore/rules"
      - "src/**"
      - "scripts/**"
      - "tests/**"
    tools:
      preferred:
        - serena
        - graphify
        - repomix
      optional:
        - semgrep
        - markdownlint
        - vale

  scripts:
    purpose: "Project-local scripts, automation, task runners, and executable workflows."
    read_first:
      - "justfile"
      - "Justfile"
      - "scripts/README.md"
      - "Taskfile.yml"
      - "Makefile"
      - "package.json"
    generated_support:
      - "graphify-out"
      - ".ai-context"
    rules:
      - "Prefer just --list and just <task> when a justfile exists."
      - "Read scripts/README.md before running raw scripts."
      - "Treat uncataloged scripts as unknown safety."
      - "Do not run destructive scripts without explicit review."

  automation:
    purpose: "Repeatable operational workflows and project task entrypoints."
    read_first:
      - "justfile"
      - "Justfile"
      - "scripts/README.md"
      - "docs/automation.md"
    rules:
      - "Prefer cataloged commands."
      - "Prefer just when a justfile exists."
      - "Confirm inputs, outputs, side effects, and safety before execution."

  documentation:
    description: "README, docs, architecture docs, user guides."
    read:
      - "README.md"
      - "CHANGELOG.md"
      - "docs/**/*.md"
      - "ARCHITECTURE.md"
      - "architecture.md"
      - ".archcore/guides"
      - ".archcore/specs"
      - "memory-bank/activeContext.md"

  troubleshooting:
    description: "Issue investigation, debugging, root cause analysis."
    read:
      - "memory-bank/activeContext.md"
      - "memory-bank/progress.md"
      - "SCRATCHPAD.md"
      - "scratchpad.md"
      - "docs/**/*.md"
      - "logs/**"
      - "reports/**"

update_rules:
  durable_decision:
    update:
      - ".archcore/adr"
    also_consider:
      - "ARCHITECTURE.md"
      - "architecture.md"
      - "memory-bank/decisionLog.md"

  durable_rule:
    update:
      - ".archcore/rules"
    also_consider:
      - "AGENTS.md"
      - "AI_NAVIGATION.md"

  design_contract:
    update:
      - ".archcore/specs"
    also_consider:
      - "ARCHITECTURE.md"
      - "architecture.md"
      - "docs/**/*.md"

  operating_procedure:
    update:
      - ".archcore/guides"
    also_consider:
      - "README.md"
      - "docs/**/*.md"

  plan_change:
    update:
      - ".archcore/plans"
      - "ROADMAP.md"
      - "roadmap.md"
      - "memory-bank/progress.md"

  working_context_change:
    update:
      - "memory-bank/activeContext.md"

  temporary_note:
    update:
      - "SCRATCHPAD.md"

  routing_change:
    update:
      - "AI_NAVIGATION.md"
      - "context-map.yaml"
      - "AGENTS.md"

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

  scratchpad_rule:
    authoritative: false
    promotion_required_for_durable_truth: true

generated_context_policy:
  regenerate_after:
    - architecture_change
    - major_doc_change
    - roadmap_restructure
    - new_archcore_documents
    - significant_code_restructure

  commands:
    graphify: "graphify update ."
    repomix_governance: "repomix --config repomix.config.json"

answer_contract:
  require_source_paths: true
  unsupported_answer: "not found in project context"
  distinguish_assumptions: true
  do_not_invent_state: true
```

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
  "ignore": [
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
```

#### scripts/context-preflight.sh — optional local artifact, explicit request only

Do not create a repo-local preflight script during normal bootstrap, navigation-add, or refresh runs. The skill package is the maintained source for generic validation/preflight behavior.

Create `scripts/context-preflight.sh` only when the user explicitly asks for a repo-local command or when the target project already has one and the user asks to refresh it. If the file exists, audit
it for drift and propose changes instead of treating it as the source of truth.

Preferred opt-in source template: `templates/context-preflight.sh`.

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
if command -v graphify >/dev/null 2>&1; then
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

### Optional/generated support files

These are created only on explicit user request or generated by supporting tools. They are not created automatically and are not canonical truth.

| Path                           | Source                                                      | Notes                                         |
| ------------------------------ | ----------------------------------------------------------- | --------------------------------------------- |
| `scripts/context-preflight.sh` | Explicit request only; use `templates/context-preflight.sh` | Local opt-in preflight entrypoint             |
| `graphify-out/`                | Graphify CLI                                                | Generated, rebuildable; not canonical truth   |
| `.ai-context/`                 | Repomix CLI                                                 | Generated context bundle; not canonical truth |
| `docs/` audit reports          | skill-ai-it audit mode                                      | Per-run findings                              |
| `docs/archive/`                | Manual archiving                                            | One-time artifacts no longer needed in root   |

See the `#### scripts/context-preflight.sh` section above under Conditionally-created files for the full template content and generation policy.

---

## Phase 5 — Update Parent

After creating/updating files in the target folder:

1. **Parent README.md** — if it has a `## Folder index` section, add an entry:
   ```markdown
   - [<folder>/](<folder>/)
     <One-line role description.>
     Project entry: [<folder>/README.md](<folder>/README.md)
     AI navigation: [<folder>/AI_NAVIGATION.md](<folder>/AI_NAVIGATION.md) ← only if navigation file exists
   ```

2. **Parent AGENTS.md** — if it has a `Child-project routing rules` section, add:
   ```markdown
   - Use [<folder>/](<path>) for <inferred purpose>.
   ```

3. Report all changes made: which files created, which updated, which parent entries added.

---

## Conventions Baked In

- `@` import in AGENTS.md = nearest parent AGENTS.md; absolute if global, relative if same repo
- Internal domain default for APN projects: `apn.net.au`
- Time-bound doc naming: `<slug>-YYYYMMDD_hhmm.md`
- Governance pointer chain always ends at: `/Volumes/Data/_ai/governance/README.md`
- Never overwrite existing AGENTS.md — append missing sections only
- Never duplicate AGENTS.md content in CLAUDE.md
- SCRATCHPAD.md is populated from live memory systems, not written from scratch — always query before writing
- CHANGELOG.md is the durable project/governance history ledger; append to it on meaningful bootstrap, navigation, refresh, audit, or promote runs
- Mark SCRATCHPAD.md synthesized content `KEEP`; warn user before clearing any `KEEP` content
- `AI_NAVIGATION.md` is the human-readable AI context router, not a knowledge dump
- `context-map.yaml` is the machine-readable task-to-context routing map
- `AGENTS.md` remains the bootstrap instruction file and must point agents to `AI_NAVIGATION.md`
- `.archcore/` is preferred for durable accepted decisions, rules, specs, guides, and plans when present
- `memory-bank/` is preferred for active context/progress/working decisions when present
- `graphify-out/` and `.ai-context/` are generated support artifacts, not canonical truth
- Repeat runs must update managed blocks only and preserve custom content
- Task recipes never call a bare `python3` / `node` — pin runtimes in `.mise.toml`, route recipes through `{{py}}` / `{{nd}}`, and keep the venv in the working-cache peer, never in the repo
- Generate `just bootstrap` and `just runtimes` alongside any pinned-runtime justfile; without `runtimes` the pinning cannot be verified quickly
- For risky changes to existing YAML/JSON, write `.proposed` files rather than overwriting

---

## Quality Check Before Completing

- [ ] All `@` import paths in AGENTS.md resolve to real files
- [ ] CLAUDE.md contains only the `@AGENTS.md` import line + additions section
- [ ] README.md Folder index links resolve to real subfolders
- [ ] Parent README/AGENTS updated if they exist
- [ ] If `archcore` CLI is available and the run mode allowed changes, `.archcore/` exists or the initialization failure is reported
- [ ] If `.archcore/` exists after `bootstrap`, `navigation-add`, or `refresh`, `ARCHCORE_PROMOTION_CANDIDATES.md` exists in the target root or the final report explicitly explains why it was not
  created/updated. After `promote` the opposite holds: the candidates file must be **gone**, its *never promote* reasoning carried into `.archcore/README.md`, and no governance surface still routing
  to it
- [ ] `ARCHCORE_PROMOTION_CANDIDATES.md` was read back or section-checked before final response when it was created or updated
- [ ] No `.archcore/adr/`, `.archcore/rules/`, `.archcore/specs/`, `.archcore/guides/`, or `.archcore/plans/` content files were written unless mode is `promote` or the operator explicitly authorized
  promotion
- [ ] CHANGELOG.md created or appended for meaningful governance/navigation changes
- [ ] Conditional files created only when the detection condition was met — state the reason
- [ ] No placeholder text (`<...>`) left in generated files
- [ ] If navigation module is enabled, `AI_NAVIGATION.md` exists and points to the correct context sources
- [ ] If navigation module is enabled, `context-map.yaml` exists or a `.proposed` update was written
- [ ] If scripts/tasks exist, `scripts/README.md` exists or a proposed update reports missing inventory
- [ ] Script/task safety labels are present for cataloged entries; uncataloged scripts are treated as `unknown`
- [ ] **No generated recipe calls a bare `python3`, `node`, `npx`, or `ruby`** — grep the justfile to confirm. Every runtime the recipes use is pinned in `.mise.toml` (Node as well as Python where a
  recipe shells out to a JS tool), the venv is in the working-cache peer rather than the repo, `_require-venv` guards the Python recipes, and `just runtimes` was **executed** and its output reported
- [ ] No `.python-version` was created alongside `.mise.toml` — one file owns the pin
- [ ] Third-party imports the tooling needs are declared in `requirements.txt` and installed by `bootstrap`; the project's own governance checker remains stdlib-only. Prove it by running the checker
  and the navigation validator **from the pinned venv**, not from the host interpreter
- [ ] `scripts/check_governance.py` exists, was **executed**, and its exit status is reported — never claim it passes without running it
- [ ] The checker covers every catalog the project maintains in **both** directions (nothing cataloged is missing; nothing present is uncataloged)
- [ ] Every Tier 3 check cites the project rule it enforces, and no invariant was invented that the project has not stated
- [ ] No existing check was narrowed, ignore-listed, or exempted to make this run green — if one failed, the project was fixed
- [ ] The checker is wired into the task runner, and the AGENTS.md governance-checks managed block is present with the real runner command substituted
- [ ] In `audit` mode, coverage gaps (artifact classes no check covers) were reported separately from failures
- [ ] `AGENTS.md` contains an AI navigation/context preflight block or equivalent local rule
- [ ] `repomix.config.json` includes governance files and excludes generated/heavy folders when created
- [ ] If `repomix.config.json` exists and `.archcore/` exists, `.archcore/**/*.md` is included; `ARCHCORE_PROMOTION_CANDIDATES.md` is included only while it exists (pre-promote)
- [ ] After `promote`: `.archcore/README.md` indexes every document written, the orphan check points at it rather than at the candidates file, and the candidates filename is registered in
  `CONDITIONAL_PATHS` so historical mentions do not fail path resolution
- [ ] If a repo-local `scripts/context-preflight.sh` was explicitly requested, it is executable or the user was told to run `chmod +x scripts/context-preflight.sh`
- [ ] Existing YAML/JSON files were not destructively regenerated during refresh mode
- [ ] Existing `.archcore/` documents were not directly edited unless explicitly authorized
- [ ] Drift/conflict findings were reported instead of silently resolved
- [ ] SCRATCHPAD.md was populated from memory systems (not blank) — or "no prior memory" note added if all sources empty
- [ ] SCRATCHPAD.md synthesized content is marked `KEEP`

---

## Context Compaction Recovery

When recovering agent context after compaction (e.g. new session, context window cleared), follow this procedure:

1. **Read `AI_NAVIGATION.md`** first — the navigation map tells you what files exist and what to read.
2. **Read `context-map.yaml`** for machine-readable file registry and companion-file rules.
3. **Load `.archcore/`** context if present (durable project truth).
4. **Regenerate `graphify-out/`**: `graphify update .`
5. **Regenerate `.ai-context/`**: `repomix --config repomix.config.json`
6. **Verify `SCRATCHPAD.md`** has current state. If empty, populate from memory backends.
7. **Verify `CHANGELOG.md`** is current with recent governance/navigation changes.
8. **Verify `AI_NAVIGATION.md` and `context-map.yaml` companion consistency.**

Label recovered entries: `Context recovered via skill-ai-it context-recovery procedure`.

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

## Deterministic Navigation-Control Automation

**`refresh` and `navigation-add` MUST run this sequence first.** It is not an optional appendix — it is the opening move of those modes, before any manual editing. Prose reasoning about managed blocks
is what this sequence exists to replace.

**The scripts live in the SKILL PACKAGE, not in the target project.** Target projects do not carry copies. Invoke them by absolute path against the target; do not `cd` into the target and run `python
scripts/...`, which resolves to the target's own `scripts/` and fails with "can't open file".

```bash
SKILL_DIR=/Volumes/Data/_ai/_skills/skills_stuff/specialists/project/skill-ai-it
TARGET=/path/to/target/project
```

**Recommended order:**

1. `python3 "$SKILL_DIR/scripts/upgrade_navigation_control_layer.py" --project-root "$TARGET" --dry-run` — preview changes
2. Review proposed changes
3. `python3 "$SKILL_DIR/scripts/upgrade_navigation_control_layer.py" --project-root "$TARGET"` — apply changes
4. `python3 "$SKILL_DIR/scripts/validate_navigation_control_layer.py" --project-root "$TARGET"` — validate
5. `python3 "$SKILL_DIR/scripts/check_expected_diff.py" --project-root "$TARGET"` — verify only expected files changed (target must be a git repo)
6. **Governance checker** — validate reports whether `scripts/check_governance.py` exists and is wired. If absent, create it now from `templates/check_governance.py` per the *Governance coherence
   checker* section; if present, extend its registries. This step is judgement, not mechanics: the universal checks are copied, but the Tier 3 invariants must be read out of the target's own stated
   rules. Run it and report its exit status
7. Regenerate `.ai-context/governance-pack.md` if the target has one — it embeds copies of the managed blocks and will otherwise keep serving the pre-upgrade version to agents
8. Agent fixes only for remaining validation failures

**Key rules:**

- Scripts are the **primary mechanism** for existing-project upgrade.
- Markdown patterns in `patterns/` are **policy/explanation**, not the primary execution path.
- Agents should not manually infer schema migrations when the upgrade script can do it.
- Always use `--dry-run` on first pass. Commit or review before applying.
- If YAML merging is too risky, the script writes `.proposed` files. Do not overwrite the live file.
- The scripts do not create `.archcore/`, `.ai-context/`, or `graphify-out/`.
- Generated outputs remain support-only. No automatic promotion.

Available scripts:

| Script                                         | Purpose                                                                |
| ---------------------------------------------- | ---------------------------------------------------------------------- |
| `scripts/upgrade_navigation_control_layer.py`  | Idempotent managed-block upgrade, marker fix, context-map key addition |
| `scripts/validate_navigation_control_layer.py` | Coherence validation with pass/warn/fail output                        |
| `scripts/check_expected_diff.py`               | Git-diff check against expected governance file changes                |

Available just targets (only where the project's `justfile` came from `templates/justfile`, which defines a `skill_dir` variable pointing at the skill package — a project whose justfile predates that
variable, or was hand-written, will not have these recipes at all; use the absolute-path form above):

- `just nav-upgrade-dry-run`
- `just nav-upgrade`
- `just nav-validate`
- `just nav-check-diff`
- `just check` — the project's own governance checker, once it has one

Override the skill location per invocation with `just skill_dir=/path/to/skill-ai-it nav-validate`.

---

## Audit Output Format

For `audit`, `refresh`, `navigation-add`, and repeat runs, finish with this report shape:

```markdown
## skill-ai-it result

Mode: <bootstrap | navigation-add | refresh | audit | promote>
Target: <path>
Project type: <code | docs | ops | comms | mixed>

### Created
- <file> — <why>

### Updated
- <file> — <managed section or exact area updated>
- `CHANGELOG.md` — appended summary of meaningful governance/navigation changes

### Proposed only
- <file.proposed> — <why not applied directly>

### Skipped
- <file> — <reason, e.g. already complete / user-authored / risky overwrite>

### Drift / conflicts
- <conflict or "none found">

### Next recommended action
- <one precise next action>
```

## Public Pattern Inspiration

This skill intentionally borrows proven patterns from public AI-agent context tooling:

- `AGENTS.md` pattern: predictable repo-local agent instructions and bootstrap rules.
- Archcore pattern: Git-native project truth for decisions, rules, conventions, specs, and plans.
- Memory Bank pattern: Markdown-based active context, progress, decisions, patterns, and open questions.
- Graphify pattern: generated relationship/navigation graph for code, docs, diagrams, and mixed project content.
- Repomix pattern: deterministic AI-readable context pack to survive context compaction and reduce missed files.
- MCP pattern: expose external context/tools through standard agent-accessible interfaces where available.

These tools are optional integrations. The skill must still work with plain files only.

## Required Follow-Up Packaging Task

If this skill is being maintained as a reusable package, extract the embedded fallback templates into these files:

- `templates/AI_NAVIGATION.md`
- `templates/context-map.yaml`
- `templates/repomix.config.json`
- `templates/AGENTS-navigation-block.md`
- `templates/justfile`
- `templates/scripts-README.md`
- `templates/context-preflight.sh`
- `patterns/archcore-routing.md`
- `patterns/memory-bank-structure.md`
- `patterns/drift-audit.md`
- `patterns/script-task-audit-checklist.md`
- `CHANGELOG.md` as the skill-package governance history ledger

After extraction, keep `SKILL.md` focused on orchestration logic and keep detailed reusable content in the template/pattern files.
