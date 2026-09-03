# SCRATCHPAD

Agent working memory for skills_stuff.
Use for: draft plans, terminal output, intermediate analysis, refactor outlines.
Cleared between sessions unless content is explicitly marked KEEP.

---

<!-- KEEP: populated 2026-04-22 from mcp-project-context (no memory-keeper entries found for channel) -->

## Current state

**Phase:** Active maintenance — skill authoring and governance updates. <!-- KEEP -->

skills_stuff is the canonical authoring source for Claude Code and Codex skills. Recent work has focused on governance bootstrap automation (skill-ai-it), skill-commtracker MIME/attachment capture, Python helper scripts for commtracker, skill-slurp-chat persistence improvements, and Claude auto-memory governance (2026-05-22).

Auto-memory is now consolidated: all Claude auto-memory writes go to `/Volumes/Data/_ai/claude-auto-memory/` (governed, single path, 36 files + MEMORY.md). Per-project fragmentation eliminated.

---

## Open items

- [ ] Broader `~/.codex/skills` vs `~/.agents/skills` authority decision (from strategy-os governance session)
- [ ] sync-script rollback hardening (from strategy-os governance session)

---

## Key anchors

| Item | Detail |
|---|---|
| Authoring root | `/Volumes/Data/_ai/_skills/skills_stuff/` |
| Installed skills (Claude) | `~/.claude/skills/` |
| Installed skills (Codex) | `~/.codex/skills/` or `~/.agents/skills/` |
| Specialists dir | `specialists/` — canonical authoring for specialist skills |
| Exports dir | `exports/` — client adapter layer |
| skills.md | Skill index/registry |
| Swarms install | `skills_stuff/swarms/swarms-github/` (7 skills; avoid parallel-task-tmux — Snyk Critical Risk) |

---

## Recent decisions

- 2026-05-22 — auto-memory coherence: merged 3 governance-scan files into 1 (`feedback_governance_scan.md`); normalized frontmatter on 7 files (flat `type:` not `metadata:` nesting); renamed `claude_md_thin_wrapper.md` → `feedback_claude_md_thin_wrapper.md`; MEMORY.md rebuilt alphabetically (36 entries, 0 broken links, 0 duplicate name fields).
- 2026-05-22 — auto-memory relocation: `autoMemoryDirectory` → `/Volumes/Data/_ai/claude-auto-memory/`; `cleanupPeriodDays: 36500` (0 schema-rejected); CLAUDE.md governance rule added (capture-cache-only); 37 files migrated from per-project dirs, old files deleted.
- 2026-04-28 — graphify MCP: use uv-tool isolated Python 3.10 env (not a new venv) since graphifyy[mcp] already installed; Python 3.14 excluded by graphify's `<3.14` constraint.
- 2026-04-22 — commtracker scripts: slug uses email's own TZ (not forced AEST); reconcile tries AEST fallback for historical tracker compatibility. Scripts live at `~/.agents/scripts/commtracker/`.
- 2026-04-22 — skill-commtracker: Step 4.5 added for MIME attachment/inline image extraction; signature detection (Outlook-*.png, UUID-named, ≤200b) skips chrome by default.
- 2026-04-22 — skill-slurp-chat Step 6.5 added: slurp now updates SCRATCHPAD.md after checkpointing both backends. Tiered ownership enforced.
- 2026-04-22 — skill-ai-it created: content-aware governance bootstrap. Queries memory systems before writing SCRATCHPAD (not blank). Conditional files: ARCHITECTURE, CONVENTIONS, ROADMAP based on project signals.
- 2026-04-22 — SCRATCHPAD generation in skill-ai-it queries all 3 memory sources; session summaries 2-3 bullets only in SCRATCHPAD; full detail stays in memory-keeper.

---

## Session history (summaries — full detail in memory-keeper)

