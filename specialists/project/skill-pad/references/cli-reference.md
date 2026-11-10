---
Title: skill-pad reference: the pad CLI map and traps
Category: reference
Status: current
Authority: canonical
Scope: Every pad command group at v0.19.2 with the commands agents use, how to look up exact flags, and CLI behaviours met in use
Last reviewed: 2026-11-10
Summary: >-
  A map of the 24 command groups and 184 commands of pad v0.19.2, marked by who should run them, plus cmdhelp lookups and traps learned in the
  operator's projects. The installed binary is the authority for flags.
---

# The pad CLI

Built from `pad help --all --format json` on v0.19.2 (22e50fe, 2026-11-08), VERIFIED_PRIMARY 2026-11-10. Full dump: [upstream/v0.19.2/cli/pad-cli-reference.md](upstream/v0.19.2/cli/pad-cli-reference.md) (search it; 5,758 lines).

## Contents

- [Looking up flags](#looking-up-flags)
- [Groups](#groups)
- [Global flags and environment](#global-flags-and-environment)
- [Traps](#traps)

## Looking up flags

The repo README's "CLI Reference" (also shown on the GHCR package page) is a 176-line summary of the same tree; on `main` after 0.19.2 it adds
`--stdin` to `pad item comment` (not in the installed binary yet). The binary stays the authority.

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

## Traps

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
> terminal_options"), repo `CLAUDE.md` Data Model (fallback name list), smc-resiliency bootstrap schemas · Falsifier: a collection created with
> `--fields "status:select:open,answered"` whose `answered` items leave `pad project next` and the needs-you inbox.
> A status select created with the `--fields` DSL has no `terminal_options`, so Pad decides "closed" from a global name list (rejected, cancelled,
> wontfix, duplicate, declined, abandoned, disabled); `answered`, `done`-like custom words stay open forever. Create any workflow collection with
> `--schema` and set `terminal_options` (and `abandoned_options` for values that close without delivering), as the templates do (tasks: done and
> cancelled; plans: completed).
