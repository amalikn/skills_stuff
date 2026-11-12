---
Title: Build from data (draft part for skill-presentation)
Category: skill-seed-part
Status: drafted
Authority: >-
  Drafted 2026-11-12 from the enterprise-strategy engagement (session 39f36749): the strategy deck, the one-pager pack in PowerPoint and draw.io, and the render tool, all built and reviewed that
  day; code cited by path and commit
Scope: How a deliverable is built from data: source, data, builders, the same content in two formats, drift checks, rendering and review, and the content rules the builders enforce
Last reviewed: 20261112_1815
Summary: >-
  Markdown is the source, one data file feeds every format, a builder per format holds only layout, generated files carry a drift check, and every page is rendered and looked at. Worked example:
  enterprise-strategy's strategy deck and one-pager pack (PowerPoint through pptxgenjs, draw.io through skill-drawio's drawio.mxfile).
---

# Build from data

## Contents

- [The pattern](#the-pattern)
- [Worked example: files and commits](#worked-example-files-and-commits)
- [One data file, two formats](#one-data-file-two-formats)
- [pptxgenjs: margins are points](#pptxgenjs-margins-are-points)
- [draw.io pages from code](#drawio-pages-from-code)
- [Rendering PowerPoint on macOS](#rendering-powerpoint-on-macos)
- [Content rules the data enforces](#content-rules-the-data-enforces)
- [Review findings that changed the build](#review-findings-that-changed-the-build)

## The pattern

1. **Markdown is the source of truth.** It says each page's message. Change it first.
2. **One data file holds the content** (wording, dates, states). JSON when two languages read it; a JS module when only the JS builder does.
3. **One builder per format holds only layout.** It reads the data and writes the file beside the markdown, same stem. The output is never edited by hand; a rebuild overwrites it.
4. **A task runs the builders** (`just one-pagers`), and **a drift check** (`just one-pagers-check`, in `just check`) fails when a generated file differs from a fresh render of its data. Prove the
   check can fail by changing the data once.
5. **Render every page and look** before anyone sees it; fix the builder, never the output.

## Worked example: files and commits

All paths under `/Volumes/Data/_ai/_project/project_stuff/apn/enterprise-strategy/` (repo `apn`, commits a3e29af7, ee9046df, 6c262ea9, 12 Nov 2026).

| File | Role |
| --- | --- |
| `slides/strategy-deck-20261112_1550.md` | Source of truth for the 14-slide strategy deck (ten business slides, a four-slide technical appendix) |
| `scripts/strategy_deck_data.js` | Deck data: requirements by phase, solutions grid, site menu card, quiet-site story, field cost, priority, gaps, timeline |
| `scripts/build_strategy_pptx.js` | Deck layout in pptxgenjs 3.12.0 (helpers `box`, `line`, `headRow`, `keyRow`, `contentSlide`; one function per slide) |
| `slides/one-pagers-20261112_1752.md` | Source of truth for the four one-pagers (overview and one page per project) |
| `scripts/one_pagers_data.json` | One-pager data, read by both builders below |
| `scripts/build_one_pagers_pptx.js` | One-pager layout in pptxgenjs |
| `scripts/build_one_pagers_drawio.py` | The same pages in draw.io through skill-drawio's `drawio.mxfile` (`Page`, `label`, `mxfile`, `banner`) and `drawio.audit.page_audit` |
| `scripts/test_build_one_pagers_drawio.py` | Tests: four pages and banner, no requirement codes, step codes with descriptions, known states, drift |
| `scripts/render_pptx_pages.py` | Renders a pptx to page PNGs through PowerPoint (or LibreOffice) on a fresh copy |
| `scripts/test_render_pptx_pages.py` | Tests: fresh name, container default, the AppleScript addresses the copy by name |
| `scripts/check_governance.py` | `check_plain_requirement_names`: no BR or TR code outside the sections that define them |
| `justfile` | Recipes `strategy-pptx`, `one-pagers`, `one-pagers-check`, `render-pages` |

## One data file, two formats

The operator asked for the one-pagers in PowerPoint and in draw.io. Both builders read `scripts/one_pagers_data.json` and use one geometry: inches in pptxgenjs, 100 px per inch in draw.io, so a
layout fix is made once in each builder at the same coordinates. The draw.io file is byte-for-byte deterministic, so the drift check is a string comparison:

```python
# scripts/build_one_pagers_drawio.py (ee9046df)
text = render(args.skill_root)
if args.check:
    current = OUT.read_text(encoding="utf-8") if OUT.exists() else ""
    print("ok: one-pagers drawio is current" if current == text else f"drift: {OUT.name} is out of step; run just one-pagers")
    return 0 if current == text else 1
```

Fonts differ by renderer: draw.io's export has no Calibri or Cambria and falls back to a serif, so the draw.io builder uses Helvetica and Georgia while the PowerPoint keeps Calibri and Cambria.

## pptxgenjs: margins are points

pptxgenjs 3.12 reads a text box's `margin` as points (it calls `valToPts`), but a table cell's margin below 1 as inches. A builder that passed `margin: 0.12` meaning inches left every card's text on
its border. Convert in the one box helper:

```js
// scripts/build_strategy_pptx.js (a3e29af7)
const PT_PER_INCH = 72;
function box(s, text, x, y, w, h, o = {}) {
  s.addText(text, { x, y, w, h, /* ... */ margin: (o.margin ?? 0.08) * PT_PER_INCH });
}
```

Verified in the slide XML (`lIns="109728"` EMU = 0.12 in) and in the render.

## draw.io pages from code

skill-drawio's flow-map engine draws flows; a page layout (cards, tables, a milestone line) is built directly with `drawio.mxfile.Page.box` and `label`, given unique ids per page, wrapped with the
`banner` (GENERATED, how to rebuild, which check fails) and `mxfile`. `page_audit()` is run on every page and any fault stops the write:

```python
# scripts/build_one_pagers_drawio.py (ee9046df)
faults = {pg.name: {k: v for k, v in page_audit(pg).items() if v} for pg in pages}
faults = {name: f for name, f in faults.items() if f}
if faults:
    raise ValueError(f"layout audit found faults: {faults}")
head = banner("scripts/build_one_pagers_drawio.py", "scripts/one_pagers_data.json", "just one-pagers", "just check")
```

Export for review with skill-drawio's `scripts/drawio_export.py FILE --out-dir DIR --pages 1,2,3,4` (desktop CLI, under a timeout).

## Rendering PowerPoint on macOS

Three faults met in one day, each fixed in `scripts/render_pptx_pages.py` (6c262ea9):

1. **A cached copy of a re-opened path.** Copy the deck to a fresh name before every render.
2. **"Grant File Access" on every run.** PowerPoint is sandboxed: it asks once per new folder outside its container, and a render that writes to a new folder each run asked each time; an
   unanswered prompt failed the export with error -9074 or "User cancelled". Default the output to PowerPoint's own container, which needs no grant:

   ```python
   POWERPOINT_CONTAINER = Path.home() / "Library" / "Containers" / "com.microsoft.Powerpoint" / "Data" / "tmp"
   base = POWERPOINT_CONTAINER if engine == "powerpoint" else Path(tempfile.gettempdir())
   return base / "render-pages" / f"{src.stem}-{now.strftime('%Y%m%d_%H%M%S')}"
   ```

3. **The wrong deck exported.** The AppleScript saved `active presentation`; with the operator's own window on the same deck open, that window (older content) was exported instead of the fresh
   copy. Address the copy by name and wait until it is open:

   ```python
   name = copy.name
   f'open POSIX file "{copy}"\n'
   f'repeat 30 times\nif exists presentation "{name}" then exit repeat\ndelay 0.5\nend repeat\n'
   f'save presentation "{name}" in POSIX file "{pdf}" as save as PDF\n'
   f'close presentation "{name}" saving no\n'
   ```

   The test asserts `"active presentation"` never appears in the script. Before the fix, a render can look current and be stale: check one changed word on the page.

## Content rules the data enforces

Operator rules of 12 Nov 2026 for management material, each held by a test or check where it can be:

- **No internal codes a reader must look up.** Requirement codes (BR, TR) stay out of management pages; a plan step keeps its code beside a plain description, "R2.4 · first two sites" (the
  operator: "If I don't remember them, how can we expect Martin or Sandro to?"). Held by `check_plain_requirement_names` and the one-pager test.
- **No date or recommendation nobody gave.** An undated item says "to agree on <meeting>" or "to confirm"; a review caught proposed dates and a "recommended" tag the agent had added.
- **No prices when the operator rules them out;** show cost as reductions and as counts (days on site per install, visits per site, faults found first), with a baseline to be taken.
- **Name what the audience knows.** The operator renamed "management platform" to the product's own name, the Unified Network Controller.
- **Team documents are references.** Source files supplied by a team are read, indexed and never edited.

## Review findings that changed the build

- An engineer's traceability grid is not a business story: lead with a mission, what we heard (paraphrased), every requirement for every solution, a before-and-after scenario in the audience's
  own example, where the money is, what comes later with its next decision, and a priority question; put the grid in an appendix.
- A "menu card" (a function as rows, each platform as a column, cost rows) lets management pick the cheapest option and see in writing what it gives up; the operator's own model for the site box and the
  radio equipment.
- Supplied documents change facts: read every file in a folder the operator points at, including later additions, before building on it.