### 2026-05-22 — Auto-memory governance and coherence <!-- KEEP -->
- Relocated Claude auto-memory to `/Volumes/Data/_ai/claude-auto-memory/`; `autoMemoryDirectory` + `cleanupPeriodDays: 36500` in settings.json; CLAUDE.md governance rule added; 37 files migrated from 15 per-project dirs, old files deleted
- Audited all 38 memory files: found 3-way name collision on governance-scan rule, scope mismatch in skill-smc entry, hardcoded project reference in general rule, inconsistent frontmatter, broken naming convention
- Fixed all issues: merged 3→1, normalized 7 frontmatter blocks, renamed `claude_md_thin_wrapper.md`, rebuilt MEMORY.md (36 entries, alphabetical, verified 0 broken links, 0 duplicate names)

### 2026-04-28 — graphify MCP install <!-- KEEP -->
- Added graphify MCP server to `~/.claude/settings.json` using uv-tool Python at `/Users/malik.ahmad/.local/share/uv/tools/graphifyy/bin/python`
- graphify requires Python >=3.10,<3.14; graphifyy[mcp] already installed via uv tool (no new venv needed)
- MCP serves `graphify-out/graph.json` relative to CWD; run `/graphify .` in a project first to generate graph

### 2026-04-22 — skill-commtracker attachment capture + Python scripts
- Added MIME attachment/inline image extraction to skill-commtracker (Steps 3/4/4.5/6 + quality checklist); both SKILL.md files updated
- Built `extract.py`, `reconcile.py`, `toc.py` under `~/.agents/scripts/commtracker/` (stdlib-only, Python 3.14)
- Validated on aurukun-fni (7 real images extracted, 36 signatures skipped) and of-si (40 signatures all skipped correctly)

### 2026-04-22 — skill-slurp-chat SCRATCHPAD step
- Added Step 6.5 to skill-slurp-chat: update SCRATCHPAD.md after checkpoints, before closeout
- Updated both installed (`~/.claude/skills/skill-slurp-chat/SKILL.md`) and authoring source
- Evidence basis: mcp-project-context `skills_stuff.skill-slurp-chat.scratchpad-step-20260422`

### 2026-04-22 — skill-ai-it creation and installation
- Created skill-ai-it: 5-phase content-aware governance bootstrap (Inventory→Understand→Infer→Generate→Update Parent)
- Always creates: README, AGENTS, CLAUDE, SCRATCHPAD (populated from memory); conditionally: ARCHITECTURE, CONVENTIONS, ROADMAP
- Tested on aurukun-fni (full bootstrap) and of-si (update pass)
- Evidence basis: mcp-project-context note `skill-ai-it created and installed`

### 2026-04-20 — swarms skill pack
- Installed am-will/swarms: 7 skills including co-design, parallel-task, swarm-planner, super-swarm
- Avoid parallel-task-tmux (Snyk Critical Risk)
- Evidence basis: mcp-project-context note

---

## Next actions

- Respond to any follow-up requests on skill-commtracker, helper scripts, or skill-slurp-chat behavior
- Resolve `~/.codex/skills` vs `~/.agents/skills` authority question when prioritized
- Monitor auto-memory: verify new session writes land in `/Volumes/Data/_ai/claude-auto-memory/` (not per-project dirs)

---

## Memory pointers (navigation only — content is above)

- memory-keeper channel: `skills-stuff` / keys: `skills_stuff.graphify.mcp-install-20260428`, `skills_stuff.skill-commtracker.attachment-capture-20260422`, `skills_stuff.commtracker-scripts-20260422`, `skills_stuff.skill-slurp-chat.scratchpad-step-20260422`
- project-context project ID: `b8c5525e-3e2f-4fb5-bf87-e5751f3ad49c`
- MK checkpoint: `slurp-20260428-graphify-mcp` (ID: 85a20c64)
- PC checkpoint: `slurp-20260428-graphify-mcp` (ID: 1a531e71)
