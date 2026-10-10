---
Title: skill-ai-it reference: Finishing: parent update, conventions, quality check, audit format
Category: reference
Status: current
Authority: local-supplement
Scope: On-need reference moved verbatim from SKILL.md
Last reviewed: 2026-10-10
Summary: >-
  Finishing: parent update, conventions, quality check, audit format; moved verbatim from SKILL.md so SKILL.md stays an orchestration file within budget.
---

# skill-ai-it reference: Finishing: parent update, conventions, quality check, audit format

Moved verbatim from `SKILL.md` on 2026-10-10 to keep that file within its budget for files loaded whole.

## Contents

- [Phase 5 — Update Parent](#phase-5--update-parent)
- [Conventions Baked In](#conventions-baked-in)
- [Quality Check Before Completing](#quality-check-before-completing)
- [Audit Output Format](#audit-output-format)

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
- Nor an *implicit* `mise exec -- python`: address the venv interpreter by path via `{{py}}` and guard it with `_require-venv`, so a missing venv fails loudly instead of degrading to the host
  interpreter. Give `.mise.toml` tasks the absolute venv path for the same reason

- Generate `just bootstrap` and `just runtimes` alongside any pinned-runtime justfile; without `runtimes` the pinning cannot be verified quickly
- For risky changes to existing YAML/JSON, write `.proposed` files rather than overwriting

## Quality Check Before Completing

- [ ] All `@` import paths in AGENTS.md resolve to real files
- [ ] The project's justfile runs `doc_freshness.py --check` in `check` and has a `stale` recipe; a baseline exists when findings predate adoption
- [ ] CLAUDE.md contains only the `@AGENTS.md` import line + additions section
- [ ] README.md Folder index links resolve to real subfolders
- [ ] Parent README/AGENTS updated if they exist
- [ ] If `archcore` CLI is available and the run mode allowed changes, `.archcore/` exists or the initialization failure is reported
- [ ] If `.archcore/` exists after `bootstrap`, `navigation-add`, or `refresh`, `ARCHCORE_PROMOTION_CANDIDATES.md` exists in the target root or the final report explicitly explains why it was not
  created/updated. After `promote` the opposite holds: the candidates file must be **gone**, its *never promote* reasoning carried into `.archcore/index.guide.md`, and no governance surface still
  routing to it

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

- [ ] **No recipe reaches Python through an implicit `mise exec -- python`** — grep for it. Every Python recipe addresses `{{py}}` by path, and `mise run` tasks in `.mise.toml` carry the absolute venv
  path too, so the justfile and the mise tasks cannot resolve differently. Verify by confirming `just runtimes` reports the working-cache venv, not a host or mise-shim path

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
- [ ] `.markdownlint-cli2.jsonc` exists (created from `templates/.markdownlint-cli2.jsonc` or already owned by the project) — never both created and left conflicting with an existing config
- [ ] If `repomix.config.json` exists and `.archcore/` exists, `.archcore/**/*.md` is included; `ARCHCORE_PROMOTION_CANDIDATES.md` is included only while it exists (pre-promote)
- [ ] After `promote`: `.archcore/index.guide.md` (with `title`/`status`/`tags` frontmatter — not `.archcore/README.md`, which `archcore status` rejects) indexes every document written, the orphan
  check points at it rather than at the candidates file, and the candidates filename is registered in `CONDITIONAL_PATHS` so historical mentions do not fail path resolution

- [ ] `archcore status` was run after `promote` and reports the new documents cleanly (no "unrecognized file" issues)
- [ ] If a repo-local `scripts/context_preflight.sh` was explicitly requested, it is executable or the user was told to run `chmod +x scripts/context_preflight.sh`
- [ ] Existing YAML/JSON files were not destructively regenerated during refresh mode
- [ ] Existing `.archcore/` documents were not directly edited unless explicitly authorized
- [ ] Drift/conflict findings were reported instead of silently resolved
- [ ] SCRATCHPAD.md was populated from memory systems (not blank) — or "no prior memory" note added if all sources empty
- [ ] SCRATCHPAD.md synthesized content is marked `KEEP`

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
