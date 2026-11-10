---
Title: Pad setup message sent to smc-resiliency (worked example)
Category: example
Status: historical
Authority: record
Scope: The setup message relayed from unified-network-controller to smc-resiliency on 2026-11-10, kept verbatim
Last reviewed: 2026-11-10
Summary: >-
  A worked example of setting Pad up in a project. Kept verbatim as sent; its skill install paths (skills_stuff/pad, ~/.claude/skills/pad) predate
  skill-pad and are superseded by SETUP.md.
---

Operator request (relayed from the unified-network-controller session, 10 Nov 12:20): set up Pad for smc-resiliency and seed its tasks, the way UNC did today.

Pad (github.com/PerpetualSoftware/pad, v0.19.2, installed by brew) is the operator's personal project-management layer. The project's own trackers (ROADMAP, SCRATCHPAD open items, D12 and the rest) stay the source of truth; Pad items name the tracker entry they serve.

What already exists (machine-wide, done in UNC):
- ~/.pad is a symlink to /Volumes/malik1tb/malik-storage/pad. The one pad.db holds every workspace. The server runs on 127.0.0.1:7777 and the CLI is already logged in (check with `pad auth whoami`).
- The nightly backup (launchd au.malik.pad-backup, 02:30) goes to OneDrive pad_backups and covers all workspaces.
- The /pad skill is central: skills_stuff/pad, with ~/.claude/skills/pad and ~/.agents/skills/pad as symlinks. No per-project copies.

Steps for smc-resiliency:
1. In the smc-resiliency folder, since the CLI is authenticated: `pad workspace init smc-resiliency --template startup`. Run `pad init` instead only if `pad auth whoami` fails.
2. Delete the skill copies Pad writes into the project: `.claude/skills/pad/` and `.agents/skills/pad/`. Keep `.pad.toml`.
3. Give `.pad.toml` a two-line `#` comment header. The project's freshness check refuses a file without a summary; UNC's header is in ../unified-network-controller/.pad.toml.
4. Rewrite the startup template's conflicting conventions, as the operator chose for UNC:
   - CONVE-1 ("Conventional commit format", feat:/fix:) becomes the project's own commit style through `just commit-project`.
   - CONVE-2 ("Never push directly to main") becomes "commit only through just commit-project (one repo, one branch, operator 2026-10-21)".
   - Use `pad item update <ref> --title ... --content ... --expected-seq <seq> --comment ...`.
5. Add an always-on convention: "Repo trackers are the truth; Pad items link to them".
6. Seed plans and tasks from your ROADMAP phases and SCRATCHPAD open items. Each item names its tracker entry. Use `--op-key` on every create so a rerun does not duplicate.
7. Export to the repo: `just pad-export --apply`, a recipe calling /Volumes/Data/_ai/_scripts/scripts_stuff/python/pad_export/pad_export.py with `--out docs/trackers/pad-focus.md` (or your trackers folder). Run it non-fatally inside your commit gate (`-@...` in just), as UNC's `commit-gate` does, so every `just commit-project` carries the current list. Index the page.
8. Load /pad first (`pad bootstrap --format json`) and follow its conventions.

Reference: UNC CHANGELOG 20261110_1202 and later entries, and docs/trackers/pad-focus.md. I am also telling the hub (`to es:`) so it is recorded there.