"""Offline tests for the helpers in scripts/: the lab inventory ("vagrant_lab_inventory"), the Vagrantfile lint ("vagrantfile_lint"), the copy check
("vagrant_copy_check") and the governance gate ("check_governance"). No Vagrant, Parallels or network is touched: commands are faked.

Run: just test.
"""

from __future__ import annotations

import contextlib
import importlib
import io
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
inventory = importlib.import_module("vagrant_lab_inventory")
lint = importlib.import_module("vagrantfile_lint")
copy_check = importlib.import_module("vagrant_copy_check")

GLOBAL_STATUS = """1794027384,,metadata,machine-count,2
1794027384,,machine-id,aaa1111
1794027384,,provider-name,parallels
1794027384,,machine-home,{home}
1794027384,,state,running
1794027384,,machine-id,bbb2222
1794027384,,provider-name,parallels
1794027384,,machine-home,{home}
1794027384,,state,not_created
"""
BOX_LIST = """1794027392,,ui,info,bento/ubuntu-24.04 (parallels%!(VAGRANT_COMMA) 202510.26.0)
1794027392,,box-name,bento/ubuntu-24.04
1794027392,,box-provider,parallels
1794027392,,box-version,202510.26.0
1794027392,,box-architecture,arm64
"""
VMS = [
  {
    "Name": "lab-a",
    "ID": "{u-a}",
    "State": "running",
    "Parent VM": None,
    "GuestTools": {"state": "outdated"},
    "Hardware": {"cpu": {}, "net0": {"type": "shared", "state": "connected"}, "net1": {"type": "host"}},
  },
  {
    "Name": "lab-a-clone",
    "ID": "{u-c}",
    "State": "running",
    "Parent VM": "lab-a",
    "GuestTools": {"state": "installed"},
    "Hardware": {"net0": {"type": "shared", "state": "disconnected"}},
  },
]
VBOX_VMS = '"vbox-lab" {11111111-2222-3333-4444-555555555555}\n"other" {aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee}\nnoise line\n'
VBOX_RUNNING = '"vbox-lab" {11111111-2222-3333-4444-555555555555}\n'
LAB_VAGRANTFILE = """Vagrant.configure("2") do |config|
  config.vm.box = "bento/ubuntu-24.04"
  config.vm.box_version = "202510.26.0"
  config.vm.define "lab-a", primary: true do |a|
    a.vm.provider "parallels" do |p|
      p.name = "lab-a"
    end
  end
  config.vm.define "lab-b", autostart: false do |b|
    b.vm.provider "parallels" do |p|
      p.name = "lab-b"
    end
  end
end
"""


def fake_runner(home: str, fail: str | None = None):
  """A command runner that answers the commands the inventory runs (vagrant, prlctl, VBoxManage, prlsrvctl).

  Args:
    home: the machine-home to report.
    fail: a command name that should fail.

  Returns:
    A callable like run_command.
  """

  def run(argv):
    if fail and argv[0] == fail:
      raise inventory.InventoryError(f"{fail} failed")
    if argv[:2] == ["vagrant", "global-status"]:
      return GLOBAL_STATUS.format(home=home)
    if argv[:3] == ["vagrant", "box", "list"]:
      return BOX_LIST
    if argv[:2] == ["prlctl", "list"]:
      return json.dumps(VMS)
    if argv[:3] == ["VBoxManage", "list", "vms"]:
      return VBOX_VMS
    if argv[:3] == ["VBoxManage", "list", "runningvms"]:
      return VBOX_RUNNING
    if argv[0] == "prlsrvctl":
      return json.dumps({"edition": "pro", "status": "ACTIVE", "serial": "SECRET-SHOULD-NOT-PRINT"})
    raise AssertionError(argv)

  return run


