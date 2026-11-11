---
Title: skill-pad reference: items, safe edits, leases, reminders and attachments
Category: reference
Status: current
Authority: canonical
Scope: Creating, querying, updating and editing Pad items safely from an agent, with the commands for each
Last reviewed: 2026-11-10
Summary: >-
  Extracted from Pad's skill text (v0.19.2) and its development guide: intent-to-command routing for items, status comments, partial patches,
  guarded whole-body writes and idempotency keys, work leases, reminders, notes and decisions, dependencies, attachments, collections and moves.
---

# Items, safe edits, leases, reminders and attachments

Source: Pad v0.19.2 `skills/pad/SKILL.md` (Natural Language Routing, CLI Reference, Key Principles), repo `CLAUDE.md` (CLI), `pad agent guide items`; VERIFIED_PRIMARY 2026-11-10. Exact flags: `pad
help item <command> --format md`.

## Contents

- [Principles](#principles)
- [Intent to command](#intent-to-command)
- [Updating and editing](#updating-and-editing)
- [Claiming work](#claiming-work)
- [Notes, decisions, comments, reminders](#notes-decisions-comments-reminders)
- [Dependencies and moves](#dependencies-and-moves)
- [Attachments](#attachments)
- [Collections](#collections)

## Principles

1. Issue IDs (`TASK-5`, `BUG-8`, `IDEA-12`), never slugs. The CLI prints the ID on create. Collection names take singular forms (`task` = `tasks`).
2. Discuss first; show what will be created or changed and get confirmation. Never save without asking (unless a loaded convention opts into autonomous capture).
3. Read an item before updating it; send only changed fields; confirm the mutation from the returned object before saying it succeeded.
4. Every status change carries `--comment` saying why; same for priority, role and assignee changes. The audit trail is the point.
5. Everything goes through `pad`; never touch `~/.pad/pad.db` or `~/.pad/attachments/` directly.
6. Link related items with `[[Item Title]]` in content (`[[workspace::REF]]` across workspaces). Size an item as one meaningful unit of work (one branch or PR for code); follow the workspace's sizing
   conventions.
7. Prefer summary reads and bounded lists (`--limit`); fetch bodies (`--full`, `--agent`) only when needed.

## Intent to command

| The user says                                             | Run                                                                                           |
| --------------------------------------------------------- | --------------------------------------------------------------------------------------------- |
| "I have an idea for X" / "new task: fix Y" / "document Z" | `pad item create idea\|task\|doc "Title" --content "..."` (match the workspace's collections) |
| "what's on my plate?"                                     | role queue if a role is active, else `pad project next`                                       |
| "what should I work on?" / "what's ready?"                | `pad project ready`                                                                           |
| "what's stuck?" / "what needs attention?"                 | `pad project stale`                                                                           |
| "how are we doing?"                                       | `pad project dashboard`                                                                       |
| "list bugs" / "show all tasks"                            | `pad item list <collection>` (`--status`, `--role`, `--assign`, `--parent`, `--all`)          |
| "find anything about X"                                   | `pad item search "X"`                                                                         |
| "what changed?" / "what did other agents do?"             | `pad project activity [--limit N] [--actor user\|agent] [--since DATE]`                       |
| "catch me up" / "what needs me?"                          | `pad project catch-up` (read-only; marking caught up is web-only)                             |
| "prep for standup"                                        | `pad project standup [--days N]`                                                              |
| "what shipped?" / "generate changelog"                    | `pad project changelog [--days N] [--since DATE] [--parent PLAN-N]`                           |
| "what's blocking us?"                                     | `pad item deps <ref>` over the open items; `pad project reconcile` for stale branch/PR state  |
| "remind me about TASK-5 next Tuesday"                     | `pad item remind TASK-5 --remind-at <RFC3339 instant>` (ask the time of day)                  |
| "open it"                                                 | `pad item open <ref>` (web UI)                                                                |

Completed-work views (`changelog`, `standup`, reports) count terminal minus abandoned statuses (`cancelled`, `wontfix`, `rejected`, ...).

## Updating and editing

- **Fields:** `pad item update <ref> [--status X] [--priority X] [--role X] [--assign X] [--field key=value] --comment "why"`. `--field` is repeatable and schema-aware; a list field (`commands`) needs
  `--fields-json` (skill-pad Learned, 2026-11-10).
- **Part of a body:** `pad item patch <ref> --old "exact text" --new "replacement"` (repeatable; `--edits @file.json` for many or multi-line). Each `--old` must occur exactly once; `pad item show
  <ref> --lines 40-80` numbers lines to quote from. Read the printed diff: anchors fix position, not meaning. `--undo <patch-id>` inverts one, refused if its text changed since. It rebases over other
  writes while anchors match, and works on an item open in a browser editor. `patch_unstable_roundtrip` or `patch_room_open`: use a guarded whole-body update instead.
- **Whole body:** `--stdin` and `--content` REPLACE the body. Read with `pad item show <ref> --agent` (carries `seq` and `content`), edit that text, write `pad item update <ref> --stdin --expected-seq
  <seq>`. A conflict means someone changed it: re-read and re-apply to the CURRENT body; never resend yours. `--replace` overwrites on purpose. Unguarded writes warn now and will be refused in a later
  release.
- **Retries:** every call sends a new idempotency key, so re-running after a timeout can apply twice. Choose `--op-key <k>` before the first attempt and reuse it; on a failed write the CLI prints the
  key it used on stderr. Applies to `create`, `patch`, `comment`, `note`, `decide`, `copy`, `push`.
- `pad item edit <ref>` opens `$EDITOR` (human use); `pad item history <ref>` lists versions; `pad item set-aside <ref>` shows edits an editor upgrade set aside.

> **Learned 2026-11-11** · Pad v0.19.2 web UI · VERIFIED_PRIMARY · Source: github.com/PerpetualSoftware/pad web/src/lib/utils/markdown.ts:224 (`ALLOWED_URI_REGEXP`,
> https?, mailto, ftp, tel) and web/src/lib/components/editor/extensions/safeLink.ts (`openOnClick: false`) at tag v0.19.2 · Falsifier: a vscode:// link that stays clickable in an item page
> Links in an item body: a relative repo link (`../../lab/x.py`) resolves against the Pad page and goes nowhere, and a `vscode://` link is stripped. Write repo links as
> pad_link_opener links (`just link-url <path> --line N`; `pad_tracker.py` converts on import and with `links`, and back on export). Pad has no plugin system.
> A project whose commit gate exports trackers runs `pad_tracker.py links ... --apply` before each export, so a link written later is converted on the
> next commit (smc-resiliency `just pad-trackers`, 2026-11-11).

## Claiming work

Before working an item (not just discussing it): `pad item claim <ref> [--ttl 2h]`. `lease_held` means another agent has it: pick something else, do not retry in a loop. `pad item release <ref>` when
done or blocked. Leases expire (15 minutes by default; re-claim to extend); `project next` and `ready` skip items another holder leased. The lease is keyed on the session's worker id from `pad session
register`; an unregistered session falls back to its agent name.

## Notes, decisions, comments, reminders

- `pad item note <ref> "what you did" [--details ...|--stdin]`: an implementation note, addressed to the record.
- `pad item decide <ref> "what you chose" [--rationale ...|--stdin]`: a decision-log entry; use it when a choice would otherwise live only in chat.
- `pad item comment <ref> "..." [--reply-to <id>]`, `comments`, `comment-edit` (correct your own in place), `comment-delete`: addressed to a person.
- Reminders: `remind --remind-at <RFC3339>` (a bare date is refused on purpose), `reminders`, `ack <reminder-id>`, `unremind`. A fired reminder stays in `project next`/`ready` until acknowledged;
  finishing the item does NOT acknowledge it.
- `pad item star|unstar|starred` for quick access; `pad tag list` for tags in use.

## Dependencies and moves

- `pad item block <src> <tgt>` (src blocks tgt), `blocked-by <src> <tgt>`, `unblock`, `deps <ref>`; also `implements`, `supersedes`, `split-from` with their `un...` forms, `related`, `backlinks`,
  `implemented-by`.
- `pad item move <ref> <collection>` within a workspace: fields the target has no home for are dropped and reported; a move between open, done and abandoned is refused unless the status field is named
  (the CLI prints the hint).
- `pad item copy <ref> --to-workspace <slug> --collection <slug> [--dry-run] [--archive-source]`: across workspaces; preview with `--dry-run`. It never retries; relations and `github_pr` do not carry;
  `[[wiki-links]]` re-resolve in the destination.
- `pad item delete <ref>` archives (soft delete); `pad item restore <ref>` undoes it.

## Attachments

Content references them as `![alt](pad-attachment:<uuid>)` or `[label](pad-attachment:<uuid>)`. Always use the CLI, never `~/.pad/attachments/` (it bypasses ACLs, breaks on Cloud, Postgres and S3, and skips thumbnails, EXIF strip and rotation):

```bash
pad attachment list [--item REF] [--category image|video|audio|document|text|archive|other]
pad attachment show <id>                    # metadata only
IMG=$(pad attachment view <id>)             # bytes to a temp file; prints the path; then open "$IMG" or read it
pad attachment upload <item-ref|-> <path> [--filename "..."]
pad attachment attach <id> <item-ref>       # bind an unattached upload to an item
pad attachment download <id> <out-path>
```

## Collections

`pad collection list` (add `--format json` for `traits`), `create "Name" --fields "key:type[:opts];..."` for simple schemas or `--schema JSON|@file|-` for the full one (`terminal_options`,
`abandoned_options`, defaults, computed and relation fields; the two flags are exclusive), `update <slug>`, `delete` (archives, owner-only), `archived`, `restore`.
