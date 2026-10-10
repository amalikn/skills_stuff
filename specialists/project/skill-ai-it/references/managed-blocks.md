---
Title: skill-ai-it reference: Managed block pattern
Category: reference
Status: current
Authority: local-supplement
Scope: On-need reference moved verbatim from SKILL.md
Last reviewed: 2026-10-10
Summary: >-
  Managed block pattern; moved verbatim from SKILL.md so SKILL.md stays an orchestration file within budget.
---

# skill-ai-it reference: Managed block pattern

Moved verbatim from `SKILL.md` on 2026-10-10 to keep that file within its budget for files loaded whole.

### Managed block pattern

When adding repeat-refreshable content into existing files, wrap it with comments using the standard format:

```markdown
<!-- BEGIN MANAGED: skill-ai-it:<section-name> -->
<!-- skill-ai-it-version: 2026-10-10-compact-v1 -->
...managed content...
<!-- END MANAGED: skill-ai-it:<section-name> -->
```

- `<section-name>` describes the managed section (e.g. `navigation`, `scripts`).

#### The upgrader will not overwrite project-authored content

Two guards, added 2026-08-12 after a dry run against a real project would have removed **222 lines** from its `AI_NAVIGATION.md` — every supersession chain, every gate reference and the whole
domain-routing table — reporting only `replaced-old-block`, which reads like a successful migration.

1. **Provenance.** A block this skill wrote carries a `skill-ai-it-version:` line. A block **without** one was either never written by the skill or has been hand-edited since, so the upgrader
   **refuses to replace it**, writes the generic block to `<file>.proposed-<section>-block`, and flags the run for manual review. Note the original bug was worse than "replaces managed blocks": the
   old-style-marker branch is tested **first** and matches preferentially, so legacy markers were the *most* exposed, not the least.

2. **Explicit opt-out.** A project that has deliberately taken ownership declares it inside the block:

   ```markdown
   <!-- BEGIN skill-ai-it:navigation -->
   <!-- skill-ai-it:manual reason="project-authored routing rules" -->
   ```

The upgrader then never touches that block — including **never inserting** the section if it is absent, because a file that declares itself project-managed and omits a section has decided it does not
want it. The validator reports it as a pass, not a missing-block failure. `--force` overrides both guards and **discards** the current contents; it exists for the case where you have read the
`.proposed` file and decided against your own content.

3. **Layout (added 2026-10-07).** A block stamped before `2026-09-23` (`LAYOUT_SINCE`) comes from the layout in which projects wrote their own content inside the block: the whole scripts README with
   its task catalogue, project rules in the navigation and agents blocks. A stamp alone did not protect it: the first `nav_upgrade` run after the snake_case bump removed 171 catalogue lines from
   cambium-swap and 113 rules from unified-network-controller before the diff review caught it. The upgrader now refuses these blocks (`refused-legacy-layout`, exit 3) and points at `/skill-ai-it
   refresh`. There `just nav_migrate_legacy <project> --dry-run` (`scripts/migrate_legacy_blocks.py`) classifies every section of the old
   block against every block the skill emitted in that era and today: skill text is replaced, project sections move outside the block, and a skill section the
   project edited is copied verbatim under `## Moved from the managed block` for trimming by hand. Then `nav_upgrade` as usual.

`context-map.yaml` is edited as text: a stamp change rewrites one line and missing top-level keys are appended, so comments and quoting survive. Only a nested `update_rules` merge re-serialises the
whole file, and that path flags the run for review. Recipe renames reach `scripts/README.md`, the root governance docs, `SETUP.md` and `requirements.txt` as well as the justfile; `CHANGELOG.md` keeps
the names it was written with.

**Why the opt-out matters as much as the guard.** Without it, a project that has legitimately diverged is permanently red in the validator. A validator that always fails is one nobody reads, and the
next *real* failure goes unnoticed with it. "Expected failures" is not a stable state — it is a slow way of turning the check off.

**Both constants are restated in both scripts on purpose** (`MANUAL_TOKEN`, `VERSION_MARKER`). Drift between them would let the upgrader skip a block the validator still fails, which is the worst of
both.

- The version line must be the first comment inside the managed block.
- On repeat runs, replace only content inside the matching managed block.
- If a block is absent, append it under the most relevant existing heading.
- If a block exists with an older version string, upgrade it in place. Do not duplicate.
