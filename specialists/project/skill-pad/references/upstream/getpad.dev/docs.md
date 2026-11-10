**Title:** Getting Started

**Source:** [https://www.getpad.dev/docs](https://www.getpad.dev/docs)

---

# Page Structure Map
```text
Getting Started
├── Installation
│   ├── Homebrew (macOS & Linux)
│   ├── Binary Download
│   ├── Docker
│   └── From Source
├── Quick Start
│   ├── 1\. Initialize Pad
│   ├── 2\. Create your first task
│   ├── 3\. Open the web UI (local mode)
│   ├── 4\. Use the CLI
│   └── 5\. Talk to your AI agent
└── What’s Next?
```

---

Pad is a project management tool built for developers and AI agents. It ships as a single binary with an embedded web UI, a powerful CLI, and a natural-language skill that works with any major AI coding tool.

## Installation

### Homebrew (macOS & Linux)

```
brew install PerpetualSoftware/tap/pad
```

### Binary Download

Pre-built binaries for macOS, Linux, and Windows are on the [releases page](https://github.com/PerpetualSoftware/pad/releases).

### Docker

```
docker run -p 127.0.0.1:7777:7777 -v pad-data:/data ghcr.io/perpetualsoftware/pad
```

For an install you keep, pin a release tag and use Docker Compose for PostgreSQL. See [Self-hosting](https://www.getpad.dev/docs/self-hosting#docker).

### From Source

```
git clone https://github.com/PerpetualSoftware/pad.git
cd pad
make build
# Binary is at ./pad
```

`go install github.com/PerpetualSoftware/pad/cmd/pad@latest` is **not supported** for Pad — the embedded SvelteKit web UI must be built and embedded during the binary build, which `go install` skips. Use one of the paths above.

After installation, verify it’s working:

```
pad --version
```

## Quick Start

This walkthrough runs Pad on your computer. When `pad init` asks how to connect, choose **Local**, and pick the `startup` template, which includes Tasks, Ideas, Plans and Docs. With another template, use its collection names.

Using Pad Cloud or an existing workspace? Follow [Connect a Workspace](https://www.getpad.dev/docs/connect-workspace) instead. Cloud workspaces are created at [app.getpad.dev](https://app.getpad.dev/).

### 1\. Initialize Pad

Navigate to your project directory and run:

```
pad init
```

In local mode, `pad init` configures the connection, starts the local server, creates the first admin account on a fresh install, logs you in, links the directory to a Pad workspace (writing `.pad.toml`), and installs the `/pad` skill for any AI coding tools it detects in the project.

With the startup template, your workspace includes Tasks, Ideas, Plans, Docs, Conventions and Playbooks. Safe to re-run anytime — `pad init` skips finished steps and prints a status summary.

> **Started on the web?** If you already created your workspace in the Pad Cloud or self-hosted UI and you’re connecting it to your local repo, run `pad init --url <server> --workspace <slug>` instead. See [Connect a Workspace](https://www.getpad.dev/docs/connect-workspace) for the full walkthrough. Adding Pad to a project you already work in? See [Add Pad to an Existing Project](https://www.getpad.dev/docs/existing-project).

### 2\. Create your first task

```
pad item create task "Set up CI pipeline" --priority high
```

### 3\. Open the web UI (local mode)

In local mode, `pad init` automatically starts a local server. Open your browser to:

```
http://localhost:7777
```

You’ll see a dashboard with your workspace, collections, and the task you just created. You can switch between board and list views, edit items, and manage your project visually.

### 4\. Use the CLI

```
# List open tasks
pad item list tasks

# Update a task status
pad item update set-up-ci-pipeline --status in-progress

# See your project dashboard
pad project dashboard

# Get a recommendation for what to work on next
pad project next
```

### 5\. Talk to your AI agent

`pad init` already installed the `/pad` skill for any AI tools it detected. Open a fresh agent session in your project and say:

```
/pad onboard
```

Every new workspace ships with the canonical `onboard` playbook auto-activated. The agent walks an interview, inspects your codebase if it has shell access, and adapts your workspace’s collections, conventions, roles, and playbooks to match your actual project. After that, just talk to your project:

```
/pad what should I work on next?
```

Your AI agent can create tasks, update statuses, create plans, and query your project through natural conversation. To install the skill for additional tools, or for the full setup details, see the [Agent Integration](https://www.getpad.dev/docs/agent-integration) guide.

## What’s Next?

- **[Collections & Schemas](https://www.getpad.dev/docs/collections)** — Learn about Pad’s data model and how to create custom collections
- **[Playbooks](https://www.getpad.dev/docs/playbooks)** — Author invokable procedures the agent can run with `/pad <slug>`
- **[CLI Reference](https://www.getpad.dev/docs/cli)** — Full command reference with examples
- **[Web UI Guide](https://www.getpad.dev/docs/web-ui)** — Tour the web dashboard
- **[Agent Integration](https://www.getpad.dev/docs/agent-integration)** — Set up the `/pad` skill for your AI tools
