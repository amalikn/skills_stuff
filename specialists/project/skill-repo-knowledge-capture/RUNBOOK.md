# RUNBOOK

## Use When
Use this specialist when the user explicitly wants to preserve or version local repo knowledge such as `.serena/`, `.smart-coding-cache/`, `AGENTS.md`, `.agents/`, or local `.vscode/` overrides without contaminating the production repository.

## Standard Workflow
1. Verify the target path is a git repo.
2. Run `setup` to add or confirm local-only excludes in `.git/info/exclude`.
3. Ensure the exclude set covers the local knowledge artifacts in scope. The default supported set is:
   - `.serena/`
   - `.smart-coding-cache/`
   - `AGENTS.md`
   - `.agents/`
   - `.vscode/`
4. Run `snapshot` to copy current local knowledge artifacts into `~/_ansible/local-knowledge/<repo-name>/snapshots/<timestamp>/`.
5. Run `history-init` once per repo if local history does not exist.
6. Run `history-commit` to record the latest snapshot into the separate `history/` repository.
7. Use `restore` only when the user explicitly wants to repopulate `.serena/`, `.smart-coding-cache/`, `AGENTS.md`, `.agents/`, or local `.vscode/` overrides in the target repo.

## Automation Mode
- A clone-local Git hook may run this workflow automatically before `git push`.
- Preferred implementation: `.git/hooks/pre-push` in the target clone.
- Hook sequence:
  - `setup`
  - `snapshot`
  - determine latest snapshot
  - `history-init`
  - `history-commit`
- If capture fails, the hook should print a clear error and exit non-zero so push is blocked.
- Keep this automation local-only; do not introduce tracked hook files or `core.hooksPath` changes unless the user explicitly asks for repo-wide hook management.

## Helper Script
- Script path: `scripts/repo_knowledge_capture.sh`
- Usage: `repo_knowledge_capture.sh <setup|snapshot|history-init|history-commit|restore> <repo-path> [snapshot-name]`
- `setup` is idempotent. It must preserve an existing local-only exclude set and add missing entries without editing tracked `.gitignore`.
- When a repo uses local VS Code overrides, the exclude set should also cover `.vscode/`. If `.vscode/settings.json` was previously tracked, keep local changes local with `skip-worktree` or remove `.vscode` from repo tracking.

## Safety Rules
- Never edit the target repo's tracked `.gitignore` as part of this workflow unless the user explicitly asks for repo-wide ignore behavior.
- Never write captured artifacts into tracked paths under the target repo.
- Never configure remotes or run `git push` from the `history/` repository.
