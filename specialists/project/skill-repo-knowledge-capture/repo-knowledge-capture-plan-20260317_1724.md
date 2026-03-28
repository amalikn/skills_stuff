# Repo Knowledge Capture Skill Plan

## Summary
Create a canonical skill pack named `skill-repo-knowledge-capture` under `skills_stuff` and export it for Codex as `repo-knowledge-capture`. The skill captures and versions local repo knowledge artifacts such as `.serena/` and `.smart-coding-cache/` outside the target GitHub/Bitbucket repository so nothing is pushed or tracked in the production repo.

The workflow is explicit-use only. Default behavior is local-only safety first: add local git excludes, snapshot the knowledge directories outside the repo, and maintain optional local-only history in a separate git repository.

## Key Changes
### Canonical skill structure
Create the canonical specialist at:

`/Volumes/Data/_ai/_mcp/skills_stuff/specialists/project/skill-repo-knowledge-capture`

Include these files:
- `manifest.json`
- `PROFILE.md`
- `RUNBOOK.md`
- `SYSTEM_PROMPT.md`
- `REVISION_HISTORY.md`
- `CHANGELOG.md`
- `KNOWN_ISSUES.md`
- `CONTEXT/assumptions.md`
- `CONTEXT/boundaries.md`
- `CONTEXT/dependencies.md`
- `CONTEXT/relationships.md`
- `CHECKLISTS/triage.md`
- `CHECKLISTS/change.md`
- `CHECKLISTS/rollback.md`
- `CHECKLISTS/healthcheck.md`
- `scripts/repo_knowledge_capture.sh`

The canonical specialist is the only authoring surface. Future edits should happen there, not in exports.

### Codex export and install shape
Render a Codex export at:

`/Volumes/Data/_ai/_mcp/skills_stuff/exports/codex/project/skill-repo-knowledge-capture`

Export only the Codex-facing adapter files needed by the runtime packaging model. Install the runtime skill as:

`~/.codex/skills/repo-knowledge-capture`

The runtime skill should expose a concise `SKILL.md` that tells Codex when to use the helper script and what safety constraints apply.

### Runtime behavior
The skill must support any local git clone, regardless of whether the remote is GitHub or Bitbucket. It should determine the repo name from the local repo path and use this storage root:

`~/_ansible/local-knowledge/<repo-name>/`

Standard layout:
- `snapshots/<YYYYMMDD_hhmm>/`
- `history/` as a separate local-only git repo

The helper script must require an explicit repo path and implement these commands:
- `setup`
  - append `.serena/` and `.smart-coding-cache/` to `.git/info/exclude` only if missing
  - never edit tracked `.gitignore`
- `snapshot`
  - copy `.serena/` and `.smart-coding-cache/` into `snapshots/<timestamp>/`
  - tolerate either directory being absent
- `history-init`
  - initialize `history/` as a standalone local-only git repo if not already present
- `history-commit`
  - stage the current snapshot set in `history/` and commit only if content changed
  - never configure remotes or run `git push`
- `restore`
  - restore one named snapshot back into the target repo working tree
  - replace only `.serena/` and `.smart-coding-cache/`

### Skill contract and safety
The skill must state these rules clearly:
- Never store captured knowledge inside tracked files of the target repo unless the user explicitly asks for that
- Never run `git push`
- Never modify repo-tracked files as part of the normal workflow
- `.git/info/exclude` is the correct local-only ignore mechanism
- `.serena/` is durable knowledge and `.smart-coding-cache/` is local cache/state; both may be captured, but the user should not rely only on the cache database as canonical knowledge

## Test Plan
- Validate canonical specialist layout matches the existing `skills_stuff` specialist pattern
- Validate Codex export exists and installs cleanly into `~/.codex/skills/repo-knowledge-capture`
- Run the helper on a test repo containing `.serena/` and `.smart-coding-cache/`
- Confirm `.git/info/exclude` is updated locally and no tracked repo files change
- Confirm snapshots are created under `~/_ansible/local-knowledge/<repo-name>/snapshots/<timestamp>/`
- Confirm `history-init` creates a standalone local git repo under `history/`
- Confirm `history-commit` creates a commit only when snapshot contents changed
- Confirm `restore` recreates `.serena/` and `.smart-coding-cache/` from a selected snapshot
- Confirm the workflow is identical for both GitHub-backed and Bitbucket-backed clones because it depends only on local git layout

## Assumptions
- The skill is explicitly invoked by the user and is not auto-triggered in unrelated sessions
- `skills_stuff` remains the canonical source of truth and exports are derived artifacts
- Codex is the first runtime target; other runtimes can be added later via separate exports
- The default local knowledge root is `~/_ansible/local-knowledge/`
- No remote synchronization or cloud backup is part of v1
