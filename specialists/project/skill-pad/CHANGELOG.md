---
Title: Changelog
Category: change-log
Status: current
Authority: record
Scope: Dated changes to skill-pad
Last reviewed: 2026-11-10
Summary: Newest entries only; older ones rotate to docs/history (just history <term>).
Kind: log
Budget: 200 lines, 25 KB
Archive: docs/history/ (`just history`, `just history-show`)
---

# Changelog — skill-pad

## 20261110_1724 — pad_conventions --only; writing-standard live in both workspaces

### Added

- `scripts/pad_conventions.py --only ID[,ID]` (`select_entries`, test added; unknown id exits 2): plans or applies only the named entries.
- Applied `--only writing-standard` to smc-resiliency (CONVE-32) and unified-network-controller (CONVE-25); read back `same`; their own wording of
  the other conventions left untouched.

## 20261110_1719 — writing standard for plans, tasks, updates and tags

### Added

- `writing-standard` convention (always, should) in `conventions/apn-baseline.toml`, now six conventions; README table and tests updated (operator: yes).
- Proposal section 3.3 (Writing standard): plan and task body templates, four update channels, comment types, tags; 3.8 lists the new convention;
  section 3 renumbered without letter suffixes (operator).

## 20261110_1708 — Pad data moved to tools_stuff/pad; container image facts

### Changed

- Pad data moved from `/Volumes/malik1tb/malik-storage/pad` to `/Volumes/Data/_ai/_tool/tools_stuff/pad` (operator; tracked in tools_stuff by the
  operator's choice). Server stopped, copied and compared, `~/.pad` relinked, restarted; the server holds the new pad.db, item counts unchanged (30 and
  24). Old copy kept as `pad.moved-20261110_1706` on malik1tb. SETUP, ARCHITECTURE, SCRATCHPAD, cli-reference, integrations, the proposal and
  `pad_backup.sh` updated.
- integrations.md: container image `ghcr.io/perpetualsoftware/pad` (pin a version tag, first-run setup URL, PUID/PGID). cli-reference.md: the README
  CLI Reference is a summary of the same tree. Mirror: `references/upstream/github.com/pkgs_container_pad.md`, treated as verbatim by the checker.

## 20261110_1701 — usage proposal moved to docs/ with three diagrams

### Changed

- `docs/pad-usage-guidelines-proposal-20261110_1628.md` (was under references/; operator: "move this under docs folder"): links repointed to
  `../references/`; ASCII diagrams added for Pad over the trackers, the ask lifecycle, and session start when Pad is down. Pointers in SKILL.md,
  README, AGENTS and SCRATCHPAD updated.

## 20261110_1659 — usage proposal reviewed and rewritten; archcore, lint and repomix

### Added

- `.archcore/` (archcore init) with three ADRs (own skill, no plugin; rewrite not vendor; live feed via Monitor) and `index.guide.md`, pointing at ARCHITECTURE.md Key decisions.
- `.markdownlint-cli2.jsonc` (mirror excluded), `repomix.config.json`, `.gitignore` for `.ai-context/` (operator: gitignore).
- cli-reference.md Traps: a `--fields` status select has no closed states, so custom words such as `answered` never close.

### Changed

- `references/pad-usage-guidelines-proposal-20261110_1628.md` moved back from the pack root and rewritten (operator: "rewrite it"): closable Asks schema via
  `--schema` and `--tracks-work false`, site names removed, one joint trial review through UNC TASK-20, no tracker-ID tags, dates in fields, status apart
  from the claim, degraded mode and restore test, tracker drift as a script. Still a draft; routed from SKILL.md as not in force.

## 20261110_1644 — own skill replaces Pad's skill text; plugin parts rebuilt; governance scaffold

### Added

- `SKILL.md` (name skill-pad): the operator's own Pad skill, replacing the Pad-generated `.claude/skills/pad/` and `.agents/skills/pad/` copies (operator: "develop our own skill and not rely on the
  plugin"; "extract information from both ... then remove these files"). Install links `~/.claude/skills/skill-pad` and `~/.agents/skills/skill-pad` now point at the pack root.
- References rewritten from Pad v0.19.2 sources (not pasted): `workspace-context.md`, `items-and-edits.md`, `playbooks-and-workflows.md`, `modes.md` (status, capture, onboard, connect, disconnect,
  presence), `cli-reference.md` (24 groups, 184 commands, traps), `integrations.md`, `upgrade.md`.
- `scripts/pad_monitor.sh` (live feed under the Monitor tool, adapted from Pad's Apache-2.0 plugin monitor) with `tests/test_pad_monitor.py` (4 tests, shown to fail when the lock gate breaks);
  `scripts/pad_upstream_refresh.sh` (mirror a release; reproduces v0.19.2 byte for byte, 21 s).
- Upstream mirror extended: plugin manifests, hooks, monitor, `internal/cli/agents.go`, the disconnect skill, ChatGPT integration, `agent-guide-all.md`, 20 more site pages (MCP local/remote, client
  setup, self-hosting, security, blog). CLI dumps regenerated outside any workspace.
- Governance: AGENTS.md, CLAUDE.md, ARCHITECTURE.md, SETUP.md, SCRATCHPAD.md, this file, `.mise.toml`, justfile, `scripts/README.md`, `scripts/check_governance.py` (govcheck package with pack-rule checks), `code-map.toml`; presence hooks in `~/.claude/settings.json`.

### Changed

- README: layout and refresh sections now describe the own skill and the mirror refresh.

### Notes

- Generated by `skill-ai-it` in `bootstrap` mode; a parallel smc-resiliency session added the first mirror pass and the usage-guidelines proposal (left as is).
