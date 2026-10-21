"""Offline tests for flow page routing (flowmap.routing, "routing", 2026-10-21): a decision's branches read Yes and No or the step's own
cases, and a crowded page (two gates in one lane, skips into another lane) routes every forward arrow clear of boxes with no two runs alongside.

Run: `just test` (unittest, the pack's venv). The scripts folder is put on sys.path, as a consuming project does.
"""

from __future__ import annotations

import importlib
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

audit = importlib.import_module("drawio.audit")
router, pages, lanes = (importlib.import_module(f"flowmap.{n}") for n in ("routing", "pages", "lanes"))
TestMap = importlib.import_module("test_layout_rules")


def _crowded() -> dict:
    """A map shaped like smc-resiliency's commissioning flow: two gates in one lane, a skip over each, a skip into the next lane.

    Returns:
        The map.
    """
    data = TestMap._minimal()
    data["flows"][0]["steps"] = [
        {"id": "reg", "actor": "a", "action": "x", "via": ["API"], "gate": "g1", "next": ["rec", "probe"]},
        {"id": "probe", "actor": "a", "action": "x", "via": ["SSH"], "gate": "g2", "next": ["ref", "rec"]},
        {"id": "rec", "actor": "a", "action": "x", "via": ["API"], "next": ["fetch"]},
        {"id": "ref", "actor": "a", "action": "x", "via": ["API"], "next": []},
        {"id": "fetch", "actor": "b", "action": "x", "via": ["API"]}]
    return data


class FlowRouterTests(unittest.TestCase):
    """The router's contract."""

    def test_branch_labels(self) -> None:
        """A two-way gate's branches read Yes (green) then No (red); `when` names other cases; a plain step and `branch_labels: off` keep the number."""
        gate = {"gate": "g", "next": ["a", "b"]}
        self.assertEqual(router.branch_label(gate, "a", 4, {}), ("4 · Yes", router.YES))   # yes/no branches green and red
        self.assertEqual(router.branch_label(gate, "b", 5, {}), ("5 · No", router.NO))
        self.assertEqual(router.branch_label(dict(gate, when={"b": "stale"}), "b", 5, {}), ("5 · stale", router.PLAIN))
        self.assertEqual(router.branch_label({"next": ["a"]}, "a", 2, {}), ("2", router.PLAIN))
        self.assertEqual(router.branch_label(gate, "a", 4, {"branch_labels": "off"}), ("4", router.PLAIN))

    def test_lane_head_symbol_sized_to_text(self) -> None:
        """lanes: an external (cloud) lane head needs room for its text; a plain head needs none."""
        data = TestMap._minimal()
        prof = TestMap._profile(data)
        cloud = {"id": "x", "name": "Setup menu", "kind": "external", "host": "a long host description that wraps", "health": "ok"}
        self.assertGreater(lanes.head_symbol_h(cloud, prof), 60)
        self.assertEqual(lanes.head_symbol_h(dict(cloud, kind="service"), prof), 0)

    def test_crowded_page_routes_clean(self) -> None:
        """Every forward arrow avoids the boxes, no two runs lie alongside, and the page's layout audit is clean."""
        data = _crowded()
        prof = TestMap._profile(data)
        comps = {c["id"]: c for c in data["components"]}
        page = pages.flow_page(data["flows"][0], comps, 1, prof)
        self.assertEqual(audit.faults(audit.page_audit(page)), [])
        segs = {r.cid: audit.segments(r.points) for r in page.routes}
        ids = sorted(segs)
        for i, a in enumerate(ids):
            for b in ids[i + 1:]:
                self.assertFalse(any(router._along(s, t) for s in segs[a] for t in segs[b]), f"{a} runs alongside {b}")


if __name__ == "__main__":
    unittest.main()
