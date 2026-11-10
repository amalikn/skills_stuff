**Title:** CLI Reference

**Source:** [https://www.getpad.dev/docs/cli](https://www.getpad.dev/docs/cli)

---

# Page Structure Map
```text
CLI Reference
├── Quick Start
│   └── pad init
├── Workspace Commands
│   ├── pad auth configure
│   ├── pad auth setup
│   ├── pad auth login
│   ├── pad auth logout
│   ├── pad auth whoami
│   ├── pad auth reset-password
│   ├── pad workspace init
│   ├── pad workspace list
│   ├── pad workspace link
│   ├── pad workspace switch
│   ├── pad workspace members
│   ├── pad workspace invite
│   ├── pad workspace join
│   ├── pad workspace context
│   ├── pad workspace context set
│   ├── pad project dashboard
│   └── pad project next
├── Item Commands
│   ├── pad item create
│   ├── pad item list
│   ├── pad item show
│   ├── pad item update
│   ├── pad item move
│   ├── pad item bulk-update
│   ├── pad item comment
│   ├── pad item comments
│   ├── pad item star / pad item unstar / pad item starred
│   ├── pad item delete
│   ├── pad item edit
│   └── pad item search
├── Collection Commands
│   ├── pad collection list
│   └── pad collection create
├── Agent Roles
│   ├── pad role list
│   ├── pad role create
│   └── pad role delete
├── Webhooks
│   ├── pad webhook list
│   ├── pad webhook create
│   ├── pad webhook test
│   └── pad webhook delete
├── Playbooks
│   ├── pad playbook list
│   ├── pad playbook show
│   └── pad playbook run
├── Bootstrap
│   └── pad bootstrap
├── Sessions
│   ├── pad session register
│   ├── pad session list
│   └── pad session prune
├── Library
│   ├── pad library list
│   └── pad library activate
├── Database
│   ├── pad db backup
│   ├── pad db restore
│   └── pad db migrate-to-pg
├── Intelligence Commands
│   ├── pad project standup
│   ├── pad project changelog
│   └── pad project watch
├── Query Commands
│   ├── pad project ready
│   ├── pad project stale
│   ├── pad item related
│   └── pad item implemented-by
├── Dependency Commands
│   ├── pad item block
│   ├── pad item blocked-by
│   ├── pad item deps
│   └── pad item unblock
├── Lineage Commands
│   ├── pad item split-from
│   ├── pad item supersedes
│   ├── pad item implements
│   ├── pad item unsplit
│   ├── pad item unsupersede
│   └── pad item unimplements
├── Structured Context Commands
│   ├── pad item note
│   └── pad item decide
├── Setup Commands
│   ├── pad agent install
│   ├── pad server start
│   ├── pad server stop
│   ├── pad server open
│   ├── pad server info
│   └── Onboard a workspace
├── Data Commands
│   ├── pad workspace export
│   └── pad workspace import
├── GitHub Integration
│   ├── pad github link
│   ├── pad github status
│   └── pad github unlink
├── Attachments
│   ├── pad attachment list
│   ├── pad attachment show
│   ├── pad attachment view
│   ├── pad attachment download
│   └── pad attachment upload
├── Output Formats
└── MCP integration
```

---

Pad’s CLI is the primary interface for managing your project. All commands operate on the workspace detected from `.pad.toml` in your directory tree.

## Quick Start

### pad init

Smart entry point — detects what’s needed for this project and walks you through it.

```
pad init
```

In order, it: configures the connection (local server / remote / Docker), starts the local server if needed, creates the first admin account on a fresh install, logs you in if needed, creates or links a workspace, and installs the `/pad` skill for any AI tools detected in this project. Run from the project root.

If you’d rather drive each step explicitly, use the lower-level commands documented below (`pad auth configure`, `pad auth setup`, `pad workspace init`, `pad agent install`).

## Workspace Commands

### pad auth configure

Configure how this Pad client connects to a server.

```
pad auth configure
pad auth configure --mode local
pad auth configure --mode remote --url http://192.168.0.3:7777
pad auth configure --mode docker --url http://127.0.0.1:7777
```

Use `Local` for the default laptop workflow where Pad auto-starts a local server. Use `Remote` or `Docker` when this client should connect to an already-managed Pad server instead of starting one itself.

**Options:**

- `--mode` — Connection mode: `local`, `remote`, `docker`
- `--url` — Base URL for remote or Docker-managed Pad servers
- `--host` — Local server bind host override for `local` mode
- `--port` — Local server bind port override for `local` mode

### pad auth setup

Initialize a fresh Pad instance by creating the first admin account on the server host.

```
pad auth setup
```

For `local` mode, run this directly on the machine managing the local Pad server. For `docker`, run it inside the container, for example:

```
docker exec -it <container> pad auth setup
```

For `remote`, run `pad auth setup` on the machine or container where the Pad server is running.

### pad auth login

Sign in to Pad using email and password. Credentials are saved to `~/.pad/credentials.json` (mode 0600) and the CLI auto-attaches the resulting token to subsequent requests.

```
pad auth login
```

### pad auth logout

Sign out, removing the stored credentials.

```
pad auth logout
```

### pad auth whoami

Show the currently signed-in user.

```
pad auth whoami
pad auth whoami --format json
```

### pad auth reset-password

Recover a locked-out account when email isn’t configured. Run it **on the server host** — it uses a loopback-only endpoint (the same trust model as `pad auth setup`), so it needs no login and refuses proxied or remote requests. Disabled in cloud mode.

```
# Print a single-use reset link to open in a browser:
pad auth reset-password user@example.com

# Or set a random temporary password, printed to the terminal (headless boxes).
# Log in with it, then change it immediately — existing sessions are signed out:
pad auth reset-password user@example.com --temp-password
```

See [Self-Hosting → Forgotten password (locked out)](https://www.getpad.dev/docs/self-hosting#forgotten-password-locked-out) for the full recovery flow.

### pad workspace init

Initialize a new Pad workspace in the current directory.

```
pad workspace init
pad workspace init --template scrum
pad workspace init --template product
```

Run `pad auth configure` first if this client has not been set up yet.

On a fresh Pad instance, run `pad auth setup` before `pad workspace init` so the first admin account exists.

**Options:**

- `--template` — Workspace template: `startup` (default), `scrum`, `product`, `demo`, `hiring`, `interviewing`. Run `pad workspace init --list-templates` for the live catalog grouped by category.
- `--list-templates` — Print the available templates grouped by category and exit.

### pad workspace list

List all workspaces you have access to.

```
pad workspace list
pad workspace list --format json
```

### pad workspace link

Link the current directory to an existing workspace.

```
pad workspace link my-project
```

### pad workspace switch

Re-link the current directory to a different workspace.

```
pad workspace switch other-project
```

### pad workspace members

List workspace members and pending invitations.

```
pad workspace members
pad workspace members --format json
```

### pad workspace invite

Invite a user to the current workspace by email. If the user already exists, they’re added directly. Otherwise an invitation join code is generated (and emailed if email is configured).

```
pad workspace invite alice@example.com
pad workspace invite bob@example.com --role viewer
```

**Options:**

- `--role` — Role to assign: `owner`, `editor`, `viewer` (default: `editor`)

### pad workspace join

Accept a workspace invitation using the join code.

```
pad workspace join INV-ABC123
```

### pad workspace context

Show the machine-readable workspace context stored with the current workspace.

```
pad workspace context
pad workspace context --format json
```

Use this to inspect the structured repository, command, stack, deployment, and assumption metadata that agents can rely on.

### pad workspace context set

Replace the current workspace context from a JSON object.

```
pad workspace context set --file workspace-context.json
cat workspace-context.json | pad workspace context set --stdin
```

The JSON payload can include:

- `repositories`
- `paths`
- `commands`
- `stack`
- `deployment`
- `assumptions`

### pad project dashboard

Show a project dashboard with collection summaries, active plans, and attention items.

```
pad project dashboard
pad project dashboard --format json
```

### pad project next

Get a recommendation for what to work on next, based on project plans and priority.

```
pad project next
pad project next --format json
```

## Item Commands

### pad item create

Create a new item in a collection. Collection names accept singular forms (`task` → `tasks`, `idea` → `ideas`).

```
pad item create task "Fix OAuth redirect" --priority high
pad item create idea "Real-time collaboration" --category infrastructure
pad item create plan "API Redesign" --status active
pad item create doc "Auth Architecture" --category architecture --stdin <<< "# Auth\n\nContent here..."
```

**Options:**

- `--status` — Item status (collection-specific options)
- `--priority` — Priority level: `low`, `medium`, `high`, `critical`
- `--assignee` — Assignee name
- `--category` — Category label
- `--content` — Item content (markdown)
- `--stdin` — Read content from stdin
- `--field key=value` — Set any custom field
- `--parent <ref>` — Link this item to a parent (e.g. `--parent PLAN-3` to attach a task to a plan). Parents track child progress automatically.

### pad item list

List items, optionally filtered by collection and fields.

```
pad item list                          # All open items
pad item list tasks                    # Open tasks
pad item list tasks --status done      # Completed tasks
pad item list --all                    # Everything including done/archived
pad item list --field quarter=2026-Q1  # Filter by custom field
pad item list --format json            # JSON output
```

**Options:**

- `--status` — Filter by status
- `--priority` — Filter by priority
- `--all` — Include done/archived items
- `--field key=value` — Filter by any field
- `--sort` — Sort field (e.g. `priority`, `created_at`)
- `--group-by` — Group results by field (e.g. `status`, `priority`)
- `--limit` — Maximum number of items to return

### pad item show

Show full details of an item by slug.

```
pad item show fix-oauth-redirect
pad item show fix-oauth-redirect --format json
pad item show fix-oauth-redirect --format markdown
```

### pad item update

Update an item’s fields. Only specified fields are changed. Accepts the same `--parent` flag as create; to REMOVE a parent link, use `--clear-parent`. An empty `--parent ""` does not detach and is refused — it silently did nothing for a long time, which is what this line used to recommend.

```
pad item update fix-oauth --status done --comment "Verified in staging"
pad item update fix-oauth --priority critical --assignee "Alice"
pad item update fix-oauth --field effort=m
pad item update fix-oauth --title "Fix OAuth redirect bug"
pad item update fix-oauth --parent PLAN-3   # Attach to plan
pad item update fix-oauth --stdin <<< "Updated content..."
```

The `--comment` flag attaches a short note to the change so the item’s history shows *why* a status moved. Recommended for every status transition.

### pad item move

Move an item between collections, migrating its fields to the destination schema.

```
pad item move TASK-5 bugs       # Re-classify TASK-5 as a bug
```

### pad item bulk-update

Update many items in one call.

```
pad item bulk-update --status done TASK-5 TASK-8 TASK-12
pad item bulk-update --priority high TASK-3 TASK-4
```

### pad item comment

Add a comment to an item. Optional `--reply-to <comment-id>` for threaded replies.

```
pad item comment TASK-5 "Investigated the race condition; root cause is in the mutex handler."
pad item comment TASK-5 "Good catch, fixed in abc123" --reply-to <comment-id>
```

### pad item comments

List all comments on an item.

```
pad item comments TASK-5
pad item comments TASK-5 --format json
```

### pad item star / pad item unstar / pad item starred

Star an item to surface it in the sidebar’s quick-access list.

```
pad item star TASK-5
pad item unstar TASK-5
pad item starred                  # List your starred items
pad item starred --format json
```

### pad item delete

Archive an item (soft delete).

```
pad item delete fix-oauth-redirect
```

### pad item edit

Open an item in your `$EDITOR` for inline editing.

```
pad item edit fix-oauth-redirect
```

### pad item search

Full-text search across all items in the workspace.

```
pad item search "OAuth"
pad item search "OAuth" --format json
```

## Collection Commands

### pad collection list

List all collections in the workspace with item counts.

```
pad collection list
pad collection list --format json
```

### pad collection create

Create a custom collection with typed fields.

```
pad collection create "Bugs" --fields "severity:select:low,medium,high,critical; browser:text; reproducible:select:yes,no,sometimes" --icon "🐛"
```

**Field syntax:** `key:type[:options]` separated by semicolons.

**Field types:** `text`, `select`, `multi_select`, `number`, `date`, `checkbox`, `url`, `relation`

## Agent Roles

Roles let you label items by the kind of thinking they require — Planner, Implementer, Reviewer, Researcher, etc. Items can be assigned to a `(user, role)` pair so each agent or human pulls work matching their capability profile.

### pad role list

List the roles defined for the current workspace.

```
pad role list
pad role list --format json
```

### pad role create

Create a new role.

```
pad role create "Designer" --description "UX research, IA, visual design" --icon "🎨"
```

**Options:**

- `--description` — One-line description shown in the UI
- `--icon` — Emoji shown next to the role name

### pad role delete

Delete a role by slug.

```
pad role delete designer
```

## Webhooks

Webhooks POST a JSON payload to a configured URL whenever workspace events happen — items created/updated/deleted, comments added, etc. Each delivery includes an `X-Pad-Signature` header (HMAC-SHA256) when a secret is configured.

### pad webhook list

List configured webhooks.

```
pad webhook list
pad webhook list --format json
```

### pad webhook create

Register a webhook URL.

```
pad webhook create https://example.com/hook
pad webhook create https://example.com/hook --events "item.created,item.updated"
pad webhook create https://example.com/hook --secret "shared-hmac-secret"
```

**Options:**

- `--events` — Comma-separated event types. Default is all. Available: `item.created`, `item.updated`, `item.deleted`, `item.moved`, `comment.created`.
- `--secret` — Shared HMAC secret used to sign each delivery.

### pad webhook test

Send a sample payload to a webhook, useful for verifying receiver wiring.

```
pad webhook test 7fde5e41
```

### pad webhook delete

Remove a webhook by ID.

```
pad webhook delete 7fde5e41
```

## Playbooks

Playbooks are workspace-owned, user-invokable procedures — see [Playbooks →](https://www.getpad.dev/docs/playbooks) for the author guide. The CLI exposes three subcommands:

### pad playbook list

List the workspace’s playbooks. Metadata only (slug, invocation\_slug, trigger, status, has\_arguments, summary); same shape as the bootstrap response.

```
pad playbook list
pad playbook list --format json
```

### pad playbook show

Show a playbook’s full body and metadata. Accepts the `invocation_slug` (e.g. `ship`), the item slug, or the issue ref (`PLAYB-1160`).

```
pad playbook show ship
pad playbook show release --format json
```

### pad playbook run

Bind args to a playbook’s declared spec and return the rendered body + bound args. **Side-effect-free** — the server never executes a playbook; it parses the args and hands the body back so the agent (or a human reading the output) executes the steps.

```
pad playbook run ship PLAN-1377 stop-after-each merge-strategy=rebase
pad playbook run release 0.5.0
```

Parsing rules:

- Required positional args first, in declared order.
- Flag-typed args: bareword presence (`stop-after-each`).
- Other typed args: `key=value` form (`merge-strategy=rebase`, `limit=3`).
- Refs accept either issue IDs (`TASK-5`) or item slugs.

## Bootstrap

### pad bootstrap

One round-trip workspace overview: user + collections + always-on conventions + roles + playbook metadata + dashboard + recent activity. Use to prime an agent’s context at session start without making six separate calls.

```
pad bootstrap --format json
```

Same payload as the `pad://workspace/{ws}/bootstrap` MCP resource and as `pad_set_workspace`’s embedded response.

## Sessions

A local registry of the agent sessions running on this machine, and which agent each one is working as. Nothing here talks to the server: the records live in `~/.pad/sessions`, mode 0600, and never leave the machine. What a record says about *who* — the agent name, the session id — is what the session declared, exactly like the agent name on writes.

### pad session register

Record this session: the harness session process (`$PAD_SESSION_PID`, else `$CLAUDE_PID`, else the calling process), its working directory, its messaging socket’s identity (what liveness is judged against), and the agent name its writes carry (`.pad.toml` `agent_name`, else `$PAD_AGENT`, else the detected runtime). The Claude Code plugin runs this on session start; any other harness calls it from its own session-start hook.

```
pad session register                  # name from .pad.toml / PAD_AGENT / runtime
pad session register --agent reviewer # explicit name
pad session register --agent ""       # anonymous
```

Safe to run more than once — each call refreshes the session’s one record — and it prunes the records of sessions it can see are dead on the way.

### pad session list

Registered sessions with a liveness verdict each. `alive` means every signal the record carries — its messaging socket, its owner pid, and the identity captured for each at registration — still checks out. `dead` means one of them is gone or has been taken over by something else: a socket rebound at the same path is a different session, and a reused pid is not the one that registered, where the platform records a process start token to tell them apart (Linux does; without one, a live pid is taken at face value). `unknown` means one of them could not be examined (a platform that cannot probe pids, a socket that cannot be stat’ed) and nothing was dead. Newest first; dead rows are hidden unless `--all`.

```
pad session list
pad session list --agent reviewer --format json
pad session list --cwd /path/to/repo --all
```

`--format json` is the stable shape: `session_pid`, `session_pid_source` (`PAD_SESSION_PID`, `CLAUDE_PID` or `self`; `legacy-socket` / `legacy-registrar` on a legacy row), `session_pid_verified`, `agent`, `cwd`, `session_id`, `liveness`, `registered_at`, `messaging_socket_path`, `path`, plus `legacy` and `malformed` where they apply. `session_pid_verified` is true when the recorded pid was checked against the registering process’s ancestry (Linux), and when the registering process IS the session, which needs no check; it is false when the claim could not be checked. `legacy` marks a row written before sessions carried an agent name; `malformed` marks a file that no longer parses as a registration. Neither can say WHO a session is, so neither matches an `--agent` filter — including `--agent ""`.

Reading the output as a decision — “is this name in use here right now?” — takes a rule: count only rows that are `alive`, not `legacy`/`malformed`, and `session_pid_verified`; treat `unknown`, legacy, or malformed rows in the same directory as indeterminate rather than free (so list without `--agent` and filter yourself); read an empty result as “no registered row”, not “nobody” — a harness that never registers is invisible; and never pick between two alive rows by `registered_at`, which is each session’s own clock. A row carries the name the session registered under, so a window that changes its `PAD_AGENT` afterwards is still listed under the old one until it runs `pad session register` again. `--cwd` matches directory identity (symlinks resolved on both sides). The registry is per OS user.

### pad session prune

Remove dead sessions’ records. A record the command can see is alive is never touched; `unknown` ones (and malformed files) go only under an explicit age bound — live or not, since unknown means exactly that.

```
pad session prune
pad session prune --older-than 72h
```

## Library

Pre-built conventions and playbooks you can adopt without writing them yourself.

### pad library list

Browse the library.

```
pad library list
pad library list --type conventions
pad library list --type playbooks
```

### pad library activate

Copy a library item into the current workspace and mark it active.

```
pad library activate "Run tests before completing tasks"
```

## Database

Database management for backups, restores, and migrations.

### pad db backup

Back up the database. SQLite produces a copy of the `.db` file; PostgreSQL produces a `pg_dump` SQL file.

```
pad db backup                                 # Default file name with timestamp
pad db backup --output ~/pad-backup.db
pad db backup --cron                          # Structured log output for cron jobs
```

### pad db restore

Restore a database from a backup file. Stop the server first.

```
pad db restore ~/pad-backup.db
```

### pad db migrate-to-pg

Migrate from SQLite to PostgreSQL. Reads the current SQLite DB and writes it into a fresh PostgreSQL database. Run once when promoting a single-user install to a multi-user shared deployment.

```
pad db migrate-to-pg --target "postgres://pad:secret@localhost:5432/pad"
```

## Intelligence Commands

### pad project standup

Auto-generate a daily standup report from recent activity.

```
pad project standup                 # Yesterday's completed, today's in-progress, blockers
pad project standup --days 3        # Look back 3 days
pad project standup --format json   # Machine-readable output
```

**Options:**

- `--days` — Number of days to look back (default: 1)

### pad project changelog

Generate release notes from completed items, grouped by collection.

```
pad project changelog                              # Last 7 days
pad project changelog --days 14                    # Last 2 weeks
pad project changelog --since 2026-03-01           # Since a specific date
pad project changelog --parent open-source-launch   # Items under a specific parent
pad project changelog --format markdown             # GitHub Releases-ready output
```

**Options:**

- `--days` — Number of days to look back (default: 7)
- `--since` — Only show items completed after this date (YYYY-MM-DD)
- `--parent` — Filter to items under a specific parent (plan, idea, etc.)
- `--format markdown` — Clean markdown for GitHub Releases

### pad project watch

Stream real-time workspace activity to your terminal via SSE.

```
pad project watch
```

Shows colored events as they happen — item creation, updates, deletions. Agent activity is highlighted in purple. Press `Ctrl+C` to stop.

## Query Commands

### pad project ready

Show the current actionable next items, using the same suggestion logic that powers `pad project next`.

```
pad project ready
pad project ready --format json
```

### pad project stale

Show items that need attention because they are stalled, blocked, overdue, or otherwise falling out of the active workflow.

```
pad project stale
pad project stale --format json
```

### pad item related

Show the direct relationship graph around an item, grouped by dependency, lineage, wiki-link, and generic related-item sections.

```
pad item related TASK-126
```

### pad item implemented-by

Show the incoming implementation items for an idea, task, or other parent item.

```
pad item implemented-by IDEA-108
```

## Dependency Commands

### pad item block

Mark that one item blocks another.

```
pad item block TASK-5 TASK-8    # TASK-5 blocks TASK-8
```

### pad item blocked-by

Mark that an item is blocked by another.

```
pad item blocked-by TASK-8 TASK-5   # TASK-8 is blocked by TASK-5
```

### pad item deps

Show all dependencies for an item.

```
pad item deps TASK-8
```

### pad item unblock

Remove a blocking dependency.

```
pad item unblock TASK-5 TASK-8
```

## Lineage Commands

### pad item split-from

Mark that one item was split from another item.

```
pad item split-from TASK-122 TASK-121   # TASK-122 was split from TASK-121
```

### pad item supersedes

Mark that one item supersedes another.

```
pad item supersedes TASK-130 TASK-118   # TASK-130 supersedes TASK-118
```

### pad item implements

Mark that one item implements another.

```
pad item implements TASK-121 IDEA-108   # TASK-121 implements IDEA-108
```

### pad item unsplit

Remove a split-from relationship.

```
pad item unsplit TASK-122 TASK-121
```

### pad item unsupersede

Remove a supersedes relationship.

```
pad item unsupersede TASK-130 TASK-118
```

### pad item unimplements

Remove an implements relationship.

```
pad item unimplements TASK-121 IDEA-108
```

## Structured Context Commands

### pad item note

Append an implementation note to an item. Use `--details` for short inline context or `--stdin` for longer notes.

```
pad item note TASK-125 "Added typed item metadata" --details "Expose implementation notes and decisions as top-level item fields"
```

### pad item decide

Append a decision log entry to an item. Use `--rationale` for the tradeoff or `--stdin` for longer rationale text.

```
pad item decide TASK-125 "Store structured notes in reserved item fields" --rationale "Avoids a schema migration for the first cut"
```

## Setup Commands

### pad agent install

Install the `/pad` skill for your AI coding tools. Auto-detects tools in use.

```
pad agent install              # Auto-detect and install
pad agent install claude       # Claude Code
pad agent install cursor       # Cursor / Codex / Windsurf
pad agent install copilot      # GitHub Copilot
pad agent install amazon-q     # Amazon Q
pad agent install junie        # JetBrains Junie
pad agent status               # Show supported tools and status
pad agent install --all        # Install for all detected tools
pad agent update               # Update installed integrations
```

### pad server start

Start the Pad API server (and embedded web UI) in the foreground.

```
pad server start
pad server start --host 0.0.0.0 --port 7777
```

Most users don’t need to call this — the CLI auto-starts a local server when needed. Use it explicitly only when running Pad as a service, in a container, or on a non-default port.

### pad server stop

Stop the local Pad server managed by this CLI.

```
pad server stop
```

### pad server open

Open the Pad web UI in your default browser.

```
pad server open
```

### pad server info

Show a client-oriented snapshot of how this Pad CLI is configured and connected. This includes the configured mode and URL, whether the server is reachable, current auth state, the linked workspace when available, and local runtime details like the DB path and local server PID in local mode. It does not inspect remote server internals.

```
pad server info
pad server info --format json
```

### Onboard a workspace

Workspace setup is driven by the `onboard` playbook, not a CLI subcommand. Every new workspace ships with it auto-activated. Open an agent session in the workspace directory and run:

```
/pad onboard
```

The agent walks an interview, detects your build/test/CI tooling, and adapts your collections, conventions, roles, and playbooks to match the project.

## Data Commands

### pad workspace export

Export a workspace to a JSON file for backup or migration.

```
pad workspace export > backup.json
pad workspace export --format json
```

### pad workspace import

Import a workspace from a JSON export.

```
pad workspace import < backup.json
```

## GitHub Integration

### pad github link

Link the current branch’s GitHub PR to a Pad item. Auto-detects item refs from branch names (e.g. `fix/TASK-5-oauth-bug` links to TASK-5).

```
pad github link TASK-5          # Link current branch's PR to TASK-5
pad github link                 # Auto-detect from branch name
```

Requires the [GitHub CLI](https://cli.github.com/) (`gh`).

### pad github status

Show PR status for linked items.

```
pad github status               # All items with linked PRs
pad github status TASK-5        # PR status for one item
pad github status --format json # Machine-readable output
```

### pad github unlink

Remove a PR link from an item.

```
pad github unlink TASK-5
```

## Attachments

Pad items can carry image and file attachments. They appear in item content as `` for images or `[label](pad-attachment:<uuid>)` for files. The CLI fetches attachments through the same authenticated REST API the web UI uses, so it works on every Pad install (local SQLite, Pad Cloud, remote/Postgres) and respects workspace ACLs.

### pad attachment list

List attachments in the current workspace, with optional filters.

```
pad attachment list                              # all originals (newest first)
pad attachment list --item TASK-5                # attachments on a specific item
pad attachment list --category image --limit 20  # filter by MIME bucket
pad attachment list --unattached                 # orphan uploads with no parent item
pad attachment list --format json                # machine-readable
```

Categories: `image`, `video`, `audio`, `document`, `text`, `archive`, `other`.

### pad attachment show

Print metadata (MIME, size, filename, ETag, Last-Modified) without transferring the bytes. Uses HTTP HEAD under the hood, so it’s cheap.

```
pad attachment show <attachment-id>
pad attachment show <attachment-id> --format json
pad attachment show <attachment-id> --variant thumb-md
```

### pad attachment view

Fetch an attachment to a file and print the absolute path to stdout. With no `-o` flag, the file lands in a fresh OS temp directory using the attachment’s stored filename — designed for AI agents to use as `$(pad attachment view <id>)`.

```
pad attachment view <attachment-id>                  # → /tmp/.../filename.png
pad attachment view <attachment-id> -o ./pic.png     # save to a chosen path
pad attachment view <attachment-id> --variant thumb-sm
pad attachment view <attachment-id> --format json    # {path,mime,size}
```

This is the recommended command for AI agents (Claude Code, Cursor, etc.) when they encounter `pad-attachment:<uuid>` references in item content. **Never read directly from `~/.pad/attachments/`** — that bypasses workspace ACLs, doesn’t work on Pad Cloud / remote / Postgres deployments, and breaks when storage moves to S3.

### pad attachment download

Download an attachment to an explicit path, or stream to stdout for piping into another tool.

```
pad attachment download <attachment-id> ./screenshot.png
pad attachment download <attachment-id> --variant thumb-md ./thumb.png
pad attachment download <attachment-id> -  | open -f -a Preview
```

The file case writes to a sibling temp file and atomically renames on success, so a partial download never truncates an existing destination.

### pad attachment upload

Upload a local file as an attachment, optionally associating it with an item. Pass `-` instead of an item ref for an orphan upload.

```
pad attachment upload TASK-5 ./screenshot.png
pad attachment upload TASK-5 ./design.pdf --filename "Design v2.pdf"
pad attachment upload - ./standalone.zip                         # no parent item
```

## Output Formats

All commands support the global `--format` flag with three options:

- `table` — Human-readable formatted output (default)
- `json` — Machine-readable JSON for scripting and AI agents
- `markdown` — Markdown-formatted output
```
pad item list tasks --format json | jq '.[] | .title'
pad item show fix-oauth-redirect --format markdown
```

## MCP integration

Want a desktop AI app (Claude Desktop, Cursor, Windsurf) to call these commands directly? Pad ships a local MCP server — every command on this page becomes a tool in the agent’s tool list, plus resources for items / dashboard / collections and prompts for multi-step workflows.

```
pad mcp install claude-desktop   # or: cursor, windsurf, --all
pad mcp status                   # see what's installed
```

Full guide: [Pad MCP — Local](https://www.getpad.dev/mcp/local).
