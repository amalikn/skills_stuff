---
title: "Archcore index — skill-goal-guard"
type: guide
status: accepted
tags: [governance, procedure]
created: 2026-10-27
---

# Archcore index — skill-goal-guard

Promoted on 2026-10-27 by `/skill-ai-it promote` from `ARCHCORE_PROMOTION_CANDIDATES.md` (now deleted); the operator approved all candidates ("promote and approve all").
Every document here is a **pointer document**: it states the decision, rule, contract, procedure or plan and links to the section that stays canonical, so
`references/` remains where this pack's rules change (as skill-smc and skill-nautobot keep their domain knowledge in `references/`). Where a document here and
AGENTS.md prose differ, the document wins; where it differs from its canonical section, fix the document.

An accepted document is not immutable: amend it in place with a dated note naming what changed and what still stands, rather than deleting it.

## Decisions

| Document | Canonical source |
| --- | --- |
| [The hook ships as a draft with file-scoped verdicts](adr/hook-draft-file-scoped-verdicts.adr.md) | `references/enforcement-and-hooks.md`, "Learned" |
| [The prose name is Goal Guard](adr/name-goal-guard.adr.md) | `AGENTS.md`, "Working rules" |
| [D1: one apn repository, scoped by path](adr/one-apn-repository.adr.md) | `references/project-layout-and-storage.md`, "Shared repository" |
| [Pilot decisions D2-D6](adr/pilot-decisions-d2-d6.adr.md) | `references/pilot-plan.md`, "Owner decisions (answered 2026-10-27)" |
| [Settled conflicts between the source documents](adr/settled-source-conflicts.adr.md) | `references/decision-rules.md`, "Settled conflicts" |
| [Vikunja owns live tasks; Goal Guard owns scope](adr/vikunja-owns-live-tasks.adr.md) | `references/vikunja-integration.md`, "Position" |

## Rules

| Document | Canonical source |
| --- | --- |
| [Front matter, a blank line after it, and a catalog row](rules/front-matter-and-catalog.rule.md) | `AGENTS.md`, "Working rules" |
| [No secrets in pack files](rules/no-secrets-in-pack.rule.md) | `AGENTS.md`, "Working rules" |
| [Only the owner approves scope](rules/owner-alone-approves-scope.rule.md) | `SKILL.md`, "Standing rules" |
| [references/ is where rules change; docs/ stays verbatim](rules/references-canonical-docs-verbatim.rule.md) | `AGENTS.md`, "Working rules" |
| [Standing rules: commitments, partitions, enforcement claims, estimates](rules/standing-rules.rule.md) | `SKILL.md`, "Standing rules" |
| [Behaviour claims stay UNVERIFIED until observed](rules/unverified-until-observed.rule.md) | `AGENTS.md`, "Working rules" |

## Contracts

| Document | Canonical source |
| --- | --- |
| [Proposal, verdict and decision-log records](specs/decision-records.spec.md) | `references/decision-rules.md`, "Record formats" |
| [Front-end exit codes](specs/front-end-exit-codes.spec.md) | `scripts/readme.md`, "Exit codes and settings" |
| [The MVP contract](specs/mvp-contract.spec.md) | `references/mvp-contract-and-change-control.md`, "Contract fields (conceptual schema)" |
| [Snapshot and manifests](specs/snapshot-format.spec.md) | `references/snapshot-and-restore.md`, "Snapshot" |

## Procedures

| Document | Canonical source |
| --- | --- |
| [Workflow at a handoff](guides/handoff-workflow.guide.md) | `SKILL.md`, "Workflow at a handoff" |
| [Live checks before trusting results](guides/live-checks-before-trust.guide.md) | `scripts/readme.md`, "Open checks before trusting live results" |

## Plans

| Document | Canonical source |
| --- | --- |
| [The v1.7 pilot](plans/v1-7-pilot.plan.md) | `references/pilot-plan.md`, "Steps" |

## Not promoted, and why

- The skill-coder code rule: inherited from the parent skills_stuff AGENTS.md; governed there.
- Roadmap phases L1-L5: speculative until the pilot report.
- The readme quick start: too short to be a guide; it stays in the readme.
- `changelog.md`, the generated flow map and drawing, unmarked SCRATCHPAD notes, open proposals (shell-write coverage, the owner approval path) and the
  verbatim sources under `docs/`.

## Proposing another

Run `/skill-ai-it refresh` to surface candidates into `ARCHCORE_PROMOTION_CANDIDATES.md`, then `/skill-ai-it promote` once the operator authorizes them.
