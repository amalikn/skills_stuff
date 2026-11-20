---
Title: skill-pad flow map index
Category: index
Status: current
Authority: local-supplement
Scope: docs/flows/ in skill-pad: the flow map's parts, the assembled map and the draw.io drawing rendered from it
Last reviewed: 2026-11-20
Summary: >-
  How Pad work moves between the agent, the pad CLI, skill-pad's scripts and a project's repo, as data (parts/) rendered to draw.io by
  skill-drawio's engine with `just flows`; `just check` fails when the drawing is out of step or a layout audit finds a fault.
---

# skill-pad flow map

Flows are data first (operator, 2026-11-20: "add flows to skill-pad", draw.io flows). The parts are edited by hand; `just flows` assembles `flows.yaml` from them and renders the drawing with
skill-drawio's engine, run in skill-drawio's own environment. `just flows-check` (part of `just check`) fails when the assembled map or the drawing is out of step, a step cites a script or function
that does not exist, or a layout audit finds a fault.

| File                          | Role                                                                                                                       |
| ----------------------------- | -------------------------------------------------------------------------------------------------------------------------- |
| [parts/](parts/)              | **Edit here.** `master.yaml` (drawing settings, families, `#@include` lines), one file per component group and per flow family |
| [flows.yaml](flows.yaml)      | **Generated, do not edit.** The assembled map                                                                              |
| [drawio/skill-pad-flows.drawio](drawio/skill-pad-flows.drawio) | **Generated, do not edit.** Overview, the end-to-end page, then one page per flow                                          |

## The flows

| Family           | Flows                                                                                            |
| ---------------- | ------------------------------------------------------------------------------------------------ |
| Work items       | 1 a piece of work from start to done; 2 an ask that blocks its work; 3 a bug to fixed and live   |
| Records          | 4 bug and feature trackers generated from Pad; 5 decisions mirrored into Pad; 6 the focus export |
| Writing standard | 7 conventions from the central baseline; 8 the layout pass; 9 the links pass                     |
| Operations       | 10 the nightly backup; 11 the live push feed                                                     |

Pages count from 1 when exported: 1 = Overview, 2 = End-to-end, then flow n is page n + 2. A step's `code` names `scripts/<file>[:function]`; the renderer checks it exists, so a renamed function
breaks the check rather than the map going stale. When a script or rule in this pack changes a flow, update its part in the same pass and run `just flows`.
