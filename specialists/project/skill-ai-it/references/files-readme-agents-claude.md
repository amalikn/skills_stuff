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

Create if missing. If it exists: add missing front matter (`adopt_governed_files.py` does it at every slurp), a **Quick start** when there is none,
the **Governance pointers** section, and update **Folder index**. A status, history or architecture section is reported (`just roles`), not moved
without the operator: it belongs in ROADMAP, CHANGELOG, SCRATCHPAD or ARCHITECTURE. README is read whole, so it stays within 200 lines and links to
detail instead of holding it (role: [governed-file-roles.md](governed-file-roles.md)).

```markdown
---
Title: <Project Name>
Category: readme
Status: current
Authority: canonical
Scope: Front door of <project folder>
Last reviewed: <YYYY-MM-DD>
Summary: <One or two sentences: what the project is for and who uses it.>
Budget: 200 lines
---

# <Project Name>

<One-sentence purpose.>

## Purpose

<2–3 sentences on what this project area is for and why it exists.>

## Quick start

<The few lines a newcomer runs first: `just bootstrap`, `just --list`, the main command. When setup takes more than a few steps, one line
linking [SETUP.md](SETUP.md) instead.>

## Context

<Optional. Background a newcomer needs: why the project exists, external parties, triggering event. Not status or history: those live in
ROADMAP, CHANGELOG and SCRATCHPAD. Omit the section if there is nothing useful to say.>

## Folder index

- [<subfolder>/](<subfolder>/)
  <One-line role description.>
  Index: [<subfolder>/readme.md](<subfolder>/readme.md) ← only if index exists

## Governance pointers

- Local agent guidance: [AGENTS.md](AGENTS.md)
- Parent area guidance: [../AGENTS.md](../AGENTS.md)
- AI navigation entrypoint: [AI_NAVIGATION.md](AI_NAVIGATION.md)
- Machine-readable context map: [context-map.yaml](context-map.yaml)
- Change history: [CHANGELOG.md](CHANGELOG.md); current phase and plan: [ROADMAP.md](ROADMAP.md) when present
- Canonical governance root: [/Volumes/Data/_ai/governance/README.md](/Volumes/Data/_ai/governance/README.md)
```

#### AGENTS.md

Create if missing. If it exists, add missing sections only — do not overwrite existing rules.

Front matter comes first, fenced; the parent import follows it (an unfenced `Title:` block under the import is the legacy form, fenced by
`adopt_governed_files.py`). AGENTS.md is loaded whole by every agent: imperative rules and pointers only, within 200 lines; reasoning goes to
ARCHITECTURE.md, area rules to a file read before that work.

```markdown
---
Title: <Project Name> Agent Policy
Category: agent-governance-guide
Status: current
Authority: local-supplement
Scope: <inferred scope — one line>
Last reviewed: <YYYY-MM-DD>
Summary: <One-line summary of what this policy governs.>
---

@<absolute-or-relative path to nearest parent AGENTS.md>

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

<Insert the navigation managed block here verbatim from `templates/AGENTS-navigation-block.md` (never from a copy: copies drift).>

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

No project-specific Claude additions at this time. Add here only behaviour that differs for Claude Code.
```

Repeat-run rule: if `CLAUDE.md` already contains `@AGENTS.md`, do not rewrite it. Only append Claude-specific additions if explicitly needed.
