---
Title: Screenshots - UNC Overview before and after the real-route placement guards, 2026-10-29
Category: reference
Status: current
Authority: local-supplement
Scope: Evidence for the Learned 2026-10-29 entry on real-route placement guards in references/layout-and-routing.md
Last reviewed: 2026-10-29
Summary: >-
  unified-network-controller's Overview page exported at 0.6 scale with the desktop CLI (component and group names only, no addresses or
  credentials): before, the map's own group placement; after, overview_group_search and overview_row_search on with the shared-run guard.
---

# UNC Overview, before and after (2026-10-29)

- `overview-before.png`: unc-flows.drawio as committed before ec08930 (map's placement): 245 crossings, 1 shared run.
- `overview-after.png`: ec08930, `overview_group_search` and `overview_row_search` on: 135 crossings, 1 shared run (`just layout-quality`).
  The thin arrows inside the OpenWISP group (bottom left) still cross 21 times: open in ROADMAP (in-group arrows).
