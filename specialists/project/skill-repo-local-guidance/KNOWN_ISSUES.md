# KNOWN_ISSUES

- `.agents/` is not auto-loaded by Codex; the root `AGENTS.md` must direct Codex to read it.
- `.git/info/exclude` is per-clone: a fresh clone of a company repo needs its exclusions (and the symlinks) set up again.
- Versions up to 0.1.0 told agents to exclude `AGENTS.md` and `.agents/` in every repo; that hid every nested `AGENTS.md` in eight repos until 2026-11-09.
