Title: Archcore Index — Agent Stack
Category: durable-truth-index
Status: current
Last reviewed: 20260902_0300
Summary: Index of Agent Stack's 29 accepted durable decisions, rules, contracts, guides and plans, with the division of labour against MEMORY.md and the standing never-promote list.

# Archcore — Agent Stack

Durable project truth: decisions that are settled, rules that are enforced, contracts that other work must satisfy. Promoted 20260902_0245 by `skill-ai-it promote` from a candidate queue regenerated
the same night; that queue is deleted, as it is a proposal mechanism and not a record.

**All 29 documents were ACCEPTED by the operator on 20260902_0300.** They are now the highest-authority statement of what this project has decided. Each states a decision already in force, and most
are enforced by a check that has been proven able to fail.

An accepted document is not immutable. It is superseded **in place** with a dated banner naming what replaced it and what still stands — never deleted, because the superseded reasoning is usually the
part a later reader needs. [ADR 0009](adr/0009-sync-apply-is-atomic.md) is the worked example: it supersedes a deferral recorded in `REVISION_NOTES.md` and says so.

## Contents

- [Division of labour with MEMORY.md](#division-of-labour-with-memorymd)
- [Decisions](#decisions)
- [Rules](#rules)
- [Contracts](#contracts)
- [Guides](#guides)
- [Plans](#plans)
- [Never promoted, and why](#never-promoted-and-why)
- [Proposing another](#proposing-another)

## Division of labour with MEMORY.md

Two durable surfaces exist and they do not overlap. Getting this wrong recreates the two-taxonomies problem this project already paid for once with `satisfied_by_skills`.

| Surface      | Holds                                                                             | Changes                      |
| ------------ | --------------------------------------------------------------------------------- | ---------------------------- |
| `.archcore/` | Decisions, rules and contracts — the shape of the system                          | Rarely, by explicit decision |
| [MEMORY.md](../MEMORY.md)    | Measured baselines, metric definitions, traps already hit, what is currently open | Every substantive session    |

**The test:** a document belongs here only if it would still read as true after the next three baselines. Anything carrying a number a re-run could move stays in `MEMORY.md`. That is why no figure in
this directory is a current measurement — where one appears, it is cited as the evidence for a decision and dated.

## Decisions

| Document                                                | Governs                                                          |
| ------------------------------------------------------- | ---------------------------------------------------------------- |
| [0001 Autonomy is excluded by design](adr/0001-autonomy-is-excluded-by-design.md)                     | Why the upstream loop, consensus and daemon are absent           |
| [0002 Canonical source, symlinked delivery](adr/0002-canonical-source-symlinked-delivery.md)               | Where content is authored and how it is delivered                |
| [0003 The manifest is the contract](adr/0003-the-manifest-is-the-contract.md)                       | Why installer, validator and routing share one source            |
| [0004 Sync is report-first](adr/0004-sync-is-report-first.md)                               | What upstream sync may apply without review                      |
| [0005 Stdlib-only governance gate](adr/0005-stdlib-only-governance-gate.md)                        | Why the gate must never fail for environment reasons             |
| [0006 Capability-based routing](adr/0006-capability-based-routing.md)                           | Gate as obligation, capability declared once, strength semantics |
| [0007 The model judges; the system satisfies constraints](adr/0007-model-judges-system-satisfies.md) | The division of labour between model and closure layer           |
| [0008 Scope excludes slurp and coherence](adr/0008-scope-excludes-slurp-and-coherence.md)                 | An operator scope decision with a revert as evidence             |
| [0009 Sync apply is staged, then promoted](adr/0009-sync-apply-is-atomic.md)                | The upstream sync transaction model                              |

## Rules

| Document                                                                | Enforced by                                            |
| ----------------------------------------------------------------------- | ------------------------------------------------------ |
| [0001 Safety model](rules/0001-safety-model.md)                                                       | Review; it is the project's defining constraint set    |
| [0002 Runtime placement and interpreter pinning](rules/0002-runtime-placement.md)                          | `check_venv_outside_repo`, `check_interpreter_pinning` |
| [0003 Registration and upstream baseline hygiene](rules/0003-manifest-registration.md)                         | Manifest coverage checks, both directions              |
| [0004 An audit is evidence, not policy](rules/0004-audit-is-evidence-not-policy.md)                                   | Review discipline                                      |
| [0005 One persona model](rules/0005-one-persona-model.md)                                                  | Two validator checks, both negative-tested             |
| [0006 required_personas is mandatory ownership](rules/0006-required-personas-is-ownership.md)                           | Corpus authoring policy                                |
| [0007 Capability annotations are honest](rules/0007-capability-annotations-are-honest.md)                                  | Review; the taxonomy's cardinal rule                   |
| [0008 An execution error is not a routing score](rules/0008-execution-errors-are-not-scores.md)                          | `evaluate_routing.py` denominator handling             |
| [0009 A provenance stamp covers inputs](rules/0009-provenance-covers-inputs.md)                                   | Contract-block validator check                         |
| [0010 Sync refuses symlinks and enforces containment](rules/0010-sync-refuses-symlinks.md)                     | `sync_auto_company.py`                                 |
| [0011 Gate errors are asymmetric](rules/0011-gate-errors-are-asymmetric.md)                                         | `evaluate_routing.py` scorer                           |
| [0012 Gate flags are advisory until the collapse is localised](rules/0012-gate-flags-are-advisory-until-localised.md) *(proposed)* | Operator policy for current use                        |

## Contracts

| Document                                                          | Defines                                                 |
| ----------------------------------------------------------------- | ------------------------------------------------------- |
| [0001 Skill package contract](specs/0001-skill-package-contract.md)                                       | The shape of a skill package                            |
| [0002 Runtime prerequisite contract](specs/0002-runtime-prerequisites.md)                                | What a tool-class skill owes before it can be routed to |
| [0003 The four-table routing catalogue](specs/0003-routing-catalogue-contract.md)                             | capabilities, gates, precedence, route invariants       |
| [0004 Route closure contract](specs/0004-route-closure-contract.md)                                       | What the repair layer may and may not do                |
| [0005 Routing eval corpus contract](specs/0005-eval-corpus-contract.md)                                 | Hard versus preferred assertions; the corpus freeze     |
| [0006 Runner qualification before evidence is spent](specs/0006-runner-qualification.md) *(proposed)*     | Evaluation pipeline reliability                         |
| [0007 Gate-only evaluation and precision/recall scoring](specs/0007-gate-only-evaluation.md) *(proposed)* | Localising the gate collapse                            |

## Guides

| Document                                    | Procedure                                         |
| ------------------------------------------- | ------------------------------------------------- |
| [0001 Upstream sync workflow](guides/0001-upstream-sync.md)                 | status, dry-run, fetch-dry-run, apply             |
| [0002 Global installation](guides/0002-global-installation.md)                    | Symlink-only install, preview, and safe removal   |
| [0003 Running and reading a routing baseline](guides/0003-running-a-routing-baseline.md) | Freeze, stamp, smoke-test, rescore, read honestly |

## Plans

| Document                           | Status                                                  |
| ---------------------------------- | ------------------------------------------------------- |
| [0001 Next evaluation phase](plans/0001-next-evaluation-phase.md)         | Approved; unseen holdout, real-task replay, shadow mode |
| [0002 Sync hardening (audit A1/A2)](plans/0002-sync-hardening.md)  | **Completed** 2026-09-02                                    |
| [0003 Holdout 2 protocol](plans/0003-holdout-two-protocol.md) *(proposed)* | Preconditions before a second blind corpus              |

## Never promoted, and why

Carried out of the candidate queue before it was deleted, so a future scan does not re-propose these.

| Item                                             | Why not                                                                                                                        |
| ------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------ |
| Audit findings as a whole                        | Findings are evidence, not decisions. `REVISION_NOTES.md` records which were accepted. See [rule 0004](rules/0004-audit-is-evidence-not-policy.md).                          |
| `docs/audit-agent-stack.md`                      | It is the audit **prompt**, not a second report. Never a duplicate and never a promotion candidate.                                |
| `CHANGELOG.md` entries                           | History, not truth. Explicitly excluded from candidate inspection.                                                             |
| `upstream-state.json`, `translation-memory.json` | Generated sync state, rewritten by the tool.                                                                                   |
| `.ai-context/`, `graphify-out/`                  | Generated support artifacts, always rebuildable.                                                                               |
| Individual `skills/*/SKILL.md` content           | Upstream-derived and governed by `SKILL_STANDARD.md`; promoting it would fork the library.                                     |
| Session summaries in `SCRATCHPAD.md`             | Working memory. The durable history layer is memory-keeper and `CHANGELOG.md`.                                                 |
| **Measured baselines and metric values**             | A re-run moves them. A promoted copy would be stale within a day and would then contradict its source. `MEMORY.md` owns these. |
| **Traps already hit**                                | Operational memory. They accumulate faster than an ADR set should, and `MEMORY.md` owns them.                                  |

## Proposing another

1. Write the candidate into the source it belongs to first — `AGENTS.md`, `ARCHITECTURE.md`, or `MEMORY.md`.
2. Run `/skill-ai-it refresh` to regenerate a candidate queue, or add the document here directly with a provenance header, starting at `Status: proposed`.
3. Apply the test above: would it still read as true after the next three baselines? If not, it belongs in `MEMORY.md`.
4. Cite it from the check that enforces it, if one exists. A rule with no enforcement and no citation is a preference.
