---
Title: skill-ai-it reference: context compaction recovery
Category: reference
Status: current
Authority: local-supplement
Scope: On-need reference moved verbatim from SKILL.md
Last reviewed: 2026-10-10
Summary: >-
  Context compaction recovery; moved verbatim from SKILL.md so SKILL.md stays within budget.
---

# skill-ai-it reference: context compaction recovery

Moved verbatim from `SKILL.md` on 2026-10-10 to keep that file within its budget for files loaded whole.

## Context Compaction Recovery

When recovering agent context after compaction (e.g. new session, context window cleared), follow this procedure:

1. **Read `AI_NAVIGATION.md`** first — the navigation map tells you what files exist and what to read.
2. **Read `context-map.yaml`** for machine-readable file registry and companion-file rules.
3. **Load `.archcore/`** context if present (durable project truth).
4. **Skip `graphify-out/`**: Graphify is disabled (operator, 2026-10-10); do not regenerate it.
5. **Regenerate `.ai-context/`**: `repomix --config repomix.config.json`
6. **Verify `SCRATCHPAD.md`** has current state. If empty, populate from memory backends.
7. **Verify `CHANGELOG.md`** is current with recent governance/navigation changes.
8. **Verify `AI_NAVIGATION.md` and `context-map.yaml` companion consistency.**

Label recovered entries: `Context recovered via skill-ai-it context-recovery procedure`.
