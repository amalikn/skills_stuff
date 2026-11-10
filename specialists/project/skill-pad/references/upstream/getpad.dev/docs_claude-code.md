**Title:** Claude Code Plugin

**Source:** [https://www.getpad.dev/docs/claude-code](https://www.getpad.dev/docs/claude-code)

---

# Page Structure Map
```text
Claude Code Plugin
├── Install
│   └── In the Claude Desktop app
├── Get connected
├── Using the panel
├── Requirements
└── Other AI tools
```

---

The Pad plugin is the fastest way to use Pad from Claude Code. One install gives you:

- **The `/pad` skill**: talk to your project in plain language (“what should I work on next?”, “I finished the OAuth fix”).
- **Typed shortcuts**: `/pad:status`, `/pad:capture`, `/pad:onboard`, `/pad:connect` and `/pad:disconnect`.
- **A side panel** (`/pad-pane`): browse what’s in progress, what’s next and every collection; open an item, change its status, comment, or quick-add, without leaving your session.
- **Live notifications**: when an item you’re watching changes, or someone pushes one to your session, Claude hears about it. This is off until you opt in with `/pad:connect`.

The plugin updates itself, so you never have to re-copy a skill file.

## Install

In a Claude Code session:

```
/plugin marketplace add PerpetualSoftware/pad
/plugin install pad@pad
```

Or from your shell:

```
claude plugin marketplace add PerpetualSoftware/pad
claude plugin install pad@pad
```

### In the Claude Desktop app

In a local or SSH session in the **Code** tab, open **\+ → Plugins**, add the marketplace `PerpetualSoftware/pad`, and install **pad**. Plugins you install at user scope in the terminal also show up in the Desktop app on the same machine.

## Get connected

Open the panel:

```
/pad-pane
```

If this folder is already linked to a Pad workspace, you’ll see what’s in progress straight away. If not, the panel’s **Get started** view offers three ways in:

1. **Pad Cloud**: nothing to install. The panel adds Pad Cloud’s MCP server to Claude Code, then you send `/reload-plugins` and sign in from `/mcp`.
2. **Pad on this machine**: Claude installs the `pad` CLI (Homebrew or a release binary) and runs `/pad:onboard` to set up this folder.
3. **Your own server**: Claude links this folder to your self-hosted Pad with `pad init --url …` and `pad auth login`. New to self-hosting? See [Self-Hosting](https://www.getpad.dev/docs/self-hosting).

Then run `/pad:onboard` to shape the workspace around your project.

## Using the panel

| Key | What it does |
| --- | --- |
| `n` `x` `b` `f` `a` `g` | Now, Next, Browse, Find, Activity, Settings |
| `↑` `↓` | Move through the list |
| `Tab` / `Shift+Tab` | Move between the views and the list |
| `Enter` | Open the selected item |
| `s` `c` `w` | In an item: change status, comment, or put “work on it” in your prompt |
| `y` `o` | Copy the item’s ref or its web link |
| `q` | Quick-add an item |
| `Esc` | Step back; at the top, close the panel |

In the terminal, press `Ctrl+X` then `Tab` to move the keyboard between the panel and your prompt. **Settings** (`g`) holds the view the panel opens on, how often it refreshes, whether it talks to Pad through the CLI or MCP, and a darker background if you want one.

## Requirements

- **The panel** needs Claude Code 2.1.287 or later (the Desktop app 2.1.286 or later). The skills and shortcuts work on any version.
- **The CLI path** needs the `pad` CLI; **the Cloud path** needs nothing but a Pad Cloud account.
- Plugins aren’t available in the Desktop app’s WSL sessions.

## Other AI tools

Using Cursor, Codex, Windsurf, Copilot or another tool? Install the `/pad` skill with `pad agent install`: see [Agent Integration](https://www.getpad.dev/docs/agent-integration). For desktop chat apps, see [MCP](https://www.getpad.dev/mcp).
