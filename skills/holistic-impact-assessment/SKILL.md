---
name: holistic-impact-assessment
description: Use when the user asks for rename analysis, refactor impact, schema/change blast radius, touch-point discovery, or “which files need updating”. Force source-of-truth discovery, transform tracing, consumer mapping, scope separation, and contradiction checks before answering.
metadata:
  short-description: Holistic impact analysis
---

# Holistic Impact Assessment

## Use When
Use this skill for non-trivial impact analysis, especially renames, refactors, schema changes, dependency tracing, and “what needs updating” questions.

## Rules
- Define scope before concluding.
- Identify source-of-truth, transforms, direct consumers, and downstream surfaces.
- Separate direct edits, impacted consumers, generator/source implications, verified non-issues, and uncertainty.
- Reconcile static findings with runtime or rendered evidence where practical.
- Run a contradiction check before final answer.

## References
- references/PROFILE.md
- references/RUNBOOK.md
- references/KNOWN_ISSUES.md
- references/CHANGELOG.md
- references/CHECKLISTS/triage.md
- references/CHECKLISTS/change.md
- references/CHECKLISTS/healthcheck.md
- references/CONTEXT/boundaries.md
- references/CONTEXT/relationships.md
