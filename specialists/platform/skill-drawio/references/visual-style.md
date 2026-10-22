---
Title: Visual style for generated drawings
Category: skill-reference
Status: current
Authority: Operator rules recorded in UNC (2026-10-19), the renderer's palette and styles, and W3C WCAG 2.2 for contrast; the cited sources win over this summary
Scope: >-
  Colour, contrast, line weight, layers, legends and label weight for draw.io drawings a generator produces, so every arrow family is distinguishable, readable
  and can be hidden
Last reviewed: 2026-10-19
Summary: Distinct colours at 4.5:1 or better on the background, one neutral grey for secondary arrows, one layer per colour or family, legends and bold labels.
---

# Visual style for generated drawings

Rules from UNC's flow-map renderer and the operator's reviews of it, generalised. Claim IDs refer to [sources.yaml](../sources.yaml).

## Contents

- [Colour](#colour)
- [Contrast](#contrast)
- [Line weight and dash](#line-weight-and-dash)
- [One layer per colour or family](#one-layer-per-colour-or-family)
- [Legends](#legends)
- [Labels and text](#labels-and-text)
- [Checklist](#checklist)

## Colour

- **Every primary family gets its own colour**, and no two may share one (operator, 2026-10-19: no two target groups may share a colour) [C-D30]. On UNC's overview a thick arrow takes the colour of
  the group it points into; on the End-to-end page an arrow takes its flow family's colour.
- **Distinct hues, not shades**: blue, green, red, purple, teal, olive, magenta, orange, navy-black, then brown. Brown is kept last because next to orange it reads as the same colour; when a drawing
  needs more colours than the palette has distinct hues, split the drawing or group families rather than adding near-duplicates.
- **One neutral thin grey for every secondary arrow** (UNC: `#4b5563` for arrows inside a group), so no secondary arrow is mistaken for a primary one [C-D30].
- A dot on a box in an arrow's colour marks a box that feeds that arrow; stack several dots down the box's right edge and keep a text margin so they never sit on the label.

UNC's palette (`DISTINCT` in the renderer), with contrast against white computed with the WCAG relative-luminance formula:

| Colour     | Hex       | Contrast on white |
| ---------- | --------- | ----------------- |
| Blue       | `#1f4e9c` | 7.99:1            |
| Green      | `#1b7a3a` | 5.40:1            |
| Red        | `#b3261e` | 6.54:1            |
| Purple     | `#6a3fa0` | 7.42:1            |
| Teal       | `#00707a` | 5.84:1            |
| Olive      | `#4d6b00` | 6.14:1            |
| Magenta    | `#a0306e` | 6.68:1            |
| Orange     | `#b45309` | 5.02:1            |
| Navy-black | `#0f172a` | 17.85:1           |
| Brown      | `#8a5a00` | 5.93:1            |
| Thin grey  | `#4b5563` | 7.56:1            |

## Contrast

Every colour drawn as a line or as text is at least 4.5:1 against the page background (white unless stated) [C-D30]. WCAG 2.2 asks 4.5:1 for normal text and 3:1 for large text and for graphical
objects such as lines and icons; 4.5:1 for every arrow is stricter than WCAG asks for lines, chosen because arrow counts and step numbers are drawn in the arrow's colour and are text [C-D31]. Compute
the ratio, do not judge it by eye, and do not round up (4.499:1 fails).

```python
def contrast(hex_a: str, hex_b: str = "#ffffff") -> float:
    """WCAG 2 contrast ratio between two sRGB colours."""
    def lum(h: str) -> float:
        c = [int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)]
        c = [x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
        return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]
    hi, lo = sorted((lum(hex_a), lum(hex_b)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)
```

A drawing that will also be shown on a dark background needs a second value per colour checked against that background; a project with a light and dark view (UNC's topology pages) records both. A
static draw.io export renders light unless `--theme dark` is passed ([export-and-self-review.md](export-and-self-review.md)).

## Line weight and dash

Weight carries meaning as much as colour does. UNC's choices:

| Arrow                                        | Style                                                             |
| -------------------------------------------- | ----------------------------------------------------------------- |
| Primary (overview group-to-group)            | `strokeWidth=4`, `endArrow=block`, `endSize=9`, hops `jumpSize=7` |
| Flow step (End-to-end)                       | `strokeWidth=2`, block head                                       |
| Secondary (inside a group)                   | `strokeWidth=1.5`, thin grey, `endSize=6`, hops `jumpSize=4`      |
| Dependency connector (touches, does not act) | `strokeWidth=1.25`, `dashed=1;dashPattern=8 4`, oval end          |
| Loop-back on a flow page                     | dashed purple                                                     |

Routed arrows use `edgeStyle=none` with explicit waypoints, so draw.io draws straight runs between the generator's points and adds nothing of its own.

## One layer per colour or family

Put each arrow colour or family in its own draw.io layer, with its labels and dots, so a reader can hide it in the Layers panel (View > Layers, Ctrl+Shift+L or Cmd+Shift+L) and see the rest clearly
[C-D32]. Boxes, groups and legends stay on the base layer. Name layers for what they hold ("Thick: into Nautobot", "Thin: inside groups", a family name).

This also makes the export testable: exporting the base layer alone (`--layers 0`) must show every box with every arrow, count and dot hidden, which proves the layers hold what they claim
([export-and-self-review.md](export-and-self-review.md)).

## Legends

- One legend per encoding: a kind legend for box fills, a colour legend for arrow colours (one swatch per colour, plus the thin grey and the dot), a family legend listing each family's flows.
- Place legends where they do not compete with the drawing (UNC: right of the group grid, the colour legend under the kind legend; the family legend at the bottom of the End-to-end page), and say what
  a number on an arrow means. A count is written `×n` (operator, 2026-10-21), so it never reads as a flow step label such as `4.2`.
- A flow index of clickable boxes (page links, see [file-format.md](file-format.md)) helps on a multi-page file.

> **Learned 2026-10-21** · component symbols on the Overview and End-to-end pages · VERIFIED_PRIMARY · Source: `scripts/flowmap/shapes.py` (`component_shape`, `fit_height`, `person_badge`, `component_shapes_used`), `tests/test_shapes.py` (`ComponentShapeTests`) · Falsifier: a store drawn as a rectangle with `component_shapes` on, or a cylinder with it off
> smc-resiliency's operator asked whether the Overview and End-to-end boxes should take the symbols the flow pages already gave lane heads, and chose
> "yes, default for all". `drawing.look.component_shapes` (default true) draws each box as its lane head's symbol; services stay rectangles. The first
> render failed review: cloud labels spilled out and store labels sat on the cylinder's rim, so outline-heavy symbols are sized for their outline
> (`FIT`: cloud x1.6 + 24 px with centred text, cylinder + 30 px). The person figure went to the bottom right because the Overview's dependency dots
> hold the top right (UNC's operator box). Both pages gained "Shapes on this page" (one column on the Overview's legend column, three on End-to-end), and
> the Overview an index-box legend after the operator noticed the green option boxes had none. Screenshots: `references/screenshots/20261021-component-shapes/`.
>
> ```python
> # scripts/flowmap/shapes.py, skill-drawio, 2026-10-21
> FIT = {
>     "external": ("align=center;verticalAlign=middle;spacingLeft=34;spacingRight=34;spacingTop=10;spacingBottom=10;", 1.6, 24),
>     "stored-data": ("verticalAlign=middle;spacingTop=16;spacingBottom=2;", 1.0, 30),
> }
> def fit_height(comp: dict, profile, height: float) -> float:
>     if not profile.look.get("component_shapes", True):
>         return height
>     _style, factor, extra = FIT.get(lane_shape(comp, profile.kind_shapes), ("", 1.0, 0))
>     return round(height * factor + extra)
> ```

## Labels and text

- Pages of open questions and their choices are **decision pages**, never "options", split by subject where a page would mix unrelated
  questions (operator, 2026-10-22; data-first-diagrams.md, Learned 2026-10-22).
- Two arrows never cross where drawing them in the other order would avoid it (operator, 2026-10-22: "unnecessary overlap for the arrows";
  `look.uncross`, on by default; layout-and-routing.md, Learned 2026-10-22).
- Arrows turn with rounded corners on every page (operator, 2026-10-21: "make the arrows with curves like the overview"; `look.arrow_corners`).
- Box names and arrow labels are bold (operator, 2026-10-19). Labels mix bold field names with plain values; render `**...**` spans as `<b>` everywhere in a line, and test that no literal `**`
  survives into the drawing [C-D30].
- Code paths in a monospace font (`<font face="Courier New">`), with soft breaks so they wrap ([layout-and-routing.md](layout-and-routing.md)).
- Arrow labels sit on a white label background (`labelBackgroundColor=#ffffff`) so a crossing line does not run through the digits.
- Size boxes to their text; a box that is too small for its text is a fault, and so is a group much taller than its content.
  The Overview's flow index boxes follow it too: each is as tall as its wrapped title and status line (operator, 2026-10-22: "box ten and eleven is
  getting a bit tight"; `overview_index.index_height`).
- Keep step boxes wider than tall: long text widens a box (`look.max_aspect`, 0.8) rather than stretching it; rounded shapes use a fixed corner
  radius so a tall box never becomes a pill (operator, 2026-10-21: "some shapes' dimensions need care").
- A box's heading line (a component name, a step title, an option head, a decision title) is drawn at `look.heading_scale` (default 125%) of the box's
  font (operator, 2026-10-21: "text size for the headings in the boxes should be bigger"); mark it with `drawio.mxfile.heading()` so `wrapped_lines()`
  sizes the box for it.

## Checklist

- [ ] No two primary families share a colour; secondary arrows are one neutral grey.
- [ ] Every line and text colour is at least 4.5:1 on its background, computed.
- [ ] Each colour or family has its own layer; base-layer-only export shows boxes with no arrows.
- [ ] A legend for every encoding, including what an arrow's number means.
- [ ] Names and arrow labels bold; no literal Markdown markers in the drawing.

> **Learned 2026-10-21** · page headers and legends · USER_STATED · Source: smc-resiliency operator review, 2026-10-21; `scripts/drawio/mxfile.py` (`HEADER_STYLE`, `header_height`) · Falsifier: an exported page whose header text spills out of its box
> Every page opens with the same boxed header (light grey fill, grey border, font 13, left aligned), never plain floating text: a bold title, a
> blank line, the generation note, a blank line, then one line per item with its name in bold ("**Thick arrows:** ...", "**Layers panel:** ..."),
> and the back link last. The box is sized to its wrapped text (`header_height`) and grows upward from its planned bottom so the layout below does
> not move. Boxing a header exposes overflow plain text hid: export and look after any header change. Every page that colours boxes carries a
> legend for those colours, placed in free space beside the first block (the Options page puts it right of the Decisions taken box).
>
> ```python
> # scripts/flowmap/e2e.py, skill-drawio, 2026-10-21
> head_h = header_height(head, right - MARGIN, 60)   # grows upward from its old bottom, so the layout below stays put
> page.box("e2e-title", label(*head), MARGIN, MARGIN + 60 - head_h, right - MARGIN, head_h,
>          HEADER_STYLE, link="data:page/id,overview")
> ```

> **Learned 2026-10-21** · categories and labels · USER_STATED · Source: smc-resiliency operator review, 2026-10-21 ("why custom is written everywhere") · Falsifier: a project where one value in every flow's category helps a reader
> A field shown on every flow (category in the header and the Overview index) must carry information in that project. A value copied from another
> project (UNC's native/custom split) that is the same everywhere is noise: give the project its own categories (build, config-swap, measurement).

> **Proposed 2026-10-21, adopted the same day (see the next entry)** · shape vocabulary · USER_STATED (asked for a sample) · Source: `references/screenshots/20261021-shape-vocabulary-sample/` · Falsifier: the operator declines it
> Standard flowchart shapes could carry meaning the map already has: terminator (first step, a step with no next), decision (a step with a gate),
> manual operation (a person's step), preparation (set-up), predefined process (a step that runs another flow), delay (timer), stored data
> (store), document (a file written), data in or out (a network transport), external system (cloud), person (actor). Sample drawn by hand-run code;
> the engine does not draw them until the operator decides.

> **Learned 2026-10-21** · shape vocabulary adopted · USER_STATED · Source: smc-resiliency operator, 2026-10-21 (chose all twelve; "the two green shapes are not easily distinguishable"); `scripts/flowmap/shapes.py`, `tests/test_shapes.py` · Falsifier: a page where two meanings share one outline
> Flow pages draw each step as a flowchart symbol derived from the map (`flowmap.shapes.step_shape`: explicit `shape`, gate = decision, `flow`
> = predefined process linked to that page, person actor = manual operation, first or last = terminator, network transport = data in or out,
> else process) and each lane head by kind (`lane_shape`: store = stored data, timer = delay, external = cloud, person = a figure in the corner;
> a component's `shape` wins). Every flow page ends with "Shapes on this page". An outline eats text area: shrink characters per line and grow the
> box (diamond 0.6 and 1.5). On the Options page a decision taken is a **document** (a record), never a rounded box beside rectangles of the same
> colour, which read as one shape; questions and decisions carry a small diamond; pros and cons are notes. Text centred in a box takes no top
> padding meant for top-aligned boxes. The Decisions taken box at the head of the chain is a document too (operator, 2026-10-21), and an arrow leaving
> a document's bottom starts on its wavy edge (`WAVE`, 0.075 of the height above the box bottom at the centre), not at the box's bounding line.
> Screenshots: `references/screenshots/20261021-shapes-adopted/`.
>
> ```python
> # scripts/flowmap/shapes.py (step_shape), skill-drawio, 2026-10-21
> if s.get("shape"):
>     return s["shape"]
> if s.get("gate"):
>     return "decision"
> if s.get("flow"):
>     return "predefined-process"
> if lane_shape(comps[s["actor"]], kind_shapes) == "person":
>     return "manual-operation"
> last = s.get("next") == [] or (k == len(steps) - 1 and "next" not in s)
> if k == 0 or last:
>     return "terminator"
> if any(v.lower() in io_vias for v in s.get("via", [])):
>     return "data-io"
> return "process"
> ```

> **Learned 2026-10-21** · opaque dashed boxes · USER_STATED · Source: smc-resiliency operator, 2026-10-21 ("white background so that I don't see the draw.io grid ... as a standard"); `scripts/flowmap/overview.py` group style; `tests/test_shapes.py` (`OpaqueDashedBoxTests`) · Falsifier: a dashed vertex rendered with `fillColor=none`
> A box drawn with a dashed border (Overview groups, proposed or designed components) always has a fill: white for a container, its kind colour
> for a component. A see-through box shows the editor's grid and reads as unfinished. The test fails on any dashed vertex without a fill.

> **Learned 2026-10-21** · flow page proportions and routing · USER_STATED · Source: smc-resiliency operator review of unified-network-controller's pages, 2026-10-21 ("arrows strangely connected", "unusually tall", "crossing over so many shapes", "cluttered", "nothing stopping it to be wider"); `scripts/flowmap/flow_geometry.py`, `scripts/flowmap/pages.py`, `scripts/flowmap/shapes.py` · Falsifier: an export with an arrow end off a slanted side, a step box with more than two empty lines, a back arrow crossing a step, or a diamond whose text touches its edge
> - **Slanted shapes** (data in or out, manual operation, preparation): pin arrow ends to the box edge (`exitPerimeter=0`, `entryPerimeter=0`);
>   draw.io's projection slides them along the slant to a corner. Diamonds keep the projection.
> - **Proportion over height:** a decision gets a wider column (`DEC_STEP_W` 380) and generous side padding (72), so its text sits inside the
>   diamond; every step box is sized from 38 characters a line at 220 px and font 10 (33 left boxes half empty).
> - **Return arrows** are routed by the engine, not draw.io. The short way first: out of the source's left side a fifth of the way down (clear
>   of the forward arrows' entries), along the source's lane, into the target's top right (bottom right when the target's lane is higher).
>   When a step blocks that path, the long way: down in the source's column, along a band below every lane, up into the target. Either way
>   the route crosses no other step (`flow_geometry._clear`); the label is a text mark on the route.
> - **Long actions** written as clauses joined by "; " are set one clause a line as bullets.

> **Learned 2026-10-22** · action bullets keep bracketed asides whole · VERIFIED_PRIMARY · Source: unified-network-controller flow page review, 2026-10-22; `scripts/flowmap/pages.py` (`action_clauses`), `tests/test_shapes.py` (`ActionClauseTests`) · Falsifier: a step box whose bullet starts or ends inside a bracket
> `look.action_bullets` sets an action of clauses joined by "; " one clause a line. The split ran on every "; ", so "(the operator's click;
> agents never approve)" became two bullets with a broken bracket. It now splits only outside brackets; an unbalanced closing bracket resets
> to depth zero. Four unified-network-controller pages changed (each had a bracketed "; "), smc-resiliency's pages audit clean.
>
> ```python
> # scripts/flowmap/pages.py (skills_stuff, 2026-10-22)
> while i < len(text):
>     if depth == 0 and text.startswith("; ", i):
>         out, cur, i = out + [cur], "", i + 2
>         continue
>     depth = max(0, depth + (text[i] in "([{") - (text[i] in ")]}"))
>     cur, i = cur + text[i], i + 1
> ```
