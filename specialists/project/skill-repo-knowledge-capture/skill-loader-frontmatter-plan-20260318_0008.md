# Skill Loader Frontmatter Repair Plan

## Scope
Repair skipped Codex skill loading for the managed runtime skills `repo-knowledge-capture`, `repo-local-guidance`, and `repo-bootstrap-and-governance`.

## Planned changes
- Add required YAML frontmatter to the installed `SKILL.md` files under `~/.codex/skills`.
- Repair canonical `skill-repo-knowledge-capture/manifest.json` so `mcp_skill_builder.render_client_adapter` passes schema validation again.
- Validate by checking the top of each runtime `SKILL.md` and rerunning the previously failing dry-run render step.

## Risks
- Runtime-only fixes could drift from canonical generation behavior.
- Validation proves loader prerequisites and renderability, but not a full Codex reload cycle.
