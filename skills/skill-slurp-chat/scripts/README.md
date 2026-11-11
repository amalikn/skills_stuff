---
Title: skill-slurp-chat scripts
Category: skill-scripts-index
Status: current
Authority: canonical
Scope: Scripts shipped with skill-slurp-chat
Last reviewed: 2026-11-05
Summary: Catalogue of raw Claude transcript and explicit Codex rollout helpers, with offline regression tests.
---

# skill-slurp-chat scripts

| Script | Purpose | Inputs | Output | Safety | Run |
| ------ | ------- | ------ | ------ | ------ | --- |
| `transcript_passes.py` | Step 3's passes from the raw session transcript; `--reports` prints every sub-agent report in full (pass 3 since 2026-10-29: every sub-agent from `<session>/subagents/`, its task, final report and `sub-` side effects): compaction points, every user message (typed, mid-turn, slash commands with their arguments since 2026-10-27, question answers; a repeated typed turn such as four "yes" approvals is listed each time and command tags quoted in a tool result are not a command, both since 2026-11-11), every Bash command, file write and MCP write, with times and counts. Required after a compaction (2026-10-09). | `[--transcript PATH] [--since ISO-UTC] [--pass 1\|2]`; default the newest transcript of the current directory | stdout | read-only | `python3 scripts/transcript_passes.py --since 2026-10-09T01:53` |
| `private_commit.py` | Step 5b commit in a repository live sessions share: builds the commit in a private index from HEAD plus only the named paths, moves the branch only if it is still at that HEAD, and leaves the shared index and other sessions' staged files alone (2026-11-05: two sessions' `git commit` each took the other's staged files). | `--repo --message-file path[=@work\|@index\|file]... [--apply]` | stdout | dry run by default; `--apply` writes one commit and the named index entries | `just private-commit <repo> <msg> <paths> --apply` |
| `test_private_commit.py` | Offline test: a peer's staged file stays staged and out of the commit. | none | test result | temp folder only | `just test` |
| `writeback_status.py` | Step 5b/6b: per named skill, uncommitted files, newest CHANGELOG entry, manifest version, last commit; then unpushed commits. Exit 1 when a skill is dirty or missing (2026-10-26: two slurps passed 6b with dirty skills). | skill folder names `[--repo PATH]` | stdout | read-only (git status/log) | `just writeback-status skill-smc skill-coder` |
| `test_writeback_status.py` | Offline test with a temporary git repo: clean, dirty and missing skills. | none | test result | temp folder only | `just test` |
| `test_transcript_passes.py` | Offline tests for the sub-agent pass, IDE prefixes, slash commands (not inside tool results), repeated typed turns and their queued copies, Codex repeated turns, mirrored messages, compaction, tool-name privacy, time filtering and pass-2 CLI. | none | test result | read-only | `python3 -m unittest scripts/test_transcript_passes.py` |

Codex rollouts require `--transcript PATH` explicitly; default discovery remains Claude-only. Codex pass 2 lists envelope and nested tool names,
with all arguments omitted to avoid leaking command or patch secrets. It is an inventory of candidate actions, not a claim that each tool wrote
state; inspect relevant inputs locally. Repeated actual user turns are preserved, mirrored response-item messages are ignored. The helper streams
the file; do not save its private transcript output into a project or public source archive.
