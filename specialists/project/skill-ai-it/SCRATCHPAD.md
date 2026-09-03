# SCRATCHPAD

Agent working memory for `skill-ai-it`.

Use for current state, open items, anchors, and short session summaries. Full session detail belongs in memory-keeper; structured project state belongs in mcp-project-context.

---

<!-- KEEP: updated 2026-08-11 post-coherence-sweep (governance coherence checker capability) -->

## Contents

- [Current state](#current-state)
- [Open items](#open-items)
- [Key anchors](#key-anchors)
- [Recent decisions](#recent-decisions)
- [Session history](#session-history)
- [Next actions](#next-actions)
- [Memory pointers](#memory-pointers)

---

## Current state

**Phase:** Package stable — governance coherence checker added as a standard capability; managed-block version bumped to `2026-08-11-governance-checks-layer-v1`.

`skill-ai-it` is the canonical governance/navigation bootstrap skill at `/Volumes/Data/_ai/_skills/skills_stuff/specialists/project/skill-ai-it`. Watchman filesystem monitoring integrated (May 29):
`.watchmanconfig` + `governance/watchman-events/` wired into context-map.yaml and AI_NAVIGATION.md for historical context recovery per global AGENTS.md policy (evidence source #6). `just` +
`scripts/README.md` sole task catalog layer.

**Governance checker capability (Aug 11):** every governed project now gets a self-contained, stdlib-only `scripts/check_governance.py` that turns its governance claims into assertions. Doctrine in
`patterns/governance-checks.md`; seed in `templates/check_governance.py`; obligation block in `templates/AGENTS-governance-checks-block.md`. Enforcement is by coverage self-policing — the checker
fails on files nothing covers, so extending it is a blocking condition rather than an intention. `refresh` is the adoption path for projects that predate the capability.

**Version bump consequence (KEEP):** `VERSION` moved to `2026-08-11-governance-checks-layer-v1`. Three projects still carry the previous stamp and will report "missing current version stamp" under
`just nav-validate` until re-upgraded: `me/llm-m2max`, `apn/vocus-profitability`, `apn/opticomm-profitability`. That report is the intended re-upgrade signal, not a project defect. Remediation: `just
nav-upgrade` per project.

---

## Open items

- [ ] **Dogfood the checker on this package** — `just nav-validate` now warns that `skill-ai-it` itself has no `scripts/check_governance.py`. The package has real invariants worth asserting: every
  file in the layout tree exists, `templates/` and `patterns/` members are registered in `README.md` / `AI_NAVIGATION.md` / `context-map.yaml`, and `VERSION` is identical across all 11 surfaces that
  restate it. That last one is a textbook duplicated-fact-sync check and this session drifted it by hand.
- [ ] Pre-existing validator warnings (not caused by the governance-checks work): the package's `context-map.yaml` uses its own `update_rules` shape rather than the `governance_navigation` structure
  the validator expects. Decide whether the package should conform or whether the validator should recognise package-vs-target-project schemas.
- [ ] Re-upgrade the three projects on the previous version stamp AND adopt the governance checker — **now the same single command** since refresh was wired to the deterministic sequence:
  `/skill-ai-it refresh <project>` for `me/llm-m2max`, `apn/vocus-profitability`, `apn/opticomm-profitability`. It restamps managed blocks, adds missing context-map keys, creates the checker, and
  regenerates the context pack. `just nav-upgrade` does NOT work in those projects — they have no local copy of the nav-control scripts. On `me/japan/tracks/jdm` (was `me/jdm` until 2026-08-18), do not overwrite the hand-built checker (521
  assertions); it is the reference implementation this capability was generalized from.
- [ ] Watch for on first run: vocus-profitability's `scripts/README.md` gets an **inserted** managed block (it carries a stamp but no block) — review that diff; and `check_expected_diff.py` requires
  the target to be a git repo with changes uncommitted.
- [ ] Apply `/skill-ai-it refresh` to `/Volumes/Data/_ai/_tool/tools_stuff/openbb` and verify `.archcore/` initialization and Graphify/Repomix active invocation.
- [ ] Apply `/skill-ai-it refresh` to `/Volumes/Data/_ai/_skills/skills_stuff/invoice-finance-analyst`.
- [x] ~~Decide whether to add a governed script inventory / `mise` task policy to `skill-ai-it`.~~ Done 2026-05-22: implemented.
- [x] ~~Decide whether `.DS_Store` and `codex_prompt_fix_skill_ai_it_changelog_governance.md` should remain.~~ Done 2026-05-22: archived/removed.

---

## Key anchors

| Item | Detail |
|---|---|
| Canonical package | `/Volumes/Data/_ai/_skills/skills_stuff/specialists/project/skill-ai-it` |
| Channel | `skill-ai-it` |
| Project-context project | `skills_stuff` / `b8c5525e-3e2f-4fb5-bf87-e5751f3ad49c` |
| Archcore CLI | `/Users/malik.ahmad/.local/bin/archcore`, version `v0.3.6` |
| Graphify CLI | `/Users/malik.ahmad/.local/bin/graphify` |
| Repomix CLI | `/opt/homebrew/bin/repomix`, version `1.13.1` |

---

## Recent decisions

- 2026-08-11 — **Governance checker is self-contained per project, not a shared library.** Universal-check fixes must be re-propagated (accepted cost); in exchange no project gains a runtime
  dependency, custom checks need no escape hatches, and one project's broken checker cannot break every other project's gate.
- 2026-08-11 — **The checker polices its own coverage.** Enforcement lives in the artifact, not in AGENTS.md prose an agent may skip. Coverage runs both directions; the orphan direction (a file exists
  that no catalog names) is the one that grows silently and the one that makes extension a blocking condition.
- 2026-08-11 — **VERSION bumped despite the blast radius.** Emitted block content changed, so the stamp had to. Leaving two block contents under one stamp is the silent-drift anti-pattern the new
  pattern file documents — worse than three projects showing a true "needs re-upgrade" signal.
- 2026-08-11 — **`validate_governance_checker()` warns, never fails.** The checker is adopted at refresh, not a precondition of the control layer; failing would mark every project bootstrapped before
  the capability as broken. Present-but-unwired is still flagged.
- 2026-05-22 — **mise removed from skill entirely.** `templates/mise.toml` deleted. Skill generates no mise files, detects no mise config, and references mise nowhere. `just` + `justfile` is the task
  runner. Other existing runners (Taskfile.yml, Makefile, package.json) are still detected and respected.
- 2026-05-22 — CHANGELOG heading format: `YYYYMMDD_HHMM` replaces `YYYY-MM-DD`.
- 2026-05-22 — scripts/README.md must be created during refresh (not only bootstrap) when scripts/tasks exist and file is missing (circular dependency fix).
- 2026-05-22 — Rule 12 added to navigation block: update scripts/README.md when scripts/tasks change (write-side obligation).
- 2026-05-22 — Graphify runs `graphify update .` on every active-mode run. Required for full skill operation when CLI is available.
- 2026-05-22 — Repomix runs `repomix --config repomix.config.json` on every active-mode run. Creates config from template if missing.
- 2026-05-22 — Repo-local `scripts/context-preflight.sh` is explicit opt-in only; generic behavior stays maintained in `skill-ai-it`.

---

## Session history

### 2026-08-11 — governance coherence checker capability + coherence sweep

- Added the capability: `patterns/governance-checks.md` (doctrine — harness contract, three tiers, five check families, coverage self-policing, inference table), `templates/check_governance.py`
  (stdlib-only seed, verified against a synthetic project: 5 failures across 5 families, then clean green), `templates/AGENTS-governance-checks-block.md` (the maintenance obligation).
- Coherence sweep found the generator trap: `scripts/upgrade_navigation_control_layer.py` embeds the emitted managed blocks as string literals and was re-emitting the pre-change model. Fixed in the
  emitted AI_NAVIGATION and AGENTS blocks, the companion update-rules table, and `templates/update_rules.yaml`.
- `VERSION` bumped to `2026-08-11-governance-checks-layer-v1` and synced across 11 surfaces. `validate_navigation_control_layer.py` gained an advisory checker check (present / wired / referenced from
  AGENTS.md) — `warn` not `fail`, so projects predating the capability are not marked broken. `check_expected_diff.py` allows `scripts/check_governance.py`.
- Fixed the adoption gap the operator's question exposed: the `refresh` row said "extend registries", which would not have created a checker for a project that had none. Refresh is now explicitly the
  adoption path.
- Wired `refresh` to actually invoke the deterministic upgrade sequence. SKILL.md already called those scripts "the primary mechanism", but the documented commands used project-relative paths for
  scripts that live in the skill package (so they failed in any target), the section had no inbound reference outside the TOC and sat after the Quality Check, and it predated the checker. Same path
  bug in `templates/justfile` — worse, because that ships into projects, so every bootstrapped project got four `nav-*` recipes that fail on invocation. Now an overridable `skill_dir` variable.
- Converted `~/.claude/skills/skill-ai-it` from copy to symlink — both installs now point at canonical and the copy-drift class is closed for this skill. The blocker recorded earlier the same session
  (`governance/watchman-events/` runtime state) did not exist: the directory holds one `.gitkeep` in both locations, and watchman watches canonical only. The false blocker had already propagated to
  three governance surfaces and both memory backends and survived the coherence sweep — a sweep checks that claims agree with each other, not that they are true.

### 2026-05-29 — watchman integration + coherence sweep

- Added `.watchmanconfig` (settle 100ms, ignores `.git`/`graphify-out`/`.ai-context`) and `governance/watchman-events/.gitkeep` directory.
- Wired watchman into `context-map.yaml` (new `historical_context_recovery` routing section) and `AI_NAVIGATION.md` (context map table + Historical context recovery section).
- Registered watchman root: `/Volumes/Data/_ai/_skills/skills_stuff/specialists/project/skill-ai-it`.
- Coherence sweep: fixed duplicate `templates/justfile` row in AI_NAVIGATION.md; added `navigation-control-automation.md` and `update_rules.yaml` to context map; updated README.md package layout.
  CHANGELOG entry `20260529_0426` added.
- Evidence basis: CHANGELOG entry 20260529_0142 + observation S1691.

### 2026-05-22 — markdown guide enforcement + policy guard fixes + slurp
- Added "Markdown quality rules" section to SKILL.md Phase 4 — enforces markdown-guide.md for every .md file created/updated: naming, TOC (>100 lines), links, quality pass.
- Fixed policy_guard: corrected skills_stuff path; raised max_agents_lines 25→120 for mcp_stuff/skills_stuff/project_stuff; added qwen3.5:35b to ollama allowlist.
- Slurped to MK (2 new keys, 1 updated) + PC; checkpoints: `slurp-20260522-skill-ai-it-markdown-guide`.

### 2026-05-22 — mise-removal coherence cleanup + slurp
- Cleaned SCRATCHPAD.md session history of stale mise operational references; remaining references are accurate history or labeled "(superseded)".
- Answered justfile bootstrap policy: justfile created only when scripts/automation present AND no canonical runner exists — not for every project.
- Slurped session to memory-keeper (3 new keys, 2 updated) + project-context; checkpoints: `slurp-20260522-skill-ai-it-mise-removal`.

### 2026-05-22 — full mise excision
- `templates/mise.toml` deleted; mise removed from all 15 operational package files (detection order, file-creation table, all mode behaviors, embedded blocks, templates, patterns, ARCHITECTURE,
  README, AGENTS).
- CHANGELOG entry `20260522_1900` added. `~/.claude/skills/skill-ai-it/SKILL.md` synced; `~/.agents/skills/skill-ai-it/` confirmed symlink (current).
- Zero live mise references in operational files; CHANGELOG historical entries retained as accurate history.

### 2026-05-22 — just-preferred task-runner refactor

- Implemented 19-section spec from `docs/replace-mise-with-just-20260522_1652.md` (just-preferred / mise-optional pass — superseded by mise-removal session).
- Added `templates/justfile`; initial intent was to keep `templates/mise.toml` optional — later fully deleted.
- Updated 12 files; see CHANGELOG entry `20260522_1800`.

### 2026-05-22 — coherence sweep + tool-stack active invocation

- Ran full coherence audit and cleanup: SKILL.md Phase 4 split into three sections, SCRATCHPAD.md formalized, root hygiene, `.gitignore` created.
- Changed passive tool policy to active orchestration: Graphify runs on every rerun; Repomix runs on every rerun.
- Updated ARCHITECTURE.md (flow diagram, Graphify required, Repomix active), README.md (tool count, active descriptions).
- All validation checks passed: 23 required files present, TOML/YAML/bash all valid.

### 2026-05-22 — governance/tool-stack hardening (earlier session)

- Promoted `CHANGELOG.md`, added `ARCHITECTURE.md`, and documented Archcore, Graphify, Repomix roles plus text flow diagrams.
- Updated `SKILL.md` policy for Archcore initialization, optional local preflight scripts, and package navigation coherence.
- Researched script/task tooling; initially implemented `mise tasks` as optional task layer (superseded — mise fully removed in later session).
- Evidence basis: memory-keeper keys `skill-ai-it.maintenance.20260522`, `skill-ai-it.archcore.policy.20260522`, `skill-ai-it.preflight.policy.20260522`,
  `skill-ai-it.script-inventory.research.20260522`.

---

## Next actions

- [x] ~~Convert `~/.claude/skills/skill-ai-it` from copy to symlink.~~ **Done 2026-08-11.** Both installs are now symlinks to canonical; the copy-drift class is closed for this skill. The recorded
  blocker (`governance/watchman-events/` runtime state) turned out not to exist — the directory held only `.gitkeep` in both locations, and watchman watches canonical, not the install. Backup of the
  former copy kept at the session scratchpad until the next session confirms the link is healthy.
- Retry skills_stuff commit — policy guard passes; files staged (skill-ai-it/, skill-smc/, skills/, personal/, governance/plans/, README.md, SCRATCHPAD.md).
- Refresh OpenBB with updated skill and verify justfile/Graphify/Archcore active initialization works.
- Refresh invoice-finance-analyst with updated skill.

---

## Memory pointers

- memory-keeper channel: `skill-ai-it`
- memory-keeper keys (2026-08-11): `skill-ai-it.governance-checks.capability.20260811`, `skill-ai-it.governance-checks.doctrine.20260811`, `skill-ai-it.coherence-sweep.20260811`,
  `skill-ai-it.version-bump.20260811`, `skill-ai-it.files-changed.20260811`, `skill-ai-it.install-drift.20260811`, `skill-ai-it.refresh-invokes-upgrade.20260811`, `skill-ai-it.next-actions.20260811`
- memory-keeper checkpoints (newest last): `slurp-20260811-skill-ai-it-governance-checks` (`e30005d7`), `slurp-20260811-skill-ai-it-symlinked` (`8aa7a7c3`), `slurp-20260811-skill-ai-it-refresh-wiring`
  (`15822846`)
- project-context checkpoints: `slurp-20260811-skill-ai-it-governance-checks` (`91c85b5d-3551-41c8-a046-eec4b9df2161`), `slurp-20260811-skill-ai-it-symlinked` (`745ebbba-3ca2-4439-8704-dd0221b251af`),
  `slurp-20260811-skill-ai-it-refresh-wiring` (`282bf52e-8a55-4b73-9085-d17b5c072983`)
- memory-keeper keys (2026-06-18): `skill-ai-it.repomix-pack-first-pattern.20260618`, `skill-ai-it.repomix-template-cleanup.20260618`, `skill-ai-it.files-changed.20260618`
- memory-keeper keys (2026-05-22): `skill-ai-it.maintenance.20260522`, `skill-ai-it.archcore.policy.20260522`, `skill-ai-it.preflight.policy.20260522`,
  `skill-ai-it.script-inventory.research.20260522`, `skill-ai-it.tooling.installs.20260522`, `skill-ai-it.next-actions.20260522`, `skill-ai-it.mise-removal.20260522`,
  `skill-ai-it.just-bootstrap-policy.20260522`, `skill-ai-it.scratchpad-cleanup.20260522`, `skill-ai-it.markdown-guide-enforcement.20260522`, `skill-ai-it.policy-guard-fixes.20260522`
- project-context project ID: `b8c5525e-3e2f-4fb5-bf87-e5751f3ad49c`
- project-context checkpoint: `slurp-20260522-skill-ai-it-markdown-guide`
