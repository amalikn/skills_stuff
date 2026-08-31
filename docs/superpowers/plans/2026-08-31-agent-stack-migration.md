# Agent Stack Migration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox
> (`- [ ]`) syntax for tracking.

**Goal:** Move Auto Company's complete persona and skill library into the canonical `agent-stack` pack, then replace Auto Company's local directories with symlinks to that pack.

**Architecture:** `skills_stuff/specialists/agent-stack/` becomes the only authoring surface. Auto Company keeps its existing `.claude/agents` and `.claude/skills` paths as absolute directory
symlinks, while its loop, consensus state, settings, and prompts remain local.

**Tech Stack:** Git worktrees, shell inventory commands, Markdown/YAML, directory symlinks.

## Contents

- [Task 1: Establish the migration baseline and commit gate](#task-1-establish-the-migration-baseline-and-commit-gate)
- [Task 2: Create the English-only canonical content](#task-2-create-the-english-only-canonical-content)
- [Task 3: Add the canonical manifest and installation documentation](#task-3-add-the-canonical-manifest-and-installation-documentation)
- [Task 4: Update source-of-truth indexes](#task-4-update-source-of-truth-indexes)
- [Task 5: Integrate the canonical pack and make the symlink cutover](#task-5-integrate-the-canonical-pack-and-make-the-symlink-cutover)
- [Task 6: Verify the completed migration and preserve recovery evidence](#task-6-verify-the-completed-migration-and-preserve-recovery-evidence)
- [Task 7: Add the upstream refresh workflow](#task-7-add-the-upstream-refresh-workflow)

---

### Task 1: Establish the migration baseline and commit gate

**Files:**

- Create: `/private/tmp/agent-stack-migration/baseline-paths.txt`
- Create: `/private/tmp/agent-stack-migration/baseline-sha256.txt`
- Create: `/private/tmp/agent-stack-migration/non-english-baseline.txt`
- Modify: `/Volumes/Data/_ai/_skills/skills_stuff/.gitignore` only if the approved `.worktrees/` entry is still uncommitted
- Test: both repositories' worktree and path inventories

- [ ] **Step 1: Capture the exact source inventory before content changes**

Run:

```bash
mkdir -p /private/tmp/agent-stack-migration
cd /Volumes/Data/_ai/_tool/tools_stuff/auto-company
find .claude/agents .claude/skills -type f | LC_ALL=C sort > /private/tmp/agent-stack-migration/baseline-paths.txt
shasum -a 256 $(cat /private/tmp/agent-stack-migration/baseline-paths.txt) > /private/tmp/agent-stack-migration/baseline-sha256.txt
```

Expected: 14 persona files and 170 skill files are recorded before any migration write.

- [ ] **Step 2: Capture every non-English or non-ASCII language occurrence**

Run:

```bash
cd /Volumes/Data/_ai/_tool/tools_stuff/auto-company
rg -n -P '[\x{4E00}-\x{9FFF}\x{3040}-\x{30FF}\x{AC00}-\x{D7AF}\x{0400}-\x{04FF}]' .claude/agents .claude/skills > /private/tmp/agent-stack-migration/non-english-baseline.txt
```

Expected: the 14 persona files, `skills/team/SKILL.md`, `skills/github-explorer/SKILL.md`, and two Cyrillic identifier occurrences in `skills/web-scraping/SKILL.md` are captured.

- [ ] **Step 3: Verify that the canonical repository can commit without bypassing policy**

Run:

```bash
cd /Volumes/Data/_ai/_skills/skills_stuff/.worktrees/agent-stack
git commit --dry-run -m "chore: verify agent-stack commit gate"
```

Expected: PASS. If the existing `AGENTS.md` line-count guard still fails, stop before Task 5; do not use `--no-verify`, do not alter unrelated governance, and obtain an operator decision.

- [ ] **Step 4: Commit the worktree-ignore rule if the gate passes**

Run:

```bash
cd /Volumes/Data/_ai/_skills/skills_stuff
git add .gitignore
git commit --only .gitignore -m "chore: ignore local worktrees"
```

Expected: `.worktrees/` is tracked as ignored without staging unrelated work.

### Task 2: Create the English-only canonical content

**Files:**

- Create: `specialists/agent-stack/personas/` with the 14 files listed below
- Create: `specialists/agent-stack/skills/` with all 36 current skill entries and 170 source files
- Test: source-to-canonical path comparison and English-content audit

- [ ] **Step 1: Copy the source tree into the canonical pack while preserving package layout**

Create `specialists/agent-stack/personas/` from `.claude/agents/` and `specialists/agent-stack/skills/` from `.claude/skills/`. Preserve all file names, package directories, executable bits,
reference folders, templates, scripts, and `.gitignore` files. Do not move `settings.json`, `PROMPT.md`, `consensus.md`, or any loop component.

Expected canonical personas: `ceo-bezos.md`, `cfo-campbell.md`, `critic-munger.md`, `cto-vogels.md`, `devops-hightower.md`, `fullstack-dhh.md`, `interaction-cooper.md`,
`marketing-godin.md`, `operations-pg.md`, `product-norman.md`, `qa-bach.md`, `research-thompson.md`, `sales-ross.md`, and `ui-duarte.md`.

- [ ] **Step 2: Translate the identified Chinese prose into idiomatic English**

Translate every prose field, heading, instruction, table cell, and template in all 14 persona files, `skills/team/SKILL.md`, and `skills/github-explorer/SKILL.md`. Preserve Markdown structure, YAML
keys, command names, code fences, URLs, and role/file identifiers. Change output-language instructions from Chinese to English. Translate the Chinese example search terms and report-template
placeholders in `github-explorer` to English equivalents.

Expected: the translated documents preserve their original purpose and runnable examples while containing English prose only.

- [ ] **Step 3: Remove the Cyrillic lookalike identifier from web-scraping**

In `skills/web-scraping/SKILL.md`, rename `TrafilaturaСscraper` to ASCII-only `TrafilaturaCscraper` in both its class definition and its instantiation. No other code or behaviour changes are
permitted in this file.

Expected: the two references still match exactly and no Cyrillic script remains in the canonical pack.

- [ ] **Step 4: Prove the canonical tree is structurally complete and English-only**

Run:

```bash
cd /Volumes/Data/_ai/_tool/tools_stuff/auto-company
find .claude/agents .claude/skills -type f | sed 's#^.claude/agents/#personas/#; s#^.claude/skills/#skills/#' | LC_ALL=C sort > /private/tmp/agent-stack-migration/source-relative-paths.txt
cd /Volumes/Data/_ai/_skills/skills_stuff/.worktrees/agent-stack
find specialists/agent-stack/personas specialists/agent-stack/skills -type f | sed 's#^specialists/agent-stack/##' | LC_ALL=C sort > /private/tmp/agent-stack-migration/canonical-relative-paths.txt
diff -u /private/tmp/agent-stack-migration/source-relative-paths.txt /private/tmp/agent-stack-migration/canonical-relative-paths.txt
rg -n -P '[\x{4E00}-\x{9FFF}\x{3040}-\x{30FF}\x{AC00}-\x{D7AF}\x{0400}-\x{04FF}]' specialists/agent-stack || true
```

Expected: path comparison has no output; the language audit has no output.

### Task 3: Add the canonical manifest and installation documentation

**Files:**

- Create: `specialists/agent-stack/manifest.yaml`
- Create: `specialists/agent-stack/README.md`
- Test: YAML parse and manifest-to-filesystem consistency check


- [ ] **Step 1: Create `manifest.yaml` with all portable capabilities**

List the 14 personas as `kind: persona`. List all 36 skills with `kind: package` except `frontend-design`, which is `kind: single_file`. Every capability entry must have `id`, `kind`, `path`, and
`portability` fields.

Use `portability: general` for:

```text
code-review-security
cold-email-sequence-generator
community-led-growth
competitive-intelligence-analyst
content-strategy
deep-analysis
deep-reading-analyst
deep-research
email-sequence
financial-unit-economics
find-skills
frontend-design
market-sizing-analysis
micro-saas-launcher
ph-community-outreach
premortem
pricing-strategy
product-strategist
scientific-critical-thinking
security-audit
senior-qa
seo-audit
seo-content-strategist
skill-creator
startup-business-models
startup-financial-modeling
team
user-persona-creation
user-research-synthesis
ux-audit-rethink
web-scraping
```

Use `portability: tool-specific` for:

```text
agent-browser
devops
github-explorer
tailwind-v4-shadcn
websh
```

Record the canonical relative path for every entry.

Expected: the manifest includes all 50 capabilities, has no runtime scheduling fields, and distinguishes selection guidance from enforced policy.

- [ ] **Step 2: Create the pack README**

Document the pack purpose, exclusions, English-only rule, portability tags, and symlink-only installation model. Include these canonical target paths:

```text
/Volumes/Data/_ai/_skills/skills_stuff/specialists/agent-stack/personas
/Volumes/Data/_ai/_skills/skills_stuff/specialists/agent-stack/skills
```

State that Auto Company's loop and `consensus.md` are not part of `agent-stack`, and that other projects must link only the persona or skill entries they select.

- [ ] **Step 3: Validate the manifest**

Run:

```bash
cd /Volumes/Data/_ai/_skills/skills_stuff/.worktrees/agent-stack
ruby -e 'require "yaml"; YAML.load_file("specialists/agent-stack/manifest.yaml"); puts "manifest parses"'
```

Expected: `manifest parses` and no YAML exception.

### Task 4: Update source-of-truth indexes

**Files:**

- Modify: `README.md`
- Modify: `REVISION_HISTORY.md`
- Modify: `docs/superpowers/specs/2026-08-31-agent-stack-design.md` only if the approved implementation differs from it
- Test: Markdown links and index references by inspection

- [ ] **Step 1: Add Agent Stack to the canonical repository index**

Add `specialists/agent-stack/` to the root README folder index and identify it as the canonical home for Auto Company-derived personas and skills. Do not label it an Auto Company runtime component.

- [ ] **Step 2: Record the source-of-truth change**

Add an entry to `REVISION_HISTORY.md` describing the new canonical pack, English-only translation, and symlink-only installation rule. Preserve the file's existing chronological convention.

- [ ] **Step 3: Validate repository documentation**

Run:

```bash
cd /Volumes/Data/_ai/_skills/skills_stuff/.worktrees/agent-stack
git diff --check
rg -n 'agent-stack' README.md REVISION_HISTORY.md specialists/agent-stack/README.md
```

Expected: no whitespace errors and each index points to the canonical pack.

### Task 5: Integrate the canonical pack and make the symlink cutover

**Files:**

- Modify: `/Volumes/Data/_ai/_skills/skills_stuff` through a reviewed merge of the `agent-stack` worktree branch
- Modify: `/Volumes/Data/_ai/_tool/tools_stuff/auto-company/.claude/agents` as a directory symlink
- Modify: `/Volumes/Data/_ai/_tool/tools_stuff/auto-company/.claude/skills` as a directory symlink
- Modify: `/Volumes/Data/_ai/_tool/tools_stuff/auto-company/README.md`
- Test: symlink resolution and unchanged exclusion paths

- [ ] **Step 1: Commit and merge the canonical pack after the commit gate passes**

Commit only the plan-approved `agent-stack`, index, revision-history, and worktree-ignore changes. Merge the reviewed `agent-stack` branch into the main `skills_stuff` checkout without staging or
committing its unrelated existing work.

Expected: `/Volumes/Data/_ai/_skills/skills_stuff/specialists/agent-stack/` exists on the canonical branch before Auto Company is changed.

- [ ] **Step 2: Preserve a temporary rollback snapshot and replace the source directories**

Move the existing Auto Company `.claude/agents` and `.claude/skills` directories to `/private/tmp/agent-stack-migration/rollback/`. Create these absolute directory symlinks in their former
locations:

```text
.claude/agents -> /Volumes/Data/_ai/_skills/skills_stuff/specialists/agent-stack/personas
.claude/skills -> /Volumes/Data/_ai/_skills/skills_stuff/specialists/agent-stack/skills
```

Expected: Auto Company has no copied persona or skill library after the cutover; the temporary rollback snapshot is outside both repositories.

- [ ] **Step 3: Document Auto Company's new source-of-truth boundary**

Update the Auto Company README's agent/skill description to state that `.claude/agents` and `.claude/skills` are symlinked views of `skills_stuff/specialists/agent-stack/`. State explicitly that
the loop, prompt, consensus file, and daemon remain Auto Company-local.

### Task 6: Verify the completed migration and preserve recovery evidence

**Files:**

- Verify: both repository diffs, the two Auto Company directory symlinks, and all canonical files
- Remove: `/private/tmp/agent-stack-migration/rollback/` only after all checks pass

- [ ] **Step 1: Validate every symlink and every expected file path**

Run:

```bash
cd /Volumes/Data/_ai/_tool/tools_stuff/auto-company
test -L .claude/agents && test "$(readlink .claude/agents)" = "/Volumes/Data/_ai/_skills/skills_stuff/specialists/agent-stack/personas"
test -L .claude/skills && test "$(readlink .claude/skills)" = "/Volumes/Data/_ai/_skills/skills_stuff/specialists/agent-stack/skills"
test "$(find .claude/agents -maxdepth 1 -type f -name '*.md' | wc -l | tr -d ' ')" = 14
test "$(find .claude/skills -type f | wc -l | tr -d ' ')" = 170
find .claude/skills -type f -name SKILL.md -exec test -r {} \;
```

Expected: exit code 0; 14 persona files, 170 skill files, and all `SKILL.md` files readable through Auto Company's links.

- [ ] **Step 2: Prove excluded Auto Company state was untouched**

Run:

```bash
cd /Volumes/Data/_ai/_tool/tools_stuff/auto-company
git diff -- scripts/core/auto-loop.sh memories/consensus.md .claude/settings.json PROMPT.md
git diff --check
cd /Volumes/Data/_ai/_skills/skills_stuff
git diff --check
```

Expected: the first diff has no output for the excluded paths; both whitespace checks pass.

- [ ] **Step 3: Remove the temporary rollback snapshot only after evidence is clean**

Run:

```bash
test -L /Volumes/Data/_ai/_tool/tools_stuff/auto-company/.claude/agents
test -L /Volumes/Data/_ai/_tool/tools_stuff/auto-company/.claude/skills
rm -rf /private/tmp/agent-stack-migration/rollback
```

Expected: no local duplicate library remains. If any validation fails, restore the two original directories from the rollback snapshot instead of deleting it.

### Task 7: Add the upstream refresh workflow

**Files:**

- Create: `specialists/agent-stack/.mise.toml`
- Create: `specialists/agent-stack/justfile`
- Create: `specialists/agent-stack/scripts/sync_auto_company.py`
- Create: `specialists/agent-stack/upstream-state.json`
- Create: `specialists/agent-stack/tests/test_sync_auto_company.py`
- Modify: `specialists/agent-stack/README.md`
- Test: `tests/test_sync_auto_company.py`

- [ ] **Step 1: Write failing refresh-classification tests**

Create stdlib `unittest` cases that make temporary Git repositories and exercise these outcomes: an added upstream English file is `safe_add`; an upstream English change to an unchanged canonical file
is `safe_replace`; Chinese or other non-English upstream prose is `translation_required`; a canonical file changed since its recorded import is `manual_merge`; and an upstream deletion is
`remove_review`.

Run:

```bash
cd /Volumes/Data/_ai/_skills/skills_stuff/.worktrees/agent-stack/specialists/agent-stack
mise exec -- python -m unittest tests/test_sync_auto_company.py -v
```

Expected: FAIL because `scripts/sync_auto_company.py` does not exist.

- [ ] **Step 2: Implement the stdlib-only sync script**

Create `scripts/sync_auto_company.py` with `--dry-run`, `--apply`, `--fetch`, `--upstream-url`, `--branch`, and `--working-cache` arguments. The default upstream URL is
`https://github.com/MaxMiksa/Auto-Company.git`; the default working mirror is `/Volumes/Data/_ai/_skills/skills-working-cache/agent-stack/upstreams/auto-company`.

The script must clone or fetch that mirror only when `--fetch` is given. It must compare the upstream commit recorded in `upstream-state.json` with the fetched branch, inspect only
`.claude/agents` and `.claude/skills`, and classify each path using recorded source and canonical SHA-256 hashes. Dry-run writes no canonical files. Apply may write only `safe_add` and
`safe_replace` files that are English-only; it writes a timestamped report and proposal copies for `translation_required`, `manual_merge`, and `remove_review` paths.

- [ ] **Step 3: Add durable upstream state and a narrow Justfile interface**

Create `upstream-state.json` with the upstream URL, branch, `last_imported_commit`, and a per-file mapping of source and canonical hashes. Populate it after the initial migration. Create `.mise.toml`
with Python 3.14, then write a `justfile` whose recipes use `mise exec -- python`, never a bare interpreter.

The recipes must be:

```text
just upstream-status
just upstream-dry-run
just upstream-fetch-dry-run
just upstream-apply
```

`upstream-status` reads current state without network access. `upstream-dry-run` compares an existing mirror without fetching. `upstream-fetch-dry-run` fetches and classifies without writing canonical
files. `upstream-apply` requires an explicit `confirm=apply` argument and still writes proposals instead of overwriting translated or diverged files.

- [ ] **Step 4: Run the tests through red-green verification**

Run:

```bash
cd /Volumes/Data/_ai/_skills/skills_stuff/.worktrees/agent-stack/specialists/agent-stack
mise exec -- python -m unittest tests/test_sync_auto_company.py -v
just upstream-status
```

Expected: all tests pass; status reports the configured upstream and the last-imported commit without making a network request.

- [ ] **Step 5: Document and validate the update workflow**

Add a README section describing the four Just recipes, the classification meanings, the proposal-review path, and the fact that upstream refresh never imports Auto Company's loop, consensus, settings,
or prompts. Run `git diff --check`, `just --list`, and the complete test command. Confirm that all new prose and example output are English.
