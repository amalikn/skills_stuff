# SCRATCHPAD — skill-ansible-repo-intelligence (aka skill-ari)

Live working state. Resume anchor. `KEEP`.

## Current state `KEEP`

All **3 phases built + feature-complete** (2026-07-03). Deterministic, offline,
FOSS static intelligence for Ansible repos.

**Verdict: efficiency FAILURE was REMEDIATED (digest); q21 routing fix confirmed
via Gate A retest (22/22, PASS); Experiment 2 pending for the general claim.**
- First external blind benchmark (16:40): **failed** — +8% tokens, 19% fewer
  files, q05 wrong. 96.7% was a naive-grep proxy.
- Fix (17:10): **managed-resource enrichment + `--view actions` digest.**
  Experiment 1 (blind): **0 source files opened, 78.8k tokens (below baseline
  79.1k), 21/22 with the q05 error FIXED.** Sole miss = q21 (topology vars) —
  a routing miss, not a tool defect.
- **Gate A retest (17:36): PASS.** New deterministic `routing.py` + `route` CLI
  fixed q21. 3-agent isolated rerun (direct / digest+routing / blind grader):
  **both runs 22/22 correct, 0 unsupported claims**; digest run 0 source files,
  0 map/graph reads, 22/22 answered from index alone (46 tool calls vs direct's
  12 — honest tradeoff). Token comparison was a noise-level tie, not a
  re-validated savings claim. See
  `docs/reports/ari-experiment1-routing-retest-20260703_1736.md`.
- Still no *general* token-savings claim until Experiment 2 (relationship-heavy)
  runs. See `docs/reports/ari-efficiency-experiment1-20260703_1710.md`.
- Playbook Execution Digest prompt (`docs/prompts/playbook-execution-digest-
  for-ansible-prompt.md`) reviewed and **deferred** — gated behind Experiment 2
  (Gate D), not built yet.

- **27 Python modules + `routing.py`, 80 tests passing** (~7s), Python 3.14.
- CLI: `scan` `validate` `clean` `query` `impact` `explain` `benchmark` — all
  live, **no stubs**.
- Custom plugins graphed: vars/callback/filter/lookup/action/module/module_utils
  (callbacks flagged if enabled in ansible.cfg).
- 13 `.archcore/` docs **accepted** (highest-authority). Golden-file test +
  opt-in `ansible-playbook-grapher` adapter present.
- Verified on real 94-role **ansible-wifi**: 5114+ nodes, 0 errors,
  byte-deterministic reruns, map 415 lines. Benchmark: **96.7% fewer files
  opened (3519→117), 100% retrieval recall**.

## Open items `KEEP`

- [x] External benchmark (failed) → **remediated via digest** (Experiment 1:
  0 files, sub-baseline tokens, q05 fixed, 21/22). Mechanism validated.
- [x] **Confirm direct-22 re-run** with vars-origin routing fix → **Gate A PASS**
  (22/22 both runs, 0 unsupported, q21 confirmed via vars_plugin evidence).
  `routing.py` + `route` CLI + SKILL.md rule; 16 new tests, 80/80 total green.
- [ ] **Experiment 2** (relationship-heavy: handler chains / `impact` /
  variable-origin / cross-flavor) — direct vs always-indexed vs routed-hybrid,
  blind. The defensible efficiency claim lives here; gates any Regular-Skills
  promotion AND gates the Playbook Execution Digest decision (Gate D).
- [ ] After Exp2: update all docs with validated per-class results.
- [ ] Playbook Execution Digest (`docs/prompts/playbook-execution-digest-for-
  ansible-prompt.md`) — DEFERRED, do not build until Experiment 2 (Gate D)
  shows a repeated measurable gap.
- [ ] Deferred: deterministic question router; `scripts/` wrappers;
  `templates/ANSIBLE_REPO_MAP.md.j2`; node-kind filter to slim ~3 MB `graph.yaml`.
- [x] Phases 1, 2, 3 implemented + verified; full CLI, **no stubs** (`explain` done).
- [x] skill-ai-it governance pass; **13 `.archcore/` docs accepted** (highest-authority).
- [x] Golden-file test; opt-in `ansible-playbook-grapher` adapter.
- [x] Callback/custom-plugin nodes (callback/filter/lookup/action/module/module_utils).
- [x] Moved `implementation-prompt*.md` → `docs/prompts/`; alias `skill-ari`.

## Key anchors `KEEP`

| Thing | Value |
|---|---|
| Source | `/Volumes/Data/_ai/_skills/skills_stuff/skills/skill-ansible-repo-intelligence` |
| Venv | `/Volumes/Data/_ai/_skills/skills-working-cache/skill-ansible-repo-intelligence/venv/` |
| Runtime | `/Volumes/Data/_ai/_skills/skills-runtime/skill-ansible-repo-intelligence/{logs,run}` |
| Target repo | `/Volumes/Data/_ansible/ansible-wifi` (94 roles) |
| Report | `docs/reports/ansible-repo-intelligence-implementation-report-20260703_1420.md` |
| Benchmark set | `tests/benchmark/questions.ansible_wifi.yaml` (22 Q) |
| Run tests | `<venv>/bin/python -m pytest tests -q` |
| Console script | `<venv>/bin/ansible-repo-intelligence` |
| Canonical prompt | `docs/prompts/implementation-prompt-20260703_1349.md` (4 rounds) |
| Durable truth | `.archcore/{rules,adr,specs}/` (13 docs, status: proposed) |

