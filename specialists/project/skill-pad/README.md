---
Title: skill-pad (the operator's own Pad skill)
Category: skill-install
Status: current
Authority: canonical; the operator's own Pad skill, conventions baseline and scripts (this folder is the one copy)
Scope: The /pad skill for Claude Code and for Codex, Cursor, Windsurf and OpenCode, the apn convention baseline, and the Pad backup and export scripts
Last reviewed: 2026-11-19
Summary: >-
  Pad (github.com/PerpetualSoftware/pad) is the operator's personal project-management layer over each project's trackers. This folder (renamed from
  skills_stuff/pad on 2026-11-10) holds the operator's own Pad skill (SKILL.md and references, no Pad-shipped skill file), the conventions every apn
  workspace carries, the scripts that back Pad up, export a workspace, generate trackers from Pad collections, check and rewrite items to the
  writing standard and run the live feed, and a verbatim mirror of Pad's documentation.
Budget: 200 lines, 25 KB
---

# skill-pad

Operator, 2026-11-10: manage Pad's skill centrally like the other skills (symlinked, no per-project copies), keep its conventions here so other projects copy the same, and name it skill-pad under
`specialists/project/`.

## Quick start

`just bootstrap`, `just check`; in a linked project, `/skill-pad status`. Full setup: [SETUP.md](SETUP.md).

## Contents

- [Quick start](#quick-start)
- [Layout and install](#layout-and-install)
- [Refresh after a Pad upgrade](#refresh-after-a-pad-upgrade)
- [Conventions baseline](#conventions-baseline)
- [Scripts](#scripts)
- [Setting Pad up in a project](#setting-pad-up-in-a-project)
- [Learned](#learned)

## Layout and install

| Path                            | Used by                           | What                                                                                                      |
| ------------------------------- | --------------------------------- | --------------------------------------------------------------------------------------------------------- |
| `SKILL.md`                      | Claude Code, Codex, Cursor, ...   | the operator's own skill (name skill-pad); `~/.claude/skills/skill-pad` and `~/.agents/skills/skill-pad` link here |
| `references/*.md`               | agents                            | topic references routed from SKILL.md, rewritten from Pad v0.19.2 sources                                 |
| `references/upstream/`          | agents, readers                   | verbatim Pad sources: repo at tag v0.19.2, getpad.dev pages, CLI help; index [readme.md](references/upstream/readme.md) |
| `references/examples/`          | readers                           | a worked setup message sent to a project (2026-11-10)                                                     |
| `conventions/apn-baseline.toml` | every apn project workspace       | applied by `scripts/pad_conventions.py`                                                                   |
| `conventions/collection-schemas/` | agents creating collections     | Asks, Bugs, Feature Requests, Tech Debt, Decisions schemas; index [readme.md](conventions/collection-schemas/readme.md) |
| `scripts/`                      | the operator's Mac                | see [Scripts](#scripts) and [scripts/README.md](scripts/README.md)                                        |
| `docs/pad-usage-guidelines-20261110_1628.md` | operator         | guidelines in force (operator, 2026-11-10): asks, plans, tasks, writing standard, tags |
| `docs/pad-markdown-sync-plan-20261119_1845.md` | operator    | proposed 2026-11-19: one owner per record type, markdown keys, sync with journal and revert, link checks, script gaps G1-G18, collections to add |

Operator, 2026-11-10: "develop our own skill and not rely on the plugin"; Pad's generated `.claude/skills/pad/` and `.agents/skills/pad/` copies were
extracted into the references and removed. Install and first run: [SETUP.md](SETUP.md); how the parts fit: [ARCHITECTURE.md](ARCHITECTURE.md).

## Refresh after a Pad upgrade

`brew upgrade perpetualsoftware/tap/pad`, then `just upstream <version>` (plan) and `just upstream <version> --apply` to mirror the release, diff it
against the previous mirror, and carry what changed into the references by hand: [references/upgrade.md](references/upgrade.md). Never run `pad agent
install` or `pad agent update` here or in a home folder.

## Conventions baseline

`conventions/apn-baseline.toml` holds the seven conventions agreed in unified-network-controller and smc-resiliency on 2026-11-10, with `{project}` and `{trackers}` filled per project:

| id             | Title                                                                 | Trigger          | Replaces (startup template)       |
| -------------- | --------------------------------------------------------------------- | ---------------- | --------------------------------- |
| commit-message | Commit messages: '{project}: <summary>' through just commit-project   | on-commit        | Conventional commit format        |
| one-branch     | Commit only through just commit-project (one repo, one branch)        | on-commit        | Never push directly to main       |
| just-check     | just check passes before a task is done (`commands = ["just check"]`) | on-task-complete | Run tests before completing tasks |
| review-diff    | Review your own diff before committing (no PRs here)                  | on-commit        | Review your own changes before PR |
| trackers-truth | Repo trackers are the truth; Pad items link to them                   | always           | (new)                             |
| writing-standard | Write plans, tasks and updates to the apn writing standard | always | (new, 2026-11-10) |
| pad-owned-trackers | Bugs, feature requests and tech debt live in Pad; their tracker files are generated | always | (new, 2026-11-10) |

Apply to a workspace, from the project folder: `python3 <this folder>/scripts/pad_conventions.py --project <name> --trackers "<its trackers>"` (plan), then `--apply`. It rewrites the template's four
in place, creates the other three, and leaves any other convention alone. A project may keep richer wording of its own: the plan shows `update ... content` for those; apply only when the baseline text
should win. To add one new entry without touching the rest, pass `--only <id>` (2026-11-10: how `writing-standard` reached both workspaces).

## Scripts

Catalogue with safety labels and recipes: [scripts/README.md](scripts/README.md) (conventions, export, backup, live monitor, upstream refresh, tracker generation, decisions mirror, item rewrite, format spec and
writing-standard check, link opener, `.pad.toml` probe, governance checker). Tests: `just test`. The old scripts_stuff paths (`bash/pad_backup.sh`, `python/pad_export/pad_export.py`) are symlinks to these until every
project points here.

## Setting Pad up in a project

Learned in unified-network-controller, 2026-11-10:

1. `pad auth whoami` reports a user, then `pad workspace init <name> --template startup` in the project folder (`pad init` only on a machine not yet set up).
2. Delete the `.claude/skills/pad/` and `.agents/skills/pad/` copies Pad writes into the project; this folder serves every project. Keep `.pad.toml` and give it a `#` comment header (governance
   freshness checks refuse a file without a summary). `pad workspace switch` deletes that comment: [references/workspace-context.md](references/workspace-context.md), Learned 2026-11-11.
3. Apply the conventions baseline (above). The startup template's commit conventions contradict a single-branch repo with its own commit recipe.
   A project with no bug, feature or tech-debt trackers (the apn hub, enterprise-strategy, 2026-11-20) applies it with `--only` and leaves `pad-owned-trackers` out;
   start such a workspace with the Asks collection (docs/pad-usage-guidelines, 3.1; create flags in the `=` form on 0.21.1).
4. Seed plans and tasks that each name their tracker entry; pass `--op-key` on every create so a rerun does not duplicate.
5. Keep a readable copy in Git: a `pad-export` recipe calling `scripts/pad_export.py --out <trackers>/pad-focus.md --apply`, run non-fatally in the project's commit gate (`-@` in just) so it never
   blocks a commit when Pad is stopped or its disk is absent.
6. Decisions (operator, 2026-11-20: every decision, existing and new, in Pad; "this will be standard"): keep `docs/decision-log.md` with rows
   `| DL-nnn | date | architecture or process | decision | reason | status |` (status accepted, deferred, rejected or `superseded by DL-nnn`; a reversal supersedes,
   never rewrites), create the Decisions collection once from `conventions/collection-schemas/decisions.json`, and add a `pad-decisions` recipe calling
   `scripts/pad_decisions.py --project-root . --decision-log docs/decision-log.md`. Accepted decisions are a closed status: list them with `pad item list decisions --all`.
   A project with a `docs/trackers/` folder keeps the log there (smc-resiliency, 20 Nov 2026: 90 decisions, 1 superseded, built from SCRATCHPAD's
   Recent decisions, live and rotated). Run the recipe non-fatally in the commit gate, and have the project's check fail on a KEEP decision with no log row.

Install facts behind this folder (verified 2026-11-10): Claude Code reads user skills only from its own skills folder; Codex reads `~/.agents/skills` (path:install-example) and the deprecated codex
skills folder (source openai/codex `codex-rs/ext/skills/src/host_roots.rs`); Pad writes skills with a plain file write, which follows a symlink.

## Learned

Moved to [references/cli-reference.md](references/cli-reference.md), Traps (2026-11-10), where CLI behaviours met in use are kept.
