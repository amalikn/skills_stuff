---
Title: Straight-first branches, diamond-aware labels and the End-to-end left channel (screenshots)
Category: reference-evidence
Status: current
Authority: evidence for references/layout-and-routing.md Learned 2026-11-07
Scope: skill-drawio flow pages and End-to-end pages, rendered from smc-resiliency's lab flow map
Last reviewed: 2026-11-07
Summary: Before and after images for straight-first routing, labels judged by a diamond's outline, and in-column links on the first column's left.
---

# Straight-first and left channel: before and after

Taken 2026-11-07 from smc-resiliency's `docs/flows/flows.yaml` (lab and spike flows only, no site names, addresses or serials). "Before" is the committed drawing
`docs/flows/drawio/smc-resiliency-flows.drawio` (engine at skills_stuff bd1691d plus the uncommitted compact diamonds); "after" is the same map rendered by this change to a scratch file. Exported with
`scripts/drawio_export.py` at scale 1, cropped with `sips`.

| Image                       | Page                                      | What it shows                                                                                                             |
| --------------------------- | ----------------------------------------- | ------------------------------------------------------------------------------------------------------------------------- |
| [before-commission-gates.png](before-commission-gates.png) | 9. Commissioning (page 24), gates 3 and 4 | 3 -> 4 (the step beside 3) leaves 3's top, 3 -> 5 leaves its right; the "4 No" label sits above its line on the lane edge |
| [after-commission-gates.png](after-commission-gates.png) | the same crop                             | 3 -> 4 and 4 -> 5 run straight across; 3 -> 5 leaves 3's bottom, 4 -> 6 its top; labels on their lines                    |
| [before-testing-e2e.png](before-testing-e2e.png) | E2E: Testing and verification (page 14)   | links inside the Lab column share the gap to "On the SMC" with every cross-column arrow                                   |
| [after-testing-e2e.png](after-testing-e2e.png) | the same page                             | the Lab column's in-column links run in a channel on its left; the middle gap holds only cross-column arrows              |
| [after-vagrant-e2e-corridor.png](after-vagrant-e2e-corridor.png) | E2E: Vagrant VM (page 8), after the left channel | the State file and /data/confexts connectors each have their own run; no shared corridor |
