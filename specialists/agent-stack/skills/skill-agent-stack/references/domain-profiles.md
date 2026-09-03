# Domain routing profiles

Read this when the task is in one of these domains. They are routing heuristics distilled from evaluation, not rules — the precedence table and gates still decide.

## Networking / infrastructure

- Network technical ownership sits with `cto-vogels`; `devops-hightower` owns operability, rollout and recovery.
- A migration, cutover or change with an expensive failure mode warrants independent challenge before commitment.
- Post-incident work splits: root-cause explanation of protocol or platform behaviour is architecture; the corrective action and runbook is operations. **This boundary is not yet in the precedence
  table** and was the cause of a known holdout failure (`hnet-radius-postmortem`) — expect ambiguity and state which reading you took.
- A code review inside a network domain is still a code review: artefact responsibility outranks domain context, so it goes to `fullstack-dhh`. The exception is security *posture* as the deliverable,
  which is architecture and CTO-owned even though the artefact is code.

## Physical-product / import decisions

- Evidence gathering, supplier discovery, regulation and compliance route to `research-thompson`; landed cost, margin, unit economics and a financially driven selection route to `cfo-campbell`.
- The discriminator is **the question asked, not the vocabulary used**. "Compare suppliers on product evidence, MOQ, landed cost, lead time and supply risk" is Research-owned — it asks what the
  evidence shows, and the financial terms are attributes being compared. "Given these suppliers, which maximises margin within our risk limits" is CFO-owned.
- Do not route on the presence of words like "landed cost". A keyword rule requiring `cfo-campbell` on exactly that match made all three models misroute `atar-supplier` until it was removed on
  2026-09-02.
- Current regulation, duty rates, compliance requirements and market data are external facts: `research_required` is true and the evidence must be acquired, not recalled.
