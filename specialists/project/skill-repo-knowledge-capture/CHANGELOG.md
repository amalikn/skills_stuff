# CHANGELOG

## 0.1.0
- Added canonical specialist for local-only repo knowledge capture.
- Added deterministic helper script for setup, snapshot, history init/commit, and restore.
- Added Codex export and runtime installation target.
- Extended capture workflow to include `AGENTS.md` and `.agents/` as local repo guidance artifacts.
- Clarified that the default local-only exclude set is `.serena/`, `.smart-coding-cache/`, `AGENTS.md`, `.agents/`, and `.vscode/`.
- Extended capture workflow and default local-only exclude guidance to include `.vscode/` for local editor overrides.
- Added documented support for clone-local `pre-push` hook automation that blocks push on capture failure.
