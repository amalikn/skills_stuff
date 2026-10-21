"""Offline tests for the optional `status` field (added 2026-10-21): a proposed or designed component draws dashed on the Overview, End-to-end
and its flow lane; a flow's status shows in its page header and Overview index line, with a status legend; maps without status are unchanged.

Run: `just test` (unittest, the pack's venv). The scripts folder is put on sys.path, as a consuming project does.
"""

from __future__ import annotations

import importlib
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

model, overview_index, pages = (importlib.import_module(f"flowmap.{n}") for n in ("model", "overview_index", "pages"))
TestMap = importlib.import_module("test_layout_rules")


class StatusTests(unittest.TestCase):
    """The status field's contract."""

    def test_without_status_nothing_changes(self) -> None:
        """No status anywhere: no dashed component, no Status line, no status legend."""
        data = TestMap._minimal()
        text = pages.render(data, TestMap._profile(data))
        self.assertNotIn("ov-status-leg", text)
        self.assertNotIn("Status:", text)

    def test_status_is_drawn(self) -> None:
        """A designed component is dashed everywhere it is drawn; a flow's status is in its header, index line and legend."""
        data = TestMap._minimal()
        data["components"][0]["status"] = {"state": "designed", "since": "2026-10-14"}
        data["flows"][0]["status"] = {"state": "spike-proved", "since": "2026-10-20", "evidence": "report"}
        text = pages.render(data, TestMap._profile(data))
        self.assertIn("ov-status-leg", text)
        self.assertIn("spike-proved since 2026-10-20 (report)", text)
        cells = [c for c in text.split("<UserObject ") if c.startswith('id="ov-c-a"') or c.startswith('id="e2e-c-a"')]
        self.assertEqual(len(cells), 2)   # both drawings of the component found, so the check below can fail
        for cell in cells:
            self.assertIn("dashed=1", cell.split("</UserObject>")[0])

    def test_flow_index_links_options_and_status(self) -> None:
        """overview_index.flow_index lists the Options page and draws the status legend only when the map has them."""
        data = TestMap._minimal()
        prof = TestMap._profile(data)
        page = importlib.import_module("drawio.mxfile").Page("overview", "Overview")
        overview_index.flow_index(page, data, prof, 0, 0)
        self.assertNotIn("ov-f-options", page.rects)
        data["options"] = {"title": "T", "groups": []}
        data["flows"][0]["status"] = {"state": "proposed", "since": "2026-10-21"}
        page = importlib.import_module("drawio.mxfile").Page("overview", "Overview")
        overview_index.flow_index(page, data, prof, 0, 0)
        self.assertIn("ov-f-options", page.rects)
        self.assertIn("ov-status-leg", page.rects)

    def test_status_text_and_style(self) -> None:
        """status_text names state, date and evidence; only proposed and designed get a dashed style (negative: built does not)."""
        self.assertEqual(model.status_text({"status": {"state": "built", "since": "2026-01-02"}}), "built since 2026-01-02")
        self.assertEqual(model.status_style({"status": {"state": "built", "since": "2026-01-02"}}), "")
        self.assertIn("dashed=1", model.status_style({"status": {"state": "proposed", "since": "2026-01-02"}}))


if __name__ == "__main__":
    unittest.main()
