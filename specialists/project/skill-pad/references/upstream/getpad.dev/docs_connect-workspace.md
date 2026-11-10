**Title:** Connect a Workspace

**Source:** [https://www.getpad.dev/docs/connect-workspace](https://www.getpad.dev/docs/connect-workspace)

---

# Page Structure Map
```text
Connect a Workspace
├── TL;DR
├── Where to find your server URL and workspace slug
├── Prerequisites
├── What.pad.toml does
├── Switching between Pad Cloud, a remote server, and local
├── Troubleshooting
│   ├── “Workspace ‘X’ not found on https://…”
│   ├── “This directory is already linked to workspace ‘Y’; refusing to relink to ‘X’”
│   ├── “Pad is not configured. Run ‘pad auth configure’ first…”
│   ├── “Failed to connect to server at …”
│   └── My CLI command worked, but the web UI still shows the connect banner
└── What’s next
```

---

You created a workspace on the web — Pad Cloud or your own self-hosted Pad — and now you want to manage it from your terminal: run `pad item create`, hand the `/pad` agent skill to your AI tooling, or just have a `.pad.toml` link the directory so subsequent commands “just work.” This page covers the one-line connect flow.

## TL;DR

From your project directory, run:

```
pad init --url https://app.getpad.dev --workspace my-workspace
```

…replacing `https://app.getpad.dev` with your Pad server’s URL and `my-workspace` with your workspace’s slug. Pad will:

1. **Configure the CLI** to talk to that server (saved to `~/.pad/config.toml` the first time this machine is set up; after that, the server is pinned per project, below).
2. **Authenticate** in your browser (skipped if you’re already signed in to that server).
3. **Link this directory** by writing a `.pad.toml` file with the workspace slug and, for a remote or Cloud server, that server’s URL.
4. **Install the `/pad` skill** for any AI coding agent it detects (Claude Code, Cursor, Windsurf, Codex, OpenCode, Copilot, Amazon Q, Junie).

You only need to do this once per project.

## Where to find your server URL and workspace slug

The web UI surfaces both for you. Inside the workspace, click your avatar (top right) and choose **Connect a project…** — the dialog pre-fills the exact `pad init …` command for your environment, ready to copy.

If you’d rather build it by hand:

- **Server URL** is the origin you visit in the browser:
	- Pad Cloud: `https://app.getpad.dev`
		- A team self-hosted instance: whatever URL your operator gave you (e.g. `https://pad.acme.internal`)
		- A local server: `http://localhost:7777` (or whatever port you bound)
- **Workspace slug** is the slug in the URL when you’re inside a workspace: `app.getpad.dev/{username}/{workspace-slug}`. The slug is the workspace’s name lowercased and hyphenated.

## Prerequisites

If you haven’t installed pad yet, do that first. The CLI is the same binary as the server — install once and you have both.

```
# macOS & Linux (Homebrew)
brew install PerpetualSoftware/tap/pad

# Docker
docker run -p 127.0.0.1:7777:7777 -v pad-data:/data ghcr.io/perpetualsoftware/pad
```

For Windows, [download a pre-built binary from the releases page](https://github.com/PerpetualSoftware/pad/releases). For all install paths see [Installation](https://www.getpad.dev/docs#installation).

## What.pad.toml does

`pad init` writes a small file at the root of your project. Linked to Pad Cloud or another remote server, it pins both the workspace and the server:

```
workspace = "my-workspace"
url = "https://app.getpad.dev"
```

Linked to your local pad server, it holds only the workspace, because the local server is implied:

```
workspace = "my-workspace"
```

The pad CLI walks up from the current directory looking for `.pad.toml`, so any `pad` command you run inside the project knows which workspace to operate against, and, when the file has a `url`, which server to talk to. The `/pad` agent skill uses the same detection so AI agents pick up the right workspace automatically.

**Should you commit `.pad.toml`?** Generally yes. Committing it means anyone who clones the repo and has the pad CLI installed can run `pad item list`, `pad project dashboard`, etc. without first re-running `pad init`, against the right server. The file contains no secrets: the workspace slug and, for a remote workspace, the server URL. Each person still signs in with their own account. If your project is public and you’d rather not advertise the slug or the server, add `.pad.toml` to `.gitignore` instead.

**What about the skill folders?** `pad init` also writes the `/pad` skill into the repo for the AI tools it finds: `.claude/skills/pad/`, `.agents/skills/pad/`, and for some tools `.github/instructions/pad.instructions.md`, `.amazonq/rules/pad.md` or `.junie/guidelines/pad.md`. Leave these out of git. They are generated from the pad version you have installed, and `pad init` rewrites them whenever they don’t match it, so a committed copy changes every time someone with a different pad version runs it. Add the paths `pad init` reported writing to `.gitignore`; for every tool it supports, that’s:

```
.claude/skills/pad/
.agents/skills/pad/
.github/instructions/pad.instructions.md
.amazonq/rules/pad.md
.junie/guidelines/pad.md
```

A teammate who clones the repo runs `pad init` once in it. With `.pad.toml` already there, it keeps the link as committed, signs them in if they aren’t already, and installs the skill for the AI tools on their machine. To install only the skill files, `pad agent install --all` does the same without contacting the server.

Edits to these files don’t survive the next `pad init`. Put project rules in a convention instead, which every agent reads from the workspace.

## Switching between Pad Cloud, a remote server, and local

You can have multiple Pad servers and bounce between them with `--url`:

```
# This directory points at a workspace on Pad Cloud
pad init --url https://app.getpad.dev --workspace cloud-project

# A different directory points at a self-hosted instance
cd ../other-project
pad init --url https://pad.acme.internal --workspace acme-roadmap

# Yet another directory uses your local pad server (default if --url is omitted)
cd ../personal-notes
pad init
```

Each directory linked to a remote or Cloud server keeps that server’s URL in its `.pad.toml`, so commands run there always go to that server, whatever the rest of the machine is set up for. Switching one project to a different server does not move the others.

`~/.pad/config.toml` is the **global default**. The first `pad init` on a machine (or `pad auth configure`) saves the connection there; a later `pad init --url …` does not change it, it only pins its own directory. The default applies to directories linked to the local server, whose `.pad.toml` has no `url`, and to commands run outside any project.

When more than one setting names a server, the most specific wins: `--url` on the command, then the directory’s `.pad.toml` `url`, then the `PAD_URL` environment variable, then `~/.pad/config.toml`. A per-command override looks like this:

```
pad --url https://pad.acme.internal item list
```

To point an already-linked project at a different server, edit the `url` line in its `.pad.toml`, or delete the file and run `pad init --url <server> --workspace <slug>` again. Re-running `pad init` in a directory that is already linked to that workspace leaves the file as it is.

The local server’s own commands (`pad server start` / `stop`, `pad auth setup`, `pad auth configure`) ignore a directory’s `url`, so a project pinned to Pad Cloud never redirects the server you run on this machine.

## Troubleshooting

### “Workspace ‘X’ not found on https://…”

The slug doesn’t exist on that server, or your account doesn’t have access to it. After authenticating, run `pad workspace list` to see the workspaces you can connect to.

### “This directory is already linked to workspace ‘Y’; refusing to relink to ‘X’”

There’s already a `.pad.toml` in this directory or one of its parents pointing to a different workspace. To change it, edit or remove that file and re-run `pad init`. (`pad init` refuses to silently clobber an existing link.)

### “Pad is not configured. Run ‘pad auth configure’ first…”

You ran `pad init` without `--url` on a fresh machine that has no `~/.pad/config.toml` yet, in a non-interactive context (CI, scripts). Pass both `--url <server>` and `--workspace <slug>` together to make `pad init` work without prompts — that combination is the canonical non-interactive cold-start.

### “Failed to connect to server at …”

The URL is wrong, your network can’t reach it, or the server is down. Check the URL in your browser; if your team self-hosts, ask whoever runs the server.

### My CLI command worked, but the web UI still shows the connect banner

The banner refreshes when you open and close the **Connect a project…** dialog, or on a page reload. Either action will flip the banner off once you’ve created your first item from the CLI.

## What’s next

- [Add Pad to an Existing Project](https://www.getpad.dev/docs/existing-project) — setting up the workspace around a codebase you already have, and bringing in its open work
- [CLI Reference](https://www.getpad.dev/docs/cli) — every `pad` subcommand
- [Agent Integration](https://www.getpad.dev/docs/agent-integration) — how the `/pad` skill works in Claude Code, Cursor, and other AI coding tools
- [Web UI Guide](https://www.getpad.dev/docs/web-ui) — keyboard shortcuts and power-user features
- [Configuration](https://www.getpad.dev/docs/configuration) — what lives in `~/.pad/config.toml` and how to manage multiple servers
