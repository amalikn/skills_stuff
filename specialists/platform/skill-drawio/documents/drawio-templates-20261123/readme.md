---
Title: draw.io templates kept for reuse
Category: reference
Status: current
Authority: External examples fetched 2026-11-23; the drawings are jgraph's, kept verbatim as starting points
Scope: Templates the operator picked to keep, what each suits and how to use it with this pack
Last reviewed: 20261123_0000
Summary: >-
  An Ishikawa (fishbone) cause-and-effect example and the story-map example from the draw.io blog, stored verbatim, with when to use each and how to
  rebuild them data first.
---

# draw.io templates kept for reuse

| File | Source (fetched 2026-11-23) | What it is | Use it for |
| ---- | --------------------------- | ---------- | ---------- |
| `ishikawa-example-manufacturing.svg` (and `.drawio`, the source embedded in the SVG) | https://www.drawio.com/img/blog/ishikawa-example-manufacturing.svg (operator link, 2026-11-23) | Ishikawa or fishbone diagram: one effect at the head ("Defective part"), cause categories as main bones (Measurements; Mission and environment; Production state; Materials and information; Methods and processes ...), causes as small bones | Root-cause analysis after an incident or a recurring failure: a post-mortem, a failed gate or push, a flaky test, an outage. Bones for software and infrastructure: People and process, Tooling and code, Platform and host, Network, Data and storage, Identity and secrets, Monitoring. Not for a timeline (use a journey page) or a flow (use the flow-map engine). |
| `story-map.drawio` | https://raw.githubusercontent.com/jgraph/drawio-diagrams/master/blog/story-map.drawio | User story map: a goal bar, activities as a backbone, tasks and sub-tasks below | Product scope and releases: what a person does, what is built, next and later. Used first in continuum's journey.drawio (Story map page, Built / Next / Later bands). |

How to use them here: never edit a copy for a project by hand when the drawing should stay current; rebuild the layout data first (a YAML file
and a small page builder with `drawio.mxfile.Page`, `page.base_locked = True` for one-click links, `page_audit()` before writing; see
[data-first-diagrams](../../references/data-first-diagrams.md), "page layouts without flows"). A one-off picture may start from a copy of the file;
then it is hand-made and never regenerated over.

Facts about the files: the SVG embeds the editable diagram in its `content` attribute (draw.io's "editable SVG"), extracted verbatim to the
`.drawio` here. sha256 prefixes at fetch: SVG 544b4dbf0a554703, story map d163c86b60bb37f9.
