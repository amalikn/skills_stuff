---
title: Reference Update Discipline
type: rule
status: accepted
provenance: promoted from AGENTS.md on 20260626
---

# Rule: Reference Update Discipline

After editing any `references/` file, verify consistency with the index layer in the same pass:

- Check `SKILL.md` References section — description must match file content
- Check `RUNBOOK.md` routing table — task-to-file mapping must still be accurate

After **adding** a new reference file, update all six surfaces in the same commit/session:

1. `RUNBOOK.md` routing table — add row for new file
2. `SKILL.md` References section — add bullet for new file
3. `exports/claude_code/project/skill-smc/adapter.md` — add row to source→install mapping
4. `exports/claude_code/project/skill-smc/install.md` — add file to copy step
5. `AI_NAVIGATION.md` reference routing table and Project context files table — add row for new file
6. `context-map.yaml` routing section — add a routing entry for the new domain

**Rationale:** The routing index (RUNBOOK.md), skill entrypoint (SKILL.md), client adapter docs, and the two pack-maintenance routers (AI_NAVIGATION.md, context-map.yaml) all restate the same
task-to-file mapping in different formats. Updating one without the others causes navigation failures and install drift. This list was widened from four to six surfaces on 2026-09-08 after an audit
found AI_NAVIGATION.md and context-map.yaml were never in scope for this rule even though the pack's own `AGENTS.md` Tier 2 checklist already expected them to be kept current.
