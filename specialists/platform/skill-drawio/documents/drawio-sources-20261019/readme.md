---
Title: draw.io sources 2026-10-19
Category: reference
Status: current
Authority: local-supplement
Scope: Verbatim copies of the external pages and tool outputs skill-drawio relies on
Last reviewed: 2026-10-19
Summary: Index of the draw.io, W3C and macOS sources fetched or captured on 2026-10-19, with the URL or command and what each supports.
---

# draw.io sources 2026-10-19

Each file is the page or output as fetched or captured on 2026-10-19 and kept verbatim. Web pages were converted to Markdown text; source files (`.js`, `.html`, `.xsd`, README) are byte copies. The
draw.io help pages do not document the compressed-page codec or the `data:page/id,` link form; the codec comes from the official drawio-tools source below, and the link form from the installed desktop
app (see `sources.yaml` C-D07).

| File                               | URL or command                                                               | Fetched    | Supports                                                            |
| ---------------------------------- | ---------------------------------------------------------------------------- | ---------- | ------------------------------------------------------------------- |
| [style-reference.txt](style-reference.txt) | <https://www.drawio.com/docs/reference/diagram-generation/style-reference/>  | 2026-10-19 | mxfile skeleton, root cells 0 and 1, `html=1`, waypoints            |
|                                    |                                                                              |            |   `Array as="points"`, exit and entry fractions, perimeter flags,   |
|                                    |                                                                              |            |   `jumpSize`, group-relative coordinates, UserObject, uncompressed  |
|                                    |                                                                              |            |   output for generators                                             |
| [mxfile-xsd.txt](mxfile-xsd.txt)   | <https://raw.githubusercontent.com/jgraph/drawio-mcp/main/shared/mxfile.xsd> | 2026-10-19 | Schema companion to the style reference: layers are `mxCell` with   |
|                                    |                                                                              |            |   `parent="0"`, UserObject and object carry id, label, link,        |
|                                    |                                                                              |            |   tooltip; compressed pages are deflated and base64-encoded         |
| [drawio-tools-js.txt](drawio-tools-js.txt) | <https://jgraph.github.io/drawio-tools/utils/drawio-tools.js>                | 2026-10-19 | Codec: encode is `encodeURIComponent`, `deflateRaw`, `btoa`; decode |
|                                    |                                                                              |            |   is `atob`, `inflateRaw`, `decodeURIComponent`                     |
| [drawio-tools-text-tools.txt](drawio-tools-text-tools.txt) | <https://jgraph.github.io/drawio-tools/tools/text-tools.html>                | 2026-10-19 | The official tool page that loads the codec ("URL encode,           |
|                                    |                                                                              |            |   Deflate, Base64")                                                 |
| [save-file-formats.txt](save-file-formats.txt) | <https://www.drawio.com/docs/manual/editor/save-file-formats/>               | 2026-10-19 | `.drawio` is the default format and is uncompressed XML             |
| [export-to-xml.txt](export-to-xml.txt) | <https://www.drawio.com/docs/manual/export/export-to-xml/>                   | 2026-10-19 | The Compressed checkbox on XML export; the official decompress tool |
| [diagram-source-edit.txt](diagram-source-edit.txt) | <https://www.drawio.com/doc/faq/diagram-source-edit>                         | 2026-10-19 | Extras > Edit Diagram shows a page's `mxGraphModel` XML             |
| [layers.txt](layers.txt)           | <https://www.drawio.com/docs/manual/layers/>                                 | 2026-10-19 | Layers panel (Ctrl+Shift+L or Cmd+Shift+L); one layer per shape;    |
|                                    |                                                                              |            |   connectors may join shapes on different layers                    |
| [how-layers-work.txt](how-layers-work.txt) | <https://www.drawio.com/docs/manual/layers/how-layers-work/>                 | 2026-10-19 | Cell tree: root, then layers, then elements; stacking within and    |
|                                    |                                                                              |            |   across layers                                                     |
| [hide-display-layers.txt](hide-display-layers.txt) | <https://www.drawio.com/docs/manual/layers/hide-display-layers/>             | 2026-10-19 | Hiding and showing layers in the editor and viewer                  |
| [links-tooltips-tags.txt](links-tooltips-tags.txt) | <https://www.drawio.com/docs/manual/links-tooltips-tags/>                    | 2026-10-19 | Links can open another page of a multi-page diagram                 |
| [tooltips.txt](tooltips.txt)       | <https://www.drawio.com/docs/manual/links-tooltips-tags/tooltips/>           | 2026-10-19 | Tooltips on shapes, with HTML                                       |
| [waypoints-connectors.txt](waypoints-connectors.txt) | <https://www.drawio.com/docs/manual/connectors/waypoints-connectors/>        | 2026-10-19 | Waypoints fix a connector's route; line jumps for crossings         |
| [connector-fixed-vs-floating.txt](connector-fixed-vs-floating.txt) | <https://www.drawio.com/docs/manual/connectors/connector-fixed-vs-floating/> | 2026-10-19 | Fixed connection points versus floating perimeter ends              |
| [group-shapes-connectors.txt](group-shapes-connectors.txt) | <https://www.drawio.com/docs/manual/editor/group-shapes-connectors/>         | 2026-10-19 | Groups behave as one shape; children belong to the group            |
| [export-to-png.txt](export-to-png.txt) | <https://www.drawio.com/docs/manual/export/export-to-png/>                   | 2026-10-19 | PNG export options in the editor (zoom, border, size)               |
| [drawio-desktop-readme.txt](drawio-desktop-readme.txt) | <https://raw.githubusercontent.com/jgraph/drawio-desktop/dev/README.md>      | 2026-10-19 | draw.io desktop releases and updates; it does not document the      |
|                                    |                                                                              |            |   CLI flags                                                         |
| [drawio-desktop-cli-help-32.5.5.txt](drawio-desktop-cli-help-32.5.5.txt) | `/Applications/draw.io.app/Contents/MacOS/draw.io --help`                    | 2026-10-19 | Every CLI flag in 32.5.5: `-x`, `-f`, `-o`, `-p` (1-based),         |
|                                    |                                                                              |            |   `--layers` (indexes), `-s`, `--crop` (PDF only), `--size`,        |
|                                    |                                                                              |            |   `--timeout`, `-u`                                                 |
| [macos-sips-help.txt](macos-sips-help.txt) | `sips --help` (macOS 27.0.1)                                                 | 2026-10-19 | `--cropOffset` and `-c` for zoomed crops                            |
| [wcag22-contrast-minimum.txt](wcag22-contrast-minimum.txt) | <https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html>          | 2026-10-19 | 4.5:1 for text, 3:1 for large text; ratios are not rounded          |
| [wcag22-non-text-contrast.txt](wcag22-non-text-contrast.txt) | <https://www.w3.org/WAI/WCAG22/Understanding/non-text-contrast.html>         | 2026-10-19 | 3:1 for graphical objects such as lines and icons                   |
