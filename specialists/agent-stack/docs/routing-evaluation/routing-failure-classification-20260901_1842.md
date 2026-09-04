Title: Baseline v2 Unsatisfied-Gate Failure Classification
Category: routing-evaluation-analysis
Status: current
Scope: The 22 gate-unsatisfied hard failures in Baseline v2, classified before any capability-taxonomy change
Last reviewed: 20260901_2015
Summary: All 22 classify as ROUTING DEFECT and none as capability-mapping, so the capability-taxonomy refactor is a maintainability change with a predicted re-score gain of zero.

# Baseline v2 Unsatisfied-Gate Failure Classification

Step 1 of the sequence in agent-stack-capability-taxonomy-and-scoring.md, a draft that was never migrated into this repository and sits untracked at the `specialists/` level above it — found stale by
the 2026-09-04 staleness audit. Its governing principle is the reason this document exists before any catalogue edit: *the capability taxonomy should describe what skills genuinely do, not what the
eval suite wishes they had done.* That principle is now carried forward by [Rule 0007](../../.archcore/rules/0007-capability-annotations-are-honest.md) and the capability model in
[routing.toml](../../routing.toml); the draft itself was superseded by the Baseline v3/v4 and deterministic-closure work and should not be treated as a live governing document.

## Contents

- [Headline finding](#headline-finding)
- [Why none of these are capability-mapping defects](#why-none-of-these-are-capability-mapping-defects)
- [Two checks run before classifying](#two-checks-run-before-classifying)
- [The 22](#the-22)
- [What actually fixes these](#what-actually-fixes-these)
- [Falsifiable prediction — CONFIRMED 2026-09-01](#falsifiable-prediction-confirmed-2026-09-01)
## Headline finding

**All 22 are ROUTING DEFECTS. Zero are capability-mapping defects, zero are gate-trigger defects, zero are corpus defects, zero are scoring defects.**

In every case the router judged the gate correctly and then equipped the route with neither a satisfying skill nor the gate's persona — while the corpus itself lists that persona as required or
preferred, so a satisfying route was always reachable.

| Classification            | Count | Share |
| ------------------------- | ----: | ----: |
| ROUTING DEFECT            | 22    | 100%  |
| CAPABILITY-MAPPING DEFECT | 0     | 0%    |
| GATE-TRIGGER DEFECT       | 0     | 0%    |
| CORPUS DEFECT             | 0     | 0%    |
| SCORING/VALIDATOR DEFECT  | 0     | 0%    |

By gate: `critic_required` 11 · `research_required` 9 · `qa_required` 2. By route shape: 17 selected non-satisfying skills, 5 selected no skills at all.

## Why none of these are capability-mapping defects

A mapping defect requires that the selected skill *genuinely provides* the capability and the catalogue merely fails to say so. Each candidate was checked against what the skill actually does, not
against whether relabelling it would raise the score:

| Selected skill                     | Gate it failed to satisfy | Would a relabel be honest?                                                                                                          |
| ---------------------------------- | ------------------------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| `financial-unit-economics`         | research, critic          | No. Unit economics is analysis of supplied assumptions. It acquires no external evidence and challenges no conclusion.              |
| `deep-analysis`                    | research                  | No. Structured multi-angle analysis of what is already present. Its persona list includes `critic-munger`, which is a tempting but  |
|                                    |                           |   insufficient reason.                                                                                                              |
| `premortem`                        | research                  | No. It is already the canonical `independent-challenge` provider; that does not make it an evidence-acquisition skill.              |
| `security-audit`, `senior-qa`      | critic                    | No. Security and test review are `validation` and `security-review`, not independent challenge of a conclusion.                     |
| `devops`                           | qa                        | No. Release checks are incidental to a deployment skill — `validation` supporting at best, which by design does not satisfy a       |
|                                    |                           |   hard gate.                                                                                                                        |
| `competitive-intelligence-analyst` | critic                    | No. It is already a `research` satisfier. Competitive analysis is not adversarial challenge.                                        |
| `team`                             | critic, qa                | No. Team formation carries neither capability.                                                                                      |

Marking any of these would breach the taxonomy document's own §14 prohibition and would destroy the `analysis ≠ independent challenge` invariant that `critic_required` exists to enforce.

## Two checks run before classifying

Both were written to falsify the classification, not to support it.

1. **Corpus self-consistency.** For every case asserting a gate, do that case's own required + preferred skills and personas contain something that satisfies it? **0 of 60 fail.** A corpus that
   asserted an unsatisfiable gate would make some of these failures corpus defects; none does.
2. **Hallucinated skill ids.** Do any Baseline v2 plans name a skill absent from `routing.toml`? **None.** `team` looked like a hallucination and is a real catalogue entry, so case 1 and 2 are genuine
   selections of a non-satisfying skill rather than a parse artefact.

## The 22

| #   | Case                      | Family             | Gate     | Selected skills                            | Route shape         | Class   | Reachable fix the router missed                       |
| --: | ------------------------- | ------------------ | -------- | ------------------------------------------ | ------------------- | ------- | ----------------------------------------------------- |
| 1   | `agent-routing-design`    | software-ai        | critic   | `team`                                     | non-satisfying      | ROUTING | add satisfier or `critic-munger` (corpus lists        |
|     |                           |                    |          |                                            |   skills            |         |   it preferred)                                       |
| 2   | `agent-routing-design`    | software-ai        | qa       | `team`                                     | non-satisfying      | ROUTING | add satisfier or `qa-bach` (corpus lists              |
|     |                           |                    |          |                                            |   skills            |         |   it preferred)                                       |
| 3   | `ambiguous-best-nas`      | direct-adversarial | critic   | `competitive-intelligence-analyst`         | non-satisfying      | ROUTING | add satisfier or `critic-munger` (corpus lists        |
|     |                           |                    |          |                                            |   skills            |         |   it preferred)                                       |
| 4   | `atar-landed-cost`        | atar-import        | research | `financial-unit-economics`                 | non-satisfying      | ROUTING | add satisfier or `research-thompson` (corpus lists    |
|     |                           |                    |          |                                            |   skills            |         |   it required)                                        |
| 5   | `atar-landed-cost`        | atar-import        | critic   | `financial-unit-economics`                 | non-satisfying      | ROUTING | add satisfier or `critic-munger` (corpus lists        |
|     |                           |                    |          |                                            |   skills            |         |   it preferred)                                       |
| 6   | `atar-pilot`              | atar-import        | critic   | `financial-unit-economics`,                | non-satisfying      | ROUTING | add satisfier or `critic-munger` (corpus lists        |
|     |                           |                    |          |   `market-sizing-analysis`                 |   skills            |         |   it preferred)                                       |
| 7   | `generic-import-pilot`    | atar-import        | critic   | `financial-unit-economics`,                | non-satisfying      | ROUTING | add satisfier or `critic-munger` (corpus lists        |
|     |                           |                    |          |   `market-sizing-analysis`                 |   skills            |         |   it preferred)                                       |
| 8   | `infra-cicd-rollout`      | networking-infra   | qa       | `devops`                                   | non-satisfying      | ROUTING | add satisfier or `qa-bach` (corpus lists it required) |
|     |                           |                    |          |                                            |   skills            |         |                                                       |
| 9   | `jdm-landed-cost`         | jdm-import         | critic   | `financial-unit-economics`,                | non-satisfying      | ROUTING | add satisfier or `critic-munger` (corpus lists        |
|     |                           |                    |          |   `deep-research`                          |   skills            |         |   it preferred)                                       |
| 10  | `jdm-pilot-one-car`       | jdm-import         | research | `financial-unit-economics`                 | non-satisfying      | ROUTING | add satisfier or `research-thompson` (corpus lists    |
|     |                           |                    |          |                                            |   skills            |         |   it preferred)                                       |
| 11  | `jdm-pilot-one-car`       | jdm-import         | critic   | `financial-unit-economics`                 | non-satisfying      | ROUTING | add satisfier or `critic-munger` (corpus lists        |
|     |                           |                    |          |                                            |   skills            |         |   it preferred)                                       |
| 12  | `jdm-sales-channel`       | jdm-import         | research | *none*                                     | no skills at all    | ROUTING | add satisfier or `research-thompson` (corpus lists    |
|     |                           |                    |          |                                            |                     |         |   it preferred)                                       |
| 13  | `jdm-sourcing-workflow`   | jdm-import         | research | *none*                                     | no skills at all    | ROUTING | add satisfier or `research-thompson` (corpus lists    |
|     |                           |                    |          |                                            |                     |         |   it preferred)                                       |
| 14  | `jdm-sourcing-workflow`   | jdm-import         | critic   | *none*                                     | no skills at all    | ROUTING | add satisfier or `critic-munger` (corpus lists        |
|     |                           |                    |          |                                            |                     |         |   it preferred)                                       |
| 15  | `jdm-warranty-risk`       | jdm-import         | research | `financial-unit-economics`                 | non-satisfying      | ROUTING | add satisfier or `research-thompson` (corpus lists    |
|     |                           |                    |          |                                            |   skills            |         |   it preferred)                                       |
| 16  | `jdm-warranty-risk`       | jdm-import         | critic   | `financial-unit-economics`                 | non-satisfying      | ROUTING | add satisfier or `critic-munger` (corpus lists        |
|     |                           |                    |          |                                            |   skills            |         |   it preferred)                                       |
| 17  | `nas-architecture`        | networking-infra   | research | `premortem`                                | non-satisfying      | ROUTING | add satisfier or `research-thompson` (corpus lists    |
|     |                           |                    |          |                                            |   skills            |         |   it preferred)                                       |
| 18  | `net-bgp-flap`            | networking-infra   | research | *none*                                     | no skills at all    | ROUTING | add satisfier or `research-thompson` (corpus lists    |
|     |                           |                    |          |                                            |                     |         |   it preferred)                                       |
| 19  | `net-dns-migration`       | networking-infra   | critic   | *none*                                     | no skills at all    | ROUTING | add satisfier or `critic-munger` (corpus lists        |
|     |                           |                    |          |                                            |                     |         |   it preferred)                                       |
| 20  | `net-pppoe-capacity`      | networking-infra   | research | `deep-analysis`, `premortem`               | non-satisfying      | ROUTING | add satisfier or `research-thompson` (corpus lists    |
|     |                           |                    |          |                                            |   skills            |         |   it preferred)                                       |
| 21  | `repo-architecture-audit` | software-ai        | critic   | `deep-analysis`,                           | non-satisfying      | ROUTING | add satisfier or `critic-munger` (corpus lists        |
|     |                           |                    |          |   `security-audit`, `senior-qa`            |   skills            |         |   it preferred)                                       |
| 22  | `saas-pricing`            | business-research  | research | `pricing-strategy`,                        | non-satisfying      | ROUTING | add satisfier or `research-thompson` (corpus lists    |
|     |                           |                    |          |   `financial-unit-economics`               |   skills            |         |   it preferred)                                       |

## What actually fixes these

> **UPDATE 2026-09-01 — BOTH MECHANISMS BELOW WERE BUILT AND BOTH FAILED. Read this before acting on them.**
>
> The route invariant and the derived capability index were implemented exactly as recommended and measured as Baseline v3: **34/60, true routing delta zero**, with stage-2 "no selection" more than
> doubling. A three-way Flash / Pro / Claude holdout then showed `unsatisfied` at **7 / 6 / 7** — the defect is model-invariant, and ten of twenty holdout failures occur on both production models.
>
> **What still stands:** the classification itself — all 22 are routing defects, none are mapping defects — and the diagnosis that the router judges the gate then finishes without closing it. What is
> wrong is only the assumed remedy. **Prompt-level closure is the wrong mechanism; the replacement is deterministic closure** (the model proposes, a validator repairs). See
> [MEMORY.md](../../MEMORY.md).


The router is not confused about what the skills mean. It stops one step early: it judges the gate, then completes the route without closing the obligation. Two mechanisms follow from that, and
neither is a capability relabel.

1. **Make satisfaction a route invariant rather than an instruction.** The taxonomy document's §3.4 step 3 is currently advice; a true gate with no primary satisfier and no gate persona should be an
   invalid route the router is required to repair before returning it.
2. **Move the satisfier information to where selection happens.** `satisfied_by_skills` currently lives in the `[[gates]]` block, structurally distant from the skill list the router is scanning when
   it chooses. Capability metadata on the skill itself — the taxonomy refactor — puts the answer at the point of decision. That is the real argument for the refactor, and it is an argument about
   legibility, not about scoring.

## Falsifiable prediction — CONFIRMED 2026-09-01

Because zero of the 22 are mapping defects, **re-scoring the stored Baseline v2 plans under the new capability taxonomy should recover 0 cases.** Baseline v2 should stay at 33/60.

If the re-score moves the number at all, this classification is wrong somewhere and the moved case identifies exactly where. That makes step 6 of the sequence a test of this document rather than a
victory lap, which is the only reason to spend the effort on it before the router change.

**Outcome: 33/59 before, 33/59 after, no case changed verdict.** The prediction held and the classification stands.
