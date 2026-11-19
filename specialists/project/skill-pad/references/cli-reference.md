---
Title: skill-pad reference: the pad CLI map and traps
Category: reference
Status: current
Authority: canonical
Scope: Every pad command group at v0.19.2 with the commands agents use, how to look up exact flags, and CLI behaviours met in use
Last reviewed: 2026-11-19
Summary: >-
  A map of the 24 command groups and 184 commands of pad v0.19.2, marked by who should run them, plus cmdhelp lookups and traps learned in the
  operator's projects (through v0.21.0). The installed binary is the authority for flags.
---

# The pad CLI

Built from `pad help --all --format json` on v0.19.2 (22e50fe, 2026-11-08), VERIFIED_PRIMARY 2026-11-10. Full dump: [upstream/v0.19.2/cli/pad-cli-reference.md](upstream/v0.19.2/cli/pad-cli-reference.md) (search it; 5,758 lines).

## Contents

- [Looking up flags](#looking-up-flags)
- [Groups](#groups)
- [Global flags and environment](#global-flags-and-environment)
- [Traps](#traps)

## Looking up flags

The repo README's "CLI Reference" (also shown on the GHCR package page) is a 176-line summary of the same tree; on `main` after 0.19.2 it adds `--stdin` to `pad item comment` (not in the 0.19.2
binary; used with 0.21.0, Learned 2026-11-19 below). The binary stays the authority.

`pad help <group> [command] --format md|json|llm` (cmdhelp v0.1, `pad help --capabilities`); `pad <group> <command> --help` for the human form. `pad agent guide <topic>` prints Pad's own agent
guidance for the installed version (`context-loading`, `items`, `before-performing-work`, `role-awareness`, `multi-step-workflows`, `all`).

## Groups

Who: **A** an agent may run it (reads freely; writes after confirmation), **H** a human runs it (auth, interactive, destructive or server-level), **N** never from this skill.

| Group        | Commands                                                                                                              | Who | Notes                                                   |
| ------------ | --------------------------------------------------------------------------------------------------------------------- | --- | ------------------------------------------------------- |
| `bootstrap`  | (one call)                                                                                                            | A   | context load; [workspace-context.md](workspace-context.md) |
| `item`       | create list show update patch edit delete restore search move copy comment(s) note decide claim release remind        | A   | [items-and-edits.md](items-and-edits.md)                |
|              |   ack ...                                                                                                             |     |                                                         |
| `project`    | dashboard next ready stale standup changelog report activity catch-up reconcile watch                                 | A   | read-only views                                         |
| `playbook`   | list show run match                                                                                                   | A   | [playbooks-and-workflows.md](playbooks-and-workflows.md) |
| `library`    | list get activate diff update                                                                                         | A   | `update` only after a person decides                    |
| `collection` | list create update delete archived restore                                                                            | A   | delete and restore are owner-only                       |
| `role`       | list create update delete                                                                                             | A   |                                                         |
| `tag`        | list                                                                                                                  | A   |                                                         |
| `attachment` | list show view upload attach download                                                                                 | A   | never read `~/.pad/attachments/`                        |
| `github`     | link status unlink                                                                                                    | A   | links the current branch's PR to an item                |
| `session`    | status arm disarm register list prune reset activity (hidden: first-connect, should-arm)                              | A   | [modes.md](modes.md)                                    |
| `watch`      | (create) list remove; `--stream --for-session` is the monitor stream                                                  | A   | `scripts/pad_monitor.sh` runs the stream                |
| `push`       | (one call): push an item and instruction to your own armed sessions                                                   | A   | receivers treat it as direction, still confirm          |
| `chat`       | list inbox show send read delete; arm disarm                                                                          | A/N | an agent never runs `chat arm`                          |
| `workspace`  | list init link switch create members invite invitations accept decline join context storage export import deleted     | A/H | init after `pad auth whoami`; invite and import with    |
|              |   restore audit-log claim                                                                                             |     |   the operator                                          |
| `auth`       | whoami (A); login logout setup configure reset-password 2fa timezone (H)                                              | A/H | whoami is the only safe probe                           |
| `init`       | (guided setup)                                                                                                        | H   | needs a terminal and a browser                          |
| `agent`      | status guide (A); install update (N for global targets)                                                               | A/N | would overwrite this skill's links: [upgrade.md](upgrade.md) |
| `mcp`        | status (A); install uninstall serve (H)                                                                               | A/H | [integrations.md](integrations.md)                      |
| `server`     | info open (A); start stop (H)                                                                                         | A/H | the CLI auto-starts the local server                    |
| `db`         | backup (A, read-only copy); restore migrate-to-pg repair-nul release-cloud (H); scan-nul (A)                          | A/H | nightly backup: `scripts/pad_backup.sh`                 |
| `token`      | list (A); create rotate revoke (H)                                                                                    | A/H | a secret shows once: straight to KeePassXC              |
| `webhook`    | list (A); create delete test (H)                                                                                      | A/H | HMAC-signed                                             |
| `completion` | bash zsh fish powershell                                                                                              | H   |                                                         |

## Global flags and environment

- `--format table|json|markdown` (default table; parse with json), `--workspace <slug>` (override `.pad.toml`), `--url <server>`.
- Workspace detection: `.pad.toml` in the folder tree. Config: `~/.pad/config.toml` (here `mode = "local"`, `127.0.0.1:7777`). Data: `~/.pad`, a symlink to `/Volumes/Data/_ai/_tool/tools_stuff/pad` on
  this Mac (pad.db, attachments, sessions, credentials).
- Database: `PAD_DB_PATH` > `PAD_DATA_DIR/pad.db` > `~/.pad/pad.db`; `PAD_DB_DRIVER=postgres` for Postgres.
- `PAD_AGENT=<name>` (or `agent_name` in `.pad.toml`) names the agent under harnesses other than Claude Code.

> **Learned 2026-11-19** · `pad item comment-edit` and `pad_rewrite.py` comment rewrites · VERIFIED_PRIMARY (observed) · Source: Continuum workspace,
> `just rewrite spec.json --apply` (pad_rewrite.py) · Falsifier: the same server accepting `comment-edit` again. The server can stop advertising `item_scoped_comment_writes`; then every comment edit
> fails with "this server does not support editing or deleting comments from the CLI". The same edits had worked that morning. Body rewrites still apply. Fallback that keeps the writing standard: add
> the formatted statement as a new comment (`pad item comment <ref> --stdin`), leave the old one as history; `item-check` then passes because a `DONE:` comment exists.
>
> ```text
> pad_rewrite: pad item comment-edit TASK-26 failed: Error: this server does not support editing or deleting comments from the CLI
> (it does not advertise item_scoped_comment_writes); upgrade the server, or use the web UI
> ```

## Traps

> **Learned 2026-11-19** · Pad CLI v0.21.0 · VERIFIED_PRIMARY · Source: continuum workspace (TASK-164, TASK-171, TD-191); `pad attachment --help` · Falsifier: a later release with
> an attachment delete, comments in `item show --format json`, or a declared priority on Tech Debt. Three traps met closing work: (1) `pad attachment` has no delete or replace (attach, download, list,
> show, upload, view): a wrong file attached stays, so check a log's content before `upload` and, if one slips through, upload the right file and add a `CORRECTION:` comment naming both. (2) `pad item
> show <ref> --format json` carries no comments; list them, with their ids, by `pad item comments <ref> --format json` (needed to rewrite one with `pad_rewrite.py`). (3) `pad item create tech-debt ...
> --priority medium` prints "1 field not declared by this collection's schema, stored as-is: priority": Tech Debt has no priority field in this workspace, so the value is kept but not shown as a
> field. Back-to-back calls also meet `rate_limited` (retry after about 1 s): pause between bulk calls or use the retrying scripts.

> **Learned 2026-11-18** · Pad CLI v0.21.0 · VERIFIED_PRIMARY · Source: `pad collection create "Asks" ... --awaits-human true --tracks-work false` -> `Error: accepts 1 arg(s), received 2`;
> the same with `--awaits-human=true --tracks-work=false` created the collection (continuum workspace) · Falsifier: the space form accepted by a later release. `--awaits-human` and `--tracks-work` are
> string flags in 0.21.0, and the space-separated form is read as extra arguments; write them as `--flag=value`. The README's collection command for Asks uses the space form and needs this change.
> `pad workspace init` in 0.21.0 still writes `.claude/skills/pad/` and `.agents/skills/pad/`, and the copy appears in Claude Code's skill list at once; move them to the Trash (`trash`) and remove the
> empty folders with `rmdir`.

> **Learned 2026-11-18** · Pad CLI v0.21.0 · VERIFIED_PRIMARY · Source: `pad item block TASK-14 TASK-12` printed "TASK-14 ... now blocks TASK-12" (continuum workspace) · Falsifier: the same
> command reporting TASK-12 as the blocker. `pad item block <source> <target>` means source blocks target, the reverse of "block TASK-14 by TASK-12". To say the spike blocks the re-estimate, run `pad
> item block TASK-12 TASK-14`; read the printed sentence, and undo a wrong one with `pad item unblock <source> <target>`.

> **Learned 2026-11-18** · Pad CLI v0.21.0 · VERIFIED_PRIMARY · Source: `pad item list decisions --format json` returned `[]` right after a create; with `--all` it returned the item
> (status `accepted`, a terminal option) · Falsifier: a default list that shows terminal-status items. `pad item list` leaves out items whose status is terminal, so a sync that matches existing items
> must pass `--all` or it creates duplicates. The list JSON carries no body; read it with `pad item show <ref> --format json` (`content`).

> **Learned 2026-11-10** · Pad CLI v0.19.2 · VERIFIED_PRIMARY (unified-network-controller and smc-resiliency) · Source: `pad item update --help`, CLI
> errors · Falsifier: a release that accepts these writes or lists disabled items by default. `pad item update --fields-json` refuses the `convention` key ("system metadata ... BUG-2627"): set
> `trigger`, `status`, `commands` and Pad rewrites its own `convention` block. `pad item list conventions` hides disabled items; add `--all` (a disabled template rule looks deleted). `--fields-json`
> sets a list field (`commands`); `--field key=value` sets strings only. Bare `pad agent install` asks interactively and does nothing with stdin closed: name the tool. `pad workspace init` with an
> authenticated CLI needs no browser; `pad init` does.

> **Learned 2026-11-10** · Pad CLI v0.19.2 · VERIFIED_PRIMARY · Source: `pad agent status` run in this pack's folder, `internal/cli/agents.go` ·
> Falsifier: `pad agent status` reporting the global install from any folder. `pad agent status` reports the skill files of the CURRENT folder (and `pad workspace init` writes `.claude/skills/pad/`
> and `.agents/skills/pad/` into the project), so "installed" there says nothing about `~/.claude/skills/skill-pad`.

> **Learned 2026-11-10** · Pad CLI v0.19.2 · VERIFIED_PRIMARY · Source: `pad session first-connect --help`, `pad session should-arm --help` · Falsifier:
> either command missing from a later release (then [modes.md](modes.md) connect needs a new step). `session first-connect` and `session should-arm` are hidden from `pad help` (marked internal, used by the
> plugin) but run normally.

> **Learned 2026-11-10** · Pad CLI v0.19.2 · VERIFIED_PRIMARY · Source: `pad help collection create --format md` (`--fields`: "use --schema for
> terminal_options"), repo `CLAUDE.md` Data Model (fallback name list), smc-resiliency bootstrap schemas · Falsifier: a collection created with `--fields "status:select:open,answered"` whose
> `answered` items leave `pad project next` and the needs-you inbox. A status select created with the `--fields` DSL has no `terminal_options`, so Pad decides "closed" from a global name list
> (rejected, cancelled, wontfix, duplicate, declined, abandoned, disabled); `answered`, `done`-like custom words stay open forever. Create any workflow collection with `--schema` and set
> `terminal_options` (and `abandoned_options` for values that close without delivering), as the templates do (tasks: done and cancelled; plans: completed).

> **Learned 2026-11-10** · Pad CLI v0.19.2 · VERIFIED_PRIMARY (rate limit, observed) and UNVERIFIED (comment history) · Source: `pad item note`
> burst error `rate_limited` with `retry_after_seconds: 1`; docs_api.md comment edit and delete routes · Falsifier: a burst of 12 notes accepted without a wait; an API or CLI read that returns an
> edited comment's earlier text. Pad rate-limits bursts of writes: back off by `retry_after_seconds` (scripts/pad_rewrite.py retries up to 5 times). `pad item history` keeps item body versions, but
> nothing found keeps the earlier text of an edited comment: save a comment's original as a note before editing it.

> **Learned 2026-11-10** · Pad CLI v0.19.2 · VERIFIED_PRIMARY · Source: `update_conflict` (expected_seq 53, actual 110) after `pad item note`
> writes on the same item · Falsifier: a note that leaves the item's seq unchanged. `pad item note`, `decide` and comment writes move the item's `seq`, so a body update guarded by a seq read before
> them is refused. Write the body first, or re-read the seq (and check the body is unchanged) before the guarded write.

> **Learned 2026-11-10** · Pad v0.19.2 web UI and CLI · VERIFIED_PRIMARY · Source: web/src/lib/components/collections/collection-templates.ts at
> v0.19.2 (mirrored), the operator's screenshot of the New Collection dialog; `pad help collection create` · Falsifier: a `--template` flag on `pad collection create`, or a Feature Requests or Tech
> Debt template that declares terminal_options. The web UI's New Collection dialog offers templates (Blank, Bug Tracker, Feature Requests, Meeting Notes, Decisions, Tech Debt, OKRs, Sprint Backlog,
> Knowledge Base); the CLI has none, so an agent recreates one with `--schema` from that file. Only Bug Tracker declares its closed statuses (fixed, wont-fix); Feature Requests and Tech Debt declare
> none, so add terminal_options (shipped/declined, resolved) or they never close. The schemas used: conventions/collection-schemas/. An agent once answered "Pad has no collection types" from the CLI
> docs alone: check the web UI source before saying a feature does not exist.

> **Learned 2026-11-18** · Pad CLI v0.21.0 · VERIFIED_PRIMARY · Source: `pad help item create --format md` header `version: 0.21.0 (9bc5523 2026-11-18T01:06:08Z)` · Falsifier: `pad --version` below 0.21
> The installed CLI is 0.21.0 while this file maps v0.19.2: `item create` still takes `--field key=value`, `--op-key`, `--status`, `--content`. A new `section` value on a bug renders as its own
> generated heading in the project's bug tracker on the next `pad-trackers --apply` (BUG-185 to 191, unified-network-controller). Refresh the map per references/upgrade.md.

> **Learned 2026-11-18** · Pad CLI v0.21.0 · VERIFIED_PRIMARY · Source: commands run in the smc-resiliency workspace (PLAN-56, TASK-57 to 61, BUG-62 to 68; apn f5c16060) ·
> Falsifier: a create that drops the JSON fields, or `--workspace` writing to the folder's own workspace. A whole run can be put into Pad in a few calls, with every custom field set at create:
>
> ```bash
> pad item create plan "<outcome and date>" --status active --fields-json '{"end_date":"2026-11-20"}' --op-key <key> --content "Serves: ..."
> pad item create task "<verb and object>" --parent PLAN-56 --priority high --tags '["bench"]' --op-key <key> --content "Serves: ..."
> pad item create bug "B18-02 <what was seen>" --fields-json '{"tracker_id":"B18-02","section":"Bench run 2026-11-18","severity":"high","order":20}' --op-key <key> --content "..."
> pad item update TASK-14 --parent PLAN-56 --status in-progress --comment "why"      # moves an existing task under the plan
> pad item list conventions --workspace unified-network-controller                    # read another workspace from any folder
> ```
>
> Practice the operator asked for the same day ("take inspiration from unc workspace", "capture all the information about a ticket"): plan the run in Pad before starting it; file each finding as a bug
> in the other workspace's form (`tracker_id`, `section` for the session, `severity`, `order`; body: what was seen with the evidence path, cause, effect, options, closure); put results on the task
> with `pad item note`, and what was not verified and the state left behind in the same ticket. No visual surface: no screenshot.

> **Learned 2026-11-18** · Pad CLI v0.21.0 · VERIFIED_PRIMARY · Source: `pad item update BUG-196 --title ... --op-key ...` answered `Error: unknown flag: --op-key`; `pad item update --help` lists no
> such flag, `pad item create`, `decide` and `comment` do (unified-network-controller) · Falsifier: an `item update --help` that lists `--op-key`. `item update` takes no `--op-key`, so SKILL.md's
> "pass `--op-key` on writes" cannot be met for an update: a retried update is applied again. Make an update safe to repeat by its content (the same title, body and comment), and guard a body rewrite
> with `--expected-seq`. A code path written in backticks in an item body is exported into the project's tracker file and is then judged by that project's own checks (a short path failed a path check
> there): write full project paths in item bodies, or name the script without backticks. A workspace without an Asks collection holds a question for the operator as a Task under its plan, blocking the
> work it holds up (`pad item block`); the guidelines' Asks collection is created only on the operator's word.

> **Learned 2026-11-19** · Pad CLI v0.21.0 (the pack documents v0.19.2) · VERIFIED_PRIMARY · Source: smc-resiliency session 19 Nov (TASK-71, TASK-55) · Falsifier: an upload of a binary-looking .log accepted, or a comment starting with "-" accepted without `--`.
> - `pad attachment upload` refuses a file sniffed as application/octet-stream (a serial console log with control bytes): strip to printable text first
>   (`LC_ALL=C tr -cd '\11\12\15\40-\176'`) and keep the raw log elsewhere.
> - `pad item comment <ref> "- **What:** ..."` fails ("unknown shorthand flag"): text starting with "-" needs `pad item comment <ref> -- "<text>"`.
> - Body rewrites: `pad item update <ref> --stdin --replace` (a blank stdin is refused, nothing sent).

> **Learned 2026-11-19** · Pad CLI v0.21.0 · VERIFIED_PRIMARY · Source: `pad workspace init skills --template startup` run from the skills_stuff repo root by an agent, no terminal, `pad auth whoami` a real user · Falsifier: the same command opening a browser or waiting for input when signed in
> With a signed-in user it created the workspace and wrote `.pad.toml` (`workspace = "skills"`) without a browser or a prompt, and it still wrote `.claude/skills/pad/SKILL.md` and
> `.agents/skills/pad/SKILL.md` (delete both, Rules). One `.pad.toml` at a repo root serves every folder under it, so a monorepo of packs shares one workspace. The `conventions` recipe split a
> spaced `--trackers` value until it used `[positional-arguments]` and `"$@"` (fixed the same day); the other `*ARGS` recipes still pass `{{ARGS}}` unquoted.
