"""Exercise disk_grow.py plans for every platform, its plan/check/apply gating, and the guest script's syntax.

Usage: just test (or: <venv python> -B -m unittest discover -s tests -v)
Plans are built in memory; execution tests run only `true`/`false`; nothing touches a host.
"""

import contextlib
import importlib.util
import io
import shutil
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_SPEC = importlib.util.spec_from_file_location("disk_grow", ROOT / "scripts" / "disk_grow.py")
disk_grow = importlib.util.module_from_spec(_SPEC)
sys.modules["disk_grow"] = disk_grow
_SPEC.loader.exec_module(disk_grow)


def plan(argv):
  """Build the step list for one command line.

  Args:
    argv: Arguments as on the command line.
  Returns:
    List of disk_grow.Step.
  Raises:
    SystemExit: On invalid arguments.
  """
  a = disk_grow.parse_args(argv)
  return disk_grow.PLANS[a.platform](a)


def joined(steps):
  """Join every step's argv into one string per step.

  Args:
    steps: List of Step.
  Returns:
    List of command strings.
  Raises:
    None.
  """
  return [" ".join(s.argv) for s in steps]


class PlanTests(unittest.TestCase):
  """Each platform's ordered steps and their write flags."""

  def test_aws_order_and_flags(self):
    """describe, modifications, snapshot, modify (size + type), wait, guest.

    Args:
      None.
    Returns:
      None.
    """
    steps = plan(["aws", "--volume-id", "vol-1", "--size", "500", "--type", "gp3", "--profile", "p", "--region", "r", "--guest-ssh", "ssh root@h"])
    cmds = joined(steps)
    self.assertEqual([s.write for s in steps], [False, False, True, True, True, True])
    self.assertIn("create-snapshot --volume-id vol-1", cmds[2])
    self.assertIn("modify-volume --volume-id vol-1 --size 500 --volume-type gp3", cmds[3])
    self.assertEqual(steps[4].kind, "ebs-wait")
    self.assertEqual(steps[5].argv, ["ssh", "root@h", "bash -s -- --mount /"])

  def test_no_snapshot_and_no_guest(self):
    """--no-snapshot drops the snapshot; no --guest-ssh drops the guest step.

    Args:
      None.
    Returns:
      None.
    """
    cmds = joined(plan(["aws", "--volume-id", "vol-1", "--size", "50", "--no-snapshot"]))
    self.assertFalse(any("create-snapshot" in c for c in cmds))
    self.assertFalse(any("bash -s" in c for c in cmds))

  def test_proxmox_vm_remote(self):
    """qm commands are wrapped in the host transport as one remote string.

    Args:
      None.
    Returns:
      None.
    """
    steps = plan(["proxmox-vm", "--vmid", "101", "--disk", "scsi0", "--size", "64", "--host-ssh", "ssh root@pve1", "--snap-name", "s1"])
    self.assertEqual(steps[1].argv, ["ssh", "root@pve1", "qm snapshot 101 s1"])
    self.assertEqual(steps[2].argv, ["ssh", "root@pve1", "qm disk resize 101 scsi0 64G"])

  def test_proxmox_ct_local(self):
    """pct resize runs locally without a host transport and ends with a df read.

    Args:
      None.
    Returns:
      None.
    """
    steps = plan(["proxmox-ct", "--vmid", "200", "--size", "20"])
    self.assertEqual(steps[2].argv, ["pct", "resize", "200", "rootfs", "20G"])
    self.assertFalse(steps[-1].write)

  def test_libvirt_extend_flag(self):
    """blockresize always carries --extend so it cannot shrink.

    Args:
      None.
    Returns:
      None.
    """
    steps = plan(["libvirt", "--domain", "vm1", "--target", "vda", "--size", "40"])
    self.assertEqual(steps[2].argv, ["virsh", "blockresize", "vm1", "vda", "40G", "--extend"])

  def test_qemu_img(self):
    """qemu-img resize without --shrink.

    Args:
      None.
    Returns:
      None.
    """
    steps = plan(["qemu-img", "--image", "/v/d.qcow2", "--size", "30"])
    self.assertEqual(steps[2].argv, ["qemu-img", "resize", "/v/d.qcow2", "30G"])

  def test_bad_size(self):
    """Zero and oversize are refused with exit 2.

    Args:
      None.
    Returns:
      None.
    """
    for size in ("0", str(disk_grow.MAX_GIB + 1)):
      with self.assertRaises(SystemExit) as cm, contextlib.redirect_stderr(io.StringIO()):
        disk_grow.parse_args(["aws", "--volume-id", "v", "--size", size])
      self.assertEqual(cm.exception.code, 2)


class GateTests(unittest.TestCase):
  """plan runs nothing, check runs reads only, apply stops at the first failure."""

  def steps(self):
    """A read that succeeds, a write that fails, a read after it.

    Args:
      None.
    Returns:
      List of Step.
    """
    return [disk_grow.Step("r1", ["true"], False), disk_grow.Step("w", ["false"], True), disk_grow.Step("r2", ["true"], False)]

  def run_mode(self, mode):
    """Execute the fixture steps in one mode, capturing output.

    Args:
      mode: plan, check or apply.
    Returns:
      Exit status.
    """
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
      return disk_grow.execute(self.steps(), mode)

  def test_modes(self):
    """plan 0 (nothing run), check 0 (failing write skipped), apply 1 (failing write run).

    Args:
      None.
    Returns:
      None.
    """
    self.assertEqual(self.run_mode("plan"), 0)
    self.assertEqual(self.run_mode("check"), 0)
    self.assertEqual(self.run_mode("apply"), 1)


class GuestScriptTests(unittest.TestCase):
  """The guest script parses and refuses bad arguments."""

  def test_syntax(self):
    """bash -n accepts the script.

    Args:
      None.
    Returns:
      None.
    """
    res = subprocess.run(["bash", "-n", str(disk_grow.GUEST_SCRIPT)], capture_output=True, timeout=30, check=False)
    self.assertEqual(res.returncode, 0, res.stderr)

  def test_bad_argument(self):
    """An unknown flag exits 2 before any read.

    Args:
      None.
    Returns:
      None.
    """
    res = subprocess.run(["bash", str(disk_grow.GUEST_SCRIPT), "--bogus"], capture_output=True, timeout=30, check=False)
    self.assertEqual(res.returncode, 2)

  @unittest.skipUnless(shutil.which("shellcheck"), "shellcheck not installed")
  def test_shellcheck(self):
    """shellcheck reports nothing.

    Args:
      None.
    Returns:
      None.
    """
    res = subprocess.run(["shellcheck", str(disk_grow.GUEST_SCRIPT)], capture_output=True, timeout=60, check=False)
    self.assertEqual(res.returncode, 0, res.stdout)


if __name__ == "__main__":
  unittest.main()
