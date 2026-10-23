"""Offline tests for flowmap.e2e_family ("e2e_family"): one End-to-end page per family after the full one when `look.e2e_family_pages` is on
(operator, 2026-10-23), drawn from the example shop map.

Run: `just test` (unittest, the pack's venv). The scripts folder is put on sys.path, as a consuming project does.
"""

from __future__ import annotations

import importlib
import re
import sys
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
(page_audit,) = (importlib.import_module("drawio.audit").page_audit,)
e2e_family, pages, profile = (importlib.import_module(f"flowmap.{n}") for n in ("e2e_family", "pages", "profile"))
EXAMPLE = ROOT / "examples" / "shop" / "flows.yaml"


def _map(**look: object) -> dict:
    """The example shop map with look keys pinned.

    Args:
        look: the `drawing.look` keys to set.

    Returns:
        The map.
    """
    data = yaml.safe_load(EXAMPLE.read_text(encoding="utf-8"))
    data["drawing"]["look"] = {**(data["drawing"].get("look") or {}), **look}
    return data


def _diagrams(text: str) -> list[ET.Element]:
    """The `<diagram>` elements of a rendered file.

    Args:
        text: the file text (banner comment first).

    Returns:
        The diagrams, in tab order.
    """
    return list(ET.fromstring(text.split("-->", 1)[1]).iter("diagram"))


def _render(data: dict) -> str:
    """Render a map under the profile its drawing block gives.

    Args:
        data: the map.

    Returns:
        The file text.
    """
    return pages.render(data, profile.Profile.from_drawing(data, "flows.yaml", "s.json", "g"))


class FamilyPages(unittest.TestCase):
    """Family End-to-end pages: off by default, after the full page when on, the map's flow numbers, unique ids, audits clean."""

    def test_off_by_default_and_full_page_unchanged(self) -> None:
        """Without the key no family page is drawn; with it the full End-to-end page is byte-identical to before."""
        off, on = _render(_map()), _render(_map(e2e_family_pages=True))
        self.assertFalse([d for d in _diagrams(off) if d.get("id", "").startswith("end-to-end-")])
        full = [ET.tostring(d) for d in _diagrams(off) if d.get("id") == "end-to-end"]
        self.assertEqual(full, [ET.tostring(d) for d in _diagrams(on) if d.get("id") == "end-to-end"])

    def test_one_page_per_family_after_the_full_page(self) -> None:
        """Pages follow the full one in family order, each holding only its family's flows, numbered as in the whole map."""
        data = _map(e2e_family_pages=True, e2e_layers="flow")
        ids = [d.get("id") for d in _diagrams(_render(data))]
        at = ids.index("end-to-end")
        self.assertEqual(ids[at + 1:at + 4], ["end-to-end-orders", "end-to-end-catalogue", "end-to-end-operations"])
        number = {f["id"]: i for i, f in enumerate(data["flows"], 1)}
        prof = profile.Profile.from_drawing(data, "flows.yaml", "s.json", "g")
        for fam, _name, part in e2e_family.family_parts(data, prof):
            page = next(d for d in _diagrams(_render(data)) if d.get("id") == f"end-to-end-{fam}")
            labels = {re.match(r"<b>(\d+)\.", u.get("tooltip")).group(1) for u in page.iter("UserObject") if "step-arrow" in (u.get("tags") or "")}
            self.assertEqual(labels, {str(number[f["id"]]) for f in part["flows"]}, fam)

    def test_ids_unique_in_the_file_and_colours_unique_per_page(self) -> None:
        """Family pages rename their ids (no clash with the full page); per-flow colours do not repeat on one page."""
        text = _render(_map(e2e_family_pages=True, e2e_layers="flow"))
        ids = [c.get("id") for d in _diagrams(text) for c in d.iter() if c.get("id") and c.tag in ("mxCell", "UserObject") and c.get("id") not in ("0", "1")]
        self.assertEqual(len(ids), len(set(ids)))
        for d in _diagrams(text):
            if d.get("id", "").startswith("end-to-end-"):
                swatches = [re.search(r"fillColor=(#\w+)", c.get("style")).group(1) for c in d.iter("mxCell")
                            if (c.get("style") or "").startswith("rounded=0") and "strokeColor=none" in c.get("style") and "fillColor=#f" not in c.get("style")]
                self.assertEqual(len(swatches), len(set(swatches)), d.get("id"))

    def test_audits_clean_and_unused_tiers_dropped(self) -> None:
        """Every family page passes the layout audits; a family that touches two tiers draws two columns."""
        data = _map(e2e_family_pages=True)
        prof = profile.Profile.from_drawing(data, "flows.yaml", "s.json", "g")
        for page in e2e_family.family_pages(data, prof):
            self.assertFalse([k for k, v in page_audit(page).items() if v], page.page_id)
        comps = [c for c in data["components"] if c["group"] in ("People", "Application")]
        self.assertEqual([t[0] for t in e2e_family.narrowed(prof, comps).tiers], ["People", "Application"])

    def test_overview_index_links_each_family_page(self) -> None:
        """The Overview index gains one entry per family page, linking to it."""
        overview = _diagrams(_render(_map(e2e_family_pages=True)))[0]
        links = {u.get("link") for u in overview.iter("UserObject") if (u.get("id") or "").startswith("ov-f-end-to-end-")}
        self.assertEqual(links, {f"data:page/id,end-to-end-{f}" for f in ("orders", "catalogue", "operations")})


if __name__ == "__main__":
    unittest.main()
