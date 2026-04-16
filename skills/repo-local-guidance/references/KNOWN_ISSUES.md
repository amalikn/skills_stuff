# KNOWN_ISSUES

- `.agents/` is not auto-loaded by Codex; the root `AGENTS.md` must direct Codex to read it.
- Local-only ignore behavior depends on `.git/info/exclude`, which is per-clone and not shared remotely.
