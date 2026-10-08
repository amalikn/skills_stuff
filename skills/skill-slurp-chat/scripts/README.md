---
Title: skill-slurp-chat scripts
Category: skill-scripts-index
Status: current
Authority: canonical
Scope: Scripts shipped with skill-slurp-chat
Last reviewed: 2026-10-09
Summary: Catalogue of skill-slurp-chat helper scripts.
---

# skill-slurp-chat scripts

| Script | Purpose | Inputs | Output | Safety | Run |
| ------ | ------- | ------ | ------ | ------ | --- |
| `transcript_passes.py` | Step 3's two passes from the raw session transcript: compaction points, every user message (typed, mid-turn, question answers), every Bash command, file write and MCP write, with times and counts. Required after a compaction (2026-10-09). | `[--transcript PATH] [--since ISO-UTC] [--pass 1\|2]`; default the newest transcript of the current directory | stdout | read-only | `python3 scripts/transcript_passes.py --since 2026-10-09T01:53` |
