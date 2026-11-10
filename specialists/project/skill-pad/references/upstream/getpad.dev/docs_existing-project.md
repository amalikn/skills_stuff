**Title:** Add Pad to an Existing Project

**Source:** [https://www.getpad.dev/docs/existing-project](https://www.getpad.dev/docs/existing-project)

---

# Page Structure Map
```text
Add Pad to an Existing Project
├── 1\. Create a workspace
├── 2\. Link the repo
├── 3\. Ask your agent to set it up
├── Bringing in open work you already have
└── Importing a Pad workspace
```

---

Adding Pad to a project you already have works the same way as starting a new one. You create a workspace, link the repo, and ask your agent to set it up. The setup interview reads the codebase you already have, and can bring in the open work you already track.

## 1\. Create a workspace

On the web, choose **New Workspace**. Pick **Blank** if you want your agent to build the collections around your project, or a template (such as **Startup**) if you’d rather start from Tasks, Ideas, Plans and Docs and adapt them.

From a terminal, `pad init` in the project directory creates and links a workspace in one step. If you do that, skip step 2.

## 2\. Link the repo

From the root of the project:

```
pad init --url https://app.getpad.dev --workspace my-workspace
```

Replace the URL with your Pad server’s and `my-workspace` with your workspace’s slug. In the web UI, your avatar menu’s **Connect a project…** shows the exact command. This writes `.pad.toml` and installs the `/pad` skill for the AI coding tools it finds. [Connect a Workspace](https://www.getpad.dev/docs/connect-workspace) covers it in full.

## 3\. Ask your agent to set it up

Open an agent session in the project and say:

```
set up my workspace
```

In Claude Code the shortcut is `/pad onboard`. The agent runs Pad’s onboarding playbook, an interview that adapts the workspace to your project:

- **It reads the codebase.** An agent that can read files looks at markers like `README.md`, `go.mod`, `package.json`, `Makefile` and `.github/workflows/`, so conventions use your real build and test commands instead of placeholders.
- **It asks where your open work lives.** It checks for files like `TODO.md` or `ROADMAP.md`, unchecked `- [ ]` lists in the README, and a GitHub remote, and asks you about anything else.
- **It adapts what’s there.** Collections, conventions, roles and playbooks are rewritten to fit the project, and nothing changes until you confirm it.

## Bringing in open work you already have

Pad has no importer for other trackers. Nothing reads a TODO file, GitHub Issues or another tool on its own. During setup, your agent does it for you, with your say-so:

1. It gathers the candidates. That means one per open TODO line or unchecked entry, and one per open GitHub issue. Issues come through the `gh` CLI if the agent has a shell. Otherwise you can paste a list.
2. It shows you the list, with where each entry came from and where it will land. You drop, merge or rename entries before anything is written.
3. It creates one item per entry you confirmed, with the source (file and line, or issue URL) in the item. It works in batches of 25 and checks in between them.
4. It leaves your source alone. It won’t delete TODO lines or close issues unless you ask.

Lines that aren’t clearly work, such as headings, notes or finished items, are asked about rather than imported.

To do this later, run the setup again and say you want to bring in your open work.

## Importing a Pad workspace

The import under **New Workspace › Import** reads a Pad workspace export (`.tar.gz`), for moving a workspace between Pad servers. `pad item import` reads a single playbook or convention exported from Pad. Neither one reads other tools’ data.
