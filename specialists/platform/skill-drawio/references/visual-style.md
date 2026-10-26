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
- **Distinct hues, not shades**: blue, green, red, purple, teal, olive, magenta, orange, navy-black, then brown. Brown is kept last because next to orange it reads as the same colour. A second ten
  follow (operator, 2026-10-23: "extend the color palette"): chocolate, sky, maroon, pine, fuchsia, ultramarine, mustard, bronze, plum, jade, picked farthest-first by CIEDE2000, each at least
  13.8 from every other colour and the thin grey, above the first ten's closest pair (green and olive, 13.1). Twenty is the ceiling at that bar (the next pick measured 11.9); a drawing that needs more
  than twenty colours repeats them, so split it or group families rather than adding near-duplicates.
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
| Chocolate  | `#572f19` | 11.50:1           |
| Sky        | `#0f7ab3` | 4.71:1            |
| Maroon     | `#71142b` | 11.43:1           |
| Pine       | `#195744` | 8.44:1            |
| Fuchsia    | `#c200c2` | 5.16:1            |
| Ultramarine | `#0000c2` | 11.80:1           |
| Mustard    | `#857700` | 4.53:1            |
| Bronze     | `#574b19` | 8.66:1            |
| Plum       | `#680863` | 11.64:1           |
| Jade       | `#008571` | 4.57:1            |
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
| Primary (overview group-to-group)            | `strokeWidth=4`, `endArrow=classic`, `endSize=9`, hops `jumpSize=7` |
| Flow step (End-to-end)                       | `strokeWidth=2`, classic head                                     |
| Secondary (inside a group)                   | `strokeWidth=1.5`, thin grey, `endSize=6`, hops `jumpSize=4`      |
| Dependency connector (touches, does not act) | `look.connector_width` (1.25), `dashed=1;dashPattern=8 4`, oval end |
| Loop-back on a flow page                     | dashed purple                                                     |

Every arrowhead is draw.io's classic head (`drawio.mxfile.ARROW_HEAD`, `endArrow=classic;endFill=1;`, the skill's default), never the block triangle (operator, 2026-10-23: "use this arrow type, not the
default one. Everywhere"); only the dependency connector keeps its oval end, which marks "not a step".

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
- Every arrow and its label carry a tooltip saying what happens (End-to-end: the step, the steps that stayed in the source, `via`; a dashed
  connector: why the flow needs the component); step boxes and component boxes carry the whole map entry (`flowmap.tips`). On the Overview
  every thin arrow, thick arrow (and its ×n count) and dot lists who needs whom, with each needed health check (operator, 2026-10-23). A tooltip only adds:
  exported PNG and PDF have none, so must-read facts stay in boxes and notes (operator, 2026-10-23).
- draw.io tags on generated cells, for the Tags dialog (select, hide or show across layers): `flow-<id>`, `family-<id>`, `step-arrow`,
  `connector`, `back-arrow`, `kind-<kind>`, `group-<group>`, `gate`, `decision`, `fails`, `runs-flow-<id>` (`drawio.cell`; operator, 2026-10-23).
- Every generated cell is frozen (`drawio.mxfile.FROZEN`: `movable`, `resizable`, `rotatable`, `bendable`, `editable`, `deletable` all 0):
  nothing is dragged, resized, re-bent, retyped or deleted by mistake, yet every box and arrow stays clickable and hoverable; layers are never
  locked, which would block clicks (operator, 2026-10-23).
- Tooltips are HTML (draw.io sanitises and renders them): a bold title, bold field names, bullets for several items, and commands, paths,
  file names and snake_case names in code font (`flowmap.tips.tip_html`, `code_spans`; operator, 2026-10-23). Paths, file names, flags and
  snake_case are found automatically; a command such as `tsh ssh` or `apt-get update` is not, so the map marks it with backticks (quote
  a YAML value that starts with one); boxes and notes honour the same backticks (operator, 2026-10-23: "apt get or tsh ssh" had no format).
- End-to-end labels read x.y: flow x, step y. x.1 runs from the component the flow `runs_on`; a step done by the same component as the step
  before draws no arrow and is named in the next arrow's tooltip. `look.e2e_layers: flow` gives each flow its own colour and layer (default
  `family`); `look.connector_width` sets the dashed connectors' stroke (default 1.25, 2 for bold) (operator, 2026-10-23).
