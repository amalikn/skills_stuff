#!/usr/bin/env python3
"""Offline tests for smc_mark_iridium.py: placement, idempotence, refusal with nothing written.

Run: python3 scripts/ansible/test_smc_mark_iridium.py   (or `just test_smc_mark_iridium`)
"""

from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path

_SPEC = importlib.util.spec_from_file_location("smc_mark_iridium", Path(__file__).resolve().parent / "smc_mark_iridium.py")
assert _SPEC and _SPEC.loader
m = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(m)


def make_repo(root: Path, files: dict[str, str]) -> Path:
  """Write host vars files into a fake checkout.

  Args:
    root: temporary directory.
    files: host name -> file content.

  Returns:
    the host vars directory.
  """
  hv = root / "inventories" / "rct" / "host_vars"
  hv.mkdir(parents=True)
  for h, body in files.items():
    (hv / f"{h}.yml").write_text(body)
  return hv


class MarkIridiumTest(unittest.TestCase):
  """Behaviour of plan and apply."""

  def test_adds_after_siteid_and_is_idempotent(self) -> None:
    """The line lands after site_eclipse_siteid; a second apply adds nothing."""
    with tempfile.TemporaryDirectory() as d:
      hv = make_repo(Path(d), {"a-smc01": "---\nsite_eclipse_siteid: 1\nother: x\n"})
      self.assertEqual(m.main(["--repo", d, "--flavor", "rct", "a-smc01", "--apply"]), 0)
      self.assertEqual((hv / "a-smc01.yml").read_text(), "---\nsite_eclipse_siteid: 1\nsmc_bases_iridium: true\nother: x\n")
      self.assertEqual(m.main(["--repo", d, "--flavor", "rct", "a-smc01", "--apply"]), 0)
      self.assertEqual((hv / "a-smc01.yml").read_text().count("smc_bases_iridium"), 1)

  def test_refuses_missing_or_conflict_and_writes_nothing(self) -> None:
    """A missing host or a false value stops the run before any write."""
    with tempfile.TemporaryDirectory() as d:
      hv = make_repo(Path(d), {"a-smc01": "---\nsite_eclipse_siteid: 1\n", "b-smc01": "---\nsmc_bases_iridium: false\n"})
      self.assertEqual(m.main(["--repo", d, "--flavor", "rct", "a-smc01,b-smc01", "--apply"]), 1)
      self.assertEqual(m.main(["--repo", d, "--flavor", "rct", "a-smc01,nope-smc01", "--apply"]), 1)
      self.assertNotIn("smc_bases_iridium", (hv / "a-smc01.yml").read_text())

  def test_plan_writes_nothing(self) -> None:
    """Without --apply the file is unchanged."""
    with tempfile.TemporaryDirectory() as d:
      hv = make_repo(Path(d), {"a-smc01": "---\n"})
      self.assertEqual(m.main(["--repo", d, "--flavor", "rct", "a-smc01"]), 0)
      self.assertEqual((hv / "a-smc01.yml").read_text(), "---\n")


if __name__ == "__main__":
  unittest.main()