## Recent decisions `KEEP`

- 2026-07-03 — Reviewed the 18-phase Playbook Execution Digest prompt vs the
  close-Experiment-1/run-Experiment-2 prompt; endorsed the latter's sequencing
  (evidence before feature) and deferred the former behind Gate D.
- 2026-07-03 — q21 fixed with a deterministic offline router (`routing.py`),
  not a parser/graph change — q21 was diagnosed as a routing miss, not a tool
  defect, so scope stayed minimal per "smallest justified fix."
- 2026-07-03 — GENERIC flavor/environment discovery (0/1/N inventory scopes),
  never hardcoded to ansible-wifi. User-driven.
- 2026-07-03 — Custom vars plugins `ast`-parsed, never executed → dynamic nodes;
  detected `consumed_dirs` feed flavor discovery generically.
- 2026-07-03 — Vendored collections excluded from first-class nodes; FQCN tracked.
- 2026-07-03 — Incremental = fingerprint short-circuit + safe full rebuild.
- 2026-07-03 — Benchmark never self-grades → PARTIAL by construction.

## Session history `KEEP`

- 2026-07-03 (pm-5) — **q21 routing fix + Experiment 1 Gate A retest.** Reviewed
  and endorsed the close-Exp1/run-Exp2 prompt over the 18-phase playbook-digest
  prompt (deferred). Built `routing.py` (deterministic router, q21 fix) + `route`
  CLI + SKILL.md rule; 16 new tests, 80/80 green. Ran isolated 3-agent
  Experiment 1 retest (direct / digest+routing / blind grader): **Gate A PASS**
  — 22/22 both runs, 0 unsupported claims, 0 files/map/graph reads on digest
  run. Report: `ari-experiment1-routing-retest-20260703_1736.md`. Next:
  Experiment 2 (relationship-heavy, not yet run).
- 2026-07-03 (pm-4) — **Efficiency remediation (digest).** Built managed-resource
  enrichment (`actions.py`) + `--view actions` fact digest (`query.py`), dropped
  map-first. Experiment 1 (blind): **0 files, 78.8k tok (< baseline), q05 FIXED,
  21/22** — sole miss q21 = routing (fixed). Mechanism validated. 64 tests, graph +7.8%.
- 2026-07-03 (pm-3) — External benchmark run (blind, 3 agents): efficiency targets
  NOT met vs a capable agent (later remediated, see pm-4). Corrected overclaims.
- 2026-07-03 (pm-2) — Feature-complete pass: wired `explain` (no stubs);
  accepted 13 `.archcore/` docs; golden-file test; opt-in grapher adapter
  (finds skill-ansible-grapher venv); closed callback-plugin gap (callback/
  filter/lookup/action/module now graphed). 27 modules, 52 tests, deterministic.
- 2026-07-03 (pm) — skill-ai-it bootstrap + promote: created 7 governance docs +
  justfile, archcore init, promoted 13 durable docs to `.archcore/`
  (status: proposed). Moved prompts to `docs/prompts/`. 32 tests still green.
- 2026-07-03 — Reviewed the implementation prompt across 4 rounds (each finding
  fixed), then built all 3 phases end-to-end, verified on ansible-wifi, added
  alias `skill-ari`. Found a true-positive invalid-YAML bug in
  `roles/smc_rise_overlay/tasks/main.yml:3`.

## Next actions `KEEP`

1. Design + run **Experiment 2** (24-question relationship-heavy benchmark,
   3 workflows: direct / always-indexed / routed-hybrid, blind-graded).
2. Apply **Gate D**: build the Playbook Execution Digest spike only if Exp2
   proves a repeated measurable gap; otherwise mark it DEFERRED and stop.
3. After Exp2: update SKILL.md/README/ROADMAP/CHANGELOG with validated
   per-class results before any Regular-Skills promotion.

## Memory pointers `KEEP`

- memory-keeper (channel `skill-ansible-repo-i`, truncated): `skill-ari.overview.status`,
  `.architecture`, `.runtime.env`, `.verification.ansible-wifi`, `.design.decisions`,
  `.open.next-actions`, `.alias`, `.governance.archcore`,
  `.completions.cli-golden-grapher-plugins`, `.benchmark.external-result`,
  `.efficiency.digest-fix`, `.prompts.playbook-digest-vs-exp1-review`,
  `.q21-fix.routing-module`, **`.experiment1.retest-gate-a`**.
  Checkpoints `slurp-20260703-skill-ari-{phases123, governance,cli-complete,
  benchmark-failed,digest-win,exp1-gate-a-pass}`.
- mcp-project-context: project **skills_stuff** (`b8c5525e-3e2f-4fb5-bf87-e5751f3ad49c`),
  channel `skill-ansible-repo-i`, milestone + decision notes,
  checkpoints `slurp-20260703-skill-ari-{phases123,governance,cli-complete,benchmark-failed,digest-win,exp1-gate-a-pass}`.
