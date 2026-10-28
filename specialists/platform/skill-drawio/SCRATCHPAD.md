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
Last rotated: 20261028_2305
---

# Scratchpad

## Open items

- Older open items are tracked in [this](this).
- KEEP 2026-10-27 router changes (sibling branch crossings, own reserved corners, exhaustive row-gap order, one-flow family label) change
  the drawings of other consumers: re-render and drift-check unified-network-controller and smc-resiliency in their own sessions; expect fewer
  crossings, never more per gap.
- Done 2026-10-19: unified-network-controller's as-built reader re-exports `drawio.read` (byte-identical on 27 files), its flow renderer
  retired in favour of `render_flowmap.py` and its engine tests moved to `tests/test_layout_rules.py` (ROADMAP items ticked).
- draw.io desktop on the operator's Mac is now 32.5.5 (32.4.1 when the engine was built); the export flags were re-checked on 32.5.5, the
  "static export draws through boxes" claim (C-D16) only on 32.4.1.
- Vendor captures `documents/drawio-sources-20261019/style-reference.txt` and `documents/drawio-sources-20261019/mxfile-xsd.txt` hold example private addresses from the vendor docs;
  a redaction test like skill-nautobot's would flag them (verbatim captures are exempt by design; decide before adding such a test).
