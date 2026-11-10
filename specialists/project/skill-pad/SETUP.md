---
Title: Setup — skill-pad
Category: setup
Status: current
Authority: canonical
Scope: Installing Pad and skill-pad on the operator's Mac, and checking that each part works
Last reviewed: 2026-11-10
Summary: A working setup needs the pad CLI from Homebrew, an initialised local Pad, the two install links, the pack's venv, the backup job and the presence hooks.
Depends on: justfile, .mise.toml, scripts/pad_backup.plist
---

# Setup — skill-pad

## Contents

- [Prerequisites](#prerequisites)
- [Bootstrap](#bootstrap)
- [Install links](#install-links)
- [Backup job](#backup-job)
- [Presence hooks](#presence-hooks)
- [Environment](#environment)
- [First run](#first-run)
- [Troubleshooting](#troubleshooting)

## Prerequisites

| Tool       | Version | Pinned in / from                                    |
| ---------- | ------- | --------------------------------------------------- |
| pad        | 0.19.2  | `brew install perpetualsoftware/tap/pad`            |
| Python     | 3.14    | `.mise.toml` (venv in the working-cache peer)       |
| just, mise | current | Homebrew                                            |
| gh, curl   | current | Homebrew; `gh auth status` for the upstream refresh |
| shellcheck | current | Homebrew (script lint)                              |

Pad's data folder: `~/.pad` is a symlink to `/Volumes/malik1tb/malik-storage/pad`, so malik1tb must be mounted for Pad to start. First-time Pad setup is interactive: `pad init` in a terminal (browser
sign-in); after that `pad auth whoami` reports the user.

## Bootstrap

`just bootstrap`, then `just check`.

## Install links

Both point at this folder (operator, 2026-11-10):

```bash
ln -sfn /Volumes/Data/_ai/_skills/skills_stuff/specialists/project/skill-pad ~/.claude/skills/skill-pad
ln -sfn /Volumes/Data/_ai/_skills/skills_stuff/specialists/project/skill-pad ~/.agents/skills/skill-pad
```

Never add `~/.claude/skills/pad` or `~/.agents/skills/pad` (what `pad agent install` writes): two Pad skills would compete.

## Backup job

`scripts/pad_backup.plist` is symlinked as `~/Library/LaunchAgents/au.malik.pad-backup.plist`; load it with `launchctl load` on that path. Log:
`/Volumes/Data/_ai/_scripts/scripts-runtime/pad-backup.log`.

## Presence hooks

`UserPromptSubmit` and `Stop` entries in `~/.claude/settings.json` running `pad session activity busy|idle` (exact JSON: [references/modes.md](references/modes.md), Presence hooks).

## Environment

| Variable                              | Purpose                                   | Source of the value                            |
| ------------------------------------- | ----------------------------------------- | ---------------------------------------------- |
| `PAD_AGENT`                           | agent name under Codex or other harnesses | set per harness; Claude Code detected          |
| `PAD_BACKUP_DIR`, `_KEEP`, `_TIMEOUT` | backup target, copies kept, timeout       | defaults in `scripts/pad_backup.sh`            |
| `PAD_MONITOR_BACKOFF`, `PAD_BIN`      | monitor reconnect delay, pad binary       | defaults in `scripts/pad_monitor.sh`           |
| Pad credentials                       | CLI session                               | `~/.pad/credentials.json` (0600); never copied |

## First run

```bash
pad --version && pad auth whoami && pad server info      # CLI, user, server reachable
ls -la ~/.claude/skills/skill-pad ~/.agents/skills/skill-pad
launchctl list | grep au.malik.pad-backup
just check
```

In a linked project, `/skill-pad status` prints the connection header and the dashboard.

## Troubleshooting

- `pad` hangs or the server will not start: malik1tb is not mounted (`ls ~/.pad/`).
- `Pad is not configured`: run `pad init` in a terminal.
- `/skill-pad` not offered in Claude Code: the link points at a folder without `SKILL.md`; recheck the links above.
- Backup missing: `cat /Volumes/Data/_ai/_scripts/scripts-runtime/pad-backup.log`; run `bash scripts/pad_backup.sh` (plan) to see why.
