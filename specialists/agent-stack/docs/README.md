Title: Working documents index
Category: document-index
Status: current
Scope: Non-governance markdown produced by the work — audits, proposals, failure classifications and evaluation records
Last reviewed: 20260904_0735
Summary: Index of the project's working documents, grouped into subfolders by content once the flat list grew past a dozen files. Kept out of the root so the root carries only governance and contract
  entrypoints.

# Working documents

The project root carries **governance and contract entrypoints only** — `AGENTS.md`, `README.md`, `ARCHITECTURE.md`, `AI_NAVIGATION.md`, `CHANGELOG.md`, `MEMORY.md`, `SCRATCHPAD.md`,
`REVISION_NOTES.md`, `ROUTING_EVALS.md`, `RUNTIME.md` and `SKILL_STANDARD.md`. Everything else this work produces lives here.

These are **evidence and working artifacts, not policy.** Durable decisions live in [`.archcore/`](../.archcore/README.md), which is the highest authority; measured figures live in
[`MEMORY.md`](../MEMORY.md). A document here records what was found or proposed at a point in time and is not superseded by later work unless it says so.

## Contents

- [Audits](#audits)
- [Routing evaluation](#routing-evaluation)
- [Reliability adaptation](#reliability-adaptation)
- [Off-topic](#off-topic)

Reorganised 2026-09-04 from a single flat table into these four subfolders, once the flat list passed a dozen files and grouping by content became more useful than one long table. Coverage is enforced
recursively — a document added anywhere under `docs/` and not linked here fails the coverage check, the same guarantee the old flat layout gave.

## Audits

| Document                                                    | What it is                                                                        |
| ----------------------------------------------------------- | --------------------------------------------------------------------------------- |
| [audits/audit-agent-stack.md](audits/audit-agent-stack.md)  | The audit **prompt** — the brief, not a report. Never a duplicate of the report below |
| [audits/audit-agent-stack-full-20260901_1010.md](audits/audit-agent-stack-full-20260901_1010.md) | The full audit report it produced. Verdict: SOUND WITH MATERIAL GAPS              |
| [audits/audit-response-agent-stack-current-state-20260902.md](audits/audit-response-agent-stack-current-state-20260902.md) | Current-state response to the audit, 2026-09-02                                   |

## Routing evaluation

| Document                                                           | What it is                                                                                                      |
| ------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------- |
| [routing-evaluation/gate-definitions-proposal-20260901_1600.md](routing-evaluation/gate-definitions-proposal-20260901_1600.md) | The settled gate/capability policy, after two review rounds                                                     |
| [routing-evaluation/routing-failure-classification-20260901_1842.md](routing-evaluation/routing-failure-classification-20260901_1842.md) | Per-case classification of the v2 `unsatisfied` failures                                                        |
| [routing-evaluation/holdout24-analysis-20260902_1120.md](routing-evaluation/holdout24-analysis-20260902_1120.md) | Result analysis of the spent 24-case unseen holdout, Claude arm                                                 |
| [routing-evaluation/gate-only-analysis-20260903_0030.md](routing-evaluation/gate-only-analysis-20260903_0030.md) | A/B1/B2 result: isolated gate judgement works, the collapse costs routing nothing                               |
| [routing-evaluation/routing-failure-classification-20260903_1800.md](routing-evaluation/routing-failure-classification-20260903_1800.md) | All 27 production-shape failures classified: what "fix it all" can and cannot mean                              |
| [routing-evaluation/token-optimization-tools-and-strategy.md](routing-evaluation/token-optimization-tools-and-strategy.md) | Token-efficient context architecture guide; all 9 cited tools source-verified, one fabricated reference removed |

## Reliability adaptation

| Document                                                                                 | What it is                                                                                                |
| ---------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------- |
| [reliability-adaptation/external-orchestrator-survey-20260903_1849.md](reliability-adaptation/external-orchestrator-survey-20260903_1849.md) | Source-verified survey of 25 external repos; converges on a missing post-dispatch verification subsystem  |
| [reliability-adaptation/agent-stack-reliability-adaptation-proposal-20260903_1943.md](reliability-adaptation/agent-stack-reliability-adaptation-proposal-20260903_1943.md) | Phased, safety-preserving proposal for adapting the survey's reliability mechanisms                       |
| [reliability-adaptation/phased-implementation-and-self-verification-plan-20260904_1208.md](reliability-adaptation/phased-implementation-and-self-verification-plan-20260904_1208.md) | Per-phase implementation steps and self-verification checklists; inert until an operator triggers a phase |

## Off-topic

Filed here at operator request even though it does not bear on Agent Stack's own routing or safety model, kept in its own subfolder so it never blends in with genuine Agent Stack evidence.

| Document                                                   | What it is                                                                                 |
| ---------------------------------------------------------- | ------------------------------------------------------------------------------------------ |
| [off-topic/vertical-agent-framework-survey-20260903_2126.md](off-topic/vertical-agent-framework-survey-20260903_2126.md) | Fact-check of a separate proposed stack for building new vertical domain-specialist agents |

Add a document here and it must appear in this table — the coverage check fails until it does.
