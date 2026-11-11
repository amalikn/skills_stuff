---
title: Archcore index — skill-ai-it
status: accepted
tags: [index]
---

The pack's working rules, one small file each, so an agent opens only the rule it needs (operator, 2026-11-11; the same layout skill-ai-it's
[archcore pattern](../patterns/archcore-routing.md) gives projects). [AGENTS.md](../AGENTS.md) keeps one line per rule pointing here. A new rule
gets its own file, a row below, and a line in AGENTS.md.

## rules/

| Rule | What it says |
| --- | --- |
| [templates-are-the-source.rule.md](rules/templates-are-the-source.rule.md) | Templates are the source; SKILL.md fallbacks follow them |
| [layout-changes-carry-companions.rule.md](rules/layout-changes-carry-companions.rule.md) | A layout or routing change updates its companions in the same pass |
| [repeat-safe-writes.rule.md](rules/repeat-safe-writes.rule.md) | Every write into a project is repeat-safe |
| [catalogued-tasks-only.rule.md](rules/catalogued-tasks-only.rule.md) | Run catalogued tasks only; a new script is catalogued |
| [code-follows-skill-coder.rule.md](rules/code-follows-skill-coder.rule.md) | Code follows skill-coder: code map, ruff on new files, tests |
| [history-by-kind.rule.md](rules/history-by-kind.rule.md) | docs/history is one folder per kind with a generated index |
| [ask-about-pad-at-bootstrap.rule.md](rules/ask-about-pad-at-bootstrap.rule.md) | Bootstrap and refresh ask whether to link a Pad workspace |
| [tool-agnostic-and-generic.rule.md](rules/tool-agnostic-and-generic.rule.md) | The pack stays tool-agnostic, generic and free of project output |
