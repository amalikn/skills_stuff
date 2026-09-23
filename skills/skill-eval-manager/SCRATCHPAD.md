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

- [x] Operator decision 1 — **closed 20260923_1350**: installed by symlink into `~/.claude`, `~/.codex` and `~/.hermes`, all three resolving to this canonical path. Verified end to end through
      the `~/.claude` link: template validated, an observation appended, a report rendered with the second eval correctly deriving `not_evaluated`.
- [x] Operator decision 2 — **closed 20260923_1352**: `unified-network-controller` writes the first real suite. Evidenced, not assumed: its
      `/Volumes/Data/_ai/_project/project_stuff/apn/unified-network-controller/docs/evaluation-framework-implementation-20260923_0819.md`
      already defines 14 axes with a measure, named oracle, evidence altitude and tier each, and the shipped
      `examples/network-controller/` suite was modelled on it. No other candidate project has an evaluation framework at all.
- [ ] **First-suite blocker (found 20260923_1352) — the gate is now on the controller, not on this package.** `unified-network-controller` has neither `tests/` nor `evals/`, no inventory
      CSV to serve as an independent denominator, and its own plan states that nothing from P3 onward starts until its open decisions 1, 3 and 4 are answered. Its decision 1 (tree split)
      fixes where a suite file lives and its decision 6 fixes the first scorecard's scope, so writing a suite before both are answered produces an artifact in the wrong tree at the wrong
      scope. Ask the operator; do not guess.
- [ ] Operator decision 3: where a consuming project's `history.jsonl` lives. Design record recommends in-repo and committed, because the diff is the audit trail.
- [ ] Operator decision 4: whether a `blocked` verdict satisfies a gate. Design record recommends never, so an unrunnable check does not read as a passing one.
- [ ] Operator decision 5: wire `scripts/validate_suite.py` into a skills-level check so the shipped examples cannot rot. **Partly actioned 20260923_1222** — `just validate-all` now does this
      locally; a
      skills_stuff-wide check is still unwired.
- [ ] Operator decision 6: v0.2 basis hashing — wait for the first project that asks "did this change since we measured it?", then record the question in `BRIEF.md`.
- [x] Package git state — **closed 20260923_1345**: committed as `fed0f74` (package), `293c42b` (skill-ai-it), `7e77d12` (memory pointers) and pushed to <https://github.com/amalikn/skills_stuff>. Decided
      before the first real suite, so the first consuming project pins a published version rather than a moving local tree.

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

- 2026-09-23 — A routing log for consuming-project feedback records **where** knowledge was incorporated, never the knowledge. The obvious design — a place to write findings down — would
  have legitimised recording instead of incorporating, which was the failure being fixed.

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

### 2026-09-23 — rename to the estate convention, and the guard it attracted

- Operator renamed the routing record to `ledger.jsonl` to match `skill-walk-before-run` (v0.1.5). Asked whether to undo it once the OPA consequence surfaced; recommended keeping it, and
  that held: the guard blocks hand-edits of an append-only file, which is the discipline this package demands and could not enforce itself. Git recorded a pure rename, so rows are unchanged.
- The real defect was the policy's routing message, so it was fixed there — <https://github.com/amalikn/tools_stuff> `3096a59`. A second writer added to the exemption, and **both** block reasons (the
  Write/Edit
  one sits separately and was missed on the first pass) stopped sending authors to the other pack's writer, which enforces a different schema.
- Two things corrected in this pack because the rename inverted them: the `scripts/record_writeback.py` docstring and the 0.1.4 changelog paragraph both *argued for* the old name.
- Caught my own unfailable test: the exemption test stayed green after the exemption was removed, because its command never named a ledger file so the guard could not fire. Fixed; the canary
  now goes red. Testing an exemption means first proving the guarded condition was reachable.

### 2026-09-23 — the write-back that half-landed, and the routing log it produced

- Asked where consuming-project feedback is incorporated. Checking rather than quoting the contract showed `references/` — its **first** named destination — had never been touched: zero
  commits, and both schema facts absent from it. The 0.1.3 write-back shipped the executable half (fix + regression fixture) and left the method knowledge in a memory backend.
- Closed that leak in [references/02_defining-evals.md](references/02_defining-evals.md) (*The enclosing document*), then shipped v0.1.4: `ledger.jsonl`,
  [scripts/record_writeback.py](scripts/record_writeback.py), [schemas/write-back-entry.schema.json](schemas/write-back-entry.schema.json) and `check_write_back_log`.
- The log records **where** a finding went, never the finding — a log you can write to and feel finished with would legitimise the very failure it exists to catch. `incorporated_in` is
  defended at write time (destination must exist) and at check time (it must still exist). `open` rows are reported, never fail the build. Checks 353 to 378.

### 2026-09-23 — first real suite, and the first write-back it produced

- `unified-network-controller` wrote the first suite outside this package: one eval, `A6.coverage.epmp-ap`, in its `tests/` tree. Denominator 119 active ePMP AP from the Cambium asset
  register, which is maintained upstream of the controller and not written by the collector. Counterexample fixture built because the controller's fault-injection catalogue has no A6 entry.
- **The write-back contract paid for itself on day one.** Validating that suite crashed `scripts/validate_suite.py` with `AttributeError` instead of reporting a malformed `suite` block,
  whenever `--history` was also passed. Fixed, fixture added, and the package version bumped — see the top of [CHANGELOG.md](CHANGELOG.md).
