# Repo Local Guidance Outcome

Date: 2026-03-17 18:28 AEDT

## Summary
Implemented the local-only repo guidance split for `ansible-wifi` by replacing the long root `AGENTS.md` with a thin auto-loaded file, moving longer repo-specific guidance into `.agents/`, keeping both local-only via `.git/info/exclude`, creating a canonical `skill-repo-local-guidance` specialist, and updating related runtime/canonical skills to support the workflow.

## Implemented Changes
- Replaced repo root `AGENTS.md` with a thin local-only guide that points to `.agents/` support docs.
- Added repo-local support docs:
  - `.agents/repo-map.md`
  - `.agents/topology-and-derived-artifacts.md`
  - `.agents/validation.md`
  - `.agents/task-patterns.md`
- Added `AGENTS.md` and `.agents/` to `ansible-wifi/.git/info/exclude`.
- Created canonical specialist `skill-repo-local-guidance` under `skills_stuff/specialists/project`.
- Created Codex export for `skill-repo-local-guidance` under `skills_stuff/exports/codex/project`.
- Installed runtime skill `repo-local-guidance` under `~/.codex/skills`.
- Updated canonical `skill-repo-bootstrap-and-governance` to prefer thin root `AGENTS.md` plus `.agents/` for local-only repo guidance.
- Updated canonical `skill-repo-knowledge-capture` and its helper script so it captures and restores:
  - `.serena/`
  - `.smart-coding-cache/`
  - `AGENTS.md`
  - `.agents/`
- Patched runtime `SKILL.md` files for:
  - `repo-local-guidance`
  - `repo-bootstrap-and-governance`
  - `repo-knowledge-capture`
  so the installed skills describe the actual workflow instead of the generic generated wrapper.

## Validation
- Confirmed thin root `AGENTS.md` exists and points to `.agents/` docs.
- Confirmed `.agents/` exists with focused repo-specific support docs.
- Confirmed `.git/info/exclude` contains:
  - `AGENTS.md`
  - `.agents/`
- Confirmed `git status --short -- AGENTS.md .agents .gitignore` in `ansible-wifi` hides `AGENTS.md` and `.agents/`; only the pre-existing non-semantic `.gitignore` newline diff remains visible.
- Validated installed runtime skills with `mcp_skill_builder`:
  - `repo-local-guidance`
  - `repo-bootstrap-and-governance`
  - `repo-knowledge-capture`
  all returned `valid: true`.
- Ran an end-to-end throwaway repo test for the updated `repo-knowledge-capture` helper using `setup`, `snapshot`, `history-init`, `history-commit`, and `restore` with `REPO_KNOWLEDGE_ROOT` pointed at `/tmp`.
- Verified the helper restored:
  - `AGENTS.md`
  - `.agents/`
  - `.serena/`
  - `.smart-coding-cache/`
  and created a local-only history commit.

## Caveats
- The installed runtime `SKILL.md` files were patched after install because the current canonical export/install pipeline still renders weak generic wrappers by default.
- Reinstalling these runtime skills from canonical source may overwrite the strengthened runtime wording unless the export/render path is improved later.
- `ansible-wifi/.gitignore` still shows the pre-existing trailing-blank-line diff; no ignore rules were changed there.

## Next Steps
1. Improve the canonical export/render path so runtime `SKILL.md` generation preserves richer trigger text.
2. Commit the new/updated specialist and export directories in `skills_stuff` if you want these changes versioned there.
3. Reuse `repo-local-guidance` for other repos where root `AGENTS.md` should stay thin and local-only.
