---
Title: skill-ai-it reference: Always-created files: README, AGENTS, CLAUDE
Category: reference
Status: current
Authority: local-supplement
Scope: On-need reference moved verbatim from SKILL.md
Last reviewed: 2026-10-10
Summary: >-
  Always-created files: README, AGENTS, CLAUDE; moved verbatim from SKILL.md so SKILL.md stays an orchestration file within budget.
---

# skill-ai-it reference: Always-created files: README, AGENTS, CLAUDE

Moved verbatim from `SKILL.md` on 2026-10-10 to keep that file within its budget for files loaded whole.

## Contents

- [README.md](#readmemd)
- [AGENTS.md](#agentsmd)
- [CLAUDE.md](#claudemd)

#### README.md

Create if missing. If it exists, add a **Governance pointers** section and update **Folder index** only.

```markdown
# <Project Name>

<One-sentence purpose.>

## Purpose

<2–3 sentences on what this project area is for and why it exists.>

## Context

<Optional. Fill only when meaningful background exists — e.g. engagement history,
external parties, triggering event. Omit section if nothing useful to say.>

## Folder index

- [<subfolder>/](<subfolder>/)
  <One-line role description.>
  Index: [<subfolder>/readme.md](<subfolder>/readme.md) ← only if index exists

## Governance pointers

- Local agent guidance: [AGENTS.md](../AGENTS.md)
- Parent area guidance: [../AGENTS.md](../AGENTS.md)
- AI navigation entrypoint: [AI_NAVIGATION.md](../AI_NAVIGATION.md)
- Machine-readable context map: [context-map.yaml](../context-map.yaml)
- Project change/governance history: [CHANGELOG.md](../CHANGELOG.md)
- Canonical governance root: [/Volumes/Data/_ai/governance/README.md](/Volumes/Data/_ai/governance/README.md)
```

#### AGENTS.md

Create if missing. If it exists, add missing sections only — do not overwrite existing rules.

```markdown
@<absolute-or-relative path to nearest parent AGENTS.md>

Title: <Project Name> Agent Policy
Category: agent-governance-guide
Status: current
Authority: local-supplement
Scope: <inferred scope — one line>
Last reviewed: <YYYY-MM-DD>
Summary: <One-line summary of what this policy governs.>

# AGENTS.md

## Working rules

<Rules derived from content analysis. Examples:>
- Treat [communications/](communications/) as the canonical location for all correspondence.
- When processing EML files for this project, use `<internal domain>` as the internal domain.
  Mark senders/recipients on other domains as `**[External]**`.
- Log correspondence to [communications/communications-tracking.md](communications/communications-tracking.md)
  using the `skill-commtracker` workflow.
- Follow naming convention: `<slug>-YYYYMMDD_hhmm.md` for time-bound notes.
- Keep [README.md](../README.md) current when adding subfolders or significant documents.

<!-- BEGIN MANAGED: skill-ai-it:navigation -->
<!-- skill-ai-it-version: 2026-10-10-compact-v1 -->

## AI navigation and context preflight

Before answering, planning, editing, or creating files in this project:

1. Read [AI_NAVIGATION.md](../AI_NAVIGATION.md).
2. Read [context-map.yaml](../context-map.yaml).
3. Read recent entries in [CHANGELOG.md](../CHANGELOG.md).
4. Load relevant `.archcore/` context if present.
5. Load relevant `memory-bank/` files if present.
6. Consult generated context when available:
   - `graphify-out/GRAPH_REPORT.md`
   - `.ai-context/governance-pack.md`
7. Before making durable changes, inspect companion-file rules in `context-map.yaml update_rules`. Update all companion files when changing source files.
8. If sources conflict, stop and report the conflict instead of guessing.
9. Do not treat `SCRATCHPAD.md` as durable truth unless content is marked `KEEP` or promoted into `.archcore/`, ROADMAP, or memory-bank.
10. Do not treat Graphify (`graphify-out/`) or Repomix (`.ai-context/`) output as canonical truth. These are generated support artifacts only, always rebuildable.
11. Before running scripts or automation, inspect `justfile`, `scripts/README.md`, `Taskfile.yml`, `Makefile`, and `package.json` when present.
    Prefer `just --list` and `just <task>` when a `justfile` exists.
12. Treat uncataloged scripts as `unknown` safety until inspected.
13. When adding, modifying, or removing scripts or tasks, update `scripts/README.md` to reflect the change — purpose, inputs, outputs, safety label, and idempotency.
14. Run defined audit/check commands before completing work. Where `scripts/check_governance.py` exists, that includes it — and when it fails, fix the project, not the check.
    Adding a new artifact class, generated output, or a constant restated across files requires extending its registries in the same pass.
15. After making changes, update `CHANGELOG.md` for all durable governance/navigation changes.
16. Preserve user-authored content outside managed sections. Do not rewrite custom project notes.

<!-- END MANAGED: skill-ai-it:navigation -->

<Insert the governance-checks managed block here verbatim from `templates/AGENTS-governance-checks-block.md`, with `<RUNNER CHECK COMMAND>` replaced by this project's actual command (e.g. `just check`).>

## Canonical governance linkage

- Parent area guidance: [../AGENTS.md](../AGENTS.md)
- Cross-repo governance root: [/Volumes/Data/_ai/governance/README.md](/Volumes/Data/_ai/governance/README.md)
```

#### CLAUDE.md

Always create as thin wrapper. Never duplicate AGENTS.md content here.

```markdown
@AGENTS.md

## Claude-specific additions
# No project-specific Claude additions at this time.
# Add here only if this project needs Claude Code behaviour that differs from global policy.
```

Repeat-run rule: if `CLAUDE.md` already contains `@AGENTS.md`, do not rewrite it. Only append Claude-specific additions if explicitly needed.
