---
Title: Goal Guard Hub, Management Baseline and Dates
Category: reference
Status: current
Authority: consolidated from the v1.7 handoff §22-29 (Enterprise-Strategy hub, management plan traceability, dual deadlines, migration)
Scope: Enterprise-Strategy hub and spokes, management-plan to Vikunja traceability, the four date kinds, Excel, and the Markdown-plan cutover gate
Last reviewed: 2026-10-27
Summary: >-
  Enterprise-Strategy stays the APN hub; spokes check its revision at handoff and material changes; management commitments are immutable baselines
  separate from the owner's internal target, the forecast and the evidenced actual; Excel is a dated snapshot; cutover from Markdown is gated.
---

# Hub, management baseline and dates

## Real names

Workspace paths and the shared `apn` repository are recorded once, in [project-layout-and-storage.md](project-layout-and-storage.md) (Workspace facts).

## Hub and spokes (handoff §22)

- Enterprise-Strategy owns strategic direction, approved shared interfaces and cross-project decisions; it is not folded into Goal Guard. Spokes own implementation, local specs, MVP evidence and ADRs.
- Register hub/spoke relations explicitly (stable project IDs, real roots, document references); never by auto-discovery alone.
- **At session start, resume and handoff:** read the relevant approved hub decisions, compare revision (commit, ref or checksum) with the spoke's acknowledged one, record a read receipt (project, hub
  ref, revision, time, decision IDs). Do not copy hub content into spokes.
- **Recheck** only at material boundaries: shared interface, device-identity schema, inter-project dependency, rollout assumption, external deadline.
- **Cross-project proposal:** candidate decision with source, impacted projects, evidence, proposed change, milestones, requester → REVIEW at the hub; never mutate the hub or another spoke.
- **Hub unavailable:** cached, version-pinned decisions may support already-approved non-cross-project work; shared-contract changes are REVIEW/BLOCK; never claim the latest revision was checked.
- AI-inferred dependencies are candidates with cited passages until corroborated or approved; no Vikunja blocker is created from inference (H05).

## Management plan traceability (handoff §23)

The plan files, the issued workbook, its columns and its approval route **have not been inspected**; discover them first. If management treats Excel as the editable authority, establish one sanctioned
update path rather than assuming Markdown wins.

Minimal link per milestone (conceptual):

```yaml
plan_baseline: {hub_project: enterprise-strategy, document_ref: <path>, revision: <commit or version>, approved_by: <ref>, management_export_ref: <file/version/hash>}
milestone_link: {milestone_id: <stable ID>, milestone_revision: <rev>, delivery_project_id: unified-network-controller, vikunja_project_id: <id>,
                 vikunja_task_ids: [<id>], goalguard_mvp_id: <id>, mapping_status: proposed}   # proposed | verified | superseded
```

Milestone progress needs the milestone's own acceptance evidence, not task closure counts. Discrepancies (dates, missing tasks, unlinked deliverables, completed tasks without evidence) produce
reconciliation records, never silent overwrites. Status reports are keyed to the published baseline and new exports are new versions.

## Four kinds of date (handoff §25-26)

| Kind                    | Owner                                                    | Mutable?                                              |
| ----------------------- | -------------------------------------------------------- | ----------------------------------------------------- |
| Management commitment   | Approved baseline (hub)                                  | Only by a new approved revision (DATE-001)            |
| Owner's internal target | Goal Guard metadata                                       | Owner-editable; may precede the commitment (DATE-002) |
| Forecast                | Goal Guard, with assumptions, evidence time and `unknown` | Recalculated on evidence; never invented (DATE-003)   |
| Actual completion       | Vikunja status plus acceptance evidence and timestamp    | Audited corrections only (DATE-007)                   |

Alerts are distinct: internal-target breach, management deadline at risk, missed commitment (DATE-005). Example (illustrative): commitment 2026-12-15, internal target 2026-12-01; a forecast of
2026-12-05 breaches the internal target only; 2026-12-18 puts the commitment at risk. Reports default to commitment, status, forecast, risk and evidence; private internal targets are not published
unless asked (DATE-006). Dates are compared with explicit timezone or date-only semantics (DATE-008).

## Excel

The issued workbook is a historical snapshot (date, audience, hash, baseline revision). A generated export is labelled with generation time and baseline revision and compared to the original before
any claim of reproduction (handoff §25.1 step 5, D09).

## Markdown-plan cutover gate (handoff §25.1)

Discover and hash the plan and workbook → extract one milestone and reconcile with Excel → link to Vikunja idempotently → register the protected baseline → export and compare → owner sign-off → only
then stop operational scheduling edits in Markdown (strategy and rationale stay there). Every record carries `authority_state` (`legacy_draft | published_baseline | vikunja_operational`) and
`migration_status` (`proposed | reconciled | cutover | rolled_back`). Rollback: stop writes, restore mappings and the source-of-truth flag, keep the audit trail.
