# Automatic Repo Knowledge Capture on Push

## Summary
Add a local-only `pre-push` Git hook in the `ansible-wifi` clone that runs the canonical `repo-knowledge-capture` helper before every push. The hook executes the capture workflow for this repo, prints clear status, and blocks the push if capture fails.

This is clone-local automation, not a tracked repo feature. It will not be pushed to the remote and will not affect other clones unless explicitly installed there too.

## Key Changes
- Create a local `.git/hooks/pre-push` hook in the `ansible-wifi` clone.
- Hook behavior:
  - resolve repo root from the hook location
  - call the canonical helper at `/Volumes/Data/_ai/_skills/skills_stuff/specialists/project/skill-repo-knowledge-capture/scripts/repo_knowledge_capture.sh`
  - run `setup`
  - run `snapshot`
  - determine the newest snapshot name
  - run `history-init`
  - run `history-commit`
- Failure policy:
  - print a clear warning/error to stderr
  - exit non-zero
  - block the push until capture succeeds
- Scope of capture:
  - `.serena/`
  - `.smart-coding-cache/`
  - `AGENTS.md`
  - `.agents/`
  - `.vscode/`
- Keep this local-only:
  - use `.git/hooks/pre-push`, not tracked hook infrastructure
  - do not introduce repo-tracked hook files or `core.hooksPath` changes unless explicitly requested later
- Update `repo-knowledge-capture` canonical/runtime docs so hook-based automation is recognized as a supported local workflow.

## Test Plan
- Run the hook manually with `.git/hooks/pre-push` from the repo root and confirm it:
  - creates a new snapshot under `~/_ansible/local-knowledge/ansible-wifi/snapshots/<timestamp>`
  - creates or updates `~/_ansible/local-knowledge/ansible-wifi/history`
  - records a new history commit when content changed
- Simulate helper failure by executing a temporary copy of the hook that points at a bad helper path and confirm:
  - the hook prints a clear failure message
  - the hook exits non-zero and would block push
- Confirm no repo-tracked files are changed by the hook itself.

## Assumptions
- Installation target is the current local `ansible-wifi` clone only.
- The canonical helper path remains `/Volumes/Data/_ai/_skills/skills_stuff/specialists/project/skill-repo-knowledge-capture/scripts/repo_knowledge_capture.sh`.
- Default capture root remains `~/_ansible/local-knowledge/ansible-wifi/`.
- Blocking push on capture failure is the intended enforcement model.
