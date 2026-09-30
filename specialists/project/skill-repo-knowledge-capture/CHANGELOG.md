# CHANGELOG

## 0.1.1 (2026-09-30)
- Fixed: run as a pre-push hook from a linked git worktree, the helper inherited `GIT_DIR` and its `git -C <history dir>` calls acted on the
  repo being pushed: it wrote the history identity into that repo's config and committed the snapshot onto its checked-out branch (ansible-wifi,
  2026-09-30; cleaned up by hand). The helper now clears git's repo-locating variables before any git call. Reproduced in a throwaway repo
  before the fix (branch moved, identity written, no history commit) and passing after it.

## 0.1.0
- Added canonical specialist for local-only repo knowledge capture.
- Added deterministic helper script for setup, snapshot, history init/commit, and restore.
- Added Codex export and runtime installation target.
- Extended capture workflow to include `AGENTS.md` and `.agents/` as local repo guidance artifacts.
- Clarified that the default local-only exclude set is `.serena/`, `.smart-coding-cache/`, `AGENTS.md`, `.agents/`, and `.vscode/`.
- Extended capture workflow and default local-only exclude guidance to include `.vscode/` for local editor overrides.
- Added documented support for clone-local `pre-push` hook automation that blocks push on capture failure.
