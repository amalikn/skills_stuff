---
Title: skill-slurp-chat scripts
Category: skill-scripts-index
Status: current
Authority: canonical
Scope: Scripts shipped with skill-slurp-chat
Last reviewed: 2026-10-16
Summary: Catalogue of raw Claude transcript and explicit Codex rollout helpers, with offline regression tests.
---

# skill-slurp-chat scripts

| Script | Purpose | Inputs | Output | Safety | Run |
| ------ | ------- | ------ | ------ | ------ | --- |
| `transcript_passes.py` | Step 3's two passes from the raw session transcript: compaction points, every user message (typed, mid-turn, question answers), every Bash command, file write and MCP write, with times and counts. Required after a compaction (2026-10-09). | `[--transcript PATH] [--since ISO-UTC] [--pass 1\|2]`; default the newest transcript of the current directory | stdout | read-only | `python3 scripts/transcript_passes.py --since 2026-10-09T01:53` |
| `test_transcript_passes.py` | Offline tests for IDE prefixes and Codex repeated turns, mirrored messages, compaction, tool-name privacy, time filtering and pass-2 CLI. | none | test result | read-only | `python3 -m unittest scripts/test_transcript_passes.py` |

Codex rollouts require `--transcript PATH` explicitly; default discovery remains Claude-only. Codex pass 2 lists envelope and nested tool names,
with all arguments omitted to avoid leaking command or patch secrets. It is an inventory of candidate actions, not a claim that each tool wrote
state; inspect relevant inputs locally. Repeated actual user turns are preserved, mirrored response-item messages are ignored. The helper streams
the file; do not save its private transcript output into a project or public source archive.