class Inventory(unittest.TestCase):
  """vagrant_lab_inventory: parsing, joining, and that nothing secret is printed."""

  def setUp(self):
    self.tmp = tempfile.TemporaryDirectory()
    home = Path(self.tmp.name)
    (home / "Vagrantfile").write_text(LAB_VAGRANTFILE)
    idf = home / ".vagrant/machines/lab-a/parallels/id"
    idf.parent.mkdir(parents=True)
    idf.write_text("{u-a}\n")
    self.home = str(home)

  def tearDown(self):
    self.tmp.cleanup()

  def test_machine_readable_unescapes_commas(self):
    rows = inventory.machine_readable("1,,ui,info,a%!(VAGRANT_COMMA) b\n")
    self.assertEqual(rows, [("ui", ["info", "a, b"])])

  def test_global_status_groups_rows_per_machine(self):
    machines = inventory.parse_global_status(GLOBAL_STATUS.format(home="/x"))
    self.assertEqual([(m.machine_id, m.state) for m in machines], [("aaa1111", "running"), ("bbb2222", "not_created")])

  def test_vms_report_linked_parent_and_adapter_state(self):
    vms = inventory.parse_vms(json.dumps(VMS))
    self.assertEqual(vms[1]["parent"], "lab-a")
    self.assertEqual(vms[0]["nets"], {"net0": "shared/connected", "net1": "host/connected"})
    self.assertEqual(vms[1]["nets"], {"net0": "shared/disconnected"})
    with self.assertRaises(inventory.InventoryError):
      inventory.parse_vms("not json")

  def test_vagrantfile_pins_literal_missing_and_computed(self):
    self.assertEqual(inventory.vagrantfile_boxes(LAB_VAGRANTFILE), [("bento/ubuntu-24.04", "202510.26.0")])
    self.assertEqual(inventory.vagrantfile_boxes('c.vm.box = "x/y"\n'), [("x/y", "")])
    self.assertEqual(inventory.vagrantfile_boxes("c.vm.box = BOX\nc.vm.box_version = V\n"), [("?", "?")])

  def test_collect_joins_machines_to_vms_and_pins(self):
    inv = inventory.collect(fake_runner(self.home), want_latest=True, want_edition=True, fetch=lambda url: b'{"current_version": {"version": "202601.01.0"}}')
    self.assertEqual(inv["edition"], "pro/ACTIVE")
    self.assertEqual(inv["machines"][0]["vm_uuids"], {"lab-a": "u-a"})
    self.assertEqual(inv["pins"], [{"box": "bento/ubuntu-24.04", "pin": "202510.26.0", "installed": True, "latest": "202601.01.0"}])
    text = "\n".join(inventory.report(inv))
    self.assertIn("lab-a (parallels)->lab-a", text)
    self.assertIn("lab-a-clone | running | lab-a", text)
    self.assertNotIn("SECRET", text + json.dumps(inv))

  def test_registry_failure_is_unknown_not_an_error(self):
    def boom(url):
      raise OSError("offline")

    self.assertEqual(inventory.latest_version("bento/x", boom), "")

  def test_failed_required_command_exits_1(self):
    err = io.StringIO()
    with contextlib.redirect_stderr(err), contextlib.redirect_stdout(io.StringIO()):
      self.assertEqual(inventory.main(["--no-edition"], run=fake_runner(self.home, fail="vagrant")), 1)
    self.assertIn("vagrant failed", err.getvalue())

  def test_missing_hypervisor_cli_is_unavailable_not_an_error(self):
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
      self.assertEqual(inventory.main(["--no-edition"], run=fake_runner(self.home, fail="prlctl")), 0)
    self.assertIn("parallels unavailable: prlctl failed", out.getvalue())
    self.assertIn("vbox-lab | running", out.getvalue())

  def test_vbox_listing_parses_names_uuids_and_running(self):
    vms = inventory.parse_vbox_vms(VBOX_VMS, VBOX_RUNNING)
    self.assertEqual([(v["name"], v["state"]) for v in vms], [("vbox-lab", "running"), ("other", "not running")])

  def test_machine_ids_for_virtualbox_and_qemu_providers(self):
    for provider, vm_id in (("virtualbox", "11111111-2222-3333-4444-555555555555"), ("qemu", "q-123")):
      idf = Path(self.home) / f".vagrant/machines/lab-{provider}/{provider}/id"
      idf.parent.mkdir(parents=True)
      idf.write_text(vm_id)
    (Path(self.home) / ".vagrant/machines/lab-x/docker/id").parent.mkdir(parents=True)
    (Path(self.home) / ".vagrant/machines/lab-x/docker/id").write_text("ignored")
    inv = inventory.collect(fake_runner(self.home), want_latest=False, want_edition=False)
    self.assertEqual(inv["machines"][0]["vm_providers"], {"lab-a": "parallels", "lab-qemu": "qemu", "lab-virtualbox": "virtualbox"})
    text = "\n".join(inventory.report(inv))
    self.assertIn("lab-virtualbox (virtualbox)->vbox-lab", text)
    self.assertIn("lab-qemu (qemu)->qemu id q-123", text)

  def test_edition_unreadable_is_unknown(self):
    self.assertEqual(inventory.edition(fake_runner(self.home, fail="prlsrvctl")), "unknown")


