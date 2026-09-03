Title: Working documents index
Category: document-index
Status: current
Scope: Non-governance markdown produced by the work — audits, proposals, failure classifications and evaluation records
Last reviewed: 20260902_1130
Summary: Index of the project's working documents, kept out of the root so the root carries only governance and contract entrypoints.

# Working documents

The project root carries **governance and contract entrypoints only** — `AGENTS.md`, `README.md`, `ARCHITECTURE.md`, `AI_NAVIGATION.md`, `CHANGELOG.md`, `MEMORY.md`, `SCRATCHPAD.md`,
`REVISION_NOTES.md`, `ROUTING_EVALS.md`, `RUNTIME.md`, `SKILL_STANDARD.md` and `translation-policy.md`. Everything else this work produces lives here.

These are **evidence and working artifacts, not policy.** Durable decisions live in [`.archcore/`](../.archcore/README.md), which is the highest authority; measured figures live in
[`MEMORY.md`](../MEMORY.md). A document here records what was found or proposed at a point in time and is not superseded by later work unless it says so.

| Document                                             | What it is                                                                         |
| ---------------------------------------------------- | ---------------------------------------------------------------------------------- |
| [audit-agent-stack.md](audit-agent-stack.md)                                 | The audit **prompt** — the brief, not a report. Never a duplicate of the report below  |
| [audit-agent-stack-full-20260901_1010.md](audit-agent-stack-full-20260901_1010.md)              | The full audit report it produced. Verdict: SOUND WITH MATERIAL GAPS               |
| [audit-response-agent-stack-current-state-20260902.md](audit-response-agent-stack-current-state-20260902.md) | Current-state response to the audit, 2026-09-02                                    |
| [gate-definitions-proposal-20260901_1600.md](gate-definitions-proposal-20260901_1600.md)           | The settled gate/capability policy, after two review rounds                        |
| [routing-failure-classification-20260901_1842.md](routing-failure-classification-20260901_1842.md)      | Per-case classification of the v2 `unsatisfied` failures                           |
| [holdout24-analysis-20260902_1120.md](holdout24-analysis-20260902_1120.md)                  | Result analysis of the spent 24-case unseen holdout, Claude arm                    |
| [gate-only-analysis-20260903_0030.md](gate-only-analysis-20260903_0030.md)                  | A/B1/B2 result: isolated gate judgement works, the collapse costs routing nothing  |
| [routing-failure-classification-20260903_1800.md](routing-failure-classification-20260903_1800.md)      | All 27 production-shape failures classified: what "fix it all" can and cannot mean |

Add a document here and it must appear in this table — the coverage check fails until it does.
