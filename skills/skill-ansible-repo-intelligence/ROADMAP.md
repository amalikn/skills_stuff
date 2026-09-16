# Roadmap — skill-ansible-repo-intelligence (skill-ari)

## Current phase

**Phases 1–3 built and verified; efficiency failure remediated; Gate A PASS.**
External benchmark grading (16:40) found efficiency targets **NOT met** vs a
capable LLM agent (19% fewer files vs ≥60% target; +8% tokens; correctness
21/22 vs 22/22). Root cause: the harness's 96.7%/100% figures were a
*naive-search proxy*, not a real-agent win.

That failure was **remediated** (17:10) with managed-resource enrichment
(`actions.py`) + a `--view actions` fact digest: Experiment 1 rerun showed
0 source files opened, 78.8k tokens (below the 79.1k baseline), and the q05
Asterisk error fixed. The sole remaining miss, q21 (topology-variable origin),
was diagnosed as a **routing** failure, not a tool defect.

q21 was fixed (17:20) with a deterministic offline router (`routing.py` +
`ansible-repo-intelligence route`) and confirmed (17:36) via an isolated
3-agent Experiment 1 retest: **Gate A PASS** — 22/22 correct both runs (direct
baseline and digest+routing), 0 unsupported claims, 0 source files/map/graph
reads on the digest workflow. Token comparison in the retest was a noise-level
tie, not a re-validated savings claim — treat the original 78.8k/79.1k figures
as the reference for that claim, not this retest's numbers.

**Verdict: role-level digest + routing READY; general efficiency claim still
gated on Experiment 2** (relationship-heavy: handler chains, `impact`,
variable-origin, cross-flavor). Full analysis:
`docs/reports/benchmark-external-grading-20260703_1640.md`,
`docs/reports/ari-efficiency-experiment1-20260703_1710.md`,
`docs/reports/ari-experiment1-routing-retest-20260703_1736.md`.

The 18-phase **Playbook Execution Digest** proposal
(`docs/prompts/playbook-execution-digest-for-ansible-prompt.md`) was reviewed
and **deferred** — it will only be built if Experiment 2 proves a repeated
measurable gap (Gate D in
`docs/prompts/close-experiment1-and-run-expermient2.md`).

## Completed

- [x] **Phase 1** — discovery, parsing, canonical graph, bounded map, 5 schemas,
  2 config rule tables, security controls, deterministic hashing. Verified on
  94-role ansible-wifi (5115 nodes, byte-deterministic, map 415 lines).
- [x] **Phase 2** — shared `traversal.py`, bounded `query` + `impact`, incremental
  scan (fingerprint short-circuit + safe full rebuild).
- [x] **Phase 3** — `benchmark` harness, 22-question gold set, blind-grading
  RUNBOOK. Harness proxy (vs naive grep): 96.7% fewer files, 100% recall — the
  real-agent external run initially did NOT meet targets, then was remediated
  (see Current phase).
- [x] **Efficiency remediation** — managed-resource digest (`actions.py`,
  `--view actions`) turned the +8% token loss into a sub-baseline result with
  zero source-file opens (Experiment 1, 2026-07-03 17:10).
- [x] **q21 routing fix + Gate A retest** — deterministic router (`routing.py`,
  `route` CLI) + isolated 3-agent rerun: 22/22 correct, 0 unsupported claims,
  0 files/map/graph reads on the digest workflow (2026-07-03 17:36).
- [x] Governance scaffold (this bootstrap).

## Next milestones

- [x] **External benchmark grading** — done (2026-07-03, blind, 3 isolated
  agents). Initial targets NOT met vs a capable agent; remediated via digest;
  see outcome docs.
- [x] **q21 routing fix + Experiment 1 retest (Gate A)** — done (2026-07-03,
  blind, 3 isolated agents). PASS: 22/22 correct, 0 unsupported claims, 0 files
  opened on digest workflow.
- [ ] **Experiment 2** — relationship-heavy benchmark (handler-chain / `impact` /
  reachability / variable-origin / cross-flavor / dynamic-reference questions),
  3 isolated workflows (direct / always-indexed / routed-hybrid), blind-graded.
  This is where the defensible *general* efficiency claim lives; also decides
  Gate D (Playbook Execution Digest justified or deferred).
- [x] Accept the 13 `.archcore/` docs — done (2026-07-03); now `status: accepted`.
- [x] Wire `explain` command — done; no CLI stubs remain.
- [x] Golden-file acceptance test under `tests/golden/` — done.
- [x] `ansible-playbook-grapher` optional adapter (opt-in, supplementary) — done.
- [x] Custom plugin & module nodes (callback/filter/lookup/action/module) — done.
- [ ] `scripts/` wrappers + `templates/ANSIBLE_REPO_MAP.md.j2` (map currently
  rendered in code).
- [ ] Optional: node-kind filtering to slim `graph.yaml` (~3 MB on ansible-wifi).
- [ ] Playbook Execution Digest — DEFERRED pending Experiment 2 Gate D.

## Promotion gate

Experiment 2 must run and clear its per-category gates (see
`docs/prompts/close-experiment1-and-run-expermient2.md` Part 6) before promotion
from `skills_stuff/AGENTS.md` "Skill Authoring Projects" to "Regular Skills" and
install to `~/.claude/skills`, `~/.codex/skills`, `~/.hermes/skills/domain`.
Role-digest efficiency (Gate A) is confirmed; the general claim is not yet.
