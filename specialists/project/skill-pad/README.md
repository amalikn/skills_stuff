---
Title: skill-pad (the Pad skill, central)
Category: skill-install
Status: current
Authority: Pad's own skill text (`pad agent install`) plus the operator's conventions baseline and scripts; this folder is the one copy
Scope: The /pad skill for Claude Code and for Codex, Cursor, Windsurf and OpenCode, the apn convention baseline, and the Pad backup and export scripts
Last reviewed: 2026-11-10
Summary: >-
  Pad (github.com/PerpetualSoftware/pad) is the operator's personal project-management layer over each project's trackers. This folder (renamed from
  skills_stuff/pad on 2026-11-10) holds Pad's skill in the layout `pad agent install` writes, the conventions every apn workspace carries, and the
  scripts that back Pad up and export a workspace into its project.
---

# skill-pad

Operator, 2026-11-10: manage Pad's skill centrally like the other skills (symlinked, no per-project copies), keep its conventions here so other projects copy the same, and name it skill-pad under
`specialists/project/`.

## Contents

- [Layout and install](#layout-and-install)
- [Refresh after a Pad upgrade](#refresh-after-a-pad-upgrade)
- [Conventions baseline](#conventions-baseline)
- [Scripts](#scripts)
- [Setting Pad up in a project](#setting-pad-up-in-a-project)

## Layout and install

| Path                            | Used by                           | Installed as                                                                                 |
| ------------------------------- | --------------------------------- | -------------------------------------------------------------------------------------------- |
| `.claude/skills/pad/SKILL.md`   | Claude Code                       | `~/.claude/skills/skill-pad` (path:install-example), a symlink to `.claude/skills/pad/` here |
| `.agents/skills/pad/SKILL.md`   | Codex, Cursor, Windsurf, OpenCode | `~/.agents/skills/skill-pad` (path:install-example), a symlink to `.agents/skills/pad/` here |
| `conventions/apn-baseline.toml` | every apn project workspace       | applied by `scripts/pad_conventions.py`                                                      |
| `scripts/`                      | the operator's Mac                | see [Scripts](#scripts)                                                                      |
| `references/examples/`          | readers                           | a worked setup message sent to a project (2026-11-10)                                        |

The SKILL.md files are Pad's text and keep Pad's own `name: pad` (a refresh rewrites them); the install links carry the name skill-pad. Do not edit them by hand.

## Refresh after a Pad upgrade

```bash
cd /Volumes/Data/_ai/_skills/skills_stuff/specialists/project/skill-pad && pad agent install codex && pad agent install claude   # name the tools: bare `pad agent install` only asks
git -C /Volumes/Data/_ai/_skills/skills_stuff diff -- specialists/project/skill-pad/   # read what Pad changed, then commit
```

Pad writes with a plain file write into the current folder (source: `internal/cli/agents.go` `InstallForTool`, v0.19.2), so running it here updates these files in place and the install links keep
pointing at them.

## Conventions baseline

`conventions/apn-baseline.toml` holds the five conventions agreed in unified-network-controller and smc-resiliency on 2026-11-10, with `{project}` and `{trackers}` filled per project:

| id             | Title                                                                 | Trigger          | Replaces (startup template)       |
| -------------- | --------------------------------------------------------------------- | ---------------- | --------------------------------- |
| commit-message | Commit messages: '{project}: <summary>' through just commit-project   | on-commit        | Conventional commit format        |
| one-branch     | Commit only through just commit-project (one repo, one branch)        | on-commit        | Never push directly to main       |
| just-check     | just check passes before a task is done (`commands = ["just check"]`) | on-task-complete | Run tests before completing tasks |
| review-diff    | Review your own diff before committing (no PRs here)                  | on-commit        | Review your own changes before PR |
| trackers-truth | Repo trackers are the truth; Pad items link to them                   | always           | (new)                             |

Apply to a workspace, from the project folder: `python3 <this folder>/scripts/pad_conventions.py --project <name> --trackers "<its trackers>"` (plan), then `--apply`. It rewrites the template's four
in place, creates the fifth, and leaves any other convention alone. A project may keep richer wording of its own: the plan shows `update ... content` for those; apply only when the baseline text
should win.

## Scripts

| Script                       | What it does                                                                     | Run                                                                                |
| ---------------------------- | -------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------- |
| `scripts/pad_conventions.py` | Applies the conventions baseline to one workspace (plan, then `--apply`)         | from the project folder                                                            |
| `scripts/pad_export.py`      | One workspace's items as a Markdown page in its project; rewrites only when an   | each project's `just pad-export`, run non-fatally by its `commit-gate`             |
|                              |   item changed                                                                   |                                                                                    |
| `scripts/pad_backup.sh`      | Online-safe backup of pad.db (all workspaces) to OneDrive `pad_backups`, newest  | launchd `au.malik.pad-backup` at 02:30 (`scripts/pad_backup.plist`, symlinked      |
|                              |   30 kept                                                                        |   into ~/Library/LaunchAgents)                                                     |

Tests: `tests/test_pad_export.py`, `tests/test_pad_conventions.py` (`python3 -m unittest discover -s tests`). The old scripts_stuff paths (`bash/pad_backup.sh`, `python/pad_export/pad_export.py`) are
symlinks to these until every project points here.

## Setting Pad up in a project

Learned in unified-network-controller, 2026-11-10:

1. `pad auth whoami` reports a user, then `pad workspace init <name> --template startup` in the project folder (`pad init` only on a machine not yet set up).
2. Delete the `.claude/skills/pad/` and `.agents/skills/pad/` copies Pad writes into the project; this folder serves every project. Keep `.pad.toml` and give it a `#` comment header (governance
   freshness checks refuse a file without a summary).
3. Apply the conventions baseline (above). The startup template's commit conventions contradict a single-branch repo with its own commit recipe.
4. Seed plans and tasks that each name their tracker entry; pass `--op-key` on every create so a rerun does not duplicate.
5. Keep a readable copy in Git: a `pad-export` recipe calling `scripts/pad_export.py --out <trackers>/pad-focus.md --apply`, run non-fatally in the project's commit gate (`-@` in just) so it never
   blocks a commit when Pad is stopped or its disk is absent.

Install facts behind this folder (verified 2026-11-10): Claude Code reads user skills only from its own skills folder; Codex reads `~/.agents/skills` (path:install-example) and the deprecated codex
skills folder (source openai/codex `codex-rs/ext/skills/src/host_roots.rs`); Pad writes skills with a plain file write, which follows a symlink.

## Learned

> **Learned 2026-11-10** · Pad CLI v0.19.2 · VERIFIED_PRIMARY (run in unified-network-controller and smc-resiliency) · Source: `pad item update --help`,
> CLI errors · Falsifier: a Pad release that accepts these writes or lists disabled items by default.
> `pad item update --fields-json` refuses the `convention` key ("system metadata ... BUG-2627"): set `trigger`, `status`, `commands` and Pad rewrites
> its own `convention` block. `pad item list conventions` hides disabled items; add `--all` to see them (a disabled template rule looks deleted).
> `--fields-json` is the way to set a list field (`commands`); `--field key=value` only sets strings. Bare `pad agent install` asks interactively and
> does nothing with stdin closed: name the tool. `pad workspace init` with an authenticated CLI needs no browser; `pad init` does.
