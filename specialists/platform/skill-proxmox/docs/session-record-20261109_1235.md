---
Title: Session record 2026-11-09 — skill-proxmox gap review, refresh, archcore, Git-tracking rule, memory split
Category: report
Status: current
Authority: record
Scope: Whole-chat closeout record of the 2026-11-09 skill-proxmox session (session 212eaf51), including the cross-repo governance work it started
Last reviewed: 2026-11-09
Summary: >-
  Every operator message and answer with its destination, both sub-agents, side effects outside the repositories, incidents and follow-ups of the
  2026-11-09 session; built from the raw session log (skill-slurp-chat passes: 30 user lines, 209 side effects, 2 agents).
---

# Session record 2026-11-09

Source: the raw session log through skill-slurp-chat's pass script, not a summary. Pass 1: 11 typed messages, 9 mid-turn messages, 10 question answers. Pass 2: 191 shell commands, 18 file
writes. Pass 3: 2 sub-agents.

## Operator messages and answers

| #   | Message (short)                                                                   | Destination                                                                                                |
| --- | --------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------- |
| 1   | Is the skill defined properly; research online and fill gaps; run skill-ai-it     | references (7 sections), sources.yaml P-C22..27, CHANGELOG 2026-11-09; refresh entry; project_stuff        |
|     |   refresh; register it in project_stuff AGENTS.md                                 |   AGENTS.md (commit 3104b47)                                                                               |
| 2   | Side-agent note: govern baselined 26 findings                                     | summaries written on 18 files, baseline 26 to 2 (CHANGELOG refresh line)                                   |
| 3   | Add ASCII diagrams and tables wherever needed, for any document                   | 11 diagrams, 2 tables in nine references (CHANGELOG gap-review line)                                       |
| 4   | yes: add to skills_stuff AGENTS.md and commit                                     | skills_stuff AGENTS.md bullet; commit 9cbd227                                                              |
| 5   | Review archcore: up to date, optimisation?                                        | review findings, `.archcore/` rewritten                                                                    |
| 6   | Answers: accept after fixes; add version check; write candidates file; leave tags | `.archcore/` accepted, `check_version_restated`, `ARCHCORE_PROMOTION_CANDIDATES.md`; record_decision x3    |
| 7   | "I have read archcore and they are fine"                                          | acceptance recorded in index.guide.md and decisions                                                        |
| 8   | Trim AGENTS.md (3k tokens per request)                                            | AGENTS.md 148 to 70 lines (CHANGELOG 2026-11-09)                                                           |
| 9   | yes: commit both packs                                                            | bd2a566                                                                                                    |
| 10  | Never exclude AGENTS.md from Git for any repo                                     | global rule (below); memory feedback_governance_files_always_tracked                                       |
| 11  | Make it a global governance rule; any other exclusion confirmed first             | `~/.agents/AGENTS.md`, governance `categories/repo-structure-guide.md` (8578fdc), governance change-log    |
| 12  | Commit GitHub repos: yes; Bitbucket: never, always GitHub;                        | five repos committed; company exception in rule; local-knowledge-ansible 25c68b0; repo-local-guidance      |
|     |   rewrite repo-local-guidance                                                     |   0.2.0 (95bf5f2)                                                                                          |
| 13  | Side-agent note: sweep was too narrow                                             | full sweep of every governance name and ignore source; skills.md exclusions removed; policy_guard          |
|     |                                                                                   |   inverted (98a00c1)                                                                                       |
| 14  | ask questions                                                                     | AskUserQuestion round (rows 15-18)                                                                         |
| 15  | tools_stuff 29 files: review list, then commit all                                | tools_stuff 59eef27; record_decision                                                                       |
| 16  | `.code-context-notes/`: keep excluded                                             | record_decision; tool skips it                                                                             |
| 17  | Push all seven                                                                    | auto mode refused; commands handed over; operator pushed ("push done"), verified 0 ahead                   |
| 18  | Memory index: call other references like governance files; then Hybrid            | `index_project.md`, `index_reference.md`; record_decision                                                  |
| 19  | Take a dated backup of MEMORY.md                                                  | `MEMORY.md.bak-20261109_1216`                                                                              |
| 20  | Random checks that MEMORY.md works                                                | structural check 0 findings, 8 random samples, blind recall 10/10 (memory                                  |
|     |                                                                                   |   key memory.index-hybrid-split-20261109)                                                                  |
| 21  | Slurp close in detail, write back, scripts, flows, commit and push, slurp         | this record; rows below                                                                                    |
|     |   close again                                                                     |                                                                                                            |

