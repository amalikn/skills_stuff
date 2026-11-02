---
Title: Sources for charts and flow-map trace
Category: reference
Status: current
Authority: External pages read 2026-11-02; the quoted facts are theirs
Scope: What the flowchart, swimlane, BPMN and trace work took from outside
Last reviewed: 2026-11-02
Summary: The pages behind references/charts-and-trace.md, what each gave, and what was left out.
---

# Sources for charts and flow-map trace

| Source                       | Label                                | What it gave                                                                                                                   |
| ---------------------------- | ------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------ |
| [jamb, traceability](https://jamb.readthedocs.io/en/latest/iec-62304/traceability.html) | VERIFIED_PRIMARY                     | A hash mismatch flags downstream links suspect; a review clears them; trace both directions                                    |
| [Jama, clear suspect links](https://help.jamasoftware.com/ah/en/manage-content/coverage-and-traceability/relationships/clear-suspect-links.html) | VERIFIED_PRIMARY                     | The flag is cleared by a person who found no impact or made the change                                                         |
| [menard](https://nlebovits.github.io/menard/) | VERIFIED_PRIMARY                     | A deterministic pre-commit check, section-level links, JSON output for agents                                                  |
| [snippetdrift 0.1.0](https://pypi.org/project/snippetdrift/) | USER_STATED (operator's PDF of the   | `check` apart from `accept`, a `reviewed:` sign-off, the accepted text kept for diffs. Its line-range anchors were not taken   |
|                              |   page; PyPI refuses agents)         |                                                                                                                                |
| [Swimm, code-coupled docs](https://docs.swimm.io/new-to-swimm/benefits-of-code-coupled-documentation) | VERIFIED_SECONDARY (search summary)  | Code elements in a doc are checked on every change. Its algorithm is proprietary and not copied                                |
| [ELK layered overview](https://eclipse.dev/elk/blog/posts/2025/25-08-21-layered.html) | VERIFIED_PRIMARY                     | The phases (cycle breaking, layers, crossings, placement, routing) and the MODEL_ORDER strategy                                |
| [BPMN, Wikipedia](https://en.wikipedia.org/wiki/Business_Process_Model_and_Notation) | VERIFIED_SECONDARY                   | The element families. The X-less exclusive gateway is from memory of the BPMN 2.0 specification: UNVERIFIED against            |
|                              |                                      |   the specification                                                                                                            |
| `drawio-example-BPMN.xml`    | VERIFIED_PRIMARY                     | The real `mxgraph.bpmn.shape` style keys (`outline`, `symbol`); the `error` symbol was confirmed by rendering it               |
|   (draw.io's                 |                                      |                                                                                                                                |
|   own, jgraph.github.io)     |                                      |                                                                                                                                |
