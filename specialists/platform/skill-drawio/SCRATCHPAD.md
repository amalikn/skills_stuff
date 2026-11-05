---
Title: skill-drawio scratchpad
Category: state
Status: current
Authority: local-supplement
Scope: Working state of the skill-drawio pack between sessions
Last reviewed: 2026-10-19
Kind: state
Budget: 200 lines, 25 KB
Keep: KEEP-marked items only
Open items tracker: this file, Open items
Summary: Transient working state for skill-drawio; durable facts move to references, sources.yaml or CHANGELOG.
Archive: docs/history/ (`--find`, `--show`)
Last rotated: 20261106_1032
---

# Scratchpad

## Open items

- 20261102 chart-php-steps arc_clashes on `cli~0-close` (smc_change_flows_check exits 1). Plain flowchart: real spanning and the measured swap. `just check` runs no unit tests: add them.

- Older open items are tracked in [this](this).
- KEEP 2026-10-27 router changes (sibling branch crossings, own reserved corners, exhaustive row-gap order, one-flow family label) change
  the drawings of other consumers: re-render and drift-check unified-network-controller and smc-resiliency in their own sessions; expect fewer
  crossings, never more per gap.
- Done 2026-10-19: unified-network-controller's as-built reader re-exports `drawio.read` (byte-identical on 27 files), its flow renderer
  retired in favour of `render_flowmap.py` and its engine tests moved to `tests/test_layout_rules.py` (ROADMAP items ticked).
