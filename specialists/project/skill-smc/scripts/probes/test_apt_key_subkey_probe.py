"""Offline test for apt_key_subkey_probe.sh: a stand-in tsh runs the probe locally against a fake apt root; no SMC is contacted.

Run: `just apt_key_subkey_probe_test`. Needs gpg on PATH. About 5 s (two throwaway keys are generated).
"""

from __future__ import annotations

import os
import stat
import subprocess
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent / "apt_key_subkey_probe.sh"

# Stand-in tsh: "tsh ssh --proxy=X root@<node> '<env> bash -s'" runs the last argument locally with the probe on stdin; dark-smc01 does not answer.
FAKE_TSH = """#!/bin/sh
for a in "$@"; do last="$a"; case "$a" in root@dark-smc01) exit 1 ;; esac; done
exec sh -c "$last"
"""


def make_key(home: Path, uid: str, with_subkey: bool) -> tuple[bytes, str, str]:
  """Generate a throwaway key, optionally with a signing subkey, and export it.

  Args:
    home: an empty folder used as GNUPGHOME.
    uid: user id for the key.
    with_subkey: add a signing subkey to the primary.

  Returns:
    (exported public key bytes, primary fingerprint, subkey fingerprint or "").
  """
  env = {**os.environ, "GNUPGHOME": str(home)}

  def run(*args: str) -> subprocess.CompletedProcess[str]:
    """Run gpg in batch mode with an empty passphrase in this GNUPGHOME.

    Args:
      args: gpg arguments.

    Returns:
      The completed process; raises CalledProcessError on failure.
    """
    return subprocess.run(["gpg", "--batch", "--pinentry-mode", "loopback", "--passphrase", "", *args], env=env, capture_output=True, text=True, check=True)

  run("--quick-gen-key", uid, "ed25519", "sign", "never")
  fprs = [line.split(":")[9] for line in run("--with-colons", "--list-keys", uid).stdout.splitlines() if line.startswith("fpr")]
  primary = fprs[0]
  sub = ""
  if with_subkey:
    run("--quick-add-key", primary, "ed25519", "sign", "never")
    fprs = [line.split(":")[9] for line in run("--with-colons", "--list-keys", uid).stdout.splitlines() if line.startswith("fpr")]
    sub = fprs[-1]
  exported = subprocess.run(["gpg", "--export", primary], env=env, capture_output=True, check=True).stdout
  return exported, primary, sub


class AptKeySubkeyProbeTest(unittest.TestCase):
  """Present/absent lookup of primaries and subkeys, the source column and exit codes."""

  @classmethod
  def setUpClass(cls) -> None:
    """Build a fake apt root holding a key with a subkey (trusted.gpg) and a source line commented out."""
    cls.tmp = tempfile.TemporaryDirectory()
    base = Path(cls.tmp.name)
    (base / "gpg").mkdir(mode=0o700)
    root = base / "root"
    for sub in ("etc/apt/trusted.gpg.d", "etc/apt/keyrings", "etc/apt/sources.list.d", "usr/share/keyrings"):
      (root / sub).mkdir(parents=True)
    exported, cls.primary, cls.subkey = make_key(base / "gpg", "Vendor <v@example.invalid>", with_subkey=True)
    (root / "etc/apt/trusted.gpg").write_bytes(exported)
    (root / "etc/apt/sources.list.d/vendor.list").write_text("# deb https://pkgs.example.invalid/deb stable main\n")
    bin_dir = base / "bin"
    bin_dir.mkdir()
    tsh = bin_dir / "tsh"
    tsh.write_text(FAKE_TSH)
    tsh.chmod(tsh.stat().st_mode | stat.S_IXUSR)
    cls.env = {**os.environ, "PATH": f"{bin_dir}:{os.environ['PATH']}", "APT_ROOT": str(root)}

  @classmethod
  def tearDownClass(cls) -> None:
    """Remove the fake root."""
    cls.tmp.cleanup()

  def probe(self, fpr: str, *nodes: str) -> subprocess.CompletedProcess[str]:
    """Run the probe through the stand-in tsh.

    Args:
      fpr: fingerprint to look for.
      nodes: node names.

    Returns:
      The completed process.
    """
    cmd = [str(SCRIPT), "--proxy", "p.invalid", "--source", "pkgs.example.invalid", "--fpr", fpr, *nodes]
    return subprocess.run(cmd, env=self.env, capture_output=True, text=True, timeout=60, check=False)

  def test_subkey_present_names_primary(self) -> None:
    """A subkey fingerprint is found in trusted.gpg and reported with its primary and the commented source line."""
    out = self.probe(self.subkey, "a-smc01")
    self.assertEqual(out.returncode, 0, out.stdout + out.stderr)
    self.assertIn("|fpr=present|in=/etc/apt/trusted.gpg|", out.stdout)
    self.assertIn(f"|primary={self.primary}|", out.stdout)
    self.assertIn("|source=# deb https://pkgs.example.invalid/deb stable main;", out.stdout)

  def test_absent_and_dark(self) -> None:
    """An unknown fingerprint reads absent; a node that does not answer gives FAIL and exit 1."""
    out = self.probe("0" * 40, "a-smc01", "dark-smc01")
    self.assertEqual(out.returncode, 1, out.stdout + out.stderr)
    self.assertIn("APTKEY|a-smc01|", out.stdout)
    self.assertIn("|fpr=absent", out.stdout)
    self.assertIn("FAIL|dark-smc01|", out.stdout)

  def test_bad_usage(self) -> None:
    """A short fingerprint or no node is refused with exit 2."""
    self.assertEqual(subprocess.run([str(SCRIPT), "--proxy", "p", "--fpr", "ABC", "n"], capture_output=True, timeout=30, check=False).returncode, 2)
    self.assertEqual(subprocess.run([str(SCRIPT), "--proxy", "p", "--fpr", "0" * 40], capture_output=True, timeout=30, check=False).returncode, 2)


if __name__ == "__main__":
  unittest.main()
