#!/usr/bin/env python3
"""One draw.io cell's XML: a plain `mxCell`, or a `UserObject` wrapping it when the cell has a link, a hover text or tags. Stdlib only.

draw.io keeps a cell's link, tooltip and tags on the value object that wraps the `mxCell` (a plain `mxCell` cannot carry them); the wrapper
holds the id and the label, the `mxCell` inside holds the style, parent, ends and geometry. Tags are one space-separated attribute, each tag
without spaces (draw.io XML reference, @drawio/mcp 1.5.0 `xml-reference.md`, "Tags", read 2026-10-23).

Imported, not run: `from drawio.cell import cell_xml, tag` with the skill's scripts/ on sys.path.
"""

from __future__ import annotations

import re
from xml.sax.saxutils import quoteattr


def tag(*parts: str) -> str:
    """One draw.io tag from words: lower case, every run of other characters a single dash (a tag may not hold a space).

    Args:
        parts: the words, for example ("flow", "apply").

    Returns:
        The tag, for example "flow-apply".
    """
    return re.sub(r"[^a-z0-9]+", "-", "-".join(parts).lower()).strip("-")


def cell_xml(cid: str, label: str, attrs: str, body: str, link: str = "", tooltip: str = "", tags: tuple = ()) -> str:
    """A cell's XML; with a link, tooltip or tags it is a `UserObject` wrapping its `mxCell`, as draw.io writes it.

    Args:
        cid: the cell id.
        label: the HTML label.
        attrs: the `mxCell` attributes after id and value (style, vertex or edge, parent, source and target).
        body: the `mxCell` content (its geometry).
        link: an optional link.
        tooltip: an optional hover text.
        tags: optional tags, each already a single word (see tag()); written in order, without repeats.

    Returns:
        The XML text.
    """
    tags = tuple(dict.fromkeys(t for t in tags if t))
    if not (link or tooltip or tags):
        return f'<mxCell id="{cid}" value={quoteattr(label)} {attrs}>{body}</mxCell>'
    extra = "".join(f" {k}={quoteattr(v)}" for k, v in (("link", link), ("tooltip", tooltip), ("tags", " ".join(tags))) if v)
    return f'<UserObject id="{cid}" label={quoteattr(label)}{extra}><mxCell {attrs}>{body}</mxCell></UserObject>'
