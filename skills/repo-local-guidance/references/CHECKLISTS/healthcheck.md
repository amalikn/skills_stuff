# Healthcheck Checklist

- Root `AGENTS.md` is present and thin.
- `.agents/` contains the longer support docs and the root file links them.
- Operator GitHub remote: `git ls-files AGENTS.md .agents` lists them; neither appears in `.git/info/exclude` or `.gitignore`.
- Company remote: `AGENTS.md` and `CLAUDE.md` are symlinks into the GitHub companion repo, the companion has them committed, and the clone shows them as ignored.
