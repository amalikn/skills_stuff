# Repo Knowledge Capture Skill Outcome

## Summary
Implemented the canonical specialist `skill-repo-knowledge-capture` under `skills_stuff`, added the Codex export, and installed the runtime skill as `~/.codex/skills/repo-knowledge-capture`.

The skill now provides a deterministic local-only workflow for preserving and versioning `.serena/` and `.smart-coding-cache/` outside the target repository.

## Implemented Artifacts
### Canonical specialist
Created under:

`/Volumes/Data/_ai/_skills/skills_stuff/specialists/project/skill-repo-knowledge-capture`

Implemented files:
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

### Codex export
Created under:

`/Volumes/Data/_ai/_skills/skills_stuff/exports/codex/project/skill-repo-knowledge-capture`

Implemented files:
- `SYSTEM.md`
- `AGENTS.fragment.md`
- `install.md`

### Runtime install
Installed under:

`/Users/malik.ahmad/.codex/skills/repo-knowledge-capture`

Implemented files include:
- `SKILL.md`
- `.skill_builder.json`
- copied reference files under `references/`

## Behavior Delivered
- `setup` adds `.serena/` and `.smart-coding-cache/` to `.git/info/exclude` only if missing
- `snapshot` stores copies under `~/_ansible/local-knowledge/<repo-name>/snapshots/<YYYYMMDD_hhmm>/`
- `history-init` creates a standalone local git repo under `history/`
- `history-commit` writes commits only in the local history repo and never pushes remotely
- `restore` restores `.serena/` and `.smart-coding-cache/` from a named snapshot back into the target repo
- local history commits set a dedicated local git identity automatically so they do not depend on global git config

## Validation Result
Validated successfully on a throwaway git repo using a temporary knowledge root.

Checks completed:
- `.git/info/exclude` updated locally only
- snapshots created successfully
- `history-init` created a standalone git repo
- `history-commit` created a commit in local history
- `restore` recreated both `.serena/` and `.smart-coding-cache/`
- target repo tracked files remained unchanged during the workflow

## Notes
Current uncommitted changes in `skills_stuff`:
- `exports/codex/project/skill-repo-knowledge-capture/`
- `specialists/project/skill-repo-knowledge-capture/`

The runtime skill currently targets Codex first. Additional exports for other runtimes can be added later from the same canonical specialist.
