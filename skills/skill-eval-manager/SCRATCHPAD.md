# SCRATCHPAD

Agent working memory for skill-eval-manager.
Use for: draft plans, terminal output, intermediate analysis, refactor outlines.
Cleared between sessions unless content is explicitly marked KEEP.

---

<!-- KEEP: populated 20260923_1222 by skill-ai-it bootstrap; persisted to both backends by /slurp-chat at 20260923_1305. -->
<!-- KEEP: mcp-project-context: no project registered for skill-eval-manager; nearest is skills_stuff. claude-mem: not yet seeded. -->
<!-- KEEP: current state below is inferred from package contents, CHANGELOG.md, BRIEF.md and the design record. -->

## Current state

**Phase:** the version at the top of [CHANGELOG.md](CHANGELOG.md) has shipped and been independently verified; not yet installed to client runtimes, and no real project has written a suite against it.

`skill-eval-manager` is a method-and-recordkeeping skill package for evaluation suites over operational systems. It was built on 2026-09-23 between 11:48 and 12:05 from an authoring prompt, then
independently verified at 12:11 by a separate session, which found and fixed two defects (markdown column-rule violations; a renderer that collapsed *expired* and *invalidated* into one reason
string). Governance scaffolding — `AGENTS.md`, `AI_NAVIGATION.md`, `context-map.yaml`, `justfile`, pinned runtimes and an executable governance gate — was added on 2026-09-23 at 12:22. Durable truth
was promoted into `.archcore/` at 13:11; [.archcore/index.guide.md](.archcore/index.guide.md) is now the entry point for decisions, rules and specs, and the transient candidates file is gone.

---

## Open items

- [ ] Operator decision 1: install to `~/.claude`, `~/.codex` and `~/.hermes` by symlink now, or run unlinked against one real project first. Design record recommends installing now.
- [ ] Operator decision 2: which project writes the first real suite. Design record recommends the network controller, whose framework already exists.
- [ ] Operator decision 3: where a consuming project's `history.jsonl` lives. Design record recommends in-repo and committed, because the diff is the audit trail.
- [ ] Operator decision 4: whether a `blocked` verdict satisfies a gate. Design record recommends never, so an unrunnable check does not read as a passing one.
- [ ] Operator decision 5: wire `scripts/validate_suite.py` into a skills-level check so the shipped examples cannot rot. **Partly actioned 20260923_1222** — `just validate-all` now does this
      locally; a
      skills_stuff-wide check is still unwired.
- [ ] Operator decision 6: v0.2 basis hashing — wait for the first project that asks "did this change since we measured it?", then record the question in `BRIEF.md`.
- [ ] Package is untracked in git. Decide whether it is committed to `skills_stuff` before or after the first real suite.

---

## Key anchors

| Item | Detail |
|---|---|
| Canonical package root | `/Volumes/Data/_ai/_skills/skills_stuff/skills/skill-eval-manager` |
| Design record | `/Volumes/Data/_ai/_skills/skills_stuff/docs/skill-eval-manager-design-record-20260923_1211.md` |
| Authoring prompt | `/Volumes/Data/_ai/_skills/skills_stuff/docs/skill-eval-manager-authoring-prompt-20260923_0846.md` |
| Venv (rebuildable) | `/Volumes/Data/_ai/_skills/skills-working-cache/skills/skill-eval-manager/.venv` |
| Pinned runtimes | Python 3.14.5, Node 26.2.0 — see `.mise.toml`; host Python is 3.14.7, which is why recipes address the venv by path |
| Completion gate | `just runtimes && just validate-all && just check` |

---

## Recent decisions

- 2026-09-23 — Package-specific drift handling, update rules and answer-contract additions live as `###` subsections of *Package-specific routing*, below the managed END marker, so they extend the
  generic sections rather than colliding with them and survive future upgrades.
- 2026-09-23 — Verdict reasons split: `expired: older than <max_age>` and `invalidated: <trigger> (<reference>)` are reported separately, and both when both apply. Merging them hid two different
  required actions.
- 2026-09-23 — Basis hashing reserved in the schema but deliberately not implemented in v0.1. Now promoted as [defer-basis-hashing](.archcore/adr/defer-basis-hashing.adr.md) with its revisit trigger
  stated.