- A second gap behind it: `just validate-negatives` asserted only a non-zero exit, so a crash was indistinguishable from a clean rejection — the gate meant to catch that regression would
  have passed it. It now requires a non-zero exit, an `INVALID:` line, and no `Traceback`. Proven by reverting the fix.

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
- Take a first A6 measurement for `unified-network-controller` and record it. The suite and procedure exist; its
  `/Volumes/Data/_ai/_project/project_stuff/apn/unified-network-controller/tests/report.md` reads `not_evaluated` until
  someone runs the counts.
- Propose the A6 counterexample as **F13** in the controller's fault-injection catalogue when that plan document is next revised.
- ~~Review the eleven `status: proposed` documents~~ — **done 20260923_1331**: all eleven ratified to `status: accepted` and now outrank `AGENTS.md`/`SKILL.md` in the source priority.
- Resolve operator decisions 1 and 2 — nothing else about this package is blocked, but neither is it in use until one of them is answered.
- Once a real suite exists, record the session in memory-keeper and register the project in mcp-project-context so this file stops being the only record.

---

## Memory pointers (navigation only — content is above)

- memory-keeper channel: `skills-stuff`. Keys from the 20260923_1305 slurp: `skills_stuff.skill-eval-manager.governance-bootstrap-20260923`,
  `skills_stuff.task.skill-eval-manager-open-decisions-20260923`, plus the `skills_stuff.skill-ai-it.*` entries covering the upgrader defect that touched this package.
- mcp-project-context project ID: `b8c5525e-3e2f-4fb5-bf87-e5751f3ad49c` (`skills_stuff`); this package has no project of its own.
- Checkpoints: `slurp-20260923-skill-ai-it-template-drift` in both backends (project-context id `4c8a9164-7b60-4072-8390-5d7e91f5ae01`).
- memory-keeper channel `skill-eval-manager`, session `98449180-a728-4e94-b246-8a56b23478e9`, from the 20260923_1337 persist. Keys: `archcore-promote-ratify-20260923`,
  `archcore-filename-shape`, `archcore-cli-checks-filename-only`, `lint-md-gate-could-not-fail`, `write-back-contract-pattern`, `agents-md-untracked-in-skills-stuff`,
  `commit-state-20260923`. Matching notes under the same channel in project-context.
- Checkpoint `archcore-promote-ratify-20260923` in both backends (memory-keeper `810dfe26`, project-context `019d14d7-f5cc-477c-9635-6b45e1ab3f04`).
- **Slurp 20260923_1411** (this session's second persist, Zone B from the 13:40 boundary): 13 new memory-keeper keys plus 2 updated in place, and 6 matching project-context notes, all on
  channel `skill-eval-manager`. New keys: `install-and-push-20260923`, `markdownlint-config-absence-measures-wrong-standard`, `skill-invocation-and-arguments`, `eval-suite-schema-gotchas`,
  `first-real-suite-unc-a6`, `a6-denominator-derivation`, `unc-no-a6-falsifiability-entry`, `validator-crash-malformed-suite-block`, `negatives-gate-could-not-detect-crash`,
  `write-back-contract-first-return`, `unc-concurrent-session-uncommitted`, `unc-skill-path-rule`, `open-tasks-20260923-1411`. Updated in place: `commit-state-20260923` (now pushed),
  `lint-md-gate-could-not-fail` (remediation complete).
- Checkpoint `slurp-20260923-first-real-suite-and-writeback` in both backends (memory-keeper `45fe682e`, project-context `8e98da89-8c81-4275-b1a4-b38cb8f53dd2`).
- **Slurp 20260923_1426** (Zone B from the 14:13 boundary): 5 new memory-keeper keys plus 3 updated in place, and 3 project-context notes, channel `skill-eval-manager`. New:
  `write-back-routing-log-design`, `opa-guard-matches-command-text`, `references-destination-has-no-gate`, `wrong-claude-mem-observation-writeback`, `open-tasks-20260923-1426`.
  Updated: `write-back-contract-first-return` (it half-landed), `eval-suite-schema-gotchas` (now in the package, not memory-only), `commit-state-20260923`.
- Checkpoint `slurp-20260923-write-back-routing-log` in both backends (memory-keeper `71028bef`, project-context `b7fd2785-b309-4819-92b5-b63c190fddba`).
- Session closeout: memory-keeper `session.closeout.20260923.eval-manager-writeback`, with a matching project-context note. Covers the whole 2026-09-23 arc — promotion through to the
  routing log — in one place, including the open issues and next actions.
- **Slurp 20260923_1628** (Zone B from the 14:28 boundary): 7 new memory-keeper keys plus 2 updated in place, and 3 project-context notes. New: `ledger-rename-bought-enforcement`,
  `opa-ledger-guard-exact-semantics`, `opa-guard-second-writer-fix`, `unfailable-test-caught-by-canary`, `opa-repo-uncommitted-work`, `auto-mode-classifier-denied-opa-verification`,
  `open-tasks-20260923-1628`. Updated: `write-back-routing-log-design` (filename changed), `commit-state-20260923` (two repos now).
- Checkpoint `slurp-20260923-ledger-rename-and-opa-guard` in both backends (memory-keeper `c47c2374`, project-context `d95a262f-c7fa-4883-af8e-286d23247db8`).
- claude-mem: not seeded for this project
