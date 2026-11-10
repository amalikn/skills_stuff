---
cmdhelp_version: "0.1"
binary: pad
version: 0.19.2 (22e50fe 2026-11-08T04:17:17Z)
generated: 2026-11-10T05:32:21Z
---

# pad

Pad — project management for developers and AI agents

Homepage: <https://getpad.dev>

## Global flags

| flag | type | default | description |
| --- | --- | --- | --- |
| `--format` | string | `table` | output format: table, json, markdown |
| `--url` | string |  | server URL override (e.g., https://app.getpad.dev) |
| `--workspace` | string |  | workspace slug override |

## `pad agent`

Install and manage Pad agent skills

### Synopsis

```
pad agent
```

## `pad agent guide`

Print Pad agent guidance on demand

### Synopsis

```
pad agent guide [topic]
```

### Arguments

| name | type | required | description |
| --- | --- | --- | --- |
| `topic` | string | no |  |

### Examples

```bash
pad agent guide playbooks
```

## `pad agent install`

Install the /pad skill for your AI coding tools

Install the Pad skill file for AI coding tools.

With no arguments, auto-detects tools in use and offers to install for each.
Specify a tool name to install for that tool directly.

Supported tools:
  claude       Claude Code (.claude/skills/)
  cursor       Cursor (.agents/skills/) — also covers Codex, Windsurf & OpenCode
  codex        OpenAI Codex (.agents/skills/)
  windsurf     Windsurf (.agents/skills/)
  opencode     OpenCode (.agents/skills/)
  copilot      GitHub Copilot (.github/instructions/)
  amazon-q     Amazon Q Developer (.amazonq/rules/)
  junie        JetBrains Junie (.junie/guidelines/)

### Synopsis

```
pad agent install [tool] [flags]
```

### Arguments

| name | type | required | description |
| --- | --- | --- | --- |
| `tool` | enum: claude\|agents\|codex\|cursor\|windsurf\|opencode\|copilot\|github-copilot\|amazon-q\|amazonq\|q\|junie | no |  |

### Flags

| flag | type | default | description |
| --- | --- | --- | --- |
| `--all` | bool |  | install for all detected tools |
| `--force` | bool |  | replace a skill file even when it was edited or written by a newer pad (BUG-3466) |
| `--list` | bool |  | list supported tools and installation status |
| `--update` | bool |  | update all installed tool integrations |

### Examples

```bash
pad agent install
```

```bash
pad agent install claude
```

```bash
pad agent install cursor
```

```bash
pad agent install opencode
```

```bash
pad agent install --all
```

```bash
pad agent status
```

## `pad agent status`

Show installed Pad skill status across supported tools

### Synopsis

```
pad agent status
```

### Examples

```bash
pad agent status
```

## `pad agent update`

Update installed Pad skills across all supported tools

### Synopsis

```
pad agent update [flags]
```

### Flags

| flag | type | default | description |
| --- | --- | --- | --- |
| `--force` | bool |  | replace a skill file even when it was edited or written by a newer pad (BUG-3466) |

### Examples

```bash
pad agent update
```

## `pad attachment`

Upload, download, view, and list item attachments

Upload, download, view, and list attachments (images, files) on items.

Attachments belong to a workspace and may optionally reference an item.
Pass "-" as the item argument to upload without associating with any item.
An unattached image does not render on share pages even when an item embeds
it, because a share serves only attachments its items own. Prefer uploading
to the item; "pad attachment attach" fixes one after the fact.

For agents: ALWAYS use these CLI commands to read attachments — never read
directly from ~/.pad/attachments/. The CLI goes through the authenticated
REST API, which works on local SQLite, Pad Cloud, and remote/Postgres
deployments and respects workspace ACLs.

### Synopsis

```
pad attachment
```

### Examples

```bash
pad attachment list
```

```bash
pad attachment list --item TASK-5
```

```bash
pad attachment list --category image --limit 20
```

```bash
pad attachment show <attachment-id>
```

```bash
pad attachment view <attachment-id>
```

```bash
pad attachment view <attachment-id> -o ./pic.png
```

```bash
pad attachment upload TASK-5 ./screenshot.png
```

```bash
pad attachment attach <attachment-id> TASK-5
```

```bash
pad attachment download <attachment-id> ./pic.png
```

## `pad attachment attach`

Attach an unattached attachment to an item

Attach an attachment that was uploaded without an item ("upload -") to an item.

Share pages serve only attachments the shared item owns, so an unattached image
an item embeds renders as a placeholder there until it is attached to that item.

Only an unattached attachment can be attached; one that already belongs to an
item is refused, never moved. You must be able to edit the item, and you must
have uploaded the attachment or be a workspace owner.

### Synopsis

```
pad attachment attach <attachment-id> <item-ref>
```

### Arguments

| name | type | required | description |
| --- | --- | --- | --- |
| `attachment-id` | string | yes |  |
| `item-ref` | string | yes |  |

### Examples

```bash
pad attachment attach 3f2a9c1e-... TASK-5
```

## `pad attachment download`

Download an attachment by ID

Download the bytes of an attachment by its UUID. Pass "-" as the out
path to stream to stdout (useful for piping into image viewers etc.).

### Synopsis

```
pad attachment download <attachment-id> <out-path> [flags]
```

### Arguments

| name | type | required | description |
| --- | --- | --- | --- |
| `attachment-id` | string | yes |  |
| `out-path` | string | yes |  |

### Flags

| flag | type | default | description |
| --- | --- | --- | --- |
| `--variant` | string |  | request a derived variant (thumb-sm \| thumb-md) |

### Examples

```bash
pad attachment download <id> ./screenshot.png
```

```bash
pad attachment download <id> --variant thumb-sm ./thumb.png
```

```bash
pad attachment download <id> -  | open -f -a Preview
```

## `pad attachment list`

List attachments in the workspace

List attachments in the current workspace, with optional
filters. Returns the same fields the web UI uses (id, mime, size,
filename, parent item, collection, created_at).

The --item flag accepts an item ref (TASK-5) or slug; the CLI
resolves it to a UUID before calling the API.

### Synopsis

```
pad attachment list [flags]
```

### Flags

| flag | type | default | description |
| --- | --- | --- | --- |
| `--attached` | bool |  | only attachments associated with an item |
| `--category` | string |  | filter by MIME category: image\|video\|audio\|document\|text\|archive\|other |
| `--collection` | string |  | filter by collection UUID |
| `--item` | string |  | filter to attachments on a specific item (ref or slug) |
| `--limit` | int |  | page size (1-200, default 50) |
| `--offset` | int |  | page offset |
| `--sort` | string |  | sort: size\|size_desc\|filename\|filename_desc\|created_at\|created_at_desc (default created_at_desc) |
| `--unattached` | bool |  | only orphan attachments (no parent item) |

### Examples

```bash
pad attachment list
```

```bash
pad attachment list --item TASK-5
```

```bash
pad attachment list --category image --limit 20
```

```bash
pad attachment list --unattached
```

```bash
pad attachment list --format json
```

## `pad attachment show`

Show attachment metadata (size, MIME, filename) without downloading

Issue a HEAD request and print the attachment's MIME type,
size, filename, ETag, and Last-Modified — without transferring the
bytes. Useful to confirm an attachment exists, or to size a
download before committing to it.

### Synopsis

```
pad attachment show <attachment-id> [flags]
```

### Arguments

| name | type | required | description |
| --- | --- | --- | --- |
| `attachment-id` | string | yes |  |

### Flags

| flag | type | default | description |
| --- | --- | --- | --- |
| `--variant` | string |  | request a derived variant (thumb-sm \| thumb-md) |

### Examples

```bash
pad attachment show <id>
```

```bash
pad attachment show <id> --format json
```

```bash
pad attachment show <id> --variant thumb-sm
```

## `pad attachment upload`

Upload a file as an item attachment

Upload a file. The first argument is the parent item (issue ref or slug).
Use "-" to upload without associating with any item. Prefer the item: an
unattached image does not render on share pages even when an item embeds it,
because a share serves only attachments its items own. To fix one afterwards,
run "pad attachment attach <attachment-id> <item-ref>".

### Synopsis

```
pad attachment upload <item-ref-or-dash> <path> [flags]
```

### Arguments

| name | type | required | description |
| --- | --- | --- | --- |
| `item-ref-or-dash` | string | yes |  |
| `path` | string | yes |  |

### Flags

| flag | type | default | description |
| --- | --- | --- | --- |
| `--filename` | string |  | override the stored filename (defaults to basename of path) |

### Examples

```bash
pad attachment upload TASK-5 ./screenshot.png
```

```bash
pad attachment upload - ./standalone.pdf
```

```bash
pad attachment upload TASK-5 ./design.pdf --filename "Design v2.pdf"
```

## `pad attachment view`

Fetch an attachment to a file and print its path

Fetch an attachment by UUID through the authenticated REST API
and save it to disk. Prints the absolute path of the saved file on
stdout — designed for agents to use as $(pad attachment view <id>).

With no -o flag, the file lands in a fresh OS temp directory. The
filename starts from the attachment's Content-Disposition header,
reduced to a safe local path component (whitespace trimmed, path
separators and dot-only or trailing-dot forms removed — stricter
than what the server stores, because this name is written to YOUR
filesystem); when the result has no extension, the canonical
extension for the attachment's MIME type is appended so viewers
that dispatch on extension still open it. An unusable name falls
back to the attachment id, reduced the same way.

With -o <path>, the file is written to that path using the same
atomic temp-then-rename strategy as 'pad attachment download'.

This is the recommended way for AI agents (Claude Code, Cursor, etc.)
to view attachments referenced in item content as
![alt](pad-attachment:<uuid>). It works for every Pad install
(local SQLite, Pad Cloud, remote/Postgres) and respects workspace
ACLs. Reading directly from ~/.pad/attachments/ does NOT — never
do that.

### Synopsis

```
pad attachment view <attachment-id> [flags]
```

### Arguments

| name | type | required | description |
| --- | --- | --- | --- |
| `attachment-id` | string | yes |  |

### Flags

| flag | type | default | description |
| --- | --- | --- | --- |
| `--output` | string |  | save to this path instead of an OS temp file |
| `--variant` | string |  | request a derived variant (thumb-sm \| thumb-md) |

### Examples

```bash
pad attachment view <id>
```

```bash
pad attachment view <id> -o ./screenshot.png
```

```bash
pad attachment view <id> --variant thumb-md
```

```bash
pad attachment view <id> --format json
```

## `pad auth`

Configure authentication and account access

### Synopsis

```
pad auth
```

## `pad auth 2fa`

Manage two-factor authentication for your account

### Synopsis

```
pad auth 2fa
```

## `pad auth 2fa disable`

Turn off two-factor authentication

Turn off two-factor authentication.

An account with a password confirms with the password. An account without
one (signed up with GitHub, Google or Apple) confirms with a code from the
authenticator app or a recovery code. Turning 2FA off signs out your other
sessions; this one is kept.

### Synopsis

```
pad auth 2fa disable
```

### Examples

```bash
pad auth 2fa disable
```

## `pad auth 2fa setup`

Turn on two-factor authentication (authenticator app)

Turn on two-factor authentication.

Pad shows an otpauth:// URI and its secret for your authenticator app, asks
for a code from the app, and then prints your recovery codes. The recovery
codes are shown once: store them somewhere safe.

### Synopsis

```
pad auth 2fa setup
```

### Examples

```bash
pad auth 2fa setup
```

## `pad auth configure`

Configure how this Pad client connects to a server

Configure how this Pad client connects to a server.

Modes:
  cloud   This client connects to your Pad Cloud account at https://app.getpad.dev.
          Managed, OAuth sign-in, no setup. Recommended.
  local   This client manages a local Pad server on this machine.
  remote  This client connects to your own self-hosted Pad server by base URL.

### Synopsis

```
pad auth configure [flags]
```

### Flags

| flag | type | default | description |
| --- | --- | --- | --- |
| `--host` | string |  | local server host override for local mode |
| `--mode` | string |  | connection mode: cloud, local, remote |
| `--port` | int |  | local server port override for local mode |
| `--url` | string |  | server base URL for remote mode |

### Examples

```bash
pad auth configure --mode remote --url https://pad.example.com
```

## `pad auth login`

Log in to Pad

### Synopsis

```
pad auth login [flags]
```

### Flags

| flag | type | default | description |
| --- | --- | --- | --- |
| `--interactive` | bool |  | Use email/password prompt instead of browser-based login |

### Examples

```bash
pad auth login
```

## `pad auth logout`

Log out of Pad

### Synopsis

```
pad auth logout
```

### Examples

```bash
pad auth logout
```

## `pad auth reset-password`

Recover a locked-out account from the server host

Recover an account when you're locked out and email isn't configured.

Run this ON THE SERVER HOST. It talks to the local Pad instance over
loopback — the same trust model as 'pad auth setup' — so it needs no
login (the whole point is that you can't log in). The endpoint refuses
proxied or remote requests and is disabled entirely in cloud mode.

By default it prints a single-use reset link; open it in a browser to
choose a new password. Use --temp-password to instead set a random
temporary password printed to this terminal — handy on a headless box.
Rotate it right after you log in.

### Synopsis

```
pad auth reset-password <email> [flags]
```

### Arguments

| name | type | required | description |
| --- | --- | --- | --- |
| `email` | string | yes |  |

### Flags

| flag | type | default | description |
| --- | --- | --- | --- |
| `--temp-password` | bool |  | Set a random temporary password instead of printing a reset link |

### Examples

```bash
pad auth reset-password alex@example.com
```

## `pad auth setup`

Initialize a fresh Pad instance with the first admin account

Initialize a fresh Pad instance with the first admin account.

By default the CLI hands the operator a deep link into the browser-based
/setup form (which uses password managers, HTML5 email validation, and the
live strength meter). If the browser path won't work — headless server
without an SSH tunnel, broken X11, etc. — re-run with --cli-prompt for the
legacy in-terminal email/name/password prompts, or supply --email/--name/
--password for fully non-interactive (agent) use.

### Synopsis

```
pad auth setup [flags]
```

### Flags

| flag | type | default | description |
| --- | --- | --- | --- |
| `--cli-prompt` | bool |  | Use the legacy in-terminal email/name/password prompts instead of the browser /setup flow. |
| `--email` | string |  | Admin email address (headless bootstrap — requires --name and --password) |
| `--name` | string |  | Admin display name (headless bootstrap — requires --email and --password) |
| `--password` | string |  | Admin password (headless bootstrap — requires --email and --name) |

### Examples

```bash
pad auth setup
```

## `pad auth timezone`

Show or set your IANA time zone

### Synopsis

```
pad auth timezone [zone]
```

### Arguments

| name | type | required | description |
| --- | --- | --- | --- |
| `zone` | string | no |  |

### Examples

```bash
pad auth timezone America/New_York
```

## `pad auth whoami`

Show current user info

### Synopsis

```
pad auth whoami
```

### Examples

```bash
pad auth whoami
```

## `pad bootstrap`

Print the agent bootstrap blob (workspace + collections + conventions + roles + playbooks + dashboard) in one round-trip

Print the consolidated agent bootstrap blob for the current workspace.

The blob carries everything the /pad skill needs to start a session:

  - Workspace identity (slug, name, id)
  - The calling user (name, email, id)
  - Collections (with schemas)
  - Always-on, active conventions (full body — must-follow rules)
  - Convention index (METADATA ONLY — every active convention by
    trigger, so triggered rules are discoverable; bodies load on demand)
  - Agent roles
  - Playbooks (METADATA ONLY — full bodies load on invocation)
  - Dashboard (active items, attention, suggested next)
  - Recent activity (last 24h, capped)

Use --format json for machine consumption (default). Use --format markdown
for a readable summary.

### Synopsis

```
pad bootstrap
```

### Examples

```bash
pad bootstrap --format json
```

## `pad chat`

Chat with agents across workspaces

Global chat. Targets are C<n>, <n>, or @<name> for your DM with an agent.

### Synopsis

```
pad chat
```

## `pad chat arm`

Accept chat instructions for this session

### Synopsis

```
pad chat arm [flags]
```

### Flags

| flag | type | default | description |
| --- | --- | --- | --- |
| `--accept-instructions` | bool |  | Allow human chat messages to drive this agent for this session |

### Examples

```bash
pad chat arm --accept-instructions
```

## `pad chat delete`

Delete one of your chat messages

### Synopsis

```
pad chat delete <target> <seq>
```

### Arguments

| name | type | required | description |
| --- | --- | --- | --- |
| `target` | string | yes |  |
| `seq` | string | yes |  |

### Examples

```bash
pad chat delete C12 4
```

## `pad chat disarm`

Treat chat as information again

### Synopsis

```
pad chat disarm
```

### Examples

```bash
pad chat disarm
```

## `pad chat inbox`

Show unread chat counts

### Synopsis

```
pad chat inbox [flags]
```

### Flags

| flag | type | default | description |
| --- | --- | --- | --- |
| `--agent` | string |  | Filter by agent key |

### Examples

```bash
pad chat inbox --agent rook
```

## `pad chat list`

List your global chat conversations

### Synopsis

```
pad chat list
```

### Examples

```bash
pad chat list
```

## `pad chat read`

Mark chat read through a message sequence

### Synopsis

```
pad chat read <target> [flags]
```

### Arguments

| name | type | required | description |
| --- | --- | --- | --- |
| `target` | string | yes |  |

### Flags

| flag | type | default | description |
| --- | --- | --- | --- |
| `--to` | int |  | Mark read through this sequence |

### Examples

```bash
pad chat read C12 --to 4
```

## `pad chat send`

Send a chat message (- reads stdin)

### Synopsis

```
pad chat send <target> <body> [flags]
```

### Arguments

| name | type | required | description |
| --- | --- | --- | --- |
| `target` | string | yes |  |
| `body` | string | yes |  |

### Flags

| flag | type | default | description |
| --- | --- | --- | --- |
| `--context-workspace` | string |  | Workspace for resolving message references (defaults to cwd link) |
| `--op-key` | string |  | Caller-owned idempotency key |
| `--reply-to` | int |  | Reply to this message sequence (marks read through this sequence) |

### Examples

```bash
pad chat send @rook "Ready for review"
```

## `pad chat show`

Show chat messages and mark read when no unread messages are skipped

### Synopsis

```
pad chat show <target> [flags]
```

### Arguments

| name | type | required | description |
| --- | --- | --- | --- |
| `target` | string | yes |  |

### Flags

| flag | type | default | description |
| --- | --- | --- | --- |
| `--limit` | int | `50` | Maximum messages to return |
| `--no-mark` | bool |  | Do not mark returned messages read |
| `--since` | int |  | Show messages after this sequence |

### Examples

```bash
pad chat show C12 --since 4
```

## `pad collection`

List, create, update, and delete collections

### Synopsis

```
pad collection
```

## `pad collection archived`

List archived collections and their item counts (owner-only)

### Synopsis

```
pad collection archived
```

### Examples

```bash
pad collection archived
```

## `pad collection create`

Create a custom collection

Create a new collection with custom fields.

Two ways to define the schema:

  --fields  Compact DSL for the simple case: key:type[:option1,option2,...]
            Separate multiple fields with semicolons. Does not support
            terminal_options, custom defaults, computed fields, or suffixes.

            For a relation the third part is the TARGET COLLECTION slug
            rather than an options list, and it is required:
              owner:relation:people
            A relation with no target is refused, because such a field
            cannot accept any value.

  --schema  Full CollectionSchema JSON for everything else. Accepts:
              inline JSON:  --schema '{"fields":[...]}'
              file path:    --schema @./schema.json
              stdin:        --schema -

  --fields and --schema are mutually exclusive.

Tip: if you omit "label" on a --schema field, the CLI auto-fills it from
the key using Title Case (e.g. "due_date" → "Due Date") — matching what
the --fields DSL does. Set "label" explicitly when you want a custom display name.

### Synopsis

```
pad collection create <name> [flags]
```

### Arguments

| name | type | required | description |
| --- | --- | --- | --- |
| `name` | string | yes |  |

### Flags

| flag | type | default | description |
| --- | --- | --- | --- |
| `--awaits-human` | string |  | true: the collection's items are asks of a person, routed to their assignee's needs-you list; false: an ordinary collection. Default: false |
| `--board-group-by` | string | `status` | field to group by in board view |
| `--default-view` | string | `board` | default view type: list, board, table |
| `--description` | string |  | collection description |
| `--fields` | string |  | field definitions DSL (key:type[:options]; ...); use --schema for terminal_options, computed, defaults, etc. |
| `--icon` | string |  | collection emoji icon |
| `--layout` | string | `fields-primary` | item detail layout: fields-primary, content-primary, balanced |
| `--schema` | string |  | full CollectionSchema JSON: inline, @path, or - for stdin; mutually exclusive with --fields |
| `--tracks-work` | string |  | true: items count as work (progress, parent completion, Insights); false: reference material. Default: work when the done field can finish |

### Examples

```bash
pad collection create "Bugs" --fields "status:select:new,triaged,fixing,resolved;severity:select:low,medium,high,critical;component:text"
```

```bash
pad collection create "Decisions" --icon "⚖️" --fields "status:select:proposed,accepted,rejected;impact:select:low,medium,high"
```

```bash
pad collection create "Reviews" --fields "status:select:open,done;reviewer:relation:people"
```

```bash
pad collection create "Asks" --awaits-human --fields "status:select:open,done"
```

```bash
pad collection create "Marketing" --schema '{"fields":[{"key":"status","label":"Status","type":"select","options":["idea","drafting","review","published","archived"],"terminal_options":["published","archived"],"default":"idea","required":true}]}'
```

```bash
pad collection create "Marketing" --schema @./marketing-schema.json
```

```bash
cat schema.json | pad collection create "Marketing" --schema -
```

## `pad collection delete`

Archive a non-default collection and hide its items (owner-only; restore with 'pad collection restore')

Soft-delete a collection by slug.

Constraints:
  - Workspace owner role required.
  - Cannot delete a default collection (template-seeded ones are
    marked is_default=true). For seeded collections, use
    'pad collection update' to adapt them (rename, reshape schema,
    swap icon) instead.
  - Items in the collection are NOT deleted — they stay in the
    database, hidden with the collection.
  - Reversible: 'pad collection archived' lists archived collections
    and 'pad collection restore <slug>' brings one back with its items
    (TASK-2189).

### Synopsis

```
pad collection delete <slug>
```

### Arguments

| name | type | required | description |
| --- | --- | --- | --- |
| `slug` | string | yes |  |

### Examples

```bash
pad collection delete experiments
```

## `pad collection list`

List collections with item counts

### Synopsis

```
pad collection list
```

### Examples

```bash
pad collection list
```

## `pad collection restore`

Restore an archived collection, with its items (owner-only)

Restore an archived collection by its slug (or id). Its items come back
with it: archiving never deleted them. See 'pad collection archived'.

### Synopsis

```
pad collection restore <slug>
```

### Arguments

| name | type | required | description |
| --- | --- | --- | --- |
| `slug` | string | yes |  |

### Examples

```bash
pad collection restore experiments
```

## `pad collection update`

Update an existing collection

Update an existing collection's name, icon, description, prefix,
schema, or sort order.

Only flags you explicitly set are sent — every other property is left
untouched. Use this to rename collections, swap icons, or reshape the
schema (e.g. change status enum options or add/remove fields).

The --schema and --fields flags accept the same input modes as
'pad collection create':

  --fields  Compact DSL for the simple case: key:type[:option1,option2,...]
  --schema  Full CollectionSchema JSON: inline, @path, or - for stdin

Collections can be referenced by slug (e.g. 'tasks') only — there is no
issue-ID equivalent for collections themselves.

### Synopsis

```
pad collection update <slug> [flags]
```

### Arguments

| name | type | required | description |
| --- | --- | --- | --- |
| `slug` | string | yes |  |

### Flags

| flag | type | default | description |
| --- | --- | --- | --- |
| `--awaits-human` | string |  | true: the collection's items are asks of a person, routed to their assignee's needs-you list; false: an ordinary collection |
| `--description` | string |  | new description (use empty string to clear) |
| `--fields` | string |  | replacement schema via DSL: "key:type[:options]; ..." |
| `--icon` | string |  | new emoji icon (use empty string to clear) |
| `--name` | string |  | new display name |
| `--prefix` | string |  | new issue-ID prefix (e.g. TASK, BUG) |
| `--schema` | string |  | replacement CollectionSchema JSON: inline, @path, or - for stdin |
| `--sort-order` | int |  | new sort order (lower = appears first) |
| `--tracks-work` | string |  | true: items count as work (progress, parent completion, Insights); false: the collection is reference material |

### Examples

```bash
pad collection update tasks --name Issues --icon 🎯
```

```bash
pad collection update conventions --description "Updated rules"
```

```bash
pad collection update bugs --schema @./new-bug-schema.json
```

```bash
pad collection update tasks --fields "status:select:open,doing,done;priority:select:high,medium,low"
```

```bash
pad collection update human-tasks --awaits-human
```

```bash
pad collection update human-tasks --awaits-human=false
```

## `pad completion`

Generate shell completion scripts

Generate shell completion scripts for your shell.

Usage:
  source <(pad completion bash)
  pad completion zsh > "${fpath[1]}/_pad"
  pad completion fish | source

### Synopsis

```
pad completion [value]
```

### Arguments

| name | type | required | description |
| --- | --- | --- | --- |
| `value` | enum: bash\|zsh\|fish\|powershell | no |  |

### Examples

```bash
pad completion bash
```

```bash
pad completion zsh
```

```bash
pad completion fish
```

```bash
pad completion powershell
```

## `pad db`

Database backup, restore, repair, and migration tools

### Synopsis

```
pad db
```

## `pad db backup`

Back up the database

Creates a backup of the Pad database.

For PostgreSQL (PAD_DB_DRIVER=postgres): creates a SQL dump using pg_dump.
For SQLite (default): writes an online-safe single-file backup via VACUUM INTO —
safe to run while the server is live. The database path is resolved the same way
the server resolves it (PAD_DB_PATH > PAD_DATA_DIR/pad.db > ~/.pad/pad.db).

### Synopsis

```
pad db backup [flags]
```

### Flags

| flag | type | default | description |
| --- | --- | --- | --- |
| `--cron` | bool |  | cron mode: structured log output, no interactive messages |
| `--output` | string |  | output file path (default: pad-backup-YYYYMMDD-HHMMSS.db or .sql) |

### Examples

```bash
pad db backup --output pad-backup.db
```

## `pad db migrate-to-pg`

Migrate data from SQLite to PostgreSQL

One-time migration from a SQLite database to PostgreSQL.
Uses application-level export/import to transfer all workspace data.

This reads each workspace from the SQLite database and imports it into
the PostgreSQL database. Users, platform settings, and auth data are
NOT migrated — only workspace content (collections, items, comments,
links, versions).

Steps:
  1. Set up a fresh PostgreSQL database
  2. Run 'pad server start' with PAD_DB_DRIVER=postgres once to create the schema
  3. Stop the server
  4. Run this command to migrate workspace data

### Synopsis

```
pad db migrate-to-pg [flags]
```

### Flags

| flag | type | default | description |
| --- | --- | --- | --- |
| `--discard-unflushed-edits` | bool |  | migrate even though some items have edits only in the collaborative op-log, permanently losing them |
| `--force` | bool |  | migrate even though a Pad server appears to be running, OR the config needed to check for one could not be read (an edit made during the migration may be lost) |
| `--from` | string |  | SQLite database path (default: server-resolved — PAD_DB_PATH > PAD_DATA_DIR/pad.db > ~/.pad/pad.db) |
| `--to` | string |  | PostgreSQL connection URL (default: PAD_DATABASE_URL) |

### Examples

```bash
pad db migrate-to-pg --to postgres://pad@localhost:5432/pad
```

## `pad db release-cloud`

Let a self-hosted boot convert this database's free users to self-hosted (moving off Pad Cloud)

Records that this database is deliberately leaving Pad Cloud, so the next
non-cloud boot converts free and empty plans to self-hosted (no limits).

A database a cloud-mode server has booted is marked cloud-owned, and a
non-cloud boot leaves its plans alone (TASK-3551). Run this on the server
host, against the database the server uses. It refuses while users carry
Pad Cloud billing state (a Stripe plan source or customer id) unless
--force. A later cloud-mode boot marks the database cloud-owned again.

### Synopsis

```
pad db release-cloud [flags]
```

### Flags

| flag | type | default | description |
| --- | --- | --- | --- |
| `--force` | bool |  | release even though users carry Pad Cloud billing state |

### Examples

```bash
pad db release-cloud
```

```bash
pad db release-cloud --force
```

## `pad db repair-nul`

Replace stored NULs and invalid UTF-8 with U+FFFD (rewrites user content)

Rewrites every stored value 'pad db scan-nul' reports, replacing each NUL,
and each invalid UTF-8 byte sequence, with U+FFFD (the Unicode replacement
character) and leaving the rest of the value byte for byte as it was. In a valid
JSON document an invalid byte can only sit inside a string, so the document
stays valid JSON with that string's bad bytes replaced; a value that was not
valid JSON to begin with is not made valid by this.

THIS CHANGES USER CONTENT. It is a separate command, and never part of a
migration, for that reason: a migration that rewrote stored text would decide
on the operator's behalf. Every value it changes is listed.

Run 'pad db scan-nul' first to see what would change — that is the dry run, so
this command has no --dry-run of its own. Running it twice is safe: the second
pass finds nothing to do.

A row whose PRIMARY KEY carries the NUL is reported and left alone, because
repairing it would change the row's identity and could collide with another
row.

### Synopsis

```
pad db repair-nul [flags]
```

### Flags

| flag | type | default | description |
| --- | --- | --- | --- |
| `--force` | bool |  | skip the confirmation prompt and the running-server check |
| `--from` | string |  | SQLite database path (default: server-resolved) |

### Examples

```bash
pad db repair-nul
```

## `pad db restore`

Restore a database from a backup

Restores a Pad database from a backup created by 'pad db backup'.

For PostgreSQL: restores in one transaction using psql, stopping on SQL errors
and ignoring psql startup files. Requires PAD_DATABASE_URL.
For SQLite (default): stages and checks the backup before atomically replacing
the live database after checkpointing existing WAL data. The database path
is resolved the same way the server resolves it (PAD_DB_PATH > PAD_DATA_DIR/pad.db
> ~/.pad/pad.db). Stop the server first — restore refuses to run while it detects
a live server (a running WAL checkpoint could clobber the restored file); use
--force to override.

WARNING: This will overwrite the current database contents.

### Synopsis

```
pad db restore <file> [flags]
```

### Arguments

| name | type | required | description |
| --- | --- | --- | --- |
| `file` | string | yes |  |

### Flags

| flag | type | default | description |
| --- | --- | --- | --- |
| `--force` | bool |  | skip confirmation prompt |

### Examples

```bash
pad db restore pad-backup.db
```

## `pad db scan-nul`

Report stored values PostgreSQL refuses: a NUL, or invalid UTF-8 (read-only)

Counts and locates every stored value that violates Pad's NUL invariant:
a real NUL byte in any protected column, or a JSON escape in a JSON column
that a JSON parser would decode to one. It also reports every value that is
not valid UTF-8. That is not a NUL, but PostgreSQL refuses it too (SQLSTATE
22021 under a UTF8 database), so it breaks a migration in the same way.

Finding invalid UTF-8 means reading every stored value in full, since SQLite
has no way to test for it in a query; on a large database that takes about as
long as reading the database once.

Such rows can only have been written by a binary older than the enforcement
that now refuses them. They are not cosmetic: their workspace exports fine and
re-imports with a 400, and 'pad db migrate-to-pg' fails partway through the
copy against PostgreSQL. A SQL_ASCII PostgreSQL would accept the invalid-UTF-8
bytes; they are reported anyway, because nothing on the Pad side can tell which
encoding a later migration will target.

The scan itself only reads. Opening the database does apply any pending schema
migrations, exactly as starting the server does — pass --from to inspect a
backup file instead of the live database.

Nothing is repaired. Run 'pad db repair-nul' for that.

### Synopsis

```
pad db scan-nul [flags]
```

### Flags

| flag | type | default | description |
| --- | --- | --- | --- |
| `--from` | string |  | SQLite database path (default: server-resolved — PAD_DB_PATH > PAD_DATA_DIR/pad.db > ~/.pad/pad.db) |

### Examples

```bash
pad db scan-nul
```

## `pad github`

Link GitHub pull requests to Pad items

Link GitHub pull requests to Pad items and view their status.

Requires the GitHub CLI (gh) to be installed: https://cli.github.com/

### Synopsis

```
pad github
```

### Examples

```bash
pad github link TASK-5
```

```bash
pad github link
```

```bash
pad github status
```

```bash
pad github status TASK-5
```

```bash
pad github unlink TASK-5
```

## `pad github link`

Link the current branch's PR to a Pad item

Link the current branch's GitHub pull request to a Pad item.

If no item ref is provided, attempts to auto-detect from the branch name.
For example, branch "fix/TASK-5-oauth-bug" would auto-link to TASK-5.

### Synopsis

```
pad github link [item-ref] [flags]
```

### Arguments

| name | type | required | description |
| --- | --- | --- | --- |
| `item-ref` | string | no |  |

### Flags

| flag | type | default | description |
| --- | --- | --- | --- |
| `--pr-branch` | string |  | the PR's head branch, with --pr-number |
| `--pr-number` | int |  | link this PR number instead of the current branch's (with --pr-url; nothing is fetched from GitHub) |
| `--pr-repo` | string |  | the PR's repository (owner/name), with --pr-number |
| `--pr-state` | string |  | the PR's state (e.g. open, merged, closed), with --pr-number |
| `--pr-title` | string |  | the PR's title, with --pr-number |
| `--pr-url` | string |  | the PR's URL, with --pr-number |

### Examples

```bash
pad github link TASK-5
```

```bash
pad github link fix-oauth-bug
```

```bash
pad github link
```

```bash
pad github link TASK-5 --pr-number 42 --pr-url https://github.com/acme/app/pull/42 --pr-state open
```

## `pad github status`

Show GitHub PR status for linked items

Show the GitHub PR status for one or all items that have linked PRs.

### Synopsis

```
pad github status [item-ref]
```

### Arguments

| name | type | required | description |
| --- | --- | --- | --- |
| `item-ref` | string | no |  |

### Examples

```bash
pad github status
```

```bash
pad github status TASK-5
```

## `pad github unlink`

Remove the GitHub PR link from an item

### Synopsis

```
pad github unlink <item-ref>
```

### Arguments

| name | type | required | description |
| --- | --- | --- | --- |
| `item-ref` | string | yes |  |

### Examples

```bash
pad github unlink TASK-5
```

## `pad init`

Set up Pad — configure, authenticate, and create a workspace

Initialize Pad for this project. This smart command detects what's needed and
walks you through each step:

  1. Configure connection (local server, remote, or Docker)
  2. Start local server if needed
  3. Create the first admin account (fresh installs)
  4. Log in if not authenticated
  5. Create or link a workspace for the current directory
  6. Install/update the /pad skill for detected AI tools

Safe to re-run anytime — it skips steps that are already done and shows
your current status.

### Synopsis

```
pad init [name] [flags]
```

### Arguments

| name | type | required | description |
| --- | --- | --- | --- |
| `name` | string | no |  |

### Flags

| flag | type | default | description |
| --- | --- | --- | --- |
| `--cli-prompt` | bool |  | Use the legacy in-terminal email/name/password prompts for the admin-account step instead of the browser /setup flow. |
| `--email` | string |  | Admin email address (headless bootstrap — requires --name and --password) |
| `--name` | string |  | Admin display name (headless bootstrap — requires --email and --password) |
| `--password` | string |  | Admin password (headless bootstrap — requires --email and --name) |
| `--template` | string |  | workspace template (omit for interactive picker; run 'pad workspace init --list-templates' to see all) |

### Examples

```bash
pad init
```

```bash
pad init myproject
```

```bash
pad init --template scrum
```

## `pad item`

Create, update, relate, and discuss Pad items

### Synopsis

```
pad item
```

## `pad item ack`

Acknowledge a fired reminder

Acknowledge a reminder that has fired, removing it from 'pad project next'.

Nothing else acknowledges a reminder. In particular, completing the item does
NOT: a reminder may have been armed precisely to fire after the work was done,
and consuming it on a status change would throw that away. A reminder on a
completed item is hidden from the recommendation surface but stays in the
table, still unacknowledged, exactly as you left it.

### Synopsis

```
pad item ack <reminder-id>
```

### Arguments

| name | type | required | description |
| --- | --- | --- | --- |
| `reminder-id` | string | yes |  |

### Examples

```bash
pad item ack <reminder-id>
```

## `pad item backlinks`

List items that link to this item via [[ref]]

Show items whose body contains a [[<ref>]] reference to the target.

Backlinks are the reverse of [[]] wiki-links: if BUG-5's body contains
[[TASK-1]], then "pad item backlinks TASK-1" lists BUG-5 as a source.

Code blocks (fenced and inline) are excluded — example refs in docs
don't count as real links. Self-links (an item referencing its own
ref in its own body) are hidden.

### Synopsis

```
pad item backlinks <ref> [flags]
```

### Arguments

| name | type | required | description |
| --- | --- | --- | --- |
| `ref` | string | yes |  |

### Flags

| flag | type | default | description |
| --- | --- | --- | --- |
| `--limit` | int |  | max backlinks to return (default 50, max 300) |
| `--offset` | int |  | skip the first N backlinks (for pagination) |

### Examples

```bash
pad item backlinks TASK-5
```

```bash
pad item backlinks PLAN-42 --limit 10
```

```bash
pad item backlinks IDEA-3 --format json
```

## `pad item block`

Mark that one item blocks another

Create a blocking dependency between two items.

The source item blocks the target item. For example:
  pad item block TASK-5 TASK-8    # TASK-5 blocks TASK-8

### Synopsis

```
pad item block <source-ref> <target-ref>
```

### Arguments

| name | type | required | description |
| --- | --- | --- | --- |
| `source-ref` | string | yes |  |
| `target-ref` | string | yes |  |

### Examples

```bash
pad item block TASK-5 TASK-8
```

## `pad item blocked-by`

Mark that an item is blocked by another

Create a blocking dependency (reverse direction).

The source item is blocked by the blocker item. For example:
  pad item blocked-by TASK-5 TASK-3    # TASK-5 is blocked by TASK-3

### Synopsis

```
pad item blocked-by <source-ref> <blocker-ref>
```

### Arguments

| name | type | required | description |
| --- | --- | --- | --- |
| `source-ref` | string | yes |  |
| `blocker-ref` | string | yes |  |

### Examples

```bash
pad item blocked-by TASK-8 TASK-5
```

## `pad item bulk-update`

Update multiple items at once

Update the status or priority of multiple items in a single command.

Items can be referenced by issue ID (e.g. TASK-5) or slug.

### Synopsis

```
pad item bulk-update <ref>... [flags]
```

### Arguments

| name | type | required | description |
| --- | --- | --- | --- |
| `ref` | string (repeatable) | yes |  |

### Flags

| flag | type | default | description |
| --- | --- | --- | --- |
| `--force` | bool |  | override the open-children guard (allow marking items terminal even if children are non-terminal) |
| `--priority` | string |  | set priority for all items |
| `--status` | string |  | set status for all items |

### Examples

```bash
pad item bulk-update --status done TASK-5 TASK-8 TASK-12
```

```bash
pad item bulk-update --priority high IDEA-3 IDEA-7
```

```bash
pad item bulk-update --status in_progress --priority urgent TASK-1 TASK-2
```

## `pad item claim`

Atomically claim an item for execution (lease with expiry)

Acquire the execution lease on an item, or refresh it if you already
hold it (a re-claim by the live holder extends the expiry — heartbeat).

Fails with the live holder and expiry when someone else holds the item, so
the loser can log who won and skip instead of double-working. The lease
expires on its own; a crashed holder blocks nobody past the TTL.

The lease is held under this session's WORKER ID plus your account: an
opaque id "pad session register" mints, kept across a /clear and new for
each process, so two sessions get distinct leases even under one agent
name. --worker-id (or $PAD_WORKER_ID) acts as a given id, e.g. to resume
after a restart. An unregistered session sends none and is matched on its
holder label, as before: two unregistered sessions of one runtime share a
name, and a name-only claim of a worker-bound lease is refused.

--holder is the display label (default: this session's agent name, else
your account's email). "pad project next" / "ready" leave out items another
worker has leased, by the same identity a claim uses.

### Synopsis

```
pad item claim <ref> [flags]
```

### Arguments

| name | type | required | description |
| --- | --- | --- | --- |
| `ref` | string | yes |  |

### Flags

| flag | type | default | description |
| --- | --- | --- | --- |
| `--holder` | string |  | lease holder display label (default: this session's agent name, else your email); the lease is matched by worker id when this session has one |
| `--ttl` | string |  | lease duration, e.g. 15m, 1h (default: 15m; max 24h) |
| `--worker-id` | string |  | lease worker id ("wk_" + 32 hex) to act as (default: this session's own, from pad session register or $PAD_WORKER_ID) |

### Examples

```bash
pad item claim TASK-5
```

```bash
pad item claim TASK-5 --holder sweep-runner --ttl 30m
```

## `pad item comment`

Add a comment to an item

### Synopsis

```
pad item comment <ref> <message> [flags]
```

### Arguments

| name | type | required | description |
| --- | --- | --- | --- |
| `ref` | string | yes |  |
| `message` | string | yes |  |

### Flags

| flag | type | default | description |
| --- | --- | --- | --- |
| `--op-key` | string |  | idempotency key: retrying the SAME comment with the same key returns the comment it made instead of a second one (default: a new key per invocation) |
| `--reply-to` | string |  | reply to a specific comment ID |

### Examples

```bash
pad item comment TASK-5 "Reproduced on main; the fix is in progress"
```

## `pad item comment-delete`

Delete a comment from an item

Delete a comment from an item.

Anyone who may edit the item may delete its comments. A comment that still
has replies is refused and nothing is deleted; delete the replies first.
Get comment IDs from "pad item comments <ref>".

### Synopsis

```
pad item comment-delete <ref> <comment-id>
```

### Arguments

| name | type | required | description |
| --- | --- | --- | --- |
| `ref` | string | yes |  |
| `comment-id` | string | yes |  |

### Examples

```bash
pad item comment-delete TASK-5 <comment-id>
```

## `pad item comment-edit`

Replace the body of a comment on an item

Replace the body of a comment on an item.

Only the comment's author may edit it; an admin may too, but only from a
browser session. Get comment IDs from "pad item comments <ref>". An edited
comment is shown with "edited" in that listing.

  pad item comment-edit TASK-5 3f2a... "corrected threshold is 0.7"
  pad item comment-edit TASK-5 3f2a... --stdin < note.md

### Synopsis

```
pad item comment-edit <ref> <comment-id> [message] [flags]
```

### Arguments

| name | type | required | description |
| --- | --- | --- | --- |
| `ref` | string | yes |  |
| `comment-id` | string | yes |  |
| `message` | string | no |  |

### Flags

| flag | type | default | description |
| --- | --- | --- | --- |
| `--stdin` | bool |  | read the new body from stdin instead of the message argument (a blank read is refused) |

### Examples

```bash
pad item comment-edit TASK-5 <comment-id> "The fix landed in #1234"
```

## `pad item comments`

List comments on an item

### Synopsis

```
pad item comments <ref>
```

### Arguments

| name | type | required | description |
| --- | --- | --- | --- |
| `ref` | string | yes |  |

### Examples

```bash
pad item comments TASK-5
```

## `pad item context`

Everything an agent needs before working an item, in one brief

Fetch one deterministic brief for working an item (PLAN-3598): the item
with its seq, its parent chain with parsed acceptance criteria, the bodies
of the conventions whose trigger matches the intent (plus the always-on
ones), matching playbooks, dependencies with statuses, the typed decisions
Pad would surface (the rest are only counted), linked items, and the sections that say what was left out for size and
which rules may conflict.

--intent maps onto the workspace's convention triggers: "implement" means
on-implement when that trigger is declared. --role keeps a convention scoped
to another role out of the brief. --budget caps the brief in characters;
whole parts are dropped from the end, never cut, and each is listed under
omitted.

### Synopsis

```
pad item context <ref> [flags]
```

### Arguments

| name | type | required | description |
| --- | --- | --- | --- |
| `ref` | string | yes |  |

### Flags

| flag | type | default | description |
| --- | --- | --- | --- |
| `--budget` | int |  | size cap in characters (default 40000 on the server) |
| `--intent` | string |  | what you are about to do (implement, review, commit, ...): selects the conventions whose trigger matches |
| `--role` | string |  | your agent role slug: conventions scoped to another role are left out |

### Examples

```bash
pad item context TASK-5 --intent implement
```

```bash
pad item context TASK-5 --intent implement --role implementer --format json
```

```bash
pad item context TASK-5 --intent review --budget 20000
```

## `pad item copy`

Copy an item into another workspace

Copy an item into a different workspace, choosing the destination collection.

Fields are migrated into the destination collection's schema: matching keys with
compatible types carry across, incompatible ones are dropped, and destination
fields that end up required-but-empty must be supplied with --field.

With --archive-source the source is archived after a successful copy — that is
the MOVE path. The archived source records where it went.

What never carries: child items, the parent link, dependency links (blocks /
blocked-by / related), the assignee when they are not a member of the
destination workspace, and the agent role (role slugs are workspace-local).
--dry-run reports all of it before anything happens.

The content is copied as written, with two exceptions worth knowing:

  - pad-attachment: references that resolve to a LIVE attachment in the source
    workspace are repointed at the copied attachments (originals and their
    thumbnail variants). Any other reference — an id from another workspace, a
    soft-deleted one, or one that never existed — is left in the text
    unchanged and reported as unresolvable; it does not become a copy.
  - [[wiki-links]] are NOT rewritten. The copy is re-resolved in the
    DESTINATION workspace, so a link can end up pointing at a different item
    there, or at nothing at all. An explicit [[workspace::REF]] link stays a
    genuine cross-workspace reference to the original.

--dry-run calls a read-only preview endpoint and changes nothing. Without it,
the preview still runs first: if any destination field needs a value you have
not supplied, the copy is refused before any mutating request is sent.

A copy is attempted at most once per invocation and is NEVER retried
automatically. There is no idempotency key, so a blind re-run after an
ambiguous failure would create a duplicate item — on such a failure the
command tells you to check the destination workspace instead.

Items can be referenced by issue ID (e.g. TASK-5) or slug.

### Synopsis

```
pad item copy <ref> <slug> <slug> [flags]
```

### Arguments

| name | type | required | description |
| --- | --- | --- | --- |
| `ref` | string | yes |  |
| `slug` | string | yes |  |
| `slug` | string | yes |  |

### Flags

| flag | type | default | description |
| --- | --- | --- | --- |
| `--archive-source` | bool |  | archive the source after a successful copy (the move path) |
| `--collection` | string |  | destination collection slug (required) |
| `--dry-run` | bool |  | report what the copy would do, without doing any of it |
| `--field` | string (repeatable) |  | set a destination field value (repeatable): --field key=value |
| `--op-key` | string |  | idempotency key: retrying the SAME copy with the same key returns the first copy instead of making another (default: a new key per invocation) |
| `--to-workspace` | string |  | destination workspace slug (required) |

### Examples

```bash
pad item copy IDEA-12 --to-workspace pad-web --collection tasks --dry-run
```

```bash
pad item copy IDEA-12 --to-workspace pad-web --collection tasks
```

```bash
pad item copy TASK-5 --to-workspace pad-web --collection tasks --archive-source
```

```bash
pad item copy TASK-5 --to-workspace pad-web --collection tasks --field priority=high
```

## `pad item create`

Create a new item in a collection

Create a new item in the specified collection.

Run with --help-collections to see available collections and their status values.

### Synopsis

```
pad item create <collection> <title> [flags]
```

### Arguments

| name | type | required | description |
| --- | --- | --- | --- |
| `collection` | string | yes |  |
| `title` | string | yes |  |

### Flags

| flag | type | default | description |
| --- | --- | --- | --- |
| `--assign` | string |  | assign to user (name or email) |
| `--category` | string |  | category field value |
| `--content` | string |  | item body content |
| `--field` | string (repeatable) |  | set arbitrary field (repeatable): --field key=value; refused for implementation_notes, decision_log, github_pr and convention (create the item, then use `pad item note` / `pad item decide` / `pad github link`; conventions come from `pad library activate`) |
| `--fields-json` | string |  | set fields from one JSON object, values keeping their JSON type (e.g. '{"labels":["a","b"],"meta":{"k":1}}'); for structured values --field key=value cannot carry. A key also set by --field or a dedicated flag is refused, and so is null |
| `--op-key` | string |  | idempotency key: retrying the SAME create with the same key returns the item it created instead of a second one (default: a new key per invocation) |
| `--parent` | string |  | parent item (ref, slug, or ID) |
| `--priority` | string |  | priority field value |
| `--role` | string |  | assign agent role (slug) |
| `--status` | string |  | status field value |
| `--stdin` | bool |  | read content from stdin |
| `--tags` | string |  | JSON array of tags |

### Examples

```bash
pad item create task "Fix OAuth redirect" --priority high
```

```bash
pad item create idea "Real-time collaboration" --category infrastructure
```

```bash
pad item create plan "API Redesign" --status active
```

```bash
pad item create doc "Payment Architecture" --category architecture --stdin
```

## `pad item decide`

Append a decision log entry to an item

### Synopsis

```
pad item decide <ref> <decision> [flags]
```

### Arguments

| name | type | required | description |
| --- | --- | --- | --- |
| `ref` | string | yes |  |
| `decision` | string | yes |  |

### Flags

| flag | type | default | description |
| --- | --- | --- | --- |
| `--op-key` | string |  | idempotency key: retrying the SAME decision with the same key returns the decision it appended instead of a second one (default: a new key per invocation) |
| `--rationale` | string |  | decision rationale |
| `--stdin` | bool |  | read decision rationale from stdin |

### Examples

```bash
pad item decide TASK-5 "Use SQLite FTS5 for search" --rationale "No extra service to run"
```

## `pad item delete`

Archive (soft-delete) an item

### Synopsis

```
pad item delete <ref>
```

### Arguments

| name | type | required | description |
| --- | --- | --- | --- |
| `ref` | string | yes |  |

### Examples

```bash
pad item delete TASK-5
```

## `pad item deps`

Show all dependencies for an item

Display blocking relationships for an item.

Shows two sections:
  Blocks:      items that this item is blocking
  Blocked by:  items that are blocking this item

### Synopsis

```
pad item deps <ref>
```

### Arguments

| name | type | required | description |
| --- | --- | --- | --- |
| `ref` | string | yes |  |

### Examples

```bash
pad item deps TASK-5
```

## `pad item edit`

Open an item's content in $EDITOR

Open an item's rich content in your default editor. After editing
and saving, the content is updated in Pad.

Items can be referenced by issue ID (e.g. TASK-5) or slug.
Set EDITOR or VISUAL env var to choose your editor (default: vi).

The save is guarded: it is refused if the stored item was written since
the editor opened. If it is refused, or the save fails for any other
reason, your edited text is written to a recovery file and its path is
printed. Exiting the editor with a nonzero status (e.g. vim's :cq) aborts
without saving, as git does.

A browser tab's unsaved typing is not a write to the stored item until the
tab writes it back, so the version token alone cannot see it. The command
checks for such typing when the editor opens and again just before saving,
and the server refuses the save if any is pending when it arrives. With an
editor tab open, typing in the instant between the server's check and the
editor applying the new body can still be replaced.

Refuses to open when the stored body is behind the item's live
collaborative document (an editor in a browser tab holds edits not yet
written back), because saving would replace those edits. Open the item
in a browser tab so it flushes, then retry — or pass --force to edit the
stored body anyway. It refuses the same way when the item holds edits an
editor upgrade set aside (see pad item set-aside); opening the item does not
restore those, and --force discards them.

### Synopsis

```
pad item edit <ref> [flags]
```

### Arguments

| name | type | required | description |
| --- | --- | --- | --- |
| `ref` | string | yes |  |

### Flags

| flag | type | default | description |
| --- | --- | --- | --- |
| `--force` | bool |  | edit even when the stored body is behind the live collaborative document, and save with overwrite_pending_edits (replaces edits held only there) |

### Examples

```bash
pad item edit DOC-3
```

## `pad item export`

Export a playbook or convention as a portable artifact

Export a single playbook or convention item to a portable artifact
(Markdown body + YAML frontmatter) that can be imported into another workspace.

Only playbooks and conventions can be exported. They are Pad's two "library"
item types — the ones designed to move between workspaces. Every other item
type is workspace-local and has no portable-artifact form, so the server
rejects it. To pull data out of a task, idea, doc, or any other item, use
"pad item show <ref> --format json" instead.

Items can be referenced by issue ID (e.g. PLAYB-3) or slug.

### Synopsis

```
pad item export <ref> [flags]
```

### Arguments

| name | type | required | description |
| --- | --- | --- | --- |
| `ref` | string | yes |  |

### Flags

| flag | type | default | description |
| --- | --- | --- | --- |
| `--output` | string |  | output file path (default <slug>.pad.md; use - for stdout) |

### Examples

```bash
pad item export PLAYB-3
```

```bash
pad item export ship -o ship.pad.md
```

```bash
pad item export CONVE-7 -o -
```

## `pad item history`

Show an item's version history (read-only)

Show the recorded version history for an item, newest first.

Each row is a snapshot captured when the item's content changed (edits from
the web editor, CLI, MCP, collab flushes, and version restores). This is a
READ-ONLY view — use the web UI to restore a specific version.

Shows the newest 50 by default; pass --limit 0 for the whole history. A
collab-edited item records a version every few seconds while someone types, so
histories get long.

A single request is capped server-side, so a very large --limit returns the
cap rather than everything, and the "showing the newest N" notice cannot detect
that case. Use --limit 0 when you genuinely want the complete history.

Items can be referenced by issue ID (e.g. TASK-5) or slug.

### Synopsis

```
pad item history <ref> [flags]
```

### Arguments

| name | type | required | description |
| --- | --- | --- | --- |
| `ref` | string | yes |  |

### Flags

| flag | type | default | description |
| --- | --- | --- | --- |
| `--full` | bool |  | include each version's resolved content body (JSON output only) |
| `--limit` | int | `50` | show only the newest N versions (0 = all; very large values are capped server-side) |

### Examples

```bash
pad item history TASK-5
```

```bash
pad item versions TASK-5 --format json
```

```bash
pad item history TASK-5 --limit 10
```

```bash
pad item history TASK-5 --limit 0
```

```bash
pad item history TASK-5 --full --format json
```

## `pad item implemented-by`

Show items that implement the given item

List the direct incoming "implements" lineage relationships for an item.

This is useful for ideas or parent tasks that are realized by one or more
implementation tasks.

### Synopsis

```
pad item implemented-by <ref>
```

### Arguments

| name | type | required | description |
| --- | --- | --- | --- |
| `ref` | string | yes |  |

### Examples

```bash
pad item implemented-by SPEC-2
```

## `pad item implements`

Mark that one item implements another

Create a lineage relationship showing that one item implements another.

The first item is the implementation work item, and the second item is the item being implemented.
For example:
  pad item implements TASK-121 IDEA-108

### Synopsis

```
pad item implements <implementer-ref> <target-ref>
```

### Arguments

| name | type | required | description |
| --- | --- | --- | --- |
| `implementer-ref` | string | yes |  |
| `target-ref` | string | yes |  |

### Examples

```bash
pad item implements TASK-5 SPEC-2
```

## `pad item import`

Import a playbook or convention artifact into the workspace

Import a portable artifact (Markdown body + YAML frontmatter) as a new
playbook or convention in the current workspace.

Only playbooks and conventions have a portable-artifact form, so an import
only ever creates one of those two "library" item types. No other item type
can be created this way.

The item is always imported as a draft — review and activate it afterward.
The server may emit warnings (e.g. a foreign select value cleared, or an
invocation_slug de-collided); each is printed on its own line.

Use - to read the artifact from stdin.

### Synopsis

```
pad item import <file>
```

### Arguments

| name | type | required | description |
| --- | --- | --- | --- |
| `file` | string | yes |  |

### Examples

```bash
pad item import ship.pad.md
```

```bash
cat ship.pad.md | pad item import -
```

## `pad item list`

List items, optionally filtered by collection

List items in the workspace. If a collection is specified, only items
in that collection are shown. Items with status "done" are hidden by default.

### Synopsis

```
pad item list [collection] [flags]
```

### Arguments

| name | type | required | description |
| --- | --- | --- | --- |
| `collection` | string | no |  |

### Flags

| flag | type | default | description |
| --- | --- | --- | --- |
| `--all` | bool |  | include done/completed/archived items |
| `--assign` | string |  | filter by assigned user (name or email) |
| `--field` | string (repeatable) |  | filter by field value (repeatable): --field key=value |
| `--full` | bool |  | JSON output only: include full content + all fields (default: token-light summary shape) |
| `--group-by` | string |  | group results by field |
| `--limit` | int |  | max number of items to return (default 200, max 1000; with --format json and no --limit, every matching item is returned) |
| `--offset` | int |  | skip the first N items (for pagination) |
| `--parent` | string |  | filter by parent item (ref, slug, or ID) |
| `--priority` | string |  | filter by priority |
| `--role` | string |  | filter by agent role (slug) |
| `--sort` | string |  | sort order (e.g. priority:desc,created_at:asc) |
| `--status` | string |  | filter by status (comma-separated) |
| `--tag` | string |  | filter by tag (exact match; spans collections) |
| `--unparented` | bool |  | filter to items with no parent or implements relationship |

### Examples

```bash
pad item list
```

```bash
pad item list tasks
```

```bash
pad item list tasks --status done
```

```bash
pad item list ideas --status exploring
```

```bash
pad item list --all
```

## `pad item move`

Move an item to a different collection

Move an item to a different collection with automatic field migration.

Fields with matching names and compatible types transfer automatically.
Incompatible fields are dropped. Use --field to set values for target-specific fields.

Items can be referenced by issue ID (e.g. TASK-5) or slug.

### Synopsis

```
pad item move <ref> <target-collection> [flags]
```

### Arguments

| name | type | required | description |
| --- | --- | --- | --- |
| `ref` | string | yes |  |
| `target-collection` | string | yes |  |

### Flags

| flag | type | default | description |
| --- | --- | --- | --- |
| `--field` | string (repeatable) |  | set field values in target collection (key=value) |
| `--force` | bool |  | override the open-children guard when the move would write a terminal done-field value |

### Examples

```bash
pad item move BUG-3 tasks
```

```bash
pad item move IDEA-7 tasks --field priority=high
```

## `pad item note`

Append an implementation note to an item

### Synopsis

```
pad item note <ref> <summary> [flags]
```

### Arguments

| name | type | required | description |
| --- | --- | --- | --- |
| `ref` | string | yes |  |
| `summary` | string | yes |  |

### Flags

| flag | type | default | description |
| --- | --- | --- | --- |
| `--details` | string |  | implementation details |
| `--op-key` | string |  | idempotency key: retrying the SAME note with the same key returns the note it appended instead of a second one (default: a new key per invocation) |
| `--stdin` | bool |  | read note details from stdin |

### Examples

```bash
pad item note TASK-5 "Added retry with backoff" --details "Three attempts at 1s, 2s and 4s"
```

## `pad item open`

Open an item in the Pad web UI

### Synopsis

```
pad item open <ref>
```

### Arguments

| name | type | required | description |
| --- | --- | --- | --- |
| `ref` | string | yes |  |

### Examples

```bash
pad item open TASK-5
```

## `pad item patch`

Replace exact text in an item's body, and print the diff

Edit part of an item's body without sending the whole of it. Each edit
names text (--old) that must occur EXACTLY ONCE in the current body and the
text that replaces it (--new). Edits apply in order, all or nothing. The
answer is a unified diff of what changed.

Anchors are text, not line numbers: line N when you read is not line N when
the write lands. Quote enough surrounding text to be unique. Anchors
guarantee position, not meaning: if someone rewrote the paragraph around your
anchor, the edit still lands; read the diff.

--expected-seq does not refuse a moved item. If every anchor still matches,
the patch applies and reports rebased, with the writes in between and the
diff; if an anchor no longer matches, nothing is written.

For several or multi-line edits use --edits with a JSON array of
{"old","new","line_hint"} (line_hint, 1-based, only chooses among several
exact matches): --edits @edits.json, or --edits - to read stdin.

--undo PATCH-ID inverts an earlier patch on this item (the patch_id a patch
printed). It anchors on the text around each edit as it landed, so it refuses,
writing nothing, when that text has changed since: it never reverts someone
else's later edit. The undo is itself a patch, with its own patch id.

On an item open in a browser editor, that editor applies the patch to its live
document, merging with the typing there; the row catches up on its next flush.
It refuses with patch_unstable_roundtrip when applying would also change
content you did not edit, and patch_room_open when only an older editor that
cannot apply patches holds the item.

### Synopsis

```
pad item patch <ref> [flags]
```

### Arguments

| name | type | required | description |
| --- | --- | --- | --- |
| `ref` | string | yes |  |

### Flags

| flag | type | default | description |
| --- | --- | --- | --- |
| `--edits` | string |  | edits as a JSON array of {"old","new","line_hint"}: @FILE, - for stdin, or the JSON itself |
| `--expected-seq` | int |  | the seq you read; a moved item is still patched when every anchor matches, and reported as rebased |
| `--new` | string (repeatable) |  | replacement text (repeatable, paired in order with --old; may be empty to delete) |
| `--old` | string (repeatable) |  | text to replace; must occur exactly once in the current body (repeatable, paired in order with --new) |
| `--op-key` | string |  | idempotency key: retrying the SAME request with the same key returns the first answer instead of applying it again (default: a new key per invocation) |
| `--undo` | string |  | invert an earlier patch on this item by its patch id; refused, writing nothing, if the text it changed has changed since |

### Examples

```bash
pad item patch TASK-5 --old "Status: draft" --new "Status: ready"
```

```bash
pad item patch DOC-3 --old "old line" --new "new line" --expected-seq 41
```

```bash
pad item patch DOC-3 --edits @edits.json
```

```bash
pad item patch DOC-3 --undo 3f2c9a1e-…
```

## `pad item related`

Show direct relationships around an item

Show the direct dependency, lineage, wiki-link, and related-item graph around a single item.

This is a query-oriented view of the item's immediate context.

### Synopsis

```
pad item related <ref>
```

### Arguments

| name | type | required | description |
| --- | --- | --- | --- |
| `ref` | string | yes |  |

### Examples

```bash
pad item related TASK-5
```

## `pad item release`

Release an item's execution lease (idempotent)

Release the execution lease you hold on an item. Releasing an absent or
already-expired lease is a no-op, not an error — cleanup code never needs
to check whether it still holds the lease first. Releasing another
holder's LIVE lease is refused.

### Synopsis

```
pad item release <ref> [flags]
```

### Arguments

| name | type | required | description |
| --- | --- | --- | --- |
| `ref` | string | yes |  |

### Flags

| flag | type | default | description |
| --- | --- | --- | --- |
| `--holder` | string |  | lease holder display label (default: this session's agent name, else your email; a name-only lease must match the claim's) |
| `--worker-id` | string |  | lease worker id ("wk_" + 32 hex) to act as (default: this session's own, from pad session register or $PAD_WORKER_ID) |

### Examples

```bash
pad item release TASK-5
```

## `pad item remind`

Arm a reminder on an item

Arm a one-shot reminder that fires at a specific instant.

The instant is RFC3339 and must carry a time of day — 2026-08-01T09:00:00Z, or
2026-08-01T09:00:00-04:00, which is stored as the same moment in UTC. A bare
date is refused rather than assumed to mean midnight: "2026-08-01" names a
24-hour span, and picking an hour inside it would be Pad choosing a time you
did not and then firing at it.

When the reminder fires it appears in 'pad project next' and 'pad project
ready' until you acknowledge it with 'pad item ack', and it emits an
item.reminder_due webhook event. The poll surface is not optional: an instance
with no webhook configured delivers reminders that way and only that way.

### Synopsis

```
pad item remind [ref] [flags]
```

### Arguments

| name | type | required | description |
| --- | --- | --- | --- |
| `ref` | string | no |  |

### Flags

| flag | type | default | description |
| --- | --- | --- | --- |
| `--rearm` | string |  | move an existing reminder by id instead of arming a new one |
| `--remind-at` | string |  | when to fire (RFC3339 instant, e.g. 2026-08-01T09:00:00Z) |

### Examples

```bash
pad item remind TASK-5 --remind-at 2026-11-02T09:00:00Z
```

## `pad item reminders`

Show an item's reminders

List every reminder on an item — armed, fired, and acknowledged.

Fired reminders are kept rather than deleted: the row is the record that a
reminder existed and went out.

### Synopsis

```
pad item reminders <ref>
```

### Arguments

| name | type | required | description |
| --- | --- | --- | --- |
| `ref` | string | yes |  |

### Examples

```bash
pad item reminders TASK-5
```

## `pad item restore`

Restore (un-archive) a soft-deleted item

### Synopsis

```
pad item restore <ref>
```

### Arguments

| name | type | required | description |
| --- | --- | --- | --- |
| `ref` | string | yes |  |

### Examples

```bash
pad item restore TASK-5
```

## `pad item search`

Full-text search across all items

### Synopsis

```
pad item search <query> [flags]
```

### Arguments

| name | type | required | description |
| --- | --- | --- | --- |
| `query` | string | yes |  |

### Flags

| flag | type | default | description |
| --- | --- | --- | --- |
| `--collection` | string |  | filter by collection (e.g. tasks, ideas) |
| `--limit` | int |  | max results to return (default 50, max 200) |
| `--offset` | int |  | skip this many results (for pagination) |
| `--priority` | string |  | filter by priority (e.g. high, medium) |
| `--sort` | string |  | sort by: relevance (default), created_at, updated_at, title |
| `--status` | string |  | filter by status (e.g. open, done) |

### Examples

```bash
pad item search "oauth redirect" --collection tasks
```

## `pad item set-aside`

Show or discard edits an editor upgrade set aside

Show the edits an editor upgrade set aside on an item, or discard them.

When the collaborative editor's schema changes, edits that were typed under the
old editor and never saved to the item's body can no longer be replayed. They
are set aside instead of deleted, and the item reads
content_state=superseded_set_aside. Opening the item does NOT restore them.

With no flag this prints them as raw Yjs updates (base64 in --format json), so
they can be kept or recovered with a matching editor. --discard deletes them and
clears the state. A content write or version restore sent with
--overwrite-pending-edits discards them too.

### Synopsis

```
pad item set-aside <ref> [flags]
```

### Arguments

| name | type | required | description |
| --- | --- | --- | --- |
| `ref` | string | yes |  |

### Flags

| flag | type | default | description |
| --- | --- | --- | --- |
| `--discard` | bool |  | delete the set-aside edits and clear the state |

### Examples

```bash
pad item set-aside DOC-3
```

## `pad item show`

Show item detail (fields + content)

Show item detail (fields + content).

When the server marks the stored body as BEHIND the item's live collaborative
document (an editor holds unflushed edits), the default table output says so on
its FIRST line, on stdout. --format markdown does NOT: that output is the body
verbatim, for redirecting into a file and writing back with "item update
--stdin", so a notice there would become part of the body. It prints the notice
on stderr instead. --format json carries it as the content_state field.

### Synopsis

```
pad item show <ref> [flags]
```

### Arguments

| name | type | required | description |
| --- | --- | --- | --- |
| `ref` | string | yes |  |

### Flags

| flag | type | default | description |
| --- | --- | --- | --- |
| `--agent` | bool |  | return compact agent-oriented JSON |
| `--lines` | string |  | show only these body lines, numbered (A-B, A- or A; 1-based), with the seq: for targeting pad item patch. Line numbers are for reading; a patch anchors on text |

### Examples

```bash
pad item show TASK-5
```

## `pad item split-from`

Mark that an item was split from another item

Create a lineage relationship showing that one item was split from another.

The first item is the derived item, and the second item is the original source.
For example:
  pad item split-from TASK-122 TASK-121

### Synopsis

```
pad item split-from <child-ref> <parent-ref>
```

### Arguments

| name | type | required | description |
| --- | --- | --- | --- |
| `child-ref` | string | yes |  |
| `parent-ref` | string | yes |  |

### Examples

```bash
pad item split-from TASK-9 TASK-5
```

## `pad item star`

Star an item for quick access

Star an item to mark it as personally important. Starred items appear on your dashboard and in the Starred sidebar page.

### Synopsis

```
pad item star <ref>
```

### Arguments

| name | type | required | description |
| --- | --- | --- | --- |
| `ref` | string | yes |  |

### Examples

```bash
pad item star TASK-5
```

## `pad item starred`

List your starred items

### Synopsis

```
pad item starred [flags]
```

### Flags

| flag | type | default | description |
| --- | --- | --- | --- |
| `--all` | bool |  | include completed/terminal items |
| `--limit` | int |  | at most this many, from the most recently starred (default: all) |

### Examples

```bash
pad item starred
```

## `pad item supersedes`

Mark that one item supersedes another

Create a lineage relationship showing that one item supersedes another.

The first item is the newer replacement, and the second item is the older item.
For example:
  pad item supersedes TASK-130 TASK-118

### Synopsis

```
pad item supersedes <new-ref> <old-ref>
```

### Arguments

| name | type | required | description |
| --- | --- | --- | --- |
| `new-ref` | string | yes |  |
| `old-ref` | string | yes |  |

### Examples

```bash
pad item supersedes DOC-7 DOC-3
```

## `pad item unblock`

Remove a blocking dependency between items

Remove a "blocks" relationship where source blocks target.

### Synopsis

```
pad item unblock <source-ref> <target-ref>
```

### Arguments

| name | type | required | description |
| --- | --- | --- | --- |
| `source-ref` | string | yes |  |
| `target-ref` | string | yes |  |

### Examples

```bash
pad item unblock TASK-5 TASK-8
```

## `pad item unimplements`

Remove an implements relationship

### Synopsis

```
pad item unimplements <implementer-ref> <target-ref>
```

### Arguments

| name | type | required | description |
| --- | --- | --- | --- |
| `implementer-ref` | string | yes |  |
| `target-ref` | string | yes |  |

### Examples

```bash
pad item unimplements TASK-5 SPEC-2
```

## `pad item unremind`

Disarm a reminder

Remove a reminder.

Deletion is the only disarm — there is no cancelled state, because a cancelled
reminder and an absent one are indistinguishable to everything that reads them.

### Synopsis

```
pad item unremind <reminder-id>
```

### Arguments

| name | type | required | description |
| --- | --- | --- | --- |
| `reminder-id` | string | yes |  |

### Examples

```bash
pad item unremind <reminder-id>
```

## `pad item unsplit`

Remove a split-from relationship

### Synopsis

```
pad item unsplit <child-ref> <parent-ref>
```

### Arguments

| name | type | required | description |
| --- | --- | --- | --- |
| `child-ref` | string | yes |  |
| `parent-ref` | string | yes |  |

### Examples

```bash
pad item unsplit TASK-9 TASK-5
```

## `pad item unstar`

Remove a star from an item

### Synopsis

```
pad item unstar <ref>
```

### Arguments

| name | type | required | description |
| --- | --- | --- | --- |
| `ref` | string | yes |  |

### Examples

```bash
pad item unstar TASK-5
```

## `pad item unsupersede`

Remove a supersedes relationship

### Synopsis

```
pad item unsupersede <new-ref> <old-ref>
```

### Arguments

| name | type | required | description |
| --- | --- | --- | --- |
| `new-ref` | string | yes |  |
| `old-ref` | string | yes |  |

### Examples

```bash
pad item unsupersede DOC-7 DOC-3
```

## `pad item update`

Update an item's fields or content

Update an existing item. Only the specified fields are changed.

Items can be referenced by issue ID (e.g. TASK-5) or slug.

When --content is written while someone has the item open in an editor, the
markdown goes to that live document first and the stored copy is updated only by
a later collab-snapshot flush — usually from the tab that applied it, though any
such write updates the row. The response echoes what you sent and carries
warnings.content_outcome=applied_pending_flush; a warning line is printed to
stderr, and the last line of stdout says the body went to the open editor. A "pad item show" before such a flush lands reads the stored copy and shows
the PREVIOUS content — that is the lag, not a failed write. Nothing here
guarantees the flush happens (see BUG-3000), so the window has no stated
duration.

--stdin REPLACES the body with what it reads, and a blank read (empty or
whitespace-only) is refused before anything is sent, because it is what a lost
heredoc looks like. To empty a body on purpose, use --clear-content.

A body write replaces whatever is stored, so guard it with the version you
read: --expected-seq <seq from pad item show --agent>. A conflict means the item
changed after your read. Re-read it and apply your edit to the CURRENT body;
resending yours would undo the other change. --replace overwrites on purpose.
A body write with neither prints a warning, and a future release refuses it
(PLAN-3555).

### Synopsis

```
pad item update <ref> [flags]
```

### Arguments

| name | type | required | description |
| --- | --- | --- | --- |
| `ref` | string | yes |  |

### Flags

| flag | type | default | description |
| --- | --- | --- | --- |
| `--assign` | string |  | assign to user (name or email) |
| `--category` | string |  | update category field |
| `--clear-agent-role` | bool |  | clear the item's agent role (agent_role_id) |
| `--clear-assigned-user` | bool |  | unassign the item (clear assigned_user_id) |
| `--clear-content` | bool |  | clear the item's body; conflicts with --content and --stdin (a blank --stdin is refused, BUG-3100) |
| `--clear-parent` | bool |  | detach the item from its parent (clear the parent link); conflicts with --parent |
| `--comment` | string |  | attach a comment explaining this update (e.g. why status changed) |
| `--content` | string |  | REPLACE the whole body with this text (an empty value is ignored; use --clear-content) |
| `--expected-seq` | int |  | optimistic concurrency (preferred): the `seq` you last read; rejected with a conflict if the item changed since. Unlike --expected-updated-at this distinguishes two writes inside the same second (BUG-3037) |
| `--expected-updated-at` | string |  | optimistic concurrency: RFC3339 updated_at you last read; the update is rejected with a conflict (exit non-zero) if the item changed since |
| `--field` | string (repeatable) |  | set a field (repeatable): --field key=value; refused for implementation_notes (use `pad item note`), decision_log (`pad item decide`), github_pr (`pad github link`) and convention (`pad library activate`) |
| `--fields-json` | string |  | set fields from one JSON object, values keeping their JSON type (e.g. '{"labels":["a","b"],"meta":{"k":1}}'); for structured values --field key=value cannot carry. A key also set by --field or a dedicated flag is refused, and so is null |
| `--force` | bool |  | override the open-children guard (allow marking the item terminal even if children are non-terminal) |
| `--overwrite-pending-edits` | bool |  | with a version token and new content: replace unflushed edits a browser tab holds for this item instead of being refused with content_pending_flush (BUG-3133) |
| `--parent` | string |  | update parent item (ref, slug, or ID); an empty --parent "" is REFUSED, it does not clear — use --clear-parent |
| `--priority` | string |  | update priority field |
| `--replace` | bool |  | with --content, --stdin or --clear-content: overwrite the body on purpose, whatever changed since you read it (no version token). A body write with neither this nor --expected-seq is warned about now and will be refused in a future release (PLAN-3555) |
| `--role` | string |  | assign agent role (slug) |
| `--sort-order` | int |  | set the item's sort_order key (lower appears first; a sort key, not a position: drag-reorder writes values far apart, TASK-3525) |
| `--status` | string |  | update status field |
| `--stdin` | bool |  | REPLACE the whole body with what is read from stdin (a blank read is refused) |
| `--tags` | string |  | update tags (JSON array) |
| `--title` | string |  | update title |

### Examples

```bash
pad item update TASK-5 --status done
```

```bash
pad item update TASK-5 --status done --comment "Fixed the login bug"
```

```bash
pad item update PLAN-2 --status active --priority high
```

```bash
pad item update DOC-3 --stdin --expected-seq 41 < updated-doc.md
```

```bash
pad item update DOC-3 --stdin --replace < replacement.md
```

```bash
pad item update DOC-3 --clear-content
```

## `pad library`

Browse and activate pre-built conventions and playbooks

### Synopsis

```
pad library
```

## `pad library activate`

Activate a library convention or playbook in the current workspace

Look up a convention or playbook in the library by title and create it as an item
in the appropriate collection (conventions or playbooks) with all fields set.

### Synopsis

```
pad library activate <title>
```

### Arguments

| name | type | required | description |
| --- | --- | --- | --- |
| `title` | string | yes |  |

### Examples

```bash
pad library activate "Commit after task completion"
```

```bash
pad library activate "Ship tasks"
```

## `pad library diff`

Compare a built-in convention or playbook with Pad's current library text

Show how an item made from one of the conventions or playbooks Pad ships
differs from the library's current text: what the library changed since the
item was made, what you changed, and which settings an update would replace.
Read-only. Take the update with "pad library update <ref>".

### Synopsis

```
pad library diff <ref>
```

### Arguments

| name | type | required | description |
| --- | --- | --- | --- |
| `ref` | string | yes |  |

### Examples

```bash
pad library diff PLAYB-12
```

```bash
pad library diff PLAYB-12 --format json
```

## `pad library get`

Show the full body of one library convention or playbook by exact title

Fetch a single library entry by exact title match. Conventions are checked
first, then playbooks — same precedence `pad library activate` uses, so a title
resolves to the same kind in both surfaces.

Pair with `pad library list` (which returns summaries for playbooks by default)
to browse, then `pad library get` for the full body of any entry you want to
read end-to-end before activating.

### Synopsis

```
pad library get <title>
```

### Arguments

| name | type | required | description |
| --- | --- | --- | --- |
| `title` | string | yes |  |

### Examples

```bash
pad library get "Commit after task completion"
```

```bash
pad library get "Ship tasks"
```

```bash
pad library get "Ship tasks" --format json
```

## `pad library list`

Browse pre-built conventions and playbooks

Browse the convention and playbook libraries and activate items in your workspace.

JSON output: conventions always carry their full content (bodies are short).
Playbooks carry a short `summary` instead of full `content` by default — use
`--full` to opt into full playbook bodies (e.g. when piping into a tool that
needs the entire text). For one entry's full body use `pad library get <title>`.

### Synopsis

```
pad library list [flags]
```

### Flags

| flag | type | default | description |
| --- | --- | --- | --- |
| `--category` | string |  | server-side filter by category |
| `--full` | bool |  | return full playbook bodies instead of summaries |
| `--type` | string |  | filter by type: conventions, playbooks |

### Examples

```bash
pad library list
```

```bash
pad library list --type conventions
```

```bash
pad library list --type playbooks
```

```bash
pad library list --category git
```

```bash
pad library list --format json
```

```bash
pad library list --full --format json
```

```bash
pad library get "Ship tasks"
```

```bash
pad library activate "Commit after task completion"
```

## `pad library update`

Replace a built-in convention or playbook with Pad's current library text

Give an item made from one of the conventions or playbooks Pad ships the
library's current text: its body and the settings an update writes. Status and
title are never changed, and the item's previous text stays in its version
history. Review first with "pad library diff <ref>"; nothing updates on its own.

The update is guarded by the version read just before it: if the item changes
in between, it is refused rather than applied over the change.

### Synopsis

```
pad library update <ref> [flags]
```

### Arguments

| name | type | required | description |
| --- | --- | --- | --- |
| `ref` | string | yes |  |

### Flags

| flag | type | default | description |
| --- | --- | --- | --- |
| `--overwrite-pending-edits` | bool |  | Also replace edits that are not in the item's stored text (unsaved typing, or edits set aside by an editor upgrade); they are not kept |

### Examples

```bash
pad library update PLAYB-12
```

```bash
pad library update PLAYB-12 --overwrite-pending-edits
```

## `pad mcp`

Run pad as a Model Context Protocol server

Run pad as an MCP server so AI agents (Claude Desktop, Cursor, Windsurf,
Claude Code, Codex, etc.) can call pad commands as tools and read pad data
as resources.

Use `pad mcp serve` to start the server over stdio.
Use `pad mcp install` to register pad with a client app.
See https://getpad.dev/mcp/local for client configuration.

### Synopsis

```
pad mcp
```

## `pad mcp install`

Install pad as an MCP server for a client app

Write a "pad" entry into the named agent's MCP server config.

Supported agents:
  claude-desktop   Claude Desktop        (~/.../Claude/claude_desktop_config.json)
  cursor           Cursor                (~/.cursor/mcp.json)
  windsurf         Windsurf              (~/.codeium/windsurf/mcp_config.json)
  claude-code      Claude Code           (project-local ./.mcp.json)
  codex            Codex                 (~/.codex/config.toml)

claude-code writes a project-local .mcp.json in the current directory,
so it's install-on-request only — `--all` and `pad mcp status` skip it
(they cover the per-user configs). codex writes TOML; the rest write JSON.

With no arguments, lists current install status across supported
agents (run `pad mcp status` for the same view). With
--all, installs for every per-user agent, creating config files
on demand.

For Cursor or Codex, --compact-results removes the duplicate successful-result
channel while preserving the channel that client exposes to its model. It
configures text-only results for Cursor and structured-only results for Codex.

Existing MCP server entries (other servers configured by the user)
are preserved — only the "pad" entry is touched.

### Synopsis

```
pad mcp install [agent] [flags]
```

### Arguments

| name | type | required | description |
| --- | --- | --- | --- |
| `agent` | enum: claude-desktop\|cursor\|windsurf\|claude-code\|codex | no |  |

### Flags

| flag | type | default | description |
| --- | --- | --- | --- |
| `--all` | bool |  | install for every supported agent |
| `--compact-results` | bool |  | configure one model-visible result channel (Cursor/Codex) |

### Examples

```bash
pad mcp install claude-desktop
```

## `pad mcp serve`

Run the MCP server over stdio

Starts the MCP server speaking JSON-RPC on stdin/stdout.
Logs go to stderr — stdout is reserved for protocol traffic.

Intended to be spawned by an MCP client (Claude Desktop, Cursor, Windsurf,
etc.) per its mcp.json configuration. Direct human invocation is rare;
when running interactively you'll see an idle process waiting for the
client's initialize message.

The tool surface is the hand-curated v0.106 catalog —
ten resource × action tools (`pad_item`, `pad_workspace`, `pad_collection`, `pad_project`, `pad_role`, `pad_search`, `pad_meta`, `pad_playbook`, `pad_library`, `pad_attachment`) plus `pad_set_workspace` for session-default workspace
pinning. cmdhelp (v0.1) still drives per-command argument
schemas at dispatch time, but the historical leaf-walker that
exposed every CLI verb as its own tool was retired in TASK-981
of PLAN-969's v0.2 rollout.

Shuts down cleanly on EOF, SIGINT, or SIGTERM.

### Synopsis

```
pad mcp serve [flags]
```

### Flags

| flag | type | default | description |
| --- | --- | --- | --- |
| `--debug` | bool |  | verbose logging on stderr (development) |
| `--structured-only` | bool |  | omit duplicate structured-result JSON text |
| `--text-only` | bool |  | omit duplicate structuredContent while keeping JSON text |

### Examples

```bash
pad mcp serve
```

## `pad mcp status`

Show pad MCP install status across supported clients

### Synopsis

```
pad mcp status
```

### Examples

```bash
pad mcp status
```

## `pad mcp uninstall`

Remove the pad MCP entry from a client's config

Remove the "pad" entry from the named agent's MCP server
config. Other server entries are preserved. Idempotent: removing a
non-existent entry is not an error.

### Synopsis

```
pad mcp uninstall <agent>
```

### Arguments

| name | type | required | description |
| --- | --- | --- | --- |
| `agent` | enum: claude-desktop\|cursor\|windsurf\|claude-code\|codex | yes |  |

### Examples

```bash
pad mcp uninstall claude-desktop
```

## `pad playbook`

Work with playbooks — first-class invokable procedures

### Synopsis

```
pad playbook
```

## `pad playbook list`

List the workspace's playbooks (metadata only)

### Synopsis

```
pad playbook list
```

### Examples

```bash
pad playbook list
```

## `pad playbook match`

Ask the typed-decision provider which active playbook (if any) matches text

Send free text to the workspace's typed-decision provider and get back a
Choice over the workspace's ACTIVE playbooks (draft and deprecated are
excluded), plus a reserved "none" option for text that doesn't ask for any
of them. Read-only and side-effect-free — nothing is stored or enqueued.

Refuses with 404 (decision_provider_unavailable) when no provider is
configured for this instance — callers should fall back to slug/trigger
routing rather than treating that as a hard failure.

Text is user speech and may start with "-" (a dash-led sentence, or literal
text like "-ship it"); the flag parser reads a leading "-" as a flag, so put
"--" before the text to stop that (BUG-3142 tracks this for the CLI/MCP
stdio surface generally — this command's own help just tells you the
workaround):

### Synopsis

```
pad playbook match <text>
```

### Arguments

| name | type | required | description |
| --- | --- | --- | --- |
| `text` | string | yes |  |

### Examples

```bash
pad playbook match -- "-ship it"
```

## `pad playbook run`

Bind args to a playbook's declared spec and return the body + bound args

Parse the supplied args against the playbook's declared argument spec
(stored as the 'arguments' field on the item) and return the body with
those args bound. The server does NOT execute the playbook — playbooks
are agent instructions, not shell scripts. The CLI just primes the call
so an agent can take it from there.

Parsing rules:
  - Required positional args first, in declared order.
  - Flag-typed args: bareword presence (e.g. `stop-after-each`).
  - Other typed args: `key=value` form (e.g. `merge-strategy=rebase`).
  - Refs accept either issue IDs (TASK-5) or item slugs.

Draft gate: the server refuses to run a playbook whose status isn't
"active" (e.g. one still being drafted). Pass --allow-draft to override
and run it anyway.

### Synopsis

```
pad playbook run <ref> [args]... [flags]
```

### Arguments

| name | type | required | description |
| --- | --- | --- | --- |
| `ref` | string | yes |  |
| `args` | string (repeatable) | no |  |

### Flags

| flag | type | default | description |
| --- | --- | --- | --- |
| `--allow-draft` | bool |  | Run a playbook even if its status isn't "active" (the draft gate escape hatch) |

### Examples

```bash
pad playbook run ship TASK-5
```

## `pad playbook show`

Show a single playbook's full body and metadata

Print a playbook by invocation_slug, item slug, or issue ref. The resolver tries each in turn.

### Synopsis

```
pad playbook show <ref>
```

### Arguments

| name | type | required | description |
| --- | --- | --- | --- |
| `ref` | string | yes |  |

### Examples

```bash
pad playbook show ship
```

## `pad project`

Inspect project state, reports, and activity

### Synopsis

```
pad project
```

## `pad project activity`

Show recent workspace activity — what agents and users changed (non-streaming)

Show a bounded, non-streaming snapshot of workspace activity.

Answers "what did other agents/users do since I last worked?" — the query
counterpart to the live 'pad project watch' stream. Backed by the same
enriched activity feed the web UI uses (item refs, titles, change details).

### Synopsis

```
pad project activity [flags]
```

### Flags

| flag | type | default | description |
| --- | --- | --- | --- |
| `--actor` | string |  | filter by actor category: user or agent |
| `--limit` | int | `20` | maximum number of activity entries to return |
| `--since` | string |  | only show activity on or after this date (YYYY-MM-DD) |

### Examples

```bash
pad project activity --since 2026-10-09 --actor agent
```

## `pad project catch-up`

Show your catch-up digest: what changed since you last marked the workspace caught up

Show your own catch-up digest for the workspace: what needs you now, and what
others finished, created, reopened, commented on, or did as agents since you
last pressed Mark caught up (at most 14 days back).

Read-only. It never moves your cursor; Mark caught up is done in the web UI.

--format json prints the server's JSON, re-indented.

### Synopsis

```
pad project catch-up
```

### Examples

```bash
pad project catch-up --format markdown
```

## `pad project changelog`

Generate release notes from completed items

### Synopsis

```
pad project changelog [flags]
```

### Flags

| flag | type | default | description |
| --- | --- | --- | --- |
| `--days` | int | `7` | show items completed in last N days |
| `--parent` | string |  | only show items under a specific parent (ref, slug, or title) |
| `--since` | string |  | only show items completed after this date (YYYY-MM-DD) |

### Examples

```bash
pad project changelog --days 7
```

## `pad project dashboard`

Show project dashboard — progress, attention items, suggested next

### Synopsis

```
pad project dashboard
```

### Examples

```bash
pad project dashboard
```

## `pad project next`

Recommend the next task to work on

### Synopsis

```
pad project next [flags]
```

### Flags

| flag | type | default | description |
| --- | --- | --- | --- |
| `--worker-id` | string |  | lease worker id ("wk_" + 32 hex) to act as (default: this session's own, from pad session register or $PAD_WORKER_ID) |

### Examples

```bash
pad project next
```

## `pad project ready`

Show actionable next items for an agent

List up to three items Pad suggests working on next, best first.

It is the same ranked list as 'pad project next' and the dashboard's Up next:
fired reminders, then overdue work, in-progress work, open items in active
plans, and high or critical priority items. Any slot left over is filled with
other open items from collections that track priority or severity (Tasks,
Bugs, Features, Backlog), ranked by priority (else severity), then age.
Blocked items are never listed; 'pad project stale' shows them.

### Synopsis

```
pad project ready [flags]
```

### Flags

| flag | type | default | description |
| --- | --- | --- | --- |
| `--worker-id` | string |  | lease worker id ("wk_" + 32 hex) to act as (default: this session's own, from pad session register or $PAD_WORKER_ID) |

### Examples

```bash
pad project ready
```

## `pad project reconcile`

Detect stale task, branch, and pull request state

Inspect items with linked code metadata, compare their stored GitHub PR and branch state
against live GitHub data, and report drift.

By default, reconcile only reports findings. With --apply, it refreshes stored GitHub PR metadata
on items when the live PR state differs, but it does not automatically change item statuses.

### Synopsis

```
pad project reconcile [item-ref] [flags]
```

### Arguments

| name | type | required | description |
| --- | --- | --- | --- |
| `item-ref` | string | no |  |

### Flags

| flag | type | default | description |
| --- | --- | --- | --- |
| `--apply` | bool |  | refresh stored PR metadata from GitHub when it is stale |

### Examples

```bash
pad project reconcile TASK-5
```

## `pad project report`

Windowed project report — throughput, net flow, completions, status mix

Show a time-windowed project report: items created vs completed per bucket,
net flow, completed-by-collection, and a current status-distribution snapshot.

--window day|week|2wk|month (default week; day buckets hourly, others daily).
--collections restricts to a comma-separated list of collection slugs.

### Synopsis

```
pad project report [flags]
```

### Flags

| flag | type | default | description |
| --- | --- | --- | --- |
| `--collections` | string |  | Comma-separated collection slugs to include (default: all visible, non-system; name a system collection to include it) |
| `--window` | string | `week` | Report window: day\|week\|2wk\|month |

### Examples

```bash
pad project report --window month
```

## `pad project stale`

Show stale or attention-worthy items for an agent

List the current workspace items that need attention because they are stalled,
blocked, overdue, or otherwise falling out of the active workflow.

### Synopsis

```
pad project stale
```

### Examples

```bash
pad project stale
```

## `pad project standup`

Auto-generate a daily standup report from recent activity

### Synopsis

```
pad project standup [flags]
```

### Flags

| flag | type | default | description |
| --- | --- | --- | --- |
| `--days` | int | `1` | number of days to look back for completed items |

### Examples

```bash
pad project standup --days 1
```

## `pad project watch`

Stream real-time workspace activity (like kubectl get events --watch)

### Synopsis

```
pad project watch
```

### Examples

```bash
pad project watch
```

## `pad push`

Push an item + instruction to your own connected agent session(s)

pad push <ref> -m "message"
    Publish a self-addressed push notification on an item. It reaches
    your OWN plugin-monitor sessions (pad watch --stream --for-session)
    that are ACCEPTING pushes and can see the item — a connected session
    that hasn't opted in, or that lacks access to the item, does not
    receive it. Fire-and-forget over the watch-events bus, with no
    durable inbox: a push nothing is listening for is simply not seen
    (Phase 1 scope).

    On a multi-instance deployment (PAD_REDIS_URL set) both broadcast
    and session-targeted pushes reach your sessions on every instance:
    the notification bus and the session-presence registry are both
    shared, so a session connected to one server is visible and
    addressable from any of them. Addressable is still not the same as
    delivered. The count does check that a session is accepting pushes
    and that it can see the item (BUG-2725 — it applies the same
    visibility predicate delivery applies), but it is taken before the
    publish and nothing acknowledges receipt, so treat it as a
    prediction rather than a receipt. It can also under-count: a session
    past the per-user registry cap receives broadcasts while never
    entering the registry.

    -m/--message is required and must not be blank; it is the
    instruction text the receiving agent acts on (load the item first,
    then do what the message says — see the plugin skill's notification
    section for the full contract). Newlines are collapsed to spaces:
    the monitor stream is a one-line-per-event wire contract. Limited to
    4096 characters after that collapse — the server rejects anything
    longer rather than truncating it.

### Synopsis

```
pad push <ref> [flags]
```

### Arguments

| name | type | required | description |
| --- | --- | --- | --- |
| `ref` | string | yes |  |

### Flags

| flag | type | default | description |
| --- | --- | --- | --- |
| `--message` | string |  | instruction text to push (required, max 4096 characters after whitespace collapse) |
| `--op-key` | string |  | idempotency key: re-running the SAME push with the same key answers the first push instead of delivering it again (default: a new key per invocation) |

### Examples

```bash
pad push TASK-5 --message "Pick this up next"
```

## `pad role`

Manage agent roles

Agent roles define capability specializations (e.g. Planner, Implementer, Reviewer) for human-agent work assignment.

### Synopsis

```
pad role
```

## `pad role create`

Create a new agent role

### Synopsis

```
pad role create <name> [flags]
```

### Arguments

| name | type | required | description |
| --- | --- | --- | --- |
| `name` | string | yes |  |

### Flags

| flag | type | default | description |
| --- | --- | --- | --- |
| `--description` | string |  | role description |
| `--icon` | string |  | role icon (emoji) |
| `--tools` | string |  | preferred tools/models (e.g. 'Claude Code + Sonnet 4.6') |

### Examples

```bash
pad role create "Reviewer" --description "Reviews PRs against the conventions" --icon "🔍"
```

## `pad role delete`

Delete an agent role

### Synopsis

```
pad role delete <slug>
```

### Arguments

| name | type | required | description |
| --- | --- | --- | --- |
| `slug` | string | yes |  |

### Examples

```bash
pad role delete reviewer
```

## `pad role list`

List agent roles in the workspace

### Synopsis

```
pad role list
```

### Examples

```bash
pad role list
```

## `pad role update`

Update an existing agent role

Update an existing agent role's name, slug, description,
icon, tools, or sort order.

Only flags you explicitly set are sent — every other property is left
untouched. The <slug> positional accepts either the role's current
slug ("planner") or its UUID.

NOTE: the rename flag is --new-slug, not --slug. This is deliberate:
the MCP catalog passes the positional via MCP property "slug" and
the rename target via "new_slug"; calling the CLI flag --slug too
would collide on the local stdio MCP path (Codex review on PR #574).

### Synopsis

```
pad role update <slug> [flags]
```

### Arguments

| name | type | required | description |
| --- | --- | --- | --- |
| `slug` | string | yes |  |

### Flags

| flag | type | default | description |
| --- | --- | --- | --- |
| `--description` | string |  | new description (empty string clears) |
| `--icon` | string |  | new emoji icon (empty string clears) |
| `--name` | string |  | new display name |
| `--new-slug` | string |  | rename target — new slug (kebab-case identifier) |
| `--sort-order` | int |  | new sort order (lower = appears first) |
| `--tools` | string |  | preferred tools/models string |

### Examples

```bash
pad role update planner --description "Decomposes plans into tasks"
```

```bash
pad role update reviewer --icon 👁️
```

```bash
pad role update implementer --name "Engineer" --new-slug engineer
```

## `pad server`

Manage the Pad server process and web UI

### Synopsis

```
pad server
```

## `pad server info`

Show local Pad client, connection, and server status

Show a client-oriented snapshot of this Pad installation and connection state.

This command reports local configuration, reachability, auth/session state, and
local runtime details when applicable. It does not auto-start the server and it
does not inspect remote server internals.

### Synopsis

```
pad server info
```

### Examples

```bash
pad server info
```

## `pad server open`

Open the Pad web UI in your browser

### Synopsis

```
pad server open
```

### Examples

```bash
pad server open
```

## `pad server start`

Start the Pad API server

### Synopsis

```
pad server start [flags]
```

### Flags

| flag | type | default | description |
| --- | --- | --- | --- |
| `--force` | bool |  | start even if the database schema is newer than this binary (a downgrade — risks data corruption; see the README "Upgrading Pad" section) |
| `--host` | string | `127.0.0.1` | host address to listen on |
| `--port` | int | `7777` | port to listen on |

### Examples

```bash
pad server start --port 7777
```

## `pad server stop`

Stop the background Pad server

### Synopsis

```
pad server stop
```

### Examples

```bash
pad server stop
```

## `pad session`

Manage this session's pad registry entry and push-arming

### Synopsis

```
pad session
```

## `pad session activity`

Report this worker's activity (best effort, for hooks)

### Synopsis

```
pad session activity <value>
```

### Arguments

| name | type | required | description |
| --- | --- | --- | --- |
| `value` | enum: busy\|idle | yes |  |

### Examples

```bash
pad session activity busy
```

```bash
pad session activity idle
```

## `pad session arm`

Declare that this session accepts pad push notifications

Arm this session: declare consent to receive 'pad push' notifications.

Writes a local, session-scoped arm-state file. A push monitor for this
session announces armed=true to the server on its next stream connect,
and only armed sessions receive pushes (the consent gate). Run
'pad session disarm' to withdraw consent, or 'pad session status' to see
the current state.

Re-running 'pad session arm' creates a new arm generation and ends chat
direction. To accept chat instructions again, the user must re-run
'pad chat arm --accept-instructions'.

Arming is per-session and transient. To opt a whole REPOSITORY in without
arming each session by hand, set 'push.auto_arm = true' under a [push]
table in the repo's .pad.toml (a deliberate, committed choice).

A headless session (no messaging socket) is identified by CLAUDE_PID or
PAD_SESSION_PID, exactly as for 'pad session disarm'; with neither set this
command exits non-zero.

### Synopsis

```
pad session arm
```

### Examples

```bash
pad session arm
```

## `pad session disarm`

Withdraw this session's consent to pad push notifications

Disarm this session: stop accepting 'pad push' notifications for the
rest of this session.

This holds even when the repository opted in via .pad.toml
'push.auto_arm = true' — the disconnect is session-scoped and wins for this
session. It does NOT revoke the repo's standing consent: a NEW session in
an auto_arm repo arms again. To turn auto-arm off permanently, remove
'push.auto_arm' from .pad.toml (the same deliberate edit that turned it on).

Without a messaging socket (a headless session), the disarm is tied to the
session's process, which the harness names: Claude Code exports CLAUDE_PID,
and any other harness or shell can set PAD_SESSION_PID to the pid of the
long-lived session process. With neither set, this command exits non-zero
rather than report a disarm that would expire the moment it returns. Where
the session's process cannot be checked at all (headless on Windows), the
disarm is kept for the directory until 'pad session reset'.

Idempotent.

### Synopsis

```
pad session disarm
```

### Examples

```bash
pad session disarm
```

## `pad session list`

List registered sessions on this machine with a liveness verdict each

Reads ~/.pad/sessions and reports each registered session: its owner pid,
the agent it registered as, its working directory, and whether it is
alive right now.

Liveness is decided locally and fails toward honesty: "alive" means every
signal the record carries — its messaging socket, its owner pid, and the
identity captured for each at registration where the platform supplies
one — still checks out; "dead" means one is gone or has been reused by
something else; "unknown" means one could not be examined (a platform
that cannot probe pids, a socket that cannot be stat'ed, or an owner that
this version registered in a different PID or mount namespace from this
reader's, such as a host session read from inside a sandbox or container;
a row registered before this version may still read dead there). A legacy row
(registered before sessions carried an agent name) is judged by its pid
alone: it can say a session exists but not who it is, and it matches no
--agent filter.

Everything a row says about WHO — agent, session id, and (unless
session_pid_verified is true) the owner pid itself — is what the session
declared. On Linux the pid claim is checked against the registering
process's ancestry; a consumer that needs that check reads
session_pid_verified in the JSON.

Deciding whether a NAME is in use from this output (the rule a script
needs, and where it is only as good as its inputs):

  - List WITHOUT --agent (use --cwd to scope), then apply the rule
    yourself: a row with liveness "alive", no legacy/malformed flag, and
    session_pid_verified true, whose agent is the name, means IN USE by
    that session (identify it by session_id, else session_pid).
  - Any "unknown", legacy, or malformed row scoped to the same directory
    is INDETERMINATE, never "not in use" — such a row cannot say who it
    is, so --agent NAME would have hidden it.
  - No matching row means "no registered row", not "nobody": a harness
    that never registers, or whose registration failed, is invisible.
  - Two or more alive rows for one name is ambiguous; do not pick the
    newest — registered_at is each session's own clock.
  - The registry is this OS user's; other users' sessions are not here.
  - The verdict is a sample: a session can register or exit right after.
  - A row's name IS the name the session's writes carry (BUG-2882), and
    it outranks PAD_AGENT and .pad.toml while the row is alive. A plain
    're-register' keeps it; to change it, run 'pad session register
    --agent <name>' — changing PAD_AGENT alone changes nothing.

Newest first. Use --format json for the stable shape.

### Synopsis

```
pad session list [flags]
```

### Flags

| flag | type | default | description |
| --- | --- | --- | --- |
| `--agent` | string |  | only sessions registered as this agent name ("" matches anonymous sessions) |
| `--all` | bool |  | include dead sessions |
| `--cwd` | string |  | only sessions registered from this directory (symlinks resolved on both sides) |

### Examples

```bash
pad session list
```

## `pad session prune`

Remove dead sessions' records from the local session registry

Deletes registry records whose session is dead, with each one's chat-seen
log (~/.pad/chat-seen/<pid>.log and .log.1). Never deletes a record it can
see is alive.

Records whose liveness is unknown (this platform cannot probe the owner,
this version registered the owner in a different PID or mount namespace
from this reader's, or the file is malformed) are kept unless --older-than
is given, in which
case those older than the bound are deleted too — live or not, since
unknown means exactly that; it is the only way such a registry ever
shrinks, and an explicit choice for that reason.

'pad session register' already prunes the records it can see are dead on
every call; this verb is for the unknown ones and for cleaning up
without registering.

### Synopsis

```
pad session prune [flags]
```

### Flags

| flag | type | default | description |
| --- | --- | --- | --- |
| `--older-than` | duration |  | also remove unknown-liveness records older than this (e.g. 72h) |

### Examples

```bash
pad session prune --older-than 72h
```

## `pad session register`

Register this session, and the agent it runs as, in the local session registry

Records this session — the harness session process (from $PAD_SESSION_PID,
else $CLAUDE_PID, else this process), its working directory, the agent
name it runs as, and its messaging socket's identity — to
~/.pad/sessions/<session_pid>.json, mode 0600. 'pad session list' reads
the registry back with a liveness verdict per session.

The agent name defaults to what every write is attributed to (.pad.toml
agent_name, else $PAD_AGENT, else the detected runtime); --agent overrides
it, and --agent "" registers an anonymous session. A registered name is
then what this session's writes carry from that point on — the record is
consulted before .pad.toml and the environment (BUG-2882) — so re-registering
under a different name re-attributes the session's later writes with it. An
anonymous registration leaves an environment-declared name in force.

Safe to call from any directory — it does not require a linked workspace
(.pad.toml) — and safe to call more than once per session: each call
overwrites the session's record with a fresh timestamp. Records of
sessions it can see are dead are pruned on the way (see 'pad session
prune').

### Synopsis

```
pad session register [flags]
```

### Flags

| flag | type | default | description |
| --- | --- | --- | --- |
| `--agent` | string |  | agent name to register as; becomes the name this session's writes carry (default: the current one; "" for an anonymous row) |

### Examples

```bash
pad session register --agent wren
```

## `pad session reset`

Remove this session's local arm/disarm override so auto_arm decides

Remove this session's local arm-state file, so the repository's
.pad.toml 'push.auto_arm' decides whether this session accepts pushes.

Needed mainly where a session cannot be verified (a headless session on
Windows): there a local arm or disarm is kept rather than expiring with the
session, and stays in force for the directory until reset.

Idempotent.

### Synopsis

```
pad session reset
```

### Examples

```bash
pad session reset
```

## `pad session status`

Show this session's push-arming state and the server's session view

### Synopsis

```
pad session status
```

### Examples

```bash
pad session status
```

## `pad tag`

Inspect tags used across the workspace

Tags are free-form labels on items. They span collections, so a single tag groups items of any type (an Idea and a Bug can share one tag).

### Synopsis

```
pad tag
```

## `pad tag list`

List distinct tags in the workspace with item counts

### Synopsis

```
pad tag list
```

### Examples

```bash
pad tag list
```

## `pad token`

Manage API tokens for automation and agents

Manage user-scoped API tokens (the pad_ tokens PAD_TOKEN carries).

Tokens act as the user who minted them. The secret is shown exactly once,
at mint time — the server stores only a hash and cannot show it again.

### Synopsis

```
pad token
```

### Examples

```bash
pad token create --name ci-agent
```

```bash
pad token create --name cursor --expires-in 30
```

```bash
pad token list
```

```bash
pad token rotate 7fde5e41-...
```

```bash
pad token revoke 7fde5e41-...
```

## `pad token create`

Mint a new API token (secret shown once)

### Synopsis

```
pad token create <name> [flags]
```

### Arguments

| name | type | required | description |
| --- | --- | --- | --- |
| `name` | string | yes |  |

### Flags

| flag | type | default | description |
| --- | --- | --- | --- |
| `--expires-in` | int |  | expiry in days (0 = platform default) |
| `--name` | string |  | token name (required; shown in list and audit log) |
| `--scopes` | string |  | comma-separated scopes: *, read, write, pad:read, pad:write, pad:admin (default: full access) |

### Examples

```bash
pad token create ci-deploy --scopes read --expires-in 90
```

## `pad token list`

List your API tokens (metadata only, never secrets)

### Synopsis

```
pad token list
```

### Examples

```bash
pad token list
```

## `pad token revoke`

Revoke an API token by id (immediate; cannot be undone)

Revoke an API token by its exact id (from 'pad token list').

Revocation is immediate: anything authenticating with the token fails on
its next call. The id must be exact — there is no prefix matching, so a
typo is a not-found error rather than a wrong token revoked.

### Synopsis

```
pad token revoke <token-id>
```

### Arguments

| name | type | required | description |
| --- | --- | --- | --- |
| `token-id` | string | yes |  |

### Examples

```bash
pad token revoke <token-id>
```

## `pad token rotate`

Replace a token's secret (the old one stops working immediately)

Rotate an API token by its exact id (from 'pad token list'): the server
generates a new secret and the old one stops working with the same write —
there is no grace window, so anything still using the old secret fails on
its next call. Metadata (name, scopes) is preserved; last-used resets.

The new secret is shown exactly once. --expires-in sets a new expiry in
days; without it the original expiry is preserved.

Like create, rotation needs a login session: a call authenticated by a
pad_ API token is refused with 403 session_required.

### Synopsis

```
pad token rotate <token-id> [flags]
```

### Arguments

| name | type | required | description |
| --- | --- | --- | --- |
| `token-id` | string | yes |  |

### Flags

| flag | type | default | description |
| --- | --- | --- | --- |
| `--expires-in` | int |  | new expiry in days (0 = keep the original expiry) |

### Examples

```bash
pad token rotate <token-id>
```

## `pad watch`

Create a durable watch on an item, or run the session-monitor stream

pad watch <ref>
    Create (or update) a durable, server-side watch on an item. Watches
    survive monitor restarts and padd restarts — they are not client-side
    state.

pad watch <ref> --until status=X
    Same, but the item only notifies once its status-equivalent field
    reaches X (an unconditional watch, the default, notifies on every
    status-change / assignment / comment on the item).

pad watch list
    List your active watches, across every workspace you belong to.

pad watch remove <ref>
    Stop watching an item.

pad watch --stream --for-session
    The plugin monitor command (see monitors/monitors.json). Prints one
    line per matching event to stdout in a fixed, machine-readable
    format, and one "PAD (resync) ..." line when the server says the
    stream may have missed notifications it cannot replay: after that line,
    re-check watched items rather than assuming nothing changed.

    Chat replies append a reference and server-supplied quote excerpt after
    the body (and its truncation pointer); missing/deleted quotes are omitted.
    After chat identity first resolves, ensures the owner-agent DM once per
    monitor process in the background, using the presence agent key. No agent
    name skips it; existing DMs are uncharged. Only 429 retries, waiting
    Retry-After (defaulting to 120s when the server gives no usable value),
    with at most three attempts. Success is silent; a final failure writes
    one stderr line and delivery continues.

    Every chat line is also appended, byte for byte, to
    ~/.pad/chat-seen/<harness pid>.log (0600), so the person at the agent's
    terminal can see it: the Claude Code plugin shows it above the prompt,
    and any other harness can tail the file. The pid is PAD_SESSION_PID,
    else CLAUDE_PID; with neither set, or with one that is not a pid,
    there is no log, and the first chat line writes one stderr line saying
    so. The log holds 256 KiB, then moves
    to <pid>.log.1; pad session prune removes both with the session.

    Silent on startup in three cases, and silence does not distinguish
    them: no workspace linked (retries hourly), padd unreachable
    (backoff from 5s, capped at 5min), and the server refusing the
    stream at its connection limit — a 429, which folds into that same
    backoff. See the DOC-2479 behavior contract in this command's
    source. Not meant to be run by hand; the pad plugin's monitor entry
    invokes it.

### Synopsis

```
pad watch [ref] [flags]
```

### Arguments

| name | type | required | description |
| --- | --- | --- | --- |
| `ref` | string | no |  |

### Flags

| flag | type | default | description |
| --- | --- | --- | --- |
| `--for-session` | bool |  | format output for the Claude Code plugin monitor (requires --stream) |
| `--stream` | bool |  | run the session-monitor stream (requires --for-session) |
| `--until` | string |  | optional predicate, e.g. --until status=done |

## `pad watch list`

List your active watches

### Synopsis

```
pad watch list
```

### Examples

```bash
pad watch list
```

## `pad watch remove`

Stop watching an item

### Synopsis

```
pad watch remove <ref>
```

### Arguments

| name | type | required | description |
| --- | --- | --- | --- |
| `ref` | string | yes |  |

### Examples

```bash
pad watch remove TASK-5
```

## `pad webhook`

Manage workspace webhooks

Manage webhooks that receive POST notifications when events occur.

### Synopsis

```
pad webhook
```

### Examples

```bash
pad webhook list
```

```bash
pad webhook create https://httpbin.org/post --events "item.created,item.updated"
```

```bash
pad webhook delete 7fde5e41
```

```bash
pad webhook test 7fde5e41
```

## `pad webhook create`

Register a new webhook

Register a new webhook URL to receive event notifications.

### Synopsis

```
pad webhook create <url> [flags]
```

### Arguments

| name | type | required | description |
| --- | --- | --- | --- |
| `url` | string | yes |  |

### Flags

| flag | type | default | description |
| --- | --- | --- | --- |
| `--events` | string |  | comma-separated event types (default: all) |
| `--secret` | string |  | shared secret for HMAC signature verification |

### Examples

```bash
pad webhook create https://httpbin.org/post
```

```bash
pad webhook create https://slack.com/webhook/... --events "item.created,item.updated"
```

```bash
pad webhook create https://example.com/hook --secret "mysecret"
```

## `pad webhook delete`

Delete a webhook

### Synopsis

```
pad webhook delete <id>
```

### Arguments

| name | type | required | description |
| --- | --- | --- | --- |
| `id` | string | yes |  |

### Examples

```bash
pad webhook delete <id>
```

## `pad webhook list`

List all webhooks in the workspace

### Synopsis

```
pad webhook list
```

### Examples

```bash
pad webhook list
```

## `pad webhook test`

Send a test payload to a webhook

### Synopsis

```
pad webhook test <id>
```

### Arguments

| name | type | required | description |
| --- | --- | --- | --- |
| `id` | string | yes |  |

### Examples

```bash
pad webhook test <id>
```

## `pad workspace`

Manage workspaces and workspace membership

### Synopsis

```
pad workspace
```

## `pad workspace accept`

Accept a workspace invitation from pad workspace invitations

### Synopsis

```
pad workspace accept <invitation-id>
```

### Arguments

| name | type | required | description |
| --- | --- | --- | --- |
| `invitation-id` | string | yes |  |

### Examples

```bash
pad workspace accept <invitation-id>
```

## `pad workspace audit-log`

View the compliance audit log (admin-only)

### Synopsis

```
pad workspace audit-log [flags]
```

### Flags

| flag | type | default | description |
| --- | --- | --- | --- |
| `--action` | string |  | filter by action type |
| `--actor` | string |  | filter by actor (user ID) |
| `--days` | int | `30` | number of days to look back |
| `--limit` | int | `50` | maximum number of entries |

### Examples

```bash
pad workspace audit-log --days 7
```

## `pad workspace claim`

Redeem a 6-digit claim code to add a workspace to this OAuth connection's allow-list

Redeem a 6-digit claim code at POST /api/v1/oauth/claim, granting the
calling OAuth connection access to one specific workspace.

Generate the code in the workspace's web UI ("Connect project" modal,
avatar menu). The code is valid for 5–10 minutes (sliding window).

Claim is meaningful only over cloud-mode OAuth MCP sessions where
workspace allow-lists actually constrain access. CLI session tokens
and PATs already see every workspace you belong to; running this from
the CLI succeeds (the code verifies) but the side effect no-ops —
the response 'note' field explains.

### Synopsis

```
pad workspace claim <code> [flags]
```

### Arguments

| name | type | required | description |
| --- | --- | --- | --- |
| `code` | string | yes |  |

### Flags

| flag | type | default | description |
| --- | --- | --- | --- |
| `--workspace` | string |  | Workspace slug to claim (defaults to CWD-linked workspace) |

### Examples

```bash
pad workspace claim 482913
```

## `pad workspace context`

Show or update machine-readable workspace context

Show or update the structured workspace context stored in the current workspace.

### Synopsis

```
pad workspace context
```

### Examples

```bash
pad workspace context --format json
```

```bash
pad workspace context
```

```bash
pad workspace context set --file workspace-context.json
```

```bash
cat workspace-context.json | pad workspace context set --stdin
```

## `pad workspace context set`

Replace the structured workspace context from JSON input

Replace the structured workspace context using a JSON object.

The JSON must match the workspace context schema, including optional sections like
repositories, paths, commands, stack, deployment, and assumptions.

### Synopsis

```
pad workspace context set [flags]
```

### Flags

| flag | type | default | description |
| --- | --- | --- | --- |
| `--file` | string |  | path to a JSON file containing workspace context |
| `--stdin` | bool |  | read workspace context JSON from stdin |

### Examples

```bash
pad workspace context set --file context.json
```

## `pad workspace create`

Create a workspace non-interactively (use 'pad workspace init' for the guided flow)

Create a new workspace by name. Non-interactive — no prompts, no
CWD link side effect. Hits POST /api/v1/workspaces directly with the
supplied name + optional slug + template.

For the guided flow that ensures auth, picks a template interactively,
and links the CWD, use 'pad workspace init' instead. The 'create' shape
exists to back the MCP pad_workspace.action: create route + scripts
that just want the workspace row.

When called over an OAuth-bound MCP session whose grant has
may_create_workspaces=true, the new workspace is auto-added to that
connection's allow-list (PLAN-1519 / TASK-1521 / IDEA-1517 §1) so
the agent can use it immediately without re-auth. When that grant has
may_create_workspaces=false the create is REFUSED with a 403 and no
workspace is made (IDEA-2756). Only the user can lift it, either by
re-authorizing or by enabling the flag on the existing connection at
/console/connected-apps.

### Synopsis

```
pad workspace create <name> [flags]
```

### Arguments

| name | type | required | description |
| --- | --- | --- | --- |
| `name` | string | yes |  |

### Flags

| flag | type | default | description |
| --- | --- | --- | --- |
| `--slug` | string |  | Workspace slug (default: derived from name) |
| `--template` | string |  | Template to seed collections from (run 'pad workspace init --list-templates' to see options) |

### Examples

```bash
pad workspace create "Mobile App" --template startup
```

## `pad workspace decline`

Decline a workspace invitation from pad workspace invitations

### Synopsis

```
pad workspace decline <invitation-id>
```

### Arguments

| name | type | required | description |
| --- | --- | --- | --- |
| `invitation-id` | string | yes |  |

### Examples

```bash
pad workspace decline <invitation-id>
```

## `pad workspace deleted`

List soft-deleted workspaces still within the restore window

### Synopsis

```
pad workspace deleted
```

### Examples

```bash
pad workspace deleted
```

## `pad workspace export`

Export workspace as a self-contained tar.gz bundle

Export the current workspace (collections, items, comments, versions,
and attachments) to a portable tar.gz bundle:

  pad-export.json              — workspace metadata + items + collections + ...
  attachments/manifest.json    — uuid → {filename, mime, size, content_hash}
  attachments/<uuid>.<ext>     — original attachment blobs

Pass --json to emit the legacy items-only JSON file (no attachments).
Both formats can be re-imported via 'pad workspace import'.

### Synopsis

```
pad workspace export [flags]
```

### Flags

| flag | type | default | description |
| --- | --- | --- | --- |
| `--json` | bool |  | emit legacy items-only JSON (no attachments) |
| `--output` | string |  | output file path (default: stdout) |

### Examples

```bash
pad workspace export --output backup.tar.gz
```

## `pad workspace import`

Import workspace from JSON export or tar.gz bundle

Import a workspace from a previously exported file. Creates a new
workspace with regenerated IDs.

Accepts both formats produced by 'pad workspace export':
  - .json (legacy, items only)
  - .tar.gz (new bundle, includes attachment blobs)

Format is detected by file extension. Override workspace name with --name.

### Synopsis

```
pad workspace import <file> [flags]
```

### Arguments

| name | type | required | description |
| --- | --- | --- | --- |
| `file` | string | yes |  |

### Flags

| flag | type | default | description |
| --- | --- | --- | --- |
| `--name` | string |  | override workspace name |
| `--repair-nul` | bool |  | replace NULs carried by the export with U+FFFD instead of refusing it (rewrites content; default is strict) |

### Examples

```bash
pad workspace import backup.tar.gz --name "Mobile App (restored)"
```

## `pad workspace init`

Create a workspace and link it to the current directory

Create a workspace and link it to the current directory.

Use --template to choose a workspace template:
  pad workspace init myproject --template scrum
  pad workspace init myproject --template blank    # build it out via /pad onboard

The 'blank' template ships only the system collections (Conventions,
Playbooks) plus the canonical /pad onboard playbook. Run /pad onboard
inside the workspace and the agent will adapt collections, conventions,
roles, and playbooks to whatever your project actually is.

Use --list-templates to see available templates.

Tip: 'pad init' handles everything — configure, authenticate, and create
a workspace in one step.

### Synopsis

```
pad workspace init [name] [flags]
```

### Arguments

| name | type | required | description |
| --- | --- | --- | --- |
| `name` | string | no |  |

### Flags

| flag | type | default | description |
| --- | --- | --- | --- |
| `--list-templates` | bool |  | list available workspace templates |
| `--template` | string |  | workspace template (use --list-templates to see available templates by category) |

### Examples

```bash
pad workspace init --template startup
```

## `pad workspace invitations`

List workspace invitations waiting for your answer

### Synopsis

```
pad workspace invitations
```

### Examples

```bash
pad workspace invitations
```

## `pad workspace invite`

Invite a user to the workspace

### Synopsis

```
pad workspace invite <email> [flags]
```

### Arguments

| name | type | required | description |
| --- | --- | --- | --- |
| `email` | string | yes |  |

### Flags

| flag | type | default | description |
| --- | --- | --- | --- |
| `--role` | string | `editor` | role for the invited user (owner, editor, viewer) |

### Examples

```bash
pad workspace invite alex@example.com --role editor
```

## `pad workspace join`

Accept a workspace invitation

### Synopsis

```
pad workspace join <code>
```

### Arguments

| name | type | required | description |
| --- | --- | --- | --- |
| `code` | string | yes |  |

### Examples

```bash
pad workspace join <code>
```

## `pad workspace link`

Link the current directory to an existing workspace

Link the current directory to an existing workspace by writing its .pad.toml file.

Unlike 'pad workspace init', this does NOT create a new workspace — it only links to one that already exists.

  pad workspace link myproject

An existing .pad.toml is updated, not replaced: only the workspace and the
server url change, so agent_name and [push] are kept. With --url, a directory
linked to another server is moved to that one, even when the slug is the same
there (moving a workspace to Pad Cloud):

  pad workspace link myproject --url https://app.getpad.dev

Use 'pad workspace list' to see available workspaces.

### Synopsis

```
pad workspace link <workspace>
```

### Arguments

| name | type | required | description |
| --- | --- | --- | --- |
| `workspace` | string | yes |  |

### Examples

```bash
pad workspace link mobile-app
```

## `pad workspace list`

List all workspaces

### Synopsis

```
pad workspace list
```

### Examples

```bash
pad workspace list
```

## `pad workspace members`

List workspace members

### Synopsis

```
pad workspace members
```

### Examples

```bash
pad workspace members
```

## `pad workspace restore`

Restore a soft-deleted workspace within the restore window

### Synopsis

```
pad workspace restore <slug>
```

### Arguments

| name | type | required | description |
| --- | --- | --- | --- |
| `slug` | string | yes |  |

### Examples

```bash
pad workspace restore mobile-app
```

## `pad workspace storage`

Show workspace storage usage and effective limit

Print the workspace's current attachment storage usage versus the
effective limit for the workspace owner's plan.

The effective limit follows the resolution chain:
  1. Per-user storage_bytes override (admin-set)
  2. Platform plan_limits_<plan>_storage_bytes setting
  3. Hardcoded plan default (free=100MB, pro=1GB)

On Pro the limit is one pool for the owner's whole account: usage sums every
workspace they own, including soft-deleted ones until they are purged. On Free
it is per workspace. On Pad Cloud an upload that would pass the limit is
refused; existing files stay available, and deleting files frees space. A
limit of "unlimited" indicates no enforced cap (self-hosted / workspaces with
no owner).

### Synopsis

```
pad workspace storage
```

### Examples

```bash
pad workspace storage
```

## `pad workspace switch`

Link current directory to a different workspace

### Synopsis

```
pad workspace switch <workspace>
```

### Arguments

| name | type | required | description |
| --- | --- | --- | --- |
| `workspace` | string | yes |  |

### Examples

```bash
pad workspace switch mobile-app
```

