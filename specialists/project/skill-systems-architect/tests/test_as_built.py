"""Offline tests for scripts/as_built.py and as_built_probes.py: a fake runner stands in for SSH and local commands. Run: just test."""

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
_spec = importlib.util.spec_from_file_location("as_built", _SCRIPTS / "as_built.py")
ab = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ab)


def fake_runner(answers: dict[str, str], counter: list | None = None):
  """A runner answering by substring of the last argument.

  Args:
    answers: substring of the command to output.
    counter: when given, an int list whose first item is appended to every output (simulates churn).

  Returns:
    The runner.
  """

  def run(cmd, stdin=None, timeout=0):
    """Answer one command.

    Args:
      cmd: argv; stdin: ignored; timeout: ignored.
    Returns:
      (0, output).
    """
    last = cmd[-1]
    for key, out in answers.items():
      if key in last:
        if counter is not None:
          counter[0] += 1
          return 0, out + f"tick {counter[0]}\n"
        return 0, out
    return 0, ""

  return run


class Masking(unittest.TestCase):
  """Secrets and emails never reach a capture file."""

  def test_masks(self):
    """Secret-shaped values, tokens and emails are replaced; fingerprints and digests stay.

    Args:
      None.
    Returns:
      None.
    """
    raw = "cipassword: x\npassword=hunter2\nroot hvs.ABCDEFGHIJKLMNOPQRSTUVWX12\nowner admin@example.org\nSHA256:fA0b0Dv17b2l sha256:47e43b1b"
    out = ab.mask(raw, [])
    for bad in ("hunter2", "hvs.ABCDEFGHIJ", "admin@example.org"):
      self.assertNotIn(bad, out)
    self.assertIn("SHA256:fA0b0Dv17b2l sha256:47e43b1b", out)


class Churn(unittest.TestCase):
  """Churn lines go, and --twice catches what is left."""

  def test_drop(self):
    """Lines matching a drop pattern and trailing spaces are removed.

    Args:
      None.
    Returns:
      None.
    """
    self.assertEqual(ab.drop_churn("a  \ntick 1\nb\n\n", ["^tick "]), "a\nb\n")

  def test_twice_detects_and_filters(self):
    """A changing line makes two captures differ; a drop pattern for it makes them identical.

    Args:
      None.
    Returns:
      None.
    """
    t = [{"name": "h", "type": "command", "commands": {"x": "uptime"}}]
    c = [0]
    run = fake_runner({"uptime": "up\n"}, c)
    one, _ = ab.capture({}, t, run)
    two, _ = ab.capture({}, t, run)
    self.assertNotEqual(one, two)
    t[0]["drop"] = ["^tick "]
    self.assertEqual(ab.capture({}, t, run)[0], ab.capture({}, t, run)[0])


class Manifest(unittest.TestCase):
  """Bad manifests are refused before anything runs."""

  def test_refusals(self):
    """Unknown type, missing name and duplicate names give ValueError.

    Args:
      None.
    Returns:
      None.
    """
    with tempfile.TemporaryDirectory() as d:
      for body in (
        '[[target]]\nname="a"\ntype="nope"\n',
        '[[target]]\ntype="hand"\nrows=[]\n',
        '[[target]]\nname="a"\ntype="hand"\nrows=[]\n[[target]]\nname="a"\ntype="hand"\nrows=[]\n',
      ):
        p = Path(d) / "m.toml"
        p.write_text(body)
        with self.assertRaises(ValueError):
          ab.load_manifest(p)


class Probes(unittest.TestCase):
  """Probe shapes: one file per target, pve-pool one per guest, sections in name order."""

  def test_pool_files_per_guest(self):
    """A pool with a running VM and a stopped LXC gives two files; the VM is read inside over SSH.

    Args:
      None.
    Returns:
      None.
    """
    pool = json.dumps({"members": [{"vmid": 702, "type": "qemu", "status": "running"}, {"vmid": 101, "type": "lxc", "status": "stopped"}]})
    run = fake_runner({"pvesh get /pools": pool, "qm config 702": "ipconfig0: ip=192.168.86.202/24,gw=192.168.86.1\n", "PRETTY_NAME": "Ubuntu\n"})
    files, failed = ab.capture({}, [{"name": "pool", "type": "pve-pool", "ssh": "root@n", "pool": "p", "guest_user": "ubuntu"}], run)
    self.assertEqual(sorted(files), ["pool/lxc-101.txt", "pool/qemu-702.txt"])
    self.assertIn("== os\nUbuntu", files["pool/qemu-702.txt"])
    self.assertIn("stopped, not read", files["pool/lxc-101.txt"])
    self.assertEqual(failed, [])

  def test_apply_writes_and_plan_does_not(self):
    """Plan reports new without writing; apply writes; a second plan reports same.

    Args:
      None.
    Returns:
      None.
    """
    with tempfile.TemporaryDirectory() as d:
      m = Path(d) / "as-built.toml"
      m.write_text('[capture]\nout="caps"\n[[target]]\nname="router"\ntype="hand"\nrows=[{what="forward 443", value="to .201", checked="2026-11-26"}]\n')
      self.assertEqual(ab.main(["--manifest", str(m)]), 0)
      self.assertFalse((Path(d) / "caps/router.txt").exists())
      self.assertEqual(ab.main(["--manifest", str(m), "--apply"]), 0)
      self.assertIn("forward 443 | to .201", (Path(d) / "caps/router.txt").read_text())
      self.assertEqual(ab.compare(Path(d) / "caps", ab.capture(*ab.load_manifest(m))[0]), {"router.txt": "same"})


if __name__ == "__main__":
  unittest.main()
