---
Title: GoalGuard MVP Contract and Change Control
Category: reference
Status: current
Authority: consolidated from the v1.7 handoff §1-2, §5-6, §8, §10, research pack 01 M0, 05 B-01 and 06 (task template)
Scope: The MVP contract fields, planning exit, approval, revisions, deferred ideas and the completion gate
Last reviewed: 2026-10-27
Summary: >-
  An implementation handoff needs an owner-approved MVP contract with testable criteria and exclusions; changes create a new revision through an
  explicit request and owner decision; ideas are parked, and delivery needs evidence for every criterion.
---

# MVP contract and change control

## Intent

Stop projects idling in planning and stop coding agents enlarging approved MVPs. Success is a small, working, tested deliverable, not a complete plan (handoff §1). Brainstorming (ChatGPT or otherwise)
stays unrestricted; governance starts at the implementation handoff (handoff §2).

## Contract fields (conceptual schema)

From handoff §5, plus the explicit NOT-in-scope and stop condition adopted from Thekedar's task template (pack 06):

```yaml
mvp_id: UNC-MVP-001
baseline_version: 1
status: draft            # draft | approved | delivered | superseded
owner: <human owner>
problem: <the user problem>
outcome: <one observable, independently demonstrable outcome>
deliverable: <smallest working artefact>
acceptance_criteria:
  - id: AC-01
    test: <observable pass/fail condition>
    evidence_required: <test output, log, demonstration reference>
exclusions: [<feature consciously deferred>]
necessary_blockers: [<dependency already judged necessary, with the criterion it unblocks>]
constraints: [<binding Archcore or operational constraint, by reference>]
planning_exit: {result: commit, unresolved_blockers: []}   # commit | defer | blocked
approval: {actor: <owner>, evidence_ref: <auditable reference>, approved_at: <ISO-8601>}
links: {management_milestone_id: null, target_map_ref: null, vikunja_project_id: null}
```

Use the project's existing format if one fits; the schema file (`schemas/mvp.schema.json`) is pilot work, not yet written. Reject subjective criteria ("enterprise ready", "scalable", "bulletproof").
An exclusion cannot be overridden by a task title, a planning note or agent inference. Ad-hoc work uses a compact contract: outcome, reason, next action, urgency, stop condition, optional deadline
(pack 01 M0); no Git or file list is required (GG-408).

## Planning exit

Before handoff, planning ends in exactly one of: **commit** (smallest verifiable MVP, owner-approved), **defer** (status preserved), or **blocked** (named dependency or owner question). No
planning-hour limit (handoff §6 Stage B, MVP-010).

## Change control

An agent asking for a change supplies: baseline ID and criterion affected; why the current deliverable is impossible, unsafe or invalid; evidence and the smallest change; alternatives that keep scope;
impact on deadline, tests, dependencies, exclusions; an explicit request to the owner (handoff §8). Only an authenticated owner decision naming the exact proposal creates a new revision;
conversational assent to another subject is not approval. Denied and deferred proposals are recorded too. Verification (decision D3): the approval commit must carry a valid signature from a key listed in an owner-held allowed-signers file (`git verify-commit`, with `gpg.ssh.allowedSignersFile` for SSH keys); exact setup and the agent-usable-key risk are settled before pilot step 5 ([pilot-plan.md](pilot-plan.md), D3 risk). Revisions never overwrite history (MVP-011).

Hub-affecting changes go to Enterprise-Strategy instead ([hub-management-and-dates.md](hub-management-and-dates.md)).

## Deferred ideas

`deferred.yaml` per project: title, source reference (a link, not a copied conversation), why it may be valuable, why it is not needed now, optional future milestone (handoff §10). A parked idea never
becomes a Vikunja task without explicit promotion.

## Completion gate

Delivered only when every applicable criterion has linked passing evidence, no blocking REVIEW is open and any required sign-off is captured. CI passing without the observable outcome is not enough;
task counts are not milestone acceptance (handoff §6 Stage E, MVP-009, DATE-007, H09, D08). A completion record lists what changed, what was deliberately not changed and the evidence per criterion
(pack 06, changelog-entry pattern).
