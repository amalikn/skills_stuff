---
name: mempalace-mine
description: Use when the user says "mempalace mine conversations", "mine conversations", "mine mempalace", "mine sessions to mempalace", or any variation requesting that Claude Code and/or Codex conversation transcripts be ingested into the mempalace memory system.
version: 1.0.0
---

# Mempalace Mine Conversations

Mine Claude Code and Codex conversation transcripts into the mempalace memory palace.

## Constants

```
MP=/Volumes/Data/_ai/_mcp/mcp-working-cache/mempalace/venv/bin/mempalace
PALACE=/Volumes/Data/_ai/_mcp/mcp-data/mempalace/palace
CLAUDE_PROJECTS=$HOME/.claude/projects/
CODEX_SESSIONS=$HOME/.codex/sessions/
```

## Wings

| Source | Wing |
|---|---|
| Claude Code project dirs (`~/.claude/projects/*/`) | `claude-code` |
| Codex sessions (`~/.codex/sessions/`) | `codex` |

## Procedure

Run both mining jobs in parallel in the background:

```bash
# Claude Code — mine all project directories
export MEMPALACE_PALACE_PATH="/Volumes/Data/_ai/_mcp/mcp-data/mempalace/palace"
MP="/Volumes/Data/_ai/_mcp/mcp-working-cache/mempalace/venv/bin/mempalace"

for proj_dir in "$HOME/.claude/projects"/*/; do
  [ -d "$proj_dir" ] || continue
  $MP mine "$proj_dir" --mode convos --wing claude-code 2>&1
done

# Codex — mine sessions directory
$MP mine "$HOME/.codex/sessions" --mode convos --wing codex 2>&1
```

Run the Claude Code loop in the background (slow — many projects). Run Codex in background too.

## Reporting

After both jobs complete, report:
- New drawers filed per wing
- Files skipped (already filed)
- Any errors

Telemetry errors (`Failed to send telemetry event`) are harmless — no API key for telemetry, mining still succeeds.

## Notes

- Do NOT mine claude-web unless the user provides a source path — no default source exists.
- Verify the taxonomy first if you need to confirm wings: `mempalace_get_taxonomy` MCP tool.
- The pre-compact hook also runs this automatically before compaction via `pre-compact-mine.sh`.