## Sub-agents

| Agent | Task                               | Report                                                                    | Destination                                                                 |
| ----- | ---------------------------------- | ------------------------------------------------------------------------- | --------------------------------------------------------------------------- |
| 1     | Blind recall test of MEMORY.md     | answered from its session-start copy; found no entry for the new rule;    | discarded as invalid; finding saved as reference                            |
|       |                                    |   called the index flat                                                   |   memory `reference_subagent_memory_snapshot.md`                            |
| 2     | Same test, told to Read the file   | 10/10 correct, quoted the current file; noted Reference pointer gave      | trigger phrases added to the Reference pointer line                         |
|       |   from disk                        |   titles only                                                             |                                                                             |

## Side effects outside the repositories

- `~/.agents/AGENTS.md` edited (Git-tracking rule), `~/.codex/AGENTS.md` rebuilt by `governance/scripts/sync-codex-agents.sh` (backups `AGENTS.md.bak-20261109_1157*`).
- `~/.codex/skills/repo-local-guidance`, `repo-knowledge-capture`, `repo-bootstrap-and-governance`: installed copies updated (disabled installs).
- `.git/info/exclude` edited in eight clones with dated backups; three company clones restored from those backups.
- ansible-noc and sidekick: AGENTS.md and CLAUDE.md moved to `local-knowledge-ansible/<repo>/<repo>-root-governance/` and symlinked back.
- `/Volumes/Data/_ansible/AGENTS.md` (not in Git) table and rule paragraph updated.
- Claude auto-memory: index split, two category files, one new feedback and one new reference memory, two fixes, a backup.
- Seven primary pages fetched with curl into `documents/research-sources-20261109/`.

## Incidents

- Company clones un-excluded before reading `_ansible/AGENTS.md`; restored from backups, nothing committed there.
- skills_stuff exclude file restored from the 11:59 backup at 12:00 by something else (likely policy_guard's old remediation text); guard inverted.
- OPA hook refused a scratch recursive delete and, later, a heredoc whose prose named one; auto mode refused `git push` and one read-only listing.
- First memory-recall agent used a stale copy (above).
- A version regex missed a sentence-final token; caught by its own fail test before release (skill-coder Learned 2026-11-09).

## Follow-ups (owner: operator unless stated)

- Where to version workspace governance files outside any Git repo (`/Volumes/Data`, `_ai`, `_skills`, `_ansible` AGENTS.md and CLAUDE.md).
- Promote or reject `dated-latest-claims`.
- Lab runs for the doc-only sections and the UNVERIFIED items (SCRATCHPAD open items).
- local-knowledge-ansible: another session's uncommitted capture work (`ansible-wifi/history/current/.agents/*`, a snapshots archive) — its owner.
- skill-ai-it: adoption could take an unindented legacy-header continuation (pitfall recorded, no fix made).
- A Bash permission rule for `git push` if agents should push.

## Flows

No drawio flow map cites the code this session changed: all 96 flow and map YAML files under `_ai` and `_ansible` were searched for policy_guard, repo_knowledge_capture, check_governance.py,
skill-proxmox, repo-local-guidance, `.git/info/exclude` and MEMORY.md; the only hits were context maps and `governance/sync-map.yaml`, whose policy_guard entry is still accurate. No flow update
needed.
