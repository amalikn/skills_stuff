---
Title: Group columns screenshots
Category: skill-reference
Status: current
Authority: Renders of smc-resiliency's S2 flow map (a lab design, no site data); the before image is the operator's screenshot, the after exported with scripts/drawio_export.py
Scope: Overview groups "Outside the box" and "Storage on the box" before and after drawing.group_columns and group_layout
Last reviewed: 2026-10-20
Summary: Two Overview groups of unlinked boxes in the default three-column grid, then stacked (vertical) and in a 2 by 2 grid (grid 2).
---

# Group columns (2026-10-20)

- [before-three-columns.png](before-three-columns.png) The group in the default grid of three: wide and mostly empty (operator's screenshot, draw.io desktop).
- [after-one-column.png](after-one-column.png) The same group with `group_columns: {Outside the box: 1}`: the three boxes stacked (crop of page 1 exported at scale 1).
- [storage-before-three-columns.png](storage-before-three-columns.png) Four boxes in the default grid of three: a lone fourth box on its own row (operator's screenshot).
- [storage-after-grid-2.png](storage-after-grid-2.png) The same group with `group_layout: {Storage on the box: grid 2}` (crop of page 1, scale 1).
- [storage-cell-before-left.png](storage-cell-before-left.png) Storage as the fourth group, wrapped to row 2, column 1, under Lab and far from its main writer (operator's screenshot).
- [storage-cell-after-2-2.png](storage-cell-after-2-2.png) The same with `group_cell: {Storage on the box: [2, 2]}`: under On the SMC, both thick arrows straight down (crop of page 1).
