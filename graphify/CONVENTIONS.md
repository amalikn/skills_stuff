Title: Graphify CONVENTIONS
Category: ai-governance
Status: current
Labels: graphify, skills_stuff, ai-files, governance
Last reviewed: 2026-04-28

# Conventions — Graphify Workspace

## Naming

| Thing | Pattern | Example |
|---|---|---|
| Time-bound docs | `<slug>-YYYYMMDD_hhmm.md` | `graphify-workspace-outcome-20260428_1945.md` |
| Governance entrypoints | Stable uppercase names | `README.md`, `AGENTS.md`, `CLAUDE.md`, `SCRATCHPAD.md` |
| Upstream source folder | `<project>-github` | `graphify-github/` |

## Code style

- Do not impose local style changes on `graphify-github/` unless the task explicitly targets upstream source edits.
- Keep local governance edits concise and operationally specific.

## Anti-patterns

- Mixing workspace governance notes inside upstream package files without explicit request.
- Replacing install-path facts with generic install instructions when concrete local paths are known.
- Treating runtime install location as canonical source-of-truth for authored governance.

## Doc conventions

- Keep install/runtime facts in a dedicated section (`Local install notes`) in [README.md](README.md).
- Keep SCRATCHPAD session summaries short (2–3 bullets) and move deep detail to memory backends.
- Preserve explicit parent governance pointers in all entrypoint docs.
