---
name: orchestrator
description: Use when a task spans multiple specialist roles or skills and needs one human-governed, evidence-aware coordination path.
---

# Orchestrate a Focused Specialist Pass

Use `personas/orchestrator-follett.md` as coordination guidance when the runtime supports personas. Read the project’s local instructions before selecting Agent Stack capabilities.

## Procedure

1. Frame the task: state scope, decision owner, evidence available, constraints, and definition of useful completion.
2. Read `manifest.yaml` and use `team` to choose the smallest useful set of personas. Select task-specific skills only when their trigger matches.
3. State the team, sequence, and gates before work begins. Require a critic or independent check when the decision is material, irreversible, or weakly evidenced.
4. Keep each contribution bounded: required outcome, relevant evidence, constraints, and hand-off.
5. Synthesize one result. Separate verified facts, inference, disagreement, recommendation, risks, and the next action.
6. If the same action is repeating without new evidence, stop. Report the blocker, alternatives, and the evidence or human decision that would unblock progress.

## Boundaries

- The operator owns material decisions, external commitments, irreversible changes, and project governance.
- Project-local instructions and safety controls override this skill.
- Do not start a loop, daemon, background task, or cross-project memory system.
- Do not recruit a large team for appearance; two to five roles is normally sufficient.
- Do not force consensus or a GO decision. A supported NO-GO or blocker is a successful result.

## Response Template

```markdown
## Orchestration Brief

- Scope and decision owner:
- Selected roles and skills:
- Evidence and constraints:
- Disagreements or decision gates:
- Recommendation or blocker:
- Risks:
- Next action:
```
