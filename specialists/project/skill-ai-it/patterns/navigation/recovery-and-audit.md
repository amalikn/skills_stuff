---
Title: Navigation reference: generated context, recovery, audit and answer contract
Category: reference
Status: current
Authority: skill-ai-it
Scope: Full text behind these sections of every project's compact AI_NAVIGATION.md managed block: Generated context, Context compaction recovery, Audit procedure, Agent answer contract
Last reviewed: 2026-10-10
Summary: Moved verbatim from templates/AI_NAVIGATION.md on 2026-10-10 (Graphify steps are obsolete: Graphify was disabled workspace-wide that day).
---

# Navigation reference: generated context, recovery, audit and answer contract

## Generated context

Generated files are useful but not authoritative by themselves.

| Generated file | Purpose |
|---|---|
| `graphify-out/GRAPH_REPORT.md` | Relationship/navigation overview |
| `graphify-out/graph.json` | Machine-readable graph |
| `.ai-context/governance-pack.md` | Deterministic context bundle |
| `.ai-context/repo-pack.md` | Larger project/repo context bundle |

Regenerate these after large documentation, architecture, or source changes.

## Context compaction recovery

After context compaction, rebuild agent context in this order:

1. **Read `AI_NAVIGATION.md`** first — this file is the navigation map.
2. **Load `.archcore/`** — durable project truth (ADRs, rules, specs, guides, plans).
3. **Regenerate `graphify-out/`**: `graphify update .`
4. **Regenerate `.ai-context/`**: `repomix --config repomix.config.json`
5. **Verify `SCRATCHPAD.md`** — if empty, populate from memory-keeper / mcp-project-context.
6. **Verify `CHANGELOG.md`** is current.
7. **Verify `AI_NAVIGATION.md` and `context-map.yaml` companion consistency.**

Label recovered entries: `Context recovered via skill-ai-it context-recovery procedure`.

## Audit procedure

To verify project context coherence, run these checks:

1. Confirm `AGENTS.md` points to `AI_NAVIGATION.md`.
2. Confirm `AI_NAVIGATION.md` points to `context-map.yaml`.
3. Confirm `CHANGELOG.md` exists and recent governance/navigation changes are recorded.
4. Confirm `context-map.yaml` has routing for architecture, planning, governance, implementation, documentation, and scripts.
5. Confirm `.archcore/` is either present and routed, or absent and treated as optional.
6. Confirm generated context paths (`graphify-out/`, `.ai-context/`) are excluded from source-of-truth decisions.
7. Confirm `SCRATCHPAD.md` is marked transient.
8. Confirm repeat-run managed blocks exist where needed.
9. Confirm companion files in `context-map.yaml update_rules` were updated when source files changed.
10. Confirm drift/conflict policy says stop-and-report.

## Agent answer contract

When answering from project context:

1. Prefer cited file paths.
2. Do not invent project state.
3. Say “not found in project context” if unsupported.
4. Distinguish confirmed facts from assumptions.
5. Ask only when required; otherwise proceed with stated assumptions.
