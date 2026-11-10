---
Title: Pad upstream documentation (saved copies)
Category: vendor-sources
Status: current
Authority: Copies of PerpetualSoftware/pad documentation; upstream is the authority, these are dated snapshots
Scope: Pad v0.19.2 repo docs and the getpad.dev site pages, saved 2026-11-10
Last reviewed: 2026-11-10
Summary: >-
  Pad's own documentation saved into skill-pad so agents read it locally: repo files at tag v0.19.2 (fetched with gh api) and getpad.dev pages (fetched
  with all-scraper md). Refresh both after a Pad upgrade.
---

# Pad upstream documentation (saved copies)

Saved 2026-11-10. The installed CLI is v0.19.2, so the repo copies are pinned to tag `v0.19.2`; the site is unversioned and reflects its state on that date.

## Refresh

```bash
# repo files at a tag (one file shown; repeat for each in the table)
gh api "repos/PerpetualSoftware/pad/contents/docs/api.md?ref=<tag>" -H 'Accept: application/vnd.github.raw' > v<tag>/docs_api.md
# a site page
just -f /Volumes/Data/_ai/_tool/tools_stuff/all-scraper/justfile md https://getpad.dev/docs/collections --links --out getpad.dev/docs_collections.md
```

## CLI reference (v0.19.2, from the binary)

Pad implements its own cmdhelp v0.1 standard ([getpad.dev/cmdhelp](getpad.dev/cmdhelp.md)), so the installed binary prints its whole command tree. These
are the authoritative CLI reference for v0.19.2; read them before guessing a flag.

| File | Holds |
| --- | --- |
| [cli/pad-cli-reference.md](v0.19.2/cli/pad-cli-reference.md) | Every command, flag, argument and example, for reading (`pad help --all --format md`) |
| [cli/pad-cli-reference.json](v0.19.2/cli/pad-cli-reference.json) | The same as JSON, 184 commands keyed by path, for scripts (`pad help --all --format json`) |
| [cli/capabilities.txt](v0.19.2/cli/capabilities.txt) | `pad help --capabilities`: `cmdhelp/0.1: text, md, json, llm` |
| [releases-latest8.md](v0.19.2/releases-latest8.md) | GitHub release notes v0.18.0-rc.11 to v0.19.2 (`gh api repos/PerpetualSoftware/pad/releases`) |

Regenerated outside any workspace (2026-11-10): cmdhelp is context-aware, and a dump made inside a workspace names it and its members. Regenerate after an upgrade: `pad help --all --format md > v<ver>/cli/pad-cli-reference.md` (and `--format json`), about 1 s.

## v0.19.2 (repo, tag v0.19.2)

| File | Holds |
| --- | --- |
| [CLAUDE.md](v0.19.2/CLAUDE.md) | CLAUDE |
| [CONTRIBUTING.md](v0.19.2/CONTRIBUTING.md) | CONTRIBUTING |
| [README.md](v0.19.2/README.md) | README |
| [SECURITY.md](v0.19.2/SECURITY.md) | SECURITY |
| [docs_api.md](v0.19.2/docs_api.md) | docs/api |
| [docs_apps.md](v0.19.2/docs_apps.md) | docs/apps |
| [docs_architecture.md](v0.19.2/docs_architecture.md) | docs/architecture |
| [docs_backup.md](v0.19.2/docs_backup.md) | docs/backup |
| [docs_deployment.md](v0.19.2/docs_deployment.md) | docs/deployment |
| [docs_mcp.md](v0.19.2/docs_mcp.md) | docs/mcp |
| [docs_plugin-releases.md](v0.19.2/docs_plugin-releases.md) | docs/plugin-releases |
| [integrations_chatgpt_README.md](v0.19.2/integrations_chatgpt_README.md) | integrations/chatgpt/README |
| [integrations_chatgpt_skills_pad_SKILL.md](v0.19.2/integrations_chatgpt_skills_pad_SKILL.md) | integrations/chatgpt/skills/pad/SKILL |
| [internal_mcp_chatgpt_instructions.md](v0.19.2/internal_mcp_chatgpt_instructions.md) | internal/mcp/chatgpt/instructions |
| [internal_mcp_instructions.md](v0.19.2/internal_mcp_instructions.md) | internal/mcp/instructions |
| [plugin_skills_capture_SKILL.md](v0.19.2/plugin_skills_capture_SKILL.md) | plugin/skills/capture/SKILL |
| [plugin_skills_connect_SKILL.md](v0.19.2/plugin_skills_connect_SKILL.md) | plugin/skills/connect/SKILL |
| [plugin_skills_disconnect_SKILL.md](v0.19.2/plugin_skills_disconnect_SKILL.md) | plugin/skills/disconnect/SKILL |
| [plugin_skills_onboard_SKILL.md](v0.19.2/plugin_skills_onboard_SKILL.md) | plugin/skills/onboard/SKILL |
| [plugin_skills_pad_SKILL.md](v0.19.2/plugin_skills_pad_SKILL.md) | plugin/skills/pad/SKILL |
| [plugin_skills_status_SKILL.md](v0.19.2/plugin_skills_status_SKILL.md) | plugin/skills/status/SKILL |
| [schema_README.md](v0.19.2/schema_README.md) | schema/README |
| [skills_INSTALL.md](v0.19.2/skills_INSTALL.md) | skills/INSTALL |
| [skills_pad_SKILL.md](v0.19.2/skills_pad_SKILL.md) | skills/pad/SKILL |

