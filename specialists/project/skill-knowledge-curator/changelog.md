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

- 2026-10-27 20:39 (operational): the skill-ai-it session repointed this `justfile` to `scripts/checks/doc_freshness.py` and `role_check.py`; `just check`
  passes again. Left uncommitted with this slurp's lines (no commit asked).
- 2026-10-27 20:38 (incident): the commit of the two lines below was not made: `just check` exited 2 because skill-ai-it `scripts/doc_freshness.py` was moved to
  `scripts/checks/` by another session (uncommitted) while this justfile names the old path; the pack's own ruff and 42 tests passed. Not bypassed; options in SCRATCHPAD.
- 2026-10-27 (proposed, not decided): this changelog's dated bullets give the wiki page no Recent changes (the generator reads dated headings).
- 2026-10-27 20:32 (fix, wiki_stuff `45423a3`): `project_page.py` now accepts annotated `## Current state` headings (`— KEEP`, comment, date);
  this pack's wiki page shows its Current state. Open item closed.
- 2026-10-27 20:21 (docs): `references/feature-inventory.md` gains the v2 staged roadmap (gate 0 = real-corpus pilot; stages 1 gap matrix, 2 deterministic
  additions, 3 semantic and optional model adapter, 4a code and Mermaid, 4b draw.io and ASCII, 4c PDF and Office, 5 federation within one portfolio,
  6 slurp Step 4b, 7 optional engines), each stage with its `V2-T` exit tests; the v1 "rejected" line now says which two items v2 narrows.
- 2026-10-27 (decisions, operator): v2 is a staged roadmap on top of v1; all four new source types adopted; federation within one portfolio only;
  v1 schema and libraries kept with a v2 mapping; optional model adapter in `kc`; promotion and proposal paths both kept; slurp hook is a conditional
  Step 4b; run envelope, `offline_only` and model allowlist added. Detail: `docs/catalog.md`, v2 section.
- 2026-10-27 (incident): the catalog first listed V7 (test-ID namespace) and V8 (layout) under operator answers; both were agent defaults, never
  asked. Relabelled as defaults the operator may override. The markdown hook cannot wrap inside a long link label and left a 283-character
  line in feature-inventory.md; fixed by shorter labels.
- 2026-10-27 (finding): the wiki project page renders no Current state, because wiki_stuff `project_page.py` matches the heading exactly and this
  SCRATCHPAD marks it `— KEEP`; left open in SCRATCHPAD.
- 2026-10-27 20:15 (docs): v2 spec moved from the pack root to `docs/knowledge-curator-foss-implementation-spec-v2.md` (front matter and Contents added, text verbatim); `docs/catalog.md` gains its
  row, conflicts V1-V9 against the built v1, and two rounds of operator answers. Nothing built.
- 2026-10-27 (operational): venv built at `skills-working-cache/skill-knowledge-curator/.venv` (Python 3.14.5, mise) with the pinned requirements; read-only `kc inventory` (no --apply) over
  `project_stuff/mcp-post-migration-audit`: 24 files, 213 sections, 0.14 s, five byte-identical pairs between `final-audit-pack/` and the step reports; nothing written there.
- 2026-10-27 (install): symlinks `~/.claude/skills/skill-knowledge-curator` and `~/.codex/skills/skill-knowledge-curator` to this folder; `/skill-kc` alias block added to `~/.claude/CLAUDE.md`.
- 2026-10-27 (incident): the OPA gate refused a recursive delete of a scratchpad run folder; later runs used fresh `mktemp -d` folders. The security hook refused a test file holding an `os.system`
  YAML tag string; the test now uses `!!python/name:builtins.print`.
- 2026-10-27 (incident): running markdown_rewrap with `--toc-depth 3 --update` on skill-coder `references/design-patterns.md` to fix one entry reflowed the whole file (115 lines deleted); restored
  from git HEAD and only the P-31 entry re-applied (diff 29 added lines).
- 2026-10-27: skill-ai-it governed-file standard adopted (`adopt_governed_files.py --apply`: recipes, freshness and role checks in `check`, baselines); `SCRATCHPAD.md` created; catalogue rows added in
  skills_stuff `README.md` and `.agents/skill-surfaces.md`.
- 2026-10-27: Pack created (alias skill-kc). Source documents moved to `docs/` with hyphenated names, front matter, level-3 Contents and a redrawn handoff 4.1 diagram; `docs/catalog.md` records the
  operator decisions and settles conflicts C1-C12.
- 2026-10-27: v1 kernel `scripts/knowledge_curator.py` (kc) and `knowledge_curator_lib/` written under skill-coder: inventory, worksheet, claims, coverage, candidates, relate, review, decide, render,
  promote, archive-plan (plan only), query, intake, validate, report. 42 tests pass; `just check` green.
- 2026-10-27: `evidence_verified` promotion gate on by default (review note: a source edited after render would be promoted stale).
- 2026-10-27: References consolidated from both documents: workflow, claim model and taxonomy, conflicts and review, authority and promotion, archive safety, invocation contract, evaluation, feature
  inventory.
