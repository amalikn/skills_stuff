#!/usr/bin/env python3
"""Offline tests for topology_variance.py: names normalised, whitespace ignored, hidden caches skipped, missing flavor refused.

Run: python3 scripts/ansible/test_topology_variance.py   (or `just test_topology_variance`)
"""

from __future__ import annotations

import contextlib
import importlib.util
import io
import tempfile
import unittest
from pathlib import Path

_SPEC = importlib.util.spec_from_file_location("topology_variance", Path(__file__).resolve().parent / "topology_variance.py")
assert _SPEC and _SPEC.loader
m = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(m)

LAYOUT = "---\ntopology:\n  hosts:\n    - name: {host}\n      subnets:{pad}\n        last:{gap}+110\n"


class TopologyVarianceTest(unittest.TestCase):
  """Grouping on a fake inventory."""

  def test_groups_and_skips(self) -> None:
    """Two sites differing only in names and whitespace share a layout; a third differs; the cache file is not read."""
    with tempfile.TemporaryDirectory() as d:
      topo = Path(d, "inventories", "rct", "topology_vars")
      topo.mkdir(parents=True)
      (topo / "alpha.yml").write_text(LAYOUT.format(host="alpha-smc01", pad=" ", gap="  "))
      (topo / "beta.yml").write_text(LAYOUT.format(host="beta-smc01", pad="", gap=" "))
      (topo / "gamma.yml").write_text(LAYOUT.format(host="gamma-smc01", pad="", gap=" ").replace("+110", "+120"))
      (topo / ".alpha.yml").write_text("cache")
      groups = m.layouts(topo)
      self.assertEqual([sites for _, sites in groups], [["alpha", "beta"], ["gamma"]])
      buf = io.StringIO()
      with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
        rc = m.main(["--repo", d, "rct", "nope"])
      self.assertEqual(rc, 2)
      self.assertIn("== rct: 3 files, 2 layouts", buf.getvalue())


if __name__ == "__main__":
  unittest.main()
