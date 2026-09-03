# Therapy & Counselling

Personal support companion skill using evidence-based therapeutic frameworks (CBT, MI, SFBT).

## Purpose

Structured emotional support, psychoeducation, and skill-building through structured conversation. Not a substitute for licensed therapy.

## Files

- [SKILL.md](SKILL.md) — Main skill definition with full frameworks, session structure, crisis protocol, and boundaries
- [PROFILE.md](PROFILE.md) — Concise persona and expertise profile
- [SYSTEM_PROMPT.md](SYSTEM_PROMPT.md) — Standalone system prompt for direct injection
- [manifest.json](manifest.json) — Metadata for cross-agent discovery

## Agent install targets

| Platform | Path |
|---|---|
| Hermes | Installed via `skill_manage` |
| Claude Code | Copy SKILL.md to `.claude/skills/` or `~/.claude/skills/` |
| Codex CLI | Copy to `~/.codex/skills/` |
