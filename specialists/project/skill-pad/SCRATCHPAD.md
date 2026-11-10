---
Title: Scratchpad
Category: working-state
Status: current
Authority: working-state
Scope: Working state of skill-pad between sessions
Last reviewed: 2026-11-10
Summary: Current working state, newest first per section; older entries rotate to docs/history, older open items to docs/trackers.
Kind: state
Budget: 200 lines, 25 KB
Archive: docs/history/ (`just history <term>`)
Keep: Next actions=1, Memory pointers=1, Session history=2, Current state=3, Recent decisions=3
Open items tracker: docs/trackers/open-items-20261110_1644.md
---

# SCRATCHPAD

Agent working memory for skill-pad: current state, open items, decisions pending promotion, next actions. Older entries rotate to docs/history (`just history <term>`); durable facts are promoted out,
not kept here.

---

<!-- populated 2026-11-10 from memory-keeper (cross-project entries only), mcp-project-context (no project), claude-mem (search unavailable) -->

## Current state

**Phase:** own skill in place (2026-11-10).

skill-pad is now the operator's own Pad skill: SKILL.md routes to seven rewritten references; the plugin's status, capture, onboard, connect and disconnect are modes; the live feed runs
`scripts/pad_monitor.sh` under Monitor. Pad's generated skill files are gone from the pack; the upstream mirror holds v0.19.2 sources. Pad workspaces exist in unified-network-controller and
smc-resiliency.

---

## Open items

- [ ] Live test of `connect` in a linked project (unc or smc-resiliency): Monitor receives a `pad push` from the operator; `disconnect` stops it. Include the delivery-limit case: push after more than 30 minutes idle (modes.md, Delivery limits).
- [ ] Operator answers Q1-Q6 of the rewritten usage proposal (`docs/pad-usage-guidelines-proposal-20261110_1628.md`); then rollout step 1 (restore test).
- [ ] Projects that ran `pad workspace init` after today: delete their `.claude/skills/pad/` and `.agents/skills/pad/` copies.
- [ ] Old scripts_stuff symlinks (`bash/pad_backup.sh`, `python/pad_export/pad_export.py`): retire once every project points here.

---

## Key anchors

| Item          | Detail                                                                  |
| ------------- | ----------------------------------------------------------------------- |
| Pad CLI       | v0.19.2 (22e50fe), Homebrew `perpetualsoftware/tap/pad`                 |
| Pad data      | `~/.pad` -> `/Volumes/Data/_ai/_tool/tools_stuff/pad` (moved 2026-11-10; old copy `/Volumes/malik1tb/malik-storage/pad.moved-20261110_1706`)                       |
| Install links | `~/.claude/skills/skill-pad`, `~/.agents/skills/skill-pad` -> pack root |
| Backup job    | launchd `au.malik.pad-backup`, 02:30                                    |
| Presence hooks | `~/.claude/settings.json` UserPromptSubmit and Stop, added 2026-11-10 |

---

## Recent decisions

- 2026-11-10 — Usage proposal rewritten after review; archcore ADRs written; `.ai-context/` gitignored (operator).
- 2026-11-10 — Own skill, no plugin; Pad text extracted and rewritten into references, the Pad-generated copies removed (operator).
- 2026-11-10 — Rebuild all plugin parts: status/capture/onboard, connect/disconnect live feed, busy/idle presence hooks (operator).
- 2026-11-10 — One SKILL.md for Claude Code and Codex (operator).

---

## Session history (summaries — full detail in memory-keeper)

### 2026-11-10 — skill-ai-it bootstrap and own skill

- Researched Pad's site (sitemap) and repo at v0.19.2; mirrored missing pages and plugin files; regenerated CLI help outside any workspace.
- Wrote SKILL.md and seven references; monitor and refresh scripts with tests; governance scaffold.
- Evidence basis: this session's CHANGELOG entry 20261110_1644.

---

## Next actions

- Run the live `connect` test in smc-resiliency or unc, then close that open item.

---

## Memory pointers (navigation only — content is above)

- memory-keeper: no skill-pad keys yet; related `unc.skill-pad-and-deploy.20261110`, `smc-resiliency.urlcapture-prune-20261110` (Pad TASK-30)
- project-context project ID: none
- claude-mem: search unavailable this session (Chroma connection closed)
