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
Open items tracker: docs/trackers/open-items-20261028_2305.md
Summary: Transient working state for skill-drawio; durable facts move to references, sources.yaml or CHANGELOG.
Archive: docs/history/ (`--find`, `--show`)
Last rotated: 20261120_1836
---

# Scratchpad

## Open items

- Review follow-ups (periodic review 2026-11-19, found by the review agents, not fixed): references/file-format.md:60 says the UNC tests assert layer order (no such test found in the pack); some Learned entries still name scripts/ascii_*.py from before skill-ascii-diagrams took them.
- 20261102 chart-php-steps arc_clashes on `cli~0-close` (smc_change_flows_check exits 1). Plain flowchart: real spanning and the measured swap. `just check` runs no unit tests: add them.

- Older open items are tracked in [open-items-20261028_2305.md](docs/trackers/open-items-20261028_2305.md).
- Done 2026-10-19: unified-network-controller's as-built reader re-exports `drawio.read` (byte-identical on 27 files), its flow renderer
  retired in favour of `render_flowmap.py` and its engine tests moved to `tests/test_layout_rules.py` (ROADMAP items ticked).
