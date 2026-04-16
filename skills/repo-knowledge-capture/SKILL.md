---
name: repo-knowledge-capture
description: Use this skill when the user explicitly wants to preserve or locally version repo-specific knowledge artifacts outside a GitHub or Bitbucket repo without pushing or tracking them.
metadata:
  short-description: Capture local repo knowledge
---

# Repo Knowledge Capture

## Use When
Use this skill when the user explicitly wants to preserve or locally version repo-specific knowledge artifacts outside a GitHub or Bitbucket repo without pushing or tracking them.

Trigger this skill for:
- capturing `.serena/`, `.smart-coding-cache/`, repo `AGENTS.md`, `.agents/`, or local `.vscode/`
- local-only repo knowledge snapshots
- local history for repo guidance, editor overrides, and Codex memory artifacts
- restoring local repo knowledge artifacts into a working clone
- verifying or extending the local-only exclude set for those artifacts
- automating capture before `git push`

## Workflow
1. Run the helper with an explicit repo path.
2. Use `setup` to add or confirm local-only excludes in `.git/info/exclude`.
3. Treat the default exclude set as:
   - `.serena/`
   - `.smart-coding-cache/`
   - `AGENTS.md`
   - `.agents/`
   - `.vscode/`
4. Use `snapshot` to copy those artifacts into the external knowledge root.
5. Use `history-init` and `history-commit` to maintain local-only history outside the target repo.
6. Use `restore` to restore a chosen snapshot back into the target repo working tree.
7. When push-time enforcement is desired, install a clone-local `.git/hooks/pre-push` hook that runs the workflow and exits non-zero on failure.

## Rules
- Never store captured knowledge inside tracked files of the target repo unless the user explicitly asks for that.
- Never use tracked `.gitignore` for this workflow unless the user explicitly asks for repo-wide ignore behavior.
- `setup` should be treated as idempotent: preserve existing local-only excludes and add only missing entries.
- Never run `git push` from the `history/` repository.
- The helper script requires an explicit target repo path.

## Stable Facts
- The canonical storage root is `~/_ansible/local-knowledge/<repo-name>/` unless `REPO_KNOWLEDGE_ROOT` overrides it.
- The workflow uses `.git/info/exclude` instead of tracked `.gitignore` changes for local-only visibility.
- The default local-only exclude set is `.serena/`, `.smart-coding-cache/`, `AGENTS.md`, `.agents/`, and `.vscode/`.
- Clone-local `pre-push` hook automation is a supported enforcement model.
- The helper script requires an explicit target repo path.

## References
- references/PROFILE.md
- references/RUNBOOK.md
- references/KNOWN_ISSUES.md
- references/CHANGELOG.md
- references/CHECKLISTS/healthcheck.md
- references/CHECKLISTS/change.md
- references/CHECKLISTS/rollback.md
- references/CONTEXT/assumptions.md
- references/CONTEXT/dependencies.md
- references/CONTEXT/boundaries.md

## Source
- specialist_type: project
- slug: skill-repo-knowledge-capture
- version: 0.1.0
