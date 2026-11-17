---
Title: Changelog
Category: change-log
Status: current
Summary: Newest entries only; older ones rotate to docs/history.
Authority: record
Scope: Dated changes to this pack
Kind: log
Budget: 200 lines, 25 KB
Last reviewed: 2026-11-17
---

# Changelog

## Unreleased

- 2026-11-17: a row whose source holds an arrow (`-> a -> b`, a chain continued) is not part of an arrow list; found by the first `--check` gate run.
- 2026-11-17: `ascii-fix --check`, a read-only gate for a project's closing check (exit 1 when a diagram would change); `edge_issues()`, `ch()` and
  `GRID_BORDER` moved to `scripts/ascii/checks.py` to keep `ascii_fix.py` under the 400-line budget (behaviour unchanged: sweep counts identical).
- 2026-11-17: arrow lists line up (operator): `align_arrows()` in `scripts/ascii/checks.py`; box rows, chains and rows already in place excluded
  after a sweep over real documents; tests mutation-proven; references/fixing-diagrams.md rule.
- 2026-11-17: pack created with skill-ai-it `new-skill scaffold` from a seed kept outside the pack; references, scripts and evidence to be written from the seed.
- 2026-11-17: built from the seed (operator: "do you think it is better to have skill-ascii-diagrams of its own?", answered both): `scripts/ascii_flow_render.py`,
  `scripts/ascii_fix.py`, `scripts/ascii/` and their tests moved from skill-drawio with history (`git mv`), with `documents/ascii-sources-20261117/`; six
  references written from the seed's lessons; `sources.yaml` claims C-AD01 to C-AD04; ROADMAP from skill-drawio's ASCII items; pack contract 0 errors, 0 warnings.
- History before the move (skill-drawio CHANGELOG): the renderer promoted 2026-11-16; `ascii-fix` built 2026-11-17 and corrected over real documents (grid
  dividers, glued connectors, generated files refused, fan-out branches, borders carrying arrows and tees, ragged-row tails); stage 1 checks and snapping.
