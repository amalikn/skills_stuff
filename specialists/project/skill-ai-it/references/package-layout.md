---
Title: skill-ai-it reference: Skill package layout
Category: reference
Status: current
Authority: local-supplement
Scope: On-need reference moved verbatim from SKILL.md
Last reviewed: 2026-10-10
Summary: >-
  Skill package layout; moved verbatim from SKILL.md so SKILL.md stays an orchestration file within budget.
---

# skill-ai-it reference: Skill package layout

Moved verbatim from `SKILL.md` on 2026-10-10 to keep that file within its budget for files loaded whole.

## Skill Package Layout

This skill is expected to be packaged with reusable template and pattern files. The embedded examples in this `SKILL.md` are fallback/reference content only; when the files below exist, use them as
the source for generated content.

```text
skill-ai-it/
├── SKILL.md
├── README.md
├── AGENTS.md
├── CLAUDE.md
├── AI_NAVIGATION.md
├── context-map.yaml
├── CHANGELOG.md
├── ARCHITECTURE.md
├── justfile
├── .mise.toml
├── .markdownlint-cli2.jsonc
├── scripts/
│   ├── upgrade_navigation_control_layer.py
│   ├── validate_navigation_control_layer.py
│   ├── check_expected_diff.py
│   ├── check_governance.py
│   ├── selftest_blocks.py
│   └── README.md
├── templates/
│   ├── AI_NAVIGATION.md
│   ├── context-map.yaml
│   ├── update_rules.yaml
│   ├── repomix.config.json
│   ├── justfile
│   ├── AGENTS-navigation-block.md
│   ├── AGENTS-governance-checks-block.md
│   ├── scripts-README.md
│   ├── check_governance.py
│   ├── context_preflight.sh
│   └── .markdownlint-cli2.jsonc
└── patterns/
    ├── archcore-routing.md
    ├── memory-bank-structure.md
    ├── drift-audit.md
    ├── governance-checks.md
    ├── navigation-control-automation.md
    └── script-task-audit-checklist.md
```

### Template precedence

1. Prefer files under `templates/` for generated project files.
2. Prefer files under `patterns/` for optional guidance modules.
3. Use embedded examples in this `SKILL.md` only when the separate template/pattern files are missing.
4. If a template file and embedded example disagree, the external template file wins.
5. On repeat runs, never overwrite target project files wholesale; apply managed blocks or write `.proposed` files as defined in the Repeat-Safety Contract.
