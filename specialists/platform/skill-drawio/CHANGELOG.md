---
Title: skill-drawio changelog
Category: log
Status: current
Authority: local-supplement
Scope: Release and governance history of the skill-drawio pack
Last reviewed: 2026-10-19
Kind: log
Budget: 200 lines, 25 KB
Archive: docs/history/
Summary: Release history and governance changes of skill-drawio; the release heading holds the version of record.
---

# Changelog

## Unreleased

- 20261019 Adopted by unified-network-controller in full: its renderer wrapper retired (its profile is now the `drawing:` block of its map,
  rendered by `render_flowmap.py`; the drawing changed only in its banner and `host` lines), and its as-built reader re-exports `drawio.read`
  (byte-identical output on 27 as-built files). The engine tests it held moved here as `tests/test_layout_rules.py` (17 tests: text fitting, notes,
  step boxes, header lines, bold spans, arrow ports, overview arrow styles and each audit at its exact threshold).
- 20261019 Fix: a map whose components share one End-to-end tier raised IndexError (no channel between columns). The grid keeps at least one
  channel and the page widens to hold it; drawings with two or more tiers are unchanged (UNC's and the example's byte-identical). Learned 2026-10-19 in `references/layout-and-routing.md`; regression test `test_one_column_end_to_end_page_draws_and_passes_every_audit`.
- 20261019 `ROADMAP.md` and `SETUP.md` added (operator, 2026-10-19: "add ROADMAP.md in both the skills", "and SETUP.md"), to skill-ai-it's templates; ROADMAP from this pack's SCRATCHPAD open items and unified-network-controller's retirement assessment, SETUP from the justfile, `.mise.toml` and requirements. README lists both and links SETUP from Quick start.
- 20261019 Archcore promoted (operator: "promote and accept"): 4 ADRs and 7 rules written `accepted` under `.archcore/`, indexed in
  `.archcore/index.guide.md` with the deferred spec and guide and the never-promoted reasons; `ARCHCORE_PROMOTION_CANDIDATES.md` deleted;
  `context-map.yaml`, `repomix.config.json` and the checker's `CONDITIONAL_PATHS` updated to match.
  Incident, no harm: a heredoc edit script failed its assertion, but the `git rm` on the following line still ran (the delete was intended).

- 20261019 Installed (operator: "Install skill-drawio into Claude, Codex and Hermes, as skill-coder was"): directory symlinks into the Claude and
  Codex skill folders and Hermes's `diagramming` category, all pointing at this canonical folder; Claude Code lists the skill.
- 20261019 Process notes from the build (no effect on the pack's content): `# noqa` imports were written twice (UNC wrapper, `tests/test_helpers.py`)
  and replaced with `importlib` the same hour (skill-coder Learned entry in its Python override); one check log went to `/tmp` instead of the
  scratchpad; skill-drawio files were marked intent-to-add in the skills_stuff index (`git add -N`) so doc freshness could see them before the commit.
  `references/export-and-self-review.md` crop example no longer writes to `/tmp`.
- 20261019 Archcore candidates reviewed (operator: "assess if the archcore entries for skill-drawio are correct ... fix them before I promote"):
  `ARCHCORE_PROMOTION_CANDIDATES.md` rewritten in skill-ai-it's report format with five corrections and six new candidates. Code fixed to match:
  `scripts/flowmap/pages.py` `write_drawing` refuses to write over a drawing without the generated banner (test added); `Profile` defaults neutral
  (`default_tier` 0, band title "Stores and secrets"). unified-network-controller's drawing re-proven byte-identical.
## 0.1.0 — 2026-10-19

- 20261019 Pack created (operator, 2026-10-19: a reusable skill capturing all the draw.io work from unified-network-controller, so any project can draw
  its own components from YAML). Engine promoted from unified-network-controller `scripts/render/flows_drawio.py` (2342 lines) and split into the
  `drawio` package (`mxfile`, `audit`, `route`, `read`, `export`) and the `flowmap` package (`profile`, `model`, `overview_layout`, `overview`,
  `e2e_grid`, `e2e`, `pages`), with `schema_lite.py` and `code_refs.py`; UNC's constants became a `Profile`, and `Profile.from_drawing()` reads an
  optional `drawing:` block for new projects. Every module is under 400 lines and every function under 60 (the 192-line overview function became an
  `Overview` class; the End-to-end class split into grid and search-and-draw).
- Proof: unified-network-controller's drawing renders byte-identical through the skill (SHA-1 `b8b22e66e1fb1932323ba6f103c6bd9a2a1953cd`
  before and after); its `just test` (1640) and `just check` pass with its renderer as a thin wrapper. Render time unchanged (0.89 to 0.90 s).
- New: `scripts/drawio/read.py` (from UNC's as-built reader, draw.io part, plus the page codec's encoder and nearest-line label matching),
  `scripts/drawio/export.py` and `drawio_export.py` (desktop CLI, pages from 1, layers, subprocess timeout), `yaml_list_patch.py` (comment-preserving list
  edits, plan by default, `--apply`; generalised from a one-off), `render_flowmap.py` (generic front end with `--audit`),
  `schemas/flowmap.schema.json`, and the example map `examples/shop/` (renders, current, every audit clean, every component reached).
- References (7) captured from UNC `docs/flows/readme.md`, UNC CHANGELOG 20261019_1602 and 20261019_1607, the enterprise-strategy CHANGELOG of
  2026-10-12, and the draw.io documentation (21 verbatim captures); `sources.yaml` C-D01 to C-D34; `compatibility.yaml` (desktop 32.4.1 and 32.5.5).
- Governance through skill-ai-it (AGENTS, AI_NAVIGATION, context-map, checker, justfile); `.archcore/` initialised empty, candidates in
  `ARCHCORE_PROMOTION_CANDIDATES.md` (proposed).
