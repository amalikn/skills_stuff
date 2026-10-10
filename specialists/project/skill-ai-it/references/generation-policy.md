---
Title: skill-ai-it reference: Generation policy and optional tools
Category: reference
Status: current
Authority: local-supplement
Scope: On-need reference moved verbatim from SKILL.md
Last reviewed: 2026-10-10
Summary: >-
  Generation policy and optional tools; moved verbatim from SKILL.md so SKILL.md stays an orchestration file within budget.
---

# skill-ai-it reference: Generation policy and optional tools

Moved verbatim from `SKILL.md` on 2026-10-10 to keep that file within its budget for files loaded whole.

## Contents

- [File creation/update policy](#file-creationupdate-policy)
- [Markdown quality rules](#markdown-quality-rules)
- [Archcore initialization and promotion candidate reporting](#archcore-initialization-and-promotion-candidate-reporting)
- [Graphify initialization and refresh](#graphify-initialization-and-refresh)
- [Repomix initialization and refresh](#repomix-initialization-and-refresh)

### File creation/update policy

| File                           | Bootstrap                                            | Navigation-add                      | Refresh                                                 | Audit        |
| ------------------------------ | ---------------------------------------------------: | ----------------------------------: | ------------------------------------------------------: | -----------: |
| `README.md`                    | create/update                                        | update pointers                     | update index/pointers only                              | check        |
| `AGENTS.md`                    | create/update                                        | add navigation block                | refresh managed block only                              | check        |
| `CLAUDE.md`                    | create/update                                        | ensure wrapper                      | ensure wrapper                                          | check        |
| `SCRATCHPAD.md`                | create/update                                        | update memory pointers              | append/protect KEEP                                     | check        |
| `CHANGELOG.md`                 | create/update                                        | append navigation addition          | append refresh summary                                  | check        |
| `.archcore/`                   | initialize if CLI available                          | initialize if CLI available         | initialize if CLI available                             | check        |
| Graphify / `graphify-out/`     | disabled (2026-10-10)                                | disabled (2026-10-10)               | disabled (2026-10-10)                                   | check        |
| `repomix.config.json`          | initialize if CLI available                          | initialize if CLI available         | run to refresh context pack                             | check        |
| `.markdownlint-cli2.jsonc`     | create unless a markdown lint config already exists  | create unless a markdown lint       | create unless a markdown lint config already exists     | check        |
|                                |                                                      |   config already exists             |                                                         |              |
| `AI_NAVIGATION.md`             | create if useful                                     | create                              | update managed sections only                            | check        |
| `context-map.yaml`             | create if useful                                     | create                              | write `.proposed` if risky                              | check        |
| `scripts/README.md`            | create if scripts/tasks exist                        | add pointer if scripts/tasks exist  | create from template if scripts/tasks exist and file    | check        |
|                                |                                                      |                                     |   missing; update managed blocks if exists              |              |
| `justfile`                     | create from template if no canonical runner exists   | no unless needed                    | propose only if drift/conflict                          | check        |
|                                |   and scripts/automation present                     |                                     |                                                         |              |
| `scripts/check_governance.py`  | create from template, tuned to inferred invariants   | add if governance surfaces exist    | **create from template if missing**; if present, extend | run it,      |
|                                |                                                      |                                     |   registries for new artifacts — never narrow an        |   report     |
|                                |                                                      |                                     |   existing check                                        |   failures   |
|                                |                                                      |                                     |                                                         |   and        |
|                                |                                                      |                                     |                                                         |   coverage   |
|                                |                                                      |                                     |                                                         |   gaps       |
| `scripts/context_preflight.sh` | explicit request only                                | explicit request only               | audit/propose only                                      | check        |
| `ARCHITECTURE.md`              | conditional                                          | no unless needed                    | update pointers only                                    | check        |
| `CONVENTIONS.md`               | conditional                                          | no unless needed                    | update pointers only                                    | check        |
| `ROADMAP.md`                   | conditional                                          | no unless needed                    | update progress only                                    | check        |

### Markdown quality rules

Apply these rules to every markdown file created or updated by this skill. Authority:
[`/Volumes/Data/_ai/governance/categories/markdown-guide.md`](/Volumes/Data/_ai/governance/categories/markdown-guide.md).

#### Naming

- Time-bound files: `<slug>-YYYYMMDD_hhmm.md` (e.g. `design-notes-20260522_1400.md`).
- Stable entrypoints (`README.md`, `AGENTS.md`, `CLAUDE.md`, `SCRATCHPAD.md`, `.agents/*.md`) keep their exact names — do not rename them.
- Metadata timestamp fields (`Last reviewed`, `Last updated`, etc.) use `YYYYMMDD_hhmm` format.

#### Table of contents

- Any file that exceeds 100 lines **must** have a TOC.
- Generate the TOC automatically when creating or first extending a file past 100 lines.
- Place the TOC immediately after the document's main `#` heading (after any frontmatter, before the first section).
- Use a `## Contents` heading for the TOC section. Exclude the `#` title from the TOC itself.
- TOC anchors follow GitHub-flavored markdown: lowercase, spaces → hyphens, special characters stripped.
- When editing any long file that already has a TOC, update the TOC in the same pass — reflect any added or removed section headings before finishing.

#### Links and references

- In `README.md`, `readme.md`, and similar index files, references to other markdown files must be written as markdown links, not plain paths or filenames.
- Metadata fields (`Source of truth`, `Synced from`, `Synced to`) that name a specific file must render that file as a markdown link.
- Keep generic filename patterns and placeholders as code literals (e.g. `` `<slug>-YYYYMMDD_hhmm.md` ``) unless they refer to a single concrete existing document.

#### Quality pass

- After writing or editing a markdown file, fix malformed list structure, awkward rendering, and stale headings in the same pass.
- Treat `README.md` as a navigation and inventory surface: lead with folder index and governance pointers, not prose.

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

**Extraction rules:** apply heuristics from [`patterns/archcore-routing.md`](../patterns/archcore-routing.md).

**Output:** write `ARCHCORE_PROMOTION_CANDIDATES.md` in the project root. Format per `patterns/archcore-routing.md`. Do not create any `.archcore/` content files — report only.

**Tell the user:** "Review `ARCHCORE_PROMOTION_CANDIDATES.md`, then run `/skill-ai-it promote` to authorize writing Archcore content."

- On `refresh`: re-scan and update `ARCHCORE_PROMOTION_CANDIDATES.md`; do not overwrite existing `.archcore/` content.
- On `audit`: report what candidates would be surfaced; do not write the file.
- On `promote`: read `ARCHCORE_PROMOTION_CANDIDATES.md`; write or propose `.archcore/` content files with provenance headers and `status: proposed`; write or update `.archcore/index.guide.md` as the
  index; carry any still-relevant *never promote* reasoning into that index; then **delete `ARCHCORE_PROMOTION_CANDIDATES.md`**.

#### The candidates file is transient — promote deletes it

`ARCHCORE_PROMOTION_CANDIDATES.md` is a **proposal queue**, not a record. It exists between the run that surfaces candidates and the run that promotes them, and `promote` removes it.

Two reasons, and the second is the one that bites:

1. **A queue that outlives its proposals becomes a stale second index.** Once the documents exist, a file listing them under a name that says "candidates" is a governance surface misdescribing its own
   contents — and a later session reading it cannot tell a pending proposal from a completed one.

2. **It lives at the repo root, which `bootstrap` and `refresh` both rewrite.** Anything durable recorded there is destroyed by the next skill invocation with no trace. Observed 2026-08-25: a
   post-promotion ledger was written into it and would have been silently erased on the next refresh.

**The durable index is `.archcore/index.guide.md`**, written or updated by `promote`: what each document governs, the `status:` of the set, how to propose another, and — carried out of the candidates
file before it is deleted — what is **deliberately never promoted** and why. That last table is the part a future scan needs, or it re-proposes the same rejected candidates every refresh.

**Not `.archcore/README.md`.** `archcore status` rejects any `.md` under `.archcore/` that isn't named `<slug>.<type>.md` with YAML frontmatter — a bare `README.md` there reports as an issue, not an
index. Give `index.guide.md` frontmatter too: `title`, `status: accepted`, `tags: [index]` — it is itself an archcore document, not an exception to the naming rule.

Point the project's orphan check at `.archcore/index.guide.md`, not at the candidates file. Register the candidates filename in the checker's `CONDITIONAL_PATHS` with its reason, so historical
mentions in `CHANGELOG.md` do not fail path resolution once the file is gone — history is not a live claim.

### Graphify initialization and refresh

**Disabled (operator, 2026-10-10).** Do not run `graphify update .` in any mode, and do not add Graphify recipes or hooks to a project. Measured that day: 0 `graphify query`/`path`/`explain` calls in 30 days of agent sessions against thousands of rebuilds, and most `graphify-out/` folders behind their project ([assessment](/Volumes/Data/_ai/_project/project_stuff/apn/unified-network-controller/docs/reports/knowledge-tooling/okf-adoption-assessment-20261010_1700.md), section 5). The 25 existing `graphify-out/` folders were deleted the same day (operator); tracked ones through `git rm`, so history keeps them. Project recipes and `templates/context_preflight.sh` skip it unless `GRAPHIFY_ENABLED=1` is set. Re-enable only on the operator's decision, by removing this paragraph and the gates. The rules below are kept for that day.

When enabled: run `graphify update .` whenever the `graphify` CLI is available, in all active modes (`bootstrap`, `navigation-add`, `refresh`).

- If `graphify-out/` is missing and the CLI is available, `graphify update .` will initialize and populate it.
- If `graphify-out/` already exists, `graphify update .` refreshes the graph on every run.
- Treat `graphify-out/GRAPH_REPORT.md` and `graphify-out/graph.json` as disposable generated support — always regenerable, never canonical truth.
- In `audit` mode: report whether Graphify would run, but do not invoke it unless the user requests changes.

### Repomix initialization and refresh

Run Repomix whenever the `repomix` CLI is available, in all active modes (`bootstrap`, `navigation-add`, `refresh`).

- If `repomix.config.json` is missing and the CLI is available, create it from `templates/repomix.config.json`, then run `repomix --config repomix.config.json`.
- If `repomix.config.json` already exists, run `repomix --config repomix.config.json` to refresh the context pack.
- Treat `repomix-output.md` and `.ai-context/` as disposable generated support — always regenerable, never canonical truth.
- In `audit` mode: report whether Repomix would run, but do not invoke it unless the user requests changes.
