# Ansible Repo Intelligence — Implementation Report (Phases 1–3)

Date: 2026-07-03 (created _1420; addenda through _1556)
Author: Malik Ahmad
Scope: the full phased implementation contract — Phase 1 (discovery, parsing,
canonical graph, bounded map, schema validation, security, determinism), Phase 2
(shared traversal, query, impact, incremental), Phase 3 (benchmark harness).

## Contents

- [Verdict: built & correct, but efficiency targets NOT met](#verdict-built--correct-but-efficiency-targets-not-met)
- [Phase 2 addendum](#phase-2-addendum-2026-07-03-same-day)
- [Phase 3 addendum](#phase-3-addendum-2026-07-03-same-day)
- [Final module/command inventory](#final-modulecommand-inventory)
- [Files created](#files-created)
- [Dependencies selected](#dependencies-selected)
- [CLI commands implemented](#cli-commands-implemented)
- [Test results](#test-results)
- [Real-repository validation (ansible-wifi, 94 roles)](#real-repository-validation-ansible-wifi-94-roles)
- [Security review](#security-review)
- [Deterministic-output proof](#deterministic-output-proof)
- [Repository-map size-budget proof](#repository-map-size-budget-proof)
- [Notable true-positive finding](#notable-true-positive-finding)
- [Limitations / unresolved (honest)](#limitations--unresolved-honest)
- [Next actions](#next-actions)

## Verdict: built & correct, but efficiency targets NOT met

> Updated 20260703_1640 after the external blind-graded benchmark ran.

All 3 phases are implemented, correct, deterministic, and secure. The external
benchmark has now been run (blind, 3 isolated agents) and the **efficiency
targets were not met versus a capable LLM agent**: 19% fewer files (target ≥60%),
+8% tokens (target −40%), correctness 21/22 vs 22/22 baseline. The impressive
harness figures (96.7% fewer files, 100% recall) are a *naive-search proxy*, not
a real-agent result. **The tool is a solid, verified deterministic
navigation/relationship engine; it is NOT validated as a token-savings tool** and
should not be promoted on that basis. Re-scope the benchmark to the tool's real
differentiators before any efficiency claim. Full analysis:
`docs/reports/benchmark-external-grading-20260703_1640.md`.

## Phase 2 addendum (2026-07-03, same day)

Implemented `traversal.py` (shared bounded BFS), `query.py`, and wired the
`query` + `impact` CLI commands plus incremental scan.

- **Shared traversal**: both `query` and `impact` call the same `bounded_bfs`;
  no duplicated reachability/cycle logic (gate #17). Deterministic (sorted
  neighbour visitation).
- **Query bounds**: default 25 nodes / 1 hop / 65 KB; roots exceeding the limit
  mark the result truncated (bug found + fixed in test).
- **Impact bounds**: default 50 nodes / 3 hops / 131 KB; root matching is
  exact-path or directory-prefix only — the initial greedy basename match
  (which hit 1361 roots for `main.yml`) was found and fixed. Now
  `impact roles/smc_dns/tasks/main.yml` → 10 roots, correctly surfaces the file's
  tasks + the `Restart unbound`/`Restart stubby` handlers they notify, with the
  static-only caveat.
- **Incremental**: fingerprint short-circuit — matching parser+config
  fingerprint and unchanged file hashes → "no changes; outputs current" (verified
  on the real repo); any change → safe full rebuild (cross-file resolution needs
  the whole graph). Incremental-force output is byte-identical to a full scan.
- **Tests**: 26 passed (14 Phase 1 gates + 5 hashing + 7 Phase 2).

Real-repo Phase 2 examples validated: `query role smc_dns` (bounded, 1-hop),
`impact --path roles/smc_dns` (tasks/templates/vars/handlers/reaching-play +
`affected` summary). Both stay within bounds and print the source-of-truth
caveat.

## Phase 3 addendum (2026-07-03, same day)

Implemented `benchmark.py`, a 22-question gold-answer set
(`tests/benchmark/questions.ansible_wifi.yaml`), the two-session blind-grading
`tests/benchmark/RUNBOOK.md`, and wired the `benchmark` CLI command.

**Design honesty**: the harness computes only the *deterministic* half and
**never self-grades** correctness. The two isolated agent sessions +
time-to-first-file + answer-correctness + unsupported-claim counting are handed
to the runbook. Overall verdict is therefore PARTIAL by construction.

**Deterministic (harness) results — NAIVE-SEARCH PROXY, not a real-agent win**:

```
files opened — baseline (grep proxy): 3519  |  indexed (map+topic+query): 117
                                       → 96.7% fewer   (vs naive grep only)
indexed retrieval recall: 100.0%   baseline recall: 95.5%   map: 415 lines
```

⚠️ These compare the index against *naive keyword grep of 3519 files* — NOT
against a capable agent. See the external result below.

**External blind-graded run (2026-07-03) — targets NOT met vs a capable agent**:

```
                  baseline   indexed   target        met?
files opened        36         29      ≥60% fewer    NO (19%)
input tokens        79.1k      85.4k   ≥40% lower     NO (+8%)
correctness (blind) 22/22      21/22   no reduction   NO (−1)
unsupported claims   0          1      no increase    NO (+1)
```

A strong agent navigates straight to the right role, so the index's
file-reduction edge collapses (~97% vs grep → ~19% vs agent) and CLI overhead
adds tokens. Full analysis:
`docs/reports/benchmark-external-grading-20260703_1640.md`.

**Tests**: 32 passed (14 Phase 1 + 5 hashing + 7 Phase 2 + 6 Phase 3).

## Final module/command inventory

27 Python modules. CLI: `scan`, `validate`, `clean`, `query`, `impact`,
`explain`, `benchmark` — all fully implemented; no stubs remain (test suite: 52).
Custom plugins & modules (callback/filter/lookup/action/module/module_utils) are
graphed as first-class `dynamic` nodes; `ansible-playbook-grapher` is an opt-in,
structurally-validated, supplementary adapter (`grapher.py`).

## Files created

- Runtime: `.mise.toml` (Python 3.14), `pyproject.toml`. Venv at
  `/Volumes/Data/_ai/_skills/skills-working-cache/skill-ansible-repo-intelligence/venv/`.
- Source (`src/ansible_repo_intelligence/`): `__init__`, `models`, `hashing`,
  `app_config`, `ansible_config`, `yaml_loader`, `discovery`, `collections`,
  `parser`, `inventory_flavors`, `significance`, `vars_plugins`, `variables`,
  `handlers`, `templates`, `resolver`, `inventory`, `context_integration`,
  `graph`, `diagnostics`, `renderer`, `validator`, `cli`.
- Schemas (5): `manifest`, `graph`, `diagnostics`, `significance_rules`,
  `variable_precedence_rules`.
- Config rule tables (2): `config/significance_rules.yaml`,
  `config/variable_precedence_rules.yaml` (both schema-validated before scan).
- Tests: `tests/_gen_fixture.py`, `tests/conftest.py`,
  `tests/unit/test_phase1_gates.py` (14), `tests/unit/test_hashing.py` (5).
- Docs: `SKILL.md`, `README.md`, `AGENTS.md`, this report.

## Dependencies selected

`ruamel.yaml` (line-aware safe/round-trip load), `jsonschema` (Draft 2020-12),
`jinja2` (parse-only AST — added per review, never renders), `networkx`
(available for Phase 2 traversal). All FOSS, offline.

## CLI commands implemented

All seven are fully implemented: `scan`, `validate`, `clean` (Phase 1);
`query`, `impact` (Phase 2); `explain`, `benchmark` (Phase 3). No stubs remain.
(In the original Phase 1 build these later commands returned an explicit
"not available" message with exit 10 — never fake output — until implemented.)

## Test results

```
tests/unit — 19 passed in 0.61s
```

Gates covered by tests: role discovery, vendored-collection exclusion with FQCN
retained, notify→handler resolution, dynamic-include labelling (ARI002),
destructive-task → critical significance (config rule id verified), custom
vars-plugin dynamic modelling + `supplies` edges, role dependency edges, secret
NAME flagged while VALUE never emitted, precedence conflict (ARI006),
source provenance on every source node, inventory flavor+environment scoping,
end-to-end determinism (byte-identical), map line budget, ansible.cfg honoured,
CRLF/CR/BOM hash invariance, non-UTF-8 raises.

## Real-repository validation (ansible-wifi, 94 roles)

```
scan complete: 5114 nodes, 836 edges, diagnostics={'info':38,'warning':85,'error':0,'fatal':0}
map: 415 lines (budget 1000)   validate: valid
2 scans → graph.yaml / ANSIBLE_REPO_MAP.md / diagnostics.yaml byte-identical
source_fingerprint + configuration_fingerprint identical across runs
```

Node kinds: role 94, task 1497, task_file 118, playbook 23, play 96,
handler 119, template 136, variable 1656, inventory_flavor 7,
inventory_group 891, inventory_host 474, collection 2, vars_plugin 1.
Edge types: notifies 186, member_of 495, uses_role 83, include/import_* 45,
depends_on (role deps), supplies 10 (vars-plugin → topology_* vars).

Vendored exclusion: 1160 vendored collection YAML files excluded from
first-class indexing; `community.general` 11.1.2 and `community.grafana` 1.4.0
tracked as collections. Backup exclusion: 4 `inventories/**/*.zip` excluded.
Symlink-escape prevention: 27 governance symlinks flagged (ARI007).
Generated-cache: hidden `.<site>.yml` under `topology_vars/` flagged (ARI024).

## Security review

No repo script executed; Jinja `.parse()` only (tolerant filter map is never
invoked); Vault files detected and never decrypted; secret VALUES never emitted
(verified by test asserting `CHANGEME` absent from graph); external symlinks not
followed by default; max-file-bytes enforced; safe YAML (round-trip, no arbitrary
object construction; `!vault`/`!unsafe` handled as opaque); inventory execution
opt-in only. Custom vars plugin analyzed by `ast`, never imported/executed.

## Deterministic-output proof

Two independent scans of unchanged sources produced byte-identical `graph.yaml`,
`ANSIBLE_REPO_MAP.md`, and `diagnostics.yaml`, and identical manifest
fingerprints. Hashing normalizes BOM + CRLF/CR → LF so clones on different OSes
hash identically (unit-tested).

## Repository-map size-budget proof

Real repo map = 415 lines against a 1000-line hard budget (target band
400–1000). Truncation is visible: `_bounded_list` emits exact omitted counts +
the retrieval command and raises ARI021.

## Notable true-positive finding

`roles/smc_rise_overlay/tasks/main.yml:3` contains
`- name: Guard: overlay must be disabled for apt operations` — an unquoted
`name:` value with an embedded `: `, which is invalid YAML. The scanner flagged
it (ARI023) with precise location and continued; a real latent repo issue, not a
tool defect.

## Limitations / unresolved (honest)

> Updated 20260703_1556 — Phases 2 & 3 are now built (see addenda above); the
> governance pass has run. This section reflects what genuinely remains.

- **External benchmark grading — DONE (2026-07-03), targets NOT met.** Blind,
  3 isolated agents: 19% fewer files (target ≥60%), +8% tokens, correctness
  21/22 vs 22/22. The tool is not validated as a token-savings tool; re-scope the
  benchmark to its real differentiators (handler chains, impact, cross-flavor).
  See `docs/reports/benchmark-external-grading-20260703_1640.md`.
- **`.archcore/` docs are `status: proposed`** — 13 promoted rules/ADRs/specs
  await review + acceptance to become highest-authority truth.
- **Play-level handlers** are parsed as tasks but not double-indexed as handler
  records (role handlers are the dominant case and fully handled).
- **Variable precedence** conflict detection uses a conservative overlap
  heuristic; it never claims a runtime winner (correct per spec) but may
  over-report cross-flavor group/host overlaps. Tunable via config.
- **Not yet built**: golden-file test, `ansible-playbook-grapher` adapter,
  `scripts/` wrappers, `templates/ANSIBLE_REPO_MAP.md.j2` (map is rendered in
  code, not from the j2 template).
- **Resolved since first draft**: Phase 2 (`traversal.py`/`query`/`impact`/
  incremental), Phase 3 (benchmark harness + gold set + RUNBOOK), and the full
  `skill-ai-it` governance pass (ARCHITECTURE/AI_NAVIGATION/context-map/
  CONVENTIONS/ROADMAP/CHANGELOG/justfile + `.archcore` init & promotion).

## Next actions

1. Run external benchmark grading per `tests/benchmark/RUNBOOK.md` (blocks READY).
2. Review + accept the 13 `.archcore/` proposed docs.
3. Add golden-file acceptance test + `ansible-playbook-grapher` adapter.
