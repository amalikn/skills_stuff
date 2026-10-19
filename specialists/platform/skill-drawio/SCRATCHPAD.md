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
---

# Scratchpad

## Open items

- Archcore: 4 ADRs and 7 rules accepted 2026-10-19 (operator: "promote and accept"), indexed in `.archcore/index.guide.md`. Deferred: the
  flow-map spec and the adoption guide, until a second project adopts the engine.
- Installed 2026-10-19 (operator): directory symlinks `~/.claude/skills/skill-drawio`, `~/.codex/skills/skill-drawio` and
  `~/.hermes/skills/diagramming/skill-drawio` to this folder; listed in the skills_stuff `README.md`.
- unified-network-controller `wc-local/scripts/site_onboarding/asbuilt_read.py` still carries its own copy of the draw.io reader now in
  `scripts/drawio/read.py`; make it a thin caller (its KMZ part stays there) with its tests, when that project is next touched.
- draw.io desktop on the operator's Mac is now 32.5.5 (32.4.1 when the engine was built); the export flags were re-checked on 32.5.5, the
  "static export draws through boxes" claim (C-D16) only on 32.4.1.
- Vendor captures `documents/drawio-sources-20261019/style-reference.txt` and `documents/drawio-sources-20261019/mxfile-xsd.txt` hold example private addresses from the vendor docs;
  a redaction test like skill-nautobot's would flag them (verbatim captures are exempt by design; decide before adding such a test).
