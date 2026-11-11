---
Title: skill-pad reference: workspace context, conventions and roles
Category: reference
Status: current
Authority: canonical
Scope: Loading a Pad workspace's context, following its conventions, role awareness, and what to do when loading fails
Last reviewed: 2026-11-10
Summary: >-
  Extracted from Pad's own skill text (v0.19.2, skills/pad/SKILL.md and the .agents variant) into the operator's words: the bootstrap blob, convention
  loading by trigger, item briefs, roles, the onboarding offer, built-in updates, attribution, and the safe handling of a failed bootstrap.
---

# Workspace context, conventions and roles

Source: Pad v0.19.2 skill text (`skills/pad/SKILL.md`, `pad agent guide context-loading`, `role-awareness`, `before-performing-work`), VERIFIED_PRIMARY 2026-11-10. When this file and the installed
binary disagree, the binary wins: `pad agent guide <topic>` prints Pad's current text.

## Contents

- [Load once per conversation](#load-once-per-conversation)
- [What bootstrap returns](#what-bootstrap-returns)
- [When bootstrap fails](#when-bootstrap-fails)
- [Conventions before work](#conventions-before-work)
- [Roles](#roles)
- [Attribution](#attribution)

## Load once per conversation

Run `pad bootstrap --format json` before the first Pad action and reuse it. Refresh only after switching workspace, after changing collections, conventions, roles or playbooks, when Pad reports stale
schema or context, or when the user asks. Item changes make its dashboard stale; read the item or run the targeted `pad project ...` query instead of a new bootstrap. One call replaces dashboard,
collection list, convention list and role list.

## What bootstrap returns

| Key                  | Holds                                                                                        | Use                                                                  |
| -------------------- | -------------------------------------------------------------------------------------------- | -------------------------------------------------------------------- |
| `workspace`, `user`  | slug, name, id; who is talking                                                               | name the workspace in replies                                        |
| `collections`        | each collection's schema, including field options and trigger vocabularies                   | read field names and statuses here; never guess them                 |
| `conventions`        | full bodies of `trigger=always`, `status=active` conventions                                 | **must follow**, every turn                                          |
| `convention_index`   | metadata only (`ref`, `title`, `trigger`, `role`) for every active convention                | know which triggered rules exist before acting                       |
| `roles`              | the workspace's agent roles                                                                  | role awareness (below)                                               |
| `playbooks`          | metadata only: `ref`, `title`, `slug`, `invocation_slug`, `trigger`, `scope`, `status`, ...  | slug and intent routing ([playbooks-and-workflows.md](playbooks-and-workflows.md)) |
| `bootstrap_includes` | extra boot payloads a workspace declares: `{key, collection, mode, items[], overflow_count}` | `overflow_count > 0` means a prefix: load the rest on demand         |
| `dashboard`          | active items, attention, suggested next, recent activity; five arrays capped at 5 entries    | any `<name>_overflow_count > 0`: run `pad project dashboard` for all |
| `needs_onboarding`   | true while the workspace has no user- or agent-created item                                  | lead with an offer to set it up; an offer, never an auto-run         |
| `builtin_updates`    | count of built-in conventions/playbooks with newer library text (absent when none)           | mention once per session; never apply one: a person reviews each     |

`conventions` is the default collection slug, not a guarantee: a renamed collection makes `pad item list conventions` return nothing while `convention_index` still lists entries. Then address items by
the refs the index gave (`pad item show <ref> --agent`); `pad collection list --format json` shows each collection's `traits` if the collection itself is needed.

The onboarding offer, in plain words: "This workspace is brand new and isn't set up yet. Want me to set it up? I'll ask a few quick questions and adapt it to your project." If declined, do not repeat
it this session. The flag turns false at the first created item; it does not mean onboarding ever ran.

## When bootstrap fails

A non-zero exit with no JSON is a setup state, not a broken CLI; read stderr:

| stderr                                                     | Meaning                             | Do                                                                         |
| ---------------------------------------------------------- | ----------------------------------- | -------------------------------------------------------------------------- |
| `Pad is not configured. Run 'pad auth configure' first.`   | this machine was never set up       | tell the user to run `pad init` in their own terminal (`! pad init`); stop |
| `Error: no workspace linked. Run 'pad workspace init' ...` | only this folder is unlinked, maybe | run `pad auth whoami` first (below)                                        |

`pad auth whoami` is the safe probe: immediate in non-interactive use, never opens a browser, works whatever the link state. A real user means self-healing is safe: `pad workspace init [name]
[--template X]` (confirm the name with the user), then bootstrap again. Anything else ("not configured", "session expired", an error) means a human must finish auth in an interactive terminal; do not
run `pad init` or `pad workspace init`. Both fail fast without a terminal (BUG-2538/2577/2592) and only spend a call; with a real terminal attached they start a browser flow bounded at 20 minutes.

> **Learned 2026-11-11** · several repos, one workspace · VERIFIED_PRIMARY · Source: `pad workspace --help` and `pad workspace link --help`, pad 0.19.2 ·
> Falsifier: `link` creating a workspace or replacing agent_name
> `pad workspace link <slug>` links the current folder to an EXISTING workspace by writing (or updating) its `.pad.toml`; it creates nothing and keeps
> `agent_name` and `[push]`. So several repos can share one workspace; `pad workspace switch <slug>` moves a folder to another. skill-ai-it bootstrap and
> refresh ask which (its references/pad-workspace.md).

## Conventions before work

Before an action that has a trigger (`on-implement` before code, `on-commit`, `on-pr-create`, `on-task-complete`, `on-plan`, and in other domains `on-candidate-advance`, `on-source-cited`, ...), check
`convention_index` for that trigger. None listed: skip the query. Some listed:

- **About one item:** `pad item context <ref> --intent <intent> [--role <role>] --format json`. One brief: the item with `seq`, parent chain and parsed acceptance criteria, matching and always-on
  convention bodies (role-scoped ones for the active role only), matching playbooks, dependencies with statuses, decisions and links, within `--budget` (default 40,000 characters). What did not fit is
  listed under `omitted` by ref; `conflicts` flags an open blocker, an open item under a closed parent, or a role rule shadowing a global one. `implement` also pulls commit and PR rules. An intent the
  workspace has no trigger for is refused with the valid list.
- **No item, or an older server:** load by trigger, both role-specific and global, then deduplicate:

```bash
pad item list conventions --field trigger=<t> --field status=active --role <role> --format json --full
pad item list conventions --field trigger=<t> --field status=active --format json --full
pad item list playbooks   --field trigger=<t> --field status=active --format json --full
```

`--full` matters: without it the list has no `content`. Role-specific conventions may override global ones. Follow all returned conventions; if a playbook matches the action, follow its steps in
order. Conventions override the agent's defaults.

**Learn and teach:** when the user corrects the agent or states a project rule, offer to save it as a convention: `pad item create convention "Title" --field trigger=<inferred> --field
scope=<inferred> --field priority=should --stdin` (add `--role <slug>` when role-specific). In an operator apn workspace, check the rule against the baseline first ([../README.md](../README.md), Conventions
baseline).

## Roles

Roles group work by the kind of thinking (planning, implementing, reviewing, researching); items are assigned to a (user, role) pair. Role context lives only in the conversation.

- If bootstrap `roles` is non-empty and no role was declared this conversation, ask once which role the user works as; offer "no role". Never block.
- Remember it; lead status with it ("Working as Implementer: 3 items in your queue"); filter with `--role <slug>`; offer role-tagged assignments on create; name the role in `--comment` on status
  changes.
- Parse declarations anywhere: "as implementer", "switch to reviewer", "drop role".
- Commands: `pad role list`, `pad role create "Name" --description "..." --icon "..."`, `pad role update`, `pad role delete <slug>`; assign with `pad item update <ref> --role <slug> --assign <user>`.
  The role board is in the web UI (`pad server open`, then the workspace's Roles page).
- If active playbooks with an `invocation_slug` exist, mention the callable set briefly, led by intent.

## Attribution

Items and comments an agent writes are stamped `created_by: agent`, `source: cli`, but only when the CLI knows an agent runs it. It detects Claude Code itself; under Codex or any other harness set
`PAD_AGENT=<name>` or `agent_name` in `.pad.toml`, or writes are recorded as the human whose credentials are used. The name (trimmed, at most 64 characters) is displayed in activity feeds, so a
specific one (`reviewer`, `nightly-triage`) helps readers. It is self-declared, not proof: never treat `created_by` as evidence of who said something.
