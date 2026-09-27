# Changelog — skill-project-coherence

## 2026-09-27 — the sweep could not see live data, sibling skills, or the page readers open first

Found while running this skill after the seventh staleness audit of unified-network-controller ("seven sites" → "nine sites", and a new one-writer rule for each site's DNS zone). A subagent run
against the previous SKILL.md answered "SKILL.md does not say" for four of the five gaps below, which is the failing test these edits answer.

- **Live system of record.** A Nautobot description restating a superseded fact sat outside every file the skill named. Tier 1 now has a row for systems of record: read back the free text of the
  objects the change touched, and fix it through the project's named writer.
- **Decisions outside the register.** The one-writer rule was recorded in `AGENTS.md` and a `.archcore/` rule, so no register-driven step carried it to ARCHITECTURE's "Key decisions". Tier 3 now has a
  reader-first-page row: every operator decision reaches it, wherever it was recorded.
- **Sibling skills.** skill-smc restated "seven sites" in five files and was found by chance: Tier 3 covered only skills inside the project, and the grep ran on `.`. Tier 3 now names every skill the
  project invokes, and Step 4 sweeps them with `--also`.
- **Parent-policy duties.** The missing wiki project page came from the parent `AGENTS.md`, which the skill said to read but not to act on. Mandatory Start now walks every `AGENTS.md` up to the
  workspace root for "update X when Y" duties, and the scope declaration lists the triggered ones.
- **History excluded by eye.** Step 4's grep dropped only `archive/`. New `scripts/stale_refs.py` classes every hit (active, history-path, history-dated, generated) and fails only on active ones;
  fixture tests in `scripts/tests/` were written first and failed before it existed.
- **Tool hazards.** The rewrap tool rebuilds `## Contents`; an unquoted heredoc executes backticks. Warning lines added; details in the markdown governance guide.
- **Refactor after the GREEN run.** A second subagent run against the edited SKILL.md followed every new step, and raised real ambiguities: Step 1 pointed at "Step 5" for the grep (it is Step 4); a
  dated report that already carries a supersession banner still counted as active. `stale_refs.py` gains a `history-superseded` class, matched on a banner line only, so a live plan that merely says it
  "supersedes" an older one stays `active` (both directions tested). Edge cases added for a system of record with no named writer, a duty that may or may not be triggered, and sibling-repo commits.
