---
Title: skill-ai-it reference: Conditional file: AI_NAVIGATION.md
Category: reference
Status: current
Authority: local-supplement
Scope: On-need reference moved verbatim from SKILL.md
Last reviewed: 2026-10-14
Summary: >-
  Conditional file: AI_NAVIGATION.md; moved verbatim from SKILL.md so SKILL.md stays an orchestration file within budget.
---

# skill-ai-it reference: Conditional file: AI_NAVIGATION.md

Moved verbatim from `SKILL.md` on 2026-10-10 to keep that file within its budget for files loaded whole.

## Contents

- [AI_NAVIGATION.md — create when: missing during `navigation-add`, requested explicitly, or project has more than one governance/context source](#ai_navigationmd--create-when-missing-during-navigation-add-requested-explicitly-or-project-has-more-than-one-governancecontext-source)

#### AI_NAVIGATION.md — create when: missing during `navigation-add`, requested explicitly, or project has more than one governance/context source

From `templates/AI_NAVIGATION.md`: fill `{{PROJECT_NAME}}` and set the front matter's `Last reviewed` to the bootstrap date. The front matter is outside the managed
block and gives the file the header summary `doc_freshness.py` requires; without it a new project's first commit fails on it (smc-resiliency, 2026-10-14).

Create as the human-readable context router. If it exists, preserve custom content and update only the managed routing sections.

Preferred source template: `templates/AI_NAVIGATION.md`.

The template is the only source. An embedded copy used to sit here; it had drifted to the older long form (no front matter, 200 lines
against the template's compact 60), which is the drift `AGENTS.md` forbids, so it was removed on 2026-10-14. AI_NAVIGATION.md is read first in
every session: it routes to files and summarises a rule in at most one line with its owner named; the rule itself lives in AGENTS.md.
