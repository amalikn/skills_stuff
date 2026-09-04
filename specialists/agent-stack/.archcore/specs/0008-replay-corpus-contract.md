Title: Spec 0008 — Replay corpus contract
Category: design-contract
Status: accepted
Proposed: 20260903_0130 direct, per .archcore/README.md step 2
Accepted: 20260904_1150 by operator
Source: docs/routing-evaluation/gate-only-analysis-20260903_0030.md, .archcore/plans/0001-next-evaluation-phase.md
Summary: Replay cases are labelled from what the work actually produced, never from what a router would say. Ownership is the target; artifacts are the ground truth.

# Spec 0008 — Replay corpus contract

## What replay is for

Ownership is the leading open routing defect. All three holdout 24 failures were ownership, and B1 and B2 each carry ~10 `missing required persona` failures that gate correctness does not touch. The
spent 24 cannot be reused, and authoring more blind cases produces more of the author's judgement rather than more evidence.

Replay is different in kind: the tasks **already happened**, and they left artifacts. That makes a ground truth available that no authored corpus has.

## The circularity trap, and the rule that avoids it

**A replay case labelled from an opinion about who should have owned it is not evidence — it is the author's routing judgement in a costume.** Running the router against it measures agreement between
two guesses, and it will look like a result.

**Rule: every assertion in a replay case cites an artifact that exists.** Not a memory, not a reconstruction, not "this is obviously a CFO task". If a label cannot be traced to something the work
produced, the case does not carry that assertion at all. A case with two evidenced assertions and three omissions is worth more than a case with five confident guesses, and the scorer already treats
an absent assertion as no constraint.

## What counts as evidence

| Assertion                   | Evidenced by                                                                                                                          | NOT evidenced by               |
| --------------------------- | ------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------ |
| `research_required = true`  | The work consulted a source outside the repo — a fetched page, vendor documentation, a regulation, a figure with a cited              | The topic sounding external    |
|                             |   external origin                                                                                                                     |                                |
| `research_required = false` | Every input was present in the task or the repo at the time                                                                           | Nobody having happened to look |
|                             |                                                                                                                                       |   anything up                  |
| `critic_required = true`    | The decision proved irreversible or high-consequence **as it played out**: money committed, a cutover executed, a contract signed     | The task sounding weighty      |
| `qa_required = true`        | Code, config or a release was actually validated — or shipped and then found defective                                                | Code merely being present      |
| `runtime_required`          | Computed, never asserted. A tool-class skill was genuinely executed                                                                   | —                              |
| `primary_owner`             | The **discipline of the artifact that was produced** — a landed-cost model is financial analysis, a fabric design is architecture, a  | Who happened to be in the room |
|                             |   runbook is operations                                                                                                               |                                |
| `required_skills`           | A catalogued procedure that was actually followed                                                                                     | A skill that would have helped |

## Ownership is labelled from the artifact, not the topic

This is where the corpus earns its keep, and where the precedence rules that failed in holdout 24 are under test:

- `hnet-radius-postmortem` failed because the table has no rule for **incident root-cause versus operational corrective action**. Replay can settle it: look at what the post-incident work actually
  produced. A config change and a runbook edit is operations; an explanation of protocol behaviour is architecture.
- `hnet-firewall-consolidation` failed because `artefact-vs-domain-review` reads both ways when the artifact **is** policy. Real consolidations can settle that too.

**Do not resolve either from this spec.** Resolve them from cases, and only where several independent cases agree.

## Corpus rules

- **Minimum two independent tasks per ownership boundary under test.** One case is an anecdote and cannot move a precedence rule.
- **Every case carries a `provenance` field naming its evidence** — repo path, commit, document, or memory key with a date. A case whose provenance cannot be followed is retired, not repaired.
- **Replay is re-runnable, not single-use**, because the tasks are already known to this project. It is therefore **not** a substitute for Holdout 2, and a good replay score is not generalisation
  evidence.

## What a replay result licenses

- **Changing a precedence rule**, where two or more independently evidenced cases agree against it — and only confirmed afterwards on Holdout 2.
- **Nothing about gates.** Gate behaviour is settled for now by [the A/B1/B2 result](../../docs/routing-evaluation/gate-only-analysis-20260903_0030.md). Replay must not reopen it; its gate assertions
  exist only so ownership is scored inside a realistic route rather than a stripped one.
