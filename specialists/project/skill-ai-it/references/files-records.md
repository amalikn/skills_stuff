---
Title: skill-ai-it reference: Always-created files: SCRATCHPAD, CHANGELOG, markdownlint
Category: reference
Status: current
Authority: local-supplement
Scope: On-need reference moved verbatim from SKILL.md
Last reviewed: 2026-10-10
Summary: >-
  Always-created files: SCRATCHPAD, CHANGELOG, markdownlint; moved verbatim from SKILL.md so SKILL.md stays an orchestration file within budget.
---

# skill-ai-it reference: Always-created files: SCRATCHPAD, CHANGELOG, markdownlint

Moved verbatim from `SKILL.md` on 2026-10-10 to keep that file within its budget for files loaded whole.

## Contents

- [SCRATCHPAD.md](#scratchpadmd)
- [CHANGELOG.md](#changelogmd)
- [.markdownlint-cli2.jsonc](#markdownlint-cli2jsonc)

#### SCRATCHPAD.md

Always create (or update if exists). Populated from live memory systems — not a blank template.

**Step 1 — Query all three memory sources** using the inferred project name and folder name as search terms. Try at least two query variations per source before declaring empty.

| Source                | Tool                                    | Query strategy                                 |
| --------------------- | --------------------------------------- | ---------------------------------------------- |
| `memory-keeper`       | `context_search`                        | project name, folder name, channel name        |
| `mcp-project-context` | `list_projects` + `get_project_context` | match project name; use project ID             |
| `claude-mem`          | `search`                                | project name, key participants, topic keywords |

**Step 2 — Synthesize results** into the SCRATCHPAD structure below. SCRATCHPAD owns current state, anchors, open items, and session summaries (2–3 bullets per session — not full detail). Deep session
logs and file-change lists belong in memory-keeper, not here. Structured task tracking belongs in project-context, not here.

Populate every section from found data. If a source returns nothing, note "no results" in Memory pointers and infer content from folder reads (Phase 2).

**Step 3 — Write SCRATCHPAD.md.** Do not mark synthesized content `KEEP`: everything rotates to `docs/history/` by default (`just rotate`),
and `KEEP` is for the few items that must stay until promoted. SCRATCHPAD is read whole at session start, so it holds working state only, within
200 lines; durable facts are promoted to ARCHITECTURE, AGENTS, ROADMAP or `.archcore/`.

```markdown
---
Title: Scratchpad
Category: working-state
Status: current
Authority: working-state
Scope: Working state of <project name> between sessions
Last reviewed: <YYYY-MM-DD>
Summary: Current working state, newest first per section; older entries rotate to docs/history, older open items to docs/trackers.
Kind: state
Budget: 200 lines, 25 KB
Archive: docs/history/ (`just history <term>`)
Keep: Next actions=1, Memory pointers=1, Session history=2, Current state=3, Recent decisions=3
Open items tracker: docs/trackers/open-items-<YYYYMMDD_hhmm>.md
---

# SCRATCHPAD

Agent working memory for <project name>: current state, open items, decisions pending promotion, next actions.
Older entries rotate to docs/history (`just history <term>`); durable facts are promoted out, not kept here.

---

<!-- populated <YYYY-MM-DD> from memory-keeper + mcp-project-context + claude-mem -->

## Current state

**Phase:** <current phase from project-context or last memory-keeper session>

<2–4 sentences: what the project is, where it stands, what just happened, what comes next.>

---

## Open items

- [ ] <Item — include enough context to act on without querying other sources>

---

## Key anchors

| Item | Detail |
|---|---|
| <pointer: key path, ID or contact> | <value; a durable fact goes to ARCHITECTURE, AGENTS or .archcore/ instead> |

---

## Recent decisions

- <YYYY-MM-DD> — <Decision. Brief rationale if known.>

---

## Session history (summaries — full detail in memory-keeper)

### <YYYY-MM-DD> — <session title>
- <2–3 bullets: what was done, decisions made, key outcome>
- Evidence basis: memory-keeper key `<key>`

---

## Next actions

- <Specific next action>

---

## Memory pointers (navigation only — content is above)

- memory-keeper channel: `<channel>` / key(s): `<key1>`, `<key2>`
- project-context project ID: `<uuid>`
- claude-mem: <results found / no results>
```

**If all three sources return no results**: write minimal SCRATCHPAD with current-state inferred from folder content (Phase 2 reads) and note: `<!-- no prior memory — populate after first closeout
-->`

#### CHANGELOG.md

Always create during bootstrap. If it exists, append entries only; do not rewrite historical entries.

Use CHANGELOG.md as the durable project history and governance-change ledger. It is not a scratchpad and must not contain long terminal logs or unverified speculation.
Newest entry first, directly under the heading; each entry says what changed, why, and where, in a few lines (detail belongs in the commit or the
document changed). Older entries rotate to `docs/history/` (`just rotate`, read on need with `just history <term>`); add entries with
`just changelog-entry`.

```markdown
---
Title: Changelog
Category: change-log
Status: current
Authority: record
Scope: Dated changes to <Project Name>
Last reviewed: <YYYY-MM-DD>
Summary: Newest entries only; older ones rotate to docs/history (just history <term>).
Kind: log
Budget: 200 lines, 25 KB
Archive: docs/history/ (`just history`, `just history-show`)
---

# Changelog — <Project Name>

## <YYYYMMDD_HHMM> — <what changed, in a few words>

### Added

- Initial governance scaffold created.

### Changed

- <Governance/navigation/context changes made during this run.>

### Notes

- Generated by `skill-ai-it` in `<bootstrap | navigation-add | refresh | audit | promote>` mode.
```

Repeat-run append format (newest first):

```markdown
## <YYYYMMDD_HHMM> — <what changed, in a few words>

### Changed

- <file> — <brief exact change>

### Skipped

- <file> — <reason>

### Proposed only

- <file.proposed> — <reason>
```

#### .markdownlint-cli2.jsonc

Create during `bootstrap`, `navigation-add`, and `refresh` unless the project already owns a markdown lint config — check for `.markdownlint-cli2.jsonc`, `.markdownlint-cli2.yaml`,
`.markdownlint.json(c)`, `.markdownlint.yaml`, or a `markdownlint-cli2` key in `package.json` first, and skip (report as skipped, not overwritten) if any is present.

Preferred source template: `templates/.markdownlint-cli2.jsonc`. It encodes the same rule the *Markdown quality rules* section already enforces on every file this skill writes — prose wraps at 200
columns, tables/code/headings exempt, `MD024` allows repeated headings across non-sibling sections — so `just lint_md` (or a bare `markdownlint-cli2` run) checks the same standard the skill already
applies by hand, instead of a stricter or looser one fighting it.

The template's `ignores` list covers generated/support surfaces common across this skill's own vocabulary (`graphify-out/`, `.ai-context/`, `.remember/`, `.code-context-notes/`, `.staleness-audit/`,
`node_modules/`, `.git/`). Add project-specific exemptions — immutable baseline/seed docs, archived research passes predating the project's markdown conventions — as additional `ignores` entries; do
not strip the shared ones.

On `refresh`, if the file exists and was written by this skill (its header comment cites this policy), merge in any newly-relevant generated-support ignores that the project has gained since; leave
project-specific ignores entries untouched. If the file exists without that header, treat it as user-owned and do not touch it.
