---
Title: Central project tooling plan (govcheck, just modules, hooks, configs)
Category: plan
Status: proposed
Authority: proposal; nothing here is decided until the operator approves it stage by stage
Scope: >-
  Tooling copied into each project under /Volumes/Data/_ai/_project/project_stuff (govcheck, justfile governance recipes, Pad and commit-gate
  recipes, the apn pre-commit hook, lint configs) and where its central home should be
Last reviewed: 2026-11-11
Summary: >-
  Two read-only surveys (2026-11-11) found the same governance engine, checks and justfile recipes copied into 3 to 14 projects and drifting.
  Recommends one project standard (Core, Modules, Local) with a per-project profile, declared deviations and a conformance check, served from
  skill-ai-it as imported packages run from a pinned worktree, with a consumer check, in gated stages with rollout waves. Reviewed against
  skill-coder and skill-systems-architect on 2026-11-11; section 7 gives the proposed scripts with the excerpts that carry their logic, and the language chosen for each job.
---

# Central project tooling plan

Prepared by: Malik Ahmad. Written 2026-11-11 from a unified-network-controller (UNC) session, after the operator asked which project scripts should be central and whether skill-ai-it or another home
should hold them. Nothing in this plan has been done; each stage starts only on the operator's go.

<!-- toc-depth: 3 -->
## Contents

