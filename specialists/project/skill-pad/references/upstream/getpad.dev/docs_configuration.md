**Title:** Configuration

**Source:** [https://www.getpad.dev/docs/configuration](https://www.getpad.dev/docs/configuration)

---

# Page Structure Map
```text
Configuration
├── Project File:.pad.toml
├── Global Config: ~/.pad/config.toml
│   └── Settings
├── Environment Variables
├── CLI Flags
│   └── pad server start
├── Workspace Detection
└── Precedence
```

---

Pad is designed to work with zero configuration, but offers several ways to customize behavior.

## Project File:.pad.toml

Each project has a `.pad.toml` file in its root directory, created by `pad init`. This file links the directory to a Pad workspace, and for a workspace on Pad Cloud or another remote server, to that server:

```
workspace = "my-project"
url = "https://app.getpad.dev"   # written for a remote or Cloud server; absent for the local server
```

| Key | Written by | What it does |
| --- | --- | --- |
| `workspace` | `pad init` | The workspace slug this directory belongs to. |
| `url` | `pad init`, for a remote or Cloud server | The server this directory talks to. It wins over `PAD_URL` and `~/.pad/config.toml`; only `--url` on a command overrides it. The local server’s own commands (`pad server start` / `stop`, `pad auth setup` / `configure`) ignore it. |
| `agent_name` | you (optional) | The agent name this repository’s writes are attributed to. A session’s own `pad session register --agent` name comes first; this beats `$PAD_AGENT` and the detected runtime. |

See [Connect a workspace](https://www.getpad.dev/docs/connect-workspace) for how the URL pin behaves across several servers.

## Global Config: ~/.pad/config.toml

Server and editor settings are stored in the global config file at `~/.pad/config.toml`:

```
host = "127.0.0.1"
port = 7777
url = ""
editor = ""
log_level = "info"
```

### Settings

| Key | Default | Description |
| --- | --- | --- |
| `host` | `127.0.0.1` | Server bind address |
| `port` | `7777` | HTTP server port |
| `url` | — | Full base URL override (e.g. `https://pad.example.com`). When set, the CLI connects to this URL instead of constructing one from host/port. |
| `editor` | `$EDITOR` | Editor for `pad item edit` command |
| `log_level` | `info` | Logging verbosity |

Pad authenticates with per-user accounts (email + password), not a single shared password. Set up the first admin with `pad auth setup` — see [Self-Hosting → Authentication](https://www.getpad.dev/docs/self-hosting#authentication).

## Environment Variables

| Variable | Default | Description |
| --- | --- | --- |
| `PAD_HOST` | `127.0.0.1` | Server bind address (overrides config) |
| `PAD_PORT` | `7777` | Server port (overrides config) |
| `PAD_URL` | — | Full base URL override (overrides config) |
| `PAD_DATA_DIR` | `~/.pad` | Base data directory — holds `config.toml`, `pad.db`, and `logs/` |
| `PAD_DB_PATH` | `~/.pad/pad.db` | Path to SQLite database file (overrides the `pad.db` under `PAD_DATA_DIR`) |
| `EDITOR` | — | Editor for `pad item edit` command |

## CLI Flags

### pad server start

Start the Pad server manually (usually auto-started):

```
pad server start --port 8080 --host 0.0.0.0
```

| Flag | Default | Description |
| --- | --- | --- |
| `--port` | `7777` | Server port |
| `--host` | `127.0.0.1` | Bind address |

## Workspace Detection

Pad finds your workspace by walking up the directory tree looking for `.pad.toml`. This means you can run `pad` commands from any subdirectory:

```
my-project/
├── .pad.toml          ← workspace link (workspace = "my-project")
├── src/
│   └── (your code)    ← `pad` works here too
└── docs/
    └── (your docs)    ← and here
```

The SQLite database is stored globally at `~/.pad/pad.db` (not in the project directory), so multiple workspaces share a single database.

## Precedence

Configuration values are resolved in this order (highest priority first):

1. CLI flags (`--port 8080`)
2. Environment variables (`PAD_PORT=8080`)
3. `~/.pad/config.toml` settings
4. Built-in defaults
