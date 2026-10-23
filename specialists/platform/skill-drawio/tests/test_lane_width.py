"""Offline test for flow-page lane width: lanes span the label-widened column gaps, so no step box sticks out past them (operator review of the
ansible-wifi smc_change map, 2026-10-23: the last step and its note overhung the lanes once long branch labels widened the gaps).

Run: `just test` (unittest, the pack's venv). The scripts folder is put on sys.path, as a consuming project does.
"""

from __future__ import annotations

import importlib
import sys
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
pages, profile = (importlib.import_module(f"flowmap.{n}") for n in ("pages", "profile"))


def _decision_map() -> dict:
  """A map whose flow has a decision with long branch labels, which widen the gaps after it.

  Returns:
    The map as loaded YAML would be.
  """
  steps = [
    {"id": "ask", "actor": "a", "action": "x", "via": ["SSH"], "shape": "decision", "next": ["yes", "no"],
     "when": {"yes": "a very long reason to take this branch", "no": "another very long reason for this one"}},
    {"id": "yes", "actor": "b", "action": "y", "via": ["API"], "next": ["end"]},
    {"id": "no", "actor": "a", "action": "z", "via": ["API"], "next": ["end"]},
    {"id": "end", "actor": "b", "action": "w", "via": ["file"]},
  ]
  return {
    "schema_version": 1, "title": "T", "updated": "2026-10-23",
    "components": [
      {"id": "a", "name": "A", "kind": "host", "group": "G", "host": "h", "health": "ok"},
      {"id": "b", "name": "B", "kind": "container", "group": "G", "host": "h", "health": "ok"},
    ],
    "flows": [{"id": "f", "title": "F", "category": "custom", "purpose": "p", "trigger": {"kind": "timer", "detail": "d"},
               "runs_on": "a", "owner": "b", "steps": steps}],
  }


def _right_edges(cells: list, prefix: str) -> list[float]:
  """Right edge (x + width) of every cell whose id starts with prefix.

  Args:
    cells: the page's mxCell elements.
    prefix: id prefix, for example "f-lane-" or "f-s-".

  Returns:
    The right edges.
  """
  out = []
  for c in cells:
    geo = c.find("mxGeometry")
    cid = c.get("id") or c.get("parent_id") or ""
    if cid.startswith(prefix) and geo is not None and geo.get("width"):
      out.append(float(geo.get("x", 0)) + float(geo.get("width")))
  return out


class LaneWidth(unittest.TestCase):
  """Lanes reach past the rightmost step box even when branch labels widen the gaps."""

  def test_lanes_cover_every_step(self) -> None:
    """Every lane's right edge is at or past every step box's right edge."""
    data = _decision_map()
    text = pages.render(data, profile.Profile.from_drawing(data, "flows.yaml", "s.json", "g"))
    page = ET.fromstring(text.split("\n", 2)[2]).findall("diagram")[2]
    cells = []
    for el in page.iter():
      if el.tag == "UserObject":
        cell = el.find("mxCell")
        cell.set("parent_id", el.get("id"))
        cells.append(cell)
      elif el.tag == "mxCell":
        cells.append(el)
    lanes, boxes = _right_edges(cells, "f-lane-"), _right_edges(cells, "f-s-")
    self.assertTrue(lanes and boxes)
    self.assertGreaterEqual(min(lanes), max(boxes))


if __name__ == "__main__":
  unittest.main()
