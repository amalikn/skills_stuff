# skills_stuff Path Migration And Superpowers Install Plan

Date: 2026-04-05 01:04

## Scope
- Move the canonical `skills_stuff` repo from `/Volumes/Data/_ai/_mcp/skills_stuff` to `/Volumes/Data/_ai/_skills/skills_stuff`.
- Rename the intermediate umbrella from `_skill` to `_skills`.
- Update live references that are part of the current runtime and governance surface.
- Promote `superpowers` from `pending_skills/` into the canonical repo root before installing it for Codex native discovery.

## Assumptions
- Historical backups and timestamped audit/outcome artifacts should remain unchanged unless they are active runtime or governance entrypoints.
- The correct promoted location for the third-party repo is `/Volumes/Data/_ai/_skills/skills_stuff/superpowers`.
- Codex native discovery should use `~/.agents/skills/superpowers` as a symlink to the promoted `skills/` directory.

## Planned Direct Edits
- Filesystem move of `skills_stuff` into the new `_skills` umbrella.
- Literal path replacement in active files:
  - `~/.codex/config.toml`
  - `governance/README.md`, `governance/catalog.md`, `governance/sources-inventory.md`, `governance/sync-map.yaml`
  - `/Volumes/Data/_ai/_mcp/mcp_stuff/mcp-skill-builder/README.md`
  - `/Volumes/Data/_ai/_mcp/mcp_stuff/mcp-skill-builder/examples/config.sample.yaml`
  - `/Volumes/Data/_ai/_mcp/mcp_stuff/scripts/mcp_streamable/start_phase1_servers_http.sh`
  - `/Volumes/Data/_ai/_project/project_stuff/governance/scripts/run-governance-import-chain-final-verification.sh`
  - current non-backup path references inside this repo
- Promote `pending_skills/superpowers` to `superpowers/` at repo root.
- Create the Codex discovery symlink at `~/.agents/skills/superpowers`.

## Validation
- Verify new directory locations exist and old ones do not.
- Re-scan the targeted live surfaces for stale `/_mcp/skills_stuff` or `/_skill/skills_stuff` references.
- Confirm the symlink resolves and lists the expected `SKILL.md` files.

## Risks
- Historical documents outside the active surface may still mention the old path by design.
- Codex needs a restart to discover newly installed skills in a new session.
