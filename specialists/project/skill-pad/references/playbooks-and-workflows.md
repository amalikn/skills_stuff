---
Title: skill-pad reference: playbooks and multi-step workflows
Category: reference
Status: current
Authority: canonical
Scope: Routing to Pad playbooks by slug, trigger and typed decision, binding their arguments, creating them, and the ideation, plan, decompose, status, standup and retro workflows
Last reviewed: 2026-11-10
Summary: >-
  Extracted from Pad's skill text (v0.19.2) and development guide: the three routing rungs for playbooks, argument binding, the activation gotcha,
  library activation, and the multi-step workflows the skill drives.
---

# Playbooks and multi-step workflows

Source: Pad v0.19.2 `skills/pad/SKILL.md` (Playbook Invocation, Multi-Step Workflows), repo `CLAUDE.md` (Playbooks), `pad agent guide multi-step-workflows`; VERIFIED_PRIMARY 2026-11-10.

## Contents

- [What a playbook is](#what-a-playbook-is)
- [Routing: three rungs](#routing-three-rungs)
- [Binding arguments](#binding-arguments)
- [Creating a playbook](#creating-a-playbook)
- [Library](#library)
- [Workflows](#workflows)

## What a playbook is

A workspace-owned, user-editable multi-step procedure in the `playbooks` collection. Two fields make it callable: `invocation_slug` (optional, workspace-unique, kebab-case, 2+ characters) and
`arguments` (JSON array of `{name, type, required, default, description, enum}`; types `ref`, `string`, `flag`, `enum`, `number`), mirrored in the body's `## Arguments` section. Natural language is
the canonical way in on every surface; the slug is a shortcut: `/skill-pad <slug>` here (Pad's own skill uses `/pad`), `$skill-pad <slug>` in Codex, `pad playbook run <slug>` at the CLI, `pad_playbook
action=run ref=<slug>` over MCP.

## Routing: three rungs

Only `status=active` playbooks are routed or offered, on every rung; a draft or deprecated one is never dispatched, even on an exact slug.

1. **Slug.** The first token of the input exactly matches an active `invocation_slug` from bootstrap `playbooks`: load the body (`pad playbook show <slug> --format markdown`), bind the rest as
   arguments, execute the steps. "let's discuss IDEA-3" falls through: `let's` is not a slug.
2. **Trigger and intent.** "let's do a release": find active playbooks whose `trigger` fits (`on-release`) and whose title or summary matches, and offer: "Sounds like the release playbook
   (PLAYB-1160). Want me to run it? It expects a `version` argument."
3. **Typed decision.** Only when the user plainly asks for a procedure and rungs 1 and 2 found nothing (each call costs provider money): `pad playbook match -- "<the user's words>"` (the `--` stops
   text starting with `-` being read as a flag, BUG-3142). A 404 or any error, or `choice: "none"`: carry on silently. Any match is an offer, never an auto-run; there is no confidence threshold to
   gate on.

## Binding arguments

- Required positional arguments first, in declared order; ask for a missing required one rather than failing.
- `flag` is presence (`stop-after-each`); `enum`, `string`, `number` take `key=value`; `ref` accepts issue IDs or slugs.
- Defaults from context ("current git branch") are the agent's to compute.
- Flexible parsing is the agent's job ("ship PLAN-1377 squashed, no install" binds `target=PLAN-1377, merge-strategy=squash, no-install=true`); `pad playbook run <slug> [tokens...]` parses strictly
  and is side-effect free (it returns the body with bound arguments).

## Creating a playbook

"save this workflow as a playbook": create an item in `playbooks` with `--field invocation_slug=<slug>` (omit for trigger-only), `--field 'arguments=[...]'` and the body on `--stdin`. **New playbooks
default to `status=draft`**: pass `--field status=active` or the shortcut silently falls through. Then tell the user how to invoke it by intent and by shortcut. Flags: `pad help item create --format
md`; the web editor is under `pad server open`, Playbooks, New Playbook.

## Library

`pad library list|get "<exact title>"|activate "<exact title>"` browse and copy Pad's built-in conventions and playbooks; `pad library diff <ref>` and `update <ref>` compare and take newer library
text for a built-in copy (a person decides each; this is what bootstrap `builtin_updates` counts). Software templates seed `plan` and `decompose`; `startup` adds `ship`; every non-blank template seeds
`onboard` as active. Activation check: look for `invocation_slug=<x>, status=active` in bootstrap `playbooks`; `pad playbook show <x>` resolves regardless of status, so it is no check. An entry that
exists as draft or deprecated is reactivated in place (`pad item update PLAYB-N --field status=active`); activating from the library beside it duplicates or fails on the slug.

## Workflows

**Ideation ("let's brainstorm about X").** `pad project dashboard --format json` and `pad item list --format json --limit 20`; `pad item search "X"`; discuss, ask, reference items with `[[Title]]`; at
natural checkpoints offer to save (`pad item create idea "X" --content ...`, or `doc "X" --category decision --stdin` for an architecture decision). Never save without asking.

**Plan ("let's plan X").** Run the `plan` playbook. Not active: point at the library (`pad server open`, Playbooks, Library) and offer to walk goal, scope and breakdown by hand meanwhile.

**Decompose ("break PLAN-2 into tasks", also a SPEC).** Run `decompose` with `target`, optional `dry-run` and `collection` (default tasks); it reconciles children, wires dependencies and confirms each
task.

**Status ("how are we doing?").** `pad project dashboard --format json`; with an active role also `pad item list tasks --role <slug> --assign <user> --format json`. Present: role queue first,
collection summaries, active plan progress, attention items (stalled, overdue), suggested next; offer to dig in.

**Standup.** Done tasks (`pad item list tasks --status done`), in-progress, and dashboard blockers, as Yesterday / Today / Blockers; or `pad project standup`.

**Retro ("plan X is done").** `pad item show PLAN-2 --agent`; `pad item list tasks --all --format json --full` filtered to the plan (`--full` carries the notes a retro needs); write what shipped, what
was deferred, lessons; offer `pad item create doc "Plan N Retrospective" --category retro --stdin` and `pad item update PLAN-2 --status completed --comment "Retro complete, see DOC-N"`.

**Onboarding.** The `onboard` playbook: see [modes.md](modes.md), onboard. "use pad to get IDEA-1" is legacy phrasing for the same; new workspaces have no IDEA-1.
