---
Title: skill-ai-it reference: Background: pattern inspiration and packaging task
Category: reference
Status: current
Authority: local-supplement
Scope: On-need reference moved verbatim from SKILL.md
Last reviewed: 2026-10-10
Summary: >-
  Background: pattern inspiration and packaging task; moved verbatim from SKILL.md so SKILL.md stays an orchestration file within budget.
---

# skill-ai-it reference: Background: pattern inspiration and packaging task

Moved verbatim from `SKILL.md` on 2026-10-10 to keep that file within its budget for files loaded whole.

## Public Pattern Inspiration

This skill intentionally borrows proven patterns from public AI-agent context tooling:

- `AGENTS.md` pattern: predictable repo-local agent instructions and bootstrap rules.
- Archcore pattern: Git-native project truth for decisions, rules, conventions, specs, and plans.
- Memory Bank pattern: Markdown-based active context, progress, decisions, patterns, and open questions.
- Graphify pattern: generated relationship/navigation graph for code, docs, diagrams, and mixed project content.
- Repomix pattern: deterministic AI-readable context pack to survive context compaction and reduce missed files.
- MCP pattern: expose external context/tools through standard agent-accessible interfaces where available.

These tools are optional integrations. The skill must still work with plain files only.

## Required Follow-Up Packaging Task

If this skill is being maintained as a reusable package, extract the embedded fallback templates into these files:

- `templates/AI_NAVIGATION.md`
- `templates/context-map.yaml`
- `templates/repomix.config.json`
- `templates/AGENTS-navigation-block.md`
- `templates/justfile`
- `templates/scripts-README.md`
- `templates/context_preflight.sh`
- `patterns/archcore-routing.md`
- `patterns/memory-bank-structure.md`
- `patterns/drift-audit.md`
- `patterns/script-task-audit-checklist.md`; `patterns/navigation/` (full routing tables and procedures behind the compact navigation block, one file per topic)
- `CHANGELOG.md` as the skill-package governance history ledger

After extraction, keep `SKILL.md` focused on orchestration logic and keep detailed reusable content in the template/pattern files.
