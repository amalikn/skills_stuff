Title: Skills Stuff Repo Skills
Category: misc-governance-guide
Status: current
Authority: local-supplement
Scope: Repo-local workflow patterns for the skills_stuff source-of-truth repo
Source of truth: [skills.md](/Volumes/Data/_ai/_mcp/skills_stuff/skills.md)
Synced from: [skills.md](/Volumes/Data/_ai/governance/skills.md)
Synced to: /Volumes/Data/_ai/governance/sync-map.yaml
Last reviewed: 2026-03-24
Summary: Repo-local task patterns for skills_stuff with explicit linkage to canonical governance.

# skills.md

This repo commonly involves:
- authoring specialist packs under `specialists/`
- maintaining client export adapters under `exports/codex`, `exports/claude_code`, and `exports/local_llm`
- keeping canonical source-of-truth boundaries clear between authoring content and delivery adapters
- updating repo-level revision history when canonical packs change

Use this workflow:
- decide whether the task is canonical-authoring, export-adapter, or both
- edit `specialists/` first when the change affects reusable knowledge or workflow content
- update only the touched export adapter when the change is client-specific
- use [`.agents/validation.md`](/Volumes/Data/_ai/_mcp/skills_stuff/.agents/validation.md) to decide whether manual consistency checks are enough or whether you need operator direction

Prompt the operator when:
- it is unclear whether a change belongs in `specialists/`, `exports/`, or both
- a requested change would alter canonical-vs-delivery boundaries
- adapter regeneration or synchronization is expected but not authoritatively documented in this repo

## Canonical Governance Linkage

- Cross-repo reusable workflow and governance rules live under [`/Volumes/Data/_ai/governance/README.md`](/Volumes/Data/_ai/governance/README.md).
- Repo-local governance routing for this workspace is indexed in [`/Volumes/Data/_ai/_mcp/skills_stuff/governance/README.md`](/Volumes/Data/_ai/_mcp/skills_stuff/governance/README.md).
- These task patterns remain local to `skills_stuff` and do not replace the canonical governance stack.
