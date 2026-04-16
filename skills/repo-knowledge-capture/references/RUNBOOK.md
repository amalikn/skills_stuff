# RUNBOOK

## Use When
Use this specialist when the user explicitly wants to preserve or version local repo knowledge such as `.serena/`, `.smart-coding-cache/`, `AGENTS.md`, or `.agents/` without contaminating the production repository.

## Standard Workflow
1. Verify the target path is a git repo.
2. Run `setup` to add local-only excludes in `.git/info/exclude`.
3. Run `snapshot` to copy current local knowledge artifacts into `~/_ansible/local-knowledge/<repo-name>/snapshots/<timestamp>/`.
4. Run `history-init` once per repo if local history does not exist.
5. Run `history-commit` to record the latest snapshot into the separate `history/` repository.
6. Use `restore` only when the user explicitly wants to repopulate `.serena/`, `.smart-coding-cache/`, `AGENTS.md`, or `.agents/` in the target repo.

## Helper Script
- Script path: `scripts/repo_knowledge_capture.sh`
- Usage: `repo_knowledge_capture.sh <setup|snapshot|history-init|history-commit|restore> <repo-path> [snapshot-name]`

## Safety Rules
- Never edit the target repo's tracked `.gitignore` as part of this workflow.
- Never write captured artifacts into tracked paths under the target repo.
- Never configure remotes or run `git push` from the `history/` repository.
