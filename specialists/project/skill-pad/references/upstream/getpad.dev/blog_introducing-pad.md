**Title:** Introducing Pad — Pad Blog

**Author:** The Pad Team

**Date:** 2026-03-26

**Source:** [https://www.getpad.dev/blog/introducing-pad](https://www.getpad.dev/blog/introducing-pad)

---

# Page Structure Map
```text
Introducing Pad — Pad Blog
├── Why Another Project Management Tool?
├── A Single Binary
├── Built for AI Agents
├── Collections, Not Just Tasks
└── What’s Next
```

---

We’re excited to open source **Pad** — a project management tool built from the ground up for developers and AI coding agents.

## Why Another Project Management Tool?

Most project management tools are built for managers, not makers. They live in the browser, require accounts, and assume you want to context-switch away from your code to update a ticket.

We wanted something different:

- **Runs locally.** Your data stays on your machine in a SQLite database. No accounts, no cloud dependency.
- **CLI-first.** Create tasks, update statuses, and check progress without leaving your terminal.
- **Web UI included.** When you want a visual overview, a full dashboard runs at `localhost:7777` — embedded in the same binary.
- **AI-native.** A built-in `/pad` skill works with Claude Code, Cursor, Windsurf, Codex, GitHub Copilot, and more — manage your project through natural conversation.

## A Single Binary

Pad is a single Go binary. Install it with Homebrew, run `pad init`, and you’re managing a project. No Docker, no Postgres, no configuration files to wrestle with.

```
brew install PerpetualSoftware/tap/pad
cd my-project
pad init
pad item create task "Ship the thing" --priority high
```

The embedded web UI starts automatically. Open your browser and you’ve got a full dashboard with board views, list views, and a rich item editor — all reading from the same SQLite database the CLI uses.

## Built for AI Agents

This is where Pad is different. We didn’t bolt on AI support after the fact — it’s a core design principle.

The `/pad` skill lets your AI agent interact with your project naturally:

```
/pad what should I work on next?
/pad I finished the auth refactor, mark it done
/pad let's create a plan for v0.2
```

But it goes further. **Conventions** let you encode project rules that agents follow automatically:

```
pad item create convention "Run tests before completing tasks" \
  --field trigger=on-task-complete \
  --field priority=must
```

Now when any agent marks a task as done, it runs your test suite first. **Playbooks** extend this with multi-step workflows. Your AI agents learn your team’s practices and follow them consistently.

## Collections, Not Just Tasks

Pad isn’t limited to task tracking. The data model is built around **collections** — typed containers with JSON schemas:

- **Tasks** — work items with status, priority, effort, and parent linking
- **Ideas** — capture inspiration before it’s lost
- **Plans** — track project milestones and progress across tasks
- **Docs** — notes, architecture decisions, reference material

You can create custom collections too. Need a bug tracker with severity fields? A roadmap with quarter-based planning? A collection of design decisions? Define the schema and go.

**Wiki links** (`[[Item Title]]`) connect items across collections, building a knowledge graph for your project.

## What’s Next

Pad is Apache 2.0 licensed and free for local use. We’re actively working on:

- **Pad Cloud** — sync across devices, collaborate with your team
- **More templates** — specialized setups for different team workflows
- **Plugin system** — extend Pad with custom integrations

We’d love for you to try it out:

- Get Started — install and create your first project in under a minute
- GitHub — star the repo, file issues, contribute
- Try Pad Cloud — the managed version, free to start

Happy building. 🚀
