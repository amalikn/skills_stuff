#!/usr/bin/env python3
"""Offline tests for smc_inventory_add.py: every flavor's topology source, the Iridium flag, output faults, refusals with nothing written.

Run: python3 scripts/ansible/test_smc_inventory_add.py   (or `just test_smc_inventory_add`); needs ansible-playbook on PATH.
"""

from __future__ import annotations

import contextlib
import importlib.util
import io
import shutil
import tempfile
import unittest
from pathlib import Path

_SPEC = importlib.util.spec_from_file_location("smc_inventory_add", Path(__file__).resolve().parent / "smc_inventory_add.py")
assert _SPEC and _SPEC.loader
m = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(m)

INVENTORY = "[old_smc_bases]\nold-smc01\n\n[smc_bases:children]\nold_smc_bases\n\n[old:children]\nold_smc_bases\n\n# End of File\n"
RCP_SMALL = (
  "---\ntopology:\n  hosts:\n    - name: small-smc01\n      interfaces:\n        eth0: \n          name: enp1s0\n          last:  +110\n          vlanid: 525\n"
)


def make_repo(root: Path) -> Path:
  """Build a fake ansible-wifi checkout with one existing site per flavor and the rcp small profile.

  Args:
    root: temporary directory.

  Returns:
    the checkout path.
  """
  for flavor in m.FLAVORS:
    inv = root / "inventories" / flavor
    for sub in ("group_vars", "host_vars", "topology_vars"):
      (inv / sub).mkdir(parents=True)
    (inv / "prod").write_text(INVENTORY)
    (inv / "host_vars" / "old-smc01.yml").write_text("---\nsite_eclipse_siteid: 100\n")
  (root / "inventories" / "rcp" / "topology_vars" / "small.yml").write_text(RCP_SMALL)
  return root


def run(repo: Path, *args: str) -> tuple[int, str]:
  """Run the tool's main() on the fake checkout.

  Args:
    repo: fake checkout.
    *args: command-line arguments after --repo.

  Returns:
    (exit code, printed output).
  """
  buf = io.StringIO()
  with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
    try:
      rc = m.main(["--repo", str(repo), "--env", "prod", *args])
    except SystemExit as exc:
      rc = exc.code if isinstance(exc.code, int) else 1
      print(exc.code)
  return rc, buf.getvalue()


