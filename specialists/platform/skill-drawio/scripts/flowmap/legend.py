"""The End-to-end page's legend under the grid. Stdlib only.

Imported, not run: `from flowmap.legend import draw_legend` with the skill's scripts/ on sys.path.
"""

from __future__ import annotations

from drawio.mxfile import Page, label

from .e2e_grid import MARGIN
from .isolate import E2E_DIMMED, LEGEND_TAG, dim_level, group_tag, isolate_link
from .shapes import component_shapes_used, shape_legend
from .step_labels import legend_fit, legend_text


def draw_legend(self: object, page: Page, right: float) -> None:
    """The family legend under the grid: a swatch and the family's flows per family, then how to read an arrow.

    Args:
        self: the End-to-end page model (flowmap.e2e.EndToEnd).
        page: the page.
        right: the right edge of the last column.
    """
    y = self.bottom + 10
    per_flow = self.profile.look.get("e2e_layers", "family") == "flow"
    total = self.step_total
    count = {f["title"]: f" ({len(f['steps'])} step{'' if len(f['steps']) == 1 else 's'})" if total else "" for f in self.data["flows"]}   # legend step counts (2026-10-26)
    page.box("e2e-leg-title", label("**Legend: flows** (one colour and layer each)" if per_flow else "**Legend: flow families** (one layer each)"),
             MARGIN, y, 600, 24, "text;html=1;align=left;fontSize=14;")
    dim, leg = dim_level(self.profile.look), "1"
    if dim is not None:   # rows on a locked layer, so a click runs there
        leg = "e2e-L-legend"
        page.add_layer(leg, "Legend (click a row)", locked=True)
    for i, (fam, name, col, titles) in enumerate(self.groups):
        ly, gtag = y + 34 + i * 28, group_tag(self.profile.look, fam)
        iso = {} if dim is None else {"tags": (gtag, LEGEND_TAG), "link": isolate_link(i, E2E_DIMMED, gtag, dim)}
        page.box(f"e2e-leg-{fam}-s", "", MARGIN, ly + 10, 40, 3, f"rounded=0;html=1;fillColor={col};strokeColor=none;", layer=leg, **iso)
        text = f"**{name}**{count[titles[0]]}" if per_flow else f"**{name}:** " + "; ".join(t + count[t] for t in titles)
        page.box(f"e2e-leg-{fam}-t", label(text), MARGIN + 50, ly, right - MARGIN - 50, 24,
                 "text;html=1;align=left;verticalAlign=middle;fontSize=12;", layer=leg, **iso)
    ly = y + 34 + len(self.groups) * 28 + 6
    text = legend_text(self.step_total, bool(self.loops), dim is not None)
    wrap, h = legend_fit(text, right - MARGIN)
    page.box("e2e-leg-solid", label(text), MARGIN, ly, right - MARGIN, h, f"text;html=1;{wrap}align=left;verticalAlign=middle;fontSize=12;")
    used = component_shapes_used(list(self.comps.values()), self.profile)
    if used:   # the symbols the boxes use, as on a flow page
        shape_legend(page, used, MARGIN, ly + h + 16, "e2e")