- [1. Why now](#1-why-now)
- [2. What the surveys found](#2-what-the-surveys-found)
  - [2.1 govcheck (UNC, smc-resiliency, islam)](#21-govcheck-unc-smc-resiliency-islam)
  - [2.2 Other categories](#22-other-categories)
- [3. Where should it live](#3-where-should-it-live)
- [4. The project standard](#4-the-project-standard)
  - [4.1 Three layers](#41-three-layers)
  - [4.2 The profile: the gov-map, kept in `context-map.yaml`](#42-the-profile-the-gov-map-kept-in-context-mapyaml)
  - [4.3 Other maps: which exist, which to add](#43-other-maps-which-exist-which-to-add)
  - [4.4 Map formats](#44-map-formats)
  - [4.5 Seeing drift: the conformance check](#45-seeing-drift-the-conformance-check)
  - [4.6 How the standard changes](#46-how-the-standard-changes)
- [5. Stages](#5-stages)
- [6. Stage details](#6-stage-details)
  - [S0. Coordinate and freeze](#s0-coordinate-and-freeze)
  - [S1. Safety net](#s1-safety-net)
  - [S1a. Trials](#s1a-trials)
  - [S1b. Record-file fix](#s1b-record-file-fix)
  - [S2. Central govcheck engine](#s2-central-govcheck-engine)
  - [S3. Merge drifted checks](#s3-merge-drifted-checks)
  - [S4. Importable just modules](#s4-importable-just-modules)
  - [S4b. Decisions into Pad (per project)](#s4b-decisions-into-pad-per-project)
  - [S5. apn pre-commit hook](#s5-apn-pre-commit-hook)
  - [S6. Retire duplicates](#s6-retire-duplicates)
  - [S7. Shared config bases](#s7-shared-config-bases)
  - [S8. Update the standard](#s8-update-the-standard)
- [7. Proposed scripts](#7-proposed-scripts)
  - [7.1 consumer_check.py: same output before and after](#71-consumer_checkpy-same-output-before-and-after)
  - [7.2 standard_refresh.py: move a project to the next tag](#72-standard_refreshpy-move-a-project-to-the-next-tag)
  - [7.3 conformance.py: the standard, checked](#73-conformancepy-the-standard-checked)
  - [7.4 cue_seam.py: the one place that calls cue](#74-cue_seampy-the-one-place-that-calls-cue)
  - [7.5 promotion_scan.py: candidates already used elsewhere](#75-promotion_scanpy-candidates-already-used-elsewhere)
  - [7.6 toml_emit.py: the small TOML writer for generated maps](#76-toml_emitpy-the-small-toml-writer-for-generated-maps)
  - [7.7 tracker_feeds.py: one loop over tracker-map.toml](#77-tracker_feedspy-one-loop-over-tracker-maptoml)
  - [7.8 pad_toml_probe.py: the Pad upgrade test](#78-pad_toml_probepy-the-pad-upgrade-test)
  - [7.9 env_map_from_plan.py: machine facts from the OpenTofu plan](#79-env_map_from_planpy-machine-facts-from-the-opentofu-plan)
  - [7.10 job_runs.py: append one measured run](#710-job_runspy-append-one-measured-run)
  - [7.11 Language choice](#711-language-choice)
- [8. Not promoted, and why](#8-not-promoted-and-why)
- [9. Risks and coordination](#9-risks-and-coordination)
- [10. Decisions for the operator](#10-decisions-for-the-operator)
- [11. Evidence](#11-evidence)

## 1. Why now

Two events on 2026-11-11 showed both failure modes of the current model:

| Event                                                                       | What went wrong                                                               | Failure mode                           |
| --------------------------------------------------------------------------- | ----------------------------------------------------------------------------- | -------------------------------------- |
| skill-ai-it moved its scripts into                                          | Five apn justfiles (cambium-swap, smc-file-writing-analysis, vocus, voip,     | Copied recipes: one central change, N  |
|   subfolders (`scripts/{checks,records,navigation,markdown,adoption}/`)     |   UNC) are being repointed by hand, one recipe at a time                      |   hand edits                           |
| `docs/history/` grouped by kind (smc-resiliency, then UNC)                  | UNC's own `check_docs_indexed` failed 367 times; `check_constant_sync` in UNC | Copied checks drift; a fix in one      |
|                                                                             |   and islam lacks the `docs/history/` skip that smc-resiliency added          |   project never reaches the others     |

The opposite risk is also real: 14 projects run skill-ai-it's scripts straight from its source folder, so one session's edit reaches all of them at once, unannounced. The plan addresses both: import
instead of copy, and check every consumer before a central change is pushed.

## 2. What the surveys found

Measured by hashing function bodies (govcheck) and whitespace-stripped recipe bodies (justfiles); diff line counts for whole files.

### 2.1 govcheck (UNC, smc-resiliency, islam)

| Item                                                 | Projects            | Drift                                                                 | Class                                           |
| ---------------------------------------------------- | ------------------- | --------------------------------------------------------------------- | ----------------------------------------------- |
| Engine `core.py`, helpers `read`, `without_code`,    | all 3               | identical (docstrings only); matches `templates/govcheck/core.py`     | PROMOTE                                         |
|   `table_rows`, `members`                            |                     |                                                                       |                                                 |
| `check_index_links`, `check_govcheck_structure`      | all 3               | identical, also in the template                                       | PROMOTE                                         |
| `check_count_claims`, `check_catalog_coverage`,      | all 3               | identical or docstring only                                           | PROMOTE-WITH-CONFIG                             |
|   `check_derived_freshness`,                         |                     |                                                                       |                                                 |
|   `check_append_only_grain`,                         |                     |                                                                       |                                                 |
|   `check_evidence_provenance`                        |                     |                                                                       |                                                 |
| `check_constant_sync`                                | all 3               | smc-resiliency adds a type guard and the `docs/history/` skip         | PROMOTE-WITH-CONFIG (smc-resiliency's version)  |
| `check_interpreter_pinning`                          | all 3               | smc-resiliency most complete (run-by-path, script interpreters)       | PROMOTE-WITH-CONFIG (smc-resiliency's version)  |
| `check_task_recipes`                                 | all 3               | UNC handles `mod` and `just x::y`; islam skips `just fetch-*` globs   | PROMOTE-WITH-CONFIG (merge both)                |
| `check_referenced_paths`                             | all 3               | 0.67 to 0.83 similar: UNC sibling checkouts and moved paths, islam    | PROMOTE-WITH-CONFIG (pluggable resolvers)       |
|                                                      |                     |   upstream owners and external roots                                  |                                                 |
| Docs indexed (`check_docs_indexed` UNC,              | 2                   | different logic: per-folder readme vs one docs index; UNC             | PROMOTE-WITH-CONFIG (two modes)                 |
|   `check_docs_index_coverage` islam)                 |                     |   accepts `docs/history/<kind>/`                                      |                                                 |
| `ai_it_script` loader and the `target_map` /         | UNC, smc-resiliency | smc-resiliency re-copied the loader                                   | PROMOTE                                         |
|   `plan_timeline` wrappers                           |                     |                                                                       |                                                 |
| `check_write_gates` (UNC)                            | 1                   | re-implements skill-coder `write_gates.py`, which was promoted        | RETIRE (smc-resiliency already                  |
|                                                      |                     |   from it                                                             |   calls skill-coder)                            |
| `check_flow_map`                                     | UNC, smc-resiliency | 0.08 similar; both call skill-drawio                                  | belongs to skill-drawio, not here               |
| `check_code_map`                                     | UNC, smc-resiliency | different scope; wraps skill-coder `code_map.load`                    | PROJECT-ONLY for now                            |

Defects found on the way: smc-resiliency's `structure.py` imports names its `config.py` does not define and is not registered (dead code that would fail if registered). Only UNC has govcheck tests
(`tests/test_govcheck_*.py`, 3 files); skill-ai-it has none for govcheck.

### 2.2 Other categories

| #   | Item                                  | Projects             | Drift                                                               | Suggested home                  | Class                   |
| --- | ------------------------------------- | -------------------- | ------------------------------------------------------------------- | ------------------------------- | ----------------------- |
| 1   | Records recipes `stale`, `docs`,      | 10                   | identical but for the python variable name (`py`, `VENV`, `PYTHON`, | skill-ai-it                     | PROMOTE-WITH-CONFIG     |
|     |   `history`, `history-show`, `rotate` |                      |   `ai_py`); `rotate` has 6 variants                                 |   `just/governance.just`        |                         |
| 2   | Navigation and section recipes        | 5                    | identical in 4 apn projects; islam points at the installed copy;    | same module                     | PROMOTE                 |
|     |   (`nav-*`, `outline`, `section`,     |                      |   snake vs kebab names                                              |                                 |                         |
|     |   `changelog-entry`, `roles`,         |                      |                                                                     |                                 |                         |
|     |   `budget`, `move-sections`)          |                      |                                                                     |                                 |                         |
| 3   | `govern`                              | UNC, smc-resiliency, | cambium lacks 4 steps                                               | same module                     | PROMOTE                 |
|     |                                       |   ES (identical),    |                                                                     |                                 |                         |
|     |                                       |   cambium (slim)     |                                                                     |                                 |                         |
| 4   | `skill-ai-it/templates/justfile`      | copied once          | never re-synced; nothing imports it                                 | becomes the module              | ALREADY-CENTRAL         |
|     |   (204 lines)                         |   per project        |                                                                     |                                 |   (as copy)             |
| 5   | `pad-trackers`, `pad-export`,         | UNC, smc-resiliency  | identical                                                           | skill-pad `just/pad.just`       | PROMOTE                 |
|     |   `plan-timeline`, `commit-gate`      |                      |                                                                     |                                 |                         |
| 6   | `commit-project`,                     | UNC,                 | scripts central in `apn/scripts`; recipes in 3 variants             | `apn/apn.just`                  | PROMOTE-WITH-CONFIG     |
|     |   `sync-projects` recipes             |   smc-resiliency, ES |                                                                     |                                 |                         |
| 7   | apn pre-commit hook                   | all apn projects     | `apn/.git/hooks/pre-commit` is a symlink into                       | `apn/scripts/githooks/` plus    | PROMOTE (wrong owner)   |
|     |                                       |                      |   `unified-network-controller/scripts/githooks/pre-commit`, which   |   per-project drop-ins          |                         |
|     |                                       |                      |   carries UNC-only logic                                            |                                 |                         |
| 8   | UNC `scripts/render/roadmap_trim.py`  | UNC                  | 39-line wrapper of the central script                               | call skill-ai-it directly       | RETIRE                  |
| 9   | `scripts/check_governance.py`         | 8                    | UNC, smc-resiliency, islam: 57-line loaders; cambium, ES, health,   | the skill-ai-it loader          | PROMOTE                 |
|     |                                       |                      |   japan, psy-assess: stale 684-line template copies (230 to 905     |                                 |   (migration backlog)   |
|     |                                       |                      |   diff lines)                                                       |                                 |                         |
| 10  | `check_versions.py`                   | UNC, smc-resiliency  | large (443 diff lines); pin locations project-specific              | skill-coder engine plus         | PROMOTE-WITH-CONFIG     |
|     |                                       |                      |                                                                     |   project adapter               |   (low priority)        |
| 11  | `.markdownlint-cli2.jsonc`            | 7 copies             | 3 to 30 lines from the template; none `extends`; 4 projects         | skill-ai-it base,               | PROMOTE-WITH-CONFIG     |
|     |                                       |   plus template      |   have none                                                         |   projects `extends`            |                         |
| 12  | `ruff.toml`                           | smc-resiliency,      | all different                                                       | skill-coder base                | PROMOTE-WITH-CONFIG     |
|     |                                       |   ntg, skill-ai-it   |                                                                     |                                 |                         |
| 13  | Tests of central code                 | —                    | skill-ai-it has no tests for `doc_freshness.py`, `file_headers.py`, | the owning skill                | PROMOTE                 |
|     |                                       |                      |   `docstring_ratchet.py`, `check_expected_diff.py`, though 10       |                                 |                         |
|     |                                       |                      |   projects and the apn hook run them; `project_sync_selftest.sh`    |                                 |                         |
|     |                                       |                      |   runs only from ES                                                 |                                 |                         |
| 14  | ASCII diagram tools                   | UNC; smc-resiliency  | none (one copy), but a cross-project path dependency                | skill-ai-it `scripts/markdown/` | PROMOTE (UNC code-map   |
|     |   (`ascii_box_render.py` 77 lines,    |   calls UNC's files  |                                                                     |   (UNC's code-map suggests      |   `candidate`, its      |
|     |   `ascii_box_check.py` 122 lines,     |   by relative path;  |                                                                     |   `scripts_stuff/python`;       |   condition met)        |
|     |   both tested)                        |   used on this plan  |                                                                     |   skill-ai-it keeps them with   |                         |
|     |                                       |                      |                                                                     |   the other markdown tools and  |                         |
|     |                                       |                      |                                                                     |   the standard)                 |                         |

## 3. Where should it live

| Home                                             | For                                                                 | Against                                                                     |
| ------------------------------------------------ | ------------------------------------------------------------------- | --------------------------------------------------------------------------- |
| **A. skill-ai-it**, as separate packages         | Already the central code 14 projects run by path (`ai_it := ...` in | Scope grows from "governance docs" toward "runtime library"; several        |
|   (`scripts/govcheck/`, `just/`)                 |   each justfile); has 27 test files, the govcheck template and the  |   sessions edit it; no version pin, so a change reaches every project       |
|                                                  |   pattern doc; no new path to wire                                  |   at once                                                                   |
| **B. A new skill** (for example `skill-govcheck`) | Narrow scope, smaller files to read                                 | A skill is agent instructions; a code library with no agent workflow is not |
|                                                  |                                                                     |   one; one more absolute path in every project; splits the govcheck         |
|                                                  |                                                                     |   template from the bootstrap that installs it                              |
| **C. A versioned package in** **`tools_stuff`**  | Real versions: each project pins and upgrades on purpose, as UNC's  | An install step per project; 4 projects have no venv recipe; slower to      |
|   (installed or run with a pinned version        |   "versions are pinned" rule asks                                   |   change while the design is still moving                                   |
|   per project)                                   |                                                                     |                                                                             |
| **D. `/Volumes/Data/_ai/governance`**            | Holds the standards and hooks                                       | Not a code library; holds no lint, ruff or just files today                 |

**Recommendation: A now, built so it can become C.** The code already lives in skill-ai-it and runs from there; moving it elsewhere adds a path and a migration without fixing either failure mode. What
fixes them is (1) import instead of copy, and (2) a **consumer check**: a read-only script that runs every consumer project's `just check` before a skill-ai-it change is pushed (skill-drawio's
`consumer_check` is the precedent). Each package gets a `VERSION` line in semantic versioning (skill-coder version-control-and-review.md:136) and a CHANGELOG section so it can be lifted out cleanly;
the dated `2026.11` stays the label of the standard.

```text
+----------------------------------------------+-------------------------------------------------+
|  TODAY: copy at bootstrap                    |  TARGET: import, with a consumer check          |
+----------------------------------------------+-------------------------------------------------+
|  skill-ai-it template                        |  skill-ai-it packages (Core, versioned)         |
|       |  copied once                         |       |  imported by every project              |
|       v                                      |       v                                         |
|  project A copy --> drifts                   |  project A: config.py + local checks            |
|  project B copy --> drifts                   |  project B: config.py + local checks            |
|  project C copy --> drifts                   |  project C: config.py + local checks            |
|                                              |                                                 |
|  a fix in A never reaches B or C;            |  one fix reaches all; the consumer check        |
|  a path move means N hand edits              |  runs every project's check before a push       |
+----------------------------------------------+-------------------------------------------------+
```

**Version pin (operator, 2026-11-11; both reviews):** 14 projects run skill-ai-it's working folder, so an edit there reaches them before any push, and a `standard.version` label alone protects
nothing. Until home C, projects run a **pinned checkout**: a `git worktree` of skill-ai-it at a tag (`standard-2026.11`), outside the folder being edited. Each project's `ai_it` path points at that
worktree; `standard.version` names the tag; `just refresh` moves a project to the next tag and diffs its check output in the same change; conformance fails when the label and the checked-out tag
differ. A new tag is cut only after the consumer check passes on it. This meets skill-coder's rule that a project importing skill code pins the revision (runtime-boundaries.md:59) and
skill-systems-architect's "pin dependencies" (automation-and-safety.md:55).

```text
+------------------------------+--------------------------+-----------------------------+
|  1. AUTHORS EDIT             |  2. TAG CUT              |  3. PROJECTS RUN THE TAG    |
|  skill-ai-it working folder  |  consumer check passes,  |  ai_it := shared worktree;  |
|  (never run by projects)     |  tag standard-2026.11    |  refresh moves to next tag  |
+------------------------------+--------------------------+-----------------------------+
```

**Who cuts tags, and how projects follow (proposed, for the operator to decide).** The pin's cost is that a central fix reaches no project until a tag is cut and each project refreshes, so projects
can sit on different tags and one check can pass here and fail there. To keep that from becoming per-project work again:

- the session that changes skill-ai-it cuts the tag, right after the consumer check passes on it; no separate release owner;
- projects follow in one central batch, not one by one: `just consumers --refresh --apply` moves every project in the waves of section 5, saves each project's before and after output, and stops at the
  first unaccepted difference;
- a project that must stay behind declares it (`item = "pin:standard-2026.11"`, with reason and `review_by`); conformance reports any project more than one tag behind without such a declaration;
- an urgent fix is a patch tag plus the same batch refresh on the same day.

**Extraction trigger (when to move to C):** any one of these, recorded in skill-ai-it's ROADMAP:

- a central change breaks a consumer project after passing the consumer check (the check was not enough);
- a project needs to stay on an older tag for more than two weeks while others move on (the worktree pin is no longer enough);
- the govcheck package passes 3,000 lines or a second team uses it.

Two items are not skill-ai-it's: the Pad recipes belong to **skill-pad** (`just/pad.just`), and the apn hub tooling (hook, `commit-project`, `sync-projects`) to **`apn/scripts`**, which already holds
those scripts.

## 4. The project standard

The operator's aim (2026-11-11): every project starts standard from skill-ai-it, then drifts; projects cannot all be identical, but there must be one standard they follow, so the operator does not
explain to each project how to do the same thing. Imports (section 3) stop copies drifting; this section says **what the standard is**, **how a project may differ**, and **how drift is seen**.

### 4.1 Three layers

| Layer                           | What it holds                                                                  | How a project gets it                   | May a project change it?                |
| ------------------------------- | ------------------------------------------------------------------------------ | --------------------------------------- | --------------------------------------- |
| **Core** (every project)        | records and rotation (`docs/history/<kind>/`), navigation files, doc           | imported from skill-ai-it at bootstrap  | No. A change is made centrally, for     |
|                                 |   freshness, file headers, the govcheck engine and T1 checks, the governance   |   and on refresh                        |   everyone, through the consumer check  |
|                                 |   just module, the markdownlint base, the ASCII diagram tools                  |                                         |                                         |
| **Modules** (when a trigger exists) | Pad (skill-pad), apn hub (`apn/scripts`), flow maps (skill-drawio), code map   | switched on by name in the project's    | Choose which modules; not               |
|                                 |   and write gates (skill-coder), archcore, T2 checks                           |   profile when its trigger              |   their contents                        |
|                                 |                                                                                |   artifact exists                       |                                         |
| **Local** (this project only)   | project-only checks (T3: domain invariants), domain recipes, project data      | written in the project                  | Yes, freely                             |
|                                 |   in `config.py`                                                               |                                         |                                         |

```text
+------------------------------------------------------------------------------------------------+
|  a project (for example unified-network-controller)                                            |
+-------------------------------+--------------------------------+-------------------------------+
|  CORE (every project)         |  MODULES (when triggered)      |  LOCAL (this project only)    |
|                               |                                |                               |
|  records and rotation         |  pad          (skill-pad)      |  domain checks (T3)           |
|  navigation files             |  apn-hub      (apn/scripts)    |  domain recipes               |
|  doc freshness, file headers  |  drawio-flows (skill-drawio)   |  config.py data               |
|  govcheck engine + T1 checks  |  code-map     (skill-coder)    |                               |
|  governance just module       |  archcore, T2 checks           |                               |
|  markdownlint base            |                                |                               |
|  ASCII diagram render, check  |                                |                               |
|  imported; changed centrally  |  switched on in the profile    |  written in the project       |
+------------------------------------------------------------------------------------------------+
|  context-map.yaml, standard block: version = "2026.11", modules = [...],                       |
|  deviations: each with item, reason, by and review_by                                          |
+------------------------------------------------------------------------------------------------+
```

Anything the operator would otherwise have to explain again to a second project belongs in Core or a Module, not Local.

### 4.2 The profile: the gov-map, kept in `context-map.yaml`

The operator asked (2026-11-11) whether a "gov-map" is needed. The function is: one file per project that says which standard it follows, which modules are on, and where it differs. It should not be a
new file. `context-map.yaml` is already that file in 17 projects: skill-ai-it's template writes it at bootstrap, and it already carries a `skill_ai_it_version` field. That field shows the drift this
plan is about:

| `skill_ai_it_version` in context-map.yaml   | Projects |
| ------------------------------------------- | -------- |
| `2026-10-07-snake-case-recipes-v1`          | 4        |
| the current stamp (compact v2, 2026-10-14)  | 3        |
| `2026-10-10-compact-v1`                     | 1        |
| `2026-05-29-ai-navigation-control-layer-v1` | 1        |
| no version field                            | 8        |

So the gov-map is a `standard:` block added to `context-map.yaml` (fold before create), replacing `skill_ai_it_version`:

```yaml
standard:
  version: "2026.11"                 # the skill-ai-it standard this project follows (replaces skill_ai_it_version)
  modules: [pad, apn-hub, drawio-flows, code-map]
  python: "{{py}}"                   # the one interpreter name the shared recipes use
  deviations:                        # declared differences from Core, each with reason, owner and review date
    - item: "recipe:rotate"
      reason: "UNC trims ROADMAP with its own wrapper (to be retired in S6)"
      by: "operator, 2026-11-11"
      review_by: "2026-12-11"
```

A deviation is allowed, but only declared: what differs, why, who agreed, and when it is looked at again. An expired `review_by` is a finding.

### 4.3 Other maps: which exist, which to add

File types follow one rule (operator, 2026-11-11):

- **TOML** for a registry keyed by id (`[jobs.<id>]`, `[modules."<path>"]`): a duplicated id fails at parse, which YAML does not catch (it keeps the last of two equal keys and never checks ids in a
  list); tested 2026-11-11.
- **YAML** for nested data, graphs and long rows (TOML cannot wrap an inline table across lines, so a table of long rows stays YAML).
- **JSON Lines** (`.jsonl`) for records a script appends (measured runs, conformance results): one line per record, history kept, never rewriting a hand-written file (Python reads TOML but cannot
  write it, and rewriting loses comments).
- **Markdown with front matter** stays the format for documents; a map that would copy a document's facts is generated from it, or from the tool that owns them, never kept twice.

**Levels.** Every map has one of three levels:

| Level     | Meaning                                                            | What conformance does                                                                                  |
| --------- | ------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------ |
| **Mandatory** | every project the condition covers has it                          | fails when it is missing                                                                               |
| **Advised** | recommended wherever the condition holds                           | warns when it is missing; a project may decline with a declared deviation (reason, owner, review date) |
| **Optional** | used when the project wants it, switched on in `standard: modules` | says nothing when it is missing; checks it when present                                                |

**Existing maps, and the one central map to add:**

| Map                                  | Level     | When it applies                    | Where today                              | Role in the standard                                              |
| ------------------------------------ | --------- | ---------------------------------- | ---------------------------------------- | ----------------------------------------------------------------- |
| `context-map.yaml`                   | Mandatory | every project                      | 17 projects                              | Core: navigation routing plus the `standard:` block (the gov-map, |
|                                      |           |                                    |                                          |   section 4.2)                                                    |
| `code-map.toml`                      | Mandatory | every project with scripts         | UNC, smc-resiliency                      | Core: every script's status (`project_only`, `candidate`,         |
|                                      |           |                                    |                                          |   `promoted`); without it a project cannot report promotion       |
|                                      |           |                                    |                                          |   candidates (section 4.6)                                        |
| `versions.toml`                      | Advised   | a project that deploys images or   | UNC, smc-resiliency                      | Module `version-pins`                                             |
|                                      |           |   pins tools                       |                                          |                                                                   |
| `target-map.yaml`,                   | Optional  | a staged project with a            | UNC, smc-resiliency                      | Module `planning`                                                 |
|   `plan-timeline.yaml`               |           |   plan tracker                     |                                          |                                                                   |
| `docs/flows/flows.yaml` (assembled   | Optional  | a project that draws its flows     | UNC, smc-resiliency                      | Module `drawio-flows` (skill-drawio)                              |
|   from `parts/`)                     |           |                                    |                                          |                                                                   |
| `guide-map.yaml`                     | Optional  | a project that renders team guides | UNC                                      | Local: UNC's team guides                                          |
| `tracker-map.toml` (new,             | Mandatory | a project that uses an external    | none yet (settings sit in justfile       | Module `tracker`: which tracker source feeds which repo file, the |
|   tool-neutral; beside the tool's    |           |   work tracker (the `tracker`      |   arguments, already drifted between UNC |   focus export, the commit gate; read by the tracker just module  |
|   own file, `.pad.toml` today)       |           |   module; Pad today)               |   and smc-resiliency)                    |   (S4); the tool is a setting, so a new tool needs no rename      |
| **`consumers.toml`** (new, central   | Mandatory | skill-ai-it only (one file)        | none yet                                 | The only map to add for certain: which projects use the standard  |
|   in skill-ai-it)                    |           |                                    |                                          |   and how to check them (path, check command); read by            |
|                                      |           |                                    |                                          |   `just consumers` and the conformance table (S1)                 |

**Candidate maps (the operator decides which to adopt; levels proposed).** Each holds something otherwise explained again per project. Each adopted map gets a schema and a check in skill-ai-it, so it
is written once.

| Map                        | Level (proposed) | Holds                                                    | Fits                               | Exists partly today         | Value                  |
| -------------------------- | ---------------- | -------------------------------------------------------- | ---------------------------------- | --------------------------- | ---------------------- |
| `rule-map.toml`            | Advised          | each rule's id, its source anchor (`AGENTS.md#heading`)  | every project                      | no                          | high: a rule with no   |
|                            |                  |   and what enforces it (or `none`); never the            |                                    |                             |   check is where       |
|                            |                  |   rule's text                                            |                                    |                             |   drift starts         |
| `job-map.toml`             | Advised          | the map: each repeated job's schedule, runtime budget,   | a project with repeated jobs (UNC, | scattered                   | high: "efficiency is   |
|   + `job-runs.jsonl`       |                  |   owner (hand-written); the log: one line per measured   |   smc-resiliency, profitability)   |   (`CYCLE_BUDGET_MIN`,      |   part of done" has no |
|                            |                  |   run (script-appended)                                  |                                    |   CHANGELOG lines)          |   single home          |
| `access-map.toml` (or a    | Advised          | each script that writes to or reaches a system: target,  | a project that touches production  | partly, UNC `code-map.toml` | high where production  |
|   section                  |                  |   gate (`--apply`), credential entry, approver           |   (UNC, smc-resiliency, ansible)   |   `write_gates`             |   is touched           |
|   of `code-map.toml`)      |                  |                                                          |                                    |                             |                        |
| `data-map.yaml`            | Optional         | inputs, transforms and outputs as a graph, so a stale    | a data pipeline (vocus, opticomm,  | partly, govcheck            | medium                 |
|                            |                  |   output is found                                        |   voip, cambium-swap)              |   `DERIVED` lists           |                        |
| `decision-map.toml`        | Optional         | each decision's status, category, date, constraints,     | a project that records decisions   | inside UNC's options        | medium                 |
|   (generated)              |                  |   what supersedes it and who relies on it; generated     |   (UNC, smc-resiliency,            |   register (Markdown)       |                        |
|                            |                  |   from the tracker's Decisions collection (Pad today),   |   enterprise-strategy)             |                             |                        |
|                            |                  |   never edited                                           |                                    |                             |                        |
| `sources.yaml`             | Optional         | each load-bearing claim: source, evidence label, date    | a research project (cambium-swap,  | yes in skills               | medium                 |
|                            |                  |                                                          |   profitability, islam)            |                             |                        |
| `env-map.toml` (generated  | Optional         | environments and hosts, how each is reached (proxy),     | a project with deployed            | spread over `instance.conf` | medium                 |
|   from OpenTofu where      |                  |   what runs where                                        |   environments                     |   and AGENTS rules          |                        |
|   it exists)               |                  |                                                          |   (UNC, smc-resiliency)            |                             |                        |
| `term-map.yaml`            | Optional         | domain words, dictation aliases, words banned in         | a project with dictated input or   | no                          | low to medium          |
|                            |                  |   user-facing text                                       |   user-facing text rules (UNC)     |                             |                        |

Not recommended: a test map (the rule map covers which check proves which rule) and a communications map (only enterprise-strategy would use it).

Two formats beyond YAML, TOML and JSON are used (operator, 2026-11-11): **CUE** for the schemas and the cross-file rules of the standard (section 4.4), and **HCL** as the source of the environment map
wherever infrastructure is declared in OpenTofu (no hand-written copy). CUE needs the `cue` binary, pinned in skill-ai-it's `versions.toml`; HCL is read through `tofu output -json`, so no HCL parser
is needed.

Formats considered and not used (operator asked for whatever suits best, 2026-11-11):

| Format                          | Why not                                                                                                                                         |
| ------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| CSV or TSV                      | no nesting and no comments; fine for exports, not for maps                                                                                      |
| SQLite                          | not readable in a git diff; history and review are lost                                                                                         |
| DOT (Graphviz) for the data map | Python cannot read it without an extra library; the YAML graph can be rendered to DOT when a picture is wanted                                  |
| Pkl                             | does the same job as CUE through inheritance and overrides; one validation language is enough, and CUE's constraints fit rules that cross files |
| KDL                             | pleasant for hand-written nested files, but the only candidate (flow-map parts) follows skill-drawio's YAML standard; no gain                   |
| JSON for hand-written maps      | no comments; kept for schemas, machine-written baselines and JSON Lines records                                                                 |

### 4.4 Map formats

Rules every map follows:

- **Header: a `meta` block (operator, 2026-11-11).** Every map opens with the same keys as Markdown front matter, held as data so the normal parser reads them and the schema checks them: `title`,
  `status`, `authority`, `scope`, `last_reviewed`, `summary`, plus `schema` (the format version its check expects). YAML: a top-level `meta:` mapping; TOML: a `[meta]` table. Keys map one to one onto
  front matter (`Title` to `title`, `Last reviewed` to `last_reviewed`), so doc freshness and `just docs` treat a map like a document. Literal `---` front matter is not used: `yaml.safe_load` rejects
  a file with two documents and TOML has no front matter. A list-shaped part (`docs/flows/parts/*.yaml`) and a generated file (`flows.yaml`, with its GENERATED banner) are exempt; the map's
  `master.yaml` carries the `meta` block. Existing maps gain it at their next edit; tool keys they already have (`title`, `updated`, `stale_after_days`) stay until their tool is changed.
- **Ids** are stable and kebab-case; **paths** are relative to the project root; **dates** are ISO (`2026-11-11`); an operator decision is written `by: "operator, 2026-11-11"`.
- **One schema per map, in CUE** (operator, 2026-11-11), in skill-ai-it: `schemas/<map>.cue` for each map's shape, and one `schemas/standard.cue` for the rules that cross files (each switched-on
  module has its map; each `[[feed]]` file exists and is generated; each `enforced_by` names a real check or script; each `versions.toml` value matches every place it is pinned). `cue vet` checks the
  maps where they are, YAML, TOML and JSON, so the maps keep their formats. JSON Schema for the editor lines below is exported from the CUE (`cue` can emit JSON Schema: UNVERIFIED for the pinned
  version, checked in S1a). A project never writes its own checker for a standard map. `cue` is a binary dependency, so it is reached through one module (`scripts/standard/cue_seam.py`): resolved by
  path from skill-ai-it's pin, called with a timeout, covered by an upgrade test on planted-error fixtures, never installed into a project. Inside a project's `just check`, conformance runs on the
  Python standard library only and says plainly when the CUE pass was skipped; the full CUE pass runs centrally from `just consumers --conformance` (skill-coder runtime-boundaries.md:56, :58;
  dependencies.md:21-23).
- **Generated outputs** (trackers, drawings, guides) name the map they come from and are never edited by hand.
- **Editor validation.** Each map names its schema on its first line, so VS Code flags a wrong key while typing: YAML `# yaml-language-server: $schema=<path to schema>`, TOML `#:schema <path to
  schema>`. How the two editor extensions read these lines is UNVERIFIED (from memory) and is checked first in S1.

The layouts below are the standard shape: existing maps as UNC writes them today (read 2026-11-11), candidates as proposed. Keys shown are the required ones plus the common optional ones; `...` marks
repetition.

#### Existing maps

**`context-map.yaml`** (project root; Core): the machine-readable router, plus the gov-map.

```yaml
meta:
  schema: 1
  title: Context map
  status: current
  authority: source of truth for its subject
  scope: <project>
  last_reviewed: 2026-11-11
  summary: Machine-readable router for agents, and the project's standard block (gov-map).
version: 1
project:
  name: unified-network-controller
  context_policy: AI_NAVIGATION.md is the human-readable router; this file is the machine-readable routing map.
bootstrap:
  required_first_read: [AGENTS.md, AI_NAVIGATION.md, context-map.yaml, CHANGELOG.md]
audit_checks:
  governance_file_presence: [README.md, AGENTS.md, CLAUDE.md, AI_NAVIGATION.md, context-map.yaml, CHANGELOG.md]
standard:                          # new (section 4.2); replaces skill_ai_it_version
  version: "2026.11"
  modules: [pad, apn-hub, drawio-flows, code-map]
  python: "{{py}}"
  deviations:
    - {item: "recipe:rotate", reason: "...", by: "operator, 2026-11-11", review_by: "2026-12-11"}
# optional routing blocks: planning_surface, decision_preflight, code_structure_review, promotion_rules, context_recovery, update_rules
```

**`code-map.toml`** (project root; Core for projects with scripts): what is scanned, import layers, write gates, each script's status.

```toml
[meta]
schema = 1
title = "Code map"
status = "current"
authority = "source of truth for its subject"
scope = "<project>"
last_reviewed = 2026-11-11
summary = "What is scanned, import layers, write gates and each script's promotion status."

[scan]
roots = ["scripts", "src"]
python = "3.12"

[layers]                                   # optional: import-layer rules for a package
src = "src"
package = "<package>"
baseline = "scripts/registries/import-layers-baseline.json"
[layers.rules.core]
layer = "L0"
may_import = []

[write_gates]
roots = ["scripts"]
apply_pattern = "add_argument\\(\\s*[\"']--apply[\"']"
write_patterns = ["[\"'](POST|PATCH|PUT|DELETE)[\"']"]
[write_gates.exceptions]
"scripts/collector/push.py" = "pushes by design; --dry-run reads only"

[modules."scripts/checks/ascii_box_check.py"]
status = "candidate"                       # project_only (with reason) | candidate (with needs) | promoted (with skill, since)
needs = "what must be true before it moves, and where to"
```

**`versions.toml`** (project root; module `version-pins`): every pinned version and where it is pinned.

```toml
[meta]
schema = 1
title = "Version pins"
status = "current"
authority = "source of truth for its subject"
scope = "<project>"
last_reviewed = 2026-11-11
summary = "Every pinned version and every place it is pinned."

[build.just]                               # tools; other tables: [host.*], [lab.*], [components.*]
version = "1.58.0"
at = [{ files = "infra/host/cloud-init.yaml.tftpl", pattern = '--tag ([0-9.]+) ' }]
note = "optional: why, or where else it is read"

[image.postgres]                           # container images: tag and digest
ref = "postgres:16.15-alpine"
digest = "sha256:..."
```

**`target-map.yaml`** (project root; module `planning`): goals and staged targets, rendered to the step tracker.

```yaml
meta:
  schema: 1
  title: Target map
  status: current
  authority: source of truth for its subject
  scope: <project>
  last_reviewed: 2026-11-11
  summary: Goals and staged targets, rendered to the step tracker.
schema: 1
title: Implementation step tracker
render_to: docs/trackers/implementation-step-tracker.md
updated: 2026-11-05
stale_after_days: 7
roadmap_file: ROADMAP.md
changelog: {path: CHANGELOG.md, entry_heading: '^## (?P<stamp>\d{8}_\d{4}) — '}
sources:
  - {id: plan, path: docs/.../plan.md, target_heading: '^## Step (?P<id>\d+) — (?P<name>.+)$'}
goals:
  - {id: P0, name: "<goal name>", statement: "..."}
targets:
  - id: 1
    goal: P0
    state: groundwork                      # the project's state vocabulary
    exit_met: false
    reviewed: 2026-11-06 20:25             # the CHANGELOG stamp of the last real review
    summary: "..."
    blocker: {owner: operator, text: "..."}
    next: {owner: both, text: "..."}
    evidence: [{label: "...", path: "..."}]
```

**`docs/trackers/plan-timeline.yaml`** (module `planning`): dated stages rendered as the Timeline table.

```yaml
meta:
  schema: 1
  title: Plan timeline
  status: current
  authority: source of truth for its subject
  scope: <project>
  last_reviewed: 2026-11-11
  summary: Dated stages rendered as the Timeline table.
title: Timeline
source: the plan this timeline follows, with its link
render_to: docs/trackers/plan-tracker.md
columns:
  - {key: stage, header: Stage}
  - {key: steps, header: Steps, link_ids: {page: docs/trackers/implementation-step-tracker.md, heading: "Step {id}"}}
rows:
  - {due: 2026-10-23, done: 2026-11-05, stage: U1.3, step: "...", steps: "1, 2", where: "...", record: "[U1.3](...)"}
  - {due: 2026-10-30, stage: U1.4, step: "...", flag: at_risk, where: "LATE ..."}
```

**`docs/flows/parts/*.yaml`** (module `drawio-flows`; the skill-drawio standard): `master.yaml` holds the `drawing:` block and `#@include` lines; one part per component group and per flow family
(lists, exempt from `meta`); `master.yaml` also carries the `meta` block; `flows.yaml` is assembled from them and never edited.

```yaml
# parts/components-<group>.yaml
- id: app-host
  status: {state: live, since: "2026-10-12", evidence: "..."}
  name: "<host> (EC2)"
  kind: host
  group: "<group>"
  depends_on: [efs, aws]
  code: [infra/<host>/ops/verify-host.sh]

# parts/flows-<family>.yaml
- id: deploy
  status: {state: live, since: "2026-10-12", evidence: "..."}
  title: Deploy (bootstrap steps)
  trigger: {kind: deploy, detail: "..."}
  runs_on: mac
  dependencies: {flows: [...], components: [...], credentials: [...]}
  steps:
    - {id: guard, actor: bootstrap, action: "...", via: [SSH], gate: "...", code: [...], failures: [...], look: [...]}
```

**`guide-map.yaml`** (project root; Local to UNC): facts read from source files, used to render the team guides.

```yaml
meta:
  schema: 1
  title: Guide map
  status: current
  authority: source of truth for its subject
  scope: <project>
  last_reviewed: 2026-11-11
  summary: Facts read from source files, used to render the team guides.
updated: 2026-10-16
facts:
  app_version:
    regex: {file: "<app>/__init__.py", pattern: '^__version__ = "([^"]+)"', format: "app {0}"}
  relationship:
    label: catalog Relationship
    yaml: {file: "<catalog>.yaml", path: relationships, item_key: key}
# then the guide pages and the facts each one cites
```

**`tracker-map.toml`** (project root; module `tracker`): how this project's external work tracker reaches its repo tracker files. The name is tool-neutral (operator, 2026-11-11): the tool is the
`tool` setting, tool-only settings sit under `[tool.<name>]`, and a change of tool edits the file, never renames it or the recipes.

Why a separate file, not the tool's own (tested 2026-11-11 on pad 0.19.2, scratch copy, `VERIFIED_PRIMARY`): Pad owns `.pad.toml`. `pad workspace link` refuses an already linked folder and writes
nothing; `pad workspace switch` rewrites the file, keeping unknown tables' data but deleting every comment and reformatting it; both also install Pad's own skill copies into `.claude/skills/pad` and
`.agents/skills/pad`. A future release may change this further (operator, 2026-11-11), so the project's settings live in a file no tool writes. Guards:

- one writer per file: the tool writes its own file; people write `tracker-map.toml`; the adapter reads only the workspace name from the tool's file;
- the tool version is pinned in `versions.toml` (`[build.pad]` today);
- the tool's skill keeps an upgrade test (skill-pad today): a backup first, then on a scratch copy `switch` away and back and assert the workspace still parses and `tracker-map.toml` is untouched; it
  runs before a new version is used in any project, a failure stops the upgrade, and a downgrade is forward repair only;
- before any collection becomes the truth for a repo record, the nightly backup is restored into a scratch Pad and compared with the live export (item count and fields); a backup that has never been
  restored is not counted as recovery (skill-systems-architect SKILL.md:149, backup-disaster-recovery.md:81);
- when Pad cannot be reached, the commit gate warns and keeps the last export; it never blocks a commit. Whether a Pad server upgrade reaches every project at once, whatever the client pin, is
  UNVERIFIED and checked in S1a.

```toml
[meta]
schema = 1
title = "Tracker map"
status = "current"
authority = "source of truth for how tracker items reach this repo"
scope = "<project>"
last_reviewed = 2026-11-11
summary = "Which external tracker source feeds which repo tracker file, the focus export and the commit gate."

[tracker]
tool = "pad"                               # change this, not the file name, when the tool changes
workspace_from = ".pad.toml"               # the tool's own file; only the workspace name is read from it

[focus]
out = "docs/trackers/pad-focus.md"
timeout_s = 30

[[feed]]
source = "bugs"                            # the tool's collection, list or project
file = "docs/trackers/bug-tracker.md"
kind = "bugs"

[[feed]]
source = "feature-requests"
file = "docs/trackers/features-to-add.md"
kind = "features"

[[feed]]
source = "decisions"                        # Pad's Decisions collection (ADR template)
file = "decision-map.toml"
kind = "decisions"                         # written as TOML, not Markdown

[gate]
commit = true                              # focus export and feeds run in the commit gate

[tool.pad]                                 # settings only Pad understands
focus_skip = ["conventions", "playbooks", "bugs", "feature-requests", "tech-debt", "decisions"]
links = true                               # convert repo links in each feed (smc-resiliency's extra step, now a setting)
```

```text
+-----------------------------+----------------------+------------------------------------+
|  PAD (the truth)            |  tracker-map.toml    |  REPO (generated, never edited)    |
+-----------------------------+----------------------+------------------------------------+
|  Bugs                       |  [[feed]] bugs       |  docs/trackers/bug-tracker.md      |
|  Feature Requests           |  [[feed]] features   |  docs/trackers/features-to-add.md  |
|  Decisions                  |  [[feed]] decisions  |  decision-map.toml                 |
|  Plans, Tasks, Asks, Ideas  |  [focus]             |  docs/trackers/pad-focus.md        |
|  Tech Debt                  |  none yet (gap)      |  -                                 |
+-----------------------------+----------------------+------------------------------------+
```

Pad collections, their use and where each goes in the repo (skill-pad `docs/pad-usage-guidelines-20261110_1628.md` section 3.1, and the UNC and smc-resiliency recipes read 2026-11-11). One rule
decides the destination: a collection whose items are the truth for a repo record gets its own `[[feed]]` and generated file; working items (plans, tasks, asks, ideas) go to the one focus export;
rules and procedures stay in Pad with their baseline in skill-pad.

| Collection (prefix)    | Use                                                    | Exported to                                    | How                        | In UNC and smc-resiliency today      |
| ---------------------- | ------------------------------------------------------ | ---------------------------------------------- | -------------------------- | ------------------------------------ |
| Bugs (BUG)             | every bug, open and fixed; Pad is the truth            | `docs/trackers/bug-tracker.md`                 | `[[feed]]`,                | yes                                  |
|                        |   (2026-11-10); closed: fixed, wont-fix                |                                                |   `kind = "bugs"`          |                                      |
| Feature Requests (FR)  | the operator's features to add, verbatim; closed:      | `docs/trackers/features-to-add.md`             | `[[feed]]`,                | yes                                  |
|                        |   shipped, declined                                    |                                                |   `kind = "features"`      |                                      |
| Decisions (new; Pad's  | every decision and its rationale; closed: accepted,    | `decision-map.toml`                            | `[[feed]]`,                | not created yet                      |
|   ADR template)        |   rejected, superseded                                 |                                                |   `kind = "decisions"`     |                                      |
|                        |                                                        |                                                |   (TOML)                   |                                      |
| Tech Debt (TD)         | internal clean-up (refactors, tool pins);              | nothing of its own today: skipped by the focus | none                       | created; not exported (a gap: add a  |
|                        |   closed: resolved                                     |   export; UNC's refactor tracker is a separate |                            |   feed or include it in focus)       |
|                        |                                                        |   generated file one TD item points at         |                            |                                      |
| Plans                  | one plan per current timeline focus                    | `docs/trackers/pad-focus.md`                   | focus export               | yes                                  |
| Tasks (TASK)           | agent work and operator hands-on work                  | `docs/trackers/pad-focus.md`                   | focus export               | yes                                  |
| Asks (ASK; new)        | every item waiting on the operator                     | `docs/trackers/pad-focus.md`                   | focus export               | not created yet (guidelines          |
|                        |                                                        |                                                |                            |   say create)                        |
| Ideas                  | proposals not yet on the timeline                      | `docs/trackers/pad-focus.md`                   | focus export               | yes                                  |
| Docs                   | unused: documents live in the repo                     | nothing                                        | none                       | empty                                |
| Conventions, Playbooks | rules and procedures agents follow                     | nothing per project; the baseline is           | skill-pad conventions sync | yes                                  |
|                        |                                                        |   skill-pad `conventions/`                     |                            |                                      |

Making Decisions the truth in Pad follows the bugs precedent, but two texts still say the repo holds decisions: skill-pad's usage guidelines (the "project repo (truth)" diagram) and the
`trackers-truth` convention. Both are updated in the same step that creates the collection (S4).


#### New central map

**`consumers.toml`** (skill-ai-it root; certain): every project that uses the standard, and how to check it. skill-drawio's existing `consumers.yaml` and `consumer_check.py` are generalised into this
one registry and one checker (module `drawio-flows` selects the drawing consumers), so there is one list, not two.

```toml
[meta]
schema = 1
title = "Consumers"
status = "current"
authority = "source of truth for which projects use the standard"
scope = "skill-ai-it"
last_reviewed = 2026-11-11
summary = "Projects that use the skill-ai-it standard; read by `just consumers` and the conformance table."

[consumers.unified-network-controller]
path = "/Volumes/Data/_ai/_project/project_stuff/apn/unified-network-controller"
check = "just check"
timeout_s = 300
hub = "enterprise-strategy"                # optional: who to tell when a change affects it
stratum = "apn-govcheck"                  # rollout group (section 5)
lock = ""                                  # "S2, <session>, <date>" while a stage is in flight here; one stage at a time
# modules and standard version are read from the project's context-map.yaml, never repeated here
```

#### Candidate maps (proposed formats)

**`rule-map.toml`** (project root): which rule is enforced by what. Keyed by rule id, so a duplicate fails at parse; the rule's wording is always read from its source anchor, never copied, so it
cannot drift.

```toml
[meta]
schema = 1
title = "Rule map"
status = "current"
authority = "source of truth for how each rule is enforced"
scope = "<project>"
last_reviewed = 2026-11-11
summary = "Each rule this project follows, where it is written and what enforces it."

[rules.no-restart-while-job-running]
source = "AGENTS.md#writes-credentials-and-safety"   # file and heading anchor; the text is read from there
level = "project"                          # standard (inherited from skill-ai-it) | module | project
enforced_by = { kind = "script", ref = "infra/<host>/ops/jobs-running.sh" }   # check | hook | script | test | none
since = "operator, 2026-10-14"
```

**`job-map.toml`** + **`job-runs.jsonl`** (project root): what each repeated job should cost, and what it did cost. The map is hand-written; the log is appended by the job (or the measuring script),
one line per run, so history is kept and no script rewrites the map.

```toml
[meta]
schema = 1
title = "Job map"
status = "current"
authority = "source of truth for job budgets"
scope = "<project>"
last_reviewed = 2026-11-11
summary = "Repeated jobs: schedule, runtime budget and owner. Measured runs are in job-runs.jsonl."

[jobs.collector-cycle]
runs = "every 15 min, systemd timer"
owner = "collector"
budget_s = 900
on_breach = "alarm: cycle over budget"
```

```json
{"job": "collector-cycle", "at": "2026-11-10T12:40:00+11:00", "seconds": 412, "ok": true, "evidence": "CHANGELOG 20261110_1240"}
{"job": "collector-cycle", "at": "2026-11-10T12:55:00+11:00", "seconds": 398, "ok": true}
```

Conformance reads both: a job with no run in its expected window, or whose last runs exceed `budget_s`, is a finding.

**`access-map.toml`** (project root, or an `[access]` section of `code-map.toml`): what each script reaches and how a write is gated.

```toml
[meta]
schema = 1
title = "Access map"
status = "current"
authority = "source of truth for its subject"
scope = "<project>"
last_reviewed = 2026-11-11
summary = "Systems each script reads or writes, the gate and the credential entry."

[access."scripts/collector/push.py"]
target = "<system> API"
mode = "write"                             # read | write
gate = "--dry-run reads only; writes by design (code-map exception)"
credential = "<vault entry name>"          # an entry name, never the secret
approver = "operator"
```

**`data-map.yaml`** (project root): inputs, transforms and outputs as a graph, so a stale output is found.

```yaml
meta:
  schema: 1
  title: Data map
  status: current
  authority: source of truth for its subject
  scope: <project>
  last_reviewed: 2026-11-11
  summary: Inputs, transforms and outputs as a graph, so a stale output is found.
nodes:
  - {id: invoices-raw, kind: input, path: data/raw/invoices-*.csv, source: "monthly export from the carrier portal"}
  - {id: build-db, kind: transform, script: scripts/build_db.py, recipe: "just build-db"}
  - {id: profit-db, kind: output, path: data/profit.duckdb}
edges:
  - {from: invoices-raw, to: build-db}
  - {from: build-db, to: profit-db}
# an output older than any of its inputs is stale
```

**`decision-map.toml`** (project root; generated): every decision, from the tracker's Decisions collection (operator, 2026-11-11: Pad is the truth, the file is generated like `bug-tracker.md`). It is
a `[[feed]]` in `tracker-map.toml` with `kind = "decisions"`; the generator writes `[meta]`, a GENERATED banner and one table per decision. Edit the item in Pad, never this file. Python's standard
library reads TOML but cannot write it, so skill-pad carries a small tested emitter for the few types this file uses (strings, lists, dates, tables): sorted keys, stable order, no timestamps beyond
the data, and a drift check that renders to memory and compares (operator, 2026-11-11; skill-coder generated-artifacts.md:31-32).

Pad's Decisions template (web UI, "Record architecture decisions and their rationale (ADRs)"; source `collection-templates.ts`, pad 0.19.2, `VERIFIED_PRIMARY`) has `status` (proposed, accepted,
rejected, superseded), `category` and `decision_date`. The collection schema skill-pad keeps (`conventions/collection-schemas/decisions.json`) adds what the map needs, and `terminal_options` so
decisions close:

| Field           | Type                                                        | Why                                                               |
| --------------- | ----------------------------------------------------------- | ----------------------------------------------------------------- |
| `status`        | select: proposed, accepted, rejected, superseded (template) | terminal: accepted, rejected, superseded                          |
| `category`      | text (template)                                             | groups decisions (platform, data, access ...)                     |
| `decision_date` | date (template)                                             | when it was decided                                               |
| `decided_by`    | text                                                        | `operator, <date>` style attribution                              |
| `superseded_by` | relation to decisions                                       | the chain from old to current                                     |
| `constraints`   | text                                                        | what every later choice inherits                                  |
| `relied_on_by`  | text (paths)                                                | documents and code that depend on it, so a change can be traced   |
| `record`        | text (path)                                                 | the Markdown record holding the full rationale, when there is one |

```toml
# GENERATED from Pad collection "decisions" by skill-pad pad_tracker.py (kind = "decisions"); edit the items in Pad, not this file.
[meta]
schema = 1
title = "Decision map"
status = "current"
authority = "generated from the Pad Decisions collection"
scope = "<project>"
last_reviewed = 2026-11-11
summary = "Every decision, its status, constraints and dependants."

[decisions.DECIS-12]                       # the item's Pad reference; the prefix Pad assigns is confirmed when the collection is created
title = "Link discovery and topology view"
status = "accepted"
category = "topology"
decision_date = 2026-10-09
decided_by = "operator, 2026-10-09"
constraints = ["the code and the design win over any explainer"]
superseded_by = ""
relied_on_by = ["docs/architecture/topology/<explainer>.md"]
record = "docs/architecture/topology/<decision record>.md"
```

Moving a project's existing decisions into Pad changes where the data lives, so it is its own per-project stage, S4b, separate from the tooling (skill-systems-architect
migration-and-hybrid.md:150-161, :239): the repo register (UNC's options register today) stays the truth and read-only until a reconciliation passes (item count and a field-by-field comparison); the
point of no return is the first decision edited only in Pad, recorded with its date; after it, rollback is an export back to the repo (forward repair).

```text
+------------------------+------------------------+----------------------+-------------------------+
|  1. IMPORT             |  2. RECONCILE          |  3. FEED ON          |  4. POINT OF NO RETURN  |
|  repo register stays   |  item count and every  |  decision-map.toml   |  first decision edited  |
|  the truth, read-only  |  field; differ = stop  |  generated from Pad  |  only in Pad (dated)    |
+------------------------+------------------------+----------------------+-------------------------+
|  rollback before step 4: switch the feed off, keep the register                                  |
|  rollback after step 4: export Pad back into the register (forward repair)                       |
+--------------------------------------------------------------------------------------------------+
```

**`sources.yaml`** (project root; the skills' existing layout): each load-bearing claim and its evidence.

```yaml
meta:
  schema: 1
  title: Sources
  status: current
  authority: source of truth for its subject
  scope: <project>
  last_reviewed: 2026-11-11
  summary: Each load-bearing claim, its evidence label and where it is used.
claims:
  - id: VP-C01
    statement: "The carrier bills speed tiers ex-GST."
    evidence_status: VERIFIED_PRIMARY      # VERIFIED_PRIMARY | VERIFIED_SECONDARY | UNVERIFIED | USER_STATED
    lifecycle: current
    source_type: official_documentation
    evidence: "URL or file:line, with the section"
    reference: docs/reports/<report>.md    # where the claim is used
```

**`env-map.toml`** + **`env-map.tofu.json`** (project root): environments and hosts, how each is reached, what runs where (operator, 2026-11-11, after both reviews). Two files, one writer each, joined
by environment id:

- `env-map.toml` is hand-written: how a person reaches each environment and what the team calls it. These are documentation, so they never live in HCL, where a wording change would become an
  infrastructure change.
- `env-map.tofu.json` is generated, where hosts are built with OpenTofu (UNC's `infra/apn-unc01/main.tf`), from the plan's planned outputs (`tofu plan -out`, then `tofu show -json`), so no apply is
  needed for a new output (UNVERIFIED for the pinned OpenTofu, checked in S1a). It records the state serial it came from; a freshness check compares that serial with the current state. JSON, because a
  script writes it.
- Conformance joins the two by id, reads only the committed files and never holds cloud credentials. A project with no OpenTofu has only the hand-written file.

```text
+-------------------+--------------------------+------------------------+------------------------+
|  OpenTofu plan    |  env-map.tofu.json       |  env-map.toml          |  conformance           |
|  tofu show -json  |  generated: kind, host,  |  hand-written: reach,  |  joins by env id;      |
|  (no apply)       |  runs, state serial      |  team name             |  no cloud credentials  |
+-------------------+--------------------------+------------------------+------------------------+
```

```hcl
# infra/<host>/outputs.tf: machine facts only
output "env_map" {
  value = {
    production = {
      kind     = "production"
      host     = "AWS EC2, ${var.region}"
      runs     = local.services
      identity = "infra/<host>/instance.conf"
    }
  }
}
```

```toml
[meta]
schema = 1
title = "Environment map"
status = "current"
authority = "source of truth for how people reach each environment"
scope = "<project>"
last_reviewed = 2026-11-11
summary = "How each environment is reached and named; machine facts are in env-map.tofu.json."

[env.production]
reach = "tsh ssh --proxy=<proxy> ubuntu@<node>"   # names, never secrets
called = "the production controller"
```

```json
{"generated_from": "tofu show -json (plan)", "state_serial": 412, "env": {"production": {"kind": "production", "host": "AWS EC2, ap-southeast-2", "runs": ["<service>"], "identity": "infra/<host>/instance.conf"}}}
```

**`term-map.yaml`** (project root): domain words, dictation aliases and words kept out of user-facing text.

```yaml
meta:
  schema: 1
  title: Term map
  status: current
  authority: source of truth for its subject
  scope: <project>
  last_reviewed: 2026-11-11
  summary: Domain words, dictation aliases and words kept out of user-facing text.
terms:
  - {term: SMC, means: "site management computer", use: always}
aliases:
  - {heard: "scales", means: "skills"}
  - {heard: "radium", means: "Iridium"}
banned_in_user_text:
  - {word: "<platform name>", reason: "the team sees the product, not the platform"}
  - {pattern: "just [a-z]", reason: "no command names in user-facing text"}
```

### 4.5 Seeing drift: the conformance check

`skill-ai-it/scripts/standard/conformance.py --project-root <p>` (read-only) compares a project with the standard version it names. It runs `cue vet` with `schemas/standard.cue` and each map's schema
for the shape and cross-file rules, and Python only for what CUE cannot see (file contents such as copied recipes, git state):

- Core recipes, checks and configs present and imported, not copied (a local copy of a Core item is drift);
- each switched-on module wired (its import line, its config);
- every difference from Core listed in `standard.deviations`; an undeclared one is a finding, a declared one is reported, not failed;
- the project's `standard` version against the current one (behind = an upgrade is due; `just refresh` applies it, plan first);
- the checked-out tag of its skill-ai-it worktree against its `standard.version` label (a mismatch fails);
- the undeclared-drift count, held by skill-coder's `ratchet.py` as a shrink-only baseline from S1 and failing from S8 (testing.md:50-52).

```text
+--------------------------------------------------------------------------------------------------+
|  conformance.py --project-root <p>: compares the project with the standard version it names      |
+----------------------+--------------------------+----------------------+-------------------------+
|  FOLLOWS             |  DECLARED DEVIATION      |  UNDECLARED DRIFT    |  BEHIND                 |
|                      |                          |                      |                         |
|  Core present and    |  differs from Core,      |  Core item copied,   |  standard older than    |
|  imported; modules   |  listed in deviations    |  missing or changed, |  current, or review_by  |
|  wired               |  with reason and date    |  and not declared    |  date passed            |
|                      |                          |                      |                         |
|  pass                |  reported, not failed    |  finding             |  upgrade or review due  |
+----------------------+--------------------------+----------------------+-------------------------+
```

It runs inside each project's `just check`, and across all projects from skill-ai-it (`just consumers --conformance`), giving one table of who follows the standard, who deviates (declared) and who
drifted (undeclared). Each run appends one line per project to `conformance-runs.jsonl` in skill-ai-it, so drift over time is visible; the table people read is generated from it.

### 4.6 How the standard changes

A new rule is added once, in skill-ai-it: a Core change bumps `standard` (for example `2026.12`), lands with its check, and passes the consumer check; projects pick it up with `just refresh` (plan,
then `--apply`). A project that needs a rule the standard lacks proposes it for Core or a Module rather than inventing a local variant; the operator decides once, and every project gets it.

Promotion candidates are found the same way: a read-only scan lists every `candidate` in each project's `code-map.toml` and whether code outside that project already uses it (path-qualified match,
since bare file names such as `__main__.py` or `render.py` give false hits). A met condition is reported to the operator rather than waiting for someone to notice.

```text
+-----------------------+------------------------+-----------------------+--------------------------+
|  1. rule added once   |  2. standard bumped    |  3. consumer check    |  4. projects take it     |
|     in skill-ai-it    |     2026.11 -> 2026.12 |     every project's   |     just refresh (plan,  |
|     with its check    |     CHANGELOG names    |     just check run;   |     then --apply);       |
|     and test          |     what changed       |     no new failures   |     conformance confirms |
+-----------------------+------------------------+-----------------------+--------------------------+
```

## 5. Stages

Each stage is a gate: it starts only after the operator's go, ends when its checklist passes in every project it touched, and has numbers agreed before it starts (skill-systems-architect
migration-and-hybrid.md:44, :230). The operator owns every go and abort; the running session owns the evidence. One stage is in flight per project at a time, recorded as `lock` in `consumers.toml` and
released at the stage's close, so a change in a project's output can be traced to one stage (fleet-management.md:46).

| Stage | Target                                                    | Touches                             | Size   | Go when                 | Abort when                                              |
| ----- | --------------------------------------------------------- | ----------------------------------- | ------ | ----------------------- | ------------------------------------------------------- |
| [S0](#s0-coordinate-and-freeze) | No other session is editing the same files                | messages only                       | small  | the owning              | an owner cannot commit within a day                     |
|       |                                                           |                                     |        |   sessions acknowledged |                                                         |
| [S1](#s1-safety-net) | Tests on central code; consumer check; baselines;         | skill-ai-it                         | medium | S0 done                 | the consumer check cannot finish within 10 minutes with |
|       |   worktree pin                                            |                                     |        |                         |   4 workers                                             |
| [S1a](#s1a-trials) | Trials: CUE, HCL plan output, editor lines, Pad restore   | skill-ai-it, skill-pad, UNC         | small  | S1 done                 | a trial fails: its part falls back as the trial         |
|       |   and server upgrade                                      |   (plan only)                       |        |                         |   step says                                             |
| [S1b](#s1b-record-file-fix) | Rotation tool writes complete front matter                | skill-ai-it                         | small  | S1 done                 | the characterisation diff shows any change besides the  |
|       |                                                           |                                     |        |                         |   two keys                                              |
| [S2](#s2-central-govcheck-engine) | One govcheck engine and the identical checks, imported    | skill-ai-it, 3 projects             | medium | S1 done                 | any consumer's saved output differs, beyond             |
|       |                                                           |                                     |        |                         |   accepted lines                                        |
| [S3](#s3-merge-drifted-checks) | Drifted checks merged with options                        | skill-ai-it, 3 projects             | medium | S2 done                 | a merged check loses assertions (count drops)           |
| [S4](#s4-importable-just-modules) | Governance, Pad and apn recipes imported, not copied      | skill-ai-it, skill-pad,             | large  | S1 and the S4           | a replaced recipe's output differs, or a name collides  |
|       |                                                           |   apn/scripts, 10+ projects         |        |   spike done            |                                                         |
| [S4b](#s4b-decisions-into-pad-per-project) | One project's decisions move into Pad                     | Pad, one project at a time          | small  | S4 done and the Pad     | the reconciliation differs in count or any field        |
|       |                                                           |                                     |        |   restore test passed   |                                                         |
| [S5](#s5-apn-pre-commit-hook) | apn hook owned by `apn/scripts`, project parts            | apn/scripts, UNC                    | small  | S4 step 4 done          | a test commit is gated differently from before          |
|       |   as drop-ins                                             |                                     |        |                         |                                                         |
| [S6](#s6-retire-duplicates) | Shims, re-implementations and stale copies gone           | UNC, 5 stale projects               | medium | S2 and S3 done          | a by-path reader still names a deleted file             |
| [S7](#s7-shared-config-bases) | Lint configs extend one base                              | skill-ai-it, skill-coder,           | small  | S1 done                 | a project's lint output changes beyond accepted lines   |
|       |                                                           |   7+ projects                       |        |                         |                                                         |
| [S8](#s8-update-the-standard) | The skill's own rules say "import", bootstrap             | skill-ai-it docs and templates      | small  | S2 to S7 done           | a fresh bootstrap fails its own check                   |
|       |   writes loaders                                          |                                     |        |                         |                                                         |

**Rollout waves** (skill-systems-architect automation-and-safety.md:62-63, provisioning-and-lifecycle.md:106-114, :142). A change that reaches consumer projects runs in waves by stratum, never all at
once:

```text
+-----------------------------+----------------------------+--------------------------+
|  WAVE 0: one per stratum    |  STOP RULE                 |  WAVE 1: the rest        |
|  UNC (apn, govcheck)        |  a finding not in its      |  at most 4 per session,  |
|  islam (me, govcheck)       |  baseline stops the wave;  |  same stop rule          |
|  cambium-swap (stale copy)  |  a breaking change is      |                          |
|  vocus (no venv recipe)     |  reverted centrally first  |                          |
+-----------------------------+----------------------------+--------------------------+
```

A central change found to break a consumer is reverted centrally (the tag is not cut, or the previous tag is restored) before the next wave.

```text
S0 --> S1 --> S1a, S1b
          \
           +--> S2 --> S3 --> S6 --> S8
           \
            +--> S4 --> S4b (per project)
            |      \
            |       +--> S5
            \
             +--> S7
```

## 6. Stage details

### S0. Coordinate and freeze

- **Target:** no session edits a file this plan changes while it runs.
- **Prerequisites:** none.
- **Steps:**
  1. Read `git status` in skills_stuff and apn; list uncommitted changes in the files below.
  2. Ask the sessions that own them (smc-resiliency on skill-ai-it; whoever is repointing the five apn justfiles) to commit, and agree that this plan's stages own those files until done.
  3. Commit UNC's pending history migration first (separate decision, already planned in the UNC session).
- **Completion checklist:** working trees clean for skill-ai-it, the apn justfiles, `apn/scripts`; the owning sessions acknowledged.
- **Rollback:** nothing to roll back.

### S1. Safety net

- **Target:** a central change cannot silently break a consumer, and consumers run a pinned skill-ai-it.
- **Prerequisites:** S0.
- **Steps:**
  1. Tests in skill-ai-it for `doc_freshness.py`, `file_headers.py`, `docstring_ratchet.py`, `check_expected_diff.py` (characterisation tests: record today's output on fixtures first).
  2. Generalise skill-drawio's `scripts/consumer_check.py` into skill-ai-it `scripts/consumers/consumer_check.py` (read-only), reading `consumers.toml`: `--out DIR [--compare BEFORE] [--engine
     WORKTREE]` saves each consumer's normalised check output and its check and assertion counts; a refactor must leave them byte-identical, and any difference is listed for acceptance (skill-coder
     refactoring-and-promotion.md:26, :72). The before run can come from a `git worktree` of the previous tag. It compares `git status --porcelain` before and after each consumer and fails when a run
     changed files. Budget: 10 minutes wall time with 4 workers and a serial switch; over budget is a finding. Recipe `just consumers`.
  3. Record a baseline run: which consumers fail today and why, so later runs compare against it rather than demanding all green.
  4. The worktree pin (section 3): tag `standard-2026.11`, create the shared worktree, point one project's `ai_it` at it, and check that conformance reads the tag.
  5. First cut of `conformance.py` (section 4.5), report-only, against a draft Core list; run it on all 14 projects to see today's drift; hold the undeclared-drift count with skill-coder's
     `ratchet.py`.
  6. `scripts/standard/promotion_scan.py` (read-only): the code-map candidate scan of section 4.6, run across all consumers. First run (2026-11-11, by hand): 89 candidates (UNC 34, smc-resiliency 55);
     one with its condition met, the ASCII diagram tools (section 2.2 row 14); `check_versions.py` is the known duplicate (row 10); the other hits were mentions only (a promoted part already in
     skill-drawio, an example path in skill-pad tests). 15 of 17 projects have no `code-map.toml`, so the scan cannot see their scripts yet.
  7. Every new script starts from skill-coder's `scaffold.py` and passes `script_headers.py`; each new check (`conformance.py`, `consumer_check.py`) lands with a planted-failure test (skill-coder
     testing.md:50-52).
- **Completion checklist:** new tests pass and each has a negative case; `just consumers` lists all 14 projects with their baseline, inside its budget, with no changed working trees; one project runs
  on the pinned worktree; the drift table exists; runtimes recorded.
- **Rollback:** delete the new files and the worktree; repoint the trial project's `ai_it`; nothing else changed.

### S1a. Trials

- **Target:** every UNVERIFIED tool behaviour the plan relies on is tested before anything depends on it. Behaviour changes are kept out of this stage (skill-coder refactoring-and-promotion.md:27).
- **Prerequisites:** S1.
- **Steps:**
  1. CUE on two maps (`context-map.yaml` and `tracker-map.toml` of UNC): pin `cue` in skill-ai-it's `versions.toml`; write their schemas and one cross-file rule (the `tracker` module needs
     `tracker-map.toml`) behind `cue_seam.py`; prove `cue vet` reads YAML and TOML, fails on a planted error, and exports JSON Schema for the editor lines. If TOML or the export fails on the pinned
     version, record it and fall back to JSON Schema plus Python for that part only.
  2. OpenTofu plan output for UNC: add the `env_map` output beside `infra/apn-unc01/main.tf`, run a plan only, and generate `env-map.tofu.json` from `tofu show -json`; if planned outputs are not
     present for a new output on the pinned version, record it and use UNC's logged `unc01::plan|apply` step with the operator instead.
  3. Editor schema lines (section 4.4) in VS Code with a sample YAML and TOML map: a wrong key is flagged; record the extension versions; if a line form does not work, use the extension's settings
     mapping instead.
  4. Pad: restore the nightly backup into a scratch Pad and compare it with the live export; find out whether a Pad server upgrade reaches every project at once whatever the client pin.
- **Completion checklist:** each trial recorded here with its result, version and evidence; each fallback chosen where a trial failed.
- **Rollback:** delete the trial files; the UNC plan was never applied.

### S1b. Record-file fix

- **Target:** the rotation tool writes complete front matter.
- **Prerequisites:** S1 (its characterisation tests).
- **Steps:**
  1. The open-items tracker, the rotated archive and the `docs/history/readme.md` the rotation tool creates lack `Authority` and `Scope` (found 2026-11-11 in skill-pad, fixed there by hand); add them
     in `rotate_records.py`, `history_layout.py` and their templates.
  2. A test that a newly written file passes the front-matter check; the characterisation diff shows only the two added keys.
- **Completion checklist:** the test passes; a rotation in a scratch project passes that project's check.
- **Rollback:** revert the commit.

### S2. Central govcheck engine

- **Target:** `skill-ai-it/scripts/govcheck/` holds `core.py`, the shared helpers and the identical checks; projects import them.
- **Prerequisites:** S1.
- **Steps:**
  1. Create the package from the template plus the identical checks (section 2.1, PROMOTE rows); constants come from the project's `config.py` passed in, never inline.
  2. Port UNC's three govcheck test files; add negative tests for each promoted check.
  3. Project side: central checks are loaded only through the project's one loader (`skill_scripts.py`, made Core here), by path, under the `ai_it_` module-name prefix, never by putting skill-ai-it on
     `sys.path` (skill-coder refactoring-and-promotion.md:70, :117-119); `checks/__init__.py` lists central and local checks; each deleted local copy gets a moved-paths entry, and every by-path reader
     (docstring baselines, `code-map.toml`, `check_referenced_paths`) is repointed (refactoring-and-promotion.md:36-40, :131-134).
  4. Canary UNC: `just consumers --compare` before and after (same output, same assertion counts); then the rest of wave 0 and wave 1 (section 5). Run skill-coder's `code_size.py` with a baseline on
     the new package.
- **Completion checklist:** the three projects' check output is unchanged; `just consumers` matches baseline; the structure check still runs.
- **Rollback:** each project reverts its `checks/__init__.py` and restores its local modules from git (one commit per project).

### S3. Merge drifted checks

- **Target:** one version of each drifted check, with options for the intended differences.
- **Prerequisites:** S2.
- **Steps:**
  1. `check_constant_sync` and `check_interpreter_pinning` from smc-resiliency's versions.
  2. `check_task_recipes`: UNC's `mod` handling plus islam's glob skip.
  3. `check_referenced_paths` with resolver options (sibling roots, moved paths file, upstream owners, external roots).
  4. Docs indexed with two modes: per-folder readme (accepting `docs/history/<kind>/` via the history index) and one docs index.
  5. The `ai_it_script` loader and the `target_map` / `plan_timeline` wrappers.
  6. For every changed check: list the differences each project will see before switching it, held with skill-coder's `ratchet.py` (a project that gains findings gets them as a baseline, not a
     failure).
- **Completion checklist:** as S2; new findings in any project listed and accepted by the operator.
- **Rollback:** per project, as S2.

### S4. Importable just modules

- **Target:** projects `import` the shared recipes; a central path change is one edit.
- **Prerequisites:** S1. First step is a spike, because how `import` treats absolute paths and variables defined in the importing file is `UNVERIFIED` until read in the just manual for the pinned
  version.
- **Steps:**
  1. Spike: confirm with the installed just version that an absolute `import` works, that imported recipes see the importer's `py`, and how a name clash behaves; record the result here.
  2. `skill-ai-it/just/governance.just`: records, navigation and `govern` recipes, one python variable, kebab names with snake aliases.
  3. `skill-pad/just/pad.just`: `pad-trackers`, `pad-export`, `plan-timeline`, `commit-gate`, reading each project's `tracker-map.toml` (section 4.4) instead of per-project arguments; skill-pad gains
     the Pad upgrade test and `[build.pad]` joins each Pad project's `versions.toml`. skill-pad's `pad_tracker.py` gains `kind = "decisions"` (writes TOML through its tested emitter) and
     `conventions/collection-schemas/decisions.json` (template fields plus `decided_by`, `superseded_by`, `constraints`, `relied_on_by`, `record`, and `terminal_options`): the interface only; no
     project's decisions move here (that is S4b). Tech Debt gets a feed or joins the focus export.
  4. `apn/scripts/apn.just`: `sync-projects`, `commit-project` (options for `--push-cmd`, `--check-cmd`).
  5. Canary UNC: replace its copies with imports; `just --list` and every replaced recipe run and compared; then the waves of section 5. Recipe names pass skill-coder's `naming_check.py`; recipe and
     path repoints use skill-ai-it's `scripts/adoption/repoint_paths.py`.
- **Completion checklist:** `just --list` per project shows the same recipe names (aliases included); each replaced recipe gives the same output; `just consumers` matches baseline.
- **Rollback:** restore the project's justfile from git; the modules can stay unused.

### S4b. Decisions into Pad (per project)

- **Target:** one project's decisions are held in Pad and `decision-map.toml` is generated from them.
- **Prerequisites:** S4 done; the Pad restore test of S1a passed; the operator's go for this project.
- **Steps:**
  1. Create the Decisions collection from skill-pad's schema; import the project's decisions; the repo register stays the truth and read-only.
  2. Reconcile: item count and a field-by-field comparison between the register and the Pad export; any difference stops the stage.
  3. Switch the feed on; update skill-pad's usage guidelines and the `trackers-truth` convention to name Decisions as Pad-held (first project only).
  4. Record the point of no return: the date of the first decision edited only in Pad.
- **Completion checklist:** reconciliation passed; `decision-map.toml` generated and its drift check passing; the register marked archived with a pointer to Pad.
- **Rollback:** before the point of no return, switch the feed off and keep the register; after it, export from Pad back into the register (forward repair).

### S5. apn pre-commit hook

- **Target:** the hook that governs every apn project is owned by `apn/scripts`, not by UNC.
- **Prerequisites:** S4 step 4.
- **Steps:**
  1. Move the generic loop to `apn/scripts/githooks/pre-commit`; each project's own part becomes `<project>/scripts/githooks/pre-commit.d/*`.
  2. Repoint the symlink in `apn/.git/hooks/`.
  3. Prove it: a commit in UNC and one in smc-resiliency each run the same checks as before (timing recorded).
- **Completion checklist:** both test commits gated as before; a failing check still blocks a commit (negative test); with the central path missing the hook fails closed with a message naming the
  cause (negative test); an operator-only bypass is documented; a missing `import` makes `just check` fail, never skip (skill-systems-architect automation-and-safety.md:70).
- **Rollback:** point the symlink back at the UNC file.

### S6. Retire duplicates

- **Target:** no copy of central code remains where the central one would do.
- **Prerequisites:** S2, S3.
- **Steps:**
  1. Delete UNC `scripts/render/roadmap_trim.py`; `rotate` and `roadmap-trim` call skill-ai-it directly; `code-map.toml` updated.
  2. Replace UNC `check_write_gates` with skill-coder's `write_gates.py`, as smc-resiliency does.
  3. Compare UNC `check_docstrings` with `docstring_ratchet.py`; retire it if the same.
  4. cambium-swap, enterprise-strategy, health, japan, psy-assess: stale 684-line `check_governance.py` replaced by the loader plus a `config.py`; each project's findings before and after listed.
  5. Move `ascii_box_render.py` and `ascii_box_check.py` with their tests to skill-ai-it `scripts/markdown/`; the `ascii-box-render` and `ascii-boxes` recipes join the governance just module; UNC and
     smc-resiliency drop their recipes and UNC's files (`code-map.toml` status `promoted`); UNC's AGENTS.md diagram rule moves into the standard (`references/project-standard.md`).
- **Completion checklist:** each deleted file has a moved-paths entry and no by-path reader still names it; each project's check output unchanged or the differences accepted; deleted files gone from
  `code-map.toml` and `scripts/README.md`.
- **Rollback:** restore the deleted files from git.

### S7. Shared config bases

- **Target:** lint settings come from one base per tool.
- **Prerequisites:** S1.
- **Steps:**
  1. `skill-ai-it/templates/markdownlint-base.jsonc`; projects `extends` it and keep only their exclusions. Add configs to smc-resiliency, islam, vocus, voip, which run `lint-md` without one.
  2. `skill-coder/configs/ruff-base.toml` (two-space indent rule) with `extend` in each project's `ruff.toml`.
- **Completion checklist:** each project's lint output unchanged or differences accepted.
- **Rollback:** restore the project configs from git.

### S8. Update the standard

- **Target:** the skill's own rules match what was built.
- **Prerequisites:** S2 to S7 as done.
- **Steps:**
  1. `patterns/governance-checks.md` "Structure and growth": engine and generic checks are imported from skill-ai-it; projects hold `config.py` and their project-only families.
  2. Bootstrap writes the loader and an `import` line, not copies; `templates/justfile` becomes the module plus a short project stub.
  3. SKILL.md and README name the packages, the consumer check and the extraction trigger.
  4. `references/project-standard.md` explains the Core list, the modules and their triggers, and the standard version history, and `schemas/standard.cue` holds the same as checkable rules; bootstrap
     writes the `standard:` block in `context-map.yaml`; refresh upgrades it; `conformance.py` moves from report-only to failing on undeclared drift.
  5. Each project's remaining differences are written as `deviations` entries (operator approves each), or removed.
  6. Map headers: the governance file-header rule for YAML and TOML changes from a leading comment block to the `meta` block (section 4.4); skill-ai-it `file_headers.py` and `doc_freshness.py` read
     `meta` (summary, status, `last_reviewed`) with a negative test each; `sync-map.yaml` checked for the governance change; existing maps move over at their next edit, reported by conformance until
     then.
  7. skill-coder write-back: the consumer-check pattern (saved outputs compared across a pinned worktree) and the CUE seam, as design patterns with code excerpts (skill-coder SKILL.md, standing
     write-back contract).
- **Completion checklist:** a fresh bootstrap in a scratch folder produces a project whose `just check` and conformance pass; every project's conformance shows no undeclared drift; `just consumers`
  matches baseline.
- **Rollback:** revert the doc and template commits.

## 7. Proposed scripts

The scripts this plan needs, with the excerpts that carry their logic, so a later session builds them as designed (operator, 2026-11-11).
They are designs, not code that has run: every name and flag is proposed. The excerpts were reviewed against skill-coder on 2026-11-11 and
corrected (five logic bugs, escaping, shared-repo handling, timeouts, names, two-space indentation); each fix is marked `(review n)`. When a
script is written it starts from skill-coder's `scaffold.py` (module purpose and run line, docstrings with `Args:`/`Returns:`/`Raises:`, a
timeout on every subprocess, `--apply` for any write), passes skill-coder's checkers (`script_headers`, `call_timeouts`, `write_gates`,
`code_size`, `naming_check`), and lands with a planted-failure test. Standard library only unless the excerpt says otherwise; timeouts and
budgets come from configuration (`consumers.toml`, `[settings]`), never literals in the code (review 12).

| Script                  | Home                                        | Stage              | Reads                                     | Writes                                                      |
| ----------------------- | ------------------------------------------- | ------------------ | ----------------------------------------- | ----------------------------------------------------------- |
| `consumer_check.py`     | skill-ai-it `scripts/consumers/`            | S1                 | `consumers.toml`, each project's          | `--out DIR` only                                            |
|                         |   (generalised from skill-drawio's)         |                    |   check output                            |                                                             |
| `standard_refresh.py`   | skill-ai-it `scripts/standard/`             | S1                 | `context-map.yaml` `standard:`, git tags  | git worktrees per tag; `standard.version`, only with        |
|   (`just refresh`)      |                                             |                    |                                           |   `--apply` and an accepted diff                            |
| `conformance.py`        | skill-ai-it `scripts/standard/`             | S1 (report),       | maps (PyYAML at the edge for YAML),       | `conformance-runs.jsonl` (central run only; listed          |
|                         |                                             |   S8 (fail)        |   justfile, `consumers.toml`              |   in `[write_gates.exceptions]`)                            |
| `cue_seam.py`           | skill-ai-it `scripts/standard/`             | S1a                | maps, `schemas/*.cue`                     | nothing                                                     |
| `promotion_scan.py`     | skill-ai-it `scripts/standard/`             | S1                 | every `code-map.toml`, consumer sources   | nothing                                                     |
|                         |                                             |                    |   (one `rg` pass)                         |                                                             |
| `toml_emit.py`          | skill-pad `scripts/` (a library)            | S4                 | values                                    | nothing: returns text                                       |
| `tracker_feeds.py`      | skill-pad `scripts/` (its own script;       | S4                 | `tracker-map.toml`, the tool's file       | each feed's file, the focus export, `decision-map.toml`,    |
|                         |   `pad_tracker.py` calls it)                |                    |   (`.pad.toml`), Pad exports              |   with `--apply`                                            |
| `pad_toml_probe.py`     | skill-pad `scripts/` (built                 | S1a, every         | a scratch `.pad.toml`                     | a temporary folder; whether `switch` also changes Pad's own |
|                         |   2026-11-11, `just pad-toml-probe`)        |   Pad upgrade      |                                           |   current-workspace state is UNVERIFIED                     |
| `env_map_from_plan.py`  | skill-ai-it `scripts/standard/` (or         | S1a                | `tofu show -json` of a plan               | `env-map.tofu.json`, with `--apply`                         |
|                         |   the project)                              |                    |                                           |                                                             |
| `job_runs.py`           | skill-ai-it `scripts/standard/`             | when `job-map`     | `job-map.toml`                            | appends to `job-runs.jsonl` (listed in                      |
|                         |                                             |   is adopted       |                                           |   `[write_gates.exceptions]`: an append-only log)           |

### 7.1 consumer_check.py: same output before and after

The core of S1: run every consumer's check against a given skill-ai-it checkout, save what it printed and its exit code, and compare two runs.
A refactor passes only when outputs, exit codes and assertion counts match; a run that changed a project's files fails.

```python
def run_one(name: str, consumer: dict, engine: Path, out_dir: Path) -> dict:
  """Run one consumer's check against `engine` and save its normalised output.

  Args:
    name: consumer id from consumers.toml.
    consumer: its table: `path`, `check` (an argv list, never a shell string; review 12), `timeout_s`.
    engine: the skill-ai-it checkout this run must use.
    out_dir: folder for `<name>.txt` and `<name>.json`.
  Returns:
    {"name", "rc", "seconds", "counts", "tree_changed"}; rc is None when the check timed out.
  Raises:
    EngineNotUsed: the project's justfile does not resolve `ai_it` to `engine`, so the run would prove nothing (review 3).
  """
  root = Path(consumer["path"])
  env = {**os.environ, "AI_IT": str(engine)}
  used = run(["just", "--evaluate", "ai_it"], cwd=root, env=env, timeout_s=30).stdout.strip()
  if Path(used).resolve() != engine.resolve():
    raise EngineNotUsed(f"{name}: ai_it is {used}, expected {engine}")
  before = tree_state(root)
  started = time.monotonic()
  try:
    proc = run(consumer["check"], cwd=root, env=env, timeout_s=consumer["timeout_s"])
    rc, text = proc.returncode, normalise(proc.stdout + proc.stderr)
  except subprocess.TimeoutExpired:  # one slow consumer is a result, not a crash of the pool (review 3)
    rc, text = None, "timeout"
  result = {"name": name, "rc": rc, "seconds": round(time.monotonic() - started, 1), "counts": COUNTS.findall(text), "tree_changed": tree_state(root) != before}
  (out_dir / f"{name}.txt").write_text(text, encoding="utf-8")
  (out_dir / f"{name}.json").write_text(json.dumps(result, sort_keys=True), encoding="utf-8")
  return result


def tree_state(root: Path) -> tuple[str, str]:
  """This project's own working-tree state, so a shared repository does not blame one project for another's files (review 3).

  Args:
    root: the project folder inside its repository.
  Returns:
    (porcelain status of this folder only, hash of `git diff -- .`), so an already-dirty file that changes again is still seen.
  """
  status = run(["git", "status", "--porcelain=v1", "--untracked-files=all", "--", "."], cwd=root, timeout_s=30).stdout
  diff = run(["git", "diff", "--", "."], cwd=root, timeout_s=30).stdout
  return status, hashlib.sha256(diff.encode()).hexdigest()


def run(argv: list[str], cwd: Path, timeout_s: int, env: dict | None = None) -> subprocess.CompletedProcess:
  """Run a command in its own process group and end the whole group on timeout, since `just` children outlive a plain timeout (review 3).

  Args:
    argv: the command as a list.
    cwd: working folder.
    timeout_s: seconds before the group is ended.
    env: environment, default the current one.
  Returns:
    The completed process.
  Raises:
    subprocess.TimeoutExpired: after the group was ended.
  """
  with subprocess.Popen(argv, cwd=cwd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, start_new_session=True) as proc:
    try:
      stdout, stderr = proc.communicate(timeout=timeout_s)
    except subprocess.TimeoutExpired:
      os.killpg(proc.pid, signal.SIGTERM)
      proc.communicate()
      raise
  return subprocess.CompletedProcess(argv, proc.returncode, stdout, stderr)


def compare(before: Path, after: Path) -> list[str]:
  """Consumers whose run differs between two saved runs; each difference needs the operator's acceptance.

  Args:
    before: folder of the earlier run.
    after: folder of the later run.
  Returns:
    One line per consumer whose text, exit code or counts differ, or that is present in only one run (review 3).
  """
  names = sorted({p.stem for p in before.glob("*.json")} | {p.stem for p in after.glob("*.json")})
  differ = []
  for name in names:
    old, new = before / f"{name}.json", after / f"{name}.json"
    if not (old.exists() and new.exists()):
      differ.append(f"{name}: present in one run only")
      continue
    same_text = (before / f"{name}.txt").read_text() == (after / f"{name}.txt").read_text()
    old_res, new_res = json.loads(old.read_text()), json.loads(new.read_text())
    if not same_text or (old_res["rc"], old_res["counts"]) != (new_res["rc"], new_res["counts"]):
      differ.append(f"{name}: output, exit code or counts differ")
  return differ
```

Run as `just consumers --out runs/new --engine <worktree> [--compare runs/old]`. Consumers in one repository run one after another; separate
repositories run in parallel up to `[settings] workers` (4); over `[settings] budget_s` (600) in total is a finding; a `tree_changed` run fails.

### 7.2 standard_refresh.py: move a project to the next tag

Plan by default: the plan runs both checks and shows the difference; `--apply` moves the pin only when outputs match or the difference was
accepted (review 7; skill-coder safety-and-writes.md:68, runtime-boundaries.md:59).

```python
def refresh(project: Path, to_tag: str, apply: bool, accept_diff: bool) -> int:
  """Move a project from its current standard tag to `to_tag`.

  Args:
    project: project root.
    to_tag: e.g. "standard-2026.12"; must carry a recorded consumer-check pass.
    apply: False prints the plan and the output difference only.
    accept_diff: with apply, allow a move whose check output differs (the operator accepted the listed difference).
  Returns:
    0 moved or already there, 1 outputs differ and the move was not applied, 2 refused.
  Raises:
    subprocess.TimeoutExpired: a git or check call exceeded its timeout.
  """
  current = read_standard(project)["version"]
  if current == to_tag:
    print(f"{project.name}: already on {to_tag}")
    return 0
  if "consumer-check: pass" not in tag_message(to_tag):
    return refuse(f"{to_tag} has no consumer-check pass recorded")
  old = run_check(project, ensure_worktree(current))
  new = run_check(project, ensure_worktree(to_tag))
  difference = diff_outputs(old, new)
  print(f"plan: {project.name} {current} -> {to_tag}; {len(difference)} difference(s)")
  print("\n".join(difference))
  if not apply or (difference and not accept_diff):
    return 1 if difference else 0
  set_standard_version(project, to_tag)
  return 0


def tag_message(tag: str) -> str:
  """The full annotation of a tag (`git tag -n` shows one line only; review 7).

  Args:
    tag: the tag name.
  Returns:
    The annotation text.
  Raises:
    subprocess.TimeoutExpired: git did not answer within 30 s.
  """
  return subprocess.run(["git", "for-each-ref", "--format=%(contents)", f"refs/tags/{tag}"], cwd=SKILL, capture_output=True, text=True, timeout=30).stdout
```

### 7.3 conformance.py: the standard, checked

Inside a project's `just check` it runs with the project's interpreter (PyYAML at the edge, needed for `context-map.yaml`; review 9); the full
CUE pass runs centrally. Undeclared drift is a count held by skill-coder's `ratchet.py` until S8.

```python
def findings(project: Path, core: dict, today: dt.date) -> tuple[list[str], list[str]]:
  """What separates a project from the standard it names.

  Args:
    project: project root.
    core: the Core list for the project's standard version.
    today: the date deviations are judged against.
  Returns:
    (findings, declared): findings fail or count; declared deviations are listed so the report shows them (review 9).
  """
  standard = read_standard(project)
  findings, declared_lines = [], []
  if checked_out_tag(project) != standard["version"]:
    findings.append(f"pin: worktree is {checked_out_tag(project)}, label says {standard['version']}")
  declared = {d["item"]: d for d in standard.get("deviations", [])}
  for item, deviation in declared.items():
    review_by = deviation.get("review_by")
    if review_by is None:  # fail closed: a deviation without a review date is a finding (review 9)
      findings.append(f"deviation {item}: no review_by")
    elif dt.date.fromisoformat(str(review_by)) < today:
      findings.append(f"deviation {item}: review_by {review_by} passed")
    else:
      declared_lines.append(f"declared {item}: {deviation.get('reason', '')} (by {deviation.get('by', '?')}, review {review_by})")
  for recipe in core["recipes"]:
    state = recipe_state(project, recipe)  # "imported" | "copied" | "missing"
    if state != "imported" and f"recipe:{recipe}" not in declared:
      findings.append(f"recipe:{recipe} {state}, not declared")
  for module in standard.get("modules", []):
    findings += module_wired(project, module)
  return findings, declared_lines
```

### 7.4 cue_seam.py: the one place that calls cue

```python
Status = Literal["ok", "fail", "skipped"]


def vet(schema: Path, data: dict, definition: str, timeout_s: int) -> tuple[Status, str]:
  """Check one combined data document against a CUE definition.

  Args:
    schema: a file under skill-ai-it schemas/.
    data: every map of one project merged into one document (CUE vets several files one by one rather than merging them; UNVERIFIED for the
      pinned version, checked in S1a), keyed by map name, plus `files`: the project's file list.
    definition: the definition to apply, e.g. "#Project" (without `-d` it is never applied; UNVERIFIED, S1a).
    timeout_s: seconds.
  Returns:
    ("ok" | "fail" | "skipped", message). A project check prints "skipped" when cue is missing; the central run fails on it. Never a pass
    for a check that did not run (review 2).
  """
  if not CUE.exists():
    return "skipped", f"cue not found at {CUE}"
  with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as handle:
    json.dump(data, handle, sort_keys=True)
  try:
    proc = subprocess.run([str(CUE), "vet", "-d", definition, str(schema), handle.name], capture_output=True, text=True, timeout=timeout_s)
  except subprocess.TimeoutExpired:
    return "fail", f"cue vet timed out after {timeout_s} s"
  finally:
    Path(handle.name).unlink(missing_ok=True)
  return ("ok" if proc.returncode == 0 else "fail"), (proc.stderr or proc.stdout).strip()
```

A cross-file rule in `schemas/standard.cue`. The first draft added the missing field instead of requiring it, so it could not fail (review
1); this form asserts the file is in the project's file list:

```cue
import "list"

#Project: {
  standard: modules: [...string]
  files: [...string]
  if list.Contains(standard.modules, "tracker") {
    _trackerMap: true & list.Contains(files, "tracker-map.toml")
  }
}
```

### 7.5 promotion_scan.py: candidates already used elsewhere

One pass over all files with one `rg` call (review 10: reading every file once per candidate breaks the efficiency rule); a match needs the
parent folder plus the stem as a path, a dotted module or a `from parent import stem`; a top-level script matches by its file name.

```python
def patterns(candidates: list[str]) -> dict[str, re.Pattern]:
  """One pattern per candidate path.

  Args:
    candidates: paths inside their project, e.g. "lab/registry.py" or "build_db.py".
  Returns:
    {path: compiled pattern}. A top-level script has no parent, so it matches by its file name, never by a bare stem (review 10).
  """
  out = {}
  for path in candidates:
    parent, stem = Path(path).parent.name, Path(path).stem
    if not parent:
      out[path] = re.compile(rf"\b{re.escape(Path(path).name)}\b")
      continue
    p, s = re.escape(parent), re.escape(stem)
    out[path] = re.compile(rf"\b{p}[/.]{s}\b|\bfrom\s+{p}\s+import\s+(\w+,\s*)*{s}\b")
  return out


def users(hits: list[tuple[Path, str]], owner: dict[str, Path], pats: dict[str, re.Pattern]) -> dict[str, set[str]]:
  """Projects or skills outside each candidate's own that reference it.

  Args:
    hits: (file, line) pairs from one `rg` run over every root with all patterns combined (timeout from settings).
    owner: candidate path -> its project root, resolved.
    pats: from `patterns()`.
  Returns:
    {candidate: names of the other projects or skills using it}.
  """
  found = {path: set() for path in pats}
  for file, line in hits:
    resolved = file.resolve()
    for path, pat in pats.items():
      if owner[path] not in resolved.parents and pat.search(line):  # both sides resolved (review 10)
        found[path].add(owner_name(resolved))
  return found
```

### 7.6 toml_emit.py: the small TOML writer for generated maps

Python reads TOML but cannot write it; generated maps need only these types. Deterministic: sorted keys, fixed order, no timestamps beyond
the data, so the drift check compares bytes. Strings: TOML rejects the raw DEL character that `json.dumps` leaves (review 4, tested with
`tomllib` on Python 3.14), so it is escaped; keys that are not bare are quoted.

```python
BARE_KEY = re.compile(r"[A-Za-z0-9_-]+")


def value(item: object) -> str:
  """One TOML value for the types generated maps use.

  Args:
    item: str, bool, int, datetime.date, or a list of those.
  Returns:
    The TOML text.
  Raises:
    TypeError: any other type (a float, a nested table in a list), so an unsupported shape fails loudly.
  """
  if isinstance(item, bool):
    return "true" if item else "false"
  if isinstance(item, int):
    return str(item)
  if isinstance(item, dt.date):
    return item.isoformat()
  if isinstance(item, str):
    return json.dumps(item, ensure_ascii=False).replace("\x7f", "\\u007F")
  if isinstance(item, list):
    return "[" + ", ".join(value(x) for x in item) + "]"
  raise TypeError(f"unsupported TOML value: {type(item).__name__}")


def key(name: str) -> str:
  """A TOML key: bare when it can be, quoted otherwise (`a.b` would make a nested table, `a b` would not parse; review 4).

  Args:
    name: the key.
  Returns:
    The key as TOML text.
  """
  return name if BARE_KEY.fullmatch(name) else value(name)


def tables(banner: str, meta: dict, name: str, rows: dict[str, dict]) -> str:
  """The whole file: banner, [meta], then one [name.<id>] table per row, every key sorted.

  Args:
    banner: one line naming the generator and the source; a newline is refused.
    meta: the `[meta]` table.
    name: the table family, e.g. "decisions".
    rows: id -> fields.
  Returns:
    The file text, ending in a newline.
  Raises:
    ValueError: the banner holds a newline.
  """
  if "\n" in banner:
    raise ValueError("banner must be one line")
  lines = [f"# {banner}", "[meta]"] + [f"{key(k)} = {value(v)}" for k, v in sorted(meta.items())]
  for rid in sorted(rows):
    lines += ["", f"[{key(name)}.{key(rid)}]"] + [f"{key(k)} = {value(v)}" for k, v in sorted(rows[rid].items())]
  return "\n".join(lines) + "\n"
```

The test round-trips: `tomllib.loads(tables(...))` equals the input, for every supported type, a key with a dot or space, and a string with
DEL and a quote in it.

### 7.7 tracker_feeds.py: one loop over tracker-map.toml

Replaces the per-project recipe arguments. The tool is a setting; only the adapter knows Pad. Every feed is rendered before any is written,
so a failed export leaves no mix of old and new files; every output path must stay inside the project (review 8).

```python
ADAPTERS = {"pad": PadAdapter}  # a new tool adds one adapter, never a rename


def run(project: Path, apply: bool, timeout_s: int) -> int:
  """Regenerate every feed and the focus export named in tracker-map.toml.

  Args:
    project: project root.
    apply: False prints what each file would become.
    timeout_s: seconds per tool call.
  Returns:
    0 done, 3 the tool is unreachable (the commit gate warns and keeps the last export; it never blocks).
  Raises:
    UnknownTool: `tracker.tool` names no adapter.
    OutsideProject: a feed or focus path resolves outside the project.
  """
  tracker_map = tomllib.loads((project / "tracker-map.toml").read_text(encoding="utf-8"))
  tool_name = tracker_map["tracker"]["tool"]
  if tool_name not in ADAPTERS:
    raise UnknownTool(f"tracker.tool = {tool_name!r} has no adapter")
  tool = ADAPTERS[tool_name](
    workspace=read_workspace(project / tracker_map["tracker"]["workspace_from"]), settings=tracker_map.get("tool", {}).get(tool_name, {}), timeout_s=timeout_s
  )
  if not tool.reachable():
    print("warn: tracker unreachable; keeping the last export")
    return 3
  rendered = {inside(project, feed["file"]): RENDER[feed["kind"]](tool.export(feed["source"])) for feed in tracker_map.get("feed", [])}
  rendered[inside(project, tracker_map["focus"]["out"])] = tool.focus()
  for path, text in sorted(rendered.items()):
    write_if_changed(path, text, apply)
  return 0


def inside(project: Path, relative: str) -> Path:
  """Resolve a path from the map and refuse one outside the project (skill-coder security.md:34).

  Args:
    project: project root.
    relative: the path as written in tracker-map.toml.
  Returns:
    The resolved path.
  Raises:
    OutsideProject: the path escapes the project.
  """
  path = (project / relative).resolve()
  if project.resolve() not in path.parents:
    raise OutsideProject(f"{relative} is outside {project}")
  return path
```

### 7.8 pad_toml_probe.py: the Pad upgrade test

Built on 2026-11-11 (`skill-pad/scripts/pad_toml_probe.py`, `just pad-toml-probe`, 4 offline tests with fake pad binaries; a real run on
pad 0.19.2 reported "behaves as known"). Still to add from the review (review 5): catch `tomllib.TOMLDecodeError` and report "workspace file
not parseable" instead of crashing on the very failure it tests; write the slug through `toml_emit.value()` rather than an f-string; and find
out whether `pad workspace switch` changes Pad's own current-workspace state outside the scratch folder (UNVERIFIED).

### 7.9 env_map_from_plan.py: machine facts from the OpenTofu plan

```python
class PlanNotUsable(Exception):
  """The plan cannot give env_map: missing, unknown until apply, or sensitive."""


def build(plan_json: dict, state_serial: int) -> dict:
  """env-map.tofu.json content from `tofu show -json <planfile>`.

  Args:
    plan_json: the parsed plan (planned outputs; UNVERIFIED for the pinned OpenTofu's JSON until S1a).
    state_serial: the state's serial the plan was made against.
  Returns:
    {"generated_from", "state_serial", "env"}.
  Raises:
    PlanNotUsable: no env_map, any part unknown until apply, or the output is sensitive (a secret must never reach the repo; review 6).
  """
  output = plan_json.get("planned_values", {}).get("outputs", {}).get("env_map")
  change = plan_json.get("output_changes", {}).get("env_map", {})
  if not output or output.get("value") is None:
    raise PlanNotUsable("env_map is not in the plan's planned outputs; use the logged apply step instead")
  if output.get("sensitive") or change.get("after_sensitive"):
    raise PlanNotUsable("env_map is sensitive; it is never written to the repo")
  if "true" in json.dumps(change.get("after_unknown", False)):
    raise PlanNotUsable("part of env_map is unknown until apply")
  return {"generated_from": "tofu show -json (plan)", "state_serial": state_serial, "env": output["value"]}
```

The freshness check compares `state_serial` with the current state, read by the operator's logged step, never by conformance (no cloud
credentials there).

### 7.10 job_runs.py: append one measured run

An append-only log is an ungated write by design, so it is listed in the project's `[write_gates.exceptions]` with that reason (review 11).

```python
class UnknownJob(KeyError):
  """A job id that job-map.toml does not define."""


def record(project: Path, job: str, seconds: float, ok: bool, evidence: str = "") -> None:
  """Append one line to job-runs.jsonl; never rewrites job-map.toml.

  Args:
    project: project root.
    job: id from job-map.toml `[jobs.<id>]`.
    seconds: measured wall time.
    ok: whether the run succeeded.
    evidence: optional pointer (a CHANGELOG stamp, a log path).
  Raises:
    UnknownJob: the id is not in job-map.toml.
  """
  jobs = tomllib.loads((project / "job-map.toml").read_text(encoding="utf-8"))["jobs"]
  if job not in jobs:
    raise UnknownJob(f"{job} not in job-map.toml")
  line = {"job": job, "at": dt.datetime.now().astimezone().isoformat(timespec="seconds"), "seconds": round(seconds, 1), "ok": ok}
  if evidence:
    line["evidence"] = evidence
  with (project / "job-runs.jsonl").open("a", encoding="utf-8") as handle:
    handle.write(json.dumps(line, sort_keys=True) + "\n")
```

Conformance reads both files: no run in a job's window, or the last runs over `budget_s`, is a finding.

### 7.11 Language choice

Asked by the operator (2026-11-11): is Python and shell always the best choice here? Not always; each language below is chosen for one job.

| Language       | Use here                                                                              | Why                                                                                         |
| -------------- | ------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------- |
| Python         | every script in this section                                                          | already in every project and skill; `tomllib`, `json`, `ast`, `subprocess` with timeouts;   |
|   (stdlib)     |                                                                                       |   skill-coder's rules, helpers and tests are written for it                                 |
| Shell          | thin glue only: the pre-commit hook, recipe lines                                     | logic in shell is hard to test and quote safely; a hook calls a Python script and passes    |
|                |                                                                                       |   its exit code on                                                                          |
| just           | the task runner and the shared modules (S4)                                           | one runner for every project; `import` lets recipes live in one place                       |
| CUE            | schemas and the rules that cross files (section 4.4)                                  | constraints over several files at once, which JSON Schema and per-file Python checks        |
|                |                                                                                       |   do poorly                                                                                 |
| HCL (OpenTofu) | the source of the environment map's machine facts                                     | the hosts are already declared there; a second copy would drift                             |
| SQL (DuckDB)   | optional: questions over `conformance-runs.jsonl` and `job-runs.jsonl` ("which        | DuckDB reads JSON Lines directly and the profitability projects already use it; nothing is  |
|                |   projects drifted this month", "p95 runtime per job")                                |   installed into the projects                                                               |
| Go             | not now; only if the consumer check or conformance must run where no Python           | one static binary and fast parallel runs, but a second toolchain to keep; the runtime is    |
|                |   environment exists (CI, another machine)                                            |   dominated by each project's own check, not by the runner                                  |
| TypeScript     | not now; only for a custom VS Code integration beyond the editor schema lines         | the schema lines already give in-editor validation through existing extensions              |
| Rust           | not for these scripts; use Rust-built tools instead of writing Rust: `ripgrep` (`rg`) | a single fast binary with strong safety, but slow to write and compile, and no part of this |
|                |   for the promotion scan's text search across repositories, called from Python with   |   work is CPU-bound; the scan's cost is reading files, which `rg` already does at           |
|                |   a timeout                                                                           |   that speed                                                                                |

## 8. Not promoted, and why

| Item                                                                                                     | Why it stays                                                                              |
| -------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------- |
| UNC domain checks (decisions, catalog, devices, audience, location, guides, topology, roadmap,           | Nautobot and UNC specific                                                                 |
|   app revision)                                                                                          |                                                                                           |
| smc-resiliency vagrant copies, superseded banners, decision records                                      | Project rules                                                                             |
| islam archcore, records, corpora, phantom paths                                                          | Candidates later for any project with archcore (T2), not now                              |
| `check_flow_map`                                                                                         | Belongs in skill-drawio's own check, a separate item for that skill                       |
| `check_code_map`                                                                                         | Scope differs per project; revisit after S6                                               |
| `check_versions.py`                                                                                      | Pin locations are project-specific; low value until a third project needs it              |
| Profitability scripts (vocus, opticomm, voip)                                                            | Large drift, domain logic; extend `apn/scripts/speed_tier_engine.py` separately if wanted |
| `.mise.toml` pins                                                                                        | Per project by design                                                                     |

## 9. Risks and coordination

- **Concurrent sessions.** skill-ai-it was changed by smc-resiliency today; five apn justfiles have uncommitted path fixes. S0 exists for this.
- **Intended differences flattened by mistake.** UNC's local trim, UNC's `--push-cmd`, cambium's slim `govern`, islam's bash path, per-project lint exclusions. Every merge lists the differences first
  and keeps them as options.
- **Live edits reach everyone.** Closed by the worktree pin (section 3): projects run a tag, and a tag is cut only after the consumer check passes. Until S1 step 4 is done, the consumer check before a
  push is the only guard.
- **Data moves.** Moving decisions into Pad changes where data lives; S4b keeps the repo register as the truth until a reconciliation passes and records the point of no return.
- **Single points of failure.** One central path and one hook gate every apn commit; the hook fails closed with a clear message and an operator-only bypass is documented (S5).
- **just `import` behaviour** is unverified (S4 spike).
- **New findings on adoption.** A merged check may find real problems a project's copy missed; they become that project's baseline, decided by the operator, never a reason to weaken the check.

## 10. Decisions for the operator

1. Home: A (skill-ai-it now, extraction trigger to C), or another.
2. Order: S0 to S8 as drawn, or S4 (just modules) first because it has the most duplicated lines.
3. Which session runs it: this plan touches skill-ai-it, which the smc-resiliency session owns today.
4. Whether islam and the other `me/` projects are in scope from S2, or after the apn projects.
5. The Core list (section 4.1): what every project must have, and which items are modules.
6. Whether conformance fails `just check` on undeclared drift from S8, or stays a report.
7. The gov-map as a `standard:` block in `context-map.yaml` (recommended) or a separate file; and whether `code-map.toml` becomes Core for every project with scripts.
8. Which candidate maps of section 4.3 to adopt, at which level (Mandatory, Advised, Optional), and in which order (recommended first: `rule-map.toml`, then `job-map.toml` and `access-map.toml`).
9. Tag cadence and refresh (section 3): the session that changes skill-ai-it cuts tags, and projects follow in one central batch refresh (recommended), or another arrangement.

## 11. Evidence

- govcheck survey: read-only agent comparison of `apn/unified-network-controller/scripts/govcheck`, `apn/smc-resiliency/scripts/govcheck`, `me/islam/scripts/govcheck` against `templates/govcheck/`
  (function bodies parsed and compared with difflib), 2026-11-11.
- Tooling survey: read-only agent comparison of justfiles, scripts, hooks and configs across 13 projects under `project_stuff`, 2026-11-11.
- Checked by hand before writing: the hook symlink (`apn/.git/hooks/pre-commit` points into UNC), the uncommitted vocus justfile diff (paths `scripts/doc_freshness.py` to
  `scripts/checks/doc_freshness.py`), no shared justfile `import` in any project, 14 justfiles naming skill-ai-it.
- Current standard: `patterns/governance-checks.md` "Structure and growth" (engine copied per project).