- 2026-09-23 — Eleven documents promoted to `.archcore/`, all `status: proposed` pending operator review. Five candidates were deliberately rejected and the reasoning carried
  into [.archcore/index.guide.md](.archcore/index.guide.md), so the next scan does not re-propose them.
- 2026-09-23 — `type: manual` is a first-class executor; a procedure can produce a recorded observation without being automated.
- 2026-09-23 — Package version pointers in `SKILL.md` and `README.md` corrected forward from 0.1.0 to match the shipped [CHANGELOG.md](CHANGELOG.md) heading, and the three-surface restatement
      registered in the governance
  checker so the next bump cannot drift.

---

## Session history (summaries — full detail belongs in memory-keeper once a channel exists)

### 2026-09-23 — Archcore promotion

- Ratified all eleven documents to `status: accepted` at 13:31 on operator authorisation; ADR body `## Status` lines updated to match the frontmatter.
- Added `check_archcore_contract`: five required frontmatter keys, closed `status` set, and `type:` must match the filename's type segment. `archcore status` checks none of these.
  All four failure modes proven red. Checks 241 to 337.

- Promoted 4 ADRs, 4 rules and 3 specs from `BRIEF.md`, `SKILL.md` and `references/`; deleted `ARCHCORE_PROMOTION_CANDIDATES.md` as `promote` requires.
- `.archcore/index.guide.md` registered as a governance catalog over `.archcore/*/*.md`, enforced in both directions and proven red by deliberate breakage. Checks 189 to 217.
- Found and fixed a lint gate that could not fail: `just lint-md` printed "not installed; skipped" and exited 0 on real violations. Fixed at source in `skill-ai-it`'s template, its own
  justfile and its `SKILL.md` fallback, so other bootstrapped projects stop inheriting it.

### 2026-09-23 — re-upgrade onto template-sourced managed blocks

- The thin navigation block seen at bootstrap was a defect in `skill-ai-it`, not in this package: its upgrade script held an inlined copy that had drifted nine sections behind its template since
  2026-08-11. Fixed at source the same day; this package was re-upgraded onto stamp `2026-09-23-template-sourced-blocks-v1`, gaining the generic sections back inside the markers.
- Headings 17 → 26, no project-authored section lost, and a second consecutive `just nav-upgrade` left `AI_NAVIGATION.md` byte-identical.
- Re-verified: `just check` 189, `just nav-validate` 0/0, `just lint-md` 0, `just validate-all` green.

### 2026-09-23 — governance bootstrap (skill-ai-it)

- Added `AGENTS.md`, `CLAUDE.md`, `AI_NAVIGATION.md`, `context-map.yaml`, `SCRATCHPAD.md`, `justfile`, `.mise.toml`, `requirements.txt`, `.markdownlint-cli2.jsonc`, `repomix.config.json`, and a tuned
  `scripts/check_governance.py`.
- Found and fixed a live version drift: the shipped `CHANGELOG.md` heading was one patch ahead of `SKILL.md` and `README.md`, which both still advertised 0.1.0.
- Registered the package's real invariants as assertions: derived reports must not be older than their inputs; scripts must be cataloged; the version must be stated identically on three surfaces.

---

## Next actions

- Run `just validate-all` and `just check` after any change to a script, schema, example or governance surface.
- ~~Review the eleven `status: proposed` documents~~ — **done 20260923_1331**: all eleven ratified to `status: accepted` and now outrank `AGENTS.md`/`SKILL.md` in the source priority.
- Resolve operator decisions 1 and 2 — nothing else about this package is blocked, but neither is it in use until one of them is answered.
- Once a real suite exists, record the session in memory-keeper and register the project in mcp-project-context so this file stops being the only record.

---

## Memory pointers (navigation only — content is above)

- memory-keeper channel: `skills-stuff`. Keys from the 20260923_1305 slurp: `skills_stuff.skill-eval-manager.governance-bootstrap-20260923`,
  `skills_stuff.task.skill-eval-manager-open-decisions-20260923`, plus the `skills_stuff.skill-ai-it.*` entries covering the upgrader defect that touched this package.
- mcp-project-context project ID: `b8c5525e-3e2f-4fb5-bf87-e5751f3ad49c` (`skills_stuff`); this package has no project of its own.
- Checkpoints: `slurp-20260923-skill-ai-it-template-drift` in both backends (project-context id `4c8a9164-7b60-4072-8390-5d7e91f5ae01`).
- claude-mem: not seeded for this project
