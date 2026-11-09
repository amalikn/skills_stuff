# Skills Stuff Detailed Skill Surfaces

## Contents

- [Superpowers Plugin Skills](#superpowers-plugin-skills)
- [Personal Skills](#personal-skills)
- [Regular Skills](#regular-skills)
- [Skill Authoring Projects](#skill-authoring-projects)

## Superpowers Plugin Skills

The `superpowers/skills/` directory inside this repo is the canonical source-of-truth for all Claude Code superpowers skills. This includes bundled superpowers skills and custom operator-added skills.

Rules:

- Author under `superpowers/skills/<skill-name>/SKILL.md`; do not edit the installed plugin cache as the primary authoring surface.
- After a change, sync it to the current `~/.claude/plugins/cache/claude-plugins-official/superpowers/<version>/skills/<skill-name>/SKILL.md` install path.
- Every `SKILL.md` needs YAML frontmatter with `name` and `description` at minimum.
- Use `specialists/` for complex multi-file canonical definitions. Use `superpowers/skills/` for simple Claude Code skill files.
- After a plugin update, re-sync custom skills from `superpowers/skills/` to the new installed-cache version.

### Current custom skills

| Skill name | Path | Purpose |
|---|---|---|
| `crewai` | `superpowers/skills/crewai/SKILL.md` | Guide for invoking the mcp-crewai MCP server from any AI agent |
| `skill-coder` | `specialists/project/skill-coder/SKILL.md` | Programming practice for any project and language; the default skill for any code (operator, 2026-10-20) |
| `skill-goal-guard` | `specialists/project/skill-goal-guard/SKILL.md` | GoalGuard (alias skill-gg): owner-approved MVP scope gate and portfolio focus over Vikunja; not installed yet (operator, 2026-10-27) |
| `skill-knowledge-curator` | `specialists/project/skill-knowledge-curator/SKILL.md` | Knowledge Curator (alias skill-kc): evidence-linked claims, conflict review, derived and promoted knowledge pages, archive plans; installed (symlinks) 2026-10-27 |

## Personal Skills

The `personal/` directory holds personal-use skill packs for productivity, wellbeing, and career workflows.

Rules:

- Single-file skills go in `personal/skills/<skill-name>/`.
- Multi-file specialist packs go in `personal/<skill-name>/`.
- The canonical source is here; install to the relevant runtime path after authoring.

| Skill name | Path | Type | Purpose |
|---|---|---|---|
| `skill-careertracker` | `personal/skills/skill-careertracker/SKILL.md` | Single-file | Career/job tracking and assessment |
| `therapy-counselling` | `personal/therapy-counselling/` | Multi-file pack | CBT/MI/SFBT conversational support, crisis protocol, session structure |

## Regular Skills

Skills under `skills/` are single-file `SKILL.md` behavioral contracts.

| Skill name | Path | Purpose |
|---|---|---|
| `skill-anydoc` | `skills/skill-anydoc/SKILL.md` | Convert common document formats to GitHub-Flavored Markdown. |
| `skill-commtracker` | `skills/skill-commtracker/SKILL.md` | Extract comm data from email/.eml/Teams and maintain a markdown thread tracker. |
| `skill-project-coherence` | `skills/skill-project-coherence/SKILL.md` | Run a proportional coherence sweep after substantive changes. |
| `skill-staleness-audit` | `skills/skill-staleness-audit/SKILL.md` | Audit repository facts that have quietly stopped being true. |
| `skill-project-wiki-rag-bridge` | `skills/skill-project-wiki-rag-bridge/SKILL.md` | Connect a project to shared wiki and Qdrant RAG tooling safely. |
| `skill-slurp-chat` | `skills/skill-slurp-chat/SKILL.md` | Persist session state to memory-keeper and mcp-project-context. |
| `skill-ifa` | `invoice-finance-analyst/internal-invoice-analysis/SKILL.md` | Reconcile invoices and perform finance analysis. |

Install targets are `~/.claude/skills/`, `~/.codex/skills/`, and `~/.hermes/skills/domain/`.

Install with a symlink, never a copy. Default to a directory symlink; use a file symlink only where the canonical folder carries payload the agent should not see.

```bash
SKILL=<skill-name>
SRC=/Volumes/Data/_ai/_skills/skills_stuff/skills/$SKILL
for T in ~/.claude/skills ~/.codex/skills ~/.hermes/skills/domain; do
  ln -sfn "$SRC" "$T/$SKILL"
done
```

Audit for genuine copies while accepting both supported link forms:

```bash
for base in ~/.claude/skills ~/.codex/skills ~/.hermes/skills/domain; do
  for d in "$base"/*; do [ -e "$d/SKILL.md" ] || continue
    [ -L "$d" ] && continue; [ -L "$d/SKILL.md" ] && continue
    echo "COPY $d"; done
done
```

`skill-anydoc` is the file-symlink example because its canonical folder has an upstream clone and a launcher. The known runtime-link audit state is recorded in the relevant skills' documentation rather than this entrypoint.

## Skill Authoring Projects

Active skill authoring surfaces are under the repository root. Treat them as canonical authoring surfaces rather than runtime installs.

| Folder | Skill being built | Phase | Purpose |
|---|---|---|---|
| `skills/skill-ansible-repo-intelligence/` | `skill-ansible-repo-intelligence` (alias `skill-ari`) | Partial | Deterministic static Ansible repository intelligence. |

Rules:

- Do not edit runtime installs as the primary surface.
- When a skill reaches Phase 1 completion, move it to the regular-skills catalog and update its install targets.
- Each authoring project maintains its own governance and implementation documentation.