- `look.e2e_family_pages: true` keeps the full End-to-end page and adds one page per family after it (`flowmap.e2e_family`): only that
  family's flows and the boxes they touch, the whole map's flow numbers on every x.y, colours taken in the page's own order so none repeats,
  unused tier columns dropped, ids renamed `e2f-<family>-`; the Overview index links each one. It is the exportable form of View > Tags
  `family-<id>` (operator, 2026-10-23: "leave the existing end to end as it is and add more end to end pages").
- `look.e2e_family_colours` (with `e2e_layers: flow`) picks the family pages' colours: `page` (default) restarts the palette on each page,
  so none repeats; `flow` keeps each flow's full-page colour on every page, so a flow is the same colour everywhere and two flows 20 apart
  share one when a family holds both (operator, 2026-10-26: "switch to one colour per flow everywhere").
- A family with `own_page: true` (in `drawing.families`) tells a story of its own, for example one change run through a generic role: its
  flows are drawn only on its own End-to-end page (drawn even with `e2e_family_pages` off) and never on the full one, they are numbered from
  1 with colours of their own, and their tabs and Overview index rows carry the family's `prefix` ("PHP 1. Plan"; default the family name).
  The full page's shared flows are numbered among themselves, so adding such a family renumbers nothing, and the full page drops a tier
  column only such a family uses (`flowmap.map_parts`, `narrowed`; operator,
  2026-10-26: "it wont be added to the e2e flow", "it should not be starting from 5.x").
- `flow_pages: false` on a family drops its flows' own pages and Overview index rows; the family is read on its End-to-end page only
  (operator, 2026-10-26: "Don't need individual PHP pages").
- `look.e2e_step_total` adds each flow's step count n to its End-to-end arrow labels and legend rows, so a reader knows how long a flow is
  and that a skipped number is a step done by the same component, not a missing arrow: `sub` (x.y with n as a subscript; `true` means
  `sub`), `sup` or `slash` (x.y/n). `look.e2e_label_font` sets the label size (default 10); the label box is sized from the text
  (operator, 2026-10-26: "x.y/max_y", then "subscript or superscript instead", and labels at 12).
