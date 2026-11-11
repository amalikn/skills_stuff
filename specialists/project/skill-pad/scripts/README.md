---
Title: skill-pad scripts
Category: script-catalog
Status: current
Authority: canonical
Scope: Every script in skill-pad/scripts: what it does, inputs, outputs, safety, recipe
Last reviewed: 2026-11-10
Summary: Catalogue of the Pad helper scripts (conventions, export, backup, live monitor, upstream refresh) and the governance checker, with their recipes and safety labels.
---

# skill-pad scripts

Run them through the justfile (`just --list`); recipes marked "project folder" run where they are called (`just -f <pack>/justfile <recipe>`), because Pad resolves the workspace from the current
folder's `.pad.toml`. Tests: `just test` (offline, fake pad).

| Script                    | What it does                                                                                           | Safety                             | Recipe                     |
| ------------------------- | ------------------------------------------------------------------------------------------------------ | ---------------------------------- | -------------------------- |
| `pad_conventions.py`      | Applies `conventions/apn-baseline.toml` to one workspace: rewrites the template's four,                | plan; writes Pad with `--apply`    | `conventions`              |
|                           |   adds `trackers-truth`                                                                                |                                    |   (project folder)         |
| `pad_toml_probe.py`       | Pad upgrade test: switches a scratch `.pad.toml` away and back and reports whether Pad still keeps the workspace, unknown tables and other files (comments are known to be deleted) | writes a temporary folder only     | `pad-toml-probe`           |
| `pad_export.py`           | One workspace's items as a Markdown page in its project; rewrites only when an item changed            | plan; writes the file              | `export` (project folder)  |
|                           |                                                                                                        |   with `--apply`                   |                            |
| `pad_backup.sh`           | `pad db backup` (online-safe) to OneDrive `pad_backups`, newest 30 kept; launchd nightly 02:30         | plan; writes and prunes            | `backup`                   |
|                           |   via `pad_backup.plist`                                                                               |   with `--apply`                   |                            |
| `pad_monitor.sh`          | The live push/watch feed for one session: consent gate, per-session lock, reconnect loop               | read-only (registers the           | `monitor` (project         |
|                           |   over `pad watch --stream --for-session`                                                              |   session locally)                 |   folder); Monitor tool    |
| `pad_upstream_refresh.sh` | Mirrors a Pad release into `references/upstream/v<version>/` (repo files at tag, CLI help, agent       | plan; writes the mirror            | `upstream VERSION`         |
|                           |   guide, release notes)                                                                                |   with `--apply`                   |                            |
| `pad_rewrite.py`          | Applies a reviewed JSON spec to Pad items: bodies (guarded by seq), titles, tags, comment type prefixes, note and decide entries (idempotent keys) | plan; writes Pad with `--apply` | `rewrite SPEC` (project folder) |
| `pad_tracker.py`          | Keeps a Markdown tracker as a file generated from a Pad collection: `import` (items created, round trip proved), `export` (marked blocks; a hand edit is refused) and `links` (relative repo links in Pad bodies become opener links; the export turns them back) | plan; writes Pad and the file with `--apply` | `tracker CMD FILE` (project folder) |
| `pad_link_opener.py`      | Localhost service (127.0.0.1:47800) that redirects `/open/<absolute path>?f=L<n>` to `vscode://file/<path>:<n>`, so repo links in Pad open in VS Code (Pad strips vscode:// links); `url <path>` prints a link | read-only; serves redirects only, for existing paths under `/Volumes/Data` | `link-opener [status\|install\|uninstall\|restart]`, `link-url PATH` |
| `check_governance.py`     | The pack's governance claims as assertions (`govcheck/` package: core, config, helpers, checks         | read-only                          | `governance`, `check`      |
|                           |   by family)                                                                                           |                                    |                            |

`pad_backup.plist` is the launchd job for `pad_backup.sh` (symlinked into `~/Library/LaunchAgents`), not a script; `pad_link_opener.plist` is the same for
`pad_link_opener.py serve` (kept alive; `just link-opener install`).

## Governance recipes (skill-ai-it)

- `just check`: the project's governance checks, then document freshness and file roles. Read-only; `safe`.
- `just govern`: governance up to the current skill-ai-it standard (adoption, record budgets with `just check`, role findings); content fixes are `/skill-ai-it refresh`. `modifies-files`.
- `just roles`: root governance files outside their roles (front matter, README quick start, ROADMAP shape, duplicated sections). Read-only; `safe`.
- `just stale`: stale docs by rule (review due, superseded outside archive/, a Depends on file changed). Read-only; `safe`.
- `just docs [folder]`: one header line per file, to triage before opening. Read-only; `safe`.
- `just history <term>`: search rotated CHANGELOG (or SCRATCHPAD) entries in docs/history. Read-only; `safe`.
- `just history-show <stamp>`: print one rotated entry. Read-only; `safe`.
- `just rotate [--apply]`: move old CHANGELOG/SCRATCHPAD entries and done ROADMAP items to docs/history, verified. Plan by default; `modifies-files`.
- `just budget [--apply]`: bring governed files within budget (normalise, rotate, move reference sections, audit, check). Plan by default; `modifies-files`.
- `just changelog-entry --title ... --body-file ...`: add a CHANGELOG entry in this project's style, with its Contents line. Plan by default; `modifies-files`.
- `just move-sections ...`: move named sections verbatim to an on-need reference doc. Plan by default; `modifies-files`.
- `just outline <file.md>`: each heading with its line range, to read one section instead of the file. Read-only; `safe`.
- `just section <file.md> "<title>"`: print one section (exact title, `Parent > Child`, `#anchor`, `~text`). Read-only; `safe`.