## getpad.dev (site, 2026-11-10)

| File | Page |
| --- | --- |
| [blog_claude-isnt-getting-dumber.md](getpad.dev/blog_claude-isnt-getting-dumber.md) | https://getpad.dev/blog/claude-isnt-getting-dumber |
| [blog_conventions-and-playbooks.md](getpad.dev/blog_conventions-and-playbooks.md) | https://getpad.dev/blog/conventions-and-playbooks |
| [blog_multi-session-claude-code.md](getpad.dev/blog_multi-session-claude-code.md) | https://getpad.dev/blog/multi-session-claude-code |
| [blog_pad-v0-11-item-pane.md](getpad.dev/blog_pad-v0-11-item-pane.md) | https://getpad.dev/blog/pad-v0-11-item-pane |
| [blog_pad-v0-4-collab-local-first.md](getpad.dev/blog_pad-v0-4-collab-local-first.md) | https://getpad.dev/blog/pad-v0-4-collab-local-first |
| [blog_pad-v0-7-share-insights-tags.md](getpad.dev/blog_pad-v0-7-share-insights-tags.md) | https://getpad.dev/blog/pad-v0-7-share-insights-tags |
| [blog_software-factory-with-pad.md](getpad.dev/blog_software-factory-with-pad.md) | https://getpad.dev/blog/software-factory-with-pad |
| [changelog.md](getpad.dev/changelog.md) | https://getpad.dev/changelog |
| [cmdhelp.md](getpad.dev/cmdhelp.md) | https://getpad.dev/cmdhelp |
| [compare.md](getpad.dev/compare.md) | https://getpad.dev/compare |
| [docs.md](getpad.dev/docs.md) | https://getpad.dev/docs |
| [docs_agent-integration.md](getpad.dev/docs_agent-integration.md) | https://getpad.dev/docs/agent-integration |
| [docs_api.md](getpad.dev/docs_api.md) | https://getpad.dev/docs/api |
| [docs_claude-code.md](getpad.dev/docs_claude-code.md) | https://getpad.dev/docs/claude-code |
| [docs_cli.md](getpad.dev/docs_cli.md) | https://getpad.dev/docs/cli |
| [docs_collections.md](getpad.dev/docs_collections.md) | https://getpad.dev/docs/collections |
| [docs_configuration.md](getpad.dev/docs_configuration.md) | https://getpad.dev/docs/configuration |
| [docs_connect-workspace.md](getpad.dev/docs_connect-workspace.md) | https://getpad.dev/docs/connect-workspace |
| [docs_existing-project.md](getpad.dev/docs_existing-project.md) | https://getpad.dev/docs/existing-project |
| [docs_mcp_tools.md](getpad.dev/docs_mcp_tools.md) | https://getpad.dev/docs/mcp/tools |
| [docs_mcp_troubleshooting.md](getpad.dev/docs_mcp_troubleshooting.md) | https://getpad.dev/docs/mcp/troubleshooting |
| [docs_playbooks.md](getpad.dev/docs_playbooks.md) | https://getpad.dev/docs/playbooks |
| [docs_templates.md](getpad.dev/docs_templates.md) | https://getpad.dev/docs/templates |
| [docs_web-ui.md](getpad.dev/docs_web-ui.md) | https://getpad.dev/docs/web-ui |
| [faq.md](getpad.dev/faq.md) | https://getpad.dev/faq |
| [learn.md](getpad.dev/learn.md) | https://getpad.dev/learn |
| [learn_existing-project.md](getpad.dev/learn_existing-project.md) | https://getpad.dev/learn/existing-project |
| [learn_first-task.md](getpad.dev/learn_first-task.md) | https://getpad.dev/learn/first-task |
| [learn_new-project.md](getpad.dev/learn_new-project.md) | https://getpad.dev/learn/new-project |
| [learn_onboard.md](getpad.dev/learn_onboard.md) | https://getpad.dev/learn/onboard |
| [learn_plan.md](getpad.dev/learn_plan.md) | https://getpad.dev/learn/plan |
| [spec-driven.md](getpad.dev/spec-driven.md) | https://getpad.dev/spec-driven |

## Added by the skill-pad session (2026-11-10)

Plugin parts, the install source and the agent guide (repo at tag v0.19.2, fetched with curl from raw.githubusercontent.com; the guide from the binary):

