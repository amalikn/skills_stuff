# Changelog — skill-ansible-repo-intelligence (skill-ari)

## 20260703_1736

### q21 routing fix + Experiment 1 Gate A retest — PASS

- **Note:** the managed-resource digest remediation (`actions.py`,
  `--view actions`, ~17:10) that reversed the 16:40 benchmark failure was not
  logged as its own CHANGELOG entry at the time — see
  `docs/reports/ari-efficiency-experiment1-20260703_1710.md` for that work.
  This entry covers the follow-on q21 fix and retest.
- Reviewed two competing next-step prompts: an 18-phase Playbook Execution
  Digest proposal (deferred — premature, no evidence yet) vs a prompt that
  fixes q21 routing, reruns Experiment 1, then gates the playbook digest
  behind a relationship-heavy Experiment 2. Endorsed and executed the latter.
- **New `src/ansible_repo_intelligence/routing.py`** — deterministic, pure,
  offline `classify_question()`. Never executes a tool; variable-origin/
  precedence/vars-plugin question classes are checked before role-config
  keywords so a q21-shaped question can no longer route to the role digest.
- **New `route` CLI subcommand** (`cli.py::cmd_route`) — advisory only.
- **SKILL.md** — new mandatory "Variable-origin routing" section.
- **New `tests/unit/test_routing.py`** — 16 tests. Full suite: 80/80 passed.
- **Experiment 1 retest** (isolated 3-agent rerun: direct baseline / digest+
  routing / blind grader on anonymized outputs): **Gate A PASS** — 22/22
  correct both runs, 0 unsupported claims, 0 source files/map/graph reads on
  the digest workflow (was 21/22 with the q21 miss). Token comparison was a
  noise-level tie, not a re-validated savings claim.
  Report: `docs/reports/ari-experiment1-routing-retest-20260703_1736.md`.
- Updated `ROADMAP.md`, `README.md`, `ARCHITECTURE.md` (module ownership:
  `routing.py`, `actions.py` backfilled), `AGENTS.md` (local + parent
  `skills_stuff/AGENTS.md` authoring row), `justfile` (`route` task),
  `SCRATCHPAD.md` for coherence.
- Playbook Execution Digest remains DEFERRED pending Experiment 2 (Gate D).

## 20260703_1640

### Benchmark (external, blind) — targets NOT met

- Ran `tests/benchmark/RUNBOOK.md` properly: 3 isolated subagent contexts
  (baseline no-index / indexed map+CLI / blind grader that read gold source and
  didn't know which run was which).
- **Result: efficiency targets NOT met vs a capable LLM agent.** Files opened
  36→29 (19% fewer, target ≥60%); tokens 79.1k→85.4k (+8%, target −40%);
  correctness 21/22 indexed vs 22/22 baseline; unsupported claims 1 vs 0.
  Retrieval recall (harness proxy) 100%.
- **Corrected overclaims** in SKILL.md, README.md, ROADMAP.md and the
  implementation report: the "96.7% fewer files / 100% recall" figures are a
  *naive-grep proxy*, not a real-agent win. Repositioned the tool as
  deterministic **navigation & relationship intelligence**, not token-savings.
- New outcome doc: `docs/reports/benchmark-external-grading-20260703_1640.md`.
- **Do not promote to Regular Skills on efficiency grounds.** Re-scope the
  benchmark to the tool's real differentiators and re-run first.

## 20260703_1615

### Added

- **Custom plugin & module nodes** (was a gap — only vars plugins were graphed):
  `callback_plugin`, `filter_plugin`, `lookup_plugin`, `action_plugin`, `module`,
  `module_utils` now emit first-class nodes, all `resolution: dynamic` (runtime
  behaviour). Callback plugins enabled in `ansible.cfg`
  (`callbacks_enabled`/`callback_whitelist`) carry `enabled_in_ansible_cfg: true`
  and appear in the map's new "Custom plugins & modules" section. Verified on
  ansible-wifi: `role_version_logger` flagged enabled.
- **Golden-file acceptance test** (`tests/integration/test_golden.py` +
  `tests/golden/multi_role_repo/`): scan → byte-for-byte diff against committed
  golden, golden self-validates, and scan-repeatability. `just golden` regenerates.
- **`ansible-playbook-grapher` adapter** (`grapher.py`): OPT-IN via
  `--playbook-grapher` (+ `--grapher-playbook`). Supplementary evidence only —
  scan never depends on it. Resolves the binary from PATH **or the sibling
  `skill-ansible-grapher` managed venv** (`ANSIBLE_PLAYBOOK_GRAPHER` env override).
  Output is structurally validated (a zero exit is never trusted alone); honest
  provenance recorded in `manifest.external_tools`. Default scan keeps
  `external_tools: {}` so machine-specific availability never breaks determinism.
- Tests: +12 (grapher, plugins, golden). Suite now **52 passing**.

### Accepted

- All 13 `.archcore/` docs flipped `status: proposed` → `accepted` (5 rules,
  6 ADRs, 2 specs) — now highest-authority durable truth. `archcore status` clean.

## 20260703_1602

### Added

- `explain` command — focused explanation of one node: source (path:lines),
  resolution status/confidence/reason, significance + rule id, key attributes,
  and 1-hop incoming/outgoing relationships each with their edge reason. Resolves
  a target by exact node id or by name; lists candidates when a name is
  ambiguous (e.g. `dns` = role + inventory group). Implemented in `query.py`
  reusing `GraphStore`; wired into CLI. **No CLI stubs remain.**
- 9 `explain` tests (`tests/unit/test_explain.py`); suite now 41 passing.

### Changed

- `README.md`, `SKILL.md`, `ROADMAP.md` — reflect `explain` implemented / all
  CLI commands live.

## 20260703_1558

### Changed (report maintenance)

- `docs/reports/ansible-repo-intelligence-implementation-report-20260703_1420.md`:
  - Corrected self-contradictory "Limitations / unresolved" + "Next actions"
    sections — they still claimed "Phase 2 not built / Phase 3 not built" and
    listed the `skill-ai-it` governance pass as pending, contradicting the
    report's own top. Now reflects reality (only remaining: external benchmark
    grading, accept 13 `.archcore` proposed docs, `explain` stub).
  - Added `## Contents` TOC (file >100 lines, per markdown-guide).
  - Merged the verdict heading that was split across two `##` lines (rendered as
    two broken headings) into one.
  - Retitled "Phase 1 Implementation Report" → "Implementation Report
    (Phases 1–3)"; scope line updated to cover all three phases.

