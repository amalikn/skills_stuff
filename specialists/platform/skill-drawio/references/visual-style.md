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
  a number on an arrow means.
- A flow index of clickable boxes (page links, see [file-format.md](file-format.md)) helps on a multi-page file.

## Labels and text

- Box names and arrow labels are bold (operator, 2026-10-19). Labels mix bold field names with plain values; render `**...**` spans as `<b>` everywhere in a line, and test that no literal `**`
  survives into the drawing [C-D30].
- Code paths in a monospace font (`<font face="Courier New">`), with soft breaks so they wrap ([layout-and-routing.md](layout-and-routing.md)).
- Arrow labels sit on a white label background (`labelBackgroundColor=#ffffff`) so a crossing line does not run through the digits.
- Size boxes to their text; a box that is too small for its text is a fault, and so is a group much taller than its content.

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

> **Proposed 2026-10-21, not decided** · shape vocabulary · USER_STATED (asked for a sample) · Source: `references/screenshots/20261021-shape-vocabulary-sample/` · Falsifier: the operator declines it
> Standard flowchart shapes could carry meaning the map already has: terminator (first step, a step with no next), decision (a step with a gate),
> manual operation (a person's step), preparation (set-up), predefined process (a step that runs another flow), delay (timer), stored data
> (store), document (a file written), data in or out (a network transport), external system (cloud), person (actor). Sample drawn by hand-run code;
> the engine does not draw them until the operator decides.

