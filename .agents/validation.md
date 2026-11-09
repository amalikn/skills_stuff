Title: Skills Stuff Validation Notes
Category: validation-and-change-discipline-guide
Status: current
Authority: local-supplement
Scope: Repo-local validation boundaries for the skills_stuff source-of-truth repo
Source of truth: [validation.md](/Volumes/Data/_ai/_mcp/skills_stuff/.agents/validation.md)
Synced from: [validation-and-change-discipline-guide.md](/Volumes/Data/_ai/governance/categories/validation-and-change-discipline-guide.md)
Synced to: /Volumes/Data/_ai/governance/sync-map.yaml
Last reviewed: 2026-03-24
Summary: Repo-local validation boundaries for skills_stuff with explicit linkage to canonical validation governance.

# Validation

## Purpose
Document the current validation and consistency boundaries for the canonical specialist/source repo.

## Current Status
This repo clearly exposes canonical authoring under `specialists/` and client adapters under `exports/`, but no top-level README or single documented root validation command was found during rollout discovery.

Known structural anchors:
- canonical packs live under `specialists/`
- client adapters live under `exports/codex`, `exports/claude_code`, and `exports/local_llm`
- root revision tracking currently exists in `REVISION_HISTORY.md`

## Required Information
Still missing:
- authoritative root-level commands for validating, rendering, or syncing specialist/export changes
- a documented policy for when touching a specialist requires updating one or more export adapters
- a documented release or regeneration workflow for client adapter outputs

## Agent Behavior Until Defined
- Validate touched specialist and export paths for consistency by inspection before finalizing.
- Do not assume runtime-installed skills or exports outside this repo are authoritative.
- If a task appears to require rendering, syncing, or regenerating adapters and the command is not documented here, stop and ask the operator.
- Prefer narrow edits that preserve existing canonical-vs-delivery boundaries.

## Canonical Governance Linkage

- Cross-repo validation rules live under [`/Volumes/Data/_ai/governance/categories/validation-and-change-discipline-guide.md`](/Volumes/Data/_ai/governance/categories/validation-and-change-discipline-guide.md).
- The local governance index for this repo lives under [`/Volumes/Data/_ai/_mcp/skills_stuff/governance/README.md`](/Volumes/Data/_ai/_mcp/skills_stuff/governance/README.md).
- This file remains repo-local validation guidance and only reconciles reusable rules upward through explicit review.

## When to Prompt Operator
- Prompt when the correct source-of-truth is unclear.
- Prompt when a task touches both a specialist and multiple client adapters without an authoritative sync workflow.
- Prompt when a requested change implies generation or publication behavior that is not documented in this repo.