## 20260703_1556

### Changed (coherence sweep)

- `README.md` "Status / limitations" — corrected stale claim that Phases 2–3 are
  "planned"; now reflects all 3 phases built + PARTIAL-by-design verdict. This was
  the only drift found after the prompt move + governance/promotion changes.

### Notes

- Coherence sweep (`skill-project-coherence`): verified no stale root-level
  `implementation-prompt` references remain after the `docs/prompts/` move (only
  the CHANGELOG audit-trail entry, which is correct); phase-status consistent
  across README/SKILL/ROADMAP; 32 tests still green.

## 20260703_1555

### Changed

- Moved `implementation-prompt.md`, `implementation-prompt-20260703_1347.md`,
  `implementation-prompt-20260703_1349.md` → `docs/prompts/` (root de-cluttered;
  canonical prompt is `docs/prompts/implementation-prompt-20260703_1349.md`).

## 20260703_1552

### Added (promote)

- Promoted 13 durable-truth documents into `.archcore/` (all `status: proposed`,
  with provenance headers):
  - Rules (5): `no-runtime-execution`, `bounded-retrieval`, `lean-output`,
    `determinism`, `derived-context-authority`.
  - ADRs (6): `ruamel-round-trip`, `tolerant-jinja-filters`,
    `generic-inventory-scoping`, `shared-traversal`, `incremental-safe-rebuild`,
    `benchmark-no-self-grade`.
  - Specs (2): `node-edge-schema`, `module-ownership`.
- Files follow archcore `<slug>.<type>.md` naming; `archcore status` clean.

### Removed

- `ARCHCORE_PROMOTION_CANDIDATES.md` — consumed by promotion (all content files
  written successfully).

### Notes

- Generated by `skill-ai-it` in `promote` mode. Docs are `status: proposed`;
  accept/finalize in archcore when reviewed.

## 20260703_1545

### Added

- Governance scaffold via `skill-ai-it` (bootstrap): `ARCHITECTURE.md`,
  `AI_NAVIGATION.md`, `context-map.yaml`, `CONVENTIONS.md`, `ROADMAP.md`,
  `CHANGELOG.md`, `justfile`.
- Initialized `.archcore/` (archcore CLI available).
- Added AI navigation managed block to `AGENTS.md`; governance pointers to `README.md`.

### Notes

- Generated by `skill-ai-it` in `bootstrap` mode. Existing base governance
  (`README.md`, `AGENTS.md`, `CLAUDE.md`, `SKILL.md`, `SCRATCHPAD.md`) preserved,
  not overwritten.

## 20260703_1420

### Added

- **Phases 1–3 implemented** in a single session. 26 Python modules, 32 tests.
  - Phase 1: discovery, parsing, canonical graph, bounded map, 5 schemas,
    2 config rule tables, security controls, deterministic hashing.
  - Phase 2: shared `traversal.py`, bounded `query` + `impact`, incremental scan.
  - Phase 3: `benchmark` harness, 22-question gold set, blind-grading RUNBOOK.
- CLI: `scan`, `validate`, `clean`, `query`, `impact`, `benchmark` live; `explain` stub.
- SKILL.md/README.md/AGENTS.md/CLAUDE.md; alias `skill-ari` registered.

### Changed

- Registered in `skills_stuff/AGENTS.md` "Skill Authoring Projects" table.

### Notes

- Verified on real 94-role `ansible-wifi`: 5114 nodes/836 edges, 0 errors,
  byte-deterministic reruns, map 415 lines. Benchmark: 96.7% fewer files opened,
  100% retrieval recall.
- **Verdict: PARTIAL** — benchmark correctness/unsupported-claim grading requires
  external two-session blind grading (`tests/benchmark/RUNBOOK.md`); never self-graded.
- True-positive found: invalid YAML in `roles/smc_rise_overlay/tasks/main.yml:3`
  (flagged ARI023, scan continued).
