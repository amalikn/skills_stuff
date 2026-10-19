---
Title: Layout audits
Category: skill-reference
Status: current
Authority: scripts/drawio/audit.py as read on 2026-10-19 and the UNC flow-map tests that prove each audit can fail; the code wins over this summary
Scope: >-
  The checks a routed draw.io drawing must pass before a person sees it: what each audit catches, its threshold, how a generator runs it, and the rule that every
  audit has a test showing it can fail
Last reviewed: 2026-10-19
Summary: Eight geometric audits (box crossings, diagonals, shared runs, short heads, labels on arrows, label overlaps, arc clashes, missing layers) with thresholds.
---

# Layout audits

Each audit in `scripts/drawio/audit.py` encodes an operator complaint about a real drawing: something a reviewer must never be shown. A generator runs them on every routed page in its tests and
asserts that every list is empty. Claim IDs refer to [sources.yaml](../sources.yaml).

## Contents

- [How to run them](#how-to-run-them)
- [The audits](#the-audits)
- [Thresholds](#thresholds)
- [Coverage: a page-specific audit](#coverage-a-page-specific-audit)
- [Every audit must be able to fail](#every-audit-must-be-able-to-fail)
- [Limits](#limits)

## How to run them

```python
from drawio.audit import page_audit, faults   # the skill's scripts/ on sys.path

report = page_audit(page)            # page: a drawio.mxfile.Page built with route() and mark()
assert not faults(report), "\n".join(faults(report))
```

`page_audit()` reads what `Page` recorded while building (each solid box's rectangle, every routed polyline, every edge label and the declared layers), so it never parses the XML back.
`layout_audit()` takes those pieces directly for a drawing built another way. `faults()` turns the report into one line per fault, in a fixed order, for a test message or a command line. Geometry is
orthogonal: a run is horizontal or vertical within half a unit.

## The audits

| Key                | Catches                                           | How it decides                                                                                                              |
| ------------------ | ------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------- |
| `box_crossings`    | An arrow drawn through a box                      | A run overlaps a solid box's inside, shrunk by a 2-unit inset (touching the border is fine); the arrow's own ends and the   |
|                    |                                                   |   ids in its `ignore` set (such as the group holding both ends) are exempt                                                  |
| `diagonal`         | A slanted run in an orthogonal drawing            | A run that moves more than half a unit in both x and y                                                                      |
| `shared_runs`      | Two thick arrows drawn as one                     | Two runs of different thick arrows lie on one line (within 3 units) and overlap by more than 2 units                        |
| `short_heads`      | An arrowhead with no straight run before its box  | The last run is shorter than the head room for the arrow's class (thick 24, thin 22), with half a unit tolerance            |
| `labels_on_arrows` | A count or step label sitting on another arrow    | Any run of an arrow other than the label's owner touches the label's rectangle                                              |
| `label_overlaps`   | Two labels on top of each other                   | Two label rectangles overlap (touching does not count)                                                                      |
| `arc_clashes`      | Two crossing hops merging into a double twist     | On one run of an arrow that hops (`jump` above 0), two neighbouring crossings are closer than `2 * jump + ARC_GAP`          |
| `missing_layers`   | A cell or route naming a layer that does          | A `parent` in the cell XML, or a route's or label's layer, is not `0`, `1` or a declared layer                              |
|                    |   not exist                                       |                                                                                                                             |

The audits apply to both thick and thin arrows except `shared_runs`, which checks thick arrows only (thin arrows inside a group may meet on purpose at a shared box) [C-D28].

## Thresholds

| Threshold            | Value                        | Source of the number                                                                                                       |
| -------------------- | ---------------------------- | -------------------------------------------------------------------------------------------------------------------------- |
| `HEAD_ROOM["thick"]` | 24                           | Below this an arrowhead on a thick line (stroke width 4, end size 9, on the overview) looks cramped against its box                                       |
| `HEAD_ROOM["thin"]`  | 22                           | The same for thin arrows                                                                                                   |
| `ARC_GAP`            | 6                            | Extra room two hops need beyond their arcs; `jumpSize` is a hop's full width, so hops closer than `2 * jumpSize + 6` merge |
| Box inset            | 2                            | How far inside a box a run must reach to count as crossing it                                                              |
| Collinear tolerance  | 3 apart, more than 2 overlap | When two runs count as one line                                                                                            |
| Diagonal tolerance   | 0.5                          | A run off-axis by more than this in both directions                                                                        |

The head room and arc gap were set from visual review of real exports (UNC, 2026-10-19), not from draw.io documentation [C-D15] [C-D28]. `jumpSize` being the hop's full width is documented ("Jump
width at crossings", default 6) [C-D14]. Pass `head_room={...}` to `page_audit()` to tighten or relax the head room for a drawing with different line widths, and say why in the generator.

The renderer's own spacing constants are chosen to clear these thresholds with margin: overview thick arrows keep `OV_MIN_HEAD` (34) before a box, thin arrows `OV_MIN_THIN` (22), and hops are 7
(thick) and 4 (thin), needing 20 and 14 between crossings ([layout-and-routing.md](layout-and-routing.md)).

## Coverage: a page-specific audit

Some checks belong to one page's purpose, not to geometry. UNC's End-to-end page must touch every component; `e2e_untouched()` in `scripts/flowmap/e2e.py` lists components that no path or connector
reaches, and a test asserts the list is empty. Write such checks beside the page that needs them, with the same rule: a test that feeds a bad case and sees it reported.

## Every audit must be able to fail

An audit that never fails proves nothing. Each audit has a test that feeds it a deliberately bad drawing and asserts the fault is reported, beside a test that a clean route passes [C-D29]. In this pack's `tests/test_layout_rules.py` (moved from UNC's `tests/test_flows_drawio.py`, 2026-10-19) these are: a clean route passes; box crossing; diagonal run; shared run; short head; label on another arrow and overlapping labels; arc clash (and arc clash on thin
arrows); missing layer; untouched component. The real map's Overview and End-to-end pages are then checked by "passes every audit" tests.

When adding an audit:

1. Write the failing-case test first and watch it fail for the right reason.
2. Add the key to `AUDIT_KEYS`, so `faults()` reports it in order.
3. Run it on every real page the generator draws; fix the layout, not the threshold, unless the threshold itself was wrong (and record why).

When the skill's own `tests/` gains these cases (the scripts are being refactored as this is written), they belong there; until then the UNC tests are the proof.

## Limits

- The audits check geometry the generator recorded. They do not see what draw.io renders: text overflowing a box, a font substitution, a hop drawn where the generator did not expect one. Export and
  look ([export-and-self-review.md](export-and-self-review.md)).
- They assume orthogonal routes; curved or diagonal edges are reported as `diagonal` and otherwise not checked.
- Edges routed by draw.io itself (`Page.edge()`) are not recorded and are not audited.
