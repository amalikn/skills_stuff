---
Title: skill-pad reference: refreshing after a Pad release
Category: reference
Status: current
Authority: canonical
Scope: Updating the Pad CLI, the upstream mirror and skill-pad's own text when Pad releases a new version
Last reviewed: 2026-11-10
Summary: >-
  The upgrade procedure: brew upgrade, refresh the mirror into references/upstream/<version>/ with scripts/pad_upstream_refresh.sh, diff Pad's skill
  and plugin texts between versions, and carry what changed into skill-pad's references by hand.
---

# Refreshing after a Pad release

skill-pad is the operator's text, so a Pad release never overwrites it. What a release changes reaches it in four steps.

1. **Upgrade the CLI:** `brew upgrade perpetualsoftware/tap/pad`, then `pad --version`. Release notes are Pad's changelog (GitHub Releases; the site's changelog page only links there).
2. **Refresh the mirror:** `just upstream <version>` (plan), then `just upstream <version> --apply`. `scripts/pad_upstream_refresh.sh` writes `references/upstream/v<version>/`: the repo files at that
   tag (skills, plugin, docs, MCP instructions, `internal/cli/agents.go`), Pad's agent guide (`pad agent guide all`; `skills_pad_SKILL.md` from the repo is the Claude skill text), the cmdhelp dump
   (`cli/pad-cli-reference.md` and `.json`, generated outside any workspace), and the release notes since the last mirrored version. Site pages under `references/upstream/getpad.dev/` are refreshed with all-scraper on need.
3. **Diff:** `git diff --no-index references/upstream/v<old>/ references/upstream/v<new>/` and read every changed skill, plugin and docs file. Pad's skill text has many short rules with ticket
   numbers; a new rule is usually one paragraph.
4. **Carry it over:** rewrite what matters into the reference that owns the topic (table below), in this pack's words; correct a contradicted claim in place; update `Last reviewed`; CHANGELOG entry;
   `just check`. Then delete the older mirror folder once nothing cites it.

| Upstream text changed                     | Owning reference                                      |
| ----------------------------------------- | ----------------------------------------------------- |
| context loading, bootstrap keys, roles    | [workspace-context.md](workspace-context.md)          |
| item commands, edits, leases, attachments | [items-and-edits.md](items-and-edits.md)              |
| playbooks, workflows                      | [playbooks-and-workflows.md](playbooks-and-workflows.md) |
| plugin skills, monitor script, hooks      | [modes.md](modes.md), `scripts/pad_monitor.sh`        |
| command groups, flags, hidden commands    | [cli-reference.md](cli-reference.md)                  |
| MCP, clients, plugin manifest             | [integrations.md](integrations.md)                    |
| chat and push safety                      | `SKILL.md` Rules (keep it inline: it is load-bearing) |

Never run `pad agent install <tool>` or `pad agent update` from a home folder or a project: they write Pad's skill text into `~/.claude/skills/` or the project and add a second `pad` skill beside this
one.