@unittest.skipUnless(shutil.which("ansible-playbook"), "needs ansible-playbook")
class InventoryAddTest(unittest.TestCase):
  """Plan and apply per flavor."""

  def setUp(self) -> None:
    """Create a fresh fake checkout per test."""
    self._tmp = tempfile.TemporaryDirectory()
    self.repo = make_repo(Path(self._tmp.name))

  def tearDown(self) -> None:
    """Remove the fake checkout."""
    self._tmp.cleanup()

  def inv(self, flavor: str, sub: str, name: str) -> str:
    """Read a written vars file.

    Args:
      flavor: inventory flavor.
      sub: group_vars, host_vars or topology_vars.
      name: file stem.

    Returns:
      the file content.
    """
    return (self.repo / "inventories" / flavor / sub / f"{name}.yml").read_text()

  def test_rct_iridium_is_plain_true(self) -> None:
    """--iridium writes smc_bases_iridium: true unquoted, and the topology names the host."""
    rc, out = run(self.repo, "--flavor", "rct", "--host", "new-smc01", "--siteid", "663", "--iridium", "--apply")
    self.assertEqual(rc, 0, out)
    self.assertEqual(self.inv("rct", "host_vars", "new-smc01"), "---\nsite_eclipse_siteid: 663\nsmc_bases_iridium: true\n")
    self.assertIn("name: new-smc01", self.inv("rct", "topology_vars", "new"))
    self.assertEqual(self.inv("rct", "group_vars", "new"), "---\nsite_name: new\n")
    inv = (self.repo / "inventories" / "rct" / "prod").read_text()
    self.assertIn("[new_smc_bases]\nnew-smc01\n", inv)
    self.assertTrue(inv.rstrip().endswith("[new:children]\nnew_smc_bases\n\n# End of File"), inv)

  def test_no_iridium_line_without_flag(self) -> None:
    """Without --iridium the host_vars has the site ID only."""
    rc, out = run(self.repo, "--flavor", "wh", "--host", "new-smc01", "--siteid", "664", "--apply")
    self.assertEqual(rc, 0, out)
    self.assertNotIn("iridium", self.inv("wh", "host_vars", "new-smc01"))

  def test_nbn_wh_uses_standard_topology(self) -> None:
    """nbn_wh renders the common topology like rct."""
    rc, out = run(self.repo, "--flavor", "nbn_wh", "--host", "new-smc01", "--siteid", "665", "--apply")
    self.assertEqual(rc, 0, out)
    self.assertIn("template common/topology_vars.j2", out)

  def test_nbn_accelerate_needs_size_and_renders_nics(self) -> None:
    """nbn_accelerate refuses without --size; with --size big the NIC names are filled."""
    rc, _ = run(self.repo, "--flavor", "nbn_accelerate", "--host", "new-smc01", "--siteid", "666")
    self.assertEqual(rc, 2)
    rc, out = run(self.repo, "--flavor", "nbn_accelerate", "--host", "new-smc01", "--siteid", "666", "--size", "big", "--apply")
    self.assertEqual(rc, 0, out)
    self.assertIn("name: eno1", self.inv("nbn_accelerate", "topology_vars", "new"))

  def test_nbn_accelerate_booth_uses_common(self) -> None:
    """--booth takes common/topology_vars.j2, not the sized flavor template."""
    rc, out = run(self.repo, "--flavor", "nbn_accelerate", "--host", "booth-smc01", "--siteid", "668", "--booth", "--apply")
    self.assertEqual(rc, 0, out)
    self.assertIn("template common/topology_vars.j2", out)

  def test_rcp_size_clones_profile_tidied(self) -> None:
    """rcp --size small clones the small profile, host renamed, whitespace the lint rejects removed."""
    rc, out = run(self.repo, "--flavor", "rcp", "--host", "new-smc01", "--siteid", "667", "--size", "small", "--apply")
    self.assertEqual(rc, 0, out)
    topo = self.inv("rcp", "topology_vars", "new")
    self.assertIn("name: new-smc01", topo)
    self.assertNotIn("small-smc01", topo)
    self.assertIn("last: +110", topo)
    self.assertFalse([ln for ln in topo.splitlines() if ln != ln.rstrip()])
    self.assertIn("NICs enp1s0; VLAN IDs 525", out)
    self.assertIn("NOTE  rcp host_vars usually carry the VoIP", out)

  def test_refusals_write_nothing(self) -> None:
    """An existing host, a missing sibling, or --size on rct changes no file."""
    before = (self.repo / "inventories" / "rct" / "prod").read_text()
    self.assertEqual(run(self.repo, "--flavor", "rct", "--host", "old-smc01", "--siteid", "1", "--apply")[0], 1)
    self.assertEqual(run(self.repo, "--flavor", "rct", "--host", "x-smc01", "--siteid", "100", "--apply")[0], 1)
    self.assertEqual(run(self.repo, "--flavor", "rcp", "--host", "x-smc01", "--siteid", "2", "--topology-from", "nope", "--apply")[0], 1)
    self.assertEqual(run(self.repo, "--flavor", "rct", "--host", "x-smc01", "--siteid", "3", "--size", "big", "--apply")[0], 2)
    self.assertEqual((self.repo / "inventories" / "rct" / "prod").read_text(), before)
    self.assertFalse((self.repo / "inventories" / "rct" / "host_vars" / "x-smc01.yml").exists())
    self.assertFalse((self.repo / "inventories" / "rcp" / "group_vars" / "x.yml").exists())


class OutputFaultsTest(unittest.TestCase):
  """The output check alone."""

  def test_flags_quoted_iridium_empty_name_trailing_space(self) -> None:
    """Each fault the old generator produced is caught."""
    with tempfile.TemporaryDirectory() as d:
      p = Path(d, "f.yml")
      p.write_text('smc_bases_iridium: "True"\n  name:\nsubnets: \n')
      faults = m.output_faults({"host_vars": str(p)})
    self.assertEqual(len(faults), 3, faults)


if __name__ == "__main__":
  unittest.main()
