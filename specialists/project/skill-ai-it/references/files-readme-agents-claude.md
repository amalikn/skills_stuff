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
Budget: 200 lines, 25 KB
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

## AGENTS.md chains across folders: Claude Code vs Codex

> **Learned 2026-11-05** · Claude Code and codex-cli 0.166.0, AGENTS.md above a repo · VERIFIED-OBSERVED (`codex exec -s read-only` asked which project AGENTS.md files it was given, before and
> after each change; operator's /Volumes/Data, _ansible and repo files) · Source: `scripts/checks/agents_chain.py` (this commit); codex-cli 0.166.0 config schema (`project_root_markers = [".git"]`,
> `project_doc_max_bytes = 32768`) · Falsifier: Codex listing a parent folder's AGENTS.md with the default markers

A chain that imports each level with `@<absolute path>` (repo → workspace → volume root → global) reaches **Claude Code** whole. **Codex** ignores `@` lines and loads its global file
(`$CODEX_HOME/AGENTS.md`) plus one `AGENTS.override.md` or `AGENTS.md` per folder from its **project root** down to the working folder; the root is the nearest folder holding a `project_root_markers`
entry (default `.git`), or the working folder itself when none is found. So with defaults Codex never sees files above the repo. Two ways to give it the chain, both used together (operator, 2026-11-05):

1. **An inline block in the repo's own AGENTS.md** carrying what Codex must know (for example the skills routing), with a pointer to the full registry.
2. **A root marker:** `project_root_markers = [".codex-root"]` in `config.toml` and an empty `.codex-root` at the chain's top. Do not keep `.git` in the list: the nearest marker wins, so the repo stays
   the root. Raise `project_doc_max_bytes` (65536) when the chain is long: Codex cuts from the end, so the repo's own file is what gets lost (a 7-level chain measured 37.4 KB).

Traps:
- **Trust follows the project root.** Moving the root to a parent folder makes per-repo trust entries stop matching (stricter, Codex asks to trust the parent), and a marker in an already trusted folder
  silently extends that trust to every repo under it. Never put a marker in a trusted folder holding repos nobody trusted (a `~` marker was removed for this); mark each such repo instead.
- **Symlinked AGENTS.md:** a relative `@../AGENTS.md` inside a symlinked file may resolve from the link's target folder; use absolute imports.

Check any folder: `just agents-chain <folder>` (`--check` exits 1 on a missing import, a cycle, a cut file or trust spread):

```python
# scripts/checks/agents_chain.py (2026-11-05): Codex project root as observed on codex-cli 0.166.0
def codex_root(start: Path, markers: list[str]) -> Path:
    for d in [start, *start.parents]:
        if any((d / m).exists() for m in markers):
            return d
    return start
```
No visual surface.
