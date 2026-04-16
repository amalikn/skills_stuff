# PROFILE

## Subject
- Type: project
- Name: repo_knowledge_capture
- Slug: skill-repo-knowledge-capture

## Stable Facts
- Purpose: capture and version local repo knowledge artifacts outside the target repository.
- Primary artifacts: `.serena/`, `.smart-coding-cache/`.
- Safety model: local-only, no `git push`, no tracked-file edits in the target repo.
- Storage root: `~/_ansible/local-knowledge/<repo-name>/`.
- Snapshot layout: `snapshots/<YYYYMMDD_hhmm>/`.
- Versioning layout: `history/` as a separate standalone git repository.
