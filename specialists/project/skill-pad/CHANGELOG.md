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

## 20261110_2031 — slurp close: session record, write-backs, collection schemas

### Added

- `docs/session-record-20261110_2029.md`: all 56 operator messages with destinations, side effects outside the repos, open work by owner.
- `conventions/collection-schemas/` (asks, bugs, feature-requests, tech-debt) with a readme; cli-reference Traps: web collection templates.
- Write-backs: skill-coder `references/tooling-and-runtime.md` (dataclass loaded by path, flushed progress lines); skill-ai-it
  `references/pitfalls.md` (generation-policy table rows; markdown hook re-wraps whole files).

### Notes

- Flows: smc-resiliency and UNC rendered and traced; nothing of this session's changes is described there; UNC's 157 unstamped steps are its own.

## 20261110_2020 — UNC moved: bugs, feature requests and tech debt in Pad in both workspaces

### Changed

- UNC: Bugs (73, nested as children), Feature Requests (84, 49 children) imported, round trip identical; TASK-21 and TASK-22 moved to Tech Debt
  (TD-21, TD-22) and TD-183 points at the refactor tracker (a generated inventory read by check_script_structure, so it stays a file); commit gate
  runs `just pad-trackers`; AGENTS.md rule and task text point at Pad; 34 bug IDs set; tasks linked to their bugs (implements).
- Both workspaces: trackers-truth conventions (CONVE-9, CONVE-24) and the baseline gain the Pad exception; pad-owned-trackers applied to UNC.
- Guidelines: principle 1 exception; 3.1 lists Bugs, Feature Requests, Tech Debt.

## 20261110_2014 — bugs, feature requests and tech debt in Pad (smc-resiliency done)

### Added

- `scripts/pad_tracker.py` (import and export of a Markdown tracker as a file generated from a Pad collection; hand-edited blocks refused; 4 tests).
- Convention `pad-owned-trackers` (always, must; exception to trackers-truth) in the baseline, now seven; applied to smc-resiliency.
- smc-resiliency: collections Bugs (BUG), Feature Requests (FR), Tech Debt (TD) from Pad's web templates plus section, order and declared closed
  states (the Feature Requests and Tech Debt templates declare none); 16 bugs and 1 feature imported, round trip identical; commit gate runs
  `just pad-trackers`; tasks link to their bugs (implements). UNC next.

## 20261110_2004 — closed items on the standard; output order fix

### Changed

- The four closed items (smc TASK-29; UNC TASK-15, TASK-19, IDEA-23) rewritten to guidelines 3.3; their 8 comment originals saved as notes first,
  then reformatted. Sweep: 36 plans, tasks and ideas and 20 comments in both workspaces on the standard.
- `pad_rewrite.py` flushes each progress line, so an error is no longer printed ahead of it (the earlier "silent stop" was an `update_conflict`
  hidden by that order). cli-reference Traps: notes and comments move an item's seq.

## 20261110_1958 — original comment texts kept; rate-limit retries

### Changed

- The 12 smc-resiliency comments' original texts saved verbatim as notes on their items (side agent: Pad may not keep an edited comment's
  earlier text). Guidelines 3.3: keep the original as a note before reformatting a comment. `pad_rewrite.py` retries `rate_limited` answers up to
  5 times (the likely cause of the earlier silent stop). cli-reference Traps: rate limit, comment history.

## 20261110_1956 — smc-resiliency comments rewritten to the comment standard

### Changed

- The 12 smc-resiliency comments rewritten to guidelines 3.3 (operator: comment formatting not updated): stamp and type first (times from each
  comment's creation, AEDT), at most five lines, verified and not verified said, `Next:` last; every fact kept. `pad_rewrite.py` comment entries
  take `body` to replace the text (skipped when equal); test added.

## 20261110_1955 — open Pad items rewritten to the writing standard; pad_rewrite.py; item links

### Added

- `scripts/pad_rewrite.py` (spec-driven, plan by default, seq-guarded bodies, idempotent notes and decisions; 3 tests, `just rewrite`, code-map).
- Guidelines 3.10: Pad link types mapped to Jira's (blocks, implements, supersedes, split-from, parent; fallbacks for relates, duplicates, clones).

### Changed

- All 32 open plans and tasks rewritten to guidelines 3.3 (smc-resiliency 20, UNC 12): bodies, titles, dates from the timelines, tags; smc's 12
  comments gained type words, with 8 notes and 2 decisions extracted. Old text compared token by token; two facts dropped from TASK-30 restored as a
  note (side agent). Open: the first smc apply stopped once without an error message; a rerun completed it; cause not found.

## 20261110_1940 — guard for the live Pad database in tools_stuff

### Changed

- SETUP.md: Git tracks the live pad.db in tools_stuff (operator); no stash, checkout, restore, clean or branch switch there while Pad runs, and
  `pad/` is committed only with the server stopped. Rule kept in tools_stuff `.agents/pad-data.md` (operator chose a rule over untracking).

## 20261110_1936 — Pad usage guidelines in force (Q1 to Q6 answered)

### Changed

- Operator answered Q1 to Q6: Asks collection, current focus only, no roles, answers on the ask or in chat (both), roll out to smc-resiliency and
  UNC together, keep the OneDrive backup. Proposal renamed `docs/pad-usage-guidelines-20261110_1628.md` (Status current); rollout reworked for both
  workspaces (smc-resiliency canary first within each step); SKILL.md, AGENTS, README and SCRATCHPAD now treat it as in force.

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
