---
Title: skill-knowledge-curator Changelog
Category: changelog
Status: current
Authority: local-supplement
Scope: Changes to the skill-knowledge-curator pack
Last reviewed: 2026-10-27
Summary: Dated record of changes to the Knowledge Curator pack.
Kind: log
Budget: 200 lines, 25 KB
---

# Changelog

## Unreleased

- 2026-10-27 (operational): venv built at `skills-working-cache/skill-knowledge-curator/.venv` (Python 3.14.5, mise) with the pinned requirements;
  read-only `kc inventory` (no --apply) over `project_stuff/mcp-post-migration-audit`: 24 files, 213 sections, 0.14 s, five byte-identical
  pairs between `final-audit-pack/` and the step reports; nothing written there.
- 2026-10-27 (install): symlinks `~/.claude/skills/skill-knowledge-curator` and `~/.codex/skills/skill-knowledge-curator` to this folder;
  `/skill-kc` alias block added to `~/.claude/CLAUDE.md`.
- 2026-10-27 (incident): the OPA gate refused a recursive delete of a scratchpad run folder; later runs used fresh `mktemp -d` folders.
  The security hook refused a test file holding an `os.system` YAML tag string; the test now uses `!!python/name:builtins.print`.
- 2026-10-27 (incident): running markdown_rewrap with `--toc-depth 3 --update` on skill-coder `references/design-patterns.md` to fix one
  entry reflowed the whole file (115 lines deleted); restored from git HEAD and only the P-31 entry re-applied (diff 29 added lines).
- 2026-10-27: skill-ai-it governed-file standard adopted (`adopt_governed_files.py --apply`: recipes, freshness and role checks in `check`,
  baselines); `SCRATCHPAD.md` created; catalogue rows added in skills_stuff `README.md` and `.agents/skill-surfaces.md`.
- 2026-10-27: Pack created (alias skill-kc). Source documents moved to `docs/` with hyphenated names, front matter, level-3 Contents and a redrawn
  handoff 4.1 diagram; `docs/catalog.md` records the operator decisions and settles conflicts C1-C12.
- 2026-10-27: v1 kernel `scripts/knowledge_curator.py` (kc) and `knowledge_curator_lib/` written under skill-coder: inventory, worksheet, claims,
  coverage, candidates, relate, review, decide, render, promote, archive-plan (plan only), query, intake, validate, report. 42 tests pass;
  `just check` green.
- 2026-10-27: `evidence_verified` promotion gate on by default (review note: a source edited after render would be promoted stale).
- 2026-10-27: References consolidated from both documents: workflow, claim model and taxonomy, conflicts and review, authority and promotion,
  archive safety, invocation contract, evaluation, feature inventory.
