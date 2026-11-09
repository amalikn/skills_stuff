# Change Checklist

- Keep only always-on rules and pointers in root `AGENTS.md`.
- Move longer repo-specific guidance into `.agents/`, one topic per file.
- Operator GitHub remote: commit `AGENTS.md`, `CLAUDE.md` and `.agents/`; remove any exclusion of them.
- Company remote: real files in the GitHub companion repo, symlinks in the clone, symlinks in `.git/info/exclude`.
- Ask before adding any other exclusion.