| File | Holds |
| --- | --- |
| [agent-guide-all.md](v0.19.2/agent-guide-all.md) | `pad agent guide all`: Pad's agent guidance by topic, from the binary |
| [internal_cli_agents.go](v0.19.2/internal_cli_agents.go) | internal/cli/agents.go: where `pad agent install` writes and how it stamps files |
| [claude-plugin_marketplace.json](v0.19.2/claude-plugin_marketplace.json) | .claude-plugin/marketplace.json (plugin pinned to v0.18.1) |
| [plugin_.claude-plugin_plugin.json](v0.19.2/plugin_.claude-plugin_plugin.json) | plugin/.claude-plugin/plugin.json |
| [plugin_hooks_activity-hooks.json](v0.19.2/plugin_hooks_activity-hooks.json) | plugin/hooks/activity-hooks.json (busy/idle presence) |
| [plugin_hooks_hooks.json](v0.19.2/plugin_hooks_hooks.json) | plugin/hooks/hooks.json |
| [plugin_monitors_monitors.json](v0.19.2/plugin_monitors_monitors.json) | plugin/monitors/monitors.json (the connect monitor) |
| [plugin_scripts_pad-monitor.sh](v0.19.2/plugin_scripts_pad-monitor.sh) | plugin/scripts/pad-monitor.sh (source of scripts/pad_monitor.sh) |

Site pages missing from the first pass, from the www.getpad.dev sitemap (all-scraper `md`); privacy, terms, subprocessors, support, delete-account and
the blog category pages were left out as not useful to an agent:

| File | Page |
| --- | --- |
| [blog.md](getpad.dev/blog.md) | https://www.getpad.dev/blog |
| [blog_built-for-makers.md](getpad.dev/blog_built-for-makers.md) | https://www.getpad.dev/blog/built-for-makers |
| [blog_claude-desktop-pad-mcp.md](getpad.dev/blog_claude-desktop-pad-mcp.md) | https://www.getpad.dev/blog/claude-desktop-pad-mcp |
| [blog_homebrew-signed-releases.md](getpad.dev/blog_homebrew-signed-releases.md) | https://www.getpad.dev/blog/homebrew-signed-releases |
| [blog_introducing-pad.md](getpad.dev/blog_introducing-pad.md) | https://www.getpad.dev/blog/introducing-pad |
| [blog_pad-cloud-launch.md](getpad.dev/blog_pad-cloud-launch.md) | https://www.getpad.dev/blog/pad-cloud-launch |
| [blog_remote-mcp-launch.md](getpad.dev/blog_remote-mcp-launch.md) | https://www.getpad.dev/blog/remote-mcp-launch |
| [blog_run-pad-on-unraid.md](getpad.dev/blog_run-pad-on-unraid.md) | https://www.getpad.dev/blog/run-pad-on-unraid |
| [blog_self-hosted-dot.md](getpad.dev/blog_self-hosted-dot.md) | https://www.getpad.dev/blog/self-hosted-dot |
| [contribute.md](getpad.dev/contribute.md) | https://www.getpad.dev/contribute |
| [docs_mcp_chatgpt.md](getpad.dev/docs_mcp_chatgpt.md) | https://www.getpad.dev/docs/mcp/chatgpt |
| [docs_mcp_claude-desktop.md](getpad.dev/docs_mcp_claude-desktop.md) | https://www.getpad.dev/docs/mcp/claude-desktop |
| [docs_mcp_cursor.md](getpad.dev/docs_mcp_cursor.md) | https://www.getpad.dev/docs/mcp/cursor |
| [docs_mcp_windsurf.md](getpad.dev/docs_mcp_windsurf.md) | https://www.getpad.dev/docs/mcp/windsurf |
| [docs_self-hosting.md](getpad.dev/docs_self-hosting.md) | https://www.getpad.dev/docs/self-hosting |
| [docs_self-hosting_unraid.md](getpad.dev/docs_self-hosting_unraid.md) | https://www.getpad.dev/docs/self-hosting/unraid |
| [mcp.md](getpad.dev/mcp.md) | https://www.getpad.dev/mcp |
| [mcp_local.md](getpad.dev/mcp_local.md) | https://www.getpad.dev/mcp/local |
| [mcp_remote.md](getpad.dev/mcp_remote.md) | https://www.getpad.dev/mcp/remote |
| [security.md](getpad.dev/security.md) | https://www.getpad.dev/security |

The whole mirror is refreshed for a new release with `scripts/pad_upstream_refresh.sh <version> --apply` (repo files, CLI help, agent guide, release
notes); site pages stay a manual all-scraper pass. The CLI dumps in `v0.19.2/cli/` were regenerated outside any workspace on 2026-11-10, so they no
longer name smc-resiliency.

## github.com (2026-11-10)

| File | Holds |
| --- | --- |
| [github.com/pkgs_container_pad.md](github.com/pkgs_container_pad.md) | GHCR package page `ghcr.io/perpetualsoftware/pad`: tags `latest` = 0.19.2, 0.19.1, digests; its "CLI reference" anchor is the repo README section, mirrored as `v0.19.2/README.md` |
