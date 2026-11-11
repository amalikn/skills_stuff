---
Title: Pad workspace at bootstrap and refresh
Category: reference
Status: current
Authority: skill-module
Scope: The Pad question bootstrap and refresh ask, how its answer is acted on, and how several repos share one workspace
Last reviewed: 2026-11-11
Summary: >-
  When a repo has no .pad.toml, bootstrap and refresh ask once whether to link it to a Pad workspace, suggesting the folder name and listing the existing
  workspaces (repos may share one); the answer is carried out through skill-pad and a "no" is recorded so the question is not asked again.
---

# Pad workspace at bootstrap and refresh

Operator, 2026-11-11: "when we run skill-ai-it bootstrap/refresh it should ask if Pad needs to be initialized for that particular repo, and if so ask by suggesting the name for the workspace in Pad,
because for some of the repos I might use the same workspace; multiple projects might be using the same workspace." Pad (getpad.dev) and its CLI are skill-pad's domain; this page is only the question
and its hand-off.

## Contents

- [When to ask](#when-to-ask)
- [The question](#the-question)
- [Acting on the answer](#acting-on-the-answer)
- [Sharing one workspace](#sharing-one-workspace)

## When to ask

| State of the repo                                  | bootstrap                   | refresh                |
| -------------------------------------------------- | --------------------------- | ---------------------- |
| `.pad.toml` in the folder or a parent              | report the linked workspace | report it; ask nothing |
| no `.pad.toml`, and `pad` missing or not signed in | skip; say why in the report | same                   |
| no `.pad.toml`, no recorded answer                 | ask                         | ask                    |
| no `.pad.toml`, `Pad: none` recorded               | do not ask                  | do not ask             |

The signed-in probe is `pad auth whoami` (immediate, never opens a browser; skill-pad references/workspace-context.md). Never run `pad init` or `pad workspace init` without a terminal: they start a
browser flow.

## The question

One question in the mode's question round (with the other bootstrap questions, options first):

- **Create `<folder name>`** (recommended when no workspace fits): a new workspace named after the repo folder.
- **Link to `<existing workspace>`**: one option per workspace from `pad workspace list` whose name shares a word with the repo or its parent folder (for example `smc-resiliency` beside
  `unified-network-controller` under `apn/`), at most two; the free-text answer can name any other.
- **No Pad for this repo**: recorded, so refresh does not ask again.

## Acting on the answer

Through skill-pad, in the repo folder, after the operator's answer:

| Answer          | Command (VERIFIED_PRIMARY: `pad workspace --help`, v0.19.2)       | Then                                                          |
| --------------- | ----------------------------------------------------------------- | ------------------------------------------------------------- |
| create `<name>` | `pad workspace init <name> --template startup` (in a terminal)    | skill-pad's conventions baseline (`just conventions --apply`) |
| link `<slug>`   | `pad workspace link <slug>` (writes `.pad.toml`, creates nothing) | nothing: the workspace already carries its conventions        |
| no Pad          | none                                                              | record `Pad: none (operator, <date>)` in the repo's AGENTS.md |

`.pad.toml` is a governed file: tracked in Git like the rest of the repo's governance (never ignored). Delete the `.claude/skills/pad/` and `.agents/skills/pad/` copies `pad workspace init` writes
(skill-pad SKILL.md: two Pad skills would compete).

## Sharing one workspace

Several repos linked to one workspace share its items, collections and conventions. Keep each repo's items findable: a `project` field or tag per repo (skill-pad conventions), and each repo's exports
(`pad-focus.md`, generated trackers) filtered to its own items. A repo that later needs its own workspace moves with `pad workspace switch <slug>`.
