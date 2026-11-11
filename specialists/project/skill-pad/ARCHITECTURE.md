---
Title: Architecture — skill-pad
Category: architecture
Status: current
Authority: canonical
Scope: How skill-pad's parts connect: the skill, its references and mirror, the Pad CLI and server, the projects, the backup and export paths
Last reviewed: 2026-11-11
Summary: >-
  skill-pad is a CLI-driven skill over a local Pad server whose data lives in tools_stuff/pad on the Data volume; repo trackers stay the truth, Pad items point at them, and
  exports and nightly backups keep copies outside Pad.
Depends on: SKILL.md, scripts/, conventions/apn-baseline.toml
---

# Architecture — skill-pad

## Overview

Agents (Claude Code, Codex) load one skill, `SKILL.md`, through two symlinks. The skill drives the `pad` CLI, which auto-starts a local Pad server (`127.0.0.1:7777`, SQLite). Each project links to a
Pad workspace with `.pad.toml`. The operator's rules for those workspaces (conventions baseline) and the scripts that keep copies of Pad's data live in this pack. Pad's own documentation is mirrored
verbatim under `references/upstream/` and rewritten into topic references the skill routes to.

## Components

| Component                          | Role                                                                                                       |
| ---------------------------------- | ---------------------------------------------------------------------------------------------------------- |
| `SKILL.md`                         | activation surface: preflight, routing to references, modes, load-bearing rules                            |
| `references/*.md`                  | the operator's text on Pad: context, items, playbooks, modes, CLI map, integrations, upgrade               |
| `references/upstream/`             | verbatim Pad sources per version (repo at tag, site pages, CLI help, release notes); index `readme.md`     |
| `conventions/apn-baseline.toml`    | the five conventions every apn workspace carries                                                           |
| `scripts/pad_conventions.py`       | applies the baseline to one workspace (plan, then `--apply`)                                               |
| `scripts/pad_export.py`            | renders one workspace's items to Markdown in its project (run by each project's commit gate)               |
| `scripts/pad_tracker.py`           | a Bugs or Features tracker file generated from its Pad collection: `import`, `export` (commit gate), `links` |
| `scripts/pad_rewrite.py`           | applies a reviewed JSON spec of Pad item rewrites (bodies by seq, comments, notes, decisions); shared `pad` call |
| `scripts/pad_link_opener.py` + `.plist` | 127.0.0.1:47800 redirect from an http link in Pad to `vscode://file/<path>:<line>` (launchd `au.malik.pad-link-opener`, kept alive) |
| `scripts/pad_backup.sh` + `.plist` | nightly `pad db backup` to OneDrive `pad_backups` (launchd `au.malik.pad-backup`, 02:30, newest 30)        |
| `scripts/pad_monitor.sh`           | the live push/watch feed for one session, run under Claude Code's Monitor tool by `connect`                |
| `scripts/pad_upstream_refresh.sh`  | mirrors a Pad release into `references/upstream/v<version>/`                                               |
| Pad CLI + server                   | Homebrew `perpetualsoftware/tap/pad`; data in `~/.pad`, a symlink to `/Volumes/Data/_ai/_tool/tools_stuff/pad` |

## Data flow and source of truth

```text
repo trackers (truth) <-- linked from -- Pad items (personal queue) --pad_export.py--> <project>/<trackers>/pad-focus.md (Git copy)
                                              |
                                              +--pad db backup (pad_backup.sh, 02:30)--> OneDrive pad_backups/pad-YYYYMMDD_HHMM.db
Pad release --pad_upstream_refresh.sh--> references/upstream/v<ver>/ --read, rewritten by hand--> references/*.md --> SKILL.md routes
```

A fact is recorded when it is in the project's trackers (convention `trackers-truth`); Pad holds the work queue, links and discussion.
Exception (operator, 2026-11-10): a project's Bugs and Features collections are the truth, and `docs/trackers/bug-tracker.md` and `features-to-add.md` are generated from
them by `pad_tracker.py export` in the commit gate. Repo links in those bodies are stored as link-opener links (Pad strips `vscode://` and a relative link means nothing on a
Pad page) and turned back into relative links in the generated file.

## Boundaries

- Owns: the skill text, the apn conventions baseline, the Pad helper scripts and their schedules, the upstream mirror.
- Does not own: Pad itself (upstream PerpetualSoftware/pad), each project's trackers and `.pad.toml`, the workspaces' content.
- Interfaces: the `pad` CLI (cmdhelp v0.1 for lookups), the Monitor tool for the live feed, `~/.claude/settings.json` hooks for presence.

## Key decisions

- Own skill instead of Pad's Claude Code plugin, because the operator wants one controllable source for Claude Code and Codex with the apn rules beside it (operator, 2026-11-10); the plugin's parts
  are rebuilt as modes, a monitor script and two hooks ([references/integrations.md](references/integrations.md)).
- Pad's text is rewritten, not vendored, because a verbatim copy would be overwritten by every release and mixes upstream and operator rules; the mirror keeps the source for diffing
  ([references/upgrade.md](references/upgrade.md)).
- A localhost link opener instead of a patched Pad, because Pad v0.19.2 keeps only http(s), mailto, ftp and tel links (web/src/lib/utils/markdown.ts:224) and a rebuilt fork would need
  the patch reapplied at every upgrade; the opener needs nothing when Pad is upgraded (operator, 2026-11-11; skill-coder P-66).
- Monitor instead of a plugin monitor, because a skill cannot declare a session-long background process; the Monitor runs at most 30 minutes and is re-armed, and the script's per-session lock prevents
  a double stream.