class Lint(unittest.TestCase):
  """vagrantfile_lint: each rule fires on a bad file and stays quiet on the worked example's shape."""

  def rules(self, text):
    return sorted({f.rule for f in lint.lint_text(text)})

  def test_clean_lab_file(self):
    self.assertEqual(lint.lint_text(LAB_VAGRANTFILE), [])

  def test_unpinned_range_and_computed(self):
    self.assertIn("box-unpinned", self.rules('c.vm.box = "a/b"\nc.vm.provider "parallels" do |p| end\n'))
    self.assertIn("box-range", self.rules('c.vm.box = "a/b"\nc.vm.box_version = ">= 1.0"\nc.vm.provider "parallels"\n'))
    self.assertIn("box-range", self.rules('c.vm.box = "a/b"\nc.vm.box_version = "~> 2.0"\nc.vm.provider "parallels"\n'))
    self.assertIn("box-computed", self.rules('c.vm.box = BOX\nc.vm.box_version = "1"\nc.vm.provider "parallels"\n'))

  def test_exact_versions_pass(self):
    for v in ("202510.26.0", "= 4.3.2", "1.0.0-rc1"):
      self.assertNotIn("box-range", self.rules(f'c.vm.box = "a/b"\nc.vm.box_version = "{v}"\nc.vm.provider "parallels"\n'), v)

  def test_commented_box_is_ignored(self):
    self.assertEqual(self.rules('# c.vm.box = "a/b"\nc.vm.provider "parallels"\n'), [])

  def test_provider_missing_and_names(self):
    self.assertIn("provider-missing", self.rules('c.vm.box = "a/b"\nc.vm.box_version = "1"\n'))
    two = 'c.vm.box = "a/b"\nc.vm.box_version = "1"\nc.vm.define "x"\nc.vm.define "y"\nc.vm.provider "parallels" do |p|\n p.memory = 1\nend\n'
    self.assertIn("vm-name-missing", self.rules(two))

  def test_customize_device_needs_post_import(self):
    base = 'c.vm.box = "a/b"\nc.vm.box_version = "1"\nc.vm.provider "parallels" do |p|\n'
    self.assertIn("customize-device", self.rules(base + '  p.customize ["set", :id, "--device-add", "hdd"]\nend\n'))
    self.assertNotIn("customize-device", self.rules(base + '  p.customize "post-import", ["set", :id, "--device-add", "hdd"]\nend\n'))

  def test_secrets_including_commented_ones(self):
    for bad in (
      'config.ssh.password = "hunter22"',
      '# config.ssh.password = "hunter22"',
      "-----BEGIN OPENSSH PRIVATE KEY-----",
      'ENVV = { api_key: "abcd1234" }',
      "AKIAABCDEFGHIJKLMNOP",
    ):
      self.assertIn("secret", self.rules(bad + '\nc.vm.provider "parallels"\n'), bad)
    self.assertNotIn("secret", self.rules('config.ssh.password = ENV["LAB_PW"]\nc.vm.provider "parallels"\n'))

  def test_cli_exit_codes(self):
    with tempfile.TemporaryDirectory() as tmp:
      good, bad = Path(tmp, "good"), Path(tmp, "bad")
      good.write_text(LAB_VAGRANTFILE)
      bad.write_text('c.vm.box = "a/b"\n')
      with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        self.assertEqual(lint.main([str(good)]), 0)
        self.assertEqual(lint.main([str(bad)]), 1)
        self.assertEqual(lint.main([str(Path(tmp, "missing"))]), 2)


class CopyCheck(unittest.TestCase):
  """vagrant_copy_check: equal, different, missing copy, missing canonical."""

  def test_states(self):
    with tempfile.TemporaryDirectory() as tmp:
      canon, copy = Path(tmp, "canon"), Path(tmp, "copy")
      canon.write_text("a")
      self.assertEqual(copy_check.compare(copy, canon)[0], "fail")
      copy.write_text("a")
      self.assertEqual(copy_check.compare(copy, canon)[0], "ok")
      copy.write_text("b")
      status, message = copy_check.compare(copy, canon)
      self.assertEqual(status, "fail")
      self.assertIn("copy the canonical file over it", message)
      self.assertEqual(copy_check.compare(copy, Path(tmp, "gone"))[0], "skipped")
      self.assertEqual(copy_check.compare(copy, Path(tmp, "gone"), require_canonical=True)[0], "fail")
      with contextlib.redirect_stdout(io.StringIO()):
        self.assertEqual(copy_check.main([f"{copy}={canon}"]), 1)
        copy.write_text("a")
        self.assertEqual(copy_check.main([f"{copy}={canon}"]), 0)

  def test_bad_pair_is_rejected(self):
    with self.assertRaises(copy_check.argparse.ArgumentTypeError):
      copy_check.parse_pair("no-equals-sign")


class Governance(unittest.TestCase):
  """scripts/check_governance.py ("check_governance") is the pack's governance gate; it runs here so `just test` covers it."""

  PACK = Path(__file__).resolve().parents[1]

  def _run(self, root: Path) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(root / "scripts" / "check_governance.py")], capture_output=True, text=True, check=False, timeout=60)

  def test_governance_claims_hold(self):
    result = self._run(self.PACK)
    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

  def test_a_broken_reference_fails_the_gate(self):
    with tempfile.TemporaryDirectory() as tmp:
      copy = Path(tmp) / "pack"
      shutil.copytree(self.PACK, copy, ignore=shutil.ignore_patterns(".git", "documents", "graphify-out", ".ai-context", "__pycache__"))
      (copy / "documents" / "research-sources-20261107").mkdir(parents=True)
      shutil.copy(self.PACK / "documents" / "readme.md", copy / "documents" / "readme.md")
      shutil.copy(self.PACK / "documents" / "research-sources-20261107" / "readme.md", copy / "documents" / "research-sources-20261107" / "readme.md")
      with (copy / "README.md").open("a", encoding="utf-8") as fh:
        fh.write("\nSee `references/does-not-exist.md`.\n")
      result = self._run(copy)
    self.assertEqual(result.returncode, 1, result.stdout)
    self.assertIn("does-not-exist.md", result.stdout)


if __name__ == "__main__":
  unittest.main()