- `look.e2e_loops` draws a step done by the same component as the step before as a loop on that box, labelled x.y (x.y–z for a run),
  Turing-machine style: on the box's top or bottom edge, whichever had more clear room once the page was laid out, packed by label width
  and overflowing to the other edge; a gap is widened only by the room an edge lacks (operator, 2026-10-26: "create a 14.3 as a loop on
  the same box", "the top or the bottom, depending where more space is available ... case by case").
- `look.click_isolate` (true, or the opacity of the rest) makes one click show a colour alone and a second click show everything: on the
  End-to-end pages a step arrow, its label, a dashed connector or a legend row (other rows dim too); on the Overview a thick arrow, its
  count, a dot, a thin arrow or a legend row. A click on another colour switches in one click; there is no "Show all" button. Nothing is
  saved: the file never counts as changed. The clickable layers are locked (the editor runs a link on a click only there).
  `look.lock_base_layer` locks every page's background layer; `look.e2e_tab` names the End-to-end tabs ("E2E flow", "E2E: <family>")
  (operator, 2026-10-26: "make it a toggle ... with a single step", "clicking on dashed lines should also do the same", "do the same for
  the overview legend arrow colors", "make the background layer locked on all the pages", "change End-to-end to E2E ... in the tab names").
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

> **Learned 2026-10-23** · decision branch labels · VERIFIED_PRIMARY · Source: ansible-wifi smc_change flow map render; scripts/flowmap/routing.py:branch_label ·
> Falsifier: a step with `shape: decision` and two `next` targets rendered with bare step numbers on its arrows
> A step drawn as a decision through `shape: decision` (no `gate`) used to get bare numbers on its branches, its `when` cases dropped. Every branch
> out of a diamond now says why it is taken (operator, 2026-10-23): its `when` case, else Yes/No for two branches. Screenshot:
> `references/screenshots/20261023-decision-branch-labels/`.
>
> ```python
> nxt = step.get("next") or []
> decision = step.get("gate") or step.get("shape") == "decision"
> if not decision or len(nxt) < 2 or look.get("branch_labels", "yes-no") == "off":
>     return str(number), PLAIN
> case = (step.get("when") or {}).get(target)
> ```

> **Learned 2026-10-23** · a flag with a value splits its code span · VERIFIED_PRIMARY · Source: smc-resiliency flow map render (commit 602c73c), tooltip of
> component Activation step; scripts/flowmap/tips.py:CODEISH (skills_stuff bfd150c) · Falsifier: a tooltip that sets `--noexec=false` as one code span
> `code_spans()` matches a flag as `--?[a-z][\w-]*` and stops at `=`, so `--noexec=false` renders as `--noexec` in code font and `=false` plain (also
> `--level=24.04-20261020`). Open, not fixed: letting the flag alternative take `(?:=[\w.<>/-]+)?` changes every consumer's drawing, so the fix is
> released with a re-render of each map. Until then a map can mark the whole flag with backticks. Screenshot: none, tooltips are not exported; the excerpt is the output.
>
> ```python
> # scripts/flowmap/tips.py (skills_stuff bfd150c)
> CODEISH = re.compile(r"(?<![\w`])(--?[a-z][\w-]*|[\w.<>*-]*/[\w./<>*-]+|...")
> code_spans("refreshes with --noexec=false, then")  # -> 'refreshes with `--noexec`=false, then'
> ```

> **Learned 2026-10-23** · palette extended to twenty hues · VERIFIED_PRIMARY · Source: `scripts/flowmap/profile.py` `DISTINCT`, `scripts/palette_check.py`
> (skills_stuff 9166fcb and this entry's commit); screenshot `references/screenshots/20261023-palette-export/` · Falsifier: two of the twenty read as one
> colour in a legend review, or `just palette-check` reporting a pair under 13.1
> The operator asked to extend the palette after unified-network-controller's 31 flows cycled ten colours. Distance is measured (CIEDE2000), not
> judged: the first ten's closest pair is green and olive at 13.1, so a new hue had to beat that and reach 4.5:1 on white. Farthest-first picks from a
> grid of dark hues gave ten at 13.8 or more; the eleventh measured 11.9, so twenty is the ceiling. Appending kept every drawing of ten or fewer
> families byte-identical (the shop example unchanged). `just palette-check` measures a palette and `--suggest N` picks more.
>
> ```python
> # scripts/palette_check.py (skills_stuff, 2026-10-23)
> def suggest(palette, avoid, n):
>     chosen, picks, pool = list(palette) + list(avoid), [], candidates()
>     for _ in range(n):
>         best = max(pool, key=lambda c: min(de2000(c, x) for x in chosen))
>         near = min(chosen, key=lambda x: de2000(best, x))
>         picks.append((best, de2000(best, near), near))
>         chosen.append(best)
>     return picks
> ```

> **Learned 2026-10-23** · End-to-end family pages · VERIFIED_PRIMARY · Source: `scripts/flowmap/e2e_family.py`, `tests/test_e2e_family.py`;
> unified-network-controller render; screenshots `references/screenshots/20261023-e2e-family-pages/` · Falsifier: a family page whose x.y
> numbers differ from the full page's, or a file with a cell id used on two pages
> unified-network-controller's End-to-end page held 31 flows and 73 boxes (5,534 x 8,622 px). Splitting by boxes does not work there: the best
> two-page split still put five hub boxes (Nautobot web, the Celery worker, apn-unc01, the SMC, the operator) on both pages and left 23 flows on
> one. Splitting by family does: five extra pages of 4 to 11 flows and 17 to 37 boxes (2,000 to 3,600 px, whole at export scale 1), the full
> page byte-identical. One engine draws both: the family page is the same EndToEnd built on a part of the map, given the whole map's numbers,
> and its ids are renamed when written, since draw.io ids must be unique in the file.
>
> ```python
> # scripts/flowmap/e2e_family.py (skills_stuff, 2026-10-23)
> numbers = {f["id"]: i for i, f in enumerate(data["flows"], 1)}
> e2e = EndToEnd(part, narrowed(profile, part["components"]), {f["id"]: numbers[f["id"]] for f in part["flows"]})
> page = e2e.page(f"end-to-end-{fam}", f"End-to-end: {name}")
> page.rename = ("e2e-", f"e2f-{fam}-")
> ```


> **Learned 2026-10-26** · family page colours by flow · VERIFIED_PRIMARY · Source: `scripts/flowmap/tips.py` `e2e_groups`,
> `tests/test_e2e_family.py` `test_flow_colours_match_the_full_page`; unified-network-controller render; screenshot
> `references/screenshots/20261026-e2e-family-colours/` · Falsifier: a family page under `e2e_family_colours: flow` whose flow colour differs
> from that flow's colour on the full End-to-end page
> Restarting the palette on each family page avoids repeats but gives one flow a different colour on each page; the operator chose one colour
> per flow everywhere (2026-10-26). With 20 colours, flows n and n+20 share one, so a family holding both repeats it: in
> unified-network-controller's 31 flows, Monitoring (7, 27) and Onboarding (8 and 28, 9 and 29); the x.y numbers still tell them apart.
> Count a forced repeat per family from the numbers (n mod 20) before predicting it: the first prediction named only Onboarding.
>
> ```python
> # scripts/flowmap/tips.py e2e_groups (skills_stuff, 2026-10-26)
> whole = numbers and profile.look.get("e2e_family_colours", "page") == "flow"   # a part keeps each flow's full-page colour
> groups = tuple((f["id"], f"{num[f['id']]}. {f['title']}", DISTINCT[((num[f["id"]] if whole else i) - 1) % len(DISTINCT)], (f["title"],))
>                for i, f in enumerate(flows, 1))
> ```

> **Learned 2026-10-26** · step totals and label size on the End-to-end page · VERIFIED_PRIMARY · Source: `scripts/flowmap/step_labels.py`
> `e2e_label_size`, `label_spot`, `label_spots`, `step_label`; `tests/test_e2e_family.py` `StepTotals`;
> unified-network-controller render; screenshots `references/screenshots/20261026-e2e-step-totals/` · Falsifier: a page with
> `e2e_step_total: sub` at font 12 whose audit reports a label on another arrow where the same map at x.y and font 10 is clean
> A label is placed only where it touches no other run, and End-to-end tracks are 24 px apart (E2E_SP), so a label on a vertical run must
> be under about 48 px wide. `x.y/n` at 12 pt is wider (`10.13/19` about 55 px with padding) and left 16 labels on other arrows in
> unified-network-controller; a subscript n at 0.75 of the font, with 2 px padding a side, keeps the widest at 46 px and every page clean.
> Size labels from the font's advance widths (Helvetica bold: digit 0.556 em, `.` and `/` 0.278 em), not a flat factor per character,
> which overstated `10.13/19` by 20 px. Where the nine fixed spots on a run fail, a scan every 6 px along every run (any run that holds the
> label with 8 px to spare) finds room; the default drawing is byte-identical because the scan runs only after the fixed spots fail.
>
> ```python
> # scripts/flowmap/step_labels.py (skills_stuff, 2026-10-26)
> def label_width(xy: str, n: str, font: float, total: str | None) -> float:
>     if total == "slash":
>         return em_width(f"{xy}/{n}") * font
>     return (em_width(xy) + (em_width(n) * SCRIPT_SCALE if total else 0)) * font
> # step_label
> if style in ("sub", "sup"):
>     return f"<b>{xy}<{style}>{n}</{style}></b>"
> ```

> **Superseded 2026-10-26** by the Learned entry "click toggle without changing the file" below (two clicks and a reset button, and a
> lock on the cell rather than its layer, replaced the same day).
> **Learned 2026-10-26** · click a flow to see it alone · VERIFIED_PRIMARY · Source: draw.io 32.5.5 bundle (`app.asar`
> `drawio/src/main/webapp/js/app.min.js`: action names `"wait fadeIn fadeOut fadeTo opacity ..."`, `null!=x.opacity&&null!=x.opacity.value&&
> Graph.setOpacityForNodes(...)`), jgraph/drawio v32.5.5 `js/viewer-static.min.js`; drawio.com/docs/reference/animation-actions-json;
> `scripts/flowmap/isolate.py`; `tests/test_e2e_family.py` `ClickIsolate`; screenshots `references/screenshots/20261026-e2e-click-isolate/`
> · Falsifier: a click on an arrow in draw.io's viewer that leaves another flow's arrow at opacity 1
> A `data:action/json` link `{"actions":[{"opacity":{"tags":[...],"tagsMatch":"or","value":0.15}},{"opacity":{"tags":["flow-<id>"],"value":1},
> "immediate":true}]}` dims by tag and restores one flow; tags reach every cell kind, so the page needs only a `box` tag on components.
> The docs name the action "Set Opacity" but not its JSON key; the key is `opacity` with `value`, read from the installed bundle. Tested in
> the viewer of the same version under headless Edge (Playwright): a label click set the clicked flow's arrows and boxes to 1 and others to
> 0.15, a legend row did the same, "Show all flows" set all back to 1. In the desktop editor a click runs a link directly only on a locked
> cell (hence `locked=1`); that path is not yet tested by hand. The effect is transient (never saved); exports stay static.
>
> ```python
> # scripts/flowmap/isolate.py (skills_stuff, 2026-10-26)
> def isolate_link(tag: str, dim: float) -> str:
>     return _link([{"opacity": {"tags": list(DIMMED_TAGS), "tagsMatch": "or", "value": dim}},
>                   {"opacity": {"tags": [tag], "value": 1}, "immediate": True}])
> ```

> **Learned 2026-10-26** · click toggle without changing the file · VERIFIED_PRIMARY · Source: draw.io 32.5.5 `app.asar` app.min.js
> (`Graph.nextToggleStyleValue`, `toggleCellStylesTransient`, `toggleCellStyleValues`, `executeCustomActions`, the Graph click handler
> `isCellLocked(this.getLayerForCell(...))`), jgraph/drawio v32.5.5 `js/viewer-static.min.js`; `scripts/flowmap/isolate.py`;
> `tests/test_e2e_family.py` `ClickIsolate`; screenshots `references/screenshots/20261026-click-toggle/` · Falsifier: a click sequence in
> draw.io 32.5.5 where a second click on the same colour leaves cells dimmed, or a click that marks the file changed
> Three findings from the installed code. (1) A link clicked on a cell runs with that cell passed, and then every action without its own
> `"transient"` is a saved model change (the file counts as modified); mark each action `"transient": true`. A link run without a cell
> (a page animation) is transient by default, which hid this in a first test. (2) A transient `toggleStyle` decides per cell: a cell
> holding the value returns to the default, any other takes the value. Giving each colour its own dim value (15.001, 15.002, ..., the same
> to the eye) makes one stateless link toggle its colour and switch from another colour in one click; no marker cells are needed. A
> saved `toggleStyle` decides once from the first selected cell instead, which toggles too, but changes the file. (3) In the editor a
> click runs a link directly only when the cell's layer is locked; `locked=1` on the cell itself only stops selection, and the editor
> shows the link in a hint to click instead. Measured in the viewer under headless Edge: example and unified-network-controller E2E and
> Overview pages, click, click again, switch, all as intended; the model kept no opacity.
>
> ```python
> # scripts/flowmap/isolate.py isolate_link (skills_stuff, 2026-10-26)
> value, keys = f"{dim * 100:.0f}.{index + 1:03d}", ("opacity", "textOpacity")
> actions = [{"toggleStyle": {"tags": list(dimmed), "tagsMatch": "or", "key": k, "value": value, "defaultValue": "100", "transient": True}}
>            for k in keys]
> actions += [{"style": {"tags": [keep], "key": k, "value": "100", "transient": True}} for k in keys]
> ```

> **Learned 2026-10-26** · self-loops on the End-to-end page · VERIFIED_PRIMARY · Source: `scripts/flowmap/loops.py`
> (`loop_runs`, `_room`, `plan_loops`, `draw_loops`), `scripts/flowmap/e2e_grid.py` `loop_reserve`; `tests/test_e2e_family.py` `Loops`;
> unified-network-controller render; screenshots `references/screenshots/20261026-e2e-loops/` · Falsifier: a page with loops on whose
> audit reports a fault, or a box whose loops sit on the edge that had less room
> Arrows meet End-to-end boxes only on their sides, so the sides hold a port every 24 px and are 34 px from the first track, while the top
> and bottom are free: in unified-network-controller the looped boxes had 34 to 1,686 px clear above or below. Measuring that room after
> the first layout and widening a gap only by an edge's shortfall placed 21 loops (27 steps) with the full page 22 px taller and four of
> six pages unchanged in size. A loop is 24 px tall so its last run passes the thick head-room audit, and is drawn before the arrow
> labels so they keep clear of it. A draw.io edge with the same source and target and explicit waypoints renders as the loop.
>
> ```python
> # scripts/flowmap/loops.py plan_loops (skills_stuff, 2026-10-26)
> up, down = _room(e2e, comp, taken)
> edges = ("top", "bottom") if up >= down else ("bottom", "top")
> for loop in by_comp[comp]:
>     loop.edge = edges[0] if used[edges[0]] + loop.width <= E2E_BW - 2 * LOOP_PAD else edges[1]
>     used[loop.edge] += loop.width
> ```

> **Learned 2026-10-26** · loops keep clear of headings · VERIFIED_PRIMARY · Source: `scripts/flowmap/loops.py` `_room`,
> `title_spans`, `scripts/flowmap/e2e_grid.py` `E2E_TIER_HEAD`, `E2E_BAND_HEAD`; `tests/test_e2e_family.py`
> `test_loops_keep_clear_of_headings`; smc-resiliency render; screenshots `references/screenshots/20261026-loop-heading-clearance/` ·
> Falsifier: a loop or its label drawn over a tier heading or the band heading
> The room above a top-row box was measured to the column's top, but the tier heading text sits inside that room (4 to 44 px below it),
> so a box with clear lines above put its loop on the heading: smc-resiliency's x86 family page drew 8.8 over "On the SMC", and the page
> audit passed it (it checks arrows, boxes and labels, not heading text). Headings are now obstacles like boxes; the band heading in the
> first column too. The test repeats every step a top-row box does, so each carries a loop, and fails without the fix ("4.1 on
> report-timer: 506-548 over heading 512-542"). UNC's and the example's drawings stayed byte-identical; only the x86 page moved its loop below.
>
> ```python
> # scripts/flowmap/loops.py _room (skills_stuff, 2026-10-26)
> for y0, y1 in title_spans(grid, c):   # a top-row box's room ends at its tier heading, not the column's top
>     up = min(up, top - y1) if y1 <= top else up
>     down = min(down, y0 - top - h) if y0 >= top + h else down
> ```

> **Learned 2026-10-26** · a change on a page of its own · VERIFIED_PRIMARY · Source: `scripts/flowmap/map_parts.py` (`shared_part`,
> `flow_numbers`, `flow_labels`), `scripts/flowmap/e2e_family.py` `family_pages`; `tests/test_own_page.py`; ansible-wifi smc_change render;
> screenshots `references/screenshots/20261026-own-page/` · Falsifier: a map with an `own_page` family whose full End-to-end page carries a
> cell tagged with one of its flows, or whose own page numbers a flow other than 1..n
> A role that runs many changes (ansible-wifi's smc_change) wants one page per change, but a family page reuses the whole map's numbers and
> the full page draws every flow, so the first PHP page read "5.1" and its flow also crowded the shared page. Leaving the family's flows out of
> the full page's part, and dropping only the components no shared flow touches, keeps that page whole; numbering per family keeps every
> page readable alone. The operator then asked for phases of one run as separate flows (1 Plan ... 5 Prove), not one long flow.
>
> ```python
> # scripts/flowmap/map_parts.py (skills_stuff, 2026-10-26)
> for f in data["flows"]:
>     fam = flow_family(f, profile) if profile.own_families else ""
>     key = fam if fam in profile.own_families else ""
>     seen[key] = seen.get(key, 0) + 1
>     out[f["id"]] = seen[key]
> # shared_part: the full page's flows and components
> kept = set(c["id"] for c in flows_part(data, shared)["components"])
> only_own = set(c["id"] for c in flows_part(data, own)["components"]) - kept
> ```

> **Learned 2026-10-26** · thin arrows on one line, and legend text that never wrapped · VERIFIED_PRIMARY · Source: `scripts/drawio/audit.py`
> `shared_runs`, `scripts/flowmap/overview.py` `_thin_routes`, `scripts/flowmap/step_labels.py` `legend_fit`; `tests/test_own_page.py`
> `ThinSharedRuns` (proved red with the nudge disabled) · Falsifier: an Overview whose thin arrows with no end in common share a run while
> the audit reports clean, or an End-to-end legend line wider than its box
> The shared-run audit checked thick arrows only, so an Overview thin arrow that dropped down another box's exit line (a box stacked straight
> above the other's target, both at the centre fraction) passed as clean; the operator saw it in the export. Thin arrows are now checked
> unless they share an end (a fan-out may share its first run), and an entry that would land on another exit line moves half a slot. The
> End-to-end legend's reading line had no `whiteSpace=wrap`: draw.io laid it out on one line about 2,400 px wide whatever its box, which
> showed only on a narrow family page; it now wraps when the estimate needs more than one line, so wide pages are byte-identical.
>
> ```python
> # scripts/flowmap/overview.py _thin_routes (skills_stuff, 2026-10-26)
> if any(abs(pos[ch[-1]][0] + OV_BW * fi - x) < 3 for k, x in exits.items() if k != id(ch)):
>     fi += 1 / (2 * (len(ins[ch[-1]]) + 1))   # its drop would run down another box's exit line: enter half a slot right
> ```

> **Learned 2026-10-26** · joint moves in the End-to-end search · VERIFIED_PRIMARY · Source: `scripts/flowmap/crossing_search.py`
> (`improve`, `port_and_tracks`, `moved_next_to`); `tests/test_crossing_search.py` (fixture `tests/fixtures/crossing_search.yaml`, proved
> red with the worse run kept); screenshots `references/screenshots/20261026-joint-moves/` · Falsifier: a page whose crossings after
> `improve` exceed the plain search's, or an out-and-back pair left crossing where a port swap plus one track move clears it
> The search kept one swap at a time, only when crossings dropped. An arrow from box A to B and the next step back from B to A crossed on
> the operator's PHP page: clearing it needs their ports on A swapped and one vertical track moved, and either alone adds a crossing, so
> the search never got there (operator, 2026-10-26: "improve the logic in the skill, not like a manual handwork"). What did not work: swapping
> the two tracks outright (jumped over three dashed tracks, +13 crossings); running joint moves inside the plain search (the shop example
> rose 11 -> 13: a greedy path to a worse end); judging every candidate on the whole page (unified-network-controller 4 s -> 81 s). What
> did: move one track beside the other with the rest in order, count only the links whose track or port moved (their crossings against
> every link are the page's whole change), check spacing only on the chosen move, try only a pair that crosses itself, and run the plain
> and the joint search from one start, keeping the one with fewer crossings. Measured: smc_change E2E 72 -> 24, PHP 29 -> 20,
> unified-network-controller's 31-flow page 4,177 -> 3,689 (render 4 s -> about 18 s), smc-resiliency p5 671 -> 528; shop byte-identical.
>
> ```python
> # scripts/flowmap/crossing_search.py improve (skills_stuff, 2026-10-26)
> for joint in (False, True):
>     grid.vslot, grid.gslot, grid.pools = deepcopy(start)
>     grid._refresh(every)
>     _search(grid, joint)
>     results.append((grid._crossings(every), joint, deepcopy((grid.vslot, grid.gslot, grid.pools))))
> _n, _joint, best = min(results, key=lambda r: (r[0], r[1]))   # the plain run on a tie: a page no joint move helps is unchanged
> ```
