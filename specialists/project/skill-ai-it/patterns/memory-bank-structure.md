# Memory Bank Structure Pattern

Use `memory-bank/` for current working memory and progress, not permanent architecture truth.

## Files

| File | Purpose |
|---|---|
| `memory-bank/activeContext.md` | Current working context and immediate focus |
| `memory-bank/progress.md` | Current status, completed work, next actions |
| `memory-bank/decisionLog.md` | Working decisions before promotion |
| `memory-bank/systemPatterns.md` | Stable patterns and conventions |
| `memory-bank/openQuestions.md` | Questions blocking progress |

## Rules

- Keep entries concise and current.
- Promote durable decisions into Archcore/ADR/rules/specs/plans.
- Do not use memory-bank as a replacement for `AI_NAVIGATION.md`.
- On repeat runs, create only missing files and never overwrite existing memory-bank content.
