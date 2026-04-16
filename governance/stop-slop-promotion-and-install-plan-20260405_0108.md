# stop-slop Promotion And Install Plan

Date: 2026-04-05 01:08

## Scope
- Promote `stop-slop` out of `pending_skills/` into the canonical `skills_stuff` root.
- Install it for Codex native discovery via `~/.agents/skills/stop-slop`.

## Assumptions
- `stop-slop` is a single-skill package because it exposes one top-level `SKILL.md` rather than a nested `skills/` tree.
- The canonical promoted location should be `/Volumes/Data/_ai/_skills/skills_stuff/stop-slop`.

## Planned Changes
- Move `/Volumes/Data/_ai/_skills/skills_stuff/pending_skills/stop-slop` to `/Volumes/Data/_ai/_skills/skills_stuff/stop-slop`.
- Create the native-discovery symlink:
  - `~/.agents/skills/stop-slop -> /Volumes/Data/_ai/_skills/skills_stuff/stop-slop`

## Validation
- Verify the promoted directory exists.
- Verify the symlink exists and resolves.
- Verify `SKILL.md` is readable through the symlink.
