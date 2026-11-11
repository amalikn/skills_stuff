---
Title: Business-view prototypes (candidates for skill-drawio views)
Category: prototypes
Status: proposed
Authority: working
Scope: Hand-drawing scripts kept so the operator can choose which business views become generated skill-drawio views
Last reviewed: 2026-11-11
Summary: >-
  One-off scripts that drew the enterprise-strategy business views on 11 Nov 2026 (roadmap matrix, benefit network, solution scorecard, requirement
  tree, site shapes, cost drivers, and a Gantt from a skill-drawio session); none is an engine view yet; the next session decides which to adopt.
---

# Business-view prototypes

Kept at the operator's request (2026-11-11: "I don't want you to lose those codes"). These are not engine views and are not run by any recipe. Each wrote a plain, hand-made draw.io file once; the
drawings live in enterprise-strategy `docs/flows/`. The next session decides which become skill-drawio views (data-first, generated, audited) and which stay hand drawings.

## Contents

- [What the trial showed](#what-the-trial-showed)

| Script           | Draws                                                              | Reads                                               | Drawing it made (enterprise-strategy)                  |
| ---------------- | ------------------------------------------------------------------ | --------------------------------------------------- | ------------------------------------------------------ |
| `draw_matrix.py` | Roadmap matrix: requirements (rows) by Today, Phase 1, Phase 2,    | a flow map part whose flows are one per             | `docs/flows/roadmap-matrix-20261111_2106.drawio`       |
|                  |   Target; cells coloured by project                                |   requirement, step labels "Today: / Phase 1,       |                                                        |
|                  |                                                                    |   <when>: / Phase 2: / Target:"                     |                                                        |
| `draw_views.py`  | Five pages: benefit dependency network, solution scorecard (RAG by | nothing: content is written into the script         | `docs/flows/business-views-20261111_2135.drawio`       |
|                  |   stage), requirement tree, site shapes (today and shapes A and    |                                                     |                                                        |
|                  |   C), cost driver tree                                             |                                                     |                                                        |
| `draw_gantt.py`  | Program Gantt chart, drawn by the skill-drawio                     | nothing: tasks and dates hard-coded in TASKS, from flows-program.yaml (11 Nov)                            | `docs/flows/drawio/program-gantt-20261111_2103.drawio` |
|                  |   session skill-drawio-fa                                          |                                                     |                                                        |

Run, from the enterprise-strategy project (its venv has PyYAML):

```bash
python -I draw_matrix.py docs/flows/parts/flows-requirements.yaml docs/flows/roadmap-matrix-<stamp>.drawio
python -I draw_views.py docs/flows/business-views-<stamp>.drawio
python3 draw_gantt.py docs/flows/drawio/program-gantt-<stamp>.drawio   # stdlib only; added by skill-drawio-fa
```

All three overwrite their output: never point one at a drawing someone has edited by hand.

## What the trial showed

- Benefit network, scorecard and cost tree follow from data a map could hold (a changes and benefits list, ratings per stage, cost drivers): good candidates for generated views.
- Site shapes reads best as an illustration; it may stay hand-drawn.
- The requirement tree is many-to-many and gets busy; draw.io's own orthogonal routing ran lines through boxes, so these scripts use straight lines between fixed sides (`edgeStyle=none`, exit right,
  entry left; top to bottom on trees).
- In `draw_views.py` the content (steps, changes, benefits, ratings) is hard-coded; an engine view would read it from the map.
- Routing learnings from the operator's review (2026-11-11, `draw_views.py`):
  - Cost driver tree: a root box as tall as all its drivers, and each driver as tall as its steps, lets every line run straight across with no shared end
    point. Reusable for any one-to-many tree.
  - Requirement tree (10 to 7 to 3 boxes, 21 and 9 links): reordering the middle row by barycentre made it worse to the operator (order matters more
    than crossings). Square lines on tracks with their own ports, a crossing-minimising local search over tracks and gaps sized 14 px a track cut the
    upper gap from 138 to 94 crossings with no shared segments; first-fit tracks squeezed into a fixed gap looked worse than straight lines. Still busy:
    open whether this view stays a tree or becomes a grid (next session). Untried: let each box's exit order follow its line's track order.

