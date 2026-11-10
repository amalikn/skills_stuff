**Title:** Agent Integration

**Source:** [https://www.getpad.dev/docs/agent-integration](https://www.getpad.dev/docs/agent-integration)

---

# Page Structure Map
```text
Agent Integration
├── Installing the Skill
│   ├── Supported Tools
│   └── Managing Installations
├── The /pad Skill
│   └── How It Works
├── Conventions
│   ├── Convention Fields
│   └── How Agents Use Conventions
├── Playbooks
├── Teaching Your Agent
└── Machine-Readable Output
```

---

Pad is built from the ground up to work with AI coding agents. The `/pad` skill lets your agent manage your project through natural conversation — and it works with any major AI coding tool.

> **Using Claude Code?** Install the [Pad plugin](https://www.getpad.dev/docs/claude-code) instead. It bundles this skill with shortcuts, a side panel and live notifications, and it updates itself.

## Installing the Skill

```
pad agent install              # Auto-detect your tools and install
pad agent install claude       # Claude Code
pad agent install cursor       # Cursor (also covers Codex, Windsurf & OpenCode)
pad agent install codex        # OpenAI Codex
pad agent install windsurf     # Windsurf
pad agent install opencode     # OpenCode
pad agent install copilot      # GitHub Copilot
pad agent install amazon-q     # Amazon Q Developer
pad agent install junie        # JetBrains Junie
```

`pad agent install` with no arguments scans your project for tool directories (`.claude/`, `.cursor/`, `.github/`, etc.) and installs the skill for each detected tool.

### Supported Tools

| Tool | Skill Location | Notes |
| --- | --- | --- |
| Claude Code | `.claude/skills/pad/SKILL.md` | Full skill with allowed-tools |
| Cursor | `.agents/skills/pad/SKILL.md` | Shared with Codex, Windsurf & OpenCode |
| OpenAI Codex | `.agents/skills/pad/SKILL.md` | Shared with Cursor, Windsurf & OpenCode |
| Windsurf | `.agents/skills/pad/SKILL.md` | Shared with Cursor, Codex & OpenCode |
| OpenCode | `.agents/skills/pad/SKILL.md` | Shared with Cursor, Codex & Windsurf |
| GitHub Copilot | `.github/instructions/pad.instructions.md` | Uses `applyTo` frontmatter |
| Amazon Q | `.amazonq/rules/pad.md` | Plain markdown |
| JetBrains Junie | `.junie/guidelines/pad.md` | Plain markdown |

**Tip:** Cursor, Codex, Windsurf and OpenCode all share the `.agents/skills/` directory. One install covers all four.

**Don’t commit these files.** They are generated from your installed pad version, and `pad init` rewrites them when they don’t match it, so each developer installs their own. Commit `.pad.toml` and add the skill paths to `.gitignore`; a teammate who clones the repo runs `pad init` once to install their own. [Connect a Workspace](https://www.getpad.dev/docs/connect-workspace#what-padtoml-does) has the details.

### Managing Installations

```
pad agent status         # See supported tools and installation status
pad agent update         # Update all installed tool integrations
pad agent install --all  # Install for all detected tools
```

## The /pad Skill

Once installed, just talk to your project. On a fresh workspace, the most useful first move is:

```
/pad onboard
```

`onboard` is the canonical playbook auto-activated in every new workspace. The agent walks an interview, inspects your codebase if it has shell access, and adapts your collections, conventions, roles, and playbooks to match your actual project — capturing what you tell it as plans, tasks, and ideas. After that, you can ask anything:

```
/pad what should I work on next?
/pad create a task for fixing the auth bug
/pad mark the OAuth fix as done
/pad let's create a plan for v0.2
/pad how are we doing on the MVP?
/pad I have an idea for real-time sync
```

### How It Works

1. The agent loads your workspace context (`pad project dashboard`, `pad collection list`)
2. It interprets your natural language request
3. It maps your intent to CLI commands
4. It executes the commands and presents results conversationally
5. It always confirms before creating or modifying items

## Conventions

Conventions are project-specific rules that AI agents follow automatically. They’re stored as items in the **Conventions** collection.

```
pad item create convention "Run tests before completing tasks" \
  --field trigger=on-task-complete \
  --field scope=all \
  --field priority=must \
  --content "Always run the test suite before marking a task as done. Fix any failures before completing."
```

### Convention Fields

| Field | Options | Description |
| --- | --- | --- |
| trigger | `always`, `on-task-start`, `on-task-complete`, `on-implement`, `on-commit`, `on-pr-create`, `on-plan` | When the convention applies |
| scope | `all`, `backend`, `frontend`, `mobile`, `docs`, `devops` | What part of the project it covers |
| priority | `must`, `should`, `nice-to-have` | How strictly it should be followed |

### How Agents Use Conventions

Before performing any action, the agent loads relevant conventions:

- Starting implementation → loads `on-implement` conventions
- Completing a task → loads `on-task-complete` conventions
- Creating a PR → loads `on-pr-create` conventions
- `always` conventions are loaded on every `/pad` invocation

The agent treats `must` conventions as hard rules and `should` conventions as strong guidelines.

## Playbooks

Playbooks are first-class invokable procedures — multi-step workflows the user (or the agent) can call directly: `/pad ship PLAN-42`, `/pad release 0.5.0`. They’re like conventions but with ordered steps and a declared argument contract.

A playbook can be invoked three ways:

1. **Slug routing in chat:** `/pad <slug> [args]` — the agent matches the first token against the workspace’s playbook slug list and binds the rest with flexible NL parsing.
2. **CLI:** `pad playbook run <slug> [tokens...]` — strict positional + bareword-flag + `key=value` parsing.
3. **MCP:** the `pad_playbook` tool with `action: run`. Returns the body + bound args; the agent executes the steps.
```
# Trigger-only playbook (no slug — auto-loaded on intent/trigger match)
pad item create playbook "Implementation Workflow" \
  --field trigger=on-implement \
  --field scope=all \
  --stdin <<'EOF'
1. Read the task description and acceptance criteria
2. Check for related items using wiki links
3. Create a feature branch
4. Implement the change
5. Run tests: `make test`
6. Run the build: `make build`
7. Update the task status to done
EOF
```

For playbooks that take **arguments** (slug-invocable from `/pad <slug>`), declare the argument spec in the web UI’s playbook editor at `/{username}/{workspace}/playbooks` (click ”+ New Playbook”). The structured arguments form is two-way bound with the body’s `## Arguments` section — the structured field is what the strict CLI parser reads, the markdown is the human-readable mirror. Fresh `startup` workspaces also ship a generic `ship` playbook that’s the canonical worked example.

See [Playbooks →](https://www.getpad.dev/docs/playbooks) for the full author guide, including the argument types, the test-invocation helper, and the bootstrap metadata flow.

## Teaching Your Agent

When your AI agent does something you want to correct or standardize, you can save it as a convention:

```
/pad save a convention: always use conventional commit messages
```

The agent will create a convention with an appropriate trigger and scope, so all future interactions follow the rule.

## Machine-Readable Output

All CLI commands support `--format json` for agent consumption:

```
pad project dashboard --format json
pad item list tasks --format json
pad item show fix-oauth --format json
```

This makes it easy for agents to parse structured data rather than scraping table output.
