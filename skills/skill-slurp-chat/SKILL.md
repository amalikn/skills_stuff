---
name: skill-slurp-chat
description: Persist conversation content to memory-keeper and mcp-project-context to prevent loss from auto-compaction. /slurp-chat reads existing state from both backends, finds the last save point in each, scans the unsaved portion thoroughly and the already-covered portion lightly for missed detail, then saves only gaps. /slurp-chat close adds a full save-and-exit closeout. mcp-project-context has no delete — reading before writing is mandatory.
---

# skill-slurp-chat

## Modes
- **`/slurp-chat`** — read existing → find last save points → zone-aware scan → save gaps → checkpoint
- **`/slurp-chat close`** — same + full closeout template (see end)

## Step 1 — Channel and project ID
Derive channel from active repo (e.g. `ansible-wifi`). Never `claude-main`.
Get project ID via `list_projects` if not known.

## Step 2 — Read existing state and find last-save timestamps (mandatory before any write)

Both backends support `sort="created_desc"` — use it to get the most recent entry first.

```
# memory-keeper — read all entries for channel, newest first
context_get(channel="<channel>", includeMetadata=true, sort="created_desc")

# mcp-project-context — read all notes for project/channel, newest first
get_project_context(projectId="<id>", channel="<channel>", section="notes", sort="created_desc")
```

From each result, extract:
- **Last MK timestamp** — `createdAt` of the first (newest) memory-keeper entry
- **Last PC timestamp** — `createdAt` of the first (newest) project-context note
- **Topics covered in MK** — keys that exist and their content summary
- **Topics covered in PC** — notes that exist and what they cover

**Zone boundary = the LATER of the two timestamps.**
Anything after the later timestamp is Zone B (unsaved in both backends).
Anything before it is Zone A (at least partially covered, light check only).

If no entries exist in either backend → entire conversation is Zone B.

## Step 3 — Zone B scan (after last-save boundary — thorough)

Extract every significant item from this portion. Categorize:

| Category | mk category |
|---|---|
| Technical finding / constraint / tool behavior | `note` |
| Decision + reason + alternatives | `decision` |
| File change + why | `progress` |
| Error / fix / workaround | `error` |
| Pending task + target + commands | `task` |
| Access detail (SSH, Teleport, node names) | `note` |
| Cron / write inventory (frequencies, destinations) | `note` |

Skip: chitchat, tool scaffolding, content derivable from repo (file contents, git log).

## Step 4 — Zone A scan (before last-save boundary — light gap-fill)

For each existing MK entry and PC note, re-read the corresponding conversation segment.
Ask only: *does the conversation contain specific detail (exact commands, sizes, node names, error text, config snippets) that the existing entry omits?*
- Yes → plan an update to that key (MK) or a delta note (PC) with only the missing detail
- No → skip entirely

This pass should be fast — most Zone A content is already covered.

## Step 5 — Save gaps

### memory-keeper
Key format: `<project>.<topic>` e.g. `smc.audit.tooling.overlayfs`
One key per topic. Same key = overwrites in place (use this for Zone A additions to existing entries).

```
context_save(key, category, priority="high|normal|low", channel, value)
```

Priority: `high` for blockers and tasks gating the next milestone.

### mcp-project-context
- Zone B topics: `add_note` with the new content
- Zone A gaps: `add_note` only if the missing detail is material; title it clearly as a delta/addendum so it is distinguishable from the existing note
- If existing notes already cover the topic sufficiently → skip; no duplicate notes (project-context cannot delete)

## Step 6 — Checkpoint both
```
context_checkpoint(name="slurp-<YYYYMMDD>-<topic>")
create_checkpoint(projectId, name="slurp-<YYYYMMDD>-<topic>")
```

## Step 6.5 — Update SCRATCHPAD.md

Locate `SCRATCHPAD.md` in the project folder (same directory as AGENTS.md / README.md for the
active project). If none exists, create one via `/skill-ai-it` first.

Update only the sections affected by this session's Zone B content. Do not rewrite sections that
are already current. Apply tiered ownership rules:

| Section | What to write |
|---|---|
| `## Current state` | Update phase and prose if project state changed this session |
| `## Open items` | Add new items; tick off completed ones |
| `## Key anchors` | Add new paths, contacts, or facts discovered this session |
| `## Recent decisions` | Prepend decisions made this session (date + decision + brief rationale) |
| `## Session history` | Prepend 2–3 bullet summary of this session (not full detail — full detail is in memory-keeper) |
| `## Next actions` | Replace with current next actions |
| `## Memory pointers` | Add/update memory-keeper keys and project-context IDs from this slurp |

Mark updated content `KEEP`. Do not duplicate: no file-change lists (those live in memory-keeper),
no structured task detail (that lives in project-context), no full session logs.

If the project spans multiple channels/projects saved in this slurp, update each project's
SCRATCHPAD.md separately.

## Closeout mode only — Step 7
Save one additional `progress` entry to memory-keeper:
```
key: session.closeout.<YYYYMMDD>.<topic>
Session / Workstream:
Scope:
Completed:
Files Changed:
Decisions:
Open Issues:
Next Actions:
Persistence Status: memory-keeper: / project-context: / checkpoints:
```

## Report
Compact table: key | zone | action (created/updated/skipped) | reason if skipped.
State: last MK timestamp, last PC timestamp, zone boundary used, how much conversation was in each zone.
