---
title: Reference Update Discipline
type: rule
status: proposed
provenance: promoted from AGENTS.md on 20260626
---

# Rule: Reference Update Discipline

After editing any `references/` file, verify consistency with the index layer in the same pass:

- Check `SKILL.md` References section — description must match file content
- Check `RUNBOOK.md` routing table — task-to-file mapping must still be accurate

After **adding** a new reference file, update all four surfaces in the same commit/session:

1. `RUNBOOK.md` routing table — add row for new file
2. `SKILL.md` References section — add bullet for new file
3. `exports/claude_code/project/skill-smc/adapter.md` — add row to source→install mapping
4. `exports/claude_code/project/skill-smc/install.md` — add file to copy step

**Rationale:** The routing index (RUNBOOK.md), skill entrypoint (SKILL.md), and client adapter docs are interdependent. Updating one without the others causes navigation failures and install drift.
