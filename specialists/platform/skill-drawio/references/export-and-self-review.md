---
Title: Export and self-review
Category: skill-reference
Status: current
Authority: >-
  The draw.io desktop command-line help (32.5.5, captured 2026-10-19), exports run against it the same day, macOS sips help, and the operator's
  self-review rule; the captured help wins over this summary
Scope: >-
  Exporting draw.io pages to PNG from the desktop command line (page, layers, scale, timeout), cropping exports for zoomed review, and the self-review loop every
  rendered drawing passes before it is shown to the operator
Last reviewed: 2026-10-19
Summary: draw.io desktop CLI export flags verified on 32.5.5, always run under a timeout, then a self-review loop of export, crop, trace, fix and re-render.
---

# Export and self-review

Claim IDs refer to [sources.yaml](../sources.yaml). The CLI help is copied verbatim in
[documents/drawio-sources-20261019/drawio-desktop-cli-help-32.5.5.txt](../documents/drawio-sources-20261019/drawio-desktop-cli-help-32.5.5.txt).

## Contents

- [The command line](#the-command-line)
- [Flags that matter](#flags-that-matter)
- [Run it under a timeout](#run-it-under-a-timeout)
- [Zoomed crops with sips](#zoomed-crops-with-sips)
- [The self-review loop](#the-self-review-loop)
- [What to look for](#what-to-look-for)

## The command line

On macOS the desktop app's binary doubles as the CLI:

```bash
/Applications/draw.io.app/Contents/MacOS/draw.io \
  -x -f png -p 2 -o out/page2.png \
  docs/diagrams/system.drawio
```

`--help` and `--version` are read only; run `--help` first on a new machine and compare it with the copy in `documents/` [C-D17]. Version 32.5.5 was installed on 2026-10-19 (32.4.1 had been observed
earlier the same day in UNC), see [compatibility.yaml](../compatibility.yaml).

## Flags that matter

| Flag                      | Meaning (32.5.5 help)                                                | Notes                                                                     |
| ------------------------- | -------------------------------------------------------------------- | ------------------------------------------------------------------------- |
| `-x`, `--export`          | Export the input files or folders                                    | Required for any export                                                   |
| `-f`, `--format`          | `pdf`, `png`, `jpg`, `svg`, `xml`, `html`                            | Ignored when `-o` has an extension                                        |
| `-o`, `--output`          | Output file or folder                                                | Without it, the input name with the format's extension                    |
| `-p`, `--page-index`      | Selects one page, **1-based**                                        | Without it, an image export takes the first page only [C-D17]             |
| `-l`, `--layers`          | Comma-separated **layer indexes** to export, all pages               | Index 0 is the base layer (cell `1`); others follow in file order [C-D18] |
| `-s`, `--scale`           | Scales the diagram size                                              | `-s 2` doubled the image (284 x 44 to 565 x 85)                           |
| `--width`, `--height`     | Fit the output into a size, keeping the aspect ratio                 |                                                                           |
| `-b`, `--border`          | Border width around the diagram (default 0)                          | Exports observed 2 px larger than the content each way                    |
| `--size`                  | `diagram` (default, crops to content) or `page`                      | For png, jpg and svg                                                      |
| `--crop`                  | Crops **PDF** to diagram size                                        | Not for PNG; PNG is already cropped by `--size diagram` [C-D19]           |
| `-t`, `--transparent`     | Transparent background for PNG and SVG                               | Avoid for review images                                                   |
| `--theme`                 | `dark`, `light`, `auto` (default)                                    | `auto` renders PNG light                                                  |
| `--timeout`               | Fail one file's export after that many seconds (default 0, no limit) | Per file, inside the app [C-D19]                                          |
| `-u`, `--uncompressed`    | Uncompressed XML output (xml and svg only)                           |                                                                           |
| `-a`, `--all-pages`       | All pages (pdf and html only)                                        | For PNG, loop over `-p`                                                   |
| `--layout`, `--normalize` | Run a layout or repair the model on open                             | Never on a generated drawing: they move what the generator placed         |

Exercised on 2026-10-19 with 32.5.5 against a two-page, two-layer scratch file: no `-p` exported page 1; `-p 2` exported page 2; `--layers 0` exported page 1 with the arrow (on the second layer)
hidden; `-s 2` doubled the pixel size [C-D17] [C-D18].

Static export does not route around shapes, so every arrow in a drawing meant for export needs waypoints ([layout-and-routing.md](layout-and-routing.md)) [C-D16].

## Run it under a timeout

The desktop CLI starts an Electron app; it can hang (a first-run prompt, an update check, a file it cannot parse). Always run it from code with a subprocess timeout, and treat a timeout as a failure
to report, not a reason to retry silently [C-D20]. `--timeout` limits each file's export inside the app; it does not cover start-up, so keep the outer timeout too. Pass `--disable-update` in automated
runs to keep the updater out of the way.

```python
import subprocess

DRAWIO = "/Applications/draw.io.app/Contents/MacOS/draw.io"

def export_png(src: str, out: str, page: int, layers: str | None = None, scale: float = 1.0, timeout: float = 120) -> None:
    """Export one page (1-based) of a .drawio file to PNG; raise on failure or timeout."""
    cmd = [DRAWIO, "-x", "-f", "png", "-p", str(page), "-s", str(scale), "--disable-update", "-o", out]
    if layers is not None:
        cmd += ["--layers", layers]
    subprocess.run([*cmd, src], check=True, timeout=timeout, capture_output=True)
```

Budget: one small page took 3.5 s with this function (32.5.5, `--disable-update`, 2026-10-19), most of it app start-up; measure your own pages and record the runtime with the check that uses them.

## Zoomed crops with sips

A whole-page glance hides the faults that matter. Crop the densest areas at full resolution with macOS `sips` (PIL may not be installed) [C-D21]:

```bash
cp out/page1.png <review dir>/crop.png                   # a folder inside the project or the session scratchpad, never /tmp
sips --cropOffset 400 1200 -c 600 900 <review dir>/crop.png      # offset y x, then height width
```

`sips` edits the file in place, so crop a copy. The order is y before x and height before width; `sips --help` labels the second offset "offsetH", but it is the x offset. Export at `-s 2` first when
lines are thin.

> **Learned 2026-10-21** · sips crop offsets · VERIFIED_PRIMARY · Source: `sips` on macOS 27.0.1, crops compared with `cmp` · Falsifier: a `--cropOffset 0 0` crop that differs from the same crop with no offset
> An offset of `0 0` is read as no offset: `sips --cropOffset 0 0 -c 1000 944` returned the centred crop, byte-identical to one without
> `--cropOffset`, while `--cropOffset 1 1` returned the top of the page. To crop from the top or left edge, use 1, not 0.


## The self-review loop

Never present a first render. Before any drawing (or screenshot, chart or page) goes to the operator [C-D22]:

```text
  +---------+    +------------------+    +-------------------+
  | export  | -> | zoomed crops of  | -> | trace every arrow |
  | (png)   |    | the densest areas|    | end to end        |
  +---------+    +------------------+    +-------------------+
       ^                                          |
       |          +------------+                  v
       +--------- | fix, then  | <---- any fault? yes
                  | re-render  |
                  +------------+         no: present, saying what was checked
```

1. Run the layout audits in tests first ([layout-audits.md](layout-audits.md)); they catch geometry, not rendering.
2. Export every page you changed, at scale 2 for dense pages.
3. Crop the densest areas and look at each crop.
4. Trace each arrow from its source to its head: does it take a needless bend or detour, cross a box, a label or another arrow's run, or hop where it should not?
5. Export the base layer alone and each colour layer alone; each must show what its name says.
6. Fix the cause in the map or the renderer, re-render, and repeat.
7. Present the result and say what was checked (pages, crops, layers, audits).

The rule exists because a sample once went out after a whole-page glance, and the operator found a group full of needless twists and turns: "You should have assessed yourself before presenting it to
me."

## What to look for

| Fault                | Seen as                                                | Usual cause                                                       |
| -------------------- | ------------------------------------------------------ | ----------------------------------------------------------------- |
| Needless bends       | Zig-zags inside a group                                | Ports or tracks badly ordered; run the barycentre and swap search |
| Arrow through a box  | Line over text                                         | Missing waypoints, or an obstacle not marked solid                |
| Double twist         | Two hops merged into an S                              | Crossings closer than `2 * jumpSize + 6`                          |
| Cramped head         | Arrowhead touching its turn                            | Last run under the head room                                      |
| Text overflow        | Words outside the box                                  | Characters-per-line budget too generous for bold text             |
| Ghost layer          | Colour layer hides nothing, or base layer shows arrows | A cell's parent is the wrong layer                                |
| Same-looking colours | Two families indistinguishable                         | Hues too close (orange and brown)                                 |

> **Learned 2026-10-23** · large pages clip at export scale 1 · VERIFIED_PRIMARY · Source: unified-network-controller End-to-end page export
> (draw.io 32.5.5, `scripts/drawio_export.py --pages 5 --scale 1`); screenshots `references/screenshots/20261023-palette-export/` · Falsifier: a page
> over about 8,000 px tall exporting whole at scale 1 on the same draw.io version
> A page of about 5,500 x 8,600 px exported at scale 1 came back full size but blank below about 4,500 px, its arrows cut off mid-run, with exit 0; at
> scale 0.5 the same page exported whole. Before reviewing a big page, check its export reaches the legend; export it at 0.5 for the whole view and crop
> the scale 1 export only where it is drawn. Do not judge the drawing from a clipped export: the cells were all there (geometry up to y 8516).
>
> ```bash
> # unified-network-controller, 2026-10-23: the review that found it
> drawio_export.py docs/flows/drawio/unc-flows.drawio --out-dir out --pages 1,5,8 --scale 1    # page 5 clipped
> drawio_export.py docs/flows/drawio/unc-flows.drawio --out-dir half --pages 5 --scale 0.5     # page 5 whole
> ```
