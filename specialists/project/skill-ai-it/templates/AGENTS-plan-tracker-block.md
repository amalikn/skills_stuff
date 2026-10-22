---
Title: AGENTS.md plan tracker rules (template)
Category: template
Status: current
Authority: canonical
Scope: The working rules a project pastes into its AGENTS.md when it keeps a plan tracker (docs/trackers/plan-tracker.md)
Last reviewed: 2026-10-22
Summary: >-
  Paste-in rules for keeping a plan tracker current and navigable; from smc-resiliency and unified-network-controller (operator, 2026-10-21 and
  2026-10-22). Reference: references/target-map-and-timeline.md, "The plan tracker page".
---

# AGENTS.md plan tracker rules (template)

Paste under the project's Working rules; replace `<date>` with the adoption date.

```markdown
- Keep [docs/trackers/plan-tracker.md](docs/trackers/plan-tracker.md) current (skill-ai-it plan tracker, adopted <date>): read it first; update it
  in the same pass as a stage moving, a document starting or stopping to govern, or a decision made or folded into a design. Its Stages table and
  Timeline are generated (`just target-map`, `just plan-timeline` from target-map.yaml and docs/trackers/plan-timeline.yaml); edit those, never the blocks.
- Where we are is rewritten, never appended: an "As of" date, one line on the live state, one numbered item per workstream led by its stage
  links, then what waits on the operator and a horizon line from the plan's dates.
- Hyperlink wherever possible: each named section, stage, risk, decision stamp or drawing links to the exact heading. What next rows link to where
  their work starts and stay on one line (the markdown hook splits a row rendered wider than 200 columns: shorten it). `just check` runs
  `anchor_links.py` (a retitled heading fails until its links follow) and `plan_tracker.py --check`.
- After a CHANGELOG entry names a started stage, review that stage in target-map.yaml and set its `reviewed`.
```
